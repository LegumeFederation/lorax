#!/bin/bash
#
# Get environmental variables.
#
source ~/.lorax/lorax_rc
set -e
error_exit() {
   >&2 echo "ERROR--unexpected exit from ${BASH_SOURCE} script at line:"
   >&2 echo "   $BASH_COMMAND"
}
trap error_exit EXIT
#
DOC="""Create a set of protein family definitions from unaligned peptide
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
nfiles=`find ${fastapath} -type f | wc -l`
let count=0 || true
rm -f families.raw
echo -e "#family_name\tseqs\tavg_len" >families.tsv
for seqfile in `find ${fastapath}/* -type f` ; do
        let count=${count}+1
        seqname=${seqfile##*/}
	fam=${seqname%%.*}
	nseqs=`grep \> ${seqfile} | wc -l`
	nchars=`grep -v \> ${seqfile} | wc -c`
	avg_len=`echo "$nchars $nseqs" | awk '{print int($1/$2+0.5)'`
	if [ "$_V" -ne 0 ]; then
		echo "Creating family ${fam} with ${nseqs} sequences of length ${avg_len}."
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
	echo -e "${fam}\t${nseqs}\t${avg_len}">>families.raw
done
if [ "$_Q" -ne 0 ]; then
  echo "" # newline after progress barq
fi
#
# Sort, histogram, and print stats on families.
#
echo "${nfilmes} families created."
sort -rgk2 families.raw >> families.tsv
echo "Size-ordered (large to small) list of families can be found in families.tsv"
rm -f families.raw families_histogram.tsv
echo "Histogram of family sizes can be found in families_histogram.tsv"
echo -e "#size\tfamilies" >families_histogram.tsv
grep -v \# families.tsv | awk '{n[$2]++} END {for (i in n) print i,"\t",n[i]}' | sort -n >>families_histogram.tsv
IFS=',' read -r -a bigfam <<< `grep -v \# families.tsv | head -1| tr "\\t" ","`
echo "Largest familiy is ${bigfam[0]} with ${bigfam[1]} members of average length ${bigfam[2]}."
IFS=',' read -r -a modal <<< `grep -v \# families_histogram.tsv | sort -rgk 2 | head -1 | tr "\\t" ","`
echo "Modal size of families is ${modal[0]} sequences, with ${modal[1]} examples."
