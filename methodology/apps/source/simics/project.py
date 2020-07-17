import json
import logging
import os
import pathlib
import platform
import shutil

from jinja2 import Template

import errors
from errors import ConfigError
from shell import run

from .package import PackageLight

PATH_FLC_CONFIG = '.flc.config'
if platform.system() == 'Windows':
    PATH_KEYS = pathlib.Path('//pdxcv20a-cifs.pdx.intel.com/ssg_stc_simics_users/simics_lab/keys')
else:
    PATH_KEYS = pathlib.Path('/nfs/site/disks/ssg_stc_simics_users/simics_lab/keys')
PATH_WORKLOADS = pathlib.Path('/p/simics/workloads')


class LightProject:
    def __init__(self, path, simics_version, base_version):
        self.path = path
        path_simics = pathlib.Path('/nfs/site/disks/ssg_stc_simics_base-packages-release/simics-6')
        path_base = path_simics / f'simics-{simics_version}.{base_version}'

        path_project_setup = path_base / 'bin' / 'project-setup'
        command = f'{path_project_setup} {self.path}'
        returncode = run(command)
        if returncode:
            logging.error('failed to create Simics project')

    def launch(self, target):
        path_target = self.path / target
        if not path_target.exists():
            raise errors.SimicsError('target not found')
        path_simics = self.path / 'simics'
        command = f'{path_simics} {path_target}'
        return run(command, self.path)

    def unpack(self):
        path_package = self.path / 'packages' / 'package.tar.gz'
        package = PackageLight('package.tar.gz', path_package)
        package.unpack(self.path)


class Project:
    ''' Simics project

        Responsibilities:
            - create Simics project using contour of Simics packages and generate files reuqired for build, test and run
            - build binaries

        Test Strategy:
            - TBD
    '''
    def __init__(self, splatform):
        self.splatform = splatform
        self.path = self.splatform.path
        self.path_config = self.splatform.path / PATH_FLC_CONFIG
        self.__finalize()

    @staticmethod
    def from_path(source_tree, path):
        path_config = path / PATH_FLC_CONFIG
        if not path_config.exists():
            raise ConfigError(f'not a Simics project: {path}')
        data = json.loads(path_config.read_text())
        name = data.get('name')
        simics_version = data.get('simics version')

        splatform = source_tree.get_platform(name, simics_version)
        project = Project(splatform)

        return project

    @staticmethod
    def create(splatform):
        logging.info('creating Simics project')

        generate_global_config(splatform)
        path_package_list = generate_package_list(splatform)

        package_number_base = 1000
        contour = splatform.source_tree.get_contour()
        package = contour.get_package(package_number_base, splatform.simics_version)

        path_setup = package.path / 'bin' / 'project-setup'
        if platform.system() == 'Windows':
            path_setup = path_setup.with_suffix('.bat')
        
        if not path_setup.exists():
            logging.error("path '%s' does not exist", path_setup)
            for parent in path_setup.parents:
                if parent.exists():
                    logging.debug("path '%s' exists", parent)
                else:
                    logging.debug("path '%s' does not exists", parent)
            raise ProjectError('cannot find Simics installation')
        
        cmd = f'{path_setup} --ignore-existing-files --force --package-list {path_package_list}'
        run(cmd, splatform.path)

        path_config = splatform.path / PATH_FLC_CONFIG
        if path_config.exists():
            logging.warning('overriding existing config: %s', path_config)
        data = {
            'name': splatform.platform,
            'simics version': splatform.simics_version
        }
        path_config.write_text(json.dumps(data, indent=4))

        project = Project(splatform)

        return project

    def build_binaries(self):
        logging.info('building binaries')
        if platform.system() != 'Windows':
            os.environ['SCAN_DEPENDENCIES'] = 'yes'
        else:
            os.environ['SCAN_DEPENDENCIES'] = 'no'

        self.__update_environment()

        # names = set()
        # if setup_build:
        #     for script in bundle.setup_build:
        #         names.add(script)
        # if setup_bronze:
        #     for script in bundle.setup_bronze:
        #         names.add(script)
        # if setup_all_tests:
        #     for script in bundle.setup_all_tests:
        #         names.add(script)

        # sys.path.append(os.getcwd())
        # for name in names:
        #     logging.info('importing: %s', name)
        #     importlib.import_module(script.replace('.py', ''))

        number_usable_cpus = len(os.sched_getaffinity(0))
        # TODO: replace pkg-prep step
        # targets_prep = map(lambda x: f'pkg-prep-{x}', self.splatform.packages)
        # targets_prep = ' '.join(targets_prep)
        # command = f'gmake {targets_prep} -k -j{number_usable_cpus}'
        # result = run(command, self.splatform.path)
        # if result:
        #     logging.warning('ignoring failure of pkg-prep step as not all platforms implement it. Should be deprecated')
        # try doing common things ignore if they do not exists
        targets = [
            'common-images',
            'common-prepare',
        ]
        for target in targets:
            command = f'gmake {target}'
            logging.info('trying common target: %s', target)
            result = run(command, self.splatform.path)
            if result:
                logging.warning('common target %s failed, ignoring...', target)

        targets_build = map(lambda x: f'pkg-{x}', self.splatform.packages)
        targets_build = ' '.join(targets_build)

        command = f'gmake {targets_build} -j{number_usable_cpus}'
        result = run(command, self.splatform.path)
        return result

    def prepare_for_tests(self):
        self.__update_environment()

        path_source = self.splatform.source_tree.path / '_tools' / 'test_utils' / 'to_copy'
        path_destination = self.splatform.path / 'test' / '_common'
        path_destination.mkdir(exist_ok=True, parents=True)
        shutil.copy(path_source / 'TEST.simics', path_destination)
        shutil.copy(path_source / 'runtest.py', path_destination.parent)

        # build_targets = map(lambda x: f'pkg-prep-{x}', self.splatform.packages)
        # targets = ' '.join(build_targets)
        # number_usable_cpus = len(os.sched_getaffinity(0))
        # command = f'gmake {targets} -k -j{number_usable_cpus}'
        # result = run(command, self.splatform.path)
        # if result:
        #     logging.warning('ignoring failure of pkg-prep step as not all platforms implement it. Should be deprecated')

        return 0

    def __finalize(self):
        if not self.path_config.exists():
            raise ConfigError('project is not initialized')

        data = json.loads(self.path_config.read_text())
        name = data.get('name')
        simics_version = data.get('simics version')
        platform_name = f'{name}-{simics_version}'
        if platform_name != self.splatform.name:
            raise ConfigError(
                f'project already initialized for {platform_name}, do clean first'
            )
        self.path_simics = self.path / 'simics'
        if not self.path_simics.exists():
            raise errors.Simics('cannot find Simics executable')
        self.path_test_runner = self.path / 'bin' / 'test-runner'
        if not self.path_test_runner.exists():
            raise errors.Simics('cannot find Simics test-runner executable')

    def __update_environment(self):
        if self.splatform.internal:
            os.environ['INTERNAL_RELEASE'] = 'yes'
            os.environ['BUILD_CONFIDENTIALITY'] = '99'
        else:
            os.environ['INTERNAL_RELEASE'] = 'no'
            os.environ['BUILD_CONFIDENTIALITY'] = '2'

    def __repr__(self):
        return f'Project[{self.path_config.parent}]'


def generate_global_config(splatform):
    filename = 'config-global.mk'
    path_config_mk = splatform.path / filename
    logging.debug('generating %s', path_config_mk)
    path_root = pathlib.Path(__file__) / '..' / '..' / '..'
    path_templates = path_root / 'resources' / 'templates'
    filename = pathlib.Path(f'{filename}.ninja')
    path_config_global_template = path_templates / 'devtools' / filename
    path_tests = [
        path_config_global_template,
        pathlib.Path(__file__).parent / '..' / filename,
        pathlib.Path(__file__).parent / '..' / '..' / filename,
    ]
    for path in path_tests:
        if path.exists():
            path_config_global_template = path
            break
    path_config_global_template = path_config_global_template.resolve()
    template_config_global_mk = Template(path_config_global_template.read_text())
    data_config_global_mk = template_config_global_mk.render(
        VP_ROOT=str(splatform.source_tree.path),
        WORKLOADS=str(PATH_WORKLOADS),
        HPM='hpm-linux',
    )
    path_config_mk.write_text(data_config_global_mk)


def generate_package_list(splatform):
    name_package_list = '.package-list.local'
    path_package_list = splatform.path / name_package_list
    logging.debug('generating %s', path_package_list)
    contour = splatform.source_tree.get_contour()
    packages = contour.get_packages(splatform.simics_version)
    path_packages = list(map(lambda x: x.path, packages))
    path_package_list.write_text('\n'.join(map(str, path_packages)))

    return path_package_list
