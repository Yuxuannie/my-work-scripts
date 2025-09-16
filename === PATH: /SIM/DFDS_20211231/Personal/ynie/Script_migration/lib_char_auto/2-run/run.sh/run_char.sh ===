#!/bin/bash
 
# -----------------------------------------------------
# Source License & LSF
# -----------------------------------------------------
 
source ./source_license_lsf.sh
 
# -----------------------------------------------------
# Configuration
# -----------------------------------------------------
 
PYTHON_PATH="/usr/local/python/3.9.10/bin/python3.9"
GEN_SCRIPT="../run.py/run_char.py"
LOG_FILE="2-run_char.log"
WORK_DIR="/TIER3/DFSD_C651_chamber/Personal/ynie/0-lib_char/2025/Internal/N2_Tanager/2_25c_typical/ttg_0p480v"
#WORK_DIR="/TIER3/DFSD_C651_chamber/Personal/ynie/0-lib_char/2025/Internal/N2_Tanager/3_25c_cworst_T/ttg_0p445v"
DIRS=(
"tcbn02_bwph130nppnl3p48cpd_base_lvt_c240207_094b"
"tcbn02_bwph130nppnl3p48cpd_base_lvtll_c240207_094b"
"tcbn02_bwph130nppnl3p48cpd_base_svt_c240207_094b"
"tcbn02_bwph130pnnpl3p48cpd_base_lvt_c240207_094b"
"tcbn02_bwph130pnnpl3p48cpd_base_lvtll_c240207_094b"
"tcbn02_bwph130pnnpl3p48cpd_base_svt_c240207_094b"
"tcbn02_bwph130pnpnl3p48cpd_base_lvt_c240207_094b"
"tcbn02_bwph130pnpnl3p48cpd_base_lvtll_c240207_094b"
"tcbn02_bwph130pnpnl3p48cpd_base_svt_c240207_094b"
"tcbn02_bwph130pnpnl3p48cpd_mb_lvt_c240207_094b"
"tcbn02_bwph130pnpnl3p48cpd_mb_lvtll_c240207_094b"
"tcbn02_bwph130nppnl3p48cpd_base_lvt_c240209_094b"
"tcbn02_bwph130nppnl3p48cpd_base_lvtll_c240209_094b"
"tcbn02_bwph130nppnl3p48cpd_base_svt_c240209_094b"
"tcbn02_bwph130pnnpl3p48cpd_base_lvt_c240209_094b"
"tcbn02_bwph130pnnpl3p48cpd_base_lvtll_c240209_094b"
"tcbn02_bwph130pnnpl3p48cpd_base_svt_c240209_094b"
"tcbn02_bwph130pnpnl3p48cpd_base_lvt_c240209_094b"
"tcbn02_bwph130pnpnl3p48cpd_base_lvtll_c240209_094b"
"tcbn02_bwph130pnpnl3p48cpd_base_svt_c240209_094b"
"tcbn02_bwph130pnpnl3p48cpd_mb_lvt_c240209_094b"
"tcbn02_bwph130pnpnl3p48cpd_mb_lvtll_c240209_094b"
 
# 0p445v_25c_cworst_T & typical
#"tcbn02_bwph130nppnl3p48cpd_base_svt_c230828_094b"
#"tcbn02_bwph130pnnpl3p48cpd_base_svt_c230828_094b"
#"tcbn02_bwph130pnpnl3p48cpd_base_svt_c230828_094b"
)
 
PVT_CORNERS=(
#"ttg_0p480v_25c_cworst_T"
"ttg_0p480v_25c_typical"
#"ttg_0p445v_25c_cworst_T"
#"ttg_0p445v_25c_typical"
)
USE_REPLACE=false
RUN_NOM_CHAR=false
RUN_LVF_CHAR=true
 
# -----------------------------------------------------
# Run Nominal Characterization Step
# -----------------------------------------------------
echo "Running nominal characterization step..."
$PYTHON_PATH $GEN_SCRIPT \
    --work_dir "$WORK_DIR" \
    --dirs "${DIRS[@]}" \
    --pvt_corners "${PVT_CORNERS[@]}" \
    --use_replace ${USE_REPLACE,,} \
    --run_nom_char ${RUN_NOM_CHAR,,} \
    --run_lvf_char ${RUN_LVF_CHAR,,} \
    --log_file "$LOG_FILE" 2>&1 | tee -a $LOG_FILE
 
if [ ${PIPESTATUS[0]} -ne 0 ]; then
    echo "Error: Nominal characterization step failed. Check the log file for details." | tee -a $LOG_FILE
    exit 1
fi
 
echo "Nominal characterization step completed successfully."
 
 
