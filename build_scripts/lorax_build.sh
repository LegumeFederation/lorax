#!/bin/bash
# Build configuration system.
set -e # exit on error
error_exit() {
   echo "ERROR--unexpected exit from build script."
}
trap error_exit EXIT
script_name=`basename "${BASH_SOURCE}"`
pkg="${script_name%_build}"
confdir=~/.${pkg}/build
TOP_DOC="""Builds and installs ${pkg} components.

Usage:
        $scriptname COMMAND [COMMAND_OPTIONS]

Commands:
       root - print the root directory.
  make_link - links the ${pkg}_env file to bin_dir for convenience.
  make_dirs - Creates needed directories in ${pkg} root directory.
link_python - Creates python and pip links.
    install - Installs a binary package.
        set - set/print configuration variables.

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
   gmake
   gmake install
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
   gmake -f Makefile${model} CC="${3} -march=native"
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
   gmake
   gmake install
   gmake clean
   popd
   rm -r hmmer-${1}-linux-intel-x86_64
}
install_redis() {
   redis_cflags=`get_value redis_cflags` # -DAF_LOCAL=1
   echo "Installing redis $1 to $2"
   curl -L -o redis-${1}.tar.gz  http://download.redis.io/releases/redis-${1}.tar.gz
   tar xf redis-${1}.tar.gz
   rm redis-${1}.tar.gz
   export CFLAGS=$redis_cflags
   export CC=$3
   export PREFIX=${2}
   pushd redis-${1}
   pushd deps
   gmake lua linenoise jemalloc hiredis
   popd
   gmake
   gmake install
   popd
   rm -r redis-${1}
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
   echo "Creating directories in ${root}."
   mkdir -p ${root}/{bin,build_configuration}
   cp -R ${confdir}/ ${root}/build_configuration
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
elif [ "$1" == "install" ]; then
  shift 1
  INSTALL_DOC="""Installs a binary package.

Usage:
   $scriptname install PACKAGE

Packages:
      python - Python interpreter.
       raxml - RAxML binaries.
       hmmer - HMMer binaries.
       redis - redis binaries.
     
"""
  if [ "$#" -ne 1 ]; then #doc
      trap - EXIT 
      >&2 echo "$INSTALL_DOC"
      exit 1
  fi
  root=`get_root`
  cc=`get_value cc`
  commandlist="python raxml hmmer redis"
  case $commandlist in
    *"$1"*)
       install_$1 `get_value $1` `get_root` `get_value cc`
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
