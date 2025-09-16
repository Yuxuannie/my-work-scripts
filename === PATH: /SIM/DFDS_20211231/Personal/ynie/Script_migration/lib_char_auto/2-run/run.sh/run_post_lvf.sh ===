#!/bin/bash

 # -----------------------------------------------------
# Source License & LSF
# -----------------------------------------------------
source ./source_license_lsf.sh
 
# -----------------------------------------------------
# Configuration
# -----------------------------------------------------
 
PYTHON_PATH="/usr/local/python/3.9.10/bin/python3.9"
MAIN_SCRIPT="../run.py/postprocess/post_process_lvf.py"
LOG_FILE="3-post_lvf.log"
#WORK_DIR="/TIER3/DFSD_C651_chamber/Personal/ynie/0-lib_char/2025/Internal/N2_Tanager/2_25c_typical/ttg_0p480v"
WORK_DIR="/TIER3/DFSD_C651_chamber/Personal/ynie/0-lib_char/2025/Internal/N2_Tanager/3_25c_cworst_T/ttg_0p480v"
DIRS=(
# 0p480v_cworst_T & 0p480v_typical
"tcbn02_bwph130nppnl3p48cpd_base_lvt_c240207_094b"
"tcbn02_bwph130nppnl3p48cpd_base_lvtll_c240207_094b"
"tcbn02_bwph130nppnl3p48cpd_base_svt_c240207_094b"
"tcbn02_bwph130pnnpl3p48cpd_base_lvt_c240207_094b"
"tcbn02_bwph130pnnpl3p48cpd_base_lvtll_c240207_094b"
"tcbn02_bwph130pnnpl3p48cpd_base_svt_c240207_094b"
"tcbn02_bwph130pnpnl3p48cpd_base_lvt_c240207_094b"
"tcbn02_bwph130pnpnl3p48cpd_base_lvtll_c240207_094b"
"tcbn02_bwph130pnpnl3p48cpd_base_svt_c240207_094b"
"tcbn02_bwph130nppnl3p48cpd_base_lvt_c240209_094b"
"tcbn02_bwph130nppnl3p48cpd_base_lvtll_c240209_094b"
"tcbn02_bwph130nppnl3p48cpd_base_svt_c240209_094b"
"tcbn02_bwph130pnnpl3p48cpd_base_lvt_c240209_094b"
"tcbn02_bwph130pnnpl3p48cpd_base_lvtll_c240209_094b"
"tcbn02_bwph130pnnpl3p48cpd_base_svt_c240209_094b"
"tcbn02_bwph130pnpnl3p48cpd_base_lvt_c240209_094b"
"tcbn02_bwph130pnpnl3p48cpd_base_lvtll_c240209_094b"
"tcbn02_bwph130pnpnl3p48cpd_base_svt_c240209_094b"
"tcbn02_bwph130pnpnl3p48cpd_mb_lvt_c240207_094b"
"tcbn02_bwph130pnpnl3p48cpd_mb_lvtll_c240207_094b"
"tcbn02_bwph130pnpnl3p48cpd_mb_lvt_c240209_094b"
"tcbn02_bwph130pnpnl3p48cpd_mb_lvtll_c240209_094b"

 
# 0p445v_25c_cworst_T & typical
#"tcbn02_bwph130nppnl3p48cpd_base_svt_c230828_094b"
#"tcbn02_bwph130pnnpl3p48cpd_base_svt_c230828_094b"
#"tcbn02_bwph130pnpnl3p48cpd_base_svt_c230828_094b"
)
 
PVT_CORNERS=(
    "ttg_0p480v_25c_cworst_T"
#    "ttg_0p480v_25c_typical"
#    "ttg_0p445v_25c_cworst_T"
#    "ttg_0p445v_25c_typical"
)
 
USE_REPLACE=false
MERGE=false
 
# -----------------------------------------------------
# Run Post LVF Processing Step
# -----------------------------------------------------
 
echo "Running post LVF processing step..."
$PYTHON_PATH $MAIN_SCRIPT  --work_dir  "$WORK_DIR" \
    --dirs "${DIRS[@]}" \
    --pvt_corners "${PVT_CORNERS[@]}" \
    --log_file "$LOG_FILE"
 
if [ ${PIPESTATUS[0]} -ne 0 ]; then
    echo "Error: Post LVF processing step failed. Check the log file for details." | tee -a $LOG_FILE
    exit 1
fi
 
echo "Post LVF processing step completed successfully."
 
 
 
