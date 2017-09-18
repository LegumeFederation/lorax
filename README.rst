.. epigraph:: I am the Lorax. I speak for the trees. I speak for the trees, for the trees have no tongues.
                  --Dr. Seuss, The Lorax

lorax is a web service for calculating multiple sequence alignments
and phylogenetic trees for genes and gene families.  Under the hood, lorax uses
`FastTree`_ or `RAxML`_ to calculate trees, `HMMER`_ to do multiple sequence
alignments, `RQ`_ to queue long calculations, and `Flask`_ to serve up results.

 .. |TheLorax| image:: docs/lorax_big_icon.jpg
     :target: https://en.wikipedia.org/wiki/The_Lorax
     :alt: Dr. Suess, The Lorax

.. |pypi| image:: https://img.shields.io/pypi/v/lorax.svg
    :target: https://pypi.python.org/pypi/lorax
    :alt: Python package

.. |repo| image:: https://img.shields.io/github/commits-since/LegumeFederation/lorax/0.94.svg
    :target: https://github.com/LegumeFederation/lorax
    :alt: GitHub repository

.. |license| image:: https://img.shields.io/github/license/LegumeFederation/lorax.svg
    :target: https://github.com/LegumeFederation/lorax/blob/master/LICENSE.txt
    :alt: License terms

.. |docs| image:: https://readthedocs.org/projects/lorax/badge/?version=latest
    :target: https://lorax.readthedocs.io/en/latest
    :alt: ReadTheDocs documentation

.. |travis| image:: https://secure.travis-ci.org/LegumeFederation/lorax.png
    :target:  https://travis-ci.org/LegumeFederation/lorax
    :alt: Travis CI

.. |landscape| image:: https://landscape.io/github/LegumeFederation/lorax/master/landscape.svg?style=flat
    :target: https://landscape.io/github/LegumeFederation/lorax
    :alt: landscape.io status

.. |codacy| image:: https://api.codacy.com/project/badge/Grade/2ebc65ca90f74dc7a9238c202f327981
    :target: https://www.codacy.com/app/joelb123/lorax?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=LegumeFederation/lorax&amp;utm_campaign=Badge_Grade
    :alt: Codacy.io grade

.. |coverage| image:: https://codecov.io/gh/LegumeFederation/lorax/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/LegumeFederation/lorax
    :alt: Codecov.io test coverage

.. |issues| image:: .. https://img.shields.io/github/issues/LegumeFederation/lorax.svg
    :target:  https://github.com/LegumeFederation/lorax/issues
    :alt: Issues reported


+-------------------+------------+------------+
| Latest Release    | |pypi|     | |TheLorax| |
+-------------------+------------+            +
| GitHub Repository | |repo|     |            |
+-------------------+------------+            +
| License           | |license|  |            |
+-------------------+------------+            +
| Documentation     |  |docs|    |            |
+-------------------+------------+            +
| Travis Build      | |travis|   |            |
+-------------------+------------+            +
| Coverage          | |coverage| |            |
+-------------------+------------+            +
| landscape.io score| |landscape||            |
+-------------------+------------+            +
| Codacy Grade      | |codacy|   |            |
+-------------------+------------+            +
| Issues            | |issues|   |            |
+-------------------+------------+------------+

.. _Flask: http://flask.pocoo.org/
.. _RQ: https://github.com/nvie/rq
.. _HMMER: http://hmmer.org
.. _RAxML: https://github.com/stamatak/standard-RAxML
.. _FastTree: http://www.microbesonline.org/fasttree




