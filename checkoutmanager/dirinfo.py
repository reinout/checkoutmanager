"""Information on one directory"""
import os

from checkoutmanager.utils import system
from checkoutmanager.utils import CommandError

# 8-char codes
#         '12345678'
CREATED = 'created '
MISSING = 'missing '
PRESENT = 'present '


class DirInfo(object):
    """Wrapper for information on one directory"""

    vcs = 'xxx'

    def __init__(self, directory, url):
        self.directory = directory
        self.url = url

    def __repr__(self):
        return '<DirInfo (%s) for %s>' % (self.vcs, self.directory)

    def __cmp__(self, other):
        # Easy sorting in tests
        return cmp(self.__repr__(), other.__repr__())

    @property
    def parent(self):
        return os.path.abspath(os.path.join(self.directory, '..'))

    @property
    def exists(self):
        return os.path.exists(self.directory)

    def cmd_exists(self, report_only_missing=False):
        if self.exists:
            answer = PRESENT
            if report_only_missing:
                return
        else:
            answer = MISSING
        print ' '.join([answer, self.directory])

    def cmd_up(self):
        raise NotImplementedError()

    def cmd_st(self):
        raise NotImplementedError()

    def cmd_co(self):
        raise NotImplementedError()

    def cmd_out(self):
        raise NotImplementedError()


class SvnDirInfo(DirInfo):

    vcs = 'svn'

    def cmd_up(self):
        print self.directory
        os.chdir(self.directory)
        print system("svn up")

    def cmd_st(self):
        os.chdir(self.directory)
        output = system("svn st --ignore-externals")
        lines = [line.strip() for line in output.splitlines()
                 if line.strip()
                 and not line.startswith('X')]
        if lines:
            print self.directory
            print output
            print

    def cmd_co(self):
        if not os.path.exists(self.parent):
            print "Creating parent dir %s" % self.parent
            os.makedirs(self.parent)
        if self.exists:
            answer = PRESENT
        else:
            answer = CREATED
            os.chdir(self.parent)
            print system("svn co %s %s" % (
                self.url, self.directory))

        print ' '.join([answer, self.directory])

    def cmd_out(self):
        # Outgoing changes?  We're svn, not some new-fangled dvcs :-)
        pass


class BzrDirInfo(DirInfo):

    vcs = 'bzr'

    def cmd_up(self):
        print self.directory
        os.chdir(self.directory)
        print system("bzr up")

    def cmd_st(self):
        os.chdir(self.directory)
        output = system("bzr st")
        if output.strip():
            print self.directory
            print output
            print

    def cmd_co(self):
        if not os.path.exists(self.parent):
            print "Creating parent dir %s" % self.parent
            os.makedirs(self.parent)
        if self.exists:
            answer = PRESENT
        else:
            answer = CREATED
            os.chdir(self.parent)
            print system("bzr checkout %s %s" % (
                self.url, self.directory))

        print ' '.join([answer, self.directory])

    def cmd_out(self):
        os.chdir(self.directory)
        output = system("bzr missing %s" % self.url)
        if not 'Branches are up to date' in output:
            print "Unpushed outgoing changes in %s:" % self.directory
            print output


class HgDirInfo(DirInfo):

    vcs = 'hg'

    def cmd_up(self):
        print self.directory
        os.chdir(self.directory)
        print system("hg pull -u %s" % self.url)

    def cmd_st(self):
        os.chdir(self.directory)
        output = system("hg st")
        if output.strip():
            print self.directory
            print output
            print

    def cmd_co(self):
        if not os.path.exists(self.parent):
            print "Creating parent dir %s" % self.parent
            os.makedirs(self.parent)
        if self.exists:
            answer = PRESENT
        else:
            answer = CREATED
            os.chdir(self.parent)
            # TODO: check!
            print system("hg clone %s %s" % (
                self.url, self.directory))

        print ' '.join([answer, self.directory])

    def cmd_out(self):
        os.chdir(self.directory)
        try:
            output = system("hg out %s" % self.url)
        except CommandError, e:
            if e.returncode == 1:
                # hg returns 1 if there are no outgoing changes!
                # Checkoutmanager is as quiet as possible, so we print
                # nothing.
                return
            else:
                raise
        # No errors means we have genuine outgoing changes.
        print "Unpushed outgoing changes in %s:" % self.directory
        print output


class GitDirInfo(DirInfo):

    vcs = 'git'

    def cmd_up(self):
        print self.directory
        os.chdir(self.directory)
        print system("git pull")

    def cmd_st(self):
        os.chdir(self.directory)
        output = system("git status --short")
        if output.strip():
            print self.directory
            print output
            print

    def cmd_co(self):
        if not os.path.exists(self.parent):
            print "Creating parent dir %s" % self.parent
            os.makedirs(self.parent)
        if self.exists:
            answer = PRESENT
        else:
            answer = CREATED
            os.chdir(self.parent)
            # TODO: check!
            print system("git clone %s %s" % (
                self.url, self.directory))

        print ' '.join([answer, self.directory])

    def cmd_out(self):
        os.chdir(self.directory)
        output = system("git log origin/master..HEAD")
        if output.strip():
            print "Unpushed outgoing changes in %s:" % self.directory
            print output
