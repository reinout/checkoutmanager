import os
import subprocess
import sys

# For zc.buildout's system() method:
MUST_CLOSE_FDS = not sys.platform.startswith('win')
# When you set '-v', this constant is changed.  A bit hacky.
VERBOSE = False


class CommandError(Exception):

    def __init__(self, returncode, command, output):
        self.returncode = returncode
        self.command = command
        self.output = output
        self.working_dir = os.getcwd()

    def print_msg(self):
        print "Something went wrong when executing:"
        print "    %s" % self.command
        print "while in directory:"
        print "    %s" % self.working_dir
        print "Returncode:"
        print "    %s" % self.returncode
        print "Output:"
        print self.output


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
        raise CommandError(p.returncode, command, result)

    return result
