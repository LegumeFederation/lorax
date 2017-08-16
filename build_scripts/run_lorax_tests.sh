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
${root}/bin/lorax_env supervisord
#
# Sleep for a while, then get the statuses.
#
sleep 20
${root}/bin/lorax_env supervisorctl status
echo "Hopefully you just saw a set of processes with status RUNNING!"
sleep 5
#
# Create the test directory and cd to it.
#
rm -rf test_lorax
rm -f ~/.lorax/lorax_rc
mkdir test_lorax
pushd test_lorax
echo "Getting a set of test files in test_lorax directory."
${root}/bin/lorax_env lorax create_test_files
echo "Running test of lorax server."
./lorax_test.sh
echo ""
echo "Hopefully you just got the message  \"lorax tests completed successfully\" ."
sleep 5
popd
#
# Clean up.
#
echo "Stopping lorax processes."
${root}/bin/lorax_env supervisorctl shutdown
rm -r test_lorax
echo "Tests completed successfully."
trap - EXIT
exit 0
