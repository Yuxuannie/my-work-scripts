import os
import glob
import time
import logging
import argparse
from datetime import datetime
 
# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('simulation_monitor.log'),
        logging.StreamHandler()
    ]
)
 
def check_simulation_status(corners, types, folder_path):
    """Monitor HSPICE simulation results by checking .mt0 files."""
    status_summary = {
        'total': 0,
        'completed': 0,
        'running': 0,
        'failed': 0,
        'not_started': 0,
        'failed_jobs': []
    }
 
    for corner in corners:
        decks_folder = os.path.join(folder_path, f"{corner}_DECKS", types, "DECKS")
        logging.info(f"\nChecking simulations in {decks_folder}")
 
        # Find all spice folders
        spice_folders = glob.glob(os.path.join(decks_folder, "*"))
 
        for folder in spice_folders:
            if not os.path.isdir(folder):
                continue
 
            status_summary['total'] += 1
 
            # Check for required files
            mc_sim = os.path.join(folder, "mc_sim.sp")
            nominal_sim = os.path.join(folder, "nominal_sim.sp")
            if not (os.path.exists(mc_sim) and os.path.exists(nominal_sim)):
                continue
 
            # Check for .mt0 file
            mt0_file = os.path.join(folder, "mc_sim.mt0")
            err_file = os.path.join(folder, "mc_sim.err")
 
            try:
                # Check if simulation completed successfully (.mt0 exists)
                if os.path.exists(mt0_file):
                    status_summary['completed'] += 1
                    continue
 
                # Check for errors
                if os.path.exists(err_file) and os.path.getsize(err_file) > 0:
                    status_summary['failed'] += 1
                    status_summary['failed_jobs'].append({
                        'folder': folder,
                        'error_file': err_file
                    })
 
                    # Log error details
                    with open(err_file, 'r') as f:
                        error_content = f.read()
                        logging.error(f"Error in {folder}:\n{error_content[:500]}...")
                    continue
 
                # Check if job is in bjobs queue
                folder_name = os.path.basename(folder)
                bjobs_check = os.popen(f"bjobs | grep {folder_name}").read()
                if bjobs_check:
                    status_summary['running'] += 1
                else:
                    status_summary['not_started'] += 1
 
            except Exception as e:
                logging.error(f"Error checking folder {folder}: {str(e)}")
 
    return status_summary
 
def print_status_report(status_summary):
    """Print formatted status report."""
    print("\n" + "="*50)
    print("HSPICE Simulation Status Report")
    print(f"Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*50)
 
    total = status_summary['total']
    if total > 0:
        completed_pct = (status_summary['completed'] / total) * 100
        running_pct = (status_summary['running'] / total) * 100
        failed_pct = (status_summary['failed'] / total) * 100
        not_started_pct = (status_summary['not_started'] / total) * 100
 
        print(f"\nTotal Simulations: {total}")
        print(f"Completed (.mt0 found): {status_summary['completed']} ({completed_pct:.1f}%)")
        print(f"Running:               {status_summary['running']} ({running_pct:.1f}%)")
        print(f"Failed:                {status_summary['failed']} ({failed_pct:.1f}%)")
        print(f"Not Started:           {status_summary['not_started']} ({not_started_pct:.1f}%)")
 
        if status_summary['failed'] > 0:
            print("\nFailed Simulations:")
            for job in status_summary['failed_jobs']:
                print(f"- {job['folder']}")
 
    print("="*50 + "\n")
 
def monitor_simulations(corners, types, folder_path, interval=300):
    """Continuous monitoring of simulation status."""
    try:
        while True:
            status_summary = check_simulation_status(corners, types, folder_path)
            print_status_report(status_summary)
 
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
    parser = argparse.ArgumentParser(description="Monitor HSPICE simulations")
    parser.add_argument("--corners", nargs='+', required=True, help="List of corners to monitor")
    parser.add_argument("--types", required=True, help="Type of simulation (e.g., 'delay', 'hold')")
    parser.add_argument("--folder_path", required=True, help="Base path to the simulation folders")
    args = parser.parse_args()
 
    monitor_simulations(args.corners, args.types, args.folder_path, interval=300)
 
if __name__ == "__main__":
    main()
 
