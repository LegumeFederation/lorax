EAPI=5

PYTHON_COMPAT=( python2_7 python3_{4,5,6} )
inherit distutils-r1

SRC_URI="https://github.com/nvie/${PN}/archive/${PV}.tar.gz -> ${P}.tar.gz"

DESCRIPTION="RQ is a simple, lightweight, library for creating background jobs, and processing them."

HOMEPAGE="https://github.com/nvie/rq/"
LICENSE="BSD"

SLOT="0"
KEYWORDS="~amd64 ~x86"

RDEPEND="
		>=dev-python/click-3.0[${PYTHON_USEDEP}]
		>=dev-python/redis-py-2.7.0[${PYTHON_USEDEP}]"

