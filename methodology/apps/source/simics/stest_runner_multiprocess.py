import io
import logging
import multiprocessing as mp
import time
import queue

from errors import SimicsError
from shell import run

from .stest_loader import STestLoader
from .stest_result import STestResult
from .stest_runner import STestRunner
from .stest_suite import STestSuite


TIMEOUT_MULTIPROCESS = 10

class STestRunnerMultiprocess(STestRunner):
    splatform = None
    verbose = False
    def __init__(self, verbose=False):
        super().__init__(verbose)
        STestRunnerMultiprocess.verbose = verbose

    def collect(self, test, queue, tasks, result):
        timeouts = []
        for case in test:
            self.add_task(queue, tasks, case)
            timeouts.append(case.timeout)
            logging.debug('added test %s (%s) to %s', len(tasks), tasks[-1], queue)
        return max(timeouts)

    def run(self, test):
        STestRunnerMultiprocess.splatform = test.splatform
        queue_test = mp.Queue()
        queue_result = mp.Queue()
        result = self._make_result()
        tasks = []
        completed = []
        workers = []
        workers_number = mp.cpu_count()

        time_start = time.perf_counter()
        timeout = self.collect(test, queue_test, tasks, result)
        logging.debug('max timeout is %s', timeout)

        logging.debug('staring %s workers', workers_number)
        for iworker in range(workers_number):
            process = self.start_process(iworker, queue_test, queue_result, result.__class__)
            workers.append(process)
            logging.debug('started worker %s', iworker)

        tasks_total = len(tasks)

        while tasks:
            logging.debug('waiting for results (%s/%s tasks)', len(completed), tasks_total)
            iworker, case_name, batch_result = queue_result.get(timeout=timeout)
            tasks.remove(case_name)
            completed.append([case_name, batch_result])
            self.consolidate(result, batch_result)
            # for worker in workers:
                # if not worker.is_alive():
                    # logging.info('worker %s is not alive', workers)
        
        time_stop = time.perf_counter()

        result.stream.write_line()
        result.print_errors()
        result.print_summary(time_start, time_stop)

        for worker in workers:
            if worker.is_alive():
                queue_test.put('STOP', block=False)
        for iworker, worker in enumerate(workers):
            if worker.is_alive():
                logging.debug('joining worker %s', iworker)
                worker.join()
                if worker.is_alive():
                    logging.warning('failed to join worker %s', iworker)

        return 0 if result.is_successfull() else 1

    def start_process(self, iworker, queue_test, queue_result, result_class):
        process = mp.Process(
            target=runner,
            args=(
                iworker,
                queue_test,
                queue_result,
                result_class,
            )
        )
        process.start()
        return process

    def consolidate(self, result, batch_result):
        output, test_run, failures, skipped = batch_result
        result.stream.write(output)
        result.stream.flush()
        result.test_run += test_run
        result.failures.extend(failures)
        result.skipped.extend(skipped)

    @staticmethod
    def add_task(queue, tasks, case):
        arg = None
        queue.put((case.name, arg), block=False)
        if tasks is not None:
            tasks.append(case.name)


def runner(iworker, queue_test, queue_result, result_class):
    try:
        __runner(iworker, queue_test, queue_result, result_class)
    except queue.Empty:
        logging.debug('worker %s timed out waiting for tasks', iworker)
    except KeyboardInterrupt:
        logging.debug('worker %s keyboard interrupt, stopping...', iworker)


def __runner(iworker, queue_test, queue_result, result_class):
    loader = STestLoader(STestRunnerMultiprocess.splatform)

    def get():
        return queue_test.get(timeout=TIMEOUT_MULTIPROCESS)

    def make_result():
        stream = io.StringIO()
        result = result_class(stream=stream, verbose=STestRunnerMultiprocess.verbose)
        return result

    def batch(result):
        failures = [(c, err) for c, err in result.failures]
        skipped = [(c, err) for c, err in result.skipped]
        return (
            result.stream.getvalue(),
            result.test_run,
            failures,
            skipped,
        )

    for case_name, arg in iter(get, 'STOP'):
        stest_suites = loader.load_by_names([case_name])
        assert len(stest_suites) == 1
        logging.debug('worker %s tests %s', iworker, case_name)
        stest_suite = stest_suites[0]
        result = make_result()
        stest_suite.run(result)
        queue_result.put([iworker, case_name, batch(result)])

    logging.debug('workder %s ending', iworker)
