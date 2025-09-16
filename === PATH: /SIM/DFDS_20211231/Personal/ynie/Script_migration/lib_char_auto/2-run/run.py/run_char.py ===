import os
import subprocess
import logging
import argparse
 
####################################################################################################################
#################################### UTILITY FUNCTIONS #############################################################
####################################################################################################################
 
def setup_logging(log_file='generate_run_script.log'):
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        filename=log_file,
        filemode='w'
    )
    # Also output to console
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)
 
def str2bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')
 
#####################################################################################################################
################################# Generate run scripts ##############################################################
#####################################################################################################################
 
def generate_run_script(work_dir, dirs, pvt_corners):
    subdirs = ["Char", "LVF/Char"]
 
    commands = {
        "Char": "/tools/cadence/Liberate/21.1.2.270_42/bin/liberate --trio",
        "LVF/Char": "/tools/cadence/Liberate/21.1.2.270_48/bin/variety --trio"
    }
 
    for dir_index, dir in enumerate(dirs, 1):
        logging.info("Processing directory %d/%d: %s", dir_index, len(dirs), dir)
 
        for subdir in subdirs:
            dir_path = os.path.join(work_dir, dir, subdir)
            logging.debug("Checking directory path: %s", dir_path)
 
            if os.path.isdir(dir_path):
                logging.info("Directory exists: %s", dir_path)
                run_script_path = os.path.join(dir_path, "run.scr")
 
                # Remove existing run.scr if it exists
                if os.path.exists(run_script_path):
                    os.remove(run_script_path)
                    logging.info("Removed existing run.scr at %s", run_script_path)
 
                try:
                    with open(run_script_path, 'w') as run_script:
                        run_script.write("#!/bin/tcsh -f \n")
                        run_script.write("source /tools/dotfile_new/cshrc.lsfc2\n")
                        run_script.write("source /tools/dotfile_new/cshrc.liberate 21.1.2.270_48\n")
                        run_script.write("setenv LIBERATE_TRIO 1\n")
                        run_script.write("setenv CDS_LIC_FILE 5280@f15lic18:5280@f15lic20\n")
 
                        # Find and filter TCL files based on corner information
                        for tcl_file in os.listdir(dir_path):
                            if tcl_file.endswith(".tcl"):
                                tcl_path = os.path.join(dir_path, tcl_file)
                                if contains_pvt_corner(tcl_path, pvt_corners):
                                    base_name = os.path.splitext(tcl_file)[0]
                                    log_file = f"{base_name}.log"
                                    command = f"{commands[subdir]} {tcl_path} >& {os.path.join(dir_path, log_file)}\n"
                                    logging.debug("Writing command to run script: %s", command)
                                    run_script.write(command)
 
                    os.chmod(run_script_path, 0o777)
                    logging.info("Created %s successfully", run_script_path)
 
                except Exception as e:
                    logging.error("Error writing run script at %s: %s", run_script_path, e)
            else:
                logging.warning("Directory does not exist: %s", dir_path)
 
def contains_pvt_corner(tcl_path, pvt_corners):
    """Check if a TCL file contains any of the specified PVT corner information."""
    try:
        with open(tcl_path, 'r') as file:
            content = file.read()
            for corner in pvt_corners:
                if corner in content:
                    logging.debug("File %s contains corner: %s", tcl_path, corner)
                    return True
    except Exception as e:
        logging.error("Error reading file %s: %s", tcl_path, e)
    return False
 
def run_lib_char(work_dir, dirs, run_nom_char, run_lvf_char):
    for dir_index, dir_name in enumerate(dirs, 1):
        logging.info("Starting Lib Char for %d/%d: %s", dir_index, len(dirs), dir_name)
 
        char_dir = os.path.join(work_dir, dir_name, 'Char')
        lvf_char_dir = os.path.join(work_dir, dir_name, 'LVF', 'Char')
 
        ## Run Nominal Lib Char
        if run_nom_char:
            try:
                subprocess.run(["bsub", "run.scr"], cwd=char_dir)
                logging.info("Executed the run.scr at %s  successfully", char_dir)
 
            except subprocess.CalledProcessError as e:
                logging.info("Failed to execute run.scr at %s: %s", char_dir, e)
        else:
            logging.info("Skipping Nominal Library Characterization Run")
 
        ## Run LVF lib Char
        if run_lvf_char:
            try:
                subprocess.run(["bsub", "run.scr"], cwd=lvf_char_dir)
                logging.info("Executed the run.scr at %s  successfully", lvf_char_dir)
 
            except subprocess.CalledProcessError as e:
                logging.info("Failed to execute run.scr at %s: %s", lvf_char_dir, e)
        else:
            logging.info("Skipping LVF Library Characterization Run")
 
#####################################################################################################################
################################### Main Function ###################################################################
#####################################################################################################################
 
def parse_arguments():
    parser = argparse.ArgumentParser(description="Generate run scripts for library characterization")
    parser.add_argument("--work_dir", required=True, help="Base working directory")
    parser.add_argument("--dirs", nargs='+', required=True, help="List of directories to process")
    parser.add_argument("--pvt_corners", nargs='+', required=True, help="List of PVT corners to process")
    parser.add_argument("--use_replace", type=str2bool, required=True, help="Whether to use replace")
    parser.add_argument("--run_nom_char", type=str2bool, required=True, help="Whether to run nominal characterization")
    parser.add_argument("--run_lvf_char", type=str2bool, required=True, help="Whether to run LVF characterization")
    parser.add_argument("--log_file", default="lib_char_automation.log", help="Path to the log file")
 
    return parser.parse_args()
 
def main():
    args = parse_arguments()
    setup_logging(args.log_file)
 
    # Log all arguments for verification
    logging.info("Received arguments:")
    for arg, value in vars(args).items():
        logging.info("  %s: %s", arg, value)
 
    logging.info("\n")
    logging.info("###########################################################")
    logging.info(" Starting Generate the run.scr and run lib Char")
    logging.info("###########################################################\n")
 
    generate_run_script(args.work_dir, args.dirs, args.pvt_corners)
    run_lib_char(args.work_dir, args.dirs, args.run_nom_char, args.run_lvf_char)
 
if __name__ == "__main__":
    main()
 
