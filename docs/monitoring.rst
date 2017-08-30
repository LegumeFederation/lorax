Monitoring
==========
There is monitoring of ``lorax`` and associated processes via web interfaces
at multiple levels:

=============================== ===============================
Address                         Type of monitor
=============================== ===============================
SUPERVISOR_HOST:SUPERVISOR_PORT Supervisord status and controls 
                                (password-protected).
LORAX_HOST:LORAX_PORT/rq        RQ queue info, including errors.
=============================== ===============================

The default supervisord port is 58928.
