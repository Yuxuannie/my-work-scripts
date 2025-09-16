#!/bin/bash
 
# Set the base path
BASE_PATH="/SIM/DFDS_20211231/Personal/ynie/0-lib_char/2025/External/sens_char/Primelib/1-baseline_updated_0624_2025/to_TSMC_20250619_nom_ocv_sens_package/"
 
# Define the subdirectories
SUB_DIRS=(
    "tcbn02_bwph130nppnl3p48cpd_base_elvt_ssgnp_0p800v_m25c_cworst_t_hm_lvf_p_ccs"
 
# Define the log file path
LOG_FILE="$(dirname $0)/replacements.log"
 
# Run the Python script with the base path, log file, and subdirectories as arguments
/usr/local/python/3.9.10/bin/python3 replace_strings.py "$BASE_PATH" "$LOG_FILE" "${SUB_DIRS[@]}"
 
