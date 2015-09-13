"""Information on one directory"""
from __future__ import print_function
from __future__ import unicode_literals
import os
import re

from checkoutmanager.utils import CommandError
from checkoutmanager.utils import capture_stdout
from checkoutmanager.utils import system
from checkoutmanager import reports

# 8-char codes
#         '12345678'
CREATED = 'created '
MISSING = 'missing '
PRESENT = 'present '


class DirInfo(object):
    """Wrapper for information on one directory"""

    vcs = 'xxx'
    rev_type = str

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
        return os.path.exists(self.directory)

    @capture_stdout
    def cmd_exists(self, report_only_missing=False):
        if self.exists:
            answer = PRESENT
            if report_only_missing:
                return
        else:
            answer = MISSING
        print(' '.join([answer, self.directory]))

    def parse_exists(self, output):
        parts = output.split(' ', 1)
        parts = [x.strip() for x in parts]
        if parts[1] == self.directory:
            if parts[0].upper() == 'PRESENT':
                return reports.ReportExists(self, True)
            if parts[0].upper() == 'ABSENT':
                return reports.ReportExists(self, False)
        else:
            raise reports.DirectoryMismatchError(self, parts[1])

    def cmd_rev(self):
        raise NotImplementedError()

    def parse_rev(self, output):
        lines = output.splitlines()
        lines = [x.strip() for x in lines if x]
        if lines[0] == self.directory:
            try:
                return reports.ReportRevision(self, self.rev_type(lines[1]))
            except IndexError:
                raise reports.LineNotFoundError(self, 'Revision Line')
            except ValueError:
                raise reports.LineParseError(self, lines[1], self.rev_type)
        else:
            raise reports.DirectoryMismatchError(self, lines[0])

    def cmd_in(self):
        raise NotImplementedError()

    def parse_in(self, output):
        pass

    def cmd_up(self):
        raise NotImplementedError()

    def parse_up(self, output):
        pass

    def cmd_st(self):
        raise NotImplementedError()

    def parse_st(self, output):
        pass

    def cmd_co(self):
        raise NotImplementedError()

    def parse_co(self, output):
        lines = output.splitlines()
        lines = [x.strip() for x in lines if x.strip()]
        try:
            line = lines[-1]
        except IndexError:
            raise reports.LineNotFoundError(self, "Checkout Result")
        result, path = line.split(' ', 1)
        if path.strip() != self.directory:
            raise reports.DirectoryMismatchError(self, path)
        if result.upper() == 'PRESENT':
            raise reports.LogicalParseError(
                self, output, "We expected the checkout to not exist!"
            )
        elif result.upper() == 'CREATED':
            return reports.ReportCheckout(self)
        else:
            raise reports.LogicalParseError(
                self, output, "Result isn't where we expect it to be.")

    def cmd_out(self):
        raise NotImplementedError()

    def parse_out(self, output):
        pass

    def cmd_upgrade(self):
        # This is only useful for subversion.
        pass

    def parse_upgrade(self, output):
        pass

    def cmd_info(self):
        # This is only known to be useful for subversion.
        pass

    def parse_info(self, output):
        pass


class SvnDirInfo(DirInfo):

    vcs = 'svn'
    rev_type = int

    regex_last_changed = re.compile(r'last changed rev: (?P<rev>\d+)')

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

    regex_incoming = re.compile(r'Revision (?P<local>\d+) to (?P<remote>\d+)')

    def parse_in(self, output):
        if not output.strip():
            return
        lines = output.splitlines()
        lines = [x.strip() for x in lines if x]
        if lines[0] == self.directory:
            try:
                if lines[1].startswith("Incoming changes :"):
                    m = self.regex_incoming.search(lines[1])
                    if not m:
                        raise reports.LineParseError(self, lines[1],
                                                     self.regex_incoming.pattern)
                    local_rev = int(m.group('local'))
                    remote_rev = int(m.group('remote'))
                    return reports.ReportIncoming(self, local_rev, remote_rev,
                                                  range(local_rev+1,
                                                        remote_rev+1))
            except IndexError:
                raise reports.LineNotFoundError(self, "Incoming Changes Line")
        elif lines[0].startswith("Could not connect to repository for "):
            return
        else:
            raise reports.DirectoryMismatchError(self, lines[0])

    @capture_stdout
    def cmd_up(self):
        print(self.directory)
        os.chdir(self.directory)
        print(system("svn up --non-interactive"))

    regex_up_change = re.compile(r'^(?P<change>(?P<item>[ADUCGER ])(?P<prop>[ADUCGER ])(?P<lock>[B ])(?P<treeconflict>[C ])) (?P<path>.+)$')
    regex_up_result = re.compile(r'^(Updated to revision (?P<final_rev>\d+).)|(At revision \d+.)$')

    def parse_up(self, output):
        if not output.strip():
            return
        lines = output.splitlines()
        lines = [x.strip() for x in lines if x.strip()]
        if not lines[0] == self.directory:
            raise reports.DirectoryMismatchError(self, lines[0])
        result = self.regex_up_result.match(lines[-1])
        if not result:
            raise reports.LineParseError(self, lines[-1], self.regex_up_result.pattern)
        if not result.group('final_rev'):
            return
        final_head = self.rev_type(result.group('final_rev'))
        initial_head = None
        changes = []
        for line in lines[1:-1]:
            if line.startswith('Updating'):
                continue
            m = self.regex_up_change.match(line)
            if not m:
                raise reports.LineParseError(self, line, self.regex_up_change.pattern)
            changes.append((m.group('path'), m.group('change'), None))
        return reports.ReportUpdate(self, initial_head, final_head, changes)

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

    regex_change = re.compile(r'^(?P<change>(?P<item>[ACDIMRX?!~ ])(?P<prop>[CM ])(?P<elock>[L ])(?P<sched>[+ ])(?P<sx>[SX ])(?P<lock>[ KOTB])(?P<conflict>[C ]))\s+(?P<path>.+)$')

    def parse_st(self, output):
        if not output.strip():
            return
        lines = output.splitlines()
        lines = [x.strip() for x in lines if x.strip()]
        if not lines[0] == self.directory:
            raise reports.DirectoryMismatchError(self, lines[0])
        try:
            changes = []
            change_lines = lines[1:]
            while len(change_lines):
                line = change_lines.pop(0)
                m = self.regex_change.match(line)
                if not m:
                    raise reports.LineParseError(self, line,
                                                 self.regex_change.pattern)
                path = m.group('path')
                change = m.group('change')
                if m.group('conflict') == 'C':
                    moreinfo = change_lines.pop(0)
                else:
                    moreinfo = None
                changes.append((path, change, moreinfo))
            return reports.ReportStatus(self, changes)
        except IndexError:
            raise reports.LineNotFoundError(self, "No change line found")

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
    rev_type = int

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

    regex_revno = re.compile(r'^revno: (?P<revno>\d+)$')

    def parse_in(self, output):
        if not output.strip():
            return
        lines = output.splitlines()
        lines = [x.strip() for x in lines if x]
        if not lines[0] == self.directory:
            raise reports.DirectoryMismatchError(self, lines[0])
        try:
            if lines[1].startswith("'bzr missing' reports incoming "
                                   "changesets :"):
                local_rev = self.parse_rev(self.cmd_rev()).revision
                changesets = []
            else:
                raise reports.LineParseError(
                    self, lines[1], "'bzr missing' reports incoming changesets :")
        except IndexError:
            raise reports.LineNotFoundError(self, "Incoming Changes Line")
        try:
            for line in lines[2:]:
                m = self.regex_revno.match(line)
                if m:
                    changesets.append(int(m.group('revno')))
        except IndexError:
            raise reports.LogicalParseError(
                self, output, "Expected changesets but got no lines")
        if not len(changesets):
            raise reports.LineParseError(
                self, lines[2:],
                'Unable to extract any incoming changesets')
        remote_rev = changesets[-1]
        return reports.ReportIncoming(self, local_rev, remote_rev,
                                      changesets)

    @capture_stdout
    def cmd_up(self):
        print(self.directory)
        os.chdir(self.directory)
        print(system("bzr up"))

    def parse_up(self, output):
        # cmd_up should first be changed to bzr pull if up on bzr
        # is to behave as all the others. Since people seem to be
        # using it as it is, I suppose I'm missing something. This
        # implementation is therefore left empty for the moment.
        return

    @capture_stdout
    def cmd_st(self):
        os.chdir(self.directory)
        output = system("bzr st")
        if output.strip():
            print(self.directory)
            print(output)
            print()

    regex_change_head = re.compile(r'^(?P<change>[a-z]+):$')

    def parse_st(self, output):
        if not output.strip():
            return
        lines = output.splitlines()
        if not lines[0].strip() == self.directory:
            raise reports.DirectoryMismatchError(self, lines[0])
        try:
            changes = []
            change_lines = lines[1:]
            while len(change_lines):
                line = change_lines.pop(0)
                m = self.regex_change_head.match(line)
                if m:
                    change = m.group('change')
                elif line:
                    path = line.strip()
                    if not change:
                        raise reports.LogicalParseError(
                            self, output, "Got file before change head.")
                    changes.append((path, change, None))
                else:
                    pass
            return reports.ReportStatus(self, changes)
        except IndexError:
            raise reports.LineNotFoundError(self, "No change line found")

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

    def parse_out(self, output):
        if not output.strip():
            return
        lines = output.splitlines()
        lines = [x.strip() for x in lines if x]
        try:
            if lines[0].startswith("Unpushed outgoing changes in"):
                local_rev = self.parse_rev(self.cmd_rev()).revision
                changesets = []
            else:
                raise reports.LineParseError(
                    self, lines[0], "Unpushed outgoing changes in")
        except IndexError:
            raise reports.LineNotFoundError(self, "Outgoing Changes Line")
        if not lines[0][:-1].endswith(self.directory):
            raise reports.DirectoryMismatchError(self, lines[0])
        try:
            for line in lines[2:]:
                m = self.regex_revno.match(line)
                if m:
                    changesets.append(int(m.group('revno')))
        except IndexError:
            raise reports.LogicalParseError(
                self, output, "Expected changesets but got no lines")
        if not len(changesets):
            raise reports.LineParseError(
                self, lines[2:],
                'Unable to extract any outgoing changesets')
        # TODO Check if this actually holds. It might not.
        # remote_rev = changesets[-1] - 1
        # And until a resolution is found:
        remote_rev = None
        return reports.ReportOutgoing(self, local_rev, remote_rev,
                                      changesets)


class HgDirInfo(DirInfo):

    vcs = 'hg'
    rev_type = str

    regex_changeset = re.compile(r'changeset:\s+((?P<num>\d+):(?P<digest>[0-9a-fA-F]+))')

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
            print("'hg incoming' reports incoming changesets :")
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

    def parse_in(self, output):
        if not output.strip():
            return
        lines = output.splitlines()
        lines = [x.strip() for x in lines if x]
        if not lines[0] == self.directory:
            raise reports.DirectoryMismatchError(self, lines[0])
        try:
            if not lines[1].startswith("'hg incoming' reports incoming "
                                       "changesets :"):
                raise reports.LineParseError(
                    self, lines[1], "'hg incoming' reports incoming changesets :")
        except IndexError:
            raise reports.LineNotFoundError(self, "Incoming Changes Line")
        local_rev = self.parse_rev(self.cmd_rev()).revision
        changesets = []
        for line in lines[2:]:
            m = self.regex_changeset.match(line)
            if m:
                changesets.append(m.group(1))
        if not len(changesets):
            raise reports.LineParseError(
                self, lines[2:],
                'Unable to extract any incoming changesets')
        remote_rev = changesets[-1]
        return reports.ReportIncoming(self, local_rev, remote_rev,
                                      changesets)

    @capture_stdout
    def cmd_up(self):
        print(self.directory)
        os.chdir(self.directory)
        print(system("hg pull -u %s" % self.url))

    regex_pull_summary = re.compile(r'^((?P<nfiles>\d+) files updated, (?P<nmerged>\d+) files merged, (?P<nremoved>\d+) files removed, (?P<nunresolved>\d+) files unresolved)|(?P<nochange>no changes found)$')

    def parse_up(self, output):
        if not output.strip():
            return
        lines = output.splitlines()
        lines = [x.strip() for x in lines if x.strip()]
        if not lines[0] == self.directory:
            raise reports.DirectoryMismatchError(self, lines[0])
        if not lines[2] == 'searching for changes':
            raise reports.LineNotFoundError(self, "searching for changes")
        result = self.regex_pull_summary.match(lines[-1])
        if not result:
            raise reports.LineParseError(self, lines[-1], self.regex_pull_summary.pattern)
        if result.group('nochange'):
            return
        final_head = self.parse_rev(self.cmd_rev()).revision
        initial_head = None
        changes = []
        if result.group('nfiles'):
            for i in range(int(result.group('nfiles'))):
                changes.append((None, 'updated', None))
        if result.group('nmerged'):
            for i in range(int(result.group('nmerged'))):
                changes.append((None, 'merged', None))
        if result.group('nremoved'):
            for i in range(int(result.group('nremoved'))):
                changes.append((None, 'removed', None))
        if result.group('nunresolved'):
            for i in range(int(result.group('nunresolved'))):
                changes.append((None, 'unresolved', None))
        return reports.ReportUpdate(self, initial_head, final_head, changes)

    @capture_stdout
    def cmd_st(self):
        os.chdir(self.directory)
        output = system("hg st")
        if output.strip():
            print(self.directory)
            print(output)
            print()

    regex_change = re.compile(r'^(?P<change>[MARC!?I ])\s+(?P<path>.+)$')

    def parse_st(self, output):
        if not output.strip():
            return
        lines = output.splitlines()
        lines = [x.strip() for x in lines if x.strip()]
        if not lines[0] == self.directory:
            raise reports.DirectoryMismatchError(self, lines[0])
        try:
            changes = []
            change_lines = lines[1:]
            while len(change_lines):
                line = change_lines.pop(0)
                m = self.regex_change.match(line)
                if not m:
                    raise reports.LineParseError(self, line,
                                                 self.regex_change.pattern)
                path = m.group('path')
                change = m.group('change')
                moreinfo = None
                changes.append((path, change, moreinfo))
            return reports.ReportStatus(self, changes)
        except IndexError:
            raise reports.LineNotFoundError(self, "No change line found")

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

    def parse_out(self, output):
        if not output.strip():
            return
        lines = output.splitlines()
        lines = [x.strip() for x in lines if x]
        try:
            if not lines[0].startswith("Unpushed outgoing changes in"):
                raise reports.LineParseError(
                    self, lines[1], "Unpushed outgoing changes in")
        except IndexError:
            raise reports.LineNotFoundError(self, "Outgoing Changes Line")
        if not lines[0][:-1].endswith(self.directory):
            raise reports.DirectoryMismatchError(self, lines[0])
        local_rev = self.parse_rev(self.cmd_rev()).revision
        changesets = []
        for line in lines[2:]:
            m = self.regex_changeset.match(line)
            if m:
                changesets.append(m.group(1))
        if not len(changesets):
            raise reports.LineParseError(
                self, lines[2:],
                'Unable to extract any outgoing changesets')
        # TODO Obtain remote revision?
        remote_rev = None
        return reports.ReportOutgoing(self, local_rev, remote_rev,
                                      changesets)


class GitDirInfo(DirInfo):

    vcs = 'git'
    rev_type = str

    regex_commit_digest = re.compile(r'commit (?P<digest>[0-9a-fA-F]+)')

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
                print(m.group('digest'))
                return

    @capture_stdout
    def cmd_in(self):
        output = system("git pull --dry-run")
        output = output.strip()
        output_lines = output.split('\n')
        if len(output_lines):
            print(self.directory)
            print("'git pull --dry-run' reports possible actions : ")
            print(output)

    regex_pull_result = re.compile(r'(?P<start>[0-9a-fA-F]+)..(?P<end>[0-9a-fA-F]+)\s+(?P<local>[\w\/]+)\s+->\s+(?P<remote>[\w\/]+)')

    def parse_in(self, output):
        if not output.strip():
            return
        lines = output.splitlines()
        lines = [x.strip() for x in lines if x]
        if not lines[0] == self.directory:
            raise reports.DirectoryMismatchError(self, lines[0])
        try:
            if not lines[1].startswith("'git pull --dry-run' reports "
                                   "possible actions :"):
                raise reports.LineParseError(
                    self, lines[1],
                    "'git pull --dry-run' reports possible actions :")
        except IndexError:
            raise reports.LineNotFoundError(self, "Incoming Changes Line")

        local_rev = None
        # TODO see if the list of changesets can be obtained
        changesets = []
        for line in lines[2:]:
            m = self.regex_pull_result.match(line)
            if m:
                if not local_rev:
                    local_rev = m.group('start')
                    remote_rev = m.group('end')
                    return reports.ReportIncoming(self, local_rev, remote_rev,
                                                  changesets)
                else:
                    raise reports.LogicalParseError(
                        self, output,
                        "Got two pull results, expecting only one")

    @capture_stdout
    def cmd_up(self):
        print(self.directory)
        os.chdir(self.directory)
        print(system("git pull"))

    regex_pull_summary = p = re.compile(r'^(?P<nfiles>\d+) file(s)? changed(, (?P<ninsertions>\d+) insertion(s)?\(\+\))?(, (?P<ndeletions>\d+) deletion(s)?\(-\))?$')

    def parse_up(self, output):
        if not output.strip():
            return
        lines = output.splitlines()
        lines = [x.strip() for x in lines if x.strip()]
        if not lines[0] == self.directory:
            raise reports.DirectoryMismatchError(self, lines[0])
        if len(lines) == 2:
            return
        m = None
        for line in lines:
            m = self.regex_pull_result.match(line)
            if m:
                break
        if not m:
            raise reports.LineNotFoundError(self, "git pull result")
        result = m
        if not result:
            raise reports.LineParseError(self, lines[2], self.regex_pull_result.pattern)
        m = None
        for line in lines:
            m = self.regex_pull_summary.match(line)
            if m:
                break
        if not m:
            raise reports.LineNotFoundError(self, "git pull changes summary")
        nchanges = int(m.group('nfiles'))
        final_head = self.rev_type(result.group('end'))
        initial_head = self.rev_type(result.group('start'))
        changes = []
        for line in lines:
            if '|' in line:
                path, change = line.split('|')
                changes.append((path.strip(), change.strip(), None))
        if nchanges != len(changes):
            raise reports.LogicalParseError(
                self, output, "Got change count differs from summary")
        return reports.ReportUpdate(self, initial_head, final_head, changes)

    @capture_stdout
    def cmd_st(self):
        os.chdir(self.directory)
        output = system("git status --porcelain")
        if output.strip():
            print(self.directory)
            print(output)
            print()

    regex_change = re.compile(r'^(?P<change>[MADRCU?! ][MADRCU?! ])\s(?P<path>.+)$')

    def parse_st(self, output):
        if not output.strip():
            return
        lines = output.splitlines()
        lines = [x.strip() for x in lines if x.strip()]
        if not lines[0] == self.directory:
            raise reports.DirectoryMismatchError(self, lines[0])
        try:
            changes = []
            change_lines = lines[1:]
            while len(change_lines):
                line = change_lines.pop(0)
                m = self.regex_change.match(line)
                if not m:
                    raise reports.LineParseError(self, line,
                                                 self.regex_change.pattern)
                path = m.group('path')
                try:
                    path, moreinfo = path.split('->')
                except ValueError:
                    moreinfo = None
                change = m.group('change')
                changes.append((path, change, moreinfo))
            return reports.ReportStatus(self, changes)
        except IndexError:
            raise reports.LineNotFoundError(self, "No change line found")

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

    def parse_out(self, output):
        if not output.strip():
            return
        lines = output.splitlines()
        lines = [x.strip() for x in lines if x]
        try:
            if not lines[0].startswith("'git push --dry-run' reports "
                                       "possible actions in"):
                raise reports.LineParseError(
                    self, lines[1],
                    "'git push --dry-run' reports possible actions in")
        except IndexError:
            raise reports.LineNotFoundError(self, "Outgoing Changes Line")
        if not lines[0][:-1].endswith(self.directory):
            raise reports.DirectoryMismatchError(self, lines[0])
        local_rev = None
        # TODO see if the list of changesets can be obtained?
        changesets = []
        for line in lines[1:]:
            m = self.regex_pull_result.match(line)
            if m:
                if not local_rev:
                    local_rev = m.group('end')
                    remote_rev = m.group('start')
                    return reports.ReportOutgoing(self, local_rev, remote_rev,
                                                  changesets)
                else:
                    raise reports.LogicalParseError(
                        self, output,
                        "Got two push results, expecting only one")
        # TODO handle 'fetch first' and similar conditions?
        return reports.ReportOutgoing(self, None, None, None)
