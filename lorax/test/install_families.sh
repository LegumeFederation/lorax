#!/bin/bash
#
# This script downloads and installs gene familes into lorax.
#
set -o errexit -o nounset -o pipefail
bindir=`dirname $0`

# FIXME: download & process phytozome gene families from upstream
if [ ! -f phytozome_10_2.done ]
then
  # post-processed phytozome_10_2 gene families
  curl -L https://ars-usda.box.com/shared/static/toe0is62567fxk6zpxo0uwdya93tz9nu.gz |
    tar -xzf -
  touch phytozome_10_2.done
fi

if [ ! -f legume.fam3.VLMQ-families.tsv ]
then
  echo "Installing FASTA sequences and HMMs."
  yuckified_data=https://data.legumeinfo.org/LEGUMES/Fabaceae/genefamilies/legume.fam3.VLMQ
  curl $yuckified_data/legume.fam3.VLMQ.baseB_hmm.tar.gz |
    tar -xzf -
  curl $yuckified_data/legume.fam3.VLMQ.sup1B_proteomes.tar.gz |
    tar -xzf -
  find legume.fam3.VLMQ.baseB_hmm -type f -exec mv {} {}.hmm \;
  find legume.fam3.VLMQ.sup1B_proteomes -type f -exec mv {} {}.faa \;
  ${bindir}/load_family.sh legume.fam3.VLMQ.sup1B_proteomes legume.fam3.VLMQ.baseB_hmm legume.fam3.VLMQ
  rm -rf legume.fam3.VLMQ.sup1B_proteomes legume.fam3.VLMQ.baseB_hmm

  # also Newick trees and MSAs
  echo "Installing Newick trees and MSAs."
  curl $yuckified_data/legume.fam3.VLMQ.sup1B_trees.tar.gz |
    tar -xzf -
  curl $yuckified_data/legume.fam3.VLMQ.sup1B_hmmalign_trim2.tar.gz |
    tar -xzf -
  find legume.fam3.VLMQ.sup1B_trees -type f -exec mv {} {}.nwk \;
  find legume.fam3.VLMQ.sup1B_hmmalign_trim2 -type f -exec mv {} {}.faa \;
  ${bindir}/copy_family.sh legume.fam3.VLMQ.sup1B_trees legume.fam3.VLMQ.sup1B_hmmalign_trim2 legume.fam3.VLMQ
  rm -rf legume.fam3.VLMQ.sup1B_trees legume.fam3.VLMQ.sup1B_hmmalign_trim2
  rm -rf legume.fam3.VLMQ
fi

echo "Installation of families done."
