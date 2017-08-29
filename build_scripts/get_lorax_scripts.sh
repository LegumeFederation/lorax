#!/usr/bin/env bash
pkg="lorax"
platform=`uname`
DOC="""Gets build/configuration scripts for ${pkg}.

Usage:
       bash get_${pkg}_scripts.sh [-n]

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
   curl -L -s -o get_${pkg}_scripts.sh.new ${rawsite}/get_${pkg}scripts.sh
   chmod 755 get_${pkg}scripts.sh.new_
   if cmp -s get_${pkg}_scripts.sh get_${pkg}_scripts.sh.new ; then
      rm get_${pkg}_scripts.sh.new
      echo "not needed."
   else
      echo "this file was updated.  Please rerun-it."
      mv get_${pkg}_scripts.sh.new get_${pkg}_scripts.sh
      trap - EXIT
      exit 0
   fi
fi
#
# Now check for updates to other files, in an edit-aware way.
#
updates=0
curl -L -s -o ${pkg}_build.sh.new ${rawsite}/${pkg}_build.sh
curl -L -s -o build_example.sh.new ${rawsite}/build_example.sh
curl -L -s -o config_example.sh.new ${rawsite}/config_example.sh
curl -L -s -o run_${pkg}_tests.sh.new ${rawsite}/run_${pkg}_tests.sh
for f in ${pkg}_build.sh build_example.sh config_example.sh run_${pkg}_tests.sh ; do
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
         set +e
         diff -u ${f}.save ${f}
       else
         echo "${my_f} differs from the (unchanged) example file."
       fi
    fi
  else
    cp ${f} ${my_f}
  fi
done
rm -f ${pkg}_build.sh.old build_example.sh.old config_example.sh.old run_${pkg}_tests.sh.old
pypi=`./${pkg}_build.sh pypi`
version=`./${pkg}_build.sh version`
if [ "version" == "${pkg} build not configured" ]; then
   echo "Next run \"./my_build.sh\" to build and configure lorax."
elif [ "$updates" -eq 1 ]; then
   echo "Update build/configuration files found, please re-build using"
   echo "    ./my_build.sh"
elif [ "$pypi" == "$version" ]; then
      echo "The latest version of ${pkg} (${pypi}) is installed, no need for updates."
else
      echo "You can update from installed version (${version}) to latest (${pypi}) with"
      echo "   ./${pkg}_build.sh pip"
fi
trap - EXIT
exit 0
