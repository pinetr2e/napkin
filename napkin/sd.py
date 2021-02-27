"""
Sequence diagram elements and API
"""

import collections
from . import sd_action


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


class CreateError(ContextError):
    pass


class DestroyError(ContextError):
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
            s += ', '.join(['%s' % str(a) for a in self.args])
            if self.kargs:
                s += ', '
        if self.kargs is not None:
            s += ', '.join(['%s=%s' % (k, v) for k, v in self.kargs.items()])
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
        self.notes = [None, None]

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

    def note(self, callee=None, caller=None):
        """
        Specify note for caller/callee side.
        """
        assert callee or caller, 'At least one argument necessary'
        self.notes[:] = (callee, caller)
        return self

    def specify_return_params(self, params):
        if self.ret_params:
            raise ReturnError('double return')
        self.ret_params = params


class Method:
    def __init__(self, obj, name, flags=''):
        self.obj = obj
        self.name = name
        self.flags = flags

    def __call__(self, *args, **kargs):
        call = MethodCall(self.obj, self, args, kargs)
        self.obj.invoke_call(call)
        return call

    def __str__(self):
        return self.name


class Object(object):
    def __init__(self, sd, name, cls=None, stereotype=None, instance_id=None):
        self.sd = sd
        self.name = name
        self.cls = cls
        self.methods = {}
        self.stereotype = stereotype

        # Becomes false if it is destroyed in the middle of sequence diagram
        self.valid = True
        # Becomes true if it is created in the middle of sequence diagram
        self.created = False
        self.instance_id = instance_id

    def __getattr__(self, name):
        return self.create_method(name)

    def create_method(self, name):
        method = self.methods.setdefault(name, Method(self, name))
        return method

    def __enter__(self):
        self.sd.enter_top_object(self)

    def __exit__(self, *exc_args):
        if exc_args[0]:
            return
        self.sd.leave_top_object()

    def __repr__(self):
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

    def note(self, text):
        self.sd.note_over(self, text)


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
    """
    Context to give API to the user diagram function and it also captures the
    diagram representation.
    """
    def __init__(self):
        # Objects used in the diagram.
        self._objects = collections.OrderedDict()

        # Capture the sequence of the actions
        self._sequence = []

        self._call_stack = []
        self._current_call = None

        self._frag_stack = []
        self._current_frag = None

        # Call created by 'obj.func' can be used both with/without 'with'.
        # self._pending_call remembers it to add proper 'return' if necessary.
        # For example,
        # ex)
        #     ...
        #     foo.func                # (1)
        #     foo.func2               # causes to add 'implicit return' for (1)
        #
        # ex)
        #     with foo.func():        # (1)
        #         bar.func            # (2)
        #
        #     When (1) exits, pending_call associated with (2) to add 'implicit
        #     return' for (2)
        #
        self._pending_call = None
        self._num_objects = 0

    def object(self, name, cls=None, stereotype=None):
        """Create an object
        """
        obj = self._objects.setdefault(name,
                                       Object(self, name, cls=cls,
                                              stereotype=stereotype,
                                              instance_id=self._num_objects))
        self._num_objects += 1
        return obj

    def enter_top_object(self, obj):
        if self._call_stack:
            raise TopLevelCallerError('Top level caller cannot be set again')
        assert self._current_call is None

        self._call_stack.append(self._current_call)
        # Add a guard call as the first item, which makes the overall logic
        # simpler.
        guard_call = MethodCall(obj, Method(obj, '<<somewhere>>'), None, None)
        self._current_call = guard_call

    def leave_top_object(self):
        assert len(self._call_stack) == 1
        self.return_any_pending_call()

        self._current_call = self._call_stack.pop()
        assert self._current_call is None

    def invoke_call(self, call):
        if self._current_call.ret_params:
            raise CallError('Current function already returned')

        if self._current_frag and self._current_frag.op_name == 'alt':
            raise CallError('Cannot be invoked inside alt level')

        self.return_any_pending_call()

        if not call.obj.valid:
            raise CallError('Object was destroyed')

        self._pending_call = call

    def return_any_pending_call(self):
        pending_call = self._pending_call
        if pending_call:
            caller = self._current_call.obj
            call_action = sd_action.Call(caller,
                                         pending_call.obj,
                                         pending_call.method.name,
                                         pending_call.params,
                                         pending_call.method.flags,
                                         pending_call.notes)
            self._sequence.append(call_action)

            ret_params = self._pending_call.ret_params
            ret_action = (sd_action.Return(ret_params)
                          if ret_params else
                          sd_action.ImplicitReturn())
            self._add_return_action(self._pending_call, ret_action)
            self._pending_call = None

    def _add_return_action(self, call, ret_action):
        if 'd' in call.method.flags:

            # Make it invalid to use the object after the destructor returns.
            call.obj.valid = False

        self._sequence.append(ret_action)

    def enter_call(self, call):
        caller = self._current_call.obj
        action = sd_action.Call(caller, call.obj,
                                call.method.name, call.params,
                                call.method.flags, call.notes)

        self._sequence.append(action)

        self._call_stack.append(self._current_call)
        self._current_call = call
        self._pending_call = None

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
        ret_params = self._current_call.ret_params
        ret_action = (sd_action.Return(ret_params)
                      if ret_params else
                      sd_action.ImplicitReturn())
        self._add_return_action(self._current_call, ret_action)

        self._current_call = self._call_stack.pop()

    def ret(self, *args, **kargs):
        """
        Return from the current call
        """
        if len(self._call_stack) == 1:
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
        self._current_call.specify_return_params(Params(args, kargs))

    def opt(self, condition=None):
        return Frag(self, 'opt', condition)

    def loop(self, condition=None):
        return Frag(self, 'loop', condition)

    def alt(self):
        return Frag(self, 'alt')

    def choice(self, condition=None):
        return Frag(self, 'choice', condition)

    def group(self, label=None):
        return Frag(self, 'group', label)

    def enter_frag(self, frag):
        if self._current_call and self._current_call.ret_params:
            raise FragError('Current function already returned')

        self.return_any_pending_call()

        if self._current_frag and self._current_frag.op_name == 'alt':
            if frag.op_name != 'choice':
                raise FragError('Other frag except choice not '
                                'allowed inside alt')

        self._frag_stack.append(self._current_frag)
        self._current_frag = frag
        self._sequence.append(
            sd_action.FragBegin(frag.op_name, frag.condition))

    def exit_frag(self):
        self.return_any_pending_call()

        # Check if there is no action inside frag
        last_sequence = self._sequence[-1]
        if isinstance(last_sequence, sd_action.FragBegin):
            raise FragError('Empty fragment')

        self._sequence.append(sd_action.FragEnd(self._current_frag.op_name))
        self._current_frag = self._frag_stack.pop()

    def create(self, obj_or_call):
        """Create object and invoke the constructor.

        If obj_or_call is Object type, default constructor called, <<create>>
        is called.
        """

        if self._current_call is None:
            raise CreateError('No caller specified')

        if isinstance(obj_or_call, Object):
            obj = obj_or_call
            method = obj.create_method('<<create>>')
            call = method()
        elif isinstance(obj_or_call, MethodCall):
            call = obj_or_call
            obj = call.obj
            method = call.method
        else:
            raise CreateError('Invalid argument')

        if len(obj.methods) > 1:
            raise CreateError('Object is already being used')

        if obj.created:
            raise CreateError('Object was already created')
        else:
            obj.created = True

        method.flags = 'c'
        return call

    def destroy(self, obj_or_call):
        """Invoke the destructor then destroy the object.
        """
        if self._current_call is None:
            raise DestroyError('No caller specified')

        if isinstance(obj_or_call, Object):
            obj = obj_or_call
            if not obj.valid:
                raise DestroyError('Object already destroyed')
            method = obj.create_method('<<destroy>>')
            call = method()
        elif isinstance(obj_or_call, MethodCall):
            call = obj_or_call
            obj = call.obj
            method = call.method
        else:
            raise CreateError('Invalid argument')

        # the object will become invalid when it returns from the destructor
        method.flags = 'd'
        return call

    def note(self, text):
        """Add note over current object.
        """
        if self._current_call is None:
            raise DestroyError('No object specified')
        self._current_call.obj.note(text)

    def note_over(self, obj, text):
        self.return_any_pending_call()
        self._sequence.append(sd_action.Note(text, obj=obj))

    def delay(self, text=None):
        self.return_any_pending_call()
        self._sequence.append(sd_action.Delay(text))

    def divide(self, text=None):
        self.return_any_pending_call()
        self._sequence.append(sd_action.Divide(text))


def parse(sd_func):
    """
    Parse sequence diagram.
    """
    sd_context = Context()
    sd_func(sd_context)
    return sd_context
