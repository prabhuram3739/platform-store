import logging
import pathlib

import simics
from .utils import get_platform


def cmd_test(args, _others):
    path_cwd = pathlib.Path.cwd()
    source_tree = simics.SourceTree(path_cwd)
    splatform = get_platform(source_tree, args.platform, args.simics_version)

    stest_suites = splatform.get_stest_suite(
        names=args.test,
        tags=args.tag,
        quality=args.quality
    )
    result = 0
    if args.list:
        for stest_suite in stest_suites:
            stest_names = '\n'.join(map(str, stest_suite._tests))
            print(f'{splatform.name} {stest_suite.name} test suite: {len(stest_suite._tests)} test cases\n{stest_names}')
    else:
        stest_runner = simics.STestRunnerMultiprocess(args.verbose_test)
        # stest_runner = simics.STestRunner(args.verbose_test)
        for stest_suite in stest_suites:
            print(f'{splatform.name} {stest_suite.name} test suite: {len(stest_suite._tests)} test cases')
            result += stest_runner.run(stest_suite)

    return result
