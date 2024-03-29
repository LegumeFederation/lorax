#!/usr/bin/env bash
# PUT an HMM into an existing family.
HMM_DOC="
Usage:
       put_HMM.sh  [-v] HMM FAMILY [CODE]
             where
	           -v     will cause the returns to be printed.
                   HMM    is a hmmer v3 HMM definition file.
		   FAMILY is the family name (already created).
		   CODE   is the expected HTTP code for this request
		          (200 if not specified).
Example:
       ./put_HMM.sh 59026816.hmm aspartic_peptidases
"
#
# Parse option (verbose flag)
#
set -e
export ARGS="$@"
error_exit() {
   >&2 echo ""
   >&2 echo "ERROR--unexpected exit from ${BASH_SOURCE} script at line:"
   >&2 echo "   $BASH_COMMAND"
   >&2 echo "   with arguments \"${ARGS}\"."
}
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
if [ ! -f "$1" ] ; then
	>&2 echo "Must specify a readable HMM file."
	exit 1
fi
#
# Parse arguments.
#
if [ "$#" -lt 2 ]; then
	>&2 echo "$HMM_DOC"
	exit 1
fi
if [ ! -f "$1" ] ; then
	>&2 echo "HMM must specify a readable HMM definition file."
	>&2 echo "$HMM_DOC"
	exit 1
fi
if [ -z "$2" ] ; then
	>&2 echo "Must specify a FAMILY name."
	>&2 echo "$HMM_DOC"
	exit 1
fi
if [ -z "${3}" ] ; then
   code="200"
else
   code="${3}"
fi
trap error_exit EXIT
#
# Issue the PUT.
#
full_target="/trees/${2}/HMM"
tmpfile=$(mktemp /tmp/put_HMM.XXX)
status=$(curl ${LORAX_CURL_ARGS}  -s -o ${tmpfile} -w '%{http_code}' -T "${1}" ${LORAX_CURL_URL}${full_target})
if [ "${status}" -eq "${code}" ]; then
   if [ $_V -eq 1 ]; then
     echo "PUT of ${1} to ${full_target} returned HTTP code ${status} as expected."
      echo "Response is:"
      cat ${tmpfile}
      echo ""
   fi
   rm "$tmpfile"
else
   >&2 echo "ERROR--PUT of ${1} to ${full_target} returned HTTP code ${status}, expected ${code}."
   >&2 echo "Full response is:"
   >&2 cat ${tmpfile}
   >&2 echo ""
   rm "$tmpfile"
   trap - EXIT
   exit 1
fi
trap - EXIT
