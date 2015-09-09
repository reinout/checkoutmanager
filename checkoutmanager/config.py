"""Config file parsing and massaging"""
from __future__ import print_function
from __future__ import unicode_literals
from six.moves import configparser
import glob
import os

from checkoutmanager import dirinfo


DEFAULTS = {'report-missing': 'true',
            'ignore': '',
            'preserve_tree': '',
            }


def linesstring_as_list(string):
    """Return \n separated string as a list"""
    lines = string.split('\n')
    lines = [line.strip() for line in lines]
    lines = [line for line in lines
             if line and not line.startswith('#')]
    return lines


def extract_spec(spec, preserve_tree=None):
    """Extract vcs spec into vcs url and directoryname"""
    vcs_url = None
    directory = None
    parts = spec.split()
    assert len(parts) <= 2, spec
    if len(parts) == 2:
        vcs_url = parts[0]
        directory = parts[1]
    if len(parts) == 1:
        vcs_url = parts[0]
    if directory is None:
        # preserve_tree provides a list of server_roots.
        # If there are no defined server_roots, this effectively
        # disables te preserve_tree option and the directoy is
        # obtained per usual
        server_roots = preserve_tree or []
        for server_root in server_roots:
            if vcs_url.startswith(server_root):
                directory = vcs_url[len(server_root):]
                break
        if directory is None:
            parts = [part for part in vcs_url.split('/')
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
    return vcs_url, directory


class Config(object):
    """Wrapper around config file for returning DirInfo objects"""

    def __init__(self, config_filename):
        assert os.path.exists(config_filename)  # Just for me atm...
        self.config_filename = config_filename
        self.parser = configparser.SafeConfigParser(DEFAULTS)
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
            preserve_tree = linesstring_as_list(
                self.parser.get(section, 'preserve_tree'))
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
                url, directory = extract_spec(checkout, preserve_tree)
                directory = os.path.join(basedir, directory)
                directory = os.path.expanduser(directory)
                result.append(dirinfoclass(directory, url))
        return sorted(result)

    def directory_from_url(self, url):
        for dir_info in self.directories():
            if dir_info.url == url:
                return dir_info

    def directory_from_path(self, abspath, allow_ancestors=True):
        for dir_info in self.directories():
            if dir_info.directory == abspath:
                return dir_info
        if allow_ancestors:
            parent = os.path.dirname(abspath)
            if parent:
                return self.directory_from_path(parent)

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
                print("Unconfigured items in %s [%s]:" % (
                    basedir, self.parser.get(section, 'vcs')))
                for full in real_missing:
                    print("    " + full)
