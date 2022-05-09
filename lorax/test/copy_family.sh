#!/bin/bash
bindir=`dirname $0`
#
# Get environmental variables.
#
let count=0 || true
#
DOC="""Copy Newick trees and MSAs for each gene family.

Usage:
	./copy_family.sh [-v]|[-q] treepath msapath familyname

Flags:
	-v  verbose, output family name for each file created
	-q  quiet, do not display progress bar

Example:
	./copy_family.sh -v phytozome_10_2/trees/ phytozome_10_2/hmmalign/ phytozome_10_2
"""
#
function ProgressBar {
    let _progress=(${1}*100/${2}*100)/100 || true
    let _done=(${_progress}*4)/10 || true
    let _left=40-$_done
    _fill=$(printf "%${_done}s")
    _empty=$(printf "%${_left}s")
printf "\rProgress (${2} families): [${_fill// /#}${_empty// /-}] ${_progress}%%"
}
#
function CopyFiles {
    while read treefile; do
        let count=${count}+1
        famname=${treefile##*/}
        fam0=${famname%%.nwk}
        fam=${fam0##legfed_v1_0.}
        if [ "$_V" -ne 0 ]; then
	    echo "Loading family ${fam} (tree and MSA)."
        elif [ "$_Q" -eq 0 ]; then
            ProgressBar ${count} ${nfiles}
        fi

        # Newick trees
        famtreedir=${fam}/FastTree
        mkdir ${famtreedir}
        cp ${treepath}/${fam0}.nwk ${famtreedir}/tree.nwk
        # MSAs
        cp ${msapath}/${fam0}.faa ${fam}/alignment.faa
    done
}
#
# Parse arguments.
#
_V=0
_Q=0
if [ "$1" == "-v" ]; then
	_V=1
	shift 1
elif [ "$1" == "-q" ]; then
	_Q=1
	shift 1
fi
if [ "$#" -lt 3   ]; then
	>&2 echo "$DOC"
	exit 1
fi
treepath=$1
msapath=$2
familyname=$3
#
# Loop over (copying the) Newick tree and MSA files.
#
nfiles=$(find ${treepath} -type f | wc -l)
find ${treepath} -name \*.nwk | CopyFiles
if [ $? -ne 0 ]; then
    exit 1
fi
if [ "$_Q" -eq 0 ]; then
  echo "" # newline after progress bar
fi
#
# Print stats on families.
#
echo "${nfiles} $familyname families modified."
