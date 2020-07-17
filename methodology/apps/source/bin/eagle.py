import argparse
import logging
import pathlib
import platform
import sys
import os
from pathlib import Path

from eagle import cmd_create_session
from eagle import cmd_delete_session
from eagle import cmd_list_oses
from eagle import cmd_list_sessions
from eagle import cmd_open_session


def get_parser():
    parser = argparse.ArgumentParser(
        description='Launcher for Virtual Platform development',
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
        description='eagle commands',
        required=True,
        help='available eagle commands',
    )

    parser_listos = subparsers.add_parser(
        'list-os',
        description='list the available host OS options to launch the session on',
        aliases=['lo'],
        # destination='listos',
        help='OS list',
    )
    parser_listos.set_defaults(func=cmd_list_oses)

    parser_create_session = subparsers.add_parser(
        'create-session',
        description='create a new cloud session with the specified OS',
        aliases=['cs'],
        help='create session in cloud',
    )
    parser_create_session.add_argument(
        '--os',
        default='sles12sp5',
        help='host OS to launch the container',
    )
    parser_create_session.set_defaults(func=cmd_create_session)

    parser_list_sessions = subparsers.add_parser(
        'list-sessions',
        description='list existing sessions',
        aliases=['ls'],
        help='list existing sessions',
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
