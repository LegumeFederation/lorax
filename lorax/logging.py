# -*- coding: utf-8 -*-
import logging
from logging.handlers import RotatingFileHandler
import sys
from datetime import datetime
from pathlib import Path
#
# Global variables.
#
DEFAULT_FILE_LOGLEVEL = logging.DEBUG
DEFAULT_STDERR_LOGLEVEL = logging.INFO
#
# Helper function definitions begin here.
#
def init_logging_to_stderr_and_file(app,
                                   ):
    '''Log to stderr and to a log file at different levels.
    '''
    app.mylogger = logging.getLogger('werkzeug')  # this is the logger we want
    verbose = app.config['DEBUG'],
    quiet = app.config['QUIET'],
    logfile = app.config['LOGFILE'],
    logfile_dir = Path(app.config['PATHS']['log'])
    if verbose:
        stderr_log_level = logging.DEBUG
    else:
        stderr_log_level = DEFAULT_STDERR_LOGLEVEL
    if quiet:
        file_log_level = logging.ERROR
    else:
        file_log_level = DEFAULT_FILE_LOGLEVEL
    app.mylogger.setLevel(min(file_log_level, stderr_log_level))
    #
    # Start log file.
    #
    if logfile: # start a log file
        logfile_name = app.config['LOGGER_NAME'] + '.log'
        app.config['LOGFILE_NAME'] = logfile_name
        logfile_path = Path(logfile_dir)/logfile_name
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
    app.mylogger.debug('Command line: "%s"', ' '.join(sys.argv))
    app.mylogger.debug('%s version %s',
                     app.config['LOGGER_NAME'],
                     app.config['VERSION'])
    app.mylogger.debug('Run started at %s', datetime.now().strftime('%Y%m%d-%H%M%S'))
