#!/bin/bash
# Test all lorax targets.
#
# Usage:
#       lorax_test.sh [-v]
#
# Options:
#       -v  verbose mode, shows all returns.
#
#
# Before running this script, lorax should be configured and
# started via the lorax_env script.
#
set -e # exit on errors
error_exit() {
  echo "ERROR-unexpected exit of test."
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
source lorax_envvars
#
# Functions
#
test_GET () {
   # Tests HTTP return code of commands, optionally printing results.
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
      echo "FATAL ERROR--GET ${1} returned HTTP code ${status}, expected ${2}."
      echo "Full response is:"
      cat ${tmpfile}
      echo ""
      rm "$tmpfile"
      exit 1
   fi
}

test_DELETE () {
   # Tests HTTP return code of commands, optionally printing results.
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
      echo "FATAL ERROR--GET ${1} returned HTTP code ${status}, expected ${2}."
      echo "Full response is:"
      cat ${tmpfile}
      echo ""
      rm "$tmpfile"
      exit 1
   fi
}


poll_until_positive() {
   echo -n "Polling ${1} "
   while [ `curl ${LORAX_CURL_ARGS} -s ${LORAX_CURL_URL}${1}` -lt 0 ]; do
     echo -n "."
     sleep ${SLEEPTIME}
   done
   echo " done."
}

# GET a bad target throws a 404.
echo "testing lorax server on ${LORAX_URL}"

test_GET /

test_GET /healthcheck

test_GET /log.txt

test_GET /badtarget 404

test_GET /test_exception 500

test_GET /trees/families.json

# Post sequences.
./post_FASTA.sh ${verbose_flag}  peptide aspartic_peptidases.faa aspartic_peptidases sequences
if [ "$?" -eq 1 ] ; then
   exit 1
fi

# Post non-FASTA file throws a 406.
 ./post_FASTA.sh ${verbose_flag}  peptide 59026816.hmm bad_seqs sequences 406
if [ "$?" -eq 1 ] ; then
   exit 1
fi

# Post alignment.
./post_FASTA.sh ${verbose_flag}  peptide aspartic_peptidases_aligned.faa prealigned alignment

# Post an invalid HMM throws a 406.
./put_HMM.sh ${verbose_flag} aspartic_peptidases.faa prealigned 406

# Post a valid HMM.
./put_HMM.sh ${verbose_flag} 59026816.hmm aspartic_peptidases


test_GET /trees/aspartic_peptidases/hmmalign

poll_until_positive /trees/aspartic_peptidases/hmmalign/status

test_GET /trees/aspartic_peptidases/alignment

test_GET /trees/aspartic_peptidases/hmmalign/run_log.txt

test_GET /trees/aspartic_peptidases/FastTree

poll_until_positive /trees/aspartic_peptidases/FastTree/status

test_GET /trees/aspartic_peptidases/FastTree/tree.nwk

test_GET /trees/aspartic_peptidases/FastTree/tree.xml

test_GET /trees/aspartic_peptidases/FastTree/run_log.txt

# Post superfamily to forbidden name.
./post_FASTA.sh ${verbose_flag}  peptide zeama.faa prealigned.FastTree sequences 403

# Post superfamily.
./post_FASTA.sh ${verbose_flag}  peptide zeama.faa aspartic_peptidases.myseqs sequences


# Test superfamily.
test_GET /trees/aspartic_peptidases.myseqs/hmmalign_FastTree

poll_until_positive /trees/aspartic_peptidases.myseqs/FastTree/status

test_GET /trees/aspartic_peptidases.myseqs/alignment

test_GET /trees/aspartic_peptidases.myseqs/FastTree/tree.nwk

test_GET /trees/aspartic_peptidases.myseqs/FastTree/tree.xml

test_GET /trees/aspartic_peptidases.myseqs/FastTree/run_log.txt

test_DELETE /trees/aspartic_paptidases.FastTree 403  # forbidden to remove subdirs this way

test_DELETE /trees/aspartic_peptidases.myseqs

#if [ "$_V" -eq 0 ]; then
# rm -r data/*  # remove data if not verbose
#fi
trap - EXIT
echo "lorax tests completed successfully."
exit 0
