def plot_sigma_analysis(results_data, output_dir, sampling_methods, sample_sizes):
    """Create plots specifically for analyzing sigma points and skewness"""
    logger.info("Creating 3-sigma analysis plots")
    create_directory(f"{output_dir}/plots")
   
    for metric in metrics_of_interest:
        logger.info(f"Creating 3-sigma analysis plots for {metric}")
       
        # 1. Early 3-sigma convergence plot
        plt.figure(figsize=(12, 8))
        for method in sampling_methods:
            early_3sigma_values = []
            for size in sample_sizes:
                key = f"{method}_{size}"
                if key in results_data and metric in results_data[key]:
                    data = results_data[key][metric]
                    if len(data) > 0:
                        mean_val = np.mean(data)
                        std_val = np.std(data)
                        early_3sigma = mean_val - 3 * std_val
                        early_3sigma_values.append((size, early_3sigma))
           
            if early_3sigma_values:
                sizes, values = zip(*early_3sigma_values)
                plt.plot(sizes, values, 'o-', label=f"{method} - Early 3Ïƒ")
       
        plt.xscale('log')
        plt.grid(True, which="both", ls="--", alpha=0.5)
        plt.xlabel('Sample Size')
        plt.ylabel(f'{metric} Early 3Ïƒ Value')
        plt.title(f'Convergence of {metric} Early 3-Sigma Point by Sample Size and Method')
        plt.legend()
        plt.tight_layout()
       
        plot_path = f"{output_dir}/plots/{metric}_early_3sigma_convergence.png"
        plt.savefig(plot_path)
        logger.info(f"  Saved early 3-sigma plot to {plot_path}")
        plt.close()
       
        # 2. Late 3-sigma convergence plot
        plt.figure(figsize=(12, 8))
        for method in sampling_methods:
            late_3sigma_values = []
            for size in sample_sizes:
                key = f"{method}_{size}"
                if key in results_data and metric in results_data[key]:
                    data = results_data[key][metric]
                    if len(data) > 0:
                        mean_val = np.mean(data)
                        std_val = np.std(data)
                        late_3sigma = mean_val + 3 * std_val
                        late_3sigma_values.append((size, late_3sigma))
           
            if late_3sigma_values:
                sizes, values = zip(*late_3sigma_values)
                plt.plot(sizes, values, 'o-', label=f"{method} - Late 3Ïƒ")
       
        plt.xscale('log')
        plt.grid(True, which="both", ls="--", alpha=0.5)
        plt.xlabel('Sample Size')
        plt.ylabel(f'{metric} Late 3Ïƒ Value')
        plt.title(f'Convergence of {metric} Late 3-Sigma Point by Sample Size and Method')
        plt.legend()
        plt.tight_layout()
       
        plot_path = f"{output_dir}/plots/{metric}_late_3sigma_convergence.png"
        plt.savefig(plot_path)
        logger.info(f"  Saved late 3-sigma plot to {plot_path}")
        plt.close()
       
        # 3. Skewness convergence plot
        plt.figure(figsize=(12, 8))
        for method in sampling_methods:
            skewness_values = []
            for size in sample_sizes:
                key = f"{method}_{size}"
                if key in results_data and metric in results_data[key]:
                    data = results_data[key][metric]
                    if len(data) > 0:
                        skew_val = stats.skew(data)
                        skewness_values.append((size, skew_val))
           
            if skewness_values:
                sizes, values = zip(*skewness_values)
                plt.plot(sizes, values, 'o-', label=f"{method} - Skewness")
       
        plt.xscale('log')
        plt.grid(True, which="both", ls="--", alpha=0.5)
        plt.xlabel('Sample Size')
        plt.ylabel(f'{metric} Skewness')
        plt.title(f'Convergence of {metric} Skewness by Sample Size and Method')
        plt.legend()
        plt.tight_layout()
       
        plot_path = f"{output_dir}/plots/{metric}_skewness_convergence.png"
        plt.savefig(plot_path)
        logger.info(f"  Saved skewness plot to {plot_path}")
        plt.close()
       
        # 4. 3-Sigma vs Actual Percentile Comparison (for largest sample size)
        largest_size = max(sample_sizes)
        plt.figure(figsize=(12, 8))
       
        x_positions = np.arange(len(sampling_methods))
        width = 0.35
       
        theoretical_early = []
        theoretical_late = []
        actual_early = []
        actual_late = []
       
        for method in sampling_methods:
            key = f"{method}_{largest_size}"
            if key in results_data and metric in results_data[key]:
                data = results_data[key][metric]
                if len(data) >= 500:  # Only if enough samples
                    mean_val = np.mean(data)
                    std_val = np.std(data)
                   
                    # Theoretical 3-sigma assuming normal distribution
                    theoretical_early.append(mean_val - 3 * std_val)
                    theoretical_late.append(mean_val + 3 * std_val)
                   
                    # Actual percentile-based (empirical) 3-sigma
                    actual_early.append(np.percentile(data, 0.13))
                    actual_late.append(np.percentile(data, 99.87))
                else:
                    theoretical_early.append(0)
                    theoretical_late.append(0)
                    actual_early.append(0)
                    actual_late.append(0)
       
        # Plot early 3-sigma comparison
        plt.subplot(1, 2, 1)
        plt.bar(x_positions - width/2, theoretical_early, width, label='Theoretical (Î¼-3Ïƒ)')
        plt.bar(x_positions + width/2, actual_early, width, label='Actual (0.13%)')
        plt.xlabel('Sampling Method')
        plt.ylabel(f'{metric} Early 3Ïƒ Value')
        plt.title('Early 3-Sigma Comparison')
        plt.xticks(x_positions, sampling_methods)
        plt.legend()
       
        # Plot late 3-sigma comparison
        plt.subplot(1, 2, 2)
        plt.bar(x_positions - width/2, theoretical_late, width, label='Theoretical (Î¼+3Ïƒ)')
        plt.bar(x_positions + width/2, actual_late, width, label='Actual (99.87%)')
        plt.xlabel('Sampling Method')
        plt.ylabel(f'{metric} Late 3Ïƒ Value')
        plt.title('Late 3-Sigma Comparison')
        plt.xticks(x_positions, sampling_methods)
        plt.legend()
       
        plt.tight_layout()
        plot_path = f"{output_dir}/plots/{metric}_3sigma_theory_vs_actual.png"
        plt.savefig(plot_path)
        logger.info(f"  Saved theory vs. actual 3-sigma comparison to {plot_path}")
        plt.close()#!/usr/bin/env python3
#=============================================================
# Monte Carlo Sampling Analysis Python Script
#=============================================================
 
import os
import sys
import re
import subprocess
import shutil
import glob
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats
import time
import argparse
import traceback
import logging
from datetime import datetime
 
# Default configuration (will be overridden by command line arguments if provided)
DEFAULT_SAMPLE_SIZES = [1000, 5000, 10000, 50000, 100000]  # Different sample sizes to test
DEFAULT_SAMPLING_METHODS = ['lhs', 'sobol', 'mc']  # Different sampling methods to test
metrics_of_interest = ['meas_delay', 'meas_tt_out']  # Metrics we care about
 
# Setup logging
def setup_logging(log_file=None):
    """Set up logging configuration"""
    log_format = '%(asctime)s - %(levelname)s - %(message)s'
   
    # Remove all handlers
    logger = logging.getLogger()
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
   
    # Configure the root logger
    logging.basicConfig(
        level=logging.DEBUG,  # Always use DEBUG level in the file
        format=log_format
    )
   
    # If log file provided, redirect all output to log file only
    if log_file:
        # Clear all handlers
        logger = logging.getLogger()
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
       
        # Add file handler
        file_handler = logging.FileHandler(log_file, mode='a')
        file_handler.setFormatter(logging.Formatter(log_format))
        logger.addHandler(file_handler)
   
    return logging.getLogger(__name__)
 
def log_section(section_name):
    """Log a section divider for better readability"""
    logger.info("")
    logger.info("----------------------------------------------")
    logger.info(f"  {section_name}")
    logger.info("----------------------------------------------")
 
def setup_environment():
    """Set up environment for HSPICE if not done in shell script"""
    # Check if environment was set up in shell
    env_setup_in_shell = os.environ.get('ENV_SETUP_IN_SHELL', '0')
   
    if env_setup_in_shell == '1':
        logger.info("Environment already set up in shell script")
        return True
   
    logger.info("Setting up environment in Python")
   
    # Get environment file paths from environment variables
    cshrc_lsfc2 = os.environ.get('ENV_CSHRC_LSFC2', '/tools/dotfile_new/cshrc.lsfc2')
    cshrc_hspice = os.environ.get('ENV_CSHRC_HSPICE', '/tools/dotfile_new/cshrc.hspice')
    hspice_version = os.environ.get('ENV_HSPICE_VERSION', '127')
   
    # Check if files exist
    if not os.path.exists(cshrc_lsfc2) or not os.path.exists(cshrc_hspice):
        logger.error(f"Environment files not found: {cshrc_lsfc2} or {cshrc_hspice}")
        return False
   
    try:
        # Use csh to source the files and print the environment
        cmd = f"csh -c 'source {cshrc_lsfc2} && source {cshrc_hspice} {hspice_version} && env'"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
       
        if result.returncode != 0:
            logger.error(f"Failed to source environment: {result.stderr}")
            return False
       
        # Parse environment variables and set them in current process
        for line in result.stdout.split('\n'):
            if '=' in line:
                name, value = line.split('=', 1)
                if name and value:
                    os.environ[name] = value
                    logger.info(f"Set environment variable: {name}")
       
        # Verify HSPICE is in PATH
        path = os.environ.get('PATH', '')
        hspice_found = False
        for directory in path.split(':'):
            if os.path.exists(os.path.join(directory, 'hspice')):
                hspice_found = True
                logger.info(f"Found HSPICE in {directory}")
                break
       
        if not hspice_found:
            logger.warning("HSPICE not found in PATH even after sourcing environment")
       
        return hspice_found
    except Exception as e:
        logger.error(f"Error setting up environment: {str(e)}")
        logger.info(traceback.format_exc())
        return False
 
def create_directory(directory):
    """Create directory if it doesn't exist"""
    logger.debug(f"Creating directory: {directory}")
    if not os.path.exists(directory):
        os.makedirs(directory)
        logger.debug(f"Directory created: {directory}")
    else:
        logger.debug(f"Directory already exists: {directory}")
 
def modify_netlist(input_file, output_file, sample_size, sampling_method):
    """Modify the netlist file with specific sample size and sampling method"""
    logger.debug(f"Modifying netlist: {input_file} -> {output_file}")
    logger.debug(f"  Setting sample_size={sample_size}, sampling_method={sampling_method}")
   
    try:
        with open(input_file, 'r') as f:
            netlist_content = f.read()
       
        # Keep original for debug comparison
        original_content = netlist_content
       
        # Replace the Monte Carlo sample size
        netlist_content = re.sub(r'sweep monte=\d+', f'sweep monte={sample_size}', netlist_content)
       
        # Replace the sampling method
        netlist_content = re.sub(r'sampling_method=\w+', f'sampling_method={sampling_method}', netlist_content)
       
        # Check if modifications were successful
        if original_content == netlist_content:
            logger.warning("No modifications were made to the netlist. Check regex patterns.")
       
        with open(output_file, 'w') as f:
            f.write(netlist_content)
       
        logger.debug(f"Netlist successfully modified and saved to {output_file}")
        return output_file
    except Exception as e:
        logger.error(f"Error modifying netlist: {str(e)}")
        logger.debug(traceback.format_exc())
        return None
 
def run_hspice(netlist_file, output_prefix):
    """Run HSPICE with the specified netlist file"""
    cmd = f"hspice -dp 400 -dpconfig ~/lsf.cfg -i {netlist_file} -o {output_prefix}"
    logger.debug(f"Running HSPICE command: {cmd}")
   
    try:
        start_time = time.time()
        process = subprocess.run(cmd, shell=True, check=True,
                                text=True, capture_output=True)
        end_time = time.time()
       
        logger.debug(f"HSPICE execution completed in {end_time - start_time:.2f} seconds")
        logger.debug(f"HSPICE stdout: {process.stdout[:200]}...")  # First 200 chars
       
        if process.stderr:
            logger.warning(f"HSPICE stderr: {process.stderr}")
       
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Error running HSPICE: {e}")
        logger.error(f"Command output: {e.stdout}")
        logger.error(f"Command error: {e.stderr}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error running HSPICE: {str(e)}")
        logger.debug(traceback.format_exc())
        return False
 
def extract_measurements(output_dir):
    """Extract measurements from HSPICE output files"""
    logger.info(f"Extracting measurements from directory: {output_dir}")
   
    # Look for .mt0 files (Monte Carlo output data)
    mt0_files = glob.glob(f"{output_dir}/*.mt0")
    logger.info(f"Found {len(mt0_files)} .mt0 files")
   
    # Extract from .lis file for backup
    lis_files = glob.glob(f"{output_dir}/*.lis")
    logger.info(f"Found {len(lis_files)} .lis files")
   
    # Extract measurements from .csv files for backup
    csv_files = glob.glob(f"{output_dir}/*.csv")
    logger.info(f"Found {len(csv_files)} .csv files")
   
    data = {}
   
    # First priority: Extract from .mt0 files (Monte Carlo data)
    if mt0_files:
        logger.info("Extracting data from .mt0 files")
        for mt0_file in mt0_files:
            try:
                # Read the file content
                with open(mt0_file, 'r') as f:
                    content = f.readlines()
               
                # Find the header line (typically starts with "index" or similar)
                header_line_idx = None
                for i, line in enumerate(content):
                    if line.strip().startswith('index') or 'meas_delay' in line.lower():
                        header_line_idx = i
                        break
               
                if header_line_idx is not None:
                    logger.info(f"Found header at line {header_line_idx+1}: {content[header_line_idx].strip()}")
                   
                    # Parse header to get column indices
                    headers = content[header_line_idx].strip().split()
                    logger.info(f"Headers: {headers}")
                   
                    # Find the indices for our metrics of interest
                    metric_indices = {}
                    for metric in metrics_of_interest:
                        for i, header in enumerate(headers):
                            if metric.lower() in header.lower():
                                metric_indices[metric] = i
                                logger.info(f"Found {metric} at column index {i}")
                                break
                   
                    # Extract data
                    if metric_indices:
                        # Initialize data arrays
                        for metric in metric_indices:
                            data[metric] = []
                       
                        # Parse data lines
                        for i in range(header_line_idx + 1, len(content)):
                            line = content[i].strip()
                            if not line or line.startswith('*'):
                                continue
                           
                            # Handle lines with varying number of fields
                            fields = line.split()
                            if len(fields) >= max(metric_indices.values()) + 1:
                                for metric, idx in metric_indices.items():
                                    try:
                                        value = float(fields[idx])
                                        data[metric].append(value)
                                    except (ValueError, IndexError) as e:
                                        logger.warning(f"Error parsing value for {metric} in line {i+1}: {e}")
                       
                        # Convert lists to numpy arrays
                        for metric in data:
                            data[metric] = np.array(data[metric])
                            logger.info(f"Extracted {len(data[metric])} values for {metric}")
                else:
                    logger.warning(f"Could not find header line in {mt0_file}")
            except Exception as e:
                logger.error(f"Error reading MT0 file {mt0_file}: {str(e)}")
                logger.info(traceback.format_exc())
   
    # Second priority: Extract from CSV files
    if not data and csv_files:
        logger.info("Falling back to CSV files")
        for metric in metrics_of_interest:
            for csv_file in csv_files:
                if metric in csv_file:
                    logger.info(f"Found CSV file for metric {metric}: {csv_file}")
                    try:
                        df = pd.read_csv(csv_file)
                        if not df.empty:
                            logger.info(f"Successfully loaded data from {csv_file}, shape: {df.shape}")
                            data[metric] = df.iloc[:, 0].values  # Assuming the data is in the first column
                            break
                        else:
                            logger.warning(f"CSV file {csv_file} is empty")
                    except Exception as e:
                        logger.error(f"Error reading {csv_file}: {str(e)}")
                        logger.info(traceback.format_exc())
   
    # Third priority: Extract from .lis files
    if not data and lis_files:
        logger.info("Falling back to .lis files")
        for lis_file in lis_files:
            try:
                with open(lis_file, 'r') as f:
                    content = f.read()
                    for metric in metrics_of_interest:
                        pattern = r'{}=\s*([^\s]+)'.format(metric)
                        matches = re.findall(pattern, content)
                        if matches:
                            logger.info(f"Found {len(matches)} matches for {metric} in {lis_file}")
                            data[metric] = np.array([float(m) for m in matches])
                        else:
                            logger.warning(f"No matches found for {metric} in {lis_file}")
            except Exception as e:
                logger.error(f"Error processing .lis file {lis_file}: {str(e)}")
                logger.info(traceback.format_exc())
   
    if data:
        logger.info(f"Successfully extracted data for metrics: {list(data.keys())}")
        for metric, values in data.items():
            logger.info(f"  {metric}: {len(values)} data points, range: {np.min(values)}-{np.max(values)}")
    else:
        logger.error("Failed to extract any measurement data")
   
    return data
 
def analyze_convergence(results_data, sampling_methods, sample_sizes):
    """Analyze convergence of metrics across different sample sizes and methods"""
    logger.info("Analyzing convergence patterns")
    convergence_data = {}
   
    for method in sampling_methods:
        logger.info(f"Analyzing method: {method}")
        method_data = {}
        for metric in metrics_of_interest:
            logger.info(f"  Analyzing metric: {metric}")
            metric_stats = []
            for size in sample_sizes:
                key = f"{method}_{size}"
                if key in results_data and metric in results_data[key]:
                    data = results_data[key][metric]
                    if len(data) > 0:
                        stats_entry = {
                            'sample_size': size,
                            'mean': np.mean(data),
                            'std': np.std(data),
                            'p10': np.percentile(data, 10),
                            'p90': np.percentile(data, 90)
                        }
                        logger.info(f"    Size {size}: mean={stats_entry['mean']:.6f}, std={stats_entry['std']:.6f}")
                        metric_stats.append(stats_entry)
                    else:
                        logger.warning(f"No data for {key}/{metric}")
            method_data[metric] = pd.DataFrame(metric_stats)
        convergence_data[method] = method_data
   
    return convergence_data
 
def plot_convergence(convergence_data, output_dir, sampling_methods):
    """Plot convergence metrics for visual analysis"""
    logger.info("Creating convergence plots")
    create_directory(f"{output_dir}/plots")
   
    # Plot mean convergence for each metric and method
    for metric in metrics_of_interest:
        logger.info(f"Creating convergence plots for {metric}")
        plt.figure(figsize=(12, 8))
        for method in sampling_methods:
            if method in convergence_data and metric in convergence_data[method]:
                df = convergence_data[method][metric]
                if not df.empty:
                    plt.plot(df['sample_size'], df['mean'], 'o-', label=f"{method} - Mean")
                    # Plot standard deviation bands
                    plt.fill_between(
                        df['sample_size'],
                        df['mean'] - df['std'],
                        df['mean'] + df['std'],
                        alpha=0.2
                    )
                    logger.info(f"  Added {method} data to plot")
                else:
                    logger.warning(f"  No data for {method}/{metric}")
       
        plt.xscale('log')
        plt.grid(True, which="both", ls="--", alpha=0.5)
        plt.xlabel('Sample Size')
        plt.ylabel(f'{metric} Value')
        plt.title(f'Convergence of {metric} Mean by Sample Size and Method')
        plt.legend()
        plt.tight_layout()
       
        plot_path = f"{output_dir}/plots/{metric}_mean_convergence.png"
        plt.savefig(plot_path)
        logger.info(f"  Saved plot to {plot_path}")
        plt.close()
       
        # Plot percentile convergence
        plt.figure(figsize=(12, 8))
        for method in sampling_methods:
            if method in convergence_data and metric in convergence_data[method]:
                df = convergence_data[method][metric]
                if not df.empty:
                    plt.plot(df['sample_size'], df['p90'] - df['p10'], 'o-',
                             label=f"{method} - P90-P10 Range")
       
        plt.xscale('log')
        plt.grid(True, which="both", ls="--", alpha=0.5)
        plt.xlabel('Sample Size')
        plt.ylabel(f'{metric} P90-P10 Range')
        plt.title(f'Convergence of {metric} Percentile Range by Sample Size and Method')
        plt.legend()
        plt.tight_layout()
       
        plot_path = f"{output_dir}/plots/{metric}_percentile_convergence.png"
        plt.savefig(plot_path)
        logger.info(f"  Saved plot to {plot_path}")
        plt.close()
 
def compare_distributions(results_data, output_dir, sampling_methods, sample_sizes):
    """Compare distributions between different sampling methods"""
    logger.info("Comparing distributions between sampling methods")
    create_directory(f"{output_dir}/plots")
   
    # Use the largest sample size for comparison
    largest_size = max(sample_sizes)
    logger.info(f"Using largest sample size for comparison: {largest_size}")
   
    for metric in metrics_of_interest:
        logger.info(f"Creating distribution comparison for {metric}")
        plt.figure(figsize=(12, 8))
        for method in sampling_methods:
            key = f"{method}_{largest_size}"
            if key in results_data and metric in results_data[key]:
                data = results_data[key][metric]
                if len(data) > 0:
                    # Plot histogram
                    plt.hist(data, bins=50, alpha=0.5, density=True, label=f"{method}")
                   
                    # Plot KDE
                    x = np.linspace(min(data), max(data), 1000)
                    kde = stats.gaussian_kde(data)
                    plt.plot(x, kde(x), label=f"{method} KDE")
                   
                    logger.info(f"  Added {method} distribution to plot")
                else:
                    logger.warning(f"  No data for {key}/{metric}")
       
        plt.grid(True, ls="--", alpha=0.5)
        plt.xlabel(metric)
        plt.ylabel('Density')
        plt.title(f'Distribution Comparison for {metric} (Sample Size = {largest_size})')
        plt.legend()
        plt.tight_layout()
       
        plot_path = f"{output_dir}/plots/{metric}_distribution_comparison.png"
        plt.savefig(plot_path)
        logger.info(f"  Saved distribution plot to {plot_path}")
        plt.close()
       
        # Create QQ plots comparing methods
        methods = list(sampling_methods)
        if len(methods) > 1:
            logger.info(f"  Creating QQ plots for method comparisons")
            fig, axes = plt.subplots(len(methods), len(methods), figsize=(15, 15))
            for i, method1 in enumerate(methods):
                for j, method2 in enumerate(methods):
                    if i != j:  # Don't compare method with itself
                        key1 = f"{method1}_{largest_size}"
                        key2 = f"{method2}_{largest_size}"
                        if (key1 in results_data and metric in results_data[key1] and
                            key2 in results_data and metric in results_data[key2]):
                            data1 = results_data[key1][metric]
                            data2 = results_data[key2][metric]
                            if len(data1) > 0 and len(data2) > 0:
                                # Create QQ plot
                                stats.probplot(data1, dist=lambda x: stats.norm.ppf(x, loc=np.mean(data2), scale=np.std(data2)),
                                              plot=axes[i, j])
                                axes[i, j].set_title(f'{method1} vs {method2}')
                                logger.info(f"    Added QQ plot for {method1} vs {method2}")
                    else:
                        axes[i, j].axis('off')  # Turn off diagonal plots
           
            plt.tight_layout()
           
            plot_path = f"{output_dir}/plots/{metric}_qq_comparison.png"
            plt.savefig(plot_path)
            logger.info(f"  Saved QQ plots to {plot_path}")
            plt.close()
        else:
            logger.info("  Skipping QQ plots (need at least 2 methods for comparison)")
 
def calculate_statistics(results_data, output_dir, sampling_methods, sample_sizes):
    """Calculate and save statistical measures for comparison"""
    logger.info("Calculating and saving statistical measures")
    stats_data = []
   
    for method in sampling_methods:
        for size in sample_sizes:
            key = f"{method}_{size}"
            if key in results_data:
                for metric in metrics_of_interest:
                    if metric in results_data[key]:
                        data = results_data[key][metric]
                        if len(data) > 0:
                            # Basic statistics
                            mean_val = np.mean(data)
                            std_val = np.std(data)
                           
                            # Calculate actual percentiles for 3-sigma approximation
                            # 3-sigma corresponds to ~0.13% and ~99.87% percentiles
                            p00_13 = np.percentile(data, 0.13) if len(data) >= 500 else None
                            p99_87 = np.percentile(data, 99.87) if len(data) >= 500 else None
                           
                            # Calculate theoretical 3-sigma points assuming normal distribution
                            early_3sigma_theoretical = mean_val - 3 * std_val
                            late_3sigma_theoretical = mean_val + 3 * std_val
                           
                            entry = {
                                'method': method,
                                'sample_size': size,
                                'metric': metric,
                                'mean': mean_val,
                                'std': std_val,
                                'min': np.min(data),
                                'max': np.max(data),
                                'p10': np.percentile(data, 10),
                                'p50': np.percentile(data, 50),
                                'p90': np.percentile(data, 90),
                                'early_3sigma_actual': p00_13,
                                'late_3sigma_actual': p99_87,
                                'early_3sigma_theoretical': early_3sigma_theoretical,
                                'late_3sigma_theoretical': late_3sigma_theoretical,
                                'skew': stats.skew(data),
                                'kurtosis': stats.kurtosis(data)
                            }
                            stats_data.append(entry)
                            logger.info(f"Added statistics for {method}, size {size}, {metric}")
   
    if stats_data:
        stats_df = pd.DataFrame(stats_data)
        stats_path = f"{output_dir}/simulation_statistics.csv"
        stats_df.to_csv(stats_path, index=False)
        logger.info(f"Saved comprehensive statistics to {stats_path}")
       
        # Create pivot tables for easier comparison
        for metric in metrics_of_interest:
            metric_stats = stats_df[stats_df['metric'] == metric]
           
            # Mean comparison
            pivot_mean = metric_stats.pivot(index='sample_size', columns='method', values='mean')
            mean_path = f"{output_dir}/{metric}_mean_comparison.csv"
            pivot_mean.to_csv(mean_path)
            logger.info(f"Saved {metric} mean comparison to {mean_path}")
           
            # Std comparison
            pivot_std = metric_stats.pivot(index='sample_size', columns='method', values='std')
            std_path = f"{output_dir}/{metric}_std_comparison.csv"
            pivot_std.to_csv(std_path)
            logger.info(f"Saved {metric} std comparison to {std_path}")
           
            # Early 3-sigma comparison
            pivot_early_3sigma = metric_stats.pivot(index='sample_size', columns='method', values='early_3sigma_theoretical')
            early_3sigma_path = f"{output_dir}/{metric}_early_3sigma_comparison.csv"
            pivot_early_3sigma.to_csv(early_3sigma_path)
            logger.info(f"Saved {metric} early 3-sigma comparison to {early_3sigma_path}")
           
            # Late 3-sigma comparison
            pivot_late_3sigma = metric_stats.pivot(index='sample_size', columns='method', values='late_3sigma_theoretical')
            late_3sigma_path = f"{output_dir}/{metric}_late_3sigma_comparison.csv"
            pivot_late_3sigma.to_csv(late_3sigma_path)
            logger.info(f"Saved {metric} late 3-sigma comparison to {late_3sigma_path}")
           
            # Skewness comparison
            pivot_skew = metric_stats.pivot(index='sample_size', columns='method', values='skew')
            skew_path = f"{output_dir}/{metric}_skewness_comparison.csv"
            pivot_skew.to_csv(skew_path)
            logger.info(f"Saved {metric} skewness comparison to {skew_path}")
    else:
        logger.warning("No statistical data to save")
 
def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Monte Carlo Sampling Analysis for HSPICE')
    parser.add_argument('--netlist', required=True, help='Path to the reference SPICE netlist')
    parser.add_argument('--sample_sizes', help='Comma-separated list of sample sizes (e.g., "1000,5000,10000")')
    parser.add_argument('--sampling_methods', help='Comma-separated list of sampling methods (e.g., "lhs,sobol,mc")')
    parser.add_argument('--logfile', help='Path to log file')
   
    args = parser.parse_args()
   
    # Setup logging
    global logger
    logger = setup_logging(args.logfile)
   
    log_section("SCRIPT INITIALIZATION")
    logger.info("Starting Monte Carlo Sampling Analysis")
    logger.info(f"Script arguments: {args}")
   
    # Setup environment if needed
    if not setup_environment():
        logger.warning("Failed to set up environment, but will attempt to continue")
   
    # Check if netlist exists
    if not os.path.exists(args.netlist):
        logger.error(f"Error: Netlist file {args.netlist} not found.")
        return 1
   
    # Check if netlist exists
    if not os.path.exists(args.netlist):
        logger.error(f"Error: Netlist file {args.netlist} not found.")
        return 1
   
    # Parse sample sizes
    if args.sample_sizes:
        try:
            sample_sizes = [int(size) for size in args.sample_sizes.split(',')]
            logger.info(f"Using custom sample sizes: {sample_sizes}")
        except ValueError:
            logger.warning(f"Invalid sample sizes format '{args.sample_sizes}'. Using defaults.")
            sample_sizes = DEFAULT_SAMPLE_SIZES
    else:
        sample_sizes = DEFAULT_SAMPLE_SIZES
        logger.info(f"Using default sample sizes: {sample_sizes}")
   
    # Parse sampling methods
    if args.sampling_methods:
        sampling_methods = [method.strip().lower() for method in args.sampling_methods.split(',')]
        valid_methods = set(['lhs', 'sobol', 'mc'])
        if not all(method in valid_methods for method in sampling_methods):
            invalid_methods = [m for m in sampling_methods if m not in valid_methods]
            logger.warning(f"Invalid sampling methods: {invalid_methods}. Using defaults.")
            sampling_methods = DEFAULT_SAMPLING_METHODS
        logger.info(f"Using sampling methods: {sampling_methods}")
    else:
        sampling_methods = DEFAULT_SAMPLING_METHODS
        logger.info(f"Using default sampling methods: {sampling_methods}")
   
    # Record start time
    start_time = time.time()
   
    # Create base output directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_output_dir = f"mc_analysis_results_{timestamp}"
    create_directory(base_output_dir)
    logger.info(f"Created output directory: {base_output_dir}")
   
    # Store results for later analysis
    results_data = {}
   
    # Run simulations for each combination of sample size and sampling method
    for i, sample_size in enumerate(sample_sizes):
        for sampling_method in sampling_methods:
            log_section(f"SIMULATION: {sampling_method} with {sample_size} samples")
           
            # Create directory for this configuration
            run_dir = f"{base_output_dir}/{i+1}_{sample_size}_{sampling_method}"
            create_directory(run_dir)
           
            # Copy and modify the netlist
            logger.info(f"Starting simulation for {sampling_method} with {sample_size} samples")
            modified_netlist = f"{run_dir}/mc_sim.sp"
           
            modified_file = modify_netlist(args.netlist, modified_netlist, sample_size, sampling_method)
            if not modified_file:
                logger.error(f"Failed to modify netlist for {sampling_method} with {sample_size} samples")
                continue
           
            # Run HSPICE
            output_prefix = f"{run_dir}/mc_sim"
           
            logger.info(f"Running HSPICE for {sampling_method} with {sample_size} samples...")
            sim_start_time = time.time()
           
            if run_hspice(modified_netlist, output_prefix):
                sim_end_time = time.time()
                logger.info(f"HSPICE completed in {sim_end_time - sim_start_time:.2f} seconds")
               
                # Extract measurements from .mt0 files (Monte Carlo data)
                logger.info(f"Extracting measurements for {sampling_method} with {sample_size} samples")
                data = extract_measurements(run_dir)
               
                if data:
                    results_data[f"{sampling_method}_{sample_size}"] = data
                    logger.info(f"Successfully completed simulation for {sampling_method} with {sample_size} samples")
                else:
                    logger.error(f"Failed to extract measurements for {sampling_method} with {sample_size} samples")
            else:
                logger.error(f"HSPICE simulation failed for {sampling_method} with {sample_size} samples")
   
    # Analyze results
    if results_data:
        log_section("DATA ANALYSIS")
        logger.info("Starting analysis of simulation results")
       
        # Analyze convergence
        logger.info("Analyzing convergence across sample sizes and methods")
        try:
            convergence_data = analyze_convergence(results_data, sampling_methods, sample_sizes)
            plot_convergence(convergence_data, base_output_dir, sampling_methods)
            logger.info("Convergence analysis completed")
        except Exception as e:
            logger.error(f"Error in convergence analysis: {str(e)}")
            logger.info(traceback.format_exc())
       
        # Compare distributions
        logger.info("Comparing distributions between sampling methods")
        try:
            compare_distributions(results_data, base_output_dir, sampling_methods, sample_sizes)
            logger.info("Distribution comparison completed")
        except Exception as e:
            logger.error(f"Error in distribution comparison: {str(e)}")
            logger.info(traceback.format_exc())
       
        # Calculate statistics
        logger.info("Calculating statistical measures")
        try:
            calculate_statistics(results_data, base_output_dir, sampling_methods, sample_sizes)
            logger.info("Statistical analysis completed")
        except Exception as e:
            logger.error(f"Error in statistical analysis: {str(e)}")
            logger.info(traceback.format_exc())
           
        # Additional 3-sigma analysis
        logger.info("Performing 3-sigma point analysis")
        try:
            plot_sigma_analysis(results_data, base_output_dir, sampling_methods, sample_sizes)
            logger.info("3-sigma analysis completed")
        except Exception as e:
            logger.error(f"Error in 3-sigma analysis: {str(e)}")
            logger.info(traceback.format_exc())
       
        # Record end time and total duration
        end_time = time.time()
        total_time = end_time - start_time
        logger.info(f"Total analysis time: {total_time:.2f} seconds")
       
        logger.info(f"Analysis complete. Results saved in {base_output_dir}")
       
        # Create a summary file
        with open(f"{base_output_dir}/summary.txt", 'w') as f:
            f.write(f"Monte Carlo Sampling Analysis Summary\n")
            f.write(f"=====================================\n\n")
            f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Reference netlist: {args.netlist}\n")
            f.write(f"Sample sizes tested: {sample_sizes}\n")
            f.write(f"Sampling methods tested: {sampling_methods}\n")
            f.write(f"Total analysis time: {total_time:.2f} seconds\n\n")
            f.write(f"Metrics analyzed: {metrics_of_interest}\n\n")
            f.write(f"Results directory: {base_output_dir}\n")
       
        return 0
    else:
        logger.error("No valid simulation results to analyze.")
        return 1
 
if __name__ == "__main__":
    sys.exit(main())
 
