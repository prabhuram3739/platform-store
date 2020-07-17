import argparse
import logging
import sys

from errors import BaseError
from falcon import cmd_check
from falcon import cmd_list


def get_parser():
    parser = argparse.ArgumentParser(
        description='Falcon VP Management',
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
        description='management commands',
        required=True,
        help='management commands and helpers',
    )

    parser_check = subparsers.add_parser(
        'check',
        description='check VP Git repository',
        help='check repository health',
    )
    parser_check.add_argument(
        '-p', '--platform',
        default=None,
        help='Simics platform name',
    )
    parser_check.add_argument(
        '--simics_version',
        type=str,
        choices=['6.0', '5.0'],
        default=None,
        help='Simics version',
    )
    parser_check.set_defaults(func=cmd_check)

    parser_list = subparsers.add_parser(
        'list',
        description='list available paltforms',
        help='list platforms',
    )
    parser_list.set_defaults(func=cmd_list)

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
    except BaseError as error:
        logging.error(error)
        exit_code = 1
    except NotImplementedError as error:
        message = str(error)
        if not message:
            message = 'functionality is not implemented yet'
        logging.error(message)
        exit_code = 1
    except Exception as error:  # pylint: disable=broad-except
        logging.error(error)
        exit_code = 1

    sys.exit(exit_code)


if __name__ == '__main__':
    main()
