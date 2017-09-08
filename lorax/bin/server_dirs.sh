#!/usr/bin/env bash
#
# Create directories needed for supervisord operation.  This script only
# works once an instance has been created.
#
set -e # exit on error
#
error_exit() {
  echo "ERROR--unexpected exit from directories script."
}
trap error_exit EXIT
#
myrealpath() {
  if hash realpath 2>/dev/null; then
     realpath "$@"
  else # realpath doesn't exist, fake it
     pushd "$(dirname "$1")" 2&>/dev/null
     islink=$(readlink "$(basename "$1")")
     while [ "$islink" ]; do
       cd "$(dirname "$islink")"
       islink=$(readlink "$(basename "$1")")
     done
     path="${PWD}/$(basename "$1")"
     popd 2&>/dev/null
     echo "$path"
  fi
}
#
# Get the real path to this script.
#
script_path=`myrealpath "${BASH_SOURCE}"`
script_name=`basename "${script_path}"`
bin_dir=`dirname "${script_path}"`
root_dir=`dirname "${bin_dir}"`
conf_dir=${root_dir}/etc/conf.d
#
# Get the names of variables to be defined.
#
pkg="${script_name%_dirs}"
PKG=`echo ${pkg} | tr /a-z/ /A-Z/`
pathlist=("${PKG}_ROOT"
          "${PKG}_VAR"
          "${PKG}_TMP"
          "${PKG}_LOG"
          "${PKG}_DATA"
          "${PKG}_USERDATA")
#
# Source configuration.
#
if [ -e "${conf_dir}/${pkg}" ]; then
        echo "Unable to source ${conf_dir}/${pkg}."
        trap - EXIT
        exit 1
fi
source "${conf_dir}/${pkg}"
#
# Create directories.
#
for path in "${pathlist[@]}" ; do
   if [ -z "${!path}" ]; then
       echo "ERROR--Path $path not defined."
       trap - EXIT
       exit 1
   elif [ ! -d "${!path}" ]; then
       echo "Creating directory ${!path}."
       mkdir -p "${!path}"
   else
       echo "Directory ${!path} exists."
   fi
done
