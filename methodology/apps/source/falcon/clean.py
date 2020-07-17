import pathlib

import simics
from shell import run
from .utils import get_platform


def cmd_clean(args, _others):
    path_cwd = pathlib.Path.cwd()
    source_tree = simics.SourceTree(path_cwd)
    splatform = get_platform(source_tree, args.platform, args.simics_version)

    dry_run = 'n' if args.dry_run else 'f'
    command = f'git clean -{dry_run}dx'

    result = run(command, splatform.path)
    return result
