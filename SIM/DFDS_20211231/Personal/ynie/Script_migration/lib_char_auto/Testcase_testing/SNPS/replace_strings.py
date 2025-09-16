import os
import re
import sys
import logging
 
# Get the base path, log file path, and subdirectories from the command line arguments
base_path = sys.argv[1]
log_file = sys.argv[2]
sub_dirs = sys.argv[3:]
 
# Configure logging
logging.basicConfig(filename=log_file, level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
 
# Start logging
logging.info('Starting replacements')
 
# Define the replacements for each file type
replacements = {
    '*.inc': [
        (r'',
         r'/CAD/DCAD_CLONE/TechPackage/2024/n02/CL/T-N02-CL-SP-010/0d9_2p1/cln2p_sp_v0d9_2p1_usage.l')
    ],
 
    'run.sh': [
 
        # POR
        #(r'primelib',
        #r'bsub -q all.q  /tools/synopsys/PrimeLib/W-2024.09-SP2/bin/primelib'),
 
        (r'/syn_n2/syn2_997008_PL/TSMC_POR_N2/fmvohra/builds/PrimeSim_DR_2020506_0506/Testing',
         r'/SIM/DFDS_20211231/Personal/ynie/3-LibCharCerti/2024/N2P/6-final_replay/2-SNPS/1-tools/PrimeSim/primesim_dr/X-2025.06-BETA-20250507/'),
 
        # Best_ULV
        (r'/syn_n2/syn2_997008_PL/Char_Builds/PL_202409SP5_sandbox/bin/primelib',
         r'bsub -q all.q   /SIM/DFDS_20211231/Personal/ynie/3-LibCharCerti/2024/N2P/6-final_replay/2-SNPS/1-tools/Primelib/primelib/W-2024.09-SP5-1-BETA-20250423/bin/primelib'),
 
        (r'\|tee', r'-o'),
 
        (r'source /syn_n2/syn2_997008_PL/Char_Builds/sourceme',
         r'# source /syn_n2/syn2_997008_PL/Char_Builds/sourceme')
 
    ],
    '*_config.*tcl.sis': [
        (r'/syn_n2/syn2_997008_PL/TSMC_POR_N2/lvf_certification/PL_202409SP1_HSP_202409SP1_golden_run/tcbn02p_bwph130pnpnl3p48cpd_base_svt_c880514', base_path),
                (r'/syn_n2/syn2_997008_PL/TSMC_POR_N2/lvf_certification/PL_202409SP1_HSP_202409SP1_ava_ml3/tcbn02p_bwph130pnpnl3p48cpd_base_svt_c880514',base_path),
 
        # POR
        (r'/syn_n2/syn2_997008_PL/Char_Builds/Hspice_202409-SP1-2/W-2024.09-SP1-2/hspice/bin/hspice',
         r'/tools/synopsys/hspice/V-2023.12-SP1/hspice/bin/hspice'),
 
        # Best_ULV
        (r'/syn_n2/syn2_997008_PL/TSMC_POR_N2/fmvohra/builds/HSPICE_202506_0506/Testing//hspice/bin/hspice',
         r'/SIM/DFDS_20211231/Personal/ynie/3-LibCharCerti/2024/N2P/6-final_replay/2-SNPS/1-tools/Hspice/hspice/X-2025.06-BETA-20250507/hspice/bin/hspice'),
 
        (r'/syn_n2/syn2_997008_PL/TSMC_POR_N2/AMD_POR_certification',
         r'/SIM/DFDS_20211231/Personal/ynie/3-LibCharCerti/2024/N2P/6-final_replay/2-SNPS/0-ori_delivery/TBC/'),
 
        (r'sis -m \"syn2_24 syn2_25 syn2_26 syn2_27 syn2_28 syn2_29 syn2_30 syn2_31 syn2_32 syn2_54 syn2_55 syn2_56 syn2_57 syn2_58 syn2_59 syn2_60 syn2_63 syn2_64\"',
         r'all.q')
 
    ],
#    '*cons.tcl': [
#        (r'(set_config_opt run_list_maxsize)\s+\d+', r'\1 48')
#    ],
    '*.tcl' : [
        (r'/syn_n2/syn2_997008_PL/TSMC_POR_N2/AMD_POR_certification',
         r'/SIM/DFDS_20211231/Personal/ynie/3-LibCharCerti/2024/N2P/6-final_replay/2-SNPS/0-ori_delivery/TBC/')
    ], 
 
}
 
# Function to replace content in files
def replace_in_file(file_path, replacements):
    try:
        with open(file_path, 'r') as file:
            file_content = file.read()
 
        for old_string, new_string in replacements:
            file_content = re.sub(old_string, new_string, file_content)
 
        with open(file_path, 'w') as file:
            file.write(file_content)
 
        logging.info(f'Successfully processed file: {file_path}')
       
    except Exception as e:
        logging.error(f'Error processing file: {file_path}, Error: {str(e)}')
 
# Function to insert text at a specific line
def insert_at_line(file_path, text, line_number):
    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()
 
        lines.insert(line_number, text)
 
        with open(file_path, 'w') as file:
            file.writelines(lines)
 
        logging.info(f'Successfully inserted text at line {line_number} in file: {file_path}')
       
    except Exception as e:
        logging.error(f'Error inserting text at line {line_number} in file: {file_path}, Error: {str(e)}')
 
# Function to comment the last line of a file
def comment_last_line(file_path):
    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()
       
        if lines and not lines[-1].strip().startswith('#'):
            lines[-1] = '#' + lines[-1]  # Add the leading '#' to comment the line
       
            with open(file_path, 'w') as file:
                file.writelines(lines)
           
            logging.info(f'Commented the last line in file: {file_path}')
        else:
            logging.info(f'Last line is already commented in file: {file_path}')
       
    except Exception as e:
        logging.error(f'Error commenting last line in file: {file_path}, Error: {str(e)}')
 
# Function to modify *_config*tcl.sis files
def modify_config_tcl_sis(file_path):
    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()
 
        for i, line in enumerate(lines):
            if line.strip().startswith('set normal_queue'):
                lines[i] = '#set normal_queue\n'
                lines.insert(i + 1, 'set normal_queue {all.q}\n')
                break
       
        with open(file_path, 'w') as file:
            file.writelines(lines)
       
        logging.info(f'Modified set normal_queue in file: {file_path}')
       
    except Exception as e:
        logging.error(f'Error modifying set normal_queue in file: {file_path}, Error: {str(e)}')
 
# Iterate over each subdirectory and perform replacements
for sub_dir in sub_dirs:
    sub_dir_path = os.path.join(base_path, sub_dir)
   
    logging.info('====================================================================================================')
    logging.info(f'Starting processing for subdirectory: {sub_dir}')
    logging.info('====================================================================================================')
   
    for file_name in os.listdir(sub_dir_path):
        file_path = os.path.join(sub_dir_path, file_name)
       
        file_processed = False
       
        for pattern, repls in replacements.items():
            if re.match(pattern.replace('*', '.*'), file_name):
                logging.info('--------------------------------------------------')
                logging.info(f'Processing file: {file_path} with pattern: {pattern}')
                replace_in_file(file_path, [(old.format(sub_dir=sub_dir), new.format(sub_dir=sub_dir)) for old, new in repls])
                file_processed = True
 
        # Special case for run.sh
        if file_name == 'run.sh':
            logging.info('--------------------------------------------------')
            logging.info(f'Processing run.sh file: {file_path}')
            env_setup_commands = (
                "setenv LM_LICENSE_FILE 27020@tsmc8:27020@lic10:27020@linux96:27020@lic20:27020@sjlic5:27020@lic12\n"
                "setenv SNPSLMD_LICENSE_FILE 27020@tsmc8:27020@lic10:27020@linux96:27020@lic20:27020@sjlic5:27020@lic12\n"
                "source /tools/dotfile_new/cshrc.lsfc2\n"
            )
            insert_at_line(file_path, env_setup_commands, 1)  # Insert after the first line (0-indexed)
            #comment_last_line(file_path)  # Comment the last line in run.sh
            logging.info(f'Inserted environment setup commands into run.sh file: {file_path}')
            file_processed = True
 
        # Special case for *_config*tcl.sis
        if re.match(r'.*_config.*tcl.sis', file_name):
            logging.info('--------------------------------------------------')
            modify_config_tcl_sis(file_path)  # Modify set normal_queue in *_config*tcl.sis files
            file_processed = True
       
        if not file_processed:
            logging.info(f'No replacements needed for file: {file_path}')
 
logging.info('Replacements completed')
 
