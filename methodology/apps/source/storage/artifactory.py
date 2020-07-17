import json
import logging
import pathlib
from urllib.parse import urlparse
from urllib import parse

import requests

from errors import StorageError


class Artifactory:
    ''' Artifactory wrapper

        Responsibilities:
            - provide a subset Artifactory interactions

        Test Strategy:
            - TBD
    '''
    def __init__(self, server, repository, auth=None):
        self.auth = auth
        self.auth = None
        self.server = server.rstrip('/')
        self.repository = repository.strip().strip('/')
        self.session = requests.Session()
        self.session.auth = self.auth

    def info(self, path_remote):
        url = f'{self.server}/artifactory/api/storage/{self.repository}/{path_remote}'
        logging.debug(f'info {url}')
        response = self.session.get(url)

        if response.status_code in (requests.codes.not_found,):
            return None
        elif response.status_code not in (requests.codes.ok, ):
            raise StorageError('cannot fetch info')

        return response.json()

    def deploy_artifact(self, path_local, path_remote):
        path_local = pathlib.Path(path_local).resolve()
        if not path_local.exists():
            raise StorageError(
                f'path does not exists: {path_local}'
            )

        if 'local' not in self.repository:
            raise StorageError(
                f'cannot deploy to non-local repository: {self.repository}'
            )

        url = f'{self.server}/artifactory/{self.repository}/{path_remote}'
        logging.debug(f'deploying artifact {path_local} to {url}')

        size_chunk = 1024
        it = FileHelper(path_local, size_chunk=size_chunk)
        data = IterableAdapter(it)
        # data = path_local.read_bytes()
        response = self.session.put(url, data=data)

        if response.status_code != requests.codes.created:
            raise StorageError(f'deploy failed: {response.status_code} {response.text}')
        
        data = response.json()
        url_download = data.get('downloadUri')

        return url_download

    def download(self, path_remote, path_local):
        path_local = pathlib.Path(path_local)
        url = f'{self.server}/artifactory/{self.repository}/{path_remote}'
        response = self.session.get(url)

        path_local.write_bytes(response.content)

    def properties_get(self, path_remote, properties=None):
        url = f'{self.server}/artifactory/api/storage/{self.repository}/{path_remote}?properties'
        if properties:
            properties = ','.join(properties)
            url = f'{url}={properties}'

        logging.debug(f'info {url}')
        response = self.session.get(url)

        if response.status_code not in (requests.codes.ok, ):
            raise StorageError('cannot get properties')
        
        return response.json()

    def properties_set(self, path_remote, properties):
        url = f'{self.server}/artifactory/api/storage/{self.repository}/{path_remote}?properties'
        properties = {x: parse.quote(y) for x, y in properties.items()}
        properties = [f'{key}={value}' for key, value in properties.items()]
        properties = ';'.join(properties)
        url = f'{url}={properties}'
        logging.debug(f'setting {url}')

        response = self.session.put(url)

        if response.status_code not in (requests.codes.no_content, ):
            raise StorageError('cannot set properties')

    def properties_update(self, path_remote, properties):
        url = f'{self.server}/artifactory/api/metadata/{self.repository}/{path_remote}'
        logging.debug(f'info {url}')

        data = {
            'props': properties,
        }
        data = json.dumps(data)
        response = self.session.patch(url, json=data)

        if response.status_code not in (requests.codes.ok, ):
            raise StorageError('cannot update properties')
        
        return response.json()

    def properties_delete(self, path_remote, properties):
        url = f'{self.server}/artifactory/api/storage/{self.repository}/{path_remote}?properties'
        properties = ','.join(properties)
        url = f'{url}={properties}'
        logging.debug(f'info {url}')

        response = self.session.delete(url)

        if response.status_code not in (requests.codes.ok, ):
            raise StorageError('cannot fetch info')
        
        return response.json()

    def _repr__(self):
        return f'Artifactory({self.server}/atifactory/{self.repository}'


class IterableAdapter():
    def __init__(self, iterable):
        self.iterator = iter(iterable)
        self.length = len(iterable)

    def read(self, blk_size=None):
        return next(self.iterator, b'')

    def __len__(self):
        return self.length


class FileHelper():
    def __init__(self, path, size_chunk=1024):
        self.path = path
        self.size_chunk = size_chunk
        self.size_total = path.stat().st_size
        self.size_read = 0

    def __iter__(self):
        with self.path.open(mode='rb') as file:
            # progress_bar = get_progressbar('uploading', self.size_total)
            while True:
                data = file.read(self.size_chunk)
                if not data:
                    break
                self.size_read += len(data)
                # progress_bar.update(self.size_read)
                yield data
            # progress_bar.finish()

    def __len__(self):
        return self.size_total
