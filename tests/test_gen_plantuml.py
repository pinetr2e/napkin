import pytest
from napkin import gen_plantuml
from napkin import sd


@pytest.fixture
def check(tmpdir):
    def fn(sd_func, exp_lines):
        exp_lines = '@startuml' + exp_lines + '@enduml\n'
        sd_context = sd.parse(sd_func)
        puml_file = gen_plantuml.generate(str(tmpdir), 'test', sd_context)[0]
        with open(puml_file, 'rt') as f:
            lines = f.read()
        assert lines == exp_lines
    return fn


class TestSimpleCalls:
    def test_call(self, check):
        def f(c):
            foo = c.object('foo')
            bar = c.object('bar')
            with foo:
                bar.func()

        check(f, """
participant foo
participant bar

foo -> bar : func()
""")

    def test_call_with_params(self, check):
        def f(c):
            foo = c.object('foo')
            bar = c.object('bar')
            with foo:
                bar.func('abc')
                bar.func2(key='value')

        check(f, """
participant foo
participant bar

foo -> bar : func(abc)
foo -> bar : func2(key=value)
""")

    def test_call_with_return(self, check):
        def f(c):
            foo = c.object('foo')
            bar = c.object('bar')
            with foo:
                bar.func().ret()

        check(f, """
participant foo
participant bar

foo -> bar : func()
activate bar
foo <-- bar
deactivate bar
""")

    def test_call_twice(self, check):
        def f(c):
            foo = c.object('foo')
            bar = c.object('bar')
            baz = c.object('baz')
            with foo:
                bar.func()
                baz.func()

        check(f, """
participant foo
participant bar
participant baz

foo -> bar : func()
foo -> baz : func()
""")

    def test_call_two_level(self, check):
        def f(c):
            foo = c.object('foo')
            bar = c.object('bar')
            baz = c.object('baz')
            with foo:
                with bar.func():
                    baz.func()

        check(f, """
participant foo
participant bar
participant baz

foo -> bar : func()
activate bar
bar -> baz : func()
deactivate bar
""")

    def test_opt(self, check):
        def f(c):
            foo = c.object('foo')
            baz = c.object('baz')
            with foo:
                with c.opt():
                    baz.func()

        check(f, """
participant foo
participant baz

opt
foo -> baz : func()
end
""")

    def test_opt_with_condition(self, check):
        def f(c):
            foo = c.object('foo')
            baz = c.object('baz')
            with foo:
                with c.opt('is_ok'):
                    baz.func()

        check(f, """
participant foo
participant baz

opt is_ok
foo -> baz : func()
end
""")

    def test_alt(self, check):
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

        check(f, """
participant foo
participant bar
participant baz

alt a
foo -> baz : func()
else b
foo -> bar : func()
end
""")


class TestObjectWithClassAndStereotype:
    def test_call(self, check):
        def f(c):
            a = c.object('a', cls='Foo')
            b = c.object('b', cls='Foo', stereotype='foo')
            with a:
                b.func()

        check(f, """
participant "a:Foo" as a
participant "b:Foo" as b <<foo>>

a -> b : func()
""")


class TestCreate:
    def test_simple_call(self, check):
        def f(c):
            foo = c.object('foo')
            with foo:
                bar = c.object('bar')
                c.create(bar)

        check(f, """
participant foo
participant bar

create bar
foo -> bar : <<create>>
""")

    def test_call_in_constructor(self, check):
        def f(c):
            foo = c.object('foo')
            baz = c.object('baz')
            with foo:
                bar = c.object('bar')
                with c.create(bar):
                    baz.func()

        check(f, """
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
    def test_simple_destroy(self, check):
        def f(c):
            foo = c.object('foo')
            bar = c.object('bar')
            with foo:
                bar.func()
                c.destroy(bar)

        check(f, """
participant foo
participant bar

foo -> bar : func()
foo -> bar : <<destroy>>
destroy bar
""")

    def test_call_in_destructor(self, check):
        def f(c):
            foo = c.object('foo')
            bar = c.object('bar')
            with foo:
                bar.func()
                with c.destroy(bar):
                    foo.end()

        check(f, """
participant foo
participant bar

foo -> bar : func()
foo -> bar : <<destroy>>
activate bar
bar -> foo : end()
deactivate bar
destroy bar
""")


class TestNote:
    def test_over_object(self, check):
        def f(c):
            foo = c.object('foo')
            bar = c.object('bar')
            with foo:
                c.note('blah')
                bar.func()

        check(f, """
participant foo
participant bar

note over foo : blah
foo -> bar : func()
""")

    def test_multiple_line_text(self, check):
        def f(c):
            foo = c.object('foo')
            bar = c.object('bar')
            with foo:
                c.note('blah\nblah')
                bar.func()

        check(f, """
participant foo
participant bar

note over foo
blah
blah
end note
foo -> bar : func()
""")

    def test_callee_caller(self, check):
        def f(c):
            foo = c.object('foo')
            bar = c.object('bar')
            with foo:
                bar.func().note(callee='callee side', caller='caller side')

        check(f, """
participant foo
participant bar

foo -> bar : func()
note right : callee side
note left : caller side
""")


class TestDelay:
    def test_without_text(self, check):
        def f(c):
            foo = c.object('foo')
            bar = c.object('bar')
            with foo:
                bar.func()
            c.delay()

        check(f, """
participant foo
participant bar

foo -> bar : func()
...
""")

    def test_with_text(self, check):
        def f(c):
            foo = c.object('foo')
            bar = c.object('bar')
            with foo:
                bar.func()
            c.delay('hello')

        check(f, """
participant foo
participant bar

foo -> bar : func()
... hello ...
""")


class TestDivide:
    def test_without_text(self, check):
        def f(c):
            foo = c.object('foo')
            bar = c.object('bar')
            with foo:
                bar.func()
                c.divide()
                bar.func2()

        check(f, """
participant foo
participant bar

foo -> bar : func()
====
foo -> bar : func2()
""")

    def test_with_text(self, check):
        def f(c):
            foo = c.object('foo')
            bar = c.object('bar')
            with foo:
                bar.func()
                c.divide('hello')
                bar.func2()

        check(f, """
participant foo
participant bar

foo -> bar : func()
== hello ==
foo -> bar : func2()
""")

    def test_group(self, check):
        def f(c):
            foo = c.object('foo')
            baz = c.object('baz')
            with foo:
                with c.group():
                    baz.func()

        check(f, """
participant foo
participant baz

group
foo -> baz : func()
end
""")

    def test_group_with_label(self, check):
        def f(c):
            foo = c.object('foo')
            baz = c.object('baz')
            with foo:
                with c.group('label'):
                    baz.func()

        check(f, """
participant foo
participant baz

group label
foo -> baz : func()
end
""")
