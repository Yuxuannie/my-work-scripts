import sys
import os
import getopt
import glob
import fnmatch
 
import libraryParser.funcs as library_parser
import utilities.fileIO as fileIO
from runMonteCarlo import printUserOptions
from timingArcInfo.funcs import convertLitWhenToLogWhen
 
 
class MCData(object):
    def __init__(
        self, stat_file, arc_type, cell, pin, pin_dir, rel_pin, rel_pin_dir,
        literal_when, logical_when, table_point, arc_id
    ):
        # Path info
        self.stat_file = stat_file
        self.arc_type = arc_type
        self.cell = cell
        self.pin = pin
        self.pin_dir = pin_dir
        self.rel_pin = rel_pin
        self.rel_pin_dir = rel_pin_dir
        self.literal_when = literal_when
        self.logical_when = logical_when
        self.table_point = table_point
        self.arc_id = arc_id
 
        # Char data
        self.variety_sigma = None
 
        # MC Data
        self.num_samples = None
        self.mc_sigma = None
        self.mc_nominal = None
        self.mc_percentile = None
        self.mc_percentile_lb = None
        self.mc_percentile_ub = None
        self.mc_skewness = None
        self.mc_kurtosis = None
        self.mc_stdev = None
        self.mc_effort = None
 
        # Errors
        self.abs_error = None
        self.rel_error = None
 
    def computeAbsError(self):
        return float(self.variety_sigma) - float(self.mc_sigma)
 
    def computeRelError(self):
        return float(self.abs_error) / float(self.mc_sigma)
 
 
def usage():
    print("usage: %s [arguments] [options] [-h]" % sys.argv[0])
 
    # Required arguments
    required_arg_info = [
        (
            "--qa_directory=", ":",
            "The path to the QA directory, including the '/DECKS' "
            "subdirectory."
        ),
        (
            "--sensitivity_file=", ":",
            "The full path to the characterization sensitivity "
            "file"
        ),
        (
            "--output_file=", ":",
            "The path to the output file where the spreadsheet is "
            "written"
        ),
    ]
    print("Arguments:")
    for opt, delm, desc in required_arg_info:
        print('\t{0:<25} {1:<5} {2:<100}'.format(opt, delm, desc))
 
    # Optional arguments
    optional_arg_info = [
        (
            "--bundle_mode", ":",
            "A flag that will allow the script to handle bundled "
            "sensitivity files."
        ),
        ("", "", "\tThis flag is required for libraries like MB, MBRFF, etc.")
    ]
    print("Options:")
    for opt, delm, desc in optional_arg_info:
        print('\t{0:<25} {1:<5} {2:<100}'.format(opt, delm, desc))
 
    # Functionality
    print(
        """\nFunctionality:
    Intentionally left blank.
    Will fill in at a later time.
    """
    )
 
    # Special note
    print(
        """\nUSAGE NOTE:
    Intentionally left blank.
    Will fill in at a later time.
    """
    )
 
    # Usage
    #print("\nUsage examples:")
    #print("\tCall the SPICE deck generation flow without any arc filters.")
    #print("\t>>> python %s "
    #      "\n\t\t--globals_file '/path_to_globals_file/globals.txt'" % sys.argv[0])
    #print("\n\tCall the SPICE deck generation flow with an arc filter.")
    #print("\t>>> python %s "
    #      "\n\t\t--globals_file '/path_to_globals_file/globals.txt'"
    #      "\n\t\t--arc_csv_filter_file '/path_to_filter_file/arc_filter.csv'\n" %
    #      sys.argv[0])
 
 
def loadDefaultOptions(user_options=None):
    if user_options is None:
        user_options = dict()
 
    user_options['BUNDLE_MODE'] = False
 
    return user_options
 
 
def parseInputArgs(input_args, user_options=None):
    if user_options is None:
        user_options = dict()
 
    short_opts = "h"
    long_opts = [
        "help", "qa_directory=", "sensitivity_file=", "output_file=",
        "bundle_mode"
    ]
 
    optlst, remainder = getopt.gnu_getopt(input_args, short_opts, long_opts)
 
    if not len(optlst):
        usage()
        sys.exit(0)
 
    for opt, arg in optlst:
        if opt in ("-h", "--help"):
            usage()
            sys.exit(0)
 
        elif opt in "--qa_directory":
            user_options['QA_DIRECTORY'] = arg
 
        elif opt in "--sensitivity_file":
            user_options['SENSITIVITY_FILE'] = arg
 
        elif opt in "--output_file":
            user_options['OUTPUT_FILE'] = arg
 
        elif opt in "--bundle_mode":
            user_options['BUNDLE_MODE'] = True
 
    return user_options
 
 
def createMCDataObj(stat_file, arc_id):
    deck_subdir_name = os.path.basename(os.path.dirname(stat_file))
    subdir_info = deck_subdir_name.split('_')
    arc_type_raw = subdir_info[0]
    cell = subdir_info[1]
    pin = subdir_info[2]
    pin_dir = subdir_info[3]
    rel_pin = subdir_info[4]
    rel_pin_dir = subdir_info[5]
    literal_when = '_'.join(subdir_info[6:-1])
    logical_when = convertLitWhenToLogWhen(literal_when)
    table_point = subdir_info[-1]
    arc_type = formFullArcType(arc_type_raw, rel_pin_dir)
 
    mc_obj = MCData(
        stat_file, arc_type, cell, pin, pin_dir, rel_pin, rel_pin_dir,
        literal_when, logical_when, table_point, arc_id
    )
 
    return mc_obj
 
 
def formFullArcType(arc_type_raw, rel_pin_dir):
    arc_type = None
    if rel_pin_dir == "fall":
        arc_type = "%s_falling" % arc_type_raw
    elif rel_pin_dir == "rise":
        arc_type = "%s_rising" % arc_type_raw
    return arc_type
 
 
def createAllMCDataObjects(qa_directory):
    mc_objs_list = list()
    arc_id = 0
    for deck_path in sorted(glob.glob(os.path.join(qa_directory, "*"))):
        arc_id += 1
        stat_file = os.path.join(deck_path, "statistics.csv")
        if not os.path.exists(stat_file):
            continue
        mc_obj = createMCDataObj(stat_file, arc_id)
        mc_objs_list.append(mc_obj)
    return mc_objs_list
 
 
def populateAllMCData(mc_objs_list):
    for mc_obj in mc_objs_list:
        # Parse file
        sigma, samples, nominal, percentile, stdev, skewness, kurtosis, effort, \
        percentile_ub, percentile_lb = parseStatisticsFile(mc_obj.stat_file)
 
        # Populate
        mc_obj.num_samples = samples
        mc_obj.mc_sigma = sigma
        mc_obj.mc_nominal = nominal
        mc_obj.mc_percentile = percentile
        mc_obj.mc_percentile_lb = percentile_lb
        mc_obj.mc_percentile_ub = percentile_ub
        mc_obj.mc_stdev = stdev
        mc_obj.mc_skewness = skewness
        mc_obj.mc_kurtosis = kurtosis
        mc_obj.effort = effort
 
 
def parseStatisticsFile(stat_file):
    stat_lines = fileIO.readFile(stat_file)
    header_info = stat_lines[0].strip().split(',')
    stat_info = stat_lines[1].strip().split(',')
    sigma = stat_info[header_info.index("Sigma")]
    samples = stat_info[header_info.index("Samples")]
    nominal = stat_info[header_info.index("Nominal")]
    percentile = stat_info[header_info.index("Percentile")]
    stdev = stat_info[header_info.index("StDev")]
    skewness = stat_info[header_info.index("Skewness")]
    kurtosis = stat_info[header_info.index("Kurtosis")]
    effort = stat_info[header_info.index("Effort [CPU-h]")]
 
    try:
        percentile_ub = stat_info[header_info.index("Percentile UB")]
        percentile_lb = stat_info[header_info.index("Percentile LB")]
    except ValueError as _:
        percentile_ub = None
        percentile_lb = None
 
    return sigma, samples, nominal, percentile, stdev, skewness, kurtosis, \
           effort, percentile_ub, percentile_lb
 
 
def storeAllVarietyDataInMCObjs(mc_objs_list, lib_data, bundle_mode):
    flat_lib_data = library_parser.flattenLibData(lib_data)
    for cell, pin, rel_pin, t_type, when, t_sense, table_name, sigma in flat_lib_data:
        matching_obj_list = findMatchingMCObjs(
            cell, pin, rel_pin, t_type, when, table_name, sigma, mc_objs_list,
            bundle_mode
        )
        if matching_obj_list is None:
            continue
 
        for mc_obj in matching_obj_list:
            vec_point = convertTablePointToVectorPoint(mc_obj.table_point)
            variety_sigma = float(
                lib_data[cell][pin][rel_pin][t_type][when][t_sense][table_name]
                [sigma][vec_point]
            ) * 1e3
 
            mc_obj.variety_sigma = variety_sigma
 
 
def convertTablePointToVectorPoint(table_point):
    row, col = table_point.split('-')
    return (int(row) - 1) * 5 + int(col) - 1
 
 
def findMatchingMCObjs(
    cell, pin, rel_pin, timing_type, when, table_name, sigma, mc_objs_list,
    bundle_mode
):
 
    matching_mc_obj_list = list()
    if not sigma in ["early", "late", "none"]:
        return matching_mc_obj_list
 
    if bundle_mode:
        bundle_pin = adjustPinForBundle(pin)
    else:
        bundle_pin = None
 
    pin_dir = getPinDirFromFlatLibData(table_name)
    rel_pin_dir = getRelPinDirFromFlatLibData(timing_type)
 
    for mc_obj in mc_objs_list:
        if (mc_obj.cell == cell) and \
                (mc_obj.pin_dir == pin_dir) and \
                (mc_obj.rel_pin == rel_pin) and \
                (mc_obj.rel_pin_dir == rel_pin_dir) and \
                (mc_obj.arc_type == timing_type) and \
                (mc_obj.logical_when == when):
 
            # Bundle mode check for MB
            if bundle_mode and fnmatch.fnmatch(mc_obj.pin, bundle_pin):
                matching_mc_obj_list.append(mc_obj)
 
            # Non-MB
            elif (not bundle_mode) and (mc_obj.pin == pin):
                matching_mc_obj_list.append(mc_obj)
 
    return matching_mc_obj_list
 
 
def adjustPinForBundle(pin):
    if "D" in pin:
        bundle_pin = "D*"
    else:
        bundle_pin = None
    return bundle_pin
 
 
def getRelPinDirFromFlatLibData(timing_type):
    rel_pin_dir = None
    if "rising" in timing_type.lower():
        rel_pin_dir = "rise"
    elif "falling" in timing_type.lower():
        rel_pin_dir = "fall"
    return rel_pin_dir
 
 
def getPinDirFromFlatLibData(table_name):
    pin_dir = None
    if "rise" in table_name.lower():
        pin_dir = "rise"
    elif "fall" in table_name.lower():
        pin_dir = "fall"
    return pin_dir
 
 
def computeAllErrorsInMCObjs(mc_objs_list):
    for mc_obj in mc_objs_list:
        try:
            mc_obj.abs_error = mc_obj.computeAbsError()
            mc_obj.rel_error = mc_obj.computeRelError()
        except TypeError as _:
            print(
                "ERROR: Couldn't compute the errors for path %s" %
                mc_obj.stat_file
            )
            if mc_obj.variety_sigma is None:
                print(
                    "This table point seems to be missing from the sensitivity file."
                )
            elif mc_obj.mc_sigma is None:
                print("Couldn't store a sigma for the MC simulation.")
            else:
                print("Unsure of root cause; needs investigation.")
 
 
def getOutputFileWriteBuffer(mc_objs_list):
    write_buffer = list()
    header = getOutputFileHeader(mc_objs_list[0])
    write_buffer.append(header)
 
    for mc_obj in mc_objs_list:
        # Use ';' delimeter so excel doesn't convert to date
        row, col = mc_obj.table_point.split('-')
 
        try:
            write_line = ','.join(
                ["%s" for _ in range(len(header.split(',')))]
            ) % (
                mc_obj.abs_error, float(mc_obj.rel_error) * 100,
                "arc_{0}".format(mc_obj.arc_id), mc_obj.cell, mc_obj.arc_type,
                mc_obj.pin, mc_obj.pin_dir, mc_obj.rel_pin, mc_obj.rel_pin_dir,
                mc_obj.logical_when, "%s;%s" %
                (row, col), mc_obj.num_samples, mc_obj.variety_sigma,
                mc_obj.mc_sigma, mc_obj.mc_nominal, mc_obj.mc_percentile,
                mc_obj.mc_skewness, mc_obj.mc_kurtosis, mc_obj.effort
            )
            write_buffer.append(write_line)
        except TypeError as _:
            write_line = ','.join(
                ["%s" for _ in range(len(header.split(',')))]
            ) % (
                mc_obj.abs_error, float(mc_obj.rel_error) * 100,
                "arc_{0}".format(mc_obj.arc_id), mc_obj.cell, mc_obj.arc_type,
                mc_obj.pin, mc_obj.pin_dir, mc_obj.rel_pin, mc_obj.rel_pin_dir,
                mc_obj.logical_when, "%s;%s" %
                (row, col), mc_obj.num_samples, mc_obj.variety_sigma,
                mc_obj.mc_sigma, mc_obj.mc_nominal, mc_obj.mc_percentile,
                mc_obj.mc_percentile_lb, mc_obj.mc_percentile_ub,
                mc_obj.mc_skewness, mc_obj.mc_kurtosis, mc_obj.effort
            )
            write_buffer.append(write_line)
        except Exception as _:
            continue
 
    return write_buffer
 
 
def getOutputFileHeader(mc_obj):
    if mc_obj.mc_percentile_ub is None:
        header = "Abs. Error [ps],Rel. Error [%],Arc ID,Cell,Arc Type,Pin,Pin Dir,Rel Pin," \
                 "Rel Pin Dir,When,Point,Samples,Variety Sigma,MC Sigma,MC Nominal, MC " \
                 "Percentile,MC Skewness,MC Kurtosis,Effort [CPU-h]"
    else:
        header = "Abs. Error [ps],Rel. Error [%],Arc ID,Cell,Arc Type,Pin,Pin Dir,Rel Pin," \
                 "Rel Pin Dir,When,Point,Samples,Variety Sigma,MC Sigma,MC Nominal, MC " \
                 "Percentile,MC Percentile LB,MC Percentile UB,MC Skewness,MC Kurtosis," \
                 "Effort [CPU-h]"
    return header
 
 
def main(input_args=None):
    if input_args is None:
        input_args = sys.argv
        user_options = loadDefaultOptions()
        user_options = parseInputArgs(input_args, user_options)
    else:
        user_options = input_args
 
    # Print
    printUserOptions(user_options)
 
    # Parse library file
    print("Parsing library file.")
    lib_data = library_parser.parseLibraryFile(
        user_options['SENSITIVITY_FILE'], "variation"
    )
 
    # Create the MC Data objects
    print("Creating MC timing objects.")
    mc_objs_list = createAllMCDataObjects(user_options['QA_DIRECTORY'])
 
    # Store the actual MC data from them
    print("Populating MC Data.")
    populateAllMCData(mc_objs_list)
 
    # Store the variety sigma
    print("Storing Variety data.")
    storeAllVarietyDataInMCObjs(
        mc_objs_list, lib_data, user_options['BUNDLE_MODE']
    )
 
    # Compute errors
    print("Computing Errors.")
    computeAllErrorsInMCObjs(mc_objs_list)
 
    # Get write buffer
    print("Generating output buffer.")
    write_buffer = getOutputFileWriteBuffer(mc_objs_list)
 
    # Write the write buffer
    print("Writing output file.")
    fileIO.writeBufferToFile(
        write_buffer, user_options['OUTPUT_FILE'], delimeter='\n'
    )
 
 
if __name__ == "__main__":
    sys.exit(main())
 
