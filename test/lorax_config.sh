#!/bin/bash
#
# Environmental-variable parameters for lorax and associated shell scripts.
#
# Run as "source lorax_config.sh".
#
export LORAX_HOST="127.0.0.1"
export LORAX_PORT="58926"
export LORAX_PYTHON="python" # may need to be python3, this is for venv
#
# Overrides of default settings in python file.  Note this
# variable must translate to an absolute path name.
#
export LORAX_SETTINGS='../test/config.py'
