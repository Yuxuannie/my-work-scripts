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
from pathlib import Path
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)
 
def setup_logging(output_dir):
    """Set up logging to file."""
    os.makedirs(output_dir, exist_ok=True)
    log_file = os.path.join(output_dir, "parser.log")
 
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
    parser = argparse.ArgumentParser(description='Parse timing files and analyze sigma vs moments correlations')
    parser.add_argument('--input_path', type=str, required=True, help='Path to input files')
    parser.add_argument('--corner', type=str, required=True, help='Corner to analyze')
    parser.add_argument('--type', type=str, required=True, help='Type to analyze (delay or slew)')
    parser.add_argument('--output_dir', type=str, required=True, help='Output directory for results')
    return parser.parse_args()
 
def find_timing_files(input_path, corner, type_name):
    """Find timing files matching the pattern."""
    pattern = os.path.join(input_path, f"MC*{corner}*{type_name}*.rpt")
    files = glob.glob(pattern)
    logging.info(f"Found {len(files)} files matching pattern: {pattern}")
 
    # Log all found files
    for file in files:
        logging.debug(f"Found file: {os.path.basename(file)}")
 
    # If no files found, try a more permissive search
    if not files:
        broader_pattern = os.path.join(input_path, f"*{corner}*{type_name}*.rpt")
        files = glob.glob(broader_pattern)
        logging.info(f"Broader search found {len(files)} files with pattern: {broader_pattern}")
 
    # Check input path existence and access
    if not os.path.exists(input_path):
        logging.error(f"Input path does not exist: {input_path}")
    elif not os.path.isdir(input_path):
        logging.error(f"Input path is not a directory: {input_path}")
    elif not os.access(input_path, os.R_OK):
        logging.error(f"Input path is not readable: {input_path}")
    else:
        try:
            # List directory contents for debugging
            for item in os.listdir(input_path):
                logging.debug(f"Directory item: {item}")
        except Exception as e:
            logging.error(f"Error listing directory contents: {e}")
 
    return files
 
def parse_arc_info(arc_string):
    """Parse Arc string to extract cell type and table position.
 
    Format: combinational_{cell}_{output_pin}_{output_pin_dir}_{input_pin}_{input_pin_dir}_{when_cond}_{index_1}-{index_2}
    Where {when_cond} may contain multiple underscores and index_1, index_2 are integers 1-8.
    """
    if not arc_string or not isinstance(arc_string, str):
        return {'cell': None, 'table_position': None, 'index_1': None, 'index_2': None}
 
    # Check if it's a typical arc format
    if not arc_string.startswith('combinational_'):
        return {'cell': None, 'table_position': None, 'index_1': None, 'index_2': None}
 
    try:
        # Extract the parts
        parts = arc_string.split('_')
 
        # First part after 'combinational_' is the cell
        cell = parts[1]
 
        # Table position is the last part (has format index_1-index_2)
        # It's the only part with a hyphen
        table_position = None
        index_1 = None
        index_2 = None
 
        for part in reversed(parts):
            if '-' in part:
                table_position = part
                idx_parts = part.split('-')
                if len(idx_parts) == 2:
                    try:
                        index_1 = int(idx_parts[0])
                        index_2 = int(idx_parts[1])
                        # Validate they're in range 1-8
                        if not (1 <= index_1 <= 8) or not (1 <= index_2 <= 8):
                            logging.warning(f"Index values out of range (1-8) in table position: {table_position}")
                    except ValueError:
                        logging.warning(f"Could not convert indices to integers in table position: {table_position}")
                break
 
        return {
            'cell': cell,
            'table_position': table_position,
            'index_1': index_1,
            'index_2': index_2
        }
    except Exception as e:
        logging.error(f"Error parsing Arc string '{arc_string}': {e}")
        return {'cell': None, 'table_position': None, 'index_1': None, 'index_2': None}
 
 
 
def extract_metadata(df):
    """Extract metadata from dataframe for correlation analysis."""
    metadata = {}
 
    # Extract arc information if available
    if 'Arc' in df.columns:
        metadata['arc_info'] = df['Arc'].copy()
 
        # Parse cell and table position information
        cell_info = []
        table_position_info = []
 
        for arc in df['Arc']:
            parsed = parse_arc_info(arc)
            cell_info.append(parsed['cell'])
            table_position_info.append(parsed['table_position'])
 
        metadata['cell'] = pd.Series(cell_info, index=df.index)
        metadata['table_position'] = pd.Series(table_position_info, index=df.index)
 
    # Extract table type information
    if 'Table_type' in df.columns:
        metadata['table_type'] = df['Table_type'].copy()
 
    return metadata
 
def parse_timing_file(file_path):
    """Parse timing file into DataFrame."""
    logging.info(f"Parsing file: {os.path.basename(file_path)}")
 
    if not os.path.exists(file_path):
        logging.error(f"File does not exist: {file_path}")
        return None
 
    try:
        # Read the first few lines to analyze structure
        with open(file_path, 'r') as f:
            first_lines = [f.readline().strip() for _ in range(min(5, sum(1 for _ in open(file_path))))]
 
        logging.debug(f"First few lines of the file:")
        for i, line in enumerate(first_lines):
            logging.debug(f"Line {i+1}: {line}")
 
        # Read the header to get column names
        with open(file_path, 'r') as f:
            header_line = f.readline().strip()
 
        logging.debug(f"Header line: {header_line}")
 
        # Split the header by comma to get column names
        columns = header_line.split(',')
        logging.debug(f"Detected {len(columns)} columns")
 
        # Try to read the file with pandas
        try:
            df = pd.read_csv(file_path, skiprows=1, names=columns)
            logging.info(f"Successfully read file with pandas. Shape: {df.shape}")
        except Exception as e:
            logging.warning(f"Error with standard parsing: {e}")
            logging.debug("Trying alternative parsing approach...")
 
            # Manual parsing as fallback
            data = []
            with open(file_path, 'r') as f:
                next(f)  # Skip header
                for line in f:
                    values = line.strip().split(',')
                    if len(values) == len(columns):
                        data.append(values)
 
            df = pd.DataFrame(data, columns=columns)
            logging.info(f"Created dataframe using manual parsing. Shape: {df.shape}")
 
        # Extract metadata before converting to numeric
        metadata = extract_metadata(df)
 
        # Convert numeric columns
        for col in df.columns:
            try:
                df[col] = pd.to_numeric(df[col])
                logging.debug(f"Converted column '{col}' to numeric")
            except Exception as e:
                logging.debug(f"Could not convert column '{col}' to numeric: {e}")
 
        # Add metadata back to dataframe
        if 'cell' in metadata:
            df['cell'] = metadata['cell']
        if 'table_position' in metadata:
            df['table_position'] = metadata['table_position']
 
        # Log some data samples
        logging.debug(f"Sample data from DataFrame:")
        if not df.empty:
            logging.debug(df.head(3).to_string())
 
        return df
    except Exception as e:
        logging.error(f"Error parsing file {file_path}: {e}")
        logging.error(traceback.format_exc())
        return None
 
def find_sigma_columns(df):
    """Find late_sigma and early_sigma columns in the dataframe."""
    # Look for late_sigma columns, excluding LB/UB
    late_cols = [col for col in df.columns if 'late' in col.lower() and 'sigma' in col.lower()
                and not '_LB' in col and not '_UB' in col]
 
    # Look for early_sigma columns, excluding LB/UB
    early_cols = [col for col in df.columns if 'early' in col.lower() and 'sigma' in col.lower()
                 and not '_LB' in col and not '_UB' in col]
 
    late_sigma = late_cols[0] if late_cols else None
    early_sigma = early_cols[0] if early_cols else None
 
    if late_sigma:
        logging.info(f"Found late_sigma column: {late_sigma}")
    else:
        logging.warning("No late_sigma column found")
 
    if early_sigma:
        logging.info(f"Found early_sigma column: {early_sigma}")
    else:
        logging.warning("No early_sigma column found")
 
    return late_sigma, early_sigma
 
 
 
def identify_outliers(df, column, threshold=2.0):
    """Identify outliers in a column using Z-score.
 
    Args:
        df: DataFrame containing the data
        column: Column name to check for outliers
        threshold: Z-score threshold (default: 2.0)
 
    Returns:
        Series with boolean values (True for outliers)
    """
    if column not in df.columns:
        return pd.Series(False, index=df.index)
 
    z_scores = np.abs((df[column] - df[column].mean()) / df[column].std())
    outliers = z_scores > threshold
 
    return outliers
# Add this function to the parse_timing_files.py script
def calculate_correlation_detailed(x, y, log_file_path=None):
    """Calculate Pearson correlation with detailed steps logged to a separate file.
 
    Args:
        x: Array-like of x values
        y: Array-like of y values
        log_file_path: Path to detailed log file (if None, no detailed logging)
 
    Returns:
        Correlation coefficient or None if calculation fails
    """
    # Setup separate logger for detailed correlation steps
    if log_file_path:
        import logging as detailed_logging
        detail_logger = detailed_logging.getLogger('correlation_details')
 
        # Remove existing handlers if any
        for handler in detail_logger.handlers[:]:
            detail_logger.removeHandler(handler)
 
        # Configure file handler
        fh = detailed_logging.FileHandler(log_file_path, mode='a')
        fh.setLevel(detailed_logging.DEBUG)
        fh.setFormatter(detailed_logging.Formatter('%(message)s'))
        detail_logger.setLevel(detailed_logging.DEBUG)
        detail_logger.addHandler(fh)
 
        # Add a separator for readability
        detail_logger.debug("\n" + "="*80)
        detail_logger.debug(f"CORRELATION CALCULATION DETAILS")
        detail_logger.debug("="*80)
    else:
        detail_logger = None
 
    # Remove NaN values
    valid_mask = ~np.isnan(x) & ~np.isnan(y)
    x_valid = x[valid_mask]
    y_valid = y[valid_mask]
 
    n = len(x_valid)
    if n <= 1:
        if detail_logger:
            detail_logger.debug("Not enough valid data points to calculate correlation")
        return None
 
    if detail_logger:
        detail_logger.debug(f"Number of valid data points: {n}")
        detail_logger.debug("\nSample data (first 5 points):")
        for i in range(min(5, n)):
            detail_logger.debug(f"  Point {i+1}: x = {x_valid[i]}, y = {y_valid[i]}")
 
    # Step 1: Calculate means
    x_mean = sum(x_valid) / n
    y_mean = sum(y_valid) / n
 
    if detail_logger:
        detail_logger.debug(f"\nStep 1: Calculate means")
        detail_logger.debug(f"  x_mean = sum({list(x_valid)[:min(5, n)]}, ...) / {n} = {x_mean}")
        detail_logger.debug(f"  y_mean = sum({list(y_valid)[:min(5, n)]}, ...) / {n} = {y_mean}")
 
    # Step 2: Calculate deviations from means
    x_dev = [xi - x_mean for xi in x_valid]
    y_dev = [yi - y_mean for yi in y_valid]
 
    if detail_logger:
        detail_logger.debug(f"\nStep 2: Calculate deviations from means")
        detail_logger.debug("  Sample deviations (first 5 items):")
        for i in range(min(5, n)):
            detail_logger.debug(f"    x_dev[{i}] = {x_valid[i]} - {x_mean} = {x_dev[i]}")
            detail_logger.debug(f"    y_dev[{i}] = {y_valid[i]} - {y_mean} = {y_dev[i]}")
 
    # Step 3: Calculate products of deviations
    products = [x_dev[i] * y_dev[i] for i in range(n)]
 
    if detail_logger:
        detail_logger.debug(f"\nStep 3: Calculate products of deviations")
        detail_logger.debug("  Sample products (first 5 items):")
        for i in range(min(5, n)):
            detail_logger.debug(f"    products[{i}] = {x_dev[i]} * {y_dev[i]} = {products[i]}")
 
    # Step 4: Calculate sum of products
    sum_products = sum(products)
 
    if detail_logger:
        detail_logger.debug(f"\nStep 4: Calculate sum of products")
        detail_logger.debug(f"  sum_products = sum({products[:min(5, n)]}, ...) = {sum_products}")
 
    # Step 5: Calculate squared deviations
    x_dev_squared = [x_dev[i] ** 2 for i in range(n)]
    y_dev_squared = [y_dev[i] ** 2 for i in range(n)]
 
    if detail_logger:
        detail_logger.debug(f"\nStep 5: Calculate squared deviations")
        detail_logger.debug("  Sample squared deviations (first 5 items):")
        for i in range(min(5, n)):
            detail_logger.debug(f"    x_dev_squared[{i}] = {x_dev[i]} ^ 2 = {x_dev_squared[i]}")
            detail_logger.debug(f"    y_dev_squared[{i}] = {y_dev[i]} ^ 2 = {y_dev_squared[i]}")
 
    # Step 6: Calculate sums of squared deviations
    sum_x_squared = sum(x_dev_squared)
    sum_y_squared = sum(y_dev_squared)
 
    if detail_logger:
        detail_logger.debug(f"\nStep 6: Calculate sums of squared deviations")
        detail_logger.debug(f"  sum_x_squared = sum({x_dev_squared[:min(5, n)]}, ...) = {sum_x_squared}")
        detail_logger.debug(f"  sum_y_squared = sum({y_dev_squared[:min(5, n)]}, ...) = {sum_y_squared}")
 
    # Step 7: Calculate correlation coefficient
    if sum_x_squared == 0 or sum_y_squared == 0:
        if detail_logger:
            detail_logger.debug(f"\nStep 7: Calculate correlation coefficient")
            detail_logger.debug("  Zero variance in x or y, correlation undefined")
            detail_logger.debug("  Returning correlation = 0")
        return 0
 
    correlation = sum_products / ((sum_x_squared ** 0.5) * (sum_y_squared ** 0.5))
 
    if detail_logger:
        detail_logger.debug(f"\nStep 7: Calculate correlation coefficient")
        detail_logger.debug(f"  correlation = {sum_products} / (sqrt({sum_x_squared}) * sqrt({sum_y_squared}))")
        detail_logger.debug(f"  correlation = {sum_products} / ({sum_x_squared ** 0.5} * {sum_y_squared ** 0.5})")
        detail_logger.debug(f"  correlation = {sum_products} / {(sum_x_squared ** 0.5) * (sum_y_squared ** 0.5)}")
        detail_logger.debug(f"  correlation = {correlation}")
 
        # Close the handler
        for handler in detail_logger.handlers[:]:
            handler.close()
            detail_logger.removeHandler(handler)
 
    return correlation
 
def extract_categories(df):
    """Extract the four categories of data plus essential metadata."""
    categories = {}
 
    # MC columns - FIXED: Now includes UB/LB for confidence intervals
    mc_cols = [col for col in df.columns if col.startswith('MC_')]
    if mc_cols:
        categories['MC'] = df[mc_cols].copy()
 
    # Lib only columns
    lib_cols = [col for col in df.columns if col.startswith('Lib_') and not 'err' in col.lower()]
    if lib_cols:
        categories['Lib'] = df[lib_cols].copy()
 
    # abs_err columns
    abs_err_cols = [col for col in df.columns if 'abs_err' in col.lower()]
    if abs_err_cols:
        categories['abs_err'] = df[abs_err_cols].copy()
 
    # rel_err columns
    rel_err_cols = [col for col in df.columns if 'rel_err' in col.lower()]
    if rel_err_cols:
        categories['rel_err'] = df[rel_err_cols].copy()
 
    # NEW: Essential metadata for 4-tier analysis
    metadata_cols = []
    essential_columns = ['rel_pin_slew', 'Arc', 'Table_type']
 
    for col in essential_columns:
        if col in df.columns:
            metadata_cols.append(col)
        else:
            # Check for case variations
            for df_col in df.columns:
                if col.lower() == df_col.lower():
                    metadata_cols.append(df_col)
                    break
 
    if metadata_cols:
        categories['metadata'] = df[metadata_cols].copy()
        logging.info(f"Preserved essential metadata columns: {metadata_cols}")
    else:
        logging.warning("No essential metadata columns found!")
 
    logging.info(f"Extracted {len(categories)} categories: {list(categories.keys())}")
 
    # Log MC columns to verify UB/LB inclusion
    if 'MC' in categories:
        mc_columns = categories['MC'].columns.tolist()
        ub_lb_cols = [col for col in mc_columns if col.endswith(('_UB', '_LB'))]
        logging.info(f"MC category includes {len(ub_lb_cols)} UB/LB columns: {ub_lb_cols}")
 
    return categories
 
def save_results(results, output_dir, file_name, late_sigma, early_sigma):
    """Save analysis results to files - UPDATED to handle metadata."""
    os.makedirs(output_dir, exist_ok=True)
 
    # Save correlation data
    correlations = {
        'late_sigma': {},
        'early_sigma': {}
    }
 
    # Save outliers data
    outliers = {
        'late_sigma': {},
        'early_sigma': {}
    }
 
    for category, results_data in results.items():
        # Skip metadata category for correlation analysis
        if category == 'metadata':
            continue
 
        if 'late_sigma' in results_data:
            correlations['late_sigma'][category] = results_data['late_sigma']
 
        if 'early_sigma' in results_data:
            correlations['early_sigma'][category] = results_data['early_sigma']
 
        # Save outliers information
        if 'outliers' in results_data:
            if category in ['abs_err', 'rel_err']:  # Only save for error categories
                outliers['late_sigma'][category] = results_data['outliers']['late_sigma']
                outliers['early_sigma'][category] = results_data['outliers']['early_sigma']
 
    # Save correlations to JSON
    with open(os.path.join(output_dir, f"{file_name}_correlations.json"), 'w') as f:
        json.dump(correlations, f, indent=2)
 
    logging.info(f"Saved correlation results to {file_name}_correlations.json")
 
    # Save outliers to JSON
    with open(os.path.join(output_dir, f"{file_name}_outliers.json"), 'w') as f:
        json.dump(outliers, f, indent=2)
 
    logging.info(f"Saved outliers results to {file_name}_outliers.json")
 
    # Save sigma column names
    sigma_info = {
        'late_sigma': late_sigma,
        'early_sigma': early_sigma
    }
 
    with open(os.path.join(output_dir, f"{file_name}_sigma_info.json"), 'w') as f:
        json.dump(sigma_info, f, indent=2)
 
    logging.info(f"Saved sigma column info to {file_name}_sigma_info.json")
 
    # Save a copy of the data for later visualization - UPDATED to handle all categories
    for category, results_data in results.items():
        df = results_data['data']
        df.to_csv(os.path.join(output_dir, f"{file_name}_{category}_data.csv"), index=False)
        logging.debug(f"Saved {category} data to CSV")
 
    # Save metadata about columns - UPDATED to handle metadata category
    metadata = {}
    for category, results_data in results.items():
        if category == 'metadata':
            # For metadata, just save column info
            metadata[category] = {
                'columns': list(results_data['data'].columns)
            }
        else:
            # For other categories, save moment column info
            metadata[category] = {
                'std_cols': results_data.get('std_cols', []),
                'skew_cols': results_data.get('skew_cols', []),
                'meanshift_cols': results_data.get('meanshift_cols', [])
            }
 
    with open(os.path.join(output_dir, f"{file_name}_metadata.json"), 'w') as f:
        json.dump(metadata, f, indent=2)
 
    logging.info(f"Saved metadata to {file_name}_metadata.json")
 
def analyze_correlations(categories, df, late_sigma, early_sigma, output_dir=None, file_name=None):
    """Analyze correlations between sigma values and moments - UPDATED to handle metadata."""
    results = {}
 
    # Create directory for detailed correlation logs if output_dir provided
    detailed_log_dir = None
    if output_dir and file_name:
        detailed_log_dir = os.path.join(output_dir, "detailed_correlations")
        os.makedirs(detailed_log_dir, exist_ok=True)
        logging.info(f"Detailed correlation logs will be saved to {detailed_log_dir}")
 
    # Skip if no sigma columns found
    if not late_sigma and not early_sigma:
        logging.error("No sigma columns found, skipping correlation analysis")
        return results
 
    # Extract metadata for outlier analysis
    metadata = {}
    if 'Arc' in df.columns:
        metadata['Arc'] = df['Arc']
    if 'Table_type' in df.columns:
        metadata['Table_type'] = df['Table_type']
    if 'cell' in df.columns:
        metadata['cell'] = df['cell']
    if 'table_position' in df.columns:
        metadata['table_position'] = df['table_position']
 
    for category_name, category_df in categories.items():
        # Skip metadata category for correlation analysis
        if category_name == 'metadata':
            # Store metadata for later use but don't analyze correlations
            results[category_name] = {
                'data': category_df,
                'metadata': metadata
            }
            continue
 
        logging.info(f"Analyzing correlations for category: {category_name}")
        category_results = {'late_sigma': {}, 'early_sigma': {}}
 
        # [Rest of the correlation analysis code remains the same...]
        # Find moment columns, excluding LB/UB variants
        std_cols = [col for col in category_df.columns if 'std' in col.lower()
                   and not col.endswith('_UB') and not col.endswith('_LB')]
        skew_cols = [col for col in category_df.columns if 'skew' in col.lower()
                    and not col.endswith('_UB') and not col.endswith('_LB')]
        meanshift_cols = [col for col in category_df.columns if 'meanshift' in col.lower()
                         and not col.endswith('_UB') and not col.endswith('_LB')]
 
        logging.debug(f"Found {len(std_cols)} STD columns, {len(skew_cols)} SKEW columns, "
                      f"and {len(meanshift_cols)} MEANSHIFT columns")
 
        # Add sigma columns to category dataframe if not already present
        if late_sigma and late_sigma not in category_df.columns:
            category_df[late_sigma] = df[late_sigma]
 
        if early_sigma and early_sigma not in category_df.columns:
            category_df[early_sigma] = df[early_sigma]
 
        # Add metadata columns to category dataframe
        for meta_key, meta_val in metadata.items():
            if meta_key not in category_df.columns:
                category_df[meta_key] = meta_val
 
        # Dictionary to store outlier information
        outliers_info = {'late_sigma': {}, 'early_sigma': {}}
 
        # [Correlation calculation code continues as before...]
        # Calculate late_sigma correlations with moments
        if late_sigma:
            for col in std_cols + skew_cols + meanshift_cols:
                try:
                    if len(category_df.dropna(subset=[col, late_sigma])) > 1:
                        # Create log file path for detailed correlation
                        log_file_path = None
                        if detailed_log_dir:
                            log_file_path = os.path.join(detailed_log_dir,
                                                       f"{file_name}_{category_name}_{late_sigma}_vs_{col}.log")
 
                        # Calculate correlation with detailed logging
                        corr = calculate_correlation_detailed(
                            category_df[late_sigma].values,
                            category_df[col].values,
                            log_file_path=log_file_path
                        )
 
                        if corr is not None:
                            category_results['late_sigma'][col] = corr
                            logging.debug(f"Correlation between {col} and {late_sigma}: {corr:.4f}")
 
                        # [Outlier analysis code continues as before...]
                    else:
                        logging.warning(f"Not enough data to calculate correlation for {col} and {late_sigma}")
                except Exception as e:
                    logging.error(f"Error calculating correlation for {col} and {late_sigma}: {e}")
                    logging.error(traceback.format_exc())
 
        # Calculate early_sigma correlations with moments
        if early_sigma:
            for col in std_cols + skew_cols + meanshift_cols:
                try:
                    if len(category_df.dropna(subset=[col, early_sigma])) > 1:
                        # Create log file path for detailed correlation
                        log_file_path = None
                        if detailed_log_dir:
                            log_file_path = os.path.join(detailed_log_dir,
                                                       f"{file_name}_{category_name}_{early_sigma}_vs_{col}.log")
 
                        # Calculate correlation with detailed logging
                        corr = calculate_correlation_detailed(
                            category_df[early_sigma].values,
                            category_df[col].values,
                            log_file_path=log_file_path
                        )
 
                        if corr is not None:
                            category_results['early_sigma'][col] = corr
                            logging.debug(f"Correlation between {col} and {early_sigma}: {corr:.4f}")
 
                        # [Outlier analysis code continues as before...]
                    else:
                        logging.warning(f"Not enough data to calculate correlation for {col} and {early_sigma}")
                except Exception as e:
                    logging.error(f"Error calculating correlation for {col} and {early_sigma}: {e}")
                    logging.error(traceback.format_exc())
 
        # Store column lists for later use
        category_results['std_cols'] = std_cols
        category_results['skew_cols'] = skew_cols
        category_results['meanshift_cols'] = meanshift_cols
        category_results['data'] = category_df
        category_results['metadata'] = metadata
        category_results['outliers'] = outliers_info
 
        results[category_name] = category_results
 
    return results
 
def main():
    try:
        args = parse_args()
        setup_logging(args.output_dir)
 
        logging.info(f"Starting analysis for corner: {args.corner}, type: {args.type}")
 
        # Create output directory
        os.makedirs(args.output_dir, exist_ok=True)
 
        # Find timing files
        files = find_timing_files(args.input_path, args.corner, args.type)
 
        if not files:
            logging.error("No timing files found. Exiting.")
            return
 
        # Process each file
        for file_path in files:
            file_name = os.path.basename(file_path).split('.')[0]
 
            # Parse file
            df = parse_timing_file(file_path)
            if df is None:
                continue
 
            # Find sigma columns
            late_sigma, early_sigma = find_sigma_columns(df)
 
            # Extract categories
            categories = extract_categories(df)
 
            # Analyze correlations - pass output_dir and file_name
            results = analyze_correlations(categories, df, late_sigma, early_sigma,
                                         args.output_dir, file_name)
 
            # Save results
            save_results(results, args.output_dir, file_name, late_sigma, early_sigma)
 
        logging.info("Analysis complete")
    except Exception as e:
        logging.error(f"Unhandled exception in main: {e}")
        logging.error(traceback.format_exc())
        sys.exit(1)
 
 
if __name__ == "__main__":
    main()
