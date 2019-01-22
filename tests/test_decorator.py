import os
import napkin


class TestDecorator(object):
    def test_seq_diagram(self, tmpdir):
        fname = os.path.join(str(tmpdir), 'sd')

        @napkin.seq_diagram(fname)
        def f(c):
            foo = c.object('foo')
            bar = c.object('bar')
            with foo:
                bar.func()
        napkin.generate()

        # Check diagram generate with fname
        assert os.stat(fname + '.puml')
