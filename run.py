#!/usr/bin/env python3
import os
from lorax import app

if __name__ == '__main__':
    if 'LORAX_START' in os.environ and os.environ['LORAX_START'] == 'direct':
        print('Direct start of lorax, discouraged for production use.')
        port = int(os.getenv('LORAX_PORT', '58926'))
        host = os.getenv('LORAX_HOST', 'localhost')
        print('Running lorax on http://%s:%d/.  ^C to stop.' %(host, port))
        app.run(host=host,
                port=port)
    else:
        app.run()

