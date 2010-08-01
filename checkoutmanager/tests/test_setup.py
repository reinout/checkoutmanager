import os
import re
import shutil
import tempfile

import z3c.testsetup
from zope.testing import renormalizing

checker = renormalizing.RENormalizing([
    # Mock homedir in temp.
    (re.compile(
        '%s[^/]+' % re.escape(
            os.path.join(tempfile.gettempdir(), 'homedir'))),
     'HOMEDIR'),
    ])


def setup(test):
    test.homedir = tempfile.mkdtemp(prefix='homedir')
    test.orig_home = os.environ.get('HOME')
    os.environ['HOME'] = test.homedir
    test.globs['homedir'] = test.homedir


def teardown(test):
    shutil.rmtree(test.homedir)
    os.environ['HOME'] = test.orig_home


test_suite = z3c.testsetup.register_all_tests(
    'checkoutmanager',
    setup=setup,
    teardown=teardown,
    checker=checker,
    )
