import getopt
import os
import glob
import sys
 
import utilities.hspiceUtilities as hspiceUtilities
 
 
def main(input_args=None):
    if input_args is None:
        input_args = sys.argv
        user_options = loadDefaultOptions()
        user_options = parseInputArgs(input_args, user_options)
    else:
        user_options = input_args
 
    # Loop
    for deck_path in glob.glob(
        os.path.join(user_options['ROOT_DIRECTORY'], "DECKS/*")
    ):
        print("Analyzing %s" % deck_path)
 
        # Check nominal
        nominal_file = os.path.join(
            deck_path, user_options['NOMINAL_MT0_FILENAME']
        )
        print("Parsing nominal file at %s" % nominal_file)
        nominal_file_exists = checkNominalFileExists(nominal_file)
        if not nominal_file_exists:
            print("Nominal file doesn't exist.")
            print("Skipping this path.")
            continue
        else:
            try:
                nominal_value = hspiceUtilities.getNominalFromMT0File(
                    nominal_file, user_options['MEASUREMENT_NAME']
                )
            except Exception as err:
                print("ERROR: %s" % err)
                print("Skipping this path.")
                continue
 
        # Check MC
        if user_options['FORMAT'] == "mpp0":
            mpp0_file = os.path.join(
                deck_path, user_options['MC_MPP0_FILENAME']
            )
            print("Parsing mpp0 file at %s" % mpp0_file)
            mpp0_exists = checkMPP0FileExists(mpp0_file)
            if not mpp0_exists:
                print("mpp0 file doesn't exist.")
                print("Skipping this path.")
                continue
 
            # Get timing data
            try:
                mpp0_obj, _ = hspiceUtilities.parseMPP0File(
                    mpp0_file, user_options['MEASUREMENT_NAME'],
                    "*Q%s*" % user_options['PERCENTILE']
                )
            except Exception as err:
                print("ERROR: %s" % err)
                print("Skipping this path.")
                continue
            mpp0_obj.nominal_value = nominal_value
            mpp0_obj.nominal_file = nominal_file
            mpp0_obj.sigma_value = mpp0_obj.computeSigmaValue(3)
 
            # Get the runtime data
            if user_options['GET_RUNTIME']:
                progress_file = os.path.join(
                    deck_path, user_options['PROGRESS_FILENAME']
                )
                runtime = hspiceUtilities.getRuntimeFromProgressFile(
                    progress_file
                )
                cpus = hspiceUtilities.getCPUSRequestedFromProgressFile(
                    progress_file
                )
                if (runtime is None) or (cpus is None):
                    mpp0_obj.runtime = 1e+39
                    mpp0_obj.cpus = 1
                else:
                    mpp0_obj.runtime = runtime
                    mpp0_obj.cpus = cpus
 
                mpp0_obj.effort = mpp0_obj.computeEffort()
 
        elif user_options['FORMAT'] == "mt0":
            mc_mt0_file = os.path.join(
                deck_path, user_options['MC_MT0_FILENAME']
            )
            print("Parsing mt0 file at %s" % mc_mt0_file)
            mc_mt0_exists = checkMCMt0FileExists(mc_mt0_file)
            if not mc_mt0_exists:
                print("mt0 file doesn't exist.")
                print("Skipping this path.")
                continue
 
            # Get the timing data
            try:
                mt0_obj = hspiceUtilities.parseMCMt0File(
                    mc_mt0_file, user_options['MEASUREMENT_NAME'],
                    user_options['PERCENTILE']
                )
            except Exception as err:
                print("ERROR: %s" % err)
                print("Skipping this path.")
                continue
            mt0_obj.nominal_value = nominal_value
            mt0_obj.nominal_file = nominal_file
            mt0_obj.sigma_value = mt0_obj.computeSigmaValue(3)
 
            # Get the runtime data
            if user_options['GET_RUNTIME']:
                lis_file = os.path.join(deck_path, user_options['LIS_FILENAME'])
                runtime = hspiceUtilities.getRuntimeFromLisFile(lis_file)
                cpus = hspiceUtilities.getThreadsRequestedLisFile(lis_file)
                if (runtime is None) or (cpus is None):
                    mt0_obj.runtime = 1e+39
                    mt0_obj.cpus = 1
                else:
                    mt0_obj.runtime = runtime
                    mt0_obj.cpus = cpus
 
                mt0_obj.effort = mt0_obj.computeEffort()
        else:
            print(
                "Unknown MC format '%s' specified by user. " %
                user_options['FORMAT']
            )
            print("Skipping this path")
            continue
 
        # Write statistics file
        output_file = os.path.join(deck_path, user_options['OUTPUT_FILENAME'])
        if user_options['FORMAT'] == "mpp0":
            sigma = mpp0_obj.sigma_value
            num_samples = mpp0_obj.num_samples
            nominal = mpp0_obj.nominal_value
            percentile = float(mpp0_obj.perc_pred) * 1e12
            percentile_ub = float(mpp0_obj.perc_ub) * 1e12
            percentile_lb = float(mpp0_obj.perc_lb) * 1e12
            stdev = float(mpp0_obj.stdDev_pred) * 1e12
            skewness = mpp0_obj.skewness_pred
            kurtosis = mpp0_obj.kurtosis_pred
            effort = mpp0_obj.effort
        elif user_options['FORMAT'] == "mt0":
            sigma = mt0_obj.sigma_value
            num_samples = mt0_obj.num_samples
            nominal = mt0_obj.nominal_value
            percentile = mt0_obj.perc_value
            percentile_ub = None
            percentile_lb = None
            stdev = mt0_obj.stddev
            skewness = mt0_obj.skewness
            kurtosis = mt0_obj.kurtosis
            effort = mt0_obj.effort
        else:
            print(
                "Unknown MC format '%s' specified by user. " %
                user_options['FORMAT']
            )
            print("Skipping this path")
            continue
 
        writeStatisticsFile(
            output_file, sigma, num_samples, nominal, percentile, percentile_ub,
            percentile_lb, stdev, skewness, kurtosis, effort
        )
 
 
def writeStatisticsFile(
    output_file, sigma_value, num_samples, nominal, percentile, percentile_ub,
    percentile_lb, stdev, skewness, kurtosis, effort
):
    if effort is None:
        effort = "1e+39"
 
    if (percentile_ub is None) or (percentile_lb is None):
        header = "Sigma,Samples,Nominal,Percentile,StDev,Skewness,Kurtosis," \
                 "Effort [CPU-h]\n"
        line = "%s,%s,%s,%s,%s,%s,%s,%s\n" % (
            sigma_value, num_samples, nominal, percentile, stdev, skewness,
            kurtosis, effort
        )
    else:
        header = "Sigma,Samples,Nominal,Percentile,Percentile LB,Percentile UB," \
                 "StDev,Skewness,Kurtosis,Effort [CPU-h]\n"
        line = "%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n" % (
            sigma_value, num_samples, nominal, percentile, percentile_lb,
            percentile_ub, stdev, skewness, kurtosis, effort
        )
 
    with open(output_file, 'w') as f:
        f.write(header)
        f.write(line)
 
 
def checkNominalFileExists(nominal_file):
    if not os.path.exists(nominal_file):
        print("Nominal file doesn't exist.")
        return False
    else:
        return True
 
 
def checkMPP0FileExists(mpp0_file):
    if not os.path.exists(mpp0_file):
        print("MPP0 file doesn't exist.")
        return False
    else:
        return True
 
 
def checkMCMt0FileExists(mc_mt0_file):
    if not os.path.exists(mc_mt0_file):
        print("MC mt0 file doesn't exist.")
        return False
    else:
        return True
 
 
def usage():
    print("usage: %s [arguments] [options] [-h]" % sys.argv[0])
 
    # Required arguments
    required_arg_info = [
        (
            "--root_directory=", ":",
            "The path to the QC directory, NOT including the "
            "'DECKS' subdirectory"
        ),
    ]
    print("Arguments:")
    for opt, delm, desc in required_arg_info:
        print('\t{0:<25} {1:<5} {2:<100}'.format(opt, delm, desc))
 
    # Optional arguments
    optional_arg_info = [
        (
            "--format=", ":",
            "[mt0 | mpp0] This option controls how the statistical data "
            "is calculated. If set to 'mt0', it is based off the "
            "mc_sim.mt0 file. If set to 'mpp0' it is based off the "
            "'mc_sim.mpp0' file."
        ), ("", "", "\tThe default format is 'mpp0'"),
        (
            "--runtime_off", ":",
            "This flag will turn off runtime/effort computation for "
            "a completed simulation."
        ), ("", "", "\tThe default method is to compute runtimes.")
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
    #      sys.argv[0])
 
 
def parseInputArgs(input_args, user_options=None):
    if user_options is None:
        user_options = dict()
 
    short_opts = "h"
    long_opts = ["help", "root_directory=", "format=", "runtime_off"]
 
    optlst, remainder = getopt.gnu_getopt(input_args, short_opts, long_opts)
 
    if not optlst:
        usage()
        sys.exit(0)
 
    for opt, arg in optlst:
        if opt in ("-h", "--help"):
            usage()
            sys.exit(0)
 
        elif opt in "--root_directory":
            user_options['ROOT_DIRECTORY'] = arg
 
        elif opt in "--format":
            user_options['FORMAT'] = arg.lower()
 
        elif opt in "--runtime_off":
            user_options['GET_RUNTIME'] = False
 
    return user_options
 
 
def loadDefaultOptions(user_options=None):
    if user_options is None:
        user_options = dict()
 
    user_options['FORMAT'] = "mpp0"
    user_options['OUTPUT_FILENAME'] = "statistics.csv"
    user_options['MEASUREMENT_NAME'] = "cp2d"
    user_options['PERCENTILE'] = "99.865"
    user_options['PROGRESS_FILENAME'] = "mc_sim_dp.progress"
    user_options['LIS_FILENAME'] = "mc_sim.lis"
    user_options['NOMINAL_MT0_FILENAME'] = "nominal_sim.mt0"
    user_options['MC_MT0_FILENAME'] = "mc_sim.mt0"
    user_options['MC_MPP0_FILENAME'] = "mc_sim.mpp0"
    user_options['GET_RUNTIME'] = True
 
    return user_options
 
 
if __name__ == "__main__":
    sys.exit(main())
 
