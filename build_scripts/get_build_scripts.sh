#!/usr/bin/env bash
platform=`uname`
DOC="""Gets build/configuration scripts for lorax.

Usage:
       bash get_build_scripts.sh [-n]

Options:
       -n Do not check for self-updates.

Platform:
   uname must return one of three values, \"Linux\", \"Darwin\",
   or \"*BSD\"; other values are not recognized.  This platform
   is \"$platform\".
"""
rawsite="https://raw.githubusercontent.com/LegumeFederation/lorax/master/build_scripts"
error_exit() {
   echo "ERROR--unexpected exit from ${BASH_SOURCE} script at line:"
   echo "   $BASH_COMMAND"
}
trap error_exit EXIT
set -e
if [ "$1" == "-n" ]; then
   echo "Not checking for self-updates."
else
   printf "Checking for self-update..."
   curl -L -s -o get_build_scripts.sh.new ${rawsite}/get_build_scripts.sh
   chmod 755 get_build_scripts.sh.new
   if cmp -s get_build_scripts.sh get_build_scripts.sh.new ; then
      rm get_build_scripts.sh.new
      echo "not needed."
   else
      echo "this file was updated.  Please rerun-it."
      mv get_build_scripts.sh.new get_build_scripts.sh
      trap - EXIT
      exit 0
   fi
fi
#
# Now check for updates to other files, in an edit-aware way.
#
updates=0
platform=`uname`
if [[ "$platform" == "Linux" ]]; then
   platform=linux
elif [[ "$platform" == *"BSD" ]]; then
   platform=bsd
elif [[ "$platform" == "Darwin" ]]; then
   platform=mac
else
   echo "$DOC"
   trap - EXIT
   exit 1
fi
curl -L -s -o lorax_build.sh.new ${rawsite}/lorax_build.sh
curl -L -s -o build_example.sh.new ${rawsite}/build_example_${platform}.sh
curl -L -s -o config_example.sh.new ${rawsite}/config_example.sh
curl -L -s -o run_lorax_tests.sh.new ${rawsite}/run_lorax_tests.sh
for f in lorax_build.sh build_example.sh config_example.sh run_lorax_tests.sh ; do
   if [ -e ${f} ]; then
      if cmp -s ${f} ${f}.new; then
         rm ${f}.new # no change
      else
        updates=1
        echo "$f has been updated."
        mv ${f} ${f}.old
        chmod 755 ${f}.new
        mv ${f}.new ${f}
      fi
   else
      updates=1
      chmod 755 ${f}.new
      mv ${f}.new ${f}
   fi
done
#
# If my_ files have changed versus example, warn but don't replace.
#
for f in build_example.sh config_example.sh ; do
  my_f="my_${f/_example/}"
  if [ -e ${f}.old ]; then
     cmp_f="${f}.old" # look for changes against old file
  else
     cmp_f="$f"       # look for changes against current file
  fi
  if [ -e ${my_f} ]; then
    if cmp -s ${cmp_f} ${my_f}; then
       if [ -e ${f}.old ]; then
         # No changes from old example, copy current file to my_f.
         cp ${f} ${my_f}
       fi
    else
       if [ -e ${f}.old ]; then
         mv ${f}.old ${f}.save
         echo "Example file on which your edited ${my_f} was based has changed."
         echo "Review the following differences between ${f} and ${f}.save"
         echo "and apply them, if necessary to ${my_f}:"
         diff -u ${f}.save ${f}
       else
         echo "${my_f} differs from the (unchanged) example file."
       fi
    fi
  else
    cp ${f} ${my_f}
  fi
done
rm -f lorax_build.sh.old build_example.sh.old config_example.sh.old
set +e
pypi=`./lorax_build.sh pypi`
version=`./lorax_build.sh version`
if [ "$?" -eq 0 ]; then
   if [ "$pypi" == "$version" ]; then
      echo "The latest version of lorax (${pypi}) is installed, no need for updates."
   else
      echo "You can update from installed version (${version})to latest (${pypi}) with"
      echo "   ./lorax_build.sh pip"
   fi
else
   echo "${version}, but latest version is ${pypi}."
fi
if [ "$updates" -eq 0 ]; then
   echo "No updated build/config files found for $platform platform."
else
   echo "Review/edit the commands in my_build.sh and my_config.sh."
   echo "Then run them to build and configure lorax."
   echo "If you do make changes to these files, we recommend that you keep"
   echo "this directory to simplify updates."
fi
trap - EXIT
exit 0
