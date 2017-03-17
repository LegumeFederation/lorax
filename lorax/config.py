# -*- coding: utf-8 -*-
'''Configuration variables for lorax.

These definitions may be overridden via two ways:
  1) a python file pointed to by the environmental variable LORAX_SETTINGS.
  2) an environmental variable that starts with "LORAX_".  If its value is
     "True" or "False", then it will be interpreted as a logical value.
     If its value can be parsed as an integer, then it will be.
'''
#
# Note that only values in uppercase will be stored in the
# configuration object.
#
import rq
class BaseConfig(object):
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
    # Server IP and port.  Note that these may only count if the internal
    # server is used.
    #
    HOST = 'localhost'
    PORT = 58927
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


class DevelopmentConfig(BaseConfig):
    DEBUG = True
    TESTING = True
    RQ_ASYNC = False


class TestConfig(BaseConfig):
    TESTING = True


class ProductionConfig(BaseConfig):
    QUIET = True