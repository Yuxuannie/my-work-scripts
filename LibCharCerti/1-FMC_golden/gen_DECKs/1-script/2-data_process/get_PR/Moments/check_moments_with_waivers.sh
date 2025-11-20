#!/bin/bash

# Enhanced Moments Check Script with Unified Waiver System
# Implements unified pass/fail system with structured waivers
# Generates 3 pass rates: Base, +Waiver1 (CI), +Optimistic After Waiver1

# Set parameters
set base_dir = "/SIM/DFDS_20211231/Personal/ynie/3-LibCharCerti/2024/N2P"
### CDNS
#combined_data_root_path="/SIM/DFDS_20211231/Personal/ynie/3-LibCharCerti/2024/N2P/7-final_results/1-CDNS/R1/moments"

### SNPS
combined_data_root_path="/SIM/DFDS_20211231/Personal/ynie/3-LibCharCerti/2024/N2P/7-final_results/2-SNPS/R4/moments"

corners=("ssgnp_0p450v_m40c" "ssgnp_0p465v_m40c" "ssgnp_0p480v_m40c" "ssgnp_0p495v_m40c")
#corners=("ssgnp_0p450v_m40c")
types=("delay" "slew")

# Create a timestamp for logging
timestamp=$(date +"%Y%m%d_%H%M%S")
run_dir=$(dirname "$combined_data_root_path")
log_dir="$run_dir/logs"

# Create log directory if it doesn't exist
mkdir -p "$log_dir"
main_log="$log_dir/run_moments_waiver_${timestamp}.log"

# Export variables so they can be used by other scripts
export combined_data_root_path
export corners
export types
export timestamp
export log_dir

# Print confirmation and log it
{
    echo "=========================================================="
    echo "Starting MOMENTS CHECK WITH UNIFIED WAIVER SYSTEM at $(date)"
    echo "=========================================================="
    echo "New Features:"
    echo "  [OK] Unified pass/fail system with structured waivers"
    echo "  [OK] 3 pass rate types: Base, +Waiver1 (CI), +Optimistic After Waiver1"
    echo "  [OK] Optimistic vs pessimistic error analysis"
    echo "  [OK] CI enlargement waiver (6%)"
    echo "  [OK] Pessimistic failures waived AFTER Waiver1"
    echo "  [OK] Combined sigma+moments pivot heatmap visualization"
    echo "  [OK] ORIGINAL LOGIC PRESERVED - Adding waiver features on top"
    echo "=========================================================="
    echo "Parameters set:"
    echo "Root path: $combined_data_root_path"
    echo "Corners: ${corners[*]}"
    echo "Types: ${types[*]}"
    echo "Log directory: $log_dir"
    echo "Main log file: $main_log"
    echo "=========================================================="

    # Check if the root path exists
    if [ ! -d "$combined_data_root_path" ]; then
        echo "ERROR: Root path does not exist: $combined_data_root_path"
        exit 1
    fi

    # Check for RPT files
    echo "Checking for input files with pattern: 'MC*{corner}*{type}*.rpt':"
    rpt_files_found=0

    for corner in "${corners[@]}"; do
        for type in "${types[@]}"; do
            # Use find with wildcard matching - note the pattern allows type in the middle
            matching_files=$(find "$combined_data_root_path" -maxdepth 1 -type f -name "MC*${corner}*${type}*.rpt" | wc -l)

            if [ "$matching_files" -gt 0 ]; then
                echo "  FOUND: $matching_files file(s) matching MC*${corner}*${type}*.rpt"
                find "$combined_data_root_path" -maxdepth 1 -type f -name "MC*${corner}*${type}*.rpt" | while read -r file; do
                    echo "    - $(basename "$file")"
                done
                rpt_files_found=$((rpt_files_found + matching_files))
            else
                echo "  MISSING: No files matching MC*${corner}*${type}*.rpt"
            fi
        done
    done

    echo "Total RPT files found: $rpt_files_found"
    echo "=========================================================="

    if [ "$rpt_files_found" -eq 0 ]; then
        echo "ERROR: No matching RPT files found in $combined_data_root_path"
        exit 1
    fi

    echo "Calling MOMENTS WAIVER Python script..."
    # Call the Python script with proper error handling
    if /usr/local/python/3.9.10/bin/python3 check_moments_with_waivers.py; then
        echo "Moments waiver Python script execution completed successfully."
        echo "=========================================================="

        # Check if waiver output files were generated
        if [ -f "$combined_data_root_path/moments_PR_table_with_waivers.csv" ]; then
            echo "[OK] moments_PR_table_with_waivers.csv generated successfully"
            echo "  File size: $(du -h "$combined_data_root_path/moments_PR_table_with_waivers.csv" | cut -f1)"
            echo "  Preview of waiver table (3 pass rates):"
            head -5 "$combined_data_root_path/moments_PR_table_with_waivers.csv"
            echo "=========================================================="
        else
            echo "[WARNING] moments_PR_table_with_waivers.csv was not generated"
        fi

        # Check for waiver summary files
        if [ -f "$combined_data_root_path/moments_waiver_summary_table.txt" ]; then
            echo "[OK] moments_waiver_summary_table.txt generated successfully"
            echo "  This file contains 3 pass rate types for all parameters"
        fi

        # Check for combined visualization
        echo ""
        echo "Generated combined sigma+moments visualization:"
        if [ -f "$combined_data_root_path/combined_sigma_moments_visualization.png" ]; then
            echo "[OK] combined_sigma_moments_visualization.png generated successfully"
            echo "  Combined pivot heatmap showing sigma + moments together"
            echo "  Parameters as columns, corners as rows"
        else
            echo "[INFO] combined_sigma_moments_visualization.png not found"
            echo "  This requires sigma_PR_table_with_waivers.csv to be present"
        fi

        # List all generated files
        echo ""
        echo "Generated moments waiver output files:"
        ls -la "$combined_data_root_path"/*moments*waiver* 2>/dev/null || echo "No moments waiver output files found"

    else
        echo "ERROR: Moments waiver Python script execution failed with status code $?"
        exit 1
    fi

    echo "=========================================================="
    echo "Moments waiver check script completed at $(date)"
    echo "=========================================================="
    echo ""
    echo "Summary of MOMENTS WAIVER SYSTEM outputs:"
    echo ""
    echo "TABLES (3 Pass Rates):"
    echo "  - moments_PR_table_with_waivers.csv: New waiver table with 3 pass rates"
    echo "  - moments_waiver_summary_table.txt: Human-readable summary"
    echo ""
    echo "VISUALIZATIONS (COMBINED SIGMA+MOMENTS):"
    echo "  - combined_sigma_moments_visualization.png: Pivot heatmap with all parameters"
    echo "    * Parameters (Early_Sigma, Late_Sigma, Meanshift, Std, Skew) as columns"
    echo "    * Corners as rows"
    echo "    * Color-coded: Blue (sigma), Green (moments)"
    echo ""
    echo "ANALYSIS:"
    echo "  - *_moments_check_with_waivers.csv: Individual corner/type results with waiver columns"
    echo ""
    echo "KEY FEATURES (UNIFIED WAIVER SYSTEM):"
    echo "  [OK] Base Pass = (rel_pass OR abs_pass) - NO CI bounds in base"
    echo "  [OK] Waiver 1: CI enlargement (6%)"
    echo "  [OK] Waiver 2: Focus on optimistic errors - pessimistic failures waived"
    echo "  [OK] 3 pass rates: Base, +Waiver1 (CI), +Optimistic After Waiver1"
    echo "  [OK] Combined sigma+moments pivot heatmap visualization"
    echo "  [OK] Integrates with sigma_PR_table_with_waivers.csv"
    echo "  [OK] ORIGINAL LOGIC PRESERVED - Waiver system added on top"
    echo "  [OK] 1-digit precision throughout"
    echo ""
    echo "Thresholds (preserved from original):"
    echo "  - Delay: Meanshift<=1%, Std<=2%, Skew<=5%, abs<=max(0.005*slew, 1ps)"
    echo "  - Slew: Meanshift<=2%, Std<=4%, Skew<=10%, abs<=max(0.005*slew, 2ps)"
    echo ""
    echo "Next steps:"
    echo "  1. Review combined_sigma_moments_visualization.png (unified view)"
    echo "  2. Analyze pessimistic failures (waived in final PR)"
    echo "  3. Use moments_PR_table_with_waivers.csv for detailed analysis"
    echo "  4. Ensure sigma script ran first for combined visualization"
    echo "=========================================================="
} 2>&1 | tee "$main_log"

echo "Moments waiver log file saved to: $main_log"