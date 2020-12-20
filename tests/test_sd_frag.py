import pytest

from napkin import sd
from napkin import sd_action


class TestBase(object):
    def check(self, context, exp_actions):
        actions = context._sequence

        # This is for better debugging
        assert str(actions) == str(exp_actions)
        assert actions == exp_actions


class TestOpt(TestBase):
    def test_top_level(self):
        c = sd.Context()

        foo = c.object('foo')
        bar = c.object('bar')

        with c.opt():
            with foo:
                bar.func()

        self.check(c, [
            sd_action.FragBegin('opt'),
            sd_action.Call(foo, bar, 'func', sd.Params()),
            sd_action.ImplicitReturn(),
            sd_action.FragEnd('opt'),
        ])

    def test_top_level_twice(self):
        c = sd.Context()

        foo = c.object('foo')
        bar = c.object('bar')

        with c.opt():
            with foo:
                bar.func()

        with c.opt():
            with foo:
                bar.func()

        self.check(c, [
            sd_action.FragBegin('opt'),
            sd_action.Call(foo, bar, 'func', sd.Params()),
            sd_action.ImplicitReturn(),
            sd_action.FragEnd('opt'),
            sd_action.FragBegin('opt'),
            sd_action.Call(foo, bar, 'func', sd.Params()),
            sd_action.ImplicitReturn(),
            sd_action.FragEnd('opt'),
        ])

    def test_inside_top_level(self):
        c = sd.Context()

        foo = c.object('foo')
        bar = c.object('bar')

        with foo:
            with c.opt():
                bar.func()

        self.check(c, [
            sd_action.FragBegin('opt'),
            sd_action.Call(foo, bar, 'func', sd.Params()),
            sd_action.ImplicitReturn(),
            sd_action.FragEnd('opt'),
        ])

    def test_inside_top_level_twice(self):
        c = sd.Context()

        foo = c.object('foo')
        bar = c.object('bar')

        with foo:
            with c.opt():
                bar.func()
            with c.opt():
                bar.func()

        self.check(c, [
            sd_action.FragBegin('opt'),
            sd_action.Call(foo, bar, 'func', sd.Params()),
            sd_action.ImplicitReturn(),
            sd_action.FragEnd('opt'),
            sd_action.FragBegin('opt'),
            sd_action.Call(foo, bar, 'func', sd.Params()),
            sd_action.ImplicitReturn(),
            sd_action.FragEnd('opt'),
        ])

    def test_inside_func_call(self):
        c = sd.Context()

        foo = c.object('foo')
        bar = c.object('bar')
        baz = c.object('baz')

        with foo:
            with bar.func():
                with c.opt():
                    baz.func()

        self.check(c, [
            sd_action.Call(foo, bar, 'func', sd.Params()),
            sd_action.FragBegin('opt'),
            sd_action.Call(bar, baz, 'func', sd.Params()),
            sd_action.ImplicitReturn(),
            sd_action.FragEnd('opt'),
            sd_action.ImplicitReturn(),
        ])

    def test_inside_func_call_twice(self):
        c = sd.Context()

        foo = c.object('foo')
        bar = c.object('bar')
        baz = c.object('baz')

        with foo:
            with bar.func():
                with c.opt():
                    baz.func()
                with c.opt():
                    baz.func()

        self.check(c, [
            sd_action.Call(foo, bar, 'func', sd.Params()),
            sd_action.FragBegin('opt'),
            sd_action.Call(bar, baz, 'func', sd.Params()),
            sd_action.ImplicitReturn(),
            sd_action.FragEnd('opt'),
            sd_action.FragBegin('opt'),
            sd_action.Call(bar, baz, 'func', sd.Params()),
            sd_action.ImplicitReturn(),
            sd_action.FragEnd('opt'),
            sd_action.ImplicitReturn(),
        ])

    def test_with_condition(self):
        c = sd.Context()

        foo = c.object('foo')
        bar = c.object('bar')

        with c.opt('condition'):
            with foo:
                bar.func()

        self.check(c, [
            sd_action.FragBegin('opt', 'condition'),
            sd_action.Call(foo, bar, 'func', sd.Params()),
            sd_action.ImplicitReturn(),
            sd_action.FragEnd('opt'),
        ])

    def test_fail_after_return_from_func(self):
        c = sd.Context()

        foo = c.object('foo')
        bar = c.object('bar')

        with foo:
            with bar.func():
                c.ret()
                with pytest.raises(sd.FragError):
                    with c.opt():
                        pass

    def test_fail_if_empty_inside(self):
        c = sd.Context()

        foo = c.object('foo')
        bar = c.object('bar')

        with foo:
            with bar.func():
                with pytest.raises(sd.FragError):
                    with c.opt():
                        pass

    def test_exception_inside(self):
        c = sd.Context()

        foo = c.object('foo')

        with pytest.raises(ZeroDivisionError):
            with foo:
                with c.opt():
                    3 / 0  # Cause exception


class TestLoop(TestBase):
    def test_top_level(self):
        c = sd.Context()

        foo = c.object('foo')
        bar = c.object('bar')

        with c.loop():
            with foo:
                bar.func()

        self.check(c, [
            sd_action.FragBegin('loop'),
            sd_action.Call(foo, bar, 'func', sd.Params()),
            sd_action.ImplicitReturn(),
            sd_action.FragEnd('loop'),
        ])


class TestAlt(TestBase):
    def test_top_level_two_choices(self):
        c = sd.Context()

        foo = c.object('foo')
        bar = c.object('bar')
        baz = c.object('baz')

        with c.alt():
            with c.choice('ok'):
                with foo:
                    bar.func()
            with c.choice('else'):
                with foo:
                    baz.func()
        self.check(c, [
            sd_action.FragBegin('alt'),
            sd_action.FragBegin('choice', 'ok'),
            sd_action.Call(foo, bar, 'func', sd.Params()),
            sd_action.ImplicitReturn(),
            sd_action.FragEnd('choice'),
            sd_action.FragBegin('choice', 'else'),
            sd_action.Call(foo, baz, 'func', sd.Params()),
            sd_action.ImplicitReturn(),
            sd_action.FragEnd('choice'),
            sd_action.FragEnd('alt'),
        ])

    def test_fail_if_call_in_alt(self):
        c = sd.Context()

        foo = c.object('foo')
        bar = c.object('bar')
        with pytest.raises(sd.CallError):
            with c.alt():
                with foo:
                    bar.func()  # need to be inside choice

    def test_fail_if_other_frag_in_alt(self):
        c = sd.Context()

        foo = c.object('foo')
        bar = c.object('bar')
        with pytest.raises(sd.FragError):
            with c.alt():
                with c.opt():  # wrong frag
                    with foo:
                        bar.func()

    def test_inside_top_level_two_sections(self):
        c = sd.Context()

        foo = c.object('foo')
        bar = c.object('bar')
        baz = c.object('baz')

        with c.alt():
            with c.choice('ok'):
                with foo:
                    bar.func()
            with c.choice('else'):
                with foo:
                    baz.func()

        self.check(c, [
            sd_action.FragBegin('alt'),
            sd_action.FragBegin('choice', 'ok'),
            sd_action.Call(foo, bar, 'func', sd.Params()),
            sd_action.ImplicitReturn(),
            sd_action.FragEnd('choice'),
            sd_action.FragBegin('choice', 'else'),
            sd_action.Call(foo, baz, 'func', sd.Params()),
            sd_action.ImplicitReturn(),
            sd_action.FragEnd('choice'),
            sd_action.FragEnd('alt'),
        ])


class TestGroup(TestBase):
    def test_top_level(self):
        c = sd.Context()

        foo = c.object('foo')
        bar = c.object('bar')

        with c.group():
            with foo:
                bar.func()

        self.check(c, [
            sd_action.FragBegin('group'),
            sd_action.Call(foo, bar, 'func', sd.Params()),
            sd_action.ImplicitReturn(),
            sd_action.FragEnd('group'),
        ])
