import os
import importlib
from . import sd

__version__ = '0.5.1'

# Note that the name should match to the module name.
SUPPORTED_FORMATS = ('plantuml', )
DEFAULT_FORAMT = SUPPORTED_FORMATS[0]

_collected_seq_diagrams = []


class seq_diagram:
    """
    Decorator to mark the sequence diagram function.

    'diagram_name' is the file name for the generated diagram. The name of
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


def generate(output_format=DEFAULT_FORAMT, output_dir='.'):
    """
    Generate sequence diagrams from all the decorated functions.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    gen_module = importlib.import_module('.' + output_format, 'napkin')
    for diagram in _collected_seq_diagrams:
        fname = diagram.name + '.uml'
        output_path = os.path.join(output_dir, fname)
        context = sd.parse(diagram.sd_func)
        with open(output_path, 'w') as f:
            print('Generate sequence diagram : {}'.format(output_path))
            f.write(gen_module.generate(context))
