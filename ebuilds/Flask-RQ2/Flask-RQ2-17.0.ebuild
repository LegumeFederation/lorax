EAPI=5

PYTHON_COMPAT=( python2_7 python3_{4,5,6} )
inherit distutils-r1

SRC_URI="https://github.com/jezdez/flask-rq2/archive/${PV}.tar.gz -> ${P}.tar.gz"

DESCRIPTION="A Flask extension for RQ (Redis Queue)."

HOMEPAGE="https://github.com/ui/flask-rq2/"
LICENSE="MIT"

SLOT="0"
KEYWORDS="~amd64 ~x86"

RDEPEND="
         <dev-python/rq-0.7.0[${PYTHON_USEDEP}]
		 >=dev-python/rq-scheduler-0.6.1[${PYTHON_USEDEP}]
		 >=dev-python/flask-0.10"
