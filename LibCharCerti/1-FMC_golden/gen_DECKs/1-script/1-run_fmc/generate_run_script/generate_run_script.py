import os
import stat
import glob
import logging
import argparse
from pathlib import Path
 
# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('script_generation.log'),
        logging.StreamHandler()
    ]
)
 
def clean_and_check_folder(folder):
    """
    Check if mc_sim.sp and nominal_sim.sp exist, remove other files.
    Returns True if both required files exist and no .mt0 or .csv file is present.
    """
    try:
        # Check for .mt0 or .csv files
        mt0_or_csv_exists = any(
            file.endswith(('.mt0', '.csv')) for file in os.listdir(folder)
        )
        if mt0_or_csv_exists:
            logging.info(f"Skipping {folder} because .mt0 or .csv file exists.")
            return False
 
        required_files = ['mc_sim.sp', 'nominal_sim.sp']
        files_exist = all(os.path.exists(os.path.join(folder, f)) for f in required_files)
 
        if not files_exist:
            logging.warning(f"Required files missing in {folder}")
            return False
 
        # Remove all other files except the required ones
        for file in os.listdir(folder):
            file_path = os.path.join(folder, file)
            if file not in required_files and os.path.isfile(file_path):
                try:
                    os.remove(file_path)
                    logging.debug(f"Removed {file_path}")
                except Exception as e:
                    logging.error(f"Error removing {file_path}: {str(e)}")
 
        return True
 
    except Exception as e:
        logging.error(f"Error processing folder {folder}: {str(e)}")
        return False
 
def find_and_clean_spice_folders(corner_deck):
    """Find all existing spice deck folders and clean them."""
    try:
        spice_folders = [f for f in glob.glob(os.path.join(corner_deck, "*"))
                         if os.path.isdir(f)]
        logging.info(f"Found {len(spice_folders)} spice folders in {corner_deck}")
 
        valid_folders = []
        for folder in spice_folders:
            if clean_and_check_folder(folder):
                valid_folders.append(folder)
 
        logging.info(f"Found {len(valid_folders)} valid spice folders")
        return valid_folders
 
    except Exception as e:
        logging.error(f"Error finding spice folders in {corner_deck}: {str(e)}")
        return []
 
def create_submission_script(types, corner, valid_folders, queue, fmc_script_path):
    """Create a job submission script for a specific corner."""
    try:
        file_name = f'submit_all_jobs_{types}_{corner}.sh'
        with open(file_name, 'w') as f:
            # Write the initial CPU checking commands
            f.write("#!/bin/csh -f\n")
            f.write("source /tools/dotfile_new/cshrc.lsfc2 > /dev/null\n")
            f.write("##MAX_PENDING/RUNNING_CPU is max CPU upper-bound\n")
            f.write("##                        set -1 to unlimit CPU counts\n")
            f.write("setenv MAX_PENDING_CPU 500\n")
            f.write("setenv MAX_RUNNING_CPU 4000\n")
            f.write("alias LSF_pend_UB 'bjobs -q {queue} -sum | tail -n1 | awk -v max_job=$MAX_PENDING_CPU '\\''{if (($5>max_job)&&(max_job>0)) {print 1} else {print 0}}'\\''' \n")
            f.write("alias LSF_run_UB 'bjobs -q {queue} -sum | tail -n1 | awk -v max_job=$MAX_RUNNING_CPU '\\''{if (($1>max_job)&&(max_job>0)) {print 1} else {print 0}}'\\''' \n")
            f.write("while ( 1 )\n")
 
            job_count = 0
            f.write(f"  # Submitting jobs for {corner}\n")
 
            for folder in valid_folders:
                # Navigate to the sub-directory
                f.write(f"  cd {folder}\n")
               
#                # Add logic to check for *.csv and *.mt0 files
#                f.write("  set CSV_FILES_EXIST=`ls *.csv 2>/dev/null | wc -l`\n")
#                f.write("  set MT0_FILES_EXIST=`ls *.mt0 2>/dev/null | wc -l`\n")
#                f.write("  if ( $CSV_FILES_EXIST > 0 && $MT0_FILES_EXIST > 0 ) then\n")
#                f.write("    echo \"[Info] Simulation completed in {folder}, skipping job submission.\"\n")
#                f.write("    cd -\n")
#                f.write("    continue\n")
#                f.write("  endif\n")
 
                # Conditional CPU checking and job submission commands
                f.write("  set RUN_TOO_MUCH=`LSF_run_UB`\n")
                f.write("  if ( $RUN_TOO_MUCH == 1 ) then\n")
                f.write("    echo \"[Info] Submission pending for 2 mins due to >$MAX_RUNNING_CPU CPUs running.\"\n")
                f.write("    sleep 120\n")
                f.write("    continue\n")
                f.write("  endif\n")
                f.write("  set PEND_TOO_MUCH=`LSF_pend_UB`\n")
                f.write("  if ( $PEND_TOO_MUCH == 1 ) then\n")
                f.write("    echo \"[Info] Submission pending for 2 mins due to >$MAX_PENDING_CPU CPUs queuing.\"\n")
                f.write("    sleep 120\n")
                f.write("    continue\n")
                f.write("  endif\n")
 
                # Submit the job
                f.write(f"  bsub -q {queue} -J {folder} {fmc_script_path}\n")
                f.write("  cd -\n\n")  # Return to original directory
                job_count += 1
 
            # End the while loop after all jobs are submitted
            f.write("  break\n")
            f.write("end\n")
 
        # Make submission script executable
        st = os.stat(file_name)
        os.chmod(file_name, st.st_mode | stat.S_IEXEC)
 
        logging.info(f"Created submission script for corner '{corner}' with {job_count} jobs")
 
    except Exception as e:
        logging.error(f"Error creating submission script for corner '{corner}': {str(e)}")
 
def main():
    logging.info("Script started")
 
    # Parse arguments
    parser = argparse.ArgumentParser(description='Generate job submission scripts.')
    parser.add_argument('--corner', nargs='+', required=True, help='List of corners to process')
    parser.add_argument('--working_path', required=True, help='Working directory path')
    parser.add_argument('--type_list', nargs='+', required=True, help='List of analysis types (e.g., "hold", "delay")')
    parser.add_argument('--queue', required=True, help='Job queue for submission (e.g., "DMKD_DFSD.q", "all.q")')
    parser.add_argument('--fmc_script_path', required=True, help='Path to FMC script for job submission')
    args = parser.parse_args()
 
    logging.info(f"Processing corner: {args.corner}")
    logging.info(f"Using queue: {args.queue}")
    logging.info(f"Using FMC script path: {args.fmc_script_path}")
 
    try:
        for types in args.type_list:
            logging.info(f"Processing type: {types}")
 
            for corner in args.corner:
                decks_folder = f"{args.working_path}/{corner}_DECKS/{types}/DECKS"
 
                if not os.path.exists(decks_folder):
                    logging.error(f"DECKS folder not found: {decks_folder}")
                    continue
 
                # Find and clean spice folders
                valid_folders = find_and_clean_spice_folders(decks_folder)
 
                if valid_folders:
                    # Create a submission script for each corner
                    create_submission_script(types, corner, valid_folders, args.queue, args.fmc_script_path)
                    logging.info(f"Script completed successfully for type '{types}' and corner '{corner}'")
                else:
                    logging.error(f"No valid spice folders found for type '{types}' and corner '{corner}', submission script not created")
 
    except Exception as e:
        logging.error(f"Main execution error: {str(e)}")
 
if __name__ == "__main__":
    main()
 
