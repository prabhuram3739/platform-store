import logging
import pathlib

import simics
from .utils import get_platform


def cmd_launch(args, _others):
    path_project = pathlib.Path(args.path).resolve()

    release_tree = simics.ReleaseTree()
    versions = release_tree.get_platform_versions(args.platform, args.simics_version)
    version = versions[-1]

    properties = release_tree.get_platform_properties(args.platform, args.simics_version, version)
    base_version = properties.get('base', ['41'])[0]
    project = simics.LightProject(path_project, args.simics_version, base_version)
    path_packages = project.path / 'packages'
    path_packages.mkdir(exist_ok=True, parents=True)
    release_tree.populate(args.platform, args.simics_version, version, path_packages)
    project.unpack()
    default_target = properties.get('default_target')
    if not default_target:
        logging.error('default target is not defined')
        return 1
    default_target = default_target[0]
    return project.launch(default_target)
