Testing
=======
If you defined the lorax host to be something other than localhost, you will
have to define the environmental variable LORAX_HOST to match::

    export LORAX_HOST=MY_HOST_IP

Ditto for the port address.

To test lorax, issue the commands::

    mkdir test_lorax # could be any name, will be deleted later
    cd test_lorax
    /path/to/lorax_env lorax create_test_files
    ./test_targets.sh

If the installation went properly, the last command should finish with
"lorax test completed successfully."

You may also wish to load a full-sized data model to work with.  The
script ``get_big_model.sh`` will do that for you.  The model of 12
legume genomes (against the phytozome 10.2 HMM's) is rather large
at 900 MB of downloads and some 7 GB of data when loaded, so expect
this to take a while (about 30 minutes on a core i7 with SSD).  This
script will define some 18,000 legume gene families.

If you wish to stop lorax after the tests, issue the command::

    /path/to/lorax_env supervisorctl shutdown