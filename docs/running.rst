Running lorax
=============

To start lorax in a test/development configuration (flask, with the lorax/ subdirectory of the git working tree bind-mounted into the ``flask`` container)::

    docker compose up -d

To start lorax in a "production" configuration (gunicorn, with no bind mounting)::

    docker compose -f docker-compose.yml up -d

To start lorax *and* load predefined gene families, add the ``--profile load`` option::

    docker compose --profile load up -d 

It is also useful to run an RQ dashboard (via ``docker-compose up -d rq_dashboard``).
The resulting dashboard is then accessible via web interface on port 9181.

To stop ``lorax`` (either development or production)::

    docker compose down [-v]

Where the optional ``-v`` option (to remove volumes) should only be used if
the lorax data directory (containing any generated MSAs and phylogenetic
trees) should not persist.

``lorax`` is intended to be run in a trusted environment and contains no
authentication.  It should be
run on ports that are accessible only to trusted hosts.  Running ``lorax`` on
a public port opens the
possibility of denial-of-service attacks.
