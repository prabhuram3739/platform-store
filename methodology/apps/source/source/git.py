import pathlib

from errors import SourceError
from shell import run

# TODO: annotate methods with factory/constructor definitions: name or documentation

class GitRepository:
    ''' Git repository wrapper

        Responsibilities:
            - provide subset of Git interactions

        Test Strategy:
            - TBD
    '''
    def __init__(self, path_local: pathlib.Path) -> None:
        self.path = path_local
        self.__finalize()

    @staticmethod
    def init(path_local):
        command = f'git init {path_local}'
        returncode = run(command)
        if returncode:
            raise SourceError(f'command failed: {command}')
        
        return GitRepository(path_local)

    def remote_add(self, path_remote, name='origin'):
        command = f'git remote add {name} {path_remote}'
        returncode = run(command, self.path)
        if returncode:
            raise SourceError(f'command failed: {command}')

    def remote(self):
        command = 'git remote'
        returncode, stdout, _ = run(command, self.path, capture_outputs=True)
        if returncode:
            raise SourceError(f'command failed: {command}')

        stdout = stdout.strip()
        return stdout.split(' ') if stdout else []

    def remote_get_url(self, remote):
        command = f'git remote get-url {remote}'
        returncode, stdout, _ = run(command, self.path, capture_outputs=True)
        if returncode:
            raise SourceError(f'command failed: {command}')
        
        return stdout.strip()

    def lfs_install(self):
        command = 'git lfs install'
        returncode = run(command, self.path)
        if returncode:
            raise SourceError(f'command failed: {command}')

    def fetch(self):
        command = 'git fetch'
        returncode = run(command, self.path)
        if returncode:
            raise SourceError(f'command failed: {command}')

    def checkout(self, revision='master'):
        command = f'git checkout {revision}'
        returncode = run(command, self.path)
        if returncode:
            raise SourceError(f'command failed: {command}')

    def diff(self, revision, args=None):
        command = f'git diff {revision}'
        if args:
            command = f'{command} {args}'
        returncode, stdout, _ = run(command, self.path, capture_outputs=True)
        if returncode:
            raise SourceError(f'command failed: {command}')
        
        return stdout.strip()

    def rev_parse(self, revision):
        command = f'git rev-parse {revision}'
        returncode, stdout, _ = run(command, self.path, capture_outputs=True)
        if returncode:
            raise SourceError(f'command failed: {command}')
        
        return stdout.strip()

    def __finalize(self):
        path_anchor = pathlib.Path(self.path.anchor)
        path = self.path
        found = False
        while True:
            if path == path_anchor:
                break
            path_git = path / '.git'
            if path_git.exists():
                found = True
                break
            path = path.parent
        if not found:
            raise SourceError(f'not a Git repository: {self.path}')

        self.path = path
        self.remotes = {}
        for remote in self.remote():
            url = self.remote_get_url(remote)
            self.remotes[remote] = url

    def __repr__(self):
        return f'GitRepository[{self.path}]'