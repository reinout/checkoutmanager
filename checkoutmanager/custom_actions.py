"""Custom actions for testing."""
from checkoutmanager import utils


def test_action(dirinfo, **kwargs):
    print 'Test action'
    print 'dirinfo: %s' % dirinfo
    print 'arguments: %s' % ', '.join('%s: %s' % (k, v) for (k, v) in sorted(kwargs.items()))
    print utils.system('echo "echo command executed."')
