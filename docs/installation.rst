.. Installation instructions

Planning Your Installation
==========================
Installation of lorax under linux can be done either via a *direct install*
(using either build scripts we supply or using your distribution's package
manager) or an *indirect install* via Anaconda Python and packages in the
bioconda channel.  Which path you choose depends on your OS and general
preferences. If you are installing on BSD, direct installs are your only
choice as Anaconda Python is not available for this platform.  If you are
installing on a Mac, you will need a number of prerequisites that are most
easily satisfied via Anaconda Python packages.  If you are installing on linux,
Anaconda Python will get you up and running more quickly while direct installs
are more heavily tested and will give you more control of the installation.
This is especially important if you anticipate using RAxML heavily
and you wish to take advantage of AVX/AVX2 hardware.

MacOS Installation
------------------
``lorax`` was tested under MacOS Sierra (10.12.6).  The minimum OS version for
proper function of Anaconda Python is MacOS 10.12.3.

Installation of ``lorax`` under MacOS requires use of ``git``. To test if you
have ``git`` installed, open a terminal window ``(under Applications -> Utilities)``
and issue the command::

        git --version

If this produces an error, the easiest way to install git is by installing the
XCode command-line tools, part of the XCode utilities, which are available for
free (but large) download from the App Store.

Besides the XCode tools, you will also need to install gcc (because the
current Mac clang does not include OpenMP) as well as the PCRE and OpenSSL
libraries.  The tested configuration was with PCRE-8.40 and OpenSSL-1.10.f.
Both libraries were configured with ``CC=clang`` and installed to ``/usr/local``.







