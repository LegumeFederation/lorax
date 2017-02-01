S
#!/bin/bash
# Example of how to POST a peptide sequence.
#
# Usage:
#       post_to_lorax.sh  HOST PORT FASTA FAMILY
#             where
#			HOST is the host ip
#                       PORT is the lorax port
#                       FASTA is the FASTA alignment file
#                       FAMILY is the name to be used for this family
#
# Example:
#         post_to_lorax.sh localhost 5000 sequences.faa short
curl \
  -F "peptide=@${3}" \
  ${1}:${2}/trees/${4}/alignment
