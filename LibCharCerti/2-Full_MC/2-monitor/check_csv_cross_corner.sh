#!/bin/bash
 
# Working path
working_path="/SIM/DFDS_20211231/Personal/ynie/3-LibCharCerti/2025/N2P_v1.0/2-select_2nd_round/2-Full_MC_golden/"
#corners=("ssgnp_0p450v_m40c" "ssgnp_0p465v_m40c" "ssgnp_0p480v_m40c" "ssgnp_0p495v_m40c")
corners=("ssgnp_0p450v_m40c" "ssgnp_0p465v_m40c")
 
# Log file
log_file="cross_corner_csv_check.log"
 
# Start logging
echo "Cross-Corner CSV File Check" > "$log_file"
echo "==========================================================================================" >> "$log_file"
 
# Collect all subdirectories (arcs) for the first corner
first_corner_path="${working_path}/${corners[0]}"
if [ ! -d "$first_corner_path" ]; then
    echo "First corner directory $first_corner_path does not exist! Exiting..." | tee -a "$log_file"
    exit 1
fi
 
# Find all subdirectories (arcs) in the first corner
arcs=($(find "$first_corner_path" -maxdepth 1 -type d -printf "%f\n" | tail -n +2))
 
# Initialize counters and lists
total_arcs=${#arcs[@]}
csv_exists_in_all=0
csv_arcs_paths=()
 
echo "Total Arcs Found: $total_arcs" | tee -a "$log_file"
echo "==========================================================================================" | tee -a "$log_file"
 
# Loop through each arc and check across all corners
for arc in "${arcs[@]}"; do
    echo "Checking arc: $arc" | tee -a "$log_file"
    csv_found_in_all=true
    arc_paths=()
 
    # Loop through each corner
    for corner in "${corners[@]}"; do
        arc_path="${working_path}/${corner}/${arc}"
        if [ ! -d "$arc_path" ]; then
            echo "Arc directory $arc_path does not exist in corner $corner!" | tee -a "$log_file"
            csv_found_in_all=false
            break
        fi
 
        # Check for *.csv files in the arc directory
        csv_count=$(find "$arc_path" -maxdepth 1 -type f -name "*.csv" | wc -l)
        if [ "$csv_count" -eq 0 ]; then
            echo "No CSV file found in $arc_path" | tee -a "$log_file"
            csv_found_in_all=false
            break
        fi
 
        # Collect the valid path
        arc_paths+=("$arc_path")
    done
 
    # Update counters and logs based on results
    if [ "$csv_found_in_all" = true ]; then
        csv_exists_in_all=$((csv_exists_in_all + 1))
        csv_arcs_paths+=("${arc_paths[@]}")
    fi
done
 
# Log summary
echo "==========================================================================================" | tee -a "$log_file"
echo "Summary of Cross-Corner CSV Check:" | tee -a "$log_file"
echo "Total Arcs: $total_arcs" | tee -a "$log_file"
echo "Arcs with CSV files in all corners: $csv_exists_in_all" | tee -a "$log_file"
 
# Log paths of arcs having *.csv files in all corners
if [ "$csv_exists_in_all" -gt 0 ]; then
    echo "==========================================================================================" | tee -a "$log_file"
    echo "Paths of arcs having CSV files in all corners:" | tee -a "$log_file"
    for arc_path in "${csv_arcs_paths[@]}"; do
        echo "$arc_path" | tee -a "$log_file"
    done
fi
echo "==========================================================================================" | tee -a "$log_file"
 
