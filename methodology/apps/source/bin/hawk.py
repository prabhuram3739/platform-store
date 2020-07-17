import argparse
import logging
import pathlib
import platform
import sys
import os
from pathlib import Path

from hawk import cmd_create_session
from hawk import cmd_delete_session
from hawk import cmd_list_oses
from hawk import cmd_list_platforms
from hawk import cmd_list_versions
from hawk import cmd_list_sessions
from hawk import cmd_open_session


def get_parser():
    parser = argparse.ArgumentParser(
        description='Virtual Platform discovery and launch command line tool',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='print debug info',
    )

    subparsers = parser.add_subparsers(
        dest='command',
        title='commands',
        description='hawk commands',
        required=True,
        help='available hawk commands',
    )

    parser_list_platforms = subparsers.add_parser(
        'list-platforms',
        aliases=['lp'],
        help='list available platforms',
    )
    parser_list_platforms.set_defaults(func=cmd_list_platforms)
    
    parser_list_versions = subparsers.add_parser(
        'list-versions',
        description='list the released versions of the platform',
        aliases=['lv'],
        help='list available versions for a platform',
    )
    parser_list_versions.add_argument(
        'platform',
        help='platform name',
    )
    parser_list_versions.add_argument(
        '--simics-version',
        choices=['6.0', '5.0'],
        default='6.0',
        help='Simics version',
    )
    parser_list_versions.set_defaults(func=cmd_list_versions)

    parser_listos = subparsers.add_parser(
        'list-os',
        description='list the available host OS options to launch the session on',
        aliases=['lo'],
        help='list available OS',
    )
    parser_listos.set_defaults(func=cmd_list_oses)

    parser_create_session = subparsers.add_parser(
        'create-session',
        description='create a new session with the specified host OS, platform and version',
        aliases=['cs'],
        help='create session to run virtual platform',
    )
    parser_create_session.add_argument(
        '-os', '--os',
        default='sles12sp5',
        help='host OS to launch the container',
    )
    parser_create_session.add_argument(
        'platform',
        help='virtual platform',
    )
    parser_create_session.add_argument(
        '--simics-version',
        choices=['6.0', '5.0'],
        default='6.0',
        help='Simics version',
    )
    parser_create_session.add_argument(
        '--version',
        help='platform version, latest if not specified',
    )
    parser_create_session.set_defaults(func=cmd_create_session)

    parser_list_sessions = subparsers.add_parser(
        'list-sessions',
        description='list the running sessions',
        aliases=['ls'],
        help='list sessions',
    )
    parser_list_sessions.set_defaults(func=cmd_list_sessions)

    if platform.system() == 'Windows':
        parser_open_session = subparsers.add_parser(
            'open-session',
            aliases=['os', 'open-session'],
            help='open VNC session',
        )
        parser_open_session.add_argument(
            'session',
            help='session to open',
        )
        parser_open_session.set_defaults(func=cmd_open_session)

    parser_delete_session = subparsers.add_parser(
        'delete-session',
        description='create a new session with the specified OS',
        aliases=['ds'],
        help='delete existing session',
    )
    parser_delete_session.add_argument(
        'sessions',
        nargs='*',
        help='sessions to delete',
    )
    parser_delete_session.set_defaults(func=cmd_delete_session)

    return parser

def main():
    parser = get_parser()
    args, args_command = parser.parse_known_args()

    if args.verbose:
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO
    logging.basicConfig(level=log_level, format='%(levelname)s: %(message)s')

    exit_code = 0
    try:
        args.func(args, args_command)
    except KeyboardInterrupt:
        exit_code = 0
    except Exception as error:  # pylint: disable=broad-except
        logging.error(error)
        exit_code = 1

    sys.exit(exit_code)


if __name__ == '__main__':
   main()
