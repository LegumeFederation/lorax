#!/bin/bash
#
# Get environmental variables.
#
source ~/.lorax/lorax_rc
let count=0 || true
#
DOC="""Create a set of protein family definitions from unaligned peptide
FASTA files and HMM's.  The HMM's may be in different directories,
but the file stems must match.

Usage:
	./load_family.sh [-v]|[-q] fastapath hmmpath familyname

Flags:
	-v  verbose, output family name for each file created
	-q  quiet, do not display progress bar

Example:
	./load_family.sh -v phytozome_10_2/fasta/ phytozome_10_2/hmm/ phytozome_10_2
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
function PostPut {
    while read seqfile; do
        let count=${count}+1
        seqname=${seqfile##*/}
        fam=${seqname%%.*}
        nseqs=$(grep \> ${seqfile} | wc -l)
        nchars=$(grep -v \> ${seqfile} | wc -c)
        avg_len=$(echo "$nchars $nseqs" | awk '{print int($1/$2+0.5)}')
        if [ "$_V" -ne 0 ]; then
            echo "Loading family ${fam} with ${nseqs} sequences of length ${avg_len}."
        elif [ "$_Q" -eq 0 ]; then
            ProgressBar ${count} ${nfiles}
        fi
        ./post_FASTA.sh peptide ${seqfile} ${fam} sequences
        if [ $? -ne 0 ]; then
            >&2 echo "POST of FASTA failed on ${fam}."
 		    exit 1
        fi
 	    ./put_HMM.sh ${hmmpath}/${fam}.hmm ${fam}
 	    if [ $? -ne 0 ]; then
 		    >&2 echo "PUT of HMM failed on ${fam}."
 		    exit 1
 	    fi
        echo -e "${fam}\t${nseqs}\t${avg_len}">>families.raw
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
fastapath=$1
hmmpath=$2
familyname=$3
#
# Loop over FASTA files, POST FASTA and PUT HMM.
#
nfiles=$(find ${fastapath} -type f | wc -l)
echo -e "#family\tseqs\tavg_len" >${familyname}-families.tsv
#
# Post sequences and put HMM's to server.
#
find ${fastapath} -name \*.faa |  PostPut
if [ $? -ne 0 ]; then
    exit 1
fi
if [ "$_Q" -eq 0 ]; then
  echo "" # newline after progress bar
fi
#
# Sort, histogram, and print stats on families.
#
echo "${nfiles} $familyname families created."
sort -rgk2 families.raw >> ${familyname}-families.tsv
echo "List of $familyname families can be found in ${familyname}-families.tsv"
rm -f families.raw ${familyname}-histogram.tsv
echo "Histogram of $familyname family sizes can be found in ${familyname}-histogram.tsv"
echo -e "#size\tfamilies" >${familyname}-histogram.tsv
grep -v \# ${familyname}-families.tsv | \
  awk '{n[$2]++} END {for (i in n) print i,"\t",n[i]}' | \
  sort -n >>${familyname}-histogram.tsv
IFS=',' read -r -a bigfam <<< $(grep -v \# ${familyname}-families.tsv | head -1| tr "\\t" ",")
echo "Largest $familyname family is ${bigfam[0]} with ${bigfam[1]} members of average length ${bigfam[2]}."
IFS=',' read -r -a modal <<< $(grep -v \# ${familyname}-histogram.tsv | sort -rgk 2 | head -1 | tr "\\t" ",")
echo "Modal size of $familyname families is ${modal[0]} sequences, with ${modal[1]} examples."
