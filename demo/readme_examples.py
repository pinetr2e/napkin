"""
Basic examples
"""
import napkin


@napkin.seq_diagram('nested calls')
def ex_nc(c):
    foo = c.object('foo')
    bar = c.object('bar')
    baz = c.object('baz')

    with foo:
        with bar.func():
            baz.func2()


@napkin.seq_diagram('calls with return value')
def ex_cwr(c):
    foo = c.object('foo')
    bar = c.object('bar')

    with foo:
        # Simple call/return
        bar.func().ret('v1')

        with bar.func():
            bar.other_func()
            c.ret('v2')


@napkin.seq_diagram('pass other object to call')
def ex_poc(c):
    foo = c.object('foo')
    bar = c.object('bar')
    baz = c.object('baz')

    with foo:
        bar.DoSomething(baz, "other value")


@napkin.seq_diagram('loop')
def ex_loop(c):
    foo = c.object('foo')
    bar = c.object('bar')

    with c.loop():
        with foo:
            bar.func()
            with c.loop('until done'):
                foo.func_other()


@napkin.seq_diagram('alt')
def ex_alt(c):
    foo = c.object('foo')
    bar = c.object('bar')
    baz = c.object('baz')

    with c.alt():
        with c.choice('ok'):
            with foo:
                bar.func()
        with c.choice('else'):
            with foo:
                baz.func()


@napkin.seq_diagram('create and destroy object')
def ex_cd(c):
    foo = c.object('foo')
    bar = c.object('bar')
    with foo:
        c.create(bar)
        bar.func()
        c.destroy(bar)
