'''Command-line interpreter functions.

lorax is designed as a stand-alone cli rather than through Flask.
'''
#
# Standard library imports.
#
import sys
import os
import pkg_resources
import pkgutil
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
from .logging import configure_logging
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
    data_dir = Path(app.config['DATA_PATH'])
    if not data_dir.is_dir(): # create logs/ dir
        try:
            data_dir.mkdir(mode=app.config['DIR_MODE'], parents=True)
        except OSError:
            app.logger.error('Unable to create data directory "%s"',
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
    current_app.run(host=host,
                    port=port,
                    debug=debug)


@cli.command()
@click.option('--type',help='Type of variable if not string.', default='str')
@click.argument('var', required=False)
@click.argument('value', required=False)
def config_value(var, value, type):
    '''Gets or sets config variables.'''
    if value == None:  # No value specified, this is a get.
        if var == None: # No variable specified, list them all.
            print('Listing all %d defined configuration variables:'
                  %(len(current_app.config)))
            for key in sorted(current_app.config):
                if 'LORAX_' + key in os.environ:
                    from_environ = ' <- from environment'
                else:
                    from_environ = ''
                print('  %s =  %s %s' %(key,
                                      current_app.config[key],
                                      from_environ))
            return
        else:
            var = var.upper()
            if var.startswith('LORAX_'):
                var = var[6:]
            if var in current_app.config:
                print(current_app.config[var])
                return
            else:
                print('"%s" not found in configuration variables.' % var,
                      file=sys.stderr)
                sys.exit(1)
    else: # Must be setting.
        var = var.upper()
        if var.startswith('LORAX_'):
            var = var[6:]
        value_type = locate(type)
        if value_type == bool:
            value = bool(strtobool(value))
        else:
            value = value_type(value)
        #
        # Create a config file, if needed.
        #
        config_file_path = Path(current_app.instance_path)/current_app.config['SETTINGS']
        if not config_file_path.exists():
            if not config_file_path.parent.exists():
                config_file_path.parent.mkdir(mode=current_app.config['DIR_MODE'],
                                              parents=True)
            with config_file_path.open(mode='w') as config_fh:
                current_app.logger.warning('Creating instance config file at "%s".',
                                          str(config_file_path))
                print("""# -*- coding: utf-8 -*-
'''Overrides of default lorax configurations.

This file will be placed in an instance-specific folder and sourced
after lorax.config but before environmental variables.  You may edit
this file, but lorax set_config will append and possible supercede
hand-edited values.

Note that configuration variables are all-caps.  Types are from python
typing rules.
'''""", file=config_fh)

        with config_file_path.open( mode='a') as config_fh:
            isodate = datetime.now().isoformat()[:-7]
            if isinstance(value, str):
                quote = '"'
            else:
                quote = ''
            current_app.logger.warning('Setting %s to %s%s%s in config file "%s".',
                                         var,
                                         quote,
                                         value,
                                         quote,
                                         str(config_file_path))
            print('%s = %s%s%s # set at %s' %(var,
                                                quote,
                                                value,
                                                quote,
                                                isodate),
                  file=config_fh)


@cli.command()
def test_logging():
    '''Test logging at the different levels.
    '''
    configure_logging(current_app)
    current_app.logger.debug('Debug message.')
    current_app.logger.info('Info message.')
    current_app.logger.warning('Warning message.')
    current_app.logger.error('Error message.')


@cli.command()
@click.option('--force/--no-force', help='Force overwrites of existing files',
              default=False)
def copy_test_files(force):
    '''Copy files test files to the current working directory.
    
    :return: 
    '''
    configure_logging(current_app)
    test_files = pkg_resources.resource_listdir(__name__, 'test')
    for filename in test_files:
        path_string = 'test/' + filename
        if not pkg_resources.resource_isdir(__name__, path_string):
            current_app.logger.info('Creating file %s":', filename)
            data = pkgutil.get_data(__name__, 'test/'+filename)
            file_path = Path(filename)
            if file_path.exists() and not force:
                current_app.logger.error('File %s already exists.  Use --force to overwrite.', filename)
            with file_path.open(mode='wb') as fh:
                fh.write(data)
