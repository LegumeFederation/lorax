#!/usr/bin/env bash
#
# Test lorax installation.
#
set -e # exit on errors
error_exit() {
   echo "ERROR--unexpected exit from test script at line:"
   echo "   $BASH_COMMAND"
}
trap error_exit EXIT
#
# Run lorax.
#
root="`./lorax_build.sh root`"
echo "Running lorax processes."
${root}/lorax_env supervisord
#
# Sleep for a while, then get the statuses.
#
sleep 10
${root}/lorax_env supervisorctl status
echo "Hopefully you just saw a set of processes with status RUNNING!"
sleep 10
#
# Create the test directory and cd to it.
#
rm -rf test_lorax
rm -f ~/.lorax/lorax_rc
pushd test_lorax
${root}/lorax_env lorax_create_test_files
echo "Running test of lorax server."
./lorax_test.sh
echo "Hopefully you just got the message  \"lorax tests completed successfully\" ."
sleep 10
popd
#
# Clean up.
#
echo "Stopping lorax processes."
${root}/lorax_env supervisorctl stop
trap - EXIT
exit 0
