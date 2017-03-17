#!/bin/bash
# starts the lorax server
#
if [ -z "$LORAX_HOST" ] ; then
	echo "Must set LORAX_HOST before running this script"
	exit 1
fi
if [ -z "$LORAX_PORT" ] ; then
	echo "Must set LORAX_PORT before running this script"
	exit 1
fi
PYTHON="$LORAX_PYTHON"
lorax
