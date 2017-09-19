#!/bin/bash
set -e
f [ -z "$LORAX_VAR" ]; then
   echo "You must source the defs script first."
   exit 1
fi
$LRX_SUDO -u $LRX_USER rm -r  $LRX_TMP $LRX_VAR ${LRX_LOG}/* 
