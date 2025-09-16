import os
import logging
import glob
import shutil
 
# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
 
 
def read_simulation_paths(file_path):
    """Read simulation paths from a file."""
    with open(file_path, 'r') as file:
        lines = file.readlines()
   
    paths = []
    for line in lines:
        # Check and split the line only if it contains ' - '
        if ' - ' in line:
            # Split by ' - ' and take the last part
            potential_path = line.strip().split(' - ')[-1]
            # Ensure no leading '-' and add to paths
            if potential_path.startswith('- '):
                potential_path = potential_path[2:]  # Remove the leading '- '
            paths.append(potential_path)
   
    # Log the extracted paths
    #logging.info("Extracted root paths: {}".format(paths))
   
    return paths
 
def clean_directory(simulation_paths, dry_run=True):
    """Log directories to be cleaned and optionally perform the cleaning."""
    for path in simulation_paths:
        altos_path = os.path.join(path, "altos*")
        deck_path = os.path.join(path, "deck*")
 
        # Log the directories that will be affected
        logging.info(f"Will attempt to remove directories matching: {altos_path}")
        logging.info(f"Will attempt to remove directories matching: {deck_path}")
 
        # If not in dry run mode, perform the deletion
        if not dry_run:
            for dir_path in [altos_path, deck_path]:
                for dir_to_remove in glob.glob(dir_path):
                    try:
                        shutil.rmtree(dir_to_remove)  # Use shutil.rmtree to remove directories and contents
                        logging.info(f"Removed directory and contents: {dir_to_remove}")
                    except Exception as e:
                        logging.error(f"Error removing {dir_to_remove}: {e}")
 
def main():
    # Paths to input files
    failed_simulations_file = 'failed_simulations.txt'
    not_started_simulations_file = 'not_started_simulations.txt'
 
    # Read the simulation paths from the files
    failed_simulations = read_simulation_paths(failed_simulations_file)
    not_started_simulations = read_simulation_paths(not_started_simulations_file)
 
    # Clean directories (dry run mode)
    logging.info("Starting dry run for failed simulations")
    clean_directory(failed_simulations, dry_run=True)
 
    logging.info("Starting dry run for not started simulations")
    clean_directory(not_started_simulations, dry_run=True)
 
    # Uncomment the lines below to perform the actual deletion
    logging.info("Performing actual deletion for failed simulations")
    clean_directory(failed_simulations, dry_run=False)
 
    # logging.info("Performing actual deletion for not started simulations")
    clean_directory(not_started_simulations, dry_run=False)
 
if __name__ == "__main__":
    main()
 
 
