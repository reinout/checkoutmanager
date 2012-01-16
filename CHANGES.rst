Changelog of checkoutmanager
============================

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
