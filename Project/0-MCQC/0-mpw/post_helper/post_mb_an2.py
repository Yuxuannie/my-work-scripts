from post_helper import post_helper
 
 
def post_process(arc_info, write_list):
    target_cells = ['MB.*AN2']
    cell = arc_info['CELL_NAME']
    match = post_helper.find_match_target_cell(
        cell, target_cells, how='re_match')
    if not match:
        return write_list
    pinlist = arc_info['TEMPLATE_PINLIST'].split()
    vector = arc_info['VECTOR']
    write_list = fix_incorrect_toggle(write_list, pinlist, vector)
    write_list = fix_final_state_check(write_list, pinlist, vector)
 
    return write_list
 
 
def fix_incorrect_toggle(write_list, pinlist, vector):
    for i, line in enumerate(write_list):
        if not line.startswith('XVD'):
            continue
        s_line = line.split(' ')
        dpin = s_line[0].replace('XV', '')
        n = dpin[-1]
        qpin = 'Q'+str(n)
        didx = pinlist.index(dpin)
        qidx = pinlist.index(qpin)
        dvec = vector[didx].replace('1', 'R').replace('0', 'F')
        qvec = vector[qidx].replace('1', 'R').replace('0', 'F')
        if dvec == qvec:
            continue
        s_line[3] = "'vdd_value'"
        s_line[0] = 'V'+dpin
        s_line = s_line[:4]
        s_line.append('\n')
        write_list[i] = ' '.join(s_line)
    return write_list
 
 
def fix_final_state_check(write_list, pinlist, vector):
    qpin = None
    for i, line in enumerate(write_list):
        if line.startswith('.meas final_state '):
            assert qpin is None
            left = line.index('(')
            right = line.index(')')
            qpin = line[left+1:right]
        elif line.startswith('.meas final_state_check '):
            assert qpin is not None
            qidx = pinlist.index(qpin)
            qvec = vector[qidx]
            if qvec == 'F':
                write_list[i] = line.replace('> 0.95', '< 0.05')
            elif qvec == 'R':
                write_list[i] = line.replace('< 0.05', '> 0.95')
            else:
                pin_n = qpin.replace('QN', '').replace('Q', '')
                da = 'DA'+pin_n
                db = 'DB'+pin_n
                da_idx = pinlist.index(da)
                db_idx = pinlist.index(db)
                da_vec = vector[da_idx]
                db_vec = vector[db_idx]
                assert da_vec not in ('R', 'F')
                assert db_vec not in ('R', 'F')
                if da_vec == '0' or db_vec == '0':
                    write_list[i] = line.replace('> 0.95', '< 0.05')
                else:
                    write_list[i] = line.replace('< 0.05', '> 0.95')
        else:
            pass
    return write_list
 
