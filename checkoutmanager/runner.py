from optparse import OptionParser
import os

import pkg_resources

from checkoutmanager import config

ACTIONS = ['exists', 'up', 'st', 'co', 'missing']
CONFIGFILE_NAME = '~/.checkoutmanager.cfg'


def main():
    usage = ("Usage: %prog action [group]\n"
             "  action can be " + '/'.join(ACTIONS))
    parser = OptionParser(usage=usage)
    (options, args) = parser.parse_args()
    if len(args) < 1:
        parser.print_help()
        return
    action = args[0]
    # TODO: check actions

    configfile = os.path.expanduser(CONFIGFILE_NAME)
    if not os.path.exists(configfile):
        print "Config file %s does not exist." % configfile
        print "Copy %s as a sample" % pkg_resources.resource_filename(
            'checkoutmanager.tests', 'sample.cfg')
        return

    conf = config.Config(configfile)

    group = None
    if len(args) > 1:
        group = args[1]
        if group not in conf.groupings:
            print "Group %s not in %r" % (group, conf.groupings)
            return

    if action == 'missing':
        # Special case
        conf.report_missing(group=group)
        return

    for dirinfo in conf.directories(group=group):
        getattr(dirinfo, 'cmd_' + action)()
