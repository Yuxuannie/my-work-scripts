#!/usr/bin/env python3
"""
Verification script for 4-tier pass criteria implementation - CORRECTED rel_err calculation
"""
 
import os
import pandas as pd
import numpy as np
import argparse
import logging
import glob
 
def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
 
def find_data_file(corner_dir, pattern):
    """Find a data file using glob pattern."""
    files = glob.glob(os.path.join(corner_dir, pattern))
    if files:
        return files[0]  # Return first match
    return None
 
def calculate_rel_err(lib_val, mc_values, lib_nominal, param_name):
    """
    Calculate relative error using the correct denominator formulas.
 
    Formulas:
    - Meanshift = lib_nominal + meanshift_mc
    - Stddev = lib_nominal + meanshift_mc + stddev_mc
    - Skewness = lib_nominal + meanshift_mc + skewness_mc
    - Early_Sigma = max(abs(lib_nominal), MC_early_sigma)
    - Late_Sigma = max(abs(lib_nominal), MC_late_sigma)
    """
 
    # Determine parameter type
    param_lower = param_name.lower()
 
    if 'meanshift' in param_lower:
        # Meanshift denominator = lib_nominal + meanshift_mc
        if lib_nominal is not None and 'meanshift' in mc_values:
            denominator = lib_nominal + mc_values['meanshift']
            mc_val = mc_values['meanshift']
        else:
            return None, None, None
 
    elif 'std' in param_lower or 'stdev' in param_lower:
        # Stddev denominator = lib_nominal + meanshift_mc + stddev_mc
        if (lib_nominal is not None and 'meanshift' in mc_values and 'std' in mc_values):
            denominator = lib_nominal + mc_values['meanshift'] + mc_values['std']
            mc_val = mc_values['std']
        elif lib_nominal is not None and 'std' in mc_values:
            # Simplified if meanshift missing
            denominator = lib_nominal + mc_values['std']
            mc_val = mc_values['std']
        else:
            return None, None, None
 
    elif 'skew' in param_lower:
        # Skewness denominator = lib_nominal + meanshift_mc + skewness_mc
        if (lib_nominal is not None and 'meanshift' in mc_values and 'skew' in mc_values):
            denominator = lib_nominal + mc_values['meanshift'] + mc_values['skew']
            mc_val = mc_values['skew']
        elif lib_nominal is not None and 'skew' in mc_values:
            # Simplified if meanshift missing
            denominator = lib_nominal + mc_values['skew']
            mc_val = mc_values['skew']
        else:
            return None, None, None
 
    elif 'sigma' in param_lower:
        # Sigma denominator = max(abs(lib_nominal), MC_sigma)
        if 'sigma' in mc_values:
            if lib_nominal is not None:
                denominator = max(abs(lib_nominal), abs(mc_values['sigma']))
            else:
                denominator = abs(mc_values['sigma'])
            mc_val = mc_values['sigma']
        else:
            return None, None, None
    else:
        return None, None, None
 
    # Avoid division by zero
    if abs(denominator) < 1e-15:
        return None, None, None
 
    # Calculate relative error
    rel_err = (lib_val - mc_val) / denominator
 
    return rel_err, denominator, mc_val
 
def extract_mc_values_for_param(mc_data, idx, param_name):
    """Extract all relevant MC values for a parameter."""
    mc_values = {}
 
    # Find columns that might contain MC values we need
    for col in mc_data.columns:
        col_lower = col.lower()
 
        # Look for meanshift
        if 'meanshift' in col_lower and not col.endswith(('_LB', '_UB')):
            mc_values['meanshift'] = mc_data.iloc[idx][col]
 
        # Look for std/stdev
        elif ('std' in col_lower or 'stdev' in col_lower) and not col.endswith(('_LB', '_UB')):
            mc_values['std'] = mc_data.iloc[idx][col]
 
        # Look for skew
        elif 'skew' in col_lower and not col.endswith(('_LB', '_UB')):
            mc_values['skew'] = mc_data.iloc[idx][col]
 
        # Look for sigma (early or late)
        elif 'sigma' in col_lower and not col.endswith(('_LB', '_UB')):
            if param_name.lower() in col_lower:
                mc_values['sigma'] = mc_data.iloc[idx][col]
 
    return mc_values
 
def find_lib_nominal_column(lib_data, param_name):
    """Find the lib_nominal column for the parameter."""
    # Look for columns that might be nominal/mean values
    for col in lib_data.columns:
        col_lower = col.lower()
        if (param_name.lower() in col_lower and
            ('nominal' in col_lower or 'mean' in col_lower or
             (not any(term in col_lower for term in ['std', 'skew', 'sigma']) and not col.endswith(('_LB', '_UB'))))):
            return col
 
    # If no specific nominal column found, might be the main parameter column
    for col in lib_data.columns:
        if param_name.lower() in col.lower() and not col.endswith(('_LB', '_UB')):
            return col
 
    return None
 
def verify_4_tier_criteria(corner_dir, corner_name, type_name, param_name, sample_size=10):
    """
    Verify the 4-tier criteria implementation for a specific parameter.
    """
 
    print(f"\n{'='*80}")
    print(f"VERIFYING 4-TIER CRITERIA: {corner_name} {type_name} {param_name}")
    print(f"{'='*80}")
 
    # Define criteria
    criteria = {
        'delay': {
            'late_sigma': {'rel_threshold': 0.03, 'abs_coeff': 0.005, 'abs_min': 1e-12},
            'early_sigma': {'rel_threshold': 0.03, 'abs_coeff': 0.005, 'abs_min': 1e-12},
            'Std': {'rel_threshold': 0.02, 'abs_coeff': 0.005, 'abs_min': 1e-12},
            'Skew': {'rel_threshold': 0.05, 'abs_coeff': 0.005, 'abs_min': 1e-12},
            'Meanshift': {'rel_threshold': 0.01, 'abs_coeff': 0.005, 'abs_min': 1e-12}
        },
        'slew': {
            'late_sigma': {'rel_threshold': 0.06, 'abs_coeff': 0.01, 'abs_min': 2e-12},
            'early_sigma': {'rel_threshold': 0.06, 'abs_coeff': 0.01, 'abs_min': 2e-12},
            'Std': {'rel_threshold': 0.04, 'abs_coeff': 0.005, 'abs_min': 2e-12},
            'Skew': {'rel_threshold': 0.10, 'abs_coeff': 0.005, 'abs_min': 2e-12},
            'Meanshift': {'rel_threshold': 0.02, 'abs_coeff': 0.005, 'abs_min': 2e-12}
        }
    }
 
    if type_name not in criteria or param_name not in criteria[type_name]:
        print(f"ERROR: No criteria defined for {type_name} {param_name}")
        return False
 
    param_criteria = criteria[type_name][param_name]
 
    # Load data files
    mc_file = find_data_file(corner_dir, "*MC_data.csv")
    lib_file = find_data_file(corner_dir, "*Lib_data.csv")
    abs_err_file = find_data_file(corner_dir, "*abs_err_data.csv")
    rel_err_file = find_data_file(corner_dir, "*rel_err_data.csv")
    metadata_file = find_data_file(corner_dir, "*metadata_data.csv")
 
    print(f"Found data files:")
    print(f"  MC: {mc_file}")
    print(f"  Lib: {lib_file}")
    print(f"  abs_err: {abs_err_file}")
    print(f"  rel_err: {rel_err_file}")
    print(f"  metadata: {metadata_file}")
 
    # Load data files
    try:
        mc_data = pd.read_csv(mc_file)
        lib_data = pd.read_csv(lib_file)
        abs_err_data = pd.read_csv(abs_err_file)
        rel_err_data = pd.read_csv(rel_err_file)
 
        if metadata_file:
            metadata = pd.read_csv(metadata_file)
        else:
            metadata = pd.DataFrame()
 
    except Exception as e:
        print(f"ERROR loading data files: {e}")
        return False
 
    # Find parameter columns
    lib_col = None
    mc_col = None
    mc_lb_col = None
    mc_ub_col = None
    abs_err_col = None
    rel_err_col = None
    lib_nominal_col = None
 
    # Search for columns (case insensitive)
    param_patterns = [param_name.lower(), param_name.replace('_', ''), param_name.replace('_', ' ')]
 
    # Find lib column
    for col in lib_data.columns:
        for pattern in param_patterns:
            if pattern in col.lower():
                lib_col = col
                break
        if lib_col:
            break
 
    # Find lib_nominal column
    lib_nominal_col = find_lib_nominal_column(lib_data, param_name)
 
    # Find MC columns
    for col in mc_data.columns:
        for pattern in param_patterns:
            if pattern in col.lower():
                if col.endswith('_LB'):
                    mc_lb_col = col
                elif col.endswith('_UB'):
                    mc_ub_col = col
                elif not col.endswith(('_LB', '_UB')):
                    mc_col = col
 
    # Find abs_err column
    for col in abs_err_data.columns:
        for pattern in param_patterns:
            if pattern in col.lower():
                abs_err_col = col
                break
 
    # Find rel_err column (but we'll calculate it ourselves)
    for col in rel_err_data.columns:
        for pattern in param_patterns:
            if pattern in col.lower():
                rel_err_col = col
                break
 
    print(f"\nFound parameter columns:")
    print(f"  Lib: {lib_col}")
    print(f"  Lib_nominal: {lib_nominal_col}")
    print(f"  MC: {mc_col}")
    print(f"  MC_LB: {mc_lb_col}")
    print(f"  MC_UB: {mc_ub_col}")
    print(f"  abs_err: {abs_err_col}")
    print(f"  rel_err (CSV): {rel_err_col}")
 
    missing_cols = []
    if not lib_col:
        missing_cols.append("Lib")
    if not mc_col:
        missing_cols.append("MC")
    if not mc_lb_col:
        missing_cols.append("MC_LB")
    if not mc_ub_col:
        missing_cols.append("MC_UB")
    if not abs_err_col:
        missing_cols.append("abs_err")
 
    if missing_cols:
        print(f"ERROR: Missing required columns for {param_name}: {missing_cols}")
        return False
 
    # Get slew values
    if not metadata.empty and 'rel_pin_slew' in metadata.columns:
        slew_values = metadata['rel_pin_slew'].values
    else:
        print("WARNING: No rel_pin_slew found, using default 100ps")
        slew_values = np.full(len(lib_data), 100e-12)
 
    # Take a sample for verification
    max_sample = min(sample_size, len(lib_data))
    sample_indices = np.random.choice(len(lib_data), max_sample, replace=False)
    sample_indices = sorted(sample_indices)
 
    print(f"\n4-TIER CRITERIA FOR {param_name}:")
    print(f"  Relative threshold: +/-{param_criteria['rel_threshold']*100:.1f}%")
    print(f"  Absolute coefficient: {param_criteria['abs_coeff']}")
    print(f"  Absolute minimum: {param_criteria['abs_min']*1e12:.0f}ps")
 
    print(f"\nREL_ERR CALCULATION FORMULA FOR {param_name}:")
    if 'meanshift' in param_name.lower():
        print("  rel_err = (lib_val - mc_meanshift) / (lib_nominal + mc_meanshift)")
    elif 'std' in param_name.lower():
        print("  rel_err = (lib_val - mc_std) / (lib_nominal + mc_meanshift + mc_std)")
    elif 'skew' in param_name.lower():
        print("  rel_err = (lib_val - mc_skew) / (lib_nominal + mc_meanshift + mc_skew)")
    elif 'sigma' in param_name.lower():
        print("  rel_err = (lib_val - mc_sigma) / max(abs(lib_nominal), abs(mc_sigma))")
 
    print(f"\nVERIFYING {len(sample_indices)} SAMPLE POINTS:")
    print("-" * 180)
    print(f"{'Index':<8} {'Lib':<12} {'MC':<12} {'Lib_Nom':<12} {'Denominator':<12} {'rel_err_calc':<12} {'rel_err_csv':<12} {'CI_Min':<12} {'CI_Max':<12} {'abs_err':<12} {'T1':<3} {'T2':<3} {'T3':<3} {'T4':<3} {'Pass':<4}")
    print("-" * 180)
 
    pass_count = 0
    tier_passes = {'T1': 0, 'T2': 0, 'T3': 0, 'T4': 0}
    rel_err_matches = 0
 
    for idx in sample_indices:
        try:
            # Get values
            lib_val = lib_data.iloc[idx][lib_col]
            mc_val = mc_data.iloc[idx][mc_col]
            mc_lb_val = mc_data.iloc[idx][mc_lb_col]
            mc_ub_val = mc_data.iloc[idx][mc_ub_col]
            abs_err_val = abs_err_data.iloc[idx][abs_err_col]
            slew_val = slew_values[idx] if idx < len(slew_values) else 100e-12
 
            # Get lib_nominal
            lib_nominal = None
            if lib_nominal_col:
                lib_nominal = lib_data.iloc[idx][lib_nominal_col]
 
            # Get rel_err from CSV for comparison
            rel_err_csv = None
            if rel_err_col:
                rel_err_csv = rel_err_data.iloc[idx][rel_err_col]
 
            # Extract MC values for calculation
            mc_values = extract_mc_values_for_param(mc_data, idx, param_name)
 
            # Calculate rel_err properly
            rel_err_calc, denominator, mc_param_val = calculate_rel_err(lib_val, mc_values, lib_nominal, param_name)
 
            # Check if calculated rel_err matches CSV rel_err
            if rel_err_calc is not None and rel_err_csv is not None:
                if abs(rel_err_calc - rel_err_csv) < 0.001:  # Within 0.1%
                    rel_err_matches += 1
 
            # Use calculated rel_err for tier evaluation
            rel_err_to_use = rel_err_calc if rel_err_calc is not None else rel_err_csv
 
            # Handle cases where LB > UB
            ci_min = min(mc_lb_val, mc_ub_val)
            ci_max = max(mc_lb_val, mc_ub_val)
 
            # Apply 4-tier criteria
            # Tier 1: Relative error check
            tier1_pass = False
            if rel_err_to_use is not None:
                tier1_pass = abs(rel_err_to_use) <= param_criteria['rel_threshold']
 
            # Tier 2: MC confidence interval check
            tier2_pass = ci_min <= lib_val <= ci_max
 
            # Tier 3: Enlarged CI check (6% expansion)
            enlarged_min = ci_min * 0.94
            enlarged_max = ci_max * 1.06
            tier3_pass = enlarged_min <= lib_val <= enlarged_max
 
            # Tier 4: Absolute error check
            abs_threshold = max(param_criteria['abs_coeff'] * slew_val, param_criteria['abs_min'])
            tier4_pass = abs(abs_err_val) <= abs_threshold
 
            # Overall pass (ANY tier passes)
            overall_pass = tier1_pass or tier2_pass or tier3_pass or tier4_pass
 
            # Count passes
            if overall_pass:
                pass_count += 1
            if tier1_pass:
                tier_passes['T1'] += 1
            if tier2_pass:
                tier_passes['T2'] += 1
            if tier3_pass:
                tier_passes['T3'] += 1
            if tier4_pass:
                tier_passes['T4'] += 1
 
            # Print row
            rel_err_calc_str = f"{rel_err_calc:.4f}" if rel_err_calc is not None else "N/A"
            rel_err_csv_str = f"{rel_err_csv:.4f}" if rel_err_csv is not None else "N/A"
            denominator_str = f"{denominator:.6g}" if denominator is not None else "N/A"
            lib_nom_str = f"{lib_nominal:.6g}" if lib_nominal is not None else "N/A"
 
            print(f"{idx:<8} {lib_val:<12.6g} {mc_val:<12.6g} {lib_nom_str:<12} {denominator_str:<12} "
                  f"{rel_err_calc_str:<12} {rel_err_csv_str:<12} {ci_min:<12.6g} {ci_max:<12.6g} {abs_err_val:<12.6g} "
                  f"{'Y' if tier1_pass else 'N':<3} {'Y' if tier2_pass else 'N':<3} "
                  f"{'Y' if tier3_pass else 'N':<3} {'Y' if tier4_pass else 'N':<3} "
                  f"{'Y' if overall_pass else 'N':<4}")
 
        except Exception as e:
            print(f"ERROR processing index {idx}: {e}")
            continue
 
    print("-" * 180)
    print(f"\nSUMMARY:")
    print(f"  Total points: {len(sample_indices)}")
    print(f"  Overall pass rate: {pass_count}/{len(sample_indices)} ({pass_count/len(sample_indices)*100:.1f}%)")
    print(f"  Tier 1 passes (rel_err <= +/-{param_criteria['rel_threshold']*100:.1f}%): {tier_passes['T1']} ({tier_passes['T1']/len(sample_indices)*100:.1f}%)")
    print(f"  Tier 2 passes (within MC CI): {tier_passes['T2']} ({tier_passes['T2']/len(sample_indices)*100:.1f}%)")
    print(f"  Tier 3 passes (within enlarged CI): {tier_passes['T3']} ({tier_passes['T3']/len(sample_indices)*100:.1f}%)")
    print(f"  Tier 4 passes (abs_err <= threshold): {tier_passes['T4']} ({tier_passes['T4']/len(sample_indices)*100:.1f}%)")
    print(f"  rel_err calculation matches CSV: {rel_err_matches}/{len(sample_indices)}")
 
    return True
 
def main():
    parser = argparse.ArgumentParser(description='Verify 4-tier criteria implementation')
    parser.add_argument('--corner_dir', required=True, help='Path to corner directory')
    parser.add_argument('--param', default='late_sigma', help='Parameter to verify (default: late_sigma)')
    parser.add_argument('--sample_size', type=int, default=10, help='Number of sample points to verify (default: 10)')
 
    args = parser.parse_args()
 
    setup_logging()
 
    # Extract corner and type from directory name
    dir_name = os.path.basename(args.corner_dir)
    parts = dir_name.split('_')
    corner_name = '_'.join(parts[:-1])
    type_name = parts[-1]
 
    print(f"Verifying 4-tier criteria implementation")
    print(f"Corner directory: {args.corner_dir}")
    print(f"Corner: {corner_name}")
    print(f"Type: {type_name}")
    print(f"Parameter: {args.param}")
 
    success = verify_4_tier_criteria(args.corner_dir, corner_name, type_name, args.param, args.sample_size)
 
    if success:
        print(f"\nSUCCESS: 4-tier criteria verification completed")
    else:
        print(f"\nFAILED: 4-tier criteria verification failed")
 
if __name__ == "__main__":
    main()
