# -*- coding: utf-8 -*-
import importlib
import os
import sys

package_name = os.path.basename(__file__).split('_')[0]

try:
    app = importlib.import_module(package_name).app
    configure_logging = importlib.import_module(
        package_name+'.logging').configure_logging
    create_dir = importlib.import_module(package_name+'.cli').create_dir
except ModuleNotFoundError:
    print('ERROR--the needed modules for the "%s" package were not found.'
          %package_name)
    sys.exit(1)

configure_logging(app)
create_dir('DATA', '', app=app)
create_dir('USERDATA', '', app=app)

if __name__ == '__main__':
    app.run()
