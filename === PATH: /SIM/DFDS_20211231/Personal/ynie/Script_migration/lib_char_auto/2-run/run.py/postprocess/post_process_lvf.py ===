mport os
import shutil
import subprocess
import logging
import argparse
import re
import functools
import time
 
 
# Utility functions
def error_handler(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logging.error("Error in %s: %s", func.__name__, str(e))
            return None
 
    return wrapper
 
 
def setup_logging(log_file='post_process_lvf.log'):
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        filename=log_file,
        filemode='w'
    )
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)
 
 
@error_handler
def extract_pvt_info(corner):
    process_match = re.match(r"^([^\W_]+)_", corner)
    voltage_match = re.search(r"_(\d+p\d+v)_", corner)
    temp_match = re.search(r"_([m]?\d+c)(_|\b)", corner)
 
    process = process_match.group(1) if process_match else None
    voltage = voltage_match.group(1).replace('p', '.').replace('v', '') if voltage_match else None
    temperature = temp_match.group(1).replace('m', '-').replace('c', '') if temp_match else None
 
    process_corner_mapping = {
        "ssgnp": "SSGNPGlobalCorner_LocalMC_MOS_MOSCAP",
        "sf": "SFGlobalCorner_LocalMC_MOS_MOSCAP",
        "fs": "FSGNPGlobalCorner_LocalMC_MOS_MOSCAP",
        "tt": "TTGlobalCorner_LocalMC_MOS_MOSCAP",
        "ffgnp": "FFGNPGlobalCorner_LocalMC_MOS_MOSCAP"
    }
 
    process_corner = process_corner_mapping.get(process, None)
    return process, voltage, temperature, process_corner
 
 
@error_handler
def find_and_replace_in_file(search_dir, search_pattern, target_file, line_pattern, target_pattern):
    try:
        found_file = None
        for filename in os.listdir(search_dir):
            if re.match(search_pattern, filename):
                found_file = filename
                break
 
        if not found_file:
            logging.error("No file matching %s found in %s", search_pattern, search_dir)
            return False, None
 
        full_path = os.path.join(search_dir, found_file)
 
        with open(target_file, 'r') as f:
            lines = f.readlines()
 
        modified = False
        for i, line in enumerate(lines):
            if re.search(line_pattern, line):
                lines[i] = target_pattern.format(full_path) + '\n'
                modified = True
                break
 
        if not modified:
            logging.error("No line matching %s found in %s", line_pattern, target_file)
            return False, None
 
        with open(target_file, 'w') as f:
            f.writelines(lines)
 
        logging.info("Successfully updated %s with %s", target_file, found_file)
        return True, full_path
 
    except Exception as e:
        logging.error("Error in find_and_replace_in_file: %s", str(e))
        return False, None
 
 
@error_handler
def retry_copy_files(lib_paths, input_source_dir):
    missing_files = []
    for key, file_path in lib_paths.items():
        if os.path.isfile(file_path):
            target_file = os.path.join(input_source_dir, os.path.basename(file_path))
            try:
                shutil.copy(file_path, target_file)
                logging.info(f"Copied {file_path} to {target_file}")
            except Exception as e:
                logging.error(f"Failed to copy {file_path} to {target_file}: {str(e)}")
                logging.info(f"Retrying to copy {file_path} to {target_file}")
                try:
                    shutil.copy(file_path, target_file)
                    logging.info(f"Successfully copied {file_path} to {target_file} on retry")
                except Exception as retry_e:
                    logging.error(f"Retry failed to copy {file_path} to {target_file}: {str(retry_e)}")
                    missing_files.append(file_path)
        else:
            logging.error(f"Lib file does not exist: {file_path}")
            missing_files.append(file_path)
    return missing_files
 
 
@error_handler
def process_release_folder_lvf(lvf_release_dir, corner, input_source_dir):
    logging.info("Processing Release Folder for LVF Post Processing")
    missing_files = []
 
    lib_paths = {}
    script_prefix = 'lvf'
    scripts = [script for script in os.listdir(lvf_release_dir)
               if script.startswith(script_prefix) and script.endswith('.sh')
               and ''.join(corner) in script]
 
    for script in scripts:
        script_name = script.replace(f'{script_prefix}_', '').replace('.sh', '')
        tcl_file = os.path.join(lvf_release_dir, f"{script_prefix}_{script_name}.tcl")
        lvf_char_dir = os.path.join(os.path.dirname(lvf_release_dir), 'Char')
 
        if not os.path.isfile(tcl_file):
            logging.error(f"Missing TCL file: {tcl_file}")
            missing_files.append(tcl_file)
            continue
 
        with open(tcl_file, 'r') as f:
            lines = f.readlines()
 
        ldb_type = None
        for line in lines:
            if 'read_ldb' in line:
                if 'non_cons.ldb.gz' in line:
                    ldb_type = 'non_cons'
                elif 'cons.ldb.gz' in line:
                    ldb_type = 'cons'
                else:
                    ldb_type = ''
                break
 
        if ldb_type is None:
            logging.error(f"No 'read_ldb' line found in {tcl_file}")
            continue
 
        search_pattern = f"tcb.*\\.{ldb_type}\\.ldb\\.gz$" if ldb_type else ".*\\.ldb\\.gz$"
        success, full_ldb_path = find_and_replace_in_file(
            search_dir=lvf_char_dir,
            search_pattern=search_pattern,
            target_file=tcl_file,
            line_pattern=r"read_ldb",
            target_pattern="read_ldb {}"
        )
 
        if not success:
            logging.warning(f"Failed to update TCL file for {script_name}, skipping this corner")
            missing_files.append(f"{lvf_char_dir}/{search_pattern}")
            continue
 
        # Create a log file for the bsub command
        bsub_log_file = os.path.join(lvf_release_dir, f"{script}.bsub.log")
 
        try:
            with open(bsub_log_file, 'w') as log_file:
                subprocess.run(
                    ['bsub ' + script],
                    shell=True,
                    check=True,
                    cwd=lvf_release_dir,
                    stdout=log_file,
                    stderr=subprocess.STDOUT
                )
        except subprocess.CalledProcessError as e:
            logging.error(f"Error running script {script}: {str(e)}")
            logging.error(f"Check the log file for details: {bsub_log_file}")
            continue
 
    logging.info(f"Searching for .lib files in corner folders under {lvf_release_dir} for corner {corner}")
 
    # Polling for .lib files
#    max_wait_time = 600  # max wait time in seconds (10 minutes)
#    poll_interval = 30  # poll every 30 seconds
#    elapsed_time = 0
#
#    while elapsed_time < max_wait_time:
#        lib_files_found = False
#        lib_files = []
#       
#        for root, dirs, files in os.walk(lvf_release_dir):
#            for dir_name in dirs:
#                if dir_name.startswith(corner):
#                    dir_path = os.path.join(root, dir_name)
#                    logging.info(f"Processing directory: {dir_path}")
#                    for f in os.listdir(dir_path):
#                        if f.endswith('.lib'):
#                            lib_file = os.path.join(dir_path, f)
#                            corner_name = os.path.basename(dir_path)
#                            lib_paths[corner_name] = lib_file
#                            lib_files.append(lib_file)
#                            logging.info(f"Found .lib file: {lib_file}")
#                            lib_files_found = True
#
#        if lib_files_found and len(lib_files) == len(scripts):
#            break
#
#        logging.info(f"Waiting for .lib files to be generated... ({elapsed_time}/{max_wait_time} seconds elapsed)")
#        time.sleep(poll_interval)
#        elapsed_time += poll_interval
#
#    if not lib_paths:
#        logging.error("No .lib files found after waiting for the maximum time.")
#        missing_files.append(f"No .lib files for corner {corner}")
 
    os.makedirs(input_source_dir, exist_ok=True)
 
    missing_files.extend(retry_copy_files(lib_paths, input_source_dir))
 
    return lib_paths, full_ldb_path, missing_files
 
 
@error_handler
def post_process_lvf(work_dir, dirs, pvt_corners):
    total_missing_files = []
 
    for dir_index, dir_name in enumerate(dirs, 1):
        logging.info("=" * 50)
        logging.info("Processing directory %d/%d: %s", dir_index, len(dirs), dir_name)
        logging.info("=" * 50)
 
        for pvt_corner in pvt_corners:
            logging.info("-" * 50)
            logging.info("Processing PVT corner: %s", pvt_corner)
            logging.info("-" * 50)
           
            process, voltage, temperature, process_corner = extract_pvt_info(pvt_corner)
 
            lvf_char_dir = os.path.join(work_dir, dir_name, 'LVF', 'Char')
            lvf_release_dir = os.path.join(work_dir, dir_name, 'LVF', 'Release')
            postprocess_dir = os.path.join(work_dir, dir_name, 'Postprocess')
 
            corner_dir = os.path.join(postprocess_dir, pvt_corner)
            input_source_dir = os.path.join(corner_dir, "input_source")
 
            # Check the state of the folders and .lib files
            corner_folder_exists = False
            lib_file_exists = False
            input_source_lib_count = 0
            sh_file_count = 0
 
            for root, dirs, files in os.walk(lvf_release_dir):
                for dir_name in dirs:
                    if ''.join(pvt_corner) in dir_name:
                        corner_folder_exists = True
                        dir_path = os.path.join(root, dir_name)
                        for f in os.listdir(dir_path):
                            if f.endswith('.lib'):
                                lib_file_exists = True
                                break
 
            if os.path.exists(input_source_dir):
                input_source_lib_count = len([f for f in os.listdir(input_source_dir) if f.endswith('.lib')])
 
            sh_file_count = len([f for f in os.listdir(lvf_release_dir) if f.endswith('.sh')])
 
            # If the input_source already has the required .lib files, skip processing
            if corner_folder_exists and lib_file_exists and input_source_lib_count == sh_file_count:
                logging.info("Skipping processing for %s as input_source already has required lib files.", pvt_corner)
                continue
 
            # If .lib files exist in the release folder but not all are in input_source, retry copying them
            elif corner_folder_exists and lib_file_exists and input_source_lib_count != sh_file_count:
                logging.info("Copy failed for %s. .lib files exist in release folder but not all in input_source. Retrying copy...", pvt_corner)
                # Clean the input_source folder
                if os.path.exists(input_source_dir):
                    shutil.rmtree(input_source_dir)
                os.makedirs(input_source_dir, exist_ok=True)
 
                lib_paths = {}
                for root, dirs, files in os.walk(lvf_release_dir):
                    for dir_name in dirs:
                        if dir_name.startswith(pvt_corner):
                            dir_path = os.path.join(root, dir_name)
                            for f in os.listdir(dir_path):
                                if f.endswith('.lib'):
                                    lib_file = os.path.join(dir_path, f)
                                    lib_paths[dir_name] = lib_file
 
                missing_files = retry_copy_files(lib_paths, input_source_dir)
                if missing_files:
                    logging.error("Retry failed for the following files:")
                    for file in missing_files:
                        logging.error(file)
                    continue
                else:
                    logging.info("Retry successful. Skipping further processing for %s.", pvt_corner)
                    continue
 
            # If no corner folder exists, clean up logs and lvf* folders before processing
            else:
                logging.info("Not started for %s. Cleaning up existing logs and lvf* folders.", pvt_corner)
                for item in os.listdir(lvf_release_dir):
                    if item.endswith('.log') or os.path.isdir(os.path.join(lvf_release_dir, item)):
                        item_path = os.path.join(lvf_release_dir, item)
                        if os.path.isfile(item_path):
                            os.remove(item_path)
                        elif os.path.isdir(item_path):
                            shutil.rmtree(item_path)
 
            os.makedirs(corner_dir, exist_ok=True)
            os.makedirs(input_source_dir, exist_ok=True)
 
            lib_paths_lvf, liberate_ldb, missing_files = process_release_folder_lvf(lvf_release_dir, pvt_corner, input_source_dir)
            total_missing_files.extend(missing_files)
            # Mark the LVF as finished
            if not missing_files:
                with open(os.path.join(corner_dir, 'LVF_completed.txt'), 'w') as f:
                    f.write("LVF processing completed successfully.\n")
 
    if total_missing_files:
        logging.error("The following files are missing or could not be processed:")
        for file in total_missing_files:
            logging.error(file)
        raise SystemExit("Processing stopped due to missing files.")
 
 
@error_handler
def parse_arguments():
    parser = argparse.ArgumentParser(description="Post Processing for LVF Library Characterization")
    parser.add_argument("--work_dir", required=True, help="Base working directory")
    parser.add_argument("--dirs", nargs='+', required=True, help="List of directories to process")
    parser.add_argument("--pvt_corners", nargs='+', required=True, help="List of PVT corners to process")
    parser.add_argument("--log_file", default="post_process_lvf.log", help="Path to the char log file")
 
    return parser.parse_args()
 
 
def main():
    args = parse_arguments()
    setup_logging(args.log_file)
 
    logging.info("Starting LVF Post Processing")
 
    post_process_lvf(args.work_dir, args.dirs, args.pvt_corners)
 
 
if __name__ == "__main__":
    main()
 
 
 
