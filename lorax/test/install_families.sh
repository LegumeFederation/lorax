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
  curl https://legumeinfo.org/data/v2/LEGUMES/Fabaceae/genefamilies/legume.genefam.fam1.M65K/legume.genefam.fam1.M65K.hmm.tar.gz |
    tar -xzf -
  curl https://legumeinfo.org/data/v2/LEGUMES/Fabaceae/genefamilies/legume.genefam.fam1.M65K/legume.genefam.fam1.M65K.family_fasta.tar.gz |
    tar -xzf -
  find legume.genefam.fam1.M65K.hmm -type f -exec mv {} {}.hmm \;
  find legume.genefam.fam1.M65K.family_fasta -type f -exec mv {} {}.faa \;
  ${bindir}/load_family.sh legume.genefam.fam1.M65K.family_fasta legume.genefam.fam1.M65K.hmm legume.genefam.fam1.M65K
  rm -rf legume.genefam.fam1.M65K.family_fasta legume.genefam.fam1.M65K.hmm legume.genefam.fam1.M65K
fi

echo "Installation of families done."
