"""
Generate PlantUML script and image file
"""
import os
import string
import base64
import zlib
import requests
import six

from . import gen_plantuml

DEFAULT_SERVER_URL = 'http://www.plantuml.com/plantuml'

_BASE64_TO_PLANTUML = {b if six.PY2 else ord(b): b2.encode() for b, b2 in zip(
    string.ascii_uppercase + string.ascii_lowercase + string.digits + '+/=',
    string.digits + string.ascii_uppercase + string.ascii_lowercase + '-_=')}


def _encode_text_diagram(text_diagram):
    """
    Encode text diagram with zlib/plantuml specific b64 encoding.

    The text diagram is:
    - Encoded in UTF-8
    - Compressed using Deflate algorithm
    - Re-encoded in ASCII using a transformation close to base64

    See https://plantuml.com/text-encoding:
    """
    utf_encoded = text_diagram.encode('utf-8')
    compressed = zlib.compress(utf_encoded)
    # Remove zlib header CMF/CM[2 bytes] and CRC[4 bytes] (RFC1950). Note that
    # Python zlib retains those but Java.util.zip.Inflater from PlantUML server
    # does not expect them.
    compressed = compressed[2:-4]
    b64_encoded = base64.b64encode(compressed)
    return b''.join(_BASE64_TO_PLANTUML[b] for b in b64_encoded)


def _generate_image(text_diagram, server_url, image_type, image_path):
    encoded_diagram = _encode_text_diagram(text_diagram)
    diagram_url = encoded_diagram.decode('utf-8')

    img_url = server_url + image_type + "/" + diagram_url
    response = requests.get(img_url)
    if response.status_code == 200:
        with open(image_path, 'wb') as f:
            f.write(response.content)
    else:
        response.raise_for_status()


def generate(diagram_name, output_dir, sd_context, options, image_type):
    generated_files = gen_plantuml.generate(diagram_name,
                                            output_dir, sd_context, options)
    puml_path = generated_files[0]
    with open(puml_path, 'rt') as f:
        text_diagram = f.read()

    server_url = options.get('server_url', DEFAULT_SERVER_URL)
    if not server_url.endswith('/'):
        server_url += '/'

    image_path = os.path.join(output_dir, diagram_name + '.' + image_type)
    _generate_image(text_diagram, server_url, image_type, image_path)
    return generated_files
