# -*- coding: utf-8 -*-
"""Define and handle configuration variables.

Definitions in this file are selected by the MYAPP_CONFIGURATION environmental
variable.  This variable may take on the following values:

* default: starts everything in production environment
* development: starts in debug environment (not secure)
* serverOnly: same as default, but without queues
* treebuilder: starts treebuilder queue only
* aligner: start aligner queue only


These definitions may be overridden via two ways:

1. A python file pointed to by the environmental variable MYAPP_SETTINGS.
2. An environmental variable that starts with MYAPP_.  If its value is
   "True" or "False", then it will be interpreted as a logical value.
   If its value can be parsed as an integer, then it will be.
"""
#
# Library imports.
#
import datetime
import os
import platform
import sys
from pathlib import Path  # python 3.4
#
# Name of this service.
#
SERVICE_NAME = 'lorax'
SERVICE_ORG = 'LegumeFederation'
#
# Definitions that *must* be set in environmental variables.  Trying to
# set these from the config file would be too late, so they are
# not settable by that mechanism.
#
IMMUTABLES = ('ROOT', 'VAR', 'TMP')
PATHVARS = ('ROOT', 'VAR', 'TMP', 'DATA', 'USERDATA')

def get_path(name, default):
    """Get path from environ, checking absoluteness."""
    varname = SERVICE_NAME.upper() + '_' + name.upper()
    if varname in os.environ:
        path_str = os.environ[varname]
        try:
            Path(path_str).relative_to('/')
        except ValueError:  # relative path, not acceptable
            print('ERROR--path variable %s="%s" not absolute, ignoring'
                  % (varname, path_str))
            path_str = default
    else:
        path_str = default
    return path_str


class BaseConfig(object):
    """Base class for configuration objects.

    Note that only values in uppercase will be stored in the app
    configuration object.
    """
    #
    # Name of this service.
    #
    NAME = SERVICE_NAME
    ENVIRONMENT_DUMP = False
    #
    # Web site associated with this project.
    #
    PROJECT_HOME = 'https://github.com/' + SERVICE_ORG + '/' +SERVICE_NAME
    #
    # File path locations.  All of these are immutable except DATA.
    # Since different components run from different locations, these
    # must be absolute.  The immutable ones should be created before
    # runtime.
    #
    ROOT = get_path('ROOT', sys.prefix)
    VAR = get_path('VAR', ROOT + '/var')
    TMP = get_path('TMP', VAR + '/tmp')
    DATA = get_path('DATA', VAR + '/data/')
    USERDATA = get_path('DATA', VAR + '/userdata/')
    #
    # Directory/file permissions.
    #
    DIR_MODE = '755'  # Note interaction with process umask
    #
    # Number of threads used in queued commands.  0 = use as many as available.
    #
    THREADS = 0
    #
    # RQ settings.  If "RQ_ASYNC" is False, then no queueing will be done.
    #
    TREE_QUEUE = 'treebuilding'
    ALIGNMENT_QUEUE = 'alignment'
    RQ_REDIS_URL = 'redis://redis:6379/0'
    RQ_SCHEDULER_QUEUE = ALIGNMENT_QUEUE
    ALIGNMENT_QUEUE_TIMEOUT = 24 * 60 * 60  # 24 hours, in seconds
    TREE_QUEUE_TIMEOUT = 30 * 24 * 60 * 60  # 30 days, in seconds
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
    # Binaries.
    #
    FASTTREE_EXE = 'FastTree'
    RAXML_EXE = 'raxmlHPC'
    #
    # Current run.
    #
    DATETIME = datetime.datetime.now().strftime("%Y-%m-%d %H:%m:%S")
    #
    # Controls of which processes get started by supervisord.
    # Setting these to empty strings will cause the process to
    # not be started.
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


#
# Dictionary of configuration levels to be used with
# the _CONFIGURATION environmental variable.
#
config_dict = {
    'default': SERVICE_NAME + '.config.BaseConfig',
}


def configure_app(app):
    """Configure the app, getting variables and setting up logging.

    :param app:
    :return:
    """
    config_name = os.getenv(SERVICE_NAME.upper() + '_MODE', 'default')
    if config_name not in config_dict:
        print('ERROR -- mode "%s" not known.' % config_name,
              file=sys.stderr) # noqa
        sys.exit(1)
    app.config.from_object(config_dict[config_name])
    app.config['MODE'] = config_name
    #
    # Do overrides from configuration, if it exists.
    #
    app.instance_path = os.getenv(SERVICE_NAME.upper() + '_ROOT',
                                  app.config['ROOT'])
    pyfile_dict = {}
    for internal_key in ['__doc__', '__builtins__']:
        if internal_key in pyfile_dict:
            del pyfile_dict[internal_key]
    if 'VAR' in pyfile_dict:  # VAR is hierarchical special case
        for subdir in ['tmp', 'log', 'data', 'userdata']:
            if not subdir.upper() in pyfile_dict:
                pyfile_dict[subdir.upper()] = pyfile_dict['VAR'] + '/' + subdir

    for key in pyfile_dict:
        app.config[key] = pyfile_dict[key]
