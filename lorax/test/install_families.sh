#!/bin/bash
#
# This script downloads and installs gene familes into lorax.
#
phytozome="phytozome_10_2"
legfed="legfed_v1_1"
set -e
install_family() {
	echo "Downloading $1 families"
        curl -o ${1}.tar.gz http://data.comparative-legumes.org/gene_families/${1}.tar.gz
	echo "Unpacking $1 families"
	tar xzf ${1}.tar.gz
	echo "Creating $1 gene families"
	./load_family.sh  ${1}/fasta/ ${1}/hmm/ $1
	rm -rf ${1}/ ${1}.tar.gz
}
if [ "$1" != "-y" ]; then
   read -r -p "Download/install $phytozome gene families (900 MB)? [y/N] " phytozome_response
   read -r -p "Download/install $legfed  gene families (700 MB)? [y/N] " legfed_response
else
  phytozome_reponse="y"
  legfed_response="y"
fi
case "$phytozome_response" in
    [yY][eE][sS]|[yY]) 
        install_family $phytozome
        echo ""
        ;;
    *)
        echo "Skipping $phytozome install."
        ;;
esac
case "$legfed_response" in
    [yY][eE][sS]|[yY])  
        install_family $legfed
        ;;
    *)
        echo "Skipping $legfed install."
        ;;
esac
echo "Installation of families done."
