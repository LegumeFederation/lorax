#!/bin/bash
# Example of how to POST a peptide sequence.
#
# Usage:
#       post_to_lorax.sh  HOST PORT FASTA FAMILYNAME
#             where
#                    
curl \
  -F "peptide=@${3}" \
  ${1}:${2}/trees/${4}/alignment
