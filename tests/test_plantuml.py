from napkin import plantuml


class TestBase(object):
    def check(self, sd_func, exp_lines):
        exp_lines = '@startuml' + exp_lines + '@enduml\n'
        lines = plantuml.generate_sd(sd_func)
        assert lines == exp_lines


class TestSimpleCalls(TestBase):
    def test_call(self):
        def f(c):
            foo = c.Object('foo')
            bar = c.Object('bar')
            with foo:
                bar.func()

        self.check(f, """
foo -> bar : func()
""")

    def test_call_with_params(self):
        def f(c):
            foo = c.Object('foo')
            bar = c.Object('bar')
            with foo:
                bar.func('abc')

        self.check(f, """
foo -> bar : func(abc)
""")

    def test_call_with_return(self):
        def f(c):
            foo = c.Object('foo')
            bar = c.Object('bar')
            with foo:
                bar.func().ret()

        self.check(f, """
foo -> bar : func()
activate bar
foo <-- bar
deactivate bar
""")

    def test_call_twice(self):
        def f(c):
            foo = c.Object('foo')
            bar = c.Object('bar')
            baz = c.Object('baz')
            with foo:
                bar.func()
                baz.func()

        self.check(f, """
foo -> bar : func()
foo -> baz : func()
""")

    def test_call_two_level(self):
        def f(c):
            foo = c.Object('foo')
            bar = c.Object('bar')
            baz = c.Object('baz')
            with foo:
                with bar.func():
                    baz.func()

        self.check(f, """
foo -> bar : func()
activate bar
bar -> baz : func()
deactivate bar
""")

    def test_opt(self):
        def f(c):
            foo = c.Object('foo')
            baz = c.Object('baz')
            with foo:
                with c.opt():
                    baz.func()

        self.check(f, """
opt
foo -> baz : func()
end
""")

    def test_opt_with_condition(self):
        def f(c):
            foo = c.Object('foo')
            baz = c.Object('baz')
            with foo:
                with c.opt('is_ok'):
                    baz.func()

        self.check(f, """
opt is_ok
foo -> baz : func()
end
""")

    def test_alt(self):
        def f(c):
            foo = c.Object('foo')
            bar = c.Object('bar')
            baz = c.Object('baz')
            with foo:
                with c.alt():
                    with c.choice('a'):
                        baz.func()
                    with c.choice('b'):
                        bar.func()

        self.check(f, """
alt a
foo -> baz : func()
else b
foo -> bar : func()
end
""")
