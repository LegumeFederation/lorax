#!/usr/bin/env bash
if [ -z "$LORAX_TEST_DIR" ]; then
  echo "ERROR--you must source the defs file before running this script."
  exit 1
fi
set -e
error_exit() {
  >&2 echo "ERROR--unexpected exit from ${BASH_SOURCE} script at line:"
  >&2 echo "   $BASH_COMMAND"
  >&2 echo "This failure may have left a running server instance."
  >&2 echo "You should stop it with the command"
  >&2 echo "   \"sudo service lorax stop\"."
}
echo "Testing production instance (not necessarily on this server)."
# Link to prod lorax config directory
rm -f ~/.lorax
ln -s ${LRX_INSTALLER_HOME}/.lorax-prod ~/.lorax
echo "testing service in $LORAX_TEST_DIR..."
pushd $LORAX_TEST_DIR
./test_targets.sh
popd 
trap - EXIT
echo "Tests completed successfully."
exit 0
