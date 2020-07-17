import pathlib

import simics


def cmd_list(_args, _others):
    path_cwd = pathlib.Path.cwd()
    source_tree = simics.SourceTree(path_cwd)
    splatforms = source_tree.get_platforms()
    splatforms_enabled = filter(lambda x: x.enabled, splatforms)

    paths = set()
    for splatform in splatforms_enabled:
        print(splatform, splatform.path)
        paths.add(splatform.path)

    import pprint
    pprint.pprint(paths)
