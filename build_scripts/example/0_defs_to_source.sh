#!/usr/bin/env bash
DOC="""Set up the proper environmental variables.

Usage:
   source ${BASH_SOURCE}
"""
#
# Check to see that this script was sourced, not run.
#
if [[ $_ == $0 ]]; then # this file was run, not sourced
  echo "$DOC"
  exit 1
fi
#
# Check for required files and define envvars based on them.
#
txtfilelist=("secret_key"
             "sentry_dsn"
             "crashmail_email")
for txtfile in "${txtfilelist[@]}" ; do
   if [ ! -e ${txtfile}.txt ]; then
      echo "ERROR--must create ${txtfile}.txt file in this directory."
      exit 1
   else
      varstring="$(echo $txtfile | tr /a-z/ /A-Z/)"
      export LRX_${varstring}="$(cat ${txtfile}.txt)"
   fi
done
#
# Exports: edit this to suit yourself.
#
#        LRX-* : Local to the build scripts only.
#      LORAX-* : Used in lorax_tool
#
export LRX_VERSION="0.94"
export LRX_ROOT="/usr/local/www/lorax-${LRX_VERSION}"
export LRX_DEV_HOSTNAME="legfed-dev.usda.iastate.edu"
export LRX_DEV_IP="10.24.27.202"
export LRX_STAGE_HOSTNAME="legfed-stage.usda.iastate.edu"
export LRX_STAGE_IP="10.24.27.228"
export LRX_PROD_HOSTNAME="legfed.usda.iastate.edu"
export LRX_PROD_IP="129.186.136.163"
export LRX_INSTALLER=$USER
export LRX_USER="www"
export LRX_GROUP="www"
export LRX_SCRIPT_DIR=$PWD
export LRX_VAR=/var/lorax/${LRX_VERSION}
export LRX_TMP=/tmp/lorax
export LRX_LOG=/var/log/lorax
export LORAX_BUILD_DIR="${LRX_ROOT}/build"
export LORAX_TEST_DIR="${LRX_ROOT}/test"
#
# The following assumes that the user has full sudo
# privs on dev, but only sudo -u $LRX_USER on stage.
#
hostname=$(hostname)
if [ "$hostname" == "$LRX_DEV_HOSTNAME" ]; then
  export LRX_STAGE="dev"
  export LRX_SUDO="sudo sudo"
elif [ "$hostname" == "$LRX_STAGE_HOSTNAME" ]; then
  export LRX_STAGE="stage"
  export LRX_SUDO="sudo"
elif [ "$hostname" == "$LRX_PROD_HOSTNAME" ]; then
  export LRX_STAGE="prod"
  export LRX_SUDO="sudo"
else
  echo "ERROR-unknown host $(hostname)"
  exit 1
fi

#
# Set up the links to config files.
#
if [ "$USER" == "$LRX_INSTALLER" ]; then
  rm -f ~/.lorax
  ln -s ~/.lorax-$LRX_STAGE ~/.lorax
else
  echo "Warning--you are not ${LRX_INSTALLER}, links to ~${LRX_INSTALLER}i/.lorax will be preserved."
fi
#
# Define convenient aliases.
#
alias cd_lorax="cd $LRX_ROOT"
