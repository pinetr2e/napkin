#
# Sequence diagram tools
#
import sd_action


class ContextError(Exception):
    pass


class TopLevelCallerError(ContextError):
    pass


class ReturnError(ContextError):
    pass


class CallError(ContextError):
    pass


class FragError(ContextError):
    pass


class Params:
    def __init__(self, args=None, kargs=None):
        self.args = args if args else None
        self.kargs = kargs if kargs else None

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __str__(self):
        s = ''
        if self.args:
            s += ", ".join(["%s" % str(a) for a in self.args])
            if self.kargs:
                s += ', '
        if self.kargs is not None:
            s += ", ".join(["%s=%s" % (k, v) for k, v in self.kargs.items()])
        return s


class MethodCall:
    def __init__(self, obj, method, args, kargs):
        self.obj = obj
        self.method = method
        self.params = Params(args, kargs)

        #
        # ret_params can be Params object to specify explicit return value.
        # None means implicit return
        #
        self.ret_params = None
        self.args = args
        self.kargs = kargs

    def __enter__(self):
        self.obj.enter_call(self)

    def __exit__(self, *exc_args):
        if exc_args[0]:
            return
        self.obj.exit_call()

    def ret(self, *args, **kargs):
        """
        Specify return params.
        ex)
        foo.func().return('value')
        """
        self.specify_return_params(Params(args, kargs))

    def specify_return_params(self, params):
        if self.ret_params:
            raise ReturnError('double return')
        self.ret_params = params


class Method:
    def __init__(self, obj, name):
        self.obj = obj
        self.name = name

    def __call__(self, *args, **kargs):
        call = MethodCall(self.obj, self, args, kargs)
        self.obj.invoke_call(call)
        return call

    def __str__(self):
        return self.name


class Object:
    def __init__(self, sd, name):
        self.sd = sd
        self.name = name
        self.methods = {}

    def __getattr__(self, name):
        method = self.methods.setdefault(name, Method(self, name))
        return method

    def __enter__(self):
        self.sd.enter_top_object(self)

    def __exit__(self, *exc_args):
        if exc_args[0]:
            return
        self.sd.leave_top_object()

    def __str__(self):
        return self.name

    def invoke_call(self, call):
        self.sd.invoke_call(call)

    #
    # Used by MethodCall
    #
    def enter_call(self, call):
        self.sd.enter_call(call)

    def exit_call(self):
        self.sd.exit_call()


class Frag:
    def __init__(self, sd, op_name, condition=None):
        self.sd = sd
        self.op_name = op_name
        self.condition = condition

    def __enter__(self):
        self.sd.enter_frag(self)

    def __exit__(self, *exc_args):
        if exc_args[0]:
            return
        self.sd.exit_frag()


class Context(object):
    def __init__(self):

        # Objects used in the diagram.
        self.objects = {}

        # Capture the sequence of the actions
        self.sequence = []

        self.call_stack = []
        self.current_call = None

        self.frag_stack = []
        self.current_frag = None

        # call created by 'obj.func' can be used both with/without 'with'.
        # self.pending_call remembers it to add proper 'return' if necessary.
        # For example,
        # ex)
        #       ...
        #       foo.func                # (1)
        #       foo.func2               # causes add 'implicit return' for (1)
        #
        # ex)
        #       with foo.func():        # (1)
        #           bar.func            # (2)
        #
        #       When (1) exits, pending_call points to (2) to add 'implicit
        #       return' for (2)
        #
        self.pending_call = None

    def Object(self, name):
        """Create an object
        """
        obj = self.objects.setdefault(name, Object(self, name))
        return obj

    def enter_top_object(self, obj):
        if self.call_stack:
            raise TopLevelCallerError('Top level caller cannot be set again')
        assert self.current_call is None

        self.call_stack.append(self.current_call)
        # Add a guard call as the first item, which makes the overall logic
        # simpler.
        guard_call = MethodCall(obj, Method(obj, '<<somewhere>>'), None, None)
        self.current_call = guard_call

    def leave_top_object(self):
        assert len(self.call_stack) == 1
        self.return_any_pending_call()

        self.current_call = self.call_stack.pop()
        assert self.current_call is None

    def invoke_call(self, call):
        if self.current_call.ret_params:
            raise CallError("Current function already returned")

        if self.current_frag and self.current_frag.op_name == 'alt':
            raise CallError('Cannot be invoked inside alt level')

        self.return_any_pending_call()
        self.pending_call = call

    def return_any_pending_call(self):
        pending_call = self.pending_call
        if pending_call:
            caller = self.current_call.obj
            call_action = sd_action.Call(caller,
                                         pending_call.obj,
                                         pending_call.method.name,
                                         pending_call.params)
            self.sequence.append(call_action)

            ret_params = self.pending_call.ret_params
            ret_action = (sd_action.Return(ret_params)
                          if ret_params else
                          sd_action.ImplicitReturn())
            self.sequence.append(ret_action)
            self.pending_call = None

    def enter_call(self, call):
        caller = self.current_call.obj
        action = sd_action.Call(caller, call.obj,
                                call.method.name, call.params)
        self.sequence.append(action)

        self.call_stack.append(self.current_call)
        self.current_call = call
        self.pending_call = None

    def exit_call(self):
        #
        # ex)
        # ...
        # with foo.func():     (2)
        #     bar.func()       (1)
        #
        # for returning (1)
        self.return_any_pending_call()
        # for returning (2)
        ret_params = self.current_call.ret_params
        ret_action = (sd_action.Return(ret_params)
                      if ret_params else
                      sd_action.ImplicitReturn())
        self.sequence.append(ret_action)

        self.current_call = self.call_stack.pop()

    def ret(self, *args, **kargs):
        """
        Return from the current call
        """
        if len(self.call_stack) == 1:
            """
            Invalid operation in the top level caller
            ex)
                    with foo:
                        bar.func()
                        c.ret()             <--- Invalid
            """
            raise CallError('Return from top level caller')

        """
        ex)
                with foo.func():
                    bar.func()
                    c.ret()             <---
        """
        self.current_call.specify_return_params(Params(args, kargs))

    def opt(self, condition=None):
        return Frag(self, 'opt', condition)

    def loop(self, condition=None):
        return Frag(self, 'loop', condition)

    def alt(self):
        return Frag(self, 'alt')

    def choice(self, condition=None):
        return Frag(self, 'choice', condition)

    def enter_frag(self, frag):
        if self.current_call and self.current_call.ret_params:
            raise FragError("Current function already returned")

        self.return_any_pending_call()

        if self.current_frag and self.current_frag.op_name == 'alt':
            if frag.op_name != 'choice':
                raise FragError('Other frag except choice not '
                                'allowed inside alt')

        self.frag_stack.append(self.current_frag)
        self.current_frag = frag
        self.sequence.append(sd_action.FragBegin(frag.op_name, frag.condition))

    def exit_frag(self):
        self.return_any_pending_call()

        # Check if there is no action inside frag
        last_sequence = self.sequence[-1]
        if isinstance(last_sequence, sd_action.FragBegin):
            raise FragError('Empty fragment')

        self.sequence.append(sd_action.FragEnd(self.current_frag.op_name))
        self.current_frag = self.frag_stack.pop()


class Diagram:
    def __init__(self, dfunc):
        self.dfunc = dfunc

    def parse(self):
        sd_context = Context()
        self.dfunc(sd_context)
        return sd_context.sequence
