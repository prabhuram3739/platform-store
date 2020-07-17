import logging
import pathlib
import shlex
import subprocess as sp

import errors
from container import K8SessionManager


def cmd_open_session(args, _):
    host_port = ''
    (headers, data) = K8SessionManager.getInstance().list_sessions('interactive')
    for session in data:
        if args.session == session[0]:
            host_port = session[2]
            break

    if host_port != '':
        path_vnc = pathlib.Path('C:/Program Files/RealVNC/VNC Viewer/vncviewer.exe')
        if path_vnc.exists():
            command = f'"{path_vnc}" {host_port}'
            popen = sp.Popen(shlex.split(command), shell=True)
        logging.info(f"Launched {args.session}")
    else:
        raise errors.LaunchError(f'could not launch session {host_port} in VNC')
    
