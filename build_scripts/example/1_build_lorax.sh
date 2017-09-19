#!/usr/bin/env bash
#
# starting from clean empty directory
#
set -e
if [ -z "$LORAX_BUILD_DIR" ]; then
   echo "You must source the defs script first."
   exit 1
fi
mkdir -p $LORAX_BUILD_DIR
cd $LORAX_BUILD_DIR
curl -L -o lorax_tool https://raw.githubusercontent.com/LegumeFederation/lorax/master/build_scripts/lorax_tool.sh
chmod 755 lorax_tool
ln -s ${LRX_SCRIPT_DIR}/my_build.sh .
ln -s ${LRX_SCRIPT_DIR}/${LRX_STAGE}_config.sh ./my_config.sh
./lorax_tool build -y
./lorax_tool configure_pkg -y
./lorax_tool testify -y
echo "If you see this line, you can be quite sure that lorax is properly installed as ${LRX_INSTALLER}."
