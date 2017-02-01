# -*- coding: utf-8 -*-
'''Global constants and common helper functions.
'''
#
# library imports
#
import logging
import sys
import os
import ast
import json
from datetime import datetime
from pathlib import Path # python 3.4 or later
from distutils.util import strtobool
from distutils.version import StrictVersion
#
# 3rd-party module imports
#
from tabulate import tabulate
#
# module version--kept in its own file for setup.py
#
from .version import version as __version__ # noqa
#
# global constants
#
PROGRAM_NAME = 'lorax'
AUTHOR = 'Joel Berendzen'
EMAIL = 'joelb@ncgr.org'
COPYRIGHT = """Copyright (C) 2017, The National Center for Genome Resources.  All rights reserved.
"""
PROJECT_HOME = 'https://github.com/LegumeFederation/lorax'
DOCS_HOME = 'https://lorax.readthedocs.org/en/stable'
DEFAULT_FILE_LOGLEVEL = logging.DEBUG
DEFAULT_STDERR_LOGLEVEL = logging.INFO
VERSION = __version__
STARTTIME = datetime.now()
CONFIGFILE_NAME = 'config.json'
TREEBUILDERS = ['FastTree', 'RaxML']
#
# global logger object
#
logger = logging.getLogger('lorax')

