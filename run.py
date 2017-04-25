#!/usr/bin/env python3
from lorax import app
from lorax.logging import configure_logging
from lorax.cli import create_data_dir

configure_logging(app)
create_data_dir(app)

if __name__ == '__main__':
    app.run()
