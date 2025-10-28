import sys
import os
 
sys.path.insert(0, os.path.split(__file__)[0])  # noqa
import glob
import time
import getopt
import fnmatch
import shutil
import hybrid_char_helper
import globalsFileReader.funcs as globalsFileReader
from pathlib import Path
from batchMode.funcs import pygrep
 
 
def usage():
    print("usage: %s [arguments] [options] [-h]" % sys.argv[0])
 
    # Required arguments
    required_arg_info = [
        (
            "--globals_file=", ":",
            "The path to the 'globals' file containing the "
            "information required to create the SPICE decks."
        ),
        (
            "", "",
            "\tFor examples of this file, see the 'mcqc_globals.txt' file in the "
            "'examples' directory of root path %s" %
            os.path.dirname(sys.argv[0])
        ),
        ("--lib_type", ":", "The library type of the library to analyze."),
        ("--lg=", ":", "The Lg of the library to analyze."),
        ("--vt=", ":", "The Vt of the library to analyze."),
        ("--corner=", ":", "The PVT corner of the library to analyze."),
        (
            "--output_path=", ":",
            "The root output path where the MC QC is generated."
        ),
    ]
 
    # Optional arguments
    optional_arg_info = [
        ("--estimate_cpus", ":", "A flag that will print resource estimation."),
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
    the scld__mcqc.py script in %s.
        ROOT
        |-- DECKS
        |   |-- SUBDIR_1
        |   |   |-- nominal_sim.sp
        |   |   |-- mc_sim.sp
        |   |-- SUBDIR_2
        |   |   |-- nominal_sim.sp
        |   |   |-- mc_sim.sp
        |   |   ..
        |   |-- SUBDIR_N
        |   |   |-- nominal_sim.sp
        |   |   |-- mc_sim.sp
    """ % sys.argv[0]
    )
 
    # Globals info
    print(
        """\mcqc_globals.txt:
    - The 'kit_path' setting defines the path to the directory structure containing
    the LVF library kits, e.g. in this format
        ROOT
        |-- Library Type
        |   |-- LgVt
        |   |   |-- Char
        |   |   |   |-- char_1.tcl
        |   |   |   |-- char_2.tcl
        |   |   |   ..
        |   |   |   |-- char_N.tcl
        |   |   |-- Template
        |   |   |   |-- template_1.tcl
        |   |   |   |-- template_2.tcl
        |   |   |   ..
        |   |   |   |-- template_N.tcl
        |   |   |-- Netlist
        |   |   |   |-- LPE_cworst_T_m25c
        |   |   |   |-- LPE_cworst_T_125c
        |   |   |   ..
 
    - The 'kit_path' is required to extract the library information (VDD, temperature,
    etc.) and timing arcs (from template.tcl) to generate correct SPICE decks.
 
    - The 'user_model_file' of the mcqc_globals.txt file specifies the library model
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
    - This package is a simple top-level wrapper that calls the standard SPICE deck
    generation flow for each library that the user specifies.
 
    - Therefore, after specifying the libraries for SPICE deck generation, the package
    still follows the following 3 step process:
        1) Parsing a library's template.tcl file to identify arcs in the library.
        2) Arc extraction to identify the types of arcs that can be properly
        sensitized (and should be sensitized based on the user's input).
        3) SPICE deck creation of the above arcs.
 
    - However, since the physical characteristics are dependent on each library,
    the VDD, temperature, model card, and LPE netlist path are all automatically
    extracted based on the directory structure of the kit_path.
    """
    )
 
    # Usage
    print("\nUsage examples:")
    print("\tCall the mcqc flow.")
    print(
        "\t>>> python %s "
        "\n\t\t--globals_file '/path_to_globals_file/batchGlobals.txt'"
        "\n\t\t--lib_type 'base'"
        "\n\t\t--lg '8'"
        "\n\t\t--vt 'svt'"
        "\n\t\t--corner 'ssgnp_0p500v_m25c_cworst_T'"
        "\n\t\t--output_path '$PWD/demo'" % sys.argv[0]
    )
    print("\n\tCall the mcqc flow and estimate resources.")
    print(
        "\t>>> python %s "
        "\n\t\t--globals_file '/path_to_globals_file/batchGlobals.txt'"
        "\n\t\t--lib_type 'base'"
        "\n\t\t--lg '8'"
        "\n\t\t--vt 'svt'"
        "\n\t\t--corner 'ssgnp_0p500v_m25c_cworst_T'"
        "\n\t\t--output_path '$PWD/demo'"
        "\n\t\t--estimate_cpus" % sys.argv[0]
    )
 
 
def parseInputArgs(input_args, input_options=None):
 
    short_opts = "h"
    long_opts = [
        "help",
        "lib_type=",
        "lg=",
        "vt=",
        "corner=",
        "output_path=",
        "globals_file=",
        "arc_csv_filter_file=",
        "spice_deck_format="
        "estimate_cpus",
        "char_type=",
    ]
 
    optlst, remainder = getopt.gnu_getopt(input_args, short_opts, long_opts)
 
    if input_options is None:
        input_options = dict()
 
    if not len(input_args) - 1:
        usage()
        sys.exit(0)
 
    input_options['ESTIMATE_CPUS'] = False
    input_options['HOLD_TAX'] = False
    input_options['SPICE_DECK_FORMAT'] = "HSPICE"
    for opt, arg in optlst:
        if opt in ("-h", "--help"):
            usage()
            sys.exit(0)
 
        elif opt in "--lib_type":
            input_options['lib_type'] = arg
 
        elif opt in "--lg":
            input_options['lg'] = arg
 
        elif opt in "--vt":
            input_options['vt'] = arg
 
        elif opt in "--corner":
            input_options['corner'] = arg
 
        elif opt in "--output_path":
            input_options['output_path'] = arg
 
        elif opt in "--globals_file":
            input_options['globals_file'] = arg
 
        elif opt in "--arc_csv_filter_file":
            input_options['ARC_CSV_FILTER_FILE'] = arg
 
        elif opt in "--estimate_cpus":
            input_options['ESTIMATE_CPUS'] = 1
 
        elif opt in "--spice_deck_format":
            input_options['SPICE_DECK_FORMAT'] = arg.upper()
        elif opt in "--char_type":
            valid_char_types = ['cons', 'cons_mixvt',
                                'non_cons', 'non_cons_mixvt']
            assert arg in valid_char_types
            input_options['CHAR_TYPE'] = arg
        elif opt in "--hold_tax":
            input_options['HOLD_TAX'] = True
 
    return input_options
 
 
def getLibTemplateFile(user_options):
    kit_path = user_options['KIT_PATH']
    lib_type = user_options['lib_type']
    lgvt = user_options['lgvt']
    if user_options['HOLD_TAX']:
        template_path = Path(kit_path) / lib_type / \
            lgvt / 'HOLD_TAX' / 'Template'
    else:
        template_path = Path(kit_path) / lib_type / lgvt / 'Template'
    try:
        template_path = str(template_path)
        pat = os.path.join(template_path,
                           "*%s*.template.tcl" % user_options['corner'])
        template_files = glob.glob(pat)
        n = len(template_files)
        if n != 1:
            raise ValueError(
                'Found Incorrecnt Number of Template Files (%d): %s' % (n, pat))
        template_file = template_files[0]
    except IndexError as _:
        print(
            "Couldn't find the char template.tcl file for library %s %s %s" % (
                user_options['lib_type'], user_options['lgvt'],
                user_options['corner']
            )
        )
        print("This is a fatal error. Exiting now.")
        sys.exit(-1)
 
    return template_file
 
 
def getCharType(user_options):
    char_type = user_options.get('CHAR_TYPE', '')
    if char_type:
        wildcard = ".%s" % char_type
    else:
        wildcard = char_type
    return wildcard
 
 
def getLibCharFile(user_options):
    char_type = getCharType(user_options)
    kit_path = user_options['KIT_PATH']
    lib_type = user_options['lib_type']
    lgvt = user_options['lgvt']
    if user_options['HOLD_TAX']:
        char_path = Path(kit_path) / lib_type / lgvt / 'HOLD_TAX' / 'Char'
    else:
        char_path = Path(kit_path) / lib_type / lgvt / 'Char'
    try:
        char_path = str(char_path)
        pat = os.path.join(char_path,
                           "char_%s%s.tcl" % (user_options['corner'], char_type))
        char_files = glob.glob(pat)
        n = len(char_files)
        if n != 1:
            raise ValueError(
                'Found Incorrecnt Number of Chartcl Files (%d): %s' % (n, pat))
        char_file = char_files[0]
    except IndexError as _:
        print("Couldn't find the lib char.tcl file for library %s %s %s %s" % (
            user_options['lib_type'], user_options['lgvt'], user_options['corner'], pat))
        print("This is a fatal error. Exiting now.")
        sys.exit(-1)
 
    return char_file
 
 
def getLibIncFile(user_options):
    char_file = user_options['CHARTCL_FILE']
    inc_file_lookup = hybrid_char_helper.parse_chartcl_for_inc(char_file)
    return inc_file_lookup
 
 
def extractVDDValue(char_file):
    stdout, stderr = pygrep(char_file, "set VOLT")
    vdd_value = stdout.decode().strip().split()[-1]
    return vdd_value
 
 
def extractTemperatureValue(char_file):
    stdout, stderr = pygrep(char_file, "set TEMP")
    temperature_value = stdout.decode().strip().split()[-1]
    return temperature_value
 
 
def extractNetlistPath(user_options, char_file):
    with open(char_file) as f:
        r_char_file = f.readlines()[::-1]
    for line in r_char_file:
        if 'Netlist' in line and 'spi' in line:
            netlist_subdir = os.path.dirname(line.strip().split('Netlist/')[1])
            break
    netlist_path = os.path.join(user_options['KIT_PATH'],
                                user_options['lib_type'],
                                user_options['lgvt'],
                                "Netlist",
                                netlist_subdir)
    return netlist_path
 
 
def formRootOutputPath(user_options):
    root_output_path = os.path.join(user_options['output_path'], "DECKS")
    return root_output_path
 
 
def formQATemplateFile(user_options):
    qa_template_file = os.path.join(
        user_options['output_path'], "%s_%s_%s.template.qa" % (
            user_options['lib_type'], user_options['lgvt'],
            user_options['corner']
        )
    )
    return qa_template_file
 
 
def copyLVFIncludeFile(user_options, inc_file_lookup):
    output_path = os.path.abspath(user_options['output_path'])
    for arc_type, inc_file in inc_file_lookup.items():
        name = Path(inc_file).name
        dst = Path(output_path) / name
        dst = str(dst)
        try:
            os.remove(dst)
        except FileNotFoundError:
            pass
        dst_parent = Path(dst).parent
        dst_parent = str(dst_parent)
        os.makedirs(dst_parent, exist_ok=True)
 
    time.sleep(3)
 
    for arc_type, inc_file in inc_file_lookup.items():
        name = Path(inc_file).name
        dst = Path(output_path) / name
        dst = str(dst)
        shutil.copy2(inc_file, dst)
        inc_file_lookup[arc_type] = dst
    return inc_file_lookup
 
 
def createLVFIncludeFile(user_options, lib_inc_file):
    write_buffer = list()
    output_inc_file = os.path.join(
        user_options['output_path'], "%s.inc" % user_options['corner']
    )
    with open(lib_inc_file, 'r') as f:
        orig_inc_lines = f.readlines()
 
    for line in orig_inc_lines:
        if fnmatch.fnmatch(line, ".lib \'*"):
            write_line = substituteLibLineWithUserModel(
                line, user_options['USER_MODEL_FILE']
            )
            write_buffer.append(write_line)
 
        else:
            write_buffer.append(line)
 
    with open(output_inc_file, 'w') as f:
        f.write('\n'.join(write_buffer))
    return output_inc_file
 
 
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
 
 
def fixCustomModulePaths(user_options):
    """
    A function that adds the 'TEMPLATE_LUT_PATH' variable to the sys.path information
    so that the LUT can be imported without error.
    This is also the function where future, path-dependent modules can be imported.
    """
 
    # path inserts
    try:
        sys.path.insert(0, user_options['TEMPLATE_LUT_PATH'])
    except KeyError as mke:
        sys.exit(
            "The %s variable was not set; cannot import module." % str(mke)
        )
 
 
def main():
    print("Parsing inputs.")
    input_args = sys.argv
    user_options = parseInputArgs(input_args)
    user_options['lgvt'] = user_options['lg'] + user_options['vt']
    print("Reading globals file.")
    user_options = globalsFileReader.loadDefaultOptions(user_options)
    user_options = globalsFileReader.readGlobalsFile(
        user_options['globals_file'], user_options
    )
 
    # Fix sys.path to fix LUT importing
    fixCustomModulePaths(user_options)
    # Import
    import runMonteCarlo
 
    # Extract data from the input
    print("Extracting file data from kit path.")
    template_file = getLibTemplateFile(user_options)
    char_file = getLibCharFile(user_options)
 
    # Parse
    print("Extracting MC QC data from library files.")
    user_options['CHARTCL_FILE'] = char_file
    user_options['TEMPLATE_FILE'] = template_file
    vdd_value = extractVDDValue(char_file)
    user_options['VDD_VALUE'] = vdd_value
    temperature = extractTemperatureValue(char_file)
    user_options['TEMPERATURE'] = temperature
    netlist_path = extractNetlistPath(user_options, char_file)
    user_options['ROOT_NETLIST_PATH'] = netlist_path
 
    # Form some variables/files
    root_output_path = formRootOutputPath(user_options)
    user_options['ROOT_OUTPUT_PATH'] = root_output_path
    qa_template_file = formQATemplateFile(user_options)
    user_options['QA_TEMPLATE_FILE'] = qa_template_file
 
    inc_file_lookup = getLibIncFile(user_options)
    inc_file_lookup = copyLVFIncludeFile(user_options, inc_file_lookup)
    user_options['INCLUDE_FILE_LOOKUP'] = inc_file_lookup
 
    # Only generate files if estimation mode is turned OFF
    if not user_options['ESTIMATE_CPUS']:
        # Create the output path
        print("Creating output directory.")
        os.makedirs(user_options['ROOT_OUTPUT_PATH'], exist_ok=True)
 
        # Make the Include file
        # print("Generating include file.")
        # mcqc_inc_file = createLVFIncludeFile(user_options, inc_file)
        # user_options['INCLUDE_FILE'] = mcqc_inc_file
 
    # Run generation (may or may not generate depending on ESTIMATE_CPUS flag
    print("Running SPICE deck generation.")
    spice_info = runMonteCarlo.main(user_options)
 
    print("Skip CPU Estimate")
    # if not user_options['ESTIMATE_CPUS']:
    # Get CPU estimate for launch purposes
    #_, _, min_effort = runMonteCarlo.getCPUEstimate(spice_info)
    # Create the launch script
    #print("Skip creating launch script.")
    # launch_script = launchScript.createLaunchScript(user_options['ROOT_OUTPUT_PATH'],
    #                                                 user_options['LSF_CFG_FILE'],
    #                                                 min_effort)
 
    # print("Find launch script at %s" % launch_script)
 
 
if __name__ == "__main__":
    sys.exit(main())
 
