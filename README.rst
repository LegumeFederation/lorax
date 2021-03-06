.. epigraph:: I am the Lorax.  I speak for the trees.
              --Dr. Seuss


lorax implements a queued web service for calculating phylogenetic trees for
gene families.  Lorax uses `HMMER`_ to do multiple sequence alignments,
`FastTree`_ or `RAxML`_ to calculate trees,
`RQ`_ to queue calculations, and `Flask`_ to serve up results.


+-------------------+------------+------------+
| Latest Release    | |pypi|     | |TheLorax| |
+-------------------+------------+            +
| GitHub            | |repo|     |            |
+-------------------+------------+            +
| License           | |license|  |            |
+-------------------+------------+            +
| Documentation     | |rtd|      |            |
+-------------------+------------+            +
| Travis Build      | |travis|   |            |
+-------------------+------------+            +
| Coverage          | |coverage| |            |
+-------------------+------------+            +
| Code Grade        | |codacy|   |            |
+-------------------+------------+            +
| Dependencies      | |pyup|     |            |
+-------------------+------------+            +
| Issues            | |issues|   |            |
+-------------------+------------+------------+


.. |TheLorax| image:: docs/lorax_big_icon.jpg
     :target: https://en.wikipedia.org/wiki/The_Lorax
     :alt: Dr. Suess, The Lorax

.. |pypi| image:: https://img.shields.io/pypi/v/lorax.svg
    :target: https://pypi.python.org/pypi/lorax
    :alt: Python package

.. |repo| image:: https://img.shields.io/github/commits-since/LegumeFederation/lorax/0.94.svg
    :target: https://github.com/LegumeFederation/lorax
    :alt: GitHub repository

.. |license| image:: https://img.shields.io/badge/License-BSD%203--Clause-blue.svg
    :target: https://github.com/LegumeFederation/lorax/blob/master/LICENSE.txt
    :alt: License terms

.. |rtd| image:: https://readthedocs.org/projects/lorax/badge/?version=latest
    :target: http://lorax.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Server

.. |travis| image:: https://img.shields.io/travis/LegumeFederation/lorax.svg
    :target:  https://travis-ci.org/LegumeFederation/lorax
    :alt: Travis CI

.. |codacy| image:: https://api.codacy.com/project/badge/Grade/2ebc65ca90f74dc7a9238c202f327981
    :target: https://www.codacy.com/app/joelb123/lorax?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=LegumeFederation/lorax&amp;utm_campaign=Badge_Grade
    :alt: Codacy.io grade

.. |coverage| image:: https://codecov.io/gh/LegumeFederation/lorax/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/LegumeFederation/lorax
    :alt: Codecov.io test coverage

.. |issues| image:: https://img.shields.io/github/issues/LegumeFederation/lorax.svg
    :target:  https://github.com/LegumeFederation/lorax/issues
    :alt: Issues reported

.. |requires| image:: https://requires.io/github/LegumeFederation/lorax/requirements.svg?branch=master
     :target: https://requires.io/github/LegumeFederation/lorax/requirements/?branch=master
     :alt: Requirements Status

.. |pyup| image:: https://pyup.io/repos/github/LegumeFederation/lorax/shield.svg
     :target: https://pyup.io/repos/github/LegumeFederation/lorax/
     :alt: pyup.io dependencies

.. _Flask: http://flask.pocoo.org/
.. _RQ: https://github.com/nvie/rq
.. _HMMER: http://hmmer.org
.. _RAxML: https://github.com/stamatak/standard-RAxML
.. _FastTree: http://www.microbesonline.org/fasttree
