#!/bin/bash
# Create a set of gene familes using peptide FASTAs and HMMs.
DOC="
Create a set of protein family definitions from unaligned peptide 
FASTA files and HMM's.  The HMM's may be in different directories,
but the file stems must match.

Usage:
	./create_families.sh [-v]|[-q] fastapath hmmpath

Flags:
	-v  verbose, output family name for each file created
	-q  quiet, do not display progress bar

Example:
	./create_families.sh -v legume_gene_families_phytozome_10_2/fasta/ \
		legume_gene_families_phytozome_10_2/hmm/
"
#
function ProgressBar {
    let _progress=(${1}*100/${2}*100)/100
    let _done=(${_progress}*4)/10
    let _left=40-$_done
    _fill=$(printf "%${_done}s")
    _empty=$(printf "%${_left}s")
printf "\rProgress (${2} families): [${_fill// /#}${_empty// /-}] ${_progress}%%"
}
#
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
if [ "$#" -lt 2   ]; then
	echo "$DOC"
	exit 1
fi
fastapath=$1
hmmpath=$2
#
# Loop over FASTA files, POST FASTA and PUT HMM.
#
nfiles=`ls ${fastapath} | wc -l`
let count=0
for seqfile in ${fastapath}/* ; do
        let count=${count}+1
        seqname=${seqfile##*/}
	fam=${seqname%%.*}
	if [ "$_V" -ne 0 ]; then
		echo "creating family $fam"
	elif [ "$_Q" -eq 0 ]; then
		ProgressBar ${count} ${nfiles}
	fi
	./post_FASTA.sh peptide ${seqfile} ${fam} sequences
	if [ "$?" -eq 1 ] ; then
		echo "POST of FASTA failed on ${fam}"
		exit 1
	fi
	./put_HMM.sh ${hmmpath}/${fam}.hmm ${fam} 
	if [ "$?" -eq 1 ] ; then
		echo "PUT of HMM failed on ${fam}"
		exit 1
	fi
done
