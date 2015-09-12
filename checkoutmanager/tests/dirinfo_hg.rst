
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

Test the 'co' dirinfo action. Create the other working copies using checkoutmanager:

    >>> hg_follower = os.path.join(hg_repos_root, 'follower')
    >>> hg_leader = os.path.join(hg_repos_root, 'leader')
    >>> from checkoutmanager import runner
    >>> from checkoutmanager import reports
    >>> executor = runner.run_one('co', directory=hg_follower, conf=conf)
    >>> assert executor.errors == []
    >>> assert executor.parse_errors == []
    >>> assert isinstance(executor.reports, list)
    >>> assert len(executor.reports) == 1
    >>> assert isinstance(executor.reports[0], reports.ReportCheckout)
    >>> executor = runner.run_one('co', directory=hg_leader, conf=conf)
    >>> assert executor.errors == []
    >>> assert executor.parse_errors == []
    >>> assert isinstance(executor.reports, list)
    >>> assert len(executor.reports) == 1
    >>> assert isinstance(executor.reports[0], reports.ReportCheckout)

Test the 'st' dirinfo action. Create commit on base to bring it ahead of the follower:

    >>> os.chdir(hg_base)
    >>> with open(os.path.join(hg_base, 'test_file_2'), 'w+') as f:
    ...     f.writelines('Foo')
    >>> executor = runner.run_one('st', directory=hg_base, conf=conf)
    >>> assert len(executor.errors) == 0
    >>> assert len(executor.parse_errors) == 0
    >>> assert len(executor.reports) == 1
    >>> report = executor.reports[0]
    >>> assert isinstance(report, reports.ReportStatus)
    >>> assert len(report.changes) == 1
    >>> change = report.changes[0]
    >>> assert isinstance(change, reports.FileStatus)
    >>> assert change.filepath == 'test_file_2'
    >>> assert change.status == '?'
    >>> assert not change.moreinfo
    >>> cmd = ['hg', 'add', 'test_file_2']
    >>> subprocess.call(cmd)
    >>> executor = runner.run_one('st', directory=hg_base, conf=conf)
    >>> assert len(executor.errors) == 0
    >>> assert len(executor.parse_errors) == 0
    >>> assert len(executor.reports) == 1
    >>> report = executor.reports[0]
    >>> assert isinstance(report, reports.ReportStatus)
    >>> assert len(report.changes) == 1
    >>> change = report.changes[0]
    >>> assert isinstance(change, reports.FileStatus)
    >>> assert change.filepath == 'test_file_2'
    >>> assert change.status == 'A'
    >>> assert not change.moreinfo
    >>> cmd = ['hg', 'commit', '-m', '\"second commit\"']
    >>> subprocess.call(cmd)
    >>> executor = runner.run_one('st', directory=hg_base, conf=conf)
    >>> assert len(executor.errors) == 0
    >>> assert len(executor.parse_errors) == 0
    >>> assert len(executor.reports) == 0

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

Tests for the 'rev' dirinfo action:

    >>> from checkoutmanager import reports
    >>> executor = runner.run_one('rev', directory=hg_base, conf=conf)
    >>> assert isinstance(executor.reports, list)
    >>> assert len(executor.reports) == 1
    >>> assert isinstance(executor.reports[0], reports.ReportRevision)
    >>> assert executor.reports[0].revision.startswith('1:')
    >>> executor = runner.run_one('rev', directory=hg_leader, conf=conf)
    >>> assert isinstance(executor.reports, list)
    >>> assert len(executor.reports) == 1
    >>> assert isinstance(executor.reports[0], reports.ReportRevision)
    >>> assert executor.reports[0].revision.startswith('2:')
    >>> executor = runner.run_one('rev', directory=hg_follower, conf=conf)
    >>> assert isinstance(executor.reports, list)
    >>> assert len(executor.reports) == 1
    >>> assert isinstance(executor.reports[0], reports.ReportRevision)
    >>> assert executor.reports[0].revision.startswith('0:')
    >>> # TODO handle error conditons

Tests for the 'in' dirinfo action:

    >>> executor = runner.run_one('in', directory=hg_follower, conf=conf)
    >>> assert isinstance(executor.reports, list)
    >>> assert len(executor.errors) == 0
    >>> if len(executor.parse_errors):
    ...     for error in executor.parse_errors:
    ...         error.print_msg()
    >>> assert len(executor.parse_errors) == 0
    >>> assert len(executor.reports) == 1
    >>> assert isinstance(executor.reports[0], reports.ReportIncoming)
    >>> assert executor.reports[0].local_head.startswith('0:')
    >>> assert executor.reports[0].remote_head.startswith('1:')
    >>> assert len(executor.reports[0].changesets) == 1
    >>> assert executor.reports[0].changesets[0].startswith('1:')

Tests for the 'out' dirinfo action:

    >>> executor = runner.run_one('out', directory=hg_leader, conf=conf)
    >>> assert isinstance(executor.reports, list)
    >>> assert len(executor.errors) == 0
    >>> if len(executor.parse_errors):
    ...     for error in executor.parse_errors:
    ...         error.print_msg()
    >>> assert len(executor.parse_errors) == 0
    >>> assert len(executor.reports) == 1
    >>> assert isinstance(executor.reports[0], reports.ReportOutgoing)
    >>> assert executor.reports[0].local_head.startswith('2:')
    >>> assert not executor.reports[0].remote_head
    >>> assert len(executor.reports[0].changesets) == 1
    >>> assert executor.reports[0].changesets[0].startswith('2:')


Teardown:

    >>> os.chdir(orig_cwd)



