#!/bin/bash
#
# This file is meant to be sourced for testing.
# The definitions are the defaults for lorax.
# These environmental variables must be defined
# before the test script may be used.
#
export LORAX_HOST="127.0.0.1"
export LORAX_PORT=58927
env | grep "LORAX"
