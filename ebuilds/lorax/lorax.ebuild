EAPI=6

PYTHON_COMPAT=( python3_{4,5,6} )
inherit distutils-r1

DESCRIPTION="web server to speak for the (phylogenetic) trees"
HOMEPAGE="https://github.com/LegumeFederation/${PN}"
SRC_URI="mirror://pypi/${PN:0:1}/${PN}/${P}.tar.gz"

LICENSE="MIT"
SLOT="0"
KEYWORDS="~amd64 ~x86"

RDEPEND="dev-python/Flask-RQ2[${PYTHON_USEDEP}]
		 dev-python/Flask-CLI[${PYTHON_USEDEP}]
         sci-biology/biopython[${PYTHON_USEDEP}]
         dev-python/rq-dashboard[${PYTHON_USEDEP}]"

