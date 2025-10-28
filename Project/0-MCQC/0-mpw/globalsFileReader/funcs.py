"""
This module contains functions to set default variable values and parse the user's
text-formatted globals file to add in any new options or overwrite the default ones.
"""
 
import fnmatch
 
 
def readGlobalsFile(globals_file, user_options=None):
    """
    A function that reads the user's text-formatted globals file and parses it
 
    Args:
        globals_file (str):
            The path to the globals file
        user_options (dict):
            A dictionary to store the options from the globals file
            Default is None, which forces the dictionary to be initialized in the
            function
 
    Returns:
        user_options (dict):
            A dictionary that represents the variable names and settings as a
            key-value pair
    """
    if user_options is None:
        user_options = dict()
    set_var_header = "set_var *"
 
    with open(globals_file, 'r') as f:
        globals_file_lines = f.readlines()
 
    for line in globals_file_lines:
        if fnmatch.fnmatch(line, set_var_header):
            myline = line.split(';')[0].strip('\n\t')
            myline_info = myline.split()
 
            var_name = myline_info[1].upper()
            # Variables with the keyword "_list" in them should be treated as lists
            if "_list".upper() in var_name:
                var_val = ' '.join(myline_info[2:]).strip('"').split()
            else:
                var_val = myline_info[2].strip('"')
            user_options[var_name] = var_val
 
    # Type casting
    user_options['MAX_NUM_WHEN'] = int(user_options['MAX_NUM_WHEN'])
    user_options['NUM_SAMPLES'] = int(user_options['NUM_SAMPLES'])
 
    return user_options
 
 
def loadDefaultOptions(user_options=None):
    """
    A function that loads the default options of the LVF QA Flow package
 
    Args:
        user_options (dict):
            A dictionary to store the options
             Default is None, which forces the dictionary to be initialized in the
             function
 
    Returns:
        user_options (dict):
            A dictionary that represents the default variable names and settings as a
            key-value pair
    """
 
    if user_options is None:
        user_options = dict()
 
    user_options['PUSHOUT_PER'] = "0.4"
    user_options['PUSHOUT_DIR'] = "POSITIVE"
    user_options['CELL_PATTERN_LIST'] = ["*D1B*"]
    user_options['VALID_ARC_TYPES_LIST'] = ["hold", "removal"]
    user_options['MAX_NUM_WHEN'] = 1
    user_options['NUM_SAMPLES'] = 5000
 
    return user_options
 
