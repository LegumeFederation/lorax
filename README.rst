lorax is a Flask-based web service for calculating multiple sequence alignments
and phylogenetic trees for genes and gene families.  Under the hood, lorax uses
`FastTree`_ or `RAxML`_ to calculate trees, `HMMER`_ to do multiple sequence
alignments, `RQ`_ to queue long calculations, and `Flask`_ to serve up results.


.. image:: https://img.shields.io/pypi/v/lorax.svg   :target:
.. image:: https://img.shields.io/pypi/l/lorax.svg   :target:
.. image:: https://img.shields.io/pypi/pyversions/lorax.svg   :target:
.. image:: https://img.shields.io/pypi/status/lorax.svg   :target:
.. image:: https://img.shields.io/github/commits-since/LegumeFederation/lorax/0.92.svg   :target:

:Homepage: `Lorax Homepage`_
:Download: `lorax on PyPI`_
:Documentation: `Readthedocs`_
:License: `BSD 3-Clause License`_
:Issue tracker: `Github Issues`_

.. _Lorax Homepage: https://github.com/LegumeFederation/lorax
.. _BSD 3-Clause License: https://github.com/LegumeFederation/lorax/blob/master/LICENSE.txt
.. _Readthedocs: https://lorax.readthedocs.io/en/latest
.. _lorax on PyPI: https://pypi.python.org/pypi/lorax
.. _Flask: http://flask.pocoo.org/
.. _RQ: https://github.com/nvie/rq
.. _HMMER: http://hmmer.org
.. _RAxML: https://github.com/stamatak/standard-RAxML
.. _FastTree: http://www.microbesonline.org/fasttree
.. _Github Issues: https://github.com/LegumeFederation/lorax/issues



