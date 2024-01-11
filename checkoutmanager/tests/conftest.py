import os
from pathlib import Path

# import re
# import shutil
import pytest

# import z3c.testsetup
# from zope.testing import renormalizing


@pytest.fixture()
def homedir_in_tmp(tmp_path: Path):
    homedir = tmp_path / "homedir"
    homedir.mkdir()
    orig_home = os.environ["HOME"]
    os.environ["HOME"] = str(homedir)
    yield homedir
    os.environ["HOME"] = orig_home


# checker = renormalizing.RENormalizing(
#     [
#         # Mock homedir in temp (with weird /private prefix for OSX).
#         (re.compile("%s[^/]+" % re.escape("/private" + _tempdir)), "HOMEDIR"),
#         # Mock homedir in temp (regular one).
#         (re.compile("%s[^/]+" % re.escape(_tempdir)), "HOMEDIR"),
#     ]
# )


# def setup(test):
#     test.homedir = tempfile.mkdtemp(prefix="homedir")
#     test.orig_home = os.environ.get("HOME")
#     os.environ["HOME"] = test.homedir
#     test.globs["homedir"] = test.homedir


# def teardown(test):
#     shutil.rmtree(test.homedir)
#     os.environ["HOME"] = test.orig_home


# test_suite = z3c.testsetup.register_all_tests(
#     "checkoutmanager",
#     setup=setup,
#     teardown=teardown,
#     checker=checker,
# )
