"""Config file parsing and massaging"""
import ConfigParser
import glob
import os

from checkoutmanager import dirinfo


DEFAULTS = {'report-missing': 'true',
            'ignore': ''}


def linesstring_as_list(string):
    """Return \n separated string as a list"""
    lines = string.split('\n')
    lines = [line.strip() for line in lines]
    lines = [line for line in lines
             if line and not line.startswith('#')]
    return lines


def extract_spec(spec):
    """Extract vcs spec into vcs url and directoryname"""
    vcs = None
    directory = None
    parts = spec.split()
    assert len(parts) <= 2, spec
    if len(parts) == 2:
        vcs = parts[0]
        directory = parts[1]
    if len(parts) == 1:
        vcs = parts[0]
    if directory is None:
        parts = [part for part in vcs.split('/')
                 if part]
        # Common structure: having a customer folder with a 'buildout'
        # directory in it.  Don't name it 'buildout'.
        parts = [part for part in parts if part != 'buildout']
        directory = parts[-1]
        # Remove /trunk from the end.  We don't want that as a name.
        if parts[-1] == 'trunk':
            parts.pop()
            directory = parts[-1]
        # If we have an svn branch, name it after the project *and* the
        # branch.
        if (len(parts) > 3) and (parts[-2] == 'branches'):
            branchname = parts[-1]
            projectname = parts[-3]
            directory = projectname + '-' + branchname
        # Common for bzr projects hosted on launchpad: they're prefixed with
        # 'lp:'.  Remove that from the name.
        if directory.startswith('lp:'):
            directory = directory[3:]
        if directory.endswith('.git'):
            directory = directory[:-4]
        if ':' in directory:
            # For example git@git.example.org:projectname
            directory = directory.split(':')[-1]
    return vcs, directory


class Config(object):
    """Wrapper around config file for returning DirInfo objects"""

    def __init__(self, config_filename):
        assert os.path.exists(config_filename)  # Just for me atm...
        self.config_filename = config_filename
        self.parser = ConfigParser.SafeConfigParser(DEFAULTS)
        self.parser.read(config_filename)

    @property
    def groupings(self):
        return sorted(self.parser.sections())

    def directories(self, group=None):
        """Return wrapped directories"""
        result = []
        if group:
            sections = [group]
        else:
            sections = self.groupings
        for section in sections:
            basedir = self.parser.get(section, 'basedir')
            vcs = self.parser.get(section, 'vcs')
            dirinfoclass = dirinfo.DirInfo
            if vcs == 'svn':
                dirinfoclass = dirinfo.SvnDirInfo
            if vcs == 'bzr':
                dirinfoclass = dirinfo.BzrDirInfo
            if vcs == 'hg':
                dirinfoclass = dirinfo.HgDirInfo
            if vcs == 'git':
                dirinfoclass = dirinfo.GitDirInfo
            checkouts = linesstring_as_list(
                self.parser.get(section, 'checkouts'))
            for checkout in checkouts:
                url, directory = extract_spec(checkout)
                directory = os.path.join(basedir, directory)
                directory = os.path.expanduser(directory)
                result.append(dirinfoclass(directory, url))
        return sorted(result)

    def report_missing(self, group=None):
        if group:
            sections = [group]
        else:
            sections = self.groupings
        # First get the currently configured items.  Note that one
        # directory can now contain checkouts from more than one vcs.
        base_configured = {}
        base_ignored = {}
        for section in sections:
            checkouts = linesstring_as_list(
                self.parser.get(section, 'checkouts'))
            configured = []
            for checkout in checkouts:
                url, directory = extract_spec(checkout)
                configured.append(directory)
            basedir = self.parser.get(section, 'basedir')
            basedir = os.path.realpath(os.path.expanduser(basedir))
            if basedir not in base_configured:
                base_configured[basedir] = []
            base_configured[basedir] += configured
            ignore = linesstring_as_list(
                self.parser.get(section, 'ignore'))
            if basedir not in base_ignored:
                base_ignored[basedir] = []
            base_ignored[basedir] += ignore

        # Now get present and missing items.
        for section in sections:
            if not self.parser.getboolean(section, 'report-missing'):
                continue
            basedir = self.parser.get(section, 'basedir')
            basedir = os.path.realpath(os.path.expanduser(basedir))
            present = set(os.listdir(basedir))
            configured = set(base_configured[basedir])
            missing = present - configured
            if not missing:
                continue

            ignores = base_ignored[basedir]
            full_paths_to_ignore = []
            for ignore in ignores:
                full_paths_to_ignore += glob.glob(
                    os.path.join(basedir, ignore))
            real_missing = []
            for directory in missing:
                full = os.path.join(basedir, directory)
                if full in full_paths_to_ignore:
                    continue
                if os.path.isfile(full):
                    # Files cannot be checkouts, so we ignore
                    # them. We only deal with directories.
                    continue
                real_missing.append(full)
            if real_missing:
                print "Unconfigured items in %s [%s]:" % (
                    basedir, self.parser.get(section, 'vcs'))
                for full in real_missing:
                    print "    " + full
