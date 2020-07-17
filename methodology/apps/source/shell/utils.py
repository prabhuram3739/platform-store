import logging
import pathlib
import platform
import shlex
import subprocess as sp


def run(cmd, cwd=None, capture_outputs=False):
    cwd = cwd if cwd else pathlib.Path().cwd()
    logging.debug('running command at %s: %s', cwd, cmd)

    is_posix = platform.system() != 'Windows'

    if capture_outputs:
        stdout = sp.PIPE
        stderr = sp.PIPE
    else:
        stdout = None
        stderr = None

    returncode = 0
    try:
        popen = sp.Popen(shlex.split(cmd, posix=is_posix), stdout=stdout, stderr=stderr, cwd=cwd)
        stdout, stderr = popen.communicate()
        if capture_outputs:
            stdout = stdout.decode()
            stderr = stderr.decode()
    except FileNotFoundError as error:
        logging.error(
            'cannot run command "%s": %s',
            cmd,
            error,
        )
        returncode = 1

    if capture_outputs:
        return popen.returncode, stdout, stderr
    return popen.returncode
