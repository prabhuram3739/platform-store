import datetime
import logging
import platform

from errors import StorageError
from storage import Artifactory


class ReleaseTree:
    ''' Release tree of packages

        Responsibilities:
            - maintain tree of releases on Artifactory
            - upload packages
            - download packages
            - discover platform's releases
            - generate next available version
            - get latet released version

        Test Strategy:
            - TBD
    '''

    def __init__(self):
        self.url = 'https://ubit-artifactory-or.intel.com'
        self.repository = 'simics-local'
        self.path_releases = 'incoming/test/platforms'
        self.version_format = '%Y.ww%W.%w'
        self.artifactory = Artifactory(self.url, self.repository)

    def get_platform_names(self):
        info = self.artifactory.info(self.path_releases)
        names = []
        if info:
            children = info.get('children')
            folders = filter(lambda x: x.get('folder'), children)
            names = map(lambda x: x.get('uri').lstrip('/'), folders)
            names = sorted(names)
        return names

    def get_platform_versions(self, platform_name, simics_version):
        path_remote = f'{self.path_releases}/{platform_name}/{simics_version}'
        info = self.artifactory.info(path_remote)
        versions = []
        if info:
            children = info.get('children')
            folders = filter(lambda x: x.get('folder'), children)
            versions = map(lambda x: x.get('uri').lstrip('/'), folders)
            versions = sorted(versions)
        return versions

    def get_platform_properties(self, platform_name, simics_version, version):
        system = platform.system().lower()
        filename = self._get_filename(platform_name, simics_version, version, system)
        path_remote = f'{self.path_releases}/{platform_name}/{simics_version}/{version}/{system}/{filename}'
        properties = self.artifactory.properties_get(path_remote)

        return properties.get('properties')

    def get_version_next(self, name, simics_version):
        # platforms/<platform>/<simics_version>/<version>/<os>/<platform>-<simics_version>-<version>-<os>.tar
        system = platform.system().lower()
        path = f'{self.path_releases}/{name}/{simics_version}'
        today = datetime.date.today()
        version_base = today.strftime(self.version_format)
        versions = self.artifactory.info(path)
        if versions:
            children = versions.get('children')
            folders = filter(lambda x: x.get('folder'), children)
            names = map(lambda x: x.get('uri').lstrip('/'), folders)
            versions = map(Version, names)
            versions = sorted(versions)
            if versions:
                version_latest = str(versions[-1])
                version_latest_base, version_latest_id = version_latest.rsplit('.', 1)
                date_latest = datetime.datetime.strptime(version_latest_base, self.version_format)
                if date_latest.date() == today:
                    version_id = int(version_latest_id) + 1
                else:
                    version_id = 0
            else:
                version_id = 0
        else:
            version_id = 0
        version = f'{version_base}.{version_id}'
        return f'{name}-{simics_version}-{version}-{system}'

    def get_version_latest(self, name, simics_version):
        system = platform.system().lower()
        path = f'{self.path_releases}/{name}/{simics_version}'
        today = datetime.date.today()
        version_base = today.strftime(self.version_format)
        versions = self.artifactory.info(path)
        if not versions:
            logging.warning('no releases yet')
            return None
        children = versions.get('children')
        folders = filter(lambda x: x.get('folder'), children)
        names = map(lambda x: x.get('uri').lstrip('/'), folders)
        versions = sorted(names)
        versions = sorted(names, key=str.split('.'))
        if not versions:
            logging.warning('no releases yet')
            return None
        version_latest = versions[-1]
            
        return version_latest

    def get_release_latest(self, name, simics_version):
        system = platform.system().lower()
        path = f'{self.path_releases}/{name}/{simics_version}'
        today = datetime.date.today()
        version_base = today.strftime(self.version_format)
        versions = self.artifactory.info(path)
        if not versions:
            logging.warning('no releases yet')
            return None
        children = versions.get('children')
        folders = filter(lambda x: x.get('folder'), children)
        names = map(lambda x: x.get('uri').lstrip('/'), folders)
        versions = sorted(names, key=str.split('.'))
        if not versions:
            logging.warning('no releases yet')
            return None
        version = versions[-1]
        filename = self._get_filename(name, simics_version, version, system)
        return filename

    def release(self, splatform, path_local, revision, flow='manual'):
        # TODO: move to Package
        assert flow in ('auto', 'manual')
        name_full = self.get_version_next(splatform.platform, splatform.simics_version)
        name_full = f'{name_full}.tar.gz'
        name, simics_version, version, system = name_full.rstrip('.tar.gz').rsplit('-', 3)
        path_remote = f'{self.path_releases}/{name}/{simics_version}/{version}/{system}/{name_full}'
        try:
            info = self.artifactory.info(path_remote)
        except ArtifactoryError:
            info = None
        if info:
            url_download = info.get('downloadUri')
            logging.warning('release already exists, skipping...')
            return url_download
        
        url_download = self.artifactory.deploy_artifact(path_local, path_remote)

        properties = {
            'quality': 'not_tested',
            'revision': revision,
            'flow': flow,
        }
        self.artifactory.properties_set(path_remote, properties)

        return url_download

    def update(self, filename, revision, quality, passed, flow='manual'):
        # TODO: move to Package
        assert flow in ('auto', 'manual')
        name, simics_version, version, system = filename.rstrip('.tar.gz').split('-')
        path_remote = f'{self.path_releases}/{name}/{simics_version}/{version}/{system}'
        path_remote = f'{path_remote}/{filename}'
        try:
            properties = self.artifactory.properties_get(path_remote)
        except StorageError:
            properties = None
        if not properties:
            logging.warning('package is not released to Artifactory')
            return 1
        properties = properties.get('properties')
        if revision not in properties['revision']:
            logging.warning('revisions do not match, skipping...')
            return 1
        if flow not in properties['flow']:
            logging.warning('flow do not match, skipping...')
            return 1

        test_result = "passed" if passed else "failed"
        properties_new = {
            'flow': flow,
            'revision': revision,
            'quality': f'{quality} {test_result}',
        }

        self.artifactory.properties_set(path_remote, properties_new)

        return 0
    
    def populate(self, name, simics_version, version, path_local):
        logging.info('populating')
        system = platform.system().lower()
        filename = self._get_filename(name, simics_version, version, system)
        path_remote = f'{self.path_releases}/{name}/{simics_version}/{version}/{system}/{filename}'
        path_local = path_local / 'package.tar.gz'

        self.artifactory.download(path_remote, path_local)

        return path_local

    def _get_filename(self, name, simics_version, version, system):
        filename = f'{name}-{simics_version}-{version}-{system}.tar.gz'
        return filename


class Version:
    def __init__(self, version):
        year, work_week, day_week, version = version.split('.')
        self.year = int(year)
        self.work_week = work_week
        self.day_week = int(day_week)
        self.version = int(version)

    def __lt__(self, other):
        if self.year > other.year:
            return False
        elif self.work_week > other.work_week:
            return False
        elif self.day_week > other.day_week:
            return False
        elif self.version > other.version:
            return False
        return True

    def __str__(self):
        return f'{self.year}.{self.work_week}.{self.day_week}.{self.version}'

    def __repr__(self):
        return f'{self.year}.{self.work_week}.{self.day_week}.{self.version}'
