#!/bin/bash
#
# Environmental-variable parameters for lorax and associated shell scripts.
#
# Run as "source lorax_config.sh".
#
export FLASK_APP="lorax"
#
# Set the python executable to use.  This is only used in the
# shell scripts and only for direct starts.
#
export LORAX_PYTHON="python" # may need to be python3, this i
#
# Many settings can be handled via one of the defined configurations:
#
#export LORAX_CONFIGURATION="default"
#export LORAX_CONFIGURATION="development"
export LORAX_CONFIGURATION="testing"
#export LORAX_CONFIGURATION="production" # similar to default, but using gunicorn
#
# These values are being derived from configuration files,
# but they may also be set directly.  Note that they can't be
# determined this way if this command is run from a directory
# other than the same directory as the lorax instance.  Note
# also that running via gunicorn can overlay these values.
#
export LORAX_HOST=`lorax get_config HOST 2>/dev/null`
export LORAX_PORT=`lorax get_config PORT 2>/dev/null`
#
env | grep "LORAX"
