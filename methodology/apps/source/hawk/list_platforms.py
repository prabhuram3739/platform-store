import logging
import sys

from click import style
from columnar import columnar

import simics


def cmd_list_platforms(args, _):
    release_tree = simics.ReleaseTree()
    platform_names = release_tree.get_platform_names()

    headers = ['Platform Name']
    platform_names = list(map(lambda x: [x], platform_names))
    data = platform_names
    table = columnar(data, headers, no_borders=True)
    print(table)
