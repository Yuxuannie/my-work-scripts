#!/bin/csh -f
 
set corner = $1
set working_path = $2
 
/usr/local/python/3.9.10/bin/python3 /SIM/DFDS_20211231/Personal/ynie/3-LibCharCerti/2024/N2P/1-FMC_Golden/gen_DECKs/1-script/run.py/generate_run_script.py --working_path $working_path --corner $corner
 
