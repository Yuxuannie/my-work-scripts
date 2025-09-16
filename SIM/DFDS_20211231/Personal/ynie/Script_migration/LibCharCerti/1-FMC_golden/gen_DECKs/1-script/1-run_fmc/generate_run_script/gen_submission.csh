#!/bin/csh -f
 
# Define variables for configuration
set corner = ("ssgnp_0p450v_m40c" "ssgnp_0p465v_m40c" "ssgnp_0p480v_m40c" "ssgnp_0p495v_m40c")
#set corner = ("ssgnp_0p495v_m40c")
set working_path = "/SIM/DFDS_20211231/Personal/ynie/3-LibCharCerti/2025/N2P_v1.0/2-select_2nd_round/1-FMC_golden/gen_DECKs/"
set type_list = ("mpw-100k")   # Define analysis types, e.g., "hold" or "delay"
set queue = "all.q"         # Define the job queue, e.g., "DMKD_DFSD.q" or "all.q"
 
# For delay, use fmc3
# set fmc_script_path = "/SIM/DFDS_20211231/Personal/ynie/3-LibCharCerti/2025/N2P_v1.0/1-MC_golden/0-FMC_golden/gen_DECKs/1-script/1-run_fmc/fmc/fmc.csh"  # Define FMC script path
# For hold , use fmc2
# set fmc_script_path = "/SIM/DFDS_20211231/Personal/ynie/3-LibCharCerti/2025/N2P_v1.0/1-MC_golden/0-FMC_golden/gen_DECKs/1-script/1-run_fmc/fmc/fmc2.csh"  # Define FMC script path
# For mpw, use fmc2_mpw
set fmc_script_path = "/SIM/DFDS_20211231/Personal/ynie/3-LibCharCerti/2025/N2P_v1.0/1-MC_golden/0-FMC_golden/gen_DECKs/1-script/1-run_fmc/fmc/fmc2_mpw.csh"  # Define FMC script path
 
# Execute the Python script with the specified parameters
/usr/local/python/3.9.10/bin/python3 ./generate_run_script.py \
    --working_path $working_path \
    --corner $corner \
    --type_list $type_list \
    --queue $queue \
    --fmc_script_path $fmc_script_path
 
