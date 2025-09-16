import os
import re
import sys
 
# Get the current path and log file from command line arguments
if len(sys.argv) < 4:
    print("Usage: python replace_strings.py <current_path> <log_file> <subdirectory1> [<subdirectory2> ...]")
    sys.exit(1)
 
current_path = sys.argv[1]
log_file = sys.argv[2]
sub_dirs = sys.argv[3:]
 
# Replacement patterns for each file type
replacements = {
 
########################################### run.csh
    "run.csh": {
        r"QNAME=altos.q,altos2.q,altos3.q": "QNAME=all.q",
        r"QNAME=altos2.q": "QNAME=all.q",
 
 
        r"setenv ALTOSHOME /cdn_n2/cdn2_764559_ext/software/LIBERATE231ISR16_23.26-e045_1": "setenv ALTOSHOME /SIM/DFDS_20211231/Personal/ynie/3-LibCharCerti/2024/N2P/3-sigma_final_replay/1-CDNS/Liberate/tools.lnx86",
 
        r"sbatch --job-name \${SCMJOBNAME} --output\=\${SCRIPT}\.log --error\=\${SCRIPT}\.log --partition\=\${QNAME} go.csh":
 
            # non_exclusive
         'bsub -q $QNAME -J $SCMJOBNAME -n 10 -o ${SCRIPT}.log -e ${SCRIPT}.log $ALTOSHOME/bin/${TOOL} --trio ${SCRIPT}.tcl',
    },
 
########################################### char*.tcl
    r"char.*\.tcl$": {
        r'set_var extsim_cmd\s+"/tools/cadence/SPECTRE/21\.1\.0\.334\.isr6/lnx64/tools\.lnx86/bin/spectre"':
        'set_var extsim_cmd "/tools/cadence/SPECTRE/23.1.0.688.isr14/lnx64/tools.lnx86/bin/spectre"',
 
        # non_exlcusive
        r'SCLD_P4_2.q': "all.q",
 
            r"/grid/cic/mmsimcm_v1/SPECTRE231_ZA/ISR13/lnx86/bin/spectre": "/tools/cadence/SPECTRE/23.1.0.688.isr14/lnx64/tools.lnx86/bin/spectre",
 
r"/dpc/tsmc_vol0371/project/jasons/TSMC_2NM/IT314983/users/smccarth/N2P_v0.9_Library_Characterization_Certification_v1.0.0/archive/rnd_settings": "$path",
 
r'/cdn_n2/cdn2_764559_ext/PE001423/N2P_V10.9_V1.0.0_Certification/archive/sourced_files':
            r'/SIM/DFDS_20211231/Personal/ynie/3-LibCharCerti/2024/N2P/6-final_replay/1-CDNS/0-original_delivery/sourced_files',
    },
 
############################################ inc file
    r".*\.inc$": {
        r"/dpc/tsmc_vol0060/project/jasons/TSMC_2NM/IT314983/users/smccarth/N2P_v0.9_Library_Characterization_Certification_v1.0.0/archive/model/cln2p_sp_v0d9_2p1_usage.l":
        "/CAD/DCAD_CLONE/TechPackage/2024/n02/CL/T-N02-CL-SP-010/0d9_2p1/cln2p_sp_v0d9_2p1_usage.l",
 
r"/cdn_n2/cdn2_764559_ext/PE001423/N2P_V10.9_V1.0.0_Certification/archive/model/cln2p_sp_v0d9_2p1_usage.l":
        "/CAD/DCAD_CLONE/TechPackage/2024/n02/CL/T-N02-CL-SP-010/0d9_2p1/cln2p_sp_v0d9_2p1_usage.l",
 
    },
 
########################################### overrides.tcl
    "overrides.tcl": {
 
        # uncomment the first line to avoid sourcing the debug.tcl
        r'source /home/smccarth/howto/debug\.tcl':
        '# source /home/smccarth/howto/debug.tcl',
 
        r"source /cdn_n2/cdn2_764559/PE001423/howto/debug.tcl":
            "# source /cdn_n2/cdn2_764559/PE001423/howto/debug.tcl",
 
        # Change the lsf settings
            r"sbatch --job-name \$JOBNAME --output=\%B\/\%L --error=\%B\/\%L --partition\=\${QNAME}":
       
            # non_exclusive
            r'bsub -q $QNAME -J $JOBNAME -n 10',
 
            r"set QNAME altos3.q":
            r"set QNAME all.q",
       
            # change the spectre path
        r'set_var extsim_cmd\s+"/grid/cic/mmsimcm_v1/SPECTRE231_ZA/ISR13/lnx86/bin/spectre"':
        'set_var extsim_cmd "/tools/cadence/SPECTRE/23.1.0.688.isr14/lnx64/tools.lnx86/bin/spectre"',
 
            r'/grid/cic/mmsimcm_v1/SPECTRE231_ZA/ISR14/lnx86/bin/spectre':
         '/tools/cadence/SPECTRE/23.1.0.688.isr14/lnx64/tools.lnx86/bin/spectre',
 
        # change the recommended settings
        r'/grid/cic/vficpv_t2b_001/QA_DEV/main/qaDaily/recommended_settings':
            '$path',
 
r'/cdn_n2/cdn2_764559_ext/PE001423/N2P_V10.9_V1.0.0_Certification/archive/sourced_files':
            r'/SIM/DFDS_20211231/Personal/ynie/3-LibCharCerti/2024/N2P/6-final_replay/1-CDNS/0-original_delivery/sourced_files',
    },
 
}
 
# Function to replace strings in a file using regular expressions
def replace_in_file(file_path, replacements):
    with open(file_path, 'r') as file:
        content = file.read()
   
    for old, new in replacements.items():
        content = re.sub(old, new, content)
   
    with open(file_path, 'w') as file:
        file.write(content)
 
# Write to log file
def log(message):
    with open(log_file, 'a') as logf:
        logf.write(message + "\n")
 
log("Starting replacements")
log("="*40)
 
# Loop through each specified subdirectory and perform replacements
for sub_dir in sub_dirs:
    ssgnp_path = os.path.join(current_path, sub_dir)
   
    for dirpath, dirnames, filenames in os.walk(ssgnp_path):
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
           
            if os.path.isfile(file_path):
                for pattern, repl_dict in replacements.items():
                    if re.match(pattern, filename, re.IGNORECASE):
                        log(f"Processing file: {file_path}")
                        log("-"*40)
                        replace_in_file(file_path, repl_dict)
                        log(f"Replaced strings in file: {file_path}")
                        log("-"*40)
 
log("="*40)
log("File replacements done.")
 
