import sys
import os
import glob
import getopt
 
import utilities.fileIO as fileIO
from runMonteCarlo import printUserOptions
 
 
def usage():
    print("usage: %s [arguments] [options] [-h]" % sys.argv[0])
 
    # Required arguments
    required_arg_info = [
        (
            "--qa_directory=", ":",
            "The path to the MC QC directory, NOT including the "
            "'DECKS' subdirectory in the path."
        )
    ]
    print("Arguments:")
    for opt, delm, desc in required_arg_info:
        print('\t{0:<25} {1:<5} {2:<100}'.format(opt, delm, desc))
 
    # Optional arguments
    optional_arg_info = [
        (
            "--output_file=", ":",
            "If this option is specified, a verbose output of the "
            "paths that are DONE and INCOMPLETE will be written to "
            "this file."
        ),
        ("", "", "\tThe default behavior is to suppress writing out any data.")
    ]
    print("Options:")
    for opt, delm, desc in optional_arg_info:
        print('\t{0:<25} {1:<5} {2:<100}'.format(opt, delm, desc))
 
    # Functionality
    print(
        """\nFunctionality:
    Intentionally left blank.
    Will update later.
    """
    )
 
    # Special note
    print(
        """\nUSAGE NOTE:
    Intentionally left blank.
    Will update later.
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
 
 
def loadDefaultArgs(user_options=None):
    if user_options is None:
        user_options = dict()
 
    user_options['MPP0_FILENAME'] = "mc_sim.mpp0"
    user_options['OUTPUT_FILE'] = None
 
    return user_options
 
 
def parseInputArgs(input_args, user_options=None):
    if user_options is None:
        user_options = dict()
 
    short_opts = "h"
    long_opts = ["help", "qa_directory=", "output_file="]
 
    optlst, remainder = getopt.gnu_getopt(input_args, short_opts, long_opts)
 
    if optlst is None:
        usage()
        sys.exit(0)
 
    for opt, arg in optlst:
        if opt in ("-h", "--help"):
            usage()
            sys.exit(0)
 
        elif opt in "--qa_directory":
            user_options['QA_DIRECTORY'] = arg
 
        elif opt in "--output_file":
            user_options['OUTPUT_FILE'] = arg
 
    return user_options
 
 
def queryStatus(qa_directory, mpp0_filename):
    # Init
    count_done = 0
    count_incomplete = 0
    count_total = 0
    write_buffer = list()
 
    # Assume path has a /DECKS subdirectory
    for deck_path in glob.glob(os.path.join(qa_directory, "DECKS", "*")):
        count_total += 1
        mpp0_file = os.path.join(deck_path, mpp0_filename)
        if not os.path.exists(mpp0_file):
            count_incomplete += 1
            status = "INCOMPLETE"
        else:
            count_done += 1
            status = "DONE"
        line = "%s,%s" % (deck_path, status)
        write_buffer.append(line)
 
    return write_buffer, count_done, count_incomplete, count_total
 
 
def printStatus(ndone, nincomplete, ntotal):
    info_list = [
        ("DONE", "::", "%s" % ndone), ("INCOMPLETE", "::", "%s" % nincomplete),
        ("TOTAL", "::", "%s" % ntotal)
    ]
    for opt, delm, desc in info_list:
        print('\t{0:<30} {1:<5} {2:<100}'.format(opt, delm, desc))
 
 
def main(input_args=None):
    if input_args is None:
        input_args = sys.argv
        user_options = loadDefaultArgs()
        user_options = parseInputArgs(input_args, user_options)
    else:
        user_options = input_args
 
    # Print options
    printUserOptions(user_options)
 
    # Get status
    print("Querying status.")
    write_buffer, ndone, nincomplete, ntotal = \
        queryStatus(user_options['QA_DIRECTORY'], user_options['MPP0_FILENAME'])
 
    # Print status
    print("STATUS:")
    printStatus(ndone, nincomplete, ntotal)
 
    # Write file
    if user_options['OUTPUT_FILE'] is not None:
        fileIO.writeBufferToFile(
            write_buffer, user_options['OUTPUT_FILE'], delimeter='\n'
        )
 
 
if __name__ == "__main__":
    sys.exit(main())
 
