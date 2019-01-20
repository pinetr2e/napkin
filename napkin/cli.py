"""
Command line interface to generate sequence diagrams.
"""
import os
import argparse
import re
from . import generate, SUPPORTED_FORMATS, DEFAULT_FORAMT, __version__


def _parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--output-format', '-f',
        default=DEFAULT_FORAMT, choices=SUPPORTED_FORMATS),
    parser.add_argument(
        '--output-dir', '-o', default='.')
    parser.add_argument(
        'srcs', nargs='+',
        help='Directory or file to find Python files containing diagrams')
    parser.add_argument(
        '--version', action='version', version=__version__)
    return parser.parse_args()


def _import_script(fname):
    with open(fname, 'rt') as f:
        file_contents = f.read()
        if '@napkin.seq_diagram' in file_contents:
            print('Load file : {}'.format(fname))
            exec(compile(file_contents, fname, 'exec'), globals(), locals())


def _collect_py_files(srcs):
    collected = []
    for src in srcs:
        if os.path.isdir(src):
            for root, dirs, files in os.walk(src):
                collected += [os.path.join(root, f)
                              for f in files if re.match(r'\w*\.py$', f)]
        else:
            collected.append(src)
    return collected


def main():
    args = _parse_args()
    for fname in _collect_py_files(args.srcs):
        _import_script(fname)
    generate(args.output_format, args.output_dir)
