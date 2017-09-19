#!/usr/bin/env bash
set -e
error_exit() {
  >&2 echo "ERROR--unexpected exit from ${BASH_SOURCE} script at line:"
  >&2 echo "   $BASH_COMMAND"
  >&2 echo "This failure may have left a running server instance."
  >&2 echo "You should stop it with the command"
  >&2 echo "   \"sudo service lorax stop\"."
}
trap error_exit EXIT
sudo cp /usr/local/www/lorax-${LRX_VERSION}/etc/rc.d/lorax /usr/local/etc/rc.d/lorax
sudo chmod 555 /usr/local/etc/rc.d/lorax
sudo cp /usr/local/www/lorax-${LRX_VERSION}/etc/conf.d/lorax /etc/rc.conf.d/lorax
sudo chmod 555 /usr/local/etc/rc.d/lorax
echo "starting service..."
sudo service lorax start
echo "getting the status"
$LRX_SUDO -u $LRX_USER ${LRX_ROOT}/bin/lorax_env supervisorctl status
echo "Stopping the service..."
sudo service lorax stop
trap - EXIT
