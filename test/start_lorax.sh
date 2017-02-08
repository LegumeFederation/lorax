#!/bin/bash
# starts the lorax server
#
if [[ ! -v LORAX_HOST ]] ; then
	echo "Must set LORAX_HOST before running this script"
	exit 1
fi
if [[ ! -v LORAX_PORT ]] ; then
	echo "Must set LORAX_PORT before running this script"
	exit 1
fi
if [[ -v VIRTUAL_ENVIRONMENT ]] ; then
	# in a virtual environment
	PYTHON="python"
else
	PYTHON="python3"
fi
lorax --host ${LORAX_HOST} --port ${LORAX_PORT}
