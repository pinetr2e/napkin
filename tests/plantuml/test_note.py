def test_over_object(check_puml):
    def f(c):
        foo = c.object('foo')
        bar = c.object('bar')
        with foo:
            c.note('blah')
            bar.func()

    check_puml(f, """
participant foo
participant bar

note over foo : blah
foo -> bar : func()
""")


def test_multiple_line_text(check_puml):
    def f(c):
        foo = c.object('foo')
        bar = c.object('bar')
        with foo:
            c.note('blah\nblah')
            bar.func()

    check_puml(f, """
participant foo
participant bar

note over foo
blah
blah
end note
foo -> bar : func()
""")


def test_callee_caller(check_puml):
    def f(c):
        foo = c.object('foo')
        bar = c.object('bar')
        with foo:
            bar.func().note(callee='callee side', caller='caller side')

    check_puml(f, """
participant foo
participant bar

foo -> bar : func()
note right : callee side
note left : caller side
""")
