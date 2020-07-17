import functools
import logging
import os
import pathlib
import re
import tarfile

from errors import SimicsError

REGEX_INCLUDE = re.compile(r'''#!include (?P<include>[\.\w/-]+)''')
REGEX_PACKAGE_FILENAME = re.compile(
    r'''simics-pkg-
    (?P<number>[\d]{4})-
    (?P<simics_version>[\.560]{3})\.
    (?P<version>[pre\d]+)-
    (?P<host>[linuxwin64]+)''',
    re.X,
)

REGEX_PACKAGE_VERSION = re.compile(
    r'''
    (?P<package_number>[\d]{4})[ ]+
    (?P<simics_version_major>[\d])\.
    (?P<simics_version_minor>[\d])\.
    (?P<package_version>[\dpre]+)''',
    re.X
)


class Package:
    ''' Legacy Simics package

        Responsibilities:
            - parse filename and `simics -v` output
            - provide Simics package details
            - handle Simics package naming conventions

        Test Strategy:
            - TBD
    '''
    def __init__(self, number, version, simics_version='6.0', path=None):
        self.number = number
        self.version = version
        self.simics_version = simics_version
        self.path = path if path else None

    @staticmethod
    def from_path(path: pathlib.Path):
        if not isinstance(path, pathlib.Path):
            path = pathlib.Path(path)
        match = REGEX_PACKAGE_FILENAME.search(path.name)
        if not match:
            raise SimicsError(f'failed to parse Simics package: {path}')
        match = match.groupdict()
        number = int(match.get('number'))
        version = match.get('version')
        simics_version = match.get('simics_version')

        package = Package(number, version, simics_version, path)

        return package

    @staticmethod
    def from_version(line):
        match = REGEX_PACKAGE_VERSION.search(line)
        if not match:
            return None
        match = match.groupdict()
        simics_version_major = match.get('simics_version_major')
        simics_version_minor = match.get('simics_version_minor')
        simics_version = f'{simics_version_major}.{simics_version_minor}'
        number = int(match.get('package_number'))
        version = match.get('package_version')
        package = Package(number, version, simics_version)

        return package

    def __str__(self):
        return f'{self.number}-{self.simics_version}.{self.version}'

    def __repr__(self):
        return f'Package({self.number}-{self.simics_version}.{self.version})'

    def __lt__(self, other):
        if self.number < other.number:
            return True
        if self.number == other.number:
            if self.version < other.version:
                return True
        return False


class PackageLight:
    ''' Light Package

        Responsibilities:
            - handle package naming conventions
            - pack files into package
            - unpack files from package

        Test Strategy:
            - TBD
    '''
    def __init__(self, name, path=None):
        self.name = name
        self.path = path
        self.path_full = None
        if self.path:
            if self.path.name != name:
                self.path_full = self.path / self.name
            else:
                self.path_full = self.path

    @staticmethod
    def create(splatform):
        path_packaging_raw = PackageLight.prepare_filelist_raw(splatform)
        path_package_list = PackageLight.prepare_filelist(splatform, path_packaging_raw)

        name_base = splatform.release_tree.get_version_next(splatform.platform, splatform.simics_version)
        name = f'{name_base}.tar.gz'
        path_package = splatform.path / 'packages' / name
        path_package.parent.mkdir(exist_ok=True, parents=True)
        release = tarfile.open(path_package, 'w')
        filenames = path_package_list.read_text().splitlines()
        map_path_filename = {
            splatform.path / x: x for x in filenames
        }
        for path, filename in map_path_filename.items():
            release.add(path, filename)
        release.close()

        package = PackageLight(name_base, path_package)
        return package

    def prepare_filelist_raw(self, splatform):
        map_path_content = {}
        map_path_includes = {}
        path_includes = [
            splatform.source_tree.path,
            splatform.source_tree.path / '_tools' / f'packaging_{splatform.simics_version}',
        ]
        def process_includes(path):
            content = path.read_text()
            map_path_content[path] = content
            includes = REGEX_INCLUDE.findall(content)

            for include in includes:
                for path_include in path_includes:
                    path_test = path_include / include
                    if path_test.exists():
                        process_includes(path_test)

        for package in splatform.packages:
            logging.debug('processing %d package', package)
            path_list = splatform.source_tree.get_package_list(package, splatform.simics_version)
            process_includes(path_list)

        content_raw = ''
        for path, content in map_path_content.items():
            content_raw = f'{content_raw}\n{content}'

        path_packaging_raw = splatform.path / 'linux64' / 'packaging' / f'{splatform.name}.list.raw'
        path_packaging_raw.parent.mkdir(exist_ok=True, parents=True)
        path_packaging_raw.write_text(content_raw)

        return path_packaging_raw

    def prepare_filelist(self, splatform, path_raw):
        lines = iter(path_raw.read_text().splitlines())
        entities = []
        for line in lines:
            entity = []
            while line:
                skip_line = False
                if line.startswith('#'):
                    skip_line = True
                if skip_line:
                    logging.debug('skipping: ', line)
                else:
                    logging.debug('adding: ', line)
                    entity.append(line.strip())
                line = next(lines, None)

            entities.append(entity)

        entities = list(filter(lambda x: x, entities))

        regex_dist = re.compile('''Dist: (?P<name>[\w-]+)''')
        regex_group = re.compile('''Group: (?P<name>[\w-]+)(\((?P<argument>[,\w]+)\))?''')
        regex_group_call = re.compile('''@(?P<name>[\w-]+)(\((?P<argument>[-, \w/]+)\))?''')

        dists = []
        def process_dist(entity):
            lines = iter(entity)
            lines_filtered = []
            processed_header = False
            for line in lines:
                while not processed_header:
                    if line.startswith('Release-notes:'):
                        line = line.lstrip('Release-notes:')
                        processed_header = True
                        break
                    line = next(lines, None)
                if line.startswith('#'):
                    continue
                if line.startswith('Provide-tokens:'):
                    continue
                if line.startswith('Doc-title:'):
                    continue
                lines_filtered.append(line)
            dists.append(lines_filtered)

        groups = {}
        def process_group(entity):
            lines = iter(entity)
            line = next(lines)
            match = regex_group.search(line)
            assert match
            match = match.groupdict()
            name = match.get('name')
            arguments = match.get('argument')
            if arguments:
                arguments = list(map(str.strip, arguments.split(',')))
            group_body = []
            while True:
                line = next(lines, None)
                if not line:
                    break
                if line.startswith('Require-tokens:'):
                    continue
                if line.startswith('Make:'):
                    continue
                if line.startswith('#'):
                    continue
                group_body.append(line)
            groups[name] = {
                'arguments': arguments,
                'body': group_body
            }

        for entity in entities:
            if regex_dist.search(entity[0]):
                process_dist(entity)
            elif regex_group.search(entity[0]):
                process_group(entity)
            else:
                print('unknown entity: ', entity[0])

        def process_line(line):
            match = regex_group_call.search(line)
            if not match:
                return [line]
            match = match.groupdict()
            name = match.get('name')
            # if name in ('tglh-punit', 'x86-cpu-generic'):
            #     import pdb; pdb.set_trace()
            arguments = match.get('argument', [])
            if arguments:
                arguments = list(map(str.strip, arguments.split(',')))
            if name not in groups:
                logging.warning('group %s not found, skipping line: %s', name, line)
                return []
            group = groups.get(name)
            group_arguments = group.get('arguments')
            group_body = group.get('body')
            if arguments:
                assert len(arguments) == len(group_arguments)
                lines_processed = []
                for line in group_body:
                    for argument, value in zip(group_arguments, arguments):
                        line = line.replace('{{{}}}'.format(argument), value)
                        # TODO: clarify why this syntax is used?
                        line = line.replace('{{{}:_}}'.format(argument), value)
                    lines_processed.append(line)
            else:
                lines_processed = group_body

            lines = []
            for line in lines_processed:
                lines.extend(process_line(line))
            return lines

        lines = []
        for dist in dists:
            for line in dist:
                lines.extend(process_line(line))

        filenames = []
        for line in lines:
            if '(+windows)' in line:
                continue
            if '(+linux)' in line:
                line = line.lstrip('(+linux)')
            line = line.replace('$(HOST)', 'linux64')
            line = line.replace('$(SO)', '.so')
            filenames.append(line.strip())
        filenames = sorted(filenames)

        path_package_list = splatform.path / 'linux64' / 'packaging' / f'{splatform.name}.list'
        path_package_list.write_text(os.linesep.join(filenames))
        return path_package_list

    def pack(self, splatform):
        logging.info('packing')
        path_packaging_raw = self.prepare_filelist_raw(splatform)
        path_package_list = self.prepare_filelist(splatform, path_packaging_raw)

        filenames = path_package_list.read_text().splitlines()
        filenames_extra = []
        for path_filename in (splatform.path / 'linux64' / 'lib').glob('**/*'):
            if not path_filename.is_file():
                continue
            if path_filename.suffix in ('.docu', '.eml', '.xml'):
                continue
            filename = str(path_filename.relative_to(splatform.path))
            if filename not in filenames:
                filenames_extra.append(filename)
        if filenames_extra:
            names = ', '.join(filenames_extra)
            logging.warning('packaging extra files: %s', names)
        filenames_all = filenames + filenames_extra
        map_path_filename = {}
        path_includes = [
            splatform.path,
            splatform.source_tree.path,
        ]

        filenames_missing = []
        for filename in filenames_all:
            found = False
            for path_include in path_includes:
                path_test = path_include / filename
                if path_test.exists():
                    map_path_filename[path_test] = filename
                    found = True
                    break
            if not found:
                filenames_missing.append(filename)

        if filenames_missing:
            message = ', '.join(filenames_missing)
            logging.warning('missing files: %s', message)

        for tmp in filenames_missing:
            if '{' in tmp and '}' in tmp:
                print(tmp)

        self.path_full.parent.mkdir(exist_ok=True, parents=True)
        release = tarfile.open(self.path_full, 'w')
        for path, filename in map_path_filename.items():
            release.add(path, filename)
        release.close()

    def unpack(self, path):
        logging.info('unpacking')
        archive = tarfile.open(self.path_full, 'r')
        archive.extractall(path)

    def __repr__(self):
        return f'Package[{self.name}]'
