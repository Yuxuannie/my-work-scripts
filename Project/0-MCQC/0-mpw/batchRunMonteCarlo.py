import fnmatch
import getopt
import os
import sys
 
import runMonteCarlo
import batchMode.funcs as batchMode
import globalsFileReader.funcs as globalsFileReader
 
 
def usage():
    print("usage: %s [arguments] [options] [-h]" % sys.argv[0])
 
    # Required arguments
    required_arg_info = [
        (
            "--globals_file=", ":",
            "The path to the 'batchGlobals' file containing the "
            "information required to create the SPICE decks."
        ),
        (
            "", "",
            "\tFor examples of this file, see the 'batchGlobals.txt' file in the "
            "'examples' directory of root path %s" %
            os.path.dirname(sys.argv[0])
        )
    ]
 
    # Optional arguments
    optional_arg_info = [
        (
            "--generate_all_combinations", ":",
            "Simultaneously generates the SPICE decks "
            "with the globals.txt file for each "
            "library in the batch."
        ),
        (
            "--arc_csv_filter_file=", ":",
            "The path to the CSV file containing the "
            "properly formatted arcs the user wants to "
            "filter IN."
        ), ("", "", "\tThis filter is applied to ALL libraries in the batch."),
        ("", "", "\tArcs in this file are sensitized."),
        (
            "", "",
            "\tFor examples of this file, see the 'examples' directory in the "
            "root path %s" % os.path.dirname(sys.argv[0])
        ),
        (
            "--estimate_cpus", ":",
            "A flag that will print resource estimation for "
            "simulating the library."
        ),
        (
            "--spice_deck_format=", ":",
            "Determines the SPICE deck format that will be "
            "used. Default is [hspice]"
        ),
        (
            "", "",
            "\tThe other valid option is 'thanos' which creates FMC formatted "
            "SPICE decks."
        )
    ]
 
    # Print
    print("Arguments:")
    for opt, delm, desc in required_arg_info:
        print('\t{0:<30} {1:<5} {2:<100}'.format(opt, delm, desc))
    print("Options:")
    for opt, delm, desc in optional_arg_info:
        print('\t{0:<30} {1:<5} {2:<100}'.format(opt, delm, desc))
 
    # Functionality
    print(
        """\nFunctionality:
    - The script will generate a directory structure, in the below format, with the
    required 'globals.txt' file that can be used to generate the SPICE decks using
    the runMonteCarlo.py script in %s.
        |-- Library Type
        |   |-- LgVt
        |   |   |-- Corner
        |   |   |   | --globals.txt
 
    - If the user wants the SPICE decks to simultaneously be generated when the
    globals.txt file is generated, simply specify the 'generate_all_combinations'
    argument when calling this script.
    """ % sys.argv[0]
    )
 
    # Globals info
    print(
        """\nbatchGlobals.txt:
    - The libraries that the user wants to generate (the 'batch') is defined by the
    contents in the library, star, and exceptions files.
 
    - The libraries defined in the batch are cross-referenced with the libraries that
    exist in the 'kit_path' setting.
        NOTE: A library 'exists' in the kit_path if it contains a template.tcl,
              char.tcl, and corner.inc file
        NOTE: If a library from the batch does not exist in the kit path, then this
              script will not generate any data for that library
 
    - The 'user_model_file' of the batchGlobals.txt file specifies the library model
    file to use when generating the include file for the SPICE decks.
        NOTE: The model's library is ALWAYS pulled from the corner.inc file that
              exists in the kit path.
        NOTE: If the 'user_model_file' is a path to a directory, then the "usage" file
              is pulled from the library's corner.inc file that exists in the kit path.
        NOTE: If the 'user_model_file' is a path to a file, then this entire path is
              used in the include file.
 
    - The user must also specify a 'waveform_file' that contains the SPICE subckt
    definition for the input waveform. This waveform file is independent of library
    and is applied to ALL libraries in the batch.
 
    - The user can control various options, such as the table points to create SPICE
    decks for, the cells (and patterns) to create SPICE decks for, and the number of
    when conditions to create for an arc.
    """
    )
 
    # Usage note
    print(
        """\nUSAGE NOTE:
    - This package is a simple top-level wrapper that iteratively calls the standard
    SPICE deck generation flow for each library that the user specifies.
 
    - Therefore, after specifying the libraries for SPICE deck generation, the package
    still follows the following 3 step process:
        1) Parsing a library's template.tcl file to identify arcs in the library.
        2) Arc extraction to identify the types of arcs that can be properly
        sensitized (and should be sensitized based on the user's input).
        3) SPICE deck creation of the above arcs.
 
    - However, since the physical characteristics are dependent on each library,
    the VDD, temperature, model card, and LPE netlist path are all automatically
    extracted based on the directory structure of the kit_path.
 
    - Consequently, to minimize sources of error, this package will write out the
    globals.txt file for each library it creates irrespective of whether the user
    wants to generate the SPICE decks or not.
    """
    )
 
    # Usage
    print("\nUsage examples:")
    print("\tCall the batch flow without any arc filters.")
    print(
        "\t>>> python %s "
        "\n\t\t--globals_file '/path_to_globals_file/batchGlobals.txt'" %
        sys.argv[0]
    )
    print("\n\tCall the batch flow with an arc filter.")
    print(
        "\t>>> python %s "
        "\n\t\t--globals_file '/path_to_globals_file/batchGlobals.txt'"
        "\n\t\t--arc_csv_filter_file '/path_to_filter_file/arc_filter.csv'\n" %
        sys.argv[0]
    )
 
 
def parseInputArgs(input_args):
 
    short_opts = "h"
    long_opts = [
        "help", "globals_file=", "arc_csv_filter_file=",
        "generate_all_combinations", "spice_deck_format="
    ]
    (optlst, remainder) = getopt.gnu_getopt(input_args, short_opts, long_opts)
 
    input_options = dict()
    input_options['GENERATE_ALL_COMBINATIONS'] = 0
    input_options['ESTIMATE_CPUS'] = False
    input_options['SPICE_DECK_FORMAT'] = "HSPICE"
    if not len(input_args) - 1:
        usage()
        sys.exit(0)
    for opt, arg in optlst:
        if opt in ("-h", "--help"):
            usage()
            sys.exit(0)
        elif opt in "--globals_file":
            input_options['GLOBALS_FILE'] = arg
        elif opt in "--arc_csv_filter_file":
            input_options['ARC_CSV_FILTER_FILE'] = arg
        elif opt in "--generate_all_combinations":
            input_options['GENERATE_ALL_COMBINATIONS'] = 1
        elif opt in "--estimate_cpus":
            input_options['ESTIMATE_CPUS'] = True
        elif opt in "--spice_deck_format":
            input_options['SPICE_DECK_FORMAT'] = arg.upper()
 
    return input_options
 
 
def printUserOptions(user_options):
    print("User options were defined as follows:")
    for opt in user_options:
        print("%s :: %s" % (opt, user_options[opt]))
 
 
def createDirectoryStructure(lib_obj, root_output_path):
    # Store some more data
    output_path = os.path.join(
        root_output_path, lib_obj.lib_type, lib_obj.lgvt, lib_obj.corner
    )
    lib_obj.lib_output_path = output_path
 
    # Make the path(s)
    os.makedirs(os.path.join(output_path, "scripts"), exist_ok=True)
    lib_obj.script_output_path = os.path.join(output_path, "scripts")
 
 
def createLVFIncludeFiles(lib_obj, user_model_file):
    write_buffer = list()
    output_inc_file = os.path.join(
        lib_obj.script_output_path, "%s.inc" % lib_obj.corner
    )
    lib_obj.output_include_file = output_inc_file
    with open(lib_obj.kit_include_file, 'r') as f:
        orig_inc_lines = f.readlines()
 
    for line in orig_inc_lines:
        if fnmatch.fnmatch(line, ".lib \'*"):
            write_line = substituteLibLineWithUserModel(line, user_model_file)
            write_buffer.append(write_line)
 
        else:
            write_buffer.append(line)
 
    with open(output_inc_file, 'w') as f:
        f.write(''.join(write_buffer))
 
 
def substituteLibLineWithUserModel(lib_line, user_model_file):
    lib_line_header, orig_lib_with_delm, lib_line_model_lib = lib_line.strip(
    ).split()
    original_lib = orig_lib_with_delm.split("'")[1]
 
    # User wants to switch the path to the lib
    if os.path.isdir(user_model_file):
        usage_filename = os.path.basename(original_lib)
        new_lib_path = "'%s'" % os.path.join(user_model_file, usage_filename)
 
    # User wants to replace the lib
    else:
        new_lib_path = "'%s'" % user_model_file
 
    new_lib_line = "%s %s %s\n" % (
        lib_line_header, new_lib_path, lib_line_model_lib
    )
    return new_lib_line
 
 
def populateLibOptions(lib_obj, user_options):
    # Initialize
    lib_options = dict()
 
    # MC QC instance-specific data
    lib_root_output_path = getLibRootOutputPath(lib_obj)
    lib_options['ROOT_OUTPUT_PATH'] = lib_root_output_path
    qa_template_file = getQATemplateFile(lib_obj, lib_root_output_path)
    lib_options['QA_TEMPLATE_FILE'] = qa_template_file
 
    # Data from kit path
    lib_options['TEMPLATE_FILE'] = lib_obj.kit_template_file
    lib_options['INCLUDE_FILE'] = lib_obj.kit_include_file
 
    # Library-specific data
    lib_options['VDD_VALUE'] = lib_obj.vdd_value
    lib_options['TEMPERATURE'] = lib_obj.temper
    lib_options['ROOT_NETLIST_PATH'] = os.path.join(
        user_options['KIT_PATH'], lib_obj.lib_type, lib_obj.lgvt, "Netlist",
        lib_obj.netlist_subdir
    )
 
    # Data from input globals file
    lib_options['TEMPLATE_DECK_PATH'] = user_options['TEMPLATE_DECK_PATH']
    lib_options['WAVEFORM_FILE'] = user_options['WAVEFORM_FILE']
    lib_options['TABLE_POINTS_LIST'] = user_options['TABLE_POINTS_LIST']
    lib_options['CELL_PATTERN_LIST'] = user_options['CELL_PATTERN_LIST']
    lib_options['VALID_ARC_TYPES_LIST'] = user_options['VALID_ARC_TYPES_LIST']
    lib_options['MAX_NUM_WHEN'] = user_options['MAX_NUM_WHEN']
    lib_options['PUSHOUT_PER'] = user_options['PUSHOUT_PER']
    lib_options['PUSHOUT_DIR'] = user_options['PUSHOUT_DIR']
    lib_options['NUM_SAMPLES'] = user_options['NUM_SAMPLES']
    lib_options['ESTIMATE_CPUS'] = user_options['ESTIMATE_CPUS']
    lib_options['SPICE_DECK_FORMAT'] = user_options['SPICE_DECK_FORMAT']
    if "ARC_CSV_FILTER_FILE" in user_options:
        lib_options['ARC_CSV_FILTER_FILE'] = user_options['ARC_CSV_FILTER_FILE']
 
    return lib_options
 
 
def getQATemplateFile(lib_obj, lib_root_output_path):
    qa_template_file = os.path.join(
        os.path.dirname(lib_root_output_path), "%s_%s_%s.template.qa" %
        (lib_obj.lib_type, lib_obj.lgvt, lib_obj.corner)
    )
    return qa_template_file
 
 
def getLibRootOutputPath(lib_obj):
    count = 1
    lib_root_output_path = None
    while True:
        lib_root_output_path = os.path.join(
            lib_obj.lib_output_path, "run%s" % count, "DECKS"
        )
        if not os.path.exists(lib_root_output_path):
            break
    return lib_root_output_path
 
 
def makeGlobalsBuffer(lib_options):
    write_buffer = list()
    #var_list = ["template_deck_path", "root_output_path", "template_file",
    #            "vdd_value", "temperature", "root_netlist_path", "include_file",
    #            "waveform_file", "table_points_list", "qa_template_file",
    #            "cell_pattern_list", "valid_arc_types_list", "max_num_when",
    #            "pushput_per", "pushout_dir"]
 
    for var_name in sorted(lib_options.keys()):
        # Skip items that don't have a value, such as 'ARC_CSV_FILTER_FILE'
        if lib_options[var_name.upper()] is None:
            continue
 
        write_buffer.append(
            'set_var {0:<30} {1:<}'.format(
                var_name, lib_options[var_name.upper()]
            )
        )
        #write_buffer.append("set_var %s \t\t\t\t\t%s" % (var_name,
        #                                                 lib_options[var_name.upper()]))
 
    return write_buffer
 
 
def writeGlobalsFile(lib_obj, globals_buffer):
    globals_file = os.path.join(lib_obj.script_output_path, "globals.txt")
 
    lib_obj.globals_file = globals_file
 
    with open(globals_file, 'w') as f:
        f.write('\n'.join(globals_buffer))
 
 
def main(input_args=None):
    if input_args is None:
        input_args = sys.argv
        user_options = parseInputArgs(input_args)
        globals_file = user_options['GLOBALS_FILE']
        user_options = globalsFileReader.loadDefaultOptions(user_options)
        user_options = globalsFileReader.readGlobalsFile(
            globals_file, user_options
        )
    else:
        user_options = input_args
 
    # Get user combinations
    user_lib_combos = batchMode.getUserLibraryCombinations(
        user_options['LIB_FILE'], user_options['STAR_FILE'],
        user_options['EXCEPTIONS_FILE']
    )
 
    # Get objects
    lib_objs_list = batchMode.getLVFKitInfo(
        user_options['KIT_PATH'], user_lib_combos
    )
 
    valid_lib_obj_list = batchMode.getValidLibGenerator(lib_objs_list)
    for lib_obj in valid_lib_obj_list:
        print(
            "Creating directory structure, include file, and globals for library %s"
            % "\t{0:<10} {1:<10} {2:<50}".
            format(lib_obj.lib_type, lib_obj.lgvt, lib_obj.corner)
        )
        # Create directory structure and include file
        createDirectoryStructure(lib_obj, user_options['ROOT_OUTPUT_PATH'])
        createLVFIncludeFiles(lib_obj, user_options['USER_MODEL_FILE'])
 
        # Create the dictionary of settings
        lib_options = populateLibOptions(lib_obj, user_options)
 
        # Create the globals file
        globals_buffer = makeGlobalsBuffer(lib_options)
        writeGlobalsFile(lib_obj, globals_buffer)
 
        # Run generation
        if user_options['GENERATE_ALL_COMBINATIONS']:
            print("Generation is turned on.")
            _ = runMonteCarlo.main(lib_options)
 
    print("Finished creating globals files.")
    print(
        "Find all data in the root path %s" % user_options['ROOT_OUTPUT_PATH']
    )
 
 
if __name__ == "__main__":
    sys.exit(main())
 
