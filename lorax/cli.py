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
from distutils.util import strtobool
from pydoc import locate
from pathlib import Path  # python 3.4 or later
#
#
# third-party imports.
import click
from flask import current_app
from flask.cli import FlaskGroup
from jinja2 import Environment, PackageLoader
#
# Local imports.
#
from .logs import configure_logging
from .filesystem import init_filesystem
#
# Global variables.
#
AUTHOR = 'Joel Berendzen'
EMAIL = 'joelb@ncgr.org'
COPYRIGHT = """Copyright (C) 2017, The National Center for Genome Resources.
All rights reserved.
"""
#
# CLI entry point.
#


@click.group(cls=FlaskGroup,
             epilog=AUTHOR + ' <' + EMAIL + '>. ' + COPYRIGHT)
def cli():
    pass


@cli.command()
def run(): # pragma: no cover
    """Run a server directly."""
    from .logs import configure_logging
    print('Direct start, use of gunicorn is recommended for production.',
          file=sys.stderr) # noqa
    port = current_app.config['PORT']
    host = current_app.config['HOST']
    debug = current_app.config['DEBUG']
    init_filesystem(current_app)
    configure_logging(current_app)
    current_app.run(host=host,
                    port=port,
                    debug=debug)


@cli.command()
def test_logging():
    """Test logging at the different levels."""
    configure_logging(current_app)
    current_app.logger.debug('Debug message.')
    current_app.logger.info('Info message.')
    current_app.logger.warning('Warning message.')
    current_app.logger.error('Error message.')


def walk_package(root):
    """Walk through a package_resource.

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


def copy_files(pkg_subdir, out_head, force, notemplate_exts=None):
    """Copy files from package, with templating.

    :param pkg_subdir:
    :param out_head:
    :param force:
    :param notemplate_exts:
    :return:
    """
    for root, dirs, files in walk_package(pkg_subdir):
        del dirs
        split_dir = os.path.split(root)
        if split_dir[0] == '':
            out_subdir = ''
        else:
            out_subdir = '/'.join(list(split_dir)[1:])
        out_path = out_head / out_subdir
        if not out_path.exists() and len(files) > 0:
            print('Creating "%s" directory' % str(out_path))
            out_path.mkdir(mode=int(current_app.config['DIR_MODE'], 8),
                           parents=True)
        #
        # Initialize Jinja2 template engine on this directory.
        #
        template_env = Environment(loader=PackageLoader(__name__, root),
                                   trim_blocks=True,
                                   lstrip_blocks=True
                                   )
        for filename in files:
            try:
                ext = os.path.splitext(filename)[1].lstrip('.')
            except IndexError:
                ext = ''
            if notemplate_exts is not None and ext in notemplate_exts:
                templated = 'directly'
                data_string = pkgutil.get_data(__name__,
                                               root + '/' +
                                               filename).decode('UTF-8')
            else:
                templated = 'from template'
                template = template_env.get_template(filename)
                data_string = template.render(current_app.config)
            outfilename = filename.replace(
                'server', current_app.config['NAME'])
            file_path = out_path / outfilename
            if file_path.exists() and not force:
                print('ERROR -- File %s already exists.' % str(file_path) +
                      '  Use --force to overwrite.')
                sys.exit(1)
            elif file_path.exists() and force:
                operation = 'Overwriting'
            else:
                operation = 'Creating'
            with file_path.open(mode='wt') as fh:
                print('%s file "%s" %s.'
                      % (operation, str(file_path), templated))
                fh.write(data_string)
            if filename.endswith(
                    '.sh') or filename == current_app.config['NAME']:
                file_path.chmod(0o755)


@cli.command()
@click.option('--force/--no-force', help='Force overwrites of existing files',
              default=False)
@click.option('--init/--no-init', help='Initialize filesystem',
              default=True)
@click.option('--var/--no-var', help='Create files in var directory',
              default=True)
def create_instance(force, init, var):
    """Configures instance files."""
    copy_files('etc', Path(current_app.config['ROOT']) / 'etc', force)
    if var:
        copy_files('var', Path(current_app.config['VAR']), force)
    if init:
        init_filesystem(current_app)

@cli.command()
@click.option('--force/--no-force', help='Force overwrites of existing files',
              default=False)
@click.option('--configonly/--no-configonly', help='Only create config file',
              default=False)
def create_test_files(force, configonly):
    """Create test files."""
    if not configonly:
        copy_files('test',
                   Path('.'),
                   force,
                   notemplate_exts=['hmm', 'faa', 'sh'])
    copy_files('user_conf',
               Path(os.path.expanduser(current_app.config['USER_CONFIG_PATH'])),
               force)

if __name__ == '__main__':
    cli()
