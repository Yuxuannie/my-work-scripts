import os
import sys
import glob
import subprocess
 
def log(message):
    """Log a message to the console and to a log file."""
    with open("process_log.txt", "a") as log_file:
        log_file.write(message + "\n")
    print(message)
 
def process_path(char_dir):
    """Process each directory to find and modify files."""
    try:
        # Add a divider for the log
        log("\n" + "="*50)
        log(f"Processing directory: {char_dir}")
        log("="*50 + "\n")
 
        # Search for the altos*ldb.gz file
        ldb_files = glob.glob(os.path.join(char_dir, "altos*ldb.gz"))
        if len(ldb_files) != 1:
            log(f"Skipping {char_dir} due to {len(ldb_files)} altos*ldb.gz files found.")
            return
 
        ldb_gz_path = ldb_files[0]
        log(f"Found ldb file: {ldb_gz_path}")
 
        # Modify char*tcl files
        for tcl_file in glob.glob(os.path.join(char_dir, "char*tcl")):
            log(f"Modifying {tcl_file}")
            with open(tcl_file, 'r') as file:
                lines = file.readlines()
           
            # Remove the first line if it starts with "read_ldb"
            if lines and lines[0].startswith("read_ldb"):
                log(f"Removing existing read_ldb line from {tcl_file}")
                lines.pop(0)
 
            # Insert the new read_ldb line
            lines.insert(0, f"read_ldb {ldb_gz_path}\n")
 
            with open(tcl_file, 'w') as file:
                file.writelines(lines)
 
        # Submit the run.scr file using bsub
        run_scr_path = os.path.join(char_dir, "run.scr")
        if os.path.exists(run_scr_path):
            log(f"Submitting {run_scr_path} using bsub")
            subprocess.run(["bsub", run_scr_path], cwd=char_dir)
        else:
            log(f"run.scr not found in {char_dir}")
 
    except Exception as e:
        log(f"Error processing {char_dir}: {e}")
 
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python process_files.py <path_to_process>")
        sys.exit(1)
 
    char_dir = sys.argv[1]
    process_path(char_dir)
 
 
