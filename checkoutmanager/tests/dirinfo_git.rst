
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

Make yourself a folder inside which all git tests will run:

    >>> git_repos_root = os.path.join(homedir, 'repos_git')
    >>> os.makedirs(git_repos_root)
    >>> print(git_repos_root)
    HOMEDIR/repos_git

Initialize git:

    >>> cmd = ['git', 'config', '--global', 'user.email', '\"someone@test.test\"']
    >>> subprocess.call(cmd)
    0
    >>> cmd = ['git', 'config', '--global', 'user.name', '\"Some Tester\"']
    >>> subprocess.call(cmd)
    0

Create a git repository:

    >>> git_base = os.path.join(git_repos_root, 'base')
    >>> os.makedirs(git_base)
    >>> cmd = ['git', 'init', git_base]
    >>> subprocess.call(cmd)
    0

Create a file inside the base working copy and commit:

    >>> os.chdir(git_base)
    >>> with open(os.path.join(git_base, 'test_file'), 'w+') as f:
    ...     f.writelines('Foo')
    >>> cmd = ['git', 'add', 'test_file']
    >>> subprocess.call(cmd)
    0
    >>> cmd = ['git', 'commit', '-m', '\"one commit\"']
    >>> subprocess.call(cmd)
    0

Create the other working copies using checkoutmanager:

    >>> git_follower = os.path.join(git_repos_root, 'follower')
    >>> git_leader = os.path.join(git_repos_root, 'leader')
    >>> from checkoutmanager import runner
    >>> executor = runner.run_one('co', directory=git_follower, conf=conf)
    >>> # TODO Test Executor for CO Action
    >>> assert executor.errors == []
    >>> executor = runner.run_one('co', directory=git_leader, conf=conf)
    >>> assert executor.errors == []

Create commit on base to bring it ahead of the follower:

    >>> os.chdir(git_base)
    >>> with open(os.path.join(git_base, 'test_file_2'), 'w+') as f:
    ...     f.writelines('Foo')
    >>> # TODO Run and Test for ST Action
    >>> cmd = ['git', 'add', 'test_file_2']
    >>> subprocess.call(cmd)
    >>> cmd = ['git', 'commit', '-m', '\"second commit\"']
    >>> subprocess.call(cmd)

Update leader to bring it alongside base:

    >>> from checkoutmanager import runner
    >>> executor = runner.run_one('up', directory=git_leader, conf=conf)
    >>> # TODO Test Executor for UP Action

Create commit on leader to bring it ahead of the base:

    >>> os.chdir(git_leader)
    >>> with open(os.path.join(git_leader, 'test_file_3'), 'w+') as f:
    ...     f.writelines('Foo')
    >>> # TODO Run and Test for ST Action
    >>> cmd = ['git', 'add', 'test_file_3']
    >>> subprocess.call(cmd)
    >>> cmd = ['git', 'commit', '-m', '\"third commit\"']
    >>> subprocess.call(cmd)

The follower - leader - base hierarchy is now setup.

Tests for the 'rev' dirinfo action:

    >>> from checkoutmanager import reports
    >>> executor = runner.run_one('rev', directory=git_base, conf=conf)
    >>> assert isinstance(executor.reports, list)
    >>> assert len(executor.reports) == 1
    >>> assert isinstance(executor.reports[0], reports.ReportRevision)
    >>> assert isinstance(executor.reports[0].revision, str)
    >>> executor = runner.run_one('rev', directory=git_leader, conf=conf)
    >>> assert isinstance(executor.reports, list)
    >>> assert len(executor.reports) == 1
    >>> assert isinstance(executor.reports[0], reports.ReportRevision)
    >>> assert isinstance(executor.reports[0].revision, str)
    >>> executor = runner.run_one('rev', directory=git_follower, conf=conf)
    >>> assert isinstance(executor.reports, list)
    >>> assert len(executor.reports) == 1
    >>> assert isinstance(executor.reports[0], reports.ReportRevision)
    >>> assert isinstance(executor.reports[0].revision, str)
    >>> # TODO handle error conditons

Tests for the 'in' dirinfo action:

    >>> executor = runner.run_one('in', directory=git_follower, conf=conf)
    >>> assert isinstance(executor.reports, list)
    >>> assert len(executor.errors) == 0
    >>> if len(executor.parse_errors):
    ...     for error in executor.parse_errors:
    ...         error.print_msg()
    >>> assert len(executor.parse_errors) == 0
    >>> assert len(executor.reports) == 1
    >>> assert isinstance(executor.reports[0], reports.ReportIncoming)
    >>> assert isinstance(executor.reports[0].local_head, str)
    >>> assert isinstance(executor.reports[0].remote_head, str)
    >>> assert len(executor.reports[0].changesets) == 0

Teardown:

    >>> os.chdir(orig_cwd)



