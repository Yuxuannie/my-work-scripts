#!/bin/bash
 
# Define the root path and subdirectories to search
root_path="/TIER3/DFSD_C651_chamber/Personal/ynie/0-lib_char/2025/Internal/N2_Tanager"
sub_dirs=("2_25c_typical/ttg_0p480v/" "3_25c_cworst_T/ttg_0p480v/" "2_25c_typical/ttg_0p445v/" "3_25c_cworst_T/ttg_0p445v/")
sub_sub_dir_pattern="tcb*/LVF/Char"
 
# Define the criteria for monitoring
completion_criteria="tcb*.lib"
total_criteria="char*.tcl"
ongoing_criteria="char*.log"
error_criteria="char*.log"
 
# Interval between checks in seconds
interval=300
 
# Convert sub_dirs array to a space-separated string
sub_dirs_string=$(IFS=' '; echo "${sub_dirs[*]}")
 
# Call the Python script with the specified arguments
/usr/local/python/3.9.10/bin/python3 ../../run.py/monitor.py \
    --root_path "$root_path" \
    --sub_dirs $sub_dirs_string \
    --sub_sub_dir_pattern "$sub_sub_dir_pattern" \
    --completion_criteria "$completion_criteria" \
    --total_criteria "$total_criteria" \
    --ongoing_criteria "$ongoing_criteria" \
    --error_criteria "$error_criteria" \
    --interval $interval
 
 
