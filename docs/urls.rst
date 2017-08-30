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
