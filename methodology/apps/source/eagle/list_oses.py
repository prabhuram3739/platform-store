import logging

from columnar import columnar

from container import K8SessionManager


def cmd_list_oses(args, _):
    (headers, data) = K8SessionManager.getInstance().get_oses()
    table = columnar(data, headers, no_borders=True)
    print(table)
