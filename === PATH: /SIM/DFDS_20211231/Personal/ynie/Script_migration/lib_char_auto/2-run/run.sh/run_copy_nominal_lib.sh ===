#!/bin/bash
 
# Define parameters
target_root_path="/TIER3/DFSD_C651_chamber/Personal/ynie/0-lib_char/2025/Internal/N2_Tanager/3_25c_cworst_T"
rc_type="cworst_T"
 
#target_root_path="/TIER3/DFSD_C651_chamber/Personal/ynie/0-lib_char/2025/Internal/N2_Tanager/2_25c_typical"
#rc_type="typical"
 
corners=("ttg_0p445v" "ttg_0p480v")
#source_path="/FSIM/PPA_C651_chamber/DFSD/Personal/rbpittu/Lib_char/N2/v1.0/Tanager/LPE_typical_25c/final_libs_TSMC_cellnames"
source_path="/FSIM/PPA_C651_chamber/DFSD/Personal/rbpittu/Lib_char/N2/v1.0/Tanager/LPE_cworst_T_25c/final_libs_TSMC_cellnames/"
 
# Call the Python script with the parameters
/usr/local/python/3.9.10/bin/python3 ../run.py/postprocess/copy_nominal.py "$target_root_path" "$rc_type" "$source_path" "${corners[@]}"
 
 
