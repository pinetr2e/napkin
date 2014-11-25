import sys
from os import path
cur_path = path.dirname(path.abspath(__file__))
napkin_path = path.normpath(path.join(cur_path, '..'))
sys.path.append(napkin_path)


from napkin import plantuml


def sd_test(c):
    foo = c.Object('foo', cls='Account')
    bar = c.Object('bar', cls='Account')
    baz = c.Object('baz')
    with foo:
        with c.opt():
            bar.func()
            with bar.func():
                baz.func()
                c.ret('a')

        with c.loop():
            bar.func().ret('value')

        with c.alt():
            with c.choice('a'):
                baz.func()
                with c.alt():
                    with c.choice('a'):
                        baz.func()
                    with c.choice('b'):
                        bar.func()
            with c.choice('b'):
                bar.func()


print plantuml.generate_sd(sd_test)
