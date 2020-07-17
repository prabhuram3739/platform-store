import logging

import errors

from container import K8SessionManager


def cmd_delete_session(args, _):
    session_manager = K8SessionManager.getInstance()
    if args.sessions[0] == 'all':
        #import pdb; pdb.set_trace()
        header, data = session_manager.list_sessions('simulation')
        if data:
            sessions = [session[0] for session in data]
            args.sessions = sessions
        else:
            return # silently since list_session will show the error message

    for session in args.sessions:
        try:
            session_manager.delete_session(
                session_type='simulation',
                session_name=session,
            )
            logging.info(f"Successfully deleted {session}")
        except errors.ContainerError:
            logging.error(f"Failed to delete {session}")
