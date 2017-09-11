Running lorax
=============

 ``lorax`` can be run via command line with no arguments.

If asynchronous queues are switched on (modes other than ``development``),
then ``redis`` will need to be started at the address specified by the
configuration variable ``RQ_REDIS_URL``.
After that, two RQ work queues will need to be started as well::

    rqworker treebuilding
    rqworker alignment

It is also useful to run a dashboard (via ``rq-dashboard``).

``lorax`` is intended to be run in a trusted environment and contains no
authentication.  It should be
run on ports that are accessible only to trusted hosts.  Running ``lorax`` on
a public port opens the
possibility of denial-of-service attacks.

We recommend that ``lorax`` be run in a virtual environment if on a shared
server.  However, the shell scripts will work for real environments as well.


