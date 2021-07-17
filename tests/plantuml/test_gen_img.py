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


def test_raw_header_file(tmpdir):
    sd_fname = os.path.join(str(tmpdir), 'sd')
    header_fname = os.path.join(str(tmpdir), 'header.txt')
    header_contents = 'skinparam monochrome true'

    with open(header_fname, 'w') as f:
        f.write(header_contents)

    @napkin.seq_diagram(sd_fname)
    def f(c):
        foo = c.object('foo')
        bar = c.object('bar')
        with foo:
            bar.func()

    napkin.generate(output_format='plantuml',
                    options={'raw_header_file': header_fname})
    with open(sd_fname + '.puml') as f:
        contents = f.read()
    assert('@startuml\n' + header_contents in contents)
