#!/bin/bash
 
CORNERS="ssgnp_0p450v_m40c ssgnp_0p465v_m40c ssgnp_0p480v_m40c ssgnp_0p495v_m40c"
#CORNERS="ssgnp_0p450v_m40c"
TYPES="hold"
FOLDER_PATH="/SIM/DFDS_20211231/Personal/ynie/3-LibCharCerti/2025/N2P_v1.0/1-MC_golden/0-FMC_golden/gen_DECKs/"
 
# Run the Python script with the provided arguments
/usr/local/python/3.9.10/bin/python3 /SIM/DFDS_20211231/Personal/ynie/3-LibCharCerti/2024/N2P/1-FMC_Golden/gen_DECKs/1-script/run.py/monitor_simulation.py --corners $CORNERS --types $TYPES --folder_path $FOLDER_PATH
 
 
