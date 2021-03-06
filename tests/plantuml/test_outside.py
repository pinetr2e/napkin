def test_calling_from_outside(check_puml):
    def f(c):
        foo = c.object('foo')
        with c.outside():
            foo.func()

    check_puml(f, """
participant foo

[-> foo : func()
""")


def test_return_to_outside(check_puml):
    def f(c):
        foo = c.object('foo')
        with c.outside():
            foo.func().ret()

    check_puml(f, """
participant foo

[-> foo : func()
activate foo
[<-- foo
deactivate foo
""")


def test_from_right_hand_side(check_puml):
    def f(c):
        foo = c.object('foo')
        with c.outside(from_right=True):
            foo.func().ret()

    check_puml(f, """
participant foo

]-> foo : func()
activate foo
]<-- foo
deactivate foo
""")
