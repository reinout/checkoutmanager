Changelog of checkoutmanager
============================

2.7 (2021-09-28)
----------------

- More robust error handling.
  [mortenlj]


2.6.1 (2019-09-23)
------------------

- Fixed small, but essential, README error.


2.6 (2019-09-10)
----------------

- Updated the setup (mostly: buildout version pins) so that the project can be
  developed/tested again.

- The ``exists`` and ``co`` command used to check only if a directory
  existed. Now it also checks if the dot directory (``.git``, ``.svn``)
  exists. This way an empty directory also will get filled with a checkout.


2.5 (2016-11-07)
----------------

- Fix #19: sometimes git remote changes were seen where there were none.
  [reinout]


2.4.1 (2015-09-10)
------------------

- Bugfix for the 2.4-introduced ``run_one()`` function.
  [chintal]


2.4 (2015-09-09)
----------------

- Added ``in`` command that reports incoming changes (so: the changes you'd
  get by running ``checkoutmanager up``). Due to differences between versions
  of git/svn/hg/bzr, the reporting might not be entirely accurate. It is
  *very* hard to get right. So: please `report an issue
  <https://github.com/reinout/checkoutmanager/issues>`_ if something is not
  quite right.
  [chintal]

- Added better support for using checkoutmanager as a library. Provided you
  first load a config file, you can now programmatically run actions on
  individual directories or urls. See the source code for the
  ``checkoutmanager.runner.run_one()`` function.
  [chintal]


2.3 (2015-09-08)
----------------

- Added a preserve_tree option to config files to allow structured
  checkouts mirroring the repository tree.
  [chintal]


2.2 (2015-08-24)
----------------

- Checkoutmanager now also runs **on python 3**!
  [reinout]

- Moved from bitbucket (https://bitbucket.org/reinout/checkoutmanager) to
  github (https://github.com/reinout/checkoutmanager).
  [reinout]


2.1 (2015-08-18)
----------------

- Fixed ``missing`` command: do not swallow the output when
  looking for not yet checked out items.  Fixes issue #24.
  [maurits]


2.0 (2015-03-25)
----------------

- Huge speed increase because commands are now run in parallel instead of
  sequentially. Great fix by Morten Lied Johansen. For me, "checkoutmanager
  up" now takes 19 seconds instead of 105 seconds!


1.17 (2015-02-06)
-----------------

- Added support for custom commands: now you can write an extension for
  checkoutmanager so that you can run ``checkoutmanager
  your_custom_command``. See the README for documentation. Patch by Rafael
  Oliveira.


1.16 (2015-01-02)
-----------------

- Added globbing support for ignores.


1.15 (2013-09-27)
-----------------

- Handle corner case in determining directory name for a git clone.


1.14 (2013-08-12)
-----------------

- Added ``--force-interactive`` to ``svn info`` for svn version 1.8
  and higher. This is for the "hidden" ``instancemanager info``
  command that is handy for updating your repositories when you've
  switched svn versions. (See the changelog entry for 1.10). Patch by
  Maurits.


1.13 (2012-07-20)
-----------------

- Not using the sample config file as the test config file anymore. This means
  there's a much nicer and more useful sample config file now.

  (Thanks Craig Blaszczyk for his pull request that was the basis for this!)


1.12 (2012-04-14)
-----------------

- For bzr, the "out" command uses the exit code instead of the command output
  now. This is more reliable and comfortable. Fix by Jendrik Seipp, thanks!


1.11 (2012-03-20)
-----------------

- Allow more than one vcs in a directory.  This was already possible
  before, but now known you no longer need to list all the checkouts
  of the competing vcs in the ignore option.  Also, items that are
  ignored in one section are now also ignored in other sections for
  the same directory.
  Fixes #11.
  [maurits]


1.10 (2012-01-16)
-----------------

- Using --mine-only option to ``bzr missing`` to only show our outgoing
  changesets when running checkoutmanager's "out" command for bzr.

- Copying sample .cfg file if it doesn't exist instead of only suggesting the
  copy. Fixes #12.

- Added hidden info command.  Should be only useful for subversion if
  your svn program is updated and your OS requires you to give svn
  access to your stored credentials again, for each repository.
  [maurits]


1.9 (2011-11-08)
----------------

- Added ``upgrade`` command that upgrades your subversion checkouts to
  the new 1.7 layout of the ``.svn`` directory.
  [maurits]


1.8 (2011-10-13)
----------------

- Using ``git push --dry-run`` now to detect not-yet-pushed outgoing changes
  with ``checkoutmanager out``. Fixes #9 (reported by Maurits van Rees).


1.7 (2011-10-06)
----------------

- Added --configfile option. Useful when you want to use checkoutmanager to
  manage checkouts for something else than your regular development projects.
  In practice: I want to use it for an 'sdistmaker' that works with git.


1.6 (2010-12-27)
----------------

- Full fix for #7: checkoutmanager doesn't stop on the first error, but
  continues.  And it reports all errors afterwards.  This helps when just one
  of your svn/hg/whatever servers is down: the rest will just keep working.

- Partial fix for #7: ``svn up`` runs with ``--non-interactive`` now, so
  conflict errors errors are reported instead of pretty much silently waiting
  for interactive input that will never come.


1.5 (2010-09-14)
----------------

- Using ``except CommandError, e`` instead of ``except CommandError as e`` for
  python2.4 compatibility.


1.4 (2010-08-17)
----------------

- Added git support (patch by Robert Kern: thanks!)  Fixes issue #6.


1.3 (2010-08-09)
----------------

- Added new "out" action that shows changesets not found in the default push
  location of a repository for a dvcs (hg, bzr).  The action doesn't make
  sense for svn, so it is ignored for svn checkouts.  Fixes issue #1.  Thanks
  Dmitrii Miliaev for this fix!


1.2.1 (2010-08-06)
------------------

- Bugfix: when reporting an error, the os.getcwd method itself would get
  printed instead of the *output* of os.getcwd()...


1.2 (2010-08-04)
----------------

- If the config file doesn't exist, just print the config file hints instead
  of the generic usage info.

- Fixed issue #4: the generic 'buildout' name is stripped from the path.
  svn://somewhere/customername/buildout/trunk is a common pattern.

- Added -v option that prints the commands and the directory where you execute
  them.  Fixes issue #3.

- Reporting on not yet checked out items when running "checkoutmanager
  missing".  Fixes issue #2.

- Checking return code from executed commands.  On error, the command and
  working directory is printed and also the output.  And the script stops
  right away.  Fixes #5.

- Updated the documentation, for instance by mentioning the config file name
  and location.


1.1 (2010-08-02)
----------------

- Switched from "commands" module to "subprocesses" for windows
  compatibility.


1.0 (2010-08-01)
----------------

- Small fixes.  It works great in practice.

- Moved from bzr to hg and made it public on bitbucket.org.

- Big documentation update as I'm going to release it.


0.1 (2010-05-07)
----------------

- First reasonably working version.

- Initial library skeleton created by thaskel.
