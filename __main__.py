import argparse
import napkin
import os

def main(args):
    if not len(args.dirs):
        args.dirs = ['.']

    collected_files = set()
    for root, dirs, files in os.walk("."):
        py_files = [f for f in files if f.endswith('.py')]
        for fname in py_files:
            fname = os.path.join(root, fname)
            with open(fname) as f:
                if '@napkin.seq_diagram' in f.read():
                    collected_files.add(fname)

    for fname in collected_files:
        print 'Process ... ', fname
        execfile(fname)


parser = argparse.ArgumentParser()
parser.add_argument('dirs', nargs='+',
                    help='Directory to find diagram definitions')
args = parser.parse_args()
main(args)



napkin.generate_collected_datagrams()
