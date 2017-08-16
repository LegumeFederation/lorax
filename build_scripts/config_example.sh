#!/usr/bin/env bash
#
# Example of lorax configuration. Rename, uncomment, and change to
# appropriate values for your installation.
#
root="`./lorax_build.sh root`"
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
# Installation-specific configurations.  Uncomment and edit as needed.
#
#${root}/bin/lorax_env lorax config secret_key mypasswd
#${root}/bin/lorax_env lorax config user www
#${root}/bin/lorax_env lorax config group www
#${root}/bin/lorax_env lorax config data /path/to/data
#${root}/bin/lorax_env lorax config userdata /path/to/userdata
#${root}/bin/lorax_env lorax config host myhost.example.com
#${root}/bin/lorax_env lorax config port 58927
#${root}/bin/lorax_env lorax config sentry_dsn sentrydsnstring
#${root}/bin/lorax_env lorax config crashmail_email user@example.com
#${root}/bin/lorax_env lorax config nginx_server_name myhost.example.com
#
# Save a copy of the configuration to a time-stamped file.
#
config_filename="config-`date '+%Y-%m-%d-%H-%M'`.txt"
${root}/bin/lorax_env lorax config > ${root}/${config_filename}
#
# Create the configured instance.
#
echo "Creating a configured instance at ${root}."
${root}/bin/lorax_env lorax create_instance
echo "To run the configured instance, issue the command:"
echo "   lorax_env supervisord "
