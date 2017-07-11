# -*- coding: utf-8 -*-
"""Command-line interpreter functions.

These functions extend the Flask CLI.

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
from .logging import configure_logging
#
# Global variables.
#
MODULE = __name__.split('.')[0]
AUTHOR = 'Joel Berendzen'
EMAIL = 'joelb@ncgr.org'
COPYRIGHT = """Copyright (C) 2017, The National Center for Genome Resources.
All rights reserved.
"""
PROJECT_HOME = 'https://github.com/LegumeFederation/'+__name__
#
# CLI entry point.
#
@click.group(cls=FlaskGroup,
             epilog=AUTHOR + ' <' + EMAIL + '>. ' + COPYRIGHT + PROJECT_HOME)
def cli():
    pass


def create_dir(config_path, subdir, app=current_app):
    """Creates runtime directories, if they don't exist.

    :param app:
    :return:
    """
    dir_path = Path(app.config[config_path])/subdir
    if not dir_path.is_dir():  # create logs/ dir
        app.logger.info('Creating directory %s/%s at %s.',
                        config_path, subdir, str(dir_path))
        try:
            dir_path.mkdir(mode=app.config['DIR_MODE'],
                           parents=True)
        except OSError:
            app.logger.error('Unable to create directory "%s"',
                             str(dir_path))
            raise OSError


@cli.command()
def run():
    """Run a server directly."""
    from  .logging import configure_logging
    print(
        'Direct start, use of gunicorn is recommended for production.',
        file=sys.stderr)
    port = current_app.config['PORT']
    host = current_app.config['HOST']
    debug = current_app.config['DEBUG']
    configure_logging(current_app)
    create_dir('DATA', '')
    create_dir('USERDATA', '')
    current_app.run(host=host,
                    port=port,
                    debug=debug)


def print_config_var(var, obj):
    """Print configuration variable with type and provenance.

    :param var:
    :param obj:
    :return:
    """
    if __name__.upper()+'_' + var in os.environ:
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
@click.option('--vartype',
              help='Type of variable, if not previously defined.',
              default=None)
@click.option('--verbose/--no-verbose', help='Verbose provenance.')
@click.option('--delete/--no-delete',
              help='Deletes config file, arguments ignored.')
@click.argument('var', required=False)
@click.argument('value', required=False)
def config(var, value, vartype, verbose, delete):
    """Gets, sets, or deletes config variables."""
    config_file_path = Path(current_app.config['ROOT']) \
                       / 'etc'/ current_app.config['SETTINGS']
    if delete:
        if config_file_path.exists():
            print('Deleting config file %s.' %(str(config_file_path)))
            config_file_path.unlink()
            sys.exit(0)
        else:
            print('ERROR--config file %s does not exist.'
                  %(str(config_file_path)))
            sys.exit(1)
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
            if var.startswith(__name__.upper()+'_'):
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
        if var.startswith(__name__.upper()+'_'):
            var = var[6:]
        if var in current_app.config and vartype is None \
                and not current_app.config[
                    var] is None:  # type defaults to current type
            old_value = current_app.config[var]
            value_type = type(old_value)
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
        create_dir('ROOT', 'etc/')
        if not config_file_path.exists():
            with config_file_path.open(mode='w') as config_fh:
                print('Creating instance config file at "%s".' % str(
                    config_file_path))
                print("""# -*- coding: utf-8 -*-
'''Overrides of default configurations.

This file will be placed in an instance-specific folder and sourced
after default configs but before environmental variables.  You may
hand-edit this file, but further sets will append and possibly supercede
hand-edited values.  You may also delete these file and start again
with the config --delete switch.

Note that configuration variables are all-caps.  Types are from python
typing rules.
'''""", file=config_fh)  # noqa
        if isinstance(value, str):
            quote = '"'
        else:
            quote = ''
        print('%s was %s%s%s, now set to %s%s%s (type %s) \n in config file "%s".'
              % (var,
                 quote, old_value, quote,
                 quote, value, quote,
                 type(value).__name__,
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
    pwd_path = Path('.')
    test_files = pkg_resources.resource_listdir(__name__, 'test')
    for filename in test_files:
        path_string = 'test/' + filename
        if not pkg_resources.resource_isdir(__name__, path_string):
            print('Creating file ./%s":' %filename)
            data = pkgutil.get_data(__name__, 'test/' + filename)
            file_path = pwd_path/filename
            if file_path.exists() and not force:
                print('ERROR-- File %s already exists.'%filename +
                      '  Use --force to overwrite.')
                sys.exit(1)
            with file_path.open(mode='wb') as fh:
                fh.write(data)

def walk_package(root):
    """walk through a package_resource
    :type module_name: basestring
    :param module_name: module to search in
    :type dirname: basestring
    :param dirname: base directory
    """
    dirs = []
    files = []
    for name in pkg_resources.resource_listdir(__name__, root):
        fullname = root + '/' + name
        if pkg_resources.resource_isdir(__name__, fullname):
            dirs.append(fullname)
        else:
            files.append(name)
    for new_path in dirs:
        yield from walk_package(new_path)
    yield root, dirs, files


def copy_files(pkg_subdir, out_head, force):
    for root, dirs, files in walk_package(pkg_subdir):
        split_dir = os.path.split(root)
        if split_dir[0] == '':
            out_subdir = ''
        else:
            out_subdir = '/'.join(list(split_dir)[1:])
        out_path = out_head / out_subdir
        if not out_path.exists() and len(files)>0:
            print('Creating "%s" directory' %str(out_path))
            out_path.mkdir(mode=current_app.config['DIR_MODE'],
            parents=True)
        for filename in files:
            executable = False
            if filename.endswith('.sh'):
                executable = True
            data = pkgutil.get_data(__name__,
                                    root +
                                    '/' +
                                    filename)
            data_string = data.decode('UTF-8')
            if not executable: # template first
                template_string = Template(data_string)
                data_string = template_string.substitute(current_app.config)
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
                fh.write(data_string)
            if executable:
                file_path.chmod(0o755)

@cli.command()
@click.option('--force/--no-force', help='Force overwrites of existing files',
              default=False)
def create_instance(force):
    """Configures instance files.

    :return:
    """
    copy_files('etc', Path(current_app.config['ROOT'])/'etc', force)
    dirs = [('TMP',''),
            ('LOG',''),
            ('VAR','redis'),
            ('VAR', 'run'),
            ('DATA',''),
            ('USERDATA','')]
    for dir_tuple in dirs:
        create_dir(*dir_tuple)

