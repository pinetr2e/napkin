import os
import importlib
import collections
from . import sd

__version__ = '0.6.7.2'

# Name and description.
# Note that the name should match to the module name, gen_<name>.
SUPPORTED_FORMATS = collections.OrderedDict()
SUPPORTED_FORMATS['plantuml'] = 'PlantUML script (default)'
SUPPORTED_FORMATS['plantuml_png'] = 'PlantUML script and PNG image'
SUPPORTED_FORMATS['plantuml_svg'] = 'PlantUML script and SVG image'
SUPPORTED_FORMATS['plantuml_txt'] = 'PlantUML script and ASCII art text'
DEFAULT_FORAMT = 'plantuml'

_collected_seq_diagrams = []


class seq_diagram:
    """
    Decorator to mark the sequence  function.

    'diagram_name' is the file name for the generated . The name of
    decorated function will be used if not specified.

    ex:
    @napkin.seq_diagram()
    def sd_simple(c):
       ...

    @napkin.seq_diagram('sd_another')
    def foo(c):
       ...
    """
    def __init__(self, name=None):
        self.name = name

    def __call__(self, wrapped_func):
        if not self.name:
            self.name = wrapped_func.__name__
        self.sd_func = wrapped_func
        _collected_seq_diagrams.append(self)


def generate(output_format=DEFAULT_FORAMT, output_dir='.', options=None):
    """
    Generate sequence diagrams from all the decorated functions.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    module_name = '.gen_' + output_format
    gen_module = importlib.import_module(module_name, 'napkin')

    for d in _collected_seq_diagrams:
        context = sd.parse(d.sd_func)
        generated_files = gen_module.generate(d.name, output_dir, context,
                                              options if options else {})
        print('File generated : {}'.format(', '.join(generated_files)))
