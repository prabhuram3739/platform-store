import argparse
import logging
import sys

from errors import BaseError
from falcon import cmd_checkout
from falcon import cmd_build
from falcon import cmd_populate
from falcon import cmd_release
from falcon import cmd_release_update
from falcon import cmd_clean
from falcon import cmd_info
from falcon import cmd_test
from falcon import cmd_run
from falcon import cmd_launch


def get_parser():
    parser = argparse.ArgumentParser(
        description='Virtual Platform development flow automation tool',
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
        description='flow commands',
        required=True,
        help='available flow steps and helpers',
    )

    parser_checkout = subparsers.add_parser(
        'checkout',
        description='checkout VP Git repository',
        aliases=['co'],
        help='checkout repository',
    )
    parser_checkout.add_argument(
        'path',
        help='path to the VP repo'
    )
    parser_checkout.add_argument(
        '--revision',
        default='master',
        help='revision to checkout'
    )
    parser_checkout.add_argument(
        '--url',
        default=None,
        help='VP repo URL'
    )
    parser_checkout.set_defaults(func=cmd_checkout)

    parser_build = subparsers.add_parser(
        'build',
        description='create Simics project if needed, '
                    'build platform and package',
        help='build platform and corresponding package',
    )
    parser_build.add_argument(
        '-p', '--platform',
        default=None,
        help='Simics platform name',
    )
    parser_build.add_argument(
        '--simics_version',
        type=str,
        choices=['6.0', '5.0'],
        default='6.0',
        help='Simics version',
    )
    parser_build.add_argument(
        '--legacy',
        default=False,
        action='store_true',
        help='legacy flow',
    )
    parser_build.set_defaults(func=cmd_build)

    parser_populate = subparsers.add_parser(
        'populate',
        description='create Simics project if needed, '
                    'populate platform from released package',
        help='populate platform from released package',
    )
    parser_populate.add_argument(
        '-p', '--platform',
        default=None,
        help='Simics platform name',
    )
    parser_populate.add_argument(
        '--simics_version',
        type=str,
        choices=['6.0', '5.0'],
        default='6.0',
        help='Simics version',
    )
    parser_populate.add_argument(
        '--version',
        default=None,
        help='platform version',
    )
    parser_populate.set_defaults(func=cmd_populate)

    parser_release = subparsers.add_parser(
        'release',
        description='release platform to Artifactory',
        help='release platform',
    )
    parser_release.add_argument(
        '-p', '--platform',
        default=None,
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

    parser_release_update = subparsers.add_parser(
        'release-update',
        description='update release properties',
        help='update platform release',
    )
    parser_release_update.add_argument(
        '-p', '--platform',
        default=None,
        help='Simics platform name',
    )
    parser_release_update.add_argument(
        '--simics_version',
        type=str,
        choices=['6.0', '5.0'],
        default='6.0',
        help='Simics version',
    )
    parser_release_update.add_argument(
        '--quality',
        type=str,
        choices=['bronze', 'silver'],
        required=True,
        help='test quality, TODO: fix argument name',
    )
    parser_release_update.add_argument(
        '--status',
        type=str,
        choices=['passed', 'failed'],
        default='passed',
        help='test status',
    )
    parser_release_update.set_defaults(func=cmd_release_update)

    parser_test = subparsers.add_parser(
        'test',
        description='run platform test suite',
        help='test platform',
    )
    parser_test.add_argument(
        '-p', '--platform',
        default=None,
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
        '--list',
        action='store_true',
        default=False,
        help='list all available tests',
    )
    parser_test.add_argument(
        '--test',
        type=str,
        action='append',
        help='test name to run',
    )
    parser_test.add_argument(
        '--tag',
        type=str,
        action='append',
        help='test tag to run',
    )
    parser_test.add_argument(
        '--quality',
        choices=['bronze', 'silver'],
        type=str,
        help='test quality to run',
    )
    parser_test.add_argument(
        '--verbose',
        dest='verbose_test',
        action='store_true',
        help='print test info',
    )
    parser_test.set_defaults(func=cmd_test)

    parser_run = subparsers.add_parser(
        'run',
        description='launch default platform target',
        help='run platform',
    )
    parser_run.add_argument(
        '-p', '--platform',
        default=None,
        help='Simics platform name',
    )
    parser_run.add_argument(
        '--simics_version',
        type=str,
        choices=['6.0', '5.0'],
        default='6.0',
        help='Simics version',
    )
    parser_run.add_argument(
        '--list',
        action='store_true',
        default=False,
        help='list all available run configurations',
    )
    parser_run.add_argument(
        '--target',
        help='target to run',
    )
    parser_run.set_defaults(func=cmd_run)

    parser_clean = subparsers.add_parser(
        'clean',
        description='clean all files not tracked by Git',
        help='clean project',
    )
    parser_clean.add_argument(
        '-p', '--platform',
        default=None,
        help='Simics platform name',
    )
    parser_clean.add_argument(
        '--simics_version',
        type=str,
        choices=['6.0', '5.0'],
        default='6.0',
        help='Simics version',
    )
    parser_clean.add_argument(
        '-n', '--dry-run',
        action='store_true',
        default=False,
        help='list files to be deleted'
    )
    parser_clean.set_defaults(func=cmd_clean)

    parser_info = subparsers.add_parser(
        'info',
        description='aggregate and print platform information '
                    'used in build, test, run and release commands, '
                    'for example: owners, default build targets, etc.',
        help='print platform info',
    )
    parser_info.add_argument(
        '-p', '--platform',
        default=None,
        help='Simics platform name',
    )
    parser_info.add_argument(
        '-v', '--simics_version',
        type=str,
        choices=['6.0', '5.0'],
        default='6.0',
        help='Simics version',
    )
    parser_info.add_argument(
        '--raw',
        action='store_true',
        default=False,
        help='print raw data',
    )
    parser_info.set_defaults(func=cmd_info)

    parser_launch = subparsers.add_parser(
        'launch',
        description='launch default platform target',
        help='populate and launch platform',
    )
    parser_launch.add_argument(
        'platform',
        help='Simics platform name',
    )
    parser_launch.add_argument(
        '--simics_version',
        type=str,
        choices=['6.0', '5.0'],
        default='6.0',
        help='Simics version',
    )
    parser_launch.add_argument(
        '-p', '--path',
        default='.',
        help='path to Simics project',
    )
    parser_launch.set_defaults(func=cmd_launch)

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
