Testing
=======
To test lorax, issue the command::

    docker-compose run test

This will bind-mount the lorax/ subdirectory in the git working tree
into the container at /usr/src/app/lorax and ``run lorax/test/test_targets.sh``.

The last command should finish with
"lorax test completed successfully."

To test a "production" deployment (not bind-mounting lorax/ in the container,
and starting a gunicorn server instead of flask)::

    docker-compose -f docker-compose.yml run test

You may also wish to load a full-sized data model to work with.  The
script ``get_big_model.sh`` will do that for you.  The model of 12
legume genomes (against the phytozome 10.2 HMM's) is rather large
at 900 MB of downloads and some 7 GB of data when loaded, so expect
this to take a while (about 30 minutes on a core i7 with SSD).  This
script will define some 18,000 legume gene families.

If you wish to stop lorax after the tests, issue the command::

    docker-compose down

