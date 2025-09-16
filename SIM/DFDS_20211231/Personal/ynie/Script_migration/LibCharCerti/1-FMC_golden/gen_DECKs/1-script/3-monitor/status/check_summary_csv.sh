#!/bin/bash
 
working_path="/SIM/DFDS_20211231/Personal/ynie/3-LibCharCerti/2025/N2P_v1.0/2-select_2nd_round/1-FMC_golden/gen_DECKs/"
corners=("ssgnp_0p450v_m40c" "ssgnp_0p465v_m40c" "ssgnp_0p480v_m40c" "ssgnp_0p495v_m40c")
#types=("delay"  "hold" "mpw")
types=("mpw-100k")
 
# Log file
log_file="summary_csv_report.log"
 
# Arrays to store summary counts
corner_names=()
type_names=()
total_simulations_counts=()
completed_counts=()
multiple_runs_counts=()
running_counts=()
not_started_counts=()
non_completed_paths=()
 
# Start logging
echo "Summary CSV Report" > "$log_file"
echo "==========================================================================================" >> "$log_file"
 
for corner in "${corners[@]}"; do
    for type in "${types[@]}"; do
        echo "Processing corner: $corner, type: $type" | tee -a "$log_file"
       
        total_simulations=0
        completed=0
        multiple_runs=0
        running=0
        not_started=0
 
        search_path="${working_path}/${corner}_DECKS/${type}/DECKS/"
        # Debug: Print the constructed search path
        echo "Constructed search path: $search_path" | tee -a "$log_file"
 
        # Check if directory exists
        if [ ! -d "$search_path" ]; then
            echo "Directory $search_path does not exist!" | tee -a "$log_file"
            echo "-----------------------------------------------------------------------------------------------------" | tee -a "$log_file"
            corner_names+=("$corner")
            type_names+=("$type")
            total_simulations_counts+=("0")
            completed_counts+=("0")
            multiple_runs_counts+=("0")
            running_counts+=("0")
            not_started_counts+=("0")
            continue
        fi
 
        # Find all immediate subdirectories
        all_folders=$(find "$search_path" -maxdepth 1 -type d)
 
        for folder in $all_folders; do
            if [ "$folder" != "$search_path" ]; then
                total_simulations=$((total_simulations + 1))
               
                if [ "$type" == "delay" ]; then
                    # Custom logic for "delay"
                    lis_file_count=$(find "$folder" -maxdepth 1 -type f -name "*.lis" | wc -l)
                    mt0_file_count=$(find "$folder" -maxdepth 1 -type f -name "*.mt0" | wc -l)
                   
                    if [ "$lis_file_count" -gt 0 ] && [ "$mt0_file_count" -gt 0 ]; then
                        # Mark as completed if both `*.lis` and `*.mt0` files exist
                        completed=$((completed + 1))
                    else
                        # Add the folder to the non-completed list
                        non_completed_paths+=("$folder")
                        if [ -f "$folder/fastmontecarlo.log" ]; then
                            running=$((running + 1))
                        else
                            not_started=$((not_started + 1))
                        fi
                    fi
                else
                    # Default logic for other types
                    csv_count=$(find "$folder" -maxdepth 1 -type f -name "summary*.csv" | wc -l)
                    if [ "$csv_count" -gt 0 ]; then
                        completed=$((completed + 1))
                        if [ "$csv_count" -gt 1 ]; then
                            multiple_runs=$((multiple_runs + 1))
                        fi
                    else
                        # Add the folder to the non-completed list
                        non_completed_paths+=("$folder")
                        # Check for the presence of fastmontecarlo.log
                        if [ -f "$folder/fastmontecarlo.log" ]; then
                            running=$((running + 1))
                        else
                            not_started=$((not_started + 1))
                        fi
                    fi
                fi
            fi
        done
 
        # Calculate percentages (if needed, not used in the summary table below)
        completed_percent=0
        multiple_runs_percent=0
        running_percent=0
        not_started_percent=0
 
        if [ "$total_simulations" -gt 0 ]; then
            completed_percent=$((100 * completed / total_simulations))
            multiple_runs_percent=$((100 * multiple_runs / total_simulations))
            running_percent=$((100 * running / total_simulations))
            not_started_percent=$((100 * not_started / total_simulations))
        fi
 
        # Log the summary for the corner and type
        echo "Summary for $corner, type: $type" | tee -a "$log_file"
        echo "Total Simulations: $total_simulations" | tee -a "$log_file"
        echo "Completed (summary*.csv or required files found): $completed ($completed_percent%)" | tee -a "$log_file"
        echo "Multiple runs (multiple summary*.csv found): $multiple_runs ($multiple_runs_percent%)" | tee -a "$log_file"
        echo "Running (fastmontecarlo.log present, required files missing): $running ($running_percent%)" | tee -a "$log_file"
        echo "Not Started (neither required files nor fastmontecarlo.log found): $not_started ($not_started_percent%)" | tee -a "$log_file"
        echo "---------------------------------------" | tee -a "$log_file"
 
        # Add counts to summary arrays
        corner_names+=("$corner")
        type_names+=("$type")
        total_simulations_counts+=("$total_simulations")
        completed_counts+=("$completed")
        multiple_runs_counts+=("$multiple_runs")
        running_counts+=("$running")
        not_started_counts+=("$not_started")
    done
done
 
# Print summary table
echo "Summary Table:" | tee -a "$log_file"
echo "==========================================================================================" | tee -a "$log_file"
printf "%-25s %-10s %-20s %-20s %-20s %-20s %-20s\n" "Corner" "Type" "Total Simulations" "Completed" "Multiple Runs" "Running" "Not Started" | tee -a "$log_file"
echo "==========================================================================================" | tee -a "$log_file"
 
for i in "${!corner_names[@]}"; do
    printf "%-25s %-10s %-20d %-20d %-20d %-20d %-20d\n" "${corner_names[$i]}" "${type_names[$i]}" "${total_simulations_counts[$i]}" "${completed_counts[$i]}" "${multiple_runs_counts[$i]}" "${running_counts[$i]}" "${not_started_counts[$i]}" | tee -a "$log_file"
done
echo "==========================================================================================" | tee -a "$log_file"
 
# Print non-completed paths
echo "Paths for non-completed simulations:" | tee -a "$log_file"
echo "==========================================================================================" | tee -a "$log_file"
for path in "${non_completed_paths[@]}"; do
    echo "$path" | tee -a "$log_file"
done
echo "==========================================================================================" | tee -a "$log_file"
 
