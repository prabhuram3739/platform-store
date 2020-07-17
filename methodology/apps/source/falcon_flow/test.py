import pathlib
import logging

import simics


def cmd_test(args, _):
    path = pathlib.Path(args.path).resolve()
    source_tree = simics.SourceTree.create(path, args.url, args.revision)
    splatform = source_tree.get_platform(args.platform, args.simics_version)
    splatform.populate()
    quality = 'bronze'
    result = splatform.test(quality)
    splatform.release_update(False if result else True, quality, flow='auto')

    return 0
