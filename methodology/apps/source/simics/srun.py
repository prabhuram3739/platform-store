import logging

from shell import run


class SRun:
    def __init__(self, srunner, name):
        self.srunner = srunner
        self.name = str(name)
        self.path = srunner.splatform.path / name
        self.default = False
        if self.srunner.splatform.target_default:
            if self.srunner.splatform.target_default == self.name:
                self.default = True
        elif self.path.stem == self.srunner.splatform.platform:
            self.default = True

    def run(self):
        logging.info('running %s', self.name)
        command = f'{self.srunner.path_simics} {self.path}'
        return run(command, self.srunner.splatform.path)

    def __call__(self, *args, **kwargs):
        self.run(*args, **kwargs)

    def __str__(self):
        result = self.name
        if self.default:
            result = f'{result} *'
        return result

    def __repr__(self):
        return f'SRun[{self.name}]'
