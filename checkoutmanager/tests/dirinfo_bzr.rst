
.. :doctest:

    >>> import subprocess
    >>> import os
    >>> from checkoutmanager.dirinfo import GitDirInfo
    >>> orig_cwd = os.getcwd()

The tests will all run inside the homedir which the testsetup made for us:

    >>> print(homedir)
    HOMEDIR

Create the config file:

    >>> vcstest_config_path = os.path.join(homedir, 'vcstestconfig.cfg')
    >>> import pkg_resources
    >>> vcstest_config_tpath = pkg_resources.resource_filename(
    ...     'checkoutmanager.tests', 'vcstestconfig.cfg.templ')
    >>> with open(vcstest_config_tpath, 'r') as f:
    ...     vcstest_config_tstr = str(f.read())
    >>> import jinja2
    >>> vcstest_config_t = jinja2.Template(vcstest_config_tstr)
    >>> with open(vcstest_config_path, 'w') as f:
    ...     lc = f.write(vcstest_config_t.render(homedir=homedir))
    >>> from checkoutmanager import config
    >>> conf = config.Config(vcstest_config_path)

Make yourself a folder inside which all bzr tests will run:

    >>> bzr_repos_root = os.path.join(homedir, 'repos_bzr')
    >>> os.makedirs(bzr_repos_root)
    >>> print(bzr_repos_root)
    HOMEDIR/repos_bzr

Initialize bzr:

    >>> cmd = ['bzr', 'whoami', '\"Some Tester <someone@test.test>\"']
    >>> subprocess.call(cmd)
    0


Create a bzr repository:

    >>> bzr_base = os.path.join(bzr_repos_root, 'base')
    >>> os.makedirs(bzr_base)
    >>> cmd = ['bzr', 'init', bzr_base]
    >>> subprocess.call(cmd)
    0

Create a file inside the base working copy and commit:

    >>> os.chdir(bzr_base)
    >>> with open(os.path.join(bzr_base, 'test_file'), 'w+') as f:
    ...     f.writelines('Foo')
    >>> cmd = ['bzr', 'add', 'test_file']
    >>> subprocess.call(cmd)
    0
    >>> cmd = ['bzr', 'commit', '-m', '\"one commit\"']
    >>> subprocess.call(cmd)
    0

Create the other working copies using checkoutmanager:

    >>> bzr_follower = os.path.join(bzr_repos_root, 'follower')
    >>> bzr_leader = os.path.join(bzr_repos_root, 'leader')
    >>> from checkoutmanager import runner
    >>> executor = runner.run_one('co', directory=bzr_follower, conf=conf)
    >>> # TODO Test Executor for CO Action
    >>> assert executor.errors == []
    >>> executor = runner.run_one('co', directory=bzr_leader, conf=conf)
    >>> assert executor.errors == []

Create commit on base to bring it ahead of the follower:

    >>> os.chdir(bzr_base)
    >>> with open(os.path.join(bzr_base, 'test_file_2'), 'w+') as f:
    ...     f.writelines('Foo')
    >>> # TODO Run and Test for ST Action
    >>> cmd = ['bzr', 'add', 'test_file_2']
    >>> subprocess.call(cmd)
    >>> cmd = ['bzr', 'commit', '-m', '\"second commit\"']
    >>> subprocess.call(cmd)

Update leader to bring it alongside base:

    >>> from checkoutmanager import runner
    >>> executor = runner.run_one('up', directory=bzr_leader, conf=conf)
    >>> # TODO Test Executor for UP Action

Create commit on leader to bring it ahead of the base:

    >>> os.chdir(bzr_leader)
    >>> with open(os.path.join(bzr_leader, 'test_file_3'), 'w+') as f:
    ...     f.writelines('Foo')
    >>> # TODO Run and Test for ST Action
    >>> cmd = ['bzr', 'add', 'test_file_3']
    >>> subprocess.call(cmd)
    >>> cmd = ['bzr', 'commit', '-m', '\"third commit\"']
    >>> subprocess.call(cmd)

The follower - leader - base hierarchy is now setup.

Teardown:

    >>> os.chdir(orig_cwd)



