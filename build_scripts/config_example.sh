#!/usr/bin/env bash
DOC="""
#
#  This script configures lorax and creates an instance ready to run
#  on localhost at the default lorax port. You should interrupt and edit this
#  script if one or more of the following is true:
#     * you wish to use a non-default path for DATA or USERDATA
#     * you wish to deploy lorax at a real IP address or non-default port
#     * you wish to enable monitoring services (crashmail, sentry)
#
"""
echo "$DOC"
sleep 2
set -e # exit on errors
error_exit() {
   echo "ERROR--unexpected exit from configuration script at line:"
   echo "   $BASH_COMMAND"
}
trap error_exit EXIT
#
root="`./lorax_build.sh root`"
version="`./lorax_build.sh set directory_version`"
var_dir="`./lorax_build.sh set var_dir`"
log_dir="`./lorax_build.sh set log_dir`"
tmp_dir="`./lorax_build.sh set tmp_dir`"
#
if [ "$var_dir" != "${root}/var" ]; then
   echo "Configuring non-default var directory ${var_dir}."
   ${root}/bin/lorax_env lorax config var $var_dir
fi
if [ "$log_dir" != "${var_dir}/log" ]; then
   echo "Configuring non-default log directory ${log_dir}."
   ${root}/bin/lorax_env lorax config log $log_dir
fi
if [ "$tmp_dir" != "${var_dir}/tmp" ]; then
   echo "Configuring non-default log directory ${tmp_dir}."
   ${root}/bin/lorax_env lorax config tmp $tmp_dir
fi
#
# Installation-specific configurations with some interesting non-default
# values.  Uncomment and edit as needed.
#
#${root}/bin/lorax_env lorax config secret_key mypasswd
#${root}/bin/lorax_env lorax config user www
#${root}/bin/lorax_env lorax config group www
#${root}/bin/lorax_env lorax config data /usr/local/www/data/lorax/${version}
#${root}/bin/lorax_env lorax config userdata /persist/lorax/${version}
#${root}/bin/lorax_env lorax config host 127.0.0.1
#${root}/bin/lorax_env lorax config server_name localhost
#${root}/bin/lorax_env lorax config port 58927
#${root}/bin/lorax_env lorax config sentry_dsn https://MYDSN@sentry.io/lorax
#${root}/bin/lorax_env lorax config crashmail_email user@example.com
#
# Save a copy of the configuration to a time-stamped file.
#
config_filename="config-`date '+%Y-%m-%d-%H-%M'`.txt"
${root}/bin/lorax_env lorax config > ${root}/${config_filename}
#
# Create the configured instance.
#
echo "Creating a configured instance at ${root}."
${root}/bin/lorax_env lorax create_instance --force
#
# Set the password for restricted parts of the site.
#
passwd="`${root}/bin/lorax_env lorax config secret_key`"
echo "Setting the http password to \"${passwd}\";"
echo "please write it down, because you will need it to access some services."
${root}/bin/lorax_env lorax set_htpasswd --force
echo "To run the configured instance, issue the command:"
echo "   lorax_env supervisord "
echo "To run the test suite, issue the command:"
echo "   ./run_lorax_tests.sh"
trap - EXIT
exit 0
