#!/bin/bash
 
# Working path
working_path="/SIM/DFDS_20211231/Personal/ynie/3-LibCharCerti/2025/N2P_v1.0/2-select_2nd_round/2-Full_MC_golden/"
#corners=("ssgnp_0p450v_m40c" "ssgnp_0p465v_m40c" "ssgnp_0p480v_m40c" "ssgnp_0p495v_m40c")
corners=("ssgnp_0p465v_m40c")
 
# Log file
log_file="summary_csv_report_full_mc.log"
 
# Arrays to store summary counts
corner_names=()
total_simulations_counts=()
completed_counts=()
not_completed_counts=()
non_completed_paths=()
 
# Start logging
echo "Summary CSV Report for Full_MC" > "$log_file"
echo "==========================================================================================" >> "$log_file"
 
for corner in "${corners[@]}"; do
    echo "Processing corner: $corner" | tee -a "$log_file"
   
    total_simulations=0
    completed=0
    not_completed=0
 
    search_path="${working_path}/${corner}/"
    # Debug: Print the constructed search path
    echo "Constructed search path: $search_path" | tee -a "$log_file"
 
    # Check if directory exists
    if [ ! -d "$search_path" ]; then
        echo "Directory $search_path does not exist!" | tee -a "$log_file"
        echo "-----------------------------------------------------------------------------------------------------" | tee -a "$log_file"
        corner_names+=("$corner")
        total_simulations_counts+=("0")
        completed_counts+=("0")
        not_completed_counts+=("0")
        continue
    fi
 
    # Find all immediate subdirectories
    all_folders=$(find "$search_path" -maxdepth 1 -type d)
 
    for folder in $all_folders; do
        if [ "$folder" != "$search_path" ]; then
            total_simulations=$((total_simulations + 1))
           
            # Check for the presence of *.csv files
            csv_count=$(find "$folder" -maxdepth 1 -type f -name "*.csv" | wc -l)
            if [ "$csv_count" -gt 0 ]; then
                completed=$((completed + 1))
            else
                # Add the folder to the non-completed list
                non_completed_paths+=("$folder")
                not_completed=$((not_completed + 1))
            fi
        fi
    done
 
    # Calculate percentages (if needed, not used in the summary table below)
    completed_percent=0
    not_completed_percent=0
 
    if [ "$total_simulations" -gt 0 ]; then
        completed_percent=$((100 * completed / total_simulations))
        not_completed_percent=$((100 * not_completed / total_simulations))
    fi
 
    # Log the summary for the corner
    echo "Summary for $corner:" | tee -a "$log_file"
    echo "Total Simulations: $total_simulations" | tee -a "$log_file"
    echo "Completed (*.csv files found): $completed ($completed_percent%)" | tee -a "$log_file"
    echo "Not Completed (*.csv files missing): $not_completed ($not_completed_percent%)" | tee -a "$log_file"
    echo "---------------------------------------" | tee -a "$log_file"
 
    # Add counts to summary arrays
    corner_names+=("$corner")
    total_simulations_counts+=("$total_simulations")
    completed_counts+=("$completed")
    not_completed_counts+=("$not_completed")
done
 
# Print summary table
echo "Summary Table:" | tee -a "$log_file"
echo "==========================================================================================" | tee -a "$log_file"
printf "%-25s %-20s %-20s %-20s\n" "Corner" "Total Simulations" "Completed" "Not Completed" | tee -a "$log_file"
echo "==========================================================================================" | tee -a "$log_file"
 
for i in "${!corner_names[@]}"; do
    printf "%-25s %-20d %-20d %-20d\n" "${corner_names[$i]}" "${total_simulations_counts[$i]}" "${completed_counts[$i]}" "${not_completed_counts[$i]}" | tee -a "$log_file"
done
echo "==========================================================================================" | tee -a "$log_file"
 
# Print non-completed paths
echo "Paths for non-completed simulations:" | tee -a "$log_file"
echo "==========================================================================================" | tee -a "$log_file"
for path in "${non_completed_paths[@]}"; do
    echo "$path" | tee -a "$log_file"
done
echo "==========================================================================================" | tee -a "$log_file"
 
