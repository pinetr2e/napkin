class TestSimpleCalls:
    def test_call(self, check_puml):
        def f(c):
            foo = c.object('foo')
            bar = c.object('bar')
            with foo:
                bar.func()

        check_puml(f, """
participant foo
participant bar

foo -> bar : func()
""")

    def test_call_with_params(self, check_puml):
        def f(c):
            foo = c.object('foo')
            bar = c.object('bar')
            with foo:
                bar.func('abc')
                bar.func2(key='value')

        check_puml(f, """
participant foo
participant bar

foo -> bar : func(abc)
foo -> bar : func2(key=value)
""")

    def test_call_with_return(self, check_puml):
        def f(c):
            foo = c.object('foo')
            bar = c.object('bar')
            with foo:
                bar.func().ret()

        check_puml(f, """
participant foo
participant bar

foo -> bar : func()
activate bar
foo <-- bar
deactivate bar
""")

    def test_call_twice(self, check_puml):
        def f(c):
            foo = c.object('foo')
            bar = c.object('bar')
            baz = c.object('baz')
            with foo:
                bar.func()
                baz.func()

        check_puml(f, """
participant foo
participant bar
participant baz

foo -> bar : func()
foo -> baz : func()
""")

    def test_call_two_level(self, check_puml):
        def f(c):
            foo = c.object('foo')
            bar = c.object('bar')
            baz = c.object('baz')
            with foo:
                with bar.func():
                    baz.func()

        check_puml(f, """
participant foo
participant bar
participant baz

foo -> bar : func()
activate bar
bar -> baz : func()
deactivate bar
""")


class TestObjectWithClassAndStereotype:
    def test_call(self, check_puml):
        def f(c):
            a = c.object('a', cls='Foo')
            b = c.object('b', cls='Foo', stereotype='foo')
            with a:
                b.func()

        check_puml(f, """
participant "a:Foo" as a
participant "b:Foo" as b <<foo>>

a -> b : func()
""")


class TestCreate:
    def test_simple_call(self, check_puml):
        def f(c):
            foo = c.object('foo')
            with foo:
                bar = c.object('bar')
                c.create(bar)

        check_puml(f, """
participant foo
participant bar

create bar
foo -> bar : <<create>>
""")

    def test_call_in_constructor(self, check_puml):
        def f(c):
            foo = c.object('foo')
            baz = c.object('baz')
            with foo:
                bar = c.object('bar')
                with c.create(bar):
                    baz.func()

        check_puml(f, """
participant foo
participant baz
participant bar

create bar
foo -> bar : <<create>>
activate bar
bar -> baz : func()
deactivate bar
""")


class TestDestroy:
    def test_simple_destroy(self, check_puml):
        def f(c):
            foo = c.object('foo')
            bar = c.object('bar')
            with foo:
                bar.func()
                c.destroy(bar)

        check_puml(f, """
participant foo
participant bar

foo -> bar : func()
foo -> bar : <<destroy>>
destroy bar
""")

    def test_call_in_destructor(self, check_puml):
        def f(c):
            foo = c.object('foo')
            bar = c.object('bar')
            with foo:
                bar.func()
                with c.destroy(bar):
                    foo.end()

        check_puml(f, """
participant foo
participant bar

foo -> bar : func()
foo -> bar : <<destroy>>
activate bar
bar -> foo : end()
deactivate bar
destroy bar
""")
