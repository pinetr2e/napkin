from napkin import plantuml


class TestBase(object):
    def check(self, sd_func, exp_lines):
        exp_lines = '@startuml' + exp_lines + '@enduml\n'
        lines = plantuml.generate_sd(sd_func)
        assert lines == exp_lines


class TestSimpleCalls(TestBase):
    def test_call(self):
        def f(c):
            foo = c.object('foo')
            bar = c.object('bar')
            with foo:
                bar.func()

        self.check(f, """
participant foo
participant bar

foo -> bar : func()
""")

    def test_call_with_params(self):
        def f(c):
            foo = c.object('foo')
            bar = c.object('bar')
            with foo:
                bar.func('abc')

        self.check(f, """
participant foo
participant bar

foo -> bar : func(abc)
""")

    def test_call_with_return(self):
        def f(c):
            foo = c.object('foo')
            bar = c.object('bar')
            with foo:
                bar.func().ret()

        self.check(f, """
participant foo
participant bar

foo -> bar : func()
activate bar
foo <-- bar
deactivate bar
""")

    def test_call_twice(self):
        def f(c):
            foo = c.object('foo')
            bar = c.object('bar')
            baz = c.object('baz')
            with foo:
                bar.func()
                baz.func()

        self.check(f, """
participant foo
participant bar
participant baz

foo -> bar : func()
foo -> baz : func()
""")

    def test_call_two_level(self):
        def f(c):
            foo = c.object('foo')
            bar = c.object('bar')
            baz = c.object('baz')
            with foo:
                with bar.func():
                    baz.func()

        self.check(f, """
participant foo
participant bar
participant baz

foo -> bar : func()
activate bar
bar -> baz : func()
deactivate bar
""")

    def test_opt(self):
        def f(c):
            foo = c.object('foo')
            baz = c.object('baz')
            with foo:
                with c.opt():
                    baz.func()

        self.check(f, """
participant foo
participant baz

opt
foo -> baz : func()
end
""")

    def test_opt_with_condition(self):
        def f(c):
            foo = c.object('foo')
            baz = c.object('baz')
            with foo:
                with c.opt('is_ok'):
                    baz.func()

        self.check(f, """
participant foo
participant baz

opt is_ok
foo -> baz : func()
end
""")

    def test_alt(self):
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

        self.check(f, """
participant foo
participant bar
participant baz

alt a
foo -> baz : func()
else b
foo -> bar : func()
end
""")


class TestObjectWithClass(TestBase):
    def test_call(self):
        def f(c):
            a = c.object('a', cls='Foo')
            b = c.object('b', cls='Foo')
            with a:
                b.func()

        self.check(f, """
participant "a:Foo" as a
participant "b:Foo" as b

a -> b : func()
""")


class TestCreate(TestBase):
    def test_simple_call(self):
        def f(c):
            foo = c.object('foo')
            with foo:
                bar = c.object('bar')
                c.create(bar)

        self.check(f, """
participant foo
participant bar

create bar
foo -> bar : <<create>>
""")

    def test_call_in_constructor(self):
        def f(c):
            foo = c.object('foo')
            baz = c.object('baz')
            with foo:
                bar = c.object('bar')
                with c.create(bar):
                    baz.func()

        self.check(f, """
participant foo
participant baz
participant bar

create bar
foo -> bar : <<create>>
activate bar
bar -> baz : func()
deactivate bar
""")


class TestDestroy(TestBase):
    def test_simple_destroy(self):
        def f(c):
            foo = c.object('foo')
            bar = c.object('bar')
            with foo:
                bar.func()
                c.destroy(bar)

        self.check(f, """
participant foo
participant bar

foo -> bar : func()
foo -> bar : <<destroy>>
destroy bar
""")

    def test_call_in_destructor(self):
        def f(c):
            foo = c.object('foo')
            bar = c.object('bar')
            with foo:
                bar.func()
                with c.destroy(bar):
                    foo.end()

        self.check(f, """
participant foo
participant bar

foo -> bar : func()
foo -> bar : <<destroy>>
activate bar
bar -> foo : end()
deactivate bar
destroy bar
""")


class TestNote(TestBase):
    def test_over_object(self):
        def f(c):
            foo = c.object('foo')
            bar = c.object('bar')
            with foo:
                c.note('blah')
                bar.func()

        self.check(f, """
participant foo
participant bar

note over foo : blah
foo -> bar : func()
""")

    def test_multiple_line_text(self):
        def f(c):
            foo = c.object('foo')
            bar = c.object('bar')
            with foo:
                c.note('blah\nblah')
                bar.func()

        self.check(f, """
participant foo
participant bar

note over foo
blah
blah
end note
foo -> bar : func()
""")
