def load_list(path, trim=True):
    with open(path, 'r') as f:
        lst = f.readlines()
    if trim:
        lst = filter(None, (map(str.strip, lst)))
    lst = list(lst)
    return lst
 
 
def unit_offset_sci_val(str_val, n=12):
    if float(str_val) == 0:
        return float(str_val)
    str_val = str_val.lower()
    e_idx = str_val.index('e')
    val = float(str_val[:e_idx])
    ori_power = int(str_val[e_idx+1:])
    offset = ori_power + n
    val = val * (10 ** offset)
    return val
 
