#!/bin/bash
 
# Configuration for paths and corners
working_path="/SIM/DFDS_20211231/Personal/ynie/3-LibCharCerti/2024/N2P/1-FMC_Golden/gen_DECKs"
resubmit_path="/SIM/DFDS_20211231/Personal/ynie/3-LibCharCerti/2024/N2P/1-FMC_Golden/gen_DECKs/1-script/run.sh/re.submit"
corners=("ssgnp_0p450v_m40c" "ssgnp_0p465v_m40c" "ssgnp_0p480v_m40c" "ssgnp_0p495v_m40c")
#corners=("ssgnp_0p465v_m40c" "ssgnp_0p495v_m40c")
 
# Convert corners array to a space-separated string
corners_str="${corners[@]}"
 
# Run the Python script with arguments
/usr/local/python/3.9.10/bin/python3 resubmit.py --working_path "$working_path" --resubmit_path "$resubmit_path" --corners $corners_str
 
