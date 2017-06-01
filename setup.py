# -*- coding: utf-8 -*-
"""
lorax -- speaks for the (phylogenetic) trees.
"""
#
#
#
# Developers, install with
#    python setup.py develop
#
from distutils.cmd import Command
import distutils.log as logger
import shutil
import subprocess
import sys
from setuptools import setup
from setuptools.command import build_py, develop
from os import environ as environ

# restrict to python 3.4 or later
if sys.version_info < (3, 4, 0, 'final', 0):
    raise SystemExit("lorax requires python 3.4 or higher.")


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
    """Run command."""
    from pathlib import Path  # python 3.4
    # Check if build is disabled by environmental variable.
    if 'NO_FASTTREE_BINARY' in environ:
        logger.info('Skipping compile of FastTree binary.')
        return
    if hasattr(sys, 'real_prefix'):
        exe_dir = sys.prefix
    elif hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix:
        exe_dir = sys.prefix
    elif 'conda' in sys.prefix:
        exe_dir = sys.prefix
    else:
        exe_dir = '.'
    bin_path = Path(exe_dir).resolve() / 'bin'
    if not bin_path.exists():
        logger.debug('Creating binary directory %s:' % (str(bin_path)))
        bin_path.mkdir(mode=0o755, parents=True)
    exe_path = str(bin_path / 'FastTree-lorax')
    logger.info('Compiling double-precision FastTree binary to %s:' % (exe_path))
    command = [shutil.which(self.cc),
               '-DUSE_DOUBLE',
               '-finline-functions',
               '-funroll-loops',
               '-O3',
               '-march=native',
               '-DOPENMP',
               '-fopenmp',
               '-o',
               str(exe_path),
               'FastTree-2.1.10.c']
    logger.debug('  %s' % (' '.join(command)))
    pipe = subprocess.Popen(command,
                            cwd='lorax/fasttree',
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    for line in pipe.stdout.readline():
        logger.debug(line.decode('UTF-8'))
    cmd_err = False
    for line in pipe.stderr.readline():
        errline = line.decode('UTF-8')
        if errline != "":
            cmd_err = True
            logger.error(stderr)
    if cmd_err:
        raise SystemError("Unable to compile FastTree.")


class BuildPyCommand(build_py.build_py):
  """Build FastTree as part of build."""

  def run(self):
    self.run_command('build_fasttree')
    build_py.build_py.run(self)


class DevelopCommand(develop.develop):
    """Build FastTree as part of develop."""

    def run(self):
        self.run_command('build_fasttree')
        develop.develop.run(self)
#
# most of the setup function has been moved to setup.cfg
#
setup(
    setup_requires=['packaging',
                    'setuptools>30.3.0',
                    #'setuptools-scm>1.5'
                    ],
    entry_points={
        'console_scripts': ['lorax = lorax.cli:cli']
    },
    cmdclass={
        'build_fasttree': BuildFasttreeCommand,
        'build_py': BuildPyCommand,
        'develop': DevelopCommand
    },
    #use_scm_version={
    #    'version_scheme': 'guess-next-dev',
    #    'local_scheme': 'dirty-tag',
    #    'write_to': 'lorax/version.py'
    #}
)
