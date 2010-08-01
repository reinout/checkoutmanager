"""Information on one directory"""
import os
import commands

# 8-char codes
#         '12345678'
CREATED  = 'created '
MISSING  = 'missing '
PRESENT  = 'present '


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

    def cmd_exists(self):
        answer = self.exists and PRESENT or MISSING
        print ' '.join([answer, self.directory])

    def cmd_up(self):
        raise NotImplementedError()

    def cmd_st(self):
        raise NotImplementedError()

    def cmd_co(self):
        raise NotImplementedError()


class SvnDirInfo(DirInfo):

    vcs = 'svn'

    def cmd_up(self):
        print self.directory
        os.chdir(self.directory)
        print commands.getoutput("svn up")

    def cmd_st(self):
        os.chdir(self.directory)
        output = commands.getoutput("svn st --ignore-externals")
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
            print commands.getoutput("svn co %s %s" % (
                self.url, self.directory))

        print ' '.join([answer, self.directory])


class BzrDirInfo(DirInfo):

    vcs = 'bzr'

    def cmd_up(self):
        print self.directory
        os.chdir(self.directory)
        print commands.getoutput("bzr up")

    def cmd_st(self):
        os.chdir(self.directory)
        output = commands.getoutput("bzr st")
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
            print commands.getoutput("bzr checkout %s %s" % (
                self.url, self.directory))

        print ' '.join([answer, self.directory])


class HgDirInfo(DirInfo):

    vcs = 'hg'

    def cmd_up(self):
        print self.directory
        os.chdir(self.directory)
        print commands.getoutput("hg pull -u")

    def cmd_st(self):
        os.chdir(self.directory)
        output = commands.getoutput("hg st")
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
            print commands.getoutput("hg clone %s %s" % (
                self.url, self.directory))

        print ' '.join([answer, self.directory])
