#!/bin/bash
 
# Parameters
ref_deck_path="/SIM/DFDS_20211231/Personal/ynie/3-LibCharCerti/2025/N2P_v1.0/1-MC_golden/0-FMC_golden/gen_DECKs/"
corners=("ssgnp_0p450v_m40c" "ssgnp_0p465v_m40c" "ssgnp_0p480v_m40c" "ssgnp_0p495v_m40c")
working_path="/SIM/DFDS_20211231/Personal/ynie/3-LibCharCerti/2025/N2P_v1.0/1-MC_golden/1-Full_MC_golden/"
type="delay"
log_file="run_copy_mc.log"
 
# Create a timestamp for the log
echo "=======================================================" > $log_file
echo "Starting MC file processing: $(date)" >> $log_file
echo "=======================================================" >> $log_file
echo "" >> $log_file
 
# Execute the Python script with the defined parameters
/usr/local/python/3.9.10/bin/python3 copy_mc_files.py "$ref_deck_path" "$working_path" "$type" "${corners[@]}" 2>&1 | tee -a $log_file
 
echo "" >> $log_file
echo "=======================================================" >> $log_file
echo "Process completed: $(date)" >> $log_file
echo "=======================================================" >> $log_file
 
echo "Process completed! Log saved to $log_file"
 
