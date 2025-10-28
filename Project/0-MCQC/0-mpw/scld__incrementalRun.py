import sys
import getopt
 
import incremental.funcs as isdg
 
 
def main(user_opts=None):
    # Handle inputs
    if user_opts is None:
        argv = sys.argv
        user_opts = parseArgv(argv)
 
    # Check options
    checkValidOpts(user_opts)
 
    # Run Incremental SPICE Deck Generation (ISDG)
    isdg.main(user_opts['SIM_PATH'], user_opts['NSAMPLES'])
 
 
def checkValidOpts(user_opts):
    errors_exist = False
    req_opts = ["SIM_PATH", "NSAMPLES"]
    for opt in req_opts:
        if user_opts[opt] is None:
            print("ERROR: The option %s is required but missing." % opt.lower())
            errors_exist = True
 
    if errors_exist:
        sys.exit("Errors exist. Review them and re-run.")
 
 
def parseArgv(argv):
    short_opts = "h"
    long_opts = ["help", "sim_path=", "nsamples="]
    (optlst, remainder) = getopt.gnu_getopt(argv, short_opts, long_opts)
 
    user_opts = dict()
    user_opts['SIM_PATH'] = None
    user_opts['NSAMPLES'] = None
    if not len(argv) - 1:
        sys.exit(usage())
    for opt, arg in optlst:
        if opt in ("-h", "--help"):
            sys.exit(usage())
 
        elif opt in "--sim_path":
            user_opts['SIM_PATH'] = arg
 
        elif opt in "--nsamples":
            user_opts['NSAMPLES'] = int(arg)
 
    return user_opts
 
 
def usage():
    print("usage: %s [arguments] [options] [-h]" % sys.argv[0])
 
    # Required arguments
    required_arg_info = [
        (
            "--sim_path", ":",
            "The path to the simulation directory containing the "
            "partial data."
        ),
        (
            "--nsamples", ":",
            "The total number of samples that is supposed to be "
            "simulated."
        )
    ]
    print("Arguments:")
    for opt, delm, desc in required_arg_info:
        print('\t{0:<25} {1:<5} {2:<100}'.format(opt, delm, desc))
 
    # Usage
    print("\nUsage examples:")
    print(
        "\tCall the incremental SPICE deck generation flow on a path for a total of "
        "5k samples."
    )
    print(
        "\t>>> python %s "
        "\n\t\t--sim_path '/tmp1/rahulk/DECKS/partial_run'"
        "\n\t\t--nsamples '5000'" % sys.argv[0]
    )
 
 
if __name__ == "__main__":
    sys.exit(main())
 
