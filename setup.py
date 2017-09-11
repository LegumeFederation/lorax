# -*- coding: utf-8 -*-
#
# This file is part of lorax.
# Copyright (C) 2017, NCGR.
#
# lorax is free software; you can redistribute it and/or modify
# it under the terms of the 3-Clause BSD License; see LICENSE.txt
# file for more details.
#
"""lorax -- speaks for the (phylogenetic) trees."""
#
# Developers, install with:
#    pip install -r requirements.txt
#    python setup.py develop
#
from distutils.cmd import Command
import distutils.log as logger
from os import environ as environ
import platform
import shutil
import string
import subprocess # noqa
import sys
from setuptools import setup, find_packages
from setuptools.command import build_py, develop, install
# Version restrictions and dependencies
if sys.version_info < (3, 4, 0, 'final', 0):
    raise SystemExit("This package requires python 3.4 or higher.")
elif sys.version_info >= (3, 6, 0, 'final', 0):
    from secrets import choice
else:
    from random import choice
from pathlib import Path  # python 3.4

NAME = 'lorax'
C_NAME = 'FastTree'
C_VERSION = '2.1.10'
BINARY_NAME = C_NAME + '-' + NAME
ENV_SCRIPT_INNAME = 'server_env.sh'
ENV_SCRIPT_OUTNAME = NAME + '_env'
RUN_SCRIPT_INNAME = 'server_run.py'
RUN_SCRIPT_OUTNAME = NAME + '_run.py'
SOURCE_PATH = Path('.') / NAME / C_NAME.lower()
BUILD_PATH = Path('.') / NAME / 'bin'
PASSWORD_LENGTH = 12
DIR_MODE = 0o775


class BuildCBinaryCommand(Command):
    """Compile C binary with custom switches."""
    description = 'Build ' + C_NAME + ' C binary'
    user_options = [
        # The format is (long option, short option, description).
        ('cc=', None, 'path to c compiler'),
        ('cflags=', None, 'CFLAGS for compiler in use'),
        ('libs=', None, 'Library options')
    ]

    def initialize_options(self):
        """Set default values for options."""
        # Each user option must be listed here with their default value.
        system = platform.system()
        if system == 'Linux':
            self.cc = 'gcc'
            self.cflags = '-DUSE_DOUBLE -finline-functions -funroll-loops' + \
                          ' -O3 -march=native -DOPENMP -fopenmp'
            self.libs = '-lm'
        elif system == 'Darwin':
            self.cc = 'gcc'
            self.cflags = '-DUSE_DOUBLE -finline-functions -funroll-loops' + \
                          ' -O3 -march=native -DOPENMP -fopenmp'
            self.libs = '-lm'
        elif system.endswith('BSD'):
            self.cc = 'clang'
            self.cflags = '-DUSE_DOUBLE -finline-functions -funroll-loops' + \
                          ' -O3 -march=native'
            self.libs = '-lm'
        else:
            logger.warning(
                'Unrecognized system, using conservative default CFLAGS')
            self.cc = 'gcc'
            self.cflags = '-DUSE_DOUBLE'
            self.libs = '-lm'

    def finalize_options(self):
        """Post-process options."""
        if shutil.which(self.cc) is None:
            raise SystemError('C compiler %s is not found on path.', self.cc)
        self.cflag_list = self.cflags.split()
        self.lib_list = self.libs.split()

    def run(self):
        """Build C binary."""
        # Check if build is disabled by environmental variable.
        if NAME.upper() + '_NO_COMPILE' in environ and \
                environ[NAME.upper() + '_NO_COMPILE'] == 'True':
            logger.info('skipping compile of ' + C_NAME + ' binary')
            return
        if (BUILD_PATH / BINARY_NAME).exists():
            logger.info(C_NAME + ' binary already built')
            return
        logger.info('compiling ' + C_NAME + ' v' + C_VERSION + ' binary using')
        command = [shutil.which(self.cc)] + \
            self.cflag_list + ['-o',
                               '../bin/' + BINARY_NAME,
                               C_NAME + '-' + C_VERSION + '.c'] + \
            self.lib_list
        logger.info('  %s' % (' '.join(command)))
        pipe = subprocess.Popen(command,
                                cwd=NAME + '/' + C_NAME.lower(),
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        logger.debug(pipe.stdout.read().decode('UTF-8'))
        stderr_messages = pipe.stderr.read().decode('UTF-8')
        if stderr_messages != '':
            logger.error(stderr_messages)
            raise SystemError("Unable to compile C binary with command %s.",
                              command)
        if platform.system() == 'Darwin':
            logger.info('fixing OpenMP file path in MacOS executable')
            gomp_name = 'libgomp.1.dylib'
            find_gomp_cmd = ['gcc', '-print-file-name=' + gomp_name]
            gomp_path_str = subprocess.check_output(find_gomp_cmd).decode(
                'UTF-8')[:-1]
            gomp_path = Path(gomp_path_str).resolve()
            if not gomp_path.exists():
                raise SystemError(
                    "Unable to find OpenMP library %s." % gomp_name)
            try:
                subprocess.check_call(['install_name_tool',
                                       '-change',
                                       '@rpath/./' + gomp_name,
                                       str(gomp_path),
                                       str(BUILD_PATH / BINARY_NAME)]
                                      )
            except subprocess.CalledProcessError:
                raise SystemError(
                    "Unable to install OpenMP path in FastTree binary.")


class InstallBinariesCommand(Command):
    """Install binaries to virtual environment bin directory."""
    description = 'Copy binaries to install location'
    user_options = [('bindir=', None, 'binaries directory')]

    def initialize_options(self):
        """Set default values for options."""
        if NAME.upper() + '_ROOT' in environ:
            install_path = Path(environ[NAME.upper() + '_ROOT'])
        else:
            install_path = Path(sys.prefix)
        self.bin_path = install_path / 'bin'
        self.etc_path = install_path / 'etc'

    def finalize_options(self):
        """Post-process options."""
        if not self.bin_path.exists():
            logger.info(
                'creating binary directory "%s"' % (str(self.bin_path)))
            self.bin_path.mkdir(parents=True, mode=DIR_MODE)
        if not self.etc_path.exists():
            logger.info('creating etc directory "%s"' % (str(self.etc_path)))
            self.etc_path.mkdir(parents=True, mode=DIR_MODE)

    def create_config_file(self, file_name):
        """Initializes config file with secret key."""
        file_path = self.etc_path / file_name
        if not file_path.exists():
            with file_path.open(mode='w') as config_fh:
                print('Creating instance config file at "%s".' % str(
                    file_path))
                alphabet = string.ascii_letters + string.digits
                nchars = 0
                secret_key = ''
                while nchars < PASSWORD_LENGTH:
                    secret_key += choice(alphabet) # noqa
                    nchars += 1
                print('SECRET_KEY = "%s" # set at install time' % (secret_key),
                      file=config_fh) # noqa

    def run(self):
        """Run command."""
        # Check if build is disabled by environmental variable.
        no_binaries = NAME.upper() + '_NO_BINARIES'
        if no_binaries in environ and \
                environ[no_binaries] == 'True':
            logger.info('skipping install of binary files')
        else:
            logger.info('copying binary to %s' % (str(self.bin_path)))
            shutil.copy2(str(BUILD_PATH / BINARY_NAME),
                         str(self.bin_path / BINARY_NAME))
            logger.info(
                'copying environment script to %s' % (str(self.bin_path)))
            shutil.copy2(str(BUILD_PATH / ENV_SCRIPT_INNAME),
                         str(self.bin_path / ENV_SCRIPT_OUTNAME))
            shutil.copy2(str(BUILD_PATH / RUN_SCRIPT_INNAME),
                         str(self.bin_path / RUN_SCRIPT_OUTNAME))
            my_python = self.bin_path / (NAME + '_python')
            if not my_python.exists():
                logger.info('creating ' + str(my_python) + ' link')
                my_python.symlink_to(sys.executable)
            self.create_config_file(NAME + '.conf')


class BuildPyCommand(build_py.build_py):
    """Build C binary as part of build."""

    def run(self):
        self.run_command('build_cbinary')
        build_py.build_py.run(self)


class DevelopCommand(develop.develop):
    """Build C binary as part of develop."""

    def run(self):
        self.run_command('build_cbinary')
        self.run_command('install_binaries')
        develop.develop.run(self)


class InstallCommand(install.install):
    """Install C binary as part of install."""

    def run(self):
        self.run_command('build_cbinary')
        self.run_command('install_binaries')
        install.install.run(self)


#
# Most of the setup function has been moved to setup.cfg,
# which requires a recent setuptools to work.  Current
# anaconda setuptools is too old, so it is strongly
# urged this package be installed in a virtual environment.
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

extras_require = dict(docs=['Sphinx>=1.4.2'], tests=tests_require)

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
        'console_scripts': [NAME + ' = ' + NAME + '.cli:cli']
    },
    cmdclass={
        'build_cbinary': BuildCBinaryCommand,
        'build_py': BuildPyCommand,
        'develop': DevelopCommand,
        'install_binaries': InstallBinariesCommand,
        'install': InstallCommand
    },
    use_scm_version={
        'version_scheme': 'guess-next-dev',
        'local_scheme': 'dirty-tag',
        'write_to': NAME + '/version.py'
    },
    extras_require=extras_require,
    tests_require=tests_require,
)
