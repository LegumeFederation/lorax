'''Command-line interpreter functions.

lorax is designed as a stand-alone cli rather than through Flask.
'''
#
# Standard library imports.
#
import sys
import socket
from datetime import datetime
from pydoc import locate
from distutils.util import strtobool
from pathlib import Path # python 3.4 or later
#
# third-party imports.
import click
from flask import current_app
from flask.cli import FlaskGroup
#
# Local imports.
#
from .version import version
#
# Global variables.
#
AUTHOR = 'Joel Berendzen'
EMAIL = 'joelb@ncgr.org'
COPYRIGHT = """Copyright (C) 2017, The National Center for Genome Resources.  All rights reserved.
"""
PROJECT_HOME = 'https://github.com/ncgr/lorax'
#
# CLI entry point.
#
@click.group(cls=FlaskGroup, epilog=AUTHOR + ' <'+EMAIL+'>. ' + COPYRIGHT + PROJECT_HOME)
@click.version_option(version=version, prog_name=__name__)
@click.pass_context
def cli(ctx):
    pass

def create_data_dir(app):
    '''Creates a data directory, if one doesn't exist.
    
    :param app: 
    :return: 
    '''
    data_dir = Path(app.config['PATHS']['data'])
    if not data_dir.is_dir(): # create logs/ dir
        try:
            data_dir.mkdir(mode=app.config['PATHS']['mode'], parents=True)
        except OSError:
            app.mylogger.error('Unable to create data directory "%s"',
                             data_dir)
            raise OSError


@cli.command()
def run():
    '''Run a lorax server directly.'''
    from lorax.logging import configure_logging
    print('Direct start of lorax, use of gunicorn is recommended for production.',
          file=sys.stderr)
    port = current_app.config['PORT']
    host = current_app.config['HOST']
    debug = current_app.config['DEBUG']
    configure_logging(current_app)
    create_data_dir(current_app)
    print('Running lorax on http://%s:%d/.  ^C to stop.' %(host, port),
          file=sys.stderr)
    current_app.run(host=host,
                    port=port,
                    debug=debug)

@cli.command()
@click.argument('var')
def get_config(var):
    '''Get the value of a configuration variable.'''
    var = var.upper()
    if var.startswith('LORAX_'):
        var = var[6:]
    if var in current_app.config:
        print(current_app.config[var])
    else:
        print('ERROR--Variable %s not found in configuration variables.' %var,
              file=sys.stderr)
        sys.exit(1)


@cli.command()
@click.option('--type',help='Type of variable if not string.', default='str')
@click.argument('var')
@click.argument('value')
def set_config(var, value, type):
    '''Sets the value of a configuration variable in SETTINGS file.'''
    var = var.upper()
    if var.startswith('LORAX_'):
        var = var[6:]
    value_type = locate(type)
    if value_type == bool:
        value = bool(strtobool(value))
        print(value)
    else:
        value = value_type(value)
    config_file_path = Path(current_app.instance_path)/current_app.config['SETTINGS']
    current_app.mylogger.info('Instance configuration file at "%s".', str(config_file_path))
    with config_file_path.open( mode='a') as config_fh:
        isodate = datetime.now().isoformat()
        hostname = socket.gethostbyaddr(socket.gethostname())[0]
        if isinstance(value, str):
            quote = '"'
        else:
            quote = ''
        print('Setting %s to %s%s%s in config file "%s".' %(var,
                                                            quote,
                                                            value,
                                                            quote,
                                                            str(config_file_path)),
              file=sys.stderr)
        print('%s = %s%s%s # set on %s at %s' %(var,
                                            quote,
                                            value,
                                            quote,
                                            hostname,
                                            isodate),
              file=config_fh)
