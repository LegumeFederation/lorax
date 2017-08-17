#!/usr/bin/env bash
#
#  This script builds lorax and its binary dependencies.
#  The example here is for a build on linux with AVX2 hardware.
#
set -e
error_exit() {
  echo "ERROR--unexpected exit from ${BASH_SOURCE} at line"
  echo "   $BASH_COMMAND"
}
trap error_exit EXIT
#
# Configure the build.
#
./lorax_build.sh set top_dir ~
./lorax_build.sh set bin_dir ~/bin  # dir in PATH where lorax_env is symlinked
./lorax_build.sh set directory_version 0.94
./lorax_build.sh set var_dir "`./lorax_build.sh root`/var"
./lorax_build.sh set tmp_dir "`./lorax_build.sh set var_dir`/tmp"
./lorax_build.sh set log_dir "`./lorax_build.sh set var_dir`/log"
./lorax_build.sh set make make
./lorax_build.sh set cc gcc
./lorax_build.sh set python 3.6.2
./lorax_build.sh set hmmer 3.1b2
./lorax_build.sh set raxml 8.2.11
./lorax_build.sh set raxml_model .AVX2.PTHREADS.gcc
./lorax_build.sh set raxml_binsuffix -PTHREADS-AVX2
./lorax_build.sh set redis 4.0.1
./lorax_build.sh set redis_cflags ""
./lorax_build.sh set nginx 1.13.4
./lorax_build.sh set all
./lorax_build.sh make_dirs
#
# Build the binaries.
#
./lorax_build.sh install python
./lorax_build.sh install raxml
./lorax_build.sh install hmmer
./lorax_build.sh install redis
./lorax_build.sh install nginx
#
# Do pip installs.
#
./lorax_build.sh link_python
./lorax_build.sh pip
./lorax_build.sh make_link
#
# Test to make sure it runs.
#
echo "Testing lorax installation."
./lorax_build.sh version > `./lorax_build.sh root`/version
echo "Installation was successful."
echo "You should now proceed with configuring lorax."
trap - EXIT
