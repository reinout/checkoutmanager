Checkoutmanager
===============

Makes bzr/hg/git/svn checkouts in several places according to a
``.checkoutmanager.cfg`` config file (in your home directory).

The advantage: you've got one command with which you can update all your
checkouts.  And with which you can ask for a list of uncommitted changes.  And
you can rebuild your entire checkout structure on a new machine just by
copying the config file (this was actually the purpose I build it for: I had
to change laptops when I switched jobs...).

Checkoutmanager works on linux, osx and windows.


Starting to use it
------------------

Starting is easy.  Just ``easy_install checkoutmanager`` and run
``checkoutmanager``.

- The first time, you'll get a sample configuration you can copy to
  ``.checkoutmanager.cfg`` in your home directory.

- The second time, you'll get a usage message.  (You'll want to do
  ``checkoutmanager co`` to grab your initial checkouts).


Generic usage
-------------

What I normally do every morning when I get to work is ``checkoutmanager
up``.  This grabs the latest versions of all my checkouts from the server(s).
So an ``svn up`` for my subversion checkouts, a ``hg pull -u`` for mercurial
and so on.

From time to time, I'll do a ``checkoutmanager st`` to show if I've got some
uncommitted files lying around somewhere.  Very handy if you've worked in
several directories throughout the day: it prevents you from forgetting to
check in that one bugfix for a whole week.

A new project means I add a single line to my config file and run
``checkoutmanager co``.

Checkoutmanager allows you to spread your checkouts over multiple
directories.  It cannot mix version control systems per directory, however.
As an example, I've got a ``~/buildout/`` directory with my big svn website
projects checked out there.  And a directory with my svn work python
libraries.  And a ``~/hg/`` dir with my mercurial projects.  And I've made
checkouts of several config directories in my home dir, such as
``~/.emacs.d``, ``~/.subversion`` and so on.  Works just fine.


Commands
--------

Available commands:

exists
  Print whether checkouts are present or missing

up
  Grab latest version from the server.

st
  Print status of files in the checkouts

co
  Grab missing checkouts from the server

missing
  Print directories that are missing from the config file


Hidden commands
---------------

A few commands are hidden because they are seldom used and are only
useful for subversion.

upgrade
  This upgrades the working copy to the new subversion 1.7 layout of
  the .svn directory.  This should be done once after you have
  upgraded your subversion to 1.7.  Note that when you accidentally
  run this twice you get an error, but nothing breaks.  Since this
  command is so rarely needed, it is not advertised in the command
  line help.

info
  Display the svn info for the remote url.  This is useful when your
  svn program has been updated and the security mechanisms on your OS
  now require you to explictly allow access to the stored credentials.
  The other commands either do not access the internet or are
  non-interactive (like command up).  In fact, the reason for adding
  this command is that a non-interactive 'svn update' will fail when
  you have not granted access to your credentials yet for this new svn
  program.  This has happened a bit too often for me (Maurits).


Output directory naming
-----------------------

If you don't specify an output directory name for your checkout url, it just
takes the last part.  Some exceptions, most for subversion:

- ``https://xxx/yyy/product/trunk`` becomes "product" instead of "trunk".

- ``https://xxx/yyy/product/branches/experiment`` becomes "product_experiment"
  instead of "experiment"

- ``https://xxx/customername/buildout/trunk`` becomes "customername"
  instead of "trunk" or "buildout".

- Bzr checkouts that start with "lp:" (special launchpad urls) get their "lp:"
  stripped.

- Git checkouts lose the ".git" at the end of the url.

If you want something else, just specify a directory name (separated by a
space) in the configuration file.


Config file
-----------

.. Comment: the config file is included into the long description by setup.py,
   it is in checkoutmanager/tests/sample.cfg!

Sample configuration file::
