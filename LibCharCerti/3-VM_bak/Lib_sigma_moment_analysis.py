#!/usr/bin/env python3
 
import os
import glob
import argparse
import pandas as pd
import numpy as np
import json
import logging
import traceback
import sys
import re
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)
 
def setup_logging(output_dir):
    """Set up logging to file."""
    os.makedirs(output_dir, exist_ok=True)
    log_file = os.path.join(output_dir, "lib_analysis.log")
 
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s',
        filename=log_file,
        filemode='w'
    )
 
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
    logging.getLogger('').addHandler(console)
 
def parse_args():
    parser = argparse.ArgumentParser(description='Analyze library-only timing files for sigma vs moments correlations')
    parser.add_argument('--input_path', type=str, required=True, help='Path to input files')
    parser.add_argument('--output_dir', type=str, required=True, help='Output directory for results')
    return parser.parse_args()
 
def extract_corner_info(file_path):
    """Extract corner and voltage information from file name."""
    file_name = os.path.basename(file_path)
 
    # Extract corner pattern (e.g., ssgnp_0p450v_m40c)
    corner_match = re.search(r'((?:ss|ff|tt|fs|sf)[gnp]*_0p\d+v_[mp]\d+c)', file_name)
    corner = corner_match.group(1) if corner_match else "unknown_corner"
 
    # Extract voltage value
    voltage_match = re.search(r'_0p(\d+)v_', corner)
    voltage = float(f"0.{voltage_match.group(1)}") if voltage_match else 0.0
 
    logging.info(f"Detected - Corner: {corner}, Voltage: {voltage}V")
 
    return corner, voltage
 
def find_timing_files(input_path):
    """Find all timing files in the input directory."""
    # Try multiple extensions
    all_files = []
    for ext in ['.csv', '.txt', '.rpt']:
        pattern = os.path.join(input_path, f"*{ext}")
        files = glob.glob(pattern)
        all_files.extend(files)
 
    logging.info(f"Found {len(all_files)} timing files")
    return all_files
 
def find_matching_column(df, possible_names):
    """Find a column that matches one of the possible names, case-insensitive."""
    df_cols_lower = [col.lower() for col in df.columns]
 
    for name in possible_names:
        # Try exact match first
        if name in df.columns:
            return name
 
        # Try case-insensitive match
        name_lower = name.lower()
        if name_lower in df_cols_lower:
            idx = df_cols_lower.index(name_lower)
            return df.columns[idx]
 
    return None
 
def ensure_dir_exists(dir_path):
    """Ensure directory exists, with proper case handling."""
    if not dir_path:
        return dir_path
 
    # Create all directories in the path
    try:
        os.makedirs(dir_path, exist_ok=True)
        logging.debug(f"Ensured directory exists: {dir_path}")
    except Exception as e:
        logging.error(f"Error creating directory {dir_path}: {e}")
        logging.error(f"This may be a case sensitivity issue or permissions problem.")
 
    return dir_path
 
def parse_timing_file(file_path):
    """Parse timing file into DataFrame."""
    logging.info(f"Parsing file: {os.path.basename(file_path)}")
 
    if not os.path.exists(file_path):
        logging.error(f"File does not exist: {file_path}")
        return None
 
    try:
        # Try to read the CSV file directly
        df = pd.read_csv(file_path)
        logging.info(f"Successfully read file. Shape: {df.shape}")
 
        # Print all column names for debugging
        logging.info(f"Available columns: {df.columns.tolist()}")
 
        # Convert numeric columns - try to convert all columns
        for col in df.columns:
            try:
                if col not in ['Nominal_Type', 'Arc']:  # Skip non-numeric columns
                    df[col] = pd.to_numeric(df[col])
                    logging.debug(f"Converted {col} to numeric")
            except Exception:
                pass
 
        return df
    except Exception as e:
        logging.error(f"Error parsing file {file_path}: {e}")
        logging.error(traceback.format_exc())
 
        # Try with different delimiters
        try:
            df = pd.read_csv(file_path, sep=None, engine='python')  # Auto-detect delimiter
            logging.info(f"Successfully read file with auto-detected delimiter. Shape: {df.shape}")
            return df
        except Exception as e2:
            logging.error(f"Error parsing with auto-detected delimiter: {e2}")
            return None
 
def get_nominal_type_column(df):
    """Find the column that contains nominal type information (delay vs slew)."""
    nominal_type_col = find_matching_column(df, [
        'Nominal_Type', 'NominalType', 'nominal_type', 'type', 'Type'
    ])
 
    if not nominal_type_col:
        logging.warning("No Nominal_Type column found. Using the first column as default.")
        if len(df.columns) > 0:
            nominal_type_col = df.columns[0]
 
    logging.info(f"Using '{nominal_type_col}' as Nominal_Type column")
    return nominal_type_col
 
def separate_delay_slew(df, nominal_type_col):
    """Separate delay and slew data based on the Nominal_Type column."""
    delay_df = pd.DataFrame()
    slew_df = pd.DataFrame()
 
    # Check if nominal_type_col exists
    if nominal_type_col not in df.columns:
        logging.error(f"Nominal_Type column '{nominal_type_col}' not found in dataframe")
        return delay_df, slew_df
 
    # Get unique values in the nominal_type_col
    unique_types = df[nominal_type_col].unique()
    logging.info(f"Found {len(unique_types)} unique types: {unique_types}")
 
    # Find delay and slew values
    delay_keywords = ['cell_rise', 'cell_fall', 'rise', 'fall', 'delay']
    slew_keywords = ['transition', 'slew', 'rise_transition', 'fall_transition']
 
    # Use sets to avoid duplicates
    delay_types = set()
    slew_types = set()
 
    for t in unique_types:
        t_lower = str(t).lower()
 
        is_delay = any(keyword in t_lower for keyword in delay_keywords)
        is_slew = any(keyword in t_lower for keyword in slew_keywords)
 
        if is_delay and not is_slew:
            delay_types.add(t)
        elif is_slew and not is_delay:
            slew_types.add(t)
        elif 'rise' in t_lower and 'transition' not in t_lower:
            # If "rise" but not "transition", assume delay
            delay_types.add(t)
        elif 'fall' in t_lower and 'transition' not in t_lower:
            # If "fall" but not "transition", assume delay
            delay_types.add(t)
        elif 'transition' in t_lower:
            # If "transition", assume slew
            slew_types.add(t)
 
    logging.info(f"Identified delay types: {delay_types}")
    logging.info(f"Identified slew types: {slew_types}")
 
    # If we couldn't identify delay or slew types, try manual mapping
    if not delay_types and not slew_types:
        logging.warning("Couldn't automatically identify delay and slew types. Using manual mapping.")
 
        for t in unique_types:
            t_str = str(t)
            if t_str.endswith('rise') or t_str.endswith('fall'):
                delay_types.add(t)
            else:
                slew_types.add(t)
 
        logging.info(f"Manual mapping - delay types: {delay_types}")
        logging.info(f"Manual mapping - slew types: {slew_types}")
 
    # Create delay and slew dataframes
    if delay_types:
        delay_df = df[df[nominal_type_col].isin(delay_types)].copy()
        logging.info(f"Created delay dataframe with shape: {delay_df.shape}")
 
    if slew_types:
        slew_df = df[df[nominal_type_col].isin(slew_types)].copy()
        logging.info(f"Created slew dataframe with shape: {slew_df.shape}")
 
    return delay_df, slew_df
 
def analyze_lib_correlations(df):
    """Analyze correlations between sigma values and library moments."""
    results = {'late_sigma': {}, 'early_sigma': {}}
 
    # Try to find matching columns for each required field
    std_col = find_matching_column(df, [
        'Standard_Deviation', 'Std', 'Std_Dev', 'StdDev', 'std',
        'Standard Deviation', 'standard_deviation'
    ])
 
    skew_col = find_matching_column(df, [
        'Skewness', 'Skew', 'skew', 'skewness'
    ])
 
    late_sigma_col = find_matching_column(df, [
        'Late_Sigma', 'late_sigma', 'Late Sigma', 'late sigma',
        'LateSigma', 'latesigma', 'Late', 'late'
    ])
 
    early_sigma_col = find_matching_column(df, [
        'Early_Sigma', 'early_sigma', 'Early Sigma', 'early sigma',
        'EarlySigma', 'earlysigma', 'Early', 'early'
    ])
 
    # Log found columns
    logging.info(f"Found columns - STD: {std_col}, SKEW: {skew_col}, "
                 f"LATE_SIGMA: {late_sigma_col}, EARLY_SIGMA: {early_sigma_col}")
 
    # Check if we have enough columns to proceed
    if not std_col and not skew_col:
        logging.error("Missing required columns: No Standard_Deviation or Skewness found")
        return results
 
    if not late_sigma_col and not early_sigma_col:
        logging.error("Missing required columns: No Early_Sigma or Late_Sigma found")
        return results
 
    # Map found columns to moment types
    moment_cols = {}
    if std_col:
        moment_cols['std'] = std_col
    if skew_col:
        moment_cols['skew'] = skew_col
 
    # Analyze Late_Sigma correlations
    if late_sigma_col:
        for moment_type, col_name in moment_cols.items():
            try:
                valid_data = df[[late_sigma_col, col_name]].dropna()
                if len(valid_data) > 1:
                    corr = valid_data[late_sigma_col].corr(valid_data[col_name])
                    results['late_sigma'][moment_type] = corr
                    logging.info(f"Late_Sigma vs {moment_type} correlation: {corr:.4f}")
            except Exception as e:
                logging.error(f"Error calculating Late_Sigma vs {moment_type} correlation: {e}")
 
    # Analyze Early_Sigma correlations
    if early_sigma_col:
        for moment_type, col_name in moment_cols.items():
            try:
                valid_data = df[[early_sigma_col, col_name]].dropna()
                if len(valid_data) > 1:
                    corr = valid_data[early_sigma_col].corr(valid_data[col_name])
                    results['early_sigma'][moment_type] = corr
                    logging.info(f"Early_Sigma vs {moment_type} correlation: {corr:.4f}")
            except Exception as e:
                logging.error(f"Error calculating Early_Sigma vs {moment_type} correlation: {e}")
 
    # Store the found columns for reference
    results['found_columns'] = {
        'std': std_col,
        'skew': skew_col,
        'late_sigma': late_sigma_col,
        'early_sigma': early_sigma_col
    }
 
    return results
 
def save_correlation_results(results, output_dir, corner, type_name):
    """Save correlation results to file."""
    # Ensure the output directory exists
    ensure_dir_exists(output_dir)
 
    output_file = os.path.join(output_dir, f"{corner}_{type_name}_lib_correlations.json")
 
    try:
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
 
        logging.info(f"Saved correlation results to {output_file}")
    except Exception as e:
        logging.error(f"Error saving correlation results: {e}")
        logging.error(f"Attempted to save to: {output_file}")
 
    return output_file
 
def create_correlation_tables(all_results, output_dir):
    """Create correlation tables organized by type, sigma and moment."""
    # Create tables for each combination of type and sigma
    tables = {
        'delay': {'late_sigma': pd.DataFrame(), 'early_sigma': pd.DataFrame()},
        'slew': {'late_sigma': pd.DataFrame(), 'early_sigma': pd.DataFrame()}
    }
 
    # Process each result
    for corner, type_name, result in all_results:
        # Skip unknown types
        if type_name not in ['delay', 'slew']:
            continue
 
        for sigma_type in ['late_sigma', 'early_sigma']:
            if sigma_type in result and result[sigma_type]:
                # Get correlation values for each moment type
                for moment_type in ['std', 'skew']:
                    if moment_type in result[sigma_type]:
                        corr_value = result[sigma_type][moment_type]
 
                        # Add to table
                        if corner not in tables[type_name][sigma_type].index:
                            tables[type_name][sigma_type].loc[corner, moment_type] = corr_value
                        else:
                            tables[type_name][sigma_type].at[corner, moment_type] = corr_value
 
    # Save tables
    for type_name in ['delay', 'slew']:
        for sigma_type in ['late_sigma', 'early_sigma']:
            table = tables[type_name][sigma_type]
            if not table.empty:
                # Sort by index
                table = table.sort_index()
 
                # Fill NaN with empty string for better display
                table = table.fillna('')
 
                # Add a meanshift column (placeholder)
                if 'meanshift' not in table.columns:
                    table['meanshift'] = ''
 
                # Rearrange columns to match requested order
                table = table[['std', 'skew', 'meanshift']]
 
                # Ensure output directory exists
                ensure_dir_exists(output_dir)
 
                # Save as CSV
                csv_file = os.path.join(output_dir, f"{type_name}_{sigma_type}_correlations.csv")
                try:
                    table.to_csv(csv_file)
                    logging.info(f"Saved {type_name} {sigma_type} correlation table to {csv_file}")
                except Exception as e:
                    logging.error(f"Error saving correlation table to {csv_file}: {e}")
 
    return tables
 
def visualize_correlation_tables(tables, output_dir):
    """Create heatmap visualizations of correlation tables."""
    # Ensure output directory exists
    ensure_dir_exists(output_dir)
 
    for type_name in ['delay', 'slew']:
        for sigma_type in ['late_sigma', 'early_sigma']:
            table = tables[type_name][sigma_type]
            if not table.empty:
                # Create figure
                plt.figure(figsize=(10, max(6, len(table) * 0.5)))
 
                # Replace empty strings with NaN for visualization
                viz_table = table.replace('', np.nan)
 
                # Create heatmap
                sns.heatmap(viz_table, annot=True, cmap='coolwarm', center=0,
                           fmt='.4f', linewidths=0.5, vmin=-1, vmax=1,
                           cbar_kws={'label': 'Correlation'})
 
                plt.title(f"{type_name.capitalize()} {sigma_type.replace('_', ' ').title()} Correlations", fontsize=14)
                plt.tight_layout()
 
                # Save figure
                output_file = os.path.join(output_dir, f"{type_name}_{sigma_type}_heatmap.png")
                try:
                    plt.savefig(output_file, dpi=150)
                    plt.close()
                    logging.info(f"Created visualization for {type_name} {sigma_type} at {output_file}")
                except Exception as e:
                    logging.error(f"Error saving visualization to {output_file}: {e}")
                    plt.close()
 
def create_scatter_plots(df, output_dir, corner, type_name, columns):
    """Create scatter plots for sigma vs moment correlations."""
    scatter_dir = os.path.join(output_dir, f"{corner}_{type_name}_scatter_plots")
    # Ensure output directory exists
    ensure_dir_exists(scatter_dir)
 
    plots_created = 0
 
    # Get found columns
    std_col = columns.get('std')
    skew_col = columns.get('skew')
    late_sigma_col = columns.get('late_sigma')
    early_sigma_col = columns.get('early_sigma')
 
    # Check if we have enough columns
    if not std_col and not skew_col:
        logging.error(f"Missing required columns for scatter plots: No STD or SKEW columns")
        return scatter_dir
 
    if not late_sigma_col and not early_sigma_col:
        logging.error(f"Missing required columns for scatter plots: No LATE_SIGMA or EARLY_SIGMA columns")
        return scatter_dir
 
    # Create scatter plots
    for sigma_col, sigma_name in [(late_sigma_col, 'late_sigma'), (early_sigma_col, 'early_sigma')]:
        if not sigma_col:
            continue
 
        for moment_col, moment_name in [(std_col, 'std'), (skew_col, 'skew')]:
            if not moment_col:
                continue
 
            try:
                # Check for valid data
                valid_data = df[[sigma_col, moment_col]].dropna()
                if len(valid_data) <= 1:
                    logging.warning(f"Not enough valid data for {sigma_col} vs {moment_col}")
                    continue
 
                # Create figure
                plt.figure(figsize=(10, 8))
 
                # Create scatter plot
                plt.scatter(df[sigma_col], df[moment_col], alpha=0.6)
 
                # Add title and labels
                plt.title(f"{corner} {type_name} - {sigma_col} vs {moment_col}", fontsize=12)
                plt.xlabel(sigma_col)
                plt.ylabel(moment_col)
 
                # Add grid
                plt.grid(True, alpha=0.3)
 
                # Add regression line
                from scipy import stats
                slope, intercept, r_value, p_value, std_err = stats.linregress(
                    valid_data[sigma_col], valid_data[moment_col]
                )
                plt.plot(
                    valid_data[sigma_col],
                    intercept + slope * valid_data[sigma_col],
                    'r-'
                )
 
                # Add correlation info
                plt.text(0.05, 0.95, f"Correlation: {r_value:.4f}",
                        transform=plt.gca().transAxes, fontsize=10,
                        verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.7))
 
                # Save figure
                output_file = os.path.join(scatter_dir, f"{sigma_name}_vs_{moment_name}.png")
                try:
                    plt.savefig(output_file, dpi=150)
                    plt.close()
                    plots_created += 1
                except Exception as e:
                    logging.error(f"Error saving scatter plot to {output_file}: {e}")
                    plt.close()
 
            except Exception as e:
                logging.error(f"Error creating scatter plot for {sigma_col} vs {moment_col}: {e}")
 
    logging.info(f"Created {plots_created} scatter plots for {corner} {type_name}")
    return scatter_dir
 
def main():
    try:
        args = parse_args()
        setup_logging(args.output_dir)
 
        logging.info("Starting library-only correlation analysis")
 
        # Create output directory - making sure it exists
        ensure_dir_exists(args.output_dir)
 
        # Create separate directories for delay and slew
        delay_dir = os.path.join(args.output_dir, "delay_analysis")
        slew_dir = os.path.join(args.output_dir, "slew_analysis")
        ensure_dir_exists(delay_dir)
        ensure_dir_exists(slew_dir)
 
        # Create intermediate directories
        intermediate_dir = os.path.join(args.output_dir, "intermediate_data")
        ensure_dir_exists(intermediate_dir)
 
        visualization_dir = os.path.join(args.output_dir, "visualizations")
        ensure_dir_exists(visualization_dir)
 
        # Create separate visualization dirs for delay and slew
        delay_vis_dir = os.path.join(visualization_dir, "delay")
        slew_vis_dir = os.path.join(visualization_dir, "slew")
        ensure_dir_exists(delay_vis_dir)
        ensure_dir_exists(slew_vis_dir)
 
        # Find timing files
        files = find_timing_files(args.input_path)
 
        if not files:
            logging.error("No timing files found. Exiting.")
            return
 
        # Store all results for table creation
        all_results = []
 
        # Count files processed
        files_analyzed = 0
        delay_count = 0
        slew_count = 0
 
        # Process each file
        for file_path in files:
            # Extract corner information
            corner, voltage = extract_corner_info(file_path)
 
            logging.info(f"\nProcessing file: {file_path}")
            logging.info(f"Corner: {corner}, Voltage: {voltage}V")
 
            # Parse file
            df = parse_timing_file(file_path)
            if df is None or df.empty:
                continue
 
            # Find Nominal_Type column
            nominal_type_col = get_nominal_type_column(df)
 
            # Separate delay and slew data
            delay_df, slew_df = separate_delay_slew(df, nominal_type_col)
 
            # Save separated dataframes
            if not delay_df.empty:
                delay_data_dir = os.path.join(intermediate_dir, "delay")
                ensure_dir_exists(delay_data_dir)
                delay_df.to_csv(os.path.join(delay_data_dir, f"{corner}_delay_data.csv"), index=False)
                delay_count += 1
 
            if not slew_df.empty:
                slew_data_dir = os.path.join(intermediate_dir, "slew")
                ensure_dir_exists(slew_data_dir)
                slew_df.to_csv(os.path.join(slew_data_dir, f"{corner}_slew_data.csv"), index=False)
                slew_count += 1
 
            # Process delay data
            if not delay_df.empty:
                logging.info(f"\nAnalyzing delay data for {corner}")
                delay_results = analyze_lib_correlations(delay_df)
 
                # Create correlations directory
                delay_corr_dir = os.path.join(delay_dir, "correlations")
                ensure_dir_exists(delay_corr_dir)
 
                save_correlation_results(delay_results, delay_corr_dir, corner, "delay")
                all_results.append((corner, "delay", delay_results))
 
                # Create scatter plots
                if 'found_columns' in delay_results:
                    create_scatter_plots(delay_df, delay_vis_dir, corner, "delay", delay_results['found_columns'])
 
            # Process slew data
            if not slew_df.empty:
                logging.info(f"\nAnalyzing slew data for {corner}")
                slew_results = analyze_lib_correlations(slew_df)
 
                # Create correlations directory
                slew_corr_dir = os.path.join(slew_dir, "correlations")
                ensure_dir_exists(slew_corr_dir)
 
                save_correlation_results(slew_results, slew_corr_dir, corner, "slew")
                all_results.append((corner, "slew", slew_results))
 
                # Create scatter plots
                if 'found_columns' in slew_results:
                    create_scatter_plots(slew_df, slew_vis_dir, corner, "slew", slew_results['found_columns'])
 
            files_analyzed += 1
 
        # Create correlation tables
        tables = create_correlation_tables(all_results, args.output_dir)
 
        # Visualize correlation tables
        visualize_correlation_tables(tables, visualization_dir)
 
        logging.info("\nAnalysis complete!")
        logging.info(f"Files analyzed: {files_analyzed}")
        logging.info(f"Delay instances found: {delay_count}")
        logging.info(f"Slew instances found: {slew_count}")
        logging.info(f"Results saved to {args.output_dir}")
 
    except Exception as e:
        logging.error(f"Unhandled exception in main: {e}")
        logging.error(traceback.format_exc())
        sys.exit(1)
 
if __name__ == "__main__":
    main()
