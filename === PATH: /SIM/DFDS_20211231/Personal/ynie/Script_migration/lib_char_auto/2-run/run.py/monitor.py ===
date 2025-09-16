import os
import glob
import time
import logging
import argparse
from datetime import datetime
from collections import deque
 
# Set up logging for general monitoring
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('simulation_monitor.log'),
        logging.StreamHandler()
    ]
)
 
# Set up logging for failed simulations
failed_log_handler = logging.FileHandler('failed_simulations.log')
failed_log_handler.setLevel(logging.ERROR)
failed_log_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
failed_logger = logging.getLogger('failed_simulations')
failed_logger.addHandler(failed_log_handler)
 
# Set up logging for no ongoing simulations
no_ongoing_log_handler = logging.FileHandler('no_ongoing_simulations.log')
no_ongoing_log_handler.setLevel(logging.INFO)
no_ongoing_log_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
no_ongoing_logger = logging.getLogger('no_ongoing_simulations')
no_ongoing_logger.addHandler(no_ongoing_log_handler)
 
def extract_last_error_lines(file_path, num_lines=3):
    """Extract the last few lines containing 'error' from a log file."""
    error_lines = deque(maxlen=num_lines)
    try:
        with open(file_path, 'r') as file:
            for line in file:
                if "error" in line.lower():
                    error_lines.append(line.strip())
    except Exception as e:
        logging.error(f"Could not read file {file_path}: {str(e)}")
    return list(error_lines)
 
def extract_last_lines(file_path, num_lines=10):
    """Extract the last few lines from a log file."""
    last_lines = deque(maxlen=num_lines)
    try:
        with open(file_path, 'r') as file:
            for line in file:
                last_lines.append(line.strip())
    except Exception as e:
        logging.error(f"Could not read file {file_path}: {str(e)}")
    return list(last_lines)
 
def check_simulation_status(root_path, sub_dirs, sub_sub_dir_pattern, completion_criteria, total_criteria, ongoing_criteria, error_criteria):
    """Monitor simulation results based on user-defined criteria."""
    logging.debug("Starting status check for simulations.")
 
    status_summary = {
        'total': 0,
        'completed': 0,
        'running': 0,
        'failed': 0,
        'not_started': 0,
        'failed_jobs': [],
        'ongoing_jobs': [],
        'completed_jobs': [],
        'not_started_jobs': []
    }
 
    for sub_dir in sub_dirs:
        base_path = os.path.join(root_path, sub_dir)
        search_pattern = os.path.join(base_path, sub_sub_dir_pattern)
        logging.debug(f"Searching for directories with pattern: {search_pattern}")
 
        # Find all target folders
        target_folders = glob.glob(search_pattern)
        logging.debug(f"Found {len(target_folders)} target folders.")
 
        for folder in target_folders:
            if not os.path.isdir(folder):
                logging.warning(f"Skipped non-directory target: {folder}")
                continue
 
            # Count total simulations based on total_criteria
            total_simulations = len(glob.glob(os.path.join(folder, total_criteria)))
            status_summary['total'] += total_simulations
            logging.debug(f"Total simulations in {folder}: {total_simulations}")
 
            # Check completion: either .lib or .ldb.gz file indicates completion
            if glob.glob(os.path.join(folder, "tcb*.lib")) or glob.glob(os.path.join(folder, "tcb*ldb.gz")):
                status_summary['completed'] += 1
                status_summary['completed_jobs'].append(folder)
                logging.info(f"Simulation completed in folder: {folder}")
                continue
 
            # Check for errors: "error" appears more than 3 times in log files
            error_files = glob.glob(os.path.join(folder, error_criteria))
            for error_file in error_files:
                with open(error_file, 'r') as f:
                    error_content = f.read().lower()
                    # Filter lines that start with "error (var"
                    error_lines = [line for line in error_content.splitlines() if line.startswith("error (var")]
                    if len(error_lines) > 3:
                        status_summary['failed'] += 1
                        status_summary['failed_jobs'].append(error_file)
                        last_errors = extract_last_error_lines(error_file)
                        failed_logger.error(f"\n{'='*40}\nFailed in {error_file}\nLast Errors:\n" + "\n".join(last_errors))
                        continue
 
            # Check if ongoing: "VARIETY exited on" should not appear in log files
            ongoing_log_files = glob.glob(os.path.join(folder, ongoing_criteria))
            ongoing = False
            for log_file in ongoing_log_files:
                with open(log_file, 'r') as f:
                    if "VARIETY exited on" not in f.read():
                        ongoing = True
                        break
 
            if ongoing:
                status_summary['running'] += 1
                status_summary['ongoing_jobs'].append(folder)
                logging.info(f"Ongoing simulations detected in folder: {folder}")
            else:
                status_summary['not_started'] += 1
                status_summary['not_started_jobs'].append(folder)
                last_lines = extract_last_lines(log_file)
                no_ongoing_logger.info(f"\n{'='*40}\nNo ongoing simulation in {folder}\nLast Lines:\n" + "\n".join(last_lines))
                logging.debug(f"No ongoing simulations in folder: {folder}")
 
    logging.debug("Completed status check for simulations.")
    return status_summary
 
def log_status_report(status_summary):
    """Log formatted status report."""
    logging.info("\n" + "="*60)
    logging.info("Simulation Status Report")
    logging.info(f"Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logging.info("="*60)
 
    total = status_summary['total']
    if total > 0:
        completed_pct = (status_summary['completed'] / total) * 100
        running_pct = (status_summary['running'] / total) * 100
        failed_pct = (status_summary['failed'] / total) * 100
        not_started_pct = (status_summary['not_started'] / total) * 100
 
        logging.info(f"Total Simulations: {total}")
 
        # Completed Simulations
        logging.info("\n" + "="*20 + " Completed Simulations " + "="*20)
        logging.info(f"Completed: {status_summary['completed']} ({completed_pct:.1f}%)")
        for job in status_summary['completed_jobs']:
            logging.info(f"- {job}")
 
        # Ongoing Simulations
        logging.info("\n" + "="*20 + " Ongoing Simulations " + "="*20)
        logging.info(f"Running: {status_summary['running']} ({running_pct:.1f}%)")
        for job in status_summary['ongoing_jobs']:
            logging.info(f"- {job}")
 
        # Failed Simulations
        logging.info("\n" + "="*20 + " Failed Simulations " + "="*20)
        logging.info(f"Failed: {status_summary['failed']} ({failed_pct:.1f}%)")
        for job in status_summary['failed_jobs']:
            logging.info(f"- {job}")
 
        # Not Started Simulations
        logging.info("\n" + "="*20 + " Not Started Simulations " + "="*20)
        logging.info(f"Not Started: {status_summary['not_started']} ({not_started_pct:.1f}%)")
        for job in status_summary['not_started_jobs']:
            logging.info(f"- {job}")
 
    logging.info("="*60 + "\n")
 
def monitor_simulations(root_path, sub_dirs, sub_sub_dir_pattern, completion_criteria, total_criteria, ongoing_criteria, error_criteria, interval=300):
    """Continuous monitoring of simulation status."""
    try:
        while True:
            logging.debug("Starting a new monitoring cycle.")
            status_summary = check_simulation_status(root_path, sub_dirs, sub_sub_dir_pattern, completion_criteria, total_criteria, ongoing_criteria, error_criteria)
            log_status_report(status_summary)
 
            # Exit if all simulations are either completed or failed
            total_done = status_summary['completed'] + status_summary['failed']
            if total_done == status_summary['total']:
                logging.info("All simulations have finished.")
                break
 
            logging.info(f"Waiting {interval} seconds before next check...")
            time.sleep(interval)
 
    except KeyboardInterrupt:
        logging.info("Monitoring stopped by user")
    except Exception as e:
        logging.error(f"Monitoring error: {str(e)}")
 
def main():
    parser = argparse.ArgumentParser(description="Monitor simulations with custom criteria")
    parser.add_argument("--root_path", required=True, help="Root path to search")
    parser.add_argument("--sub_dirs", nargs='+', required=True, help="List of subdirectories to monitor")
    parser.add_argument("--sub_sub_dir_pattern", required=True, help="Pattern for sub-subdirectories")
    parser.add_argument("--completion_criteria", required=True, help="File pattern indicating completion")
    parser.add_argument("--total_criteria", required=True, help="File pattern to calculate total simulations")
    parser.add_argument("--ongoing_criteria", required=True, help="File pattern for ongoing check")
    parser.add_argument("--error_criteria", required=True, help="File pattern to check for errors")
    parser.add_argument("--interval", type=int, default=300, help="Interval between checks in seconds")
    args = parser.parse_args()
 
    monitor_simulations(args.root_path, args.sub_dirs, args.sub_sub_dir_pattern, args.completion_criteria, args.total_criteria, args.ongoing_criteria, args.error_criteria, args.interval)
 
if __name__ == "__main__":
    main()
 
 
