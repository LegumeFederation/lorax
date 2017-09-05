# -*- coding: utf-8 -*-
import importlib
import os
import sys

package_name = os.path.basename(__file__).split('_')[0]

if package_name.upper()+'_COVERAGE' in os.environ:
    import atexit
    import coverage

    print('Starting coverage', file=sys.stderr)
    cov = coverage.coverage()
    cov.start()

    def save_coverage():
        print('Saving coverage', file=sys.stderr)
        cov.stop()
        cov.save()

    atexit.register(save_coverage)

try:
    app = importlib.import_module(package_name).app
    configure_logging = importlib.import_module(
        package_name + '.logging').configure_logging
    init_filesystem = importlib.import_module(
        package_name + '.filesystem').init_filesystem
except ModuleNotFoundError:
    print('ERROR--the needed modules for the "%s" package were not found.'
          % package_name)
    sys.exit(1)

init_filesystem(app)
configure_logging(app)

if app.config['COVERAGE']:
    import atexit
    import coverage

    coverage_config = app.config['ROOT'] + '/etc/coverage.conf'
    print('Starting coverage, config file is %s.' %coverage_config)
    cov = coverage.coverage(config_file=coverage_config,
                            auto_data=True)
    cov.start()

    def save_coverage():
        print('Saving coverage', file=sys.stderr)
        cov.stop()
        cov.save()

    atexit.register(save_coverage)

if __name__ == '__main__':
    app.run()
