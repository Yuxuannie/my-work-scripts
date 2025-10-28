import utils
 
 
def parse_sis_vars(sis_chartcl_path):
    name_map = {
        'cratering_threshold': 'mpw_input_threshold',
        'smc_degrade': 'constraint_delay_degrade',
    }
    vars = {
        'mpw_input_threshold': '1',
        'constraint_glitch_peak': parse_glitch_peak(sis_chartcl_path),
        'slew_derate': calculate_slew_derate(sis_chartcl_path)
    }
    chartcl = utils.load_list(sis_chartcl_path)
    for line in chartcl:
        strip_line = line.strip()
        if not strip_line.startswith('set_config_opt'):
            continue
        s_line = strip_line.split()
        sis_name = s_line[1]
        if sis_name not in name_map:
            continue
        value = s_line[2]
        map_name = name_map[sis_name]
        vars[map_name] = value
    return vars
 
 
def calculate_slew_derate(sis_chartcl_path):
    chartcl = utils.load_list(sis_chartcl_path)
    lookup = {
        'logic_high_threshold': None,
        'logic_low_threshold': None,
        'slew_derate_upper_threshold': None,
        'slew_derate_lower_threshold': None,
    }
 
    for line in chartcl:
        s_line = line.split()
        if len(s_line) < 2 or s_line[1].strip() not in lookup:
            continue
        item, val = s_line[1:]
        lookup[item] = val
    for key, val in lookup.items():
        assert val is not None, 'Threshold Value is None: {key}'.format(
            key=key)
    slew_derate = (float(lookup['logic_high_threshold']) - float(lookup['logic_low_threshold'])) / (
        float(lookup['slew_derate_upper_threshold']) - float(lookup['slew_derate_lower_threshold']))
 
    return slew_derate
 
 
def parse_glitch_peak(sis_chartcl_path):
    chartcl = utils.load_list(sis_chartcl_path)
    glitch_peak = None
    in_block = False
    for line in chartcl:
        strip_line = line.strip()
        if 'set_config_opt -type mpw {' in strip_line:
            in_block = True
        if in_block and '}' in line:
            break
        if in_block and 'glitch_high_threshold' in line:
            assert glitch_peak is None
            glitch_peak = line.split()[-1]
    assert glitch_peak is not None
    return glitch_peak
 
