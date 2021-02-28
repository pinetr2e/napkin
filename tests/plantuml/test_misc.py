class TestDelay:
    def test_without_text(self, check_puml):
        def f(c):
            foo = c.object('foo')
            bar = c.object('bar')
            with foo:
                bar.func()
            c.delay()

        check_puml(f, """
participant foo
participant bar

foo -> bar : func()
...
""")

    def test_with_text(self, check_puml):
        def f(c):
            foo = c.object('foo')
            bar = c.object('bar')
            with foo:
                bar.func()
            c.delay('hello')

        check_puml(f, """
participant foo
participant bar

foo -> bar : func()
... hello ...
""")


class TestDivide:
    def test_without_text(self, check_puml):
        def f(c):
            foo = c.object('foo')
            bar = c.object('bar')
            with foo:
                bar.func()
                c.divide()
                bar.func2()

        check_puml(f, """
participant foo
participant bar

foo -> bar : func()
====
foo -> bar : func2()
""")

    def test_with_text(self, check_puml):
        def f(c):
            foo = c.object('foo')
            bar = c.object('bar')
            with foo:
                bar.func()
                c.divide('hello')
                bar.func2()

        check_puml(f, """
participant foo
participant bar

foo -> bar : func()
== hello ==
foo -> bar : func2()
""")


class TestGroup:
    def test_group(self, check_puml):
        def f(c):
            foo = c.object('foo')
            baz = c.object('baz')
            with foo:
                with c.group():
                    baz.func()

        check_puml(f, """
participant foo
participant baz

group
foo -> baz : func()
end
""")

    def test_group_with_label(self, check_puml):
        def f(c):
            foo = c.object('foo')
            baz = c.object('baz')
            with foo:
                with c.group('label'):
                    baz.func()

        check_puml(f, """
participant foo
participant baz

group label
foo -> baz : func()
end
""")
