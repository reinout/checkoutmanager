"""Information on one directory"""
from __future__ import print_function
from __future__ import unicode_literals
import os
import re

from checkoutmanager.utils import CommandError
from checkoutmanager.utils import capture_stdout
from checkoutmanager.utils import system

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

    def __lt__(self, other):
        # Easy sorting in tests
        return self.__repr__() < other.__repr__()

    @property
    def parent(self):
        return os.path.abspath(os.path.join(self.directory, '..'))

    @property
    def exists(self):
        expected_dot_dir = os.path.join(self.directory, "." + self.vcs)
        return os.path.exists(expected_dot_dir)

    @capture_stdout
    def cmd_exists(self, report_only_missing=False):
        if self.exists:
            answer = PRESENT
            if report_only_missing:
                return
        else:
            answer = MISSING
        print(' '.join([answer, self.directory]))

    def cmd_rev(self):
        raise NotImplementedError()

    def cmd_in(self):
        raise NotImplementedError()

    def cmd_up(self):
        raise NotImplementedError()

    def cmd_st(self):
        raise NotImplementedError()

    def cmd_co(self):
        raise NotImplementedError()

    def cmd_out(self):
        raise NotImplementedError()

    def cmd_upgrade(self):
        # This is only useful for subversion.
        pass

    def cmd_info(self):
        # This is only known to be useful for subversion.
        pass


class SvnDirInfo(DirInfo):

    vcs = 'svn'

    regex_last_changed = re.compile('last changed rev: (?P<rev>\d+)')

    def _parse_last_changed(self, output):
        lines = [line.strip() for line in output.splitlines()
                 if line.strip()]
        for line in lines:
            m = self.regex_last_changed.match(line.lower())
            if m:
                return m.group('rev')

    @capture_stdout
    def cmd_rev(self):
        print(self.directory)
        os.chdir(self.directory)
        output = system("svn info")
        print(self._parse_last_changed(output))

    @capture_stdout
    def cmd_in(self):
        os.chdir(self.directory)
        output = system("svn info")
        local_rev = self._parse_last_changed(output)
        try:
            output = system("svn info -r HEAD")
            remote_rev = self._parse_last_changed(output)
            if remote_rev > local_rev:
                print(self.directory)
                print("Incoming changes : "
                      "Revision {0} to {1}".format(local_rev, remote_rev))
        except CommandError:
            print("Could not connect to repository for " + self.directory)
            return

    @capture_stdout
    def cmd_up(self):
        print(self.directory)
        os.chdir(self.directory)
        print(system("svn up --non-interactive"))

    @capture_stdout
    def cmd_st(self):
        os.chdir(self.directory)
        output = system("svn st --ignore-externals")
        lines = [line.strip() for line in output.splitlines()
                 if line.strip()
                 and not line.startswith('X')]
        if lines:
            print(self.directory)
            print(output)
            print()

    @capture_stdout
    def cmd_co(self):
        if not os.path.exists(self.parent):
            print("Creating parent dir %s" % self.parent)
            os.makedirs(self.parent)
        if self.exists:
            answer = PRESENT
        else:
            answer = CREATED
            os.chdir(self.parent)
            print(system("svn co %s %s" % (
                self.url, self.directory)))

        print(' '.join([answer, self.directory]))

    @capture_stdout
    def cmd_out(self):
        # Outgoing changes?  We're svn, not some new-fangled dvcs :-)
        pass

    @capture_stdout
    def cmd_upgrade(self):
        # Run 'svn upgrade'.  This upgrades the working copy to the
        # new subversion 1.7 layout of the .svn directory.
        os.chdir(self.directory)
        output = system("svn upgrade --quiet")
        lines = [line.strip() for line in output.splitlines()
                 if line.strip()
                 and not line.startswith('X')]
        print(self.directory)
        if lines:
            print(output)
            print()

    @capture_stdout
    def cmd_info(self):
        # This is useful when your svn program has been updated and
        # the security mechanisms on your OS now require you to
        # explictly allow access to the stored credentials.  The other
        # commands either do not access the internet or are
        # non-interactive (like command up).  In fact, the reason for
        # adding this command is that a non-interactive 'svn update'
        # will fail when you have not granted access to your
        # credentials yet for this new svn program.  This has happened
        # a bit too often for me (Maurits).
        os.chdir(self.directory)
        # Determine the version.
        output = system("svn --version --quiet")
        try:
            version = float(output[:3])
        except (ValueError, TypeError, IndexError):
            version = 0.0
        # Since version 1.8 we must use --force-interactive, which is
        # unavailable in earlier versions.
        if version < 1.8:
            print(system("svn info %s" % self.url))
        else:
            print(system("svn info --force-interactive %s" % self.url))


class BzrDirInfo(DirInfo):

    vcs = 'bzr'

    @capture_stdout
    def cmd_rev(self):
        print(self.directory)
        os.chdir(self.directory)
        print(system("bzr revno"))

    @capture_stdout
    def cmd_in(self):
        os.chdir(self.directory)
        try:
            system("bzr missing --theirs-only")
        except CommandError as e:
            if e.returncode == 1:
                # bzr returns 1 if there are incoming changes!
                print(self.directory)
                print("'bzr missing' reports incoming changesets : ")
                print(e.output)
                return
            if e.returncode == 3:
                # bzr returns 3 if there is no parent
                pass
            else:
                raise
        return

    @capture_stdout
    def cmd_up(self):
        print(self.directory)
        os.chdir(self.directory)
        print(system("bzr up"))

    @capture_stdout
    def cmd_st(self):
        os.chdir(self.directory)
        output = system("bzr st")
        if output.strip():
            print(self.directory)
            print(output)
            print()

    @capture_stdout
    def cmd_co(self):
        if not os.path.exists(self.parent):
            print("Creating parent dir %s" % self.parent)
            os.makedirs(self.parent)
        if self.exists:
            answer = PRESENT
        else:
            answer = CREATED
            os.chdir(self.parent)
            print(system("bzr checkout %s %s" % (
                self.url, self.directory)))

        print(' '.join([answer, self.directory]))

    @capture_stdout
    def cmd_out(self):
        os.chdir(self.directory)
        try:
            output = system("bzr missing %s --mine-only" % self.url)
        except CommandError as e:
            if e.returncode == 1:
                # bzr returns 1 if there are outgoing changes!
                print("Unpushed outgoing changes in %s:" % self.directory)
                print(e.output)
                return
            else:
                raise
        print(output)


class HgDirInfo(DirInfo):

    vcs = 'hg'

    regex_changeset = re.compile('changeset:\s+((?P<num>\d+):(?P<digest>[0-9a-fA-F]+))')

    @capture_stdout
    def cmd_rev(self):
        print(self.directory)
        os.chdir(self.directory)
        output = system("hg log -l1")
        lines = [line.strip() for line in output.splitlines()
                 if line.strip()]
        for line in lines:
            m = self.regex_changeset.match(line.lower())
            if m:
                print("{0}:{1}".format(m.group('num'), m.group('digest')))
                return

    @capture_stdout
    def cmd_in(self):
        os.chdir(self.directory)
        try:
            output = system("hg incoming")
            print(self.directory)
            print("'hg incoming' reports incoming changesets :" % (
                  self.directory))
            print(output)
        except CommandError as e:
            if e.returncode == 1:
                # hg returns 1 if there are no incoming changes.
                return
            elif e.returncode == 255:
                # hg returns 255 if there is no default parent.
                pass
            else:
                raise
        return

    @capture_stdout
    def cmd_up(self):
        print(self.directory)
        os.chdir(self.directory)
        print(system("hg pull -u %s" % self.url))

    @capture_stdout
    def cmd_st(self):
        os.chdir(self.directory)
        output = system("hg st")
        if output.strip():
            print(self.directory)
            print(output)
            print()

    @capture_stdout
    def cmd_co(self):
        if not os.path.exists(self.parent):
            print("Creating parent dir %s" % self.parent)
            os.makedirs(self.parent)
        if self.exists:
            answer = PRESENT
        else:
            answer = CREATED
            os.chdir(self.parent)
            # TODO: check!
            print(system("hg clone %s %s" % (
                self.url, self.directory)))

        print(' '.join([answer, self.directory]))

    @capture_stdout
    def cmd_out(self):
        os.chdir(self.directory)
        try:
            output = system("hg out %s" % self.url)
        except CommandError as e:
            if e.returncode == 1:
                # hg returns 1 if there are no outgoing changes!
                # Checkoutmanager is as quiet as possible, so we print
                # nothing.
                return
            else:
                raise
        # No errors means we have genuine outgoing changes.
        print("Unpushed outgoing changes in %s:" % self.directory)
        print(output)


class GitDirInfo(DirInfo):

    vcs = 'git'

    regex_commit_digest = re.compile('commit (?P<digest>[0-9a-fA-F]+)')

    @capture_stdout
    def cmd_rev(self):
        print(self.directory)
        os.chdir(self.directory)
        output = system("git show -q")
        lines = [line.strip() for line in output.splitlines()
                 if line.strip()]
        for line in lines:
            m = self.regex_commit_digest.match(line.lower())
            if m:
                print(m.group('object'))
                return

    @capture_stdout
    def cmd_in(self):
        output = system("git pull --dry-run")
        output = output.strip()
        output_lines = output.split('\n')
        if output and len(output_lines):
            print("'git pull --dry-run' reports possible actions in %s:" % (
                self.directory))
            print(output)

    @capture_stdout
    def cmd_up(self):
        print(self.directory)
        os.chdir(self.directory)
        print(system("git pull"))

    @capture_stdout
    def cmd_st(self):
        os.chdir(self.directory)
        output = system("git status --short")
        if output.strip():
            print(self.directory)
            print(output)
            print()

    @capture_stdout
    def cmd_co(self):
        if not os.path.exists(self.parent):
            print("Creating parent dir %s" % self.parent)
            os.makedirs(self.parent)
        if self.exists:
            answer = PRESENT
        else:
            answer = CREATED
            os.chdir(self.parent)
            # TODO: check!
            print(system("git clone %s %s" % (
                self.url, self.directory)))

        print(' '.join([answer, self.directory]))

    @capture_stdout
    def cmd_out(self):
        os.chdir(self.directory)
        output = system("git push --dry-run")
        output = output.strip()
        output_lines = output.split('\n')
        if len(output_lines) > 1:
            # More than the 'everything up-to-date' one-liner.
            print("'git push --dry-run' reports possible actions in %s:" % (
                self.directory))
            print(output)
