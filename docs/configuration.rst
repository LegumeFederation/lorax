Configuration
=============
The design of ``lorax`` is necessarily complex, with configuration occurring
in multiple layers at different times. Proceeding in order from highest to
lowest priority, these are:

======================= ==== ============================================================================
Layer                   Code            Description
======================= ==== ============================================================================
Program                 P    Some variables are output-only and defined (or overidden) at runtime.

Environmental Variable  E    Environmental variables beginning with ``LORAX_`` are parsed according to
                             the types of existing (lower-level) variables with matching name.  The
                             environmental variable names should be entirely upper-case.  If the variable
                             was not previously defined, it will be assumed to be of string type.

Config File             C    A config file for the instance (in the etc/ directory with prefix given by
                             the environmental variable LORAX_SETTINGS, default is ``lorax`` and extension
                             '.conf') is parsed before environmental variables.  The type is defined by
                             python parsing rules.  These values are changeable by the ``lorax config``
                             command.

Defaults                D    Default values are initialized depending on the value of the environmental
                             variable ``LORAX_CONFIGURATION``.  The following values are recognized:
                             * ``default``: a value suitable for testing and deployment
                             * ``development``: a debugging environment with much exposed.
                             * ``serverOnly``: same as default, but the queues are not started.
                             * ``treebuilder``: treebuilder queue is the only service started.
                             * ``aligner``: aligner queue is the only service started.

====================== ===== ============================================================================

Configuration Variables
-----------------------

======================= ===== ============================================================================
Configuration Variable  Code  Description
======================= ===== ============================================================================
ALERTMANAGER_DIR        P     Directory in which the alertmanager executable is found.

ALIGNERS                D     Dictionary of available aligners.

ALIGNMENT_QUEUE         D     Name of the alignment queue.

ALIGNMENT_QUEUE_TIMEOUT D     Maximum time-to-live for alignment jobs (default 86400)

CRASHMAIL_EMAIL         D     Email alert address.  Defaults to username.

CRASHMAIL_EVENTS        D     Defaults to "PROCESS_STATE_EXITED".

CURL_ARGS               P     Arguments for use with curl.

  CURL_URL type(str) =  "localhost:58927"

  DATA type(str) =  "/home/localhost/joelb/.lorax/0.94/var/data/"

  DATETIME type(str) =  "2017-09-19 13:19:07"

  DEBUG type(bool) =  False

  DIR_MODE type(str) =  "755"

  ENVIRONMENT_DUMP type(bool) =  False

  EXPLAIN_TEMPLATE_LOADING type(bool) =  False

  FASTTREE_EXE type(str) =  "FastTree-lorax"

  FILE_LOG_FORMAT type(str) =  "%(levelname)s: %(message)s"

  GUNICORN_LOG_LEVEL type(str) =  "debug"

  GUNICORN_UNIX_SOCKET type(bool) =  True

  GUNICORN_URL type(str) =  "unix://%(ENV_LORAX_VAR)s/run/gunicorn.sock"

  HMMALIGN_EXE type(str) =  "hmmalign"

  HOST type(str) =  "localhost"

  HOSTNAME type(str)      D   Hostname for nginx to use.  Defaults to

  JSONIFY_MIMETYPE type(str) =  "application/json"

  JSONIFY_PRETTYPRINT_REGULAR type(bool) =  True

  JSON_AS_ASCII type(bool) =  True

  JSON_SORT_KEYS type(bool) =  True
  LOG type(str) =  "/home/localhost/joelb/.lorax/0.94/var/log"
  LOGFILE type(bool) =  True
  LOGFILE_BACKUPCOUNT type(int) =  1
  LOGFILE_MAXBYTES type(int) =  10000000
  LOGFILE_NAME type(NoneType) =  None
  LOGGER_HANDLER_POLICY type(str) =  "always"
  LOGGER_NAME type(str) =  "lorax"
  MAX_CONTENT_LENGTH type(NoneType) =  None
  MODE type(str) =  "default"
  NAME type(str) =  "lorax"
  NGINX_EVENTS type(str) =  "use epoll;"
  NGINX_LISTEN_ARGS type(str) =  "deferred"
  NGINX_SERVER_NAME type(str) =  "localhost"
  NGINX_UNIX_SOCKET type(bool) =  False
  NGINX_URL type(str) =  "localhost:58927"
  NODE_EXPORTER_DIR type(str) =  "/home/localhost/joelb/.lorax/0.94/node_exporter-0.14.0.linux-amd64"
  PERMANENT_SESSION_LIFETIME type(timedelta) =  31 days, 0:00:00
  PLATFORM type(str) =  "Linux"
  PORT type(int) =  58927
  PREFERRED_URL_SCHEME type(str) =  "http"
  PRESERVE_CONTEXT_ON_EXCEPTION type(NoneType) =  None
  PROCESS_UMASK type(str) =  "0002"
  PROJECT_HOME type(str) =  "https://github.com/LegumeFederation/lorax"
  PROMETHEUS_DIR type(str) =  "/home/localhost/joelb/.lorax/0.94/prometheus-2.0.0-beta.2.linux-amd64"
  PROPAGATE_EXCEPTIONS type(NoneType) =  None
  PUSH_GATEWAY_DIR type(NoneType) =  None
  QUIET type(bool) =  False
  RAXML_EXE type(str) =  "raxmlHPC"
  RC_GROUP type(str) =  ""
  RC_USER type(str) =  "joelb"
  RC_VERBOSE type(bool) =  False
  REDIS_DB type(int) =  0
  REDIS_HOST type(str) =  "localhost"
  REDIS_PASSWORD type(NoneType) =  None
  REDIS_PORT type(int) =  0
  REDIS_UNIX_SOCKET type(bool) =  True
  REDIS_URL type(str) =  "unix://@'/home/localhost/joelb/.lorax/0.94/var/run/redis.sock?db=0"
  ROOT type(str) =  "/home/localhost/joelb/.lorax/0.94"
  RQ_ASYNC type(bool) =  True
  RQ_JOB_CLASS type(str) =  "rq.job.Job"
  RQ_POLL_INTERVAL type(int) =  2500
  RQ_QUEUES type(list) =  ['treebuilding', 'alignment']
  RQ_QUEUE_CLASS type(str) =  "rq.queue.Queue"
  RQ_REDIS_HOST type(str) =  "localhost"
  RQ_REDIS_PORT type(int) =  0
  RQ_REDIS_URL type(str) =  "unix://@'/home/localhost/joelb/.lorax/0.94/var/run/redis.sock?db=0"
  RQ_SCHEDULER_INTERVAL type(int) =  60
  RQ_SCHEDULER_QUEUE type(str) =  "alignment"
  RQ_UNIXSOCKET type(str) =  "unixsocket /home/localhost/joelb/.lorax/0.94/var/run/redis.sock"
  RQ_WORKER_CLASS type(str) =  "rq.worker.Worker"
  SECRET_KEY type(str) =  "b4KW2yahmcIB"  # <- from config file
  SEND_FILE_MAX_AGE_DEFAULT type(timedelta) =  12:00:00
  SENTRY_DSN type(str) =  ""
  SERVER_NAME type(NoneType) =  None
  SESSION_COOKIE_DOMAIN type(NoneType) =  None
  SESSION_COOKIE_HTTPONLY type(bool) =  True
  SESSION_COOKIE_NAME type(str) =  "session"
  SESSION_COOKIE_PATH type(NoneType) =  None
  SESSION_COOKIE_SECURE type(bool) =  False
  SESSION_REFRESH_EACH_REQUEST type(bool) =  True
  SETTINGS type(str) =  "lorax.conf"
  START_QUEUES type(list) =  ['treebuilding', 'alignment']
  STDERR_LOG_FORMAT type(str) =  "%(levelname)s: %(message)s"
  SUPERVISORD_HOST type(str) =  "localhost"
  SUPERVISORD_PORT type(int) =  58928
  SUPERVISORD_SERVERURL type(str) =  "unix://%(ENV_LORAX_VAR)s/run/supervisord.sock"
  SUPERVISORD_START_ALERTMANAGER type(bool) =  False
  SUPERVISORD_START_ALIGNMENT type(bool) =  True
  SUPERVISORD_START_CRASHMAIL type(bool) =  True
  SUPERVISORD_START_NGINX type(bool) =  True
  SUPERVISORD_START_NODE_EXPORTER type(bool) =  False
  SUPERVISORD_START_PROMETHEUS type(bool) =  False
  SUPERVISORD_START_PUSHGATEWAY type(bool) =  False
  SUPERVISORD_START_REDIS type(bool) =  True
  SUPERVISORD_START_SERVER type(bool) =  True
  SUPERVISORD_START_TREEBUILDING type(bool) =  True
  SUPERVISORD_UNIX_SOCKET type(bool) =  True
  SUPERVISORD_USER type(str) =  "lorax"
  TEMPLATES_AUTO_RELOAD type(NoneType) =  None
  TESTING type(bool) =  False
  THREADS type(int) =  0
  TMP type(str) =  "/home/localhost/joelb/.lorax/0.94/var/tmp"
  TRAP_BAD_REQUEST_ERRORS type(bool) =  False
  TRAP_HTTP_EXCEPTIONS type(bool) =  False
  TREEBUILDERS type(dict) =  {'FastTree': {'peptide': ['-nopr', '-log', 'peptide.log'], 'DNA': ['-nt', '-gtr', '-log', 'nucleotide.log', '-nopr']}, 'RAxML': {'peptide': ['-b', '12345', '-p', '12345', '-N', '10', '-m', 'PROTGAMMABLOSUM62'], 'DNA': ['-d']}}
  TREE_QUEUE type(str) =  "treebuilding"
  TREE_QUEUE_TIMEOUT type(int) =  2592000
  URL type(str) =  "http://localhost:58927"
  USERDATA type(str) =  "/home/localhost/joelb/.lorax/0.94/var/userdata/"
  USER_CONFIG_PATH type(str) =  "~/.lorax"
  USE_X_SENDFILE type(bool) =  False
  VAR type(str) =  "/home/localhost/joelb/.lorax/0.94/var"
  VERSION type(str) =  "0.94.64"
======================= ===== ============================================================================

Manual Configuration
--------------------
Configuring lorax uses the ``lorax config`` command, run in the proper
environment using the lorax_env script.  The path to this script is
the value of LORAX_ROOT you chose at install time::

        /path/to/lorax_env -i


You will now get a ``lorax_env>`` prompt and you are ready to configure.
For example::

        lorax config host MY_IP_ADDRESS
        lorax config crashmail_email MY_EMAIL_ADDRESS
        lorax config secret_key # prints value of secret_key
        lorax create_instance

Now exit the lorax_env shell with control-D.  Run lorax and its associated
processes::

        /path/to/lorax_env -v start

The start command, when run with the ``-v`` switch should return a list of
started processes, all with status RUNNING.


Configuring by Script
---------------------
If you did a direct installation using the ``lorax_tool`` script, you should
review and edit the ``my_config.sh`` script to reflect the settings you wish
to use use for your installation.  Then run ``./lorax_tool configure_pkg`` to do the build.