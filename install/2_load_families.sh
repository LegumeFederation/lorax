#!/bin/bash
lorax_env -v start
pushd $LORAX_TEST_DIR
./install_families.sh -y
popd
lorax_env -v stop
echo "loading done"
