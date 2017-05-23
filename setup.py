# -*- coding: utf-8 -*-
"""
lorax -- speaks for the (phylogenetic) trees.
"""
#
# Developers, install with
#    pip install --editable .
#
import os
import subprocess
import sys
from distutils.util import convert_path
from pathlib import Path # python 3.4
from setuptools import setup
from setuptools.command.install import install


def compile_fasttree_binary():
    """Compile the FastTree software"""
    if 'PREFIX' in os.environ:
        exe_dir = os.environ['PREFIX'] # prefix for gentoo builds
    elif hasattr(sys, 'real_prefix'):
        exe_dir = sys.prefix
    elif hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix:
        exe_dir = sys.prefix
    elif 'conda' in sys.prefix:
        exe_dir = sys.prefix
    else:
        exe_dir = '.'
    bin_path = Path(exe_dir).resolve()/'bin'
    if not bin_path.exists():
        print('Creating binary directory %s:' %(str(bin_path)))
        bin_path.mkdir(mode=0o755, parents=True)
    exe_path = str(bin_path/'FastTree-lorax')
    print('compiling double-precision FastTree binary to %s:' %(exe_path))
    command = ['gcc',
               '-DUSE_DOUBLE',
               '-finline-functions',
               '-funroll-loops',
               '-O3',
               '-march=native',
               '-DOPENMP',
               '-fopenmp',
               '-lm',
               '-o',
               str(exe_path),
               'FastTree-2.1.10.c']
    print('  %s' %(' '.join(command)))
    pipe = subprocess.Popen(command,
                            cwd='lorax/fasttree',
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    for line in pipe.stdout.readline():
        print(line.decode('UTF-8'))
    cmd_err = False
    for line in pipe.stderr.readline():
        errline = line.decode('UTF-8')
        if errline != "":
            cmd_err = True
            print(stderr)
    if cmd_err:
        sys.exit(1)



class InstallWithFastTree(install):
    """Custom handler for the 'install' command"""
    def run(self):
        compile_fasttree_binary()
        super().run()


name = 'lorax'

# restrict to python 3.4 or later
if sys.version_info < (3, 4, 0, 'final', 0):
    raise SystemExit('Python 3.4 or later is required!')

# get version from version.py
version_dict = {}
version_path = convert_path(name + '/version.py')
with open(version_path) as version_file:
    exec(version_file.read(), version_dict)
version = version_dict['version']

# data_files will be tree in examples/ directory
exampledir = os.path.join(name, 'examples')
examplefiles = [(root, [os.path.join(root, f) for f in files])
                for root, dirs, files in os.walk(exampledir)]

setup(
    name=name,
    version=version,
    data_files=examplefiles,
    cmdclass={'install': InstallWithFastTree},
    url='http://github.com/ncgr/lorax',
    keywords=['science', 'biology', 'bioinformatics', 'genomics',
              'sequence', 'curation'],
    license='BSD',
    description='Server for phylogenetic tree generation and extension',
    long_description=open('README.rst').read(),
    author='Joel Berendzen',
    author_email='joelb@ncgr.org',
    packages=[name],
    package_data={'lorax': ['test/*',
                            'templates/*',
                            'static/js/*',
                            'static/css/*,'
                            'static/favicon.ico',
                            'fasttree/*']},
    include_package_data=True,
    zip_safe=False,
    install_requires=['Flask-RQ2',
                      'biopython',
                      'rq_dashboard'
                      ],
    entry_points={
        'console_scripts': ['lorax = lorax.cli:cli']
    },
    classifiers=['Development Status :: 4 - Beta',
                 'Environment :: Console',
                 'Intended Audience :: Science/Research',
                 'License :: OSI Approved :: BSD License',
                 'Operating System :: OS Independent',
                 'Programming Language :: Python :: 3.4',
                 'Programming Language :: Python :: 3.5',
                 'Programming Language :: Python :: 3.6',
                 'Topic :: Scientific/Engineering :: Bio-Informatics'
                 ]
)
