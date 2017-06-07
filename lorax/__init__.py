# -*- coding: utf-8 -*-
"""
lorax --

A web service process to calculate and serve up phylogenetic trees, including:
    * Setting of tree calculation parameters and metadata
    * Storing input sequences
    * Multiple sequence alignment
    * Phylogenetic tree calculation
    * Serving up results
"""
#
# standard library imports
#
import io
import json
import os
import shutil
import subprocess
from collections import OrderedDict  # python 3.1
from datetime import datetime
from pathlib import Path  # python 3.4
#
# third-party imports
#
from flask import Flask, Response, request, abort
from flask_cli import FlaskCLI
from flask_rq2 import RQ
import rq_dashboard
from Bio import SeqIO, AlignIO, Phylo
#
# local imports
#
from lorax.config import configure_app
#
# Non-configurable global constants.
#
# File-name-related variables.
SEQUENCE_EXTENSIONS = OrderedDict([
    ('DNA', '.fna'),
    ('peptide', '.faa')
])
SEQUENCES_NAME = 'sequences'
ALIGNMENT_NAME = 'alignment'
RUN_LOG_NAME = 'run_log.txt'
STATUS_NAME = 'status.txt'
STOCKHOLM_NAME = 'alignment.stockholm'
RAW_TREE_NAME = 'tree_raw.nwk'
TREE_NAME = 'tree.nwk'
PHYLOXML_NAME = 'tree.xml'
SEQUENCE_DATA_NAME = 'sequence_data.json'
HMM_FILENAME = 'family.hmm'
HMMSTATS_NAME = 'hmmstats.json'
FAMILIES_NAME = 'families.json'
ALL_FILENAMES = ['',  # don't allow null name
                 ALIGNMENT_NAME + SEQUENCE_EXTENSIONS['DNA'],
                 ALIGNMENT_NAME + SEQUENCE_EXTENSIONS['peptide'],
                 SEQUENCES_NAME + SEQUENCE_EXTENSIONS['DNA'],
                 SEQUENCES_NAME + SEQUENCE_EXTENSIONS['peptide'],
                 HMM_FILENAME,
                 STATUS_NAME,
                 SEQUENCE_DATA_NAME,
                 RUN_LOG_NAME,
                 STOCKHOLM_NAME,
                 HMMSTATS_NAME,
                 FAMILIES_NAME,
                 PHYLOXML_NAME] + ['FastTree', 'RAxML']
# MIME types.
NEWICK_MIMETYPE = 'application/newick'
JSON_MIMETYPE = 'application/json'
FASTA_MIMETYPE = 'application/fasta'
TEXT_MIMETYPE = 'text/plain'
# hmmalign stuff.
HMM_SWITCHES = {'peptide': 'amino',
                'DNA': 'dna'}
#
# Library path for fixing external libraries.
#
LIBRARY_PATH_ENVVAR = {'Darwin': 'DYLD_LIBRARY_PATH'}
#
# Create an app object and configure it.
#
app = Flask(__name__,
            instance_relative_config=True,
            template_folder='templates')
FlaskCLI(app)
configure_app(app)
#
# Create a global RQ object, with dashboard at /rq.
#
rq = RQ(app)
if not app.config['RQ_ASYNC']:
    app.config.from_object(rq_dashboard.default_settings)
    app.register_blueprint(rq_dashboard.blueprint, url_prefix="/rq")


#
# Helper function defs start here.
#
def get_file(subpath, file_type='data', mode='U'):
    """Get a file, returning exceptions if they exist.

    :param subpath: path within data or log directories.
    :param file_type: 'data' or 'log'.
    :param mode: 'U' for string, 'b' for binary.
    :return:
    """
    if file_type == 'data':
        file_path = Path(app.config['DATA_PATH']) / subpath
    elif file_type == 'log':
        file_path = Path(app.config['LOG_PATH']) / subpath
    else:
        app.logger.error('Unrecognized file type %s.', file_type)
        return
    try:
        return file_path.open(mode='r' + mode).read()
    except IOError as exc:
        return str(exc)


def create_fasta(familyname, data_name, superfamily=None):
    """Verify and characterize a FASTA file and save it to disk.

    :param familyname:
    :param data_name:
    :param superfamily:
    :return:
    """
    record_dict = None
    infileext = None
    if not superfamily:
        path = Path(app.config['DATA_PATH']) / familyname
    else:
        if superfamily in ALL_FILENAMES:
            abort(403)
        path = Path(app.config['DATA_PATH']) / familyname / superfamily
    # post data
    if path.exists() and not path.is_dir():
        app.logger.warning('Removing existing file in data path name.')
        path.unlink()
    if not path.is_dir():
        app.logger.debug("Creating directory %s.", path)
        path.mkdir()
    for sequence_type in SEQUENCE_EXTENSIONS.keys():
        if sequence_type in request.files:
            fasta = request.files[sequence_type]
            infileext = SEQUENCE_EXTENSIONS[sequence_type]
            break
    else:
        fasta = None
        app.logger.error('Unrecognized request for FASTA.')
        abort(400)
    try:  # parse FASTA file
        record_dict = SeqIO.to_dict(
            SeqIO.parse(io.StringIO(fasta.read().decode('UTF-8')), 'fasta'))
        if len(record_dict) < 1:
            raise ValueError
    except (ValueError, RuntimeError):
        app.logger.error('Unparseable/empty FASTA requested for family "%s".',
                         familyname)
        abort(406)
    lengths = [len(rec.seq) for rec in record_dict.values()]
    infilename = data_name + infileext
    if superfamily:  # Do superfamily processing
        sub_path = Path(app.config['DATA_PATH']) / familyname / infilename
        sub_parsed_fasta = SeqIO.parse(str(sub_path), 'fasta')
        sub_record_dict = SeqIO.to_dict(sub_parsed_fasta)
        for rec in record_dict.values():
            if not rec.id.startswith(superfamily):
                rec.id = superfamily + '.' + rec.id
                rec.description = superfamily + '.' + rec.description
        record_dict.update(sub_record_dict)  # combine sequences
        fasta_dict = {'sequences': len(record_dict),
                      'sub_sequences': len(sub_record_dict),
                      'max_length': max(lengths),
                      'min_length': min(lengths),
                      'total_length': sum(lengths),
                      'overwrite': False,
                      'superfamily_name': superfamily}
    else:
        fasta_dict = {'sequences': len(record_dict),
                      'max_length': max(lengths),
                      'min_length': min(lengths),
                      'total_length': sum(lengths),
                      'overwrite': False}
    app.logger.debug('Saving FASTA file for family "%s".', familyname)
    if (path / infilename).exists():
        app.logger.warning('Overwriting existing FASTA file for family %s.',
                           familyname)
        fasta_dict['overwrite'] = True
    with open(str(path / infilename), 'w') as fasta_outfh:
        for seq in record_dict.values():
            SeqIO.write(seq, fasta_outfh, 'fasta')
    with open(str(path / SEQUENCE_DATA_NAME), 'w') as sequence_data_fh:
        json.dump(fasta_dict, sequence_data_fh)
    return Response(json.dumps(fasta_dict), mimetype=JSON_MIMETYPE)


def write_status(path, code):
    """Write a numeric status to file.

    :param path:
    :param code:
    :return:
    """
    with path.open(mode='wt') as status_fh:
        status_fh.write("%d\n" % code)


def run_subprocess_with_status(out_path,
                               err_path,
                               cmdlist,
                               cwd,
                               status_path,
                               post_process,
                               post_args):
    """Run a subprocess, writing a status file.

    :param post_process: Function called after processing
    :param post_args: Arguments to post_process
    :param out_path: Path to which stdout gets sent
    :param err_path: Path to which stderr gets sent
    :param cmdlist: List of commands to be sent
    :param cwd: Path to working directory
    :param status_path: Path to status log file
    :return: Return code of subprocess
    """
    environ = os.environ.copy()
    #
    # Modify the environment to select the number of threads, if requested.
    #
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


def datetime_to_isoformat(time):
    if time is None:
        return 'None'
    else:
        return datetime.isoformat(time)


def job_data_as_response(job, q):
    """Return a JSON dictionary of job parameters.

    :param job: Job object.
    :param q: Queue object.
    :return: Response of JSON data.
    """
    job_ids = q.get_job_ids()
    if job.id in job_ids:
        queue_position = job_ids.index(job.id)
    else:
        queue_position = len(job_ids)
    queue_time = 0
    # needs testing before shipping
    # if queue_position > 1:
    #    for otherjob in job_ids[:queue_position-1]:
    #        queue_time += q.fetch_job(otherjob).estimated_time

    job_dict = {'id': job.id,
                'description': job.description,
                'status': job.status,
                'tasktype': job.tasktype,
                'taskname': job.taskname,
                'family': job.family,
                'superfamily': job.superfamily,
                # booleans
                'is_queued': job.is_queued,
                'is_started': job.is_started,
                'is_finished': job.is_finished,
                'is_failed': job.is_failed,
                # times
                'created_at': datetime_to_isoformat(job.created_at),
                'enqueued_at': datetime_to_isoformat(job.enqueued_at),
                'ended_at': datetime_to_isoformat(job.ended_at),
                'started_at': datetime_to_isoformat(job.started_at),
                'estimated_job_time': job.estimated_time,
                # queue data
                'queue_name': q.name,
                'queue_position': queue_position,
                'estimated_queue_time': queue_time
                }
    return Response(json.dumps(job_dict), mimetype=JSON_MIMETYPE)


def estimate_job_time(task):
    """Placeholder for alignment calculation time estimate.

    :param task:
    :return:
    """
    if task == 'alignment':
        return 10
    elif task == 'tree':
        return 60


def convert_stockholm_to_fasta(out_path,
                               err_path,
                               cwd,
                               status,
                               fasta):
    """Convert a Stockholm-format alignment file to FASTA.

    :param cwd: 
    :param err_path: 
    :param out_path: Path to which stdout was sent.
    :param status: Status object from subprocess.
    :param fasta: Path to FASTA file to be created.
    :return: Return code of subprocess.
    """
    del err_path, cwd
    if status.returncode == 0:
        alignment = AlignIO.read(out_path.open(mode='rU'), 'stockholm')
        AlignIO.write(alignment, fasta.open(mode='w'), 'fasta')


def cleanup_tree(raw_path,
                 err_path,
                 cwd,
                 status,
                 clean_path,
                 make_rooted,
                 root_name,
                 xml_path):
    """Ladderize output tree.

    :param cwd: 
    :param err_path: 
    :param clean_path:
    :param make_rooted:
    :param root_name:
    :param xml_path:
    :param raw_path: Path to which raw tree was sent.
    :param status: Status object from subprocess.
    :return: Return code of subprocess.
    """
    del err_path, cwd
    if status.returncode == 0:
        tree = Phylo.read(raw_path.open(mode='rU'), 'newick')
        if make_rooted:
            tree.root_at_midpoint()
        tree.ladderize()
        tree.root.name = root_name
        Phylo.write(tree, clean_path.open(mode='w'), 'newick')
        Phylo.write(tree, xml_path.open(mode='w'), 'phyloxml')


def set_job_description(tasktype, taskname, job, family, superfamily):
    """Set the job description.

    :param tasktype:
    :param taskname: Type of task (string).
    :param taskname: Name of task (string).
    :param job: rc job object.
    :param family: Name of family.
    :param superfamily: Name of superfamily.
    :return:
    """
    job.tasktype = tasktype
    job.taskname = taskname
    job.family = family
    job.superfamily = superfamily
    job.estimated_time = estimate_job_time(tasktype)
    if superfamily is None:
        job.description = '%s %s of family %s' % (job.taskname,
                                                  job.tasktype,
                                                  job.family)
    else:
        job.description = '%s %s of superfamily %s.%s' % (job.taskname,
                                                          job.tasktype,
                                                          job.family,
                                                          job.superfamily)


def queue_calculation(familyname,
                      calculation,
                      superfamily=None):
    """Submit alignment or tree-building jobs or both to queue.

    :param superfamily:
    :param familyname: Name of previously-created family.
    :param calculation: Name of calculation to be done.
    :option superfamily: Name of superfamily directory.
    :return: JobID
    """
    #
    # Assignments to make PEP8 happy
    #
    alignment_tool = None
    tree_builder = None
    hmm_seq_type = None
    seqfile = None
    seq_type = None
    alignment_input_path = None
    aligner_command = None
    alignment_status_path = None
    tree_command = None
    treebuilder_status_path = None
    stockholm_path = None
    alignment_log_path = None
    raw_tree_path = None
    tree_log_path = None
    tree_dir = None
    tree_path = None
    phyloxml_path = None
    alignment_output_path = None
    #
    # Get calculation type(s).
    #
    calculation_components = calculation.split('_')
    if len(calculation_components) == 2:  # combined calculation
        if calculation_components[0] in list(app.config['ALIGNERS'].keys()):
            alignment_tool = calculation_components[0]
        else:
            app.logger.error('Unrecognized aligner %s.',
                             calculation_components[0])
            abort(404)
        if calculation_components[1] in list(
                app.config['TREEBUILDERS'].keys()):
            tree_builder = calculation_components[1]
        else:
            app.logger.error('Unrecognized tree builder %s.',
                             calculation_components[1])
            abort(404)
    elif calculation in list(app.config['ALIGNERS'].keys()):
        alignment_tool = calculation
        tree_builder = None
    elif calculation in list(app.config['TREEBUILDERS'].keys()):
        alignment_tool = None
        tree_builder = calculation
    else:
        app.logger.error('Unrecognized calculation type %s.', calculation)
        abort(404)
    #
    # Get paths to things we might need for either calculation.
    #
    if not superfamily:
        alignment_dir = Path(app.config['DATA_PATH']) / familyname
        hmm_path = Path(HMM_FILENAME)
    else:
        if superfamily in ALL_FILENAMES:
            app.logger.error('superfamily name is a reserved name, "%s".',
                             superfamily)
            abort(403)
        alignment_dir = Path(
            app.config['DATA_PATH']) / familyname / superfamily
        hmm_path = Path('..') / HMM_FILENAME
    #
    # Check for prerequisites and determine sequence types.
    #
    if not alignment_dir.is_dir():
        app.logger.error('Directory was not previously created for %s.',
                         alignment_dir)
        abort(428)
    if alignment_tool is not None:  # will do an alignment.
        stockholm_path = alignment_dir / STOCKHOLM_NAME
        alignment_status_path = alignment_dir / STATUS_NAME
        alignment_log_path = alignment_dir / RUN_LOG_NAME
        for key in SEQUENCE_EXTENSIONS.keys():
            if (alignment_dir / (
                    SEQUENCES_NAME + SEQUENCE_EXTENSIONS[key])).exists():
                seqfile = SEQUENCES_NAME + SEQUENCE_EXTENSIONS[key]
                alignment_output_path = alignment_dir / (
                    ALIGNMENT_NAME + SEQUENCE_EXTENSIONS[key])
                hmm_seq_type = HMM_SWITCHES[key]

                # These are only used if building a tree.
                alignment_input_path = Path('..') / (
                    ALIGNMENT_NAME + SEQUENCE_EXTENSIONS[key])
                seq_type = key
                break
        else:
            app.logger.error('Unable to find sequences to align.')
            abort(404)
    if tree_builder is not None:  # will build a tree.
        tree_dir = alignment_dir / tree_builder
        treebuilder_status_path = tree_dir / STATUS_NAME
        raw_tree_path = tree_dir / RAW_TREE_NAME
        tree_path = tree_dir / TREE_NAME
        phyloxml_path = tree_dir / PHYLOXML_NAME
        tree_log_path = tree_dir / RUN_LOG_NAME
        if not tree_dir.exists():
            tree_dir.mkdir()
        if alignment_tool is None:  # build tree with alignment already done
            for key in SEQUENCE_EXTENSIONS.keys():
                if (alignment_dir / (
                    ALIGNMENT_NAME +
                        SEQUENCE_EXTENSIONS[key])).exists():
                    alignment_input_path = Path('..') / (
                        ALIGNMENT_NAME + SEQUENCE_EXTENSIONS[key])
                    seq_type = key
                    break
            else:
                app.logger.error('Unable to find aligned sequences.')
                abort(404)
    #
    # Marshal command-line arguments.
    #
    if alignment_tool == 'hmmalign':
        aligner_command = ['time', 'nice', app.config['HMMALIGN_EXE']] + \
            app.config['ALIGNERS'][aligner] + \
            ['--' + hmm_seq_type, str(hmm_path), str(seqfile)]
    if tree_builder == 'FastTree':
        tree_command = ['time', 'nice', app.config['FASTTREE_EXE']] \
            + app.config['TREEBUILDERS'][tree_builder][seq_type] \
            + [str(alignment_input_path)]
    elif tree_builder == 'RAxML':
        tree_command = ['time', 'nice', app.config['RAXML_EXE']] \
            + app.config['TREEBUILDERS'][tree_builder][seq_type] \
            + ['-n',
               'production',
               '-T',
               '%d' % app.config['THREADS'],
               '-s', str(alignment_input_path)]
    #
    # Log command line and initialize status files.
    #
    if alignment_tool is not None:
        app.logger.debug('Alignment command line is %s.', aligner_command)
        write_status(alignment_status_path, -1)
    if tree_builder is not None:
        app.logger.debug('Tree builder command line is %s.', tree_command)
        write_status(treebuilder_status_path, -1)
    #
    # Queue processes.
    #
    align_queue = rq.get_queue(app.config['ALIGNMENT_QUEUE'])
    tree_queue = rq.get_queue(app.config['TREE_QUEUE'])
    if alignment_tool is not None and tree_builder is not None:
        align_job = align_queue.enqueue(run_subprocess_with_status,
                                        args=(stockholm_path,
                                              alignment_log_path,
                                              aligner_command,
                                              alignment_dir,
                                              alignment_status_path,
                                              convert_stockholm_to_fasta,
                                              (alignment_output_path,),
                                              ),
                                        timeout=app.config[
                                            'ALIGNMENT_QUEUE_TIMEOUT']
                                        )
        set_job_description('alignment', alignment_tool, align_job, familyname,
                            superfamily)
        tree_job = tree_queue.enqueue(run_subprocess_with_status,
                                      args=(raw_tree_path,
                                            tree_log_path,
                                            tree_command,
                                            tree_dir,
                                            treebuilder_status_path,
                                            cleanup_tree,
                                            (tree_path, True, familyname,
                                             phyloxml_path)),
                                      timeout=app.config['TREE_QUEUE_TIMEOUT'],
                                      depends_on=align_job
                                      )
        set_job_description('tree', tree_builder, tree_job, familyname,
                            superfamily)
        return job_data_as_response(tree_job, tree_queue)
    elif alignment_tool is not None:
        align_job = align_queue.enqueue(run_subprocess_with_status,
                                        args=(stockholm_path,
                                              alignment_log_path,
                                              aligner_command,
                                              alignment_dir,
                                              alignment_status_path,
                                              convert_stockholm_to_fasta,
                                              (alignment_output_path,)
                                              ),
                                        timeout=app.config[
                                            'ALIGNMENT_QUEUE_TIMEOUT']
                                        )
        set_job_description('alignment', alignment_tool, align_job, familyname,
                            superfamily)
        return job_data_as_response(align_job, align_queue)
    elif tree_builder is not None:
        tree_job = tree_queue.enqueue(run_subprocess_with_status,
                                      args=(raw_tree_path,
                                            tree_log_path,
                                            tree_command,
                                            tree_dir,
                                            treebuilder_status_path,
                                            cleanup_tree,
                                            (tree_path, True, familyname,
                                             phyloxml_path)),
                                      timeout=app.config['TREE_QUEUE_TIMEOUT']
                                      )
        set_job_description('tree', tree_builder, tree_job, familyname,
                            superfamily)
        return job_data_as_response(tree_job, tree_queue)
    else:
        abort(404)


#
# Target definitions begin here.
#
@app.route('/log.txt')
def return_log():
    """Return the log file.

    :return: text/plain response
    """
    content = get_file(app.config['LOGFILE_NAME'],
                       file_type='log')
    return Response(content, mimetype='text/plain')


@app.route('/trees/' + FAMILIES_NAME)
def return_families():
    """Return the list of gene familes.

    :return: JSON list
    """
    directory_list = sorted(os.listdir(path=app.config['DATA_PATH']))
    return Response(json.dumps(directory_list), mimetype=JSON_MIMETYPE)


@app.route('/trees/<family>/alignment', methods=['POST', 'GET'])
def post_or_get_alignment(family):
    """POST or GET alignment.

    :param family: Family name
    :return: FASTA of alignment on GET
    """
    test_path = None
    if request.method == 'POST':
        return create_fasta(family, ALIGNMENT_NAME)
    elif request.method == 'GET':
        alignment_path = Path(
            app.config['DATA_PATH']) / family / ALIGNMENT_NAME
        for ext in SEQUENCE_EXTENSIONS.keys():
            test_path = alignment_path.with_suffix(SEQUENCE_EXTENSIONS[ext])
            if test_path.exists():
                break
        else:
            abort(404)
        return Response(test_path.open().read(), mimetype=FASTA_MIMETYPE)


@app.route('/trees/<family>.<superfamily>/alignment', methods=['POST', 'GET'])
def post_or_get_alignment_superfamily(family, superfamily):
    """POST or GET alignment for a superfamily.

    :param family: Existing family name
    :param superfamily: Existing superfamily name
    :return:
    """
    test_path = None
    if request.method == 'POST':
        return create_fasta(family, ALIGNMENT_NAME, superfamily=superfamily)
    elif request.method == 'GET':
        alignment_path = Path(
            app.config['DATA_PATH']) / family / superfamily / ALIGNMENT_NAME
        for ext in SEQUENCE_EXTENSIONS.keys():
            test_path = alignment_path.with_suffix(SEQUENCE_EXTENSIONS[ext])
            if test_path.exists():
                break
        else:
            abort(404)
        return Response(test_path.open().read(), mimetype=FASTA_MIMETYPE)


@app.route('/trees/<family>/sequences', methods=['POST'])
def post_sequences(family):
    """POST a set of sequences that belong in a family.

    :param family: New or existing family name.
    :return:
    """
    return create_fasta(family, SEQUENCES_NAME)


@app.route('/trees/<family>.<superfamily>', methods=['DELETE'])
def delete_superfamily(family, superfamily):
    """DELETE a superfamily.

    :param family:
    :param superfamily:
    :return:
    """
    if superfamily in ALL_FILENAMES:
        abort(403)
    path = Path(app.config['DATA_PATH']) / family / superfamily
    if not path.exists():
        abort(403)

    shutil.rmtree(str(path))
    return 'Deleted "%s.%s".' % (family, superfamily)


@app.route('/trees/<family>.<superfamily>/sequences', methods=['POST'])
def post_superfamily_sequences(family, superfamily):
    """POST a set of sequences for a superfamily.

    :param family: Existing family name
    :param superfamily: Name of superfamily to be created
    :return:
    """
    return create_fasta(family, SEQUENCES_NAME, superfamily=superfamily)


@app.route('/trees/<family>/HMM', methods=['PUT'])
def put_hmm(family):
    """PUT an hmm that belongs with the family.

    :param family: name of existing family
    :return:
    """
    hmm_fh = None
    hmmstats_output = None
    hmm_path = Path(app.config['DATA_PATH']) / family / HMM_FILENAME
    try:
        hmm_fh = hmm_path.open('wb')
    except IOError:  # e.g., if family has not been created
        app.logger.error('Unable to create "%s".', str(hmm_path))
        abort(400)
    hmm_fh.write(request.data)
    hmm_fh.close()
    try:  # get HMM stats with hmmstat
        with open(os.devnull, 'w') as devnull:
            hmmstats_output = subprocess.check_output(
                ['hmmstat', HMM_FILENAME],
                universal_newlines=True,
                stderr=devnull,
                cwd=str(hmm_path.parent))
    except subprocess.CalledProcessError:
        app.logger.error('Not a valid HMM file for family %s, removing.',
                         family)
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
            except (TypeError, KeyError,
                    ValueError):  # format error on hmmstats
                app.logger.error(
                    'hmmstats did not return expected stats, check version.')
                abort(406)
    with (Path(hmm_path.parent) / HMMSTATS_NAME).open(mode='w') as hmmstats_fh:
        json.dump(hmmstats_dict, hmmstats_fh)
    return Response(json.dumps(hmmstats_dict), mimetype=JSON_MIMETYPE)


def bind_calculation(method, superfamily=False):
    """A factory for uniquely-named functions with route decorators applied.

    :param superfamily:
    :param method: Name of resulting method.
    :return: Route-decorated function.
    """
    if not superfamily:
        def _calculate(family):
            return queue_calculation(family,
                                     method)

        _calculate.__name__ = 'calculate_' + method
        _calculate = app.route('/trees/<family>/' + method)(_calculate)
        return _calculate
    else:
        def _calculate(family, sup):
            return queue_calculation(family,
                                     method,
                                     superfamily=sup)

        _calculate.__name__ = 'calculate_' + method + '_superfamily'
        _calculate = app.route('/trees/<family>.<sup>/' + method)(_calculate)
        return _calculate


calculation_methods = []
for aligner in list(app.config['ALIGNERS'].keys()):
    calculation_methods.append(bind_calculation(aligner))
    calculation_methods.append(bind_calculation(aligner, superfamily=True))
    for builder in list(app.config['TREEBUILDERS'].keys()):
        calculation_methods.append(bind_calculation(aligner + '_' + builder))
        calculation_methods.append(
            bind_calculation(aligner + '_' + builder, superfamily=True))
for builder in list(app.config['TREEBUILDERS'].keys()):
    calculation_methods.append(bind_calculation(builder))
    calculation_methods.append(bind_calculation(builder, superfamily=True))


@app.route('/trees/<familyname>/<method>/' + TREE_NAME)
def get_existing_tree(familyname, method):
    if method not in app.config['TREEBUILDERS']:
        abort(404)
    inpath = Path(app.config['DATA_PATH']) / familyname / method / TREE_NAME
    if not inpath.exists():
        abort(404)
    return Response(inpath.open().read(), mimetype=NEWICK_MIMETYPE)


@app.route('/trees/<family>.<sup>/<method>/' + TREE_NAME)
def get_existing_tree_super(family, method, sup):
    return get_existing_tree(family + '/' + sup, method)


@app.route('/trees/<familyname>/<method>/' + PHYLOXML_NAME)
def get_phyloxml_tree(familyname, method):
    if method not in app.config['TREEBUILDERS']:
        abort(404)
    inpath = Path(
        app.config['DATA_PATH']) / familyname / method / PHYLOXML_NAME
    if not inpath.exists():
        abort(404)
    return Response(inpath.open().read(), mimetype=NEWICK_MIMETYPE)


@app.route('/trees/<family>.<sup>/<method>/' + PHYLOXML_NAME)
def get_phyloxml_tree_super(family, method, sup):
    return get_phyloxml_tree(family + '/' + sup, method)


@app.route('/trees/<familyname>/<method>/' + RUN_LOG_NAME)
def get_log(familyname, method):
    inpath = None
    if method in list(app.config['TREEBUILDERS'].keys()):
        inpath = Path(
            app.config['DATA_PATH']) / familyname / method / RUN_LOG_NAME
    elif method in list(app.config['ALIGNERS'].keys()):
        inpath = Path(app.config['DATA_PATH']) / familyname / RUN_LOG_NAME
    else:
        abort(428)
    if not inpath.exists():
        abort(404)
    return Response(inpath.open().read(), mimetype=TEXT_MIMETYPE)


@app.route('/trees/<family>.<sup>/<method>/' + RUN_LOG_NAME)
def get_log_super(family, method, sup):
    return get_log(family + '/' + sup, method)


@app.route('/trees/<familyname>/<method>/status')
def get_status(familyname, method):
    inpath = None
    if method in list(app.config['TREEBUILDERS'].keys()):
        inpath = Path(
            app.config['DATA_PATH']) / familyname / method / STATUS_NAME
    elif method in list(app.config['ALIGNERS'].keys()):
        inpath = Path(app.config['DATA_PATH']) / familyname / STATUS_NAME
    else:
        abort(428)
    if not inpath.exists():
        abort(404)
    status = inpath.open().read()
    return status


@app.route('/trees/<family>.<sup>/<method>/status')
def get_status_super(family, method, sup):
    return get_status(family + '/' + sup, method)
