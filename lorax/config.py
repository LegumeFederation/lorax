# -*- coding: utf-8 -*-
"""Define and handle configuration variables.
"""
#
# Library imports.
#
import datetime
#
# Name of this service.
#
SERVICE_NAME = 'lorax'
SERVICE_ORG = 'LegumeFederation'

def configure_app(app):
    """Flask app.config
    """
    #
    # Name of this service.
    #
    app.config['NAME'] = SERVICE_NAME
    #
    # Web site associated with this project.
    #
    app.config['PROJECT_HOME'] = 'https://github.com/' + SERVICE_ORG + '/' +SERVICE_NAME
    #
    # File path locations.  All of these are immutable except DATA.
    # Since different components run from different locations, these
    # must be absolute.  The immutable ones should be created before
    # runtime.
    #
    app.config['DATA'] = '/usr/local/var/data'
    #
    # Directory/file permissions.
    #
    app.config['DIR_MODE'] = '755'  # Note interaction with process umask
    #
    # Number of threads used in queued commands.  0 = use as many as available.
    #
    app.config['THREADS'] = 0
    #
    # RQ settings.  If "RQ_ASYNC" is False, then no queueing will be done.
    #
    app.config['TREE_QUEUE'] = 'treebuilding'
    app.config['ALIGNMENT_QUEUE'] = 'alignment'
    app.config['RQ_REDIS_URL'] = 'redis://redis:6379/0'
    app.config['RQ_SCHEDULER_QUEUE'] = app.config['ALIGNMENT_QUEUE']
    app.config['ALIGNMENT_QUEUE_TIMEOUT'] = 24 * 60 * 60  # 24 hours, in seconds
    app.config['TREE_QUEUE_TIMEOUT'] = 30 * 24 * 60 * 60  # 30 days, in seconds
    #
    # Definitions for alignment algorithms.
    #
    app.config['ALIGNERS'] = {
        'hmmalign': ["--trim", "--informat", "FASTA"]  # command-line arguments
    }
    app.config['HMMALIGN_EXE'] = 'hmmalign'
    #
    # Definitions for tree-building algorithms.
    #
    app.config['TREEBUILDERS'] = {
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
    # Binaries.
    #
    app.config['FASTTREE_EXE'] = 'FastTree'
    app.config['RAXML_EXE'] = 'raxmlHPC'
    #
    # Current run.
    #
    app.config['DATETIME'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%m:%S")
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
    app.config['STDERR_LOG_FORMAT'] = '%(levelname)s: %(message)s'
