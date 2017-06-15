#!/bin/bash
echo "This script will download a 900 MB file of gene families, and"
echo "unpack it into a 7 GB directory."
read -r -p "Are you sure? [y/N] " response
case "$response" in
    [yY][eE][sS]|[yY]) 
	echo "Downloading family definitions"
        curl -o legume_gene_families.tgz http://data.comparative-legumes.org/gene_families/phytozome_10_2/legume_gene_families_phytozome_10_2.tar.gz
	tar xzf legume_gene_families.tgz
	rm legume_gene_families.tgz
	echo "Creating gene families"
	./create_families.sh  legume_gene_families_phytozome_10_2/fasta/ \
		legume_gene_families_phytozome_10_2/hmm/
	echo "Removing input files"
	rm -r legume_gene_families_phytozome_10_2/
        ;;
    *)
        exit 1
        ;;
esac
