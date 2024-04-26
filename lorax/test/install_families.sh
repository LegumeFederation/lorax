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

if [ ! -f legume.genefam.fam1.M65K-families.tsv ]
then
  echo "Installing FASTA sequences and HMMs."
  yuckified_data=https://data.legumeinfo.org/LEGUMES/Fabaceae/genefamilies/legume.fam1.M65K
  curl $yuckified_data/legume.fam1.M65K.hmm.tar.gz |
    tar -xzf -
  curl $yuckified_data/legume.fam1.M65K.family_fasta.tar.gz |
    tar -xzf -
  find legume.genefam.fam1.M65K.hmm -type f -exec mv {} {}.hmm \;
  find legume.genefam.fam1.M65K.family_fasta -type f -exec mv {} {}.faa \;
  ${bindir}/load_family.sh legume.genefam.fam1.M65K.family_fasta legume.genefam.fam1.M65K.hmm legume.genefam.fam1.M65K
  rm -rf legume.genefam.fam1.M65K.family_fasta legume.genefam.fam1.M65K.hmm

  # also Newick trees and MSAs
  echo "Installing Newick trees and MSAs."
  curl $yuckified_data/legume.fam1.M65K.trees_ML_rooted.tar.gz |
    tar -xzf -
  curl $yuckified_data/legume.fam1.M65K.hmmalign_trim.tar.gz |
    tar -xzf -
  find legume.genefam.fam1.M65K.trees_ML_rooted -type f -exec mv {} {}.nwk \;
  find legume.genefam.fam1.M65K.hmmalign_trim -type f -exec mv {} {}.faa \;
  ${bindir}/copy_family.sh legume.genefam.fam1.M65K.trees_ML_rooted legume.genefam.fam1.M65K.hmmalign_trim legume.genefam.fam1.M65K
  rm -rf legume.genefam.fam1.M65K.trees_ML_rooted legume.genefam.fam1.M65K.hmmalign_trim
  rm -rf legume.genefam.fam1.M65K
fi

echo "Installation of families done."
