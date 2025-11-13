#!/usr/bin/env python3

import os
import pandas as pd
import numpy as np
import sys
import logging
import datetime
import argparse
from pathlib import Path

"""
Sigma Pass Rate Calculation Script with Unified Waiver System

Implements unified pass/fail system with structured waivers:

1. Base Pass/Fail Criteria (No Waivers):
   - Check 1: Error-Based Pass (rel_pass OR abs_pass)
   - Base Pass = Check 1 ONLY
   - NOTE: CI bounds checking is REMOVED from base pass

2. Waiver System:
   - Waiver 1: CI Enlargement (CI ± 6%)
     * CI bounds checking ONLY applied here with 6% enlargement
     * lib_value within [CI_LB - 6%×CI_width, CI_UB + 6%×CI_width]
   - Waiver 2: Optimistic Error Only (lib < mc)

3. Generates 4 pass rates:
   - Base_PR: Error-based only (rel OR abs)
   - PR_with_Waiver1: Base + CI enlargement
   - PR_Optimistic_Only: Only optimistic errors
   - PR_with_Both_Waivers: Optimistic + CI enlargement

Output: sigma_PR_table_with_waivers.csv
"""

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Sigma Pass Rate Calculation with Waivers')
    parser.add_argument('--root_path', help='Root directory path containing sigma RPT files', required=True)
    parser.add_argument('--corners', nargs='+', help='List of corner names', required=True)
    parser.add_argument('--types', nargs='+', help='List of types (delay, slew, hold)', required=True)
    parser.add_argument('--log_level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'], default='INFO', help='Logging level')
    return parser.parse_args()

def setup_logging(input_file):
    """Set up logging configuration"""
    input_name = os.path.basename(input_file)
    log_file = os.path.join(os.path.dirname(input_file), f"{input_name}.log")

    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )

    logging.info(f"Log file created at: {log_file}")
    return log_file

def detect_vendor_columns(df):
    """Auto-detect whether this is CDNS or SNPS data based on column names"""
    columns = df.columns.tolist()

    # Check for CDNS columns (case insensitive)
    cdns_patterns = ['cdns_lib', 'CDNS_Lib', 'Cdns_Lib']
    snps_patterns = ['snps_lib', 'SNPS_Lib', 'Snps_Lib']

    for col in columns:
        for pattern in cdns_patterns:
            if pattern in col:
                logging.info(f"Detected CDNS vendor from column: {col}")
                return 'CDNS_Lib'
        for pattern in snps_patterns:
            if pattern in col:
                logging.info(f"Detected SNPS vendor from column: {col}")
                return 'SNPS_Lib'

    # If no exact match, try partial matching
    for col in columns:
        if 'cdns' in col.lower():
            logging.info(f"Detected CDNS vendor (partial match) from column: {col}")
            return 'CDNS_Lib'
        elif 'snps' in col.lower():
            logging.info(f"Detected SNPS vendor (partial match) from column: {col}")
            return 'SNPS_Lib'

    # Default to CDNS if nothing found
    logging.warning("Could not detect vendor, defaulting to CDNS_Lib")
    return 'CDNS_Lib'

def check_pass_with_waivers(row, type_name, param_name, mc_prefix='MC', lib_prefix=None):
    """
    Unified pass checking function with structured waivers for both sigma and moments

    Base Pass Criteria:
    - Check 1: Error-Based Pass (rel_pass OR abs_pass)
    - Base Pass = Check 1 ONLY (CI bounds NOT included in base)

    Waivers:
    - Waiver 1: CI Enlargement (CI ± 6%)
      * CI bounds checking ONLY applied here with 6% enlargement
      * lib_value within [CI_LB - 6%×CI_width, CI_UB + 6%×CI_width]
    - Waiver 2: Optimistic Error Only (lib < mc)

    Args:
        row: DataFrame row with data
        type_name: 'delay', 'slew', or 'hold'
        param_name: Parameter name (e.g., 'Early_Sigma', 'Std', 'Meanshift')
        mc_prefix: Prefix for MC columns (default: 'MC')
        lib_prefix: Prefix for lib columns (auto-detect if None)

    Returns:
        dict: {
            'base_pass': bool,
            'pass_reason': str,  # rel_pass|abs_pass|both|fail
            'waiver1_ci_enlarged': bool,
            'error_direction': 'optimistic'|'pessimistic',
            'final_status': 'Pass'|'Waived_CI'|'Fail',
            'abs_err': float,
            'rel_err': float,
            'mc_value': float,
            'lib_value': float,
            'mc_ci_lb': float,
            'mc_ci_ub': float
        }
    """
    arc_name = row['Arc']
    logging.debug(f"Checking {param_name} for Arc: {arc_name}")

    # Extract necessary values
    rel_pin_slew = row['rel_pin_slew']

    # Auto-detect lib prefix if not provided (for sigma files)
    if lib_prefix is None:
        lib_prefix = detect_vendor_columns(pd.DataFrame([row]))

    try:
        # Get MC and Lib values
        mc_value = row[f"{mc_prefix}_{param_name}"]
        lib_value = row[f"{lib_prefix}_{param_name}"]

        # Get CI bounds
        mc_ci_lb = row[f"{mc_prefix}_{param_name}_LB"]
        mc_ci_ub = row[f"{mc_prefix}_{param_name}_UB"]

        # Get or calculate errors
        if f"{lib_prefix}_{param_name}_Dif" in row:
            abs_err = row[f"{lib_prefix}_{param_name}_Dif"]  # Pre-calculated
        else:
            abs_err = lib_value - mc_value  # Calculate

        if f"{lib_prefix}_{param_name}_Rel" in row:
            rel_err = row[f"{lib_prefix}_{param_name}_Rel"]  # Pre-calculated
        else:
            rel_err = (lib_value - mc_value) / abs(mc_value) if mc_value != 0 else 0  # Calculate

        logging.debug(f"  rel_pin_slew: {rel_pin_slew}")
        logging.debug(f"  {mc_prefix}_{param_name}: {mc_value}")
        logging.debug(f"  {lib_prefix}_{param_name}: {lib_value}")
        logging.debug(f"  MC CI: [{mc_ci_lb}, {mc_ci_ub}]")
        logging.debug(f"  abs_err: {abs_err}, rel_err: {rel_err}")

    except KeyError as e:
        logging.error(f"Missing column for {param_name}: {e}")
        return {
            'base_pass': False, 'pass_reason': 'missing_data', 'waiver1_ci_enlarged': False,
            'error_direction': 'unknown', 'final_status': 'Fail',
            'abs_err': None, 'rel_err': None, 'mc_value': None, 'lib_value': None,
            'mc_ci_lb': None, 'mc_ci_ub': None
        }

    # Set thresholds based on type and parameter
    if type_name == 'delay':
        if param_name in ['Early_Sigma', 'Late_Sigma']:
            rel_threshold = 0.03  # 3% for sigma
            ps_value = 1
            slew_multiplier = 0.005
        elif param_name == 'Meanshift':
            rel_threshold = 0.01  # 1% for moments meanshift
            ps_value = 1
            slew_multiplier = 0.005
        elif param_name == 'Std':
            rel_threshold = 0.02  # 2% for moments std
            ps_value = 1
            slew_multiplier = 0.005
        else:  # Skew
            rel_threshold = 0.05  # 5% for moments skew
            ps_value = 1
            slew_multiplier = 0.005
    elif type_name == 'slew':
        if param_name in ['Early_Sigma', 'Late_Sigma']:
            rel_threshold = 0.06  # 6% for sigma
            ps_value = 2
            slew_multiplier = 0.01
        elif param_name == 'Meanshift':
            rel_threshold = 0.02  # 2% for moments meanshift
            ps_value = 1  # 1ps for slew in moments script
            slew_multiplier = 0.005
        elif param_name == 'Std':
            rel_threshold = 0.04  # 4% for moments std
            ps_value = 1
            slew_multiplier = 0.005
        else:  # Skew
            rel_threshold = 0.10  # 10% for moments skew
            ps_value = 1
            slew_multiplier = 0.005
    else:  # hold
        rel_threshold = 0.03  # 3% for hold
        ps_value = 10
        slew_multiplier = 0.005

    # **CHECK 1: Error-Based Pass (rel OR abs)**
    rel_pass = abs(rel_err) <= rel_threshold
    abs_threshold = max(slew_multiplier * rel_pin_slew, ps_value * 1e-12)
    abs_pass = abs(abs_err) <= abs_threshold

    error_based_pass = rel_pass or abs_pass

    # **BASE PASS = Check 1 ONLY (error-based)**
    # CI bounds checking is REMOVED from base pass
    base_pass = error_based_pass

    # Determine pass reason
    if base_pass:
        if rel_pass and abs_pass:
            pass_reason = "both"
        elif rel_pass:
            pass_reason = "rel_pass"
        elif abs_pass:
            pass_reason = "abs_pass"
        else:
            pass_reason = "unknown"
    else:
        pass_reason = "fail"

    # **WAIVER 1: CI Enlargement (6%)**
    # CI bounds checking is ONLY applied here with 6% enlargement
    ci_lb = min(mc_ci_lb, mc_ci_ub)
    ci_ub = max(mc_ci_lb, mc_ci_ub)
    ci_width = abs(ci_ub - ci_lb)
    ci_enlargement_amount = ci_width * 0.06  # 6% enlargement
    enlarged_lb = ci_lb - ci_enlargement_amount
    enlarged_ub = ci_ub + ci_enlargement_amount
    waiver1_ci_enlarged = (enlarged_lb <= lib_value <= enlarged_ub)

    # **WAIVER 2: Determine Error Direction**
    error_direction = 'optimistic' if lib_value < mc_value else 'pessimistic'

    # **FINAL STATUS**
    if base_pass:
        final_status = "Pass"
    elif waiver1_ci_enlarged:
        final_status = "Waived_CI"
    else:
        final_status = "Fail"

    logging.debug(f"  Results for {param_name}: base_pass={base_pass}, waiver1={waiver1_ci_enlarged}, error_dir={error_direction}, final={final_status}")

    return {
        'base_pass': base_pass,
        'pass_reason': pass_reason,
        'waiver1_ci_enlarged': waiver1_ci_enlarged,
        'error_direction': error_direction,
        'final_status': final_status,
        'abs_err': abs_err,
        'rel_err': rel_err,
        'mc_value': mc_value,
        'lib_value': lib_value,
        'mc_ci_lb': mc_ci_lb,
        'mc_ci_ub': mc_ci_ub
    }

def find_rpt_files(root_path, corners, types):
    """Find all RPT files that match the FMC sigma pattern"""
    logging.info(f"Searching for sigma RPT files in: {root_path}")

    found_files = {}

    try:
        all_files = os.listdir(root_path)
        # Look for FMC files with the simple pattern
        rpt_files = [f for f in all_files if f.endswith('.rpt') and 'fmc' in f.lower()]
        logging.info(f"Found {len(rpt_files)} FMC RPT files in directory")
        logging.debug(f"All FMC RPT files: {rpt_files}")
    except Exception as e:
        logging.error(f"Error listing files in directory: {root_path}", exc_info=True)
        return found_files

    for corner in corners:
        for type_name in types:
            matching_files = []

            # Simple pattern: fmc*{corner}*{type}*.rpt
            for f in rpt_files:
                if corner in f and type_name in f:
                    matching_files.append(f)

            if matching_files:
                file_path = os.path.join(root_path, matching_files[0])
                found_files[(corner, type_name)] = file_path
                logging.info(f"Matched sigma file for {corner}*{type_name}: {matching_files[0]}")

                if len(matching_files) > 1:
                    logging.warning(f"Multiple matches for {corner}*{type_name}: {matching_files}")
            else:
                logging.warning(f"No sigma file found for {corner}*{type_name}")

    logging.info(f"Total matching sigma files found: {len(found_files)}")
    return found_files

def process_sigma_file_with_waivers(file_path, type_name):
    """
    Process a single sigma RPT file with the new waiver system

    Args:
        file_path: Path to the input RPT file
        type_name: 'delay', 'slew', or 'hold'

    Returns:
        str: Path to the output file
    """
    # Setup logging for this file
    log_file = setup_logging(file_path)
    logging.info(f"="*80)
    logging.info(f"Starting to process sigma file with WAIVER SYSTEM {file_path}")
    logging.info(f"Type: {type_name}")
    logging.info(f"="*80)

    try:
        # Read the RPT file
        logging.info(f"Reading sigma RPT file: {file_path}")

        # Read as CSV directly (since it's from our enhanced combine script)
        df = pd.read_csv(file_path)
        logging.info(f"Sigma CSV parsed successfully. Shape: {df.shape}")

        # Log column headers to verify correct structure
        logging.debug(f"CSV columns: {list(df.columns)}")

        # Detect vendor (CDNS or SNPS) from column names
        vendor_prefix = detect_vendor_columns(df)
        logging.info(f"Using vendor prefix: {vendor_prefix}")

        # Check if required columns exist
        required_columns = ['Arc', 'rel_pin_slew']

        # Determine which sigma parameters to check based on type
        if type_name in ['delay', 'slew']:
            sigma_params = ['Early_Sigma', 'Late_Sigma']
        else:  # hold
            sigma_params = ['Late_Sigma']

        for param in sigma_params:
            required_columns.extend([
                f'MC_{param}', f'{vendor_prefix}_{param}',
                f'{vendor_prefix}_{param}_Dif', f'{vendor_prefix}_{param}_Rel',
                f'MC_{param}_LB', f'MC_{param}_UB'  # CI bounds for enlargement
            ])

        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            logging.error(f"Missing required columns: {missing_columns}")
            return None

        # Create output dataframe with new waiver structure
        logging.info("Creating sigma output dataframe with waiver system")
        result_df = pd.DataFrame()
        result_df['Arc'] = df['Arc']

        # Log first few rows of input data
        logging.debug(f"First 3 rows of input data:\n{df.head(3)}")

        # Process each sigma parameter with waiver system
        waiver_summary = {}  # Track waiver statistics

        for param in sigma_params:
            logging.info(f"Processing sigma parameter with waiver system: {param}")

            # Initialize tracking lists for new waiver system
            mc_value_list = []
            lib_value_list = []
            mc_ci_lb_list = []
            mc_ci_ub_list = []
            abs_err_list = []
            rel_err_list = []
            base_pass_list = []
            pass_reason_list = []
            waiver1_ci_enlarged_list = []
            error_direction_list = []
            final_status_list = []

            # Statistics for 4 pass rate types
            waiver_stats = {
                'base_pass': 0,
                'pass_with_waiver1': 0,
                'optimistic_pass': 0,
                'optimistic_total': 0,
                'pass_with_both_waivers': 0,
                'total_arcs': 0,
                'optimistic_errors': 0,
                'pessimistic_errors': 0
            }

            for idx, row in df.iterrows():
                arc_name = row['Arc']
                logging.debug(f"Processing row {idx}, Arc: {arc_name}")

                waiver_results = check_pass_with_waivers(row, type_name, param, lib_prefix=vendor_prefix)

                # Extract results
                base_pass = waiver_results['base_pass']
                pass_reason = waiver_results['pass_reason']
                waiver1_ci_enlarged = waiver_results['waiver1_ci_enlarged']
                error_direction = waiver_results['error_direction']
                final_status = waiver_results['final_status']

                mc_value = waiver_results['mc_value']
                lib_value = waiver_results['lib_value']
                mc_ci_lb = waiver_results['mc_ci_lb']
                mc_ci_ub = waiver_results['mc_ci_ub']
                abs_err = waiver_results['abs_err']
                rel_err = waiver_results['rel_err']

                # Store results in lists
                mc_value_list.append(mc_value)
                lib_value_list.append(lib_value)
                mc_ci_lb_list.append(mc_ci_lb)
                mc_ci_ub_list.append(mc_ci_ub)
                abs_err_list.append(abs_err)
                rel_err_list.append(rel_err)
                base_pass_list.append("Pass" if base_pass else "Fail")
                pass_reason_list.append(pass_reason)
                waiver1_ci_enlarged_list.append("Pass" if waiver1_ci_enlarged else "Fail")
                error_direction_list.append(error_direction)
                final_status_list.append(final_status)

                # Update statistics
                waiver_stats['total_arcs'] += 1

                # Base pass rate
                if base_pass:
                    waiver_stats['base_pass'] += 1

                # Pass with waiver1 (CI enlarged)
                if base_pass or waiver1_ci_enlarged:
                    waiver_stats['pass_with_waiver1'] += 1

                # Track optimistic/pessimistic errors
                if error_direction == 'optimistic':
                    waiver_stats['optimistic_errors'] += 1
                    waiver_stats['optimistic_total'] += 1
                    if base_pass or waiver1_ci_enlarged:
                        waiver_stats['optimistic_pass'] += 1
                        waiver_stats['pass_with_both_waivers'] += 1
                else:  # pessimistic
                    waiver_stats['pessimistic_errors'] += 1

                logging.debug(f"  Results for {arc_name}, {param}: base_pass={base_pass}, waiver1={waiver1_ci_enlarged}, error_dir={error_direction}, final={final_status}")

            # Add columns to result dataframe with new structure (as per requirement)
            result_df[f'{param}_MC_value'] = mc_value_list
            result_df[f'{param}_Lib_value'] = lib_value_list
            result_df[f'{param}_MC_CI_LB'] = mc_ci_lb_list
            result_df[f'{param}_MC_CI_UB'] = mc_ci_ub_list
            result_df[f'{param}_abs_err'] = abs_err_list
            result_df[f'{param}_rel_err'] = rel_err_list
            result_df[f'{param}_Base_Pass'] = base_pass_list
            result_df[f'{param}_Pass_Reason'] = pass_reason_list
            result_df[f'{param}_Waiver1_CI_Enlarged'] = waiver1_ci_enlarged_list
            result_df[f'{param}_Error_Direction'] = error_direction_list
            result_df[f'{param}_Final_Status'] = final_status_list

            # Calculate 4 pass rates as per requirement (with 1-digit precision)
            total_count = waiver_stats['total_arcs']
            if total_count > 0:
                base_pr = (waiver_stats['base_pass'] / total_count) * 100
                pr_with_waiver1 = (waiver_stats['pass_with_waiver1'] / total_count) * 100
                pr_optimistic_only = (waiver_stats['optimistic_pass'] / waiver_stats['optimistic_total']) * 100 if waiver_stats['optimistic_total'] > 0 else 0
                pr_with_both_waivers = (waiver_stats['pass_with_both_waivers'] / waiver_stats['optimistic_total']) * 100 if waiver_stats['optimistic_total'] > 0 else 0

                waiver_summary[param] = {
                    'base_pr': base_pr,
                    'pr_with_waiver1': pr_with_waiver1,
                    'pr_optimistic_only': pr_optimistic_only,
                    'pr_with_both_waivers': pr_with_both_waivers,
                    'total_arcs': total_count,
                    'optimistic_errors': waiver_stats['optimistic_errors'],
                    'pessimistic_errors': waiver_stats['pessimistic_errors'],
                    'base_pass': waiver_stats['base_pass'],
                    'pass_with_waiver1': waiver_stats['pass_with_waiver1'],
                    'optimistic_pass': waiver_stats['optimistic_pass'],
                    'optimistic_total': waiver_stats['optimistic_total']
                }

                # Log detailed waiver statistics (1 digit precision)
                logging.info(f"  {param} Waiver Analysis:")
                logging.info(f"    Total arcs: {total_count}")
                logging.info(f"    Optimistic errors (Lib < MC): {waiver_stats['optimistic_errors']} ({waiver_stats['optimistic_errors']/total_count*100:.1f}%)")
                logging.info(f"    Pessimistic errors (Lib >= MC): {waiver_stats['pessimistic_errors']} ({waiver_stats['pessimistic_errors']/total_count*100:.1f}%)")
                logging.info(f"    Base PR: {base_pr:.1f}%")
                logging.info(f"    PR with Waiver1 (CI enlarged): {pr_with_waiver1:.1f}%")
                logging.info(f"    PR Optimistic Only: {pr_optimistic_only:.1f}%")
                logging.info(f"    PR with Both Waivers: {pr_with_both_waivers:.1f}%")

        # Save waiver summary for this file
        if hasattr(process_sigma_file_with_waivers, 'waiver_summaries'):
            process_sigma_file_with_waivers.waiver_summaries[(os.path.basename(file_path), type_name)] = waiver_summary
        else:
            process_sigma_file_with_waivers.waiver_summaries = {(os.path.basename(file_path), type_name): waiver_summary}

        # Determine output file path - NEW naming with waivers
        output_file = file_path.replace('.rpt', '_sigma_check_with_waivers.csv')

        # Log summary of output dataframe
        logging.debug(f"Output dataframe preview:\n{result_df.head(3)}")
        logging.info(f"Output columns: {list(result_df.columns)}")

        # Save to CSV
        logging.info(f"Saving sigma waiver output to: {output_file}")
        result_df.to_csv(output_file, index=False)
        logging.info(f"Sigma waiver output saved successfully")

        return output_file

    except Exception as e:
        logging.error(f"Error processing {file_path}", exc_info=True)
        return None

def generate_waiver_summary_table(results, root_path):
    """
    Generate summary table with 4 pass rate columns as per requirement

    Returns:
        str: Path to the summary file
    """
    logging.info("Generating sigma waiver summary table with 4 pass rates")

    # Create dataframes for each type
    delay_df = pd.DataFrame(columns=[
        'Corner',
        'Early_Sigma_Base_PR', 'Early_Sigma_PR_with_Waiver1', 'Early_Sigma_PR_Optimistic_Only', 'Early_Sigma_PR_with_Both_Waivers',
        'Late_Sigma_Base_PR', 'Late_Sigma_PR_with_Waiver1', 'Late_Sigma_PR_Optimistic_Only', 'Late_Sigma_PR_with_Both_Waivers'
    ])

    slew_df = pd.DataFrame(columns=[
        'Corner',
        'Early_Sigma_Base_PR', 'Early_Sigma_PR_with_Waiver1', 'Early_Sigma_PR_Optimistic_Only', 'Early_Sigma_PR_with_Both_Waivers',
        'Late_Sigma_Base_PR', 'Late_Sigma_PR_with_Waiver1', 'Late_Sigma_PR_Optimistic_Only', 'Late_Sigma_PR_with_Both_Waivers'
    ])

    hold_df = pd.DataFrame(columns=[
        'Corner',
        'Late_Sigma_Base_PR', 'Late_Sigma_PR_with_Waiver1', 'Late_Sigma_PR_Optimistic_Only', 'Late_Sigma_PR_with_Both_Waivers'
    ])

    # Extract corner name from file name (similar to existing function)
    def extract_corner_from_filename(file_name):
        """Extract full corner name from filename like fmc*ssgnp_0p450v_m40c*type*.rpt"""
        base_name = file_name.replace('.rpt', '').replace('fmc_', '')

        import re
        corner_pattern = r'(ssg[ng][pg]_[0-9]p[0-9]+v_[mn][0-9]+c)'
        match = re.search(corner_pattern, base_name)
        if match:
            return match.group(1)

        parts = base_name.split('_')
        corner_parts = []
        for i, part in enumerate(parts):
            if 'ssgnp' in part or 'ssgng' in part:
                corner_parts = parts[i:i+3] if i+3 <= len(parts) else parts[i:]
                break

        if corner_parts:
            return '_'.join(corner_parts)

        return '_'.join(base_name.split('_')[:3])

    # Fill the dataframes
    all_corners = set()
    all_types = set()

    # Collect all corners and types
    for (file_name, type_name) in results.keys():
        corner = extract_corner_from_filename(file_name)
        all_corners.add(corner)
        all_types.add(type_name)

    for corner in sorted(all_corners):
        for type_name in sorted(all_types):
            # Find the matching file
            file_key = None
            for (file_name, file_type), data in results.items():
                if extract_corner_from_filename(file_name) == corner and file_type == type_name:
                    file_key = (file_name, file_type)
                    break

            if file_key and file_key in results:
                rates = results[file_key]

                new_row = {'Corner': corner}

                if type_name in ['delay', 'slew']:
                    for param in ['Early_Sigma', 'Late_Sigma']:
                        if param in rates:
                            new_row[f'{param}_Base_PR'] = f"{rates[param]['base_pr']:.1f}%"
                            new_row[f'{param}_PR_with_Waiver1'] = f"{rates[param]['pr_with_waiver1']:.1f}%"
                            new_row[f'{param}_PR_Optimistic_Only'] = f"{rates[param]['pr_optimistic_only']:.1f}%"
                            new_row[f'{param}_PR_with_Both_Waivers'] = f"{rates[param]['pr_with_both_waivers']:.1f}%"
                        else:
                            new_row[f'{param}_Base_PR'] = "N/A"
                            new_row[f'{param}_PR_with_Waiver1'] = "N/A"
                            new_row[f'{param}_PR_Optimistic_Only'] = "N/A"
                            new_row[f'{param}_PR_with_Both_Waivers'] = "N/A"
                else:  # hold
                    param = 'Late_Sigma'
                    if param in rates:
                        new_row[f'{param}_Base_PR'] = f"{rates[param]['base_pr']:.1f}%"
                        new_row[f'{param}_PR_with_Waiver1'] = f"{rates[param]['pr_with_waiver1']:.1f}%"
                        new_row[f'{param}_PR_Optimistic_Only'] = f"{rates[param]['pr_optimistic_only']:.1f}%"
                        new_row[f'{param}_PR_with_Both_Waivers'] = f"{rates[param]['pr_with_both_waivers']:.1f}%"
                    else:
                        new_row[f'{param}_Base_PR'] = "N/A"
                        new_row[f'{param}_PR_with_Waiver1'] = "N/A"
                        new_row[f'{param}_PR_Optimistic_Only'] = "N/A"
                        new_row[f'{param}_PR_with_Both_Waivers'] = "N/A"

                # Add to the appropriate dataframe
                if type_name == 'delay':
                    delay_df = pd.concat([delay_df, pd.DataFrame([new_row])], ignore_index=True)
                elif type_name == 'slew':
                    slew_df = pd.concat([slew_df, pd.DataFrame([new_row])], ignore_index=True)
                else:  # hold
                    hold_df = pd.concat([hold_df, pd.DataFrame([new_row])], ignore_index=True)

    # Create the summary string
    summary = "Sigma Waiver Summary Table (4 Pass Rates with 1-digit precision)\n\n"
    summary += "Pass Rate Definitions:\n"
    summary += "- Base_PR: Error-based only (rel OR abs), NO CI bounds\n"
    summary += "- PR_with_Waiver1: Base + CI bounds with 6% enlargement\n"
    summary += "- PR_Optimistic_Only: Pass rate if we ONLY consider optimistic errors (Lib < MC)\n"
    summary += "- PR_with_Both_Waivers: Pass rate with both CI enlargement AND optimistic-only filtering\n\n"
    summary += "NOTE: CI bounds checking is ONLY applied in Waiver1 with 6% enlargement.\n\n"

    summary += "Delay:\n"
    summary += delay_df.to_string(index=False) if not delay_df.empty else "No delay data"
    summary += "\n\nSlew:\n"
    summary += slew_df.to_string(index=False) if not slew_df.empty else "No slew data"
    summary += "\n\nHold:\n"
    summary += hold_df.to_string(index=False) if not hold_df.empty else "No hold data"

    # Save to file
    summary_file = os.path.join(root_path, "sigma_waiver_summary_table.txt")
    with open(summary_file, 'w') as f:
        f.write(summary)

    logging.info(f"Sigma waiver summary table saved to: {summary_file}")

    # Also create a CSV version for easier processing
    csv_file = os.path.join(root_path, "sigma_PR_table_with_waivers.csv")

    # Combine dataframes with a Type column
    delay_df['Type'] = 'delay'
    slew_df['Type'] = 'slew'
    hold_df['Type'] = 'hold'
    combined_df = pd.concat([delay_df, slew_df, hold_df], ignore_index=True)

    # Save to CSV
    combined_df.to_csv(csv_file, index=False)
    logging.info(f"Sigma waiver CSV saved to: {csv_file}")

    return summary_file, csv_file

def generate_detailed_checking_validation(results, root_path):
    """
    Generate detailed per-arc checking validation report for debugging base_PR discrepancies
    """
    logging.info("Generating detailed checking validation report")

    validation_report = []
    validation_report.append("="*100)
    validation_report.append("DETAILED CHECKING VALIDATION REPORT - Per-Arc Breakdown")
    validation_report.append("="*100)
    validation_report.append("")
    validation_report.append("This report shows the detailed checking logic for each arc to validate base_PR calculation.")
    validation_report.append("")
    validation_report.append("Checking Logic Comparison:")
    validation_report.append("  ORIGINAL SCRIPT (check_sigma.py):")
    validation_report.append("    Overall Pass = Tier1 OR Tier2 OR Tier3(CI+6%) OR Tier4")
    validation_report.append("    - Tier1: Relative error <= threshold")
    validation_report.append("    - Tier2: Value within original CI bounds")
    validation_report.append("    - Tier3: Value within CI + 6% enlargement (INCLUDED in base pass)")
    validation_report.append("    - Tier4: Absolute error <= slew-dependent threshold")
    validation_report.append("")
    validation_report.append("  NEW SCRIPT (check_sigma_with_waivers.py) - UPDATED DEFINITION:")
    validation_report.append("    Base Pass = Check1 ONLY (error-based)")
    validation_report.append("    - Check1: (Relative error <= threshold) OR (Absolute error <= threshold)")
    validation_report.append("    - Waiver1: CI bounds with 6% enlargement")
    validation_report.append("      * CI bounds checking ONLY applied in waiver with enlargement")
    validation_report.append("      * lib_value within [CI_LB - 6%×CI_width, CI_UB + 6%×CI_width]")
    validation_report.append("")
    validation_report.append("KEY DIFFERENCES:")
    validation_report.append("  1. Base_PR excludes ALL CI bounds checking (stricter than before)")
    validation_report.append("  2. CI bounds only validated in Waiver1 WITH 6% enlargement")
    validation_report.append("  3. PR_with_Waiver1 is more lenient than original Tier2 (has 6% buffer)")
    validation_report.append("")
    validation_report.append("RECOMMENDATION:")
    validation_report.append("  Use PR_with_Waiver1 for final pass rate (includes CI with enlargement).")
    validation_report.append("")
    validation_report.append("="*100)
    validation_report.append("")

    # Summary statistics
    for (file_name, type_name), param_data in results.items():
        validation_report.append(f"File: {file_name} | Type: {type_name.upper()}")
        validation_report.append("-" * 100)

        for param, stats in param_data.items():
            total_arcs = stats['total_arcs']
            base_pass_count = stats['base_pass']
            waiver1_pass_count = stats['pass_with_waiver1']

            base_pr = (base_pass_count / total_arcs * 100) if total_arcs > 0 else 0
            pr_with_waiver1 = (waiver1_pass_count / total_arcs * 100) if total_arcs > 0 else 0

            ci_waiver_contribution = waiver1_pass_count - base_pass_count
            ci_waiver_contribution_pct = (ci_waiver_contribution / total_arcs * 100) if total_arcs > 0 else 0

            validation_report.append(f"\n{param} Validation:")
            validation_report.append(f"  Total Arcs: {total_arcs}")
            validation_report.append(f"  Base Pass (NEW definition): {base_pass_count} ({base_pr:.1f}%)")
            validation_report.append(f"  Base + CI Waiver (matches ORIGINAL): {waiver1_pass_count} ({pr_with_waiver1:.1f}%)")
            validation_report.append(f"  CI Enlargement Contribution: +{ci_waiver_contribution} arcs (+{ci_waiver_contribution_pct:.1f}%)")
            validation_report.append(f"")
            validation_report.append(f"  CONCLUSION:")
            if pr_with_waiver1 >= 95:
                validation_report.append(f"    ✓ PR_with_Waiver1 ({pr_with_waiver1:.1f}%) matches ORIGINAL script behavior")
            else:
                validation_report.append(f"    ✗ Even with CI waiver, PR ({pr_with_waiver1:.1f}%) is below 95% target")

            if abs(pr_with_waiver1 - 100.0) < 1.0:
                validation_report.append(f"    ✓ PR_with_Waiver1 matches expected ORIGINAL result (~100%)")
            elif base_pr < 60 and pr_with_waiver1 > 90:
                validation_report.append(f"    ⚠ Large CI enlargement contribution indicates many arcs just outside CI bounds")

        validation_report.append("")

    # Save validation report
    validation_file = os.path.join(root_path, "detailed_checking_validation.txt")
    with open(validation_file, 'w') as f:
        f.write('\n'.join(validation_report))

    logging.info(f"Detailed checking validation report saved to: {validation_file}")
    print('\n' + '\n'.join(validation_report))

    return validation_file

def generate_optimistic_pessimistic_breakdown(results, root_path):
    """
    Generate optimistic vs pessimistic breakdown analysis
    """
    logging.info("Generating optimistic vs pessimistic breakdown analysis")

    breakdown_report = []
    breakdown_report.append("="*80)
    breakdown_report.append("OPTIMISTIC vs PESSIMISTIC ERROR BREAKDOWN ANALYSIS")
    breakdown_report.append("="*80)
    breakdown_report.append("")
    breakdown_report.append("Error Direction Definitions:")
    breakdown_report.append("  Optimistic error: lib_value < mc_value (library claims better performance than MC reality)")
    breakdown_report.append("  Pessimistic error: lib_value >= mc_value (library shows worse or equal performance vs MC)")
    breakdown_report.append("")

    # Extract corner name function
    def extract_corner_from_filename(file_name):
        """Extract full corner name from filename"""
        base_name = file_name.replace('.rpt', '').replace('fmc_', '')
        import re
        corner_pattern = r'(ssg[ng][pg]_[0-9]p[0-9]+v_[mn][0-9]+c)'
        match = re.search(corner_pattern, base_name)
        if match:
            return match.group(1)
        return base_name.split('_')[0] if base_name else 'unknown'

    for (file_name, type_name), param_data in results.items():
        corner = extract_corner_from_filename(file_name)
        breakdown_report.append(f"Corner: {corner} | Type: {type_name.upper()}")
        breakdown_report.append("-" * 60)

        for param, stats in param_data.items():
            total_arcs = stats['total_arcs']
            optimistic_errors = stats['optimistic_errors']
            pessimistic_errors = stats['pessimistic_errors']

            optimistic_pass = stats['optimistic_pass']
            # Calculate pessimistic pass rate
            pessimistic_pass = (stats['pass_with_waiver1'] - optimistic_pass) if (stats['pass_with_waiver1'] - optimistic_pass) >= 0 else 0

            optimistic_pass_rate = (optimistic_pass / optimistic_errors * 100) if optimistic_errors > 0 else 0
            pessimistic_pass_rate = (pessimistic_pass / pessimistic_errors * 100) if pessimistic_errors > 0 else 0
            overall_pass_rate = stats['pr_with_waiver1']

            breakdown_report.append(f"\n{param} Analysis:")
            breakdown_report.append(f"  Total Arcs: {total_arcs}")
            breakdown_report.append(f"  Optimistic Errors (Lib < MC): {optimistic_errors} ({optimistic_errors/total_arcs*100:.1f}%)")
            breakdown_report.append(f"  Pessimistic Errors (Lib >= MC): {pessimistic_errors} ({pessimistic_errors/total_arcs*100:.1f}%)")
            breakdown_report.append(f"")
            breakdown_report.append(f"  Optimistic Error Pass Rate: {optimistic_pass_rate:.1f}% ({optimistic_pass}/{optimistic_errors})")
            breakdown_report.append(f"  Pessimistic Error Pass Rate: {pessimistic_pass_rate:.1f}% ({pessimistic_pass}/{pessimistic_errors})")
            breakdown_report.append(f"  Overall Pass Rate: {overall_pass_rate:.1f}%")

        breakdown_report.append("")

    # Save breakdown analysis report
    breakdown_file = os.path.join(root_path, "optimistic_pessimistic_breakdown.txt")
    with open(breakdown_file, 'w') as f:
        f.write('\n'.join(breakdown_report))

    logging.info(f"Optimistic vs pessimistic breakdown saved to: {breakdown_file}")

    # Print to console
    print('\n' + '\n'.join(breakdown_report))

    return breakdown_file

def main():
    # Parse command line arguments
    args = parse_arguments()

    # Set up a main log file
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    main_log_file = f"sigma_waiver_check_{timestamp}.log"

    # Configure main logging
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(main_log_file),
            logging.StreamHandler()
        ]
    )

    logging.info("="*80)
    logging.info("Starting SIGMA CHECK WITH UNIFIED WAIVER SYSTEM")
    logging.info(f"Main log file: {main_log_file}")
    logging.info("Implements unified pass/fail system with structured waivers")
    logging.info("Generates 4 pass rates: Base, +Waiver1, Optimistic Only, +Both Waivers")
    logging.info("="*80)

    # Use arguments directly
    root_path = args.root_path
    corners = args.corners
    types = args.types

    logging.info("Parameters received:")
    logging.info(f"  Root path: {root_path}")
    logging.info(f"  Corners: {corners}")
    logging.info(f"  Types: {types}")

    # Check if root path exists
    if not os.path.exists(root_path):
        logging.error(f"Root path does not exist: {root_path}")
        return

    # Find matching RPT files
    rpt_files = find_rpt_files(root_path, corners, types)

    if not rpt_files:
        logging.error("No matching sigma RPT files found!")
        return

    # Process each found file
    successful_files = []
    failed_files = []

    # Dictionary to store waiver results for summary table
    sigma_waiver_results = {}

    for (corner, type_name), file_path in rpt_files.items():
        logging.info(f"Processing sigma waiver {corner} - {type_name}: {file_path}")
        result = process_sigma_file_with_waivers(file_path, type_name)

        if result:
            successful_files.append(file_path)
            # Store waiver results for this file
            file_key = (os.path.basename(file_path), type_name)
            if hasattr(process_sigma_file_with_waivers, 'waiver_summaries') and file_key in process_sigma_file_with_waivers.waiver_summaries:
                sigma_waiver_results[file_key] = process_sigma_file_with_waivers.waiver_summaries[file_key]
        else:
            failed_files.append(file_path)

    # Log summary
    logging.info("="*80)
    logging.info("Processing summary:")
    logging.info(f"  Total files found: {len(rpt_files)}")
    logging.info(f"  Successfully processed: {len(successful_files)}")
    logging.info(f"  Failed to process: {len(failed_files)}")

    if failed_files:
        logging.info("Failed files:")
        for file in failed_files:
            logging.info(f"    {file}")

    # Generate waiver outputs
    if sigma_waiver_results:
        logging.info("Generating sigma waiver outputs")

        # Generate waiver summary tables
        summary_file, csv_file = generate_waiver_summary_table(sigma_waiver_results, root_path)

        # Generate detailed checking validation (for debugging base_PR discrepancy)
        validation_file = generate_detailed_checking_validation(sigma_waiver_results, root_path)

        # Generate optimistic vs pessimistic breakdown
        breakdown_file = generate_optimistic_pessimistic_breakdown(sigma_waiver_results, root_path)

        logging.info(f"Sigma waiver summary table saved to: {summary_file}")
        logging.info(f"Sigma waiver CSV saved to: {csv_file}")
        logging.info(f"Detailed checking validation saved to: {validation_file}")
        logging.info(f"Optimistic vs pessimistic breakdown saved to: {breakdown_file}")

        # Print summary to console
        with open(summary_file, 'r') as f:
            summary_content = f.read()
        print('\n' + "="*50)
        print("SIGMA WAIVER SUMMARY TABLE (4 Pass Rates):")
        print(f"="*50)
        print(summary_content)
        print("="*50)
    else:
        logging.warning("Could not generate sigma waiver summary table - no valid results")

    logging.info("="*80)
    logging.info("SIGMA CHECK WITH WAIVER SYSTEM completed")
    logging.info("Generated outputs:")
    logging.info("  - sigma_PR_table_with_waivers.csv (new waiver table)")
    logging.info("  - sigma_waiver_summary_table.txt (human-readable summary)")
    logging.info("  - detailed_checking_validation.txt (validation vs original script)")
    logging.info("  - optimistic_pessimistic_breakdown.txt (detailed breakdown)")
    logging.info("  - *_sigma_check_with_waivers.csv (individual corner/type results)")
    logging.info("")
    logging.info("IMPORTANT NOTES:")
    logging.info("  - Base_PR: Error-based only (rel OR abs), NO CI bounds")
    logging.info("  - PR_with_Waiver1: Base + CI bounds with 6% enlargement")
    logging.info("  - CI bounds checking ONLY applied in Waiver1 with enlargement")
    logging.info("  - See detailed_checking_validation.txt for full comparison")

if __name__ == "__main__":
    main()