"""Command-line interpreter functions.

lorax is designed as a stand-alone cli rather than through Flask.
"""
#
# Standard library imports.
#
import json
import os
import pkg_resources
import pkgutil
import sys
import types
from datetime import datetime
from distutils.util import strtobool
from pydoc import locate
from pathlib import Path  # python 3.4 or later
from string import Template
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
COPYRIGHT = """Copyright (C) 2017, The National Center for Genome Resources.
All rights reserved.
"""
PROJECT_HOME = 'https://github.com/ncgr/lorax'


#
# CLI entry point.
#
@click.group(cls=FlaskGroup,
             epilog=AUTHOR + ' <' + EMAIL + '>. ' + COPYRIGHT + PROJECT_HOME)
@click.version_option(version=version, prog_name=__name__)
def cli():
    pass


def create_data_dir(app):
    """Creates a data directory, if one doesn't exist.

    :param app:
    :return:
    """
    data_dir = Path(app.config['DATA_PATH'])
    if not data_dir.is_dir():  # create logs/ dir
        try:
            data_dir.mkdir(mode=app.config['DIR_MODE'], parents=True)
        except OSError:
            app.logger.error('Unable to create data directory "%s"',
                             data_dir)
            raise OSError


@cli.command()
def run():
    """Run a lorax server directly."""
    from lorax.logging import configure_logging
    print(
        'Direct start, use of gunicorn is recommended for production.',
        file=sys.stderr)
    port = current_app.config['PORT']
    host = current_app.config['HOST']
    debug = current_app.config['DEBUG']
    configure_logging(current_app)
    create_data_dir(current_app)
    current_app.run(host=host,
                    port=port,
                    debug=debug)


def print_config_var(var, obj):
    """Print configuration variable with type and provenance.

    :param var:
    :param obj:
    :return:
    """
    if 'LORAX_' + var in os.environ:
        from_environ = ' <- from environment'
    elif var in obj.__dict__:
        from_environ = ' <- from config file'
    else:
        from_environ = ''
    val = current_app.config[var]
    if isinstance(val, str):
        quote = '"'
    else:
        quote = ''
    print('  %s type(%s) =  %s%s%s %s' % (var,
                                          type(val).__name__,
                                          quote,
                                          val,
                                          quote,
                                          from_environ))


@cli.command()
@click.option('--vartype', help='Type of variable, if not previously defined.',
              default=None)
@click.option('--verbose/--no-verbose', help='Verbose provenance.')
@click.argument('var', required=False)
@click.argument('value', required=False)
def config(var, value, vartype, verbose):
    """Gets or sets config variables."""
    config_file_path = Path(current_app.instance_path) / current_app.config[
        'SETTINGS']
    if value is None:  # No value specified, this is a get.
        config_obj = types.ModuleType('config')  # noqa
        if config_file_path.exists():
            config_file_status = 'exists'
            config_obj.__file__ = str(config_file_path)
            try:
                with config_file_path.open(mode='rb') as config_file:
                    exec(compile(config_file.read(), str(config_file_path),
                                 'exec'),
                         config_obj.__dict__)
            except IOError as e:
                e.strerror = 'Unable to load configuration file (%s)' \
                             % e.strerror
                raise
        else:
            config_file_status = 'does not exist'
            config_obj.__file__ = None
        if var is None:  # No variable specified, list them all.
            print('The instance-specific config file is at %s %s.' % (
                str(config_file_path),
                config_file_status))
            print('Listing all %d defined configuration variables:'
                  % (len(current_app.config)))
            for key in sorted(current_app.config):
                print_config_var(key, config_obj)
            return
        else:
            var = var.upper()
            if var.startswith('LORAX_'):
                var = var[6:]
            if var in current_app.config:
                if verbose:
                    print_config_var(var, config_obj)
                else:
                    print(current_app.config[var])
                return
            else:
                print('"%s" not found in configuration variables.' % var,
                      file=sys.stderr)
                sys.exit(1)
    else:  # Must be setting.
        var = var.upper()
        if var.startswith('LORAX_'):
            var = var[6:]
        if var in current_app.config and vartype is None \
                and not current_app.config[
                    var] is None:  # type defaults to current type
            value_type = type(current_app.config[var])
        else:  # get type from command line, or str if not specified
            if vartype is None:
                vartype = 'str'
            value_type = locate(vartype)
        if value_type == bool:
            value = bool(strtobool(value))
        elif value_type == str:
            pass
        else:  # load through JSON to handle dict and list types
            try:
                jsonobj = json.loads(value)
            except json.decoder.JSONDecodeError:
                print(
                    'ERROR--Unparseable string "%s". Did you use quotes?'
                    % value, file=sys.stderr)
                sys.exit(1)
            try:
                value = value_type(jsonobj)
            except TypeError:
                print(
                    'ERROR--Unable to convert "%s" of type %s to type %s.'
                    % (value, type(jsonobj).__name__, value_type.__name__),
                    file=sys.stderr)
                sys.exit(1)
        #
        # Create a config file, if needed.
        #
        if not config_file_path.exists():
            if not config_file_path.parent.exists():
                config_file_path.parent.mkdir(
                    mode=current_app.config['DIR_MODE'],
                    parents=True)
            with config_file_path.open(mode='w') as config_fh:
                print('Creating instance config file at "%s".' % str(
                    config_file_path))
                print("""# -*- coding: utf-8 -*-
'''Overrides of default lorax configurations.

This file will be placed in an instance-specific folder and sourced
after lorax.config but before environmental variables.  You may edit
this file, but lorax set_config will append and possible supercede
hand-edited values.

Note that configuration variables are all-caps.  Types are from python
typing rules.
'''""", file=config_fh)  # noqa
        if isinstance(value, str):
            quote = '"'
        else:
            quote = ''
        print('Setting %s to %s%s%s (type %s) \n in config file "%s".'
              % (var, quote, value, quote, type(value).__name__,
                 str(config_file_path)))
        with config_file_path.open(mode='a') as config_fh:
            isodate = datetime.now().isoformat()[:-7]
            print('%s = %s%s%s # set at %s' % (var,
                                               quote,
                                               value,
                                               quote,
                                               isodate),
                  file=config_fh)  # noqa



@cli.command()
def delete_config():
    """Deletes the config file."""
    config_file_path = Path(current_app.instance_path) / current_app.config[
        'SETTINGS']
    if config_file_path.exists():
        print('Deleting config file %s.' %(str(config_file_path)))
        config_file_path.unlink()


@cli.command()
def test_logging():
    """Test logging at the different levels.
    """
    configure_logging(current_app)
    current_app.logger.debug('Debug message.')
    current_app.logger.info('Info message.')
    current_app.logger.warning('Warning message.')
    current_app.logger.error('Error message.')


@cli.command()
@click.option('--force/--no-force', help='Force overwrites of existing files',
              default=False)
def create_test_files(force):
    """Create test files to the current directory.

    :return:
    """
    test_files = pkg_resources.resource_listdir(__name__, 'test')
    for filename in test_files:
        path_string = 'test/' + filename
        if not pkg_resources.resource_isdir(__name__, path_string):
            print('Creating file %s":' %filename)
            data = pkgutil.get_data(__name__, 'test/' + filename)
            file_path = Path(filename)
            if file_path.exists() and not force:
                print('ERROR-- File %s already exists.'%filename +
                      '  Use --force to overwrite.')
                sys.exit(1)
            with file_path.open(mode='wb') as fh:
                fh.write(data)
            if filename.endswith('.sh'):
                file_path.chmod(0o755)


@cli.command()
@click.option('--force/--no-force', help='Force overwrites of existing files',
              default=False)
def configure_instance(force):
    """Configuresinstance files in sys.prefix.

    :return:
    """
    out_path = Path(sys.prefix)
    print('Configuring instance at "%s".' %str(out_path))
    # Start by creating directories
    dirs = ['data', 'etc', 'var/log', 'var/redis', 'var/run']
    for dir in dirs:
        out_dir = out_path/dir
        if not out_dir.exists():
            print('Creating "%s" directory' %out_dir)
            out_dir.mkdir(parents=True)
    files = ['run_lorax.py']
    for filename in files:
        data = pkgutil.get_data(__name__, 'instance/' + filename)
        file_path = out_path / filename
        if file_path.exists() and not force:
            print('ERROR -- File %s already exists.' %filename+
                  'Use --force to overwrite.')
            sys.exit(1)
        elif file_path.exists() and force:
            operation = 'Overwriting'
        else:
            operation = 'Creating'
        with file_path.open(mode='wb') as fh:
            print('%s file "%s".'
                  %(operation,
                  str(file_path)))
            fh.write(data)
    templates = ['etc/supervisord.conf',
                 'etc/lorax.conf',
                 'etc/alignment.conf',
                 'etc/redis.conf',
                 'etc/treebuilder.conf']
    for filename in templates:
        data = pkgutil.get_data(__name__, 'instance/'+ filename)
        data_string = data.decode('UTF-8')
        template = Template(data_string)
        out_string = template.substitute(current_app.config)
        file_path = out_path / filename
        if file_path.exists() and not force:
            print('ERROR -- File %s already exists.' %filename+
                  'Use --force to overwrite.')
            sys.exit(1)
        elif file_path.exists() and force:
            operation = 'Overwriting'
        else:
            operation = 'Creating'
        with file_path.open(mode='wt') as fh:
            print('%s file "%s" from template.'
                  %(operation, str(file_path)))
            fh.write(out_string)
