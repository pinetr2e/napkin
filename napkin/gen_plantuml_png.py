"""
Generate PlantUML script and PNG file
"""
import os
try:
    import plantuml
except ImportError:
    raise ImportError('plantuml package is required but not yet installed.\n'
                      'Please install it by "pip install plantuml"')
from . import gen_plantuml


def generate(diagram_name, output_dir, sd_context):

    generated_files = gen_plantuml.generate(diagram_name,
                                            output_dir, sd_context)
    puml_path = generated_files[0]
    png_path = os.path.join(output_dir, diagram_name + '.png')
    if plantuml.PlantUML(plantuml.SERVER_URL).processes_file(puml_path, png_path):
        generated_files.append(png_path)
    return generated_files
