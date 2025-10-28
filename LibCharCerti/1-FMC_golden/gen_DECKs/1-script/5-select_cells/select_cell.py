#!/usr/bin/env /usr/local/python/3.9.10/bin/python3
"""
Cell Selection Script for Timing Analysis - Systematic Family-Based Selection with PT Pattern Analysis
 
This script processes timing analysis prediction files and generates
summary reports with systematic golden cell selection based on:
1. Top 10 worst case cells (fixed)
2. Top 10 families by violation count with proportional allocation of 20 additional cells
3. PT pattern analysis to understand table point distribution
 
Features:
- Systematic family-based selection to avoid drive strength redundancy
- PT pattern analysis for outlier distribution insights
- Organized output structure by timing type
- Comprehensive logging with detailed headers
 
Author: Generated for timing library analysis
Date: 2025
Version: 1.0 - Complete systematic selection with PT analysis
"""
 
import pandas as pd
import numpy as np
import argparse
import os
import glob
import sys
import re
from typing import List, Dict, Tuple, Optional
import logging
import math
from datetime import datetime
 
 
def setup_logging(verbose: bool = False, log_file: Optional[str] = None):
    """Setup logging configuration with enhanced formatting"""
    level = logging.DEBUG if verbose else logging.INFO
    format_str = '%(asctime)s - %(levelname)s - %(message)s'
   
    handlers = [logging.StreamHandler(sys.stdout)]
    if log_file:
        handlers.append(logging.FileHandler(log_file, mode='a'))
   
    logging.basicConfig(
        level=level,
        format=format_str,
        handlers=handlers
    )
 
 
def write_processing_header(log_file: str, node: str, timing_type: str, output_dir: str,
                           top_worst_count: int, family_allocation_count: int, corners: List[str]):
    """Write comprehensive header information to the processing log"""
   
    header = f"""
================================================================================
SYSTEMATIC CELL SELECTION - PYTHON PROCESSING LOG
================================================================================
Script Version: 1.0 - Family-based selection with PT pattern analysis
Processing Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Python Version: {sys.version.split()[0]}
 
PROCESSING CONFIGURATION:
================================================================================
Node: {node}
Timing Type: {timing_type}
Output Directory: {output_dir}
Corners: {', '.join(corners)}
 
SELECTION METHODOLOGY:
================================================================================
Phase 1: Top {top_worst_count} worst case cells (by absolute margin)
Phase 2: Family analysis of top 10 families by violation count
Phase 3: Proportional allocation of {family_allocation_count} additional cells
Phase 4: PT pattern analysis for outlier distribution insights
 
Cell Family Definition:
- Remove everything from 'BWP' onwards
- Remove trailing drive strength (D + digits)
- Example: CKLNQOPPZPDMZD4BWP130HPNPN3P48CPD -> CKLNQOPPZPDMZ
 
PT Pattern Analysis:
- Extract table points from fir_index and sec_index
- Analyze distribution to detect concentration patterns
- Identify if certain pt patterns dominate outliers
 
EXPECTED OUTPUTS:
================================================================================
1. Cell Summary Report: All cells ranked by worst absolute margin
2. Detailed Report: All timing entries sorted by severity
3. Golden Cell Selection: Systematic selection with methodology tracking
4. Family Allocation Report: Top 10 families with proportional allocation
5. PT Pattern Analysis: Table point distribution and concentration analysis
6. Text File: Simple cell list for simulation scripts
 
================================================================================
PROCESSING STEPS LOG:
================================================================================
 
"""
   
    with open(log_file, 'w') as f:
        f.write(header)
 
 
def parse_arc_info(key: str) -> Dict[str, str]:
    """
    Parse arc information from cell_arc_pt string
    Adapted from the original parse_arc_info function for prediction files
   
    Args:
        key: cell_arc_pt string containing timing arc information
       
    Returns:
        Dictionary containing parsed arc information
    """
    parts = key.split("_")
   
    # Detect the type of arc and adjust parsing for 'mpw' (minimum pulse width) if necessary
    if parts[0] == 'min' and parts[1] == 'pulse' and parts[2] == 'width':
        # Handle minimum pulse width case
        timing_type = f"{parts[0]}_{parts[1]}_{parts[2]}"  # Combine 'min', 'pulse', 'width'
        cell_name = parts[3]
        out_pin = parts[4]
        out_pin_direction = parts[5]
        rel_pin = parts[6]
        rel_pin_direction = parts[7]
        when_condition = parts[8:-1]  # All parts except the last one (which contains PT pattern)
       
        # Extract PT pattern from the last part (format: "condition_X-Y" where X-Y is the PT pattern)
        last_part = parts[-1]
        if '-' in last_part:
            # Split by '-' to get fir_index and sec_index
            pt_parts = last_part.split('-')
            if len(pt_parts) >= 2:
                fir_index = pt_parts[0]
                sec_index = pt_parts[1]
            else:
                fir_index = last_part
                sec_index = ""
        else:
            # If no '-' found, the whole last part might be an index
            fir_index = last_part
            sec_index = ""
       
    else:
        # Default parsing for other types of arcs
        timing_type = parts[0]
        cell_name = parts[1]
        out_pin = parts[2]
        out_pin_direction = parts[3]
        rel_pin = parts[4]
        rel_pin_direction = parts[5]
        when_condition = parts[6:-1]  # Exclude last 2 parts which are indices
        # Extract PT pattern from the last part (format: "condition_X-Y" where X-Y is the PT pattern)
        last_part = parts[-1]
        if '-' in last_part:
            # Split by '-' to get fir_index and sec_index
            pt_parts = last_part.split('-')
            if len(pt_parts) >= 2:
                fir_index = pt_parts[0]
                sec_index = pt_parts[1]
            else:
                fir_index = last_part
                sec_index = ""
        else:
            # If no '-' found, the whole last part might be an index
            fir_index = last_part
            sec_index = ""
   
    # Process the 'when_condition' to handle "NO CONDITION" or custom cases
    if len(when_condition) > 1 and when_condition[0] == "NO" and when_condition[1] == "CONDITION":
        when = "None"
    else:
        # Join all condition parts and replace 'not' with '!'
        replaced_list = [item.replace('not', '!') for item in when_condition]
        when = "_".join(replaced_list)
   
    result = {
        'timing_type': timing_type,
        'cell_name': cell_name,
        'out_pin': out_pin,
        'out_pin_direction': out_pin_direction,
        'rel_pin': rel_pin,
        'rel_pin_direction': rel_pin_direction,
        'when_condition': when,
        'fir_index': fir_index,
        'sec_index': sec_index
    }
   
    return result
 
 
def load_prediction_files(pred_files_dir: str, corners: List[str]) -> pd.DataFrame:
    """
    Load all prediction files and combine them with corner information
   
    Args:
        pred_files_dir: Directory containing prediction files
        corners: List of corner names to process
       
    Returns:
        Combined DataFrame with corner information
    """
    all_dataframes = []
   
    for corner in corners:
        # Find files matching the pattern for this corner
        pattern = os.path.join(pred_files_dir, f"prediction_results.csv.{corner}")
        files = glob.glob(pattern)
       
        if not files:
            logging.warning(f"No files found for corner: {corner}")
            continue
           
        for file_path in files:
            logging.info(f"Loading file: {os.path.basename(file_path)}")
           
            try:
                df = pd.read_csv(file_path)
                df['corner'] = corner
                df['source_file'] = os.path.basename(file_path)
                all_dataframes.append(df)
                logging.debug(f"Loaded {len(df)} rows from {os.path.basename(file_path)}")
               
            except Exception as e:
                logging.error(f"Error loading file {file_path}: {str(e)}")
                continue
   
    if not all_dataframes:
        raise ValueError("No valid prediction files found!")
   
    # Combine all dataframes
    combined_df = pd.concat(all_dataframes, ignore_index=True)
    logging.info(f"Combined {len(all_dataframes)} files into {len(combined_df)} total rows")
   
    return combined_df
 
 
def extract_cell_info(df: pd.DataFrame) -> pd.DataFrame:
    """
    Extract cell information from cell_arc_pt column
   
    Args:
        df: DataFrame containing cell_arc_pt column
       
    Returns:
        DataFrame with extracted cell information
    """
    logging.info("Extracting cell information from cell_arc_pt...")
   
    # Parse arc information for each row
    parsed_info = []
   
    for idx, row in df.iterrows():
        try:
            cell_arc_pt = row['cell_arc_pt']
            arc_info = parse_arc_info(cell_arc_pt)
            parsed_info.append(arc_info)
           
        except Exception as e:
            logging.warning(f"Error parsing row {idx}: {cell_arc_pt} - {str(e)}")
            # Add empty info for failed parsing
            parsed_info.append({
                'timing_type': 'unknown',
                'cell_name': 'unknown',
                'out_pin': 'unknown',
                'out_pin_direction': 'unknown',
                'rel_pin': 'unknown',
                'rel_pin_direction': 'unknown',
                'when_condition': 'unknown',
                'fir_index': '',
                'sec_index': ''
            })
   
    # Convert parsed info to DataFrame and join with original
    parsed_df = pd.DataFrame(parsed_info)
    result_df = pd.concat([df, parsed_df], axis=1)
   
    logging.info(f"Successfully extracted cell information for {len(result_df)} rows")
    return result_df
 
 
def filter_outliers(df: pd.DataFrame, positive_outliers_only: bool) -> pd.DataFrame:
    """
    Filter outliers based on margin values
   
    Args:
        df: DataFrame with margin column
        positive_outliers_only: If True, remove positive margin entries
       
    Returns:
        Filtered DataFrame
    """
    if not positive_outliers_only:
        logging.info("No outlier filtering requested")
        return df
   
    initial_count = len(df)
   
    # Remove positive margin entries (keep only negative margins)
    filtered_df = df[df['margin'] < 0].copy()
   
    final_count = len(filtered_df)
    removed_count = initial_count - final_count
   
    logging.info(f"Filtered outliers: removed {removed_count} positive margin entries")
    logging.info(f"Remaining entries: {final_count}")
   
    return filtered_df
 
 
def generate_cell_summary(df: pd.DataFrame) -> pd.DataFrame:
    """
    Generate summary statistics grouped by cell
   
    Args:
        df: DataFrame with cell information and margin values
       
    Returns:
        Summary DataFrame grouped by cell
    """
    logging.info("Generating cell summary statistics...")
   
    # Group by cell_name and calculate statistics
    summary_stats = []
   
    grouped = df.groupby('cell_name')
   
    for cell_name, group in grouped:
        # Calculate statistics for this cell
        count = len(group)
       
        # Find worst case (largest absolute margin value)
        abs_margins = group['margin'].abs()
        worst_case_idx = abs_margins.idxmax()
        worst_case_margin = group.loc[worst_case_idx, 'margin']
        worst_case_abs = abs(worst_case_margin)
       
        # Additional statistics
        min_margin = group['margin'].min()
        max_margin = group['margin'].max()
        mean_margin = group['margin'].mean()
        std_margin = group['margin'].std()
       
        # Count by timing type
        timing_type_counts = group['timing_type'].value_counts().to_dict()
       
        # Count by corner
        corner_counts = group['corner'].value_counts().to_dict()
       
        # Get worst case details
        worst_case_row = group.loc[worst_case_idx]
       
        summary_stats.append({
            'cell_name': cell_name,
            'total_count': count,
            'worst_case_margin': worst_case_margin,
            'worst_case_abs_margin': worst_case_abs,
            'min_margin': min_margin,
            'max_margin': max_margin,
            'mean_margin': mean_margin,
            'std_margin': std_margin,
            'worst_case_timing_type': worst_case_row['timing_type'],
            'worst_case_corner': worst_case_row['corner'],
            'worst_case_arc': worst_case_row['cell_arc_pt'],
            'timing_type_counts': str(timing_type_counts),
            'corner_counts': str(corner_counts)
        })
   
    # Convert to DataFrame and sort by worst case absolute margin
    summary_df = pd.DataFrame(summary_stats)
    summary_df = summary_df.sort_values('worst_case_abs_margin', ascending=False)
    summary_df = summary_df.reset_index(drop=True)
   
    logging.info(f"Generated summary for {len(summary_df)} unique cells")
   
    return summary_df
 
 
def generate_detailed_report(df: pd.DataFrame) -> pd.DataFrame:
    """
    Generate detailed report with all processed data
   
    Args:
        df: Processed DataFrame
       
    Returns:
        Detailed report DataFrame
    """
    logging.info("Generating detailed report...")
   
    # Sort by absolute margin value (worst case first)
    detailed_df = df.copy()
    detailed_df['abs_margin'] = detailed_df['margin'].abs()
    detailed_df = detailed_df.sort_values('abs_margin', ascending=False)
    detailed_df = detailed_df.reset_index(drop=True)
   
    # Select relevant columns for the report
    report_columns = [
        'cell_name', 'timing_type', 'corner', 'margin', 'abs_margin',
        'out_pin', 'rel_pin', 'when_condition', 'cell_arc_pt',
        'fir_index', 'sec_index', 'Predicted Error (%)', 'lib_late_sigma', 'source_file'
    ]
   
    # Include only columns that exist in the DataFrame
    available_columns = [col for col in report_columns if col in detailed_df.columns]
    detailed_report = detailed_df[available_columns].copy()
   
    logging.info(f"Generated detailed report with {len(detailed_report)} entries")
   
    return detailed_report
 
 
def extract_cell_family(cell_name: str) -> str:
    """
    Extract cell family pattern using systematic rules:
    1. Remove everything from and including "BWP" onwards
    2. Remove trailing drive strength (D + digits)
   
    Args:
        cell_name: Full cell name
       
    Returns:
        Cell family pattern
    """
    family = cell_name
   
    # Step 1: Remove everything from "BWP" onwards
    bwp_pos = family.find("BWP")
    if bwp_pos != -1:
        family = family[:bwp_pos]
   
    # Step 2: Remove trailing drive strength (D + digits)
    family = re.sub(r'D\d+$', '', family)
   
    return family
 
 
def analyze_cell_families_systematic(detailed_df: pd.DataFrame) -> pd.DataFrame:
    """
    Analyze cell families systematically:
    1. Extract family for each entry in detailed list
    2. Count total violations per family
    3. Find worst case per family
    4. Keep top 10 families by total count
   
    Args:
        detailed_df: Detailed DataFrame with all timing entries
       
    Returns:
        DataFrame with top 10 family analysis
    """
    logging.info("\n")
    logging.info("==========================================")
    logging.info("Analyzing cell families systematically...")
   
    # Create abs_margin column if it doesn't exist
    if 'abs_margin' not in detailed_df.columns:
        detailed_df['abs_margin'] = detailed_df['margin'].abs()
   
    # Extract family for each detailed entry
    detailed_df['cell_family'] = detailed_df['cell_name'].apply(extract_cell_family)
   
    # Group by family and analyze
    family_stats = []
   
    for family, group in detailed_df.groupby('cell_family'):
        # Count total violations for this family
        total_count = len(group)
       
        # Find worst case in this family (largest absolute margin)
        abs_margins = group['abs_margin']
        worst_idx = abs_margins.idxmax()
        worst_margin = group.loc[worst_idx, 'margin']
        worst_abs_margin = abs_margins.max()
        worst_cell = group.loc[worst_idx, 'cell_name']
       
        # Additional family statistics
        unique_cells = group['cell_name'].nunique()
        avg_margin = group['margin'].mean()
        timing_types = group['timing_type'].unique().tolist()
        corners = group['corner'].unique().tolist()
       
        family_stats.append({
            'family_name': family,
            'total_violations': total_count,
            'unique_cells_in_family': unique_cells,
            'worst_margin': worst_margin,
            'worst_abs_margin': worst_abs_margin,
            'worst_cell_in_family': worst_cell,
            'avg_margin': avg_margin,
            'timing_types': timing_types,
            'corners': corners
        })
   
    # Convert to DataFrame and sort by total violations (descending)
    family_df = pd.DataFrame(family_stats)
    family_df = family_df.sort_values('total_violations', ascending=False)
    family_df = family_df.reset_index(drop=True)
   
    # Keep only top 10 families
    top_10_families = family_df.head(10).copy()
   
    # Calculate ratios for top 10 families
    top_10_total = top_10_families['total_violations'].sum()
    top_10_families['violation_ratio'] = top_10_families['total_violations'] / top_10_total
   
    logging.info(f"Found {len(family_df)} total families")
    logging.info(f"Top 10 families account for {top_10_total} violations")
   
    return top_10_families
 
 
def analyze_pt_patterns(detailed_df: pd.DataFrame) -> pd.DataFrame:
    """
    Analyze PT (table point) patterns from cell_arc_pt index information
    to understand if certain pt patterns dominate outliers or are evenly distributed
   
    Args:
        detailed_df: Detailed DataFrame with all timing entries
       
    Returns:
        DataFrame with PT pattern analysis
    """
    logging.info("Analyzing PT pattern distribution...")
   
    # Debug: Check what index values we actually have
    unique_fir = detailed_df['fir_index'].unique()
    unique_sec = detailed_df['sec_index'].unique()
    logging.info(f"Unique fir_index values found: {unique_fir}")
    logging.info(f"Unique sec_index values found: {unique_sec}")
   
    # Create PT pattern from fir_index and sec_index using the format from your data (X-Y)
    detailed_df['pt_pattern'] = detailed_df['fir_index'].astype(str) + '-' + detailed_df['sec_index'].astype(str)
   
    # Debug: Show all unique patterns before filtering
    all_patterns = detailed_df['pt_pattern'].unique()
    logging.info(f"All PT patterns found: {all_patterns}")
   
    # Filter out patterns where both indices are empty (--) or contain 'nan'
    valid_patterns = detailed_df[
        (detailed_df['pt_pattern'] != '-') &
        (detailed_df['pt_pattern'] != 'nan-nan') &
        (~detailed_df['pt_pattern'].str.contains('nan', na=False))
    ].copy()
   
    logging.info(f"Valid PT patterns after filtering: {len(valid_patterns)} entries")
   
    if len(valid_patterns) == 0:
        logging.warning("No valid PT patterns found after filtering")
        # Show sample cell_arc_pt for debugging
        sample_arcs = detailed_df['cell_arc_pt'].head(5).tolist()
        logging.warning(f"Sample cell_arc_pt entries for debugging: {sample_arcs}")
        return pd.DataFrame()
   
    # Group by PT pattern and analyze
    pattern_stats = []
   
    for pattern, group in valid_patterns.groupby('pt_pattern'):
        # Count violations for this pattern
        violation_count = len(group)
       
        # Find worst case for this pattern
        abs_margins = group['margin'].abs()
        worst_idx = abs_margins.idxmax()
        worst_margin = group.loc[worst_idx, 'margin']
        worst_abs_margin = abs_margins.max()
        worst_cell = group.loc[worst_idx, 'cell_name']
       
        # Additional statistics
        avg_margin = group['margin'].mean()
        std_margin = group['margin'].std()
        unique_cells = group['cell_name'].nunique()
        timing_types = group['timing_type'].unique().tolist()
        corners = group['corner'].unique().tolist()
       
        pattern_stats.append({
            'pt_pattern': pattern,
            'violation_count': violation_count,
            'unique_cells_affected': unique_cells,
            'worst_margin': worst_margin,
            'worst_abs_margin': worst_abs_margin,
            'worst_cell': worst_cell,
            'avg_margin': avg_margin,
            'std_margin': std_margin,
            'timing_types': str(timing_types),
            'corners': str(corners)
        })
   
    # Convert to DataFrame and sort by violation count (descending)
    pattern_df = pd.DataFrame(pattern_stats)
    pattern_df = pattern_df.sort_values('violation_count', ascending=False)
    pattern_df = pattern_df.reset_index(drop=True)
   
    # Calculate distribution statistics
    total_violations = pattern_df['violation_count'].sum()
    pattern_df['violation_percentage'] = (pattern_df['violation_count'] / total_violations * 100)
   
    # Add cumulative percentage to see concentration
    pattern_df['cumulative_percentage'] = pattern_df['violation_percentage'].cumsum()
   
    logging.info(f"Found {len(pattern_df)} unique PT patterns")
    logging.info(f"Total violations analyzed: {total_violations}")
   
    # Log top patterns for distribution check
    logging.info("Top 10 PT patterns by violation count:")
    for i, (_, pattern) in enumerate(pattern_df.head(10).iterrows(), 1):
        logging.info(f"  {i}. {pattern['pt_pattern']}: {pattern['violation_count']} "
                    f"({pattern['violation_percentage']:.1f}%), "
                    f"cumulative: {pattern['cumulative_percentage']:.1f}%")
   
    # Check for concentration (if top 20% of patterns account for >80% of violations)
    if len(pattern_df) > 1:
        top_20_percent_count = max(1, len(pattern_df) // 5)
        top_20_percent_violations = pattern_df.head(top_20_percent_count)['violation_percentage'].sum()
       
        if top_20_percent_violations > 80:
            logging.warning(f"PT pattern concentration detected: Top {top_20_percent_count} patterns "
                           f"({top_20_percent_count/len(pattern_df)*100:.1f}% of patterns) account for "
                           f"{top_20_percent_violations:.1f}% of violations")
        else:
            logging.info(f"PT patterns are reasonably distributed: Top {top_20_percent_count} patterns "
                        f"account for {top_20_percent_violations:.1f}% of violations")
   
    return pattern_df
 
 
def select_golden_cells_systematic(summary_df: pd.DataFrame, detailed_df: pd.DataFrame,
                                 top_worst_count: int = 10, family_allocation_count: int = 20) -> Tuple[List[str], pd.DataFrame, Dict]:
    """
    Systematic golden cell selection:
    1. Top N worst cases (fixed selection)
    2. Top 10 families by violation count
    3. Allocate remaining cells proportionally by family ratio
    4. Avoid duplicates from top worst list
   
    Args:
        summary_df: Summary DataFrame grouped by cell
        detailed_df: Detailed DataFrame with all entries 
        top_worst_count: Number of top worst cases to always select
        family_allocation_count: Number of additional cells to allocate by family
       
    Returns:
        Tuple of (selected cells list, family analysis, allocation details)
    """
    logging.info(f"Starting systematic golden cell selection...")
    logging.info(f"Phase 1: Top {top_worst_count} worst cases (fixed)")
    logging.info(f"Phase 2: {family_allocation_count} cells allocated by family ratio")
   
    # Ensure abs_margin column exists in detailed_df for family analysis
    if 'abs_margin' not in detailed_df.columns:
        detailed_df = detailed_df.copy()  # Don't modify original
        detailed_df['abs_margin'] = detailed_df['margin'].abs()
   
    # Add family information to summary
    summary_df['cell_family'] = summary_df['cell_name'].apply(extract_cell_family)
   
    # Phase 1: Top worst cases (fixed)
    top_worst_cells = summary_df.head(top_worst_count)['cell_name'].tolist()
   
    logging.info(f"Selected top {len(top_worst_cells)} worst cases:")
    for i, cell in enumerate(top_worst_cells, 1):
        margin = summary_df[summary_df['cell_name'] == cell]['worst_case_margin'].iloc[0]
        logging.info(f"  {i}. {cell}: {margin:.6f}")
   
    # Phase 2: Family analysis and allocation
    family_analysis = analyze_cell_families_systematic(detailed_df)
   
    logging.info("Top 10 families by violation count:")
    for i, (_, family) in enumerate(family_analysis.iterrows(), 1):
        logging.info(f"  {i}. {family['family_name']}: {family['total_violations']} violations "
                    f"({family['violation_ratio']:.1%})")
   
    # Calculate allocation for each family
    allocation_details = {}
    additional_selected = []
   
    for _, family_row in family_analysis.iterrows():
        family_name = family_row['family_name']
        ratio = family_row['violation_ratio']
        allocated_count = max(1, round(family_allocation_count * ratio))  # At least 1 per family
       
        # Get all cells from this family, sorted by worst margin
        family_cells = summary_df[summary_df['cell_family'] == family_name].copy()
        family_cells = family_cells.sort_values('worst_case_abs_margin', ascending=False)
       
        # Select cells from this family, avoiding duplicates from top worst list
        selected_from_family = []
        for _, cell_row in family_cells.iterrows():
            cell_name = cell_row['cell_name']
            if cell_name not in top_worst_cells and cell_name not in additional_selected:
                selected_from_family.append(cell_name)
                additional_selected.append(cell_name)
                if len(selected_from_family) >= allocated_count:
                    break
       
        allocation_details[family_name] = {
            'ratio': ratio,
            'allocated_count': allocated_count,
            'selected_count': len(selected_from_family),
            'selected_cells': selected_from_family,
            'total_family_violations': family_row['total_violations'],
            'worst_cell_in_family': family_row['worst_cell_in_family']
        }
       
        logging.info(f"Family {family_name}: allocated {allocated_count}, selected {len(selected_from_family)}")
   
    # Combine all selections
    all_selected = top_worst_cells + additional_selected
   
    logging.info(f"Systematic selection completed:")
    logging.info(f"  Top worst cases: {len(top_worst_cells)}")
    logging.info(f"  Family allocated: {len(additional_selected)}")
    logging.info(f"  Total selected: {len(all_selected)}")
   
    return all_selected, family_analysis, allocation_details
 
 
def save_systematic_golden_selection(selected_cells: List[str], family_analysis: pd.DataFrame,
                                   allocation_details: Dict, summary_df: pd.DataFrame,
                                   detailed_df: pd.DataFrame, output_path: str,
                                   top_worst_count: int):
    """
    Save systematic golden cell selection with detailed allocation information
   
    Args:
        selected_cells: List of selected cell names
        family_analysis: Family analysis DataFrame
        allocation_details: Dictionary with allocation details per family
        summary_df: Summary DataFrame
        detailed_df: Detailed DataFrame
        output_path: Path to save the golden cell list
        top_worst_count: Number of top worst cases
    """
    logging.info(f"Saving systematic golden cell selection to: {output_path}")
   
    # Create detailed golden cell report
    golden_details = []
   
    for i, cell_name in enumerate(selected_cells, 1):
        # Get cell summary info
        cell_summary = summary_df[summary_df['cell_name'] == cell_name].iloc[0]
        cell_family = cell_summary['cell_family']
       
        # Determine selection method
        if i <= top_worst_count:
            selection_method = "top_worst_case"
            family_info = "N/A (top worst)"
        else:
            selection_method = "family_allocation"
            family_details = allocation_details.get(cell_family, {})
            family_info = f"Family ratio: {family_details.get('ratio', 0):.1%}"
       
        golden_details.append({
            'rank': i,
            'cell_name': cell_name,
            'cell_family': cell_family,
            'selection_method': selection_method,
            'worst_case_margin': cell_summary['worst_case_margin'],
            'worst_case_abs_margin': cell_summary['worst_case_abs_margin'],
            'total_violations': cell_summary['total_count'],
            'worst_timing_type': cell_summary['worst_case_timing_type'],
            'worst_corner': cell_summary['worst_case_corner'],
            'family_info': family_info,
            'worst_arc': cell_summary['worst_case_arc']
        })
   
    # Save detailed golden cell CSV
    golden_df = pd.DataFrame(golden_details)
    golden_df.to_csv(output_path, index=False)
   
    # Save family allocation summary
    allocation_summary_path = output_path.replace('.csv', '_family_allocation.csv')
    allocation_summary = []
   
    for family_name, details in allocation_details.items():
        allocation_summary.append({
            'family_name': family_name,
            'violation_ratio': details['ratio'],
            'allocated_count': details['allocated_count'],
            'selected_count': details['selected_count'],
            'total_family_violations': details['total_family_violations'],
            'worst_cell_in_family': details['worst_cell_in_family'],
            'selected_cells': ', '.join(details['selected_cells'])
        })
   
    allocation_df = pd.DataFrame(allocation_summary)
    allocation_df.to_csv(allocation_summary_path, index=False)
   
    # Save simple text list for scripting
    text_path = output_path.replace('.csv', '.txt')
    with open(text_path, 'w') as f:
        f.write("# Systematic Golden Cell Selection List\n")
        f.write(f"# Top {top_worst_count} worst cases + family-allocated cells\n")
        f.write(f"# Total: {len(selected_cells)} cells selected\n")
        f.write("# Format: cell_name\n\n")
        for cell in selected_cells:
            f.write(f"{cell}\n")
   
    logging.info(f"Golden cell list saved as text: {text_path}")
    logging.info(f"Family allocation summary saved: {allocation_summary_path}")
 
 
def save_reports(summary_df: pd.DataFrame, detailed_df: pd.DataFrame,
                summary_path: str, detailed_path: str, golden_cells: List[str] = None,
                golden_path: str = None, family_analysis: pd.DataFrame = None,
                allocation_details: Dict = None, top_worst_count: int = 10,
                pt_pattern_df: pd.DataFrame = None, pt_pattern_path: str = None):
    """
    Save summary and detailed reports to CSV files
   
    Args:
        summary_df: Summary DataFrame
        detailed_df: Detailed DataFrame
        summary_path: Path for summary report
        detailed_path: Path for detailed report
        golden_cells: List of selected golden cells
        golden_path: Path for golden cell list
        family_analysis: Family analysis DataFrame
        allocation_details: Allocation details dictionary
        top_worst_count: Number of top worst cases
        pt_pattern_df: PT pattern analysis DataFrame
        pt_pattern_path: Path for PT pattern report
    """
    try:
        # Save summary report
        summary_df.to_csv(summary_path, index=False)
        logging.info(f"Summary report saved to: {summary_path}")
       
        # Save detailed report
        detailed_df.to_csv(detailed_path, index=False)
        logging.info(f"Detailed report saved to: {detailed_path}")
       
        # Save PT pattern analysis if provided
        if pt_pattern_df is not None and pt_pattern_path:
            pt_pattern_df.to_csv(pt_pattern_path, index=False)
            logging.info(f"PT pattern analysis saved to: {pt_pattern_path}")
       
        # Save systematic golden cell selection if provided
        if golden_cells and golden_path and family_analysis is not None and allocation_details is not None:
            save_systematic_golden_selection(golden_cells, family_analysis, allocation_details,
                                           summary_df, detailed_df, golden_path, top_worst_count)
       
        # Print summary statistics
        logging.info("\n" + "="*50)
        logging.info("SYSTEMATIC CELL SELECTION SUMMARY")
        logging.info("="*50)
        logging.info(f"Total unique cells processed: {len(summary_df)}")
        logging.info(f"Total timing entries processed: {len(detailed_df)}")
       
        if pt_pattern_df is not None:
            logging.info(f"Unique PT patterns found: {len(pt_pattern_df)}")
            if len(pt_pattern_df) > 0:
                top_pattern = pt_pattern_df.iloc[0]
                logging.info(f"Most frequent PT pattern: {top_pattern['pt_pattern']} "
                           f"({top_pattern['violation_percentage']:.1f}% of violations)")
       
        if golden_cells:
            logging.info(f"Golden cells selected: {len(golden_cells)}")
            logging.info(f"  - Top worst cases: {top_worst_count}")
            logging.info(f"  - Family allocated: {len(golden_cells) - top_worst_count}")
           
        if family_analysis is not None:
            logging.info(f"Top 10 families analyzed for allocation")
       
        if len(summary_df) > 0:
            worst_cell = summary_df.iloc[0]
            logging.info(f"Worst case cell: {worst_cell['cell_name']}")
            logging.info(f"Worst case margin: {worst_cell['worst_case_margin']:.6f}")
            logging.info(f"Worst case timing type: {worst_cell['worst_case_timing_type']}")
            logging.info(f"Worst case corner: {worst_cell['worst_case_corner']}")
       
    except Exception as e:
        logging.error(f"Error saving reports: {str(e)}")
        raise
 
 
def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Systematic cell selection for timing analysis with PT pattern analysis')
   
    parser.add_argument('--work-dir', required=True, help='Working directory for scripts and output')
    parser.add_argument('--pred-files-dir', required=True, help='Directory containing prediction files')
    parser.add_argument('--output-dir', required=True, help='Output directory for reports')
    parser.add_argument('--corners', required=True, help='Comma-separated list of corners')
    parser.add_argument('--type', required=True, help='Timing type: delay, slew, hold, or mpw')
    parser.add_argument('--node', required=True, help='Node identifier for output file naming')
    parser.add_argument('--summary-report', required=True, help='Path for summary report')
    parser.add_argument('--detailed-report', required=True, help='Path for detailed report')
    parser.add_argument('--golden-cell-list', help='Path for golden cell selection list')
    parser.add_argument('--pt-pattern-report', help='Path for PT pattern analysis report')
    parser.add_argument('--top-worst-count', type=int, default=10, help='Number of top worst cases to select')
    parser.add_argument('--family-allocation-count', type=int, default=20, help='Number of additional cells for family allocation')
    parser.add_argument('--positive-outliers-only', action='store_true',
                       help='Remove positive margin entries')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose logging')
   
    args = parser.parse_args()
   
    # Setup logging with header
    python_log_file = os.path.join(args.output_dir, f'{args.node}_{args.type}_python_processing.log')
    setup_logging(args.verbose, python_log_file)
   
    # Write comprehensive header to log file
    try:
        corners = [c.strip() for c in args.corners.split(',')]
        write_processing_header(python_log_file, args.node, args.type, args.output_dir,
                               args.top_worst_count, args.family_allocation_count, corners)
        logging.info("\n")
        logging.info("================================================================")
        logging.info("Starting systematic cell selection processing...")
        logging.info("================================================================\n")
        logging.info(f"Working directory: {args.work_dir}")
        logging.info(f"Prediction files directory: {args.pred_files_dir}")
        logging.info(f"Output directory: {args.output_dir}")
        logging.info(f"Node: {args.node}")
        logging.info(f"Type: {args.type}")
        logging.info(f"Corners: {corners}")
        logging.info(f"Positive outliers only: {args.positive_outliers_only}")
        logging.info(f"Selection criteria: Top {args.top_worst_count} worst + {args.family_allocation_count} family-allocated")
       
        # Step 1: Load all prediction files
        logging.info("\n")
        logging.info("================================================================")
        logging.info("Step 1: Loading prediction files...")
        logging.info("================================================================\n")
        combined_df = load_prediction_files(args.pred_files_dir, corners)
       
        # Step 2: Extract cell information
        logging.info("\n")
        logging.info("================================================================")
        logging.info("Step 2: Extracting cell information...")
        logging.info("================================================================\n")
        processed_df = extract_cell_info(combined_df)
       
        # Step 3: Filter outliers if requested
        logging.info("\n")
        logging.info("================================================================")
        logging.info("Step 3: Filtering outliers...")
        logging.info("================================================================\n")
        filtered_df = filter_outliers(processed_df, args.positive_outliers_only)
       
        # Step 4: Generate summary report by cell
        logging.info("\n")
        logging.info("================================================================")
        logging.info("Step 4: Generating cell summary...")
        logging.info("================================================================\n")
        summary_df = generate_cell_summary(filtered_df)
       
        # Step 5: Generate detailed report
        logging.info("\n")
        logging.info("================================================================")
        logging.info("Step 5: Generating detailed report...")
        logging.info("================================================================\n")
        detailed_df = generate_detailed_report(filtered_df)
       
        # Step 6: Generate PT pattern analysis
        logging.info("\n")
        logging.info("================================================================")
        logging.info("Step 6: Analyzing PT patterns...")
        logging.info("================================================================\n")
        pt_pattern_df = None
        if args.pt_pattern_report:
            pt_pattern_df = analyze_pt_patterns(filtered_df)
       
        # Step 7: Systematic golden cell selection
        logging.info("\n")
        logging.info("================================================================")
        logging.info("Step 7: Systematic golden cell selection...")
        logging.info("================================================================\n")
        golden_cells = None
        family_analysis = None
        allocation_details = None
       
        if args.golden_cell_list:
            golden_cells, family_analysis, allocation_details = select_golden_cells_systematic(
                summary_df, filtered_df, args.top_worst_count, args.family_allocation_count)
       
        # Step 8: Save reports
        logging.info("\n")
        logging.info("================================================================")
        logging.info("Step 8: Saving reports...")
        logging.info("================================================================\n")
        save_reports(summary_df, detailed_df, args.summary_report, args.detailed_report,
                    golden_cells, args.golden_cell_list, family_analysis, allocation_details,
                    args.top_worst_count, pt_pattern_df, args.pt_pattern_report)
       
        logging.info("Systematic cell selection processing completed successfully!")
       
    except Exception as e:
        logging.error(f"Error during processing: {str(e)}")
        sys.exit(1)
 
 
if __name__ == "__main__":
    main()
 
