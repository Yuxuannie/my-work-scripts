from post_helper import post_helper
 
 
def post_process(arc_info, write_list):
    target_cells = ['LND2SR']
    cell = arc_info['CELL_NAME']
    match = post_helper.find_match_target_cell(
        cell, target_cells, how='startswith')
    if not match:
        return write_list
    lit_when = arc_info['LIT_WHEN']
    if lit_when not in ('SDN', 'CDN'):
        return write_list
    write_list = fix_not_toggle(write_list, lit_when)
 
    return write_list
 
 
def fix_not_toggle(write_list, when):
    done = False
    toggle_tempalte = "XV$PIN $PIN 0 stdvs_fall_rise VDD='vdd_value' slew='constr_pin_slew' t01='constrained_pin_t01' t02='constrained_pin_t02'\n"
    toggle_idx = None
    fixed_line = None
    for i, line in enumerate(write_list):
        if '* Toggling pins' in line:
            toggle_idx = i
            break
        if not line.startswith('V'+when):
            continue
        fixed_line = toggle_tempalte.replace('$PIN', when)
        write_list[i] = ''
    if fixed_line is None or toggle_idx is None:
        raise ValueError('Can Not Find Keyword for LND2SR for postprocessing.')
    write_list.insert(toggle_idx+1, fixed_line)
    done = True
    if not done:
        raise ValueError('LND2SR Toggloe Not Postprocessd')
    return write_list
 
