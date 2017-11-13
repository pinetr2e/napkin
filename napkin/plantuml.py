import sd
import sd_action
import util

import re


def output_participants(sd_context):
    # Add participants in the order of usage
    output = []
    for o in sd_context.objects.values():
        if o.cls:
            output.append('participant "%(name)s:%(cls)s" '
                          'as %(name)s' % o.__dict__)
        else:
            output.append('participant %(name)s' % o.__dict__)

        if o.stereotype:
            output[-1] += ' <<{}>>'.format(o.stereotype)

    output.append('')
    return output


def generate_sd(sd_func):
    sd_context = sd.Context()
    sd_func(sd_context)
    output = []
    call_stack = []
    current_call = None

    output.append('@startuml')

    output += output_participants(sd_context)

    for p_action, action, n_action in util.neighbour(sd_context.sequence):
        if isinstance(action, sd_action.Call):
            if 'c' in action.flags:
                output.append('create %(callee)s' % action.__dict__)

            if re.match('<<\w+>>', action.method_name):
                # such as <<create>> or <<destroy>>
                output.append('%(caller)s -> %(callee)s : '
                              '%(method_name)s' % action.__dict__)
            else:
                output.append('%(caller)s -> %(callee)s : '
                              '%(method_name)s(%(params)s)' % action.__dict__)

            if not isinstance(n_action, sd_action.ImplicitReturn):
                output.append('activate %s' % action.callee)
            call_stack.append(current_call)
            current_call = action

        elif isinstance(action, sd_action.ImplicitReturn):
            if not isinstance(p_action, sd_action.Call):
                output.append('deactivate %s' % current_call.callee)

            if 'd' in current_call.flags:
                output.append('destroy %s' % current_call.callee)

            current_call = call_stack.pop()

        elif isinstance(action, sd_action.Return):
            s = '%s <-- %s' % (current_call.caller, current_call.callee)
            params = str(action.params)
            if params:
                s += ': %s' % action.params
            output.append(s)
            output.append('deactivate %s' % current_call.callee)
            current_call = call_stack.pop()

        elif isinstance(action, sd_action.FragBegin):
            if action.op_name == 'alt':
                is_alt_waiting_for_first_choice = True
            else:
                if action.op_name == 'choice':
                    if is_alt_waiting_for_first_choice:
                        is_alt_waiting_for_first_choice = False
                        s = 'alt'
                    else:
                        s = 'else'
                else:
                    s = '%s' % (action.op_name)

                if action.condition:
                    s += ' %s' % action.condition
                output.append(s)

        elif isinstance(action, sd_action.FragEnd):
            if action.op_name == 'choice':
                pass
            else:
                output.append('end')

        elif isinstance(action, sd_action.Note):
            lines = action.text.splitlines()
            if len(lines) == 1:
                output.append('note over %(obj)s : %(text)s' % action.__dict__)
            else:
                output.append('note over %(obj)s' % action.__dict__)
                output += lines
                output.append('end note')
        else:
            output.append('unknown : %s' % action)

    output.append('@enduml\n')
    return "\n".join(output)
