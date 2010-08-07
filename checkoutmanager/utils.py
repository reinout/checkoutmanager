import os
import subprocess
import sys
from subprocess import CalledProcessError

# For zc.buildout's system() method:
MUST_CLOSE_FDS = not sys.platform.startswith('win')
# When you set '-v', this constant is changed.  A bit hacky.
VERBOSE = False


def system(command, input=None):
    """commands.getoutput() replacement that also works on windows

    Code copied from zc.buildout.

    """
    if VERBOSE:
        print '[%s] %s' % (os.getcwd(), command)
    p = subprocess.Popen(command,
                         shell=True,
                         stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE,
                         close_fds=MUST_CLOSE_FDS)
    stdoutdata, stderrdata = p.communicate(input=input)
    result = stdoutdata + stderrdata
    if p.returncode:
        raise CalledProcessError(p.returncode, command)

    return result
