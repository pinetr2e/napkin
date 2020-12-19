import pytest

from napkin import sd
from napkin import sd_action


class TestParams:
    def test_empty(self):
        assert "" == str(sd.Params(tuple(), dict()))

    def test_args(self):
        assert "abc, def" == str(sd.Params(('abc', 'def'), dict()))

    def test_args_kargs(self):
        assert "abc, foo=1" == str(sd.Params(('abc',),
                                             dict(foo=1)))


class TestBase(object):
    def check(self, context, exp_actions):
        actions = context._sequence

        # This is for better debugging
        assert str(actions) == str(exp_actions)
        assert actions == exp_actions


class TestTopLevel(TestBase):
    def test_call(self):
        c = sd.Context()

        foo = c.object('foo')
        bar = c.object('bar')
        with foo:
            bar.func()

        self.check(c, [
            sd_action.Call(foo, bar, 'func', sd.Params()),
            sd_action.ImplicitReturn(),
        ])

    def test_call_twice(self):
        c = sd.Context()

        foo = c.object('foo')
        bar = c.object('bar')
        with foo:
            bar.func()
            bar.func2()

        self.check(c, [
            sd_action.Call(foo, bar, 'func', sd.Params()),
            sd_action.ImplicitReturn(),
            sd_action.Call(foo, bar, 'func2', sd.Params()),
            sd_action.ImplicitReturn(),
        ])

    def test_call_with_return(self):
        c = sd.Context()

        foo = c.object('foo')
        bar = c.object('bar')
        with foo:
            bar.func().ret('val')

        self.check(c, [
            sd_action.Call(foo, bar, 'func', sd.Params()),
            sd_action.Return(sd.Params(('val',))),
        ])

    def test_call_with_return_twice(self):
        c = sd.Context()

        foo = c.object('foo')
        bar = c.object('bar')
        with foo:
            bar.func().ret('val')
            bar.func2().ret('val2')

        self.check(c, [
            sd_action.Call(foo, bar, 'func', sd.Params()),
            sd_action.Return(sd.Params(('val',))),
            sd_action.Call(foo, bar, 'func2', sd.Params()),
            sd_action.Return(sd.Params(('val2',))),
        ])

    def test_fail_when_separate_return_called(self):
        c = sd.Context()

        foo = c.object('foo')
        bar = c.object('bar')
        with foo:
            bar.func()
            with pytest.raises(sd.CallError):
                c.ret()

    def test_fail_when_top_level_caller_set_twice(self):
        c = sd.Context()

        foo = c.object('foo')
        bar = c.object('bar')
        with foo:
            bar.func()
            with pytest.raises(sd.TopLevelCallerError):
                with foo:
                    bar.func()

    def test_noop_when_do_nothing_in_top_level_caller(self):
        c = sd.Context()

        foo = c.object('foo')
        with foo:
            pass

        self.check(c, [
        ])


class TestSecondLevel(TestBase):
    def test_call(self):
        c = sd.Context()

        foo = c.object('foo')
        bar = c.object('bar')
        baz = c.object('baz')
        with foo:
            with bar.func():
                baz.func2()

        self.check(c, [
            sd_action.Call(foo, bar, 'func', sd.Params()),
            sd_action.Call(bar, baz, 'func2', sd.Params()),
            sd_action.ImplicitReturn(),
            sd_action.ImplicitReturn(),
        ])

    def test_call_twice(self):
        c = sd.Context()

        foo = c.object('foo')
        bar = c.object('bar')
        baz = c.object('baz')
        with foo:
            with bar.func():
                baz.func2()
                baz.func3()

        self.check(c, [
            sd_action.Call(foo, bar, 'func', sd.Params()),
            sd_action.Call(bar, baz, 'func2', sd.Params()),
            sd_action.ImplicitReturn(),
            sd_action.Call(bar, baz, 'func3', sd.Params()),
            sd_action.ImplicitReturn(),
            sd_action.ImplicitReturn(),
        ])

    def test_call_with_return(self):
        c = sd.Context()

        foo = c.object('foo')
        bar = c.object('bar')
        baz = c.object('baz')
        with foo:
            with bar.func():
                baz.func2().ret()

        self.check(c, [
            sd_action.Call(foo, bar, 'func', sd.Params()),
            sd_action.Call(bar, baz, 'func2', sd.Params()),
            sd_action.Return(sd.Params()),
            sd_action.ImplicitReturn(),
        ])

    def test_return_from_outside_func(self):
        c = sd.Context()

        foo = c.object('foo')
        bar = c.object('bar')
        baz = c.object('baz')
        with foo:
            with bar.func():
                baz.func2()
                c.ret()

        self.check(c, [
            sd_action.Call(foo, bar, 'func', sd.Params()),
            sd_action.Call(bar, baz, 'func2', sd.Params()),
            sd_action.ImplicitReturn(),
            sd_action.Return(sd.Params()),
        ])

    def test_fail_when_call_after_returning_from_outside_func(self):
        c = sd.Context()

        foo = c.object('foo')
        bar = c.object('bar')
        baz = c.object('baz')
        with foo:
            with bar.func():
                baz.func2()
                c.ret()
                with pytest.raises(sd.CallError):
                    baz.func3()

    def test_fail_when_return_again_from_outside_func(self):
        c = sd.Context()

        foo = c.object('foo')
        bar = c.object('bar')
        baz = c.object('baz')
        with foo:
            with bar.func():
                baz.func2()
                c.ret()
                with pytest.raises(sd.ReturnError):
                    c.ret()

    def test_return_from_outside_func_without_calling_any(self):
        c = sd.Context()

        foo = c.object('foo')
        bar = c.object('bar')
        with foo:
            with bar.func():
                c.ret()

        self.check(c, [
            sd_action.Call(foo, bar, 'func', sd.Params()),
            sd_action.Return(sd.Params()),
        ])

    def test_do_nothing_in_outside_func(self):
        c = sd.Context()

        foo = c.object('foo')
        bar = c.object('bar')
        with foo:
            with bar.func():
                pass

        self.check(c, [
            sd_action.Call(foo, bar, 'func', sd.Params()),
            sd_action.ImplicitReturn(),
        ])


class TestCreate(TestBase):
    def test_simple(self):
        c = sd.Context()

        foo = c.object('foo')
        bar = c.object('bar')
        with foo:
            c.create(bar)

        self.check(c, [
            sd_action.Call(foo, bar, '<<create>>', sd.Params(), flags='c'),
            sd_action.ImplicitReturn(),
        ])

    def test_non_default_method(self):
        c = sd.Context()

        foo = c.object('foo')
        bar = c.object('bar')
        with foo:
            c.create(bar.new())

        self.check(c, [
            sd_action.Call(foo, bar, 'new', sd.Params(), flags='c'),
            sd_action.ImplicitReturn(),
        ])

    def test_constructor_params(self):
        c = sd.Context()

        foo = c.object('foo')
        bar = c.object('bar')
        with foo:
            c.create(bar.new('a', name='bar'))

        self.check(c, [
            sd_action.Call(foo, bar, 'new',
                           params=sd.Params(('a',), dict(name='bar')),
                           flags='c'),
            sd_action.ImplicitReturn(),
        ])

    def test_call_others_in_constructor(self):
        c = sd.Context()

        foo = c.object('foo')
        bar = c.object('bar')
        baz = c.object('baz')
        with foo:
            with c.create(bar):
                baz.func()

        self.check(c, [
            sd_action.Call(foo, bar, '<<create>>', sd.Params(), flags='c'),
            sd_action.Call(bar, baz, 'func', sd.Params()),
            sd_action.ImplicitReturn(),
            sd_action.ImplicitReturn(),
        ])

    def test_fail_if_called_at_top_level(self):
        c = sd.Context()

        with pytest.raises(sd.CreateError):
            bar = c.object('bar')
            c.create(bar)

    def test_fail_if_create_object_already_being_used(self):
        c = sd.Context()

        foo = c.object('foo')
        bar = c.object('bar')
        with foo:
            bar.func()
            with pytest.raises(sd.CreateError):
                c.create(bar)

    def test_fail_if_create_object_twice(self):
        c = sd.Context()

        foo = c.object('foo')
        bar = c.object('bar')
        with foo:
            c.create(bar)
            with pytest.raises(sd.CreateError):
                c.create(bar)


class TestDestroy(TestBase):
    def test_simple(self):
        c = sd.Context()

        foo = c.object('foo')
        bar = c.object('bar')
        with foo:
            bar.func()
            c.destroy(bar)

        self.check(c, [
            sd_action.Call(foo, bar, 'func', sd.Params()),
            sd_action.ImplicitReturn(),
            sd_action.Call(foo, bar, '<<destroy>>', sd.Params(), flags='d'),
            sd_action.ImplicitReturn(),
        ])

    def test_fail_when_call_destroyed_object(self):
        c = sd.Context()

        foo = c.object('foo')
        bar = c.object('bar')
        with foo:
            c.destroy(bar)
            with pytest.raises(sd.CallError):
                bar.func()

    def test_call_other_methods_of_the_same_object_from_destructr(self):
        c = sd.Context()

        foo = c.object('foo')
        bar = c.object('bar')
        with foo:
            with c.destroy(bar):
                bar.func()

    def test_fail_when_destroy_twice_the_same_object(self):
        c = sd.Context()

        foo = c.object('foo')
        bar = c.object('bar')
        with foo:
            c.destroy(bar)
            with pytest.raises(sd.CallError):
                c.destroy(bar)

    def test_fail_if_called_at_top_level(self):
        c = sd.Context()

        foo = c.object('foo')
        with pytest.raises(sd.DestroyError):
            c.destroy(foo)


class TestNote(TestBase):
    def test_over_object_implicit(self):
        c = sd.Context()

        foo = c.object('foo')
        bar = c.object('bar')
        with foo:
            c.note('blah')
            bar.func()

        self.check(c, [
            sd_action.Note('blah', obj=foo),
            sd_action.Call(foo, bar, 'func', sd.Params()),
            sd_action.ImplicitReturn(),
        ])

    def test_over_object_explicit(self):
        c = sd.Context()

        foo = c.object('foo')
        bar = c.object('bar')
        with foo:
            foo.note('blah')
            bar.note('blah2')
            bar.func()

        self.check(c, [
            sd_action.Note('blah', obj=foo),
            sd_action.Note('blah2', obj=bar),
            sd_action.Call(foo, bar, 'func', sd.Params()),
            sd_action.ImplicitReturn(),
        ])

    def test_call_specific(self):
        c = sd.Context()

        foo = c.object('foo')
        bar = c.object('bar')
        baz = c.object('baz')
        with foo:
            bar.func().note('callee side note')
            baz.func().note(caller='caller side note',
                            callee='callee side note')
            baz.func2().note('note').ret('val')

        self.check(c, [
            sd_action.Call(foo, bar, 'func', sd.Params(),
                           notes=['callee side note', None]),
            sd_action.ImplicitReturn(),
            sd_action.Call(foo, baz, 'func', sd.Params(),
                           notes=['callee side note', 'caller side note']),
            sd_action.ImplicitReturn(),
            sd_action.Call(foo, baz, 'func2', sd.Params(),
                           notes=['note', None]),
            sd_action.Return(sd.Params(('val',))),
        ])
