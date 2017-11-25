#!/bin/bash
set -e
if [ -z "$LRX_VAR" ]; then
   echo "You must source the defs script first."
   exit 1
fi
echo "Removing directories owned by ${LRX_USER}."
$LRX_SUDO -u $LRX_USER rm -r  $LRX_TMP $LRX_VAR ${LRX_LOG}/* 
echo "Removing lorax root directory."
rm -rf ${LRX_ROOT}/*
