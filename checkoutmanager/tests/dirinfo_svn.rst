
.. :doctest:

    >>> import subprocess
    >>> import os
    >>> from checkoutmanager.dirinfo import SvnDirInfo
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

Make yourself a folder inside which all SVN tests will run:

    >>> svn_repos_root = os.path.join(homedir, 'repos_svn')
    >>> os.makedirs(svn_repos_root)
    >>> print(svn_repos_root)
    HOMEDIR/repos_svn

Create an SVN repository:

    >>> svn_upstream = os.path.join(svn_repos_root, 'a_repo')
    >>> cmd = ['svnadmin', 'create', '--fs-type', 'fsfs', svn_upstream]
    >>> subprocess.call(cmd)
    0

Create the working copies using checkoutmanager:

    >>> svn_wc2 = os.path.join(svn_repos_root, 'wc2')
    >>> svn_wc1 = os.path.join(svn_repos_root, 'wc1')
    >>> from checkoutmanager import runner
    >>> from checkoutmanager import reports
    >>> executor = runner.run_one('co', directory=svn_wc1, conf=conf)
    >>> assert executor.errors == []
    >>> assert executor.parse_errors == []
    >>> print(executor.parse_errors)
    >>> assert isinstance(executor.reports, list)
    >>> assert len(executor.reports) == 1
    >>> assert isinstance(executor.reports[0], reports.ReportCheckout)
    >>> executor = runner.run_one('co', directory=svn_wc2, conf=conf)
    >>> assert executor.errors == []
    >>> assert executor.parse_errors == []
    >>> assert isinstance(executor.reports, list)
    >>> assert len(executor.reports) == 1
    >>> assert isinstance(executor.reports[0], reports.ReportCheckout)

Create a file inside the first working copy and commit:

    >>> os.chdir(svn_wc1)
    >>> with open(os.path.join(svn_wc1, 'test_file'), 'w+') as f:
    ...     f.writelines('Foo')
    >>> cmd = ['svn', 'add', 'test_file']
    >>> subprocess.call(cmd)
    >>> cmd = ['svn', 'ci', '-m', '\"one commit\"']
    >>> subprocess.call(cmd)
    >>> # SVN needs an up before the revision changes in the source
    >>> # working copy.
    >>> cmd = ['svn', 'up']
    >>> subprocess.call(cmd)

Tests for the 'rev' dirinfo action:

    >>> from checkoutmanager import reports
    >>> executor = runner.run_one('rev', directory=svn_wc1, conf=conf)
    >>> assert isinstance(executor.reports, list)
    >>> assert len(executor.reports) == 1
    >>> assert isinstance(executor.reports[0], reports.ReportRevision)
    >>> assert executor.reports[0].revision == 1
    >>> executor = runner.run_one('rev', directory=svn_wc2, conf=conf)
    >>> assert isinstance(executor.reports, list)
    >>> assert len(executor.reports) == 1
    >>> assert isinstance(executor.reports[0], reports.ReportRevision)
    >>> assert executor.reports[0].revision == 0
    >>> # TODO handle error conditons

Tests for the 'in' dirinfo action:

    >>> executor = runner.run_one('in', directory=svn_wc2, conf=conf)
    >>> assert isinstance(executor.reports, list)
    >>> assert len(executor.errors) == 0
    >>> if len(executor.parse_errors):
    ...     for error in executor.parse_errors:
    ...         error.print_msg()
    >>> assert len(executor.parse_errors) == 0
    >>> assert len(executor.reports) == 1
    >>> assert isinstance(executor.reports[0], reports.ReportIncoming)
    >>> assert executor.reports[0].local_head == 0
    >>> assert executor.reports[0].remote_head == 1
    >>> assert len(executor.reports[0].changesets) == 1
    >>> assert executor.reports[0].changesets[0] == 1


Teardown:

    >>> os.chdir(orig_cwd)



