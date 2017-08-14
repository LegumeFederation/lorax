#!/bin/bash
set -e
platform=`uname`
DOC="""Gets the correct build scripts for lorax.

Usage:
       bash top_level_build.sh

Platform:
   `uname` must return one of three values, \"Linux\", \"Darwin\",
   or \"*BSD\"; other values are not recognized.  This platform
   is \"$platform\".
"""
platform=`uname`
if [[ "$platform" == "Linux" ]]; then
   platform=linux
elif [ "$platform" == *"BSD" ]; then
   platform=bsd
elif [ "$platform" == "Darwin" ]; then
   platform=mac
else
   echo "$DOC"
   exit 1
fi
echo "Getting build scripts for ${platform}."
curl -L -o lorax_build.sh https://raw.githubusercontent.com/LegumeFederation/lorax/master/build_scripts/lorax_build.sh
curl -L -o build_example.sh https://raw.githubusercontent.com/LegumeFederation/lorax/master/build_scriptsbuild_example_${platform}.sh
chmod 755 lorax_build.sh build_example.sh
echo "Review (and edit, if necessary) the instructions in build_example.sh."
echo "Then issue the command \"./build_example.sh\" to build lorax."
exit 0
