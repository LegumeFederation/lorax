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
import subprocess
import json
import io
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
# Non-configurable global constants.
#
AUTHOR = 'Joel Berendzen'
EMAIL = 'joelb@ncgr.org'
COPYRIGHT = """Copyright (C) 2017, The National Center for Genome Resources.  All rights reserved.
"""
PROJECT_HOME = 'https://github.com/ncgr/lorax'
# File-name-related variables.
SEQUENCE_EXTENSIONS = OrderedDict([
    ('DNA','.fna'),
    ('peptide','.faa')
])
CONFIGFILE_NAME = 'config.json'
SEQUENCES_NAME = 'sequences'
ALIGNMENT_NAME = 'alignment'
RUN_LOG_NAME = 'run_log.txt'
STATUS_NAME = 'status.txt'
STOCKHOLM_NAME = 'alignment.stockholm'
TREE_NAME = 'tree.nwk'
SEQUENCE_DATA_NAME = 'sequence_data.json'
HMM_FILENAME = 'family.hmm'
HMMSTATS_NAME = 'hmmstats.json'
ALL_FILENAMES = [CONFIGFILE_NAME,
                 ALIGNMENT_NAME+SEQUENCE_EXTENSIONS['DNA'],
                 ALIGNMENT_NAME+SEQUENCE_EXTENSIONS['peptide'],
                 SEQUENCES_NAME+SEQUENCE_EXTENSIONS['DNA'],
                 SEQUENCES_NAME+SEQUENCE_EXTENSIONS['peptide'],
                 HMM_FILENAME,
                 STATUS_NAME,
                 SEQUENCE_DATA_NAME,
                 RUN_LOG_NAME,
                 STOCKHOLM_NAME,
                 HMMSTATS_NAME] + ['FastTree', 'RAxML']
# MIME types.
NEWICK_MIMETYPE = 'text/plain'
JSON_MIMETYPE = 'application/json'
FASTA_MIMETYPE = 'text/plain'
TEXT_MIMETYPE = 'text/plain'
# hmmalign stuff.
HMM_SWITCHES = {'peptide': 'amino',
                'DNA': 'dna'}
#
# Create an app object.
#
app = Flask(__name__, instance_relative_config=True)
#
# Get configuration variables from object.
#
config_dict = {
    'base': 'lorax.config.BaseConfig',
    'development': 'lorax.config.DevelopmentConfig',
    'test': 'lorax.config.TestConfig',
    'production': 'lorax.config.ProductionConfig'
}
config_name = os.getenv('LORAX_CONFIGURATION', 'base')
if config_name not in config_dict:
    print('ERROR -- configuration "%s" not known.' %config_name)
    sys.exit(1)
app.config.from_object(config_dict[config_name])
#
# Get instance-specific configuration, if it exists.
#
pyfile_name = os.getenv('LORAX_SETTINGS', app.config['SETTINGS'])
app.config.from_pyfile(pyfile_name, silent=True)
#
# Do overrides from environmental variables.
#
for lorax_envvar, envvar in [(i, i[6:])
                             for i in sorted(os.environ)
                             if i.startswith('LORAX_')]:
    value = os.environ[lorax_envvar]
    if value == 'True':
        value = True
    elif value == 'False':
        value = False
    else:
        try:
            value = int(value)
        except ValueError:
            pass
    app.config[envvar] = value
#
# Set version in config.
#
app.config['VERSION'] = __version__
#
# Print configuration dictionary if in debug mode.
#
if app.config['DEBUG']:
    for key in sorted(app.config):
        print('%s =  %s' %(key, app.config[key]))
#
# Create a global RQ object.
#
rq = RQ(app)
#
# Function defs start here.
#
def get_file(subpath, type='data', mode='U'):
    '''Get a file, returning exceptions if they exist.

    :param subpath: path within data or log directories.
    :param type: 'data' or 'log'.
    :param mode: 'U' for string, 'b' for binary.
    :return:
    '''
    file_path = Path(app.config['PATHS'][type])/subpath
    try:
        return file_path.open(mode='r'+mode).read()
    except IOError as exc:
        return str(exc)


def create_fasta(familyname, data_name, super=None):
    '''Verify and characterize a FASTA file and save it to disk.

    :param familyname:
    :param data_name:
    :param super:
    :return:
    '''
    if not super:
        path = Path(app.config['PATHS']['data']) / familyname
    else:
        if super in ALL_FILENAMES:
            abort(403)
        path = Path(app.config['PATHS']['data']) / familyname / super
    # post data
    if path.exists() and not path.is_dir():
        app.mylogger.warning('Removing existing file in directory path name')
        path.unlink()
    if not path.is_dir():
        app.mylogger.info("Creating directory %s", path)
        path.mkdir()
    for sequence_type in SEQUENCE_EXTENSIONS.keys():
        if sequence_type in request.files:
            fasta = request.files[sequence_type]
            infileext = SEQUENCE_EXTENSIONS[sequence_type]
            break
    else:
        app.mylogger.error('unrecognized request for FASTA')
        abort(400)
    try:  # parse FASTA file
        fasta_str_fh = io.StringIO(fasta.read().decode('UTF-8'))
        parsed_fasta = SeqIO.parse(fasta_str_fh, 'fasta')
        record_dict = SeqIO.to_dict(parsed_fasta)
    except:
        app.mylogger.error('Unparseable FASTA requested for family "%s".', familyname)
        abort(406)
    if len(record_dict) < 1:  # empty FASTA
        app.mylogger.error('Empty FASTA for family "%s".', familyname)
        abort(406)
    lengths = [len(rec.seq) for rec in record_dict.values()]
    infilename = data_name + infileext
    if super: # Do super processing
        sub_path = Path(app.config['PATHS']['data']) / familyname / infilename
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
    app.mylogger.info('Saving FASTA file for family "%s".', familyname)
    if (path / infilename).exists():
        app.mylogger.warning('Overwriting existing FASTA file for family %s', familyname)
        fasta_dict['overwrite'] = True
    with open(str(path / infilename), 'w') as fasta_outfh:
        for seq in record_dict.values():
            SeqIO.write(seq, fasta_outfh, 'fasta')
    with open(str(path / SEQUENCE_DATA_NAME), 'w') as sequence_data_fh:
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


def run_subprocess_with_status(out_path,
                               err_path,
                               cmdlist,
                               cwd,
                               status_path,
                               post_process,
                               post_args):
    '''Run a subprocess, writing a status file.

    :param out_path: Path to which stdout gets sent.
    :param err_path: Path to which stderr gets sent.
    :param cmdlist: List of commands to be sent.
    :param cwd: Path to working directory.
    :param environment: Environment of the subprocess.
    :param status_path: Path to status log file.
    :return: Return code of subprocess.
    '''
    #
    # Modify the environment to select the number of threads, if requested.
    #
    environ = os.environ.copy()
    if app.config['THREADS'] > 0:
        environ['OMP_NUM_THREADS'] = str(app.config['THREADS'])
    with out_path.open(mode='wb') as out_fh:
        with err_path.open(mode='wt') as err_fh:
            status = subprocess.run(cmdlist,
                                    stdout=out_fh,
                                    stderr=err_fh,
                                    cwd=str(cwd),
                                    env=environ)
    write_status(status_path, status.returncode)
    if post_process is not None:
        post_process(out_path,
                     err_path,
                     cwd,
                     status,
                     *post_args)
    return status.returncode

def job_data_as_response(job, queue):
    job_dict = {'job_ID': job.id,
                'queue': queue
                }
    return Response(json.dumps(job_dict), mimetype=JSON_MIMETYPE)

def convert_stockholm_to_FASTA(out_path,
                               err_path,
                               cwd,
                               status,
                               fasta):
    '''Convert a Stockholm-format alignment file to FASTA.

    :param out_path: Path to which stdout gets sent.
    :param err_path: Path to which stderr gets sent.
    :param status: Status object from subprocess.
    :param fasta: Path to FASTA file to be created.
    :param status_path: Path to s.
    :return: Return code of subprocess.
    '''
    if status.returncode == 0:
        alignment = AlignIO.read(out_path.open(mode='rU'), 'stockholm')
        AlignIO.write(alignment, fasta.open(mode='w'), 'fasta')


def queue_calculation(familyname,
                      calculation,
                      super=None):
    '''Submit alignment or tree-building jobs or both to queue.

    :param config: app configuration dictionary.
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
        if calculation_components[0] in list(app.config['ALIGNERS'].keys()):
            aligner = calculation_components[0]
        else:
            app.mylogger.error('Unrecognized aligner %s.', calculation_components[0])
            abort(404)
        if calculation_components[1] in list(app.config['TREEBUILDERS'].keys()):
            tree_builder = calculation_components[1]
        else:
            app.mylogger.error('Unrecognized tree builder %s.', calculation_components[1])
            abort(404)
    elif calculation in list(app.config['ALIGNERS'].keys()):
        aligner = calculation
        tree_builder = None
    elif calculation in list(app.config['TREEBUILDERS'].keys()):
        aligner = None
        tree_builder = calculation
    #
    # Get paths to things we might need for either calculation.
    #
    if not super:
        alignment_dir = Path(app.config['PATHS']['data']) / familyname
        hmm_path = Path(HMM_FILENAME)
    else:
        if super in ALL_FILENAMES:
            app.mylogger.error('Super name is a reserved name, "%s".', super)
            abort(403)
        alignment_dir = Path(app.config['PATHS']['data']) / familyname / super
        hmm_path = Path('..') / HMM_FILENAME
    #
    # Check for prerequisites and determine sequence types.
    #
    if not alignment_dir.is_dir():
        app.mylogger.error('Directory was not previously created for %s.', alignment_dir)
        abort(428)
    if aligner is not None: # will do an alignment.
        stockholm_path = alignment_dir / STOCKHOLM_NAME
        alignment_status_path = alignment_dir / STATUS_NAME
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
            app.mylogger.error('Unable to find sequences to align.')
            abort(404)
    if tree_builder is not None: # will build a tree.
        tree_dir = alignment_dir / tree_builder
        treebuilder_status_path = tree_dir / STATUS_NAME
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
                app.mylogger.error('Unable to find aligned sequences.')
                abort(404)
    #
    # Marshal command-line arguments.
    #
    if aligner == 'hmmalign':
        aligner_command = ['time', 'nice', 'hmmalign'] + \
                           app.config['ALIGNERS'][aligner] + \
                           ['--' + hmm_seq_type, str(hmm_path), str(seqfile)]
    if tree_builder == 'FastTree':
        tree_command = ['time', 'nice', 'FastTree'] \
                  + app.config['TREEBUILDERS'][tree_builder][seq_type] \
                  + [str(alignment_input_path)]
    elif tree_builder == 'RAxML':
        tree_command = ['time', 'nice', 'raxmlHPC'] \
                  + treebuilder_args \
                  + ['-n',
                     'production',
                     '-T',
                     '%d' % app.config['THREADS'],
                     '-s', str(alignment_input_path)]
    #
    # Log command line and initialize status files.
    #
    if aligner is not None:
        app.mylogger.debug('Alignment command line is %s.', aligner_command)
        write_status(alignment_status_path, -1)
    if tree_builder is not None:
        app.mylogger.debug('Tree builder command line is %s.', tree_command)
        write_status(treebuilder_status_path, -1)
    #
    # Queue processes.
    #
    align_queue = rq.get_queue(app.config['ALIGNMENT_QUEUE'])
    tree_queue = rq.get_queue(app.config['TREE_QUEUE'])
    if aligner is not None and tree_builder is not None:
        align_job = align_queue.enqueue(run_subprocess_with_status,
                                        args=(stockholm_path,
                                              alignment_log_path,
                                              aligner_command,
                                              alignment_dir,
                                              alignment_status_path,
                                              convert_stockholm_to_FASTA,
                                              (alignment_output_path,)
                                               )
                                        )
        tree_job = tree_queue.enqueue(run_subprocess_with_status,
                                      args=(tree_path,
                                            tree_log_path,
                                            tree_command,
                                            tree_dir,
                                            treebuilder_status_path,
                                            None,
                                            None),
                                      depends_on=align_job
                                      )
        return job_data_as_response(tree_job, app.config['TREE_QUEUE'])
    elif aligner is not None:
        align_job = align_queue.enqueue(run_subprocess_with_status,
                                        args=(stockholm_path,
                                              alignment_log_path,
                                              aligner_command,
                                              alignment_dir,
                                              alignment_status_path,
                                              convert_stockholm_to_FASTA,
                                              (alignment_output_path,)
                                               )
                                        )
        return job_data_as_response(align_job, app.config['ALIGNMENT_QUEUE'])
    elif tree_builder is not None:
        tree_job = tree_queue.enqueue(run_subprocess_with_status,
                                      args=(tree_path,
                                            tree_log_path,
                                            tree_command,
                                            tree_dir,
                                            treebuilder_status_path,
                                            None,
                                            None)
                                      )
        return job_data_as_response(tree_job, app.config['TREE_QUEUE'])
    else:
        abort(404)
#
# CLI entry point.
#
@click.command(epilog='AUTHOR' + ' <'+EMAIL+'>. ' + COPYRIGHT + PROJECT_HOME)
@click.version_option(version=__version__, prog_name=__name__)
def cli():
    global app
    from .logging import init_logging_to_stderr_and_file
    #
    # Configure logging, the Flask app, and RQ.
    #
    debug = app.config['DEBUG']
    host = app.config['HOST']
    port = app.config['PORT']
    version = app.config['VERSION']
    print('lorax version %s is listening on http://%s:%d/' %(version,
                                                           host,
                                                           port))
    init_logging_to_stderr_and_file(app)
    app.run(debug=debug,
            host=host,
            port=port)
    rq.init_app(app)
#
# Target definitions begin here.
#
@app.route('/log.txt')
def show_log():
    content = get_file(app.config['LOGFILE_NAME'],
                       type='log')
    return Response(content, mimetype='text/plain')


@app.route('/trees/families.json')
def return_families():
    directory_list = os.listdir(path=app.config['PATHS']['data'])
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
        hmm_path = Path(app.config['PATHS']['data'])/family/HMM_FILENAME
        hmm_fh = hmm_path.open('wb')
    except: # e.g., if family has not been created
        app.mylogger.error('Unable to create "%s".', str(hmm_path))
        abort(400)
    hmm_fh.write(request.data)
    hmm_fh.close()
    try: # get HMM stats with hmmstat
        hmmstats_output = subprocess.check_output(['hmmstat',HMM_FILENAME],
                                                  universal_newlines=True,
                                                  cwd=str(hmm_path.parent))
    except subprocess.CalledProcessError:
        app.mylogger.error('Not a valid HMM file for family %s, removing.', family)
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
    with (hmm_path.parent/HMMSTATS_NAME).open(mode='w') as hmmstats_fh:
        json.dump(hmmstats_dict, hmmstats_fh)
    return Response(json.dumps(hmmstats_dict), mimetype=JSON_MIMETYPE)


def bind_calculation(method, superfamily=False):
    '''A factory for uniquely-named functions with route decorators applied.

    :param method: Name of resulting method.
    :return: Route-decorated function.
    '''
    if not superfamily:
        def _calculate(family):
            return queue_calculation(family,
                                     method)
        _calculate.__name__ = 'calculate_' + method
        _calculate = app.route('/trees/<family>/'+method)(_calculate)
        return _calculate
    else:
        def _calculate(family, sup):
            return queue_calculation(family,
                                     method,
                                     super=sup)
        _calculate.__name__ = 'calculate_' + method + '_superfamily'
        _calculate = app.route('/trees/<family>.<sup>/'+method)(_calculate)
        return _calculate


calculation_methods = []
for aligner in list(app.config['ALIGNERS'].keys()):
    calculation_methods.append(bind_calculation(aligner))
    calculation_methods.append(bind_calculation(aligner, superfamily=True))
    for builder in list(app.config['TREEBUILDERS'].keys()):
        calculation_methods.append(bind_calculation(aligner+'_'+builder))
        calculation_methods.append(bind_calculation(aligner+'_'+builder, superfamily=True))
for builder in list(app.config['TREEBUILDERS'].keys()):
    calculation_methods.append(bind_calculation(builder))
    calculation_methods.append(bind_calculation(builder, superfamily=True))


@app.route('/trees/<familyname>/<method>/'+TREE_NAME)
def get_existing_tree(familyname, method):
    if method not in app.config['TREEBUILDERS']:
        abort(404)
    inpath = Path(app.config['PATHS']['data'])/familyname/method/TREE_NAME
    if not inpath.exists():
        abort(404)
    return Response(inpath.open().read(), mimetype=NEWICK_MIMETYPE)


@app.route('/trees/<family>.<sup>/<method>/'+TREE_NAME)
def get_existing_tree_super(family, method, sup):
    return get_existing_tree(family+'/'+sup, method)


@app.route('/trees/<familyname>/<method>/'+RUN_LOG_NAME)
def get_log(familyname, method):
    if method in list(app.config['TREEBUILDERS'].keys()):
        inpath = Path(app.config['PATHS']['data'])/familyname/method/RUN_LOG_NAME
    elif method in list(app.config['ALIGNERS'].keys()):
        inpath = Path(app.config['PATHS']['data'])/familyname/RUN_LOG_NAME
    else:
        abort(428)
    if not inpath.exists():
        abort(404)
    return Response(inpath.open().read(), mimetype=TEXT_MIMETYPE)


@app.route('/trees/<family>.<sup>/<method>/'+RUN_LOG_NAME)
def get_log_super(family, method, sup):
    return get_log(family+'/'+sup, method)


@app.route('/trees/<familyname>/<method>/status')
def get_status(familyname, method):
    if method in list(app.config['TREEBUILDERS'].keys()):
        inpath = Path(app.config['PATHS']['data'])/familyname/method/STATUS_NAME
    elif method in list(app.config['ALIGNERS'].keys()):
        inpath = Path(app.config['PATHS']['data']) /familyname /STATUS_NAME
    else:
        abort(428)
    if not inpath.exists():
        abort(404)
    status = inpath.open().read()
    return status


@app.route('/trees/<family>.<sup>/<method>/status')
def get_status_super(family, method, sup):
    return get_status(family+'/'+sup, method)

if __name__ == '__main__':
    cli()