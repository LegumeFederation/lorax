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
from flask_rq2 import RQ
#
# local imports
#
from .config import configure_app
from .filesystem import init_filesystem
from .logs import configure_logging
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
configure_app(app)
configure_logging(app)
init_filesystem(app)
#
# Create a global RQ object
#
rq = RQ(app)
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
                'start_date': app.config['DATETIME']}
    return Response(json.dumps(app_data), mimetype=JSON_MIMETYPE)


@app.route('/test_exception')
def test_exception(): # pragma: no cover
    raise RuntimeError('Intentional error from /test_exception')


from .core import * # noqa

if __name__ == '__main__':
    app.run()
