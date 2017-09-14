#!/usr/bin/env bash
DOC="""Test all lorax targets.

Usage:
       lorax_test.sh [-v]

Options:
       -v  verbose mode, shows all returns.

Before running this script, lorax should be configured and started.
"""
set -e # exit on errors
error_exit() {
   echo "$DOC"
   echo "ERROR--unexpected exit from ${BASH_SOURCE} script at line:"
   echo "   $BASH_COMMAND"
}
trap error_exit EXIT
#
# Process option (verbose flag)
#
SLEEPTIME=1
_V=0
verbose_flag=""
while getopts "v" OPTION
do
   case ${OPTION} in
     v) _V=1
	verbose_flag="-v"
        ;;
   esac
done
#
# Get environmental variables.
#
source ~/.lorax/lorax_rc
#
# Functions
#
test_GET () {
   # Tests HTTP return code of GET, optionally printing results.
   # Arguments:
   #         $1 - target URL
   #         $2 - expected return code (200 if not supplied)
   #
   tmpfile=$(mktemp /tmp/lorax-test_all.XXXXX)
   if [ -z "${2}" ] ; then
      code="200"
   else
      code="${2}"
   fi
   status=$(curl ${LORAX_CURL_ARGS} -s -o ${tmpfile} -w '%{http_code}' ${LORAX_CURL_URL}${1})
   if [ "${status}" -eq "${code}" ]; then
      echo "GET ${1} returned HTTP code ${status} as expected."
      if [ "$_V" -eq 1 ]; then
	 echo "Response is:"
         cat ${tmpfile}
         echo ""
	 echo ""
      fi
      rm "$tmpfile"
   else
      echo "FATAL ERROR--GET ${LORAX_CURL_URL}${1} returned HTTP code ${status}, expected ${2}."
      echo "Full response is:"
      cat ${tmpfile}
      echo ""
      rm "$tmpfile"
      trap - EXIT
      exit 1
   fi
}
#
test_GET_PASSWORD() {
   # Tests HTTP return code of GET with password, optionally printing results.
   # Arguments:
   #         $1 - target URL
   #         $2 - expected return code (200 if not supplied)
   #
   tmpfile=$(mktemp /tmp/lorax-test_all.XXXXX)
   if [ -z "${2}" ] ; then
      code="200"
   else
      code="${2}"
   fi
   status=$(curl -u lorax:${LORAX_SECRET_KEY} ${LORAX_CURL_ARGS} -s -o ${tmpfile} -w '%{http_code}' ${LORAX_CURL_URL}${1})
   if [ "${status}" -eq "${code}" ]; then
      echo "GET ${1} returned HTTP code ${status} as expected."
      if [ "$_V" -eq 1 ]; then
	 echo "Response is:"
         cat ${tmpfile}
         echo ""
	 echo ""
      fi
      rm "$tmpfile"
   else
      echo "FATAL ERROR--GET ${LORAX_CURL_URL}${1} returned HTTP code ${status}, expected ${2}."
      echo "Full response is:"
      cat ${tmpfile}
      echo ""
      rm "$tmpfile"
      trap - EXIT
      exit 1
   fi
}
#
test_DELETE() {
   # Tests HTTP return code of DELETE, optionally printing results.
   # Arguments:
   #         $1 - target URL
   #         $2 - expected return code (200 if not supplied)
   #
   tmpfile=$(mktemp /tmp/lorax-test_all.XXXXX)
   if [ -z "${2}" ] ; then
      code="200"
   else
      code="${2}"
   fi
   status=$(curl ${LORAX_CURL_ARGS} -s -o ${tmpfile} -w '%{http_code}' -X 'DELETE' ${LORAX_CURL_URL}${1})
   if [ "${status}" -eq "${code}" ]; then
      echo "DELETE ${1} returned HTTP code ${status} as expected."
      if [ "$_V" -eq 1 ]; then
	 echo "Response is:"
         cat ${tmpfile}
         echo ""
	 echo ""
      fi
      rm "$tmpfile"
   else
      echo "FATAL ERROR--GET ${LORAX_CURL_URL}${1} returned HTTP code ${status}, expected ${2}."
      echo "Full response is:"
      cat ${tmpfile}
      echo ""
      rm "$tmpfile"
      trap - EXIT
      exit 1
   fi
}
#
poll_until_positive() {
   echo -n "Polling ${1} "
   while [ `curl ${LORAX_CURL_ARGS} -s ${LORAX_CURL_URL}${1}` -lt 0 ]; do
     echo -n "."
     sleep ${SLEEPTIME}
   done
   echo " done."
}
#
# Start testing.
#
echo "Testing lorax server on ${LORAX_CURL_URL}."
#
# Test random non-tree targets.
#
test_GET /status
test_GET /healthcheck
test_GET /badtarget 404
test_GET /trees/families.json

# Post sequences.
./post_FASTA.sh ${verbose_flag}  peptide aspartic_peptidases.faa aspartic_peptidases sequences
# Post non-FASTA file throws a 406.
 ./post_FASTA.sh ${verbose_flag}  peptide 59026816.hmm bad_seqs sequences 406
# Post alignment.
./post_FASTA.sh ${verbose_flag}  peptide aspartic_peptidases_aligned.faa prealigned alignment
# Post of an invalid HMM throws a 406.
./put_HMM.sh ${verbose_flag} aspartic_peptidases.faa prealigned 406
# Align to an HMM.
./put_HMM.sh ${verbose_flag} 59026816.hmm aspartic_peptidases
test_GET /trees/aspartic_peptidases/hmmalign
poll_until_positive /trees/aspartic_peptidases/hmmalign/status
test_GET /trees/aspartic_peptidases/alignment
test_GET /trees/aspartic_peptidases/hmmalign/run_log.txt
# Calculate a tree.
test_GET /trees/aspartic_peptidases/FastTree
poll_until_positive /trees/aspartic_peptidases/FastTree/status
test_GET /trees/aspartic_peptidases/FastTree/tree.nwk
test_GET /trees/aspartic_peptidases/FastTree/tree.xml
test_GET /trees/aspartic_peptidases/FastTree/run_log.txt
# Post sof uperfamily to forbidden name throws a 403.
./post_FASTA.sh ${verbose_flag}  peptide zeama.faa prealigned.FastTree sequences 403
# Superfamily tests.
./post_FASTA.sh ${verbose_flag}  peptide zeama.faa aspartic_peptidases.myseqs sequences
test_GET /trees/aspartic_peptidases.myseqs/hmmalign_FastTree
poll_until_positive /trees/aspartic_peptidases.myseqs/FastTree/status
test_GET /trees/aspartic_peptidases.myseqs/alignment
test_GET /trees/aspartic_peptidases.myseqs/FastTree/tree.nwk
test_GET /trees/aspartic_peptidases.myseqs/FastTree/tree.xml
test_GET /trees/aspartic_peptidases.myseqs/FastTree/run_log.txt
test_DELETE /trees/aspartic_paptidases.FastTree 403  # forbidden to remove subdirs this way
test_DELETE /trees/aspartic_peptidases.myseqs
#
# Passworded targets.
#
test_GET_PASSWORD /log.txt
test_GET_PASSWORD /environment
trap - EXIT
echo "lorax tests completed successfully."
exit 0
