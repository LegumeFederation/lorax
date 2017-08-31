#!/bin/bash
# Build configuration system.
set -e # exit on error
error_exit() {
   echo "ERROR--unexpected exit from ${BASH_SOURCE} script at line:"
   echo "   $BASH_COMMAND"
}
trap error_exit EXIT
script_name=`basename "${BASH_SOURCE}"`
pkg="${script_name%_tool.sh}"
if [ -z "$BUILD_CONFIG_DIR" ]; then
   confdir=~/.${pkg}/config
else
   confdir="$LORAX_BUILD_CONFIG_DIR"
fi
if [ -z "$TEST_DIR" ]; then
   testdir=~/.${pkg}/test
else
   testdir="$TEST_DIR"
fi
version="0.94"
platform=`uname`
TOP_DOC="""Builds and installs ${pkg} components.

Usage:
        $script_name COMMAND [COMMAND_OPTIONS]

Commands:
         config - Set/print configuration variables.
       download - Downloads self and other scripts.
           init - Set system-specific defaults for the build.
        install - Install one or all binary packages.
       link_env - Link the ${pkg}_env file to bin_dir for convenience.
    link_python - Create python and pip links.
      make_dirs - Create needed directories in ${pkg} root directory.
    pip_install - Do pip installations.
           pypi - Get latest pypi version.
          shell - Run a shell in installation environment.
        testify - Run tests.
        version - Get installed ${pkg} version.

Variables (accessed by \"config\" command):
           root_dir - Path to the root directory.
  directory_version - ${pkg} version for directory naming purposes.
            bin_dir - A writable directory in PATH for script links.
             python - The python version string.
                 cc - The C compiler to use.
              raxml - The raxml version string.
        raxml_model - The RAxML compiler model suffix (e.g., \".SSE3.PTHREADS.gcc\").
    raxml_binsuffix - The suffix to the binary produced (e.g., \"-PTHREADS-SSE3\").
              hmmer - The HMMer version string.
              redis - The redis version string.
       redis_cflags - CFLAGS for use in building redis.
              nginx - The nginx version string.
            version - Installed version.

Environmental variables:
       BUILD_CONFIG_DIR - The location of the build, configuration, and test
                          files.  If not set, these go in ~/.${pkg}/config.
               TEST_DIR - The location of the test directory.  If not set,
                          they go in ~/.${pkg}/test.

Platforms supported:
   uname must return one of three values, \"Linux\", \"Darwin\",
   or \"*BSD\"; other values are not recognized.  This platform
   is \"$platform\".
"""
#
# Helper functions begin here.
#
set_value() {
   if [ ! -e ${confdir} ]; then
      >&2 echo "Making ${confdir} directory."
      mkdir -p ${confdir}
   fi
   echo "$2" > ${confdir}/${1}
}
get_value() {
  if [ -e ${confdir}/${1} ]; then
    cat ${confdir}/${1}
  else
    trap - EXIT
    >&2 echo "ERROR--value for $1 variable not found."
    exit 1
  fi
}
#
# Installation functions.
#
install_python() {
   echo "Installing Python $1 to ${2}."
   curl -L -o Python-${1}.tar.gz  https://www.python.org/ftp/python/${1}/Python-${1}.tar.xz
   tar xf Python-${1}.tar.gz
   rm Python-${1}.tar.gz
   pushd Python-${1}
   ./configure --prefix=${2} CC=${3}
   ${4} install
   popd
   rm -r Python-${1}
}
install_raxml() {
   model=`get_value raxml_model`
   binsuffix=`get_value raxml_binsuffix`
   echo "Installing RAxML version $1 to $2 using ${model} model."
   curl -L -o raxml_v${1}.tar.gz https://github.com/stamatak/standard-RAxML/archive/v${1}.tar.gz
   tar xf raxml_v${1}.tar.gz 
   rm raxml_v${1}.tar.gz 
   pushd standard-RAxML-${1}
   ${4} -f Makefile${model} CC="${3} -march=native"
   cp raxmlHPC${binsuffix} ${2}/bin/raxmlHPC
   popd
   rm -r standard-RAxML-${1}
}
install_hmmer() {
   echo "Installing HMMer $1 to ${2}."
   curl -L -o hmmer-${1}-linux-intel-x86_64.tar.gz http://eddylab.org/software/hmmer3/${1}/hmmer-${1}-linux-intel-x86_64.tar.gz
   tar xf hmmer-${1}-linux-intel-x86_64.tar.gz 
   rm hmmer-${1}-linux-intel-x86_64.tar.gz 
   pushd hmmer-${1}-linux-intel-x86_64/
   ./configure --prefix=${2} CC=$3 CFLAGS='-O3 -march=native'
   ${4}
   ${4} install
   popd
   rm -r hmmer-${1}-linux-intel-x86_64
}
install_redis() {
   redis_cflags=`get_value redis_cflags` # -DAF_LOCAL=1
   echo "Installing redis $1 to ${2}."
   curl -L -o redis-${1}.tar.gz  http://download.redis.io/releases/redis-${1}.tar.gz
   tar xf redis-${1}.tar.gz
   rm redis-${1}.tar.gz
   export CFLAGS=$redis_cflags
   export CC=$3
   export PREFIX=${2}
   pushd redis-${1}
   pushd deps
   ${4} lua linenoise jemalloc hiredis
   popd
   ${4} install
   popd
   rm -r redis-${1}
}
install_nginx() {
   var=`get_value var_dir`
   tmp=`get_value tmp_dir`
   log=`get_value log_dir`
   echo "Installing nginx $1 to ${2}."
   curl -L -o nginx-${1}.tar.gz http://nginx.org/download/nginx-${1}.tar.gz
   tar xf nginx-${1}.tar.gz
   rm nginx-${1}.tar.gz
   mkdir -p ${2}/etc/nginx
   pushd nginx-${1}
   ./configure --prefix=${2} \
   --with-threads \
   --with-stream \
   --with-stream=dynamic \
   --with-pcre \
   --with-cc=${3} \
   --with-http_ssl_module \
   --with-http_v2_module \
   --with-http_auth_request_module \
   --with-http_addition_module \
   --with-http_gzip_static_module \
   --with-http_realip_module \
   --sbin-path=bin \
   --modules-path=${root}/lib/nginx/modules \
   --conf-path=${root}/etc/nginx/nginx.conf \
   --error-log-path=${log}/nginx/error.log \
   --http-log-path=${log}/nginx/access.log \
   --pid-path=${var}/run/nginx/nginx.pid \
   --lock-path=${var}/run/nginx/nginx.lock \
   --http-fastcgi-temp-path=${tmp}/nginx/fastcgi \
   --http-client-body-temp-path=${tmp}/nginx/client \
   --http-proxy-temp-path=${tmp}/nginx/proxy \
   --http-uwsgi-temp-path=${tmp}/nginx/uwsgi \
   --http-scgi-temp-path=${tmp}/nginx/scgi
   ${4} install
   rm -f ${root}/etc/nginx/* # remove generated etc files
   rm -rf ${root}/html # and html
   popd
   rm -r nginx-${1}
}
#
# Command functions begin here.
#
config() {
  CONFIG_DOC="""Sets/displays key/value pairs for the $pkg build system.

Usage:
   $scriptname set KEY [VALUE]

Arguments:
   if KEY is \"all\", all values will be set.
   If VALUE is present, the value will be set.
   If VALUE is absent, the current value will be displayed.
"""
  if [ "$#" -eq 0 ]; then #doc
      trap - EXIT
      >&2 echo "$CONFIG_DOC"
      exit 1
    elif [ "$#" -eq 1 ]; then # get
      if [ "$1" == "all" ]; then
        echo "Build configuration values for ${pkg}."
        echo "These values are stored in ${confdir}."
        echo -e "       key         \t       value"
        echo -e "-------------------\t------------------"
        for key in `ls ${confdir}`; do
          value=`get_value ${key}`
        printf '%-20s\t%s\n' ${key} ${value}
      done
    elif [ -e ${confdir}/${1} ]; then
      echo `get_value $1`
    else
      trap - EXIT
      >&2 echo "${1} has not been set."
      exit 1
    fi
  elif [ "$#" -eq 2 ]; then # set
    set_value $1 $2
  else
    trap - EXIT
    >&2 echo "$CONFIG_DOC"
    >&2 echo "ERROR--too many arguments (${#})."
    exit 1
  fi
}
download() {
DOWNLOAD_DOC="""Gets/updates build/configuration scripts for ${pkg}.

Options:
       -n Do not check for self-updates.
"""
   rawsite="https://raw.githubusercontent.com/LegumeFederation/${pkg}/master/build_scripts"
   updates=0
   if [ "$1" == "-n" ]; then
      echo "Not checking for self-updates."
   else
      printf "Checking for self-update..."
      curl -L -s -o ${pkg}_tool.sh.new ${rawsite}/${pkg}_tool.sh
      chmod 755 ${pkg}_tool.sh.new
      if cmp -s ${pkg}_tool.sh ${pkg}_tool.sh.new ; then
         rm ${pkg}_tool.sh.new
         echo "not needed."
      else
         echo "this file was updated.  Please rebuild everything."
         mv ${pkg}_tool.sh.new ${pkg}_tool.sh
         trap - EXIT
         exit 0
      fi
   fi
   # Check for updates to other files, in an edit-aware way.
   curl -L -s -o build_example.sh.new ${rawsite}/build_example.sh
   curl -L -s -o config_example.sh.new ${rawsite}/config_example.sh
   for f in build_example.sh config_example.sh; do
      if [ -e ${f} ]; then
         if cmp -s ${f} ${f}.new; then
            rm ${f}.new # no change
         else
           updates=1
           echo "$f has been updated."
           mv ${f} ${f}.old
           chmod 755 ${f}.new
           mv ${f}.new ${f}
         fi
      else
         updates=1
         chmod 755 ${f}.new
         mv ${f}.new ${f}
      fi
   done
   # If my_ files have changed versus example, warn but don't replace.
   for f in build_example.sh config_example.sh ; do
     my_f="my_${f/_example/}"
     if [ -e ${f}.old ]; then
        cmp_f="${f}.old" # look for changes against old file
     else
        cmp_f="$f"       # look for changes against current file
     fi
     if [ -e ${my_f} ]; then
       if cmp -s ${cmp_f} ${my_f}; then
          if [ -e ${f}.old ]; then
            # No changes from old example, copy current file to my_f.
            cp ${f} ${my_f}
          fi
       else
          if [ -e ${f}.old ]; then
            mv ${f}.old ${f}.save
            echo "Example file on which your edited ${my_f} was based has changed."
            echo "Review the following differences between ${f} and ${f}.save"
            echo "and apply them, if necessary to ${my_f}:"
            set +e
            diff -u ${f}.save ${f}
          else
            echo "${my_f} differs from the (unchanged) example file."
          fi
       fi
       else
       cp ${f} ${my_f}
     fi
   done
   rm -f $build_example.sh.old config_example.sh.old
   pypi=`pypi`
   version=`version`
   if [ "version" == "${pkg} build not configured" ]; then
      echo "Next run \"./my_build.sh\" to build and configure lorax."
   elif [ "$updates" -eq 1 ]; then
      echo "Update build/configuration files found, please re-build using"
      echo "    ./my_build.sh"
   elif [ "$pypi" == "$version" ]; then
      echo "The latest version of ${pkg} (${pypi}) is installed, no need for updates."
   else
      echo "You can update from installed version (${version}) to latest (${pypi}) with"
      echo "   ./${pkg}_tool.sh pip_install"
   fi
}
init() {
   #
   #  Initialize build parameters.
   #
   set_value root_dir ${confdir}/${version}
   set_value directory_version ${version}
   set_value var_dir "`get_value root_dir`/var"
   set_value tmp_dir "`get_value var_dir`/tmp"
   set_value log_dir "`get_value var_dir`/log"
   set_value python 3.6.2
   set_value hmmer 3.1b2
   set_value raxml 8.2.11
   set_value redis 4.0.1
   set_value nginx 1.13.4
   if [[ "$platform" == "Linux" ]]; then
      echo "Platform is linux."
      set_value bin_dir ~/bin
      set_value platform linux
      set_value make make
      set_value cc gcc
      set_value redis_cflags ""
      set_value raxml_model .SSE3.PTHREADS.gcc
      set_value raxml_binsuffix -PTHREADS-SSE3
   elif [[ "$platform" == *"BSD" ]]; then
      echo "Platform is bsd."
      set_value platform bsd
      set_value bin_dir ~/bin
      set_value make gmake
      set_value cc clang
      set_value raxml_model .SSE3.PTHREADS.gcc
      set_value raxml_binsuffix -PTHREADS-SSE3
      set_value redis_cflags -DAF_LOCAL=AF_UNIX
   elif [[ "$platform" == "Darwin" ]]; then
      echo "Platform is mac.  You must have XCODE installed."
      set_value platform mac
      set_value bin_dir /usr/local/bin
      set_value make make
      set_value cc clang
      set_value raxml_model .SSE3.PTHREADS.mac
      set_value raxml_binsuffix -PTHREADS-SSE3
      set_value redis_cflags ""
   else
      echo "WARNING--Unknown platform ${platform}, pretending it is linux."
      set_value platform linux
      set_value bin_dir ~/bin
      set_value make make
      set_value cc gcc
      set_value redis_cflags ""
      set_value raxml_model .AVX2.PTHREADS.gcc
      set_value raxml_binsuffix -PTHREADS-AVX2
   fi
}
install() {
  INSTALL_DOC="""Installs a binary package.

Usage:
   $scriptname install PACKAGE

Packages:
      python - Python interpreter.
       raxml - RAxML treebuilder.
       hmmer - HMMer alignment.
       redis - redis database.
       nginx - nginx web proxy server.
"""
  root=`get_value root_dir`
  cc=`get_value cc`
  make=`get_value make`
  commandlist="python raxml hmmer redis nginx"
  if [ "$#" -eq 0 ]; then # install the whole list
      for package in $commandlist; do
         version=`get_value $package`
         if [ "$version" == "system" ]; then
           echo "System version of $package will be used, skipping build."
         else
           install_$package ${version} ${root} ${cc} ${make}
         fi
      done
  else
     case $commandlist in
        *"$1"*)
           install_$1 `get_value $1` ${root} ${cc} ${make}
        ;;
        $commandlist)
          trap - EXIT
          >&2 echo  "ERROR--unrecognized package $1"
          exit 1
        ;;
      esac
   fi
}
link_env() {
   #
   # Link the _env script to $bin_dir.
   #
   root=`get_value root_dir`
   bin_dir=`get_value bin_dir`
   echo "linking ${pkg}_env to ${bin_dir}"
   if [ ! -e ${bin_dir} ]; then
     echo "Creating binary directory at ${bin_dir}"
     echo "Make sure it is on your PATH."
     mkdir ${bin_dir}
   elif [ -h ${bin_dir}/${pkg}_env ]; then
     rm -f ${bin_dir}/${pkg}_env
   fi
   ln -s  ${root}/bin/${pkg}_env ${bin_dir}
}
make_dirs() {
   #
   # Make required installation directories.
   #
   root=`get_value root_dir`
   var=`get_value var_dir`
   tmp=`get_value tmp_dir`
   log=`get_value log_dir`
   echo "Creating directories in ${root}."
   mkdir -p ${root}/{bin,configuration}
   cp -R ${confdir}/ ${root}/configuration
   mkdir -p ${root}/etc/nginx
   mkdir -p ${var}/run/nginx
   mkdir -p ${tmp}/nginx
   mkdir -p ${log}/nginx
}
link_python() {
   root=`get_value root_dir`
   root_bin="${root}/bin"
   python_version=`get_value python`
   cd $root_bin
   if [ ! -e python ]; then
      echo "creating python ${python_version} link in ${root_bin}."
      ln -s python${python_version%.*} python
   fi
   if [ ! -e pip_install ]; then
      echo "creating pip link in ${root_bin}."
      ln -s pip${python_version%%.*} pip
   fi
}
pip_install() {
   #
   # Do pip installations for package.
   #
   root="`get_value root_dir`"
   if [[ ":$PATH:" != *"${root}:"* ]]; then
      export PATH="${root}/bin:${PATH}"
   fi
   cd $root # src/ directory is left behind by git
   pip install -U setuptools
   pip install -e 'git+https://github.com/LegumeFederation/supervisor.git@4.0.0#egg=supervisor==4.0.0'
   pip install -U ${pkg}
   pkg_env_path="${root}/bin/${pkg}_env"
   pkg_version="`${pkg_env_path} ${pkg} config version`"
   set_value version $pkg_version
   echo "${pkg} version $pkg_version is now installed."
}
pypi() {
  #
  # Get the current pypi package version.
  #
  set +e
  trap - EXIT
  #
  # The piped function below does version sorting using only awk.
  #
  simple_url="https://pypi.python.org/simple/${pkg}"
  latest=`curl -L -s $simple_url |\
          grep tar.gz |\
          sed -e 's/.*lorax-//g' -e 's#.tar.gz</a><br/>##g'|\
          awk -F. '{ printf("%03d%03d%03d\n", $1, $2, $3); }'|\
          sort -g |\
          awk '{printf("%d.%d.%d\n", substr($0,0,3),substr($0,4,3),substr($0,7,3))}'|\
          tail -1`
   if [ "$?" -eq 0 ]; then
     echo "$latest"
   else
     echo "Unable to determine latest pypi version".
     exit 1
   fi
}
shell() {
   #
   # Execute in build environment.
   #
   root="`get_value root_dir`"
   export PATH="${root}/bin:${PATH}"
   trap - EXIT
   set +e
   old_prompt="$PS1"
   pushd $root 2&>/dev/null
   echo "Executing commands in ${root} with ${root}/bin in path, control-D to exit."
   export PS1="${script_name}> "
   bash
   popd 2&>/dev/null
   export PS1="$old_prompt"
}
testify() {
   TEST_DOC="""You are about to run a short test of the lorax installation
in the ${testdir} directory.
Testing should take about 2 minutes on modest hardware.
Interrupt this script if you do not wish to test at this time.
"""
   set +e
   if [ "$1" != "-y" ]; then
      echo "$TEST_DOC"
      read -p "Do you want to continue? <(y)> " response
      if [ ! -z "$response" ]; then
         if [ "$response" != "y" ]; then
            exit 1
         fi
      fi
   fi
   set -e
   # Run lorax.
   root="`./lorax_build.sh set root_dir`"
   echo "Running lorax processes."
   ${root}/bin/lorax_env supervisord
   # Wait until nothing is STARTING.
   while ${root}/bin/lorax_env supervisorctl status | grep STARTING >/dev/null; do sleep 5; done
   # Print status.
   ${root}/bin/lorax_env supervisorctl status
   # Create the test directory and cd to it.
   mkdir -p ${testdir}
   pushd ${testdir}
   echo "Getting a set of test files in the ${test_dir} directory."
   ${root}/bin/lorax_env lorax create_test_files --force
   echo "Running test of lorax server."
   ./test_targets.sh
   echo ""
   popd
   # Clean up.  Note that lorax process doesn't stop properly from
   # shutdown alone across all platforms.
   echo "Stopping lorax processes."
   ${root}/bin/lorax_env supervisorctl stop lorax alignment treebuilding nginx
   ${root}/bin/lorax_env supervisorctl shutdown
   echo "Tests completed successfully."
}
version() {
  #
  # Get installed version.
  #
   set +e
   trap - EXIT
   if [ -e ${confdir}/root_dir ]; then
    root=`cat ${confdir}/root_dir`
      pkg_env_path="${root}/bin/${pkg}_env"
      if [ -e $pkg_env_path ]; then
         echo "`${pkg_env_path} ${pkg} config version`"
      else
         >&2 echo "${pkg} package not installed"
         exit 0
      fi
  else
    >&2 echo "${pkg} build not configured"
    exit 0
   fi
}
#
# Command-line interpreter.
#
if [ "$#" -eq 0 ]; then
   trap - EXIT
   >&2 echo "$TOP_DOC"
   exit 1
fi
command="$1"
shift 1
case $command in
"config")
  config $@
  ;;
"download")
  download $@
  ;;
"init")
   init $@
   ;;
"install")
  install $@
  ;;
"link_env")
   link_env $@
   ;;
"make_dirs")
   make_dirs $@
   ;;
"link_python")
   link_python $@
   ;;
"pip_install")
   pip_install $@
   ;;
"pypi")
  pypi $@
  ;;
"shell")
   shell $@
   ;;
"testify")
   testify $@
   ;;
"version")
   version $@
   ;;
*)
  trap - EXIT
  >&2 echo "ERROR--command $command not recognized."
  exit 1
  ;;
esac
trap - EXIT
exit 0
