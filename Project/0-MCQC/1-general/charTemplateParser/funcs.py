import sys
import linecache
import os
import re
import copy
 
from charTemplateParser.classes import TemplateInfo
from charTemplateParser.classes import DefineTemplateInfo
from charTemplateParser.classes import Cell
from charTemplateParser.classes import Arc
from charTemplateParser.classes import Index
 
 
def parseTemplateFile(template_file):
    """
    A function that parses the template file and returns a data structure
    representation of its contents
 
    The function will read the template file and store both the tool and tcl
    variables defined inside of it. The function will also store the various
    blocks of the template file such as "define_template", "define_cell",
    "define_arc", and "define_index".
    The function returns a dictionary data structure with the cell, arc, and index
    definitions for the different cells of the template file. It also returns the
    definition for the various template blocks.
 
    Args:
        template_file (str):
            The path to the template file
    Returns:
        template_info (TemplateInfo):
            The data structure representing the template file
    """
    #template_info = dict()
    template_info = TemplateInfo(template_file)
    i = 0
    while 1:
        i += 1
        current_line = linecache.getline(template_file, i)
        if current_line == '':
            break
        elif 'set_var' in current_line:
            storeToolVar(current_line, template_info)
 
        elif 'set ' in current_line:
            storeTclVar(current_line, template_info, i, template_file)
 
        elif 'define_template' in current_line:
            # Parse
            template_name, template = \
                parseDefineTemplateBlock(i, template_file)
 
            # Store
            storeDefineTemplateBlockInfo(template_info, template_name,
                                         template)
 
        elif 'define_cell' in current_line:
            cell_name, cell = \
                parseDefineCellBlock(i, template_file)
            storeDefineCellBlockInfo(template_info, cell_name, cell)
 
        elif 'define_arc' in current_line:
            cell_name, arc = \
                parseDefineArcBlock(i, template_file)
            storeDefineArcBlockInfo(template_info, cell_name, arc)
 
        elif 'define_index' in current_line:
            cell_name, index = \
                parseDefineIndexHeader(i, template_file)
            storeDefineIndexBlockInfo(template_info, cell_name, index)
    sis_path = template_file.replace('/Template/', '/Template_sis/')
    sis_path = sis_path + '.sis'
    if os.path.exists(sis_path):
        sis_info = parseSISTemplate(sis_path)
        template_info._sis_template = sis_info
    return template_info
 
 
def parseSISTemplate(path):
    with open(path, 'r') as f:
        template = f.readlines()
    sis_info = {}
    ght_name = 'glitch_high_threshold'
    glt_name = 'glitch_low_threshold'
    for line in template:
        line = line.strip().replace('{', '').replace('}', '')
        if not line.startswith('set_config_opt') or '-pintype' not in line:
            continue
        if 'glitch_high_threshold' not in line and 'glitch_low_threshold' not in line:
            continue
        s_line = line.split()
        pintype_idx = s_line.index('-pintype')
        ght_idx = s_line.index(ght_name)
        glt_idx = s_line.index(glt_name)
        pintype = s_line[pintype_idx+1].upper()
        ght = s_line[ght_idx+1]
        glt = s_line[glt_idx+1]
        ght_key = '%s_%s' % (pintype, ght_name.upper())
        glt_key = '%s_%s' % (pintype, glt_name.upper())
        sis_info[ght_key] = ght
        sis_info[glt_key] = glt
    return sis_info
 
 
def removeCurlyBracesAndStrip(item):
    """
    A function to remove the enclosing curly braces from the input variable
 
    Args:
        item (str):
            The string to remove the curly braces from
 
    Returns:
        item_stripped (str):
            The input string with the curly braces removed
    """
    item_list = item.strip('{').strip('}').split()
    item_stripped = ' '.join(item_list)
    return item_stripped
 
 
def storeToolVar(line, template_info):
    """
    A function to store the char tool's variable and value that are on the current line
 
    Args:
        line (str):
            The line with the tool variable to be stored
        template_info (TemplateInfo):
            A TemplateInfo object that can store the tool variables
 
    Returns:
        None, dicts are mutable
    """
 
    var_name, var_val = getToolVar(line)
    template_info.addToolVar(var_name, var_val)
 
 
def getToolVar(line):
    """
    A function to get the char tool's variable and value that are on the input line
 
    Args:
        line (str):
            The line with the tool variable to be stored
    Returns:
        var_name (str):
            The name of the tool variable in the line
        var_val (str or None):
            The value of the tool variable in the line
            If no value exists, returns None
    """
    var_info = line.strip().split('set_var ')[1].split()
    var_name = var_info[0]
    try:
        var_val = var_info[1]
    except IndexError:
        var_val = None
    return var_name, var_val
 
 
def storeTclVar(line, template_info, line_num, template_file):
    """
    A function to store the tcl variable and value that are on the current line
 
    Args:
        line (str):
            The line with the tcl variable
        template_info (TemplateInfo):
            A data structure representing the information in the template.tcl file
        line_num (int):
            The line where the tcl variable is initially defined
            Since the tcl variable's value may continue onto later lines, we may need
            to look ahead in the file and grab those lines
        template_file (str):
            The path to the template file
    """
    var_name, var_val = getTclVar(line, line_num, template_file)
    template_info.addTclVar(var_name, var_val)
 
 
def getTclVar(line, line_num, template_file):
    """
    A function to get the value of the tcl variable on the current line
 
    Args:
        line (str):
            The line with the tcl variable
        line_num (int):
            The line where the tcl variable is defined
            The variable's value may continue onto future lines, so we may need to
            grab those lines and need to know where to start from
        template_file (str):
            The path to the template file.
 
    Returns:
        var_name (str):
            The name of the tcl variable
        var_val (str, list, or None):
            The value of the tcl variable, which may be a str or list depending on
            the value defined by the tcl variable
    """
 
    var_info = line.strip().split('set ')[1].split()
    var_name = var_info[0]
 
    # If there are more than 3 entries in the line (set var_name var_val xxx) then
    # check if we need to store the variable as a list
    if len(var_info) > 2:
        # If there is a curly brace delimeter, the variable value is a list
        if var_info[1] == '{':
            var_val_list = set()
 
            # Get lines and store the values until we hit the delimeter
            while 1:
                line_num += 1
                current_line = linecache.getline(template_file, line_num)
                if current_line == '':
                    print("ERROR: Couldn't finish storing tcl var from '%s'" % line)
                    print("Fatal error. Exiting now.")
                    sys.exit(0)
 
                current_val = current_line.strip().split()[0]
                if current_val == '}':
                    break
                var_val_list.add(current_val)
 
                if '}' in current_line:
                    break
 
            var_val = var_val_list
 
        # Otherwise, it may have just been a comment
        else:
            var_val = var_info[1]
 
    else:
        # If there is no value for the tcl variable, then assign it a value of None
        try:
            var_val = var_info[1]
        except IndexError:
            var_val = None
    return var_name, var_val
 
 
def parseDefineTemplateBlock(line_num, template_file):
    """
    A function to parse the "define_template" block of a template file.
 
    Args:
        line_num (int):
            The line number where the "define_template" block is initialized
        template_file (str):
            The path to the template file we are parsing
    Returns:
        template_block_name (str):
            The name of the template block
        attribute_list (list):
            A list of strings that correspond to the define_template attributes in
            chronological order
        value_list (list):
            A list of strings that correspond to the values for the attributes in
            the define_template block, in the same order as the attribute_list
    """
 
    # Initialize variables and define the header for the name of the template block
    template_block_name = None
    template = dict()
 
    # Search through the template file
    while 1:
        line_num += 1
        current_line = linecache.getline(template_file, line_num)
        # The name of the template is defined at the end, so break after we hit it
        if current_line.strip()[-1] != '\\':
            template_block_name = current_line.strip()
            break
        elif current_line == '':
            break
        # Store the attribute and values of the block in separate, indexed variables
        else:
            attribute, value = getBlockAttribute(current_line)
            if '{' in value:
                value = removeCurlyBracesAndStrip(value)
            template[attribute] = value
 
    return template_block_name, template
 
 
def storeDefineTemplateBlockInfo(template_info, template_block_name, template):
    """
    A function to store the contents/information of the "define_template" block
    to the input data structure.
    Functionality:
        First check if there is a non-None type template block name
            Throw an error and exit if it is a None type
        Next, iterate through the attribute list and store both the attribute name
        and corresponding attribute value from the value_list
 
    Args:
        template_info (TemplateInfo):
            A data structure that stores all the information about the template
        template_block_name (str):
            The name of the template block that we are trying to store
        attribute_list (list):
            A list of strings containing the attributes in the template block
            in order of when they were seen
        value_list (list):
            A list of strings containing the values for the attributes in
            the template block in the same order as the attribute_list argument
 
    Returns:
        None, dicts are mutable
    """
    if template_block_name is None:
        print("ERROR: Saw a define_template block but couldn't get the name.")
        print("Fatal error. Exiting now.")
        sys.exit(0)
 
    # Init
 
    template['name'] = template_block_name
 
    # Create
    dt_obj = DefineTemplateInfo(**template)
 
    # Store
    template_info.addDefineTemplate(dt_obj)
 
 
def parseDefineCellBlock(line_num, template_file):
    """
    A function to parse the "define_cell" block of a template file.
 
    Args:
        line_num (int):
            The line number where the "define_cell" block is initialized
        template_file (str):
            The path to the template file we are parsing
    Returns:
        cell_block_name (str):
            The name of the cell corresponding to the define_cell block
        attribute_list (list):
            A list of strings that correspond to the define_cell attributes in
            chronological order
        value_list (list):
            A list of strings that correspond to the values for the attributes in the
            define_cell block, in the same order as the attrbute list
    """
 
    # Initialize variables and define the header for the name of the cell of
    # the define_cell block
    cell_block_name = None
    cell = dict()
    # Search through the template file
    while 1:
        line_num += 1
        current_line = linecache.getline(template_file, line_num)
 
        # The name of the cell for this define_cell block is defined at the end,
        # so break after we hit it
        if current_line.strip()[-1] != '\\':
            cell_block_name = current_line.strip()
            break
        elif current_line == '' or current_line == '\n':
            break
        elif re.search('user_arcs_only', current_line):
            continue
        # Store the attribute and values of the block in separate, indexed variables
        elif re.search('-when', current_line):
            while 1:
                line_num += 1
                current_line = linecache.getline(template_file, line_num)
                s_cur_line = current_line.strip()
                if s_cur_line and s_cur_line[-1] != '\\':
                    line_num -= 1
                    break
                if re.search(r"\"", current_line) or '-' in current_line:
                    break
                else:
                    continue
        else:
            attribute, value = getBlockAttribute(current_line)
            if len(value) == 0:
                value = "True"
            elif '{' in value:
                value = removeCurlyBracesAndStrip(value)
            cell[attribute] = value
 
    return cell_block_name, cell
 
 
def storeDefineCellBlockInfo(template_info, cell_block_name, cell):
    """
    A function to store the contents/information of the "define_cell" block to the
    input data structure.
    Functionality:
        First check if there is a non-None type cell name for the block
            Throw an error and exit if it is a None type
        Next, iterate through the attribute list and store both the attribute name
        and corresponding attribute value from the value_list
 
    Args:
        template_info (TemplateInfo):
            A data structure that stores all the information from the template.tcl file
        cell_block_name (str):
            The name of the cell from the define_cell block that we are trying to store
        attribute_list (list):
            A list of strings containing the attributes in the define_cell block
            in order of when they were seen
        value_list (list):
            A list of strings containing the values for the attributes in the
            define_cell block in the same order as the attribute_list argument
 
    Returns:
        None, dicts are mutable
    """
    if cell_block_name is None:
        print("ERROR: Saw a define_cell block but couldn't get the name.")
        print("Fatal error. Exiting now.")
        sys.exit(0)
 
    if 'async' in cell:
        cell['aasync'] = copy.deepcopy(cell['async'])
        del cell['async']
    cell['name'] = cell_block_name
    # Create
    cell = Cell(**cell)
 
    # Store
    template_info.addCell(cell)
 
 
def parseDefineArcBlock(line_num, template_file):
    """
    A function to parse the "define_arc" block of a template file.
 
    Args:
        line_num (int):
            The line number where the "define_cell" block is initialized
        template_file (str):
            The path to the template file we are parsing
    Returns:
        cell_name (str):
            The name of the cell corresponding to the define_arc block
        attribute_list (list):
            A list of strings that corresponds to the define_arc attributes in
            chronological order
        value_list (list):
            A list of strings that correspond to the values for the attributes in the
            define_arc block, in the same order as the attribute list
    """
 
    # Initialize variables and define the header for the name of the cell of the
    # define_arc block
    cell_name = None
    arc = dict()
 
    while 1:
        line_num += 1
        current_line = linecache.getline(template_file, line_num)
        # The name of the cell for this define_arc block is defined at the end,
        # so break after we hit it
        if current_line.strip()[-1] != '\\':
            cell_name = current_line.strip()
            break
        elif current_line == '':
            break
        # Store the attribute and values of the block in separate, indexed variables
        else:
            attribute, value = getBlockAttribute(current_line)
            if '{' in value:
                value = removeCurlyBracesAndStrip(value)
            arc[attribute] = value
 
    # Add default values for some define_arc attributes if they were not defined
    if "when" not in arc:
        arc['when'] = 'NO_CONDITION'
    if "type" not in arc:
        arc['type'] = 'combinational'
 
    return cell_name, arc
 
 
def storeDefineArcBlockInfo(template_info, cell_name, arc):
    """
    A function to store the contents/information of the "define_arc" block to the
    input data structure.
    Functionality:
        First check if there is a non-None type cell name for the define_arc block
            Throw an error and exit if it is a None type
        Next, iterate through the attribute list and store both the attribute name
        and corresponding attribute value from the value_list
 
    Args:
        template_info (TemplateInfo):
            A data structure that stores all the information from the template file
        cell_name (str):
            The name of the cell that corresponds to the define_arc block
        attribute_list (list):
            A list of strings containing the attributes in the define_arc block in
            order of when they were seen
        value_list (list):
            A list of strings containing the values for the attributes in the
            define_cell block in the same order as the attribute_list argument
 
    Returns:
        None, dicts are mutable
    """
    if cell_name is None:
        print("ERROR: Saw a define_arc block but couldn't get the cell name.")
        print("Fatal error. Exiting now.")
        sys.exit(0)
 
    arc['cell'] = cell_name
    # Create
    arc = Arc(**arc)
 
    # Get the Cell
    cell_obj = template_info.getCell(arc.cell())
 
    # Store the arc (automatically adds arc ID)
    cell_obj.addArc(arc)
 
 
def parseDefineIndexHeader(line_num, template_file):
    """
    A function to parse the "define_index" block of a template file
 
    Args:
        line_num (int):
            The line number where the "define_index" block is initialized
        template_file (str):
            The path to the template file we are parsing
    Returns:
        cell_name (str):
            The name of the cell corresponding to the define_index block
        attribute_list (list):
            A list of strings that correspond to the define_index attributes in
            chronological order
        value_list (list):
            A list of strings that correspond to the values for the attributes in the
            define_index block, in the same order as attribute list
    """
 
    # Initialize variables and define the header for the name of the cell of the
    # define_index block
    cell_name = None
    index = dict()
    # Search through the template file
    while 1:
        line_num += 1
        current_line = linecache.getline(template_file, line_num)
        # The name of the cell for this define_index block is defined at the end,
        # so break after we hit it
        if current_line.strip()[-1] != '\\':
            cell_name = current_line.strip()
            break
        elif current_line == '':
            break
        # Store the attribute and values of the block in separate, indexed variables
        else:
            attribute, value = getBlockAttribute(current_line)
            if '{' in value:
                value = removeCurlyBracesAndStrip(value)
            index[attribute] = value
 
    return cell_name, index
 
 
def storeDefineIndexBlockInfo(template_info, cell_name, index):
    """
    A function to store the contents/information of the "define_index" block to the
    input data structure.
    Functionality:
        First check if there is a non-None type cell name for the block
            Throw an error and exit if it is a None type
        Next, iterate through the attribute list and store both the attribute name
        and corresponding attribute value from the value_list
 
    Args:
        template_info (TemplateInfo):
            A data structure that stores all the information from the template file
        cell_name (str):
            The name of the cell from the define_index block that we are trying to store
        attribute_list (list):
            A list of strings containing the attributes in the define_index block in
            order of when they were seen
        value_list (list):
            A list of strings containing the values for the attributes in the
            define_index block in the same order as the attribute_list argument
 
    Returns:
        None, dicts are mutable
    """
    if cell_name is None:
        print("ERROR: Saw a define_index block but couldn't get the cell name.")
        print("Fatal error. Exiting now.")
        sys.exit(0)
 
    index['cell'] = cell_name
    # Create
    di_obj = Index(**index)
 
    # Get the cell
    cell_obj = template_info.getCell(di_obj.cell())
 
    # Store the index
    if cell_obj:
        cell_obj.addIndex(di_obj)
 
 
def getBlockAttribute(attribute_line):
    """
    A function to get the attribute of a block in the template.tcl file
    Example:
        The "-input" attribute of a "define_cell" block
        The "-pin" attribute of a "define_arc" block
 
    Args:
        attribute_line (str):
            The line containing the attribute name and value
    Returns:
        attribute_name (str):
            The name of the block attribute
        attribute_value (str):
            The value of the block attribute
    """
 
    fisrt_space = attribute_line.strip().index(' ')
    attribute_name = attribute_line.strip()[1:fisrt_space].strip()
    attribute_value = attribute_line.strip()[fisrt_space:-1].strip()
 
    return attribute_name, attribute_value
 
