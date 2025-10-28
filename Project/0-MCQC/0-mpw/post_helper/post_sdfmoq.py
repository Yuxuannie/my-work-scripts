from post_helper import post_helper
 
 
def post_process(arc_info, write_list):
    target_cells = ['SDFMOQ']
    cell = arc_info['CELL_NAME']
    match = post_helper.find_match_target_cell(
        cell, target_cells, how='startswith')
    if not match:
        return write_list
    constr_pin = arc_info['CONSTR_PIN']
    constr_pin_dir = arc_info['CONSTR_PIN_DIR']
    if constr_pin == 'CP' and constr_pin_dir == 'fall':
        write_list = post_helper.change_meas_cross(
            write_list, 'cp2q_del1', '4', '3')
    return write_list
 
