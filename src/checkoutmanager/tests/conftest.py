import os
from pathlib import Path

import pytest


@pytest.fixture()
def homedir_in_tmp(tmp_path: Path):
    homedir = tmp_path / "homedir"
    homedir.mkdir()
    orig_home = os.environ["HOME"]
    os.environ["HOME"] = str(homedir)
    yield homedir
    os.environ["HOME"] = orig_home
