"""
lineParser__funcs.py
Module containing functions to parse a line and return all possible
combinations of that line
"""
 
import sys
 
 
def parseLine(input_line, star_dict, exceptions_dict):
    """
    Function to parse the input line and return all possible combinations,
    based on the star-lists and exceptions
 
    :param input_line (str): string with comma separated fields
    :param star_dict: dictionary of lists, with strings as key names
    :param exceptions_dict: dictionary of lists, with strings as key names
    :return returns a list of lists, each list is a combination
    """
 
    # Init
    final_combo_list = list()
 
    # Listify the input line; each field is an entry in the list
    input_info = [x.strip() for x in input_line.split(',')]
    if not len(input_info) >= 6:
        return final_combo_list
    lib_type = input_info[0]
    lib_length = input_info[1]
    lib_vt = input_info[2]
    lib_proc = input_info[3]
    lib_vdd = input_info[4]
    lib_temper = input_info[5]
    lib_options = None
    if len(input_info) > 6:
        lib_options = input_info[6:]
 
    # 1-at-a-time form and check
    # Get combinations
    #   Loop over all
    #   Get combinations
    #       ...
    #       Form current combination
    #       Check current combination
    #       Append
    lib_type_combos = getCombinations(lib_type, star_dict, 'libs')
    for lib_item in lib_type_combos:
 
        lib_length_combos = getCombinations(lib_length, star_dict, 'lengths')
        for length_item in lib_length_combos:
 
            lib_vt_combos = getCombinations(lib_vt, star_dict, 'vts')
            for vt_item in lib_vt_combos:
 
                lib_proc_combos = getCombinations(lib_proc, star_dict, 'procs')
                for proc_item in lib_proc_combos:
 
                    # Logic for handling lvl shifter
                    lib_vdd_combos = getLibVDDCombos(lib_item, vt_item, lib_vdd, star_dict)
                    for vdd_item in lib_vdd_combos:
 
                        lib_temper_combos = getCombinations(lib_temper, star_dict, 'tempers')
                        for temper_item in lib_temper_combos:
 
                            # Form
                            current_combination = [lib_item, length_item, vt_item, proc_item, vdd_item, temper_item]
                            #if not lib_options is None:
                            if isinstance(lib_options, list):
                                for opt_item in lib_options:
                                    current_combination.append(opt_item)
 
                            append_combo = validateCombination(current_combination, exceptions_dict)
 
                            if append_combo:
                                final_combo_list.append(current_combination)
 
    return final_combo_list
 
 
def getLibVDDCombos(lib_item, vt_item, lib_vdd, star_dict):
    """
    Logic required for lvl shifter library
    Gets the proper lib_vdd combinations based on lib type and vt
    """
 
    if (lib_item == 'lvl') or (lib_item == 'lvl2'):
        star_dict_keyname = '_'.join([lib_item, vt_item, "vdd"])
        lib_vdd_combos = getCombinations(lib_vdd,
                                         star_dict,
                                         star_dict_keyname)
    else:
        lib_vdd_combos = getCombinations(lib_vdd,
                                         star_dict, 'vdds')
 
    return lib_vdd_combos
 
 
def getCombinations(field_value, input_starlist_dict, key_name):
    """
    Returns all valid values of field_value, based on the star-list
    """
 
    combo_list = list()
 
    if not field_value == '*':
        combo_list.append(field_value)
    else:
        combo_list = input_starlist_dict[key_name]
 
    return combo_list
 
 
def validateCombination(input_combination, input_exceptions_dict, key_name='all'):
    """
    Checks if the current input combination is valid.
    """
 
    valid_combo = 1
    for exception_list in input_exceptions_dict[key_name]:
        violate_count = 0
        for exception_item in exception_list.split(','):
            # Try float cast to handle case of "0.45" vs "0.450"
            try:
                curr_exception_item = float(exception_item)
            except ValueError:
                curr_exception_item = exception_item
 
            for combo_item in input_combination[:6]:
                try:
                    curr_combo_item = float(combo_item)
                except:
                    curr_combo_item = combo_item
 
                if curr_combo_item == curr_exception_item:
                    violate_count += 1
                    break
 
        # If number of violations == len of exception, it is invalid
        if violate_count == len(exception_list.split(',')):
            valid_combo = 0
            break
 
    return valid_combo
 
 
if __name__ == "__main__":
    print("Debugging module.")
 
    input_file = sys.argv[1]
    with open(input_file, 'r') as f:
        input_lines = f.readlines()
 
    lib_combos = ['base', 'lvl', 'mb', 'pm']
    len_combos = ['8', '11']
    vt_combos = ['svt', 'lvt', 'ulvt']
    proc_combos = ['ssgnp', 'ffgnp']
    vdd_combos = ['0.525', '0.625', '0.525_0.525']
    temper_combos = ['-25', '125']
    lvl_svt_vdd_combos = ['0.625_0.525']
    lvl_lvt_vdd_combos = ['0.525_0.625']
    lvl_ulvt_vdd_combos = ['0.525_0.700']
    lvl2_svt_vdd_combos = ['0.625_0.525']
    lvl2_lvt_vdd_combos = ['0.525_0.625']
    lvl2_ulvt_vdd_combos = ['0.525_0.700']
    starlist_dict = dict()
    starlist_dict['libs'] = lib_combos
    starlist_dict['lengths'] = len_combos
    starlist_dict['vts'] = vt_combos
    starlist_dict['procs'] = proc_combos
    starlist_dict['vdds'] = vdd_combos
    starlist_dict['tempers'] = temper_combos
    starlist_dict['lvl_svt_vdd'] = lvl_svt_vdd_combos
    starlist_dict['lvl_lvt_vdd'] = lvl_lvt_vdd_combos
    starlist_dict['lvl_ulvt_vdd'] = lvl_ulvt_vdd_combos
    starlist_dict['lvl2_svt_vdd'] = lvl_svt_vdd_combos
    starlist_dict['lvl2_lvt_vdd'] = lvl_lvt_vdd_combos
    starlist_dict['lvl2_ulvt_vdd'] = lvl_ulvt_vdd_combos
 
    exceptions_list = ['svt,0.450', '1.200']
    db_exceptions_dict = dict()
    db_exceptions_dict['all'] = exceptions_list
 
    print("Combinations are like this")
    ip_combo_count = 0
    combo_count = 0
    for input_str in input_lines:
        ip_combo_count += 1
        if input_str == '\n':
            ip_combo_count -= 1
        curr_combo = parseLine(input_str, starlist_dict, db_exceptions_dict)
        if curr_combo:
            print(curr_combo)
            combo_count += len(curr_combo)
 
    print("Input had", ip_combo_count, "combinations")
    print("Output had", combo_count, "combinations")
    print("Missing", ip_combo_count - combo_count, "combinations")
 
 
