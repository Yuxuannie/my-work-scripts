import os
import argparse
import logging
 
 
def setup_logging(log_file='monitor_merge_status.log'):
    """Set up logging configuration"""
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
 
 
def check_merge_status(target_root_path, corners, rc_type):
    completed_paths = []
    incomplete_paths = []
 
    for corner_idx, corner in enumerate(corners):
        pvt_corner = f"{corner}_25c"
        full_corner = f"{pvt_corner}_{rc_type}"
        corner_path = os.path.join(target_root_path, corner)
 
        logging.info("\n%s\nChecking corner %d/%d: %s\n%s", "="*50, corner_idx + 1, len(corners), corner, "="*50)
 
        if not os.path.exists(corner_path):
            logging.error("Corner path does not exist: %s", corner_path)
            continue
 
        lib_names = [name for name in os.listdir(corner_path) if os.path.isdir(os.path.join(corner_path, name))]
 
        for idx, lib_name in enumerate(lib_names):
            logging.info("\n%s\nChecking lib_name %d/%d: %s\n%s", "-"*50, idx + 1, len(lib_names), lib_name, "-"*50)
            corner_dir = os.path.join(target_root_path, corner, lib_name, "Postprocess", full_corner)
            package_dir = os.path.join(corner_dir, "package")
            root_merge_path = os.path.join(package_dir, "merge_scripts")
 
            if not os.path.exists(root_merge_path):
                logging.info("Root merge path does not exist: %s", root_merge_path)
                incomplete_paths.append(corner_dir)
                continue
 
            # Check if any file ends with hm_lvf_p_ccs.lib
            target_lib_exists = any(file.endswith("hm_lvf_p_ccs_max_cap_8th.lib") for file in os.listdir(root_merge_path))
 
            if target_lib_exists:
                completed_paths.append(corner_dir)
            else:
                incomplete_paths.append(corner_dir)
 
            # Logging the .lib files in the merge_scripts directory
            lib_files = [file for file in os.listdir(root_merge_path) if file.endswith(".lib")]
            if lib_files:
                logging.info("Found .lib files in %s:", root_merge_path)
                for lib_file in lib_files:
                    logging.info("  - %s", lib_file)
            else:
                logging.info("No .lib files found in %s", root_merge_path)
 
    return completed_paths, incomplete_paths
 
 
def append_report_to_log(completed_paths, incomplete_paths, log_file):
    with open(log_file, 'a') as log:
        log.write("\n### Merge Status Report ###\n\n")
 
        log.write("Completed Paths:\n")
        for idx, path in enumerate(completed_paths):
            log.write(f"{idx + 1}/{len(completed_paths)}: {path}\n")
 
        log.write("\nIncomplete Paths:\n")
        for idx, path in enumerate(incomplete_paths):
            log.write(f"{idx + 1}/{len(incomplete_paths)}: {path}\n")
 
        log.write("\n" + "=" * 50 + "\n")
 
        # Brief Summary
        log.write("\n### Summary ###\n\n")
        log.write(f"Total Completed Paths: {len(completed_paths)}\n")
        log.write(f"Total Incomplete Paths: {len(incomplete_paths)}\n")
 
        log.write("\n" + "=" * 50 + "\n")
 
 
def parse_arguments():
    parser = argparse.ArgumentParser(description="Monitor Merge Status for library Characterization")
    parser.add_argument("--target_root_path", required=True, help="Target root path")
    parser.add_argument("--corners", nargs='+', required=True, help="List of corners to process")
    parser.add_argument("--rc_type", required=True, help="RC type")
    parser.add_argument("--log_file", default="monitor_merge_status.log", help="Path to the log file")
 
    return parser.parse_args()
 
 
def main():
    args = parse_arguments()
    setup_logging(args.log_file)
 
    logging.info("Starting Monitor Merge Status")
    logging.info("=" * 50)
 
    completed_paths, incomplete_paths = check_merge_status(args.target_root_path, args.corners, args.rc_type)
    append_report_to_log(completed_paths, incomplete_paths, args.log_file)
 
    logging.info("Completed monitoring merge status. Report appended to log file: %s", args.log_file)
    logging.info("=" * 50)
 
 
if __name__ == "__main__":
    main()
 
 
