# -*- coding: utf-8 -*-
"""Configure and run a queued web service.
"""
#
# standard library imports
#
import json
import os
from sys import prefix
from pathlib import Path  # python 3.4
#
# third-party imports
#
from flask import Flask, Response
from flask_cli import FlaskCLI
from flask_rq2 import RQ
import rq_dashboard
from healthcheck import HealthCheck, EnvironmentDump
import coverage
#
# Start coverage if COVERAGE_PROCESS_START is pointed at a config file.
#
coverage.process_startup()
#
# local imports
#
from .config import configure_app
#
# Non-configurable global constants.
#
# MIME types.
JSON_MIMETYPE = 'application/json'
TEXT_MIMETYPE = 'text/plain'
#
# Application data.
#
MAINTAINER = 'Joel Berendzen'
GIT_REPO = 'https://github.com/LegumeFederation/lorax'
#
# Create an app object and configure it in the directory
# specified by MYAPP_ROOT (or sys.prefix if not specified).
#
app = Flask(__name__,
            instance_path=os.getenv(__name__.split('.')[0].upper() +
                                    '_ROOT', prefix),
            template_folder='templates')
FlaskCLI(app)
app.config.from_object(rq_dashboard.default_settings)
configure_app(app)
#
# Create a global RQ object, with dashboard at /rq.
#
rq = RQ(app)
if app.config['RQ_ASYNC']:
    app.register_blueprint(rq_dashboard.blueprint, url_prefix="/rq")
#
# Application data for optional environment dump.
#
def application_data():
    return {'maintainer': MAINTAINER,
            'git_repo': GIT_REPO}
#
# Create /healthcheck and /environment URLs.
#
health = HealthCheck(app, '/healthcheck')
envdump = EnvironmentDump(app, '/environment')
envdump.add_section('application', application_data)
#
# Helper function defs start here.
#
def get_file(subpath, file_type='data', mode='U'):
    """Get a file, returning exceptions if they exist.

    :param subpath: path within data or log directories.
    :param file_type: 'data' or 'log'.
    :param mode: 'U' for string, 'b' for binary.
    :return:
    """
    if file_type == 'data':
        file_path = Path(app.config['DATA']) / subpath
    elif file_type == 'log':
        file_path = Path(app.config['LOG']) / subpath
    else:
        app.logger.error('Unrecognized file type %s.', file_type)
        return
    try:
        return file_path.open(mode='r' + mode).read()
    except IOError as exc:
        return str(exc)
#
# Target definitions begin here.
#
@app.route('/status')
def hello_world():
    """

    :return: JSON application data
    """
    app_data = {'name': __name__,
                'version': app.config['VERSION'],
                'start_date': app.config['DATETIME']}
    return Response(json.dumps(app_data), mimetype=JSON_MIMETYPE)


@app.route('/log.txt')
def return_log():
    """Return the log file.

    :return: text/plain response
    """
    content = get_file(__name__ + '_server.log',
                       file_type='log')
    return Response(content, mimetype=TEXT_MIMETYPE)


@app.route('/test_exception')
def test_exception(): # pragma: no cover
    raise RuntimeError('Intentional error from /test_exception')


from .core import * # noqa