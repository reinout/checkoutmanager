import os
import subprocess
import sys

# For zc.buildout's system() method:
MUST_CLOSE_FDS = not sys.platform.startswith('win')
# When you set '-v', this constant is changed.  A bit hacky.
VERBOSE = False


def system(command, input=''):
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
    i, o, e = (p.stdin, p.stdout, p.stderr)
    if input:
        i.write(input)
    i.close()
    result = o.read() + e.read()
    o.close()
    e.close()
    return result
