import pytest

from napkin import sd
from napkin import sd_action
from napkin.sd import Params


class TestParams:
    def test_empty(self):
        assert "" == str(sd.Params(tuple(), dict()))

    def test_args(self):
        assert "abc, def" == str(sd.Params(('abc', 'def'), dict()))

    def test_args_kargs(self):
        assert "abc, foo=1, bar=2" == str(sd.Params(('abc',),
                                                    dict(foo=1, bar=2)))


class TestBase(object):
    def check(self, context, exp_actions):
        actions = context.sequence

        # This is for better debugging
        assert str(actions) == str(exp_actions)
        assert actions == exp_actions


class TestTopLevel(TestBase):
    def test_call(self):
        c = sd.Context()

        foo = c.Object('foo')
        bar = c.Object('bar')
        with foo:
            bar.func()

        self.check(c, [
            sd_action.Call(foo, bar, 'func'),
            sd_action.ImplicitReturn(),
        ])

    def test_call_twice(self):
        c = sd.Context()

        foo = c.Object('foo')
        bar = c.Object('bar')
        with foo:
            bar.func()
            bar.func2()

        self.check(c, [
            sd_action.Call(foo, bar, 'func'),
            sd_action.ImplicitReturn(),
            sd_action.Call(foo, bar, 'func2'),
            sd_action.ImplicitReturn(),
        ])

    def test_call_with_return(self):
        c = sd.Context()

        foo = c.Object('foo')
        bar = c.Object('bar')
        with foo:
            bar.func().ret('val')

        self.check(c, [
            sd_action.Call(foo, bar, 'func'),
            sd_action.Return(Params(('val',))),
        ])

    def test_call_with_return_twice(self):
        c = sd.Context()

        foo = c.Object('foo')
        bar = c.Object('bar')
        with foo:
            bar.func().ret('val')
            bar.func2().ret('val2')

        self.check(c, [
            sd_action.Call(foo, bar, 'func'),
            sd_action.Return(Params(('val',))),
            sd_action.Call(foo, bar, 'func2'),
            sd_action.Return(Params(('val2',))),
        ])

    def test_fail_when_separate_return_called(self):
        c = sd.Context()

        foo = c.Object('foo')
        bar = c.Object('bar')
        with foo:
            bar.func()
            with pytest.raises(sd.CallError):
                c.ret()

    def test_fail_when_top_level_caller_set_twice(self):
        c = sd.Context()

        foo = c.Object('foo')
        bar = c.Object('bar')
        with foo:
            bar.func()
            with pytest.raises(sd.TopLevelCallerError):
                with foo:
                    bar.func()

    def test_noop_when_do_nothing_in_top_level_caller(self):
        c = sd.Context()

        foo = c.Object('foo')
        with foo:
            pass

        self.check(c, [
        ])


class TestInsideFirstFunc(TestBase):
    def test_call(self):
        c = sd.Context()

        foo = c.Object('foo')
        bar = c.Object('bar')
        baz = c.Object('baz')
        with foo:
            with bar.func():
                baz.func2()

        self.check(c, [
            sd_action.Call(foo, bar, 'func'),
            sd_action.Call(bar, baz, 'func2'),
            sd_action.ImplicitReturn(),
            sd_action.ImplicitReturn(),
        ])

    def test_call_twice(self):
        c = sd.Context()

        foo = c.Object('foo')
        bar = c.Object('bar')
        baz = c.Object('baz')
        with foo:
            with bar.func():
                baz.func2()
                baz.func3()

        self.check(c, [
            sd_action.Call(foo, bar, 'func'),
            sd_action.Call(bar, baz, 'func2'),
            sd_action.ImplicitReturn(),
            sd_action.Call(bar, baz, 'func3'),
            sd_action.ImplicitReturn(),
            sd_action.ImplicitReturn(),
        ])

    def test_call_with_return(self):
        c = sd.Context()

        foo = c.Object('foo')
        bar = c.Object('bar')
        baz = c.Object('baz')
        with foo:
            with bar.func():
                baz.func2().ret()

        self.check(c, [
            sd_action.Call(foo, bar, 'func'),
            sd_action.Call(bar, baz, 'func2'),
            sd_action.Return(),
            sd_action.ImplicitReturn(),
        ])

    def test_return_from_outside_func(self):
        c = sd.Context()

        foo = c.Object('foo')
        bar = c.Object('bar')
        baz = c.Object('baz')
        with foo:
            with bar.func():
                baz.func2()
                c.ret()

        self.check(c, [
            sd_action.Call(foo, bar, 'func'),
            sd_action.Call(bar, baz, 'func2'),
            sd_action.ImplicitReturn(),
            sd_action.Return(),
        ])

    def test_fail_when_call_after_returning_from_outside_func(self):
        c = sd.Context()

        foo = c.Object('foo')
        bar = c.Object('bar')
        baz = c.Object('baz')
        with foo:
            with bar.func():
                baz.func2()
                c.ret()
                with pytest.raises(sd.CallError):
                    baz.func3()

    def test_fail_when_return_again_from_outside_func(self):
        c = sd.Context()

        foo = c.Object('foo')
        bar = c.Object('bar')
        baz = c.Object('baz')
        with foo:
            with bar.func():
                baz.func2()
                c.ret()
                with pytest.raises(sd.ReturnError):
                    c.ret()

    def test_return_from_outside_func_without_calling_any(self):
        c = sd.Context()

        foo = c.Object('foo')
        bar = c.Object('bar')
        with foo:
            with bar.func():
                c.ret()

        self.check(c, [
            sd_action.Call(foo, bar, 'func'),
            sd_action.Return(),
        ])

    def test_do_nothing_in_outside_func(self):
        c = sd.Context()

        foo = c.Object('foo')
        bar = c.Object('bar')
        with foo:
            with bar.func():
                pass

        self.check(c, [
            sd_action.Call(foo, bar, 'func'),
            sd_action.ImplicitReturn(),
        ])
