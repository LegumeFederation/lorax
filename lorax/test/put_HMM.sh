#!/bin/bash
# PUT an HMM into an existing family.
DOC="
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
if [  -z "$LORAX_PORT" ] ; then
	LORAX_PORT=58927
fi
if [ ! -f "$1" ] ; then
	echo "Must specify a readable HMM file."
	exit 1
fi
#
# Parse arguments.
#
if [ "$#" -lt 2 ]; then
	echo "$DOC"
	exit 1
fi
if [ ! -f "$1" ] ; then
	echo "HMM must specify a readable HMM definition file."
	echo "$DOC"
	exit 1
fi
if [ -z "$2" ] ; then
	echo "Must specify a FAMILY name."
	echo "$DOC"
	exit 1
fi
if [ -z "${3}" ] ; then
   code="200"
else
   code="${3}"
fi
#
# Issue the PUT.
#
full_target="/trees/${2}/HMM"
tmpfile=$(mktemp /tmp/put_HMM.XXX)
status=$(curl -s -o ${tmpfile} -w '%{http_code}' -T "${1}" ${LORAX_HOST}:${LORAX_PORT}${full_target})
if [ "${status}" -eq "${code}" ]; then
   if [ $_V -eq 1 ]; then
     echo "PUT of ${1} to ${full_target} returned HTTP code ${status} as expected."
      echo "Response is:"
      cat ${tmpfile}
      echo ""
   fi
   rm "$tmpfile"
   exit 0
else
   echo "FATAL ERROR--PUT of ${1} to ${full_target} returned HTTP code ${status}, expected ${code}."
   echo "Full response is:"
   cat ${tmpfile}
   echo ""
   rm "$tmpfile"
   exit 1
fi
