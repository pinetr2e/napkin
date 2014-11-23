import sd
import sd_action


def generate_sd(sd_func):
    sd_context = sd.Context()
    sd_func(sd_context)
    output = []
    call_stack = []
    current_call = None

    output.append('@startuml')
    prev_action = None
    for action in sd_context.sequence:
        if isinstance(action, sd_action.Call):
            output.append('%(caller)s -> %(callee)s : '
                          '%(method_name)s(%(params)s)' % action.__dict__)
            output.append('activate %s' % action.callee)
            call_stack.append(current_call)
            current_call = action

        elif isinstance(action, sd_action.ImplicitReturn):
            output.append('deactivate %s' % current_call.callee)
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
            s = '%s' % (action.op_name)
            if action.condition:
                s += ' %s' % action.condition
            output.append(s)

        elif isinstance(action, sd_action.FragEnd):
            output.append('end')

        else:
            output.append('unknown : %s' % action)

        prev_action = action
    output.append('@enduml\n')
    return "\n".join(output)
