def test_opt(check_puml):
    def f(c):
        foo = c.object('foo')
        baz = c.object('baz')
        with foo:
            with c.opt():
                baz.func()

    check_puml(f, """
participant foo
participant baz

opt
foo -> baz : func()
end
""")


def test_opt_with_condition(check_puml):
    def f(c):
        foo = c.object('foo')
        baz = c.object('baz')
        with foo:
            with c.opt('is_ok'):
                baz.func()

    check_puml(f, """
participant foo
participant baz

opt is_ok
foo -> baz : func()
end
""")


def test_alt(check_puml):
    def f(c):
        foo = c.object('foo')
        bar = c.object('bar')
        baz = c.object('baz')
        with foo:
            with c.alt():
                with c.choice('a'):
                    baz.func()
                with c.choice('b'):
                    bar.func()

    check_puml(f, """
participant foo
participant bar
participant baz

alt a
foo -> baz : func()
else b
foo -> bar : func()
end
""")
