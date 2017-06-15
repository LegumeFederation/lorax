#!/bin/bash
# POST a FASTA file as sequence or alignment.
DOC="
Usage:
      post_FASTA.sh  [-v] TYPE FASTA FAMILY TARGET [CODE]
             where
                       -v will cause the returns to be printed.
                       TYPE is either \"peptide\" or \"DNA\".
                       FASTA is the FASTA alignment file.
                       FAMILY is the name to be used for this family.
                       TARGET must be either \"sequences\" or \"alignment\".
                       CODE is the expected HTTP code for this request
                            (200 if not specified).

Example:
         ./post_FASTA.sh -v peptide aspartic_peptidases.faa aspartic_peptidases sequences 200

Options:
      -v   verbose mode, shows all returns.

 Before running this script, lorax should be started.
 If the lorax server is running at an address other than the
 default, the environmental variables LORAX_HOST
 and LORAX_PORT must be defined.
"
#
# Parse option (verbose flag)
#
_V=0 
while getopts "v" OPTION
do
   case ${OPTION} in
     v) _V=1
	shift
        ;;
   esac
done
#
# Get environmental variables.
#
if [ -z "$LORAX_HOST" ] ; then
	LORAX_HOST=localhost
fi
if [ -z "$LORAX_PORT" ] ; then
	LORAX_PORT=58927
fi
#
# Parse arguments
#
if [ "$#" -lt 4 ]; then
	echo "$DOC"
	exit 1
fi
if [ "$1" == "peptide" ] ; then
	type="peptide"
elif [ "$1" == "DNA" ]; then
	type="DNA"
else
	echo "TYPE must be either \"peptide\" or \"DNA\"."
	echo "$DOC"
	exit 1
fi
if [ ! -f "$2" ] ; then
	echo "FASTA must specify a readable sequence file."
	echo "$DOC"
	exit 1
fi
if [ -z "$3" ] ; then
	echo "Must give a FAMILY name."
	echo "$DOC"
	exit 1
fi
if [ "$4" == "sequences" ]; then
	target="sequences"
elif [ "$4" == "alignment" ]; then
	target="alignment"
else
	echo "TARGET must be either \"sequences\" or \"alignment\"."
	echo "$DOC"
	exit 1
fi
if [ -z "${5}" ] ; then
   code="200"
else
   code="${5}"
fi
#
# Issue the POST.
#
full_target="/trees/${3}/${target}"
tmpfile=$(mktemp /tmp/post_FASTA.XXX)
status=$(curl -s -o ${tmpfile} -w '%{http_code}' -F "${type}=@${2}" ${LORAX_HOST}:${LORAX_PORT}${full_target})
if [ "${status}" -eq "${code}" ]; then
   if [ "$_V" -eq 1 ]; then
      echo "POST of ${2} to ${full_target} returned HTTP code ${status} as expected."
      echo "Response is:"
      cat ${tmpfile}
      echo ""
   fi
   rm "$tmpfile"
   exit 0
else
   echo "FATAL ERROR--POST of ${2} to ${full_target} returned HTTP code ${status}, expected ${code}."
   echo "Full response is:"
   cat ${tmpfile}
   echo ""
   rm "$tmpfile"
   exit 1
fi
