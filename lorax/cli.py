'''Command-line interpreter functions.

lorax is designed as a stand-alone cli rather than through Flask.
'''
import sys
import click
from flask import current_app
from flask.cli import FlaskGroup
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

@cli.command()
def run():
    '''Run a lorax server directoy'''
    print('Direct start of lorax, discouraged for production use.')
    port = current_app.config['PORT']
    host = current_app.config['HOST']
    debug = current_app.config['DEBUG']
    print('Running lorax on http://%s:%d/.  ^C to stop.' %(host, port))
    current_app.run(host=host,
                    port=port,
                    debug=debug)

@cli.command()
@click.argument('var')
def get_config_value(var):
    '''Get the value of a configuration variable.'''
    var = var.upper()
    if var.startswith('LORAX_'):
        var = var[6:]
    if var in current_app.config:
        print(current_app.config[var])
    else:
        print('ERROR--Variable %s not found in configuration variables.' %var)
        sys.exit(1)
