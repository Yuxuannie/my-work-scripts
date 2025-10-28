import sys
import linecache
import fnmatch
 
 
def parseLibraryFile(library_file, parse_type, char_type="", verbose=False):
    """
    A function that parses a library file
 
    Args:
        library_file (str):
            The full path to the library file to be parsed
        parse_type (str):
            A variable that identifies the type of library file to be parsed
            Can be set to "variation" for sensitivity files or "nominal" for nominal .lib
        char_type (str):
            The type of timing data to extract from the library file
            Default value is set to "" which extracts all timing data
            Other options include "constraint", "delay", and "slew"
        verbose (bool):
            A flag to print debug messages when parsing the library file
 
    Returns:
        lib_data (dict):
            The data structure that contains the timing data from the library file
    """
 
    # Load the headers based on the file type
    (cell_header, pin_header, related_pin_header, timing_header,
     timing_type_header, timing_sense_header, when_condition_header,
     sigma_type_header, index_header, values_header, table_header) = \
        loadHeaders(parse_type, char_type)
 
    # Initialize
    lib_data = dict()
    cell_name = ""
    pin_name = ""
    related_pin_name = ""
    timing_type = ""
    timing_sense = "none"
    when_condition = "NO_CONDITION"
    transition_type = ""
    num_tables_stored = 0
 
    # Store
    i = 0
    while 1:
        i += 1
        current_line = linecache.getline(library_file, i)
 
        if current_line == '':
            if verbose:
                print("INFO:\t Reached end of file.")
            break
 
        elif fnmatch.fnmatch(current_line, cell_header):
            if verbose:
                print("INFO:\t Saw cell header on line %s" % i)
            cell_name = getCellNameFromLine(current_line)
            if verbose:
                print("INFO:\t Current cell is set to %s" % cell_name)
 
        elif fnmatch.fnmatch(current_line, pin_header):
            if verbose:
                print("INFO:\t Saw pin header on line %s" % i)
            pin_name = getPinNameFromLine(current_line)
            if verbose:
                print("INFO:\t Current pin is set to %s" % pin_name)
 
        elif fnmatch.fnmatch(current_line, related_pin_header):
            if verbose:
                print("INFO:\t Saw related pin header on line %s" % i)
            related_pin_name = getRelatedPinNameFromLine(current_line)
            if verbose:
                print(
                    "INFO:\t Current related pin is set to %s" %
                    related_pin_name
                )
 
        elif fnmatch.fnmatch(current_line, when_condition_header):
            if verbose:
                print("INFO:\t Saw when condition header on line %s" % i)
            when_condition = getWhenConditionFromLine(current_line)
            if verbose:
                print(
                    "INFO:\t Current when condition is set to %s" %
                    when_condition
                )
 
        elif fnmatch.fnmatch(current_line, timing_type_header):
            if verbose:
                print("INFO:\t Saw a timing type header on line %s" % i)
            timing_type = getTimingTypeFromLine(current_line)
            if verbose:
                print("INFO:\t Current timing type is set to %s" % timing_type)
 
        elif fnmatch.fnmatch(current_line, timing_sense_header):
            if verbose:
                print("INFO:\t Saw a timing sense header on line %s" % i)
            timing_sense = getTimingSenseFromLine(current_line)
            if verbose:
                print(
                    "INFO:\t Current timing sense is set to %s" % timing_sense
                )
 
        elif fnmatch.fnmatch(current_line, timing_header):
            # Hit a timing block before a table, so reset some data
            if verbose:
                print("INFO:\t Saw a timing () header on line %s" % i)
                print("INFO:\t Resetting the following arc attributes:")
                print("\t\t\t TIMING SENSE = 'none'")
                print("\t\t\t WHEN CONDITION = 'NO_CONDITION'")
            timing_sense = "none"
            when_condition = "NO_CONDITION"
 
        elif fnmatch.fnmatch(current_line, table_header):
            if verbose:
                print("INFO:\t Saw a table header on line %s" % i)
            if parse_type == "variation":
                transition_type = getTranTypeFromOCVTableHeader(current_line)
            elif parse_type == "nominal":
                transition_type = getTableTypeFromNomTableHeader(current_line)
 
            if verbose:
                print(
                    "INFO:\t Current transition type is set to %s" %
                    transition_type
                )
 
            # Check valid table
            valid_table = checkValidTable(
                cell_name, pin_name, related_pin_name, timing_type,
                transition_type
            )
            if not valid_table:
                if verbose:
                    print(
                        "INFO:\t Table on line %s is invalid. Skipping it." % i
                    )
                continue
 
            # Store the data
            if verbose:
                printArcData(
                    cell_name, pin_name, related_pin_name, timing_type,
                    timing_sense, when_condition, transition_type
                )
            i = storeTableData(
                lib_data, library_file, i, cell_name, pin_name,
                related_pin_name, timing_type, timing_sense, when_condition,
                transition_type, sigma_type_header, index_header
            )
            num_tables_stored += 1
 
    print("INFO:\t Finished parsing file.")
    print("INFO:\t Found a total of %s tables." % num_tables_stored)
 
    return lib_data
 
 
def loadHeaders(parse_type, char_type):
    """
    A function that returns the headers of a library file to identify the attributes
    for the timing tables.
    Functionality:
        - Load the headers based on the type of file that is being parsed and the type of
        data to be extracted
        - Headers are strings that may contain wildcards for pattern matching
 
    Args:
        parse_type (str):
            - The type of method used to parse the library file
            - "variation" parses sensitivity files and returns sensitivity file headers
            - "nominal" parses corner libraries and returns nominal file headers
        char_type (str):
            - The type of characterization data in the library file that the user
            wants to parse
            - OPT1: empty string ("") which parses all LVF char types
            - OPT2: "constraint" which parses all LVF constraint types
            - OPT3: "delay" which parses all LVF cell delay types
            - OPT4: "slew" which parses all LVF output slew types
 
    Returns:
        cell_header (str):
            The header that identifies the "cell" attribute of a timing table
        pin_header (str):
            The header that identifies the "pin" attribute of a timing table
        related_pin_header (str):
            The header that identifies the "related pin" attribute of a timing table
        timing_header (str):
            The header that identifies when a "timing block" begins
        timing_type_header (str):
            The header that identifies the "timing type" attribute of a timing table
        timing_sense_header (str):
            The header that identifies the "timing sense" attribute of a timing table
        when_condition_header (str):
            The header that identifies the "when" attribute of a timing table
        sigma_type_header (str):
            The header that identifies the "sigma type" attribute of a timing table
        index_header (str):
            The header that identifies the "index" lines for a timing table
        values_header (str):
            The header that identifies the "values" line of a set of timing values
        table_header (str):
            The header that identifies the "table name" line for a timing table
 
    """
 
    cell_header = "*cell (*) {*"
    pin_header = "*pin*(*) {*"
    related_pin_header = "*related_pin : *"
    timing_header = "*timing () {*"
    timing_type_header = "*timing_type :*"
    timing_sense_header = "*timing_sense :*"
    when_condition_header = "*when : \"*\"*"
    sigma_type_header = "*sigma_type : *"
    index_header = "*index_* (\"*"
    values_header = "*values ( *\n"
    table_header = None
    if parse_type == "variation":
        # If no char type is specified, parse all ocv_sigma tables
        if char_type == "":
            table_header = "*ocv_sigma_*_*(*_template_*x*)*"
        # Constraints
        elif char_type == "constraint":
            table_header = "*ocv_sigma_*_constraint*(*_template_*x*)*"
        # Delay
        elif char_type == "delay":
            table_header = "*ocv_sigma_cell_*(delay_template_*x*)*"
        elif char_type == "slew":
            table_header = "*ocv_sigma_*_transition*(delay_template_*x*)*"
        else:
            print("ERROR:\t Invalid char_type of %s" % char_type)
            print(
                "INFO:\t If you specify char_type, it must be one of 'constraint' | 'delay' | 'slew'"
            )
            print("INFO:\t Exiting now.")
            sys.exit(-1)
    elif parse_type == "nominal":
        # If no char type is specified, parse all the tables
        if char_type == "":
            table_header = "*_*(*_template_*x*)*"
        elif char_type == "constraint":
            table_header = "*_constraint*(*_template_*x*)*"
        elif char_type == "delay":
            table_header = "*cell_*(delay_template_*x*)*"
        elif char_type == "slew":
            table_header = "*_transition*(delay_template_*x*)*"
        else:
            print("ERROR:\t Invalid char_type of %s" % char_type)
            print(
                "INFO:\t If you specify char_type, it must be one of 'constraint' | 'delay' | 'slew'"
            )
            print("INFO:\t Exiting now.")
    else:
        print("ERROR:\t The 'parse_type' value of %s is invalid." % parse_type)
        print("INFO:\t Only type 'variation' is valid for parse_type now.")
        print("INFO:\t Exiting now.")
        sys.exit(0)
 
    return cell_header, pin_header, related_pin_header, timing_header, \
           timing_type_header, timing_sense_header, when_condition_header, \
           sigma_type_header, index_header, values_header, table_header
 
 
def getCellNameFromLine(input_line):
    """
    A function that gets the cell value from the current line
 
    Args:
        input_line (str):
            The line from the library file that is supposed to contain the "cell"
            attribute of the current timing table
 
    Returns:
        cell_name (str):
            The "cell" of the current timing table
    """
 
    rhs_line = input_line.split('cell (')[1]
    cell_name = rhs_line.split(')')[0]
 
    return cell_name
 
 
def getPinNameFromLine(input_line):
    """
    A function that gets the pin value from the current line
    Functionality:
        Split the opening curly brace "(" separately from the keyword "pin" because a
        .lib file and .sens file write the pin attribute differently.
 
    Args:
        input_line (str):
            The line from the library file that is supposed to contain the "pin"
            attribute of the current timing table
 
    Returns:
        pin_name (str):
            The "pin" of the current timing table
    """
 
    rhs_line = input_line.split('pin')[1]
    pin_name = rhs_line.split('(')[1].split(')')[0]
 
    return pin_name
 
 
def getRelatedPinNameFromLine(input_line):
    """
    A function that gets the related_pin value from the current line
 
    Args:
        input_line (str):
            The line from the library file that is supposed to contain the
            "related_pin" attribute of the current timing table
 
    Returns:
        rel_pin_name (str):
            The "related_pin" of the current timing table
    """
 
    rhs_line = input_line.split('related_pin : ')[1]
    rel_pin_name_with_quotes = rhs_line.split(';')[0]
    rel_pin_name = rel_pin_name_with_quotes.strip('"')
 
    return rel_pin_name
 
 
def getTimingTypeFromLine(input_line):
    """
    A function that gets the timing_type value from the current line
 
    Args:
        input_line (str):
            The line from the library file that is supposed to contain the
            "timing_type" attribute of the current timing table
 
    Returns:
        timing_type (str):
            The "timing_type" of the current timing table
    """
 
    rhs_line = input_line.split('timing_type : ')[1]
    timing_type = rhs_line.split(';')[0].strip()
 
    return timing_type
 
 
def getWhenConditionFromLine(input_line):
    """
    A function that gets the when_condition value from the current line
 
    Args:
        input_line (str):
            The line from the library file that is supposed to contain the
            "when_condition" attribute of the current timing table
 
    Returns:
        when_condition (str):
            The "when_condition" of the current timing table
    """
 
    rhs_line = input_line.split('when : ')[1]
    when_condition_with_quotes = rhs_line.split(';')[0]
    when_condition = when_condition_with_quotes.strip('"')
 
    return when_condition
 
 
def getTranTypeFromOCVTableHeader(table_header):
    """
    A function that gets the table type from the current line
    Assumptions:
        Assumes the current line is in LVF format (e.g., ocv_sigma_*)
 
    Args:
        table_header (str):
            The line from the library file that represents the table header (e.g.,
            ocv_sigma_rise_constraint) of the current timing table
 
    Returns:
        table_name (str):
            The table type of the current timing table, e.g. rise_constraint
    """
 
    rhs_line = table_header.split('ocv_sigma_')[1]
    tran_type_lower = (rhs_line.split('(')[0]).strip()
    tran_type = tran_type_lower.upper()
 
    return tran_type
 
 
def getTableTypeFromNomTableHeader(table_header):
    """
    A function that gets the table type from the current line.
    Assumptions:
        Assumes the current line is in standard library format (e.g., cell_rise)
 
    Args:
        table_header (str):
            The line from the library file that represents the table header (e.g.,
            rise_constraint) of the current timing table
 
    Returns:
        table_name (str):
            The table type of the current timing table, e.g. rise_constraint
    """
 
    if "ocv_sigma" in table_header:
        tran_type = ""
    else:
        rhs_line = (table_header.split('(')[0]).strip()
        tran_type = rhs_line.upper()
 
    return tran_type
 
 
def getTimingSenseFromLine(input_line):
    """
    A function that gets the timing_sense value from the current line
 
    Args:
        input_line (str):
            The line from the library file that is supposed to contain the
            "timing_sense" attribute of the current timing table
 
    Returns:
        timing_sense (str):
            The "timing_sense" of the current timing table.
    """
 
    rhs_line = input_line.split('timing_sense : ')[1]
    timing_sense = rhs_line.split(';')[0]
 
    return timing_sense
 
 
def printArcData(
    cell_name, pin_name, related_pin_name, timing_type, timing_sense,
    when_condition, table_type
):
    """
    A function that prints the attributes for a timing table; primarily used for debug.
 
    Args:
        cell_name (str):
            The cell name that corresponds to the current timing table
        pin_name (str):
            The pin name that corresponds to the current timing table
        related_pin_name (str):
            The related pin name that corresponds to the current timing table
        timing_type (str):
            The timing type that corresponds to the current timing table
        timing_sense (str):
            The timing sense that corresponds to the current timing table
        when_condition (str):
            The when condition that corresponds to the current timing table
        table_type (str):
            The table name that corresponds to the current timing table (e.g., cell_rise)
 
    Returns:
        None, debug function that prints information
    """
 
    print("INFO:\t Storing table data for the following arc:")
    print("\t CELL:\t\t\t %s" % cell_name)
    print("\t PIN:\t\t\t %s" % pin_name)
    print("\t REL PIN:\t\t %s" % related_pin_name)
    print("\t TIMING TYPE:\t %s" % timing_type)
    print("\t TIMING SENSE:\t %s" % timing_sense)
    print("\t WHEN:\t\t\t %s" % when_condition)
    print("\t TRANSITION:\t\t %s" % table_type)
 
 
def addKeyToDict(input_dict, input_key):
    """
    Adds the input_key to the input_dict if it does not exist.
    Adds the key as type 'dict'.
 
    A function that tries to add the current key to the input dictionary.
    If the key already exists, don't overwrite the existing data
 
    Args:
        input_dict (dict):
            A dictionary whose values we want to update
        input_key:
            A variable whose value may be added as a key to the input dictionary
 
    Returns:
        None; dictionaries are mutable
    """
 
    if not input_key in input_dict:
        input_dict[input_key] = dict()
 
 
def getIndexValuesFromLines(library_file, starting_line, index_header):
    """
    A function that returns the data values in the "index_1" and "index_2" entries of
    the current timing table.
 
    First search for a line that matches the index_header variable
        If it is not found, throw an error and exit
    Assume this line is the "index_1" line and that it matches the following pattern:
        *index_1 ("a, b, c, d, e")*
    Store the data for index_1
    Get the next line in the file and assume it is the "index_2" line and repeat
    """
 
    i = starting_line
    current_line = None
    while 1:
        i += 1
        current_line = linecache.getline(library_file, i)
 
        if fnmatch.fnmatch(current_line, index_header):
            break
        elif current_line == '':
            print("ERROR:\t Prematurely reached end of file.")
            print("INFO:\t Could not find index_* headers.")
            print("INFO:\t Exiting now.")
            sys.exit(-1)
 
    index_1_data = current_line.split('"')[1].split(',')
    i += 1
    current_line = linecache.getline(library_file, i)
    index_2_data = current_line.split('"')[1].split(',')
 
    return index_1_data, index_2_data, i
 
 
def findSigmaType(library_file, starting_line, sigma_type_header, index_header):
    """
    A function that returns the "sigma_type" value of the current timing table.
    If the current timing table does not have one, default it to "none"
 
    First, search for a line that matches the sigma_type_header variable
        If it is not found before reaching the end of the file, throw an error and exit
    Call the function that gets the sigma type from this line
    """
 
    sigma_type = "none"
 
    i = starting_line
    while 1:
        i += 1
        current_line = linecache.getline(library_file, i)
 
        if current_line == '':
            print("ERROR:\t Prematurely reached end of file.")
            print("INFO:\t Reached EOF before seeing sigma type or index.")
            print("INFO:\t Exiting now.")
            sys.exit(-1)
        elif fnmatch.fnmatch(current_line, sigma_type_header):
            sigma_type = getSigmaTypeFromLine(current_line)
        elif fnmatch.fnmatch(current_line, index_header):
            i -= 1
            break
 
    return sigma_type, i
 
 
def getSigmaTypeFromLine(input_line):
    """
    A function that gets the sigma_type value from the current line
 
    Args:
        input_line (str):
            The line from the library file that is supposed to containin the
            "sigma_type" attribute of the current timing table
 
    Returns:
        sigma_type (str):
            The "sigma_type" of the current timing table.
    """
 
    rhs_line = input_line.split('sigma_type : ')[1]
    sigma_type = rhs_line.split(';')[0]
    return sigma_type
 
 
def getTimingValuesFromTable(library_file, last_index_line):
    """
    A function to store the N x M table from the library file to a list.
    Assumptions on the format of the table:
        - A table in the current context is the set of rows containing timing data only
        - The table may be preceeded by headers (e.g., a "values (" line)
        - Only rows of the table are enclosed in double quotes (")
        - The table has ended before the delimeting character "}"
    Algorithm to get the data:
        - Read the file starting after the last "index" line and store all lines of
        the file containing double quotes ("). These lines contain the actual timing data.
        - Assume the lines that were stored are comma-separated values
        - Store all values from the lines to a list of strings
 
    Args:
        library_file (str):
            The full path to the library file
        last_index_line (int):
            The line number of the last "index" line that was seen
 
    Returns:
        table_data (list):
            - A "flattened" representation of the current timing table of the library file, e.g.
            Table representation in library file
                a, b, c, d, e,
                f, g, h, i, j,
                k, l, m, n, o
            List representation from function
                [a, b, c, d, e, f, g, h, i, j, k, l, m, n, o]
 
        i (int): The last line in the file that we tried to parse
    """
 
    table_line_list = list()
 
    i = last_index_line
    while 1:
        i += 1
        current_line = linecache.getline(library_file, i)
 
        if current_line == '':
            print("ERROR:\t Prematurely reached end of file.")
            print("INFO:\t Could not find end of table before EOF.")
            print("INFO:\t Exiting now.")
            sys.exit(-1)
        elif fnmatch.fnmatch(current_line, '*"*'):
            table_line_list.append(current_line)
        elif fnmatch.fnmatch(current_line, '*}*\n'):
            break
 
    # Parse and store
    table_data = list()
    for table_line in table_line_list:
        data_line = table_line.split('"')[1].split(',')
        [table_data.append(x) for x in data_line]
 
    return table_data, i
 
 
def storeTableData(
    lib_data, library_file, table_line, cell_name, pin_name, related_pin_name,
    timing_type, timing_sense, when_condition, table_type, sigma_type_header,
    index_header
):
    """
    A function that will call other functions to extract information out of the
    current timing table and store it to the input data structure
 
    Context:
        - A timing table in the current context is the set of lines from the table
        header (e.g., ocv_sigma_rise_constraint) to the final delimeter "}"
 
    Args:
        lib_data (dict):
            Data structure representing the timing information of the library file
        library_file (str):
            The full path to the library file
        table_line (int):
            The line where the timing table begins (e.g., ocv_sigma_rise_constraint)
        cell_name (str):
            The cell name corresponding to the current timing table
        pin_name (str):
            The pin name corresponding to the current timing table
        related_pin_name (str):
            The related pin name corresponding to the current timing table
        timing_type (str):
            The timing_type corresponding to the current timing table
        timing_sense (str):
            The timing_sense corresponding to the current timing table
        table_type (str):
            The name of the transition and type of the current timing table (e.g., rise_constraint)
        sigma_type_header (str):
            The pattern to identify the "sigma_type" of the current timing table
        index_header (str):
            The pattern to identify the "index" lines of the current timing table
 
    Returns:
        i (int):
            The line of the file where the timing table delimeter "}" was seen
    """
 
    # Add keys only if they don't exist
    addKeyToDict(lib_data, cell_name)
    addKeyToDict(lib_data[cell_name], pin_name)
    addKeyToDict(lib_data[cell_name][pin_name], related_pin_name)
    addKeyToDict(lib_data[cell_name][pin_name][related_pin_name], timing_type)
    addKeyToDict(
        lib_data[cell_name][pin_name][related_pin_name][timing_type],
        when_condition
    )
    addKeyToDict(
        lib_data[cell_name][pin_name][related_pin_name][timing_type]
        [when_condition], timing_sense
    )
    addKeyToDict(
        lib_data[cell_name][pin_name][related_pin_name][timing_type]
        [when_condition][timing_sense], table_type
    )
 
    # Get the sigma type, index_1, and index_2 data
    sigma_type, i = findSigmaType(
        library_file, table_line, sigma_type_header, index_header
    )
    index_1_data, index_2_data, i = getIndexValuesFromLines(
        library_file, i, index_header
    )
 
    # Store attributes
    lib_data[cell_name][pin_name][related_pin_name][timing_type][
        when_condition][timing_sense][table_type]['index_1'] = index_1_data
    lib_data[cell_name][pin_name][related_pin_name][timing_type][
        when_condition][timing_sense][table_type]['index_2'] = index_2_data
 
    # Get and store the timing values of the table
    timing_data, i = getTimingValuesFromTable(library_file, i)
    lib_data[cell_name][pin_name][related_pin_name][timing_type][
        when_condition][timing_sense][table_type][sigma_type] = timing_data
 
    return i
 
 
def queryNumSigmaTables(lib_data, sigma_type):
    """
    Returns the number of 'sigma_type' tables in the dictionary.
    """
 
    table_count = 0
    for cell in lib_data:
        for pin in lib_data[cell]:
            for rel_pin in lib_data[cell][pin]:
                for timing_type in lib_data[cell][pin][rel_pin]:
                    for when in lib_data[cell][pin][rel_pin][timing_type]:
                        for tran in lib_data[cell][pin][rel_pin][timing_type][
                            when]:
                            tran_data = lib_data[cell][pin][rel_pin][
                                timing_type][when][tran]
 
                            if not sigma_type in tran_data:
                                continue
                            else:
                                table_count += 1
 
    print("There are %s tables with sigma type %s" % (table_count, sigma_type))
    return table_count
 
 
def checkValidTable(cell, pin, related_pin, timing_type, table_type):
    """
    A function that checks whether the current attributes that are supposed to
    represent a timing table are valid values.
 
    Functionality:
    The current implementation of the library parser does not support
    "min_pulse_width" timing types or any type of "power" table. Attributes containing
    these values mark the table as invalid.
 
    Args:
        cell (str):
            The cell name corresponding to the current timing table
        pin (str):
            The pin name corresponding to the current timing table
        related_pin (str):
            The related pin name corresponding to the current timing table
        timing_type (str):
            The timing_type corresponding to the current timing table
        table_type (str):
            The name of the table corresponding to the current timing table (e.g.,
            rise_constraint)
 
    Returns:
        valid_table (int):
            A number representing whether the attributes representing the current
            timing table form a "valid" table that can be stored/parsed.
    """
 
    valid_table = 1
    if cell == "":
        valid_table = 0
    elif pin == "":
        valid_table = 0
    elif related_pin == "":
        valid_table = 0
    elif timing_type == "":
        valid_table = 0
    elif timing_type == "min_pulse_width":
        valid_table = 0
    elif timing_type == "":
        valid_table = 0
    elif table_type == "":
        valid_table = 0
    elif "POWER" in table_type:
        valid_table = 0
 
    return valid_table
 
 
def getNumTablesForCellAndType(lib_info, in_cell, arc_type):
    """
    Gets the number of "arc_type" tables for the given cell
    """
 
    # Initialize
    valid_sigma_types = ["none", "early", "late"]
    if arc_type == "hold":
        valid_timing_types = [
            "hold_rising", "hold_falling", "non_seq_hold_rising",
            "non_seq_hold_falling", "removal_rising", "removal_falling"
        ]
        valid_table_types = ["RISE_CONSTRAINT", "FALL_CONSTRAINT"]
 
    elif arc_type == "hold_only":
        valid_timing_types = ["hold_rising", "hold_falling"]
        valid_table_types = ["RISE_CONSTRAINT", "FALL_CONSTRAINT"]
 
    elif arc_type == "removal":
        valid_timing_types = ["removal_rising", "removal_falling"]
        valid_table_types = ["RISE_CONSTRAINT", "FALL_CONSTRAINT"]
 
    elif arc_type == "non_seq_hold":
        valid_timing_types = ["non_seq_hold_rising", "non_seq_hold_falling"]
        valid_table_types = ["RISE_CONSTRAINT", "FALL_CONSTRAINT"]
 
    elif arc_type == "setup":
        valid_timing_types = [
            "setup_rising", "setup_falling", "non_seq_setup_rising",
            "non_seq_setup_falling", "recovery_rising", "recovery_falling"
        ]
        valid_table_types = ["RISE_CONSTRAINT", "FALL_CONSTRAINT"]
 
    elif arc_type == "setup_only":
        valid_timing_types = ["setup_rising", "setup_falling"]
        valid_table_types = ["RISE_CONSTRAINT", "FALL_CONSTRAINT"]
 
    elif arc_type == "non_seq_setup":
        valid_timing_types = ["non_seq_setup_rising", "non_seq_setup_falling"]
        valid_table_types = ["RISE_CONSTRAINT", "FALL_CONSTRAINT"]
 
    elif arc_type == "recovery":
        valid_timing_types = ["recovery_rising", "recovery_falling"]
        valid_table_types = ["RISE_CONSTRAINT", "FALL_CONSTRAINT"]
 
    elif arc_type == "nochange":
        valid_timing_types = [
            "nochange_low_low", "nochange_low_high", "nochange_high_low",
            "nochange_high_high"
        ]
        valid_table_types = ["RISE_CONSTRAINT", "FALL_CONSTRAINT"]
 
    elif arc_type == "delay":
        valid_timing_types = [
            "clear", "preset", "combinational", "combinational_fall",
            "combinational_rise", "falling_edge", "rising_edge",
            "three_state_disable", "three_state_enable"
        ]
        valid_table_types = ["CELL_RISE", "CELL_FALL"]
 
    elif arc_type == "slew":
        valid_timing_types = [
            "clear", "preset", "combinational", "combinational_fall",
            "combinational_rise", "falling_edge", "rising_edge",
            "three_state_disable", "three_state_enable"
        ]
        valid_table_types = ["RISE_TRANSITION", "FALL_TRANSITION"]
 
    else:
        valid_timing_types = []
 
    # Iterate
    table_count = 0
    try:
        for pin in lib_info[in_cell]:
            for rel_pin in lib_info[in_cell][pin]:
                for timing_type in lib_info[in_cell][pin][rel_pin]:
                    if not timing_type in valid_timing_types:
                        continue
                    for sense in lib_info[in_cell][pin][rel_pin][timing_type]:
                        for when in lib_info[in_cell][pin][rel_pin][timing_type
                                                                   ][sense]:
                            for tran in lib_info[in_cell][pin][rel_pin][
                                timing_type][sense][when]:
                                if not tran in valid_table_types:
                                    continue
 
                                table_info = lib_info[in_cell][pin][rel_pin][
                                    timing_type][sense][when][tran]
                                for sigma_type in table_info:
                                    if not sigma_type in valid_sigma_types:
                                        continue
                                    table_count += 1
    except KeyError as errmsg:
        print("The following exception was raised %s", errmsg)
 
    return table_count
 
 
def flattenLibData(lib_data):
    """
    A function that returns an iterator representing a "flattened" library data structure
 
    Args:
        lib_data (dict):
            The dictionary representing the parsed library file
 
    Returns:
        flat_lib_data (generator):
            A generator representing the "flattened" library, down to a timing table
    """
    flat_lib_data = \
        ((cell, pin, rel_pin, t_type, when, t_sense, table_name, sigma)
         for cell in lib_data
         for pin in lib_data[cell]
         for rel_pin in lib_data[cell][pin]
         for t_type in lib_data[cell][pin][rel_pin]
         for when in lib_data[cell][pin][rel_pin][t_type]
         for t_sense in lib_data[cell][pin][rel_pin][t_type][when]
         for table_name in lib_data[cell][pin][rel_pin][t_type][when][t_sense]
         for sigma in lib_data[cell][pin][rel_pin][t_type][when][t_sense][table_name])
 
    return flat_lib_data
 
