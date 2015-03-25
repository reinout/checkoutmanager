from __future__ import print_function
from cStringIO import StringIO
from functools import wraps
import os
import subprocess
import sys

# For zc.buildout's system() method:
MUST_CLOSE_FDS = not sys.platform.startswith('win')
# When you set '-v', this constant is changed.  A bit hacky.
VERBOSE = False


class CommandError(Exception):

    def __init__(self, returncode=0, command="", output=""):
        self.returncode = returncode
        self.command = command
        self.output = output
        self.working_dir = os.getcwd()

    def format_msg(self):
        lines = []
        lines.append("Something went wrong when executing:")
        lines.append("    %s" % self.command)
        lines.append("while in directory:")
        lines.append("    %s" % self.working_dir)
        lines.append("Returncode:")
        lines.append("    %s" % self.returncode)
        lines.append("Output:")
        lines.append(self.output)
        return "\n".join(lines)

    def print_msg(self):
        print(self.format_msg())


def system(command, input=None):
    """commands.getoutput() replacement that also works on windows

    Code copied from zc.buildout.

    """
    if VERBOSE:
        print('[%s] %s' % (os.getcwd(), command))
    p = subprocess.Popen(command,
                         shell=True,
                         stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE,
                         close_fds=MUST_CLOSE_FDS)
    stdoutdata, stderrdata = p.communicate(input=input)
    result = stdoutdata + stderrdata
    if p.returncode:
        raise CommandError(p.returncode, command, result)

    return result


def capture_stdout(func):
    """Decorator to capture stdout and return it as a string.

    NOTE: The return value of the wrapped function is discarded.
    """
    import sys

    @wraps(func)
    def newfunc(*args, **kwargs):
        sys.stdout = StringIO()
        try:
            func(*args, **kwargs)
            return sys.stdout.getvalue()
        finally:
            sys.stdout = sys.__stdout__
    return newfunc
