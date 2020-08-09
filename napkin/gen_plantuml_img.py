"""
Generate PlantUML script and image file
"""
import os
import string
import base64
import zlib
import requests

from . import gen_plantuml

DEFAULT_SERVER_URL = 'http://www.plantuml.com/plantuml'

_BASE64_TO_PLANTUML = {ord(b): b2.encode() for b, b2 in zip(
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


def _get_image_type(output_image_file_name):
    _, ext = os.path.splitext(output_image_file_name)
    assert ext.startswith('.')
    return ext[1:]


def _get_server_url(server_url):
    if not server_url:
        return DEFAULT_SERVER_URL
    return server_url[:-1] if server_url.endswith('/') else server_url


def generate_image(plantuml_file_path, image_file_path, server_url=None):
    """
    Generate image file from plantuml text file using server.

    The type of image is determined by the extension name of image_file_path.
    Default public PlantUML server is used if server_url is None.
    """
    with open(plantuml_file_path, 'rt') as input_file:
        text_diagram = input_file.read()

    encoded_diagram = _encode_text_diagram(text_diagram)
    diagram_url = encoded_diagram.decode('utf-8')

    image_type = _get_image_type(image_file_path)
    server_url = _get_server_url(server_url)
    url = server_url + "/" + image_type + "/" + diagram_url
    response = requests.get(url)

    if response.status_code == 200:
        with open(image_file_path, 'wb') as output_file:
            output_file.write(response.content)
    else:
        response.raise_for_status()


def generate(diagram_name, output_dir, sd_context, options, image_type):
    """
    Generate both plantuml file and image file.
    """
    generated_files = gen_plantuml.generate(diagram_name,
                                            output_dir, sd_context, options)
    plantuml_file_path = generated_files[0]
    image_path = os.path.join(output_dir, diagram_name + '.' + image_type)
    generate_image(plantuml_file_path, image_path, options.get('server_url'))

    generated_files.append(image_path)
    return generated_files
