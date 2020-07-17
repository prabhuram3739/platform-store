import pathlib
import logging

import simics


def cmd_release(args, _):
    path = pathlib.Path(args.path).resolve()
    source_tree = simics.SourceTree.create(path, args.url, args.revision)
    splatform = source_tree.get_platform(args.platform, args.simics_version)
    splatform.build()
    url = splatform.release('auto')
    if not url:
        logging.warning('could not find built package')
        return 1
    logging.info(f'released: {url}')

    return 0
