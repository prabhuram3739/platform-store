import sys


class _WriteLineDecorator(object):
    def __init__(self,stream):
        self.stream = stream

    def __getattr__(self, attr):
        if attr in ('stream', '__getstate__'):
            raise AttributeError(attr)
        return getattr(self.stream,attr)

    def write_line(self, arg=None):
        if arg:
            self.write(arg)
        self.write('\n')


class STestResult:
    separator1 = '=' * 70
    separator2 = '-' * 70

    def __init__(self, verbose=False, stream=None):
        self.test_run = 0
        if not stream:
            stream = sys.stderr
        self.stream = _WriteLineDecorator(stream)
        self.verbose = verbose
        self.failures = []
        self.skipped = []

    def start_test_run(self):
        pass

    def stop_test_run(self):
        pass

    def start_test(self, test):
        self.test_run += 1
        if self.verbose:
            self.stream.write(test.name)
            self.stream.write('...')
            self.stream.flush()

    def stop_test(self, test):
        if self.verbose:
            self.stream.write_line()

    def add_success(self, test):
        if self.verbose:
            self.stream.write('ok')
        else:
            self.stream.write('.')
            self.stream.flush()

    def add_failure(self, test, reason):
        self.failures.append((test.name, reason))
        if self.verbose:
            self.stream.write('FAIL')
        else:
            self.stream.write('F')
            self.stream.flush()

    def add_skip(self, test, reason):
        self.skipped.append((test, reason))
        if self.verbose:
            self.stream.write(f'skipped {reason!r}')
        else:
            self.stream.write('S')
            self.stream.flush()

    def print_errors(self):
        for test_name, reason in self.failures:
            self.stream.write_line(self.separator1)
            self.stream.write_line("FAIL: %s" % test_name)
            self.stream.write_line(self.separator2)
            self.stream.write_line("%s" % reason)

    def print_summary(self, time_start, time_stop):
        time_taken = time_stop - time_start
        self.stream.write_line(f'ran {self.test_run} test(s) in {time_taken}s')
        infos = []
        if not self.is_successfull():
            self.stream.write('FAILED')
            failed = len(self.failures)
            infos.append(f'failures={failed}')
        else:
            self.stream.write('OK')
        if self.skipped:
            skipped = len(self.skipped)
            infos.append(f'skipped={skipped}')

        if infos:
            self.stream.write_line(' (%s)' % (', '.join(infos),))
        else:
            self.stream.write_line()

    def is_successfull(self):
        return len(self.failures) == 0
