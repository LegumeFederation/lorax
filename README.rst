Server for Phylogenetic Trees
=============================

``lorax`` is a REgiSTful web server that calculates and serves up phylogenetic trees.


How does lorax calculate phylogenetic trees?
---------------------------------------------

Phylogenetic trees are built from either DNA or protein sequences by external processes in
a computationally-intensive step that can take from minutes to days depending on the number of
sequences and their sizes. Generally the computational time
increases linearly with the average length of sequences and as the square of the number of 
input sequences.  The tree-building software that ``lorax`` knows about the following tree builders:

============= =================================================================================
Tree Builder   Description 
============= =================================================================================
FastTree      `FastTree <https://www.microbesonline.org/fasttree/>`_ is the fastest tree-builder
              and is the default tree-building algorithm.  

RaxML         `RaxML <http://sco.h-its.org/exelixis/web/software/raxml/index.html>`_ is believed
              to be the more accurate tree-building algorithm, but at its fastest is probably
              100x slower than FastTree.  It is possible to the RaxML EPA algorithm to do
              placement of test sequences on existing RaxML trees.

============= =================================================================================

URLs
----
``lorax`` interacts through standard http ``GET`` and ``POST`` commands.  POST of
sequence data and calculation of trees results in permanent URLs that ``lorax`` will serve up
until such time as the corresponding disk entries are deleted. POSTing to existing sequence
data will result in over-writing.


=================================== ===========================================================
URL                                 Interpretation
=================================== ===========================================================
``/``                               Returns a browsable auto-indexed directory tree.

``/config``                         Returns the configuration in JSON representation.

``/trees/<family>/alignment``       ``PUT`` a FASTA-formatted set of aligned
                                    sequences.  Dash (``-``) characters are used as spacing
                                    in alignments.  ID fields must be unique and use ``UTF-8`
                                    encoding.  If the multipart key is ``peptide``, the FASTA is
                                    assumed to be of peptide sequences; if the key is ``DNA, DNA
                                    sequences are assumed.  <familyname> is used as a directory
                                    name , and
                                    must not include special characters such as ``/`` or an
                                    error will be returned.  See the ``post_to_lorax.sh``
                                    script for an example of how to post.

``/trees/<family>/FastTree``        A ``GET`` of this URL will cause a FastTree tree to be
                                    calculated and a Newick tree to be returned.  This
                                    operation may take a long time and result in a timeout, which
                                    is why polling methods are provided.

``/trees/<family>/RaxML``           Same as above, execpt using RaxML as the tree builder.

``/trees/<fam>/<meth>/status``      Returns -1 if tree calculation is ongoing, and the exit
                                    code of the tree-builder <meth> if calculation is complete.

``/trees/<fam>/<meth>/tree``        Returns already-calculated tree without recalculating.

``/trees/<fam>/<meth>/log``         Returns the log file, including timings, of the tree
                                    calculation.

=================================== ===========================================================

