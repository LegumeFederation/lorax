EAPI=5

PYTHON_COMPAT=( python2_7 python3_{4,5,6} )
inherit distutils-r1

SRC_URI="mirror://pypi/${PN:0:1}/${PN}/${P}.tar.gz"

DESCRIPTION="Command-line integration for Flask."

HOMEPAGE="https://github.com/inveniosoftware/flask-cli"

LICENSE="BSD"

SLOT="0"
KEYWORDS="~amd64 ~x86"
IUSE="test"

RDEPEND="
         >=dev-python/flask-0.10[cli,${PYTHON_USEDEP}]
		 >=dev-python/click-6.0[${PYTHON_USEDEP}]"


