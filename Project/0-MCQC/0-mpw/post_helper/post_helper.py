import re
 
 
def find_match_target_cell(cell, target_cells, how='startswith'):
    match = False
    match_method_map = {
        'startswith': startswith_match,
        'in': in_match,
        're_match': re_match,
    }
    match_method = match_method_map[how]
    for tc in target_cells:
        match = match_method(cell, tc)
        if match:
            break
    return match
 
 
def startswith_match(cell, target):
    return cell.startswith(target)
 
 
def in_match(cell, target):
    return target in cell
 
 
def re_match(cell, target):
    res = re.match(target, cell)
    return res is not None
 
 
def find_line_idx(write_list, keyword):
    for idx, line in enumerate(write_list):
        if keyword in line:
            return idx
    raise ValueError('Can Not Find ' + keyword + ' in Deck Content.')
 
 
def find_pin_in_when(pin, when):
    swhen = when.split('&')
    for w in swhen:
        if w.replace('!', '') == pin:
            return w
    return None
 
 
def remove_static_pin_def(arc_info, write_list, pin, check_when=True):
    need_to_remove = {"V"+pin + ' '+pin + ' ' +
                      "0 'vss_value'",
                      "V"+pin + ' '+pin + ' ' +
                      "0 'vdd_value'"}
    when = arc_info['WHEN']
    pin_in_when = find_pin_in_when(pin, when)
    if check_when and pin_in_when is None:
        return write_list
 
    for i, line in enumerate(write_list):
        for item in need_to_remove:
            write_list[i] = write_list[i].replace(item, '')
    return write_list
 
 
def fix_lost_toggle(arc_info, write_list, pin, how='when'):
    find_vec_method_map = {
        'when': find_vector_by_when,
        'vector': find_vector_in_vectors
    }
    find_vec_method = find_vec_method_map[how]
    pinlist = arc_info['TEMPLATE_PINLIST'].split()
    if pin not in pinlist:
        return write_list
    toggle_line_head = 'XV' + pin + ' ' + pin+' 0'
    for line in write_list:
        if toggle_line_head in line:
            return write_list
 
    vec = find_vec_method(arc_info, pin)
    if vec is None:
        return write_list
 
    if vec == '1' :
        pin_def = 'XV'+pin+' ' + pin + \
            " 0 stdvs_fall_rise VDD='vdd_value' slew='constr_pin_slew' t01='constrained_pin_t01' t02='constrained_pin_t02'\n"
    else:
        pin_def = 'XV'+pin+' ' + pin + \
            " 0 stdvs_rise_fall VDD='vdd_value' slew='constr_pin_slew' t01='constrained_pin_t01' t02='constrained_pin_t02'\n"
 
    line_idx = find_line_idx(write_list, '* Toggling pins')
    write_list.insert(line_idx+1, pin_def)
    return write_list
 
def fix_lost_toggle_1_time(arc_info, write_list, pin, how='when'):
    find_vec_method_map = {
        'when': find_vector_by_when,
        'vector': find_vector_in_vectors
    }
    find_vec_method = find_vec_method_map[how]
    pinlist = arc_info['TEMPLATE_PINLIST'].split()
    if pin not in pinlist:
        return write_list
    toggle_line_head = 'XV' + pin + ' ' + pin+' 0'
    for line in write_list:
        if toggle_line_head in line:
            return write_list
 
    vec = find_vec_method(arc_info, pin)
    if vec is None:
        return write_list
 
    if vec == '1' :
        pin_def = 'XV'+pin+' ' + pin + \
            " 0 stdvs_rise VDD='vdd_value' slew='constr_pin_slew' t01='constrained_pin_t01'\n"
    else:
        pin_def = 'XV'+pin+' ' + pin + \
            " 0 stdvs_fall VDD='vdd_value' slew='constr_pin_slew' t01='constrained_pin_t01'\n"
 
    line_idx = find_line_idx(write_list, '* Toggling pins')
    write_list.insert(line_idx+1, pin_def)
    return write_list
 
def find_vector_by_when(arc_info, pin):
    when = arc_info['WHEN']
    pin_when = find_pin_in_when(pin, when)
    if pin_when is None:
        return None
    if '!' in pin_when:
        vec = '0'
    else:
        vec = '1'
    return vec
 
 
def find_vector_in_vectors(arc_info, pin):
    vector = arc_info['VECTOR']
    pinlist = arc_info['TEMPLATE_PINLIST'].split()
    pin_idx = pinlist.index(pin)
    vec = vector[pin_idx]
    if vec.lower() == 'x':
        return None
    return vec
 
 
def remove_toggle(arc_info, write_list, pin):
    remove_idx = None
    toggle_line_head = 'XV'+pin + ' ' + pin+' 0'
    for idx, line in enumerate(write_list):
        if line.strip().startswith(toggle_line_head):
            remove_idx = idx
            break
    if remove_idx is not None:
        write_list.pop(remove_idx)
    return write_list
 
 
def fix_static_pin_def(arc_info, write_list, pin):
    pin_def_idx = find_line_idx(
        write_list, keyword='* Pin definitions')
 
    vector = find_vector_in_vectors(arc_info, pin)
    if vector not in ('0', '1'):
        vector = find_vector_by_when(arc_info, pin)
 
    if vector == '0':
        pin_def = 'V'+pin+' '+pin+' ' + '0'+' '+"'vss_value'\n"
    elif vector == '1':
        pin_def = 'V'+pin+' '+pin+' ' + '0'+' '+"'vdd_value'\n"
    for line in write_list:
        if pin_def in line:
            return write_list
    write_list.insert(pin_def_idx+1, pin_def)
    return write_list
 
 
def remove_tran_item(arc_info, write_list, item):
    for i, line in enumerate(write_list):
        if line.startswith('.tran') and item in line:
            s_line = line.split(',')
            for j, group in enumerate(s_line):
                if item in group:
                    s_line[j] = group.replace(item, '')
            write_list[i] = ','.join(s_line[:-1]) + ' ' + s_line[-1]
            break
    return write_list
 
 
def change_meas_cross(write_list, meas_item, cross_as_is, cross_to_be):
    meas_keyword = '.meas '+meas_item
    for i, line in enumerate(write_list):
        if not line.startswith(meas_keyword):
            continue
        if cross_as_is not in line:
            continue
 
        as_is_cross_idx = line.index(cross_as_is)
        end_as_is_cross_idx = as_is_cross_idx + len(cross_as_is)
        write_list[i] = write_list[i][:as_is_cross_idx] + \
            cross_to_be+write_list[i][end_as_is_cross_idx:]
        break
    return write_list
 
 
def remove_certain_line(arc_info, write_list, certain_line):
    new_write_list = []
    for line in write_list:
 
        if certain_line in line:
            s_line = line.split('\n')
            new_line = []
            for sl in s_line:
                if sl.startswith(certain_line):
                    continue
                new_line.append(sl)
            line = '\n'.join(new_line)
        new_write_list.append(line)
    return new_write_list
 
 
def add_tran_item(write_list, item):
    for i, line in enumerate(write_list):
        if line.startswith('.tran') and item not in line and 'results' in line:
            s_line = line.split(',')
            last_one = s_line[-1].split()
            last_one[0] = last_one[0].replace(
                last_one[0], last_one[0] + ',' + item)
            last_one = ' '.join(last_one)
            s_line[-1] = last_one
            write_list[i] = ','.join(s_line)
    return write_list
 
 
def add_meas_final_state(write_list):
    insert_idx = None
    for i, line in enumerate(write_list):
        if line.startswith('.meas'):
            insert_idx = i
        if 'targ' in line and 'cp2q_del' in line:
            probe = line.split('targ')[-1].split('v(')[-1].split(')')[0]
    final_state_line = '.meas final_state find v('+probe+') at=50u\n'
    final_state_check_line = ".meas final_state_check find par('1') at='final_state/vdd_value < 0.05 ? 0 : -1'\n\n"
    for i, line in enumerate(write_list):
        if 'final_state find' in line:
            insert_idx = i
            break
 
    if 'final_state find' not in '\n'.join(write_list):
        write_list.insert(insert_idx, final_state_line)
    if 'inal_state_check find' not in '\n'.join(write_list):
        write_list.insert(insert_idx+1, final_state_check_line)
    return write_list
 
 
def replace_final_state_check(write_list, check_ratio):
    keyword = "final_state/vdd_value"
    for i, line in enumerate(write_list):
        if keyword in line:
            if check_ratio == '0.95':
                write_list[i] = line.replace('< 0.05', '> {check_ratio}'.format(check_ratio=check_ratio))
            elif check_ratio == '0.05':
                write_list[i] = line.replace('> 0.95', '< {check_ratio}'.format(check_ratio=check_ratio))
            else:
                raise ValueError('Invalid Check Ratio')
            break
    return write_list
 
 
def insert_above_nodeset(write_list, insert_line):
    insert_idx = None
    for i, line in enumerate(write_list):
        if line.startswith('.nodeset'):
            insert_idx = i
            break
    write_list.insert(insert_idx, insert_line)
    return write_list
 
def remove_redundant_content(write_list):
    string_write_list = ','.join(write_list)
    for i, line in enumerate(write_list):
        if 'OPT_RESULTS' in line:
            criteria_lst = line.split('|')[-1].split()
            for criteria in criteria_lst :
                if string_write_list.count(criteria) == 1 :
                    write_list[i] = line.replace(criteria,'')
    return(write_list)
 
def add_tran_item_FMC(write_list, item):
    for i, line in enumerate(write_list):
        if 'OPT_RESULTS' in line:
            criteria_lst = line.split('|')[-1].split()
            if item not in criteria_lst :
                write_list[i] = line.strip() + ' ' + item + '\n'
    return(write_list)
def remove_content(write_list,content):
    for i,line in enumerate(write_list):
        if content in line :
            write_list[i] = '\n'
    return(write_list)
 
 
