.. lorax documentation master file, created by Joel Berendzen on Aug 30, 2017.

Lorax "Speaks for the Trees"
================================
``lorax`` is a Flask-based web service that uses asynchronous queues (via RQ) to
calculate and serve up multiple sequence alignments and phylogenetic trees.
``lorax`` uses pre-calculated Hidden-Markov Models (HMM) of protein families
together with ``hmmalign`` to
calculate multiple sequence alignments in either peptide or DNA space.

``lorax`` calculates phylogenetic trees from either DNA or protein sequences by external
processes in a computationally-intensive step that can take from minutes to
days depending on the number of sequences and their sizes. Generally the
computational time increases linearly with the average length of sequences
and as the square of the number of input sequences.  The tree-building
software that ``lorax`` knows about are:

============= =================================================================
Tree Builder   Description
============= =================================================================
FastTree      `FastTree <https://www.microbesonline.org/fasttree/>`_ is the
              fastest tree-builder and is the default tree-building algorithm.

RAxML         `RAxML <http://sco.h-its.org/exelixis/web/software/raxml/index.html>`_
              is believed to be the more accurate tree-building algorithm, but
              at its fastest is probably 100x slower than FastTree.  It is
              possible to use the RaxML EPA algorithm to do placement of test
              sequences on existing RaxML trees.
============= =================================================================

Sections
--------
.. toctree::
   :maxdepth: 1
   :caption: See the following sections for details:

   goals
   installation
   direct
   anaconda
   test
   configuration
   running
   urls
   monitoring
   lorax


Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
