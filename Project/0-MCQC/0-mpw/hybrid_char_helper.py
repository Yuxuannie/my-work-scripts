import os
import utils
 
 
def get_char_types(s_line):
    type_idx = s_line.index('-type')
    char_types = set()
    # set_var -type mpw
    if not s_line[type_idx+1].startswith('{'):
        char_types.add(s_line[type_idx+1])
    # set_var -type {hold removal}
    else:
        for info in s_line[type_idx+1:]:
            char_types.add(info.strip().replace('{', '').replace('}', ''))
            if info.endswith('}'):
                break
    return char_types
 
 
def parse_chartcl_for_inc(path):
    chartcl = utils.load_list(path)
    inc_file_lookup = {}
    for i, line in enumerate(chartcl):
        line = line.strip()
        # "set_var" and "extsim_model_include" is for variety model card
        if line.startswith('set_var') and ' extsim_model_include ' in line:
            s_line = line.split()
            extsim_model_include_idx = s_line.index('extsim_model_include')
            model_card = s_line[extsim_model_include_idx+1]
            if not os.path.exists(model_card):
                raise FileNotFoundError(
                    'Model Card Not Exist: %s in (%s)' % (model_card, path))
            if '-type' not in s_line:
                char_types = ['traditional']
            else:
                char_types = get_char_types(s_line)
            for char_type in char_types:
                if char_type in inc_file_lookup and inc_file_lookup[char_type] != model_card:
                    raise ValueError(
                        'Differenct Model Card Setting (%s): %s' % (char_type, path))
                inc_file_lookup[char_type] = model_card
        # "set_opc_process" is for amd sis
        elif line.startswith('set_opc_process'):
            inc_line = chartcl[i+1].strip()
            assert '.inc' in inc_line
            s_inc_line = inc_line.split()
            for info in s_inc_line[1:]:
                info = info.replace('"', '').replace('{', '').replace('}', '')
                if not info.endswith('.inc'):
                    continue
                inc_file_lookup['traditional'] = info
    return inc_file_lookup
 
 
def parse_chartcl_for_cells(path):
    chartcl = utils.load_list(path)
    cells = []
    for line in chartcl:
        if 'set cells' not in line:
            continue
        s_line = line.split()
        # Skip 'set' and 'cells' after split
        for info in s_line[2:]:
            if info in ('{', '}', '[', ']') or 'packet_slave_cells' in info:
                continue
            cells.append(info.replace('{', '').replace('}', ''))
    return cells
 
 
def parse_sis_chartcl_for_cells(path):
    # /FSIM/stdcell_char2/Altos/tcba14/tcba14_h132pnpnl3p44c_mb_lvtll_c190430_011b/LVF/Char/char_ssgnp_0p45v_0c_cworst_CCworst_config.cons.tcl.sis
    cells = []
    path = os.path.realpath(path).replace('.sis', '').replace('_config', '')
    if not os.path.exists(path):
        return cells
    chartcl = utils.load_list(path)
    for line in chartcl:
        if line.startswith('source') and line.endswith('cell_lst'):
            cell_lst = line.split()[-1]
            for content in utils.load_list(cell_lst):
                cell = content.replace('set cells', '').replace('{', '').replace('\\', '').replace('}','').strip()
                cells.append(cell)
    return cells
 
