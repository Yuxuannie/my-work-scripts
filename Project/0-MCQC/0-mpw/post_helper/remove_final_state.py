from post_helper import post_helper
 
 
def post_process(arc_info, write_list):
    target_cells = ['SYN']
    cell = arc_info['CELL_NAME']
    match = post_helper.find_match_target_cell(
        cell, target_cells, how='in')
    if not match:
        return write_list
 
    for i, line in enumerate(write_list):
        if 'final_state' in line:
            if line.startswith('.tran'):
                write_list[i] = write_list[i].replace(', final_state_check', '')
            else:
                write_list[i] = ''
 
    return write_list
 
