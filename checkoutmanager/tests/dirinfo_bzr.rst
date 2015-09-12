
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

Test the 'co' dirinfo action. Create the other working copies using checkoutmanager:

    >>> bzr_follower = os.path.join(bzr_repos_root, 'follower')
    >>> bzr_leader = os.path.join(bzr_repos_root, 'leader')
    >>> from checkoutmanager import runner
    >>> from checkoutmanager import reports
    >>> executor = runner.run_one('co', directory=bzr_follower, conf=conf)
    >>> assert executor.errors == []
    >>> assert executor.parse_errors == []
    >>> assert isinstance(executor.reports, list)
    >>> assert len(executor.reports) == 1
    >>> assert isinstance(executor.reports[0], reports.ReportCheckout)
    >>> executor = runner.run_one('co', directory=bzr_leader, conf=conf)
    >>> assert executor.errors == []
    >>> assert executor.parse_errors == []
    >>> assert isinstance(executor.reports, list)
    >>> assert len(executor.reports) == 1
    >>> assert isinstance(executor.reports[0], reports.ReportCheckout)
    >>> # bzr checkouts are bound. There is probably some scope here
    >>> # for a discussion about the consequences of bzr branch vs bzr checkout,
    >>> # in terms of behavior of in, out, up. It seems bzr checkout is akin to a
    >>> # poor man's SVN, while bzr branch is bzr-as-dvcs.
    >>> cmd = ['bzr', 'unbind']
    >>> os.chdir(bzr_follower)
    >>> subprocess.call(cmd)
    >>> os.chdir(bzr_leader)
    >>> subprocess.call(cmd)

Test the 'st' dirinfo action. Create commit on base to bring it ahead of the follower:

    >>> os.chdir(bzr_base)
    >>> with open(os.path.join(bzr_base, 'test_file_2'), 'w+') as f:
    ...     f.writelines('Foo')
    >>> executor = runner.run_one('st', directory=bzr_base, conf=conf)
    >>> assert len(executor.errors) == 0
    >>> assert len(executor.parse_errors) == 0
    >>> assert len(executor.reports) == 1
    >>> report = executor.reports[0]
    >>> assert isinstance(report, reports.ReportStatus)
    >>> assert len(report.changes) == 1
    >>> change = report.changes[0]
    >>> assert isinstance(change, reports.FileStatus)
    >>> assert change.filepath == 'test_file_2'
    >>> assert change.status == 'unknown'
    >>> assert not change.moreinfo
    >>> cmd = ['bzr', 'add', 'test_file_2']
    >>> subprocess.call(cmd)
    >>> executor = runner.run_one('st', directory=bzr_base, conf=conf)
    >>> assert len(executor.errors) == 0
    >>> assert len(executor.parse_errors) == 0
    >>> assert len(executor.reports) == 1
    >>> report = executor.reports[0]
    >>> assert isinstance(report, reports.ReportStatus)
    >>> assert len(report.changes) == 1
    >>> change = report.changes[0]
    >>> assert isinstance(change, reports.FileStatus)
    >>> assert change.filepath == 'test_file_2'
    >>> assert change.status == 'added'
    >>> assert not change.moreinfo
    >>> cmd = ['bzr', 'commit', '-m', '\"second commit\"']
    >>> subprocess.call(cmd)
    >>> executor = runner.run_one('st', directory=bzr_base, conf=conf)
    >>> assert len(executor.errors) == 0
    >>> assert len(executor.parse_errors) == 0
    >>> assert len(executor.reports) == 0

Update leader to bring it alongside base. Since we unbound the repo, we need to
``pull``, not ``up`` to get the commit here :

    >>> os.chdir(bzr_leader)
    >>> cmd = ['bzr', 'pull', bzr_base]
    >>> subprocess.call(cmd)

Create another commit on leader to bring it ahead of the base:

    >>> os.chdir(bzr_leader)
    >>> assert os.getcwd() == '{0}/repos_bzr/leader'.format(homedir)
    >>> with open(os.path.join(bzr_leader, 'test_file_3'), 'w+') as f:
    ...     f.writelines('Foo')
    >>> # TODO Run and Test for ST Action
    >>> cmd = ['bzr', 'add', 'test_file_3']
    >>> subprocess.call(cmd)
    >>> cmd = ['bzr', 'commit', '-m', '\"third commit\"']
    >>> subprocess.call(cmd)

The follower - leader - base hierarchy is now setup.

Test for the 'rev' dirinfo action:

    >>> executor = runner.run_one('rev', directory=bzr_base, conf=conf)
    >>> assert isinstance(executor.reports, list)
    >>> assert len(executor.reports) == 1
    >>> assert isinstance(executor.reports[0], reports.ReportRevision)
    >>> assert executor.reports[0].revision == 2
    >>> executor = runner.run_one('rev', directory=bzr_leader, conf=conf)
    >>> assert isinstance(executor.reports, list)
    >>> assert len(executor.reports) == 1
    >>> assert isinstance(executor.reports[0], reports.ReportRevision)
    >>> assert executor.reports[0].revision == 3
    >>> executor = runner.run_one('rev', directory=bzr_follower, conf=conf)
    >>> assert isinstance(executor.reports, list)
    >>> assert len(executor.reports) == 1
    >>> assert isinstance(executor.reports[0], reports.ReportRevision)
    >>> assert executor.reports[0].revision == 1
    >>> # TODO handle error conditons

Test for the 'out' dirinfo action:

    >>> executor = runner.run_one('out', directory=bzr_leader, conf=conf)
    >>> assert isinstance(executor.reports, list)
    >>> assert len(executor.reports) == 1
    >>> report = executor.reports[0]
    >>> assert isinstance(report, reports.ReportOutgoing)
    >>> assert report.local_head == 3
    >>> assert not report.remote_head
    >>> assert isinstance(report.changesets, list)
    >>> assert len(report.changesets) == 1
    >>> assert report.changesets[0] == 3

Teardown:

    >>> os.chdir(orig_cwd)



