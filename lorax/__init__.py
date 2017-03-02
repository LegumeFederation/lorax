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
from flask_rq2 import RQ
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

# Calculation names.  None of these may contain an underscore.
TREE_BUILDERS = ['FastTree', 'RAxML']
ALIGNERS = ['hmmalign']
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
# hmmalign stuff
HMM_SWITCHES = {'peptide': 'amino',
                'DNA': 'dna'}
#
# global objects
#
logger = logging.getLogger(PROGRAM_NAME)
app = Flask(PROGRAM_NAME)
rq = RQ(app)
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
    '''Get a file, returning exceptions if they exist.

    :param subpath: path within data or log directories.
    :param type: 'data' or 'log'.
    :param mode: 'U' for string, 'b' for binary.
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


def write_status(path, code):
    '''Write a numeric status to file.

    :param path:
    :param code:
    :return:
    '''
    with path.open(mode='wt') as status_fh:
        status_fh.write("%d\n" % code)


@rq.job('FastTree')
def run_subprocess_with_status(out_path,
                               err_path,
                               cmdlist,
                               cwd,
                               environment,
                               status_path):
    '''

    :param out_path: Path to which stdout gets sent.
    :param err_path: Path to which stderr gets sent.
    :param cmdlist: List of commands to be sent.
    :param cwd: Path to working directory.
    :param environment: Environment of the subprocess.
    :param status_path: Path to status log file.
    :return: Return code of subprocess.
    '''
    with out_path.open(mode='wb') as out_fh:
        with err_path.open(mode='wt') as err_fh:
            status = subprocess.run(cmdlist,
                                    stdout=out_fh,
                                    stderr=err_fh,
                                    cwd=str(cwd),
                                    env=environment)
    write_status(status_path, status.returncode)
    return status.returncode


@rq.job('hmmalign')
@rq.job('FastTree')
def align_with_FASTA_output(out_path,
                            err_path,
                            cmdlist,
                            cwd,
                            environment,
                            status_path,
                            fasta):
    '''

    :param out_path: Path to which stdout gets sent.
    :param err_path: Path to which stderr gets sent.
    :param cmdlist: List of commands to be sent.
    :param cwd: Path to working directory.
    :param environment: Environment of the subprocess.
    :param status_path: Path to status log file.
    :return: Return code of subprocess.
    '''
    with out_path.open(mode='wb') as out_fh:
        with err_path.open(mode='wt') as err_fh:
            status = subprocess.run(cmdlist,
                                    stdout=out_fh,
                                    stderr=err_fh,
                                    cwd=str(cwd),
                                    env=environment)
    write_status(status_path, status.returncode)
    if status.returncode == 0:
        alignment = AlignIO.read(out_path.open(mode='rU'), 'stockholm')
        AlignIO.write(alignment, fasta.open(mode='w'), 'fasta')
    return status.returncode


def queue_calculation(config,
                      familyname,
                      calculation,
                      super=None):
    '''Submit alignment or tree-building jobs or both to queue.

    :param config: configuration dictionary.
    :param familyname: Name of previously-created family.
    :param calculation: Name of calculation to be done.
    :option super: Name of superfamily directory.
    :return: JobID
    '''
    #
    # Get calculation type(s).
    #
    calculation_components = calculation.split('_')
    if len(calculation_components) == 2:
        if calculation_components[0] in ALIGNERS:
            aligner = calculation_components[0]
        else:
            logger.error('Unrecognized aligner %s.', calculation_components[0])
            abort(404)
        if calculation_components[1] in TREE_BUILDERS:
            tree_builder = calculation_components[1]
        else:
            logger.error('Unrecognized tree builder %s.', calculation_components[1])
            abort(404)
    elif calculation in ALIGNERS:
        aligner = calculation
        tree_builder = None
    elif calculation in TREE_BUILDERS:
        aligner = None
        tree_builder = calculation
    #
    # Get paths to things we might need for either calculation.
    #
    if not super:
        alignment_dir = Path(config_data['paths']['data']) / familyname
        hmm_path = Path(HMM_FILENAME)
    else:
        if super in ALL_FILENAMES:
            logger.error('Super name is a reserved name, "%s".', super)
            abort(403)
        alignment_dir = Path(config_data['paths']['data']) / familyname / super
        hmm_path = Path('..') / HMM_FILENAME
    #
    # Check for prerequisites and determine sequence types.
    #
    if not alignment_dir.is_dir():
        logger.error('Directory was not previously created for %s.', alignment_dir)
        abort(428)
    if aligner is not None: # will do an alignment.
        stockholm_path = alignment_dir / STOCKHOLM_FILE
        alignment_status_path = alignment_dir / STATUS_FILE_NAME
        alignment_log_path = alignment_dir / RUN_LOG_NAME
        for key in SEQUENCE_EXTENSIONS.keys():
            if (alignment_dir/(SEQUENCES_NAME+SEQUENCE_EXTENSIONS[key])).exists():
                seqfile = SEQUENCES_NAME+SEQUENCE_EXTENSIONS[key]
                alignment_output_path = alignment_dir/(ALIGNMENT_NAME+SEQUENCE_EXTENSIONS[key])
                hmm_seq_type = HMM_SWITCHES[key]

                # These are only used if building a tree.
                alignment_input_path = Path('..')/(ALIGNMENT_NAME+SEQUENCE_EXTENSIONS[key])
                seq_type = key
                break
        else:
            logger.error('Unable to find sequences to align.')
            abort(404)
    if tree_builder is not None: # will build a tree.
        tree_dir = alignment_dir / tree_builder
        treebuilder_status_path = tree_dir / STATUS_FILE_NAME
        tree_path = tree_dir / TREE_NAME
        tree_log_path = tree_dir / RUN_LOG_NAME
        if not tree_dir.exists():
            tree_dir.mkdir()
        if aligner is None: # building tree with alignment already done.
            for key in SEQUENCE_EXTENSIONS.keys():
                if (alignment_dir / (ALIGNMENT_NAME + SEQUENCE_EXTENSIONS[key])).exists():
                    alignment_input_path = Path('..')/(ALIGNMENT_NAME + SEQUENCE_EXTENSIONS[key])
                    seq_type = key
                    break
            else:
                logger.error('Unable to find aligned sequences.')
                abort(404)
    #
    # Modify the environment to select the number of threads, if requested.
    #
    environ = os.environ.copy()
    if config['threads'] > 0:
        environ['OMP_NUM_THREADS'] = str(config['threads'])
    #
    # Marshal command-line arguments.
    #
    if aligner == 'hmmalign':
        hmmalign_command = ['time', 'nice', 'hmmalign'] + \
                           config_data['hmmalign_defaults'] + \
                           ['--' + hmm_seq_type, str(hmm_path), str(seqfile)]
    if tree_builder == 'FastTree':
        tree_command = ['time', 'nice', 'FastTree'] \
                  + config['treebuilders'][tree_builder][seq_type] \
                  + [str(alignment_input_path)]
    elif tree_builder == 'RAxML':
        tree_command = ['time', 'nice', 'raxmlHPC'] \
                  + treebuilder_args \
                  + ['-n',
                     'production',
                     '-T',
                     '%d' % config_data['threads'],
                     '-s', str(alignment_input_path)]
    #
    # Log command line and initialize status files.
    #
    if aligner is not None:
        logger.debug('Alignment command line is %s.', hmmalign_command)
        write_status(alignment_status_path, -1)
    if tree_builder is not None:
        logger.debug('Tree builder command line is %s.', tree_command)
        write_status(treebuilder_status_path, -1)
    #
    # Queue processes.
    #
    if aligner is not None and tree_builder is not None:
        align_with_FASTA_output(stockholm_path,
                                alignment_log_path,
                                hmmalign_command,
                                alignment_dir,
                                environ,
                                alignment_status_path,
                                alignment_output_path)
        run_subprocess_with_status.queue(tree_path,
                                   tree_log_path,
                                   tree_command,
                                   tree_dir,
                                   environ,
                                   treebuilder_status_path)
        return 'Alignment and tree building queued.'
    elif aligner is not None:
        align_with_FASTA_output(stockholm_path,
                                alignment_log_path,
                                hmmalign_command,
                                alignment_dir,
                                environ,
                                alignment_status_path,
                                alignment_output_path)
        return 'alignment queued.'
    elif tree_builder is not None:
        run_subprocess_with_status.queue(tree_path,
                                   tree_log_path,
                                   tree_command,
                                   tree_dir,
                                   environ,
                                   treebuilder_status_path)
        return 'Tree building queued.'
    else:
        abort(404)
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
    rq.init_app(app)
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


def bind_calculation(method, superfamily=False):
    '''A factory for uniquely-named functions with route decorators applied.

    :param method: Name of resulting method.
    :return: Route-decorated function.
    '''
    if not superfamily:
        def _calculate(family):
            return queue_calculation(config_data,
                                     family,
                                     method)
        _calculate.__name__ = 'calculate_' + method
        _calculate = app.route('/trees/<family>/'+method)(_calculate)
        return _calculate
    else:
        def _calculate(family, sup):
            return queue_calculation(config_data,
                                     family,
                                     method,
                                     super=sup)
        _calculate.__name__ = 'calculate_' + method + '_superfamily'
        _calculate = app.route('/trees/<family>.<sup>/'+method)(_calculate)
        return _calculate


calculation_methods = []
for aligner in ALIGNERS:
    calculation_methods.append(bind_calculation(aligner))
    calculation_methods.append(bind_calculation(aligner, superfamily=True))
    for builder in TREE_BUILDERS:
        calculation_methods.append(bind_calculation(aligner+'_'+builder))
        calculation_methods.append(bind_calculation(aligner+'_'+builder, superfamily=True))
for builder in TREE_BUILDERS:
    calculation_methods.append(bind_calculation(builder))
    calculation_methods.append(bind_calculation(builder, superfamily=True))


@app.route('/trees/<familyname>/<method>/'+TREE_NAME)
def get_existing_tree(familyname, method):
    if method not in config_data['treebuilders']:
        abort(404)
    inpath = Path(config_data['paths']['data'])/familyname/method/TREE_NAME
    if not inpath.exists():
        abort(404)
    return Response(inpath.open().read(), mimetype=NEWICK_MIMETYPE)


@app.route('/trees/<family>.<sup>/<method>/'+TREE_NAME)
def get_existing_tree_super(family, method, sup):
    return get_existing_tree(family+'/'+sup, method)


@app.route('/trees/<familyname>/<method>/'+RUN_LOG_NAME)
def get_log(familyname, method):
    if method not in config_data['treebuilders']:
        abort(404)
    inpath = Path(config_data['paths']['data'])/familyname/method/RUN_LOG_NAME
    if not inpath.exists():
        abort(404)
    return Response(inpath.open().read(), mimetype=TEXT_MIMETYPE)


@app.route('/trees/<family>.<sup>/<method>/'+RUN_LOG_NAME)
def get_log_super(family, method, sup):
    return get_log(family+'/'+sup, method)


@app.route('/trees/<familyname>/<method>/status')
def get_status(familyname, method):
    if method not in config_data['treebuilders']:
        abort(404)
    inpath = Path(config_data['paths']['data'])/familyname/method/STATUS_FILE_NAME
    if not inpath.exists():
        abort(404)
    status = inpath.open().read()
    return status


@app.route('/trees/<family>.<sup>/<method>/status')
def get_status_super(family, method, sup):
    return get_status(family+'/'+sup, method)