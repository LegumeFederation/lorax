#
# This file is sourced after lorax_tool configure_pkg does initializations,
# including picking up non-default values from the build configuration for
# root_dir, var_dir, tmp_dir, and log_dir.
#
# The customizations below are the main ones needed to configure a
# server at non-default locations.  Uncomment and edit as needed.
# Values shown are not defaults, but rather example values.
#
#${root}/bin/lorax_env lorax config secret_key mypasswd
#${root}/bin/lorax_env lorax config user www
#${root}/bin/lorax_env lorax config group www
#${root}/bin/lorax_env lorax config data /usr/local/www/data/lorax/${version}
#${root}/bin/lorax_env lorax config userdata /persist/lorax/${version}
#${root}/bin/lorax_env lorax config host 127.0.0.1
#${root}/bin/lorax_env lorax config nginx_server_name mywebsite.org
#${root}/bin/lorax_env lorax config port 58927
#${root}/bin/lorax_env lorax config sentry_dsn https://MYDSN@sentry.io/lorax
#${root}/bin/lorax_env lorax config crashmail_email user@example.com
