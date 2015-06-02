#!/bin/python

import argparse
import napkin
import os

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('dirs', nargs='+',
                        help='Directory to find diagram definitions')
    return parser.parse_args()

def main():
    args = parse_args()

    if not len(args.dirs):
        args.dirs = ['.']

    collected_files = set()
    for d in args.dirs:
        for root, dirs, files in os.walk(d):
            py_files = [f for f in files if f.endswith('.py')]
            for fname in py_files:
                fname = os.path.join(root, fname)
                with open(fname) as f:
                    if '@napkin.seq_diagram' in f.read():
                        collected_files.add(fname)

    for fname in collected_files:
        print 'Process ... ', fname
        execfile(fname)

    napkin.generate_collected_datagrams()

