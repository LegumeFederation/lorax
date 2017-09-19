#
# These defs are for a production instance.
#
${root}/bin/lorax_env lorax config user_config_path ~/.lorax-prod
${root}/bin/lorax_env lorax config secret_key $LRX_SECRET_KEY
${root}/bin/lorax_env lorax config rc_user $LRX_USER
${root}/bin/lorax_env lorax config rc_group $LRX_GROUP
${root}/bin/lorax_env lorax config host $LRX_PROD_IP
${root}/bin/lorax_env lorax config nginx_server_name $LRX_PROD_HOSTNAME
${root}/bin/lorax_env lorax config sentry_dsn $LRX_SENTRY_DSN
${root}/bin/lorax_env lorax config crashmail_email $LRX_CRASHMAIL_EMAIL
