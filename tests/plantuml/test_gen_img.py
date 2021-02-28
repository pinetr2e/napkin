import os
import napkin
from napkin.gen_plantuml_img import _encode_text_diagram

DEFAULT_SERVER_URL = 'http://www.plantuml.com/plantuml'


def test_encode_text_diagram():
    text = """@startuml
Bob -> Alice : hello
@enduml"""
    exp = b'SoWkIImgAStDuNBAJrBGjLDmpCbCJbMmKiX8pSd9vt98pKi1IW80'
    act = _encode_text_diagram(text)
    assert exp == act


def test_png_generation(tmpdir):
    fname = os.path.join(str(tmpdir), 'sd')

    @napkin.seq_diagram(fname)
    def f(c):
        foo = c.object('foo')
        bar = c.object('bar')
        with foo:
            bar.func()

    napkin.generate(output_format='plantuml_png')
    assert os.stat(fname + '.puml')
    assert os.stat(fname + '.png')


def test_svg_generation(tmpdir):
    fname = os.path.join(str(tmpdir), 'sd')

    @napkin.seq_diagram(fname)
    def f(c):
        foo = c.object('foo')
        bar = c.object('bar')
        with foo:
            bar.func()

    napkin.generate(output_format='plantuml_svg')
    assert os.stat(fname + '.puml')
    assert os.stat(fname + '.svg')
