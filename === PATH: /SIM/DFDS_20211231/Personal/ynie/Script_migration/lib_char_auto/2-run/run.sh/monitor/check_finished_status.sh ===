#!/bin/bash
 
# Input file containing the original list of paths
INPUT_FILE="paths.txt"
 
# Output file for the cleaned paths
CLEANED_FILE="cleaned_paths.txt"
 
# Python script to clean and process paths
PYTHON_SCRIPT="../../run.py/extract_finished.py"
 
# Log file for the shell script
LOG_FILE="Check_ongoing_status.log"
 
# Clear previous log and cleaned files
> "$LOG_FILE"
> "$CLEANED_FILE"
 
# Check if the input file exists
if [[ ! -f "$INPUT_FILE" ]]; then
    echo "Input file '$INPUT_FILE' not found!" | tee -a "$LOG_FILE"
    exit 1
fi
 
# Run the Python script with the input file, cleaned paths file, and log file
/usr/local/python/3.9.10/bin/python3 "$PYTHON_SCRIPT" "$INPUT_FILE" "$CLEANED_FILE" "$LOG_FILE"
 
 
