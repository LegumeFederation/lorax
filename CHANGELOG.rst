Changelog
---------

.. snip

0.94
~~~~

- ``run_in_lorax_env`` script created to define the two required
  environmental variables and activate the virtual environment
  from either Anaconda or normal versions.

- ``configure_instance`` command defined to configure the supervisord
  scripts.

- Supervisord is now used to start lorax and associated version.  
  supervisord>4.0 (currently only from git) is required due to python3
  requirement.

- Setuptools >30 is now required, due to moving many things into setup.cfg.

- FastTree source now included in distribution; FastTree binary will be built
  and put in virtual environment under name ``FastTree-lorax``.

- License is now 3-clause BSD (was 4-clause BSD).

-  ``config_value`` command is now simply ``config``.

0.93.2
~~~~~~

-  Created the ``create_anaconda_venv.sh`` script for downstream to use.

-  Changed the development platform to Anaconda python 3.6 in a virtualenv.

-  Changed this file to ReStructuredText.

0.93.1
~~~~~~

-   Code passes PEP8.

0.93.2
~~~~~~

-  Redirected stderr on HMM check call.

-  ``LORAX_INSTANCE_DIR`` environmental variable allows overriding the location of the instance
   configuration file.  Useful for installations where the default instance path is not
   writable by the user.

-  ``config_value`` with no arguments now indicates whether variables are set from instance
   config files or environmental variables.

-  ``config_value --verbose VAR`` gives verbose information about the type of the variable
   and where it was set.

- The default type for ``config_value`` is now, in priority order:
     * The type specified with the ``--vartype`` option, if it exists.
     * The type of the extant variable.
     * str if not previously defined and ``--vartype`` is not specified.

-  ``config_value --type`` renamed to ``--vartype``, and now accepts any valid python type
   for its argument.  Types other than str and bool are parsed via JSON and have JSON
   typing rules (including demanding use of double quotes in places).  Note that for
   complex types, you may have to enclose the argument in single quotes to keep the
   shell from mangling it.


-  `config_value VAR` now prints the value.

v0.92
~~~~~

-  `get_config` and `set_config` commands are now condensed to `config_value`
   which does set if ``VALUE`` is defined, set get if now.  If ``VAR`` is not
   defined, ``config_value`` lists all variables along with whether they were
   set from environmental variables or not.

-- Broke up ``PATH`` from a dictionary to be three simple key:value objects:
     * DATA_PATH
     * LOG_PATH
     * DIR_MODE

v0.91
~~~~~

-  Package data moved to proper level of hierarchy.

-  ``ALIGNMENT_QUEUE_TIMEOUT`` and ``TREE_QUEUE_TIMEOUT`` config parameters.  Was defaulting to
   180 seconds.

v0.9
~~~~

-  Logging format is now configurable.

-  Added commands for easier setup:
     * copy_test_files
     * get_config
     * set_config
     * test_logging

-  Added PhyD3 files to static and template folders.

-  Added ``GET`` method for ``/alignment`` target to return MSA's.

-  Created ``requirements.in`` and ``requirements.txt ``dependencies list via pip-sync.

-  Removed ete3 in favor of biopython due to ete3 dependency problems with BSD.
   Less control over Newick formatting, though...trees may not appear to be rooted
   in some downstream programs.


v0.8
~~~~

-  Changed the tree output to be rooted, entailing a change in the exact Newick format used.
   Root node names are family names.  Trees are now ladderized.  ete3 is now a dependency.

-  Added the ``/rq`` dashboard target. rq_dashboard is now a dependency.

-  Added commands.

-  Changed startup methods considerably.  See the startup scripts for details.

v0.7
~~~~

-  Names of executables are now configuration parameters.  This allows for overriding of executable
   names on platforms where the name may vary.

-  Added DELETE target for superfamiles.

-  Calculation methods now return JSON dictionaries of job listings that include the following:
      * ``id``: id string
      * ``description``: description string, e.g., "FastTree tree of superfamily aspartic_peptidases.myseqs"
      * ``status``: job.status, e.g., "deferred"
      * ``tasktype``: "align" or "tree"
      * ``taskname``: name of aligner or builder
      * ``family``: name of family
      * ``superfamily``: name of superfamily
      * ``is_queued``: True if queued.  This will not be true until after alignment in some cases.
      * ``is_started``: True if job is running.
      * ``is_finished``: True if job is finished (since queue was reset).
      * ``is_failed``: True if job failed due to an error.
      * ``created_at``: ISO format job creation time or "None".
      * ``enqueued_at``: ISO format time of queueing or "None".
      * ``ended_at``: ISO format ending time or "None".
      * ``started_at``: ISO format start time or "None".
      * ``estimated_job_time``: Estimated run time (wallclock) in seconds.
      * ``queue_name``: Name of queue (for future queries)
      * ``queue_position``: position in queue, if queued, or length of queue if not.
      * ``estimated_queue_time``: Estimated wallclock time of preceding jobs, in seconds.
   For now all estimated times are bogus and simply placeholders until timing models are established.

-  Config parameters are settable via environmental variables starting with ``"LORAX_"``.

-  Configuration parameters are now settable by instance as a pyfile.

-  Improved logfile content.

-  Removed ``/config`` target as insecure.

-  Changed configuration from ``config.json`` to a Flask-standard pyfile.  See ``default_settings.py``.

v0.6
~~~~

-  Added ``/trees/<family>/hmmalign_FastTree`` target to chain calculations.

-  Added a polling method in ``test_all.sh`` to poll a URL until >= 0, useful for status polls.

-  Queueing for FastTree calculation via rq added.  Expects a queue named ``"FastTree"``.

v0.5
~~~~

-  Added superfamily targets.

-  Added test_all.sh script to do full testing.

-  Changed "tree" target to ``tree.nwk``.

-  Compute stats on HMM files and return as part of HMM addition.  If hmmstats fails,
   abort with 417 and delete the HMM file.

-  Added /trees/families.json target.

-  More run-time arguments.

-  Renamed /config target as /config.json

-  Returned JSON objects are now reponses of type 'application/json'.

-  Added /log.txt target that returns the current log file.

-  Added click as a dependency, removed ``flaskrun.py``.

-  Moved config.py code to __init__.py.

-  Removed AutoIndex of / directory.

-  Changed HMM from ``POST`` to ``PUT`` for consistency with HTML specs.  Added ``put_HMM.sh`` script.

-  Removed test for <family> naming, anything that passes Path addition will work.

v 0.4
~~~~~
