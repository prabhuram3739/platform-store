class BaseError(Exception):
    pass

class ConfigError(BaseError):
    pass


class ContainerError(BaseError):
    pass

class EnvironmentError(BaseError):
    pass


class FalconError(BaseError):
    pass


class ShellError(BaseError):
    pass


class SimicsError(BaseError):
    pass


class SourceError(BaseError):
    pass


class StorageError(BaseError):
    pass


class CreateSessionError(BaseError):
    pass


class DeleteSessionError(BaseError):
    pass

class HarborError(BaseError):
    pass

class CtorError(BaseError):
    pass

class LaunchError(BaseError):
    pass


