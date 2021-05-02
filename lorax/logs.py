# -*- coding: utf-8 -*-
"""Set up logging.
"""
#
# Library imports.
#
import logging
import os
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
DEFAULT_STDERR_LOGLEVEL = logging.WARNING
SERVICE_NAME = os.getenv('FLASK_APP', __name__.split('.')[0])

class ContextualFilter(logging.Filter):
    """A logging filter with request-based info."""

    def filter(self, record):
        record.utcnow = (datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S%Z'))
        try:
            record.url = request.path
            record.method = request.method
        except RuntimeError:
            record.url = ''
            record.method = ''

        return True


def configure_logging(app):
    """ Configure logging to stderr

    :param app:
    :return:
    """
    if app.config['DEBUG']:  # pragma: no cover
        stderr_log_level = logging.DEBUG
    else:
        stderr_log_level = DEFAULT_STDERR_LOGLEVEL
    app.logger.addFilter(ContextualFilter())
    app.logger.setLevel(logging.DEBUG)
    for handler in app.logger.handlers:  # set levels on existing handlers
        handler.setLevel(stderr_log_level)
        handler.setFormatter(
            logging.Formatter(app.config['STDERR_LOG_FORMAT']))
    #
    # Start Sentry monitoring, if SENTRY_DNS is configured.
    #
    if app.config['SENTRY_DSN'] is not '':  # pragma: no cover
        from raven.contrib.flask import Sentry
        # import logging
        Sentry(app,
               dsn=app.config['SENTRY_DSN'],
               # logging=True,
               # level=logging.ERROR
               )

    #
    # Do some logging on startup.
    #
    app.logger.debug('Command line: "%s"', ' '.join(sys.argv))
    app.logger.debug('%s version %s',
                     SERVICE_NAME,
                     app.config['VERSION'])
    app.logger.debug('Run started at %s',
                     datetime.now().strftime('%Y%m%d-%H%M%S'))
