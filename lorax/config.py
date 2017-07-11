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
  1) a python file pointed to by the environmental variable MYAPP_SETTINGS.
  2) an environmental variable that starts with "MYAPP_".  If its value is
     "True" or "False", then it will be interpreted as a logical value.
     If its value can be parsed as an integer, then it will be.
"""
#
# Library imports.
#
import os
import sys
from getpass import getuser
from socket import getfqdn
from pathlib import Path # python 3.4
#
# Third-party imports.
#
import arrow
#
# Local imports
#
from .version import version as __version__  # noqa
MODULE = __name__.split('.')[0]
#
# Definitions that *must* be set in environmental variables.  Trying to
# set these from the config file would be too late, so they are
# not settable by that mechanism.
#
IMMUTABLES = ('ROOT', 'VAR', 'LOG', 'TMP')
PATHVARS = ('ROOT', 'VAR', 'LOG', 'TMP', 'DATA', 'USERDATA')


def get_path(name, default):
    """Get path from environ, checking absoluteness."""
    varname = MODULE.upper() + '_' + name.upper()
    if varname in os.environ:
        path_str = os.environ[varname]
        try:
            Path(path_str).relative_to('/')
        except ValueError:  # relative path, not acceptable
            print('ERROR--path variable %s="%s" not absolute, ignoring'
                  % (var, path_str))
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
    # File path locations.  All of these are immutable except DATA.
    # Since different components run from different locations, these
    # must be absolute.  The immutable ones should be created before
    # runtime.
    #
    ROOT = get_path('ROOT', sys.prefix)
    VAR = get_path('VAR', ROOT + '/var')
    LOG = get_path('LOG', VAR + '/log')
    TMP = get_path('TMP', VAR + '/tmp')
    DATA = get_path('DATA', VAR + '/data/')
    USERDATA = get_path('DATA', VAR + '/userdata/')
    #
    #
    #
    PROCESS_UMASK = '007'
    DIR_MODE = 0o770 # Note interaction with process umask
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
    SETTINGS = MODULE +'.conf'
    #
    # Number of threads used in queued commands.  0 = use as many as available.
    #
    THREADS = 0
    #
    # RQ settings.  If "RQ_ASYNC" is False, then no queueing will be done.
    #
    RQ_ASYNC = True
    TREE_QUEUE = 'treebuilding'
    ALIGNMENT_QUEUE = 'alignment'
    RQ_QUEUES = [TREE_QUEUE, ALIGNMENT_QUEUE]
    REDIS_UNIX_SOCKET = False
    RQ_REDIS_PORT = 58929
    RQ_REDIS_HOST = 'localhost'
    RQ_SCHEDULER_INTERVAL = 60
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
    FASTTREE_EXE = 'FastTree-'+MODULE
    RAXML_EXE = 'raxmlHPC'
    #
    # Current run.
    #
    USER = getuser()
    HOSTNAME = getfqdn()
    DATETIME = arrow.now().format('YYYY-MM-DD HH:mm:ss')
    #
    # supervisord defs.
    #
    SUPERVISORD_UNIX_SOCKET = False
    SUPERVISORD_PORT = 58928
    SUPERVISORD_HOST = '127.0.0.1'
    SUPERVISORD_USER = MODULE
    SUPERVISORD_PASSWORD = MODULE + '_default_password'
    SUPERVISORD_START_REDIS = True
    SUPERVISORD_START_SERVER = True
    SUPERVISORD_START_REDIS = True
    SUPERVISORD_START_ALIGNMENT = True
    SUPERVISORD_START_TREEBUILDER = True
    SUPERVISORD_START_CRASHMAIL = True
    #
    # crashmail defs.
    #
    CRASHMAIL_EMAIL = getuser()
    CRASHMAIL_EVENTS = 'PROCESS_STATE_EXITED'
    #
    # Controls of which processes get started by supervisord.
    # Setting these to empty strings will cause the process to
    # not be started.
    #
    # Monitoring at sentry.io.
    #
    SENTRY_DSN = ''
    #
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





class DevelopmentConfig(BaseConfig):
    """Start internal server, no queues."""
    DEBUG = True
    TESTING = True
    RQ_ASYNC = False
    # Running synchronous--no need to start queues.
    SUPERVISORD_START_REDIS  = False
    SUPERVISORD_START_ALIGNMENT = False
    SUPERVISORD_START_TREEBUILDER = False
    # Use debug config settings
    SETTINGS = MODULE + '-debug.conf'


class ServerOnlyConfig(BaseConfig):
    """Start server and redis, no queues."""
    SUPERVISORD_START_ALIGNMENT = False
    SUPERVISORD_START_TREEBUILDER = False


class TreebuilderConfig(BaseConfig):
    """Start treebuilder queue only."""
    SUPERVISORD_START_REDIS = False
    SUPERVISORD_START_SERVER = False
    SUPERVISORD_START_ALIGNMENT = False


class AlignerConfig(BaseConfig):
    """Start alignment queue only"""
    SUPERVISORD_START_REDIS = False
    SUPERVISORD_START_SERVER = False
    SUPERVISORD_START_TREEBUILDER = False


#
# Dictionary of configuration levels to be used with
#  the _CONFIGURATION environmental variable.
#
config_dict = {
    'default': MODULE +'.config.BaseConfig',
    'development': MODULE +'.config.DevelopmentConfig',
    'serverOnly': MODULE +'.config.ServerOnlyConfig',
    'treebuilder': MODULE +'.config.TreebuilderConfig',
    'aligner': MODULE +'.config.AlignerConfig'
}

def configure_app(app):
    """Configure the app, getting variables and setting up logging.

    :param app:
    :return:
    """
    config_name = os.getenv(MODULE.upper()+'_MODE', 'default')
    if config_name not in config_dict:
        print('ERROR -- mode "%s" not known.' % config_name,
              file=sys.stderr)
        sys.exit(1)
    app.config.from_object(config_dict[config_name])
    app.config['MODE'] = config_name
    #
    # Get instance-specific configuration, if it exists.
    #
    if MODULE.upper()+'_ROOT' in os.environ:
        app.instance_path = os.getenv(MODULE.upper()+'_ROOT')
    pyfile_name = os.getenv(MODULE.upper()+'_SETTINGS', app.config['SETTINGS'])
    pyfile_path = str(Path(app.instance_path)/'etc'/pyfile_name)
    app.config.from_pyfile(pyfile_path, silent=True)
    #
    # Do overrides from environmental variables.
    #
    for my_envvar, envvar in [(i, i[6:])
                                 for i in sorted(os.environ)
                                 if i.startswith(MODULE.upper() + '_')]:
        value = os.environ[my_envvar]
        if value == 'True':
            value = True
        elif value == 'False':
            value = False
        else:
            try:
                value = int(value)
            except ValueError:
                pass
        if envvar not in PATHVARS: # paths already configured from envvars
            app.config[envvar] = value
    #
    # Set version.
    #
    app.config['VERSION'] = __version__
    #
    # Set redis socket type.
    #
    if app.config['REDIS_UNIX_SOCKET']:
        app.config['RQ_REDIS_PORT'] = 0
        app.config['RQ_REDIS_HOST'] = '127.0.0.1'
        app.config['RQ_REDIS_URL'] = "unix://@'" + \
            app.config['TMP'] + '/redis.sock?db=0'
        app.config['RQ_UNIXSOCKET'] = 'unixsocket %s/redis.sock' %(app.config['TMP'])
    else:
        app.config['RQ_REDIS_URL'] = 'redis://'+\
                                     app.config['RQ_REDIS_HOST'] +\
                                     ':' +\
                                     str(app.config['RQ_REDIS_PORT']) +\
                                     '/0'
        app.config['RQ_UNIXSOCKET'] = ''
    #
    # Supervisord socket type.
    #
    if app.config['SUPERVISORD_UNIX_SOCKET']:
        app.config['SOCKET_CONF'] = '%(ENV_' +\
                                    MODULE.upper() +\
                                    '_ROOT)s/etc/' +\
                                    MODULE +\
                                    '/supervisord-unix.conf'
        app.config['SUPERVISORD_SERVERURL'] = 'unix://%{ENV_' +\
                                              MODULE.upper() +\
                                              '_TMP}s/supervisord.sock'
    else:
        app.config['SOCKET_CONF'] = '%(ENV_'+\
                                    MODULE.upper() +\
                                    '_ROOT)s/etc/supervisord-inet.conf'
        app.config['SUPERVISORD_SERVERURL'] = 'http://' + \
                app.config['SUPERVISORD_HOST'] + ':'+ \
                str(app.config['SUPERVISORD_PORT'])
    supervisord_services = ['SERVER',
                            'REDIS',
                            'ALIGNMENT',
                            'TREEBUILDER',
                            'CRASHMAIL']
    has_debug = [MODULE.upper()]
    for service in supervisord_services:
        if app.config['SUPERVISORD_START_'+service]:
            if service in has_debug:
                app.config[service+'_CONF'] = '%(ENV_' +\
                                              MODULE.upper() +\
                                              '_ROOT)s/etc/' +\
                                              service.lower() +\
                                              '-supervisord-debug.conf'
            else:
                app.config[service+'_CONF'] = '%(ENV_' +\
                                              MODULE.upper() +\
                                              '_ROOT)s/etc/' +\
                                              service.lower() +\
                                              '-supervisord.conf'
        else:
            app.config[service+'_CONF'] = ''

