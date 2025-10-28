# Usage:
# /usr/local/python/3.9.10/bin/python3 change_sample.py . 100 200
# /usr/local/python/3.9.10/bin/python3 change_sample.py . 100 200 --log-level INFO
 
 
#!/usr/bin/env python3
import os, sys, glob, logging, argparse, subprocess
from pathlib import Path
 
def try_remove_file(file_path, debug=False):
    if debug:
        logging.info(f"Debug mode: would remove {file_path}")
        return True
       
    try:
        process = subprocess.run(['rm', '-f', file_path],
                               capture_output=True,
                               text=True)
        if process.returncode == 0:
            return True
        else:
            logging.error(f"rm command failed: {process.stderr}")
            return False
    except Exception as e:
        logging.error(f"Error removing {file_path}: {str(e)}")
        return False
 
def process_files(directory, old_sample_num, new_sample_num, debug=False):
    logging.info(f"Processing directory: {directory}")
   
    # Updated pattern to match ssgnp*/*/DECKS/
    patterns = [
        os.path.join(directory, "ssgnp*", "hold", "DECKS"),
#        os.path.join(directory, "ssgnp*", "delay", "DECKS")
    ]
   
    files_removed = 0
    files_modified = 0
    failed_removals = []
 
    for pattern in patterns:
        deck_dirs = glob.glob(pattern)
        logging.info(f"Found {len(deck_dirs)} directories matching pattern: {pattern}")
       
        for deck_dir in deck_dirs:
            logging.info(f"\nProcessing DECKS directory: {deck_dir}")
           
            # Walk through all subdirectories under DECKS
            for root, _, files in os.walk(deck_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    if not file_path.endswith('.sp'):
                        try:
                            stat_info = os.stat(file_path)
                            logging.info(f"Attempting to remove: {file_path}")
                            logging.debug(f"Current permissions: {oct(stat_info.st_mode)}")
                           
                            if try_remove_file(file_path, debug):
                                files_removed += 1
                                logging.info(f"Successfully removed: {file_path}")
                            else:
                                failed_removals.append(file_path)
                                logging.error(f"Failed to remove: {file_path}")
                        except Exception as e:
                            failed_removals.append(file_path)
                            logging.error(f"Error processing {file_path}: {str(e)}")
 
            # Process .sp files
            sp_files = glob.glob(os.path.join(deck_dir, "**", "*.sp"), recursive=True)
            for sp_file in sp_files:
                try:
                    with open(sp_file, 'r') as f:
                        content = f.read()
                   
                    original_content = content
                    content = content.replace(f"sweep monte={old_sample_num} monte={old_sample_num}",
                                          f"sweep monte={new_sample_num}")
                    content = content.replace(f"sweep monte={old_sample_num}",
                                          f"sweep monte={new_sample_num}")
                   
                    if content != original_content and not debug:
                        with open(sp_file, 'w') as f:
                            f.write(content)
                        files_modified += 1
                        logging.info(f"Modified: {sp_file}")
                except Exception as e:
                    logging.error(f"Error processing {sp_file}: {str(e)}")
 
    return files_removed, files_modified, failed_removals
 
def main():
    parser = argparse.ArgumentParser(description='Process SPICE files')
    parser.add_argument('directory', help='Directory to process')
    parser.add_argument('old_sample_num', type=int, help='Original monte sweep number')
    parser.add_argument('new_sample_num', type=int, help='New monte sweep number')
    parser.add_argument('--debug', action='store_true',
                       help='Run without file modifications')
    parser.add_argument('--log-level', default='INFO',
                       choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'])
 
    args = parser.parse_args()
    logging.basicConfig(level=getattr(logging, args.log_level),
                       format='%(asctime)s - %(levelname)s - %(message)s',
                       handlers=[logging.FileHandler('file_processing.log'),
                                logging.StreamHandler()])
 
    if not os.path.isdir(args.directory):
        sys.exit(f"Error: Directory '{args.directory}' does not exist")
 
    try:
        files_removed, files_modified, failed_removals = process_files(
            args.directory, args.old_sample_num, args.new_sample_num, args.debug)
       
        logging.info("\nExecution Summary:")
        logging.info(f"Files attempted to remove: {files_removed + len(failed_removals)}")
        logging.info(f"Successfully removed: {files_removed}")
        logging.info(f"Failed to remove: {len(failed_removals)}")
        logging.info(f"SP files modified: {files_modified}")
       
        if failed_removals:
            logging.error("\nFailed to remove these files:")
            for file in failed_removals:
                logging.error(f"  {file}")
           
            logging.info("\nSince you don't have sudo permissions, you might need to:")
            logging.info("1. Contact your system administrator")
            logging.info("2. Request write permissions for these directories")
            logging.info("3. Or ask them to remove these files for you")
            sys.exit(1)
           
    except Exception as e:
        logging.error(f"Script failed: {str(e)}")
        sys.exit(1)
 
if __name__ == "__main__":
    main()
 
 
