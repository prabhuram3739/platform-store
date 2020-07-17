import logging
import re

from shell import run
from .stest_result import STestResult

REGEX_PYTHON3 = re.compile('''py3: (?P<python3>[true|false])''')
REGEX_TAGS = re.compile('''tags: (?P<tags>[\w ]+)''')
REGEX_TEST = re.compile('''suite\.add_simics_test\("(?P<filename>[-\w\.]+)", (?P<timeout>[\d]+)\)''')
REGEX_TIMEOUT = re.compile('''timeout: (?P<timeout>[\d]+)''')


class STestCase:
    def __init__(self, splatform, name):
        self.name = name
        self.splatform = splatform
        self.path = self.splatform.path / self.name
        self.path_test_runner = self.splatform.project.path_test_runner
        self.__parse_suiteinfo()

    def run(self, result=None):
        if result is None:
            result = self.get_default_result()

        if self.disabled:
            result.start_test(self)
            result.add_skip(self, self.disable_reason)
            result.stop_test(self)
            return

        result.start_test(self)
        try:
            command = f'{self.path_test_runner} --project-only -v --logdir {self.path} --suite {self.name}'
            returncode, stdout, stderr = run(command, None, capture_outputs=True)
            if returncode:
                path_log = self.path / 'test.log'
                if path_log.exists():
                    reason = path_log.read_text()
                else:
                    reason = 'TBD'
                result.add_failure(self, reason)
            else:
                result.add_success(self)
        finally:
            result.stop_test(self)

    def get_default_result(self):
        return STestResult()

    def __call__(self, *args, **kwds):
        return self.run(*args, **kwds)

    def __parse_suiteinfo(self):
        path_suiteinfo = self.path / 'SUITEINFO'
        suiteinfo = path_suiteinfo.read_text()
        match = REGEX_TAGS.search(suiteinfo)
        if match:
            self.tags = set(match.groupdict().get('tags').split())
        else:
            self.tags = set()
        match = REGEX_TIMEOUT.search(suiteinfo)
        if match:
            self.timeout = int(match.groupdict().get('timeout'))
        else:
            self.timeout = 0
        match = REGEX_PYTHON3.search(suiteinfo)
        if match:
            self.python3 = bool(match.groupdict().get('python3'))
        else:
            self.python3 = False
        if not self.python3:
            logging.debug('test %s does not support Python3', self.path)

        self.disabled = False
        self.disable_reason = None
        if 'off' in self.tags:
            self.disabled = True
            self.disable_reason = 'disabled'
        elif 'skipfailure' in self.tags:
            self.disabled = True
            self.disable_reason = 'ignoring skip failure'
        elif 'flaky' in self.tags:
            self.disabled = True
            self.disable_reason = 'ignoring flaky tag'

    def __lt__(self, other):
        return self.name < other.name

    def __str__(self):
        name = self.name
        if self.tags:
            tags = ', '.join(self.tags)
            name = f'{name} tags={tags}'
        else:
            name = f'{name} no tags'
        return name

    def __repr__(self):
        tags = ', '.join(self.tags)
        return f'Test[{self.name}, tags={tags}]'


# class ModuleSTestCase(STestCase):
#     def __init__(self, splatform, name):
#         super(ModuleSTestCase, self).__init__(splatform, name)
#         self.__parse_stests()

#     def __parse_stests(self):
#         self.filenames_module = []
#         for path in self.path.glob('s-*.py'):
#             self.filenames_module.append(path)


# class ProjectSTestCase(STestCase):
#     def __init__(self, splatform, name):
#         super(ProjectSTestCase, self).__init__(splatform, name)
#         self.__parse_tests()

#     def __parse_tests(self):
#         self.filenames = []
#         self.timeout_accumulated = 0
#         path_tests = self.path / 'tests.py'
#         if not path_tests.exists():
#             return
#         self.is_test_project = True
#         tests = path_tests.read_text()
#         matches = REGEX_TEST.findall(tests)

#         if matches:
#             for filename, timeout in matches:
#                 self.filenames.append(filename)
#                 self.timeout_accumulated += int(timeout)
