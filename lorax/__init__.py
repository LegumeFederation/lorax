# -*- coding: utf-8 -*-
'''
lorax --

A web service process designed to calculate and serve up phylogenetic trees, including:
    * Setting of tree calculation parameters and metadata
    * Storing input sequences
    * Phylogenetic tree calculation
    * Serving up results

'''
#
# standard library imports
#
import os
import sys
import logging
import subprocess
from pathlib import Path # python 3.4 or later
import json
import io
from datetime import datetime
#
# third-party imports
#
from flask import Flask, request, redirect, abort
from flask_autoindex import AutoIndex
from Bio import SeqIO
#
# local imports
#
from .config import *
from .flaskrun import flaskrun
#
# Global variables
#
STARTTIME = datetime.now()
#
# global logger object
#
logger = logging.getLogger(PROGRAM_NAME)
#
# Class definitions begin here
#
class CleanInfoFormatter(logging.Formatter):
    '''A logging formatter for stderr usage
    '''
    def __init__(self, fmt = '%(levelname)s: %(message)s'):
        logging.Formatter.__init__(self, fmt)

    def format(self, record):
        if record.levelno == logging.INFO:
            return record.getMessage()
        return logging.Formatter.format(self, record)
#
# Function definitions begin here
#
def init_logging_to_stderr_and_file(verbosity,
                                    no_logfile,
                                    logfile_path,
                                    file_log_level=DEFAULT_FILE_LOGLEVEL,
                                    stderr_log_level=DEFAULT_STDERR_LOGLEVEL):
    '''Log to stderr and to a log file at different level
    '''
    # set verbosity
    if verbosity == 'verbose':
        _log_level = logging.DEBUG
    elif level == 'quiet':
        _log_level = logging.ERROR
    else:
        _log_level = stderr_log_level
    logger.setLevel(file_log_level)
    stderrHandler = logging.StreamHandler(sys.stderr)
    stderrFormatter = CleanInfoFormatter()
    stderrHandler.setFormatter(stderrFormatter)
    stderrHandler.setLevel(_log_level)
    logger.addHandler(stderrHandler)

    if not no_logfile: # start a log file
        logfile_name = PROGRAM_NAME + '-'+ STARTTIME.strftime('%Y%m%d-%H%M%S')+ '.log'
        logfile_path = Path(logfile_path)/logfile_name
        if not logfile_path.parent.is_dir(): # create logs/ dir
            try:
                logfile_path.parent.mkdir(mode=DIR_MODE, parents=True)
            except OSError:
                logger.error('Unable to create logfile directory "%s"',
                             logfile_path.parent)
                raise OSError
        logfileHandler = logging.FileHandler(str(logfile_path))
        logfileFormatter = logging.Formatter('%(levelname)s: %(message)s')
        logfileHandler.setFormatter(logfileFormatter)
        logfileHandler.setLevel(file_log_level)
        logger.addHandler(logfileHandler)
    logger.debug('Command line: "%s"', ' '.join(sys.argv))
    logger.debug('%s version %s', PROGRAM_NAME, VERSION)
    logger.debug('Run started at %s', str(STARTTIME)[:-7])

#
# main program begins here
#
try:
    config_file = open(CONFIGFILE_NAME)
except FileNotFoundError:
    logger.error('Fatal--Config file %s not found in current directory.', CONFIGFILE_NAME)
    sys.exit(1)

config_data = json.load( config_file )
data_path = Path(config_data["paths"]["data"])
logfile_path = Path(config_data["paths"]["log"])
verbosity = config_data['verbosity']
no_logfile = config_data['no_logfile']
treebuilders = config_data['treebuilders']
threads = config_data['threads']
subprocesses = config_data['subprocesses']

#
# configure logging (possibly to file)
#
init_logging_to_stderr_and_file(verbosity,
                                    no_logfile,
                                    logfile_path)

app = Flask(PROGRAM_NAME)
AutoIndex(app, browse_root=os.path.curdir)

@app.route('/config')
def show_config():
    return json.dumps(config_data)

@app.route('/trees/<familyname>/alignment', methods=['POST'])
def create_family(familyname):
    if familyname == CONFIGFILE_NAME:
        logger.error('User tried to overwrite %s', CONFIGFILE_NAME)
        abort(405)
    path = data_path/familyname
    # post data
    if path.exists() and not path.is_dir():
        logger.warn('Removing existing file in directory path name')
        path.unlink()
    if not path.is_dir():
        logger.info("Creating directory %s", path)
        path.mkdir()
    try:
        fasta = request.files[PEPTIDE_PART]
        infilename = PEPTIDE_FILENAME
    except KeyError:
        fasta = request.files[DNA_PART]
        infilename = DNA_FILENAME
    except KeyError:
        logger.error('unrecognized request')
        abort(400)
    try: # parse FASTA file
        fasta_str_fh = io.StringIO(fasta.read().decode('UTF-8'))
        parsed_fasta = SeqIO.parse(fasta_str_fh, 'fasta')
        record_dict = SeqIO.to_dict(parsed_fasta)
    except:
        abort(404)
    if len(record_dict) < 1: # empty FASTA
        abort(404)
    lengths = [len(rec.seq) for rec in record_dict.values()]
    alignment_dict = {'sequences': len(record_dict),
                      'max_length': max(lengths),
                      'min_length': min(lengths),
                      'total_length': sum(lengths),
                      'overwrite': False}
    logger.info('Saving FASTA file for family "%s".', familyname)
    if (path/infilename).exists():
        logger.warn('Overwriting existing FASTA file for family %s', familyname)
        alignment_dict['overwrite'] = True
    with open(str(path/infilename), 'w') as fasta_outfh:
        for seq in record_dict.values():
            SeqIO.write(seq, fasta_outfh, 'fasta')
    with open(str(path/ALIGNMENT_DATA_FILENAME), 'w') as align_data_fh:
        json.dump(alignment_dict, align_data_fh)
    return json.dumps(alignment_dict)

@app.route('/trees/<familyname>/FastTree')
def calculate_FastTree(familyname):
    inpath = data_path/familyname
    builder = 'FastTree'
    if not inpath.is_dir():
        abort(404)
    try:
        outpath = inpath/builder
    except:
        abort(404)
    if not outpath.exists():
        try:
            outpath.mkdir()
        except:
            abort(404)
    if (inpath/DNA_FILENAME).exists():
        infile = Path('..')/DNA_FILENAME
        seq_type = DNA_PART
    elif (inpath/PEPTIDE_FILENAME).exists():
        infile = Path('..')/PEPTIDE_FILENAME
        seq_type = PEPTIDE_PART
    else:
        logger.error('Unable to find peptide or DNA sequence in request.')
        abort(404)
    #
    # calculate tree with FastTree
    #
    logger.debug('Calculating %s tree "%s" with %s.', seq_type, familyname, builder)
    defaults = treebuilders[builder][seq_type]
    cmdlist = ['time', 'nice', 'FastTree'] + defaults + [str(infile)]
    logger.debug('Command line is %s', cmdlist)
    nwk_path = outpath/TREE_NAME
    if nwk_path.exists():
        logger.warn('Removing existing tree file in "%s".', familyname+'/'+builder)
        nwk_path.unlink()
    nwk_fh = nwk_path.open(mode='wb')
    err_fh = (outpath/'run.log').open(mode='wt')
    status_fh = (outpath/'status.txt').open(mode='wt')
    environ = os.environ.copy()
    if threads > 0:
        environ['OMP_NUM_THREADS'] = str(threads)
    status_fh.write('-1\n') # signal that calculation has been started
    status_fh.close()
    status = subprocess.run(cmdlist,
                            stdout=nwk_fh,
                            stderr=err_fh,
                            cwd=str(outpath),
                            env=environ)
    nwk_fh.close()
    err_fh.close()
    status_fh = (outpath/'status.txt').open(mode='wt')
    status_fh.write("%d\n" %status.returncode)
    status_fh.close()
    if status.returncode == 0:
        nwk_file = nwk_path.open().read()
        return nwk_file
    else:
        logger.error('%s returned a non-zero result, check log for errors.', builder)
        abort(417)

@app.route('/trees/<familyname>/RAxML')
def calculate_RAxML(familyname):
    inpath = data_path/familyname
    builder = 'RAxML'
    if not inpath.is_dir():
        abort(404)
    outpath = inpath/builder
    if not outpath.exists():
        outpath.mkdir()
    if (inpath/DNA_FILENAME).exists():
        infile = Path('..')/DNA_FILENAME
        seq_type = 'DNA'
    elif (inpath/PEPTIDE_FILENAME).exists():
        infile = Path('..')/PEPTIDE_FILENAME
        seq_type = 'peptide'
    else:
        logger.error('Unable to find peptide or DNA sequence in request.')
        abort(404)
    #
    # calculate tree with RAxML
    #
    logger.debug('Calculating %s tree "%s" with %s.', seq_type, familyname, builder)
    defaults = treebuilders[builder][seq_type]
    cmdlist = ['time', 'nice', 'raxmlHPC'] + defaults + ['-n','production',
                                                         '-T', '%d'%threads,
                                                         '-s', str(infile)]
    logger.debug('Command line is %s', cmdlist)
    nwk_path = outpath/TREE_NAME
    if nwk_path.exists():
        logger.warn('Removing existing tree file in "%s".', familyname+'/'+builder)
        nwk_path.unlink()
    nwk_fh = nwk_path.open(mode='wb')
    err_fh = (outpath/'run.log').open(mode='wt')
    environ = os.environ.copy()
    status_fh = (outpath/'status.txt').open(mode='wt')
    status_fh.write('-1\n') # signal that calculation has been started
    status_fh.close()
    status = subprocess.run(cmdlist,
                            stdout=nwk_fh,
                            stderr=err_fh,
                            cwd=str(outpath),
                            env=environ)
    nwk_fh.close()
    err_fh.close()
    status_fh = (outpath/'status.txt').open(mode='wt')
    status_fh.write("%d\n" %status.returncode)
    status_fh.close()
    if status.returncode == 0:
        nwk_file = nwk_path.open().read()
        return nwk_file
    else:
        logger.error('%s returned a non-zero result, check log for errors.', builder)
        abort(417)

@app.route('/trees/<familyname>/<method>/tree')
def get_existing_tree(familyname, method):
    if method not in TREEBUILDERS:
        abort(404)
    inpath = data_path/familyname/method/TREE_NAME
    if not inpath.exists():
        abort(404)
    tree = inpath.open().read()
    return tree


@app.route('/trees/<familyname>/<method>/log')
def get_log(familyname, method):
    if method not in TREEBUILDERS:
        abort(404)
    inpath = data_path/familyname/method/'run.log'
    if not inpath.exists():
        abort(404)
    log = inpath.open().read()
    return log

@app.route('/trees/<familyname>/<method>/status')
def get_status(familyname, method):
    if method not in TREEBUILDERS:
        abort(404)
    inpath = data_path/familyname/method/'status.txt'
    if not inpath.exists():
        abort(404)
    status = inpath.open().read()
    return status

flaskrun(app)
