#!/bin/sh

# PROVIDE: lorax

. /etc/rc.subr

name="lorax"
rcvar="set_rcvar"
start_cmd="lorax_start"
stop_cmd="lorax_stop"

load_rc_config $name

command="${LORAX_ROOT}/bin/run_in_lorax_env"
command_args="supervisord"

pidfile="${LORAX_VAR)/run/lorax.pid"
required_files="${LORAX_ROOT}/etc/supervisord.conf ${LORAX_ROOT}/run_lorax.py"
required_dirs="${LORAX_VAR}/var/log"
sig_reload="USR1"
extra_commands="reload status"

status="lorax_status"

lorax_start()
{
 ${venv_dir}/bin/run_in_lorax_env supervisord
}

lorax_stop()
{
 ${venv_dir}/bin/run_in_lorax_env supervisorctl shutdown
}

lorax_status()
{
 ${venv_dir}/bin/run_in_lorax_env supervisorctl status
}

run_rc_command "$1"
