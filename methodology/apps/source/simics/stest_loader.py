import re

import errors
from shell import run
from .stest_case import STestCase
from .stest_suite import STestSuite

REGEX_TAG = re.compile('''(?P<tag>[\w]+)''')


class STestLoader:
    def __init__(self, splatform):
        self.splatform = splatform

    def load_by_names(self, names, name='names'):
        tests = self.discover()
        tests = filter(lambda x: x.name in names, tests)
        stest_suite = STestSuite(tests, name)

        return [stest_suite]

    def load_by_tags(self, tags):
        tags = set(tags)
        tests = self.discover()
        tests = filter(lambda x: not set(x.tags).isdisjoint(tags), tests)
        stest_suite = STestSuite(tests, 'tags')

        return [stest_suite]

    def load_by_quality(self, quality):
        if quality == 'bronze':
            tags_groups = self.splatform.tests_bronze
        elif quality == 'silver':
            tags_groups = self.splatform.tests_silver
        else:
            raise errors.SimicsError(f'unsupported quality type {quality}')
        if not tags_groups:
            stest_suite = STestSuite([], f'{quality}-default')
            return [stest_suite]

        tests = self.discover()
        stest_suites = []
        for name_group, tags_equation in tags_groups.items():
            if not name_group:
                name_group = 'default'
            name_group = f'{quality}-{name_group}'
            tags_equation = tags_equation.replace('- off', '')
            tags = REGEX_TAG.findall(tags_equation)
            for tag in tags:
                tests_tagged = list(filter(lambda x: tag in x.tags, tests))
                names = set(map(
                    lambda x: x.name,
                    tests_tagged
                ))
                exec(f'{tag} = names')
            names = eval(tags_equation)
            stest_suite = self.load_by_names(names, name_group)
            stest_suites.extend(stest_suite)

        return stest_suites

    def load_all(self):
        tests = self.discover()
        stest_suite = STestSuite(tests)

        return [stest_suite]

    def discover(self):
        command = f'{self.splatform.project.path_test_runner} --list --project-only'
        returncode, stdout, stderr = run(command, self.splatform.path, capture_outputs=True)
        data = stdout.strip().replace('No tests', '')
        names = set(data.split('\n'))
        names = sorted(names)
        tests = list(map(lambda x: STestCase(self.splatform, x), names))
        
        return tests
