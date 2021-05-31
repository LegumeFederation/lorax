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
| Issues            | |issues|   |            |
+-------------------+------------+------------+


.. |TheLorax| image:: docs/lorax_big_icon.jpg
     :target: https://en.wikipedia.org/wiki/The_Lorax
     :alt: Dr. Suess, The Lorax

.. |repo| image:: https://img.shields.io/github/commits-since/LegumeFederation/lorax/0.94.svg
    :target: https://github.com/LegumeFederation/lorax
    :alt: GitHub repository

.. |license| image:: https://img.shields.io/badge/License-BSD%203--Clause-blue.svg
    :target: https://github.com/LegumeFederation/lorax/blob/master/LICENSE.txt
    :alt: License terms

.. |rtd| image:: https://readthedocs.org/projects/lorax/badge/?version=latest
    :target: http://lorax.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Server

.. |issues| image:: https://img.shields.io/github/issues/LegumeFederation/lorax.svg
    :target:  https://github.com/LegumeFederation/lorax/issues
    :alt: Issues reported

.. |requires| image:: https://requires.io/github/LegumeFederation/lorax/requirements.svg?branch=master
     :target: https://requires.io/github/LegumeFederation/lorax/requirements/?branch=master
     :alt: Requirements Status

.. _Flask: http://flask.pocoo.org/
.. _RQ: https://github.com/nvie/rq
.. _HMMER: http://hmmer.org
.. _RAxML: https://github.com/stamatak/standard-RAxML
.. _FastTree: http://www.microbesonline.org/fasttree

## Running

Test/development (flask, with $PWD bind-mounted into container)

```
docker-compose up -d
```

Production (gunicorn)

```
docker-compose -f docker-compose.yml up -d
```

## Running Tests

Development mode (flask, with $PWD bind-mounted into container)

```
docker-compose run test
```

Production (gunicorn)

```
docker-compose -f docker-compose.yml run test
```

## (Optional) RQ dashboard

```
docker-compose up -d rq_dashbaord
```

Point your browser at http://localhost:9181 (or whatever host the dockerd is running on)
