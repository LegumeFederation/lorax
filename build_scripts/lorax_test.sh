#!/usr/bin/env bash
script_name=`basename "${BASH_SOURCE}"`
pkg="${script_name%_test.sh}"
testdir=~/.${pkg}/test
DOC="""You are about to run a short test of the lorax installation
in the ${testdir} directory.
Testing should take about 2 minutes on modest hardware.
Interrupt this script if you do not wish to test at this time.
"""
if [ "$1" != "-y" ]; then
   echo "$DOC"
   read -p "Do you want to continue? <(y)> " response
   if [ ! -z "$response" ]; then
      if [ "$response" != "y" ]; then
         exit 1
      fi
   fi
fi
set -e # exit on errors
error_exit() {
   echo "ERROR--unexpected exit from test script at line:"
   echo "   $BASH_COMMAND"
}
trap error_exit EXIT
#
# Run lorax.
#
root="`./lorax_build.sh set root_dir`"
echo "Running lorax processes."
${root}/bin/lorax_env supervisord
#
# Wait until nothing is STARTING.
#
while ${root}/bin/lorax_env supervisorctl status | grep STARTING >/dev/null; do sleep 5; done
${root}/bin/lorax_env supervisorctl status
#
# Create the test directory and cd to it.
#
mkdir -p ${testdir}
pushd ${testdir}
echo "Getting a set of test files in the ${test_dir} directory."
${root}/bin/lorax_env lorax create_test_files --force
echo "Running test of lorax server."
./test_targets.sh
echo ""
popd
#
# Clean up.  Note that lorax process doesn't stop properly from
# shutdown alone across all platforms.
#
echo "Stopping lorax processes."
${root}/bin/lorax_env supervisorctl stop lorax alignment treebuilding nginx
${root}/bin/lorax_env supervisorctl shutdown
echo "Tests completed successfully."
trap - EXIT
exit 0
