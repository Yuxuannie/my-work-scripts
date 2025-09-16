#!/usr/bin/env python3
 
import os
import json
import argparse
import pandas as pd
import numpy as np
import glob
import logging
import traceback
import sys
from datetime import datetime
from jinja2 import Template
import shutil
import re
 
def setup_logging(output_dir):
    """Set up logging to file."""
    os.makedirs(output_dir, exist_ok=True)
    log_file = os.path.join(output_dir, "report_generator.log")
 
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
    parser = argparse.ArgumentParser(description='Generate HTML report for timing analysis')
    parser.add_argument('--data_dir', type=str, required=True, help='Directory with analysis data')
    parser.add_argument('--output_dir', type=str, required=True, help='Output directory for HTML report')
    parser.add_argument('--debug', action='store_true', help='Enable additional debug output')
    return parser.parse_args()
 
def get_column_case_insensitive(df, column_name):
    """Get the actual column name with case-insensitive matching."""
    for col in df.columns:
        if col.lower() == column_name.lower():
            return col
    return None
 
def filter_dataframe_by_category(df, category_value, debug=False):
    """Filter dataframe by category with case-insensitive matching."""
    if df is None or df.empty:
        return pd.DataFrame()
 
    # Try to find the category column
    category_col = get_column_case_insensitive(df, 'Category')
 
    if debug:
        logging.debug(f"DataFrame columns: {df.columns.tolist()}")
        logging.debug(f"Looking for category column matching 'Category'")
        logging.debug(f"Found column: {category_col}")
 
    if category_col:
        # Category column found, filter by it
        try:
            return df[df[category_col].str.lower() == category_value.lower()].copy()
        except Exception as e:
            logging.error(f"Error filtering by {category_col}: {e}")
            logging.error(traceback.format_exc())
            return pd.DataFrame()
    else:
        logging.warning(f"No category column found in dataframe")
        return pd.DataFrame()
 
def collect_results(data_dir):
    """Collect all analysis results from data directory."""
    logging.info(f"Collecting results from {data_dir}")
 
    # Find all corner-type subdirectories
    subdirs = [d for d in os.listdir(data_dir)
              if os.path.isdir(os.path.join(data_dir, d)) and '_' in d]
 
    # Initialize results structure
    results = {
        'corners': [],
        'types': [],
        'late_sigma_correlations': pd.DataFrame(),
        'early_sigma_correlations': pd.DataFrame(),
        'outliers': {},
        'correlation_tables': {},
        'images': {}
    }
 
    # Extract corners and types
    for subdir in subdirs:
        parts = subdir.split('_')
        if len(parts) >= 2:
            corner = '_'.join(parts[:-1])
            type_name = parts[-1]
 
            if corner not in results['corners']:
                results['corners'].append(corner)
 
            if type_name not in results['types']:
                results['types'].append(type_name)
 
    results['corners'].sort()
    results['types'].sort()
 
    logging.info(f"Found {len(results['corners'])} corners and {len(results['types'])} types")
 
    # Collect correlation data
    all_late_sigma_correlations = []
    all_early_sigma_correlations = []
 
    for subdir in subdirs:
        subdir_path = os.path.join(data_dir, subdir)
 
        # Find correlation files
        corr_files = glob.glob(os.path.join(subdir_path, "*_correlations.json"))
        sigma_files = glob.glob(os.path.join(subdir_path, "*_sigma_info.json"))
        outlier_files = glob.glob(os.path.join(subdir_path, "*_outliers.json"))
 
        for corr_file in corr_files:
            try:
                with open(corr_file, 'r') as f:
                    correlations = json.load(f)
 
                file_base = os.path.basename(corr_file).replace("_correlations.json", "")
                logging.debug(f"Processing correlation file: {file_base}")
 
                parts = subdir.split('_')
                if len(parts) >= 2:
                    corner = '_'.join(parts[:-1])
                    type_name = parts[-1]
 
                    # Get sigma column names
                    sigma_info = {}
                    for sigma_file in sigma_files:
                        if os.path.basename(sigma_file).startswith(file_base):
                            with open(sigma_file, 'r') as f:
                                sigma_info = json.load(f)
                            break
 
                    late_sigma_name = sigma_info.get('late_sigma', 'late_sigma')
                    early_sigma_name = sigma_info.get('early_sigma', 'early_sigma')
 
                    # Process late_sigma correlations
                    if 'late_sigma' in correlations:
                        for category, category_corrs in correlations['late_sigma'].items():
                            for column, corr_value in category_corrs.items():
                                # Determine moment type
                                if 'std' in column.lower():
                                    moment_type = 'STD'
                                elif 'skew' in column.lower():
                                    moment_type = 'SKEW'
                                elif 'meanshift' in column.lower():
                                    moment_type = 'MEANSHIFT'
                                else:
                                    moment_type = 'OTHER'
 
                                all_late_sigma_correlations.append({
                                    'file': file_base,
                                    'corner': corner,
                                    'type': type_name,
                                    'category': category,
                                    'column': column,
                                    'moment_type': moment_type,
                                    'sigma_name': late_sigma_name,
                                    'correlation': corr_value
                                })
 
                    # Process early_sigma correlations
                    if 'early_sigma' in correlations:
                        for category, category_corrs in correlations['early_sigma'].items():
                            for column, corr_value in category_corrs.items():
                                # Determine moment type
                                if 'std' in column.lower():
                                    moment_type = 'STD'
                                elif 'skew' in column.lower():
                                    moment_type = 'SKEW'
                                elif 'meanshift' in column.lower():
                                    moment_type = 'MEANSHIFT'
                                else:
                                    moment_type = 'OTHER'
 
                                all_early_sigma_correlations.append({
                                    'file': file_base,
                                    'corner': corner,
                                    'type': type_name,
                                    'category': category,
                                    'column': column,
                                    'moment_type': moment_type,
                                    'sigma_name': early_sigma_name,
                                    'correlation': corr_value
                                })
            except Exception as e:
                logging.error(f"Error processing {corr_file}: {e}")
                logging.error(traceback.format_exc())
 
        # Load outlier data
        for outlier_file in outlier_files:
            try:
                file_base = os.path.basename(outlier_file).replace("_outliers.json", "")
                with open(outlier_file, 'r') as f:
                    outliers = json.load(f)
 
                # Store in results
                results['outliers'][file_base] = outliers
                logging.debug(f"Loaded outliers from {file_base}")
            except Exception as e:
                logging.error(f"Error loading outliers from {outlier_file}: {e}")
 
    # Convert to DataFrame
    if all_late_sigma_correlations:
        results['late_sigma_correlations'] = pd.DataFrame(all_late_sigma_correlations)
        logging.info(f"Collected {len(results['late_sigma_correlations'])} late sigma correlation data points")
        logging.debug(f"Late sigma columns: {results['late_sigma_correlations'].columns.tolist()}")
 
    if all_early_sigma_correlations:
        results['early_sigma_correlations'] = pd.DataFrame(all_early_sigma_correlations)
        logging.info(f"Collected {len(results['early_sigma_correlations'])} early sigma correlation data points")
        logging.debug(f"Early sigma columns: {results['early_sigma_correlations'].columns.tolist()}")
 
    # Generate correlation tables by moment type
    for moment_type in ['STD', 'SKEW', 'MEANSHIFT']:
        # Create correlation tables for late sigma
        if not results['late_sigma_correlations'].empty:
            late_table = generate_correlation_table(
                results['late_sigma_correlations'],
                moment_type,
                'late_sigma'
            )
            results['correlation_tables'][f'late_sigma_{moment_type}'] = late_table
 
        # Create correlation tables for early sigma
        if not results['early_sigma_correlations'].empty:
            early_table = generate_correlation_table(
                results['early_sigma_correlations'],
                moment_type,
                'early_sigma'
            )
            results['correlation_tables'][f'early_sigma_{moment_type}'] = early_table
 
    # Collect visualization images
    for subdir in subdirs:
        plots_dir = os.path.join(data_dir, subdir, 'plots')
        if os.path.isdir(plots_dir):
            # Find all image files
            image_files = glob.glob(os.path.join(plots_dir, "*.png"))
 
            for img_file in image_files:
                img_name = os.path.basename(img_file)
                results['images'][img_name] = img_file
 
    # Add summary visualizations if they exist
    summary_plots_dirs = [os.path.join(data_dir, d, 'plots') for d in os.listdir(data_dir)
                         if os.path.isdir(os.path.join(data_dir, d)) and 'report' not in d.lower()]
 
    for plots_dir in summary_plots_dirs:
        if os.path.isdir(plots_dir):
            image_files = glob.glob(os.path.join(plots_dir, "*.png"))
 
            for img_file in image_files:
                img_name = os.path.basename(img_file)
                results['images'][img_name] = img_file
 
    # Add files from plots directory in data_dir if it exists
    plots_dir = os.path.join(data_dir, 'plots')
    if os.path.isdir(plots_dir):
        image_files = glob.glob(os.path.join(plots_dir, "*.png"))
 
        for img_file in image_files:
            img_name = os.path.basename(img_file)
            results['images'][img_name] = img_file
 
    logging.info(f"Collected {len(results['images'])} visualization images")
 
    return results
 
def generate_correlation_table(df, moment_type, sigma_type):
    """Generate a correlation table for a specific moment type and sigma type."""
    if df.empty:
        return pd.DataFrame()
 
    # Filter for the moment type
    moment_df = df[df['moment_type'] == moment_type].copy()
 
    if moment_df.empty:
        return pd.DataFrame()
 
    # Create pivot table: corner Ã— type Ã— category
    pivot_df = pd.pivot_table(
        moment_df,
        values='correlation',
        index=['corner', 'type'],
        columns=['category'],
        aggfunc='mean'
    )
 
    return pivot_df
 
def generate_summary_data(results):
    """Generate summary statistics from correlation data."""
    summary = {
        'late_sigma': {
            'avg_by_category': {},
            'avg_by_moment': {},
            'avg_by_corner': {},
            'avg_by_type': {},
            'top_correlations': [],
            'bottom_correlations': []
        },
        'early_sigma': {
            'avg_by_category': {},
            'avg_by_moment': {},
            'avg_by_corner': {},
            'avg_by_type': {},
            'top_correlations': [],
            'bottom_correlations': []
        }
    }
 
    # Process late sigma correlations
    if not results['late_sigma_correlations'].empty:
        df = results['late_sigma_correlations']
 
        # Get category column
        category_col = get_column_case_insensitive(df, 'category')
        corner_col = get_column_case_insensitive(df, 'corner')
        type_col = get_column_case_insensitive(df, 'type')
        moment_col = get_column_case_insensitive(df, 'moment_type')
        corr_col = get_column_case_insensitive(df, 'correlation')
 
        if category_col and corr_col:
            # Average by category
            summary['late_sigma']['avg_by_category'] = df.groupby(category_col)[corr_col].mean().to_dict()
 
        if moment_col and corr_col:
            # Average by moment type
            summary['late_sigma']['avg_by_moment'] = df.groupby(moment_col)[corr_col].mean().to_dict()
 
        if corner_col and corr_col:
            # Average by corner
            summary['late_sigma']['avg_by_corner'] = df.groupby(corner_col)[corr_col].mean().to_dict()
 
        if type_col and corr_col:
            # Average by type
            summary['late_sigma']['avg_by_type'] = df.groupby(type_col)[corr_col].mean().to_dict()
 
        if corr_col:
            # Top 10 correlations
            top_corrs = df.sort_values(by=corr_col, ascending=False).head(10).to_dict('records')
            summary['late_sigma']['top_correlations'] = top_corrs
 
            # Bottom 10 correlations
            bottom_corrs = df.sort_values(by=corr_col, ascending=True).head(10).to_dict('records')
            summary['late_sigma']['bottom_correlations'] = bottom_corrs
 
    # Process early sigma correlations
    if not results['early_sigma_correlations'].empty:
        df = results['early_sigma_correlations']
 
        # Get category column
        category_col = get_column_case_insensitive(df, 'category')
        corner_col = get_column_case_insensitive(df, 'corner')
        type_col = get_column_case_insensitive(df, 'type')
        moment_col = get_column_case_insensitive(df, 'moment_type')
        corr_col = get_column_case_insensitive(df, 'correlation')
 
        if category_col and corr_col:
            # Average by category
            summary['early_sigma']['avg_by_category'] = df.groupby(category_col)[corr_col].mean().to_dict()
 
        if moment_col and corr_col:
            # Average by moment type
            summary['early_sigma']['avg_by_moment'] = df.groupby(moment_col)[corr_col].mean().to_dict()
 
        if corner_col and corr_col:
            # Average by corner
            summary['early_sigma']['avg_by_corner'] = df.groupby(corner_col)[corr_col].mean().to_dict()
 
        if type_col and corr_col:
            # Average by type
            summary['early_sigma']['avg_by_type'] = df.groupby(type_col)[corr_col].mean().to_dict()
 
        if corr_col:
            # Top 10 correlations
            top_corrs = df.sort_values(by=corr_col, ascending=False).head(10).to_dict('records')
            summary['early_sigma']['top_correlations'] = top_corrs
 
            # Bottom 10 correlations
            bottom_corrs = df.sort_values(by=corr_col, ascending=True).head(10).to_dict('records')
            summary['early_sigma']['bottom_correlations'] = bottom_corrs
 
    # Process outlier data
    if results['outliers']:
        # Count outliers by cell type
        cell_counts = {}
        table_position_counts = {}
 
        for file_name, outliers in results['outliers'].items():
            # Process late sigma outliers
            if 'late_sigma' in outliers:
                for category, category_outliers in outliers['late_sigma'].items():
                    for column, outlier_list in category_outliers.items():
                        for outlier in outlier_list:
                            # Count by cell
                            if 'cell' in outlier:
                                cell = outlier['cell']
                                if cell not in cell_counts:
                                    cell_counts[cell] = 0
                                cell_counts[cell] += 1
 
                            # Count by table position
                            if 'table_position' in outlier:
                                table_pos = outlier['table_position']
                                if table_pos not in table_position_counts:
                                    table_position_counts[table_pos] = 0
                                table_position_counts[table_pos] += 1
 
            # Process early sigma outliers
            if 'early_sigma' in outliers:
                for category, category_outliers in outliers['early_sigma'].items():
                    for column, outlier_list in category_outliers.items():
                        for outlier in outlier_list:
                            # Count by cell
                            if 'cell' in outlier:
                                cell = outlier['cell']
                                if cell not in cell_counts:
                                    cell_counts[cell] = 0
                                cell_counts[cell] += 1
 
                            # Count by table position
                            if 'table_position' in outlier:
                                table_pos = outlier['table_position']
                                if table_pos not in table_position_counts:
                                    table_position_counts[table_pos] = 0
                                table_position_counts[table_pos] += 1
 
        # Add to summary
        summary['outliers'] = {
            'cell_counts': dict(sorted(cell_counts.items(), key=lambda x: x[1], reverse=True)),
            'table_position_counts': dict(sorted(table_position_counts.items(), key=lambda x: x[1], reverse=True))
        }
 
    return summary
 
def format_correlation_table(table_df, categories):
    """Format correlation table for HTML display with color coding."""
    if table_df.empty:
        return "<p>No data available for this table.</p>"
 
    html = '<table class="correlation-table">'
 
    # Header row with categories
    html += '<tr class="header-row"><th >Corner</th><th >Type</th>'
    for category in categories:
        html += f'<th>{category}</th>'
    html += '</tr>'
 
    # Data rows
    for idx, row in table_df.iterrows():
        corner, type_name = idx
        html += f'<tr><td>{corner}</td><td>{type_name}</td>'
 
        for category in categories:
            value = row.get(category, float('nan'))
 
            if pd.notna(value):
                # Determine cell class based on correlation value
                if value >= 0.75:
                    cell_class = 'strong-positive'
                elif value >= 0.5:
                    cell_class = 'positive'
                elif value >= 0.25:
                    cell_class = 'weak-positive'
                elif value > -0.25:
                    cell_class = 'neutral'
                elif value > -0.5:
                    cell_class = 'weak-negative'
                elif value > -0.75:
                    cell_class = 'negative'
                else:
                    cell_class = 'strong-negative'
 
                html += f'<td class="{cell_class}">{value:.4f}</td>'
            else:
                html += '<td class="neutral">N/A</td>'
 
        html += '</tr>'
 
    html += '</table>'
    return html
 
def create_html_template():
    """Create HTML template for the report."""
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Timing Analysis Report</title>
    <style>
        /* Keep existing styles */
       
        /* Error highlighting styles */
        .error-category {
            background-color: #fff8e1;
            border-left: 4px solid #ff9800;
            padding-left: 15px;
        }
       
        .error-title {
            color: #d84315;
            font-weight: bold;
        }
       
        .error-card {
            border: 2px solid #ff9800;
            box-shadow: 0 2px 12px rgba(255, 152, 0, 0.2);
        }
       
        .highlight-row {
            background-color: #fff8e1 !important;
            font-weight: bold;
        }
       
        .error-badge {
            display: inline-block;
            background-color: #ff9800;
            color: white;
            font-size: 0.8rem;
            padding: 2px 6px;
            border-radius: 4px;
            margin-left: 8px;
        }
       
        /* Original CSS */
        :root {
            --primary-color: #3f51b5;
            --secondary-color: #4caf50;
            --accent-color: #ff5722;
            --light-bg: #f5f7fa;
            --dark-bg: #37474f;
            --text-color: #333;
            --light-text: #fff;
            --border-color: #ddd;
        }
       
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: var(--text-color);
            margin: 0;
            padding: 0;
            background-color: var(--light-bg);
        }
       
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
       
        header {
            background-color: var(--primary-color);
            color: var(--light-text);
            padding: 20px 0;
            margin-bottom: 30px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
       
        header .container {
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
       
        h1, h2, h3, h4 {
            color: var(--primary-color);
            margin-top: 0;
        }
       
        header h1 {
            color: var(--light-text);
            margin: 0;
        }
       
        .timestamp {
            font-size: 0.9rem;
            opacity: 0.8;
        }
       
        .card {
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin-bottom: 30px;
            overflow: hidden;
        }
       
        .card-header {
            background-color: var(--primary-color);
            color: var(--light-text);
            padding: 15px 20px;
            font-weight: bold;
        }
       
        .card-body {
            padding: 20px;
        }
       
        .tabs {
            display: flex;
            border-bottom: 1px solid var(--border-color);
            margin-bottom: 20px;
            background-color: #f8f9fa;
            border-radius: 5px 5px 0 0;
            overflow: hidden;
        }
       
        .tab {
            padding: 12px 20px;
            cursor: pointer;
            background-color: #f8f9fa;
            border: none;
            border-right: 1px solid var(--border-color);
            transition: background-color 0.3s;
            font-weight: 500;
        }
       
        .tab:last-child {
            border-right: none;
        }
       
        .tab.active {
            background-color: white;
            border-bottom: 3px solid var(--primary-color);
            font-weight: bold;
        }
       
        .tab-content {
            display: none;
            animation: fadeIn 0.5s;
        }
       
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
       
        .tab-content.active {
            display: block;
        }
       
        .metric-group {
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 1px solid var(--border-color);
        }
       
        .metric-group:last-child {
            border-bottom: none;
        }
       
        .metric-group-title {
            margin-bottom: 15px;
            color: var(--dark-bg);
            font-weight: 600;
            display: flex;
            align-items: center;
        }
       
        .metric-group-title::after {
            content: '';
            flex-grow: 1;
            height: 1px;
            background-color: var(--border-color);
            margin-left: 15px;
        }
       
        .key-metrics {
            display: flex;
            flex-wrap: wrap;
            gap: 20px;
            margin-bottom: 30px;
        }
       
        .metric-card {
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            padding: 15px;
            flex: 1 1 200px;
            text-align: center;
            border-top: 4px solid var(--primary-color);
        }
       
        .metric-card h3 {
            margin-top: 0;
            font-size: 1.1rem;
        }
       
        .metric-value {
            font-size: 2.2rem;
            font-weight: bold;
            color: var(--primary-color);
            margin: 10px 0;
        }
       
        .metric-desc {
            font-size: 0.9rem;
            color: #666;
        }
       
        .visualization-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
       
        .visualization-card {
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            overflow: hidden;
        }
       
        .visualization-card img {
            width: 100%;
            height: auto;
            display: block;
            cursor: pointer;
            transition: opacity 0.2s;
        }
       
        .visualization-card img:hover {
            opacity: 0.85;
        }
       
        .visualization-details {
            padding: 15px;
        }
       
        .visualization-details h3 {
            margin-top: 0;
            font-size: 1.1rem;
        }
       
        .visualization-details p {
            font-size: 0.9rem;
            color: #666;
            margin-bottom: 0;
        }
       
        table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
        }
       
        table th, table td {
            padding: 12px 15px;
            text-align: left;
            border-bottom: 1px solid var(--border-color);
        }
       
        table th {
            background-color: #f8f9fa;
            font-weight: 600;
        }
       
        table tr:nth-child(even) {
            background-color: #f8f9fa;
        }
       
        table tr:hover {
            background-color: #f1f1f1;
        }
       
        .nav-tabs {
            border-bottom: 1px solid var(--border-color);
            margin-bottom: 20px;
        }
       
        .nav-tabs .tab {
            display: inline-block;
            padding: 8px 15px;
            margin-right: 5px;
            cursor: pointer;
            border: 1px solid transparent;
            border-bottom: none;
            border-radius: 4px 4px 0 0;
            background-color: #f8f9fa;
        }
       
        .nav-tabs .tab.active {
            background-color: white;
            border-color: var(--border-color);
            border-bottom: 2px solid white;
            margin-bottom: -1px;
            color: var(--primary-color);
            font-weight: bold;
        }
 
        /* Tab organization with error metrics first */
        .tablinks.error-tab {
            background-color: #fff8e1;
            font-weight: bold;
            border-top: 3px solid #ff9800;
        }
       
        footer {
            background-color: var(--dark-bg);
            color: var(--light-text);
            padding: 20px 0;
            margin-top: 30px;
            font-size: 0.9rem;
        }
       
        /* Image Modal Styles */
        .modal {
            display: none;
            position: fixed;
            z-index: 1000;
            padding-top: 50px;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            overflow: auto;
            background-color: rgba(0,0,0,0.9);
        }
       
        .modal-content {
            margin: auto;
            display: block;
            max-width: 90%;
            max-height: 90vh;
        }
       
        .modal-caption {
            margin: auto;
            display: block;
            width: 80%;
            max-width: 700px;
            text-align: center;
            color: white;
            padding: 10px 0;
            height: 30px;
        }
       
        .close {
            position: absolute;
            top: 15px;
            right: 35px;
            color: #f1f1f1;
            font-size: 40px;
            font-weight: bold;
            transition: 0.3s;
            cursor: pointer;
        }
       
        .close:hover,
        .close:focus {
            color: #bbb;
            text-decoration: none;
            cursor: pointer;
        }
       
        /* Correlation Table Styles */
        .correlation-table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
            font-size: 0.9rem;
        }
       
        .correlation-table th, .correlation-table td {
            padding: 10px;
            text-align: center;
            border: 1px solid var(--border-color);
        }
       
        .correlation-table th {
            background-color: #f2f2f2;
            font-weight: bold;
        }
       
        .correlation-table td {
            background-color: white;
        }
       
        .correlation-table tr.header-row th {
            background-color: var(--primary-color);
            color: white;
            text-align: center;
        }
       
        .correlation-table td.strong-positive {
            background-color: #4caf50;
            color: white;
        }
       
        .correlation-table td.positive {
            background-color: #8bc34a;
            color: black;
        }
       
        .correlation-table td.weak-positive {
            background-color: #cddc39;
            color: black;
        }
       
        .correlation-table td.weak-negative {
            background-color: #ffeb3b;
            color: black;
        }
       
        .correlation-table td.negative {
            background-color: #ff9800;
            color: black;
        }
       
        .correlation-table td.strong-negative {
            background-color: #f44336;
            color: white;
        }
       
        .correlation-table td.neutral {
            background-color: #e0e0e0;
            color: black;
        }
       
        .correlation-legend {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin-bottom: 20px;
        }
       
        .legend-item {
            display: flex;
            align-items: center;
            font-size: 0.9rem;
        }
       
        .legend-color {
            width: 20px;
            height: 20px;
            display: inline-block;
            margin-right: 5px;
            border: 1px solid #ccc;
        }
       
        @media (max-width: 768px) {
            header .container {
                flex-direction: column;
                text-align: center;
            }
           
            .timestamp {
                margin-top: 10px;
            }
           
            .tabs {
                flex-direction: column;
            }
           
            .tab {
                border-right: none;
                border-bottom: 1px solid var(--border-color);
            }
           
            .modal-content {
                width: 100%;
            }
        }
    </style>
</head>
<body>
    <header>
        <div class="container">
            <h1>Timing Correlation Analysis Report</h1>
            <div class="timestamp">Generated on: {{ timestamp }}</div>
        </div>
    </header>
   
    <div class="container">
        <div class="card">
            <div class="card-header">
                Executive Summary
            </div>
            <div class="card-body">
                <p>This report analyzes correlations between sigma values (late_sigma and early_sigma) and various moments (standard deviation, skewness, meanshift) across different corners and timing types, with <strong>special focus on error metrics (rel_err, abs_err)</strong>.</p>
               
                <!-- Updated tab ordering to prioritize error metrics -->
                <div class="nav-tabs">
                    <span class="tab active error-tab" onclick="switchSigmaTab(event, 'error-metrics')">Error Metrics <span class="error-badge">PRIORITY</span></span>
                    <span class="tab" onclick="switchSigmaTab(event, 'late-metrics')">Late Sigma</span>
                    <span class="tab" onclick="switchSigmaTab(event, 'early-metrics')">Early Sigma</span>
                </div>
               
                <div id="error-metrics" class="sigma-tab-content">
                    <div class="key-metrics">
                        <div class="metric-card error-card">
                            <h3 class="error-title">Rel_Err Correlations</h3>
                            <div class="metric-value">{{ rel_err_count }}</div>
                            <div class="metric-desc">Correlations analyzed in relative error</div>
                        </div>
                        <div class="metric-card error-card">
                            <h3 class="error-title">Abs_Err Correlations</h3>
                            <div class="metric-value">{{ abs_err_count }}</div>
                            <div class="metric-desc">Correlations analyzed in absolute error</div>
                        </div>
                        <div class="metric-card error-card">
                            <h3 class="error-title">Max Error Correlation</h3>
                            <div class="metric-value">{{ error_max_corr|round(4) }}</div>
                            <div class="metric-desc">Strongest correlation in error metrics</div>
                        </div>
                    </div>
                </div>
               
                <div id="late-metrics" class="sigma-tab-content" style="display: none;">
                    <div class="key-metrics">
                        <div class="metric-card">
                            <h3>Data Points</h3>
                            <div class="metric-value">{{ late_sigma_count }}</div>
                            <div class="metric-desc">Correlations analyzed</div>
                        </div>
                        <div class="metric-card">
                            <h3>Average Correlation</h3>
                            <div class="metric-value">{{ late_sigma_avg|round(4) }}</div>
                            <div class="metric-desc">Overall average correlation</div>
                        </div>
                        <div class="metric-card">
                            <h3>Max Correlation</h3>
                            <div class="metric-value">{{ late_sigma_max|round(4) }}</div>
                            <div class="metric-desc">Highest correlation found</div>
                        </div>
                        <div class="metric-card">
                            <h3>Min Correlation</h3>
                            <div class="metric-value">{{ late_sigma_min|round(4) }}</div>
                            <div class="metric-desc">Lowest correlation found</div>
                        </div>
                    </div>
                </div>
               
                <div id="early-metrics" class="sigma-tab-content" style="display: none;">
                    <div class="key-metrics">
                        <div class="metric-card">
                            <h3>Data Points</h3>
                            <div class="metric-value">{{ early_sigma_count }}</div>
                            <div class="metric-desc">Correlations analyzed</div>
                        </div>
                        <div class="metric-card">
                            <h3>Average Correlation</h3>
                            <div class="metric-value">{{ early_sigma_avg|round(4) }}</div>
                            <div class="metric-desc">Overall average correlation</div>
                        </div>
                        <div class="metric-card">
                            <h3>Max Correlation</h3>
                            <div class="metric-value">{{ early_sigma_max|round(4) }}</div>
                            <div class="metric-desc">Highest correlation found</div>
                        </div>
                        <div class="metric-card">
                            <h3>Min Correlation</h3>
                            <div class="metric-value">{{ early_sigma_min|round(4) }}</div>
                            <div class="metric-desc">Lowest correlation found</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
       
        <div class="card">
            <div class="tabs">
                <!-- Reordered tabs to put error metrics first -->
                <button class="tab active error-tab" onclick="openTab(event, 'correlation-tables')">Correlation Tables <span class="error-badge">NEW</span></button>
                <button class="tab error-tab" onclick="openTab(event, 'outlier-analysis')">Outlier Analysis <span class="error-badge">NEW</span></button>
                <!-- Add this to the tabs section in HTML template -->
                <button class="tab" onclick="openTab(event, 'voltage-trends')">Voltage Trends</button>
                <!-- Add this to the tabs section in HTML template -->
                <button class="tab" onclick="openTab(event, 'corner-outliers')">Corner Outlier Analysis</button>
                <!-- Add this to the tabs section in HTML template -->
                <button class="tab" onclick="openTab(event, 'cross-corner')">Cross-Corner Analysis</button>
 
                <button class="tab" onclick="openTab(event, 'overview')">Overview</button>
                <button class="tab" onclick="openTab(event, 'late-sigma')">Late Sigma</button>
                <button class="tab" onclick="openTab(event, 'early-sigma')">Early Sigma</button>
                <button class="tab" onclick="openTab(event, 'visualizations')">Visualizations</button>
            </div>
           
            
            <!-- Add this as a new tab content section -->
            <div id="cross-corner" class="tab-content">
                <div class="card-body">
                    <h3>Cross-Corner Consistency Analysis</h3>
                    <p>This analysis compares library and Monte Carlo consistency across different voltage corners.</p>
                   
                    <div class="visualization-grid">
                        {% for img_name, img_path in cross_corner_images.items() %}
                        <div class="visualization-card">
                            <img src="images/{{ img_name }}" alt="{{ img_name }}" class="enlarge-image">
                            <div class="visualization-details">
                                <h3>{{ img_name|replace('.png', '')|replace('_', ' ')|title }}</h3>
                                <p>{{ img_name }}</p>
                            </div>
                        </div>
                        {% endfor %}
                    </div>
                   
                    <div class="metric-group">
                        <h4 class="metric-group-title">Key Findings</h4>
                        <ul>
                            <li>Library vs Monte Carlo error ratios indicate systematic characterization issues</li>
                            <li>Correlation matrices show how well corners track each other</li>
                            <li>Scaling analysis reveals voltage-dependent modeling challenges</li>
                            <li>Cells with poor cross-corner consistency need special attention</li>
                        </ul>
                    </div>
                </div>
            </div>
           
            <!-- Add this as a new tab content section -->
            <div id="corner-outliers" class="tab-content">
                <div class="card-body">
                    <h3>Corner-Specific Outlier Analysis</h3>
                    <p>This analysis examines how outlier patterns vary across different voltage corners.</p>
                   
                    <div class="visualization-grid">
                        {% for img_name, img_path in corner_outlier_images.items() %}
                        <div class="visualization-card">
                            <img src="images/{{ img_name }}" alt="{{ img_name }}" class="enlarge-image">
                            <div class="visualization-details">
                                <h3>{{ img_name|replace('.png', '')|replace('_', ' ')|title }}</h3>
                                <p>{{ img_name }}</p>
                            </div>
                        </div>
                        {% endfor %}
                    </div>
                   
                    <div class="metric-group">
                        <h4 class="metric-group-title">Key Findings</h4>
                        <ul>
                            <li>Cells that show outliers only at specific corners indicate corner-sensitive characterization issues</li>
                            <li>Table position effects that vary by corner suggest voltage-dependent modeling challenges</li>
                            <li>Increasing outlier trends with voltage may indicate model breakdown at extreme conditions</li>
                        </ul>
                    </div>
                </div>
            </div>
 
            <!-- Add this as a new tab content section -->
            <div id="voltage-trends" class="tab-content">
                <div class="card-body">
                    <h3>Voltage Trend Analysis</h3>
                    <p>This analysis shows how correlations and error magnitudes change across different voltage corners.</p>
                   
                    <div class="visualization-grid">
                        {% for img_name, img_path in voltage_images.items() %}
                        <div class="visualization-card">
                            <img src="images/{{ img_name }}" alt="{{ img_name }}" class="enlarge-image">
                            <div class="visualization-details">
                                <h3>{{ img_name|replace('.png', '')|replace('_', ' ')|title }}</h3>
                                <p>{{ img_name }}</p>
                            </div>
                        </div>
                        {% endfor %}
                    </div>
                </div>
            </div>
 
 
            <!-- Correlation tables tab content -->
            <div id="correlation-tables" class="tab-content active">
                <div class="card-body">
                    <h3>Correlation Tables by Moment Type</h3>
                    <p>These tables show the correlation values between sigma values and moments across different corners and types.</p>
                   
                    <!-- Correlation table legend -->
                    <div class="correlation-legend">
                        <div class="legend-item">
                            <div class="legend-color" style="background-color: #4caf50;"></div>
                            Strong Positive (0.75 to 1.0)
                        </div>
                        <div class="legend-item">
                            <div class="legend-color" style="background-color: #8bc34a;"></div>
                            Positive (0.5 to 0.75)
                        </div>
                        <div class="legend-item">
                            <div class="legend-color" style="background-color: #cddc39;"></div>
                            Weak Positive (0.25 to 0.5)
                        </div>
                        <div class="legend-item">
                            <div class="legend-color" style="background-color: #e0e0e0;"></div>
                            Neutral (-0.25 to 0.25)
                        </div>
                        <div class="legend-item">
                            <div class="legend-color" style="background-color: #ffeb3b;"></div>
                            Weak Negative (-0.5 to -0.25)
                        </div>
                        <div class="legend-item">
                            <div class="legend-color" style="background-color: #ff9800;"></div>
                            Negative (-0.75 to -0.5)
                        </div>
                        <div class="legend-item">
                            <div class="legend-color" style="background-color: #f44336;"></div>
                            Strong Negative (-1.0 to -0.75)
                        </div>
                    </div>
                   
                    <div class="nav-tabs">
                        <span class="tab active" onclick="switchCorrTab(event, 'std-corr')">STD Correlations</span>
                        <span class="tab" onclick="switchCorrTab(event, 'skew-corr')">SKEW Correlations</span>
                        <span class="tab" onclick="switchCorrTab(event, 'meanshift-corr')">MEANSHIFT Correlations</span>
                    </div>
                   
                    <div id="std-corr" class="corr-tab-content">
                        <h4 class="metric-group-title">Late Sigma vs STD Correlations</h4>
                        {{ late_sigma_std_table|safe }}
                       
                        <h4 class="metric-group-title">Early Sigma vs STD Correlations</h4>
                        {{ early_sigma_std_table|safe }}
                    </div>
                   
                    <div id="skew-corr" class="corr-tab-content" style="display: none;">
                        <h4 class="metric-group-title">Late Sigma vs SKEW Correlations</h4>
                        {{ late_sigma_skew_table|safe }}
                       
                        <h4 class="metric-group-title">Early Sigma vs SKEW Correlations</h4>
                        {{ early_sigma_skew_table|safe }}
                    </div>
                   
                    <div id="meanshift-corr" class="corr-tab-content" style="display: none;">
                        <h4 class="metric-group-title">Late Sigma vs MEANSHIFT Correlations</h4>
                        {{ late_sigma_meanshift_table|safe }}
                       
                        <h4 class="metric-group-title">Early Sigma vs MEANSHIFT Correlations</h4>
                        {{ early_sigma_meanshift_table|safe }}
                    </div>
                   
                    <p>These tables provide a comprehensive view of the correlation patterns across all corners and types. The key observations are:</p>
                    <ul>
                        <li>Strong correlations are observed in the MC and Lib categories for all moment types.</li>
                        <li>Error categories (abs_err, rel_err) generally show weaker correlations, indicating that the errors do not follow the same pattern as the sigma values.</li>
                        <li>Some corners show stronger correlations in error categories than others, which may indicate issues in those corner conditions.</li>
                    </ul>
                </div>
            </div>
           
            <!-- Outlier Analysis tab content -->
            <div id="outlier-analysis" class="tab-content">
                <div class="card-body">
                    <h3>Outlier Analysis</h3>
                    <p>This analysis examines outliers in the correlation data to identify potential patterns and issues.</p>
                   
                    <div class="metric-group">
                        <h4 class="metric-group-title">Outliers by Cell Type</h4>
                        <p>The following cell types have the highest number of correlation outliers:</p>
                        <table>
                            <thead>
                                <tr>
                                    <th>Cell Type</th>
                                    <th>Outlier Count</th>
                                    <th>Percentage</th>
                                </tr>
                            </thead>
                            <tbody>
                                {% for cell, count in top_cell_outliers %}
                                <tr>
                                    <td>{{ cell }}</td>
                                    <td>{{ count }}</td>
                                    <td>{{ ((count / total_outliers) * 100)|round(2) }}%</td>
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                   
                    <div class="metric-group">
                        <h4 class="metric-group-title">Outliers by Table Position</h4>
                        <p>The following table positions have the highest number of correlation outliers:</p>
                        <table>
                            <thead>
                                <tr>
                                    <th>Table Position</th>
                                    <th>Outlier Count</th>
                                    <th>Percentage</th>
                                </tr>
                            </thead>
                            <tbody>
                                {% for pos, count in top_table_position_outliers %}
                                <tr>
                                    <td>{{ pos }}</td>
                                    <td>{{ count }}</td>
                                    <td>{{ ((count / total_outliers) * 100)|round(2) }}%</td>
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                   
                    <div class="metric-group">
                        <h4 class="metric-group-title">Outlier Visualizations</h4>
                        <div class="visualization-grid">
                            {% for img_name, img_path in outlier_images.items() %}
                            <div class="visualization-card error-card">
                                <img src="images/{{ img_name }}" alt="{{ img_name }}" class="enlarge-image">
                                <div class="visualization-details">
                                    <h3 class="error-title">{{ img_name|replace('.png', '')|replace('_', ' ')|replace('outlier', '')|title }}</h3>
                                    <p>{{ img_name }}</p>
                                </div>
                            </div>
                            {% endfor %}
                        </div>
                    </div>
                   
                    <div class="metric-group">
                        <h4 class="metric-group-title">Outlier Patterns</h4>
                        <p>Key observations from the outlier analysis:</p>
                        <ul>
                            <li>Certain cell types ({{ top_cell_names|join(', ') }}) show a higher tendency to produce outliers.</li>
                            <li>Table positions at the edges of the table (e.g., {{ top_table_positions|join(', ') }}) are more likely to have outliers.</li>
                            <li>Outliers are more common in the {{ top_outlier_category }} error category, suggesting that this error type shows more variability.</li>
                        </ul>
                        <p>Further investigation of these outlier patterns can help identify improvements in the characterization process.</p>
                    </div>
                </div>
            </div>
           
            <!-- Original overview tab content -->
            <div id="overview" class="tab-content">
                <div class="card-body">
                    <h3>Analysis Overview</h3>
                    <p>This analysis examines correlations between sigma values (late_sigma and early_sigma) and moment types (standard deviation, skewness, meanshift) across different categories (MC, Lib, abs_err, rel_err).</p>
                   
                    <div class="metric-group">
                        <h4 class="metric-group-title">Analysis Scope</h4>
                        <p>
                            <strong>Number of Corners:</strong> {{ corners|length }}<br>
                            <strong>Number of Types:</strong> {{ types|length }}<br>
                            <strong>Categories:</strong> MC, Lib, abs_err, rel_err<br>
                            <strong>Moment Types:</strong> Standard Deviation (STD), Skewness (SKEW), Meanshift (MEANSHIFT)
                        </p>
                    </div>
                   
                    <div class="metric-group">
                        <h4 class="metric-group-title">Key Findings</h4>
                        <p>This analysis reveals the relationships between timing sigma values and different statistical moments, which can help identify patterns in timing behavior.</p>
                       
                        <div class="nav-tabs">
                            <span class="tab active" onclick="switchOverviewTab(event, 'late-findings')">Late Sigma Findings</span>
                            <span class="tab" onclick="switchOverviewTab(event, 'early-findings')">Early Sigma Findings</span>
                        </div>
                       
                        <div id="late-findings" class="overview-tab-content">
                            <table>
                                <thead>
                                    <tr>
                                        <th>Category</th>
                                        <th>Moment Type</th>
                                        <th>Average Correlation</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {% for item in late_sigma_category_moment_avg %}
                                    <tr class="{{ 'highlight-row' if item.category in ['abs_err', 'rel_err'] }}">
                                        <td>{{ item.category }}</td>
                                        <td>{{ item.moment_type }}</td>
                                        <td>{{ item.correlation|round(4) }}</td>
                                    </tr>
                                    {% endfor %}
                                </tbody>
                            </table>
                        </div>
                       
                        <div id="early-findings" class="overview-tab-content" style="display: none;">
                            <table>
                                <thead>
                                    <tr>
                                        <th>Category</th>
                                        <th>Moment Type</th>
                                        <th>Average Correlation</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {% for item in early_sigma_category_moment_avg %}
                                    <tr class="{{ 'highlight-row' if item.category in ['abs_err', 'rel_err'] }}">
                                        <td>{{ item.category }}</td>
                                        <td>{{ item.moment_type }}</td>
                                        <td>{{ item.correlation|round(4) }}</td>
                                    </tr>
                                    {% endfor %}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
           
            <div id="late-sigma" class="tab-content">
                <div class="card-body">
                    <h3>Late Sigma Analysis</h3>
                    <p>This analysis shows correlations between late_sigma and various moments.</p>
                   
                    <div class="metric-group">
                        <h4 class="metric-group-title">Top Correlations</h4>
                        <table>
                            <thead>
                                <tr>
                                    <th>Category</th>
                                    <th>Moment Type</th>
                                    <th>Column</th>
                                    <th>Corner</th>
                                    <th>Type</th>
                                    <th>Correlation</th>
                                </tr>
                            </thead>
                            <tbody>
                                {% for item in late_sigma_summary.top_correlations %}
                                <tr class="{{ 'highlight-row' if item.category|default(item.Category, true) in ['abs_err', 'rel_err'] }}">
                                    <td>{{ item.category|default(item.Category, true) }}</td>
                                    <td>{{ item.moment_type|default(item.Moment_Type, true) }}</td>
                                    <td>{{ item.column|default(item.Column, true) }}</td>
                                    <td>{{ item.corner|default(item.Corner, true) }}</td>
                                    <td>{{ item.type|default(item.Type, true) }}</td>
                                    <td>{{ item.correlation|default(item.Correlation, true)|round(4) }}</td>
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                   
                    <div class="metric-group">
                        <h4 class="metric-group-title">Bottom Correlations</h4>
                        <table>
                            <thead>
                                <tr>
                                    <th>Category</th>
                                    <th>Moment Type</th>
                                    <th>Column</th>
                                    <th>Corner</th>
                                    <th>Type</th>
                                    <th>Correlation</th>
                                </tr>
                            </thead>
                            <tbody>
                                {% for item in late_sigma_summary.bottom_correlations %}
                                <tr class="{{ 'highlight-row' if item.category|default(item.Category, true) in ['abs_err', 'rel_err'] }}">
                                    <td>{{ item.category|default(item.Category, true) }}</td>
                                    <td>{{ item.moment_type|default(item.Moment_Type, true) }}</td>
                                    <td>{{ item.column|default(item.Column, true) }}</td>
                                    <td>{{ item.corner|default(item.Corner, true) }}</td>
                                    <td>{{ item.type|default(item.Type, true) }}</td>
                                    <td>{{ item.correlation|default(item.Correlation, true)|round(4) }}</td>
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                   
                    <div class="metric-group">
                        <h4 class="metric-group-title">Average Correlation by Category</h4>
                        <table>
                            <thead>
                                <tr>
                                    <th>Category</th>
                                    <th>Average Correlation</th>
                                </tr>
                            </thead>
                            <tbody>
                                {% for category, value in late_sigma_summary.avg_by_category.items() %}
                                <tr class="{{ 'highlight-row' if category in ['abs_err', 'rel_err'] }}">
                                    <td>{{ category }}</td>
                                    <td>{{ value|round(4) }}</td>
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                   
                    <div class="metric-group">
                        <h4 class="metric-group-title">Average Correlation by Moment Type</h4>
                        <table>
                            <thead>
                                <tr>
                                    <th>Moment Type</th>
                                    <th>Average Correlation</th>
                                </tr>
                            </thead>
                            <tbody>
                                {% for moment, value in late_sigma_summary.avg_by_moment.items() %}
                                <tr>
                                    <td>{{ moment }}</td>
                                    <td>{{ value|round(4) }}</td>
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
           
            <div id="early-sigma" class="tab-content">
                <div class="card-body">
                    <h3>Early Sigma Analysis</h3>
                    <p>This analysis shows correlations between early_sigma and various moments.</p>
                   
                    <div class="metric-group">
                        <h4 class="metric-group-title">Top Correlations</h4>
                        <table>
                            <thead>
                                <tr>
                                    <th>Category</th>
                                    <th>Moment Type</th>
                                    <th>Column</th>
                                    <th>Corner</th>
                                    <th>Type</th>
                                    <th>Correlation</th>
                                </tr>
                            </thead>
                            <tbody>
                                {% for item in early_sigma_summary.top_correlations %}
                                <tr class="{{ 'highlight-row' if item.category|default(item.Category, true) in ['abs_err', 'rel_err'] }}">
                                    <td>{{ item.category|default(item.Category, true) }}</td>
                                    <td>{{ item.moment_type|default(item.Moment_Type, true) }}</td>
                                    <td>{{ item.column|default(item.Column, true) }}</td>
                                    <td>{{ item.corner|default(item.Corner, true) }}</td>
                                    <td>{{ item.type|default(item.Type, true) }}</td>
                                    <td>{{ item.correlation|default(item.Correlation, true)|round(4) }}</td>
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                   
                    <div class="metric-group">
                        <h4 class="metric-group-title">Bottom Correlations</h4>
                        <table>
                            <thead>
                                <tr>
                                    <th>Category</th>
                                    <th>Moment Type</th>
                                    <th>Column</th>
                                    <th>Corner</th>
                                    <th>Type</th>
                                    <th>Correlation</th>
                                </tr>
                            </thead>
                            <tbody>
                                {% for item in early_sigma_summary.bottom_correlations %}
                                <tr class="{{ 'highlight-row' if item.category|default(item.Category, true) in ['abs_err', 'rel_err'] }}">
                                    <td>{{ item.category|default(item.Category, true) }}</td>
                                    <td>{{ item.moment_type|default(item.Moment_Type, true) }}</td>
                                    <td>{{ item.column|default(item.Column, true) }}</td>
                                    <td>{{ item.corner|default(item.Corner, true) }}</td>
                                    <td>{{ item.type|default(item.Type, true) }}</td>
                                    <td>{{ item.correlation|default(item.Correlation, true)|round(4) }}</td>
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                   
                    <div class="metric-group">
                        <h4 class="metric-group-title">Average Correlation by Category</h4>
                        <table>
                            <thead>
                                <tr>
                                    <th>Category</th>
                                    <th>Average Correlation</th>
                                </tr>
                            </thead>
                            <tbody>
                                {% for category, value in early_sigma_summary.avg_by_category.items() %}
                                <tr class="{{ 'highlight-row' if category in ['abs_err', 'rel_err'] }}">
                                    <td>{{ category }}</td>
                                    <td>{{ value|round(4) }}</td>
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                   
                    <div class="metric-group">
                        <h4 class="metric-group-title">Average Correlation by Moment Type</h4>
                        <table>
                            <thead>
                                <tr>
                                    <th>Moment Type</th>
                                    <th>Average Correlation</th>
                                </tr>
                            </thead>
                            <tbody>
                                {% for moment, value in early_sigma_summary.avg_by_moment.items() %}
                                <tr>
                                    <td>{{ moment }}</td>
                                    <td>{{ value|round(4) }}</td>
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
           
            <div id="visualizations" class="tab-content">
                <div class="card-body">
                    <h3>Visualizations</h3>
                    <p>This section provides visual representations of the analysis results. Click on any image to enlarge it.</p>
                   
                    <div class="nav-tabs">
                        <!-- Reordered tabs to put error metrics first -->
                        <span class="tab active error-tab" onclick="switchVisTab(event, 'error-vis')">Error Metrics <span class="error-badge">PRIORITY</span></span>
                        <span class="tab" onclick="switchVisTab(event, 'heat-vis')">Heatmaps</span>
                        <span class="tab" onclick="switchVisTab(event, 'bar-vis')">Bar Charts</span>
                        <span class="tab" onclick="switchVisTab(event, 'scatter-vis')">Scatter Plots</span>
                    </div>
                   
                    <!-- New Error Metrics visualizations tab -->
                    <div id="error-vis" class="vis-tab-content">
                        <div class="error-category">
                            <h4 class="error-title">Error Metrics Visualizations</h4>
                            <p>These visualizations focus specifically on error metrics (rel_err and abs_err), which are most important for understanding the relationship between sigma values and moments.</p>
                           
                            <div class="visualization-grid">
                                {% for img_name, img_path in error_images.items() %}
                                <div class="visualization-card error-card">
                                    <img src="images/{{ img_name }}" alt="{{ img_name }}" class="enlarge-image">
                                    <div class="visualization-details">
                                        <h3 class="error-title">{{ img_name|replace('.png', '')|replace('_', ' ')|replace('IMPORTANT', '')|title }}</h3>
                                        <p>{{ img_name }}</p>
                                    </div>
                                </div>
                                {% endfor %}
                            </div>
                        </div>
                    </div>
                   
                    <div id="heat-vis" class="vis-tab-content" style="display: none;">
                        <div class="visualization-grid">
                            {% for img_name, img_path in heatmap_images.items() %}
                            <div class="visualization-card">
                                <img src="images/{{ img_name }}" alt="{{ img_name }}" class="enlarge-image">
                                <div class="visualization-details">
                                    <h3>{{ img_name|replace('.png', '')|replace('_', ' ')|title }}</h3>
                                    <p>{{ img_name }}</p>
                                </div>
                            </div>
                            {% endfor %}
                        </div>
                    </div>
                   
                    <div id="bar-vis" class="vis-tab-content" style="display: none;">
                        <div class="visualization-grid">
                            {% for img_name, img_path in bar_images.items() %}
                            <div class="visualization-card">
                                <img src="images/{{ img_name }}" alt="{{ img_name }}" class="enlarge-image">
                                <div class="visualization-details">
                                    <h3>{{ img_name|replace('.png', '')|replace('_', ' ')|title }}</h3>
                                    <p>{{ img_name }}</p>
                                </div>
                            </div>
                            {% endfor %}
                        </div>
                    </div>
                   
                    <div id="scatter-vis" class="vis-tab-content" style="display: none;">
                        <div class="visualization-grid">
                            {% for img_name, img_path in scatter_images.items() %}
                            <div class="visualization-card">
                                <img src="images/{{ img_name }}" alt="{{ img_name }}" class="enlarge-image">
                                <div class="visualization-details">
                                    <h3>{{ img_name|replace('.png', '')|replace('_', ' ')|title }}</h3>
                                    <p>{{ img_name }}</p>
                                </div>
                            </div>
                            {% endfor %}
                           
                        </div>
                        <p>Additional scatter plots PDFs are available in the result directories for each corner and type combination.</p>
                    </div>
                </div>
            </div>
        </div>
       
        <div class="card">
            <div class="card-header">
                Explanation of Metrics
            </div>
            <div class="card-body">
                <div class="metric-group error-category">
                    <div class="metric-group-title error-title">Error Metrics (Priority)</div>
                    <p><strong>Relative Error (rel_err):</strong> The relative difference between Monte Carlo and library results, showing percentage-based discrepancies.</p>
                    <p><strong>Absolute Error (abs_err):</strong> The absolute difference between Monte Carlo and library results, showing raw magnitude discrepancies.</p>
                </div>
               
                <div class="metric-group">
                    <div class="metric-group-title">Key Terms</div>
                    <p><strong>Late Sigma:</strong> A measure of the variation in the upper/late timing distribution.</p>
                    <p><strong>Early Sigma:</strong> A measure of the variation in the lower/early timing distribution.</p>
                    <p><strong>Standard Deviation (STD):</strong> A measure of the amount of variation or dispersion in timing values.</p>
                    <p><strong>Skewness:</strong> A measure of the asymmetry of the probability distribution of timing values.</p>
                    <p><strong>Meanshift:</strong> The shift in the mean value of the timing distribution.</p>
                    <p><strong>Correlation:</strong> A statistical measure that indicates the extent to which two variables fluctuate together. Values range from -1 (perfect negative correlation) to +1 (perfect positive correlation).</p>
                </div>
               
                <div class="metric-group">
                    <div class="metric-group-title">Data Categories</div>
                    <p class="error-category"><strong>rel_err:</strong> Relative error between MC and Lib results. <span class="error-badge">PRIORITY</span></p>
                    <p class="error-category"><strong>abs_err:</strong> Absolute error between MC and Lib results. <span class="error-badge">PRIORITY</span></p>
                    <p><strong>MC:</strong> Monte Carlo simulation results.</p>
                    <p><strong>Lib:</strong> Library characterization results.</p>
                </div>
               
                <div class="metric-group">
                    <div class="metric-group-title">New Analysis</div>
                    <p><strong>Correlation Tables:</strong> Comprehensive tables showing correlation values across all corners, types, and categories.</p>
                    <p><strong>Outlier Analysis:</strong> In-depth examination of points that do not follow the general correlation trend.</p>
                    <p><strong>Cell Analysis:</strong> Breakdown of correlation patterns by cell type to identify problematic cells.</p>
                    <p><strong>Table Position Analysis:</strong> Analysis of how table positions affect the correlation strength and error patterns.</p>
                </div>
            </div>
        </div>
    </div>
   
    <footer>
        <div class="container">
            <p>Generated by the Timing Analysis Tool</p>
            <p>For detailed analysis, examine the individual visualization files in the output directory.</p>
        </div>
    </footer>
   
    <!-- The Modal -->
    <div id="imageModal" class="modal">
        <span class="close">&times;</span>
        <img class="modal-content" id="modalImage">
        <div id="modalCaption" class="modal-caption"></div>
    </div>
   
    <script>
        function openTab(evt, tabName) {
            var i, tabcontent, tablinks;
           
            // Hide all tab content
            tabcontent = document.getElementsByClassName("tab-content");
            for (i = 0; i < tabcontent.length; i++) {
                tabcontent[i].className = tabcontent[i].className.replace(" active", "");
            }
           
            // Remove "active" class from all tabs
            tablinks = document.getElementsByClassName("tab");
            for (i = 0; i < tablinks.length; i++) {
                tablinks[i].className = tablinks[i].className.replace(" active", "");
            }
           
            // Show the current tab and add an "active" class to the button that opened the tab
            document.getElementById(tabName).className += " active";
            evt.currentTarget.className += " active";
        }
       
        function switchSigmaTab(evt, tabName) {
            var i, tabcontent, tablinks;
           
            // Hide all sigma tab content
            tabcontent = document.getElementsByClassName("sigma-tab-content");
            for (i = 0; i < tabcontent.length; i++) {
                tabcontent[i].style.display = "none";
            }
           
            // Remove "active" class from all sigma tabs
            tablinks = evt.currentTarget.parentElement.getElementsByClassName("tab");
            for (i = 0; i < tablinks.length; i++) {
                tablinks[i].className = tablinks[i].className.replace(" active", "");
            }
           
            // Show the current tab and add an "active" class to the button that opened the tab
            document.getElementById(tabName).style.display = "block";
            evt.currentTarget.className += " active";
        }
       
        function switchOverviewTab(evt, tabName) {
            var i, tabcontent, tablinks;
           
            // Hide all overview tab content
            tabcontent = document.getElementsByClassName("overview-tab-content");
            for (i = 0; i < tabcontent.length; i++) {
                tabcontent[i].style.display = "none";
            }
           
            // Remove "active" class from all overview tabs
            tablinks = evt.currentTarget.parentElement.getElementsByClassName("tab");
            for (i = 0; i < tablinks.length; i++) {
                tablinks[i].className = tablinks[i].className.replace(" active", "");
            }
           
            // Show the current tab and add an "active" class to the button that opened the tab
            document.getElementById(tabName).style.display = "block";
            evt.currentTarget.className += " active";
        }
       
        function switchVisTab(evt, tabName) {
            var i, tabcontent, tablinks;
           
            // Hide all visualization tab content
            tabcontent = document.getElementsByClassName("vis-tab-content");
            for (i = 0; i < tabcontent.length; i++) {
                tabcontent[i].style.display = "none";
            }
           
            // Remove "active" class from all visualization tabs
            tablinks = evt.currentTarget.parentElement.getElementsByClassName("tab");
            for (i = 0; i < tablinks.length; i++) {
                tablinks[i].className = tablinks[i].className.replace(" active", "");
            }
           
            // Show the current tab and add an "active" class to the button that opened the tab
            document.getElementById(tabName).style.display = "block";
            evt.currentTarget.className += " active";
        }
       
        function switchCorrTab(evt, tabName) {
            var i, tabcontent, tablinks;
           
            // Hide all correlation tab content
            tabcontent = document.getElementsByClassName("corr-tab-content");
            for (i = 0; i < tabcontent.length; i++) {
                tabcontent[i].style.display = "none";
            }
           
            // Remove "active" class from all correlation tabs
            tablinks = evt.currentTarget.parentElement.getElementsByClassName("tab");
            for (i = 0; i < tablinks.length; i++) {
                tablinks[i].className = tablinks[i].className.replace(" active", "");
            }
           
            // Show the current tab and add an "active" class to the button that opened the tab
            document.getElementById(tabName).style.display = "block";
            evt.currentTarget.className += " active";
        }
       
        // Get the modal
        var modal = document.getElementById("imageModal");
       
        // Get the image and insert it inside the modal
        var modalImg = document.getElementById("modalImage");
        var captionText = document.getElementById("modalCaption");
       
        // Get all images with the enlarge-image class
        var images = document.getElementsByClassName("enlarge-image");
       
        // Add click event to each image
        for (var i = 0; i < images.length; i++) {
            images[i].onclick = function() {
                modal.style.display = "block";
                modalImg.src = this.src;
                captionText.innerHTML = this.alt;
            }
        }
       
        // Get the <span> element that closes the modal
        var span = document.getElementsByClassName("close")[0];
       
        // When the user clicks on <span> (x), close the modal
        span.onclick = function() {
            modal.style.display = "none";
        }
       
        // When the user clicks anywhere outside of the modal, close it
        window.onclick = function(event) {
            if (event.target == modal) {
                modal.style.display = "none";
            }
        }
    </script>
</body>
</html>
"""
def generate_html_report(results, summary, output_dir):
    """Generate the HTML report from the template."""
    debug_mode = True  # Set to True to enable additional debugging
 
    try:
        template = Template(create_html_template())
 
        # Print debug info
        if debug_mode:
            logging.debug("=== Results Data Structure ===")
            for key in results.keys():
                if isinstance(results[key], pd.DataFrame):
                    logging.debug(f"{key}: DataFrame with shape {results[key].shape}")
                    logging.debug(f"{key} columns: {results[key].columns.tolist()}")
                elif isinstance(results[key], list):
                    logging.debug(f"{key}: List with {len(results[key])} items")
                elif isinstance(results[key], dict):
                    logging.debug(f"{key}: Dict with {len(results[key])} keys")
                else:
                    logging.debug(f"{key}: {type(results[key])}")
 
        # Calculate statistics for late_sigma
        late_sigma_count = len(results['late_sigma_correlations']) if 'late_sigma_correlations' in results and not results['late_sigma_correlations'].empty else 0
        late_sigma_avg = results['late_sigma_correlations']['correlation'].mean() if 'late_sigma_correlations' in results and not results['late_sigma_correlations'].empty and 'correlation' in results['late_sigma_correlations'].columns else 0
        late_sigma_max = results['late_sigma_correlations']['correlation'].max() if 'late_sigma_correlations' in results and not results['late_sigma_correlations'].empty and 'correlation' in results['late_sigma_correlations'].columns else 0
        late_sigma_min = results['late_sigma_correlations']['correlation'].min() if 'late_sigma_correlations' in results and not results['late_sigma_correlations'].empty and 'correlation' in results['late_sigma_correlations'].columns else 0
 
        # Alternative cases for column names
        if 'late_sigma_correlations' in results and not results['late_sigma_correlations'].empty:
            corr_col = get_column_case_insensitive(results['late_sigma_correlations'], 'correlation')
            if corr_col and corr_col != 'correlation':
                late_sigma_avg = results['late_sigma_correlations'][corr_col].mean()
                late_sigma_max = results['late_sigma_correlations'][corr_col].max()
                late_sigma_min = results['late_sigma_correlations'][corr_col].min()
 
        # Calculate statistics for early_sigma
        early_sigma_count = len(results['early_sigma_correlations']) if 'early_sigma_correlations' in results and not results['early_sigma_correlations'].empty else 0
        early_sigma_avg = results['early_sigma_correlations']['correlation'].mean() if 'early_sigma_correlations' in results and not results['early_sigma_correlations'].empty and 'correlation' in results['early_sigma_correlations'].columns else 0
        early_sigma_max = results['early_sigma_correlations']['correlation'].max() if 'early_sigma_correlations' in results and not results['early_sigma_correlations'].empty and 'correlation' in results['early_sigma_correlations'].columns else 0
        early_sigma_min = results['early_sigma_correlations']['correlation'].min() if 'early_sigma_correlations' in results and not results['early_sigma_correlations'].empty and 'correlation' in results['early_sigma_correlations'].columns else 0
 
        # Alternative cases for column names
        if 'early_sigma_correlations' in results and not results['early_sigma_correlations'].empty:
            corr_col = get_column_case_insensitive(results['early_sigma_correlations'], 'correlation')
            if corr_col and corr_col != 'correlation':
                early_sigma_avg = results['early_sigma_correlations'][corr_col].mean()
                early_sigma_max = results['early_sigma_correlations'][corr_col].max()
                early_sigma_min = results['early_sigma_correlations'][corr_col].min()
 
        # Format correlation tables
        categories = ['MC', 'Lib', 'abs_err', 'rel_err']
 
        late_sigma_std_table = format_correlation_table(
            results['correlation_tables'].get('late_sigma_STD', pd.DataFrame()),
            categories
        )
 
        early_sigma_std_table = format_correlation_table(
            results['correlation_tables'].get('early_sigma_STD', pd.DataFrame()),
            categories
        )
 
        late_sigma_skew_table = format_correlation_table(
            results['correlation_tables'].get('late_sigma_SKEW', pd.DataFrame()),
            categories
        )
 
        early_sigma_skew_table = format_correlation_table(
            results['correlation_tables'].get('early_sigma_SKEW', pd.DataFrame()),
            categories
        )
 
        late_sigma_meanshift_table = format_correlation_table(
            results['correlation_tables'].get('late_sigma_MEANSHIFT', pd.DataFrame()),
            categories
        )
 
        early_sigma_meanshift_table = format_correlation_table(
            results['correlation_tables'].get('early_sigma_MEANSHIFT', pd.DataFrame()),
            categories
        )
 
        # Prepare rel_err and abs_err correlations
        rel_err_correlations = []
        abs_err_correlations = []
 
        # Process late_sigma correlations for rel_err and abs_err
        if 'late_sigma_correlations' in results and not results['late_sigma_correlations'].empty:
            # Get the actual column names (case-insensitive)
            df = results['late_sigma_correlations']
            cat_col = get_column_case_insensitive(df, 'category')
 
            if cat_col:
                # Filter for rel_err
                rel_err_data = df[df[cat_col].str.lower() == 'rel_err'].copy() if not df.empty else pd.DataFrame()
                if not rel_err_data.empty:
                    rel_err_correlations.extend(rel_err_data.to_dict('records'))
 
                # Filter for abs_err
                abs_err_data = df[df[cat_col].str.lower() == 'abs_err'].copy() if not df.empty else pd.DataFrame()
                if not abs_err_data.empty:
                    abs_err_correlations.extend(abs_err_data.to_dict('records'))
            else:
                logging.warning("No category column found in late_sigma_correlations")
 
        # Process early sigma correlations for rel_err and abs_err
        if 'early_sigma_correlations' in results and not results['early_sigma_correlations'].empty:
            # Get the actual column names (case-insensitive)
            df = results['early_sigma_correlations']
            cat_col = get_column_case_insensitive(df, 'category')
 
            if cat_col:
                # Filter for rel_err
                rel_err_data = df[df[cat_col].str.lower() == 'rel_err'].copy() if not df.empty else pd.DataFrame()
                if not rel_err_data.empty:
                    rel_err_correlations.extend(rel_err_data.to_dict('records'))
 
                # Filter for abs_err
                abs_err_data = df[df[cat_col].str.lower() == 'abs_err'].copy() if not df.empty else pd.DataFrame()
                if not abs_err_data.empty:
                    abs_err_correlations.extend(abs_err_data.to_dict('records'))
            else:
                logging.warning("No category column found in early_sigma_correlations")
 
        rel_err_count = len(rel_err_correlations)
        abs_err_count = len(abs_err_correlations)
 
        # Calculate maximum correlation for error metrics
        all_error_correlations = rel_err_correlations + abs_err_correlations
        if all_error_correlations:
            # Determine which correlation field to use
            if 'correlation' in all_error_correlations[0]:
                corr_field = 'correlation'
            elif 'Correlation' in all_error_correlations[0]:
                corr_field = 'Correlation'
            else:
                # Try to find any field that might contain correlation values
                potential_fields = [f for f in all_error_correlations[0].keys() if 'corr' in f.lower()]
                corr_field = potential_fields[0] if potential_fields else None
 
            if corr_field:
                error_max_corr = max([abs(c.get(corr_field, 0)) for c in all_error_correlations])
            else:
                error_max_corr = 0
                logging.warning("Could not determine correlation field in error correlations")
        else:
            error_max_corr = 0
 
        # Process outlier data
        top_cell_outliers = []
        top_table_position_outliers = []
        total_outliers = 0
        top_cell_names = []
        top_table_positions = []
        top_outlier_category = ""
 
        if 'outliers' in summary:
            # Get cell outliers
            if 'cell_counts' in summary['outliers']:
                cell_counts = summary['outliers']['cell_counts']
                top_cell_outliers = list(cell_counts.items())[:10]  # Top 10 cells
                top_cell_names = [cell for cell, _ in top_cell_outliers[:3]]  # Top 3 cell names
                total_outliers = sum(cell_counts.values())
 
            # Get table position outliers
            if 'table_position_counts' in summary['outliers']:
                table_pos_counts = summary['outliers']['table_position_counts']
                top_table_position_outliers = list(table_pos_counts.items())[:10]  # Top 10 positions
                top_table_positions = [pos for pos, _ in top_table_position_outliers[:3]]  # Top 3 positions
 
            # Determine which category has more outliers
            abs_err_outlier_count = 0
            rel_err_outlier_count = 0
 
            # Count outliers by category
            for file_name, file_outliers in results['outliers'].items():
                # Process late sigma outliers
                if 'late_sigma' in file_outliers:
                    if 'abs_err' in file_outliers['late_sigma']:
                        for column, outliers in file_outliers['late_sigma']['abs_err'].items():
                            abs_err_outlier_count += len(outliers)
 
                    if 'rel_err' in file_outliers['late_sigma']:
                        for column, outliers in file_outliers['late_sigma']['rel_err'].items():
                            rel_err_outlier_count += len(outliers)
 
                # Process early sigma outliers
                if 'early_sigma' in file_outliers:
                    if 'abs_err' in file_outliers['early_sigma']:
                        for column, outliers in file_outliers['early_sigma']['abs_err'].items():
                            abs_err_outlier_count += len(outliers)
 
                    if 'rel_err' in file_outliers['early_sigma']:
                        for column, outliers in file_outliers['early_sigma']['rel_err'].items():
                            rel_err_outlier_count += len(outliers)
 
            # Determine which category has more outliers
            top_outlier_category = "abs_err" if abs_err_outlier_count > rel_err_outlier_count else "rel_err"
 
        # Group images by category
        rel_err_images = {}
        abs_err_images = {}
        error_images = {}
        outlier_images = {}
        heatmap_images = {}
        bar_images = {}
        scatter_images = {}
        voltage_images = {}  # Initialize empty by default
        corner_outlier_images = {}  # Initialize empty by default
        cross_corner_images = {}  # Initialize empty by default
        sensitivity_images = {}  # NEW: Initialize voltage sensitivity images
 
        for img_name, img_path in results['images'].items():
            # Prioritize images with IMPORTANT prefix
            if 'IMPORTANT' in img_name:
                if 'rel_err' in img_name.lower() or 'rel_err' in img_path.lower():
                    rel_err_images[img_name] = img_path
                    error_images[img_name] = img_path
                elif 'abs_err' in img_name.lower() or 'abs_err' in img_path.lower():
                    abs_err_images[img_name] = img_path
                    error_images[img_name] = img_path
            # Categorize outlier images
            elif 'outlier' in img_name.lower():
                outlier_images[img_name] = img_path
            # Regular classification
            elif 'rel_err' in img_name.lower() or 'rel_err' in img_path.lower():
                rel_err_images[img_name] = img_path
                error_images[img_name] = img_path
            elif 'abs_err' in img_name.lower() or 'abs_err' in img_path.lower():
                abs_err_images[img_name] = img_path
                error_images[img_name] = img_path
            elif 'heatmap' in img_name.lower():
                heatmap_images[img_name] = img_path
            elif any(x in img_name.lower() for x in ['bar', 'correlation']):
                bar_images[img_name] = img_path
            elif 'scatter' in img_name.lower():
                scatter_images[img_name] = img_path
 
        # Get voltage images if they exist in results
        if 'voltage_images' in results:
            voltage_images = results['voltage_images']
 
        # Get corner outlier images if they exist in results
        if 'corner_outlier_images' in results:
            corner_outlier_images = results['corner_outlier_images']
 
        # Get cross-corner images if they exist in results
        if 'cross_corner_images' in results:
            cross_corner_images = results['cross_corner_images']
 
        # Get voltage sensitivity images if they exist in results
        if 'sensitivity_images' in results:
            sensitivity_images = results['sensitivity_images']
 
        # Process voltage sensitivity report
        sensitivity_summary = {}
        sensitivity_recommendations = []
        if 'sensitivity_report' in results and results['sensitivity_report']:
            report_data = results['sensitivity_report']
            sensitivity_summary = report_data.get('summary', {})
            sensitivity_recommendations = report_data.get('recommendations', [])
 
        # Generate category-moment averages for overview tab
        late_sigma_category_moment_avg = []
        early_sigma_category_moment_avg = []
 
        # Process late sigma correlations
        if not results['late_sigma_correlations'].empty:
            df = results['late_sigma_correlations']
            cat_col = get_column_case_insensitive(df, 'category')
            moment_col = get_column_case_insensitive(df, 'moment_type')
            corr_col = get_column_case_insensitive(df, 'correlation')
 
            if cat_col and moment_col and corr_col:
                # Group by category and moment type
                grouped = df.groupby([cat_col, moment_col])[corr_col].mean().reset_index()
                late_sigma_category_moment_avg = grouped.to_dict('records')
 
        # Process early sigma correlations
        if not results['early_sigma_correlations'].empty:
            df = results['early_sigma_correlations']
            cat_col = get_column_case_insensitive(df, 'category')
            moment_col = get_column_case_insensitive(df, 'moment_type')
            corr_col = get_column_case_insensitive(df, 'correlation')
 
            if cat_col and moment_col and corr_col:
                # Group by category and moment type
                grouped = df.groupby([cat_col, moment_col])[corr_col].mean().reset_index()
                early_sigma_category_moment_avg = grouped.to_dict('records')
 
        # Prepare template variables
        template_vars = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'corners': results['corners'],
            'types': results['types'],
            'late_sigma_count': late_sigma_count,
            'late_sigma_avg': late_sigma_avg,
            'late_sigma_max': late_sigma_max,
            'late_sigma_min': late_sigma_min,
            'early_sigma_count': early_sigma_count,
            'early_sigma_avg': early_sigma_avg,
            'early_sigma_max': early_sigma_max,
            'early_sigma_min': early_sigma_min,
            'rel_err_count': rel_err_count,
            'abs_err_count': abs_err_count,
            'error_max_corr': error_max_corr,
            'late_sigma_summary': summary['late_sigma'],
            'early_sigma_summary': summary['early_sigma'],
            'late_sigma_category_moment_avg': late_sigma_category_moment_avg,
            'early_sigma_category_moment_avg': early_sigma_category_moment_avg,
            'rel_err_images': {os.path.basename(path): path for name, path in rel_err_images.items()},
            'abs_err_images': {os.path.basename(path): path for name, path in abs_err_images.items()},
            'error_images': {os.path.basename(path): path for name, path in error_images.items()},
            'outlier_images': {os.path.basename(path): path for name, path in outlier_images.items()},
            'heatmap_images': {os.path.basename(path): path for name, path in heatmap_images.items()},
            'bar_images': {os.path.basename(path): path for name, path in bar_images.items()},
            'scatter_images': {os.path.basename(path): path for name, path in scatter_images.items()},
            'voltage_images': {os.path.basename(path): path for name, path in voltage_images.items()},
            'corner_outlier_images': {os.path.basename(path): path for name, path in corner_outlier_images.items()},
            'cross_corner_images': {os.path.basename(path): path for name, path in cross_corner_images.items()},
            'sensitivity_images': {os.path.basename(path): path for name, path in sensitivity_images.items()},
            'late_sigma_std_table': late_sigma_std_table,
            'early_sigma_std_table': early_sigma_std_table,
            'late_sigma_skew_table': late_sigma_skew_table,
            'early_sigma_skew_table': early_sigma_skew_table,
            'late_sigma_meanshift_table': late_sigma_meanshift_table,
            'early_sigma_meanshift_table': early_sigma_meanshift_table,
            'top_cell_outliers': top_cell_outliers,
            'top_table_position_outliers': top_table_position_outliers,
            'total_outliers': total_outliers if total_outliers > 0 else 1,  # Avoid division by zero
            'top_cell_names': top_cell_names,
            'top_table_positions': top_table_positions,
            'top_outlier_category': top_outlier_category,
            'sensitivity_summary': sensitivity_summary,
            'sensitivity_recommendations': sensitivity_recommendations
        }
 
        # Render template
        html_content = template.render(**template_vars)
 
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
 
        # Create images directory
        img_dir = os.path.join(output_dir, 'images')
        os.makedirs(img_dir, exist_ok=True)
 
        # Copy all images
        all_images = list(results['images'].items())
 
        # Add voltage trend images if they exist
        if 'voltage_images' in results:
            all_images.extend(list(results['voltage_images'].items()))
 
        # Add corner outlier images if they exist
        if 'corner_outlier_images' in results:
            all_images.extend(list(results['corner_outlier_images'].items()))
 
        # Add cross-corner images if they exist
        if 'cross_corner_images' in results:
            all_images.extend(list(results['cross_corner_images'].items()))
 
        # Add voltage sensitivity images if they exist
        if 'sensitivity_images' in results:
            all_images.extend(list(results['sensitivity_images'].items()))
 
        # Copy all images
        for img_name, img_path in all_images:
            dest_path = os.path.join(img_dir, os.path.basename(img_path))
            if os.path.exists(img_path):  # Check if source exists
                shutil.copy(img_path, dest_path)
            else:
                logging.warning(f"Image file not found: {img_path}")
 
        # Write HTML file
        with open(os.path.join(output_dir, 'index.html'), 'w') as f:
            f.write(html_content)
 
        logging.info(f"Generated HTML report at {os.path.join(output_dir, 'index.html')}")
 
    except Exception as e:
        logging.error(f"Error generating HTML report: {e}")
        logging.error(traceback.format_exc())
        raise
 
 
 
def load_voltage_trend_images(voltage_trends_dir):
    """Load voltage trend visualization images."""
    voltage_images = {}
 
    if os.path.exists(voltage_trends_dir):
        image_files = glob.glob(os.path.join(voltage_trends_dir, "*.png"))
 
        for img_file in image_files:
            img_name = os.path.basename(img_file)
            voltage_images[img_name] = img_file
 
    return voltage_images
 
def load_voltage_trend_summary(voltage_trends_dir):
    """Load voltage trend summary data."""
    summary_path = os.path.join(voltage_trends_dir, "voltage_trend_summary.csv")
 
    if os.path.exists(summary_path):
        return pd.read_csv(summary_path)
 
    return None
 
def load_corner_outlier_images(corner_outlier_dir):
    """Load corner outlier analysis images."""
    corner_outlier_images = {}
 
    if os.path.exists(corner_outlier_dir):
        image_files = glob.glob(os.path.join(corner_outlier_dir, "*.png"))
 
        for img_file in image_files:
            img_name = os.path.basename(img_file)
            corner_outlier_images[img_name] = img_file
 
    return corner_outlier_images
 
def load_corner_outlier_summary(corner_outlier_dir):
    """Load corner outlier summary data."""
    summary_path = os.path.join(corner_outlier_dir, "corner_outlier_summary.csv")
 
    if os.path.exists(summary_path):
        return pd.read_csv(summary_path)
 
    return None
 
def load_cross_corner_images(cross_corner_dir):
    """Load cross-corner analysis images."""
    cross_corner_images = {}
 
    if os.path.exists(cross_corner_dir):
        image_files = glob.glob(os.path.join(cross_corner_dir, "*.png"))
 
        for img_file in image_files:
            img_name = os.path.basename(img_file)
            cross_corner_images[img_name] = img_file
 
    return cross_corner_images
 
def load_cross_corner_summary(cross_corner_dir):
    """Load cross-corner summary data."""
    summary_path = os.path.join(cross_corner_dir, "cross_corner_summary.csv")
 
    if os.path.exists(summary_path):
        return pd.read_csv(summary_path)
 
    return None
 
# Add this function to generate_report.py
def load_voltage_sensitivity_data(sensitivity_dir):
    """Load voltage sensitivity analysis data."""
    sensitivity_images = {}
    sensitivity_report = None
 
    if os.path.exists(sensitivity_dir):
        # Load images
        image_files = glob.glob(os.path.join(sensitivity_dir, "*.png"))
        for img_file in image_files:
            img_name = os.path.basename(img_file)
            sensitivity_images[img_name] = img_file
 
        # Load report
        report_path = os.path.join(sensitivity_dir, "voltage_sensitivity_report.json")
        if os.path.exists(report_path):
            with open(report_path, 'r') as f:
                sensitivity_report = json.load(f)
 
    return sensitivity_images, sensitivity_report
 
def main():
    try:
        parser = argparse.ArgumentParser(description='Generate HTML report for timing analysis')
        parser.add_argument('--data_dir', type=str, required=True, help='Directory with analysis data')
        parser.add_argument('--output_dir', type=str, required=True, help='Output directory for HTML report')
        parser.add_argument('--voltage_sensitivity_dir', type=str, help='Directory with voltage sensitivity analysis')  # NEW
        parser.add_argument('--cross_corner_dir', type=str, help='Directory with cross-corner analysis')
        parser.add_argument('--voltage_trends_dir', type=str, help='Directory with voltage trend analysis')
        parser.add_argument('--corner_outlier_dir', type=str, help='Directory with corner outlier analysis')
        parser.add_argument('--debug', action='store_true', help='Enable additional debug output')
 
        args = parser.parse_args()
        setup_logging(args.output_dir)
 
        logging.info("Starting report generation")
 
        # Collect results
        results = collect_results(args.data_dir)
 
        # Generate summary data
        summary = generate_summary_data(results)
 
        # Load voltage sensitivity analysis data if available
        sensitivity_images = {}
        sensitivity_report = None
        if args.voltage_sensitivity_dir:
            sensitivity_images, sensitivity_report = load_voltage_sensitivity_data(args.voltage_sensitivity_dir)
 
        # Load cross-corner analysis data if available
        cross_corner_images = {}
        cross_corner_summary = None
        if args.cross_corner_dir:
            cross_corner_images = load_cross_corner_images(args.cross_corner_dir)
            cross_corner_summary = load_cross_corner_summary(args.cross_corner_dir)
 
        # Load voltage trend data if available
        voltage_images = {}
        voltage_summary = None
        if args.voltage_trends_dir:
            voltage_images = load_voltage_trend_images(args.voltage_trends_dir)
            voltage_summary = load_voltage_trend_summary(args.voltage_trends_dir)
 
        # Load corner outlier data if available
        corner_outlier_images = {}
        corner_outlier_summary = None
        if args.corner_outlier_dir:
            corner_outlier_images = load_corner_outlier_images(args.corner_outlier_dir)
            corner_outlier_summary = load_corner_outlier_summary(args.corner_outlier_dir)
 
        results['cross_corner_images'] = cross_corner_images
        results['voltage_images'] = voltage_images
        results['corner_outlier_images'] = corner_outlier_images
        results['sensitivity_images'] = sensitivity_images
        results['sensitivity_report'] = sensitivity_report
        # Generate HTML report
        generate_html_report(results, summary, args.output_dir)
 
        logging.info("Report generation complete")
    except Exception as e:
        logging.error(f"Error in main process: {e}")
        logging.error(traceback.format_exc())
        sys.exit(1)
 
 
if __name__ == "__main__":
    main()
