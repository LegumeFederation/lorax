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
import logging
import sys
from logging.handlers import RotatingFileHandler
from datetime import datetime
from pathlib import Path  # python 3.4
#
# Third-party imports.
#
from flask import request

#
# Global variables.
#
DEFAULT_FILE_LOGLEVEL = logging.INFO
DEFAULT_STDERR_LOGLEVEL = logging.WARNING


class ContextualFilter(logging.Filter):
    """A logging filter with request-based info."""

    def filter(self, log_record):
        log_record.utcnow = (datetime.utcnow()
                             .strftime('%Y-%m-%d %H:%M:%S%Z'))
        try:
            log_record.url = request.path
            log_record.method = request.method
        except RuntimeError:
            log_record.url = ''
            log_record.method = ''

        return True


def configure_logging(app):
    """ Configure logging to stderr and a log file.

    :param app:
    :return:
    """
    if app.config['DEBUG']:
        stderr_log_level = logging.DEBUG
    else:
        stderr_log_level = DEFAULT_STDERR_LOGLEVEL
    if app.config['QUIET']:
        file_log_level = logging.ERROR
    else:
        file_log_level = DEFAULT_FILE_LOGLEVEL
    app.logger.addFilter(ContextualFilter())
    app.logger.setLevel(logging.DEBUG)
    for handler in app.logger.handlers:  # set levels on existing handlers
        handler.setLevel(stderr_log_level)
        handler.setFormatter(
            logging.Formatter(app.config['STDERR_LOG_FORMAT']))
    #
    # Start log file.
    #
    if app.config['LOGFILE']:  # start a log file
        logfile_name = app.config['LOGGER_NAME'] + '.log'
        app.config['LOGFILE_NAME'] = logfile_name
        logfile_path = Path(app.config['LOG_PATH']) / logfile_name
        if app.config['DEBUG']:
            print('Logging to file "%s".' % str(logfile_path),
                  file=sys.stderr)
        if not logfile_path.parent.is_dir():  # create logs/ dir
            try:
                logfile_path.parent.mkdir(mode=app.config['DIR_MODE'],
                                          parents=True)
            except OSError:
                app.logger.error('Unable to create logfile directory "%s"',
                                 logfile_path.parent)
                raise OSError
        log_handler = RotatingFileHandler(str(logfile_path),
                                          maxBytes=app.config[
                                              'LOGFILE_MAXBYTES'],
                                          backupCount=app.config[
                                              'LOGFILE_BACKUPCOUNT'])

        log_handler.setLevel(file_log_level)
        werkzeug_logger = logging.getLogger('werkzeug')
        werkzeug_logger.addHandler(log_handler)
        for handler in app.logger.handlers:  # set levels on existing handlers
            handler.setLevel(file_log_level)
            handler.setFormatter(
                logging.Formatter(app.config['STDERR_LOG_FORMAT']))
        app.logger.addHandler(log_handler)
    #
    # Do some logging on startup.
    #
    app.logger.debug('Command line: "%s"', ' '.join(sys.argv))
    app.logger.debug('%s version %s',
                     app.config['LOGGER_NAME'],
                     app.config['VERSION'])
    app.logger.debug('Run started at %s',
                     datetime.now().strftime('%Y%m%d-%H%M%S'))
