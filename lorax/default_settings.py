# -*- coding: utf-8 -*-
'''Configuration variables for lorax.

These definitions may be overridden via a python file pointed to by the environmental variable
LORAX_SETTINGS.
'''
#
# Note that only values in uppercase will be stored in the
# configuration object.
#
class BaseConfig(object):
    TREEBUILDERS = {
        "FastTree": {
          "peptide": ["-nopr", "-log", "peptide.log"],
          "DNA": ["-nt", "-gtr", "-log", "nucleotide.log", "-nopr"]
        },
        "RAxML": {
          "peptide": ["-b", "12345", "-p", "12345", "-N", "10", "-m", "PROTGAMMABLOSUM62"],
          "DNA": ["-d"]
        }
    }
    ALIGNERS = {
        'hmmalign': ["--trim", "--informat", "FASTA"] # command-line arguments
    }
    #
    # Usually these paths should be absolute, but for testing these
    # are relative to the PWD of the lorax process.
    #
    PATHS = {
        'log': 'logs/',
        'data': 'data/',
        'mode': 0o755
    }
    #
    DEBUG = False
    #
    # The following variables may be overridden by environmental variables
    # prefaced with "LORAX_".
    #
    THREADS = 0  # Number of threads to use in alignment and tree-building, 0 = use all.
    DEBUG = False
    HOST = 'localhost'
    PORT = 58927
    TREE_QUEUE = 'treebuilding'
    ALIGNMENT_QUEUE = 'alignment'
    ENVVARS=['THREADS', 'DEBUG', 'HOST', 'PORT', 'TREE_QUEUE', 'ALIGNMENT_QUEUE']


class DevelopmentConfig(BaseConfig):
    DEBUG = True

class ProductionConfig(BaseConfig):
    DEBUG = False