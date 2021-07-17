"""
Basic examples
"""
import napkin


@napkin.seq_diagram('Objects and calls')
def ex_calls(c):
    # All objects to be used should be defined first
    foo = c.object('Foo')
    bar = c.object('Bar')

    # Top level 'with' specifies the caller.
    with foo:
        # <object>.<func name>() means <func name> call to the object
        bar.funcName()
        # <object> can be the caller, which means call to self
        foo.otherFuncName()

    # Now switches the caller to other object
    with bar:
        # Functions with parameters
        foo.doSomething("paramFoo", paramBar="value", paramBaz=4)


@napkin.seq_diagram('Nested calls')
def ex_nc(c):
    foo = c.object('Foo')
    bar = c.object('Bar')
    baz = c.object('Baz')

    with foo:
        with bar.func():
            baz.func2()


@napkin.seq_diagram('Calls with return value')
def ex_cwr(c):
    foo = c.object('Foo')
    bar = c.object('Bar')

    with foo:
        # Simple call/return
        bar.func().ret('v1')

        with bar.func():
            bar.other_func()
            c.ret('v2')


@napkin.seq_diagram('Pass other object to call')
def ex_poc(c):
    foo = c.object('Foo')
    bar = c.object('Bar')
    baz = c.object('Baz')

    with foo:
        bar.DoSomething(baz, "other value")


@napkin.seq_diagram('Specify class, object and stereotype')
def ex_scos(c):
    foo = c.object('firstInstance', cls='Foo')
    bar = c.object('Bar', stereotype='active')
    baz = c.object('other', stereotype='external', cls='Baz')

    with foo:
        bar.doA()
        baz.doB()


@napkin.seq_diagram('Loop')
def ex_loop(c):
    foo = c.object('Foo')
    bar = c.object('Bar')

    with c.loop():
        with foo:
            bar.func()
            with c.loop('until done'):
                foo.func_other()


@napkin.seq_diagram('Opt')
def ex_opt(c):
    foo = c.object('Foo')
    bar = c.object('Bar')
    with c.opt():
        with foo:
            bar.func()
            with c.opt('some condition'):
                bar.func_other()


@napkin.seq_diagram('Message grouping')
def ex_group(c):
    foo = c.object('Foo')
    bar = c.object('Bar')
    with foo:
        with c.group():
            bar.func()
        with c.group('own label'):
            bar.func()


@napkin.seq_diagram('Alt')
def ex_alt(c):
    foo = c.object('Foo')
    bar = c.object('Bar')
    baz = c.object('Baz')

    with c.alt():
        with c.choice('ok'):
            with foo:
                bar.func()
        with c.choice('else'):
            with foo:
                baz.func()


@napkin.seq_diagram('Create and destroy object')
def ex_cd(c):
    foo = c.object('Foo')
    bar = c.object('Bar')
    with foo:
        c.create(bar)
        bar.func()
        c.destroy(bar)


@napkin.seq_diagram('Notes')
def ex_notes(c):
    foo = c.object('Foo')
    bar = c.object('Bar')
    baz = c.object('Baz')

    foo.note('Note over object')
    bar.note('Note over object')

    with foo:
        c.note('Note over the current context')
        with bar.very_long_name_function():
            c.note('Note over the current context with\n'
                   'multiple lines')
            baz.another_very_long_name_function()

    # Note per call
    with foo:
        bar.func1().note('callee side notes')
        bar.func2().note(caller='caller side notes')
        bar.func3().note(callee='callee side notes',
                         caller=('caller side notes over\n'
                                 'multiple lines'))
        # For self call
        foo.func4().note(callee='callee side of self-call',
                         caller='caller side of self-call')


@napkin.seq_diagram('Delay')
def ex_delay(c):
    foo = c.object('Foo')
    bar = c.object('Bar')

    with foo:
        bar.func1()
        c.delay()
        bar.func2()
        c.delay('with text')
        bar.func3()


@napkin.seq_diagram('Divider')
def ex_divider(c):
    foo = c.object('Foo')
    bar = c.object('Bar')

    with foo:
        bar.func1()
        c.divide()
        bar.func2()
        c.divide('with text')
        bar.func3()


@napkin.seq_diagram('Call from outside')
def ex_outside(c):
    foo = c.object('Foo')

    with c.outside():
        foo.hello().ret('v')

    with c.outside(from_right=True):
        foo.hello().ret('v2')


@napkin.seq_diagram('Raw header')
def ex_raw_header(c):
    c.raw_header("""
    skinparam handwritten true
    skinparam monochrome true""")
    foo = c.object('Foo')
    bar = c.object('Bar')
    with foo:
        bar.hello()


if __name__ == '__main__':
    import helper
    helper.generate_markdown_file('Basic Examples', __file__)
