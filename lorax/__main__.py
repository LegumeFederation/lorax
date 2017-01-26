# -*- coding: utf-8 -*-
'''
lorax -- a server for phylogenetic trees
'''

# This file makes it easier for developers to test in-place via the command
# python3 -m lorax
# from the directory above this one.

from .__init__ import cli
if __name__ == '__main__':
    cli(auto_envvar_prefix='META_IRON')
