import shutil
import os
import glob
import fnmatch
 
import utilities.fileIO as ioutils
 
 
def main(sim_path, nsamples):
    print("Starting incremental deck generation.")
    # Extract the data
    print("BEGIN PHASE 1.")
    print("Collecting mt0 files.")
    worker_mt0_files = collectExistingWorkerMt0(sim_path)
    print("Extracting simulated samples.")
    simulated_sample_indices = getSimulatedSampleIndices(worker_mt0_files)
    print("Identifying missing samples.")
    missing_sample_indices = getMissingSampleIndices(nsamples, simulated_sample_indices)
    print("Checking if all simulated samples are done.")
    if not len(missing_sample_indices):
        print("All %s samples were simulated!" % nsamples)
        print("Creating sim.cfg for hspice datamining.")
        sim_cfg = createCFGForHSDatamining(sim_path, worker_mt0_files)
        print("Finished writing sim.cfg %s" % sim_cfg)
 
    else:
        print("%s samples still need to be simulated." % len(missing_sample_indices))
        # Move all other files to a backup path in this dir
        print("BEGIN PHASE 2.")
        print("Creating backup folder.")
        backup_folder_name = getBackupFolderName(sim_path)
        backup_folder = makeBackupFolder(sim_path, backup_folder_name)
        print("Backup folder created at %s" % backup_folder)
        print("Moving contents to backup folder.")
        moveDataToBackup(sim_path, backup_folder)
 
        # Copy the mc_sim.sp to the backup folder
        print("Copying original mc_sim.sp to backup folder")
        shutil.copyfile(os.path.join(sim_path, "mc_sim.sp"), os.path.join(backup_folder,
                                                                          "mc_sim.sp"))
 
        # Create the incremental SPICE deck
        print("BEGIN PHASE 3.")
        print("Generating incremental deck buffer.")
        inc_buff = getIncrementalMCDeckBuffer(sim_path, missing_sample_indices, nsamples)
        incremental_mc_deck = os.path.join(sim_path, "incremental_mc_sim.sp")
        print("Writing incremental deck to %s" % incremental_mc_deck)
        ioutils.writeBufferToFile(inc_buff, incremental_mc_deck)
        print("Wrote buffer to %s" % incremental_mc_deck)
 
        # Create the sim.cfg file
        print("Creating sim.cfg for hspice datamining.")
        # Re-collect the mt0 files in case they were moved
        recol_worker_mt0_files = collectExistingWorkerMt0(sim_path)
        recol_worker_mt0_files.append(os.path.join(sim_path, "incremental_mc_sim.mt0"))
        sim_cfg = createCFGForHSDatamining(sim_path, recol_worker_mt0_files)
        print("Finished writing sim.cfg %s" % sim_cfg)
 
    print("Finished incremental deck generation.")
 
 
# New deck functions
def getIncrementalMCDeckBuffer(sim_path, missing_sample_indices, nsamples):
    """
    A function that will copy the original mc_sim.sp file and modify it to only
    simulate the missing samples.
    """
 
    # Read MC contents
    mc_buffer = ioutils.readFile(os.path.join(sim_path, "mc_sim.sp"))
 
    # Get sampling method
    sampling_method = getMCSamplingMethod(mc_buffer)
 
    # Create buffer
    output_buffer = list()
    for line in mc_buffer:
        if fnmatch.fnmatch(line, "* monte*=*"):
            lhs_line = line.split('monte=')[0]
            if sampling_method.lower() == "lhs":
                rhs_line = "monte=list(%s) lhs_sample_size=%s\n" % \
                           (','.join([str(x) for x in missing_sample_indices]), nsamples)
            else:
                rhs_line = "monte=list(%s)\n" % (','.join([str(x) for x in
                                                           missing_sample_indices]))
            wline = "%s %s" % (lhs_line, rhs_line)
            output_buffer.append(wline)
        else:
            output_buffer.append(line)
 
    return output_buffer
 
 
def getMCSamplingMethod(mc_buffer):
    sampling_method = None
    for line in mc_buffer:
        if " sampling_method=" in line:
            sampling_method = line.split("sampling_method=")[1].strip().split()[0]
            break
 
    return sampling_method
 
# sim.cfg functions for hspice datamining
def createCFGForHSDatamining(sim_path, mt0_list):
    wline = ".measfile -merge %s\n" % ', '.join(mt0_list)
    sim_cfg_file = os.path.join(sim_path, "sim.cfg")
    with open(sim_cfg_file, 'w') as f:
        f.write(wline)
    return sim_cfg_file
 
 
# Backup functions
def getBackupFolderName(sim_path):
    """
    A function that will return the name of the backup where all the data will go
    """
    existing_dirs = glob.glob(os.path.join(sim_path, "sim__run__*"))
    if not len(existing_dirs):
        backup_folder_name = "sim__run__0"
    else:
        existing_sim_run_cnts = [int(os.path.basename(x).split('__run__')[1]) for x in
                                 existing_dirs]
        backup_folder_name = "sim__run__%s" % (max(existing_sim_run_cnts) + 1)
 
    return backup_folder_name
 
 
def makeBackupFolder(sim_path, backup_folder_name):
    # Don't allow existence in case the path exists but we didn't detect it somewhere
    backup_folder = os.path.join(sim_path, backup_folder_name)
    os.makedirs(backup_folder)
 
    return backup_folder
 
 
def moveDataToBackup(sim_path, backup_folder):
    backup_blacklist = getBackupBlacklist()
    for content in os.listdir(sim_path):
        blacklisted = checkItemIsBlacklisted(content, backup_blacklist)
        if blacklisted:
            print("Skipping item %s because it is in the backup blacklist." % content)
        else:
            print("Backing up item %s to %s" % (content, backup_folder))
            content_src = os.path.join(sim_path, content)
            content_dst = os.path.join(backup_folder, content)
            shutil.move(content_src, content_dst)
 
 
def checkItemIsBlacklisted(content, backup_blacklist):
    blacklisted = False
    for item in backup_blacklist:
        if fnmatch.fnmatch(content, item):
            blacklisted = True
 
    return blacklisted
 
 
def getBackupBlacklist():
    """
    A function that returns the names of items that are on the backup blacklist
    """
 
    # Don't blacklist any "incremental_run.sp" files since we want them to get moved
    backup_blacklist = [ "mc_sim.sp",
                         "sim__run__*",
                         "nominal_sim*"]
 
    return backup_blacklist
 
 
# Missing samples functions
def collectExistingWorkerMt0(sim_path):
    """
    A function that will collect all of the mt0 files for each "worker*" directory in
    the simulation path
    """
 
    # mt0 files can be foudn in one of the following formats:
    # ./mc_sim_dp/worker*/*.mt0
    # ./incremental_sim_dp/worker*/*.mt0
    # ./mc_sim.mt0
    # ./incremental_sim.mt0
    # ./sim__run__*/mc_sim_dp/worker/*.mt0
    # ./sim__run__*/incremental_sim_dp/worker*/*.mt0
    # ./sim__run__*/mc_sim.mt0
    # ./sim__run__*/incremental_sim.mt0
    #
    # Abstract to collect these types of files:
    # ./*_dp/*/*.mt0
    # ./*.mt0
    # ./sim__run__*/*_dp/*/*.mt0
    # ./sim__run__*/*.mt0
 
    worker_mt0_files = list()
 
    # ./*_dp/*/*.mt0
    _ = [worker_mt0_files.append(x) for x in glob.glob(os.path.join(sim_path, "*_dp",
                                                                    "*", "*.mt0"))]
 
    # ./*.mt0
    _ = [worker_mt0_files.append(x) for x in glob.glob(os.path.join(sim_path, "*.mt0"))]
 
    # ./sim__run__*/*_dp/*/*.mt0
    _ = [worker_mt0_files.append(x) for x in glob.glob(os.path.join(sim_path,
                                                                    "sim__run__*",
                                                                    "*_dp", "*",
                                                                    "*.mt0"))]
 
    # ./sim__run__*/*.mt0
    _ = [worker_mt0_files.append(x) for x in glob.glob(os.path.join(sim_path,
                                                                    "sim__run__*",
                                                                    "*.mt0"))]
 
    # Clean up any files we don't need
    worker_mt0_files = cleanupWorkerMt0FileList(worker_mt0_files)
 
    return worker_mt0_files
 
 
def cleanupWorkerMt0FileList(worker_mt0_files):
    """
    A function that removes items matching the patterns in the "remove list"
    This is used primarily to remove any "nominal_sim.mt0" items
    """
 
    remove_pattern_list = ["*nominal_sim.mt0"]
    new_worker_mt0_files = list()
 
    for item in worker_mt0_files:
        for remove_pattern in remove_pattern_list:
            # If not in the remove list, re-store it
            if not fnmatch.fnmatch(item, remove_pattern):
                new_worker_mt0_files.append(item)
 
    return new_worker_mt0_files
 
 
def getSimulatedSampleIndices(worker_mt0_files):
    """
    A function that will crawl through the existing mt0 files to get the list of
    samples that have already been simulated.
    """
 
    simulated_sample_indices = list()
    for worker_mt0 in worker_mt0_files:
        # Read the file
        mt0_lines = ioutils.readFile(worker_mt0)
 
        # Get the parameter line
        mt0_parameter_line, line_idx = getMt0ParameterLine(mt0_lines)
 
        # Get the index column
        index_col = getIndexColumnFromMt0ParamLine(mt0_parameter_line)
 
        # Get the indices of simulated samples
        _ = [simulated_sample_indices.append(int(x.strip().split()[index_col])) for x
             in mt0_lines[(line_idx+1):]]
 
    return simulated_sample_indices
 
 
def getMissingSampleIndices(sample_num, existing_sample_indices):
    """
    A function that gets the list of sample indices that are missing.
    """
 
    all_indices = set(range(1,sample_num+1))
    missing_indices = list(all_indices - set(existing_sample_indices))
 
    return missing_indices
 
 
def getMt0ParameterLine(mt0_lines):
    """
    A function to extract the mt0 lines with the parameter headers
    """
 
    mt0_param_line = None
    count = None
    for count in range(0, len(mt0_lines)):
        line = mt0_lines[count]
        if fnmatch.fnmatch(line, "index * temper*alter*"):
            mt0_param_line = line
            break
 
    return mt0_param_line, count
 
 
def getIndexColumnFromMt0ParamLine(mt0_parameter_line):
    index_col = mt0_parameter_line.strip().split().index("index")
    return index_col
 
 
 
 
 
 
 
 
 
 
