# -*- coding: utf-8 -*-
"""Create and manage essential filesystem locations."""

import os
from pathlib import Path # python 3.4 or later
from flask import current_app
from .config_file import create_config_file

DIRS = [('TMP', ''),
        ('LOG', ''),
        ('VAR', 'redis'),
        ('VAR', 'run'),
        ('DATA', ''),
        ('USERDATA', '')]
SERVICE_NAME = os.getenv('FLASK_APP', __name__.split('.')[0])

def create_dir(config_path, subdir, app):
    """Creates runtime directories, if they don't exist."""
    dir_path = Path(app.config[config_path])/subdir
    if not dir_path.is_dir():  # create logs/ dir
        print('Creating directory %s/%s at %s.'
              %(config_path, subdir, str(dir_path)))
        try:
            dir_path.mkdir(mode=int(app.config['DIR_MODE'],8),
                           parents=True)
        except OSError:
            print('Unable to create directory "%s"'
                  %(str(dir_path)))
            raise OSError


def init_filesystem(app):
    """Initialize the filesystem."""
    for dir_tuple in DIRS:
        create_dir(*dir_tuple, app=app)
    #
    # Config file may not exist if SETTINGS value was changed.
    #
    create_config_file(Path(app.config['ROOT'])/ 'etc' /
                       app.config['SETTINGS'])