#!/usr/bin/env bash
# POST a FASTA file as sequence or alignment.
FASTA_DOC="
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

 Before running this script, lorax should be started, and the
 environmental variables LORAX_CURL_ARGS and LORAX_CURL_URL
 must be defined.
"
set -e
ARGS="$@"
error_exit() {
   >&2 echo ""
   >&2 echo "\nERROR--unexpected exit from ${BASH_SOURCE} script at line:"
   >&2 echo "   $BASH_COMMAND"
   >&2 echo "   with arguments \"${ARGS}\"."
}
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
# Parse arguments
#
if [ "$#" -lt 4 ]; then
	>&2 echo "$FASTA_DOC"
	exit 1
fi
if [ "$1" == "peptide" ] ; then
	type="peptide"
elif [ "$1" == "DNA" ]; then
	type="DNA"
else
	>&2 echo "TYPE must be either \"peptide\" or \"DNA\"."
	>&2 echo "$FASTA_DOC"
	exit 1
fi
if [ ! -f "$2" ] ; then
	>&2 echo "FASTA must specify a readable sequence file."
	>&2 echo "$FASTA_DOC"
	exit 1
fi
if [ -z "$3" ] ; then
	>&2 echo "Must give a FAMILY name."
	>&2 echo "$FASTA_DOC"
	exit 1
fi
if [ "$4" == "sequences" ]; then
	target="sequences"
elif [ "$4" == "alignment" ]; then
	target="alignment"
else
	>&2 echo "TARGET must be either \"sequences\" or \"alignment\"."
	>&2 echo "$FASTA_DOC"
	exit 1
fi
if [ -z "${5}" ] ; then
   code="200"
else
   code="${5}"
fi
trap error_exit EXIT
#
# Issue the POST.
#
full_target="/trees/${3}/${target}"
tmpfile=$(mktemp /tmp/post_FASTA.XXX)
status=$(curl ${LORAX_CURL_ARGS} -s -o ${tmpfile} -w '%{http_code}' \
         -F "${type}=@${2}" \
         ${LORAX_CURL_URL}${full_target})
if [ "${status}" -eq "${code}" ]; then
   if [ "$_V" -eq 1 ]; then
      echo "POST of ${2} to ${full_target} returned HTTP code ${status} as expected."
      echo "Response is:"
      cat ${tmpfile}
      echo ""
   fi
   rm "$tmpfile"
else
   >&2 echo "ERROR--POST of ${2} to ${full_target} returned HTTP code ${status}, expected ${code}."
   >&2 echo "Full response is:"
   >&2 cat ${tmpfile}
   >&2 echo ""
   rm "$tmpfile"
   trap - EXIT
   exit 1
fi
trap - EXIT
