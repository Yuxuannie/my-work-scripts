#!/bin/bash
 
# -----------------------------------------------------
# Source License & LSF
# -----------------------------------------------------
 
source ./source_license_lsf.sh
 
# -----------------------------------------------------
# Configuration
# -----------------------------------------------------
 
PYTHON_PATH="/usr/local/python/3.9.10/bin/python3.9"
COPY_SCRIPT="../run.py/copy_kits.py"
LOG_FILE="1-run_copy.log"
#WORK_DIR="/TIER3/DFSD_C651_chamber/Personal/ynie/0-lib_char/2025/Internal/N2_Tanager/2_25c_typical/ttg_0p445v"
WORK_DIR="/TIER3/DFSD_C651_chamber/Personal/ynie/0-lib_char/2025/Internal/N2_Tanager/3_25c_cworst_T/ttg_0p480v"
RF_DIR="/FSIM/APRPPA/N2_Char_package/"
 
FALLBACK_C_CODE="c230828_094a"
 
## Corner Related settings
DIRS=(
 
# 0p480v_cworst_T & 0p480v_typical
"tcbn02_bwph130nppnl3p48cpd_base_lvt_c240207_094b"
#"tcbn02_bwph130nppnl3p48cpd_base_lvtll_c240207_094b"
#"tcbn02_bwph130nppnl3p48cpd_base_svt_c240207_094b"
#"tcbn02_bwph130pnnpl3p48cpd_base_lvt_c240207_094b"
#"tcbn02_bwph130pnnpl3p48cpd_base_lvtll_c240207_094b"
#"tcbn02_bwph130pnnpl3p48cpd_base_svt_c240207_094b"
#"tcbn02_bwph130pnpnl3p48cpd_base_lvt_c240207_094b"
#"tcbn02_bwph130pnpnl3p48cpd_base_lvtll_c240207_094b"
#"tcbn02_bwph130pnpnl3p48cpd_base_svt_c240207_094b"
#"tcbn02_bwph130nppnl3p48cpd_base_lvt_c240209_094b"
#"tcbn02_bwph130nppnl3p48cpd_base_lvtll_c240209_094b"
#"tcbn02_bwph130nppnl3p48cpd_base_svt_c240209_094b"
#"tcbn02_bwph130pnnpl3p48cpd_base_lvt_c240209_094b"
#"tcbn02_bwph130pnnpl3p48cpd_base_lvtll_c240209_094b"
#"tcbn02_bwph130pnnpl3p48cpd_base_svt_c240209_094b"
#"tcbn02_bwph130pnpnl3p48cpd_base_lvt_c240209_094b"
#"tcbn02_bwph130pnpnl3p48cpd_base_lvtll_c240209_094b"
#"tcbn02_bwph130pnpnl3p48cpd_base_svt_c240209_094b"
#"tcbn02_bwph130pnpnl3p48cpd_mb_lvt_c240207_094b"
#"tcbn02_bwph130pnpnl3p48cpd_mb_lvtll_c240207_094b"
#"tcbn02_bwph130pnpnl3p48cpd_mb_lvt_c240209_094b"
#"tcbn02_bwph130pnpnl3p48cpd_mb_lvtll_c240209_094b"
 
 
# 0p445v_25c_cworst_T & typical
#"tcbn02_bwph130nppnl3p48cpd_base_svt_c230828_094b"
#"tcbn02_bwph130pnnpl3p48cpd_base_svt_c230828_094b"
#"tcbn02_bwph130pnpnl3p48cpd_base_svt_c230828_094b"
 
)
 
PVT_CORNERS=(
"ssgnp_0p480v_25c_cworst_T"
#"ssgnp_0p800v_m25c_cworst_T"
#"ssgnp_0p445v_m25c_cworst_T"
)
#LPE_CORNER="LPE_typical_25c"
LPE_CORNER="LPE_cworst_T_25c"
CORNERS=("ssgnp")
USE_REPLACE=false
 
# -----------------------------------------------------
# Replacement
# -----------------------------------------------------
 
REPLACEMENTS=(
    "/FSIM/stdcell_char0_C651_chamber/Altos/tcbn02,$WORK_DIR"
    "/FSIM/stdcell_char1_C651_chamber/Altos/tcbn02,$WORK_DIR"
    "/FSIM/stdcell_char2_C651_chamber/Altos/tcbn02,$WORK_DIR"
    "/FSIM/stdcell_char3_C651_chamber/Altos/tcbn02,$WORK_DIR"
    "/FSIM/stdcell_char4_C651_chamber/Altos/tcbn02,$WORK_DIR"
    "/FSIM/stdcell_char5_C651_chamber/Altos/tcbn02,$WORK_DIR"
 
    "ssgnp,ttg"
    "SSGNP, TT"
 
    "set SPICE SKI,set SPICE SPECTRE"
  #  "set_var extsim_save_failed none,#set_var extsim_save_failed none"
  #  "#set_var extsim_save_passed all,set_var extsim_save_passed all"
    "set_var packet_clients 50,set_var packet_clients 1000"
 
    "m25c,25c"
    "-25, 25"
  #  "cworst_T, typical"
    # Add more replacements as needed
)
 
# -----------------------------------------------------
# Run Copy Step
# -----------------------------------------------------
 
echo "Running copy step..."
$PYTHON_PATH $COPY_SCRIPT \
    --work_dir "$WORK_DIR" \
    --rf_dir "$RF_DIR" \
    --replacements "${REPLACEMENTS[@]}" \
    --dirs "${DIRS[@]}" \
    --pvt_corners "${PVT_CORNERS[@]}" \
    --use_replace $USE_REPLACE \
    --LPE_corner "$LPE_CORNER" \
    --corners "${CORNERS[@]}" \
    --log_file "$LOG_FILE" \
    --new_c_code "$FALLBACK_C_CODE" 2>&1 | tee -a $LOG_FILE
 
 
if [ ${PIPESTATUS[0]} -ne 0 ]; then
    echo "Error: Copy step failed. Check the log file for details." | tee -a $LOG_FILE
    exit 1
fi
 
echo "Copy step completed successfully."
 
 
 
