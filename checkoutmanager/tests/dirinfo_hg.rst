
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

Make yourself a folder inside which all hg tests will run:

    >>> hg_repos_root = os.path.join(homedir, 'repos_hg')
    >>> os.makedirs(hg_repos_root)
    >>> print(hg_repos_root)
    HOMEDIR/repos_hg

Initialize hg:

    >>> with open(os.path.join(homedir, '.hgrc'), 'w') as f:
    ...     f.writelines("[ui]\n")
    ...     f.writelines("username = Some Tester <someone@test.test\n")

Create a hg repository:

    >>> hg_base = os.path.join(hg_repos_root, 'base')
    >>> os.makedirs(hg_base)
    >>> cmd = ['hg', 'init', hg_base]
    >>> subprocess.call(cmd)
    0

Create a file inside the base working copy and commit:

    >>> os.chdir(hg_base)
    >>> with open(os.path.join(hg_base, 'test_file'), 'w+') as f:
    ...     f.writelines('Foo')
    >>> cmd = ['hg', 'add', 'test_file']
    >>> subprocess.call(cmd)
    0
    >>> cmd = ['hg', 'commit', '-m', '\"one commit\"']
    >>> subprocess.call(cmd)
    0

Create the other working copies using checkoutmanager:

    >>> hg_follower = os.path.join(hg_repos_root, 'follower')
    >>> hg_leader = os.path.join(hg_repos_root, 'leader')
    >>> from checkoutmanager import runner
    >>> executor = runner.run_one('co', directory=hg_follower, conf=conf)
    >>> # TODO Test Executor for CO Action
    >>> assert executor.errors == []
    >>> executor = runner.run_one('co', directory=hg_leader, conf=conf)
    >>> assert executor.errors == []

Create commit on base to bring it ahead of the follower:

    >>> os.chdir(hg_base)
    >>> with open(os.path.join(hg_base, 'test_file_2'), 'w+') as f:
    ...     f.writelines('Foo')
    >>> # TODO Run and Test for ST Action
    >>> cmd = ['hg', 'add', 'test_file_2']
    >>> subprocess.call(cmd)
    >>> cmd = ['hg', 'commit', '-m', '\"second commit\"']
    >>> subprocess.call(cmd)

Update leader to bring it alongside base:

    >>> from checkoutmanager import runner
    >>> executor = runner.run_one('up', directory=hg_leader, conf=conf)
    >>> # TODO Test Executor for UP Action

Create commit on leader to bring it ahead of the base:

    >>> os.chdir(hg_leader)
    >>> with open(os.path.join(hg_leader, 'test_file_3'), 'w+') as f:
    ...     f.writelines('Foo')
    >>> # TODO Run and Test for ST Action
    >>> cmd = ['hg', 'add', 'test_file_3']
    >>> subprocess.call(cmd)
    >>> cmd = ['hg', 'commit', '-m', '\"third commit\"']
    >>> subprocess.call(cmd)

The follower - leader - base hierarchy is now setup.

Teardown:

    >>> os.chdir(orig_cwd)



