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
# Check to see if redis is running.
#
ping=`redis-cli ping 2>/dev/null`
if [ "$?" -eq 1 ]; then
  echo "ERROR--redis does not seem to be running.  Start redis-server first."
  exit 1
fi

#
# Function to check for queue workers.
#
test_workers () {
   n_workers=`lorax rq info $1 | grep workers | awk '{print $1}'`
   if [ "$n_workers" -eq 0 ]; then
      echo "ERROR--${1} queue is not running."
      echo "Issue \"lorax rq worker ${1}\" on worker and restart."
      exit 1
   else
      echo "${n_workers} workers for ${1} queue, OK."
   fi
}
async=`lorax get_config RQ_ASYNC`
if [[ $async -eq "True" ]]; then
   test_workers alignment 
   test_workers treebuilding
fi
#
# Start lorax server
#
if [ "$LORAX_CONFIGURATION" ==  "production" ]; then
   echo "Starting lorax via gunicorn at http://${LORAX_HOST}:${LORAX_PORT}"
   gunicorn --bind "${LORAX_HOST}":"${LORAX_PORT}" run:app
else
   lorax run
fi
