#!/bin/bash
 
# Specify the log file
LOG_FILE="incre_run.log"
 
# List of paths to process
paths=(
    "/TIER3/DFSD_C651_chamber/Personal/ynie/0-lib_char/2025/Internal/N2_Tanager/3_25c_cworst_T/ttg_0p480v/tcbn02_bwph130pnpnl3p48cpd_base_lvt_c240207_094b/LVF/Char/"
    "/TIER3/DFSD_C651_chamber/Personal/ynie/0-lib_char/2025/Internal/N2_Tanager/3_25c_cworst_T/ttg_0p480v/tcbn02_bwph130pnpnl3p48cpd_base_lvt_c240209_094b/LVF/Char/"
)
# Redirect all output to the log file
exec > >(tee -a "$LOG_FILE") 2>&1
 
# Call the Python script for each path
for path in "${paths[@]}"; do
    echo "Processing path: $path"
    /usr/local/python/3.9.10/bin/python3 ../../run.py/submit_incr.py "$path"
done
 
 
