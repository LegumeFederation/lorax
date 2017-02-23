# -*- coding: utf-8 -*-
'''
lorax --

A web service process designed to calculate and serve up phylogenetic trees, including:
    * Setting of tree calculation parameters and metadata
    * Storing input sequences
    * Multiple sequence alignment
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
import json
import io
from datetime import datetime
from pathlib import Path # python 3.4 or later
from collections import OrderedDict # python 3.1 or later
#
# third-party imports
#
import click
from flask import Flask, Response, request, abort
from Bio import SeqIO, AlignIO
#
# local imports
#
from .version import version as __version__ # noqa
#
# Global constants
#
START_TIMESTAMP = datetime.now().strftime('%Y%m%d-%H%M%S')
PROGRAM_NAME = 'lorax'
AUTHOR = 'Joel Berendzen'
EMAIL = 'joelb@ncgr.org'
COPYRIGHT = """Copyright (C) 2017, The National Center for Genome Resources.  All rights reserved.
"""
PROJECT_HOME = 'https://github.com/ncgr/lorax'
DEFAULT_FILE_LOGLEVEL = logging.DEBUG
DEFAULT_STDERR_LOGLEVEL = logging.INFO
LOGFILE_LINK_NAME = 'lorax.log'
VERSION = __version__
DIR_MODE = 0o755
# Sequence type dictionary
SEQUENCE_EXTENSIONS = OrderedDict([
    ('DNA','.fna'),
    ('peptide','.faa')
])

# Tree builder names
TREE_BUILDERS = ['FastTree', 'RAxML']
# File names
CONFIGFILE_NAME = 'config.json'
SEQUENCES_NAME = 'sequences'
ALIGNMENT_NAME = 'alignment'
RUN_LOG_NAME = 'run_log.txt'
STATUS_FILE_NAME = 'status.txt'
STOCKHOLM_FILE = 'alignment.stockholm'
TREE_NAME = 'tree.nwk'
SEQUENCE_DATA_FILENAME = 'sequence_data.json'
HMM_FILENAME = 'family.hmm'
HMMSTATS_FILE = 'hmmstats.json'
ALL_FILENAMES = [CONFIGFILE_NAME,
                 ALIGNMENT_NAME+SEQUENCE_EXTENSIONS['DNA'],
                 ALIGNMENT_NAME+SEQUENCE_EXTENSIONS['peptide'],
                 SEQUENCES_NAME+SEQUENCE_EXTENSIONS['DNA'],
                 SEQUENCES_NAME+SEQUENCE_EXTENSIONS['peptide'],
                 HMM_FILENAME,
                 STATUS_FILE_NAME,
                 SEQUENCE_DATA_FILENAME,
                 RUN_LOG_NAME,
                 STOCKHOLM_FILE,
                 HMMSTATS_FILE] + TREE_BUILDERS
# MIME types
NEWICK_MIMETYPE = 'text/plain'
JSON_MIMETYPE = 'application/json'
FASTA_MIMETYPE = 'text/plain'
TEXT_MIMETYPE = 'text/plain'
#
# global objects
#
logger = logging.getLogger(PROGRAM_NAME)
app = Flask(PROGRAM_NAME)
config_data = None      # JSON config data, plus others, will be here
#
# Class definitions
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
# Helper function definitions begin here.
#
def init_logging_to_stderr_and_file(verbose,
                                    quiet,
                                    no_logfile,
                                    logfile_dir):
    '''Log to stderr and to a log file at different level
    '''
    if verbose:
        stderr_log_level = logging.DEBUG
    else:
        stderr_log_level = DEFAULT_STDERR_LOGLEVEL
    if quiet:
        file_log_level = logging.ERROR
    else:
        file_log_level = DEFAULT_FILE_LOGLEVEL
    logger.setLevel(min(file_log_level, stderr_log_level))
    stderrHandler = logging.StreamHandler(sys.stderr)
    stderrFormatter = CleanInfoFormatter()
    stderrHandler.setFormatter(stderrFormatter)
    stderrHandler.setLevel(stderr_log_level)
    logger.addHandler(stderrHandler)

    if not no_logfile: # start a log file
        logfile_name = PROGRAM_NAME + '-'+ START_TIMESTAMP+ '.log'
        logfile_path = Path(logfile_dir)/logfile_name
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
    logger.debug('Run started at %s', START_TIMESTAMP)

def get_file(subpath, type='data', mode='U'):
    '''

    :param subpath: path within data or log directories
    :param type: 'data' or 'log'
    :param mode: 'U' for string, 'b' for binary
    :return:
    '''
    file_path = Path(config_data['paths'][type])/subpath
    try:
        return file_path.open(mode='r'+mode).read()
    except IOError as exc:
        return str(exc)

def create_fasta(familyname, data_name, super=None):
    if not super:
        path = Path(config_data['paths']['data']) / familyname
    else:
        if super in ALL_FILENAMES:
            abort(403)
        path = Path(config_data['paths']['data']) / familyname / super
    # post data
    if path.exists() and not path.is_dir():
        logger.warning('Removing existing file in directory path name')
        path.unlink()
    if not path.is_dir():
        logger.info("Creating directory %s", path)
        path.mkdir()
    for sequence_type in SEQUENCE_EXTENSIONS.keys():
        if sequence_type in request.files:
            fasta = request.files[sequence_type]
            infileext = SEQUENCE_EXTENSIONS[sequence_type]
            break
    else:
        logger.error('unrecognized request for FASTA')
        abort(400)
    try:  # parse FASTA file
        fasta_str_fh = io.StringIO(fasta.read().decode('UTF-8'))
        parsed_fasta = SeqIO.parse(fasta_str_fh, 'fasta')
        record_dict = SeqIO.to_dict(parsed_fasta)
    except:
        logger.error('unparseable FASTA')
        abort(406)
    if len(record_dict) < 1:  # empty FASTA
        logger.error('empty FASTA')
        abort(406)
    lengths = [len(rec.seq) for rec in record_dict.values()]
    infilename = data_name + infileext
    if super: # Do super processing
        sub_path = Path(config_data['paths']['data']) / familyname / infilename
        sub_parsed_fasta = SeqIO.parse(str(sub_path), 'fasta')
        sub_record_dict = SeqIO.to_dict(sub_parsed_fasta)
        for rec in record_dict.values():
            if not rec.id.startswith(super):
                rec.id = super + '.' + rec.id
                rec.description = super + '.' + rec.description
        record_dict.update(sub_record_dict) #combine sequences
        fasta_dict = {'sequences': len(record_dict),
                      'sub_sequences': len(sub_record_dict),
                      'max_length': max(lengths),
                      'min_length': min(lengths),
                      'total_length': sum(lengths),
                      'overwrite': False,
                      'super_name': super}
    else:
        fasta_dict = {'sequences': len(record_dict),
                      'max_length': max(lengths),
                      'min_length': min(lengths),
                      'total_length': sum(lengths),
                      'overwrite': False}
    logger.info('Saving FASTA file for family "%s".', familyname)
    if (path / infilename).exists():
        logger.warning('Overwriting existing FASTA file for family %s', familyname)
        fasta_dict['overwrite'] = True
    with open(str(path / infilename), 'w') as fasta_outfh:
        for seq in record_dict.values():
            SeqIO.write(seq, fasta_outfh, 'fasta')
    with open(str(path / SEQUENCE_DATA_FILENAME), 'w') as sequence_data_fh:
        json.dump(fasta_dict, sequence_data_fh)
    return Response(json.dumps(fasta_dict), mimetype=JSON_MIMETYPE)


def calculate_tree(familyname, builder):
    inpath = Path(config_data['paths']['data']) / familyname
    if not inpath.is_dir():
        abort(428)
    outpath = inpath / builder
    if not outpath.exists():
        outpath.mkdir()
    for key in SEQUENCE_EXTENSIONS.keys():
        if (inpath / (ALIGNMENT_NAME + SEQUENCE_EXTENSIONS[key])).exists():
            infile = Path('..') / (ALIGNMENT_NAME + SEQUENCE_EXTENSIONS[key])
            seq_type = key
            break
    else:
        logger.error('Unable to find sequence type in request.')
        abort(404)
    #
    # calculate tree
    #
    logger.debug('Calculating %s tree "%s" with %s.', seq_type, familyname, builder)
    defaults = config_data['treebuilders'][builder][seq_type]

    nwk_path = outpath / TREE_NAME
    if nwk_path.exists():
        logger.warning('Removing existing tree file in "%s".', familyname + '/' + builder)
        nwk_path.unlink()
    nwk_fh = nwk_path.open(mode='wb')
    err_fh = (outpath / RUN_LOG_NAME).open(mode='wt')
    status_fh = (outpath / STATUS_FILE_NAME).open(mode='wt')
    environ = os.environ.copy()
    if config_data['threads'] > 0:
        environ['OMP_NUM_THREADS'] = str(config_data['threads'])
    status_fh.write('-1\n')  # signal that calculation has been started
    status_fh.close()
    if builder == 'FastTree':
        cmdlist = ['time', 'nice', 'FastTree'] + defaults + [str(infile)]
    elif builder == 'RAxML':
        cmdlist = ['time', 'nice', 'raxmlHPC'] + defaults + ['-n', 'production',
                                                             '-T', '%d' % config_data['threads'],
                                                             '-s', str(infile)]
    logger.debug('Command line is %s', cmdlist)
    status = subprocess.run(cmdlist,
                            stdout=nwk_fh,
                            stderr=err_fh,
                            cwd=str(outpath),
                            env=environ)
    nwk_fh.close()
    err_fh.close()
    status_fh = (outpath / STATUS_FILE_NAME).open(mode='wt')
    status_fh.write("%d\n" % status.returncode)
    status_fh.close()
    if status.returncode == 0:
        nwk_file = nwk_path.open().read()
        return nwk_file
    else:
        logger.error('%s returned a non-zero result, check log for errors.', builder)
        abort(417)
#
# CLI entry point
#
@click.command(epilog=AUTHOR + ' <'+EMAIL+'>. ' + COPYRIGHT + PROJECT_HOME)
@click.option('-d', '--debug', is_flag=True, show_default=True,
              default=False, help='Enable (unsafe) debugging.')
@click.option('-v', '--verbose', is_flag=True, show_default=True,
              default=False, help='Log debugging info to stderr.')
@click.option('-q', '--quiet', is_flag=True, show_default=True,
              default=False, help='Suppress low-level log info.')
@click.option('--no_logfile', is_flag=True, show_default=True,
              default=False, help='Suppress logging to file.')
@click.option('-c', '--config_file', default=CONFIGFILE_NAME,
              show_default=True,
               help='Configuration file name.')
@click.option('--port', default='58927', show_default=True,
               help='Port on which to listen.')
@click.option('--host', default='127.0.0.1', show_default=True,
               help='Host IP on which to listen')
@click.version_option(version=VERSION, prog_name=PROGRAM_NAME)
def cli(debug, verbose, quiet, no_logfile, config_file, port, host):
    global app, config_data
    try:
        config_fh = Path(config_file).open()
    except FileNotFoundError:
        logger.error('Fatal--Config file "%s" not found in current directory.', config_file)
        sys.exit(1)

    config_data = json.load(config_fh)
    config_data['version'] = VERSION
    config_data['program'] = PROGRAM_NAME
    config_data['start_timestamp'] = START_TIMESTAMP

    #
    # configure logging (possibly to file)
    #
    init_logging_to_stderr_and_file(verbose,
                                    quiet,
                                    no_logfile,
                                    Path(config_data["paths"]["log"]))
    app.run(debug=debug,
            host=host,
            port=port)
#
# Target definitions begin here.
#
@app.route('/config.json')
def show_config():
    return Response(json.dumps(config_data), mimetype='application/json')


@app.route('/log.txt')
def show_log():
    content = get_file(PROGRAM_NAME+'-'+START_TIMESTAMP+'.log', type='log')
    return Response(content, mimetype='text/plain')


@app.route('/trees/families.json')
def return_families():
    directory_list = os.listdir(path=config_data['paths']['data'])
    directory_list.sort()
    return Response(json.dumps(directory_list), mimetype=JSON_MIMETYPE)


@app.route('/trees/<family>/alignment', methods=['POST'])
def create_alignment(family):
    return create_fasta(family, ALIGNMENT_NAME)


@app.route('/trees/<family>/sequences', methods=['POST'])
def create_sequences(family):
    return create_fasta(family, SEQUENCES_NAME)


@app.route('/trees/<family>.<super>/sequences', methods=['POST'])
def create_superfamily_sequences(family, super):
    return create_fasta(family, SEQUENCES_NAME, super=super)


@app.route('/trees/<family>/HMM', methods=['PUT'])
def create_HMM(family):
    try:
        hmm_path = Path(config_data['paths']['data'])/family/HMM_FILENAME
        hmm_fh = hmm_path.open('wb')
    except: # e.g., if family has not been created
        logger.error('Unable to create "%s".', str(hmm_path))
        abort(400)
    hmm_fh.write(request.data)
    hmm_fh.close()
    try: # get HMM stats with hmmstat
        hmmstats_output = subprocess.check_output(['hmmstat',HMM_FILENAME],
                                                  universal_newlines=True,
                                                  cwd=str(hmm_path.parent))
    except subprocess.CalledProcessError:
        logger.error('Not a valid HMM file for family %s, removing.', family)
        hmm_path.unlink()
        abort(406)
    hmmstats_dict = {}
    for line in io.StringIO(hmmstats_output):
        if line.startswith('#') or line.startswith('\n'):
            continue
        else:
            fields = line.split()
            try:
                hmmstats_dict['idx'] = fields[0]
                hmmstats_dict['name'] = fields[1]
                hmmstats_dict['accession'] = fields[2]
                hmmstats_dict['nseq'] = int(fields[3])
                hmmstats_dict['eff_nseq'] = float(fields[4])
                hmmstats_dict['M'] = int(fields[5])
                hmmstats_dict['relent'] = float(fields[6])
                hmmstats_dict['info'] = float(fields[7])
                hmmstats_dict['relE'] = float(fields[8])
                hmmstats_dict['compKL'] = float(fields[9])
            except: # format error on hmmstats, maybe version changed from 3.1b2?
                hmmstats_dict['statfields'] = fields
    with (hmm_path.parent/HMMSTATS_FILE).open(mode='w') as hmmstats_fh:
        json.dump(hmmstats_dict, hmmstats_fh)
    return Response(json.dumps(hmmstats_dict), mimetype=JSON_MIMETYPE)


@app.route('/trees/<familyname>/hmmalign')
def calculate_HMMalign(familyname):
    hmm_switches = {'peptide':'amino',
                    'DNA': 'dna'}
    inpath = Path(config_data['paths']['data'])/familyname
    for key in SEQUENCE_EXTENSIONS.keys():
        if (inpath/(SEQUENCES_NAME+SEQUENCE_EXTENSIONS[key])).exists():
            infile = (SEQUENCES_NAME+SEQUENCE_EXTENSIONS[key])
            outpath = inpath/(ALIGNMENT_NAME + SEQUENCE_EXTENSIONS[key])
            seq_type = hmm_switches[key]
            break
    else:
        logger.error('Unable to find sequences to align.')
        abort(404)
    #
    # Align with hmmalign.
    #
    logger.debug('Calculating %s alignment "%s" with hmmalign', seq_type, familyname)
    defaults = config_data['hmmalign_defaults']
    cmdlist = ['time', 'nice', 'hmmalign'] + defaults + ['--' + seq_type,
                                                         HMM_FILENAME,
                                                         str(infile)]
    logger.debug('Command line is %s', cmdlist)
    stockholm_path = inpath/STOCKHOLM_FILE
    if stockholm_path.exists():
        logger.warning('Removing existing stockholm alignment file in "%s".', familyname)
        stockholm_path.unlink()
    stockholm_fh = stockholm_path.open(mode='wb')
    err_fh = (inpath/RUN_LOG_NAME).open(mode='wt')
    status_fh = (inpath/STATUS_FILE_NAME).open(mode='wt')
    status_fh.write('-1\n') # signal that calculation has been started
    status_fh.close()
    status = subprocess.run(cmdlist,
                            stdout=stockholm_fh,
                            stderr=err_fh,
                            cwd=str(inpath))
    stockholm_fh.close()
    err_fh.close()
    status_fh = (inpath/STATUS_FILE_NAME).open(mode='wt')
    status_fh.write("%d\n" %status.returncode)
    status_fh.close()
    if status.returncode == 0:
        alignment = AlignIO.read(stockholm_path.open(mode='rU'), 'stockholm')
        print(outpath)
        AlignIO.write(alignment, outpath.open(mode='w'), 'fasta')
        return 'Alignment calculated'
    else:
        logger.error('hmmalign returned a non-zero result, check log for errors.')
        abort(417)


@app.route('/trees/<familyname>/FastTree')
def calculate_FastTree(familyname):
    return calculate_tree(familyname, 'FastTree')


@app.route('/trees/<familyname>/RAxML')
def calculate_RAxML(familyname):
    return calculate_tree(familyname, 'RAxML')


@app.route('/trees/<familyname>/<method>/'+TREE_NAME)
def get_existing_tree(familyname, method):
    if method not in config_data['treebuilders']:
        abort(404)
    inpath = Path(config_data['paths']['data'])/familyname/method/TREE_NAME
    if not inpath.exists():
        abort(404)
    return Response(inpath.open().read(), mimetype=NEWICK_MIMETYPE)


@app.route('/trees/<familyname>/<method>/'+RUN_LOG_NAME)
def get_log(familyname, method):
    if method not in config_data['treebuilders']:
        abort(404)
    inpath = Path(config_data['paths']['data'])/familyname/method/RUN_LOG_NAME
    if not inpath.exists():
        abort(404)
    return Response(inpath.open().read(), mimetype=TEXT_MIMETYPE)

@app.route('/trees/<familyname>/<method>/status')
def get_status(familyname, method):
    if method not in config_data['treebuilders']:
        abort(404)
    inpath = Path(config_data['paths']['data'])/familyname/method/STATUS_FILE_NAME
    if not inpath.exists():
        abort(404)
    status = inpath.open().read()
    return status
