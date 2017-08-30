Anaconda Installation
=====================
This section describes installation via Anaconda Python's package manager,
``conda``.  If you want to do a direct install, you want the previous chapter.


If you don't have Anaconda Python installed, get it by visiting the URL
https://www.continuum.io/downloads.  ``lorax`` was tested under version 3.6 of
Anaconda Python. As of this writing, there is no compelling reason to use
earlier or later versions.  You must use a 64-bit version.  The command-line
installer version is fine, and 25% smaller.  When you have downloaded the installer,
issue the following command from a terminal window in the Downloads directory::

        bash Anaconda3-<version>-<platform>.sh

where ``<version>`` is the current version number and ``<platform`` is your OS.
As part of installation, please ensure that the Anaconda Python ``bin/``
directory is prepended to your PATH (in ``~/.bash_profile`` on the Mac) or else
you will have to prepend it manually before continuing the installation and
every time you wish to use ``lorax``.

Configure channels
------------------
lorax requires some packages that are in non-default channels, which
may be obtained by the following::

	conda config --add channels conda-forge
	conda config --add channels defaults
	conda config --add channels bioconda

After the channels are configured, update the installation by issuing::

	conda update --all

This command usually results in several packages being updated.

Create a virtualenv
-------------------
It is not advisable to install ``lorax`` in the root environment because
lorax's dependencies could break other packages.  As of the current conda
version (4.3.25), there are four packages in the channels that are too old
for use with lorax:

=========== ================ ================
Package     Anaconda Version Required Version
=========== ================ ================
setuptools  27.2.0           >30.3.0
markupsafe  0.23             1.0.0
gunicorn    19.1.0           19.7.1
supervisor  3.3.2            4.0 (from git)
=========== ================ ================

Replacing setuptools, in particular, could cause breakage of your root
Anaconda Python distribution. For this reason, it is required to create a
python virtual environment for lorax and its dependencies. I prefer to name
this environment "loraxenv" to prevent confusion between package and
environment names.  You should create this environment as the user under which
you intend the web server to run (using ``sudo -u USER`` if necessary),
using the following commands::

	conda create -y --name loraxenv biopython click hmmer raxml redis nginx
	source activate loraxenv

Install gcc if using MacOSX
---------------------------
If you are installing under MacOS (and only under MacOS), gcc and libgcc
MUST be installed in the current virtual environment::

	conda install -y gcc libgcc

Failure to do this step will result in a message to the effect "Unable to
resolve paths in MacOS executable" in the lorax installation step 
later.

Upgrade setuptools
------------------
Next continue the installation by updating setuptools and installing a special
version of supervisord from a git repository. The first will end with an error;
this is expected, so don't be worried by it::

	pip install -U setuptools
	pip install -e 'git+https://github.com/LegumeFederation/supervisor.git@4.0.0#egg=supervisor==4.0.0'

Choose root location
--------------------
When lorax installs itself, it will place some files in the ``bin/`` and ``etc/``
subdirectories of ``LORAX_ROOT``.  Normally ``LORAX_ROOT`` is set to the same directory
as parent of the python installation in use (that is, in ``sys.prefix``).  This
is usually fine for most installations, but if you wish to override it,
you must define ``LORAX_ROOT`` before installation::

    export LORAX_ROOT=some_directory_you_choose

Install lorax
-------------
Next, install the lorax dependencies and binaries::

	pip install -U lorax

Put lorax_env script in alias or on path
----------------------------------------
The lorax_env script is the only executable that you will need to control
lorax and associated process. You should usually not put the entire lorax
bin/ directory into your path, as this may cause binaries from the virtual
environment such as python to be used in contexts where they were not intended
to be used.  The easiest way to do this is with a symlink to a directory
on your path, such as the Anaconda Python directory::

	ln -s /path/to/anaconda/envs/loraxenv/bin/lorax_env /path/to/anaconda/bin

Deactivate virtual environment
------------------------------
You no longer need to work inside the virtual environment you created.  Leave
the virtual environment with the following command::

   source deactivate

Next, follow the configuration instructions.
