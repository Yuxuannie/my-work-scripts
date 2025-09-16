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
from collections import defaultdict
 
def setup_logging(output_dir):
    """Set up logging to file."""
    os.makedirs(output_dir, exist_ok=True)
    log_file = os.path.join(output_dir, "corner_outlier_analysis.log")
 
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
 
def load_outlier_data(data_dir):
    """Load outlier data from all corners."""
    outlier_files = glob.glob(os.path.join(data_dir, "*/*_outliers.json"))
 
    all_outliers = {}
    for file_path in outlier_files:
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
                outliers = json.load(f)
 
            if corner not in all_outliers:
                all_outliers[corner] = {}
            if type_name not in all_outliers[corner]:
                all_outliers[corner][type_name] = {}
 
            file_base = os.path.basename(file_path).replace('_outliers.json', '')
            all_outliers[corner][type_name][file_base] = {
                'voltage': voltage,
                'outliers': outliers
            }
        except Exception as e:
            logging.error(f"Error loading {file_path}: {e}")
 
    return all_outliers
 
def analyze_outliers_by_corner(all_outliers):
    """Analyze outlier distribution by corner."""
    corner_stats = {}
 
    for corner, corner_data in all_outliers.items():
        corner_stats[corner] = {
            'voltage': extract_voltage_from_corner(corner),
            'total_outliers': 0,
            'cell_counts': defaultdict(int),
            'table_position_counts': defaultdict(int),
            'category_counts': defaultdict(int),
            'type_counts': defaultdict(int),
            'sigma_type_counts': defaultdict(int)
        }
 
        for type_name, type_data in corner_data.items():
            for file_name, file_data in type_data.items():
                outliers = file_data['outliers']
 
                # Process late_sigma outliers
                if 'late_sigma' in outliers:
                    for category, category_outliers in outliers['late_sigma'].items():
                        for column, outlier_list in category_outliers.items():
                            for outlier in outlier_list:
                                corner_stats[corner]['total_outliers'] += 1
                                corner_stats[corner]['type_counts'][type_name] += 1
                                corner_stats[corner]['sigma_type_counts']['late_sigma'] += 1
                                corner_stats[corner]['category_counts'][category] += 1
 
                                if 'cell' in outlier:
                                    corner_stats[corner]['cell_counts'][outlier['cell']] += 1
                                if 'table_position' in outlier:
                                    corner_stats[corner]['table_position_counts'][outlier['table_position']] += 1
 
                # Process early_sigma outliers
                if 'early_sigma' in outliers:
                    for category, category_outliers in outliers['early_sigma'].items():
                        for column, outlier_list in category_outliers.items():
                            for outlier in outlier_list:
                                corner_stats[corner]['total_outliers'] += 1
                                corner_stats[corner]['type_counts'][type_name] += 1
                                corner_stats[corner]['sigma_type_counts']['early_sigma'] += 1
                                corner_stats[corner]['category_counts'][category] += 1
 
                                if 'cell' in outlier:
                                    corner_stats[corner]['cell_counts'][outlier['cell']] += 1
                                if 'table_position' in outlier:
                                    corner_stats[corner]['table_position_counts'][outlier['table_position']] += 1
 
    return corner_stats
 
def create_cell_outlier_heatmap(corner_stats, output_dir):
    """Create heatmap showing cell outlier frequency by corner."""
    # Get all unique cells
    all_cells = set()
    for corner, stats in corner_stats.items():
        all_cells.update(stats['cell_counts'].keys())
 
    # Sort cells by total outlier count
    cell_totals = defaultdict(int)
    for corner, stats in corner_stats.items():
        for cell, count in stats['cell_counts'].items():
            cell_totals[cell] += count
 
    sorted_cells = sorted(cell_totals.items(), key=lambda x: x[1], reverse=True)[:20]  # Top 20 cells
    cells = [cell for cell, _ in sorted_cells]
 
    # Create data matrix
    corners = sorted(corner_stats.keys(), key=lambda x: corner_stats[x]['voltage'])
    data_matrix = []
 
    for cell in cells:
        row = []
        for corner in corners:
            count = corner_stats[corner]['cell_counts'].get(cell, 0)
            row.append(count)
        data_matrix.append(row)
 
    # Create heatmap
    plt.figure(figsize=(12, 10))
    df_heatmap = pd.DataFrame(data_matrix, index=cells, columns=[f"{corner}\n({corner_stats[corner]['voltage']}V)" for corner in corners])
 
    sns.heatmap(df_heatmap, annot=True, fmt='d', cmap='YlOrRd', cbar_kws={'label': 'Outlier Count'})
    plt.title('Cell Outlier Frequency by Corner', fontsize=16)
    plt.xlabel('Corner (Voltage)', fontsize=12)
    plt.ylabel('Cell Type', fontsize=12)
    plt.tight_layout()
 
    output_path = os.path.join(output_dir, 'cell_outlier_heatmap_by_corner.png')
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
 
    logging.info(f"Created cell outlier heatmap: {output_path}")
 
    # Also save the data as CSV
    csv_path = os.path.join(output_dir, 'cell_outlier_counts_by_corner.csv')
    df_heatmap.to_csv(csv_path)
    logging.info(f"Saved cell outlier data: {csv_path}")
 
def create_table_position_analysis(corner_stats, output_dir):
    """Analyze table position effects by corner."""
    # Create visualization of table position outliers by corner
    corners = sorted(corner_stats.keys(), key=lambda x: corner_stats[x]['voltage'])
 
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    axes = axes.flatten()
 
    for idx, corner in enumerate(corners):
        ax = axes[idx]
 
        # Get table position data for this corner
        position_counts = corner_stats[corner]['table_position_counts']
 
        if not position_counts:
            ax.text(0.5, 0.5, 'No table position data', ha='center', va='center')
            ax.set_title(f'{corner} ({corner_stats[corner]["voltage"]}V)')
            continue
 
        # Parse positions into 2D grid
        max_idx1 = max_idx2 = 0
        position_matrix = defaultdict(lambda: defaultdict(int))
 
        for position, count in position_counts.items():
            parts = position.split('-')
            if len(parts) == 2:
                try:
                    idx1, idx2 = int(parts[0]), int(parts[1])
                    position_matrix[idx1][idx2] = count
                    max_idx1 = max(max_idx1, idx1)
                    max_idx2 = max(max_idx2, idx2)
                except ValueError:
                    continue
 
        # Create matrix for heatmap
        data_matrix = []
        for i in range(1, max_idx1 + 1):
            row = []
            for j in range(1, max_idx2 + 1):
                row.append(position_matrix[i][j])
            data_matrix.append(row)
 
        # Create heatmap
        if data_matrix:
            im = ax.imshow(data_matrix, cmap='YlOrRd', aspect='auto', interpolation='nearest')
 
            # Add colorbar
            cbar = plt.colorbar(im, ax=ax)
            cbar.set_label('Outlier Count', rotation=270, labelpad=15)
 
            # Add values to cells
            for i in range(len(data_matrix)):
                for j in range(len(data_matrix[0])):
                    value = data_matrix[i][j]
                    if value > 0:
                        ax.text(j, i, str(value), ha='center', va='center',
                               color='black' if value < max([max(row) for row in data_matrix]) / 2 else 'white')
 
            ax.set_title(f'{corner} ({corner_stats[corner]["voltage"]}V)')
            ax.set_xlabel('Index 2')
            ax.set_ylabel('Index 1')
            ax.set_xticks(range(max_idx2))
            ax.set_xticklabels(range(1, max_idx2 + 1))
            ax.set_yticks(range(max_idx1))
            ax.set_yticklabels(range(1, max_idx1 + 1))
 
    plt.suptitle('Table Position Outlier Distribution by Corner', fontsize=16)
    plt.tight_layout()
 
    output_path = os.path.join(output_dir, 'table_position_outliers_by_corner.png')
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
 
    logging.info(f"Created table position analysis: {output_path}")
 
def create_outlier_trend_plots(corner_stats, output_dir):
    """Create plots showing outlier trends across voltage corners."""
    corners = sorted(corner_stats.keys(), key=lambda x: corner_stats[x]['voltage'])
    voltages = [corner_stats[corner]['voltage'] for corner in corners]
 
    # Total outliers trend
    total_outliers = [corner_stats[corner]['total_outliers'] for corner in corners]
 
    plt.figure(figsize=(10, 6))
    plt.plot(voltages, total_outliers, 'o-', marker='o', markersize=10, linewidth=3, color='red')
    plt.title('Total Outliers vs Voltage', fontsize=16)
    plt.xlabel('Voltage (V)', fontsize=12)
    plt.ylabel('Total Outlier Count', fontsize=12)
    plt.grid(True, alpha=0.3)
    plt.xticks(voltages)
 
    # Add value labels
    for i, (v, count) in enumerate(zip(voltages, total_outliers)):
        plt.text(v, count + 5, str(count), ha='center', va='bottom', fontsize=10)
 
    plt.tight_layout()
    output_path = os.path.join(output_dir, 'total_outliers_vs_voltage.png')
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
 
    # Outliers by category
    categories = ['abs_err', 'rel_err']
    plt.figure(figsize=(10, 6))
 
    for category in categories:
        category_counts = [corner_stats[corner]['category_counts'].get(category, 0) for corner in corners]
        plt.plot(voltages, category_counts, 'o-', marker='o', markersize=8, linewidth=2, label=category)
 
    plt.title('Outliers by Category vs Voltage', fontsize=16)
    plt.xlabel('Voltage (V)', fontsize=12)
    plt.ylabel('Outlier Count', fontsize=12)
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.xticks(voltages)
    plt.tight_layout()
 
    output_path = os.path.join(output_dir, 'outliers_by_category_vs_voltage.png')
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
 
    # Outliers by sigma type
    sigma_types = ['late_sigma', 'early_sigma']
    plt.figure(figsize=(10, 6))
 
    for sigma_type in sigma_types:
        sigma_counts = [corner_stats[corner]['sigma_type_counts'].get(sigma_type, 0) for corner in corners]
        plt.plot(voltages, sigma_counts, 'o-', marker='s', markersize=8, linewidth=2, label=sigma_type)
 
    plt.title('Outliers by Sigma Type vs Voltage', fontsize=16)
    plt.xlabel('Voltage (V)', fontsize=12)
    plt.ylabel('Outlier Count', fontsize=12)
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.xticks(voltages)
    plt.tight_layout()
 
    output_path = os.path.join(output_dir, 'outliers_by_sigma_type_vs_voltage.png')
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
 
def create_corner_specific_cell_analysis(corner_stats, output_dir):
    """Analyze which cells are problematic only at specific corners."""
    # Find cells that are outliers only at specific corners
    corner_specific_cells = defaultdict(list)
    all_corners = list(corner_stats.keys())
 
    # Get all unique cells
    all_cells = set()
    for corner, stats in corner_stats.items():
        all_cells.update(stats['cell_counts'].keys())
 
    for cell in all_cells:
        corners_with_outliers = []
        outlier_counts = []
 
        for corner in all_corners:
            count = corner_stats[corner]['cell_counts'].get(cell, 0)
            if count > 0:
                corners_with_outliers.append(corner)
                outlier_counts.append(count)
 
        # Categorize cells
        if len(corners_with_outliers) == 1:
            corner_specific_cells['single_corner'].append({
                'cell': cell,
                'corner': corners_with_outliers[0],
                'count': outlier_counts[0]
            })
        elif len(corners_with_outliers) == 2:
            corner_specific_cells['two_corners'].append({
                'cell': cell,
                'corners': corners_with_outliers,
                'counts': outlier_counts
            })
        elif len(corners_with_outliers) > 2:
            corner_specific_cells['multiple_corners'].append({
                'cell': cell,
                'corners': corners_with_outliers,
                'counts': outlier_counts
            })
 
    # Create visualization
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
 
    # Bar chart for single-corner outliers
    single_corner_data = corner_specific_cells['single_corner']
    if single_corner_data:
        # Sort by count
        single_corner_data.sort(key=lambda x: x['count'], reverse=True)
 
        cells = [item['cell'] for item in single_corner_data[:15]]  # Top 15
        counts = [item['count'] for item in single_corner_data[:15]]
        corners = [item['corner'] for item in single_corner_data[:15]]
 
        # Create color map for corners
        corner_colors = {corner: f'C{i}' for i, corner in enumerate(all_corners)}
        colors = [corner_colors[corner] for corner in corners]
 
        bars = ax1.bar(range(len(cells)), counts, color=colors)
        ax1.set_xticks(range(len(cells)))
        ax1.set_xticklabels(cells, rotation=45, ha='right')
        ax1.set_ylabel('Outlier Count')
        ax1.set_title('Cells with Outliers at Single Corner Only')
 
        # Add legend
        legend_elements = [plt.Rectangle((0,0),1,1, color=corner_colors[corner], label=corner)
                          for corner in all_corners]
        ax1.legend(handles=legend_elements, loc='upper right')
 
    # Summary statistics
    summary_data = [
        ['Single Corner Only', len(corner_specific_cells['single_corner'])],
        ['Two Corners', len(corner_specific_cells['two_corners'])],
        ['Multiple Corners', len(corner_specific_cells['multiple_corners'])]
    ]
 
    ax2.axis('tight')
    ax2.axis('off')
    table = ax2.table(cellText=summary_data, colLabels=['Category', 'Cell Count'],
                      cellLoc='center', loc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(12)
    table.scale(1.2, 1.5)
    ax2.set_title('Corner Specificity Summary')
 
    plt.tight_layout()
    output_path = os.path.join(output_dir, 'corner_specific_cell_analysis.png')
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
 
    # Save detailed data
    csv_data = []
    for category, cells in corner_specific_cells.items():
        if category == 'single_corner':
            for item in cells:
                csv_data.append({
                    'category': category,
                    'cell': item['cell'],
                    'corners': item['corner'],
                    'total_outliers': item['count']
                })
        else:
            for item in cells:
                csv_data.append({
                    'category': category,
                    'cell': item['cell'],
                    'corners': ','.join(item['corners']),
                    'total_outliers': sum(item['counts'])
                })
 
    df = pd.DataFrame(csv_data)
    csv_path = os.path.join(output_dir, 'corner_specific_cells.csv')
    df.to_csv(csv_path, index=False)
    logging.info(f"Saved corner-specific cell data: {csv_path}")
 
def create_summary_report(corner_stats, output_dir):
    """Create a summary report of corner-specific outlier analysis."""
    summary = []
 
    for corner, stats in corner_stats.items():
        # Find top cells for this corner
        top_cells = sorted(stats['cell_counts'].items(), key=lambda x: x[1], reverse=True)[:3]
 
        summary.append({
            'corner': corner,
            'voltage': stats['voltage'],
            'total_outliers': stats['total_outliers'],
            'abs_err_outliers': stats['category_counts'].get('abs_err', 0),
            'rel_err_outliers': stats['category_counts'].get('rel_err', 0),
            'late_sigma_outliers': stats['sigma_type_counts'].get('late_sigma', 0),
            'early_sigma_outliers': stats['sigma_type_counts'].get('early_sigma', 0),
            'delay_outliers': stats['type_counts'].get('delay', 0),
            'slew_outliers': stats['type_counts'].get('slew', 0),
            'top_cell_1': top_cells[0][0] if len(top_cells) > 0 else '',
            'top_cell_1_count': top_cells[0][1] if len(top_cells) > 0 else 0,
            'top_cell_2': top_cells[1][0] if len(top_cells) > 1 else '',
            'top_cell_2_count': top_cells[1][1] if len(top_cells) > 1 else 0,
            'top_cell_3': top_cells[2][0] if len(top_cells) > 2 else '',
            'top_cell_3_count': top_cells[2][1] if len(top_cells) > 2 else 0
        })
 
    # Sort by voltage
    summary.sort(key=lambda x: x['voltage'])
 
    # Convert to DataFrame and save
    df = pd.DataFrame(summary)
    csv_path = os.path.join(output_dir, 'corner_outlier_summary.csv')
    df.to_csv(csv_path, index=False)
 
    logging.info(f"Created corner outlier summary: {csv_path}")
 
    return df
 
def main():
    import argparse
 
    parser = argparse.ArgumentParser(description='Analyze outliers by corner')
    parser.add_argument('--data_dir', type=str, required=True,
                       help='Directory containing analysis results for all corners')
    parser.add_argument('--output_dir', type=str, required=True,
                       help='Output directory for corner outlier analysis')
 
    args = parser.parse_args()
 
    # Setup logging
    setup_logging(args.output_dir)
    logging.info("Starting corner-specific outlier analysis")
 
    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)
 
    # Load outlier data
    logging.info("Loading outlier data...")
    all_outliers = load_outlier_data(args.data_dir)
 
    # Analyze outliers by corner
    logging.info("Analyzing outliers by corner...")
    corner_stats = analyze_outliers_by_corner(all_outliers)
 
    # Create visualizations
    logging.info("Creating visualizations...")
    create_cell_outlier_heatmap(corner_stats, args.output_dir)
    create_table_position_analysis(corner_stats, args.output_dir)
    create_outlier_trend_plots(corner_stats, args.output_dir)
    create_corner_specific_cell_analysis(corner_stats, args.output_dir)
 
    # Create summary report
    logging.info("Creating summary report...")
    create_summary_report(corner_stats, args.output_dir)
 
    logging.info("Corner-specific outlier analysis complete")
 
if __name__ == "__main__":
    main()
