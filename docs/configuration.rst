Configuration
-------------
The design of ``lorax`` is necessarily complex, with configuration occurring and in multiple layers.
The lowest layer is from variables in the
``config.py`` file in the distribution, which defines multiple classes of configuration variable
settings.  These configuration modes are selected among at run time via the value of the
environmental variable ``LORAX_CONFIGURATION``:

===================== ============================================================================
LORAX_CONFIGURATION   Interpretation
===================== ============================================================================
``base``              A vanilla mode suitable for manual testing without debugging on.

``development``       A full debugging mode, not secure, highly verbose, and with synchronous
                      operation (no queues).

``testing``           A mode suitable for running test suites.

``deployment``        Production mode, with logging to file.

===================== ============================================================================

The next level of configuration is via the pyfile ``config.cfg``.  Values placed in this file
overlay values from ``config.py``.  The location of this file is instance-relative.

The lowest level of configuration is via environmental variables which begin with ``LORAX_`` and
which follow the values specified in the configuration pyfile.

We now configure lorax.  To begin, we need to enter the proper
environment, using the lorax_env script.  The path to this script is
the value of LORAX_ROOT you chose at install time::

        /path/to/lorax_env -i

You will now get a ``lorax_env>`` prompt and you are ready to configure.

If you did a direct installation using the ``lorax_tool`` script, you should
review and edit the ``my_config.sh`` script to reflect the settings you wish
to use
use for your installation.  Then run ``./lorax_tool configure_pkg`` to do the build.

configuration variables.  If you wish to change any of them, do it before
issuing the "configure_instance" command, which will write the startup
configurations which include such things as port numbers and which processes
to start.  Configuration may be done either via the "lorax config" command
or via environmental variables.  In particular the "LORAX_MODE" environmental
variable controls the setting of multiple variables in defining which processes
will get started.  Usually you will want to configure the following variables
in order to expose the lorax server to the internet (substituting the
desired values in the places beginning with ``MY_``)::

        lorax config host MY_IP_ADDRESS
        lorax config crashmail_email MY_EMAIL_ADDRESS
        lorax config secret_key # prints value of secret_key
        lorax create_instance

Now exit the lorax_env shell with control-D.  Run lorax and its associated
processes::

        /path/to/lorax_env supervisord; sleep 10
        /path/to/lorax_env supervisorctl status

The first command runs all the requested processes under control of a daemon.
The last should return a list of commands, all with status RUNNING.

Next, follow the testing instructions.