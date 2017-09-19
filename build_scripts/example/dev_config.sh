#
# These defs are for use on a development instance.
#
${root}/bin/lorax_env lorax config user_config_path ~/.lorax-dev
${root}/bin/lorax_env lorax config secret_key $LRX_SECRET_KEY
${root}/bin/lorax_env lorax config rc_user $LRX_USER
${root}/bin/lorax_env lorax config rc_group $LRX_GROUP
${root}/bin/lorax_env lorax config rc_verbose True
${root}/bin/lorax_env lorax config host $LRX_DEV_IP
${root}/bin/lorax_env lorax config nginx_server_name $LRX_DEV_HOSTNAME
