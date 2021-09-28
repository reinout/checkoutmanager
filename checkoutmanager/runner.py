from __future__ import print_function
from __future__ import unicode_literals
from functools import partial
from optparse import OptionParser
import os
import shutil
import sys

import pkg_resources

from checkoutmanager import config
from checkoutmanager import utils
from checkoutmanager.executors import get_executor

from checkoutmanager.dirinfo import DirInfo


ACTIONS = ['exists', 'up', 'st', 'co', 'missing', 'out', 'in', 'rev']
CONFIGFILE_NAME = '~/.checkoutmanager.cfg'
ACTION_EXPLANATION = {
    'exists': "Print whether checkouts are present or missing",
    'up': "Grab latest version from the server.",
    'st': "Print status of files in the checkouts",
    'co': "Grab missing checkouts from the server",
    'missing': "Print directories that are missing from the config file",
    'out': "Show changesets you haven't pushed to the server yet",
    'in': "Show incoming changesets that would be pulled in with 'up'",
    'rev': "Print the current revision number",
    }


def parse_action_name(action_name):
    """Parse an action name possibly containing arguments.

    Given an `action_name` in the form "name:arg1=val1,arg2=val2" return a
    tuple (name, args_dict), where `args_dict` maps from arguments names to
    values.

    """
    parts = action_name.split(':')
    name = parts[0]
    args_str = ''
    if len(parts) >= 2:
        args_str = parts[1]

    if not args_str:
        args_dict = {}
    else:
        args_list = [a.split('=') for a in args_str.split(',')]
        args_dict = dict((a[0], a[1]) for a in args_list)

    return (name, args_dict)


def get_action(dirinfo, custom_actions, action_name):
    """Return a tuple (action_func, kwargs) or raise RuntimeError if the action is
    not found."""
    (action_name, args_dict) = parse_action_name(action_name)

    action_func = getattr(dirinfo, 'cmd_' + action_name, None)
    if action_func is not None:
        return (action_func, args_dict)

    custom_action_func = custom_actions.get(action_name, None)
    if custom_action_func is not None:
        action_func = partial(custom_action_func, dirinfo)
        return (action_func, args_dict)

    raise RuntimeError('Invalid action: ' + action_name)


def get_custom_actions():
    return dict(
        (entrypoint.name, entrypoint.load())
        for entrypoint in pkg_resources.iter_entry_points(
            group='checkoutmanager.custom_actions'
        )
    )


def execute_action(dirinfo, custom_actions, action):
    (action_func, args_dict) = get_action(dirinfo, custom_actions, action)
    try:
        return action_func(**args_dict)
    except utils.CommandError as e:
        return e


def run_one(action, directory=None, url=None, conf=None, allow_ancestors=True):
    custom_actions = get_custom_actions()
    if not conf:
        conf = config.Config(os.path.expanduser(CONFIGFILE_NAME))
    dir_info = None
    if url:
        dir_info = conf.directory_from_url(url)
    if directory:
        if isinstance(directory, DirInfo):
            dir_info = directory
        else:
            dir_info = conf.directory_from_path(directory, allow_ancestors)
    if not dir_info:
        raise RuntimeError(
            'Could not find the repository for %s!' % (directory or url))
    executor = get_executor(single=True)
    executor.execute(execute_action, (dir_info, custom_actions, action))
    executor.wait_for_results()
    return executor


def run(action, group=None, conf=None, single=False):
    custom_actions = get_custom_actions()
    if not conf:
        conf = config.Config(os.path.expanduser(CONFIGFILE_NAME))
    executor = get_executor(single)
    for dirinfo in conf.directories(group=group):
        executor.execute(execute_action, (dirinfo, custom_actions, action))
    executor.wait_for_results()

    return executor


def main():
    usage = ["Usage: %prog action [group]",
             "  group (optional) is a heading from your config file.",
             "  action can be " + '/'.join(ACTIONS) + ":\n"]
    # Add automatic action explanations.
    usage += [action + "\n  " + ACTION_EXPLANATION[action] + "\n"
              for action in ACTIONS]
    usage = "\n".join(usage)
    parser = OptionParser(usage=usage)
    parser.add_option("-v", "--verbose",
                      action="store_true", dest="verbose", default=False,
                      help="Show debug output")
    parser.add_option("-c", "--configfile",
                      action="store",
                      dest="configfile",
                      default=CONFIGFILE_NAME,
                      help="Name of config file [%s]" % CONFIGFILE_NAME)
    parser.add_option("-s", "--single",
                      action="store_true", dest="single", default=False,
                      help="Execute actions in a single process")
    (options, args) = parser.parse_args()
    if options.verbose:
        utils.VERBOSE = True

    configfile = os.path.expanduser(options.configfile)
    if utils.VERBOSE:
        print("Using config file %s" % configfile)
    if not os.path.exists(configfile):
        print("Config file %s does not exist." % configfile)
        sample = pkg_resources.resource_filename('checkoutmanager',
                                                 'sample.cfg')
        shutil.copy(sample, configfile)
        print("Copied %s as a sample to %s" % (sample, configfile))
        print("Open it and adjust it to what you need.")
        return

    if len(args) < 1:
        parser.print_help()
        return
    action = args[0]
    # TODO: check actions

    conf = config.Config(configfile)

    group = None
    if len(args) > 1:
        group = args[1]
        if group not in conf.groupings:
            print("Group %s not in %r" % (group, conf.groupings))
            return

    if action == 'missing':
        print("Looking for items missing in the config file...")
        # Special case: report unconfigured items.
        conf.report_missing(group=group)
        # Also report on not-yet-checked-out items.
        print()
        print("Looking for not yet checked out items...")
        for dirinfo in conf.directories(group=group):
            output = dirinfo.cmd_exists(report_only_missing=True)
            if output:
                print(output)
        print("(Run 'checkoutmanager co' if found)")
        return

    executor = run(action,
                   group=group,
                   conf=conf,
                   single=options.single)

    if executor.errors:
        print()
        print("### %s ERRORS OCCURED ###" % len(executor.errors))
        for error in executor.errors:
            print()
            utils.print_exception(error)
        sys.exit(1)
