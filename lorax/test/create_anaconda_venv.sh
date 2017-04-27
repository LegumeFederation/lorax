#!/bin/bash
# Needs bioconda and conda-forge channels to work.
conda create --name loraxenv python=3.6 click flask redis pip
conda install --name loraxenv biopython gunicorn hmmer fasttree
source activate loraxenv
cd ../..
pip install --editable .
