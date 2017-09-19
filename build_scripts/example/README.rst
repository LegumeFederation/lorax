Example Build and Deployment
============================
The files in this directory give an example of a fairly typical deployment:

* Directories are to system locations rather than user.
* Build as a non-privileged login user, run as user www.
* Predefined data are copied into the var directory.
* RC scripts are deployed and tested.

You will need sudo permission to do this installation.

To use these scripts, download them to a directory, then inspect and edit them.
Then follow the steps::
    source 0_defs_to_source.sh
    ./1_build_lorax
    ./2_builder_to_user.sh
    ./3_test_rc.sh

Those steps should be done on a development instance, and when correct, run
again on the stage platform.  Then an additional step is required, to be
run on the stage platform, before copying to the production platform::
    ./4_configure_prod_on_stage.sh

Once the production instance is started, the following script may be
used to test it::
    ./5_test_prod.sh
 
