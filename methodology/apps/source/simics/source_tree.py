import json
import logging
import pathlib

from .contour import Contour
from .project import Project
from .splatform import SPlatform
from errors import SourceError, ConfigError
from source import GitRepository

URL = 'ssh://git@gitlab.devtools.intel.com:29418/simics/vp/vp.git'
# TODO: Move to simics package
# TODO: checkout -> setup/prepare
# TODO: release 'dirty' by default, the only way to have a 'clean' release is to run build-release flow
# TODO: remove is_dirty
# TODO: SourceTree -> VPTree, GitRepository should handle all interaction with git

class SourceTree:
    ''' Virtual Platforms source tree

        Responsibilities:
            - prepare source tree by clonning from pre-defined URL and perform required setup
            - extract information from source tree:
                - list of platforms
                - search for requiseted platform
                - Simics package contour
                - Simics package list needed for packaging

        Test Strategy:
            - TBD
    '''

    def __init__(self, path_local):
        self.path = None
        self.repository = GitRepository(path_local)
        self.__finalize()

    @staticmethod
    def create(path_local, path_remote, revision='master'):
        repo = None
        try:
            repo = GitRepository(path_local)
        except SourceError:
            pass
        if repo:
            return SourceTree(repo.path)
            raise SourceError(f'repository already initilized at {repo.path}')
        repo = GitRepository.init(path_local)

        remote = path_remote if path_remote else URL
        if remote not in repo.remotes.values():
            repo.remote_add(remote)
        repo.lfs_install()
        repo.fetch()
        repo.checkout(revision)

        return SourceTree(path_local)

    def is_dirty(self):
        return True if self.repository.diff('HEAD') else False

    def get_revision(self):
        result = self.repository.rev_parse('HEAD')
        return result

    def get_platforms(self):
        path_platforms = self.path / '_tools' / 'misc' / 'simics_bundles'
        splatforms = list(filter(
            lambda x: x,
            map(
                lambda x: SPlatform.get_platform(self, x),
                path_platforms.iterdir()
            )
        ))

        return splatforms

    def get_platform(self, name, simics_version):
        platforms = self.get_platforms()
        splatform = None
        if name:
            name = f'{name}-{simics_version}'
            splatforms_filtered = list(filter(
                lambda x: x.name == name,
                platforms,
            ))
            if splatforms_filtered:
                splatform = splatforms_filtered[0]
        else:
            path = pathlib.Path.cwd()
            while True:
                if path == self.path:
                    break
                try:
                    project = Project.from_path(self, path)
                    splatform = project.splatform
                    break
                except ConfigError:
                    path = path.parent

        return splatform

    def get_contour(self):
        path_contour = self.path / '_tools' / 'packages-versions.json'
        contour = Contour(path_contour)
        return contour

    def get_package_list(self, package, simics_version='6.0'):
        path_packaging = self.path / '_tools' / f'packaging_{simics_version}' / f'{package}'
        if len(list(path_packaging.glob('*.list'))) != 1:
                logging.warning(
                    'path %s does not contain signle packages.list file',
                    path_packaging,
                )
        path_list = path_packaging / 'packages.list'
        return path_list

    def __finalize(self):
        if not self.repository.remotes:
            raise SourceError(f'Git repository does not have any remotes: {self.path}')
        if URL not in self.repository.remotes.values():
            raise SourceError(f'not a Virtual Platform repository: {self.path}')
        self.path = self.repository.path

    def __repr__(self):
        return f'SourceTree[{self.path}]'