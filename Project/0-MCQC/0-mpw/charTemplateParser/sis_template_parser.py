import utils
 
 
def group_sis_template_by_cell(path):
    template = utils.load_list(path)
    group_template = {}
    cell = None
    cell_group = []
    for i, line in enumerate(template):
        if i == len(template) - 1:
            group_template[cell] = cell_group.copy()
        strip_line = line.strip()
        split_line = line.split()
        if strip_line.startswith('if') and '$cell' in strip_line:
            group_template[cell] = cell_group.copy()
            eq_idx = split_line.index('==')
 
            cell = split_line[eq_idx+1].replace('"', '').replace('}', '')
            assert cell not in group_template, 'Duplicate Cell In Template "{cell}": {path}'.format(cell=cell,
                                                                                                    path=path)
            cell_group = []
 
        if cell is None:
            continue
        cell_group.append(line)
    del group_template[None]
    return group_template
 
 
def parse_template_indexes(template):
    template_indexes = {}
    for line in template:
        s_line = line.split()
        if line.strip().startswith('#'):
            continue
        if len(s_line) > 1 and '_template_' in s_line[1]:
            template_name = s_line[1]
            indexes = ' '.join(s_line[2:])
            indexes = get_list_value(indexes)
            template_indexes[template_name] = indexes
    return template_indexes
 
 
def get_list_value(value):
    value = value.replace('{', '').replace('}', '').split()
    return value
 
 
def find_value_str(part_s_line, end_key):
    value = []
    for i, item in enumerate(part_s_line):
        if item.startswith('-') or i == len(part_s_line) - 1 or\
                end_key in item:
            value = ' '.join(value)
            if '{' in value and '}' in value:
                value = get_list_value(value)
            break
        value.append(item)
    assert len(value) != 0
    return value
 
 
def find_use_slew_load_template(template, template_indexes):
    slews = []
    loads = []
    for line in template:
        s_line = line.split()
        strip_line = line.strip()
        if strip_line.startswith('set_config_opt') and\
                'timing' in line and \
                '-from' not in line and \
                'explicit_points_load' in line:
            load_template_name = s_line[-1]
            assert load_template_name.startswith('$')
            load_template_name = load_template_name[1:]
            tmp_load = [value.replace('e-12', '') for value in template_indexes[load_template_name]]
            loads.append(tmp_load)
        elif strip_line.startswith('set_config_opt') and\
                'mpw' in strip_line and \
                'constraint_explicit_points_slew' in line:
            slew_idx = s_line.index('constraint_explicit_points_slew')
            slew_name = ' '.join(s_line[slew_idx+1:])
            if slew_name.startswith('$'):
                slew_name = slew_name[1:]
                slew = template_indexes[slew_name].copy()
            else:
                assert '{' in slew_name and '}' in slew_name
                slew = get_list_value(slew_name)
            slew = [value.replace('e-9', '') for value in slew]
            slew_id = []
            for i, item in enumerate(s_line):
                if item.startswith('-'):
                    item = item[1:]
                    value = find_value_str(
                        s_line[i+1:], end_key='constraint_explicit_points_slew')
                    if isinstance(value, list):
                        value = '-'.join(value)
                    value = value.replace('HL', 'fall').replace('LH', 'rise')
 
                    slew_id.append('{item}:{value}'.format(item=item, value=value))
            slew_id = '#'.join(slew_id)
            tmp_slew = {slew_id: slew}
            slews.append(tmp_slew)
    return slews, loads
 
 
def parse_arcs(template):
    arcs = []
    for line in template:
        s_line = line.split()
        strip_line = line.strip()
        if not strip_line.startswith('set_config_opt') or ' whens' not in line or 'mpw' not in line:
            continue
        pin = s_line[s_line.index('-from')+1]
        pin = get_list_value(pin)
        assert len(pin) == 1
        pin = pin[0]
        pin_dir = s_line[s_line.index(
            '-from_direction')+1].replace('HL', 'fall').replace('LH', 'rise')
        whens_idx = s_line.index('whens')+1
        whens = find_value_str(s_line[whens_idx:], '}')
        whens = list(map(lambda x: x.replace('"', ''), get_list_value(whens)))
        arc = {
            '{pin}-{pin_dir}'.format(pin=pin, pin_dir=pin_dir): whens
        }
        arcs.append(arc)
    return arcs
 
 
def parse_pinlist_whens(template):
    start_idx = None
    for idx, line in enumerate(template):
        if 'add special setting' not in line:
            continue
        start_idx = idx
        break
    assert start_idx is not None
    special_setting = template[start_idx:]
    start = False
    whens = []
    for idx, line in enumerate(special_setting):
        if start:
            if 'whens' in line or 'state_partitions' in line:
                continue
            if '}' in line:
                break
            whens.append(line)
        strip_line = line.strip()
        if strip_line.startswith('set_config_opt -type mpw -from CP') and not start:
            start = True
    pinlist = whens[0].replace('!', '').split('&')
    return pinlist, whens
 
 
def parse(path):
    cell_group_template = group_sis_template_by_cell(path)
    sis_template = {}
    for cell, template in cell_group_template.items():
        if not cell.startswith('MB'):
            continue
        template_indexes = parse_template_indexes(template)
        slew_template, load_template = find_use_slew_load_template(
            template, template_indexes)
        arcs = parse_arcs(template)
        pinlist, whens = parse_pinlist_whens(template)
        sis_template[cell] = {
            'template': template_indexes,
            'slew': slew_template,
            'load': load_template,
            'arcs': arcs,
            'pinlist': pinlist,
            'whens': whens
        }
    return sis_template
 
