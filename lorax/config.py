# -*- coding: utf-8 -*-
'''Configuration variables for lorax.

Definitions in this file are selected by the LORAX_CONFIGURATION environmental
variable.  This variable may take on the following values:
    * default
    * development
    * testing
    * production


These definitions may be overridden via two ways:
  1) a python file pointed to by the environmental variable LORAX_SETTINGS.
  2) an environmental variable that starts with "LORAX_".  If its value is
     "True" or "False", then it will be interpreted as a logical value.
     If its value can be parsed as an integer, then it will be.
'''
#
# Library imports.
#
import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from datetime import datetime
from pathlib import Path # python 3.4
#
# Local imports
#
from .version import version as __version__ # noqa

DEFAULT_FILE_LOGLEVEL = logging.DEBUG
DEFAULT_STDERR_LOGLEVEL = logging.INFO

class BaseConfig(object):
    '''Base class for configuration objects.

    Note that only values in uppercase will be stored in the app
    configuration object.
    '''
    #
    # Usually these paths should be absolute, but for testing these
    # are relative to the PWD of the lorax process.
    #
    PATHS = {
        'log': 'logs/',
        'data': 'data/',
        'mode': 0o755
    }
    #
    # The DEBUG parameter has multiple implications:
    #           * access to python debugging via flask
    #           * logging levels set to DEBUG
    #           * configuration variables are printed
    #
    DEBUG = False
    PORT = 58927
    HOST = '127.0.0.1'
    #
    # Create a logfile.
    #
    LOGFILE = True
    LOGFILE_NAME = None
    LOGFILE_MAXBYTES = 10000000
    LOGFILE_BACKUPCOUNT = 1
    #
    # Log only errors.
    #
    QUIET = False
    #
    # Test mode, includes propagation of errors.
    #
    TESTING = False
    #
    # Settings file name.
    #
    SETTINGS='config.cfg'
    #
    # Number of threads used in queued commands.  0 = use as many as available.
    #
    THREADS = 0
    #
    # RQ settings.  If "RQ_ASYNC" is False, then no queueing will be done.
    #
    TREE_QUEUE = 'treebuilding'
    ALIGNMENT_QUEUE = 'alignment'
    RQ_ASYNC = True
    RQ_QUEUES = [TREE_QUEUE, ALIGNMENT_QUEUE]
    RQ_REDIS_URL = "redis://localhost:6379/0"
    RQ_SCHEDULER_INTERVAL = 60
    RQ_SCHEDULER_QUEUE = ALIGNMENT_QUEUE
    #
    # Definitions for alignment algorithms.
    #
    ALIGNERS = {
        'hmmalign': ["--trim", "--informat", "FASTA"] # command-line arguments
    }
    HMMALIGN_EXE = 'hmmalign'
    #
    # Definitions for tree-building algorithms.
    #
    TREEBUILDERS = {
        "FastTree": {
          "peptide": ["-nopr", "-log", "peptide.log"],
          "DNA": ["-nt", "-gtr", "-log", "nucleotide.log", "-nopr"]
        },
        "RAxML": {
          "peptide": ["-b", "12345", "-p", "12345", "-N", "10", "-m", "PROTGAMMABLOSUM62"],
          "DNA": ["-d"]
        }
    }
    FASTTREE_EXE = 'FastTree'
    RAXML_EXE = 'raxmlHPC'


class DebugConfig(BaseConfig):
    DEBUG = True
    TESTING = True
    RQ_ASYNC = False


class TestConfig(BaseConfig):
    TESTING = True


class ProductionConfig(BaseConfig):
    QUIET = True


#
# Dictionary of configuration levels to be used with
#  the LORAX_CONFIGURATION environmental variable.
#
config_dict = {
    'default': 'lorax.config.BaseConfig',
    'development': 'lorax.config.DebugConfig',
    'testing': 'lorax.config.TestConfig',
    'production': 'lorax.config.ProductionConfig'
}


def configure_app(app):
    '''Configure the app, getting variables and setting up logging.

    :param app:
    :return:
    '''
    #
    config_name = os.getenv('LORAX_CONFIGURATION', 'default')
    if config_name not in config_dict:
        print('ERROR -- configuration "%s" not known.' % config_name)
        sys.exit(1)
    app.config.from_object(config_dict[config_name])
    #
    # Get instance-specific configuration, if it exists.
    #
    pyfile_name = os.getenv('LORAX_SETTINGS', app.config['SETTINGS'])
    app.config.from_pyfile(pyfile_name, silent=True)
    #
    # Do overrides from environmental variables.
    #
    for lorax_envvar, envvar in [(i, i[6:])
                                 for i in sorted(os.environ)
                                 if i.startswith('LORAX_')]:
        value = os.environ[lorax_envvar]
        if value == 'True':
            value = True
        elif value == 'False':
            value = False
        else:
            try:
                value = int(value)
            except ValueError:
                pass
        app.config[envvar] = value
    #
    # Set version in config.
    #
    app.config['VERSION'] = __version__
    #
    # Configure logging to stderr and to a log file at
    # different levels.
    #
    app.mylogger = logging.getLogger('werkzeug')  # this is the logger we want
    if app.config['DEBUG']:
        stderr_log_level = logging.DEBUG
    else:
        stderr_log_level = DEFAULT_STDERR_LOGLEVEL
    if app.config['QUIET']:
        file_log_level = logging.ERROR
    else:
        file_log_level = DEFAULT_FILE_LOGLEVEL
    app.mylogger.setLevel(min(file_log_level, stderr_log_level))
    #
    # Start log file.
    #
    if app.config['LOGFILE']: # start a log file
        logfile_name = app.config['LOGGER_NAME'] + '.log'
        app.config['LOGFILE_NAME'] = logfile_name
        logfile_path = Path(app.config['PATHS']['log'])/logfile_name
        if app.config['DEBUG']:
            print('Logging to file "%s".' %str(logfile_path))
        if not logfile_path.parent.is_dir(): # create logs/ dir
            try:
                logfile_path.parent.mkdir(mode=app.config['PATHS']['mode'], parents=True)
            except OSError:
                app.mylogger.error('Unable to create logfile directory "%s"',
                             logfile_path.parent)
                raise OSError
        log_handler = RotatingFileHandler(str(logfile_path),
                                      maxBytes=app.config['LOGFILE_MAXBYTES'],
                                      backupCount=app.config['LOGFILE_BACKUPCOUNT'])
        app.mylogger.addHandler(log_handler)
    #
    # Do some logging on startup.
    #
    app.mylogger.debug('Command line: "%s"', ' '.join(sys.argv))
    app.mylogger.debug('%s version %s',
                     app.config['LOGGER_NAME'],
                     app.config['VERSION'])
    app.mylogger.debug('Run started at %s', datetime.now().strftime('%Y%m%d-%H%M%S'))
    if app.config['DEBUG']:
        for key in sorted(app.config):
            if 'LORAX_'+key in os.environ:
                from_environ = ' <- from environment'
            else:
                from_environ = ''
            app.mylogger.debug('%s =  %s %s',
                               key,
                               app.config[key],
                               from_environ)


