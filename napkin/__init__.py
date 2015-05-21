import os
from . import plantuml
#
# Decorators
#
collected_seq_diagrams = []

class seq_diagram:
    def __init__(self, diagram_name=None):
        self.diagram_name = diagram_name

    def __call__(self, wrapped_func):
        if not self.diagram_name:
            self.diagram_name = wrapped_func.__name__
        self.sd_func = wrapped_func
        collected_seq_diagrams.append(self)

def generate_collected_datagrams():
    for d in collected_seq_diagrams:
        fname = d.diagram_name + '.uml'
        with open(fname, 'w') as f:
            print 'Generate sequence diagram : ' + fname
            f.write(plantuml.generate_sd(d.sd_func))
