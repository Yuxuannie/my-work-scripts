def post_process(arc_info, write_list):
    end_final_state_idx = get_final_state_idx(write_list)
    if end_final_state_idx is None or not arc_info['CELL_NAME'].startswith('MB'):
        return write_list
    pinlist = arc_info['TEMPLATE_PINLIST'].split()
    dpin_settings = get_dpin_settings(write_list)
    q_states = get_q_states(dpin_settings, pinlist)
    final_state_lines = '\n'.join(gen_final_state_lines(q_states, write_list))
    write_list.insert(end_final_state_idx+1, final_state_lines)
    return write_list
 
 
def already_added_final_state(final_line, write_list):
    for line in write_list:
        if final_line in line:
            return True
    return False
 
 
def gen_final_state_lines(q_states, write_list):
    criteria_map = {
        0: '< 0.05',
        1: '> 0.95'
    }
    final_state_lines = []
    for q, state in q_states.items():
        criteria = criteria_map[state]
        line1 = '.meas final_state find v({q}) at=50u'.format(q=q)
        if already_added_final_state(line1, write_list):
            continue
        _, n = retrive_pin_prefix_and_pin_num(q)
        line1 = line1.replace('final_state', 'final_state_{n}'.format(n=n))
        line2 = ".meas final_state_check_{n} find par('1') at='final_state_{n}/vdd_value {criteria} ? 0: -1'".format(
            criteria=criteria, n=n)
        final_state_lines.extend([line1, line2])
    final_state_lines.append('\n')
    return final_state_lines
 
 
def retrive_pin_prefix_and_pin_num(pin):
    prefix = []
    num = []
    for c in pin:
        if c.isalpha():
            prefix.append(c)
        elif c.isdigit():
            num.append(c)
        else:
            raise ValueError('Invalid Character: {pin}'.format(pin=pin))
    prefix = ''.join(prefix)
    num = ''.join(num)
    return prefix, num
 
 
def find_coresponding_q_pin(dpin, pinlist):
    _, dpin_number = retrive_pin_prefix_and_pin_num(dpin)
    found_qpin_prefix = found_qpin_number = None
    for pin in pinlist:
        if not pin.startswith('Q'):
            continue
        qpin_prefix, qpin_number = retrive_pin_prefix_and_pin_num(pin)
        if qpin_number != dpin_number:
            continue
        assert found_qpin_prefix is None
        found_qpin_prefix = qpin_prefix
        found_qpin_number = qpin_number
    assert found_qpin_number is not None
    return found_qpin_prefix, found_qpin_number
 
 
def get_q_states(dpin_settings, pinlist):
    state_map = {
        'rise': 1,
        'fall': 0
    }
 
    q_states = {}
    for dpin, dpin_dir in dpin_settings.items():
        qpin_prefix, qpin_number = find_coresponding_q_pin(dpin, pinlist)
        qpin = '{qpin_prefix}{qpin_number}'.format(
            qpin_prefix=qpin_prefix, qpin_number=qpin_number)
        q_state = state_map[dpin_dir]
        if qpin_prefix[-1] == 'N':
            # Inverte Q state
            q_state = 1 - q_state
        q_states[qpin] = q_state
    return q_states
 
 
def get_final_state_idx(write_list):
    end_idx = None
    for i, line in enumerate(write_list):
        if '.meas final_state_check ' in line:
            end_idx = i
    return end_idx
 
 
def get_dpin_settings(write_list):
    dpin_settings = {}
    for i, line in enumerate(write_list):
        strip_line = line.strip()
        if strip_line.startswith('XV'):
            _, pin, _, pin_dir, _ = strip_line.split(maxsplit=4)
            if not pin.startswith('D'):
                continue
            pin_dir = convert_pin_dir(pin_dir)
            assert pin not in dpin_settings
            dpin_settings[pin] = pin_dir
    return dpin_settings
 
 
def convert_pin_dir(pin_dir):
    s_pin_dir = pin_dir.split('_')
    final_dir = s_pin_dir[-1]
    return final_dir
 
