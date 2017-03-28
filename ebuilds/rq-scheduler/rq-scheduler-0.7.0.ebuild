EAPI=5

PYTHON_COMPAT=( python2_7 python3_{4,5,6} )
inherit distutils-r1

SRC_URI="https://github.com/ui/${PN}/archive/v${PV}.tar.gz -> ${P}.tar.gz"

DESCRIPTION="A light library that adds job scheduling capabilities to RQ (Redis Queue)."

HOMEPAGE="https://github.com/ui/rq-scheduler/"
LICENSE="BSD"

SLOT="0"
KEYWORDS="~amd64 ~x86"

RDEPEND="
         >=dev-python/rq-0.6.0[${PYTHON_USEDEP}]
		 >=dev-python/croniter-0.3.9[${PYTHON_USEDEP}]"
