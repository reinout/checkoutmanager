from optparse import OptionParser
import os
import shutil
import sys

import pkg_resources

from checkoutmanager import config
from checkoutmanager import utils

ACTIONS = ['exists', 'up', 'st', 'co', 'missing', 'out']
CONFIGFILE_NAME = '~/.checkoutmanager.cfg'
ACTION_EXPLANATION = {
    'exists': "Print whether checkouts are present or missing",
    'up': "Grab latest version from the server.",
    'st': "Print status of files in the checkouts",
    'co': "Grab missing checkouts from the server",
    'missing': "Print directories that are missing from the config file",
    'out': "Show changesets you haven't pushed to the server yet",
    }


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
    (options, args) = parser.parse_args()
    if options.verbose:
        utils.VERBOSE = True

    configfile = os.path.expanduser(options.configfile)
    if utils.VERBOSE:
        print "Using config file %s" % configfile
    if not os.path.exists(configfile):
        print "Config file %s does not exist." % configfile
        sample = pkg_resources.resource_filename('checkoutmanager.tests',
                                                 'sample.cfg')
        shutil.copy(sample, configfile)
        print "Copied %s as a sample to %s" % (sample, configfile)
        print "Open it and adjust it to what you need."
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
            print "Group %s not in %r" % (group, conf.groupings)
            return

    if action == 'missing':
        # Special case: report unconfigured items.
        conf.report_missing(group=group)
        # Also report on not-yet-checked-out items.
        print
        print "Looking for not yet checked out items..."
        for dirinfo in conf.directories(group=group):
            dirinfo.cmd_exists(report_only_missing=True)
        print "(Run 'checkoutmanager co' if found)"
        return

    errors = []
    for dirinfo in conf.directories(group=group):
        try:
            getattr(dirinfo, 'cmd_' + action)()
        except utils.CommandError, e:
            # An error occured!  Don't bail out directly but collect errors.
            errors.append(e)
            e.print_msg()

    if errors:
        print
        print "### %s ERRORS OCCURED ###" % len(errors)
        for error in errors:
            print
            error.print_msg()
        sys.exit(1)
