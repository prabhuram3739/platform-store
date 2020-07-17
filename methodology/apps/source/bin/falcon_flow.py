import argparse
import logging
import sys

from errors import BaseError
from falcon_flow import cmd_release
from falcon_flow import cmd_test


def get_parser():
    parser = argparse.ArgumentParser(
        description='Falcon Flows',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='print debug info',
    )

    subparsers = parser.add_subparsers(
        dest='flow',
        title='flows',
        description='flow commands',
        required=True,
        help='available flows',
    )

    parser_release = subparsers.add_parser(
        'release',
        description='end-to-end release',
        help='checkout repository, build and release',
    )
    parser_release.add_argument(
        '-p', '--path',
        default='vp',
        help='path to the VP repo'
    )
    parser_release.add_argument(
        '--revision',
        default='master',
        help='revision to checkout'
    )
    parser_release.add_argument(
        '--url',
        default=None,
        help='VP repo URL'
    )
    parser_release.add_argument(
        'platform',
        help='Simics platform name',
    )
    parser_release.add_argument(
        '--simics_version',
        type=str,
        choices=['6.0', '5.0'],
        default='6.0',
        help='Simics version',
    )
    parser_release.set_defaults(func=cmd_release)

    parser_test = subparsers.add_parser(
        'test',
        description='end-to-end test',
        help='checkout repository, test and update release',
    )
    parser_test.add_argument(
        '-p', '--path',
        default='vp',
        help='path to the VP repo'
    )
    parser_test.add_argument(
        '--revision',
        default='master',
        help='revision to checkout'
    )
    parser_test.add_argument(
        '--url',
        default=None,
        help='VP repo URL'
    )
    parser_test.add_argument(
        'platform',
        help='Simics platform name',
    )
    parser_test.add_argument(
        '--simics_version',
        type=str,
        choices=['6.0', '5.0'],
        default='6.0',
        help='Simics version',
    )
    parser_test.add_argument(
        '--version',
        help='Simics platform version, latest if not specifed',
    )
    parser_test.set_defaults(func=cmd_test)

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
        exit_code = args.func(args, args_command)
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
