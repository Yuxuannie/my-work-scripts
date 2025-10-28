def is_cklnenq_notTEN(cell, splited_when):
    if cell.startswith('CKLNENQ') and '!TEN' in splited_when:
        return True
    return False
 
 
def is_cklnenq_TEN(cell, splited_when):
    if cell.startswith('CKLNENQ') and 'TEN' in splited_when:
        return True
    return False
 
 
def is_cklnenq_EN(cell, splited_when):
    if cell.startswith('CKLNENQ') and 'EN' in splited_when:
        return True
    return False
 
 
def get_cklnenq_EN_setting(splited_when):
    if '!EN' in splited_when:
        direction = 'stdvs_rise_fall'
    else:
        direction = 'stdvs_fall_rise'
 
    setting = "XVEN EN 0 " + direction + \
        " VDD='vdd_value' slew='constr_pin_slew' t01='constrained_pin_t01' t02='constrained_pin_t02'\n"
    return setting
 
