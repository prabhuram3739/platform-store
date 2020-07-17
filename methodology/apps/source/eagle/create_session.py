import logging
import pathlib
import platform
import shlex
import subprocess as sp

from columnar import columnar

from container import K8SessionManager


def cmd_create_session(args, _):
    session_manager = K8SessionManager.getInstance()
    if session_manager.is_valid_os(args.os):

        service_info = session_manager.create_session(
                            session_type='interactive',
                            platform=None,
                            simics_version=None,
                            version=None,
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
    else:
        logging.error("Selected OS %s is invalid.Check valid OSes with --list-oses" % args.os)

