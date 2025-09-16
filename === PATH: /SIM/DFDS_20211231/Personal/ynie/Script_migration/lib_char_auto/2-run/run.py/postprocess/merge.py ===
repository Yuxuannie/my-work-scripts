import os
import subprocess
import shutil
import logging
import argparse
from functools import wraps
 
def error_handler(func):
    """Decorator for error handling"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logging.error("Error in %s: %s", func.__name__, str(e))
            return None
    return wrapper
 
def setup_logging(log_file):
    """Set up logging configuration"""
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
 
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
 
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)
 
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
 
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
 
    return logger
 
@error_handler
def copy_package(source_package_dir, package_dir, logger):
    """Copy the entire package folder from source_package_dir to corner_dir, always overwriting"""
    logger.info("===================================================")
    logger.info("Starting to copy package from %s to %s", source_package_dir, package_dir)
    try:
        if os.path.exists(package_dir):
            logger.info("Removing existing package directory: %s", package_dir)
            shutil.rmtree(package_dir)
        shutil.copytree(source_package_dir, package_dir)
        logger.info("Successfully copied package folder from %s to %s", source_package_dir, package_dir)
 
        # Change permissions to make all .sh files executable
        for root, _, files in os.walk(package_dir):
            for file in files:
                if file.endswith(('.sh', '.csh', '.tcl', '.pl')):
                    file_path = os.path.join(root, file)
                    try:
                        os.chmod(file_path, 0o755)
                        logger.info("Changed permissions to executable for script: %s", file_path)
                    except Exception as e:
                        logger.error("Failed to change permissions for %s: %s", file_path, str(e))
    except Exception as e:
        logger.error("Failed to copy package from %s to %s: %s", source_package_dir, package_dir, str(e))
        raise
    logger.info("===================================================")
 
def parse_product_name(lib_name):
    """Parse the product_name from lib_name"""
    parts = lib_name.split('_')
    return '_'.join(parts[:-1])
 
@error_handler
def check_input_libs(input_source_dir, logger):
    """Check if necessary input libraries with specified suffixes are present in the input_source folder"""
    logger.info("===================================================")
    logger.info("Checking input libraries in %s", input_source_dir)
    expected_suffixes = [
        "ccs_lib2lib.lib",
        "hold_unc.sens.lib",
        "mpw_unc.sens.lib",
        "psocv.sens.lib",
        "setup_unc.sens.lib"
    ]
 
    missing_libs = []
    for suffix in expected_suffixes:
        lib_found = False
        for file in os.listdir(input_source_dir):
            if file.endswith(suffix):
                lib_found = True
                break
        if not lib_found:
            missing_libs.append(suffix)
 
    if missing_libs:
        logger.error("Missing required libraries with suffixes: %s", ", ".join(missing_libs))
        raise FileNotFoundError(f"Missing required libraries: {', '.join(missing_libs)}")
    else:
        logger.info("All required libraries are present in the input_source directory.")
    logger.info("===================================================")
 
def construct_lib_file_name(product_name, pvt_corner, suffix):
    return f"{product_name}{pvt_corner}_{suffix}"
@error_handler
def run_merge_scripts(package_dir, product_name, corner_dir, pvt_corner, logger):
    """Run the merge scripts to process the libraries"""
    root_merge_path = os.path.join(package_dir, "merge_scripts")
    replace_script_source = "/SIM/DFSD_20250430_C651_chamber/N2_Tanager_LVF/1-lib_char_auto/run.py/postprocess/replace_antenna_diode_pins_script.py"
    replace_script_dest = os.path.join(root_merge_path, "replace_antenna_diode_pins_script.py")
 
    # Ensure the root_merge_path exists
    if not os.path.exists(root_merge_path):
        logger.error("The root_merge_path does not exist: %s", root_merge_path)
        return
    else:
        logger.info("===================================================")
        logger.info("Processing merge scripts in: %s", root_merge_path)
 
        # Traverse all files in the root_merge_path
        for root, _, files in os.walk(root_merge_path):
            for file in files:
                file_path = os.path.join(root, file)
 
                # Read the content of the file
                with open(file_path, 'r') as f:
                    content = f.read()
 
                # Replace placeholders with actual values
                content = content.replace("root_merge_path", root_merge_path)
                content = content.replace("product_name", product_name)
                content = content.replace("corner_dir", corner_dir)
                content = content.replace("package_dir", package_dir)
                content = content.replace("pvt_corner", pvt_corner)
 
                # Write the updated content back to the file
                with open(file_path, 'w') as f:
                    f.write(content)
 
                logger.info("Processed file: %s", file_path)
 
        logger.info("===================================================")
 
        # List of scripts to run in sequence with their corresponding output suffixes
        scripts_to_run = [
            ("run_hybrid.sh", "dfd_defined_hold_unc.sens_hybrid.lib"),
            ("run_hybrid_setup.sh", "dfd_defined_setup_unc.sens_hybrid.lib"),
            ("swap_hold.sh", "dfd_defined_hold_unc.sens_hybrid_swap.lib"),
            ("swap_setup.sh", "dfd_defined_setup_unc.sens_hybrid_swap.lib"),
            ("merge_hm_and_corner.sh", "merged_nomial_plus3sigconslvf_indx_aligned.lib"),
            ("merge_lvf_socv_and_corner.sh", "merged_1_indx_aligned.lib"),
            ("merge_merged1_with_hold.sh", "hm_lvf_p_ccs_without_setup_tables.lib"),
            ("merge_merged1_with_setup.sh", "hm_lvf_p_ccs.lib"),
            ("create_8th_index_max_cap_libs.csh", "hm_lvf_p_ccs_max_cap_8th.lib")
        ]
 
        previous_job_id = None
 
        for script, output_suffix in scripts_to_run:
            script_path = os.path.join(root_merge_path, script)
            if os.path.exists(script_path):
                try:
                    logger.info("===================================================")
                    logger.info("Submitting script to bsub: %s", script_path)
 
                    # If there is a previous job, set the dependency
                    if previous_job_id:
                        bsub_command = f"bsub -w 'done({previous_job_id})' -q DMKD_DFSD.q -sp 10 {script_path}"
                    else:
                        bsub_command = f"bsub -q DMKD_DFSD.q -sp 10 {script_path}"
 
                    result = subprocess.run(
                        bsub_command,
                        shell=True,
                        check=True,
                        cwd=root_merge_path,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE
                    )
 
                    # Extract job id from bsub output
                    output = result.stdout.decode().strip()
                    job_id = output.split('<')[1].split('>')[0]
                    previous_job_id = job_id
 
                    logger.info("Submitted script: %s with job id: %s", script_path, job_id)
 
                    # Run replace_antenna_diode_pins for certain scripts
#                    if script in ["merge_hm_and_corner.sh", "merge_lvf_socv_and_corner.sh", "merge_merged1_with_hold.sh", "merge_merged1_with_setup.sh", "create_8th_index_max_cap_libs.csh"]:
#                        logger.info(f"Waiting for {script} to complete before running replace_antenna_diode_pins for {output_suffix}")
#                        replace_antenna_diode_pins_log = os.path.join(root_merge_path, f"replace_antenna_diode_pins_{script}.log")
#
#                        # Construct the library file name based on the product name, pvt corner, and suffix
#                        lib_to_modify = construct_lib_file_name(product_name, pvt_corner, output_suffix)
#
#                        # Join the root_merge_path to get the full path
#                        lib_to_modify_full_path = os.path.join(root_merge_path, lib_to_modify)
#
#                        # Copy the replace_antenna_diode_pins_script to root_merge_path
#                        shutil.copy(replace_script_source, replace_script_dest)
#                        logger.info("Copied replace_antenna_diode_pins_script to %s", replace_script_dest)
#
#                        replace_antenna_diode_pins_command = f"bsub -w 'done({job_id})' -q DMKD_DFSD.q -sp 10 -cwd {root_merge_path} /usr/local/python/3.9.10/bin/python3 {replace_script_dest} {lib_to_modify_full_path} {replace_antenna_diode_pins_log}"
#
#                        result = subprocess.run(
#                            replace_antenna_diode_pins_command,
#                            shell=True,
#                            check=True,
#                            cwd=root_merge_path,
#                            stdout=subprocess.PIPE,
#                            stderr=subprocess.PIPE
#                        )
#
#                        output = result.stdout.decode().strip()
#                        job_id = output.split('<')[1].split('>')[0]
#                        previous_job_id = job_id
#
#                        logger.info("Submitted replace_antenna_diode_pins with job id: %s", job_id)
 
                except subprocess.CalledProcessError as e:
                    logger.error("Error submitting script %s: %s", script, e.stderr.decode())
                logger.info("===================================================")
            else:
                logger.error("Script not found: %s", script_path)
 
@error_handler
def process_lib(corner, lib_name, args, log_dir):
    corner_info = f"{corner}_25c"
    pvt_corner = f"{corner_info}_{args.rc_type}"
 
    corner_dir = os.path.join(args.target_root_path, corner, lib_name, "Postprocess", pvt_corner)
    package_dir = os.path.join(corner_dir, "package")
    input_source_dir = os.path.join(corner_dir, "input_source")
 
    log_file = os.path.join(log_dir, f"{lib_name}.log")
    logger = setup_logging(log_file)
 
    logger.info("===================================================")
    logger.info("Preparing to copy package for lib_name: %s", lib_name)
    copy_package(args.source_package_dir, package_dir, logger)
 
    product_name = parse_product_name(lib_name)
    logger.info("Parsed product name: %s for lib_name: %s", product_name, lib_name)
 
    logger.info("Checking input libraries for lib_name: %s", lib_name)
    check_input_libs(input_source_dir, logger)
 
    logger.info("Running merge scripts for lib_name: %s", lib_name)
    run_merge_scripts(package_dir, product_name, corner_dir, pvt_corner, logger)
    logger.info("===================================================")
 
@error_handler
def parse_arguments():
    parser = argparse.ArgumentParser(description="Post Processing for library Characterization - Step 2")
    parser.add_argument("--target_root_path", required=True, help="Target root path")
    parser.add_argument("--source_package_dir", required=True, help="Source package directory")
    parser.add_argument("--corner", required=True, help="Corner to process")
    parser.add_argument("--rc_type", required=True, help="RC type")
    parser.add_argument("--log_file", default="Step_2_Post.log", help="Path to the global log file")
    parser.add_argument("--log_dir", required=True, help="Directory to store individual log files")
    parser.add_argument("--max_workers", type=int, default=22, help="Maximum number of workers to run in parallel")
    parser.add_argument("--dir", required=True, help="Directory to process")
    parser.add_argument("--lib_name", required=True, help="Library name to process")
 
    return parser.parse_args()
 
def main():
    args = parse_arguments()
    global_logger = setup_logging(args.log_file)
 
    # Log all arguments for verification
    global_logger.info("Received arguments:")
    for arg, value in vars(args).items():
        global_logger.info("  %s: %s", arg, value)
 
    global_logger.info("\n")
    global_logger.info("###########################################################")
    global_logger.info("Starting Merging")
    global_logger.info("###########################################################\n")
 
    # Process a single corner, directory, and library name
    process_lib(args.corner, args.lib_name, args, args.log_dir)
 
if __name__ == "__main__":
    main()
 
 
