#!/usr/bin/env python3
 
import os
import json
import pandas as pd
import numpy as np
import glob
import logging
import traceback
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import re
 
def setup_logging(output_dir):
    """Set up logging to file."""
    os.makedirs(output_dir, exist_ok=True)
    log_file = os.path.join(output_dir, "voltage_trend_analysis.log")
 
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
 
def extract_voltage_from_corner(corner_name):
    """Extract voltage value from corner name."""
    # Pattern: ssgnp_0p450v_m40c -> 0.450
    match = re.search(r'_0p(\d+)v_', corner_name)
    if match:
        voltage_str = match.group(1)
        voltage = float(f"0.{voltage_str}")
        return voltage
    return None
 
def load_correlation_data(data_dir):
    """Load correlation data from all corners."""
    correlation_files = glob.glob(os.path.join(data_dir, "*/*_correlations.json"))
 
    all_data = {}
    for file_path in correlation_files:
        # Extract corner and type from path
        path_parts = Path(file_path).parts
        corner_type = path_parts[-2]  # e.g., "ssgnp_0p450v_m40c_delay"
 
        # Split corner and type
        parts = corner_type.split('_')
        if parts[-1] in ['delay', 'slew']:
            type_name = parts[-1]
            corner = '_'.join(parts[:-1])
        else:
            continue
 
        voltage = extract_voltage_from_corner(corner)
        if voltage is None:
            continue
 
        try:
            with open(file_path, 'r') as f:
                correlations = json.load(f)
 
            if corner not in all_data:
                all_data[corner] = {}
            if type_name not in all_data[corner]:
                all_data[corner][type_name] = {}
 
            file_base = os.path.basename(file_path).replace('_correlations.json', '')
            all_data[corner][type_name][file_base] = {
                'voltage': voltage,
                'correlations': correlations
            }
        except Exception as e:
            logging.error(f"Error loading {file_path}: {e}")
 
    return all_data
 
def load_error_data(data_dir):
    """Load error magnitude data from CSV files."""
    csv_files = glob.glob(os.path.join(data_dir, "*/*_abs_err_data.csv")) + \
                glob.glob(os.path.join(data_dir, "*/*_rel_err_data.csv"))
 
    error_data = {}
    for file_path in csv_files:
        # Extract corner and type from path
        path_parts = Path(file_path).parts
        corner_type = path_parts[-2]
 
        # Split corner and type
        parts = corner_type.split('_')
        if parts[-1] in ['delay', 'slew']:
            type_name = parts[-1]
            corner = '_'.join(parts[:-1])
        else:
            continue
 
        voltage = extract_voltage_from_corner(corner)
        if voltage is None:
            continue
 
        # Determine error type from filename
        filename = os.path.basename(file_path)
        if 'abs_err' in filename:
            error_type = 'abs_err'
        elif 'rel_err' in filename:
            error_type = 'rel_err'
        else:
            continue
 
        try:
            df = pd.read_csv(file_path)
 
            # Calculate mean errors for each column
            mean_errors = {}
            for col in df.columns:
                if col not in ['Arc', 'Table_type', 'cell', 'table_position']:
                    mean_errors[col] = df[col].mean()
 
            if corner not in error_data:
                error_data[corner] = {}
            if type_name not in error_data[corner]:
                error_data[corner][type_name] = {}
            if error_type not in error_data[corner][type_name]:
                error_data[corner][type_name][error_type] = {}
 
            error_data[corner][type_name][error_type] = {
                'voltage': voltage,
                'mean_errors': mean_errors
            }
        except Exception as e:
            logging.error(f"Error loading {file_path}: {e}")
 
    return error_data
 
def create_voltage_correlation_trends(correlation_data, output_dir):
    """Create voltage trend plots for correlations."""
    # Organize data by type and category
    trends = {}
 
    for corner, corner_data in correlation_data.items():
        voltage = extract_voltage_from_corner(corner)
 
        for type_name, type_data in corner_data.items():
            if type_name not in trends:
                trends[type_name] = {}
 
            for file_name, file_data in type_data.items():
                correlations = file_data['correlations']
 
                # Process late_sigma correlations
                if 'late_sigma' in correlations:
                    for category, category_corrs in correlations['late_sigma'].items():
                        if category not in trends[type_name]:
                            trends[type_name][category] = {
                                'late_sigma': {'voltages': [], 'correlations': []},
                                'early_sigma': {'voltages': [], 'correlations': []}
                            }
 
                        # Average correlations for this category
                        avg_corr = np.mean(list(category_corrs.values()))
                        trends[type_name][category]['late_sigma']['voltages'].append(voltage)
                        trends[type_name][category]['late_sigma']['correlations'].append(avg_corr)
 
                # Process early_sigma correlations
                if 'early_sigma' in correlations:
                    for category, category_corrs in correlations['early_sigma'].items():
                        if category not in trends[type_name]:
                            trends[type_name][category] = {
                                'late_sigma': {'voltages': [], 'correlations': []},
                                'early_sigma': {'voltages': [], 'correlations': []}
                            }
 
                        # Average correlations for this category
                        avg_corr = np.mean(list(category_corrs.values()))
                        trends[type_name][category]['early_sigma']['voltages'].append(voltage)
                        trends[type_name][category]['early_sigma']['correlations'].append(avg_corr)
 
    # Create plots
    for type_name, type_trends in trends.items():
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle(f'Correlation vs Voltage Trends - {type_name.upper()}', fontsize=16)
 
        categories = ['MC', 'Lib', 'abs_err', 'rel_err']
 
        for idx, category in enumerate(categories):
            row = idx // 2
            col = idx % 2
            ax = axes[row, col]
 
            if category in type_trends:
                data = type_trends[category]
 
                # Plot late_sigma
                if data['late_sigma']['voltages']:
                    voltages = sorted(data['late_sigma']['voltages'])
                    correlations = [data['late_sigma']['correlations'][data['late_sigma']['voltages'].index(v)]
                                  for v in voltages]
                    ax.plot(voltages, correlations, 'o-', label='late_sigma',
                           marker='o', markersize=8, linewidth=2)
 
                # Plot early_sigma
                if data['early_sigma']['voltages']:
                    voltages = sorted(data['early_sigma']['voltages'])
                    correlations = [data['early_sigma']['correlations'][data['early_sigma']['voltages'].index(v)]
                                  for v in voltages]
                    ax.plot(voltages, correlations, 's-', label='early_sigma',
                           marker='s', markersize=8, linewidth=2)
 
            ax.set_title(f'{category} Correlations')
            ax.set_xlabel('Voltage (V)')
            ax.set_ylabel('Average Correlation')
            ax.grid(True, alpha=0.3)
            ax.legend()
 
            # Set x-axis ticks to show all voltage points
            ax.set_xticks([0.450, 0.465, 0.480, 0.495])
 
        plt.tight_layout()
        output_path = os.path.join(output_dir, f'voltage_correlation_trends_{type_name}.png')
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()
 
        logging.info(f"Created voltage correlation trend plot: {output_path}")
def create_error_magnitude_trends(error_data, output_dir):
    """Create voltage trend plots for error magnitudes focusing on specific columns."""
    # Organize data by type and error type
    trends = {}
 
    for corner, corner_data in error_data.items():
        voltage = extract_voltage_from_corner(corner)
 
        for type_name, type_data in corner_data.items():
            if type_name not in trends:
                trends[type_name] = {}
 
            for error_type, error_info in type_data.items():
                if error_type not in trends[type_name]:
                    trends[type_name][error_type] = {
                        'voltages': [],
                        'mean_errors': [],
                        'all_errors': {}
                    }
 
                trends[type_name][error_type]['voltages'].append(voltage)
 
                # Store individual column errors
                for col, err in error_info['mean_errors'].items():
                    if col not in trends[type_name][error_type]['all_errors']:
                        trends[type_name][error_type]['all_errors'][col] = {
                            'voltages': [], 'errors': []
                        }
                    trends[type_name][error_type]['all_errors'][col]['voltages'].append(voltage)
                    trends[type_name][error_type]['all_errors'][col]['errors'].append(err)
 
    # Create plots
    for type_name, type_trends in trends.items():
        fig, axes = plt.subplots(1, 2, figsize=(16, 7))
        fig.suptitle(f'Error Magnitude vs Voltage Trends - {type_name.upper()}', fontsize=16)
 
        for idx, error_type in enumerate(['abs_err', 'rel_err']):
            ax = axes[idx]
 
            if error_type in type_trends:
                data = type_trends[error_type]
 
                # Define specific columns to plot
                target_columns = {
                    'Nominal': None,
                    'Std': None,
                    'Skew': None,
                    'Meanshift': None,
                    'early_sigma': None,
                    'late_sigma': None  # Added late_sigma
                }
 
                # Find matches for each target column
                for col in data['all_errors'].keys():
                    col_lower = col.lower()
                    if 'nominal' in col_lower and error_type in col_lower:
                        target_columns['Nominal'] = col
                    elif 'std' in col_lower and error_type in col_lower:
                        target_columns['Std'] = col
                    elif 'skew' in col_lower and error_type in col_lower:
                        target_columns['Skew'] = col
                    elif 'meanshift' in col_lower and error_type in col_lower:
                        target_columns['Meanshift'] = col
                    elif 'early_sigma' in col_lower and error_type in col_lower:
                        target_columns['early_sigma'] = col
                    elif 'late_sigma' in col_lower and error_type in col_lower:
                        target_columns['late_sigma'] = col
 
                # Define colors and plot order
                colors = {
                    'Nominal': 'gray',
                    'Std': 'blue',
                    'Skew': 'green',
                    'Meanshift': 'orange',
                    'early_sigma': 'purple',
                    'late_sigma': 'magenta'  # Color for late_sigma
                }
 
                # Calculate average of JUST these specific columns
                specific_errors = []
                for label, col in target_columns.items():
                    if col is not None:
                        col_data = data['all_errors'][col]
                        specific_errors.append(col_data['errors'])
 
                if specific_errors:
                    # Only calculate average if we have specific errors
                    voltages = sorted(data['voltages'])
                    avg_specific_errors = np.mean(specific_errors, axis=0)
 
                    # Plot average
                    ax.plot(voltages, avg_specific_errors, 'o-', label='Average',
                           marker='o', markersize=10, linewidth=3, color='red')
 
                # Plot each specific column
                for label, col in target_columns.items():
                    if col is not None and col in data['all_errors']:
                        col_data = data['all_errors'][col]
                        col_voltages = sorted(col_data['voltages'])
                        col_errors = [col_data['errors'][col_data['voltages'].index(v)]
                                    for v in col_voltages]
 
                        plot_label = f"{label}_{error_type}"
                        ax.plot(col_voltages, col_errors, 'o-',
                               color=colors[label],
                               alpha=0.7, markersize=6, linewidth=2,
                               label=plot_label)
 
            ax.set_title(f'{error_type} vs Voltage')
            ax.set_xlabel('Voltage (V)')
            ax.set_ylabel(f'Mean {error_type}')
            ax.grid(True, alpha=0.3)
            ax.legend(loc='best')
            ax.set_xticks([0.450, 0.465, 0.480, 0.495])
 
        plt.tight_layout()
        output_path = os.path.join(output_dir, f'error_magnitude_trends_{type_name}.png')
        plt.savefig(output_path, dpi=150)
        plt.close()
 
        logging.info(f"Created error magnitude trend plot: {output_path}")
 
def create_voltage_summary_table(correlation_data, error_data, output_dir):
    """Create summary table of trends across voltages."""
    summary = []
 
    voltages = [0.450, 0.465, 0.480, 0.495]
 
    for voltage in voltages:
        # Find the corner for this voltage
        corner = None
        for c in correlation_data.keys():
            if extract_voltage_from_corner(c) == voltage:
                corner = c
                break
 
        if corner is None:
            continue
 
        row = {'voltage': voltage, 'corner': corner}
 
        # Calculate average correlations
        for type_name in ['delay', 'slew']:
            if type_name in correlation_data.get(corner, {}):
                type_data = correlation_data[corner][type_name]
 
                # Average across all files
                all_correlations = {'MC': [], 'Lib': [], 'abs_err': [], 'rel_err': []}
 
                for file_data in type_data.values():
                    correlations = file_data['correlations']
 
                    for sigma_type in ['late_sigma', 'early_sigma']:
                        if sigma_type in correlations:
                            for category, category_corrs in correlations[sigma_type].items():
                                if category in all_correlations:
                                    all_correlations[category].extend(list(category_corrs.values()))
 
                # Calculate averages
                for category in all_correlations:
                    if all_correlations[category]:
                        avg = np.mean(all_correlations[category])
                        row[f'{type_name}_{category}_corr'] = avg
 
        # Add error magnitudes
        if corner in error_data:
            for type_name in ['delay', 'slew']:
                if type_name in error_data[corner]:
                    for error_type in ['abs_err', 'rel_err']:
                        if error_type in error_data[corner][type_name]:
                            mean_errors = error_data[corner][type_name][error_type]['mean_errors']
                            if mean_errors:
                                avg_error = np.mean(list(mean_errors.values()))
                                row[f'{type_name}_{error_type}_mag'] = avg_error
 
        summary.append(row)
 
    # Convert to DataFrame and save
    df = pd.DataFrame(summary)
    df = df.sort_values('voltage')
 
    # Save as CSV
    csv_path = os.path.join(output_dir, 'voltage_trend_summary.csv')
    df.to_csv(csv_path, index=False)
 
    # Create a formatted table plot
    fig, ax = plt.subplots(figsize=(16, 8))
    ax.axis('tight')
    ax.axis('off')
 
    # Format the dataframe for display
    display_df = df.copy()
    for col in display_df.columns:
        if 'corr' in col or 'mag' in col:
            display_df[col] = display_df[col].apply(lambda x: f'{x:.4f}' if pd.notna(x) else 'N/A')
 
    table = ax.table(cellText=display_df.values, colLabels=display_df.columns,
                     cellLoc='center', loc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1.2, 1.5)
 
    plt.title('Voltage Trend Summary Table', fontsize=16, pad=20)
    plt.savefig(os.path.join(output_dir, 'voltage_trend_summary_table.png'),
                dpi=150, bbox_inches='tight')
    plt.close()
 
    logging.info(f"Created voltage trend summary table: {csv_path}")
 
def main():
    import argparse
 
    parser = argparse.ArgumentParser(description='Analyze voltage trends in timing correlations')
    parser.add_argument('--data_dir', type=str, required=True,
                       help='Directory containing analysis results for all corners')
    parser.add_argument('--output_dir', type=str, required=True,
                       help='Output directory for voltage trend analysis')
 
    args = parser.parse_args()
 
    # Setup logging
    setup_logging(args.output_dir)
    logging.info("Starting voltage trend analysis")
 
    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)
 
    # Load data
    logging.info("Loading correlation data...")
    correlation_data = load_correlation_data(args.data_dir)
 
    logging.info("Loading error magnitude data...")
    error_data = load_error_data(args.data_dir)
 
    # Create visualizations
    logging.info("Creating voltage correlation trend plots...")
    create_voltage_correlation_trends(correlation_data, args.output_dir)
 
    logging.info("Creating error magnitude trend plots...")
    create_error_magnitude_trends(error_data, args.output_dir)
 
    logging.info("Creating summary table...")
    create_voltage_summary_table(correlation_data, error_data, args.output_dir)
 
    logging.info("Voltage trend analysis complete")
 
if __name__ == "__main__":
    main()
