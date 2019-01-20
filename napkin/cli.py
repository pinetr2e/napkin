"""
Command line interface to generate sequence diagrams.
"""
import sys
import os
import argparse
from . import generate, SUPPORTED_FORMATS, DEFAULT_FORAMT


def _parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--output-format', '-f',
        default=DEFAULT_FORAMT, choices=SUPPORTED_FORMATS),
    parser.add_argument(
        '--output-dir', '-o', default='.')
    parser.add_argument(
        'dirs', nargs='+',
        help='Directory to find Python files containing diagrams')
    return parser.parse_args()


def _import_script(fname):
    with open(fname, 'rt') as f:
        file_contents = f.read()
        if '@napkin.seq_diagram' in file_contents:
            print('Load file : {}'.format(fname))
            exec(compile(file_contents, fname, 'exec'), globals(), locals())


def _collect_py_files(py_dirs):
    collected = []
    for d in py_dirs:
        for root, dirs, files in os.walk(d):
            collected += [os.path.join(root, f)
                          for f in files if f.endswith('.py')]
    return collected


def main():
    args = _parse_args()
    for fname in _collect_py_files(args.dirs):
        _import_script(fname)
    generate(args.output_format, args.output_dir)
