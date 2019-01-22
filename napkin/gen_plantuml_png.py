"""
Generate PlantUML script and PNG file
"""
import os
import plantuml
from . import gen_plantuml


def generate(diagram_name, output_dir, sd_context):
    generated_files = gen_plantuml.generate(diagram_name,
                                            output_dir, sd_context)
    puml_path = generated_files[0]
    png_path = os.path.join(output_dir, diagram_name + '.png')
    if plantuml.PlantUML().processes_file(puml_path, png_path):
        generated_files.append(png_path)
    return generated_files
