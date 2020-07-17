from errors import SimicsError
from shell import run
from .stest_case import STestCase


class STestSuite:
    def __init__(self, tests, name='default'):
        self._tests = []
        self.name = name
        for test in tests:
            self.add_test(test)
        self.splatform = None
        if self._tests:
            self.splatform = self._tests[0].splatform

    def add_test(self, test):
        if not isinstance(test, STestCase):
            raise errors.SimicsError('%s should be instance of STestClass', test)
        self._tests.append(test)

    def run(self, result):
        for test in self:
            test(result)

    def __call__(self, *args, **kwds):
        return self.run(*args, **kwds)

    def __iter__(self):
        return iter(self._tests)

    def __repr__(self):
        return f'STestSuite[{self.name} ({len(self._tests)})]'
