import pathlib

import simics


def cmd_checkout(args, _):
    path = pathlib.Path(args.path).resolve()
    source_tree = simics.SourceTree.create(path, args.url, args.revision)

    return 0
