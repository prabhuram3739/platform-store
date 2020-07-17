import time

from errors import SimicsError
from shell import run

from .stest_result import STestResult


class STestRunner:
    def __init__(self, verbose=False):
        self.verbose = verbose

    def run(self, test):
        result = self._make_result()
        time_start = time.perf_counter()
        result.start_test_run()
        test(result)
        result.stop_test_run()
        time_stop = time.perf_counter()

        result.stream.write_line()
        result.print_errors()
        result.print_summary(time_start, time_stop)

        return 0 if result.is_successfull() else 1

    def _make_result(self):
        return STestResult(self.verbose)
