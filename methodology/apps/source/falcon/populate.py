import logging
import pathlib

import simics
from .utils import get_platform


def cmd_populate(args, _others):
    path_cwd = pathlib.Path.cwd()
    source_tree = simics.SourceTree(path_cwd)
    splatform = get_platform(source_tree, args.platform, args.simics_version)

    return splatform.populate(args.version)
