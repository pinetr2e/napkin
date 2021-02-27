"""
Actions to be captured as sequence.
"""


class _Action(object):
    def __eq__(self, other):
        return self.__dict__ == other.__dict__


class Call(_Action):
    def __init__(self, caller, callee, method_name, params,
                 flags='', notes=None):
        self.caller = caller
        self.callee = callee
        self.method_name = method_name
        self.params = params
        self.flags = flags
        self.notes = notes if notes else [None, None]

    def __repr__(self):
        return 'call from %s to %s::%s(%s) [%s%s]' % (
            self.caller,
            self.callee,
            self.method_name,
            self.params,
            self.flags,
            self.notes)

    def __eq__(self, other):
        return (self.caller is other.caller and
                self.caller is other.caller and
                self.method_name == other.method_name and
                self.params == other.params and
                self.flags == other.flags,
                self.notes == other.notes)


class Return(_Action):
    def __init__(self, params):
        self.params = params

    def __repr__(self):
        return 'return (%s)' % (self.params)

    def __eq__(self, other):
        return self.params == other.params


class ImplicitReturn(_Action):
    def __init__(self):
        pass

    def __eq__(self, other):
        return self.__class__ is other.__class__

    def __repr__(self):
        return 'implicit return'


class FragBegin(_Action):
    def __init__(self, op_name, condition=None):
        self.op_name = op_name
        self.condition = condition

    def __repr__(self):
        s = '%s begin' % self.op_name
        if self.condition:
            s += ' [%s]' % self.condition
        return s

    def __eq__(self, other):
        return (self.__class__ is other.__class__ and
                self.__dict__ == other.__dict__)


class FragEnd(_Action):
    def __init__(self, op_name):
        self.op_name = op_name

    def __repr__(self):
        return '%s end' % self.op_name

    def __eq__(self, other):
        return (self.__class__ is other.__class__ and
                self.__dict__ == other.__dict__)


class Note(_Action):
    def __init__(self, text, obj=None):
        self.text = text
        self.obj = obj

    def __repr__(self):
        return 'note over %s : %s' % (self.obj, self.text)

    def __eq__(self, other):
        return (self.__class__ is other.__class__ and
                self.__dict__ == other.__dict__)


class Delay(_Action):
    def __init__(self, text):
        self.text = text

    def __repr__(self):
        return 'delay' + ('({})'.format(self.text) if self.text else '')

    def __eq__(self, other):
        return (self.__class__ is other.__class__ and
                self.text == other.text)


class Divide(_Action):
    def __init__(self, text):
        self.text = text

    def __repr__(self):
        return 'divide' + ('({})'.format(self.text) if self.text else '')

    def __eq__(self, other):
        return (self.__class__ is other.__class__ and
                self.text == other.text)
