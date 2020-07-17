import logging
import pathlib
import platform
import shlex
import sys
import subprocess as sp

from columnar import columnar

from container import K8SessionManager
import simics


def cmd_create_session(args, _):
    release_tree = simics.ReleaseTree()
    if not args.version:
        versions = release_tree.get_platform_versions(
            args.platform,
            args.simics_version,
        )
        version = versions[-1]
    else:
        version = args.version

    session_manager = K8SessionManager.getInstance()
    if not session_manager.is_valid_os(args.os):
        logging.warning('not valid OS: %s', args.os)
    service_info = session_manager.create_session(
        session_type='simulation',
        platform=args.platform,
        simics_version=args.simics_version,
        version=version,
        host_os=args.os
    )
    name, host_port, created = service_info
    headers = ["Session Name", "Host OS", "VNC Address"]
    data = [[name, args.os, host_port]]
    table = columnar(data, headers, no_borders=True)
    print(table)

    if platform.system() == 'Windows':
        path_vnc = pathlib.Path('C:/Program Files/RealVNC/VNC Viewer/vncviewer.exe')
        if path_vnc.exists():
            command = f'"{path_vnc}" {host_port}'
            popen = sp.Popen(shlex.split(command), shell=True)
