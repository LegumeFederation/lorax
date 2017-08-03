#!/bin/bash
#
#  This script builds lorax and its binary dependencies.
#  The example here is for a build on OpenBSD.
#
set -e
error_exit() {
  echo "The top-level build script encountered an error."
}
trap error_exit EXIT
#
# Configure the build.
#
./lorax_build.sh set top_dir /usr/local/www
./lorax_build.sh set bin_dir ~/bin
./lorax_build.sh set directory_version 0.94
./lorax_build.sh set python 3.6.2
./lorax_build.sh set cc clang
./lorax_build.sh set hmmer 3.1b2
./lorax_build.sh set raxml 8.2.11
./lorax_build.sh set raxml_model .SSE3.PTHREADS.gcc
./lorax_build.sh set raxml_binsuffix -PTHREADS-SSE3
./lorax_build.sh set redis 4.0.1
./lorax_build.sh set redis_cflags -DAF_LOCAL=1
./lorax_build.sh set all
./lorax_build.sh make_dirs
#
# Build the binaries.
#
./lorax_build.sh install python
./lorax_build.sh install raxml
./lorax_build.sh install hmmer
./lorax_build.sh install redis
#
# Do pip installs.
#
./lorax_build.sh link_python
export PATH="`./lorax_build.sh root`/bin:${PATH}"
export LC_ALL=en_US.UTF-8
export LANG=en_US.UTF-8
pip install -U setuptools
pip install -e git+https://github.com/LegumeFederation/supervisor.git@4.0.0#egg=supervisor==4.0.0
pip install lorax
./lorax_build.sh make_link
#
# Test to make sure it runs.
#
echo "Testing that lorax runs".
`./lorax_build.sh root`/bin/lorax_env lorax
echo "Installation was successful."
echo "You should now proceed with configuring lorax."
trap - EXIT
