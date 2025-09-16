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
from scipy import stats
 
def setup_logging(output_dir):
    """Set up logging to file."""
    os.makedirs(output_dir, exist_ok=True)
    log_file = os.path.join(output_dir, "cross_corner_analysis.log")
 
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
    match = re.search(r'_0p(\d+)v_', corner_name)
    if match:
        voltage_str = match.group(1)
        voltage = float(f"0.{voltage_str}")
        return voltage
    return None
 
def load_and_align_data(data_dir):
    """Load and align data across all corners."""
    corner_data = {}
 
    # Find all CSV files
    csv_files = glob.glob(os.path.join(data_dir, "*/*_data.csv"))
 
    logging.info(f"Found {len(csv_files)} CSV files")
 
    # First pass: load all data
    for file_path in csv_files:
        path_parts = Path(file_path).parts
        corner_type = path_parts[-2]  # e.g., "ssgnp_0p450v_m40c_delay"
        filename = path_parts[-1]
 
        # Parse corner and type
        parts = corner_type.split('_')
        if parts[-1] in ['delay', 'slew']:
            type_name = parts[-1]
            corner = '_'.join(parts[:-1])
        else:
            continue
 
        # Parse category
        category = None
        if '_MC_data.csv' in filename:
            category = 'MC'
        elif '_Lib_data.csv' in filename:
            category = 'Lib'
        elif '_abs_err_data.csv' in filename:
            category = 'abs_err'
        elif '_rel_err_data.csv' in filename:
            category = 'rel_err'
        else:
            continue
 
        voltage = extract_voltage_from_corner(corner)
        if voltage is None:
            continue
 
        # Load data
        df = pd.read_csv(file_path)
 
        # Store data
        if corner not in corner_data:
            corner_data[corner] = {'voltage': voltage}
        if type_name not in corner_data[corner]:
            corner_data[corner][type_name] = {}
 
        corner_data[corner][type_name][category] = df
 
        logging.debug(f"Loaded {corner}/{type_name}/{category}: shape {df.shape}")
 
    # Second pass: align data across corners
    aligned_data = align_data_across_corners(corner_data)
 
    return aligned_data
 
def align_data_across_corners(corner_data):
    """Align data points across all corners."""
    corners = sorted(corner_data.keys(), key=lambda x: corner_data[x]['voltage'])
    voltages = [corner_data[corner]['voltage'] for corner in corners]
 
    aligned_data = {}
 
    for type_name in ['delay', 'slew']:
        for category in ['MC', 'Lib', 'abs_err', 'rel_err']:
            # Get common rows (based on Arc and Table_type)
            common_rows = None
 
            # Find common rows across all corners
            for corner in corners:
                if (type_name in corner_data[corner] and
                    category in corner_data[corner][type_name]):
 
                    df = corner_data[corner][type_name][category]
 
                    if 'Arc' in df.columns and 'Table_type' in df.columns:
                        current_rows = set(df[['Arc', 'Table_type']].apply(tuple, axis=1))
 
                        if common_rows is None:
                            common_rows = current_rows
                        else:
                            common_rows = common_rows.intersection(current_rows)
 
            if common_rows:
                logging.info(f"Found {len(common_rows)} common rows for {type_name}/{category}")
 
                # Create aligned dataframe for this type/category
                aligned_df = pd.DataFrame()
 
                for corner in corners:
                    voltage = corner_data[corner]['voltage']
 
                    if (type_name in corner_data[corner] and
                        category in corner_data[corner][type_name]):
 
                        df = corner_data[corner][type_name][category]
 
                        # Filter to common rows
                        df['row_key'] = df[['Arc', 'Table_type']].apply(tuple, axis=1)
                        df_filtered = df[df['row_key'].isin(common_rows)].copy()
 
                        # Get value columns
                        if category in ['MC', 'Lib']:
                            value_cols = [col for col in df_filtered.columns
                                        if col.startswith(f'{category}_') and
                                        'sigma' not in col.lower() and
                                        not col.endswith('_UB') and
                                        not col.endswith('_LB')]
                        else:
                            value_cols = [col for col in df_filtered.columns
                                        if category in col.lower() and
                                        'sigma' not in col.lower()]
 
                        logging.debug(f"Found {len(value_cols)} value columns for {corner}/{type_name}/{category}")
 
                        # Rename columns to include voltage
                        for col in value_cols:
                            new_col = f"{col}_{voltage}V"
                            df_filtered[new_col] = df_filtered[col]
 
                        # Keep only necessary columns
                        keep_cols = ['Arc', 'Table_type', 'row_key'] + [f"{col}_{voltage}V" for col in value_cols]
                        df_filtered = df_filtered[keep_cols]
 
                        # Merge with aligned dataframe
                        if aligned_df.empty:
                            aligned_df = df_filtered
                        else:
                            aligned_df = pd.merge(aligned_df, df_filtered,
                                                on=['Arc', 'Table_type', 'row_key'],
                                                how='inner')
 
                # Store aligned data
                key = f"{type_name}_{category}"
                aligned_data[key] = {
                    'data': aligned_df,
                    'corners': corners,
                    'voltages': voltages
                }
 
                logging.info(f"Aligned data for {key}: shape {aligned_df.shape}")
            else:
                logging.warning(f"No common rows found for {type_name}/{category}")
 
    return aligned_data
 
def analyze_voltage_scaling_individual(aligned_data, category):
    """Analyze voltage scaling for each individual data point."""
    results = []
 
    for key, data_dict in aligned_data.items():
        if category not in key:
            continue
 
        logging.info(f"Analyzing scaling for {key}")
 
        df = data_dict['data']
        voltages = data_dict['voltages']
        reference_voltage = voltages[0]
 
        # Get columns for each voltage
        voltage_cols = {}
        for voltage in voltages:
            cols = [col for col in df.columns if f"_{voltage}V" in col]
            voltage_cols[voltage] = cols
            logging.debug(f"Voltage {voltage}V has {len(cols)} columns")
 
        # For each column type
        for base_col in voltage_cols[reference_voltage]:
            base_name = base_col.replace(f"_{reference_voltage}V", "")
 
            # For each row (Arc/Table_type combination)
            for idx, row in df.iterrows():
                arc = row['Arc']
                table_type = row['Table_type']
 
                # Get reference value
                ref_value = row[base_col]
 
                if pd.notna(ref_value) and ref_value != 0:
                    # Calculate scaling for each other voltage
                    for voltage in voltages[1:]:
                        target_col = base_name + f"_{voltage}V"
 
                        if target_col in row and pd.notna(row[target_col]):
                            target_value = row[target_col]
                            scaling_factor = target_value / ref_value
                            voltage_ratio = voltage / reference_voltage
 
                            results.append({
                                'type': key.split('_')[0],
                                'category': category,
                                'arc': arc,
                                'table_type': table_type,
                                'column': base_name,
                                'reference_voltage': reference_voltage,
                                'target_voltage': voltage,
                                'voltage_ratio': voltage_ratio,
                                'reference_value': ref_value,
                                'target_value': target_value,
                                'scaling_factor': scaling_factor,
                                'deviation_from_linear': scaling_factor - voltage_ratio
                            })
 
    result_df = pd.DataFrame(results)
    logging.info(f"Scaling analysis for {category}: {len(result_df)} records")
 
    return result_df
 
def create_category_specific_plots(scaling_df, category, output_dir):
    """Create plots specific to each category."""
    # Create output directory for this category
    category_dir = os.path.join(output_dir, category)
    os.makedirs(category_dir, exist_ok=True)
 
    if scaling_df.empty:
        logging.warning(f"No scaling data for category {category}, skipping plots")
        return
 
    # 1. Scaling factor distribution
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    fig.suptitle(f'{category} - Voltage Scaling Analysis', fontsize=16)
 
    voltage_ratios = sorted(scaling_df['voltage_ratio'].unique())
 
    for idx, voltage_ratio in enumerate(voltage_ratios):
        ax = axes[idx // 3, idx % 3]
 
        data = scaling_df[scaling_df['voltage_ratio'] == voltage_ratio]
 
        if not data.empty:
            # Plot distribution
            ax.hist(data['scaling_factor'], bins=50, alpha=0.7, density=True)
            ax.axvline(x=voltage_ratio, color='red', linestyle='--',
                       label=f'Expected: {voltage_ratio:.3f}')
            ax.axvline(x=data['scaling_factor'].mean(), color='green',
                       linestyle='-', label=f'Mean: {data["scaling_factor"].mean():.3f}')
 
            ax.set_xlabel('Scaling Factor')
            ax.set_ylabel('Density')
            ax.set_title(f'Voltage Ratio: {voltage_ratio:.3f}')
            ax.legend()
            ax.grid(True, alpha=0.3)
 
    plt.tight_layout()
    plt.savefig(os.path.join(category_dir, 'scaling_distributions.png'), dpi=150)
    plt.close()
 
    # 2. Deviation from linear scaling
    fig, ax = plt.subplots(figsize=(12, 8))
 
    # Box plot by voltage ratio
    if 'deviation_from_linear' in scaling_df.columns and 'voltage_ratio' in scaling_df.columns:
        scaling_df.boxplot(column='deviation_from_linear', by='voltage_ratio', ax=ax)
        ax.axhline(y=0, color='red', linestyle='--', alpha=0.5)
        ax.set_xlabel('Voltage Ratio')
        ax.set_ylabel('Deviation from Linear Scaling')
        ax.set_title(f'{category} - Deviation from Linear Scaling')
        ax.grid(True, alpha=0.3)
 
    plt.tight_layout()
    plt.savefig(os.path.join(category_dir, 'scaling_deviation_boxplot.png'), dpi=150)
    plt.close()
 
    # 3. Identify worst scaling cells/arcs
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 12))
 
    # By Arc
    arc_deviation = scaling_df.groupby('arc')['deviation_from_linear'].agg(['mean', 'std', 'count'])
    arc_deviation = arc_deviation[arc_deviation['count'] >= 3]  # Filter out arcs with too few points
    arc_deviation = arc_deviation.sort_values('mean', key=abs, ascending=False)
 
    if not arc_deviation.empty:
        top_arcs = arc_deviation.head(20)
        ax1.bar(range(len(top_arcs)), top_arcs['mean'], yerr=top_arcs['std'])
        ax1.set_xticks(range(len(top_arcs)))
        ax1.set_xticklabels([idx.split('_')[-1] if len(idx) > 20 else idx
                             for idx in top_arcs.index], rotation=45, ha='right')
        ax1.set_ylabel('Mean Deviation from Linear Scaling')
        ax1.set_title(f'{category} - Worst Scaling Arcs')
        ax1.grid(True, alpha=0.3)
 
    # By column type
    col_deviation = scaling_df.groupby('column')['deviation_from_linear'].agg(['mean', 'std', 'count'])
    col_deviation = col_deviation[col_deviation['count'] >= 10]
    col_deviation = col_deviation.sort_values('mean', key=abs, ascending=False)
 
    if not col_deviation.empty:
        ax2.bar(range(len(col_deviation)), col_deviation['mean'], yerr=col_deviation['std'])
        ax2.set_xticks(range(len(col_deviation)))
        ax2.set_xticklabels(col_deviation.index, rotation=45, ha='right')
        ax2.set_ylabel('Mean Deviation from Linear Scaling')
        ax2.set_title(f'{category} - Deviation by Column Type')
        ax2.grid(True, alpha=0.3)
 
    plt.tight_layout()
    plt.savefig(os.path.join(category_dir, 'worst_scaling_analysis.png'), dpi=150)
    plt.close()
 
    # 4. Scatter plot of actual vs expected scaling
    fig, ax = plt.subplots(figsize=(10, 10))
 
    if not scaling_df.empty:
        scatter = ax.scatter(scaling_df['voltage_ratio'], scaling_df['scaling_factor'],
                            alpha=0.5, c=scaling_df['deviation_from_linear'],
                            cmap='RdBu_r', s=20)
 
        # Add identity line
        min_val = min(scaling_df['voltage_ratio'].min(), scaling_df['scaling_factor'].min())
        max_val = max(scaling_df['voltage_ratio'].max(), scaling_df['scaling_factor'].max())
        ax.plot([min_val, max_val], [min_val, max_val], 'k--', alpha=0.5, label='Linear Scaling')
 
        ax.set_xlabel('Voltage Ratio')
        ax.set_ylabel('Actual Scaling Factor')
        ax.set_title(f'{category} - Actual vs Expected Scaling')
        ax.legend()
 
        cbar = plt.colorbar(scatter)
        cbar.set_label('Deviation from Linear')
 
    plt.tight_layout()
    plt.savefig(os.path.join(category_dir, 'scaling_scatter.png'), dpi=150)
    plt.close()
 
    # 5. Summary statistics
    if not scaling_df.empty:
        summary_stats = scaling_df.groupby('voltage_ratio').agg({
            'scaling_factor': ['mean', 'std', 'min', 'max', 'count'],
            'deviation_from_linear': ['mean', 'std']
        }).round(4)
 
        summary_stats.to_csv(os.path.join(category_dir, 'scaling_summary.csv'))
 
        # Save detailed data
        scaling_df.to_csv(os.path.join(category_dir, 'detailed_scaling_data.csv'), index=False)
 
        # Also identify and save the worst scaling points
        if 'deviation_from_linear' in scaling_df.columns:
            worst_points = scaling_df.nlargest(100, 'deviation_from_linear', keep='all')
            worst_points.to_csv(os.path.join(category_dir, 'worst_scaling_points.csv'), index=False)
 
def create_comparison_plots(all_scaling_data, output_dir):
    """Create plots comparing all categories."""
    # Check if we have any data
    if not all_scaling_data or all(df.empty for df in all_scaling_data.values()):
        logging.warning("No scaling data available for comparison plots")
        return
 
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('Cross-Category Voltage Scaling Comparison', fontsize=16)
 
    categories = ['MC', 'Lib', 'abs_err', 'rel_err']
 
    for idx, category in enumerate(categories):
        ax = axes[idx // 2, idx % 2]
 
        if category in all_scaling_data and not all_scaling_data[category].empty:
            df = all_scaling_data[category]
 
            # Box plot by voltage ratio
            if 'deviation_from_linear' in df.columns and 'voltage_ratio' in df.columns:
                df.boxplot(column='deviation_from_linear', by='voltage_ratio', ax=ax)
                ax.axhline(y=0, color='red', linestyle='--', alpha=0.5)
                ax.set_xlabel('Voltage Ratio')
                ax.set_ylabel('Deviation from Linear Scaling')
                ax.set_title(f'{category}')
                ax.grid(True, alpha=0.3)
 
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'category_comparison.png'), dpi=150)
    plt.close()
 
    # Summary comparison
    fig, ax = plt.subplots(figsize=(12, 8))
 
    summary_data = []
    for category in categories:
        if category in all_scaling_data and not all_scaling_data[category].empty:
            df = all_scaling_data[category]
            if 'voltage_ratio' in df.columns and 'deviation_from_linear' in df.columns:
                for voltage_ratio in df['voltage_ratio'].unique():
                    subset = df[df['voltage_ratio'] == voltage_ratio]
                    summary_data.append({
                        'category': category,
                        'voltage_ratio': voltage_ratio,
                        'mean_deviation': subset['deviation_from_linear'].mean(),
                        'std_deviation': subset['deviation_from_linear'].std()
                    })
 
    if summary_data:
        summary_df = pd.DataFrame(summary_data)
 
        # Create grouped bar chart
        voltage_ratios = sorted(summary_df['voltage_ratio'].unique())
        x = np.arange(len(voltage_ratios))
        width = 0.2
 
        for i, category in enumerate(categories):
            if category in summary_df['category'].unique():
                data = summary_df[summary_df['category'] == category]
                means = []
                for vr in voltage_ratios:
                    vr_data = data[data['voltage_ratio'] == vr]
                    if not vr_data.empty:
                        means.append(vr_data['mean_deviation'].values[0])
                    else:
                        means.append(0)
 
                ax.bar(x + i*width, means, width, label=category, alpha=0.7)
 
        ax.axhline(y=0, color='red', linestyle='--', alpha=0.5)
        ax.set_xlabel('Voltage Ratio')
        ax.set_ylabel('Mean Deviation from Linear Scaling')
        ax.set_title('Scaling Deviation Comparison Across Categories')
        ax.set_xticks(x + width * 1.5)
        ax.set_xticklabels([f'{vr:.3f}' for vr in voltage_ratios])
        ax.legend()
        ax.grid(True, alpha=0.3)
 
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'scaling_comparison_summary.png'), dpi=150)
    plt.close()
 
def main():
    import argparse
 
    parser = argparse.ArgumentParser(description='Analyze cross-corner voltage scaling')
    parser.add_argument('--data_dir', type=str, required=True,
                       help='Directory containing analysis results for all corners')
    parser.add_argument('--output_dir', type=str, required=True,
                       help='Output directory for cross-corner analysis')
 
    args = parser.parse_args()
 
    # Setup logging
    setup_logging(args.output_dir)
    logging.info("Starting cross-corner voltage analysis")
 
    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)
 
    # Load and align data
    logging.info("Loading and aligning data across corners...")
    aligned_data = load_and_align_data(args.data_dir)
 
    # Analyze each category separately
    categories = ['MC', 'Lib', 'abs_err', 'rel_err']
    all_scaling_data = {}
 
    for category in categories:
        logging.info(f"Analyzing {category}...")
        scaling_df = analyze_voltage_scaling_individual(aligned_data, category)
 
        if not scaling_df.empty:
            all_scaling_data[category] = scaling_df
            create_category_specific_plots(scaling_df, category, args.output_dir)
        else:
            logging.warning(f"No scaling data found for {category}")
 
    # Create comparison plots
    logging.info("Creating comparison plots...")
    create_comparison_plots(all_scaling_data, args.output_dir)
 
    logging.info("Cross-corner voltage analysis complete")
 
if __name__ == "__main__":
    main()
