import os
import argparse

from .gen_plantuml_img import generate_image

_DESCRIPTION = ('Simple tool to convert PlantUML text file into image file '
                'using server.')


def _parse_args():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=_DESCRIPTION)

    parser.add_argument('--server-url', help='Default is the public server')
    parser.add_argument('input_file', help='PlantUML text file ')
    parser.add_argument(
        'output_file',
        help=('Image file to generate. '
              'Note that the extension name decides the format.'))
    return parser.parse_args()


def main():
    args = _parse_args()
    _, image_type = os.path.splitext(args.output_file)
    generate_image(args.input_file, args.output_file, args.server_url)
