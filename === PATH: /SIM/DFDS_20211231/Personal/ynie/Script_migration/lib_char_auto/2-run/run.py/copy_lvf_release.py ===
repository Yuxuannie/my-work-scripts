import os
import shutil
import logging
import argparse
import re
 
def setup_logging(log_file='copy_script.log', warning_log_file='warnings.log'):
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        filename=log_file,
        filemode='w'
    )
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)
 
    # Setup a separate logger for warnings
    warning_logger = logging.getLogger('warning_logger')
    warning_handler = logging.FileHandler(warning_log_file, mode='w')
    warning_handler.setLevel(logging.WARNING)
    warning_handler.setFormatter(formatter)
    warning_logger.addHandler(warning_handler)
    return warning_logger
 
def str2bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')
 
def find_lpe_netlist_path(rf_dir, dir_name, lpe_corner):
    logging.debug(f"Searching for LPE netlist in {rf_dir}/{dir_name} for corner {lpe_corner}")
    possible_paths = [
        os.path.join(rf_dir, dir_name, "LPE", "LPE", "LPE"),
        os.path.join(rf_dir, dir_name, "Netlist")
    ]
    pattern = re.escape(lpe_corner).replace(r'\_', '_')
    for base_path in possible_paths:
        if os.path.exists(base_path):
            logging.debug(f"Checking path: {base_path}")
            for item in os.listdir(base_path):
                if re.fullmatch(pattern, item):
                    logging.debug(f"LPE netlist found: {item}")
                    return os.path.join(base_path, item)
    logging.warning(f"No LPE netlist found in {rf_dir}/{dir_name}.")
    return None
 
def find_fallback_lpe_netlist_path(rf_dir, dir_name, new_c_code, lpe_corner):
    logging.info(f"Attempting to find fallback LPE netlist with new c_code in {rf_dir} for corner {lpe_corner}")
 
    parts = dir_name.rsplit('_', 2)
    if len(parts) == 3:
        base_name = parts[0]
        fallback_dir_name = f"{base_name}_{new_c_code}"
        logging.info(f"Constructed fallback directory name: {fallback_dir_name}")
    else:
        logging.error(f"Unexpected directory format for {dir_name}. Expected a suffix to replace.")
        return None
 
    fallback_path = find_lpe_netlist_path(rf_dir, fallback_dir_name, lpe_corner)
    if fallback_path:
        logging.info(f"Successfully found fallback LPE netlist: {fallback_path}")
    else:
        logging.error(f"Failed to find fallback LPE netlist in {rf_dir}/{fallback_dir_name}")
    return fallback_path
 
def find_and_copy_fix_ref(rf_dir, dir_name, target_dir):
    logging.debug(f"Searching for fix_ref.lib in {rf_dir}/{dir_name}")
    for root, dirs, files in os.walk(os.path.join(rf_dir, dir_name)):
        if 'fix_ref.lib' in files:
            shutil.copy(os.path.join(root, 'fix_ref.lib'), target_dir)
            logging.info(f"fix_ref.lib copied to {target_dir}")
            return
    logging.warning(f"fix_ref.lib not found in {rf_dir}/{dir_name}.")
 
def replace_paths(base_dir, replacements):
    logging.info(f"Starting path replacement process in {base_dir}")
    lvf_release_dir = os.path.join(base_dir, "LVF", "Release")
    for root, dirs, files in os.walk(lvf_release_dir):
        for file_name in files:
            file_path = os.path.join(root, file_name)
           
            with open(file_path, 'r') as file:
                content = file.read()
 
            replacements_made = False
 
            for old_path, new_path in replacements:
                if old_path in content:
                    logging.info(f"Found old path: {old_path} in {file_path}")
                    content = re.sub(re.escape(old_path), new_path, content)
                    logging.info(f"Replaced with new path: {new_path}")
                    replacements_made = True
 
            if replacements_made:
                with open(file_path, 'w') as file:
                    file.write(content)
                logging.info(f"Updated file: {file_path} with new paths")
 
    logging.info(f"Path replacement completed in {lvf_release_dir}")
 
def copy_lpe_netlist(lpe_netlist_path, destination):
    logging.debug(f"Copying LPE netlist from {lpe_netlist_path} to {destination}")
    if os.path.exists(destination):
        logging.debug(f"Removing existing directory: {destination}")
        shutil.rmtree(destination)
    shutil.copytree(lpe_netlist_path, destination)
    logging.info(f"LPE netlist copied to {destination}")
 
def copy_char_kit_and_lvf(args, dir_name, warning_logger):
    logging.info("------------------------------------------------------")
    logging.info(f"Processing directory: {dir_name}")
    logging.info("------------------------------------------------------")
   
    base_dir = os.path.join(args.work_dir, dir_name)
    lvf_release_dir = os.path.join(base_dir, "LVF", "Release")
    os.makedirs(lvf_release_dir, exist_ok=True)
 
    logging.info("------------------------------------------------------")
    # Copy fix_ref.lib
    logging.info("Attempting to copy fix_ref.lib")
    find_and_copy_fix_ref(args.rf_dir, dir_name, lvf_release_dir)
 
    # Define allowed extensions
    allowed_extensions = ('.sh', '.tcl', '.inc')
 
    # Copy files for each PVT corner
    logging.info("Starting to copy files for each PVT corner")
    for corner in args.pvt_corners:
        logging.info(f"Processing PVT corner: {corner}")
        # Copy LVF files separately
        lvf_dir = os.path.join(args.rf_dir, dir_name, "LVF")
        for section in [ "Release"]:
            src_dir = os.path.join(lvf_dir, section)
            dst_dir = os.path.join(base_dir, "LVF", section)
            if not os.path.exists(src_dir):
                warning_logger.warning(f"Source LVF directory {src_dir} does not exist. Skipping.")
                continue
            for item in os.listdir(src_dir):
                item_path = os.path.join(src_dir, item)
                if os.path.isfile(item_path) and re.search(f".*{re.escape(corner)}.*", item):
                    if item.lower().endswith(allowed_extensions):
                        shutil.copy(item_path, dst_dir)
                        logging.info(f"Copied LVF {item} to {dst_dir}")
 
    logging.info("------------------------------------------------------")
    # Replace paths in LVF/Release folder only
    logging.info("Replacing old paths with new paths in LVF/Release folder")
    replace_paths(base_dir, args.replacements)
 
    logging.info(f"Finished processing directory: {dir_name}")
    logging.info("------------------------------------------------------")
 
def parse_arguments():
    parser = argparse.ArgumentParser(description="Library Characterization Automation Script")
    parser.add_argument("--work_dir", required=True, help="Base working directory")
    parser.add_argument("--rf_dir", required=True, help="Reference directory from SCLD")
    parser.add_argument("--replacements", nargs='*', default=[], help="List of old,new path pairs for replacement")
    parser.add_argument("--dirs", nargs='+', required=True, help="List of directories to process")
    parser.add_argument("--pvt_corners", nargs='+', required=True, help="List of PVT corners to process")
    parser.add_argument("--use_replace", type=str2bool, required=True, help="Flag to process additional sf/fs corners")
    parser.add_argument("--log_file", default="Step_1_copy.log", help="Path to the copy log file")
    parser.add_argument("--LPE_corner", required=True, help="LPE corner")
    parser.add_argument("--corners", nargs='+', required=True, help="List of corners")
    parser.add_argument("--new_c_code", required=True, help="New c_code for fallback LPE netlist")
 
    args = parser.parse_args()
 
    # Convert replacements into a list of tuples
    replacements = []
    for replacement in args.replacements:
        try:
            old_path, new_path = replacement.split(',', 1)
            replacements.append((old_path.strip(), new_path.strip()))
        except ValueError:
            logging.error(f"Invalid replacement format: {replacement}. Expected format 'old_path,new_path'.")
            raise
 
    args.replacements = replacements
 
    return args
 
def main():
    args = parse_arguments()
    warning_logger = setup_logging(args.log_file, 'warnings.log')
 
    logging.info("======================================================")
    logging.info("Script arguments:")
    for arg, value in vars(args).items():
        logging.info("  %s: %s", arg, value)
    logging.info("======================================================")
 
    logging.info("Starting copy scripts from Reference folder")
    logging.info("======================================================")
 
    for dir_name in args.dirs:
        copy_char_kit_and_lvf(args, dir_name, warning_logger)
 
    logging.info("Copy script execution completed successfully")
    logging.info("======================================================")
 
if __name__ == "__main__":
    main()
 
 
 
