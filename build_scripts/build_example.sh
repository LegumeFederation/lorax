#
# lorax_tool init configures the following default values, which you may
# override by uncommenting here.  These default values are for a linux
# build and may be different then the values created by lorax_tool's init
# command.
#
# Note that if you are building nginx, some of these configuration values
# are compile-time-only settings which cannot be overridden.
#
#./lorax_tool config directory_version 0.94
#./lorax_tool config root_dir ~/.lorax/`./lorax_tool config directory_version`
#./lorax_tool config var_dir "`./lorax_tool config root_dir`/var"
#./lorax_tool config tmp_dir "`./lorax_tool config var_dir`/tmp"
#./lorax_tool config log_dir "`./lorax_tool config var_dir`/log"
#
# Version numbers of packages.  Setting these to "system" will cause them
# not to be built.
#
#./lorax_tool config python 3.6.2
#./lorax_tool config hmmer 3.1b2
#./lorax_tool config raxml 8.2.11
#./lorax_tool config redis 4.0.1
#./lorax_tool config nginx 1.13.4
#
# The following defaults are platform-specific.  Linux defaults are shown.
#
#./lorax_tool config platform linux
#./lorax_tool config bin_dir ~/bin  # dir in PATH where lorax_env is symlinked
#./lorax_tool config make make
#./lorax_tool config cc gcc
#./lorax_tool config redis_cflags ""
#
# The following defaults are hardware-specific for the RAxML build.
# If you have both hardware and compiler support, you may wish to substitute
# "SSE3" with either "AVX" or "AVX2".  Note that clang on BSD uses the gcc
# model, but mac has its own model.
#
#./lorax_tool config raxml_model .SSE3.PTHREADS.gcc
#./lorax_tool config raxml_binsuffix -PTHREADS-SSE3
#