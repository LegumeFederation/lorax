# -*- coding: utf-8 -*-
"""Configuration variables for lorax.

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
"""
#
# Library imports.
#
import os
import sys
#
# Local imports
#
from .version import version as __version__  # noqa


class BaseConfig(object):
    """Base class for configuration objects.

    Note that only values in uppercase will be stored in the app
    configuration object.
    """
    #
    # Usually these paths should be absolute, but for testing these
    # are relative to the PWD of the lorax process.
    #
    DATA_PATH = 'data/'
    LOG_PATH = 'var/log/'
    DIR_MODE = 0o755
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
    SETTINGS = 'config.cfg'
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
    RQ_REDIS_URL = "redis://localhost:58929/0"
    RQ_SCHEDULER_INTERVAL = 60
    RQ_SCHEDULER_QUEUE = ALIGNMENT_QUEUE
    ALIGNMENT_QUEUE_TIMEOUT = 1000  # About 15 minutes, in seconds
    TREE_QUEUE_TIMEOUT = 4 * 60 * 60  # 4 hours, in seconds
    #
    # Definitions for alignment algorithms.
    #
    ALIGNERS = {
        'hmmalign': ["--trim", "--informat", "FASTA"]  # command-line arguments
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
            "peptide": ["-b", "12345", "-p", "12345", "-N", "10", "-m",
                        "PROTGAMMABLOSUM62"],
            "DNA": ["-d"]
        }
    }
    #
    # Deployment definitions.
    #
    VENV_PATH = ''
    NO_BINARIES = False
    CONDA_VENV = 'loraxenv'
    FASTTREE_EXE = 'FastTree-lorax'
    RAXML_EXE = 'raxmlHPC'
    USER = 'loraxuser'
    #
    # Logging formatter.  Fields that are defined are:
    #    asctime: Time with too much precision
    #    levelname: Severity level.
    #    module:  module name.
    #    lineno: line number.
    #    pathname: File path.
    #    message: The message.
    #    url: Target address (if from a target).
    #    utcnow: Time in UTC.
    #    method: HTTP method.
    #    ip: Real IP address of the requester.
    #
    STDERR_LOG_FORMAT = '%(levelname)s: %(message)s'
    FILE_LOG_FORMAT = '%(levelname)s: %(message)s'


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
    """Configure the app, getting variables and setting up logging.

    :param app:
    :return:
    """
    #
    config_name = os.getenv('LORAX_CONFIGURATION', 'default')
    if config_name not in config_dict:
        print('ERROR -- configuration variable "%s" not known.' % config_name,
              file=sys.stderr)
        sys.exit(1)
    app.config.from_object(config_dict[config_name])
    #
    # Get instance-specific configuration, if it exists.
    #
    if 'LORAX_INSTANCE_DIR' in os.environ:
        app.instance_path = os.getenv('LORAX_INSTANCE_DIR')
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
