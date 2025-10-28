__version__ = "1.1.0"
__date__ = "2016-08-23"
__author__ = "rahulk"
__maintainer__ = "rahulk"
__email__ = rahulk@tsmc.com
 
import fnmatch
import sys
import getopt
import os
import math
import subprocess
 
import utilities.fileIO as fileIO
 
class MCMT0Data(object):
 
    def __init__(self, mc_mt0_file):
        self.mc_mt0_file = mc_mt0_file
 
        # Nominals
        self.nominal_file = None
        self.nominal_value = None
 
        # Statistics
        self.mc_data = None
        self.data_values = None
        self.num_samples = None
        self.percentile = None
        self.perc_value = None
        self.stddev = None
        self.skewness = None
        self.kurtosis = None
 
        # Computations
        self.sigma_value = None
        self.runtime = None
        self.cpus = None
        self.effort = None
 
    def getDataValues(self):
        data_values = [self.mc_data[x] for x in self.mc_data]
        return data_values
 
 
    def computeSigmaValue(self, divisor):
        return (float(self.perc_value) - float(self.nominal_value)) / float(divisor)
 
 
    def computeEffort(self):
        return float(self.runtime) * float(self.cpus)
 
 
class MPP0Data(object):
 
    def __init__(self, mpp0_file):
        # Path
        self.mpp0_file = mpp0_file
 
        # Count
        self.num_samples = None
 
        # Nominal
        self.nominal_file = None
        self.nominal_value = None
 
        # CI values
        self.ci_lb = None
        self.ci_ub = None
 
        # Sample moments
        self.mean_lb = None
        self.mean_pred = None
        self.mean_ub = None
        self.median_lb = None
        self.median_pred = None
        self.median_ub = None
        self.stdDev_lb = None
        self.stdDev_pred = None
        self.stdDev_ub = None
        self.mad_lb = None
        self.mad_pred = None
        self.mad_ub = None
        self.skewness_lb = None
        self.skewness_pred = None
        self.skewness_ub = None
        self.kurtosis_lb = None
        self.kurtosis_pred = None
        self.kurtosis_ub = None
 
        # Percentile
        self.perc_lb = None
        self.perc_pred = None
        self.perc_ub = None
 
        # Computations
        self.sigma_value = None
        self.runtime = None
        self.cpus = None
        self.effort = None
 
    def computeSigmaValue(self, divisor):
        return ((float(self.perc_pred)*1e12) - float(self.nominal_value)) / \
               float(divisor)
 
    def computeEffort(self):
        return float(self.runtime) * float(self.cpus)
 
 
# Progress file functions
def getRuntimeFromProgressFile(progress_file):
    grep_cmd = ["bash", "-c", "grep 'Elapsed Time' %s" % progress_file]
    proc = subprocess.Popen(grep_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = proc.communicate()
    try:
        timestamp_info = ' '.join([x.strip() for x in stdout.decode().strip().split(
            'Time:')[1].split()])
 
        # Compute
        hrs = 0
        mins = 0
        secs = 0
        if 'hrs' in timestamp_info:
            hrs = float(timestamp_info.split(' hrs')[0])
        if 'mins' in timestamp_info:
            mins = float(timestamp_info.split(' mins')[0].split()[-1])
        if 'secs' in timestamp_info:
            secs = float(timestamp_info.split(' secs')[0].split()[-1])
 
        runtime_sec_f = float(3600*hrs + 60*mins + secs)
        runtime_hrs_f = runtime_sec_f / 3600
 
    except IndexError as _:
        runtime_sec_f = None
        runtime_hrs_f = runtime_sec_f
 
    return runtime_hrs_f
 
 
def getCPUSRequestedFromProgressFile(progress_file):
    grep_cmd = ["bash", "-c", "grep 'Number of workers requested' %s" % progress_file]
    proc = subprocess.Popen(grep_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = proc.communicate()
    try:
        num_cpus_requested_f = float(stdout.decode().strip().split()[-1])
    except IndexError as _:
        num_cpus_requested_f = None
    except ValueError as _:
        num_cpus_requested_f = None
 
    return num_cpus_requested_f
 
 
# LIS file functions
def getRuntimeFromLisFile(lis_file):
    grep_cmd = ["bash", "-c", "grep 'total elapsed time' %s" % lis_file]
    proc = subprocess.Popen(grep_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = proc.communicate()
    try:
        runtime_sec_f = float(stdout.decode().strip().split(' seconds')[0].split()[-1])
        runtime_hrs_f = runtime_sec_f / 3600
    except IndexError as _:
        runtime_sec_f = None
        runtime_hrs_f = runtime_sec_f
 
    return runtime_hrs_f
 
 
def getThreadsRequestedLisFile(lis_file):
    grep_cmd = ["bash", "-c", "grep 'Command line options' %s" % lis_file]
    proc = subprocess.Popen(grep_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = proc.communicate()
    try:
        threads_reqstd_f = float(stdout.decode().strip().split('-mt ')[1].split()[0])
    except IndexError as _:
        threads_reqstd_f = float(1)
 
    return threads_reqstd_f
 
 
# MT0 functions
def parseMCMt0File(mc_mt0_file, measurement_name, percentile):
    # Initialize object
    mt0_obj = MCMT0Data(mc_mt0_file)
    mt0_obj.percentile = percentile
 
    # Get MC Data and store
    mc_data = getMonteCarloDataFromMT0File(mc_mt0_file, measurement_name)
    mt0_obj.mc_data = mc_data
    data_values = mt0_obj.getDataValues()
    mt0_obj.data_values = data_values
    mt0_obj.num_samples = len(mt0_obj.data_values)
 
 
    # Get percentile
    percentile_value = getPercentileValueFromMeasurements(mt0_obj.data_values,
                                                          mt0_obj.percentile)
    mt0_obj.perc_value = percentile_value
 
    # Get StdDev
    stddev_value = computeStdDevFromMeasurements(mt0_obj.data_values)
    mt0_obj.stddev = stddev_value
 
    # Get skewness and kurtosis
    skewness = getSkewnessValueFromMeasurements(mt0_obj.data_values)
    kurtosis = getKurtosisValueFromMeasurements(mt0_obj.data_values)
    mt0_obj.skewness = skewness
    mt0_obj.kurtosis = kurtosis
 
    return mt0_obj
 
 
def getMeasurementColumnIndexMT0File(meas_file, meas_name):
    meas_lines = fileIO.readFile(meas_file)
 
    meas_col = None
    for line in meas_lines:
        if fnmatch.fnmatch(line, "index *"):
            meas_col = line.strip().split().index(meas_name)
            break
 
    if meas_col is None:
        errmsg = "Couldn't find the measurement column in file %s" % meas_file
        raise Exception(errmsg)
 
    return meas_col
 
 
def getNominalFromMT0File(nominal_file, param_name):
    if not os.path.exists(nominal_file):
        return None
 
    meas_col = getMeasurementColumnIndexMT0File(nominal_file, param_name)
 
    nom_lines = fileIO.readFile(nominal_file)
    nom_info = nom_lines[-1].strip().split()
    nom_value = float(nom_info[meas_col])*float(1e12)
 
    return nom_value
 
 
def getMonteCarloDataFromMT0File(mc_file, param_name):
    if not os.path.exists(mc_file):
        return None
    meas_col = getMeasurementColumnIndexMT0File(mc_file, param_name)
 
    mc_lines = fileIO.readFile(mc_file)
 
    # Parse
    existing_samples = list()
    measurement_data = dict()
    for line in mc_lines:
        line_info = line.strip().split()
        try:
            sample_number = int(line_info[0])
            if sample_number in existing_samples:
                continue
            else:
                existing_samples.append(sample_number)
                meas_value = float(line_info[meas_col])*float(1e12)
                measurement_data[sample_number] = meas_value
        except ValueError as _:
            continue
 
    return measurement_data
 
 
def getPercentileValueFromMeasurements(meas_values, percentile):
    # The data
    meas_values_f = [float(x) for x in meas_values]
    sorted_data = sorted(meas_values_f)
    N = len(sorted_data)
    percentile = float(percentile)
 
    # The function/algorithm
    n = (percentile/100) * N
    k = int(math.floor(n))
    d = n - math.floor(n)
 
    if k == 0:
        v_p = sorted_data[0]
    elif k >= N:
        v_p = sorted_data[N-1]
    else:
        # Note, Python lists begin at 0 so need to offset by 1
        v_p = sorted_data[k-1] + d*(sorted_data[k] - sorted_data[k-1])
 
    return v_p
 
 
def computeStdDevFromMeasurements(data_values):
    data_values_f = [float(x) for x in data_values]
    mean_value = computeMeanValueFromMeasurements(data_values_f)
    num_points = len(data_values_f)
    difference_list = [x - mean_value for x in data_values_f]
    sum_diff_from_mean_sqared = getSumOfListWithPow(difference_list, 2)
    stdev = pow(sum_diff_from_mean_sqared / num_points, 0.5)
    return stdev
 
 
def getSkewnessValueFromMeasurements(data_values):
    data_values_f = [float(x) for x in data_values]
    num_entries = len(data_values_f)
    mean_value = computeMeanValueFromMeasurements(data_values_f)
    difference_list = [x - mean_value for x in data_values_f]
    sum_diff_from_mean_cubed = getSumOfListWithPow(difference_list, 3)
    stdev = computeStdDevFromMeasurements(data_values_f)
 
    skewness = sum_diff_from_mean_cubed / ((num_entries+1)*pow(stdev,3))
    return skewness
 
 
def getKurtosisValueFromMeasurements(data_values):
    data_values_f = [float(x) for x in data_values]
    num_entries = len(data_values_f)
    mean_value = computeMeanValueFromMeasurements(data_values_f)
    difference_list = [x - mean_value for x in data_values_f]
    sum_diff_from_mean_pow4 = getSumOfListWithPow(difference_list, 4)
    stdev = computeStdDevFromMeasurements(data_values_f)
 
    kurtosis = sum_diff_from_mean_pow4 / ((num_entries-1)*pow(stdev,4))
    return kurtosis
 
 
def computeMeanValueFromMeasurements(data_values):
    data_values_f = [float(x) for x in data_values]
    return sum(data_values_f) / len(data_values_f)
 
 
def getSumOfListWithPow(data_values, my_pow):
    data_values_f = [float(x) for x in data_values]
    my_sum = 0
    for value in data_values_f:
        my_sum += pow(value, my_pow)
    return my_sum
 
 
# MPP0 functions
def printSimpleDataMPP0(mpp0_data, percentile_column_header):
    print_info = [
        ("Mean", "=", mpp0_data.mean_pred),
        ("Median", "=", mpp0_data.median_pred),
        ("Skewness", "=", mpp0_data.skewness_pred),
        ("Kurtosis", "=", mpp0_data.kurtosis_pred),
        ("Percentile", "=", mpp0_data.perc_pred),
        ("Percentile LB", "=", mpp0_data.perc_lb),
        ("Percentile UB", "=", mpp0_data.perc_ub),
        ("Percentile Col Header", "=", percentile_column_header)
    ]
    for var, delm, desc in print_info:
        print('{0:<25} {1:<5} {2:<100}'.format(var, delm, desc))
 
 
def parseMPP0File(mpp0_file, param_name, percentile_header="*Q99.865*"):
 
    mpp0_data = MPP0Data(mpp0_file)
    mpp0_lines = fileIO.readFile(mpp0_file)
    mpp0_data.num_samples = getNumSamplesMPP0File(mpp0_lines)
    getSampleMomentsFromMPP0File(mpp0_data, mpp0_lines, param_name)
    percentile_column_header = getPercentileFromMPP0File(mpp0_data, mpp0_lines,
                                                         param_name, percentile_header)
 
    return mpp0_data, percentile_column_header
 
 
def getNumSamplesMPP0File(mpp0_lines):
    try:
        nsample_line_idx = fileIO.findMatchesInBuffer(mpp0_lines,
                                                      "Number of Samples:*")[0]
        num_samples_line = mpp0_lines[nsample_line_idx]
        num_samples = num_samples_line.strip().split()[-1]
    except IndexError as _:
        num_samples = 0
 
    return num_samples
 
 
def getPercentileFromMPP0File(mpp0_data, mpp0_lines, param_name, percentile_header):
    # Parse the header
    percentile_idx, percentile_column_header, percentile_header_line_idx = \
        getPercentileIndicesMPP0File(mpp0_lines, percentile_header)
 
    # Get the pred value line index
    percentile_header_line = mpp0_lines[percentile_header_line_idx]
    percentile_line_idx = fileIO.findMatchesInBuffer(mpp0_lines,
                                                     "%s *" % param_name,
                                                     percentile_header_line_idx)[0]
 
    # Get the actual lines
    lb_line = mpp0_lines[percentile_line_idx-1]
    pred_line = mpp0_lines[percentile_line_idx]
    ub_line = mpp0_lines[percentile_line_idx+1]
 
    # Store
    storeLBPercentileMPP0(mpp0_data, lb_line, percentile_idx, percentile_header_line)
    storeUBPercentileMPP0(mpp0_data, ub_line, percentile_idx, percentile_header_line)
    storePredPercentileMPP0(mpp0_data, pred_line, percentile_idx, percentile_header_line)
 
    return percentile_column_header
 
 
def getSampleMomentsFromMPP0File(mpp0_data, mpp0_lines, param_name):
    # Parse the header
    idx_dict, sample_moments_line_idx = getSampleMomentsIndicesFromMPP0File(mpp0_lines)
 
    # Get the pred value line index
    param_moments_line_idx = fileIO.findMatchesInBuffer(mpp0_lines,
                                                        "%s *" % param_name,
                                                        sample_moments_line_idx)[0]
 
    # Get the actual lines
    lb_line = mpp0_lines[param_moments_line_idx-1]
    pred_val_line = mpp0_lines[param_moments_line_idx]
    ub_line = mpp0_lines[param_moments_line_idx+1]
 
    # Store
    storeLBSampleMomentsMPP0(mpp0_data, lb_line, idx_dict)
    storePredSampleMomentsMPP0(mpp0_data, pred_val_line, idx_dict)
    storeUBSampleMomentsMPP0(mpp0_data, ub_line, idx_dict)
 
 
def storePredSampleMomentsMPP0(mpp0_data, pred_line, idx_dict):
    # Extract
    pred_info = pred_line.strip().split()
    mean_pred = pred_info[idx_dict['mean_idx']]
    median_pred = pred_info[idx_dict['median_idx']]
    stdDev_pred = pred_info[idx_dict['stdDev_idx']]
    mad_pred = pred_info[idx_dict['mad_idx']]
    skewness_pred = pred_info[idx_dict['skewness_idx']]
    kurtosis_pred = pred_info[idx_dict['kurtosis_idx']]
 
    # Update
    mpp0_data.mean_pred = mean_pred
    mpp0_data.median_pred = median_pred
    mpp0_data.stdDev_pred = stdDev_pred
    mpp0_data.mad_pred = mad_pred
    mpp0_data.skewness_pred= skewness_pred
    mpp0_data.kurtosis_pred = kurtosis_pred
 
 
def storeLBSampleMomentsMPP0(mpp0_data, lb_line, idx_dict):
    # Extract
    lb_info = lb_line.strip().split()
    ci_lb = lb_info[idx_dict['ci_idx']]
    mean_lb = lb_info[idx_dict['mean_idx']]
    median_lb = lb_info[idx_dict['median_idx']]
    stdDev_lb = lb_info[idx_dict['stdDev_idx']]
    mad_lb = lb_info[idx_dict['mad_idx']]
    skewness_lb = lb_info[idx_dict['skewness_idx']]
    kurtosis_lb = lb_info[idx_dict['kurtosis_idx']]
 
    # Update
    mpp0_data.ci_lb = ci_lb
    mpp0_data.mean_lb = mean_lb
    mpp0_data.median_lb = median_lb
    mpp0_data.stdDev_lb = stdDev_lb
    mpp0_data.mad_lb = mad_lb
    mpp0_data.skewness_lb = skewness_lb
    mpp0_data.kurtosis_lb = kurtosis_lb
 
 
def storeUBSampleMomentsMPP0(mpp0_data, ub_line, idx_dict):
    # Extract
    ub_info = ub_line.strip().split()
    ci_ub = ub_info[idx_dict['ci_idx']]
    mean_ub = ub_info[idx_dict['mean_idx']]
    median_ub = ub_info[idx_dict['median_idx']]
    stdDev_ub = ub_info[idx_dict['stdDev_idx']]
    mad_ub = ub_info[idx_dict['mad_idx']]
    skewness_ub = ub_info[idx_dict['skewness_idx']]
    kurtosis_ub = ub_info[idx_dict['kurtosis_idx']]
 
    # Update
    mpp0_data.ci_ub = ci_ub
    mpp0_data.mean_ub = mean_ub
    mpp0_data.median_ub = median_ub
    mpp0_data.stdDev_ub = stdDev_ub
    mpp0_data.mad_ub = mad_ub
    mpp0_data.skewness_ub = skewness_ub
    mpp0_data.kurtosis_ub = kurtosis_ub
 
 
def storePredPercentileMPP0(mpp0_data, pred_line, percentile_idx, percentile_header_line):
    # Extract
    pred_info = pred_line.strip().split()
    if "CI" in percentile_header_line:
        perc_pred = pred_info[percentile_idx]
    else:
        perc_pred = pred_info[percentile_idx+1]
 
    # Update
    mpp0_data.perc_pred = perc_pred
 
 
def storeLBPercentileMPP0(mpp0_data, lb_line, percentile_idx, percentile_header_line):
    # Extract
    lb_info = lb_line.strip().split()
    if "CI" in percentile_header_line:
        perc_lb = lb_info[percentile_idx]
    else:
        perc_lb = lb_info[percentile_idx+1]
 
    # Update
    mpp0_data.perc_lb = perc_lb
 
 
def storeUBPercentileMPP0(mpp0_data, ub_line, percentile_idx, percentile_header_line):
    # Extract
    ub_info = ub_line.strip().split()
    if "CI" in percentile_header_line:
        perc_ub = ub_info[percentile_idx]
    else:
        perc_ub = ub_info[percentile_idx+1]
 
    # Update
    mpp0_data.perc_ub = perc_ub
 
 
def getSampleMomentsIndicesFromMPP0File(mpp0_lines):
    try:
        starting_line = fileIO.findMatchesInBuffer(
            mpp0_lines, "*CI*mean*median*stdDev*mad*skewness*kurtosis*")[0]
 
        header_info = mpp0_lines[starting_line].strip().split()
        idx_dict = dict()
        idx_dict['ci_idx'] = header_info.index("CI")
        idx_dict['mean_idx'] = header_info.index("mean")
        idx_dict['median_idx'] = header_info.index("median")
        idx_dict['stdDev_idx'] = header_info.index("stdDev")
        idx_dict['mad_idx'] = header_info.index("mad")
        idx_dict['skewness_idx'] = header_info.index("skewness")
        idx_dict['kurtosis_idx'] = header_info.index("kurtosis")
 
    except IndexError as _:
        errmsg = "Couldn't find the header for the Sample_Moments section in mpp0 " \
                 "file."
        raise IndexError(errmsg)
 
    except ValueError as _:
        errmsg = "Couldn't parse the CI header for the sample moments in mpp0 file."
        raise ValueError(errmsg)
 
    return idx_dict, starting_line
 
 
def getPercentileIndicesMPP0File(mpp0_lines, percentile_header):
    try:
        starting_line = fileIO.findMatchesInBuffer(mpp0_lines, percentile_header)[-1]
        percentile_index = None
        percentile_column_header = None
        for x in mpp0_lines[starting_line].strip().split():
            if fnmatch.fnmatch(x, percentile_header):
                percentile_index = mpp0_lines[starting_line].strip().split().index(x)
                percentile_column_header = mpp0_lines[starting_line].strip().split()[
                    percentile_index]
                break
 
    except IndexError as _:
        errmsg = "Couldn't find the percentile header for percentile %s in the mpp0 " \
                 "file" % percentile_header
        raise IndexError(errmsg)
 
    if percentile_index is None:
        errmsg = "Couldn't find the desired percentile from percentile header %s in " \
                 "the mpp0 file." % percentile_header
        raise Exception(errmsg)
 
    return percentile_index, percentile_column_header, starting_line
 
 
def usage():
    print("usage: %s [arguments] [options] [-h]" % sys.argv[0])
 
    # Required arguments
    required_arg_info = [
        ("--mpp0_file=", ":", "The path to the mpp0 file to parse."),
        ("--param_name=", ":", "The parameter name whose values should be extracted.")
    ]
 
    optional_arg_info = [
        ("--percentile_header", ":", "The header that identifies the "
                                     "mpp0 percentile to extract."),
        ("", "", "\tDefault header is 'Q99.865'")
    ]
 
    print("\nArguments")
    for opt, delm, desc in required_arg_info:
        print('\t{0:<25} {1:<5} {2:<100}'.format(opt, delm, desc))
 
    print("\nOptions:")
    for opt, delm, desc in optional_arg_info:
        print('\t{0:<25} {1:<5} {2:<100}'.format(opt, delm, desc))
 
    print("\nFunctionality:")
    print("A simple MPP0 parser which prints out the following data:"
          "\n\t Mean"
          "\n\t Median"
          "\n\t Skewness"
          "\n\t Kurtosis"
          "\n\t Percentile"
          "\n\t Percentile LB"
          "\n\t Percentile UB")
 
    print("\nNOTE:")
    print("The user should specify as many digits as possible for the percentile "
          "header."
          "\n\tInternally, the script searches for a wildcard match so specifying 'Q99' "
          "to extract 'Q99.865' may result in unwanted data.")
    print("To help debug any issues, the column header of the extracted percentile is "
          "printed.")
 
    print("\nUsage examples:")
    print("\tParse the MPP0 file searching for param name 'cp2d' and percentile 'Q99'")
    print("\t>>> python %s "
          "\n\t\t--mpp0_file '/path/to/mpp0/file.mpp0'"
          "\n\t\t--param_name 'cp2d'"
          "\n\t\t--percentile_header 'Q99'\n")
 
 
def parseInputArgs(argv):
    shortopts = "h"
    longopts = ["help",
                "mpp0_file=",
                "param_name=",
                "percentile_header="]
 
    optlst, remainder = getopt.gnu_getopt(argv, shortopts, longopts)
 
    if not optlst:
        usage()
        sys.exit(0)
 
    user_options = dict()
    user_options['mpp0_file'] = None
    user_options['param_name'] = None
    user_options['percentile_header'] = "*Q99.865*"
 
    for opt, arg in optlst:
        if opt in ("-h", "--help"):
            sys.exit(usage())
 
        elif opt in "--mpp0_file":
            user_options['mpp0_file'] = arg
 
        elif opt in "--param_name":
            user_options['param_name'] = arg
 
        elif opt in "--percentile_header":
            user_options['percentile_header'] = "*%s*" % arg
 
    return user_options
 
 
def validateUserOptions(user_options):
    errors_exist = 0
    for arg in user_options:
        if user_options[arg] is None:
            print("ERROR: The argument --%s is missing" % arg)
            errors_exist = 1
    if errors_exist:
        sys.exit(print("Errors exist. Review and re-run."))
 
 
def main():
    argv = sys.argv
    user_options = parseInputArgs(argv)
    validateUserOptions(user_options)
    mpp0_data, percentile_column_header = parseMPP0File(user_options['mpp0_file'],
                                                        user_options['param_name'],
                                                        user_options['percentile_header'])
    printSimpleDataMPP0(mpp0_data, percentile_column_header)
 
 
if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as err:
        print("ERROR: %s" % err)
 
