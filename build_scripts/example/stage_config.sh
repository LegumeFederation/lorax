#
# These defs are for use on a staging instance.
#
${root}/bin/lorax_env lorax config user_config_path ~/.lorax-stage
${root}/bin/lorax_env lorax config secret_key $LRX_SECRET_KEY
${root}/bin/lorax_env lorax config rc_user $LRX_USER
${root}/bin/lorax_env lorax config rc_group $LRX_GROUP
${root}/bin/lorax_env lorax config host $LRX_STAGE_IP
${root}/bin/lorax_env lorax config nginx_server_name $LRX_STAGE_HOSTNAME
${root}/bin/lorax_env lorax config sentry_dsn $LRX_SENTRY_DSN
${root}/bin/lorax_env lorax config crashmail_email $LRX_CRASHMAIL_EMAIL
