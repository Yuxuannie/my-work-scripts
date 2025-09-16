#!/bin/bash
 
# Define the current path
current_path="/SIM/DFDS_20211231/Personal/ynie/3-LibCharCerti/2024/N2P/6-final_replay/1-CDNS/Best_ULV/baseline_cons/"
 
# Define the subdirectories
SUB_DIRS=(
    "ssgnp_0p450v_m40c"
#    "ssgnp_0p465v_m40c"
#    "ssgnp_0p480v_m40c"
#    "ssgnp_0p495v_m40c"
)
 
 
# Define the log file path
log_directory="/SIM/DFDS_20211231/Personal/ynie/3-LibCharCerti/2024/N2P/6-final_replay/1-CDNS/scripts/"
log_file="${log_directory}/script_log.txt"
 
# Ensure the log directory exists
mkdir -p "$log_directory"
 
# Create or clear the log file
echo "Log file for move_files.sh script" > "$log_file"
 
# Change to the current path
cd "$current_path"
echo "Changed directory to $current_path" >> "$log_file"
 
# Loop through each specified subdirectory
for sub_dir in "${SUB_DIRS[@]}"; do
    dir="${current_path}/${sub_dir}/"
    echo "Processing directory: $dir" >> "$log_file"
   
    # Create bak directory inside each specified subdirectory if it doesn't exist
    bak_dir="${dir}bak"
    mkdir -p "$bak_dir"
    echo "Created bak directory: $bak_dir" >> "$log_file"
   
    # Move all files except *.tcl, *.inc, and *.csh to the bak folder
    find "$dir" -maxdepth 1 -type f ! -name "*.tcl" ! -name "*.inc" ! -name "*.csh" -exec mv {} "$bak_dir/" \;
    echo "Moved files from $dir to $bak_dir" >> "$log_file"
done
 
# Run the Python script for replacements
/usr/local/python/3.9.10/bin/python3 ${log_directory}/replace_strings.py "$current_path" "$log_file" "${SUB_DIRS[@]}" >> "$log_file" 2>&1
echo "Ran replace_strings.py script" >> "$log_file"
 
