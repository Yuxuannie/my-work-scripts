#!/usr/bin/env python3
 
import os
import shutil
import re
import logging
import datetime
import argparse
import subprocess
from pathlib import Path
 
"""
Library Characterization Certification - Collateral Generation Script
Step 1: Collecting Collaterals for EDA Vendors
 
This script processes collateral files from SCLD and generates delivery packages
for EDA vendors with proper corner-specific modifications.
 
Key Functions:
1. Auto-detect reference corner from SCLD files
2. Create delivery folder structure for EDA vendor
3. Copy Template, Netlist, and Model folders directly
4. Process Char folder with corner-specific modifications:
   - Create subfolders for each target corner
   - Copy and rename files with target corner names
   - Replace voltage values in file content
5. SNPS translation support:
   - Translate CDNS templates to SNPS .sis format
   - Filter out .tcl files for SNPS Char delivery
   - Keep Template_sis folder intact
 
Script for Library Characterization Certification Automation
"""
 
def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Collateral Generation for EDA Vendors')
    parser.add_argument('--working_dir',
                       help='Working directory path',
                       required=True)
    parser.add_argument('--eda_vendor',
                       help='EDA vendor name (CDNS, SNPS, etc.)',
                       required=True)
    parser.add_argument('--corners',
                       nargs='+',
                       help='List of target corner names',
                       required=True)
    parser.add_argument('--lpe_type',
                       help='LPE type (e.g., cworst_CCworst_T)',
                       required=True)
    parser.add_argument('--process_snps',
                       action='store_true',
                       help='Process SNPS collaterals (requires CDNS to be done first)')
    parser.add_argument('--log_level',
                       choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                       default='INFO',
                       help='Logging level')
   
    return parser.parse_args()
 
def setup_logging(working_dir, log_level='INFO'):
    """Set up logging configuration"""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    log_dir = os.path.join(working_dir, "logs")
    os.makedirs(log_dir, exist_ok=True)
   
    log_file = os.path.join(log_dir, f"collateral_gen_{timestamp}.log")
   
    logging.basicConfig(
        level=getattr(logging, log_level),
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
   
    logging.info(f"Log file created at: {log_file}")
    return log_file
 
def detect_reference_corner(scld_char_dir):
    """
    Auto-detect the reference corner from SCLD Char folder files
   
    Args:
        scld_char_dir: Path to SCLD Char folder
       
    Returns:
        tuple: (reference_corner, reference_voltage_underscore, reference_voltage_dot)
    """
    logging.info("Auto-detecting reference corner from SCLD files...")
   
    try:
        char_files = os.listdir(scld_char_dir)
        logging.debug(f"Files in SCLD Char folder: {char_files}")
       
        # Pattern to match corner names in filenames
        # Looking for patterns like ssgnp_0p54v_m40c or similar
        corner_pattern = r'(ss\w+_\d+p\d+v_[mc]\d+c)'
        voltage_pattern = r'(\d+p\d+v)'
       
        corners_found = set()
        voltages_found = set()
       
        for filename in char_files:
            if filename.endswith(('.tcl', '.inc')):
                corner_matches = re.findall(corner_pattern, filename)
                voltage_matches = re.findall(voltage_pattern, filename)
               
                if corner_matches:
                    corners_found.update(corner_matches)
                if voltage_matches:
                    voltages_found.update(voltage_matches)
       
        if not corners_found:
            raise ValueError("No corner patterns found in SCLD Char files")
       
        if len(corners_found) > 1:
            logging.warning(f"Multiple corners found: {corners_found}")
            logging.warning("Using the first one as reference")
       
        reference_corner = sorted(corners_found)[0]
       
        # Extract voltage information
        voltage_match = re.search(r'(\d+p\d+)v', reference_corner)
        if not voltage_match:
            raise ValueError(f"Cannot extract voltage from corner: {reference_corner}")
       
        voltage_underscore = voltage_match.group(1) + 'v'  # e.g., 0p54v
        voltage_dot = voltage_match.group(1).replace('p', '.')  # e.g., 0.54
       
        logging.info(f"Detected reference corner: {reference_corner}")
        logging.info(f"Reference voltage (underscore format): {voltage_underscore}")
        logging.info(f"Reference voltage (dot format): {voltage_dot}")
       
        return reference_corner, voltage_underscore, voltage_dot
       
    except Exception as e:
        logging.error(f"Error detecting reference corner: {e}")
        raise
 
def extract_voltage_from_corner(corner):
    """
    Extract voltage information from corner name
   
    Args:
        corner: Corner name (e.g., ssgnp_0p450v_m40c)
       
    Returns:
        tuple: (voltage_underscore, voltage_dot)
    """
    voltage_match = re.search(r'(\d+p\d+)v', corner)
    if not voltage_match:
        raise ValueError(f"Cannot extract voltage from corner: {corner}")
   
    voltage_underscore = voltage_match.group(1) + 'v'  # e.g., 0p450v
    voltage_dot = voltage_match.group(1).replace('p', '.')  # e.g., 0.450
   
    return voltage_underscore, voltage_dot
 
def create_delivery_structure(working_dir, eda_vendor):
    """
    Create delivery folder structure for EDA vendor
   
    Args:
        working_dir: Working directory path
        eda_vendor: EDA vendor name
       
    Returns:
        str: Path to delivery directory
    """
    if eda_vendor == "SNPS":
        delivery_dir = os.path.join(working_dir, "2-for_SNPS")
    else:
        delivery_dir = os.path.join(working_dir, f"1-for_{eda_vendor}")
   
    logging.info(f"Creating delivery structure: {delivery_dir}")
   
    # Create main delivery directory
    os.makedirs(delivery_dir, exist_ok=True)
   
    # Create required subdirectories
    required_dirs = ['Netlist', 'Template', 'Char']
    for dir_name in required_dirs:
        sub_dir = os.path.join(delivery_dir, dir_name)
        os.makedirs(sub_dir, exist_ok=True)
        logging.debug(f"Created directory: {sub_dir}")
   
    return delivery_dir
 
def copy_static_folders(scld_dir, delivery_dir):
    """
    Copy Template, Netlist, and Model folders directly from SCLD to delivery
   
    Args:
        scld_dir: SCLD source directory
        delivery_dir: Delivery directory
    """
    static_folders = ['Template', 'Netlist', 'Model']
   
    for folder in static_folders:
        src_path = os.path.join(scld_dir, folder)
        dst_path = os.path.join(delivery_dir, folder)
       
        if os.path.exists(src_path):
            logging.info(f"Copying {folder} folder...")
           
            # Remove destination if it exists
            if os.path.exists(dst_path):
                shutil.rmtree(dst_path)
           
            # Copy the entire folder
            shutil.copytree(src_path, dst_path)
           
            # Count files copied
            file_count = sum([len(files) for r, d, files in os.walk(dst_path)])
            logging.info(f"  Copied {file_count} files from {folder}")
        else:
            if folder == 'Model':
                logging.info(f"Model folder not found (optional): {src_path}")
            else:
                logging.warning(f"Source folder not found: {src_path}")
 
def replace_voltage_in_file(file_path, ref_voltage_underscore, ref_voltage_dot,
                          target_voltage_underscore, target_voltage_dot):
    """
    Replace voltage values in a file
   
    Args:
        file_path: Path to file to modify
        ref_voltage_underscore: Reference voltage in underscore format (e.g., 0p54v)
        ref_voltage_dot: Reference voltage in dot format (e.g., 0.54)
        target_voltage_underscore: Target voltage in underscore format (e.g., 0p450v)
        target_voltage_dot: Target voltage in dot format (e.g., 0.450)
    """
    try:
        with open(file_path, 'r') as f:
            content = f.read()
       
        original_content = content
       
        # Replace underscore format (e.g., 0p54v -> 0p450v)
        content = content.replace(ref_voltage_underscore, target_voltage_underscore)
       
        # Replace dot format (e.g., 0.54 -> 0.450)
        content = content.replace(ref_voltage_dot, target_voltage_dot)
       
        # Only write if content changed
        if content != original_content:
            with open(file_path, 'w') as f:
                f.write(content)
           
            logging.debug(f"Updated voltage values in: {os.path.basename(file_path)}")
            return True
        else:
            logging.debug(f"No voltage replacements needed in: {os.path.basename(file_path)}")
            return False
           
    except Exception as e:
        logging.error(f"Error processing file {file_path}: {e}")
        return False
 
def process_char_folder(scld_dir, delivery_dir, corners, lpe_type,
                       ref_corner, ref_voltage_underscore, ref_voltage_dot):
    """
    Process Char folder for each target corner
   
    Args:
        scld_dir: SCLD source directory
        delivery_dir: Delivery directory
        corners: List of target corners
        lpe_type: LPE type
        ref_corner: Reference corner name
        ref_voltage_underscore: Reference voltage in underscore format
        ref_voltage_dot: Reference voltage in dot format
    """
    scld_char_dir = os.path.join(scld_dir, 'Char')
    delivery_char_dir = os.path.join(delivery_dir, 'Char')
   
    logging.info("Processing Char folder for target corners...")
   
    # Expected file patterns in Char folder
    file_patterns = [
        f"char_{ref_corner}_{lpe_type}.cons.tcl",
        f"char_{ref_corner}_{lpe_type}.non_cons.tcl",
        f"{ref_corner}_{lpe_type}.delay.inc",
        f"{ref_corner}_{lpe_type}.hold.inc",
        f"{ref_corner}_{lpe_type}.mpw.inc",
        f"{ref_corner}_{lpe_type}.setup.inc"
    ]
   
    # Check which files actually exist
    existing_files = []
    missing_files = []
   
    for pattern in file_patterns:
        file_path = os.path.join(scld_char_dir, pattern)
        if os.path.exists(file_path):
            existing_files.append(pattern)
        else:
            missing_files.append(pattern)
   
    if existing_files:
        logging.info(f"Found {len(existing_files)} reference files:")
        for f in existing_files:
            logging.info(f"  Found: {f}")
   
    if missing_files:
        logging.warning(f"Missing {len(missing_files)} expected files:")
        for f in missing_files:
            logging.warning(f"  Missing: {f}")
   
    # Process each target corner
    for corner in corners:
        logging.info(f"Processing corner: {corner}")
       
        # Create corner subfolder
        corner_dir = os.path.join(delivery_char_dir, corner)
        os.makedirs(corner_dir, exist_ok=True)
       
        # Extract target voltage information
        target_voltage_underscore, target_voltage_dot = extract_voltage_from_corner(corner)
       
        logging.debug(f"  Target voltage (underscore): {target_voltage_underscore}")
        logging.debug(f"  Target voltage (dot): {target_voltage_dot}")
       
        files_processed = 0
        files_updated = 0
       
        # Process each existing file
        for ref_filename in existing_files:
            # Generate target filename by replacing corner name
            target_filename = ref_filename.replace(ref_corner, corner)
           
            src_file = os.path.join(scld_char_dir, ref_filename)
            dst_file = os.path.join(corner_dir, target_filename)
           
            # Copy file
            shutil.copy2(src_file, dst_file)
            files_processed += 1
           
            # Replace voltage values in the copied file
            if replace_voltage_in_file(dst_file,
                                     ref_voltage_underscore, ref_voltage_dot,
                                     target_voltage_underscore, target_voltage_dot):
                files_updated += 1
           
            logging.debug(f"    Copied and processed: {target_filename}")
       
        logging.info(f"  Corner {corner}: {files_processed} files copied, {files_updated} files updated")
   
    logging.info("Char folder processing completed!")
 
def generate_summary_report(working_dir, delivery_dir, eda_vendor, corners,
                          ref_corner, lpe_type):
    """
    Generate a summary report of the collateral generation
   
    Args:
        working_dir: Working directory
        delivery_dir: Delivery directory
        eda_vendor: EDA vendor name
        corners: List of target corners
        ref_corner: Reference corner
        lpe_type: LPE type
    """
    summary_file = os.path.join(delivery_dir, "collateral_generation_summary.txt")
   
    try:
        with open(summary_file, 'w') as f:
            f.write("=" * 80 + "\n")
            f.write("COLLATERAL GENERATION SUMMARY\n")
            f.write("=" * 80 + "\n")
            f.write(f"Generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"EDA Vendor: {eda_vendor}\n")
            f.write(f"Reference Corner: {ref_corner}\n")
            f.write(f"LPE Type: {lpe_type}\n")
            f.write(f"Target Corners: {len(corners)} corners\n")
            f.write("\n")
           
            f.write("Target Corners:\n")
            for i, corner in enumerate(corners, 1):
                f.write(f"  {i}. {corner}\n")
            f.write("\n")
           
            f.write("Folder Structure Created:\n")
            f.write(f"  {delivery_dir}/\n")
            f.write("  â”œâ”€â”€ Netlist/          (copied from SCLD)\n")
            f.write("  â”œâ”€â”€ Template/         (copied from SCLD)\n")
            f.write("  â”œâ”€â”€ Model/            (copied from SCLD, if available)\n")
            f.write("  â””â”€â”€ Char/\n")
            for corner in corners:
                f.write(f"      â”œâ”€â”€ {corner}/\n")
            f.write("\n")
           
            f.write("Files Generated per Corner:\n")
            f.write("  - char_{corner}_{lpe_type}.cons.tcl\n")
            f.write("  - char_{corner}_{lpe_type}.non_cons.tcl\n")
            f.write("  - {corner}_{lpe_type}.delay.inc\n")
            f.write("  - {corner}_{lpe_type}.hold.inc\n")
            f.write("  - {corner}_{lpe_type}.mpw.inc\n")
            f.write("  - {corner}_{lpe_type}.setup.inc\n")
            f.write("\n")
           
            f.write("Voltage Modifications:\n")
            ref_v_underscore, ref_v_dot = extract_voltage_from_corner(ref_corner)
            f.write(f"  Reference: {ref_v_underscore} / {ref_v_dot}\n")
            for corner in corners:
                target_v_underscore, target_v_dot = extract_voltage_from_corner(corner)
                f.write(f"  {corner}: {target_v_underscore} / {target_v_dot}\n")
            f.write("\n")
           
            f.write("=" * 80 + "\n")
            f.write("Ready for delivery to EDA vendor!\n")
            f.write("=" * 80 + "\n")
       
        logging.info(f"Summary report generated: {summary_file}")
       
    except Exception as e:
        logging.error(f"Error generating summary report: {e}")
 
def process_snps_translation(working_dir, corners, lpe_type):
    """
    Process SNPS collateral translation from CDNS templates
   
    Args:
        working_dir: Working directory path
        corners: List of target corners
        lpe_type: LPE type
       
    Returns:
        str: Path to SNPS delivery directory
    """
    logging.info("=" * 80)
    logging.info("STARTING SNPS COLLATERAL TRANSLATION")
    logging.info("=" * 80)
   
    # Paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    snps_translate_dir = os.path.join(script_dir, "SNPS_translate")
    cdns_delivery_dir = os.path.join(working_dir, "1-for_CDNS")
    cdns_template_dir = os.path.join(cdns_delivery_dir, "Template")
    snps_delivery_dir = os.path.join(working_dir, "2-for_SNPS")
   
    # Validate CDNS delivery exists
    if not os.path.exists(cdns_delivery_dir):
        raise FileNotFoundError(f"CDNS delivery folder not found: {cdns_delivery_dir}")
   
    if not os.path.exists(cdns_template_dir):
        raise FileNotFoundError(f"CDNS Template folder not found: {cdns_template_dir}")
   
    # Validate SNPS translate resources
    translator_script = os.path.join(snps_translate_dir, "template_translator.sh")
    seed_lib = os.path.join(snps_translate_dir, "seed.lib")
   
    if not os.path.exists(translator_script):
        raise FileNotFoundError(f"SNPS translator script not found: {translator_script}")
   
    if not os.path.exists(seed_lib):
        raise FileNotFoundError(f"SNPS seed.lib not found: {seed_lib}")
   
    # Warning about seed.lib
    logging.warning("=" * 80)
    logging.warning("IMPORTANT: SEED.LIB NODE COMPATIBILITY WARNING")
    logging.warning("=" * 80)
    logging.warning("The seed.lib file is node-specific and may not be compatible")
    logging.warning("with your target process node. Please confirm with Jia-wei from")
    logging.warning("SCLD team that this seed.lib is correct for your process node")
    logging.warning("before proceeding with SNPS characterization.")
    logging.warning("=" * 80)
   
    # Create SNPS delivery structure
    logging.info("Creating SNPS delivery structure...")
    create_snps_delivery_structure(snps_delivery_dir, corners)
   
    # Copy translation files to CDNS Template folder (temporary)
    logging.info("Copying translation files to CDNS Template folder...")
    temp_translator = os.path.join(cdns_template_dir, "template_translator.sh")
    temp_seed_lib = os.path.join(cdns_template_dir, "seed.lib")
   
    shutil.copy2(translator_script, temp_translator)
    shutil.copy2(seed_lib, temp_seed_lib)
    logging.info(f"  Copied: template_translator.sh")
    logging.info(f"  Copied: seed.lib")
   
    try:
        # Run translation script in CDNS Template folder
        logging.info("Running SNPS template translation...")
        original_dir = os.getcwd()
        os.chdir(cdns_template_dir)
       
        # Make script executable and run it
        os.chmod(temp_translator, 0o755)
       
        result = subprocess.run(['tcsh', 'template_translator.sh'],
                              capture_output=True, text=True)
       
        if result.returncode != 0:
            logging.error(f"Translation script failed: {result.stderr}")
            raise RuntimeError(f"SNPS translation failed: {result.stderr}")
       
        logging.info(f"Translation completed successfully")
        logging.debug(f"Translation output: {result.stdout}")
       
        # Check if Template_sis folder was created
        template_sis_dir = os.path.join(cdns_template_dir, "Template_sis")
        if not os.path.exists(template_sis_dir):
            raise RuntimeError("Template_sis folder was not created by translation script")
       
        # Copy translated templates to SNPS delivery structure
        copy_snps_templates_to_delivery(template_sis_dir, snps_delivery_dir, corners)
       
        # Copy other folders from CDNS to SNPS (with filtering)
        copy_snps_static_folders(working_dir, snps_delivery_dir)
       
        # Copy seed.lib to SNPS delivery root
        copy_seed_lib_to_snps(seed_lib, snps_delivery_dir)
       
        # Generate SNPS summary report
        generate_snps_summary_report(working_dir, snps_delivery_dir, corners, lpe_type)
       
        logging.info("SNPS collateral translation completed successfully!")
        logging.info("Template_sis folder preserved in CDNS Template directory")
       
    finally:
        # Cleanup: remove only temporary files, keep Template_sis
        os.chdir(original_dir)
        cleanup_snps_temp_files(cdns_template_dir)
   
    return snps_delivery_dir
 
def create_snps_delivery_structure(snps_delivery_dir, corners):
    """Create SNPS delivery folder structure"""
    logging.info(f"Creating SNPS delivery structure: {snps_delivery_dir}")
   
    # Create main delivery directory
    os.makedirs(snps_delivery_dir, exist_ok=True)
   
    # Create required subdirectories
    required_dirs = ['Netlist', 'Template', 'Char']
    for dir_name in required_dirs:
        sub_dir = os.path.join(snps_delivery_dir, dir_name)
        os.makedirs(sub_dir, exist_ok=True)
       
        # Create corner subdirectories for Template and Char
        if dir_name in ['Template', 'Char']:
            for corner in corners:
                corner_dir = os.path.join(sub_dir, corner)
                os.makedirs(corner_dir, exist_ok=True)
                logging.debug(f"Created directory: {corner_dir}")
 
def copy_snps_templates_to_delivery(template_sis_dir, snps_delivery_dir, corners):
    """Copy translated .sis and .slew_all templates to SNPS delivery structure"""
    logging.info("Copying translated templates to SNPS delivery structure...")
   
    try:
        # Look for both .sis and .slew_all files
        sis_files = [f for f in os.listdir(template_sis_dir) if f.endswith('.sis')]
        slew_all_files = [f for f in os.listdir(template_sis_dir) if f.endswith('.slew_all')]
       
        total_files = len(sis_files) + len(slew_all_files)
        logging.info(f"Found {len(sis_files)} .sis files and {len(slew_all_files)} .slew_all files")
        logging.info(f"Total translated files: {total_files}")
       
        # Process .sis files
        for sis_file in sis_files:
            logging.debug(f"Processing .sis file: {sis_file}")
           
            # Determine which corner this template belongs to
            corner_matched = False
            for corner in corners:
                if corner in sis_file:
                    src_file = os.path.join(template_sis_dir, sis_file)
                    dst_dir = os.path.join(snps_delivery_dir, "Template", corner)
                    dst_file = os.path.join(dst_dir, sis_file)
                   
                    shutil.copy2(src_file, dst_file)
                    logging.debug(f"  Copied {sis_file} to {corner}/ folder")
                    corner_matched = True
                    break
           
            if not corner_matched:
                # If no corner match found, copy to all corners
                logging.warning(f"No corner match for {sis_file}, copying to all corners")
                for corner in corners:
                    dst_dir = os.path.join(snps_delivery_dir, "Template", corner)
                    dst_file = os.path.join(dst_dir, sis_file)
                    src_file = os.path.join(template_sis_dir, sis_file)
                    shutil.copy2(src_file, dst_file)
       
        # Process .slew_all files
        for slew_all_file in slew_all_files:
            logging.debug(f"Processing .slew_all file: {slew_all_file}")
           
            # Determine which corner this template belongs to
            corner_matched = False
            for corner in corners:
                if corner in slew_all_file:
                    src_file = os.path.join(template_sis_dir, slew_all_file)
                    dst_dir = os.path.join(snps_delivery_dir, "Template", corner)
                    dst_file = os.path.join(dst_dir, slew_all_file)
                   
                    shutil.copy2(src_file, dst_file)
                    logging.debug(f"  Copied {slew_all_file} to {corner}/ folder")
                    corner_matched = True
                    break
           
            if not corner_matched:
                # If no corner match found, copy to all corners
                logging.warning(f"No corner match for {slew_all_file}, copying to all corners")
                for corner in corners:
                    dst_dir = os.path.join(snps_delivery_dir, "Template", corner)
                    dst_file = os.path.join(dst_dir, slew_all_file)
                    src_file = os.path.join(template_sis_dir, slew_all_file)
                    shutil.copy2(src_file, dst_file)
       
        logging.info("Template copying completed")
        logging.info(f"  Distributed {len(sis_files)} .sis files")
        logging.info(f"  Distributed {len(slew_all_files)} .slew_all files")
       
    except Exception as e:
        logging.error(f"Error copying SNPS templates: {e}")
        raise
 
def copy_snps_static_folders(working_dir, snps_delivery_dir):
    """Copy Netlist, Model, and filtered Char folders to SNPS"""
    logging.info("Copying static folders to SNPS...")
   
    # Get paths
    scld_dir = os.path.join(working_dir, "0-from_SCLD")
    cdns_delivery_dir = os.path.join(working_dir, "1-for_CDNS")
   
    # Copy Netlist folder from SCLD (same as CDNS)
    scld_netlist = os.path.join(scld_dir, "Netlist")
    snps_netlist = os.path.join(snps_delivery_dir, "Netlist")
   
    if os.path.exists(scld_netlist):
        if os.path.exists(snps_netlist):
            shutil.rmtree(snps_netlist)
        shutil.copytree(scld_netlist, snps_netlist)
        logging.info("  Copied Netlist folder from SCLD")
   
    # Copy Model folder from SCLD (same as CDNS)
    scld_model = os.path.join(scld_dir, "Model")
    snps_model = os.path.join(snps_delivery_dir, "Model")
   
    if os.path.exists(scld_model):
        if os.path.exists(snps_model):
            shutil.rmtree(snps_model)
        shutil.copytree(scld_model, snps_model)
        logging.info("  Copied Model folder from SCLD")
    else:
        logging.info("  Model folder not found (optional)")
   
    # Copy Char folders by corner, but filter out .tcl files for SNPS
    cdns_char_dir = os.path.join(cdns_delivery_dir, "Char")
    snps_char_dir = os.path.join(snps_delivery_dir, "Char")
   
    if os.path.exists(cdns_char_dir):
        for corner_folder in os.listdir(cdns_char_dir):
            corner_path = os.path.join(cdns_char_dir, corner_folder)
            if os.path.isdir(corner_path):
                dst_corner_path = os.path.join(snps_char_dir, corner_folder)
                os.makedirs(dst_corner_path, exist_ok=True)
               
                # Copy only .inc files, skip .tcl files for SNPS
                files_copied = 0
                files_skipped = 0
               
                for filename in os.listdir(corner_path):
                    src_file = os.path.join(corner_path, filename)
                    if os.path.isfile(src_file):
                        if filename.endswith('.inc'):
                            dst_file = os.path.join(dst_corner_path, filename)
                            shutil.copy2(src_file, dst_file)
                            files_copied += 1
                        elif filename.endswith('.tcl'):
                            logging.debug(f"    Skipped .tcl file for SNPS: {filename}")
                            files_skipped += 1
                        else:
                            # Copy other files
                            dst_file = os.path.join(dst_corner_path, filename)
                            shutil.copy2(src_file, dst_file)
                            files_copied += 1
               
                logging.info(f"  Copied Char/{corner_folder}: {files_copied} files copied, {files_skipped} .tcl files skipped")
       
        logging.info("  Char folders copied with .tcl files filtered out for SNPS")
 
def copy_seed_lib_to_snps(seed_lib_path, snps_delivery_dir):
    """Copy seed.lib to SNPS delivery root directory"""
    logging.info("Copying seed.lib to SNPS delivery folder...")
   
    try:
        dst_seed_lib = os.path.join(snps_delivery_dir, "seed.lib")
        shutil.copy2(seed_lib_path, dst_seed_lib)
        logging.info(f"  Copied seed.lib to SNPS delivery root")
        logging.info(f"  Location: {dst_seed_lib}")
    except Exception as e:
        logging.error(f"Error copying seed.lib to SNPS delivery: {e}")
        raise
 
def cleanup_snps_temp_files(cdns_template_dir):
    """Clean up temporary files created during SNPS translation (keep Template_sis)"""
    logging.info("Cleaning up temporary files (keeping Template_sis)...")
   
    temp_files = [
        "template_translator.sh",
        "seed.lib"
    ]
   
    for item in temp_files:
        item_path = os.path.join(cdns_template_dir, item)
        try:
            if os.path.isfile(item_path):
                os.remove(item_path)
                logging.debug(f"  Removed file: {item}")
        except Exception as e:
            logging.warning(f"Could not remove {item}: {e}")
   
    logging.info("Cleanup completed (Template_sis folder preserved)")
 
def generate_snps_summary_report(working_dir, snps_delivery_dir, corners, lpe_type):
    """Generate SNPS-specific summary report"""
    summary_file = os.path.join(snps_delivery_dir, "snps_collateral_summary.txt")
   
    try:
        with open(summary_file, 'w') as f:
            f.write("=" * 80 + "\n")
            f.write("SNPS COLLATERAL GENERATION SUMMARY\n")
            f.write("=" * 80 + "\n")
            f.write(f"Generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"EDA Vendor: SNPS\n")
            f.write(f"Translation Method: From CDNS templates using template_translator.sh\n")
            f.write(f"LPE Type: {lpe_type}\n")
            f.write(f"Target Corners: {len(corners)} corners\n")
            f.write("\n")
           
            f.write("Target Corners:\n")
            for i, corner in enumerate(corners, 1):
                f.write(f"  {i}. {corner}\n")
            f.write("\n")
           
            f.write("SNPS Folder Structure Created:\n")
            f.write(f"  {snps_delivery_dir}/\n")
            f.write("  â”œâ”€â”€ Netlist/          (copied from SCLD)\n")
            f.write("  â”œâ”€â”€ Model/            (copied from SCLD, if available)\n")
            f.write("  â”œâ”€â”€ Template/\n")
            for corner in corners:
                f.write(f"  â”‚   â”œâ”€â”€ {corner}/     (.sis and .slew_all files)\n")
            f.write("  â”œâ”€â”€ Char/\n")
            for corner in corners:
                f.write(f"  â”‚   â”œâ”€â”€ {corner}/     (.inc files only, .tcl files excluded)\n")
            f.write("  â””â”€â”€ seed.lib          (node-specific library for SNPS)\n")
            f.write("\n")
           
            f.write("Translation Process:\n")
            f.write("  1. CDNS tcb*.tcl templates translated to SNPS format\n")
            f.write("  2. Multiple perl transformation scripts applied\n")
            f.write("  3. Generated .sis and .slew_all files separated by corner\n")
            f.write("  4. Both file types distributed to Template corner folders\n")
            f.write("  5. Char folders copied with .tcl files filtered out\n")
            f.write("  6. Template_sis folder preserved in CDNS delivery\n")
            f.write("  7. seed.lib copied to SNPS delivery root\n")
            f.write("\n")
           
            f.write("IMPORTANT NOTES:\n")
            f.write("  - seed.lib file is node-specific and included in delivery\n")
            f.write("  - Confirm seed.lib compatibility with Jia-wei (SCLD)\n")
            f.write("  - Translated templates include .sis and .slew_all files\n")
            f.write("  - Both template file types distributed by corner\n")
            f.write("  - .tcl files excluded from SNPS Char delivery\n")
            f.write("  - Template_sis folder kept intact in CDNS Template directory\n")
            f.write("  - seed.lib placed at delivery root for easy access\n")
            f.write("\n")
           
            f.write("=" * 80 + "\n")
            f.write("SNPS collaterals ready for delivery!\n")
            f.write("=" * 80 + "\n")
       
        logging.info(f"SNPS summary report generated: {summary_file}")
       
    except Exception as e:
        logging.error(f"Error generating SNPS summary report: {e}")
 
def main():
    """Main function"""
    args = parse_arguments()
   
    # Set up logging
    log_file = setup_logging(args.working_dir, args.log_level)
   
    if args.process_snps:
        logging.info("=" * 80)
        logging.info("SNPS COLLATERAL PROCESSING MODE")
        logging.info("=" * 80)
        logging.info(f"Working Directory: {args.working_dir}")
        logging.info(f"Target Corners: {args.corners}")
        logging.info(f"LPE Type: {args.lpe_type}")
        logging.info("=" * 80)
       
        try:
            # Process SNPS translation
            snps_delivery_dir = process_snps_translation(args.working_dir, args.corners, args.lpe_type)
           
            logging.info("=" * 80)
            logging.info("SNPS COLLATERAL PROCESSING COMPLETED SUCCESSFULLY!")
            logging.info("=" * 80)
            logging.info(f"SNPS delivery folder: {snps_delivery_dir}")
            logging.info(f"Target corners processed: {len(args.corners)}")
            logging.info("SNPS collaterals ready for delivery!")
           
        except Exception as e:
            logging.error(f"Error during SNPS collateral processing: {e}")
            logging.error("SNPS collateral processing failed!")
            raise
   
    else:
        logging.info("=" * 80)
        logging.info("CDNS COLLATERAL GENERATION")
        logging.info("=" * 80)
        logging.info(f"Working Directory: {args.working_dir}")
        logging.info(f"EDA Vendor: {args.eda_vendor}")
        logging.info(f"Target Corners: {args.corners}")
        logging.info(f"LPE Type: {args.lpe_type}")
        logging.info("=" * 80)
       
        try:
            # Define paths
            scld_dir = os.path.join(args.working_dir, "0-from_SCLD")
            scld_char_dir = os.path.join(scld_dir, "Char")
           
            # Validate input directories
            if not os.path.exists(scld_dir):
                raise FileNotFoundError(f"SCLD directory not found: {scld_dir}")
           
            if not os.path.exists(scld_char_dir):
                raise FileNotFoundError(f"SCLD Char directory not found: {scld_char_dir}")
           
            # Step 1: Auto-detect reference corner
            ref_corner, ref_voltage_underscore, ref_voltage_dot = detect_reference_corner(scld_char_dir)
           
            # Step 2: Create delivery folder structure
            delivery_dir = create_delivery_structure(args.working_dir, args.eda_vendor)
           
            # Step 3: Copy static folders (Template, Netlist, and Model)
            copy_static_folders(scld_dir, delivery_dir)
           
            # Step 4: Process Char folder for each target corner
            process_char_folder(scld_dir, delivery_dir, args.corners, args.lpe_type,
                              ref_corner, ref_voltage_underscore, ref_voltage_dot)
           
            # Step 5: Generate summary report
            generate_summary_report(args.working_dir, delivery_dir, args.eda_vendor,
                                  args.corners, ref_corner, args.lpe_type)
           
            logging.info("=" * 80)
            logging.info("CDNS COLLATERAL GENERATION COMPLETED SUCCESSFULLY!")
            logging.info("=" * 80)
            logging.info(f"Delivery folder: {delivery_dir}")
            logging.info(f"Target corners processed: {len(args.corners)}")
            logging.info(f"Reference corner: {ref_corner}")
            logging.info("Ready for delivery to EDA vendor!")
           
        except Exception as e:
            logging.error(f"Error during collateral generation: {e}")
            logging.error("Collateral generation failed!")
            raise
 
if __name__ == "__main__":
    main()
 
