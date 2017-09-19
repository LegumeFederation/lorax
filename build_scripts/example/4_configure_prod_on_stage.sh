#!/usr/bin/env bash
#
# starting from clean empty directory
#
set -e
if [ -z "$LORAX_BUILD_DIR" ]; then
   echo "You must source the defs script first."
   exit 1
fi
error_exit() {
  >&2 echo "ERROR--unexpected exit from ${BASH_SOURCE} script at line:"
  >&2 echo "   $BASH_COMMAND"
}
trap error_exit EXIT
echo "Changing configuration to prod"
cd $LORAX_BUILD_DIR
rm my_config.sh
ln -s ~${LRX_INSTALLER}/prod_config.sh ./my_config.sh
/usr/local/www/lorax-${LRX_VERSION}/bin/lorax_env lorax config --delete
pushd $LORAX_BUILD_DIR
./lorax_tool configure_pkg --no-init --no-var
popd
/usr/local/www/lorax-${LRX_VERSION}/bin/lorax_env lorax create_test_files --force --configonly
echo "Ready for move to production."
trap - EXIT
exit 0
