Server for Phylogenetic Trees
=============================

``lorax`` calculates and serves up multiple sequence alignments and phylogenetic trees.

How does lorax calculate multiple sequence alignments?
------------------------------------------------------
``lorax`` uses ``hmmalign`` to calculate multiple sequence alignments in either peptide or DNA
space.  An HMM must be given to ``lorax``.

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

``/trees/<family>/sequences``       ``PUT`` a FASTA-formatted set of aligned sequences.
                                    ID fields must be unique and use ``UTF-8`` encoding.
                                    If the multipart key is ``peptide``, the sequences
                                    are assumed to be protein sequences; if the key is
                                    ``DNA``, DNA sequences are assumed.  ``<family>``
                                    is used as a directory name and must not include
                                    special characters such as ``/``.  See the
                                    ''post_to_lorax.sh`` script in the test/ directory
                                    for an example of how to post.  Returns a JSON
                                    object that gives information about the number and
                                    length of submitted sequences.

``/trees/<family>/alignment``       ``PUT`` a FASTA-formatted set of aligned
                                    sequences.  Same as for sequences above, except
                                    dash (``-``) characters are used as spacings in
                                    alignments.

``/trees/<family>/HMM``             ``PUT`` an HMM for use with ``hmmalign``.

``/trees/<family>/hmmalign``        A ``GET`` of this URL will cause an HMM alignment
                                    to be calculated.  This step is not needed if
                                    an alignment is supplied.

``/trees/<family>/FastTree``        A ``GET`` of this URL will cause a FastTree tree to be
                                    calculated and a Newick tree to be returned.  This
                                    operation may take a long time and result in a timeout, which
                                    is why polling methods are provided.

``/trees/<family>/RAxML``           Same as above, execpt using RAxML as the tree builder.

``/trees/<fam>/<meth>/status``      Returns -1 if tree calculation is ongoing, and the exit
                                    code of the tree-builder <meth> if calculation is complete.

``/trees/<fam>/<meth>/tree``        Returns already-calculated tree without recalculating.

``/trees/<fam>/<meth>/log``         Returns the log file, including timings, of the tree
                                    calculation.

=================================== ===========================================================

Running lorax
-------------

A ``config.json`` file must exist in the current working directory; one may be obtained from the ``test`` directory
of the repository along with demo shell scripts.  ``lorax`` is started as a command-line argument with optional
``--host`` and ``--port`` arguments.

Log files with time-stamped names will be created in the directory specified by ``paths/log`` in ``config.json``.
The example that is shipped uses the ``log/`` directory.

``lorax`` is intended to be run on localhost only and contains no authentication code.

We recommend that ``lorax`` be run in a virtual environment.  However, the shell scripts will work for
real environments as well.