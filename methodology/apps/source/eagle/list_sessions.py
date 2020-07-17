import logging

from columnar import columnar

from container import K8SessionManager


def cmd_list_sessions(args, _):
    (headers, data) = K8SessionManager.getInstance().list_sessions('interactive')
    if data:
        table = columnar(data, headers, no_borders=True)
        print(table)
