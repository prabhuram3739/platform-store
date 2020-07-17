import logging

from errors import SimicsError
from .srun import SRun


class SRunner:
    def __init__(self, splatform, target=None):
        self.splatform = splatform
        self.target = target
        self.path_simics = self.splatform.path / 'simics'
        if not self.path_simics.exists():
            raise SimicsError('Simic path does not exist %s', self.path_simics)
        self.sruns = []
        self.__finalize()

    def run(self):
        sruns = list(filter(lambda x: x.default, self.sruns))
        if not sruns:
            sruns = self.sruns
        return sruns[0].run()

    def __finalize(self):
        paths_test = [
            self.splatform.path / 'targets' / self.splatform.platform,
            self.splatform.path / 'targets' / f'x86-{self.splatform.platform}',
            self.splatform.path / 'targets' / self.splatform.path.stem,
            self.splatform.path / 'targets' / f'x86-{self.splatform.path.stem}',
        ]
        paths_test = list(filter(lambda x: x.exists(), paths_test))
        # TODO: add normal comparison for sets
        sruns = {}
        if not paths_test:
            logging.warning(
                'could not find targets path, checked: targets/%s and targets/%s',
                self.splatform.platform,
                self.splatform.path.stem
            )
        else:
            for path_test in paths_test:
                for path_target in path_test.glob('*.simics'):
                    name = path_target.relative_to(self.splatform.path)
                    srun = SRun(self, name)
                    sruns[srun.name] = srun
        if self.splatform.target_default:
            srun = SRun(self, self.splatform.target_default)
            sruns[srun.name] = srun

        self.sruns = list(sruns.values())

        if self.target:
            self.sruns = list(filter(lambda x: x.name == self.target, self.sruns))

    def __repr__(self):
        return f'SRunner[{self.splatform.name}]'
