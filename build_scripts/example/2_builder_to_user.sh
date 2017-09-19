#!/usr/bin/env bash
set -e
if [ -z "$LORAX_BUILD_DIR" ]; then
   echo "You must source the defs script first."
   exit 1
fi
#
# Blow away directories owned by LRX_INSTALLER that
# should be owned by LRX_USER.
#
dirlist=("$LRX_TMP"
         "$LRX_LOG/*"
)
for dir in "${dirlist[@]}" ; do
  echo "removing $dir"
  rm -rf  $dir
done
#
echo "cp of var to $LRX_USER"
mv ${LRX_VAR} ${LRX_VAR}.${LRX_INSTALLER}
$LRX_SUDO -u $LRX_USER  mkdir ${LRX_VAR}
$LRX_SUDO -u $LRX_USER cp -R ${LRX_VAR}.${LRX_INSTALLER}/ ${LRX_VAR}
rm -r ${LRX_VAR}.${LRX_INSTALLER}
#
echo "loading model data"
$LRX_SUDO -u $LRX_USER cp -R ${LRX_SCRIPT_DIR}/data/ ${LRX_VAR}/data
#
echo "testing as $LRX_USER"
$LRX_SUDO -u $LRX_USER ${LRX_ROOT}/bin/lorax_env -v start
cd $LORAX_TEST_DIR
./test_targets.sh
echo "Done testing as $LRX_USER"
