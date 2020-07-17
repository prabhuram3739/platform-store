import json
import logging
import os
import shutil
import sys

import errors
from errors import ConfigError
from errors import SimicsError
from shell import run
from .project import Project
from .package import PackageLight as Package
from .release_tree import ReleaseTree
from .stest_loader import STestLoader
from .stest_suite import STestSuite
from .stest_runner import STestRunner
from .srunner import SRunner
from .versions import SIMICS_VERSIONS


class SPlatform:
    ''' Simics platform

        Responsibilities:
            - provides high level methods for build, populate, release commands
            - maintians Simics project, release tree for required platform

        Test Strategy:
            - TBD
    '''
    def __init__(self, source_tree, path_config):
        self.path = None
        self.path_config = path_config
        self.source_tree = source_tree
        self.release_tree = ReleaseTree()
        self.project = None
        self.path_packages = None
        self.__finalize()

    @staticmethod
    def get_platform(source_tree, path_config):
        try:
            splatform = SPlatform(source_tree, path_config)
        except SimicsError as error:
            logging.warning(error)
            splatform = None
        
        return splatform

    def build(self):
        if not self.project:
            self.project = Project.create(self)
        if self.project.build_binaries():
            raise errors.SimicsError('build failed')
        name = 'package.tar.gz'
        package = Package(name, self.path_build_package / name)
        package.pack(self)
        logging.info('generated package: %s', package.path_full)

    def populate(self, version=None):
        if not self.project:
            self.project = Project.create(self)
        if not version:
            version = self.release_tree.get_version_latest(self.platform, self.simics_version)
        if not version:
            raise SimicsError('nothing released yet')
        self.path_build_package.mkdir(exist_ok=True, parents=True)
        path_local = self.release_tree.populate(self.platform, self.simics_version, version, self.path_build_package)

        package = Package(path_local.name, path_local)
        package.unpack(self.path)

        return 0

    def release(self, flow='manual'):
        name = 'package.tar.gz'
        path_package = self.path_build_package / name
        url = self.release_tree.release(self, path_package, self.source_tree.get_revision(), flow=flow)
        return url

        urls = []
        for package in self.packages_built:
            url = self.release_tree.release(self, package.path_full, self.source_tree.get_revision(), flow=flow)
            urls.append(url)

        return urls

    def release_update(self, passed, quality='bronze', flow='manual'):
        filename = self.release_tree.get_release_latest(self.platform, self.simics_version)
        result = self.release_tree.update(filename, self.source_tree.get_revision(), quality, passed, flow=flow)

        return result

    def get_stest_suite_old(self, names=None, tags=None, quality=None):
        self.project.prepare_for_tests()

        stest_suite = STestSuite(self, names=names, tags=tags, quality=quality)
        return stest_suite

    def get_stest_suite(self, names=None, tags=None, quality=None):
        self.project.prepare_for_tests()
        loader = STestLoader(self)
        if names:
            stest_suites = loader.load_by_names(names)
        elif tags:
            stest_suites = loader.load_by_tags(tags)
        elif quality:
            stest_suites = loader.load_by_quality(quality)
        else:
            stest_suites = loader.load_all()

        return stest_suites

    def get_srunner(self, target=None):
        srunner = SRunner(self, target)

        return srunner

    def get_raw_data(self):
        return self._data

    def test(self, quality='bronze'):
        self.project.prepare_for_tests()
        stest_suite = self.get_stest_suite(quality=quality)
        stest_runner = STestRunner(verbose=True)
        result = stest_runner.run(stest_suite)

        return result

        if self.dependencies:
            message = ', '.join(self.dependencies)
            logging.warning('%s depneds on %s binaries and this functionality is not supported', self, message)

        if self.prepare_tests_all:
            logging.info('prapare all tests: %s', self.prepare_tests_all)

        if self.prepare_tests_bronze:
            logging.info('prapare bronze tests: %s', self.prepare_tests_bronze)

        if qualification == 'bronze':
            tests = self.tests_bronze
        elif qualification == 'silver':
            tests = self.tests_silver
        else:
            tests = {}

        for name, tags_string in tests.items():
            version = self.simics_version.replace('.', '')
            tags_default = ['nolnx', f'nolnx{version}', f'no{version}', 'nighlty', 'arc_nightly']
            logging.warning('magic is happening: adding default tags: %s', ', '.join(tags_default))
            tags_default_string = ' - '.join(tags_default)
            tags_string_tmp = f'(({tags_string}) - {tags_default_string})'
            # tags_string = f'(({tags_string}) - nolnx - nolnx{version} - no{version} - nightly - arc_nightly)'

            path_test_runner = self.path / 'bin' / 'test-runner'
            if not path_test_runner.exists():
                raise SimicsError('path %s does not exists', path_test_runner)

            tags = tags_string.replace('(', '').replace(')', '').replace('(', '').replace('-', '')
            tags = map(lambda x: x.strip(), tags.split())
            tags = list(set(filter(lambda x: x, tags)))

            map_tag_tests = {}
            for tag in tags:
                command = f'{path_test_runner} --list --project-only --tag={tag}'
                returncode, stdout, stderr = run(command, self.path, capture_outputs=True)
                data = stdout.strip().replace('No tests', '')
                map_tag_tests[tag] = set(data.split('\n'))

            # TODO: switch to something cleaner
            for x, y in map_tag_tests.items():
                exec(f'{x} = {y}')
            path_tests = list(eval(tags_string))
            path_tests = map(lambda x: self.path / x, path_tests)
            stests = list(map(STest, path_tests))

            path_source = self.source_tree.path / '_tools' / 'test_utils' / 'to_copy'
            path_destination = self.path / 'test' / '_common'
            path_destination.mkdir(exist_ok=True, parents=True)
            shutil.copy(path_source / 'TEST.simics', path_destination)
            shutil.copy(path_source / 'runtest.py', path_destination.parent)

            for stest in stests:
                stest.run(self.path, path_test_runner)
            stests_success = list(filter(lambda x: x.result == 'success', stests))
            stests_failure = list(filter(lambda x: x.result != 'success', stests))
            print(f'Test Summary: passed {len(stests_success)} out of {len(stests)}')
            if stests_success:
                message = '\n'.join(map(str, stests_success))
                print(f'Passed:\n{message}')
            if stests_failure:
                message = '\n'.join(map(str, stests_failure))
                print(f'Failed:\n{message}')

    def __finalize(self):
        if self.path_config.suffix not in ('.json',):
            raise SimicsError(f'not a platform file: {self.path_config}')
        self.name = self.path_config.stem
        self.platform, self.simics_version = self.name.rsplit('-', 1)
        if self.simics_version not in SIMICS_VERSIONS:
            raise SimicsError(f'cannot parse filename {self.path_config}')
        self.simics_version_major, self.simics_version_minor = self.simics_version.split('.')
        try:
            self._data = json.loads(self.path_config.read_text())
        except json.decoder.JSONDecodeError:
            raise SimicsError(f'malformed platform file: {self.path_config}')
        
        self.path = self.source_tree.path / self._data.get('subdir')
        try:
            self.project = Project(self)
        except ConfigError:
            pass
        self.enabled = not self._data.get('disable_checkout', False)
        self.internal = self._data.get('internal', True)
        self.owners = list(map(lambda x: x.strip(), self._data.get('owners', None).split(',')))
        packages_bronze = self._data['bronze_pkgs'].split(',')
        packages_bronze = filter(lambda x: x, packages_bronze)
        packages_bronze = map(int, packages_bronze)
        self.packages = list(packages_bronze)

        self.path_build_package = self.path / 'packages'

        self.dependencies = []
        if self._data.get('last_good'):
            self.dependencies.extend(self._data.get('last_good').split(','))

        self.prepare_build = self._data.get('setup_build', None)
        self.prepare_tests_all = self._data.get('setup_all_tests', None)
        self.prepare_tests_bronze = self._data.get('setup_bronze', None)
        self.prepare_tests_silver = None

        self.tests_bronze = self._data.get('bronze_tests', {})
        self.tests_silver = self._data.get('silver_tests', {})
        self.target_default = self._data.get('default_target', None)

    def __repr__(self):
        return f'SPlatform[{self.name}]'
