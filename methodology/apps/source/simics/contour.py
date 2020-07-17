import json
import logging
import pathlib
import platform

from errors import ConfigError
from .package import Package


class Contour:
    ''' Contour of Simics Packages

        Responsibilities:
            - parse JSON file with all Simics packages for the contour type:
                - simics-base
                - iss
                - nightly
                - nightly-iss
            - provide a list of packages defined in contour to setup Simics project

        Test Strategy:
            - TBD
    '''
    def __init__(self, path_config):
        self.path = path_config
        if not self.path.exists():
            raise ConfigError(f'conout config does not exist: {self.path}')
        data = json.loads(self.path.read_text())
        self._defaults = data.pop('defaults')
        self._data = data
        self.host_type = 'win64' if platform.system() == 'Windows' else 'linux64'
        self._contour = {}

    def get_packages(self, simics_version='6.0', contour_type='simics-base'):
        if simics_version in  self._contour:
            if contour_type in self._contour[simics_version][contour_type]:
                packages = self._contour[simics_version][contour_type]
                return list(packages.values())
        
        packages = self._get_packages(simics_version, contour_type)

        return list(packages.values())

    def get_package(self, number, simics_version='6.0', contour_type='simics-base'):
        if simics_version in  self._contour:
            if contour_type in self._contour[simics_version]:
                if number in self._contour[simics_version][contour_type]:
                    return self._contour[simics_version][contour_type][number]
        
        self._get_packages(simics_version, contour_type)

        if simics_version in  self._contour:
            if contour_type in self._contour[simics_version]:
                if number in self._contour[simics_version][contour_type]:
                    return self._contour[simics_version][contour_type][number]

        raise ConfigError(f'contour does not have info about package {number}')

    def _get_packages(self, simics_version, contour_type):
        packages = {}
        version_major = simics_version.split('.')[0]
        path_install_default, _ = self._get_path_install(self._defaults, contour_type, version_major)
        for package_number, package_data in self._data.items():
            package_number = int(package_number)
            if contour_type not in package_data:
                logging.debug(
                    'package %s does not have version for %s',
                    package_number,
                    contour_type
                )
                continue
            if self.host_type not in package_data['hosts']:
                logging.debug(
                    'package %s does not have version for %s',
                    package_number,
                    self.host_type,
                )
                continue
            if version_major not in package_data.get('versions'):
                logging.debug(
                    'package %s does not have Simics %s version',
                    package_number,
                    version_major,
                )
                continue
            if 'iss' in package_data:
                logging.debug("package %s has 'iss' in version data", package_number)
                continue

            path, version = self._get_path_install(package_data, contour_type, version_major, path_install_default)
            simics_version_tmp, version = version.rsplit('.', 1)
            assert simics_version_tmp == simics_version
            package = Package(package_number, version, simics_version, path)

            logging.debug('package %s', package)
            packages[package.number] = package
        
        self._contour[simics_version] = {
            contour_type: packages
        }

        return packages


    def _get_path_install(self, data, contour_type, version_major, default=None):
        data_install = data.get(contour_type)

        if data_install:
            path_install = pathlib.Path(
                data_install.get('install_dir').get(self.host_type).format(
                    SIMICS_MAJOR_VERSION=version_major
                )
            )
        elif default:
            path_install = default
        else:
            path_install = None

        if 'hosts' in data:
            name = data.get('hosts').get(self.host_type)
            if isinstance(name, dict):
                name = name.get(version_major)
        else:
            name = None
        if 'versions' in data:
            version = data.get('versions').get(version_major)
        else:
            version = None

        if name and version:
            name_full = f'{name}{version}'
        else:
            name_full = ''

        return path_install / name_full, version

    def __repr__(self):
        return f'Contour<{self.path}>'
