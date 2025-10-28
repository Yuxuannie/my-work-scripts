import sys
import getopt
import glob
import os
 
import modifyLPE.funcs as modifyLPE
 
 
def main(argv=None):
    # Handle inputs
    if argv is None:
        argv = sys.argv
        user_opts = parseArgv(argv)
        validateUserOpts(user_opts)
    else:
        user_opts = argv
 
    # Create output
    if not os.path.exists(user_opts['OUTPUT_PATH']):
        print("Output path %s doesn't exist. Creating it now." % user_opts[
            'OUTPUT_PATH'])
        os.makedirs(user_opts['OUTPUT_PATH'], exist_ok=True)
        print("Done.")
 
 
    print("Start modifying all LPE in %s" % user_opts['INPUT_PATH'])
    for input_lpe in glob.glob(os.path.join(user_opts['INPUT_PATH'], "*.spi")):
        output_lpe_name = "%s_qa.spi" % os.path.basename(input_lpe).split('.spi')[0]
        output_lpe = os.path.join(user_opts['OUTPUT_PATH'], output_lpe_name)
 
        print("Modifying input LPE %s" % input_lpe)
        modifyLPE.createLPEWithParams(input_lpe, output_lpe, user_opts['PARAMETER_LIST'])
        print("Wrote data to ouput LPE %s" % output_lpe)
    print("Finished modifying LPE. Find output in %s" % user_opts['OUTPUT_PATH'])
 
 
def usage():
    print("usage: %s [arguments] [options] [-h]" % sys.argv[0])
 
    # Required arguments
    required_arg_info = [
        ("--input_path=", ":", "The path containing all the input LPE netlists to be "
                               "modified."),
        ("--output_path=", ":", "The path where all the modified LPE netlists will be "
                                "stored.")
    ]
    print("Arguments:")
    for opt, delm, desc in required_arg_info:
        print('\t{0:<25} {1:<5} {2:<100}'.format(opt, delm, desc))
 
    # Optional arguments
    optional_arg_info = [
        ("--parameter list=", ":", "The list of random variable parameter names, "
                                   "separated by a whitespace, that you want to insert "
                                   "into the LPE netlist."),
        ("", "", "Default parameters are 'parl1 parl2 plo_tox plo_dxl "
                 "plo_dhfin plo_dtfin")
    ]
    print("Options:")
    for opt, delm, desc in optional_arg_info:
        print('\t{0:<25} {1:<5} {2:<100}'.format(opt, delm, desc))
 
    # Usage
    print("\nUsage examples:")
    print("\t>>> python %s "
          "\n\t\t--input_path /my/input/path"
          "\n\t\t--output_path /my/output/path"
          "\n\t\t--parameter_list 'parl1 parl2'")
 
 
def parseArgv(argv):
    short_opts = "h"
    long_opts = ["help",
                 "input_path=",
                 "output_path=",
                 "parameter_list="
                 ]
 
    optlst, remainder = getopt.gnu_getopt(argv, short_opts, long_opts)
 
    if not optlst:
        sys.exit(usage())
 
 
    user_opts = dict()
    user_opts['PARAMETER_LIST'] = ["parl1", "parl2", "plo_tox", "plo_dxl",
                                   "plo_dhfin", "plo_dtfin"]
    for opt,arg in optlst:
        if opt in ("-h", "--help"):
            sys.exit(usage())
 
        elif opt in "--input_path":
            user_opts['INPUT_PATH'] = arg
 
        elif opt in "--output_path":
            user_opts['OUTPUT_PATH'] = arg
 
        elif opt in "--parameter_list":
            user_opts['PARAMETER_LIST'] = arg.split()
 
    return user_opts
 
 
def validateUserOpts(user_opts):
    req_args = ["input_path", "output_path"]
    errors_exist = False
 
    for arg in req_args:
        if not arg.upper() in user_opts:
            errors_exist = True
            print("ERROR: The argument '--%s' is required but not set" % arg)
 
    if errors_exist:
        sys.exit("Errors exist. Review the usage and re-run.")
 
 
if __name__ == "__main__":
    sys.exit(main())
