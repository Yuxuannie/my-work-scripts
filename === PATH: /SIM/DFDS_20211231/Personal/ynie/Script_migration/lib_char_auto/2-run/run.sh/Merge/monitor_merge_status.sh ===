#!/bin/bash
 
# Ensure the script exits if any command fails
set -e
 
# Specify the arguments
#TARGET_ROOT_PATH="/TIER3/DFSD_C651_chamber/Personal/ynie/0-lib_char/2025/Internal/N2_Tanager/3_25c_cworst_T"
TARGET_ROOT_PATH="/TIER3/DFSD_C651_chamber/Personal/ynie/0-lib_char/2025/Internal/N2_Tanager/2_25c_typical"
CORNERS="ttg_0p445v ttg_0p480v"
#CORNERS="ttg_0p445v"
#RC_TYPE="cworst_T"
RC_TYPE="typical"
LOG_FILE="monitor_merge_status.log"
 
# Convert corners array to space-separated string
CORNERS_STR=$(printf " %s" "${CORNERS[@]}")
CORNERS_STR=${CORNERS_STR:1}
 
# Run the Python script with the provided arguments
/usr/local/python/3.9.10/bin/python3 ../../run.py/postprocess/monitor_merge_status.py --target_root_path "$TARGET_ROOT_PATH" --corners $CORNERS_STR --rc_type "$RC_TYPE" --log_file "$LOG_FILE"
 
 
