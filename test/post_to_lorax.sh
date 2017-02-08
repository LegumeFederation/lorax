#!/bin/bash
# Example of how to POST a peptide sequence.
#
# Usage:
#       post_to_lorax.sh  TYPE FASTA FAMILY
#             where
#                       TYPE is either "peptide" or "DNA"
#                       FASTA is the FASTA alignment file
#                       FAMILY is the name to be used for this family
#
# Example:
#         post_to_lorax.sh peptide sequences.faa short
#
if [[ ! -v LORAX_HOST ]] ; then
	echo "Must set LORAX_HOST before running this script"
	exit 1
fi
if [[ ! -v LORAX_PORT ]] ; then
	echo "Must set LORAX_PORT before running this script"
	exit 1
fi
if [[ $1 == "peptide" ]] ; then
	type="peptide"
elif [[ $1 == "DNA" ]]; then
	type="DNA"
else
	echo "Unrecognized sequence type ${1}"
	exit 1
fi
if [ ! -f "$2" ] ; then
	echo "Must specify a readable sequence file."
	exit 1
fi
if [ -z "$3" ] ; then
	echo "Must give a family name."
	exit 1
fi

curl \
  -F "${type}=@${2}" \
  ${LORAX_HOST}:${LORAX_PORT}/trees/${3}/alignment
