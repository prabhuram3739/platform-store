import logging
import pathlib
import pprint

import simics
from .utils import get_platform


def cmd_info(args, _others):
    path_cwd = pathlib.Path.cwd()
    source_tree = simics.SourceTree(path_cwd)
    splatform = get_platform(source_tree, args.platform, args.simics_version)

    print(f'Platform {splatform.name}: {"enabled" if splatform.enabled else "disabled"}')
    owners = ', '.join(splatform.owners)
    print(f'owners: {owners}')
    packages = ', '.join(map(str, splatform.packages))
    print(f'packages: {packages}')

    platforms = source_tree.get_platforms()
    map_platform_name = {p.name: p for p in platforms}

    dependencies_disabled = []
    for dependency in splatform.dependencies:
        if dependency not in map_platform_name:
            logging.warning("dependency '%s' does not exist, ignoring...", dependency)
            continue
        dependency = map_platform_name.get(dependency)
        if not dependency.enabled:
            dependencies_disabled.append(dependency.name)

    if dependencies_disabled:
        message = ', '.join(dependencies_disabled)
        logging.warning(
            'following dependencies are disabled, please check if they still needed: %s',
            message,
        )

    if args.raw:
        pprint.pprint(splatform.get_raw_data())
