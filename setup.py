# -*- coding: utf-8 -*-
#
# This file is part of lorax
# Copyright (C) 2017, NCGR.
#
# lorax is free software; you can redistribute it and/or modify
# it under the terms of the 3-Clause BSD License; see LICENSE.txt
# file for more details.
#
"""lorax -- speaks for the (phylogenetic) trees."""
#
# Developers, install with
#    python setup.py develop
#
from distutils.cmd import Command
import distutils.log as logger
from os import environ as environ
import platform
import shutil
import subprocess
import sys
from setuptools import setup, find_packages
from setuptools.command import build_py, develop, install
# restrict to python 3.4 or later
if sys.version_info < (3, 4, 0, 'final', 0):
    raise SystemExit("lorax requires python 3.4 or higher.")
from pathlib import Path  # python 3.4

FASTTREE_BINARY = 'FastTree-lorax'
FASTTREE_PATH = Path('.')/'lorax'/'fasttree'
BINARY_PATH = Path('.')/'lorax'/'bin'

class BuildFasttreeCommand(Command):
  """Compile FastTree with custom switches."""
  description = 'Build FastTree with gcc'
  user_options = [
      # The format is (long option, short option, description).
      ('cc=', None, 'path to c compiler'),
  ]

  def initialize_options(self):
    """Set default values for options."""
    # Each user option must be listed here with their default value.
    self.cc = 'gcc'

  def finalize_options(self):
    """Post-process options."""
    assert shutil.which(self.cc) is not None, (
          'C compiler %s is not found on path.' % self.cc)

  def run(self):
    """Build FastTree with c compiler."""
    # Check if build is disabled by environmental variable.
    if 'LORAX_NO_BINARIES' in environ and\
            environ['LORAX_NO_BINARIES'] == 'True':
        logger.info('skipping compile of FastTree binary')
        return
    if (BINARY_PATH/FASTTREE_BINARY).exists():
        logger.info('FastTree binary already built')
        return
    logger.info('compiling FastTree binary')
    command = [shutil.which(self.cc),
               '-DUSE_DOUBLE',
               '-finline-functions',
               '-funroll-loops',
               '-O3',
               '-march=native',
               '-DOPENMP',
               '-fopenmp',
               '-lm',
               '-o',
               '../bin/'+FASTTREE_BINARY,
               'FastTree-2.1.10.c']
    logger.debug('  %s' % (' '.join(command)))
    pipe = subprocess.Popen(command,
                            cwd='lorax/fasttree',
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    logger.debug(pipe.stdout.read().decode('UTF-8'))
    stderr_messages = pipe.stderr.read().decode('UTF-8')
    if stderr_messages != '':
        logger.error(stderr_messages)
        raise SystemError("Unable to compile FastTree.")
    if platform.system() == 'Darwin':
        logger.info('fixing library file paths in MacOS executable')
        gomp_name = 'libgomp.1.dylib'
        gomp_path  = Path(sys.prefix)/'lib'/gomp_name
        if not gomp_path.exists():
            logger.error('libgcc must be in the virtual environment')
            raise SystemError("Unable to resolve paths in MacOS executable")
        subprocess.check_call(['install_name_tool',
                               '-change',
                               '@rpath/'+gomp_name,
                               str(gomp_path),
                               str(BINARY_PATH/FASTTREE_BINARY)],
                              )


class InstallBinariesCommand(Command):
  """Install binaries to virtual environment bin directory."""
  description = 'Copy binaries to install location'
  user_options = [('bindir=', None, 'binaries directory')]


  def initialize_options(self):
    """Set default values for options."""
    install_root = self.distribution.get_command_obj('install').root
    if install_root is not None:
        install_dir = install_root + '/usr'
    elif hasattr(sys, 'real_prefix'):
        install_dir = sys.prefix
    elif hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix:
        install_dir = sys.prefix
    elif 'conda' in sys.prefix:
        install_dir = sys.prefix
    else:
        install_dir = '.'
    self.bin_path = Path(install_dir)/'bin'

  def finalize_options(self):
    """Post-process options."""
    if not self.bin_path.exists():
        logger.info('creating binary directory "%s"' % (str(self.bin_path)))
        self.bin_path.mkdir(parents=True)

  def run(self):
    """Run command."""
    # Check if build is disabled by environmental variable.
    if 'LORAX_NO_BINARIES' in environ and\
            environ['LORAX_NO_BINARIES'] == 'True':
        logger.info('skipping install of binary files')
    else:
        logger.info('copying binaries to %s' % (str(self.bin_path)))
        for binary in BINARY_PATH.iterdir():
            shutil.copy2(str(binary), str(self.bin_path))


class BuildPyCommand(build_py.build_py):
  """Build FastTree as part of build."""

  def run(self):
    self.run_command('build_fasttree')
    build_py.build_py.run(self)


class DevelopCommand(develop.develop):
    """Build FastTree as part of develop."""

    def run(self):
        self.run_command('build_fasttree')
        self.run_command('install_binaries')
        develop.develop.run(self)

class InstallCommand(install.install):
    """Install FastTree as part of install."""

    def run(self):
        self.run_command('build_fasttree')
        self.run_command('install_binaries')
        install.install.run(self)
#
# Most of the setup function has been moved to setup.cfg,
# which requires a recent setuptools to work.  Current
# anaconda setuptools is too old, so it is strongly
# urged that lorax be installed in a virtual environment.
#
tests_require = [
    'check-manifest>=0.25',
    'coverage>=4.0',
    'isort>=4.2.2.2',
    'pydocstyle>=1.0.0',
    'pytest-cache>=1.0',
    'pytest-cov>=1.8.0',
    'pytest-pep8>=1.0.6',
    'pytest>=2.8.0'
]

extras_require = {
    'docs': ['Sphinx>=1.4.2'
             ],
    'tests': tests_require,

}

extras_require['all'] = []
for reqs in extras_require.values():
    extras_require['all'].extend(reqs)

packages = find_packages()

setup(
    description=__doc__,
    packages=packages,
    setup_requires=['packaging',
                    'setuptools>30.3.0',
                    'setuptools-scm>1.5'
                    ],
    entry_points={
        'console_scripts': ['lorax = lorax.cli:cli']
    },
    cmdclass={
        'build_fasttree': BuildFasttreeCommand,
        'build_py': BuildPyCommand,
        'develop': DevelopCommand,
        'install_binaries': InstallBinariesCommand,
        'install': InstallCommand
    },
    use_scm_version={
        'version_scheme': 'guess-next-dev',
        'local_scheme': 'dirty-tag',
        'write_to': 'lorax/version.py'
    },
    extras_require=extras_require,
    tests_require=tests_require,
)
