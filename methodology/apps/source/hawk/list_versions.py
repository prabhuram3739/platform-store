import logging
import sys

from click import style
from columnar import columnar

import simics

#python3.7.4 simulation.py --simics-ver 6.0 --platform tigerlake --release-ver Silver/2020ww24.4
#python3.7.4 simulation.py --simics-ver 6.0 --platform alderlake --release-ver Silver/2020ww25.3

def cmd_list_versions(args, _):
    release_tree = simics.ReleaseTree()
    versions = release_tree.get_platform_versions(
        args.platform,
        args.simics_version,
    )
    versions = reversed(versions)

    headers = ['Released Version']
    data = list(map(lambda x: [x], versions))
    table = columnar(data, headers, no_borders=True)
    print(table)
