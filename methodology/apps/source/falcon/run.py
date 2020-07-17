import logging
import pathlib

import simics
from .utils import get_platform


def cmd_run(args, _others):
    path_cwd = pathlib.Path.cwd()
    source_tree = simics.SourceTree(path_cwd)
    splatform = get_platform(source_tree, args.platform, args.simics_version)

    srunner = splatform.get_srunner(args.target)
    result = 0
    if args.list:
        sruns_names = '\n'.join(map(str, srunner.sruns))
        print(f'Platform {splatform.name} runs:\n{sruns_names}')
    else:
        result = srunner.run()

    return result
