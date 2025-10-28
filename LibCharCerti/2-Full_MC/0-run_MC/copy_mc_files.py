 
import os
import sys
import shutil
import re
import logging
import time
from datetime import datetime
 
def setup_logging(log_file="mc_process.log"):
    """Set up logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
   
    # Create a file handler
    file_handler = logging.FileHandler(log_file, mode='a')
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
   
    # Add the file handler to the root logger
    logging.getLogger('').addHandler(file_handler)
 
def log_section(section_name):
    """Log a section divider to make the log more readable"""
    divider = "=" * 60
    logging.info(divider)
    logging.info(f"SECTION: {section_name}")
    logging.info(divider)
 
def create_corner_directories(working_path, corners):
    """
    Create a directory for each corner in the working path
    """
    log_section("Creating Corner Directories")
   
    for corner in corners:
        corner_dir = os.path.join(working_path, corner)
        try:
            os.makedirs(corner_dir, exist_ok=True)
            logging.info(f"Created/verified corner directory: {corner_dir}")
        except Exception as e:
            logging.error(f"Failed to create corner directory {corner_dir}: {str(e)}")
            sys.exit(1)
   
    logging.info(f"Successfully created {len(corners)} corner directories")
 
def copy_mc_files(ref_deck_path, corner, sim_type, working_path):
    """
    Copy mc_sim.sp files from reference deck path to working path for a specific corner
    """
    log_section(f"Copying Files for Corner: {corner}")
   
    source_path = os.path.join(ref_deck_path, f"{corner}_DECKS", sim_type, "DECKS")
    corner_dir = os.path.join(working_path, corner)
   
    # Check if source directory exists
    if not os.path.exists(source_path):
        logging.warning(f"Source path {source_path} does not exist. Skipping.")
        return
   
    # Get all subdirectories in the source path
    try:
        subdirs = [d for d in os.listdir(source_path) if os.path.isdir(os.path.join(source_path, d))]
    except Exception as e:
        logging.error(f"Error accessing {source_path}: {str(e)}")
        return
   
    logging.info(f"Found {len(subdirs)} subdirectories in {source_path}")
   
    # Copy mc_sim.sp from each subdirectory to working path/corner
    copied_count = 0
    skipped_count = 0
    error_count = 0
   
    for i, subdir in enumerate(subdirs):
        source_file = os.path.join(source_path, subdir, "mc_sim.sp")
        dest_dir = os.path.join(corner_dir, subdir)
        dest_file = os.path.join(dest_dir, "mc_sim.sp")
       
        # Log progress every 20 files or at the end
        if (i + 1) % 20 == 0 or i == len(subdirs) - 1:
            logging.info(f"Progress: {i+1}/{len(subdirs)} directories processed")
       
        # Check if source file exists
        if not os.path.isfile(source_file):
            logging.warning(f"File {source_file} does not exist. Skipping.")
            skipped_count += 1
            continue
       
        # Create destination directory if it doesn't exist
        os.makedirs(dest_dir, exist_ok=True)
       
        # Copy the file
        try:
            shutil.copy2(source_file, dest_file)
            copied_count += 1
            if (i + 1) % 50 == 0:  # Log details less frequently to keep log manageable
                logging.info(f"Copied {source_file} to {dest_file}")
        except Exception as e:
            logging.error(f"Error copying {source_file}: {str(e)}")
            error_count += 1
   
    logging.info(f"Corner {corner} summary: {copied_count} files copied, {skipped_count} skipped, {error_count} errors")
 
def modify_mc_files(working_path, corner):
    """
    Modify all mc_sim.sp files in the working path/corner:
    1. Replace "sweep monte=1" with "sweep monte=100000"
    2. Replace "sampling_method=lhs" with "sampling_method=sobol"
    """
    log_section(f"Modifying MC Files for Corner: {corner}")
   
    corner_dir = os.path.join(working_path, corner)
   
    # Get all subdirectories in the corner directory
    try:
        subdirs = [d for d in os.listdir(corner_dir) if os.path.isdir(os.path.join(corner_dir, d))]
    except Exception as e:
        logging.error(f"Error accessing {corner_dir}: {str(e)}")
        return
   
    logging.info(f"Found {len(subdirs)} subdirectories to process in {corner_dir}")
   
    modified_count = 0
    skipped_count = 0
    error_count = 0
   
    for i, subdir in enumerate(subdirs):
        file_path = os.path.join(corner_dir, subdir, "mc_sim.sp")
       
        # Log progress every 20 files or at the end
        if (i + 1) % 20 == 0 or i == len(subdirs) - 1:
            logging.info(f"Progress: {i+1}/{len(subdirs)} files processed")
       
        # Check if file exists
        if not os.path.isfile(file_path):
            logging.warning(f"File {file_path} does not exist. Skipping.")
            skipped_count += 1
            continue
       
        try:
            # Read the file content
            with open(file_path, 'r') as file:
                content = file.read()
           
            # Count original occurrences for verification
            monte_count_before = content.count("sweep monte=1")
            sampling_count_before = content.count("sampling_method=lhs")
           
            # Perform replacements
            new_content = content.replace("sweep monte=1", "sweep monte=100000")
            new_content = new_content.replace("sampling_method=lhs", "sampling_method=sobol")
           
            # Count new occurrences for verification
            monte_count_after = new_content.count("sweep monte=100000")
            sampling_count_after = new_content.count("sampling_method=sobol")
           
            # Write the modified content back to the file
            with open(file_path, 'w') as file:
                file.write(new_content)
           
            # Log detailed info for some files
            if (i + 1) % 50 == 0:
                logging.info(f"Modified {file_path}: Replaced {monte_count_before} monte instances and {sampling_count_before} sampling instances")
           
            modified_count += 1
        except Exception as e:
            logging.error(f"Error modifying {file_path}: {str(e)}")
            error_count += 1
   
    logging.info(f"Modification summary for corner {corner}: {modified_count} files modified, {skipped_count} skipped, {error_count} errors")
 
def create_run_scripts(working_path, corner):
    """
    Create run.sh file in each subdirectory in the working path/corner
    """
    log_section(f"Creating Run Scripts for Corner: {corner}")
   
    corner_dir = os.path.join(working_path, corner)
   
    # Get all subdirectories in the corner directory
    try:
        subdirs = [d for d in os.listdir(corner_dir) if os.path.isdir(os.path.join(corner_dir, d))]
    except Exception as e:
        logging.error(f"Error accessing {corner_dir}: {str(e)}")
        return
   
    logging.info(f"Found {len(subdirs)} subdirectories to create run scripts in {corner_dir}")
   
    created_count = 0
    error_count = 0
   
    for i, subdir in enumerate(subdirs):
        run_script_path = os.path.join(corner_dir, subdir, "run.sh")
       
        # Log progress every 20 files or at the end
        if (i + 1) % 20 == 0 or i == len(subdirs) - 1:
            logging.info(f"Progress: {i+1}/{len(subdirs)} run scripts processed")
       
        try:
            # Create run.sh with execute permission
            with open(run_script_path, 'w') as file:
                file.write("#!/bin/bash\n\n")
                file.write("# Auto-generated run script for HSPICE monte carlo simulation\n")
                file.write(f"# Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                file.write(f"# Corner: {corner}\n\n")
                file.write(f"source /tools/dotfile_new/cshrc.lsfc2\n")
                file.write('export LM_LICENSE_FILE="27020@lic10:27020@linux96:27020@lic20:27020@sjlic5:27020@lic12"\n')
                file.write('export SNPSLMD_LICENSE_FILE="27020@lic10:27020@linux96:27020@lic20:27020@sjlic5:27020@lic12"\n')
                file.write("/tools/synopsys/hspice/V-2023.12-SP1/hspice/bin/hspice -dp 400 -dpconfig ~/lsf.cfg -i ./mc_sim.sp -o ./OUT\n")
           
            # Make the script executable
            os.chmod(run_script_path, 0o755)
           
            if (i + 1) % 50 == 0:
                logging.info(f"Created run script at {run_script_path}")
           
            created_count += 1
        except Exception as e:
            logging.error(f"Error creating run script at {run_script_path}: {str(e)}")
            error_count += 1
   
    logging.info(f"Run script creation summary for corner {corner}: {created_count} scripts created, {error_count} errors")
 
 
def main():
    # Set up logging
    log_file = "mc_process.log"
    setup_logging(log_file)
   
    start_time = time.time()
   
    # Log script start
    logging.info("=" * 80)
    logging.info(f"MC Process Script Started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logging.info("=" * 80)
   
    # Check command line arguments
    if len(sys.argv) < 5:
        logging.error("Insufficient arguments provided")
        logging.error("Usage: python process_mc_files.py ref_deck_path working_path type corner1 corner2 ...")
        sys.exit(1)
   
    ref_deck_path = sys.argv[1]
    working_path = sys.argv[2]
    sim_type = sys.argv[3]
    corners = sys.argv[4:]
   
    logging.info(f"Reference Deck Path: {ref_deck_path}")
    logging.info(f"Working Path: {working_path}")
    logging.info(f"Simulation Type: {sim_type}")
    logging.info(f"Corners: {corners}")
   
    # Create working directory if it doesn't exist
    try:
        os.makedirs(working_path, exist_ok=True)
        logging.info(f"Ensured working directory exists: {working_path}")
    except Exception as e:
        logging.error(f"Failed to create working directory {working_path}: {str(e)}")
        sys.exit(1)
   
    # Create directories for each corner
    create_corner_directories(working_path, corners)
   
    # Process each corner
    for corner in corners:
        logging.info(f"Processing corner: {corner}")
       
        # Copy files for this corner
        copy_mc_files(ref_deck_path, corner, sim_type, working_path)
       
        # Modify MC files for this corner
        modify_mc_files(working_path, corner)
       
        # Create run scripts for this corner
        create_run_scripts(working_path, corner)
 

    # Log script completion
    elapsed_time = time.time() - start_time
    logging.info("=" * 80)
    logging.info(f"MC Process Script Completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logging.info(f"Total execution time: {elapsed_time:.2f} seconds")
    logging.info("=" * 80)
   
    print(f"All operations completed successfully! Log saved to {log_file}")
 
if __name__ == "__main__":
    main()
 
