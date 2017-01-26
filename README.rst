Server for Phylogenetic Trees
=============================

``lorax`` is a RESTful web server that calculates and extends/recalculates phylogenetic trees.


How does lorax calculated phylogenetic trees?
---------------------------------------------

Phylogenetic trees are built from either DNA or protein sequences by external processes in
a computationally-intensive step that can take from minutes to days depending on the number of
sequences and their sizes. If the input sequences were not delivered to already aligned, ``lorax``
may need to run a multiple-sequence-alignment step as well.  Generally the computational time
increases linearly with the average length of sequences and as the square of the number of 
input sequences.  The tree-building software that ``lorax`` knows about includes the following:

============= =================================================================================
Tree Builder   Description 
============= =================================================================================
FastTree      `FastTree <https://www.microbesonline.org/fasttree/>`_ is the fastest tree-builder
              and is the default tree-building algorithm.  

RaxML         `RaxML <http://sco.h-its.org/exelixis/web/software/raxml/index.html>`_ is believed
              to be the more accurate tree-building algorithm, but at its fastest is probably
              100x slower than FastTree.  It is possible to the RaxML EPA algorithm to do
              placement of test sequences on existing RaxML trees.

paHMM-Tree    `paHMM-Tree <http://marbogusz.github.io/paHMM-Tree/>`_ is a new algorithm for
              creating phylogenetic trees that does not require Multiple Sequence Alignments
              yet is faster than other one-step tree builders.  At the moment, it runs single-
              threaded only, and seems to be ~5X slower than RaxML in fast mode.  Currently
              for testing only.  

============= =================================================================================

Inputs
------
Input to ``lorax`` is through a ``POST`` of data to a name under the ``lorax`` hierarchy.  If
accepted, this will result in permanent URLs that ``lorax`` will serve up until such time
as the corresponding disk entries are deleted. POSTing to an existing directory will result
in over-writing the previous tree  POSTing to a subdirectory of an existing tree will result
in a new tree being calculated which includes the sequences from the existing tree.

Here are the entries in the JSON object that may be defined:

=============== ===========================================================
Definition      Interpretation
=============== ===========================================================
Sequences       A FASTA-formatted set of sequences.  This field is required.
                Dash (`-`) characters may be used a space characters in
                pre-aligned sequences.  ID fields must be unique or an error
                will be raised. ID fields must use ``UTF-8`` encodings

Prealigned      If set to ``True``, the sequences are assumed already aligned
                and the MSA step will be skipped.

TreeBuilder     May be set to any of the values listed in the table above.
                Any other value results in an error.

=============== ===========================================================
