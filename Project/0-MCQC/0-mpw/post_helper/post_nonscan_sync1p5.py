from post_helper import post_helper
 
 
def post_process(arc_info, write_list):
    target_cells = ['DFNSYNC1P5', 'DFSYNC1P5']
    cell = arc_info['CELL_NAME']
    match = post_helper.find_match_target_cell(
        cell, target_cells, how='startswith')
    if not match:
        return write_list
    pin = arc_info['CONSTR_PIN']
    pin_dir = arc_info['CONSTR_PIN_DIR']
    vector = arc_info['VECTOR']
    lit_when = arc_info['LIT_WHEN']
    if (cell.startswith('DFNSYNC1P5') and 'notD' in lit_when and pin == 'CPN' and pin_dir == 'rise' and vector[-1] == '1') or\
            (cell.startswith('DFSYNC1P5') and 'notD' in lit_when and pin == 'CP' and pin_dir == 'fall' and vector[-1] == '1'):
        criteria = '0.95'
    elif (cell.startswith('DFNSYNC1P5') and 'notD' not in lit_when and pin == 'CPN' and pin_dir == 'rise' and vector[-1] == '0') or\
            (cell.startswith('DFSYNC1P5') and 'notD' not in lit_when and pin == 'CP' and pin_dir == 'fall' and vector[-1] == '0'):
        criteria = '0.05'
    else:
        return write_list
    write_list = post_helper.replace_final_state_check(write_list, criteria)
 
    return write_list
 
