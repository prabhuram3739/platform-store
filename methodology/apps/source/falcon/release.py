import logging
import pathlib

import simics
from .utils import get_platform


def cmd_release(args, _others):
    path_cwd = pathlib.Path.cwd()
    source_tree = simics.SourceTree(path_cwd)
    splatform = get_platform(source_tree, args.platform, args.simics_version)

    url = splatform.release()
    if not url:
        logging.warning('nothing to release, no built packages')
        return 1
    logging.info(f'released: {url}')

    return 0
