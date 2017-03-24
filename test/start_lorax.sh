#!/bin/bash
# starts the lorax server
#
if [ -z "$FLASK_APP" ] ; then
	echo "Must set FLASK_APP before running this script"
	exit 1
fi
if [ -z "$LORAX_HOST" ] ; then
	echo "Must set LORAX_HOST before running this script"
	exit 1
fi
if [ -z "$LORAX_PORT" ] ; then
	echo "Must set LORAX_PORT before running this script"
	exit 1
fi
if [ -z "$LORAX_CONFIGURATION" ] ; then
	echo "Must set LORAX_CONFIGURATION before running this script"
	exit 1
fi
PYTHON="$LORAX_PYTHON"
#
if [[ $LORAX_CONFIGURATION -eq "production" ]]; then
   gunicorn --bind "${LORAX_HOST}":"${LORAX_PORT}" run:app
else
   lorax run
fi
