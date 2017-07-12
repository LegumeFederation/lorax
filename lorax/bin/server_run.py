# -*- coding: utf-8 -*-
import importlib
import os
import sys

package_name = os.path.basename(__file__).split('_')[0]

try:
    app = importlib.import_module(package_name).app
    configure_logging = importlib.import_module(
        package_name+'.logging').configure_logging
    init_filesystem = importlib.import_module(package_name+'.filesystem').init_filesystem
except ModuleNotFoundError:
    print('ERROR--the needed modules for the "%s" package were not found.'
          %package_name)
    sys.exit(1)

init_filesystem(app)
configure_logging(app)

if __name__ == '__main__':
    app.run()
