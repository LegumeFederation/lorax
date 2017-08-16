Server for Phylogenetic Trees
=============================

lorax "speaks for the trees" by calculating multiple sequence alignments and trees.

How does lorax calculate multiple sequence alignments?
------------------------------------------------------
``lorax`` uses a pre-calculated HMM and ``hmmalign`` to calculate multiple sequence alignments
in either peptide or DNA
space.

How does lorax calculate phylogenetic trees?
--------------------------------------------

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

RAxML         `RAxML <http://sco.h-its.org/exelixis/web/software/raxml/index.html>`_ is believed
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
``/log.txt``                        A ``GET`` of this URL returns the log file of the current
                                    run.

``/rq``                             A dashboard of the queues used by RQ, if asynchronous
                                    queueing is in use.

``/trees/families.json``            A ``GET`` of this URL returns a JSON list of defined
                                    families.

``/trees/<family>/sequences``       ``POST`` a FASTA-formatted set of aligned sequences.
                                    ID fields must be unique and use ``UTF-8`` encoding.
                                    If the multipart key is ``peptide``, the sequences
                                    are assumed to be protein sequences; if the key is
                                    ``DNA``, DNA sequences are assumed.  ``<family>``
                                    is used as a directory name and must not include
                                    special characters such as ``/``.  See the
                                    ''post_to_lorax.sh`` script in the test/ directory
                                    for an example of how to post.  Returns a JSON
                                    object that gives information about the number and
                                    length of submitted sequences.  Throws a 400 error if
                                    a proper multipart key is not found.  Throws a 406 error
                                    if empty or improperly-formatted FASTA file is sent.

``/trees/<family>/alignment``       ``POST`` a FASTA-formatted set of aligned
                                    sequences.  Same as for sequences above, except
                                    dash (``-``) characters are used as spacings in
                                    alignments.

``/trees/<family>/HMM``             ``PUT`` a family HMM for use with ``hmmalign``.  Throws
                                    a 400 error if family has not been previously created.
                                    Returns a JSON dictionary of HMM stats.  Throws a
                                    406 error if the HMM definition is not valid.

``/trees/<family>/hmmalign``        A ``GET`` of this URL will cause an HMM alignment
                                    to be calculated.  This step is not needed if
                                    an alignment is supplied.  Throws a 400 error if
                                    a sequence file is not found.  Throws a 417 error
                                    if ``hmmalign`` returned a non-zero process code.

``/trees/<family>/FastTree``        A ``GET`` of this URL will cause a FastTree tree to be
                                    calculated and a Newick tree to be returned.  This
                                    operation may take a long time and result in a timeout, which
                                    is why polling methods are provided.  Throws a 417 error
                                    if an improper family name was provided.  Throws a 404
                                    error if family was not previously created.  Throws a 405
                                    error if an alignment is not found.  Throws a 417 error if

``/trees/<family>/RAxML``           Same as above, execpt using RAxML as the tree builder.

``/trees/<fam>/hmmalign_FastTree``  A ``GET`` of this URL will cause the alignment and tree-
                                    building steps to be chained.

``/trees/<fam>/<meth>/status``      Returns -1 if tree calculation is ongoing, and the exit
                                    code of the tree-builder <meth> if calculation is complete.

``/trees/<fam>/<meth>/tree.nwk``    Returns already-calculated tree in Newick format.

``/trees/<fam>/<meth>/tree.xml``    Returns already-calculated tree in phyloXML format.

``/trees/<fam>/<meth>/run_log.txt`` Returns the log file, including timings, of the tree
                                    calculation.

``/trees/<fam>.<super>/sequences``  ``POST`` additional sequences to be considered a
                                    superfamily of existing family ``<fam>``.  ``<super>``
                                    cannot be a reserved name such as ``FastTree``.  These
                                    sequences will be concatenated to the existing family
                                    sequences, with ``<super>`` prepending ID strings.

``/trees/<family>.<superfamily>/``  ``DELETE`` a superfamily.

``/trees/<f>.<s>/<meth>/status``    Returns status of a superfamily tree calculation.

``/trees/<f>.<s>/<meth>/tree.nwk``  Returns tree of a superfamily in Newick format.


``/trees/<f>.<s>/<meth>/tree.xml``  Returns tree of a superfamily in phyloXML format.


``/trees/<f>.<s>/<m>/run_log.txt``  Returns the log file of a superfamily tree calculation.


=================================== ===========================================================

Configuration
-------------

``lorax`` is complex and configured in multiple layers.  The lowest layer is from variables in the
``config.py`` file in the distribution, which defines multiple classes of configuration variable
settings.  These configuration modes are selected among at run time via the value of the
environmental variable ``LORAX_CONFIGURATION``:

===================== ============================================================================
LORAX_CONFIGURATION   Interpretation
===================== ============================================================================
``base``              A vanilla mode suitable for manual testing without debugging on.

``development``       A full debugging mode, not secure, highly verbose, and with synchronous
                      operation (no queues).

``testing``           A mode suitable for running test suites.

``deployment``        Production mode, with logging to file.

===================== ============================================================================

The next level of configuration is via the pyfile ``config.cfg``.  Values placed in this file
overlay values from ``config.py``.  The location of this file is instance-relative.

The lowest level of configuration is via environmental variables which begin with ``LORAX_`` and
which follow the values specified in the configuration pyfile.

Running lorax
-------------

 ``lorax`` can be run via command line with no arguments.

If asynchronouse queues are switched on (modes other than ``development``), then ``redis``
will need to be started at the address specified by the configuration variable ``RQ_REDIS_URL``.
After that, two RQ work queues will need to be started as well:

    rqworker treebuilding
    rqworker alignment

It is also useful to run a dashboard (via ``rq-dashboard``).

``lorax`` is intended to be run in a trusted environment and contains no authentication.  It should be
run on ports that are accessible only to trusted hosts.  Running ``lorax`` on a public port opens the
possibility of denial-of-service attacks.

We recommend that ``lorax`` be run in a virtual environment if on a shared server.  However, the shell
scripts willwork for real environments as well.

Files
-----

Log files with time-stamped names will be created in the directory specified by ``PATHS['log']``, by
default an instance-relative ``log/`` directory.

Data files are created in the directory specified by ``PATHS['data']``, by default an instance-relative
``data/`` directory.  In deployment, this will usually be an absolute path.
