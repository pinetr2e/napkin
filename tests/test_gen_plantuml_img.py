import os
import napkin
import pytest

pytest.importorskip("plantuml")


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
