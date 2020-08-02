"""
Generate PlantUML script and image file
"""
import os
try:
    import plantuml
except ImportError:
    raise ImportError('plantuml package is required but not installed.\n'
                      'Please install it by "pip install plantuml"')
from . import gen_plantuml

DEFAULT_SERVER_URL = 'http://www.plantuml.com/plantuml'


def generate(diagram_name, output_dir, sd_context, options, image_type):
    server_url = options.get('server_url', DEFAULT_SERVER_URL)
    img_url = (server_url + ('' if server_url[-1] == '/' else '/') +
               image_type + '/')
    generated_files = gen_plantuml.generate(diagram_name,
                                            output_dir, sd_context, options)
    puml_path = generated_files[0]
    img_path = os.path.join(output_dir, diagram_name + '.' + image_type)
    if plantuml.PlantUML(img_url).processes_file(puml_path, img_path):
        generated_files.append(img_path)
    return generated_files
