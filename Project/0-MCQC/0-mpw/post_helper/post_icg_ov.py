from post_helper import post_helper
 
 
def post_process(arc_info, write_list):
    target_cells = ['CKLNQRM']
    cell = arc_info['CELL_NAME']
    match = post_helper.find_match_target_cell(
        cell, target_cells, how='startswith')
    if not match:
        return write_list
    constr_pin_dir = arc_info['CONSTR_PIN_DIR']
    lit_when = arc_info['LIT_WHEN']
    map_name = constr_pin_dir+'-'+lit_when
    fix_func_map = {
        'fall-E_OV_notTE': fix_fall_E_OV_notTE,
        'fall-notE_OV_notTE': fix_fall_notE_OV_notTE,
        'rise-notE_OV_notTE': fix_rise_notE_OV_notTE,
    }
    if map_name not in fix_func_map:
        return write_list
    fix_func = fix_func_map[map_name]
    write_list = fix_func(write_list)
    return write_list
 
 
def fix_fall_E_OV_notTE(write_list):
    write_list = post_helper.change_meas_cross(
        write_list, 'cp2q_del1', 'cross=4', 'cross=3')
    return write_list
 
 
def fix_fall_notE_OV_notTE(write_list):
    write_list = post_helper.replace_final_state_check(write_list, '0.95')
    return write_list
 
 
def fix_rise_notE_OV_notTE(write_list):
    write_list = post_helper.add_meas_final_state(write_list)
    return write_list
 
