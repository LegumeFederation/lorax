EAPI=6

PYTHON_COMPAT=( python2_7 python3_{4,5,6} )
inherit distutils-r1

SRC_URI="https://github.com/eoranged/${PN}/archive/${PV}.tar.gz -> ${P}.tar.gz"
DESCRIPTION="Flask-based web front-end to monitor RQ queues in realtime."
HOMEPAGE="https://github.com/eoranged/rq-dashboard/"
LICENSE="BSD"

SLOT="0"
KEYWORDS="~amd64 ~x86"
RDEPEND="
		>=dev-python/rq-0.3.8[${PYTHON_USEDEP}]
		dev-python/flask[${PYTHON_USEDEP}]
		dev-python/arrow"

