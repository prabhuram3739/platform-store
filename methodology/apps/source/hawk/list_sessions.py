import logging

from click import style
from columnar import columnar

from container import K8SessionManager


def cmd_list_sessions(args, _):
    (headers, data) = K8SessionManager.getInstance().list_sessions('simulation')
    if data:
        table = columnar(data, headers, no_borders=True)
        print(table)
