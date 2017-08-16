#!/bin/bash
# Build configuration system.
set -e # exit on error
error_exit() {
   echo "ERROR--unexpected exit from ${BASH_SOURCE} script at line:"
   echo "   $BASH_COMMAND"
}
trap error_exit EXIT
script_name=`basename "${BASH_SOURCE}"`
pkg="${script_name%_build.sh}"
confdir=~/.${pkg}/build
TOP_DOC="""Builds and installs ${pkg} components.

Usage:
        $scriptname COMMAND [COMMAND_OPTIONS]

Commands:
       root - Print the root directory.
  make_link - Link the ${pkg}_env file to bin_dir for convenience.
  make_dirs - Create needed directories in ${pkg} root directory.
link_python - Create python and pip links.
    install - Install a binary package.
        pip - Do pip installations.
       pypi - Get latest pypi version.
        set - Set/print configuration variables.
      shell - Run a shell in installation environment.
    version - Get installed lorax version.

Variables (accessed by set command):
            top_dir - directory above the root directory.
  directory_version - ${pkg} version for directory naming purposes.
            bin_dir - A writable directory in PATH for script links.
             python - The python version string.
                 cc - The C compiler to use.
              raxml - The raxml version string.
        raxml_model - The RAxML compiler model suffix (e.g., ".SSE3.PTHREADS.gcc").
    raxml_binsuffix - The suffix to the binary produced (e.g., "-PTHREADS-SSE3").
              hmmer - The HMMer version string.
              redis - The redis version string.
       redis_cflags - CFLAGS for use in building redis.
              nginx - The nginx version string.
"""
# Helper functions.
get_value() {
  if [ -e ${confdir}/${1} ]; then
    cat ${confdir}/${1}
  else
    trap - EXIT
    >&2 echo "ERROR--value for $1 variable not found."
    exit 1
  fi
}
get_root() {
  top_dir=`get_value top_dir`
  directory_version=`get_value directory_version`
  echo "${top_dir}/${pkg}-${directory_version}"
}
# Installation functions.
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
# Command-line interpreter.
if [ "$#" -eq 0 ]; then
   trap - EXIT
   >&2 echo "$TOP_DOC"
   exit 1
elif [ "$1" == "root" ]; then
   get_root
elif [ "$1" == "make_link" ]; then
   root=`get_root`
   bin_dir=`get_value bin_dir`
   echo "linking ${pkg}_env to ${bin_dir}"
   if [ ! -e ${bin_dir} ]; then
     echo "Creating binary directory at ${bin_dir}"
     echo "Make sure it is on your PATH."
     mkdir ${bin_dir}
   elif [ -e ${bin_dir}/${pkg}_env ]; then
     rm ${bin_dir}/${pkg}_env
   fi
   ln -s  ${root}/bin/${pkg}_env ${bin_dir}
elif [ "$1" == "make_dirs" ]; then
   root=`get_root`
   var=`get_value var_dir`
   tmp=`get_value tmp_dir`
   log=`get_value log_dir`
   echo "Creating directories in ${root}."
   mkdir -p ${root}/{bin,build_configuration}
   cp -R ${confdir}/ ${root}/build_configuration
   mkdir -p ${root}/etc/nginx
   mkdir -p ${var}/run/nginx
   mkdir -p ${tmp}/nginx
   mkdir -p ${log}/nginx
elif [ "$1" == "link_python" ]; then
   root=`get_root`
   root_bin="${root}/bin"
   python_version=`get_value python`
   cd $root_bin
   if [ ! -e python ]; then
      echo "creating python ${python_version} link in ${root_bin}."
      ln -s python${python_version%.*} python
   fi
   if [ ! -e pip ]; then
      echo "creating pip link in ${root_bin}."
      ln -s pip${python_version%%.*} pip
   fi
elif [ "$1" == "pip" ]; then
   root="`get_root`"
   export PATH="${root}/bin:${PATH}"
   cd $root # src/ directory is left behind by git
   pip install -U setuptools
   pip install -e 'git+https://github.com/LegumeFederation/supervisor.git@4.0.0#egg=supervisor==4.0.0'
   pip install -U lorax
elif [ "$1" == "shell" ]; then
   root="`get_root`"
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
elif [ "$1" == "version" ]; then
   set +e
   trap - EXIT
   version="Not installed"
   root=`get_root`
   if [ "$?" -eq 0 ]; then
      lorax_env_path="${root}/bin/lorax_env"
      if [ -e $lorax_env_path ]; then
         version=`${lorax_env_path} lorax config version`
         if [ "$?" -eq 0 ]; then
            echo "$version"
         else
            echo "${pkg} is not runnable"
            exit 1
         fi
      else
         echo "${pkg} is not installed"
         exit 1
      fi
   else
      echo "${pkg} build has not been configured"
      exit 1
   fi
elif [ "$1" == "pypi" ]; then
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
elif [ "$1" == "install" ]; then
  shift 1
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
  if [ "$#" -ne 1 ]; then #doc
      trap - EXIT 
      >&2 echo "$INSTALL_DOC"
      exit 1
  fi
  root=`get_root`
  cc=`get_value cc`
  commandlist="python raxml hmmer redis nginx"
  case $commandlist in
    *"$1"*)
       install_$1 `get_value $1` `get_root` `get_value cc` `get_value make`
       ;;
    $commandlist)
       trap - EXIT
       >&2 echo  "ERROR--unrecognized package $1"
       exit 1
       ;;
  esac
elif [ "$1" == "set" ]; then
  shift 1
  SET_DOC="""Sets/displays key/value pairs for the $pkg build system.

Usage:
   $scriptname set KEY [VALUE]

   if KEY is "all", all values will be set.
   
   If VALUE is present, the value will be set.
   If VALUE is absent, the current value will be displayed.
"""
  if [ "$#" -eq 0 ]; then #doc
      trap - EXIT 
      >&2 echo "$SET_DOC"
      exit 1
    elif [ "$#" -eq 1 ]; then # get
      if [ "$1" == "all" ]; then
        echo "Build configuration values for ${pkg}."
        echo "These values are stored in ${confdir}."
        echo -e "       key         \t       value"
        echo -e "-------------------\t------------------"
        for key in `ls ${confdir}`; do
          value=`cat ${confdir}/${key}`
        printf '%-20s\t%s\n' ${key} ${value} 
      done
    elif [ -e ${confdir}/${1} ]; then
      cat ${confdir}/${1}
    else
      trap - EXIT
      >&2 echo "${1} has not been set."
      exit 1
    fi
  elif [ "$#" -eq 2 ]; then # set
    if [ ! -e ${confdir} ]; then
      trap - EXIT
      >&2 echo "Making ${confdir} directory."
      mkdir -p ${confdir}
    fi
    echo "$2" > ${confdir}/${1}
  else
    trap - EXIT
    >&2 echo "$SET_DOC"
    >&2 echo "ERROR--too many arguments (${#})."
    exit 1
  fi
else
  trap - EXIT
  >&2 echo "ERROR--command $1 not recognized."
  exit 1
fi
trap - EXIT
exit 0
