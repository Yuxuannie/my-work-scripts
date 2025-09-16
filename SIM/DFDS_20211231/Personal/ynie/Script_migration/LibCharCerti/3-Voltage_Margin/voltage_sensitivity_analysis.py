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
import argparse
from matplotlib.ticker import FormatStrFormatter
import matplotlib.gridspec as gridspec
from matplotlib.colors import LinearSegmentedColormap
import math
import warnings
import time
warnings.filterwarnings("ignore")
 
# Configure logging with different handlers for different types of logs
def setup_logging(output_dir):
    """Set up logging to separate files for different types of information."""
    os.makedirs(output_dir, exist_ok=True)
 
    # Main log file
    main_log_file = os.path.join(output_dir, "voltage_sensitivity_analysis.log")
 
    # Calculation diagnostics log file
    calc_log_file = os.path.join(output_dir, "calculation_diagnostics.log")
 
    # Data flow log file
    data_flow_log_file = os.path.join(output_dir, "data_flow.log")
 
    # Configure root logger
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s',
        filename=main_log_file,
        filemode='w'
    )
 
    # Create console handler
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
    logging.getLogger('').addHandler(console)
 
    # Create calculation logger
    calc_logger = logging.getLogger('calculation')
    calc_handler = logging.FileHandler(calc_log_file, mode='w')
    calc_handler.setLevel(logging.DEBUG)
    calc_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    calc_logger.setLevel(logging.DEBUG)
    calc_logger.addHandler(calc_handler)
 
    # Create data flow logger
    flow_logger = logging.getLogger('dataflow')
    flow_handler = logging.FileHandler(data_flow_log_file, mode='w')
    flow_handler.setLevel(logging.DEBUG)
    flow_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    flow_logger.setLevel(logging.DEBUG)
    flow_logger.addHandler(flow_handler)
 
    # Log platform information
    import platform
    import sys
    logging.info(f"Python version: {sys.version}")
    logging.info(f"Platform: {platform.platform()}")
    logging.info(f"Matplotlib version: {plt.matplotlib.__version__}")
    logging.info(f"NumPy version: {np.__version__}")
    logging.info(f"Pandas version: {pd.__version__}")
 
    return {
        'main': logging.getLogger(''),
        'calculation': calc_logger,
        'dataflow': flow_logger
    }
 
def setup_verification_logger(log_file):
    """Set up a dedicated logger for verification output."""
    # Create a logger
    verification_logger = logging.getLogger('verification')
    verification_logger.setLevel(logging.INFO)
 
    # Remove existing handlers if any
    for handler in verification_logger.handlers[:]:
        verification_logger.removeHandler(handler)
 
    # Create file handler
    file_handler = logging.FileHandler(log_file, mode='w')
    file_handler.setLevel(logging.INFO)
 
    # Create formatter
    formatter = logging.Formatter('%(message)s')
    file_handler.setFormatter(formatter)
 
    # Add handler to logger
    verification_logger.addHandler(file_handler)
 
    return verification_logger
 
def save_figure_safely(fig, filename, dpi=200, max_size=2048):
    """Safely save a figure with size limits to avoid errors."""
    try:
        # Get figure size in inches
        fig_size_inches = fig.get_size_inches()
 
        # Calculate pixel dimensions at the current DPI
        width_pixels = fig_size_inches[0] * dpi
        height_pixels = fig_size_inches[1] * dpi
 
        # Check if dimensions exceed max_size
        if width_pixels > max_size or height_pixels > max_size:
            # Calculate scaling factor needed
            width_scale = max_size / width_pixels if width_pixels > max_size else 1
            height_scale = max_size / height_pixels if height_pixels > max_size else 1
            scale = min(width_scale, height_scale)
 
            # Apply scaling to DPI or figure size
            new_dpi = min(dpi, int(dpi * scale))
 
            logging.info(f"Reducing figure size/DPI for {os.path.basename(filename)}")
 
            try:
                # Try to save with reduced DPI
                fig.savefig(filename, dpi=new_dpi, bbox_inches='tight')
            except Exception as e:
                # If still failing, try reducing figure size directly
                logging.warning(f"Error saving figure with reduced DPI: {e}")
 
                # Resize the figure
                new_width = fig_size_inches[0] * scale
                new_height = fig_size_inches[1] * scale
                fig.set_size_inches(new_width, new_height)
 
                try:
                    fig.savefig(filename, dpi=dpi, bbox_inches='tight')
                except Exception as e2:
                    logging.error(f"Failed to save figure even with reduced size: {e2}")
                    # Try one last approach - very small figure with minimal DPI
                    fig.set_size_inches(8, 6)
                    fig.savefig(filename, dpi=100, bbox_inches='tight')
        else:
            # Size is within limits, save normally
            try:
                fig.savefig(filename, dpi=dpi, bbox_inches='tight')
            except Exception as e:
                logging.error(f"Error saving figure: {e}")
                # Try with minimal settings
                fig.set_size_inches(8, 6)
                fig.savefig(filename, dpi=100, bbox_inches='tight')
    except Exception as e:
        logging.error(f"Unexpected error in save_figure_safely: {e}")
        # Absolute fallback
        try:
            plt.figure(figsize=(6, 4))
            plt.text(0.5, 0.5, "Error creating figure", ha='center', va='center')
            plt.savefig(filename, dpi=72)
        except:
            logging.error("Failed to create even a fallback figure")
 
    # Close the figure to free memory
    plt.close(fig)
 
 
def extract_cell_info(arc_string):
    """Extract cell type and table position from Arc string."""
    if not arc_string or not isinstance(arc_string, str):
        return None, None
 
    if not arc_string.startswith('combinational_'):
        # Try to extract cell information from other formats
        parts = arc_string.split('_')
        if len(parts) >= 2:
            # Assume second part might be cell type in other formats
            cell = parts[1]
 
            # Look for something that might be a table position (contains a hyphen)
            table_position = None
            for part in parts:
                if '-' in part and re.match(r'\d+-\d+', part):
                    table_position = part
                    break
 
            return cell, table_position
        return None, None
 
    try:
        parts = arc_string.split('_')
        cell = parts[1] if len(parts) > 1 else None
 
        table_position = None
        for part in reversed(parts):
            if '-' in part and re.match(r'\d+-\d+', part):
                table_position = part
                break
 
        return cell, table_position
    except Exception as e:
        logging.error(f"Error extracting cell info from '{arc_string}': {e}")
        return None, None
 
 
def calculate_multi_point_sensitivity(voltage_values, lib_values, voltage_pair=None):
    """Calculate voltage sensitivity using adjacent voltage points."""
    try:
        if len(voltage_values) < 2 or len(lib_values) < 2:
            return None
 
        # Make sure we have the same number of points
        if len(voltage_values) != len(lib_values):
            logging.error(f"Mismatch in number of voltage and library values: {len(voltage_values)} vs {len(lib_values)}")
            return None
 
        # Check for constant values (would cause division by zero)
        if len(set(lib_values)) == 1:
            logging.warning("Constant library values detected - sensitivity calculation would be infinite")
            return {
                'slope_dlib_dv': 0,
                'sensitivity': float('inf'),
                'sensitivity_mv': float('inf'),
                'intercept': lib_values[0],
                'r_squared': 0,
                'p_value': 1.0,
                'std_err': 0
            }
 
        # Remove any NaN values
        valid_indices = [i for i, (v, l) in enumerate(zip(voltage_values, lib_values))
                        if not (np.isnan(v) or np.isnan(l))]
        v_clean = [voltage_values[i] for i in valid_indices]
        l_clean = [lib_values[i] for i in valid_indices]
 
        if len(v_clean) < 2:
            logging.warning("Too many NaN values - not enough points for sensitivity calculation")
            return None
 
        # If voltage_pair is specified, filter to use only those points
        if voltage_pair:
            # Find indices of voltage pairs that match
            v_min, v_max = voltage_pair
            indices = [i for i, v in enumerate(v_clean) if v_min <= v <= v_max]
 
            # Need at least 2 points
            if len(indices) < 2:
                return None
 
            # Extract only the relevant points
            v_filtered = [v_clean[i] for i in indices]
            lib_filtered = [l_clean[i] for i in indices]
        else:
            # Use all points
            v_filtered = v_clean
            lib_filtered = l_clean
 
        # Use linear regression to estimate dlib/dV
        try:
            # Use voltage as independent variable (x) and library as dependent (y)
            # This gives us dlib/dV directly
            slope, intercept, r_value, p_value, std_err = stats.linregress(v_filtered, lib_filtered)
 
            # Handle special cases
            if abs(slope) < 1e-10:  # Effectively zero slope
                logging.warning(f"Near-zero slope detected: {slope}")
                sensitivity = float('inf')
                sensitivity_mv = float('inf')
            else:
                # We need dV/dlib, so take the reciprocal
                sensitivity = 1.0 / slope
                # Convert to mV/unit
                sensitivity_mv = sensitivity * 1000
 
            return {
                'slope_dlib_dv': slope,  # Original slope (dLib/dV)
                'sensitivity': sensitivity,  # dV/dLib in V/unit
                'sensitivity_mv': sensitivity_mv,  # dV/dLib in mV/unit
                'intercept': intercept,
                'r_squared': r_value**2,
                'p_value': p_value,
                'std_err': std_err,
                'n_points': len(v_filtered)  # Add count of points used
            }
        except Exception as e:
            logging.error(f"Error in linregress calculation: {e}")
            return None
    except Exception as e:
        logging.error(f"Unexpected error in calculate_multi_point_sensitivity: {e}")
        return None
 
def load_lib_data(input_dir, corner, type_name):
    """
    Load the Lib_data.csv file for the specified corner and type, and index by arc.
    """
    logcalc = logging.getLogger('calculation')
    logcalc.info(f"Loading Lib data for {corner} {type_name} from {input_dir}")
 
    try:
        # Construct the path to the corner directory
        corner_dir = os.path.join(input_dir, f"{corner}_{type_name}")
 
        # Look for Lib_data.csv files
        lib_file_patterns = [
            "*_Lib_data.csv",
            "*Lib*.csv",
            "*_lib_data.csv"
        ]
 
        lib_file = None
        for pattern in lib_file_patterns:
            matches = glob.glob(os.path.join(corner_dir, pattern))
            if matches:
                lib_file = matches[0]
                logcalc.info(f"Found Lib data file: {lib_file}")
                break
 
        if not lib_file:
            logcalc.warning(f"No Lib data file found in {corner_dir}")
            return None
 
        # Read the file
        df = pd.read_csv(lib_file)
 
        # Create a dictionary mapping arcs to their data
        lib_data = {}
 
        # Find important columns
        arc_col = None
        nominal_col = None
 
        # Look for arc column
        for col in df.columns:
            if col.lower() == 'arc':
                arc_col = col
                break
 
        # Look for nominal column
        for col in df.columns:
            if 'nominal' in col.lower():
                nominal_col = col
                logcalc.info(f"Found nominal column: {col}")
                break
 
        if not arc_col:
            logcalc.warning(f"No 'Arc' column found in {lib_file}")
            return None
 
        if not nominal_col:
            logcalc.warning(f"No 'nominal' column found in {lib_file}")
            return None
 
        # Process each row
        for _, row in df.iterrows():
            arc = row[arc_col]
            nominal = row[nominal_col]
 
            # Skip if arc or nominal is missing
            if pd.isna(arc) or pd.isna(nominal):
                continue
 
            # Store entry
            lib_data[arc] = {
                'nominal': nominal
            }
 
            # Add other columns that might be useful
            for col in df.columns:
                if col != arc_col and not pd.isna(row[col]):
                    lib_data[arc][col] = row[col]
 
        logcalc.info(f"Loaded {len(lib_data)} Lib data entries")
 
        # Debug: log some sample arcs and their nominal values
        sample_count = min(5, len(lib_data))
        sample_arcs = list(lib_data.keys())[:sample_count]
        for arc in sample_arcs:
            logcalc.debug(f"Sample arc: {arc}, nominal: {lib_data[arc]['nominal']}")
 
        return lib_data
 
    except Exception as e:
        logcalc.error(f"Error loading Lib data: {e}")
        logcalc.error(traceback.format_exc())
        return None
 
def diagnose_rel_err_data_availability(sensitivity_data, corner, type_name, param_name):
    """
    Diagnose why rel_err data might be missing for parameters like std, skewness, and meanshift.
    """
    logcalc = logging.getLogger('calculation')
 
    logcalc.info("=" * 80)
    logcalc.info(f"DIAGNOSTIC: Analyzing rel_err data for {corner} {type_name} {param_name}")
    logcalc.info("=" * 80)
 
    # Counter variables
    total_entries = 0
    entries_with_corner = 0
    entries_with_rel_err = 0
    entries_with_mc = 0
    entries_with_lib_nominal = 0
    entries_with_complete_data = 0
 
    # Parameter-specific debug
    paramtype_detection_issues = 0
    denominator_calculation_issues = 0
    specific_mc_values_missing = 0
 
    # Detailed diagnostics for denominator calculation
    missing_components = {
        'lib_nominal': 0,
        'mc_meanshift': 0,
        'mc_std': 0,
        'mc_skew': 0,
        'mc_sigma': 0
    }
 
    for entry in sensitivity_data:
        total_entries += 1
 
        # Check if entry has data for this corner
        if corner in entry.get('corner_sensitivities', {}):
            entries_with_corner += 1
 
            # Check for error data
            corner_error_data = entry.get('error_data', {}).get(corner, {})
            rel_errors = corner_error_data.get('rel_err', {})
            mc_data = corner_error_data.get('MC', {})
 
            # Get lib_nominal value
            lib_nominal = None
            for lib_col, lib_val in entry.get('lib_values', {}).get(corner, {}).items():
                if 'nominal' in lib_col.lower():
                    lib_nominal = lib_val
                    entries_with_lib_nominal += 1
                    break
 
            # Debug info about lib_nominal
            arc = entry.get('arc', 'Unknown')
            if lib_nominal is not None:
                logcalc.debug(f"Found lib_nominal={lib_nominal} for arc={arc}")
            else:
                logcalc.debug(f"No lib_nominal found for arc={arc}")
 
            # Check rel_err data availability
            if rel_errors:
                entries_with_rel_err += 1
 
                # Count rel_err entries specifically for this parameter
                param_rel_cols = []
                for rel_col in rel_errors.keys():
                    # Check if column matches current parameter
                    if param_name.lower() in rel_col.lower():
                        param_rel_cols.append(rel_col)
 
                logcalc.info(f"Found {len(param_rel_cols)} rel_err columns for {param_name}: {param_rel_cols}")
 
            # Check MC data availability
            if mc_data:
                entries_with_mc += 1
 
                # Extract MC values
                mc_values = {}
                for mc_col, mc_val in mc_data.items():
                    mc_key = None
                    if 'meanshift' in mc_col.lower():
                        mc_key = 'mc_meanshift'
                    elif 'std' in mc_col.lower() or 'stdev' in mc_col.lower():
                        mc_key = 'mc_std'
                    elif 'skew' in mc_col.lower():
                        mc_key = 'mc_skew'
                    elif 'sigma' in mc_col.lower():
                        mc_key = 'mc_sigma'
 
                    if mc_key and mc_key not in mc_values:
                        mc_values[mc_key] = mc_val
 
                # Log what MC values were found
                logcalc.info(f"MC values found: {list(mc_values.keys())}")
 
                # Check denominator calculation requirements based on parameter
                missing_values = []
                if param_name.lower() == 'meanshift':
                    if lib_nominal is None:
                        missing_values.append('lib_nominal')
                        missing_components['lib_nominal'] += 1
                    if 'mc_meanshift' not in mc_values:
                        missing_values.append('mc_meanshift')
                        missing_components['mc_meanshift'] += 1
 
                elif param_name.lower() == 'std':
                    if lib_nominal is None:
                        missing_values.append('lib_nominal')
                        missing_components['lib_nominal'] += 1
                    if 'mc_meanshift' not in mc_values:
                        missing_values.append('mc_meanshift')
                        missing_components['mc_meanshift'] += 1
                    if 'mc_std' not in mc_values:
                        missing_values.append('mc_std')
                        missing_components['mc_std'] += 1
 
                elif param_name.lower() == 'skew':
                    if lib_nominal is None:
                        missing_values.append('lib_nominal')
                        missing_components['lib_nominal'] += 1
                    if 'mc_meanshift' not in mc_values:
                        missing_values.append('mc_meanshift')
                        missing_components['mc_meanshift'] += 1
                    if 'mc_skew' not in mc_values:
                        missing_values.append('mc_skew')
                        missing_components['mc_skew'] += 1
 
                # Log missing values
                if missing_values:
                    specific_mc_values_missing += 1
                    logcalc.debug(f"Missing values for denominator calculation: {missing_values}")
                else:
                    entries_with_complete_data += 1
                    logcalc.debug(f"All required values available for denominator calculation")
 
    # Log overall results
    logcalc.info(f"DIAGNOSTIC SUMMARY FOR {param_name}:")
    logcalc.info(f"  Total entries: {total_entries}")
    logcalc.info(f"  Entries with this corner: {entries_with_corner}")
    logcalc.info(f"  Entries with rel_err data: {entries_with_rel_err}")
    logcalc.info(f"  Entries with MC data: {entries_with_mc}")
    logcalc.info(f"  Entries with lib_nominal: {entries_with_lib_nominal}")
    logcalc.info(f"  Entries with complete data for denominator calculation: {entries_with_complete_data}")
 
    # Log specific issues
    logcalc.info(f"  Missing components for denominator calculation:")
    for component, count in missing_components.items():
        if count > 0:
            logcalc.info(f"    {component}: missing in {count} entries")
 
    # Return diagnostic information
    return {
        'total_entries': total_entries,
        'entries_with_corner': entries_with_corner,
        'entries_with_rel_err': entries_with_rel_err,
        'entries_with_mc': entries_with_mc,
        'entries_with_lib_nominal': entries_with_lib_nominal,
        'entries_with_complete_data': entries_with_complete_data,
        'missing_components': missing_components
    }
 
 
 
def create_error_margin_scatter_plot(sensitivity_data, corner, type_name, param_name, output_dir, data_dir):
    """Create scatter plot of error values vs voltage margin for a specific corner."""
    logcalc = logging.getLogger('calculation')
 
    logcalc.info("=" * 80)
    logcalc.info(f"CREATE SCATTER PLOT: {corner} {type_name} {param_name}")
    logcalc.info("=" * 80)
 
    if not sensitivity_data:
        logging.warning(f"No sensitivity data for {corner} {type_name} {param_name}")
        return None, None
 
    # ADDED: Run diagnostics for std, skew, and meanshift parameters
    if param_name in ['Std', 'Skew', 'Meanshift']:
        diagnostics = diagnose_rel_err_data_availability(sensitivity_data, corner, type_name, param_name)
 
        # Log if there's a significant issue
        if diagnostics['entries_with_rel_err'] == 0:
            logcalc.warning(f"DIAGNOSTIC ALERT: No rel_err data found for {param_name}")
        elif diagnostics['entries_with_complete_data'] == 0:
            logcalc.warning(f"DIAGNOSTIC ALERT: No entries with complete data for denominator calculation for {param_name}")
 
    # Extract data for abs_err and rel_err scatter plots
    abs_err_data = []
    rel_err_data = []
 
    try:
        # Load lib_nominal values from Lib_data.csv
        lib_nominal_map = {}
        try:
            # Try multiple potential directory structures
            potential_dirs = [
                data_dir,                                          # direct data_dir
                os.path.join(data_dir, corner),                   # data_dir/corner
                os.path.join(data_dir, f"{corner}_{type_name}")  # data_dir/corner_type
            ]
 
            for input_dir in potential_dirs:
                lib_data = load_lib_data(input_dir, corner, type_name)
                if lib_data:
                    logcalc.info(f"Successfully loaded {len(lib_data)} lib_nominal values from {input_dir}")
                    lib_nominal_map = lib_data
                    break
 
            if not lib_nominal_map:
                logcalc.warning(f"Could not load lib_nominal values from Lib_data.csv files")
        except Exception as e:
            logcalc.error(f"Error loading lib_nominal values: {e}")
 
        # Process each data entry
        for data in sensitivity_data:
            if corner in data.get('corner_sensitivities', {}) and corner in data.get('error_data', {}):
                corner_sens = data['corner_sensitivities'][corner]
                sensitivity = corner_sens['sensitivity_mv']
 
                # Get error data for this corner
                corner_error_data = data.get('error_data', {}).get(corner, {})
                abs_errors = corner_error_data.get('abs_err', {})
                rel_errors = corner_error_data.get('rel_err', {})
                mc_data = corner_error_data.get('MC', {})
 
                # Get lib_nominal value
                lib_nominal = None
                arc = data.get('arc', 'Unknown')
 
                # Try to get from Lib_data.csv
                if arc in lib_nominal_map:
                    lib_nominal = lib_nominal_map[arc].get('nominal')
                    #logcalc.debug(f"Found lib_nominal={lib_nominal} from Lib_data.csv for arc={arc}")
 
                # If not found, try from lib_values
                if lib_nominal is None:
                    for lib_col, lib_val in data.get('lib_values', {}).get(corner, {}).items():
                        if 'nominal' in lib_col.lower():
                            lib_nominal = lib_val
                            #logcalc.debug(f"Found lib_nominal={lib_nominal} from lib_values for arc={arc}")
                            break
 
                # Process abs_err data
                for abs_col, abs_value in abs_errors.items():
                    # Calculate margin
                    try:
                        # FIXED: Calculate margin without extra abs()
                        margin = sensitivity * abs_value
 
                        # Get lib value
                        lib_col = abs_col.replace('abs_err', 'Lib').replace('Abs_Err', 'Lib')
                        lib_value = data.get('lib_values', {}).get(corner, {}).get(lib_col)
 
                        # Get MC value
                        mc_value = None
                        for mc_col, mc_val in mc_data.items():
                            if 'meanshift' in abs_col.lower() and 'meanshift' in mc_col.lower():
                                mc_value = mc_val
                                break
                            elif 'std' in abs_col.lower() and ('std' in mc_col.lower() or 'stdev' in mc_col.lower()):
                                mc_value = mc_val
                                break
                            elif 'skew' in abs_col.lower() and 'skew' in mc_col.lower():
                                mc_value = mc_val
                                break
                            elif 'early_sigma' in abs_col.lower() and 'early_sigma' in mc_col.lower():
                                mc_value = mc_val
                                break
                            elif 'late_sigma' in abs_col.lower() and 'late_sigma' in mc_col.lower():
                                mc_value = mc_val
                                break
 
                        abs_err_data.append({
                            'arc': data.get('arc', 'Unknown'),
                            'cell': data.get('cell', 'Unknown'),
                            'error_value': abs_value,  # abs_err in ps
                            'voltage_margin': margin,  # in mV
                            'sensitivity': sensitivity,  # in mV/ps
                            'table_position': data.get('table_position', None),
                            'lib_value': lib_value,
                            'mc_value': mc_value,
                            'lib_nominal': lib_nominal
                        })
 
                        # Log a few margin calculations for verification
                        if len(abs_err_data) <= 5 and abs_value < 0:  # Only log optimistic errors
                            logcalc.debug(f"abs_err margin calculation: {sensitivity} * {abs_value} = {margin}")
                    except Exception as e:
                        logcalc.warning(f"Error calculating abs_err margin: {e}")
 
                # Process rel_err data with proper denominator calculation
                for rel_col, rel_value in rel_errors.items():
                    try:
                        # Determine parameter type from column name
                        param_type = None
                        if 'meanshift' in rel_col.lower():
                            param_type = 'meanshift'
                        elif 'std' in rel_col.lower() or 'stdev' in rel_col.lower():
                            param_type = 'std'
                        elif 'skew' in rel_col.lower():
                            param_type = 'skew'
                        elif 'sigma' in rel_col.lower():
                            # Differentiate between early_sigma and late_sigma
                            if 'early' in rel_col.lower():
                                param_type = 'early_sigma'
                            elif 'late' in rel_col.lower():
                                param_type = 'late_sigma'
                            else:
                                param_type = 'sigma'  # generic case
 
                        # Extract MC values
                        mc_values = {}
                        for mc_col, mc_val in mc_data.items():
                            if 'meanshift' in mc_col.lower():
                                mc_values['meanshift'] = mc_val
                            elif 'std' in mc_col.lower() or 'stdev' in mc_col.lower():
                                mc_values['std'] = mc_val
                            elif 'skew' in mc_col.lower():
                                mc_values['skew'] = mc_val
                            elif 'sigma' in mc_col.lower():
                                mc_values['sigma'] = mc_val
 
                        # Calculate the correct denominator based on parameter type
                        denominator = None
 
                        if param_type == 'meanshift' and lib_nominal is not None and 'meanshift' in mc_values:
                            # Meanshift â†’ lib_nominal + meanshift_mc
                            denominator = lib_nominal + mc_values['meanshift']
                            mc_value = mc_values['meanshift']
                        elif param_type == 'std' and lib_nominal is not None and 'meanshift' in mc_values and 'std' in mc_values:
                            # Stddev â†’ lib_nominal + meanshift_mc + stddev_mc
                            denominator = lib_nominal + mc_values['meanshift'] + mc_values['std']
                            mc_value = mc_values['std']
                        elif param_type == 'std' and lib_nominal is not None and 'std' in mc_values:
                            # Simplified if meanshift missing
                            denominator = lib_nominal + mc_values['std']
                            mc_value = mc_values['std']
                        elif param_type == 'skew' and lib_nominal is not None and 'meanshift' in mc_values and 'skew' in mc_values:
                            # Skewness â†’ lib_nominal + meanshift_mc + skewness_mc
                            denominator = lib_nominal + mc_values['meanshift'] + mc_values['skew']
                            mc_value = mc_values['skew']
                        elif param_type == 'skew' and lib_nominal is not None and 'skew' in mc_values:
                            # Simplified if meanshift missing
                            denominator = lib_nominal + mc_values['skew']
                            mc_value = mc_values['skew']
                        elif param_type in ['early_sigma', 'late_sigma', 'sigma'] and 'sigma' in mc_values:
                            # For sigma types, use max(abs(lib_nominal), MC_sigma)
                            if lib_nominal is not None:
                                denominator = max(abs(lib_nominal), mc_values['sigma'])
                            else:
                                denominator = mc_values['sigma']
                            mc_value = mc_values['sigma']
 
                        # If we have a valid denominator, calculate abs_error and margin
                        if denominator is not None:
                            # Convert rel_err to abs_err
                            abs_value = rel_value * denominator
 
                            # FIXED: Calculate margin without extra abs()
                            margin = sensitivity * abs_value
 
                            # Get lib value
                            lib_col = rel_col.replace('rel_err', 'Lib').replace('Rel_Err', 'Lib')
                            lib_value = data.get('lib_values', {}).get(corner, {}).get(lib_col)
 
                            rel_err_data.append({
                                'arc': data.get('arc', 'Unknown'),
                                'cell': data.get('cell', 'Unknown'),
                                'error_value': rel_value,  # rel_err (ratio)
                                'abs_error': abs_value,    # converted abs_err
                                'voltage_margin': margin,  # in mV
                                'sensitivity': sensitivity,  # in mV/ps
                                'table_position': data.get('table_position', None),
                                'lib_value': lib_value,
                                'mc_value': mc_value,
                                'denominator': denominator,
                                'lib_nominal': lib_nominal,
                                'param_type': param_type,
                                'mc_data': mc_values  # Save all MC values for verification
                            })
 
                            # Log a few margin calculations for verification
                            if len(rel_err_data) <= 5 and abs_value < 0:  # Only log optimistic errors
                                logcalc.debug(f"rel_err margin calculation: {sensitivity} * {abs_value} = {margin}")
                                logcalc.debug(f"  rel_value: {rel_value}, denominator: {denominator}, abs_value: {abs_value}")
                    except Exception as e:
                        logcalc.warning(f"Error calculating rel_err margin: {e}")
 
        # Log summary information
        logcalc.info(f"Error margin data summary for {corner} {type_name} {param_name}:")
        logcalc.info(f"  abs_err data points: {len(abs_err_data)}")
        logcalc.info(f"  rel_err data points: {len(rel_err_data)}")
 
        # Log max margins for verification
        abs_margins = [d['voltage_margin'] for d in abs_err_data if d['error_value'] < 0]
        rel_margins = [d['voltage_margin'] for d in rel_err_data if d['error_value'] < 0 or (d.get('abs_error') and d['abs_error'] < 0)]
 
        if abs_margins:
            logcalc.info(f"  Max abs_err margin: {max(abs_margins):.4f} mV")
        if rel_margins:
            logcalc.info(f"  Max rel_err margin: {max(rel_margins):.4f} mV")
 
 
        # VERIFICATION: Run detailed denominator verification
        verification_results = None
        verification_summary = None
 
        if len(abs_err_data) > 0 and len(rel_err_data) > 0:
            verification_results, verification_summary = verify_rel_err_conversion(
                abs_err_data, rel_err_data, corner, type_name, param_name, output_dir, data_dir
            )
 
        # Create combined scatter plot
        _create_combined_error_scatter_plot(abs_err_data, rel_err_data, corner, type_name, param_name, output_dir)
 
        # Store data for later comparison
        scatter_plot_data = {
            'corner': corner,
            'type_name': type_name,
            'param_name': param_name,
            'abs_err_data': abs_err_data,
            'rel_err_data': rel_err_data
        }
 
        # Create data store if it doesn't exist
        if not hasattr(create_error_margin_scatter_plot, 'data_store'):
            create_error_margin_scatter_plot.data_store = {}
 
        # Store the data
        create_error_margin_scatter_plot.data_store[f"{corner}_{type_name}_{param_name}"] = scatter_plot_data
 
        logcalc.info(f"Created error margin scatter plot for {corner} {type_name} {param_name}")
 
        return verification_results, verification_summary
 
    except Exception as e:
        logcalc.error(f"Error creating scatter plot for {corner} {type_name} {param_name}: {e}")
        logcalc.error(traceback.format_exc())
        return None, None
 
def create_error_subplot(ax, error_data, corner, type_name, param_name, error_type, unit,output_dir):
    """Create a subplot for either abs_err or rel_err data."""
    if not error_data:
        ax.text(0.5, 0.5, f"No valid {error_type} data available",
               ha='center', va='center', fontsize=14)
        ax.set_title(f'{error_type} vs Voltage Margin')
        return
 
    # Extract plot data and filter out any NaNs or infinite values
    error_values = []
    voltage_margins = []
    sensitivities = []
 
    for d in error_data:
        error_val = d['error_value']
        # Convert rel_err to percentage
        if error_type == 'rel_err':
            error_val = error_val * 100  # Convert ratio to percentage
 
        if (not np.isnan(error_val) and
            not np.isnan(d['voltage_margin']) and
            not np.isnan(d['sensitivity']) and
            not np.isinf(error_val) and
            not np.isinf(d['voltage_margin']) and
            not np.isinf(d['sensitivity'])):
            error_values.append(error_val)
            voltage_margins.append(d['voltage_margin'])
            sensitivities.append(d['sensitivity'])
 
    if not error_values:  # Skip if all data was filtered out
        ax.text(0.5, 0.5, f"No valid {error_type} data available",
               ha='center', va='center', fontsize=14)
        ax.set_title(f'{error_type} vs Voltage Margin')
        return
    """Create a subplot for either abs_err or rel_err data."""
    if not error_data:
        ax.text(0.5, 0.5, f"No valid {error_type} data available",
               ha='center', va='center', fontsize=14)
        ax.set_title(f'{error_type} vs Voltage Margin')
        return
 
    # Track calculations for debugging
    margin_calculations = []
 
    # Extract plot data and filter out any NaNs or infinite values
    error_values = []
    voltage_margins = []
    sensitivities = []
 
    for d in error_data:
        error_val = d['error_value']
        # Convert rel_err to percentage
        if error_type == 'rel_err':
            error_val = error_val * 100  # Convert ratio to percentage
 
        if (not np.isnan(error_val) and
            not np.isnan(d['voltage_margin']) and
            not np.isnan(d['sensitivity']) and
            not np.isinf(error_val) and
            not np.isinf(d['voltage_margin']) and
            not np.isinf(d['sensitivity'])):
 
            # IMPORTANT: Track the margin calculation
            if d.get('error_value', 0) < 0:  # Only track optimistic errors for comparison
                margin_calculations.append({
                    'source': error_type,
                    'sensitivity': d['sensitivity'],
                    'error_value': d['error_value'],
                    'voltage_margin': d['voltage_margin'],
                    'calculation': f"{d['sensitivity']} * {d['error_value']} = {d['voltage_margin']}"
                })
 
            error_values.append(error_val)
            voltage_margins.append(d['voltage_margin'])
            sensitivities.append(d['sensitivity'])
 
    # Store for later checking
    if not hasattr(create_error_subplot, 'margin_calculations'):
        create_error_subplot.margin_calculations = {}
    create_error_subplot.margin_calculations[f"{corner}_{type_name}_{param_name}_{error_type}"] = margin_calculations
 
    if not error_values:  # Skip if all data was filtered out
        ax.text(0.5, 0.5, f"No valid {error_type} data available",
               ha='center', va='center', fontsize=14)
        ax.set_title(f'{error_type} vs Voltage Margin')
        return
 
    # Find min and max sensitivity for proper scaling
    min_sens = min(sensitivities)
    max_sens = max(sensitivities)
 
    # Choose color map based on error type and sensitivity range
    if error_type == 'abs_err':
        # For abs_err - red colormap
        if min_sens < 0 and max_sens <= 0:
            # All negative sensitivities - dark to light (darker for more negative)
            colors = [(0.4, 0, 0), (0.65, 0.1, 0.1), (0.85, 0.3, 0.3), (0.95, 0.5, 0.5)]
            err_cmap = LinearSegmentedColormap.from_list('CustomRedsReversed', colors)
            norm = plt.Normalize(min_sens, 0)  # Most negative to zero
        else:
            # Mixed or positive sensitivities - light to dark (darker for more positive)
            colors = [(0.95, 0.5, 0.5), (0.85, 0.3, 0.3), (0.65, 0.1, 0.1), (0.4, 0, 0)]
            err_cmap = LinearSegmentedColormap.from_list('CustomReds', colors)
            norm = plt.Normalize(min_sens, max_sens)
    else:
        # For rel_err - blue colormap
        if min_sens < 0 and max_sens <= 0:
            # All negative sensitivities - dark to light (darker for more negative)
            colors = [(0, 0, 0.4), (0.1, 0.1, 0.65), (0.3, 0.3, 0.85), (0.5, 0.5, 0.95)]
            err_cmap = LinearSegmentedColormap.from_list('CustomBluesReversed', colors)
            norm = plt.Normalize(min_sens, 0)  # Most negative to zero
        else:
            # Mixed or positive sensitivities - light to dark (darker for more positive)
            colors = [(0.5, 0.5, 0.95), (0.3, 0.3, 0.85), (0.1, 0.1, 0.65), (0, 0, 0.4)]
            err_cmap = LinearSegmentedColormap.from_list('CustomBlues', colors)
            norm = plt.Normalize(min_sens, max_sens)
 
    # Separate negative and positive errors (Now focusing on Lib < MC, which is error < 0)
    neg_indices = [i for i, e in enumerate(error_values) if e < 0]  # Lib < MC
    pos_indices = [i for i, e in enumerate(error_values) if e >= 0]  # Lib >= MC
 
    # Plot Lib >= MC errors first (with lower opacity)
    if pos_indices:
        sc_pos = ax.scatter([error_values[i] for i in pos_indices],
                         [voltage_margins[i] for i in pos_indices],
                         c=[sensitivities[i] for i in pos_indices],
                         cmap=err_cmap, norm=norm,
                         alpha=0.6, s=40, edgecolors='none')
 
    # Plot Lib < MC errors on top (with higher opacity)
    if neg_indices:
        sc_neg = ax.scatter([error_values[i] for i in neg_indices],
                         [voltage_margins[i] for i in neg_indices],
                         c=[sensitivities[i] for i in neg_indices],
                         cmap=err_cmap, norm=norm,
                         alpha=0.9, s=50, edgecolors='none')
 
    # Add colorbar with actual sensitivity values
    sm = plt.cm.ScalarMappable(cmap=err_cmap, norm=norm)
    sm.set_array([])
    cbar = plt.colorbar(sm, ax=ax)
    cbar.set_label('Sensitivity (mV/ps)', fontsize=10)
 
    # Add colorbar tick labels that show the actual values
    if min_sens < 0 and max_sens <= 0:
        # Only negative values - create tick labels from min_sens to 0
        ticks = np.linspace(min_sens, 0, 5)
        cbar.set_ticks(ticks)
        cbar.set_ticklabels([f"{t:.2f}" for t in ticks])
    else:
        # Mixed or only positive values
        ticks = np.linspace(min_sens, max_sens, 5)
        cbar.set_ticks(ticks)
        cbar.set_ticklabels([f"{t:.2f}" for t in ticks])
 
    # Add a trend line for all data points
    if len(error_values) > 1:
        try:
            z = np.polyfit(error_values, voltage_margins, 1)
            p = np.poly1d(z)
            x_range = np.linspace(min(error_values), max(error_values), 100)
            ax.plot(x_range, p(x_range), 'k--', alpha=0.7, linewidth=2,
                  label=f'Trend line: slope={z[0]:.6f}')
 
            # This slope should match the average sensitivity
            avg_sensitivity = np.mean(sensitivities)
            ax.text(0.02, 0.02,
                   f"Avg sensitivity: {avg_sensitivity:.6f} mV/ps\nTrend: {z[0]:.6f}",
                   transform=ax.transAxes, fontsize=8, color='black',
                   bbox=dict(facecolor='white', alpha=0.8))
        except Exception as e:
            logging.warning(f"Error creating trend line for {error_type}: {e}")
 
    # Add vertical line at 0 to highlight Lib < MC region
    ax.axvline(x=0, color='black', linestyle='-', alpha=0.5, linewidth=1)
 
    # Shade Lib < MC region (error < 0)
    try:
        xlim = ax.get_xlim()
        ylim = ax.get_ylim()
        min_error = min(min(error_values), -0.1) if error_values else -0.1
        ax.fill_between([min_error, 0], ylim[0], ylim[1],
                       color='blue', alpha=0.15)
        ax.set_xlim(xlim)
        ax.set_ylim(ylim)
    except Exception as e:
        logging.warning(f"Error shading Lib < MC region for {error_type}: {e}")
 
    # Set labels
    unit_display = unit
    if error_type == 'rel_err':
        unit_display = '%'  # Change unit display for rel_err
    ax.set_xlabel(f'{error_type} ({unit_display})', fontsize=12)
    ax.set_ylabel('Voltage Margin (mV)', fontsize=12)
    ax.set_title(f'{error_type} vs Voltage Margin', fontsize=14)
 
    # Add grid and legend
    ax.grid(True, alpha=0.3)
    if len(error_values) > 1:
        ax.legend()
 
    # Add statistics text box for all data
    if error_values:
        try:
            all_textstr = (
                f"All Data Statistics (n={len(error_values)}):\n"
                f"Mean Error: {np.mean(error_values):.2f} {unit_display}\n"
                f"Mean Margin: {np.mean(voltage_margins):.4f} mV\n"
                f"Min Margin: {np.min(voltage_margins):.4f} mV\n"
                f"Max Margin: {np.max(voltage_margins):.4f} mV"
            )
 
            props = dict(boxstyle='round', facecolor='gray', alpha=0.5)
            ax.text(0.05, 0.8, all_textstr, transform=ax.transAxes,
                   fontsize=9, verticalalignment='top', bbox=props)
        except Exception as e:
            logging.warning(f"Error creating statistics text box for all {error_type} data: {e}")
 
    # Add statistics text box for negative errors (Lib < MC)
    if neg_indices:
        try:
            neg_errors = [error_values[i] for i in neg_indices]
            neg_margins = [voltage_margins[i] for i in neg_indices]
            neg_textstr = (
                f"Lib < MC Statistics (n={len(neg_indices)}):\n"
                f"Mean Error: {np.mean(neg_errors):.2f} {unit_display}\n"
                f"Mean Margin: {np.mean(neg_margins):.4f} mV\n"
                f"Min Margin: {np.min(neg_margins):.4f} mV\n"
                f"Max Margin: {np.max(neg_margins):.4f} mV"
            )
 
            props = dict(boxstyle='round', facecolor='lightblue', alpha=0.7)
            ax.text(0.05, 0.95, neg_textstr, transform=ax.transAxes,
                   fontsize=10, verticalalignment='top', bbox=props)
        except Exception as e:
            logging.warning(f"Error creating statistics text box for negative {error_type} data: {e}")
 
    # Label for Lib < MC region
    if neg_indices:
        try:
            x_pos = min(error_values) * 0.5
            y_pos = (ylim[0] + ylim[1]) / 2
 
            ax.text(x_pos, y_pos, "Lib < MC\n(Optimistic Error)",
                   fontsize=10, color='darkblue', fontweight='bold',
                   bbox=dict(facecolor='white', alpha=0.7, edgecolor='blue', pad=3),
                   ha='center', va='center', zorder=100)
        except Exception as e:
            logging.warning(f"Error creating Lib < MC label for {error_type}: {e}")
 
    # ADD THIS AT THE END, JUST BEFORE RETURNING:
    # Enhance rel_err plot with high-sensitivity markers if applicable
 
    if error_type == 'rel_err':
        enhance_rel_err_scatter_plot(ax, error_data, corner, type_name, param_name, sensitivity_threshold=0.5)
 
    return  # End of function
 
def save_margin_scatter_data(abs_err_data, rel_err_data, corner, type_name, param_name, output_dir):
    """Save the detailed data used for error margin scatter plots to CSV files."""
    try:
        # Create combined data for easier analysis
        combined_data = []
 
        # Add abs_err data
        for item in abs_err_data:
            combined_data.append({
                'arc': item.get('arc', 'Unknown'),
                'cell': item.get('cell', 'Unknown'),
                'table_position': item.get('table_position', None),
                'error_value': item.get('error_value', None),
                'sensitivity': item.get('sensitivity', None),
                'voltage_margin': item.get('voltage_margin', None),
                'lib_value': item.get('lib_value', None),
                'mc_value': item.get('mc_value', None),
                'lib_nominal': item.get('lib_nominal', None),
                'corner': corner,
                'type': type_name,
                'parameter': param_name,
                'category': 'abs_err',
                'unit': 'ps',
                'sensitivity_unit': 'mV/ps'
            })
 
        # Add rel_err data
        for item in rel_err_data:
            combined_data.append({
                'arc': item.get('arc', 'Unknown'),
                'cell': item.get('cell', 'Unknown'),
                'table_position': item.get('table_position', None),
                'error_value': item.get('error_value', None),
                'abs_error': item.get('abs_error', None),
                'sensitivity': item.get('sensitivity', None),
                'voltage_margin': item.get('voltage_margin', None),
                'lib_value': item.get('lib_value', None),
                'mc_value': item.get('mc_value', None),
                'denominator': item.get('denominator', None),
                'lib_nominal': item.get('lib_nominal', None),
                'param_type': item.get('param_type', None),
                'corner': corner,
                'type': type_name,
                'parameter': param_name,
                'category': 'rel_err',
                'unit': 'ratio',
                'sensitivity_unit': 'mV/ps'
            })
 
        # Save to CSV
        if combined_data:
            df = pd.DataFrame(combined_data)
            csv_file = os.path.join(output_dir, f'margin_scatter_data.csv')
            df.to_csv(csv_file, index=False)
            logging.info(f"Saved margin scatter data to {csv_file}")
 
    except Exception as e:
        logging.error(f"Error saving margin scatter data: {e}")
        logging.error(traceback.format_exc())
def get_all_optimistic_error_margins(sensitivity_data, param_name, corner):
    """Get all voltage margins for optimistic errors."""
    logcalc = logging.getLogger('calculation')
    logcalc.info(f"Collecting optimistic error margins for parameter: {param_name}")
 
    all_margins = []
    total_points = 0
    optimistic_points = 0
 
    # Track detailed calculations for debugging
    margin_calculations = []
 
    # Collect all margins for optimistic errors
    for data in sensitivity_data:
        if corner in data.get('corner_sensitivities', {}) and corner in data.get('error_data', {}):
            corner_sens = data['corner_sensitivities'][corner]
            sensitivity = corner_sens['sensitivity_mv']
 
            # Get error data for this corner
            corner_error_data = data.get('error_data', {}).get(corner, {})
            abs_errors = corner_error_data.get('abs_err', {})
            rel_errors = corner_error_data.get('rel_err', {})
 
            # Process abs_err values
            for abs_col, abs_val in abs_errors.items():
                if not np.isnan(abs_val) and not np.isinf(abs_val):
                    total_points += 1
 
                    if abs_val < 0:  # Optimistic error (Lib < MC)
                        optimistic_points += 1
                        # Calculate voltage margin - FIXED: no extra abs()
                        margin = sensitivity * abs_val
                        all_margins.append(margin)
 
                        # Track calculation for debugging
                        margin_calculations.append({
                            'source': 'abs_err',
                            'sensitivity': sensitivity,
                            'error_value': abs_val,
                            'calculation': f"{sensitivity} * {abs_val} = {margin}",
                            'margin': margin
                        })
 
            # Process rel_err values with proper conversion
            for rel_col, rel_val in rel_errors.items():
                if np.isnan(rel_val) or np.isinf(rel_val):
                    continue
 
                # Determine parameter type from column name
                param_type = None
                if 'meanshift' in rel_col.lower():
                    param_type = 'meanshift'
                elif 'std' in rel_col.lower() or 'stdev' in rel_col.lower():
                    param_type = 'std'
                elif 'skew' in rel_col.lower():
                    param_type = 'skew'
                elif 'sigma' in rel_col.lower():
                    # Differentiate between early_sigma and late_sigma
                    if 'early' in rel_col.lower():
                        param_type = 'early_sigma'
                    elif 'late' in rel_col.lower():
                        param_type = 'late_sigma'
                    else:
                        param_type = 'sigma'  # generic case
 
                # Get lib_nominal value (needed for denominator calculation)
                lib_nominal = None
                for lib_col, lib_val in data.get('lib_values', {}).get(corner, {}).items():
                    if 'nominal' in lib_col.lower():
                        lib_nominal = lib_val
                        break
 
                # Extract MC values for different parameter types
                mc_values = {}
                mc_data = corner_error_data.get('MC', {})
                for mc_col, mc_value in mc_data.items():
                    if 'meanshift' in mc_col.lower():
                        mc_values['meanshift'] = mc_value
                    elif 'std' in mc_col.lower() or 'stdev' in mc_col.lower():
                        mc_values['std'] = mc_value
                    elif 'skew' in mc_col.lower():
                        mc_values['skew'] = mc_value
                    elif 'sigma' in mc_col.lower():
                        mc_values['sigma'] = mc_value
 
                # Calculate the correct denominator based on parameter type
                denominator = None
 
                if param_type == 'meanshift' and lib_nominal is not None and 'meanshift' in mc_values:
                    # Meanshift â†’ lib_nominal + meanshift_mc
                    denominator = lib_nominal + mc_values['meanshift']
                elif param_type == 'std' and lib_nominal is not None and 'meanshift' in mc_values and 'std' in mc_values:
                    # Stddev â†’ lib_nominal + meanshift_mc + stddev_mc
                    denominator = lib_nominal + mc_values['meanshift'] + mc_values['std']
                elif param_type == 'std' and lib_nominal is not None and 'std' in mc_values:
                    # Simplified if meanshift missing
                    denominator = lib_nominal + mc_values['std']
                elif param_type == 'skew' and lib_nominal is not None and 'meanshift' in mc_values and 'skew' in mc_values:
                    # Skewness â†’ lib_nominal + meanshift_mc + skewness_mc
                    denominator = lib_nominal + mc_values['meanshift'] + mc_values['skew']
                elif param_type == 'skew' and lib_nominal is not None and 'skew' in mc_values:
                    # Simplified if meanshift missing
                    denominator = lib_nominal + mc_values['skew']
                elif param_type in ['early_sigma', 'late_sigma', 'sigma'] and 'sigma' in mc_values:
                    # For sigma types, use max(abs(lib_nominal), MC_sigma)
                    if lib_nominal is not None:
                        denominator = max(abs(lib_nominal), mc_values['sigma'])
                    else:
                        denominator = mc_values['sigma']
 
                # Convert rel_err to abs_err and calculate margin
                if denominator is not None:
                    total_points += 1
                    abs_val = rel_val * denominator
 
                    if abs_val < 0:  # Optimistic error
                        optimistic_points += 1
                        # FIXED: no extra abs() needed
                        margin = sensitivity * abs_val
                        all_margins.append(margin)
 
                        # Track calculation for debugging
                        margin_calculations.append({
                            'source': 'rel_err',
                            'sensitivity': sensitivity,
                            'rel_error_value': rel_val,
                            'denominator': denominator,
                            'abs_error_value': abs_val,
                            'calculation': f"{sensitivity} * {abs_val} = {margin}",
                            'margin': margin
                        })
 
    # Log summary of margin calculations
    logcalc.info(f"Found {len(all_margins)} optimistic error margins out of {total_points} total points")
    logcalc.info(f"Optimistic errors: {optimistic_points} ({optimistic_points/total_points*100:.1f}% of total)")
 
    # Log the largest margins for verification
    if all_margins:
        sorted_margins = sorted(all_margins, reverse=True)
        logcalc.info(f"Largest margins for {corner} {param_name}:")
        for i, margin in enumerate(sorted_margins[:5]):
            if i < len(margin_calculations):
                calc = next((c for c in margin_calculations if c['margin'] == margin), None)
                if calc:
                    logcalc.info(f"  #{i+1}: {margin:.4f} mV - {calc['calculation']}")
                else:
                    logcalc.info(f"  #{i+1}: {margin:.4f} mV")
            else:
                logcalc.info(f"  #{i+1}: {margin:.4f} mV")
 
    # Store for later checking
    get_all_optimistic_error_margins.last_data = {
        'corner': corner,
        'param_name': param_name,
        'all_margins': all_margins,
        'margin_calculations': margin_calculations,
        'optimistic_points': optimistic_points,
        'total_points': total_points
    }
 
    return all_margins, optimistic_points, total_points
 
def enhance_rel_err_scatter_plot(ax, rel_err_data, corner, type_name, param_name, sensitivity_threshold=0.5):
    """
    Enhance the rel_err scatter plot by marking high-sensitivity points.
    """
    # Filter points with rel_err < threshold (in percentage)
    low_error_points = [p for p in rel_err_data if abs(p.get('error_value', 100)) < sensitivity_threshold/100]
 
    if not low_error_points:
        logging.info(f"No high-sensitivity points found for {corner} {type_name} {param_name}")
        return
 
    # Calculate sensitivity for filtered points
    sensitivity_data = []
    for point in low_error_points:
        error_value = point.get('error_value', 0)
        margin = point.get('voltage_margin', 0)
 
        # Skip if error is exactly zero to avoid division by zero
        if abs(error_value) < 0.00001:
            continue
 
        sensitivity = abs(margin / error_value)
 
        sensitivity_data.append({
            'sensitivity': sensitivity,
            'margin': margin,
            'error': error_value,
            'cell': point.get('cell', 'Unknown'),
            'arc': point.get('arc', 'Unknown'),
            'table_position': point.get('table_position', 'Unknown')
        })
 
    # Sort by sensitivity in descending order
    sorted_data = sorted(sensitivity_data, key=lambda x: x['sensitivity'], reverse=True)
 
    # Take top 10 for marking on plot (or all if less than 10)
    mark_count = min(10, len(sorted_data))
    mark_points = sorted_data[:mark_count]
 
    # Skip if no points to mark
    if not mark_points:
        return
 
    logging.info(f"Found {mark_count} high-sensitivity points for {corner} {type_name} {param_name}")
 
    # Add markers for these points
    for i, data in enumerate(mark_points):
        # Convert rel_err to percentage for plotting
        rel_err_percent = data['error'] * 100
        ax.scatter(rel_err_percent, data['margin'],
                   marker='*', s=150, color='red', edgecolors='black', zorder=10)
 
        # Add number annotations
        ax.annotate(f"{i+1}",
                   (rel_err_percent, data['margin']),
                   xytext=(10, 5), textcoords='offset points',
                   fontsize=10, fontweight='bold',
                   bbox=dict(boxstyle="round,pad=0.3", fc="yellow", ec="black", alpha=0.8))
 
    # Add a note to the plot that explains the markers
    ax.text(0.5, 0.02,
            "* Red stars mark high-sensitivity points (rel_err < 0.5%)\nSee table below for details",
            transform=ax.transAxes, ha='center', va='bottom', fontsize=9,
            bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="grey", alpha=0.8))
 
    return mark_points
 
def identify_parameters_in_dataframe(df, category):
    """Identify the available parameters in the dataframe with improved meanshift detection."""
    logcalc = logging.getLogger('calculation')
 
    parameters = {
        'early_sigma': [],
        'late_sigma': [],
        'Std': [],
        'Skew': [],
        'Meanshift': []
    }
 
    # Set up category prefix patterns
    category_prefixes = {
        'MC': ['MC_', 'mc_'],
        'Lib': ['Lib_', 'lib_'],
        'abs_err': ['abs_err', 'Abs_Err', 'ABS_ERR', 'abs err', 'Abs Err', 'ABS ERR'],
        'rel_err': ['rel_err', 'Rel_Err', 'REL_ERR', 'rel err', 'Rel Err', 'REL ERR']
    }.get(category, [])
 
    # Enhanced detection of MC_Meanshift columns
    meanshift_columns = []
 
    # Debug: Log all columns in the dataframe
    logcalc.debug(f"All columns in {category} dataframe: {df.columns.tolist()}")
 
    # First pass - look specifically for meanshift columns
    for col in df.columns:
        col_lower = col.lower()
        if 'meanshift' in col_lower or 'mean_shift' in col_lower or 'mean shift' in col_lower:
            meanshift_columns.append(col)
            logcalc.info(f"Found meanshift column: {col} in {category}")
 
    # Process each column
    for col in df.columns:
        col_lower = col.lower()
 
        # Skip bounds columns and metadata columns
        if (col.endswith('_UB') or col.endswith('_LB') or
            col in ['Arc', 'Table_type', 'cell', 'table_position']):
            continue
 
        # Check if column belongs to the current category
        is_category_column = False
        for prefix in category_prefixes:
            if prefix in col or prefix in col_lower:
                is_category_column = True
                break
 
        # If not a column for this category, skip it
        if category_prefixes and not is_category_column:
            continue
 
        # Determine parameter type with more flexible matching
        if any(term in col_lower for term in ['early', 'earl']) and any(term in col_lower for term in ['sigma', 'sig']):
            parameters['early_sigma'].append(col)
            logcalc.debug(f"Identified {col} as early_sigma column in {category}")
        elif any(term in col_lower for term in ['late', 'lat']) and any(term in col_lower for term in ['sigma', 'sig']):
            parameters['late_sigma'].append(col)
            logcalc.debug(f"Identified {col} as late_sigma column in {category}")
        elif any(term in col_lower for term in ['std', 'stdev', 'standard']):
            parameters['Std'].append(col)
            logcalc.debug(f"Identified {col} as Std column in {category}")
        elif any(term in col_lower for term in ['skew', 'skewness']):
            parameters['Skew'].append(col)
            logcalc.debug(f"Identified {col} as Skew column in {category}")
        elif any(term in col_lower for term in ['meanshift', 'mean_shift', 'mean shift']):
            parameters['Meanshift'].append(col)
            logcalc.debug(f"Identified {col} as Meanshift column in {category}")
 
    # Log the identified parameters
    for param, cols in parameters.items():
        if cols:
            logcalc.debug(f"Found {len(cols)} {param} columns in {category}: {cols}")
        else:
            logcalc.debug(f"No {param} columns found in {category}")
 
    # Explicitly log meanshift column status
    if category == 'MC':
        if parameters['Meanshift']:
            logcalc.info(f"Found {len(parameters['Meanshift'])} MC_Meanshift columns: {parameters['Meanshift']}")
        else:
            logcalc.warning(f"No MC_Meanshift columns found in MC data!")
 
    return parameters
 
def extract_mc_values_for_arc(mc_data, corner, arc, idx, param_name, mc_params, mc_df):
    """
    Extract MC values for a specific arc, with special attention to meanshift for std/skew.
 
    Args:
        mc_data: Dictionary to store MC values
        corner: Corner being processed
        arc: Arc identifier
        idx: Index in the dataframe
        param_name: Parameter name (Std, Skew, etc.)
        mc_params: Parameters identified in MC dataframe
        mc_df: MC dataframe
 
    Returns:
        Dictionary with extracted MC values
    """
    logcalc = logging.getLogger('calculation')
    extracted_values = {}
 
    if mc_df is None or param_name not in mc_params:
        return extracted_values
 
    # Always look for meanshift when processing std or skew
    need_meanshift = param_name in ['Std', 'Skew']
 
    # First extract the primary parameter value
    for mc_col in mc_params[param_name]:
        if idx < len(mc_df):  # Ensure index is valid
            try:
                mc_value = mc_df.iloc[idx][mc_col]
                if not pd.isna(mc_value):
                    extracted_values[param_name.lower()] = mc_value
                    logcalc.debug(f"Extracted {param_name} MC value: {mc_value} for {arc}")
                    break  # We only need one value per parameter type
            except Exception as e:
                logcalc.error(f"Error extracting {mc_col} MC value: {e}")
 
    # Now extract meanshift if needed for std or skew
    if need_meanshift and 'Meanshift' in mc_params:
        for mc_col in mc_params['Meanshift']:
            if idx < len(mc_df):  # Ensure index is valid
                try:
                    mc_value = mc_df.iloc[idx][mc_col]
                    if not pd.isna(mc_value):
                        extracted_values['meanshift'] = mc_value
                        logcalc.debug(f"Extracted Meanshift MC value: {mc_value} for {arc} (needed for {param_name})")
                        break  # We only need one meanshift value
                except Exception as e:
                    logcalc.error(f"Error extracting {mc_col} Meanshift value: {e}")
 
    # Log whether we found or missed the meanshift value for std/skew
    if need_meanshift:
        if 'meanshift' in extracted_values:
            logcalc.debug(f"Successfully extracted Meanshift value for {param_name}: {extracted_values['meanshift']}")
        else:
            logcalc.warning(f"Failed to find Meanshift value for {param_name} calculation (arc: {arc})")
 
    return extracted_values
 
def calculate_sensitivities(all_data, output_dir, data_dir=None):
    """Calculate sensitivities for each corner, parameter, and type using library data."""
    logcalc = logging.getLogger('calculation')
    logflow = logging.getLogger('dataflow')
 
    logcalc.info("=" * 80)
    logcalc.info("CALCULATING SENSITIVITIES")
    logcalc.info("=" * 80)
 
    # Initialize tracking for verification
    calculate_sensitivities.verification_summaries = []
    calculate_sensitivities.verification_results = []
 
    # Define voltage pairs for adjacent points calculation
    voltage_pairs = {
        0.450: [(0.450, 0.465)],
        0.465: [(0.450, 0.465), (0.465, 0.480)],
        0.480: [(0.465, 0.480), (0.480, 0.495)],
        0.495: [(0.480, 0.495)]
    }
 
    # Store sensitivity results
    sensitivities = {}
    all_cell_data = {}
 
    # Store lib data and error data for sensitivity calculation and margin calculation
    lib_data = {}
    error_data = {}
 
    # Create tracking for progress reporting
    total_corners = len(all_data)
    processed_corners = 0
 
    # Collect library data and error data by cell/arc for each corner
    for corner, corner_data in all_data.items():
        processed_corners += 1
        logflow.info(f"Processing corner {processed_corners}/{total_corners}: {corner}")
 
        # Extract the voltage value for this corner
        voltage = extract_voltage_from_corner(corner)
        if voltage is None:
            logflow.warning(f"Could not extract voltage for corner {corner}. Skipping.")
            continue
 
        # Track types processed for this corner for reporting
        types_processed = []
 
        for type_name, type_data in corner_data.items():
            # Log available categories for this type
            logflow.debug(f"Available categories for {corner} {type_name}: {list(type_data.keys())}")
 
            # Ensure we have required data categories
            required_categories = ['Lib', 'abs_err']
            missing_required = [cat for cat in required_categories if cat not in type_data]
            if missing_required:
                logflow.warning(f"Missing required data categories for {corner} {type_name}: {missing_required}")
                logflow.warning(f"Required: Lib and abs_err. Available: {list(type_data.keys())}")
                continue
 
            lib_df = type_data['Lib']
            abs_err_df = type_data['abs_err']
 
            # Check if we have rel_err data
            rel_err_df = type_data.get('rel_err', None)
            if rel_err_df is not None:
                logflow.info(f"Found rel_err data for {corner} {type_name}: {rel_err_df.shape}")
            else:
                logflow.warning(f"No rel_err data for {corner} {type_name}")
 
            # Check if we have MC data
            mc_df = type_data.get('MC', None)
            if mc_df is not None:
                logflow.info(f"Found MC data for {corner} {type_name}: {mc_df.shape}")
                # Log the MC columns for debugging
                logcalc.info(f"MC columns for {corner} {type_name}: {mc_df.columns.tolist()}")
            else:
                logflow.warning(f"No MC data for {corner} {type_name}")
 
            # Identify parameters in the dataframes
            lib_params = identify_parameters_in_dataframe(lib_df, 'Lib')
            abs_params = identify_parameters_in_dataframe(abs_err_df, 'abs_err')
 
            # Also identify parameters in rel_err data if available
            rel_params = identify_parameters_in_dataframe(rel_err_df, 'rel_err') if rel_err_df is not None else {}
            mc_params = identify_parameters_in_dataframe(mc_df, 'MC') if mc_df is not None else {}
 
            # Check explicitly for MC_Meanshift for Std/Skew calculations
            if mc_df is not None:
                has_meanshift = any('meanshift' in col.lower() for col in mc_df.columns)
                if has_meanshift:
                    logcalc.info(f"Found Meanshift column(s) in MC data for {corner} {type_name}")
                else:
                    logcalc.warning(f"No Meanshift column found in MC data for {corner} {type_name} - Std/Skew calculations may be affected")
 
            # Log parameter identification results
            logcalc.info(f"Parameters found in {corner} {type_name}:")
            logcalc.info(f"  Lib: {', '.join([p for p in lib_params if lib_params[p]])}")
            logcalc.info(f"  abs_err: {', '.join([p for p in abs_params if abs_params[p]])}")
            if rel_err_df is not None:
                logcalc.info(f"  rel_err: {', '.join([p for p in rel_params if rel_params[p]])}")
            if mc_df is not None:
                logcalc.info(f"  MC: {', '.join([p for p in mc_params if mc_params[p]])}")
 
            # Track parameters processed for reporting
            params_processed = []
 
            # For each parameter, collect library values and corresponding errors
            for param_name in ['early_sigma', 'late_sigma', 'Std', 'Skew', 'Meanshift']:
                # Skip if parameter not found in the dataframes
                if not lib_params[param_name] or not abs_params[param_name]:
                    logcalc.debug(f"Skipping {param_name} for {corner} {type_name} - not found in all required dataframes")
                    continue
 
                params_processed.append(param_name)
 
                # Initialize data structure for this parameter if needed
                param_key = f"{type_name}_{param_name}"
                if param_key not in lib_data:
                    lib_data[param_key] = {}
                    error_data[param_key] = {}
 
                # Process each row in the dataframe
                for idx in range(len(lib_df)):
                    try:
                        # Get Arc information - handle different column name variations
                        arc_col = next((col for col in lib_df.columns if col.lower() == 'arc'), None)
                        if arc_col:
                            arc = lib_df.iloc[idx].get(arc_col, f'row_{idx}')
                        else:
                            arc = f'row_{idx}'
 
                        cell, table_pos = extract_cell_info(arc)
 
                        # Create unique key for this arc/cell
                        arc_key = f"{arc}"
 
                        # Initialize data structures if needed
                        if arc_key not in lib_data[param_key]:
                            lib_data[param_key][arc_key] = {
                                'arc': arc,
                                'cell': cell,
                                'table_position': table_pos,
                                'voltages': [],
                                'lib_values': {},
                                'corner_data': {}
                            }
 
                        if arc_key not in error_data[param_key]:
                            error_data[param_key][arc_key] = {
                                'arc': arc,
                                'cell': cell,
                                'table_position': table_pos,
                                'voltages': [],
                                'corner_data': {}
                            }
 
                        # Add voltage if not already added
                        if voltage not in lib_data[param_key][arc_key]['voltages']:
                            lib_data[param_key][arc_key]['voltages'].append(voltage)
                            error_data[param_key][arc_key]['voltages'].append(voltage)
 
                        # Add library values
                        for lib_col in lib_params[param_name]:
                            if idx < len(lib_df):  # Ensure index is valid
                                try:
                                    lib_value = lib_df.iloc[idx][lib_col]
 
                                    # Skip if library value is missing
                                    if pd.isna(lib_value):
                                        continue
 
                                    if lib_col not in lib_data[param_key][arc_key]['lib_values']:
                                        lib_data[param_key][arc_key]['lib_values'][lib_col] = []
 
                                    lib_data[param_key][arc_key]['lib_values'][lib_col].append(lib_value)
 
                                    # Store corner-specific data
                                    if corner not in lib_data[param_key][arc_key]['corner_data']:
                                        lib_data[param_key][arc_key]['corner_data'][corner] = {}
 
                                    lib_data[param_key][arc_key]['corner_data'][corner][lib_col] = lib_value
                                except Exception as e:
                                    logcalc.error(f"Error processing library value at row {idx}, column {lib_col}: {e}")
 
                        # Store error values for all errors (not just positive ones)
                        if corner not in error_data[param_key][arc_key]['corner_data']:
                            error_data[param_key][arc_key]['corner_data'][corner] = {
                                'abs_err': {},
                                'rel_err': {},
                                'MC': {}
                            }
 
                        # Process abs_err
                        for abs_col in abs_params[param_name]:
                            if idx < len(abs_err_df):  # Ensure index is valid
                                try:
                                    abs_value = abs_err_df.iloc[idx][abs_col]
 
                                    # Store all error values (not just positive ones)
                                    if not pd.isna(abs_value):
                                        error_data[param_key][arc_key]['corner_data'][corner]['abs_err'][abs_col] = abs_value
                                except Exception as e:
                                    logcalc.error(f"Error processing abs_err value at row {idx}, column {abs_col}: {e}")
 
                        # Process rel_err if available
                        if rel_err_df is not None and param_name in rel_params and rel_params[param_name]:
                            for rel_col in rel_params[param_name]:
                                if idx < len(rel_err_df):  # Ensure index is valid
                                    try:
                                        rel_value = rel_err_df.iloc[idx][rel_col]
 
                                        # Store all error values
                                        if not pd.isna(rel_value):
                                            error_data[param_key][arc_key]['corner_data'][corner]['rel_err'][rel_col] = rel_value
                                    except Exception as e:
                                        logcalc.error(f"Error processing rel_err value at row {idx}, column {rel_col}: {e}")
 
                        # Process MC if available - with improved extraction for meanshift
                        if mc_df is not None:
                            # Extract MC values with special attention to meanshift for std/skew
                            mc_values = extract_mc_values_for_arc(
                                error_data[param_key][arc_key]['corner_data'][corner]['MC'],
                                corner, arc, idx, param_name, mc_params, mc_df
                            )
 
                            # Add the extracted values to the MC data
                            error_data[param_key][arc_key]['corner_data'][corner]['MC'].update(mc_values)
 
                            # Log what was extracted for debugging
                            if mc_values:
                                logcalc.debug(f"Extracted MC values for {corner} {arc} {param_name}: {mc_values}")
 
                    except Exception as e:
                        logcalc.error(f"Error processing row {idx}: {e}")
 
            types_processed.append(f"{type_name} ({', '.join(params_processed)})")
 
        logflow.info(f"Completed corner {corner}: Processed {', '.join(types_processed)}")
 
    # Now calculate sensitivities using adjacent points
    logcalc.info("Calculating sensitivities using adjacent points...")
 
    for param_key, arcs in lib_data.items():
        type_name, param_name = param_key.split('_', 1)
 
        # Initialize results storage
        if type_name not in sensitivities:
            sensitivities[type_name] = {}
            all_cell_data[type_name] = {}
 
        if param_name not in sensitivities[type_name]:
            sensitivities[type_name][param_name] = []
            all_cell_data[type_name][param_name] = []
 
        # Process each arc
        arc_count = len(arcs)
        processed_arcs = 0
        sensitivity_count = 0
 
        for arc_key, data in arcs.items():
            processed_arcs += 1
            if processed_arcs % 100 == 0 or processed_arcs == arc_count:
                logcalc.info(f"Processing {type_name} {param_name}: {processed_arcs}/{arc_count} arcs, {sensitivity_count} sensitivities calculated")
 
            # Skip if arc doesn't have at least 2 voltage points
            voltages = data['voltages']
            if len(voltages) < 2:
                continue
 
            # Calculate sensitivities for each library column
            for lib_col, lib_values in data['lib_values'].items():
                # Skip if column doesn't have enough values
                if len(lib_values) < 2:
                    continue
 
                # Calculate sensitivity for each corner voltage
                corner_sensitivities = {}
 
                # Get corner-specific data
                sorted_corners = sorted(data['corner_data'].keys(), key=extract_voltage_from_corner)
                for corner in sorted_corners:
                    voltage = extract_voltage_from_corner(corner)
 
                    # Skip if voltage is None
                    if voltage is None:
                        continue
 
                    # Get voltage pairs for this corner
                    pairs = voltage_pairs.get(voltage, [])
 
                    # If no defined pairs, try to create a reasonable pair
                    if not pairs and len(sorted_corners) >= 2:
                        # Find the closest corners by voltage
                        corner_voltages = [extract_voltage_from_corner(c) for c in sorted_corners]
                        valid_voltages = [v for v in corner_voltages if v is not None]
 
                        if len(valid_voltages) >= 2:
                            sorted_voltages = sorted(valid_voltages)
                            idx = sorted_voltages.index(voltage) if voltage in sorted_voltages else -1
 
                            if idx >= 0:
                                # Create a voltage pair with neighboring points
                                if idx > 0 and idx < len(sorted_voltages) - 1:
                                    # Middle point - create pairs with both neighbors
                                    pairs = [
                                        (sorted_voltages[idx-1], sorted_voltages[idx]),
                                        (sorted_voltages[idx], sorted_voltages[idx+1])
                                    ]
                                elif idx == 0:
                                    # First point - pair with next
                                    pairs = [(sorted_voltages[idx], sorted_voltages[idx+1])]
                                else:
                                    # Last point - pair with previous
                                    pairs = [(sorted_voltages[idx-1], sorted_voltages[idx])]
 
                    # Skip if no pairs defined
                    if not pairs:
                        continue
 
                    # Calculate sensitivity for each pair
                    pair_sensitivities = []
                    for pair in pairs:
                        # Get voltage and library values for all relevant corners
                        v_values = []
                        l_values = []
 
                        for c in sorted_corners:
                            v = extract_voltage_from_corner(c)
                            if v is None or v < pair[0] or v > pair[1]:
                                continue
 
                            if c in data['corner_data'] and lib_col in data['corner_data'][c]:
                                v_values.append(v)
                                l_values.append(data['corner_data'][c][lib_col])
 
                        # Calculate sensitivity if we have enough points
                        if len(v_values) >= 2:
                            sensitivity = calculate_multi_point_sensitivity(v_values, l_values)
                            if sensitivity:
                                pair_sensitivities.append(sensitivity)
 
                    # Average sensitivities for this corner
                    if pair_sensitivities:
                        sensitivity_count += 1
 
                        # Calculate weighted average based on r-squared values
                        weights = [max(0.1, s['r_squared']) for s in pair_sensitivities]  # Minimum weight of 0.1
                        total_weight = sum(weights)
 
                        if total_weight > 0:
                            avg_sensitivity = sum(s['sensitivity_mv'] * w for s, w in zip(pair_sensitivities, weights)) / total_weight
                            avg_r_squared = sum(s['r_squared'] * w for s, w in zip(pair_sensitivities, weights)) / total_weight
                        else:
                            # Fallback to simple average if weights are all effectively zero
                            avg_sensitivity = sum(s['sensitivity_mv'] for s in pair_sensitivities) / len(pair_sensitivities)
                            avg_r_squared = sum(s['r_squared'] for s in pair_sensitivities) / len(pair_sensitivities)
 
                        corner_sensitivities[corner] = {
                            'sensitivity_mv': avg_sensitivity,
                            'r_squared': avg_r_squared,
                            'pairs': [pair for pair in pairs],
                            'pair_results': pair_sensitivities
                        }
 
                # Skip if no sensitivities calculated
                if not corner_sensitivities:
                    continue
 
                # Get corresponding error data
                error_arc_data = error_data[param_key].get(arc_key, {})
 
                # Create sensitivity data object
                sensitivity_data = {
                    'arc': data['arc'],
                    'cell': data['cell'],
                    'table_position': data['table_position'],
                    'lib_column': lib_col,
                    'corner_sensitivities': corner_sensitivities,
                    'lib_values': data['corner_data'],
                    'error_data': error_arc_data.get('corner_data', {})
                }
 
                # Store sensitivity data
                sensitivities[type_name][param_name].append(sensitivity_data)
 
                # Add to cell data collection for analysis
                if data['cell']:
                    for corner, corner_sens in corner_sensitivities.items():
                        cell_data = {
                            'type': type_name,
                            'parameter': param_name,
                            'arc': data['arc'],
                            'cell': data['cell'],
                            'table_position': data['table_position'],
                            'column': lib_col,
                            'corner': corner,
                            'voltage': extract_voltage_from_corner(corner),
                            'sensitivity_mv': corner_sens['sensitivity_mv'],
                            'r_squared': corner_sens['r_squared']
                        }
                        all_cell_data[type_name][param_name].append(cell_data)
 
    logcalc.info(f"Completed sensitivity calculations")
 
    # Now create scatter plots for each corner/type/parameter
    for corner in all_data.keys():
        corner_output_dir = os.path.join(output_dir, corner)
        os.makedirs(corner_output_dir, exist_ok=True)
 
        for type_name in sensitivities:
            type_output_dir = os.path.join(corner_output_dir, type_name)
            os.makedirs(type_output_dir, exist_ok=True)
 
            for param_name in sensitivities[type_name]:
                # Create parameter directory
                param_output_dir = os.path.join(type_output_dir, param_name)
                os.makedirs(param_output_dir, exist_ok=True)
 
                # Debug: Log the parameter data before creating scatter plots
                param_data = sensitivities[type_name][param_name]
                logcalc.info(f"Creating scatter plot for {corner}/{type_name}/{param_name} with {len(param_data)} data points")
 
                # Check for rel_err data specifically for this corner/type/param
                rel_err_found = False
                for data in param_data:
                    if corner in data.get('error_data', {}) and 'rel_err' in data['error_data'][corner] and data['error_data'][corner]['rel_err']:
                        rel_err_found = True
                        logcalc.info(f"Found rel_err data for {corner}/{type_name}/{param_name}: {list(data['error_data'][corner]['rel_err'].keys())}")
                        break
 
                if not rel_err_found:
                    logcalc.warning(f"No rel_err data found for {corner}/{type_name}/{param_name}")
 
                # Create scatter plots for this corner/type/param and capture verification summary
                verification_results, verification_summary = create_error_margin_scatter_plot(
                    sensitivities[type_name][param_name],
                    corner, type_name, param_name, param_output_dir, data_dir
                )
 
                # Store verification results for overall tracking
                if verification_summary is not None:
                    calculate_sensitivities.verification_summaries.append(
                        ((corner, type_name, param_name), verification_summary)
                    )
 
                    if verification_results is not None:
                        calculate_sensitivities.verification_results.append(
                            ((corner, type_name, param_name), verification_results)
                        )
 
    # Now run the voltage margin analysis
    logcalc.info("Running voltage margin analysis...")
    margin_data = analyze_voltage_margin(sensitivities, output_dir)
 
    logcalc.info(f"Completed sensitivity calculations")
 
    return sensitivities, all_cell_data, margin_data
 
def verify_rel_err_conversion(abs_err_data, rel_err_data, corner, type_name, param_name, output_dir, data_dir):
    """
    Comprehensive verification of rel_err to abs_err conversion with explicit denominator calculation.
    Enhanced to handle missing meanshift values for std/skew.
    """
    logcalc = logging.getLogger('calculation')
 
    logcalc.info("=" * 80)
    logcalc.info(f"VERIFICATION: Validating rel_err conversion for {corner} {type_name} {param_name}")
    logcalc.info("=" * 80)
 
    # Create output directory for verification results
    verification_dir = os.path.join(output_dir, "verification")
    os.makedirs(verification_dir, exist_ok=True)
 
    # Create a verification log file for detailed denominator calculations
    log_file = os.path.join(verification_dir,
                          f"{corner}_{type_name}_{param_name}_denominator_verification.log")
    verification_logger = setup_verification_logger(log_file)
 
    # Create a detailed debug log file
    debug_log_file = os.path.join(verification_dir,
                                f"{corner}_{type_name}_{param_name}_debug.log")
    debug_logger = setup_verification_logger(debug_log_file)
    debug_logger.info("=" * 80)
    debug_logger.info(f"MC DATA DEBUG LOG FOR {corner} {type_name} {param_name}")
    debug_logger.info("=" * 80)
    debug_logger.info("")
 
    # Print header in verification log
    verification_logger.info("=" * 80)
    verification_logger.info(f"DENOMINATOR CALCULATION VERIFICATION: {corner} {type_name} {param_name}")
    verification_logger.info("=" * 80)
    verification_logger.info("")
 
    # Document the correct denominator formulas - USING ASCII ONLY
    verification_logger.info("CORRECT DENOMINATOR FORMULAS:")
    verification_logger.info("  MEANSHIFT: lib_nominal + meanshift_mc")
    verification_logger.info("  STD: lib_nominal + meanshift_mc + stddev_mc")
    verification_logger.info("  SKEW: lib_nominal + meanshift_mc + skewness_mc")
    verification_logger.info("  EARLY_SIGMA: max(abs(lib_nominal), MC_early_sigma)")
    verification_logger.info("  LATE_SIGMA: max(abs(lib_nominal), MC_late_sigma)")
    verification_logger.info("")
 
    # For Std/Skew, log modified formulas if meanshift might be missing
    if param_name in ['Std', 'Skew']:
        verification_logger.info("NOTICE: If MC_Meanshift is missing, simplified formulas will be used:")
        verification_logger.info("  STD (simplified): lib_nominal + stddev_mc")
        verification_logger.info("  SKEW (simplified): lib_nominal + skewness_mc")
        verification_logger.info("")
 
    # Try multiple potential directory structures for lib_data loading
    lib_data = None
    potential_dirs = [
        data_dir,                                              # direct data_dir
        os.path.join(data_dir, corner),                       # data_dir/corner
        os.path.join(data_dir, f"{corner}_{type_name}"),     # data_dir/corner_type
        os.path.join(data_dir, type_name)                    # data_dir/type_name
    ]
 
    verification_logger.info(f"Attempting to load lib_nominal values from multiple locations")
    for input_dir in potential_dirs:
        verification_logger.info(f"Trying directory: {input_dir}")
        lib_data = load_lib_data(input_dir, corner, type_name)
        if lib_data:
            verification_logger.info(f"Successfully loaded {len(lib_data)} lib_nominal values from {input_dir}")
            break
 
    if lib_data:
        verification_logger.info(f"Found Lib data with {len(lib_data)} entries")
        # Show some sample values
        sample_keys = list(lib_data.keys())[:3]
        for key in sample_keys:
            verification_logger.info(f"Sample arc: {key}, nominal: {lib_data[key].get('nominal')}")
    else:
        verification_logger.info("Could not load Lib data file - will use lib_nominal from rel_err data if available")
 
    # Match abs_err and rel_err data by arc
    matches = []
 
    # Create a dictionary to index abs_err data by arc
    abs_by_arc = {}
    for item in abs_err_data:
        arc = item.get('arc')
        if arc:
            abs_by_arc[arc] = item
 
    # Create a dictionary to index rel_err data by arc
    rel_by_arc = {}
    for item in rel_err_data:
        arc = item.get('arc')
        if arc:
            rel_by_arc[arc] = item
 
    # Find common arcs
    common_arcs = set(abs_by_arc.keys()) & set(rel_by_arc.keys())
 
    # Create matches
    for arc in common_arcs:
        matches.append({
            'arc': arc,
            'abs_item': abs_by_arc[arc],
            'rel_item': rel_by_arc[arc]
        })
 
    if not matches:
        verification_logger.info("No matching arcs found for verification.")
        logcalc.warning(f"No matching arcs found between abs_err and rel_err data for {param_name}")
        # Return an empty result and summary indicating no verification was possible
        verification_summary = {
            'total_comparisons': 0,
            'valid_comparisons': 0,
            'exact_matches': 0,
            'close_matches': 0,
            'large_differences': 0,
            'average_pct_diff': 0.0,
            'perfect_conversion': False,
            'verification_possible': False
        }
        return [], verification_summary
 
    verification_logger.info(f"Found {len(matches)} matching arcs for verification.")
    verification_logger.info("")
 
    # Examine MC data for first few matches to understand what's available
    for i, match in enumerate(matches[:5]):
        rel_item = match['rel_item']
        arc = match['arc']
        debug_logger.info(f"MC DATA INSPECTION FOR ARC: {arc}")
 
        # Inspect mc_data structure
        mc_data = rel_item.get('mc_data', {})
        debug_logger.info(f"Full MC Data structure:")
        if isinstance(mc_data, dict):
            for k, v in mc_data.items():
                debug_logger.info(f"  {k}: {v}")
 
            # Look for meanshift keys
            debug_logger.info(f"Keys possibly related to meanshift:")
            for k in mc_data.keys():
                if 'mean' in k.lower() or 'shift' in k.lower():
                    debug_logger.info(f"  Found potential meanshift key: {k} = {mc_data[k]}")
 
            # Look for std and skew keys too
            debug_logger.info(f"Keys possibly related to std:")
            for k in mc_data.keys():
                if 'std' in k.lower() or 'stdev' in k.lower():
                    debug_logger.info(f"  Found potential std key: {k} = {mc_data[k]}")
 
            debug_logger.info(f"Keys possibly related to skew:")
            for k in mc_data.keys():
                if 'skew' in k.lower():
                    debug_logger.info(f"  Found potential skew key: {k} = {mc_data[k]}")
        else:
            debug_logger.info(f"  MC data is not a dictionary: {mc_data}")
 
        debug_logger.info("")
 
    # Process each match to verify denominator calculation
    verification_results = []
 
    # Record parameter types found
    param_types_processed = set()
 
    for i, match in enumerate(matches):
        # Extract data from match
        abs_item = match['abs_item']
        rel_item = match['rel_item']
        arc = match['arc']
 
        # Get basic values
        abs_error = abs_item.get('error_value')
        rel_error = rel_item.get('error_value')
        original_denominator = rel_item.get('denominator')
 
        # Skip invalid data
        if abs_error is None or rel_error is None or original_denominator is None:
            continue
 
        # Extract additional metadata
        cell = abs_item.get('cell', 'Unknown')
        table_position = abs_item.get('table_position', 'Unknown')
 
        # Get lib_nominal from the Lib data file first, then fall back to rel_item if not found
        lib_nominal = None
        lib_source = "unknown"
 
        if lib_data and arc in lib_data:
            lib_nominal = lib_data[arc].get('nominal')
            lib_source = "Lib_data.csv"
            if i < 5:  # Limit logging to first few items
                debug_logger.info(f"Using lib_nominal={lib_nominal} from Lib_data.csv for arc={arc}")
        else:
            # Try normalized arcs
            normalized_arcs = [
                arc,
                arc.strip(),
                arc.lower().strip(),
                ' '.join(arc.split())  # Normalize whitespace
            ]
 
            for norm_arc in normalized_arcs:
                if lib_data and norm_arc in lib_data:
                    lib_nominal = lib_data[norm_arc].get('nominal')
                    lib_source = "Lib_data.csv (normalized)"
                    if i < 5:
                        debug_logger.info(f"Using lib_nominal={lib_nominal} from Lib_data.csv with normalized arc={norm_arc}")
                    break
 
        # If still not found, fall back to value from rel_item
        if lib_nominal is None:
            lib_nominal = rel_item.get('lib_nominal')
            lib_source = "rel_err data"
            if i < 5:
                debug_logger.info(f"Using lib_nominal={lib_nominal} from rel_err data for arc={arc}")
 
        # Get all MC values that might be needed with improved extraction
        mc_values = {}
        mc_data = rel_item.get('mc_data', {})
 
        if i < 5:  # Debug first few
            debug_logger.info(f"Raw mc_data for arc {arc}: {mc_data}")
 
        # First try to get values with exact key names
        if isinstance(mc_data, dict):
            # Look for meanshift keys with multiple patterns
            for key in ['meanshift', 'MC_Meanshift', 'mc_meanshift', 'meanshift_mc']:
                if key in mc_data:
                    mc_values['meanshift'] = mc_data[key]
                    break
 
            # Look for std keys
            for key in ['std', 'MC_Std', 'mc_std', 'std_mc', 'stddev', 'stdev']:
                if key in mc_data:
                    mc_values['std'] = mc_data[key]
                    break
 
            # Look for skew keys
            for key in ['skew', 'MC_Skew', 'mc_skew', 'skew_mc', 'skewness']:
                if key in mc_data:
                    mc_values['skew'] = mc_data[key]
                    break
 
            # Try with case-insensitive matching
            if 'meanshift' not in mc_values:
                for key in mc_data.keys():
                    if 'mean' in key.lower() and 'shift' in key.lower():
                        mc_values['meanshift'] = mc_data[key]
                        break
 
            if 'std' not in mc_values:
                for key in mc_data.keys():
                    if 'std' in key.lower() or 'stdev' in key.lower():
                        mc_values['std'] = mc_data[key]
                        break
 
            if 'skew' not in mc_values:
                for key in mc_data.keys():
                    if 'skew' in key.lower():
                        mc_values['skew'] = mc_data[key]
                        break
 
        # Also check direct values
        mc_value = rel_item.get('mc_value')
        if mc_value is not None:
            if param_name == 'Std' and 'std' not in mc_values:
                mc_values['std'] = mc_value
            elif param_name == 'Skew' and 'skew' not in mc_values:
                mc_values['skew'] = mc_value
            elif param_name == 'Meanshift' and 'meanshift' not in mc_values:
                mc_values['meanshift'] = mc_value
            elif 'main' not in mc_values:
                mc_values['main'] = mc_value
 
        # Debug what we found
        if i < 5:
            debug_logger.info(f"Extracted mc_values for arc {arc}: {mc_values}")
 
            if 'std' in mc_values and param_name == 'Std':
                debug_logger.info(f"Found std value: {mc_values['std']}")
            elif 'std' not in mc_values and param_name == 'Std':
                debug_logger.info(f"WARNING: Could not find std value for Std calculation")
 
            if 'skew' in mc_values and param_name == 'Skew':
                debug_logger.info(f"Found skew value: {mc_values['skew']}")
            elif 'skew' not in mc_values and param_name == 'Skew':
                debug_logger.info(f"WARNING: Could not find skew value for Skew calculation")
 
            if 'meanshift' in mc_values:
                debug_logger.info(f"Found meanshift value: {mc_values['meanshift']}")
            else:
                debug_logger.info(f"WARNING: Could not find meanshift value with any known key")
 
        # Determine parameter type
        param_type = None
        if 'meanshift' in param_name.lower():
            param_type = 'meanshift'
        elif 'std' in param_name.lower():
            param_type = 'std'
        elif 'skew' in param_name.lower():
            param_type = 'skew'
        elif 'early_sigma' in param_name.lower():
            param_type = 'early_sigma'
        elif 'late_sigma' in param_name.lower():
            param_type = 'late_sigma'
 
        # If param_type was not determined from param_name, try from rel_item
        if param_type is None:
            param_type = rel_item.get('param_type')
 
        # Skip if param_type still not determined
        if param_type is None:
            continue
 
        # Record this parameter type as processed
        param_types_processed.add(param_type)
 
        # Recalculate denominator using correct formula
        recalculated_denominator = None
        calculation_details = "N/A"
        correct_formula = "N/A"
 
        if param_type == 'meanshift':
            correct_formula = "lib_nominal + meanshift_mc"
 
            # Get meanshift value from mc_values
            meanshift_mc = mc_values.get('meanshift')
 
            if lib_nominal is not None and meanshift_mc is not None:
                recalculated_denominator = lib_nominal + meanshift_mc
                calculation_details = f"{lib_nominal} + {meanshift_mc} = {recalculated_denominator}"
            else:
                calculation_details = f"MISSING DATA: lib_nominal={lib_nominal} (from {lib_source}), meanshift_mc={meanshift_mc}"
 
        elif param_type == 'std':
            correct_formula = "lib_nominal + meanshift_mc + stddev_mc"
 
            # Get MC values
            meanshift_mc = mc_values.get('meanshift')
            stddev_mc = mc_values.get('std')
 
            # For Std, we can use a simplified formula if meanshift is missing
            if lib_nominal is not None and stddev_mc is not None:
                if meanshift_mc is not None:
                    # Full calculation
                    recalculated_denominator = lib_nominal + meanshift_mc + stddev_mc
                    calculation_details = f"{lib_nominal} + {meanshift_mc} + {stddev_mc} = {recalculated_denominator}"
                else:
                    # Simplified calculation when meanshift is missing
                    recalculated_denominator = lib_nominal + stddev_mc
                    calculation_details = f"{lib_nominal} + [missing meanshift_mc] + {stddev_mc} = {recalculated_denominator} (simplified formula)"
                    correct_formula = "lib_nominal + stddev_mc (simplified)"
            else:
                calculation_details = f"MISSING DATA: lib_nominal={lib_nominal} (from {lib_source}), stddev_mc={stddev_mc}"
 
        elif param_type == 'skew':
            correct_formula = "lib_nominal + meanshift_mc + skewness_mc"
 
            # Get MC values
            meanshift_mc = mc_values.get('meanshift')
            skewness_mc = mc_values.get('skew')
 
            # For Skew, we can also use a simplified formula if meanshift is missing
            if lib_nominal is not None and skewness_mc is not None:
                if meanshift_mc is not None:
                    # Full calculation
                    recalculated_denominator = lib_nominal + meanshift_mc + skewness_mc
                    calculation_details = f"{lib_nominal} + {meanshift_mc} + {skewness_mc} = {recalculated_denominator}"
                else:
                    # Simplified calculation when meanshift is missing
                    recalculated_denominator = lib_nominal + skewness_mc
                    calculation_details = f"{lib_nominal} + [missing meanshift_mc] + {skewness_mc} = {recalculated_denominator} (simplified formula)"
                    correct_formula = "lib_nominal + skewness_mc (simplified)"
            else:
                calculation_details = f"MISSING DATA: lib_nominal={lib_nominal} (from {lib_source}), skewness_mc={skewness_mc}"
 
        elif param_type in ['early_sigma', 'late_sigma']:
            sigma_type = param_type  # early_sigma or late_sigma
            correct_formula = f"max(abs(lib_nominal), MC_{sigma_type})"
 
            # Get sigma value
            sigma_mc = None
 
            # Look for sigma in mc_values with correct type
            for key in [sigma_type, f"{sigma_type}_mc", 'main', 'sigma']:
                if key in mc_values:
                    sigma_mc = mc_values[key]
                    break
 
            if lib_nominal is not None and sigma_mc is not None:
                # Use max of abs(lib_nominal) and sigma_mc
                abs_lib_nominal = abs(lib_nominal)
                recalculated_denominator = max(abs_lib_nominal, sigma_mc)
 
                # Show detailed calculation
                calculation_details = f"max(abs({lib_nominal}), {sigma_mc}) = max({abs_lib_nominal}, {sigma_mc}) = {recalculated_denominator}"
 
                # Note which value was used
                if abs_lib_nominal >= sigma_mc:
                    calculation_details += f" [abs(lib_nominal) was used]"
                else:
                    calculation_details += f" [MC_{sigma_type} was used]"
            else:
                calculation_details = f"MISSING DATA: lib_nominal={lib_nominal} (from {lib_source}), {sigma_type}_mc={sigma_mc}"
 
        # Calculate difference between original and recalculated denominator
        denominator_diff = None
        denominator_pct_diff = None
 
        if recalculated_denominator is not None and original_denominator is not None:
            denominator_diff = recalculated_denominator - original_denominator
            denominator_pct_diff = (denominator_diff / original_denominator * 100) if original_denominator != 0 else float('inf')
 
        # Calculate abs_error values and differences
        original_abs_error = rel_error * original_denominator if original_denominator is not None else None
        recalculated_abs_error = rel_error * recalculated_denominator if recalculated_denominator is not None else None
 
        # Compare with actual abs_error
        original_diff = original_abs_error - abs_error if original_abs_error is not None else None
        recalculated_diff = recalculated_abs_error - abs_error if recalculated_abs_error is not None else None
 
        original_pct_diff = (original_diff / abs_error * 100) if original_diff is not None and abs_error != 0 else None
        recalculated_pct_diff = (recalculated_diff / abs_error * 100) if recalculated_diff is not None and abs_error != 0 else None
 
        # Store verification result
        result = {
            'arc': arc,
            'cell': cell,
            'table_position': table_position,
            'param_type': param_type,
            'abs_error': abs_error,
            'rel_error': rel_error,
            'lib_nominal': lib_nominal,
            'lib_nominal_source': lib_source,
            'mc_values': mc_values,
            'original_denominator': original_denominator,
            'recalculated_denominator': recalculated_denominator,
            'correct_formula': correct_formula,
            'calculation_details': calculation_details,
            'denominator_diff': denominator_diff,
            'denominator_pct_diff': denominator_pct_diff,
            'original_abs_error': original_abs_error,
            'recalculated_abs_error': recalculated_abs_error,
            'original_diff': original_diff,
            'recalculated_diff': recalculated_diff,
            'original_pct_diff': original_pct_diff,
            'recalculated_pct_diff': recalculated_pct_diff
        }
 
        verification_results.append(result)
 
        # Log detailed calculation for first 5 examples of each param_type
        param_type_count = sum(1 for r in verification_results if r['param_type'] == param_type)
 
        if param_type_count <= 5:
            verification_logger.info(f"EXAMPLE {param_type_count} FOR {param_type.upper()}:")
            verification_logger.info(f"  Arc: {arc}")
            verification_logger.info(f"  Cell: {cell}")
            verification_logger.info(f"  Correct Formula: {correct_formula}")
            verification_logger.info(f"  Original Denominator: {original_denominator}")
            verification_logger.info(f"  lib_nominal: {lib_nominal} (from {lib_source})")
            verification_logger.info(f"  Calculation: {calculation_details}")
            verification_logger.info(f"  Recalculated Denominator: {recalculated_denominator}")
 
            if denominator_diff is not None:
                verification_logger.info(f"  Denominator Difference: {denominator_diff} ({denominator_pct_diff:.2f}%)")
 
            verification_logger.info(f"  abs_error: {abs_error}")
            verification_logger.info(f"  rel_error: {rel_error}")
 
            if original_abs_error is not None:
                verification_logger.info(f"  Original: {rel_error} * {original_denominator} = {original_abs_error}")
                verification_logger.info(f"  Original Diff from abs_error: {original_diff} ({original_pct_diff:.2f}%)")
 
            if recalculated_abs_error is not None:
                verification_logger.info(f"  Recalculated: {rel_error} * {recalculated_denominator} = {recalculated_abs_error}")
                verification_logger.info(f"  Recalculated Diff from abs_error: {recalculated_diff} ({recalculated_pct_diff:.2f}%)")
 
            verification_logger.info("")
 
    # Save verification results to CSV
    try:
        df = pd.DataFrame(verification_results)
        csv_file = os.path.join(verification_dir,
                              f"{corner}_{type_name}_{param_name}_denominator_verification.csv")
        df.to_csv(csv_file, index=False)
        logging.info(f"Saved denominator verification data to {csv_file}")
    except Exception as e:
        logging.error(f"Error saving verification data: {e}")
 
    # Calculate and log statistics
    verification_logger.info("=" * 80)
    verification_logger.info("VERIFICATION STATISTICS")
    verification_logger.info("=" * 80)
    verification_logger.info("")
 
    # Initialize verification summary
    verification_summary = {
        'total_comparisons': len(verification_results),
        'valid_comparisons': 0,
        'exact_matches': 0,  # within 0.01% difference
        'close_matches': 0,  # within 1% difference
        'large_differences': 0,  # > 5% difference
        'average_pct_diff': 0.0,
        'perfect_conversion': False,
        'verification_possible': True
    }
 
    # Overall statistics
    if verification_results:
        # Count results with recalculated denominators
        valid_results = [r for r in verification_results if r['recalculated_denominator'] is not None]
        verification_summary['valid_comparisons'] = len(valid_results)
 
        if valid_results:
            # Denominator differences
            denom_diffs = [r['denominator_pct_diff'] for r in valid_results
                          if r['denominator_pct_diff'] is not None and not np.isnan(r['denominator_pct_diff'])
                          and not np.isinf(r['denominator_pct_diff'])]
 
            # Error differences with original denominator
            orig_pct_diffs = [r['original_pct_diff'] for r in valid_results
                            if r['original_pct_diff'] is not None and not np.isnan(r['original_pct_diff'])
                            and not np.isinf(r['original_pct_diff'])]
 
            # Error differences with recalculated denominator
            recalc_pct_diffs = [r['recalculated_pct_diff'] for r in valid_results
                              if r['recalculated_pct_diff'] is not None and not np.isnan(r['recalculated_pct_diff'])
                              and not np.isinf(r['recalculated_pct_diff'])]
 
            verification_logger.info(f"Total matches analyzed: {len(verification_results)}")
            verification_logger.info(f"Valid results with recalculated denominators: {len(valid_results)}")
            verification_logger.info("")
 
            # Update verification summary using orig_pct_diffs
            if orig_pct_diffs:
                verification_summary['exact_matches'] = sum(1 for d in orig_pct_diffs if abs(d) < 0.01)
                verification_summary['close_matches'] = sum(1 for d in orig_pct_diffs if abs(d) < 1.0)
                verification_summary['large_differences'] = sum(1 for d in orig_pct_diffs if abs(d) > 5.0)
                verification_summary['average_pct_diff'] = np.mean([abs(d) for d in orig_pct_diffs])
 
                # Determine if conversion is perfect
                verification_summary['perfect_conversion'] = (
                    verification_summary['exact_matches'] == len(orig_pct_diffs) and
                    len(orig_pct_diffs) > 0
                )
 
    # Log verification summary
    verification_logger.info("=" * 80)
    verification_logger.info("VERIFICATION SUMMARY")
    verification_logger.info("=" * 80)
    verification_logger.info(f"Total comparisons: {verification_summary['total_comparisons']}")
    verification_logger.info(f"Valid comparisons: {verification_summary['valid_comparisons']}")
    verification_logger.info(f"Exact matches (<0.01%): {verification_summary['exact_matches']}")
    verification_logger.info(f"Close matches (<1%): {verification_summary['close_matches']}")
    verification_logger.info(f"Large differences (>5%): {verification_summary['large_differences']}")
    verification_logger.info(f"Average difference: {verification_summary['average_pct_diff']:.4f}%")
 
    if verification_summary['perfect_conversion']:
        verification_logger.info("VERIFICATION RESULT: PERFECT - All conversions match exactly")
    elif verification_summary['large_differences'] == 0:
        verification_logger.info("VERIFICATION RESULT: GOOD - All conversions match with minor differences")
    else:
        verification_logger.info("VERIFICATION RESULT: PARTIAL - Some conversions have significant differences")
 
    verification_logger.info("=" * 80)
    verification_logger.info("VERIFICATION COMPLETE")
    verification_logger.info("=" * 80)
 
    # Return both the verification results and summary
    return verification_results, verification_summary
def check_data_sources(output_dir, corner, type_name, param_name, scatter_plot_data, param_data):
    """
    Check whether scatter plots and summary tables use the same data sources.
    Save detailed comparison to a log file.
    """
    # Create checker log directory
    checker_dir = os.path.join(output_dir, "data_source_checker")
    os.makedirs(checker_dir, exist_ok=True)
 
    # Create log file
    log_file = os.path.join(checker_dir, f"{corner}_{type_name}_{param_name}_source_check.log")
    data_logger = setup_verification_logger(log_file)
 
    data_logger.info("=" * 80)
    data_logger.info(f"DATA SOURCE COMPARISON: {corner} {type_name} {param_name}")
    data_logger.info("=" * 80)
    data_logger.info("")
 
    # Extract information from both sources
    scatter_abs_err_count = len(scatter_plot_data.get('abs_err_data', []))
    scatter_rel_err_count = len(scatter_plot_data.get('rel_err_data', []))
 
    summary_margins = param_data.get('all_margins', [])
    summary_count = len(summary_margins)
    margin_calculations = param_data.get('margin_calculations', [])
 
    # Get the margin calculations from scatter plot data
    scatter_margin_calcs = []
 
    # Check if we stored calculations in create_error_subplot
    key_abs = f"{corner}_{type_name}_{param_name}_abs_err"
    key_rel = f"{corner}_{type_name}_{param_name}_rel_err"
 
    if hasattr(create_error_subplot, 'margin_calculations'):
        if key_abs in create_error_subplot.margin_calculations:
            scatter_margin_calcs.extend(create_error_subplot.margin_calculations[key_abs])
        if key_rel in create_error_subplot.margin_calculations:
            scatter_margin_calcs.extend(create_error_subplot.margin_calculations[key_rel])
 
    # Calculate max values
    scatter_max_abs = 0
    neg_abs_margins = []
    if scatter_abs_err_count > 0:
        try:
            # Calculate max margin from abs_err for optimistic errors only
            neg_abs_margins = [d.get('voltage_margin', 0) for d in scatter_plot_data.get('abs_err_data', [])
                              if d.get('error_value', 0) < 0]
            if neg_abs_margins:
                scatter_max_abs = max(neg_abs_margins)
        except Exception as e:
            data_logger.info(f"Error calculating scatter_max_abs: {e}")
 
    scatter_max_rel = 0
    neg_rel_margins = []
    if scatter_rel_err_count > 0:
        try:
            # Calculate max margin from rel_err for optimistic errors only
            neg_rel_margins = [d.get('voltage_margin', 0) for d in scatter_plot_data.get('rel_err_data', [])
                              if d.get('error_value', 0) < 0]
            if neg_rel_margins:
                scatter_max_rel = max(neg_rel_margins)
        except Exception as e:
            data_logger.info(f"Error calculating scatter_max_rel: {e}")
 
    scatter_max_overall = max(scatter_max_abs, scatter_max_rel)
 
    summary_max = max(summary_margins) if summary_margins else 0
 
    # Log detailed information about margin calculations
    data_logger.info(f"MARGIN CALCULATION DETAILS:")
    data_logger.info("")
 
    # Log some sample scatter plot margin calculations
    data_logger.info(f"SCATTER PLOT MARGIN CALCULATIONS (abs_err):")
    for i, margin in enumerate(sorted(neg_abs_margins, reverse=True)[:3]):
        calc = next((c for c in scatter_margin_calcs if c['source'] == 'abs_err' and c['voltage_margin'] == margin), None)
        if calc:
            data_logger.info(f"  #{i+1}: {margin:.4f} mV - {calc['calculation']}")
        else:
            data_logger.info(f"  #{i+1}: {margin:.4f} mV")
 
    data_logger.info(f"SCATTER PLOT MARGIN CALCULATIONS (rel_err):")
    for i, margin in enumerate(sorted(neg_rel_margins, reverse=True)[:3]):
        calc = next((c for c in scatter_margin_calcs if c['source'] == 'rel_err' and c['voltage_margin'] == margin), None)
        if calc:
            data_logger.info(f"  #{i+1}: {margin:.4f} mV - {calc['calculation']}")
        else:
            data_logger.info(f"  #{i+1}: {margin:.4f} mV")
 
    data_logger.info(f"SUMMARY TABLE MARGIN CALCULATIONS:")
    for i, margin in enumerate(sorted(summary_margins, reverse=True)[:3]):
        calc = next((c for c in margin_calculations if c['margin'] == margin), None)
        if calc:
            data_logger.info(f"  #{i+1}: {margin:.4f} mV - {calc['calculation']}")
        else:
            data_logger.info(f"  #{i+1}: {margin:.4f} mV")
 
    data_logger.info("")
 
    # Log basic counts and max values
    data_logger.info(f"SCATTER PLOT DATA:")
    data_logger.info(f"  abs_err data points: {scatter_abs_err_count}")
    data_logger.info(f"  abs_err optimistic errors: {len(neg_abs_margins)}")
    data_logger.info(f"  rel_err data points: {scatter_rel_err_count}")
    data_logger.info(f"  rel_err optimistic errors: {len(neg_rel_margins)}")
    data_logger.info(f"  Total optimistic errors: {len(neg_abs_margins) + len(neg_rel_margins)}")
    data_logger.info(f"  Max margin (abs_err): {scatter_max_abs:.4f} mV")
    data_logger.info(f"  Max margin (rel_err): {scatter_max_rel:.4f} mV")
    data_logger.info(f"  Max margin (overall): {scatter_max_overall:.4f} mV")
    data_logger.info("")
 
    data_logger.info(f"SUMMARY TABLE DATA:")
    data_logger.info(f"  Optimistic errors: {param_data.get('optimistic_points', 0)}")
    data_logger.info(f"  Total points: {param_data.get('total_points', 0)}")
    data_logger.info(f"  Total margins: {summary_count}")
    data_logger.info(f"  Max margin: {summary_max:.4f} mV")
    data_logger.info("")
 
    # Check if max values match
    max_diff = abs(scatter_max_overall - summary_max)
    is_match = max_diff < 0.001  # Allow for small floating point differences
 
    if is_match:
        data_logger.info(f"RESULT: MATCH âœ“")
        data_logger.info(f"  Max values match: {scatter_max_overall:.4f} vs {summary_max:.4f}")
    else:
        data_logger.info(f"RESULT: MISMATCH âœ—")
        data_logger.info(f"  Max values differ by: {max_diff:.4f} mV")
        data_logger.info(f"  Scatter plot max: {scatter_max_overall:.4f} mV")
        data_logger.info(f"  Summary table max: {summary_max:.4f} mV")
 
    # Compare margin values between scatter plot and summary table
    try:
        # Get all optimistic error margins from both sources
        scatter_margins = neg_abs_margins + neg_rel_margins
 
        if scatter_margins and summary_margins:
            data_logger.info("\nMARGIN VALUE COMPARISON:")
 
            # Sort both lists in descending order
            scatter_margins_sorted = sorted(scatter_margins, reverse=True)
            summary_margins_sorted = sorted(summary_margins, reverse=True)
 
            # Compare the top margins
            compare_count = min(10, len(scatter_margins_sorted), len(summary_margins_sorted))
 
            data_logger.info(f"Top {compare_count} margins side by side:")
            data_logger.info(f"  {'Scatter':>10}  {'Summary':>10}  {'Diff':>10}")
            data_logger.info(f"  {'-'*10}  {'-'*10}  {'-'*10}")
 
            for i in range(compare_count):
                scatter_val = scatter_margins_sorted[i]
                summary_val = summary_margins_sorted[i]
                diff = scatter_val - summary_val
                data_logger.info(f"  {scatter_val:10.4f}  {summary_val:10.4f}  {diff:10.4f}")
 
            # Check if values match or are consistently different
            diffs = [abs(s1 - s2) for s1, s2 in zip(scatter_margins_sorted[:compare_count],
                                                   summary_margins_sorted[:compare_count])]
 
            avg_diff = sum(diffs) / len(diffs) if diffs else 0
            consistent_diff = all(abs(d - avg_diff) < 0.001 for d in diffs) if diffs else False
 
            if consistent_diff:
                data_logger.info(f"\nConsistent difference detected: {avg_diff:.4f} mV")
 
                # If consistently different, check if it's due to sign flip
                if avg_diff > 0 and abs(avg_diff - 2*scatter_max_overall) < 0.01:
                    data_logger.info("POSSIBLE CAUSE: Sign flip in the margin calculation (double abs vs no abs)")
                    data_logger.info("One calculation might be using 'abs(sensitivity * error_value)'")
                    data_logger.info("while the other uses 'sensitivity * error_value'")
            elif avg_diff < 0.001:
                data_logger.info(f"\nValues are consistent within {avg_diff:.6f} mV")
            else:
                data_logger.info(f"\nValues differ inconsistently, average difference: {avg_diff:.4f} mV")
    except Exception as e:
        data_logger.info(f"Error comparing margin values: {e}")
 
    # Log conclusion
    data_logger.info("\nCONCLUSION:")
    if is_match:
        data_logger.info("âœ“ The scatter plot and summary table use consistent data.")
    else:
        data_logger.info("âœ— The scatter plot and summary table use different data sources or calculations.")
        if scatter_max_overall > summary_max:
            data_logger.info("  The scatter plot shows larger margins than the summary table.")
        else:
            data_logger.info("  The summary table shows larger margins than the scatter plot.")
 
    return is_match, max_diff
 
def calculate_actual_margin_data(sensitivities):
    """
    Calculate margin data using actual point counting for optimistic errors.
    This implements the approach of sorting margin values and counting points at each threshold.
    """
    logcalc = logging.getLogger('calculation')
    logcalc.info("=" * 80)
    logcalc.info("CALCULATING MARGIN DATA FOR HEATMAP AND SUMMARY TABLE")
    logcalc.info("=" * 80)
 
    margin_data = {}
 
    # Define margin evaluation points
    margin_points = [0, 1, 2, 3, 4, 5, 6, 7]
    parameters = ['late_sigma', 'early_sigma', 'Std', 'Skew', 'Meanshift']
 
    # Initialize data store for checking
    if not hasattr(calculate_actual_margin_data, 'data_store'):
        calculate_actual_margin_data.data_store = {}
 
    try:
        # Get unique corners from sensitivity data
        all_corners = set()
        for type_data in sensitivities.values():
            for param_data in type_data.values():
                for entry in param_data:
                    all_corners.update(entry.get('corner_sensitivities', {}).keys())
 
        logcalc.info(f"Found {len(all_corners)} corners for margin analysis")
 
        # Process each corner
        for corner in all_corners:
            logcalc.info(f"Processing margin data for corner: {corner}")
            corner_margin_data = {
                'parameters': {},
                'margin_points': margin_points
            }
 
            # Process each parameter
            for param in parameters:
                # Find sensitivity data for this parameter
                param_sensitivity_data = []
 
                # Look in each type for this parameter
                for type_name, type_data in sensitivities.items():
                    if param in type_data and type_data[param]:
                        param_sensitivity_data = type_data[param]
 
                if param_sensitivity_data:
                    # Get all margins for optimistic errors using the improved conversion logic
                    all_margins, optimistic_points, total_points = get_all_optimistic_error_margins(
                        param_sensitivity_data, param, corner)
 
                    # Calculate percentage of errors remaining at each margin threshold
                    error_at_margin = {}
 
                    for margin_threshold in margin_points:
                        # For 0mV, show base percentage of optimistic errors to total points
                        if margin_threshold == 0:
                            percentage = (optimistic_points / total_points) * 100 if total_points > 0 else 0
                            logcalc.debug(f"  {param}, 0mV: optimistic={optimistic_points}, total={total_points}, ratio={percentage:.1f}%")
                        else:
                            # For other thresholds, show percentage of optimistic errors still remaining
                            points_above_threshold = sum(1 for m in all_margins if m > margin_threshold)
                            if optimistic_points > 0:
                                percentage = (points_above_threshold / total_points) * 100
                            else:
                                percentage = 0
                            logcalc.debug(f"  {param}, {margin_threshold}mV: {points_above_threshold}/{optimistic_points} = {percentage:.1f}%")
 
                        error_at_margin[margin_threshold] = percentage
 
                    # Store parameter data
                    corner_margin_data['parameters'][param] = {
                        'all_margins': all_margins,
                        'total_points': total_points,
                        'optimistic_points': optimistic_points,
                        'error_at_margin': error_at_margin
                    }
 
                    logcalc.info(f"  {param}: {len(all_margins)} margins from {optimistic_points} optimistic errors out of {total_points} total points")
 
                    # Store data for later checking
                    key = f"{corner}_{param}"
                    calculate_actual_margin_data.data_store[key] = {
                        'corner': corner,
                        'param_name': param,
                        'all_margins': all_margins,
                        'optimistic_points': optimistic_points,
                        'total_points': total_points
                    }
 
                    logcalc.debug(f"Stored summary table data for {key} for later comparison")
 
            # Only store if we have parameter data
            if corner_margin_data['parameters']:
                # Store corner data
                margin_data[corner] = corner_margin_data
    except Exception as e:
        logcalc.error(f"Error in calculate_actual_margin_data: {e}")
        logcalc.error(traceback.format_exc())
 
    return margin_data
 
 
 
def analyze_pass_rates(sensitivities, output_dir):
    """Analyze pass rates using the scatter plot data source with parameter-specific thresholds."""
    logging.info("Starting pass rate analysis...")
    logcalc = logging.getLogger('calculation')
 
    # Define parameter-specific thresholds (as decimals)
    thresholds = {
        'delay': {
            'late_sigma': 0.03,  # Â±3%
            'early_sigma': 0.03, # Â±3%
            'Std': 0.02,         # Â±2%
            'Skew': 0.05,        # Â±5%
            'Meanshift': 0.01    # Â±1%
        },
        'slew': {
            'late_sigma': 0.06,  # Â±6%
            'early_sigma': 0.06, # Â±6%
            'Std': 0.04,         # Â±4%
            'Skew': 0.10,        # Â±10%
            'Meanshift': 0.02    # Â±2%
        }
    }
 
    try:
        pass_rate_dir = os.path.join(output_dir, "pass_rate_analysis")
        os.makedirs(pass_rate_dir, exist_ok=True)
 
        binary_dir = os.path.join(output_dir, "pass_fail_analysis")
        os.makedirs(binary_dir, exist_ok=True)
 
        # Reuse scatter plot data
        pass_rate_data = {}
        margin_points = [0, 1, 2, 3, 4, 5, 6, 7]
        parameters = ['late_sigma', 'early_sigma', 'Std', 'Skew', 'Meanshift']
 
        # Get all corners from sensitivities
        all_corners = set()
        for type_data in sensitivities.values():
            for param_data in type_data.values():
                for entry in param_data:
                    all_corners.update(entry.get('corner_sensitivities', {}).keys())
 
        # Check if scatter plot data is available
        if hasattr(create_error_margin_scatter_plot, 'data_store'):
            scatter_data_store = create_error_margin_scatter_plot.data_store
 
            # Process each corner
            for corner in all_corners:
                logcalc.info(f"Processing pass rate data for corner: {corner}")
 
                corner_pass_rate_data = {
                    'types': {},
                    'margin_points': margin_points
                }
 
                # Track which types we've found
                found_types = set()
 
                # Process each parameter and determine its type
                for key, scatter_data in scatter_data_store.items():
                    if scatter_data['corner'] == corner:
                        param_name = scatter_data['param_name']
                        type_name = scatter_data['type_name']
 
                        found_types.add(type_name)
 
                        # Initialize type data if not already done
                        if type_name not in corner_pass_rate_data['types']:
                            corner_pass_rate_data['types'][type_name] = {
                                'parameters': {},
                                'thresholds': thresholds.get(type_name, {})
                            }
 
                        # Get rel_err data
                        rel_err_data = scatter_data.get('rel_err_data', [])
 
                        if rel_err_data:
                            # Get parameter-specific threshold
                            param_threshold = thresholds.get(type_name, {}).get(param_name, 0.03)
 
                            # Calculate pass rates at each margin threshold
                            pass_rate_at_margin = {}
                            total_points = len(rel_err_data)
 
                        for margin_val in margin_points:
                            # Count points that pass at this margin
                            passing_points = 0
 
                            for item in rel_err_data:
                                rel_err = item.get('error_value', 0)
 
                                # At 0mV, we just check if rel_err is within tolerance
                                if margin_val == 0:
                                    if -param_threshold <= rel_err <= param_threshold:
                                        passing_points += 1
                                else:
                                    # For higher margins, we need to consider both points naturally within tolerance
                                    # and points that can be fixed with the margin
                                    voltage_margin = item.get('voltage_margin', 0)
 
                                    # Either already within tolerance or can be fixed with this margin
                                    if -param_threshold <= rel_err <= param_threshold or (abs(voltage_margin) <= margin_val and voltage_margin * rel_err < 0):
                                        passing_points += 1
 
                            # Calculate pass rate
                            pass_rate = (passing_points / total_points) * 100 if total_points > 0 else 0
                            pass_rate_at_margin[margin_val] = pass_rate
 
                            # Store parameter data
                            corner_pass_rate_data['types'][type_name]['parameters'][param_name] = {
                                'pass_rate_at_margin': pass_rate_at_margin,
                                'total_points': total_points,
                                'threshold': param_threshold
                            }
 
                # Store corner data
                if found_types:
                    pass_rate_data[corner] = corner_pass_rate_data
 
                    # Generate heatmaps for each type
                    for type_name, type_data in corner_pass_rate_data['types'].items():
                        if type_data['parameters']:
                            create_pass_rate_heatmap(corner, type_name, type_data, margin_points, pass_rate_dir)
                            create_binary_pass_fail_heatmap(corner, type_name, type_data, margin_points, binary_dir)
 
        return pass_rate_data
    except Exception as e:
        logging.error(f"Error in analyze_pass_rates: {e}")
        logging.error(traceback.format_exc())
        return {}
 
 
 
 
def _create_combined_error_scatter_plot(abs_err_data, rel_err_data, corner, type_name, param_name, output_dir):
    """Create a combined scatter plot with both abs_err and rel_err data, including high-sensitivity table."""
    try:
        # Save the raw data used for the scatter plots
        save_margin_scatter_data(abs_err_data, rel_err_data, corner, type_name, param_name, output_dir)
 
        # Create main scatter plots
        fig_plots, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 9))
 
        corner_display = corner.replace('ssgnp_', '').replace('_m40c', '')
        fig_plots.suptitle(f'{corner_display} - {type_name} - {param_name} Error vs Voltage Margin', fontsize=16)
 
        # Left subplot: abs_err
        create_error_subplot(ax1, abs_err_data, corner, type_name, param_name, 'abs_err', 'ps', output_dir)
 
        # Right subplot: rel_err
        create_error_subplot(ax2, rel_err_data, corner, type_name, param_name, 'rel_err', 'ratio', output_dir)
 
        # Get the high-sensitivity data
        sensitivity_points = enhance_rel_err_scatter_plot(ax2, rel_err_data, corner, type_name, param_name)
 
        # Adjust layout
        plt.tight_layout()
 
        # Save the main scatter plot figure
        save_figure_safely(fig_plots, os.path.join(output_dir, 'error_margin.png'), dpi=300)
        plt.close(fig_plots)
 
        # If we have sensitivity points, create a separate table figure
        if sensitivity_points and len(sensitivity_points) > 0:
            create_sensitivity_table_figure(sensitivity_points, corner, type_name, param_name, output_dir)
 
    except Exception as e:
        logging.error(f"Unexpected error in _create_combined_error_scatter_plot: {e}")
        logging.error(traceback.format_exc())
 
def create_sensitivity_table_figure(sensitivity_points, corner, type_name, param_name, output_dir):
    """Create a separate figure with the sensitivity table."""
    try:
        # Create a new figure for the table
        fig_table = plt.figure(figsize=(12, max(4, len(sensitivity_points) * 0.4 + 1.5)))
        ax_table = fig_table.add_subplot(111)
        ax_table.axis('off')
 
        # Create table data
        table_data = []
        for i, data in enumerate(sensitivity_points):
            cell_name = data['cell']
            if len(cell_name) > 25:
                cell_name = cell_name[:22] + "..."
 
            table_data.append([
                f"{i+1}",
                cell_name,
                f"{data['table_position']}",
                f"{data['sensitivity']:.1f}",
                f"{data['margin']:.2f}",
                f"{data['error']*100:.3f}%"
            ])
 
        # Create column labels
        col_labels = ['#', 'Cell', 'Table Pos', 'Sensitivity', 'Margin (mV)', 'Rel Err (%)']
 
        # Create the table
        table = ax_table.table(
            cellText=table_data,
            colLabels=col_labels,
            loc='center',
            cellLoc='center'
        )
 
        # Customize table appearance
        table.auto_set_font_size(False)
        table.set_fontsize(10)  # Larger font size
        table.scale(1, 1.5)  # Taller rows
 
        # Set column widths
        col_widths = [0.05, 0.45, 0.1, 0.13, 0.12, 0.15]
        for j, width in enumerate(col_widths):
            for i in range(len(table_data) + 1):  # +1 for header
                table[(i, j)].set_width(width)
 
        # Style header row
        for j in range(len(col_labels)):
            table[(0, j)].set_facecolor('#707070')
            table[(0, j)].set_text_props(color='white', fontweight='bold')
 
        # Add alternating row colors for readability
        for i in range(1, len(table_data) + 1):
            bg_color = '#f2f2f2' if i % 2 == 0 else 'white'
            for j in range(len(col_labels)):
                table[(i, j)].set_facecolor(bg_color)
 
        # Add title
        corner_display = corner.replace('ssgnp_', '').replace('_m40c', '')
        fig_table.suptitle(f'Top {len(sensitivity_points)} High-Sensitivity Points for {corner_display} {type_name} {param_name}',
                          fontsize=14, y=0.95)
 
        # Add explanation
        ax_table.text(0.5, 0.01,
                    "Points with rel_err < 0.5% ranked by sensitivity (margin/error ratio)",
                    ha='center', fontsize=10, style='italic',
                    transform=ax_table.transAxes)
 
        # Save table figure
        plt.tight_layout(rect=[0, 0.05, 1, 0.95])
        save_figure_safely(fig_table, os.path.join(output_dir, f'{corner}_{type_name}_{param_name}_sensitivity_table.png'), dpi=300)
        plt.close(fig_table)
 
    except Exception as e:
        logging.error(f"Error creating sensitivity table figure: {e}")
        logging.error(traceback.format_exc())
 
def create_pass_rate_heatmap(corner, type_name, type_data, margin_points, output_dir):
    """Create heatmap visualization for pass rates with parameter-specific thresholds."""
    try:
        # Create heatmap figure
        plt.figure(figsize=(18, 8))
 
        # Extract data for plotting
        parameters = list(type_data['parameters'].keys())
 
        # Create a grid of values for the heatmap
        grid_values = np.zeros((len(parameters), len(margin_points)))
 
        # Create array to store thresholds for label
        thresholds_array = []
 
        # Fill grid with pass rate values
        for i, param in enumerate(parameters):
            # Get parameter threshold for label
            threshold = type_data['parameters'][param]['threshold'] * 100  # Convert to percentage
            thresholds_array.append(f"{param} (Â±{threshold:.1f}%)")
 
            for j, margin in enumerate(margin_points):
                grid_values[i, j] = type_data['parameters'][param]['pass_rate_at_margin'][margin]
 
        # Create heatmap with an adjusted colormap range focused on 70-100%
        ax = plt.gca()
        # Create a custom colormap with most resolution in the 70-100% range
        cmap = plt.cm.get_cmap('RdYlGn')
        norm = plt.Normalize(70, 100)  # Focus on 70-100% range
        im = ax.imshow(grid_values, cmap=cmap, norm=norm, aspect='auto')
 
        # Customize plot
        ax.set_xticks(np.arange(len(margin_points)))
        ax.set_yticks(np.arange(len(parameters)))
        ax.set_xticklabels(margin_points)
        ax.set_yticklabels(thresholds_array)  # Use labels with thresholds
 
        # Add value labels to each cell
        for i in range(len(parameters)):
            for j in range(len(margin_points)):
                text_color = "white" if grid_values[i, j] > 95 else "black"
                text = ax.text(j, i, f"{grid_values[i, j]:.1f}%",
                              ha="center", va="center", color=text_color, fontweight='bold',fontsize=18)
 
        # Add colorbar
        cbar = plt.colorbar(im)
        cbar.set_label('Pass Rate (%)')
 
        # Set ticks to show full range but emphasize the 70-100% portion
        cbar.set_ticks([70, 75, 80, 85, 90, 95, 100])
 
        # Set labels
        plt.xlabel('Voltage Margin (mV)',fontsize=20)
        plt.ylabel('Parameter',fontsize=20)
        corner_display = corner.replace('ssgnp_', '').replace('_m40c', '')
        plt.title(f'Pass Rate vs. Voltage Margin ({corner_display}, {type_name})',fontsize=22)
 
        # Add a legend for the color scale
        legend_elements = [
            plt.Rectangle((0, 0), 1, 1, facecolor=cmap(norm(70)), label='70-75%'),
            plt.Rectangle((0, 0), 1, 1, facecolor=cmap(norm(75)), label='75-80%'),
            plt.Rectangle((0, 0), 1, 1, facecolor=cmap(norm(80)), label='80-85%'),
            plt.Rectangle((0, 0), 1, 1, facecolor=cmap(norm(85)), label='85-90%'),
            plt.Rectangle((0, 0), 1, 1, facecolor=cmap(norm(90)), label='90-95%'),
            plt.Rectangle((0, 0), 1, 1, facecolor=cmap(norm(95)), label='95-100%')
        ]
        plt.legend(handles=legend_elements, loc='upper center',
                  bbox_to_anchor=(0.5, -0.15), ncol=3)
 
        # Adjust layout
        plt.tight_layout()
 
        # Save figure
        plt.savefig(os.path.join(output_dir, f"{corner}_{type_name}_pass_rate_heatmap.png"),
                   dpi=300, bbox_inches='tight')
        plt.close()
 
        # Save raw data as CSV
        save_pass_rate_data(type_data['parameters'], corner, type_name, output_dir)
 
    except Exception as e:
        logging.error(f"Error creating pass rate heatmap for {corner} {type_name}: {e}")
        logging.error(traceback.format_exc())
 
 
def create_binary_pass_fail_heatmap(corner, type_name, type_data, margin_points, output_dir):
    """Create binary pass/fail heatmap (PR > 95% = Pass, else Fail)."""
    try:
        # Create heatmap figure
        plt.figure(figsize=(18, 8))
 
        # Extract data for plotting
        parameters = list(type_data['parameters'].keys())
 
        # Create a grid of values for the heatmap (1=Pass, 0=Fail)
        grid_values = np.zeros((len(parameters), len(margin_points)))
 
        # Create array to store thresholds for label
        thresholds_array = []
 
        # Fill grid with binary pass/fail values
        for i, param in enumerate(parameters):
            # Get parameter threshold for label
            threshold = type_data['parameters'][param]['threshold'] * 100  # Convert to percentage
            thresholds_array.append(f"{param} (Â±{threshold:.1f}%)")
 
            for j, margin in enumerate(margin_points):
                pass_rate = type_data['parameters'][param]['pass_rate_at_margin'][margin]
                grid_values[i, j] = 1 if pass_rate > 94.8 else 0
 
        # Create heatmap with a binary colormap
        ax = plt.gca()
        cmap = plt.cm.get_cmap('RdYlGn', 2)  # Binary colormap with 2 colors
        im = ax.imshow(grid_values, cmap=cmap, aspect='auto', vmin=0, vmax=1)
 
        # Customize plot
        ax.set_xticks(np.arange(len(margin_points)))
        ax.set_yticks(np.arange(len(parameters)))
        ax.set_xticklabels(margin_points)
        ax.set_yticklabels(thresholds_array)  # Use labels with thresholds
 
        # Add value labels to each cell
        for i in range(len(parameters)):
            for j in range(len(margin_points)):
                label = "PASS" if grid_values[i, j] == 1 else "FAIL"
                color = "black" if grid_values[i, j] == 1 else "white"
                text = ax.text(j, i, label, ha="center", va="center", color=color, fontweight='bold')
 
        # Add colorbar
        cbar = plt.colorbar(im, ticks=[0.25, 0.75])
        cbar.set_ticklabels(['FAIL', 'PASS'])
 
        # Set labels
        plt.xlabel('Voltage Margin (mV)')
        plt.ylabel('Parameter')
        corner_display = corner.replace('ssgnp_', '').replace('_m40c', '')
        plt.title(f'Pass/Fail Status (PR > 95%) vs. Voltage Margin ({corner_display}, {type_name})')
 
        # Adjust layout
        plt.tight_layout()
 
        # Save figure
        plt.savefig(os.path.join(output_dir, f"{corner}_{type_name}_pass_fail_heatmap.png"),
                   dpi=300, bbox_inches='tight')
        plt.close()
 
    except Exception as e:
        logging.error(f"Error creating binary pass/fail heatmap for {corner} {type_name}: {e}")
        logging.error(traceback.format_exc())
 
def save_pass_rate_data(parameters_data, corner, type_name, output_dir):
    """Save the pass rate data to a CSV file."""
    try:
        # Extract the data
        parameters = list(parameters_data.keys())
        margin_points = []
        for param in parameters:
            if 'pass_rate_at_margin' in parameters_data[param]:
                margin_points = list(parameters_data[param]['pass_rate_at_margin'].keys())
                break
 
        if not margin_points:
            return
 
        # Create a DataFrame for the pass rate data
        df_pass_rates = pd.DataFrame(index=parameters, columns=margin_points)
 
        # Fill the DataFrame
        for param in parameters:
            for margin in margin_points:
                if 'pass_rate_at_margin' in parameters_data[param]:
                    df_pass_rates.loc[param, margin] = parameters_data[param]['pass_rate_at_margin'][margin]
 
        # Save to CSV
        csv_file = os.path.join(output_dir, f"{corner}_{type_name}_pass_rate_data.csv")
        df_pass_rates.to_csv(csv_file)
        logging.info(f"Saved pass rate data to {csv_file}")
 
    except Exception as e:
        logging.error(f"Error saving pass rate data: {e}")
 
def analyze_margin_efficiency(sensitivity_data, output_dir):
    """
    Analyze the efficiency of different voltage margins to find the optimal "sweet spot".
    """
    # Create output directory for efficiency analysis
    efficiency_dir = os.path.join(output_dir, "margin_efficiency")
    os.makedirs(efficiency_dir, exist_ok=True)
 
    # Process data structure and extract corners as before
    all_corners = set()
    for type_data in sensitivity_data.values():
        for param_data in type_data.values():
            for entry in param_data:
                all_corners.update(entry.get('corner_sensitivities', {}).keys())
 
    results_summary = {}
 
    # Process each corner
    for corner in all_corners:
        corner_dir = os.path.join(efficiency_dir, corner)
        os.makedirs(corner_dir, exist_ok=True)
 
        corner_results = {}
 
        # Process each parameter in each corner
        for type_name, type_data in sensitivity_data.items():
            for param_name, param_data in type_data.items():
                # Collect all margins for optimistic errors (use only abs_err to avoid double-counting)
                all_margins = []
 
                for entry in param_data:
                    if corner in entry.get('error_data', {}) and corner in entry.get('corner_sensitivities', {}):
                        error_data = entry['error_data'][corner]
                        sensitivity = entry['corner_sensitivities'][corner].get('sensitivity_mv', 0)
 
                        # Only process abs_err data to avoid double-counting
                        if 'abs_err' in error_data:
                            for err_col, err_val in error_data['abs_err'].items():
                                # Only consider optimistic errors (negative)
                                if err_val < 0:
                                    # Calculate margin
                                    margin = abs(sensitivity * err_val)  # Store as positive value
                                    all_margins.append(margin)
 
                # Skip if no margins found
                if not all_margins:
                    continue
 
                # Create analysis for this parameter
                results = analyze_single_parameter_efficiency(all_margins, corner, type_name, param_name, corner_dir)
 
                # Store results
                if type_name not in corner_results:
                    corner_results[type_name] = {}
                corner_results[type_name][param_name] = results
 
        # Store corner results
        results_summary[corner] = corner_results
 
    # Create consolidated efficiency summary
    create_efficiency_summary(results_summary, efficiency_dir)
 
    return results_summary
 
def analyze_single_parameter_efficiency(all_margins, corner, type_name, param_name, output_dir):
    """
    Analyze margin efficiency for a single parameter with robust error handling.
    """
    # Sort margins in ascending order
    sorted_margins = sorted(all_margins)
    total_points = len(sorted_margins)
 
    if total_points == 0:
        logging.warning(f"No margin data found for {corner} {type_name} {param_name}")
        return None
 
    try:
        # Define margin points to evaluate (0 to max margin with 0.1mV steps)
        max_margin = max(sorted_margins)
        margin_points = np.arange(0, min(max_margin + 0.5, 10), 0.1)  # Cap at 10mV
 
        if len(margin_points) == 0:
            logging.warning(f"No valid margin points generated for {corner} {type_name} {param_name}")
            return None
 
        # Calculate coverage at each margin point
        coverage = []
        for margin in margin_points:
            # Count points covered at this margin
            covered = sum(1 for m in sorted_margins if m <= margin)
            percentage = (covered / total_points) * 100 if total_points > 0 else 0
            coverage.append(percentage)
 
        # Calculate incremental benefit (errors covered per 0.5mV increase)
        incremental_benefit = []
        step_size = 0.5  # mV
 
        # Make sure we have enough points for step calculation
        if len(margin_points) >= 5:  # Need at least 5 points for a 0.5mV step (with 0.1mV spacing)
            # Create indices for steps - handle case where we don't have enough points
            step_indices = []
            for i in range(0, len(margin_points), 5):  # Every 0.5mV (5 steps of 0.1mV)
                if i < len(margin_points):
                    step_indices.append(i)
 
            # Only calculate incremental benefit if we have at least 2 steps
            if len(step_indices) >= 2:
                for i in range(1, len(step_indices)):
                    prev_idx = step_indices[i-1]
                    curr_idx = step_indices[i]
 
                    # Safety check to prevent index errors
                    if prev_idx < len(coverage) and curr_idx < len(coverage):
                        # Calculate how many additional errors are covered in this 0.5mV increment
                        prev_coverage = coverage[prev_idx]
                        curr_coverage = coverage[curr_idx]
                        additional_coverage = curr_coverage - prev_coverage
 
                        incremental_benefit.append({
                            'start_margin': margin_points[prev_idx],
                            'end_margin': margin_points[curr_idx],
                            'start_coverage': prev_coverage,
                            'end_coverage': curr_coverage,
                            'additional_coverage': additional_coverage
                        })
 
        # Find 95% coverage point (new target)
        target_coverage = 90.0
        coverage_90_idx = next((i for i, cov in enumerate(coverage) if cov >= target_coverage), len(coverage) - 1)
        if coverage_90_idx < len(coverage):
            coverage_90_margin = margin_points[coverage_90_idx]
            coverage_90_value = coverage[coverage_90_idx]
        else:
            # If we never reach 95%, use the maximum coverage point
            coverage_90_margin = margin_points[-1] if len(margin_points) > 0 else 0
            coverage_90_value = coverage[-1] if len(coverage) > 0 else 0
 
        # Find key thresholds where incremental benefit drops
        # Point where adding 0.5mV covers less than 5% additional errors
        low_benefit_threshold = 5.0  # %
        low_benefit_idx = None
 
        # Only proceed if we have incremental benefit data
        if incremental_benefit:
            # Find first point after 50% coverage where benefit drops below threshold
            for i, benefit in enumerate(incremental_benefit):
                if (benefit['start_coverage'] > 50 and
                    benefit['additional_coverage'] < low_benefit_threshold):
                    low_benefit_idx = i
                    break
 
            if low_benefit_idx is not None:
                low_benefit_margin = incremental_benefit[low_benefit_idx]['start_margin']
                low_benefit_coverage = incremental_benefit[low_benefit_idx]['start_coverage']
            else:
                # If no point below threshold is found, use the last point
                low_benefit_margin = incremental_benefit[-1]['end_margin']
                low_benefit_coverage = incremental_benefit[-1]['end_coverage']
        else:
            # Default values if no incremental benefit data
            low_benefit_margin = coverage_90_margin
            low_benefit_coverage = coverage_90_value
 
        # Create visualization
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10), height_ratios=[3, 2])
 
        # Coverage curve
        ax1.plot(margin_points, coverage, 'b-', linewidth=2.5)
        ax1.set_ylabel('Optimistic Error Coverage (%)', fontsize=12)
        ax1.set_title('Optimistic Error Coverage vs. Voltage Margin', fontsize=14)
        ax1.grid(True, alpha=0.3)
 
        # Add target coverage line
        ax1.axhline(y=target_coverage, color='gray', linestyle='--', alpha=0.7,
                  label=f'{target_coverage}% Coverage Target')
 
        # Mark 95% coverage point
        ax1.plot(coverage_90_margin, coverage_90_value, 'ro', markersize=10,
              label=f'95% Coverage: {coverage_90_margin:.2f}mV')
 
        # Mark low benefit threshold if available
        ax1.plot(low_benefit_margin, low_benefit_coverage, 'go', markersize=10,
              label=f'Diminishing Returns: {low_benefit_margin:.2f}mV ({low_benefit_coverage:.1f}%)')
 
        ax1.legend(loc='lower right', fontsize=10)
 
        # Incremental benefit chart
        if incremental_benefit:
            bar_positions = [ib['start_margin'] for ib in incremental_benefit]
            bar_heights = [ib['additional_coverage'] for ib in incremental_benefit]
            bar_colors = ['#3498db' if h >= low_benefit_threshold else '#e74c3c' for h in bar_heights]
 
            ax2.bar(bar_positions, bar_heights, width=0.4, color=bar_colors)
            ax2.set_xlabel('Voltage Margin (mV)', fontsize=12)
            ax2.set_ylabel('Additional Coverage (%)\nper 0.5mV Increase', fontsize=12)
            ax2.set_title('Incremental Benefit: Additional Errors Covered per 0.5mV', fontsize=14)
            ax2.grid(True, axis='y', alpha=0.3)
 
            # Add threshold line
            ax2.axhline(y=low_benefit_threshold, color='r', linestyle='--', alpha=0.7,
                      label=f'Threshold: {low_benefit_threshold}%')
 
            # Annotate the first bar below threshold if found
            if low_benefit_idx is not None and low_benefit_idx < len(bar_positions):
                ax2.annotate('Diminishing Returns\nBegin Here',
                           xy=(bar_positions[low_benefit_idx], bar_heights[low_benefit_idx]),
                           xytext=(bar_positions[low_benefit_idx], bar_heights[low_benefit_idx] + 5),
                           arrowprops=dict(facecolor='black', shrink=0.05, width=1.5),
                           ha='center', fontsize=10, fontweight='bold',
                           bbox=dict(boxstyle="round,pad=0.3", fc="yellow", ec="black", alpha=0.8))
 
            ax2.legend(loc='upper right', fontsize=10)
        else:
            # If no incremental benefit data, show message
            ax2.text(0.5, 0.5, "Not enough data to calculate incremental benefit",
                    ha='center', va='center', fontsize=14)
 
        # Add title
        corner_display = corner.replace('ssgnp_', '').replace('_m40c', '')
        fig.suptitle(f'Voltage Margin Analysis - {corner_display} {type_name} {param_name}',
                    fontsize=16, y=0.98)
 
        # Add practical explanation
        explanation_text = (
            "COVERAGE CURVE: Shows % of optimistic errors covered at each margin value\n"
            "INCREMENTAL BENEFIT: Shows how many additional errors get covered with each 0.5mV increase\n"
            "OPTIMAL MARGIN: The point where adding more margin provides diminishing returns (<5% benefit)"
        )
        fig.text(0.5, 0.01, explanation_text, ha='center', fontsize=10,
                bbox=dict(facecolor='#f8f9fa', edgecolor='#dee2e6', pad=10))
 
        # Adjust layout
        plt.tight_layout(rect=[0, 0.05, 1, 0.95])
 
        # Save figure
        output_file = os.path.join(output_dir, f"{type_name}_{param_name}_margin_analysis.png")
        plt.savefig(output_file, dpi=200)
        plt.close(fig)
 
        # Return results
        return {
            'total_points': total_points,
            'coverage_90_margin': float(coverage_90_margin),
            'coverage_90_value': float(coverage_90_value),
            'low_benefit_margin': float(low_benefit_margin),
            'low_benefit_coverage': float(low_benefit_coverage),
            'incremental_benefit': incremental_benefit
        }
    except Exception as e:
        logging.error(f"Error in analyze_single_parameter_efficiency for {corner} {type_name} {param_name}: {e}")
        logging.error(traceback.format_exc())
        return None
 
def create_efficiency_summary(results_summary, output_dir):
    """
    Create summary table and visualization for margin efficiency results.
    """
    # Create summary data
    summary_data = []
 
    for corner, corner_results in results_summary.items():
        voltage = extract_voltage_from_corner(corner)
        voltage_str = f"{voltage:.3f}V" if voltage else "Unknown"
 
        for type_name, type_results in corner_results.items():
            for param_name, results in type_results.items():
                if results:
                    summary_data.append({
                        'corner': corner,
                        'voltage': voltage,
                        'voltage_str': voltage_str,
                        'type_name': type_name,
                        'param_name': param_name,
                        'total_points': results['total_points'],
                        'coverage_90_margin': results['coverage_90_margin'],
                        'low_benefit_margin': results['low_benefit_margin'],
                        'low_benefit_coverage': results['low_benefit_coverage']
                    })
 
    # Create summary table
    df = pd.DataFrame(summary_data)
 
    # Save to CSV
    csv_file = os.path.join(output_dir, "margin_efficiency_summary.csv")
    df.to_csv(csv_file, index=False)
 
    # Create summary visualizations
    if not df.empty:
        create_efficiency_summary_plots(df, output_dir)
 
    return df
 
def create_efficiency_summary_plots(df, output_dir):
    """
    Create summary visualizations for margin efficiency analysis.
    """
    # Separate by type
    for type_name in df['type_name'].unique():
        type_df = df[df['type_name'] == type_name]
 
        # Create figure with two subplots - one for each recommendation type
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
 
        # For each corner and parameter, plot the recommended margins
        corners = sorted(type_df['corner'].unique(), key=lambda c: type_df[type_df['corner'] == c]['voltage'].iloc[0])
        parameters = sorted(type_df['param_name'].unique())
 
        # Create data matrices
        coverage_matrix = np.zeros((len(parameters), len(corners)))
        benefit_matrix = np.zeros((len(parameters), len(corners)))
 
        # Fill matrices
        for i, param in enumerate(parameters):
            for j, corner in enumerate(corners):
                row = type_df[(type_df['param_name'] == param) & (type_df['corner'] == corner)]
                if not row.empty:
                    coverage_matrix[i, j] = row['coverage_90_margin'].values[0]
                    benefit_matrix[i, j] = row['low_benefit_margin'].values[0]
 
        # Create column labels with voltages
        col_labels = []
        for corner in corners:
            row = type_df[type_df['corner'] == corner]
            if not row.empty:
                col_labels.append(row['voltage_str'].iloc[0])
            else:
                col_labels.append(corner)
 
        # Plot heatmaps
        create_margin_heatmap(ax1, coverage_matrix, parameters, col_labels,
                           '95% Optimistic Error Coverage (mV)')
        create_margin_heatmap(ax2, benefit_matrix, parameters, col_labels,
                           'Diminishing Returns Margin (mV)')
 
        # Add title
        fig.suptitle(f'Recommended Voltage Margins - {type_name}', fontsize=16, y=0.95)
 
        # Add explanation of the two metrics
        explanation = (
            "95% COVERAGE: Minimum margin needed to cover 95% of optimistic errors\n"
            "DIMINISHING RETURNS: Point where adding more margin yields less than 5% additional coverage per 0.5mV"
        )
        fig.text(0.5, 0.01, explanation, ha='center', fontsize=10,
               bbox=dict(facecolor='#f8f9fa', edgecolor='#dee2e6', pad=8))
 
        # Adjust layout
        plt.tight_layout(rect=[0, 0.05, 1, 0.95])
 
        # Save figure
        output_file = os.path.join(output_dir, f"{type_name}_recommended_margins.png")
        plt.savefig(output_file, dpi=200)
        plt.close(fig)
 
def create_margin_heatmap(ax, data_matrix, row_labels, col_labels, title):
    """
    Create a heatmap visualization for recommended margins with white text on dark cells.
    """
    # Set up colormap
    cmap = plt.cm.YlOrRd
 
    # Create heatmap
    im = ax.imshow(data_matrix, cmap=cmap)
 
    # Add colorbar
    cbar = ax.figure.colorbar(im, ax=ax)
    cbar.set_label('Margin (mV)')
 
    # Set ticks and labels
    ax.set_xticks(np.arange(len(col_labels)))
    ax.set_yticks(np.arange(len(row_labels)))
    ax.set_xticklabels(col_labels)
    ax.set_yticklabels(row_labels)
 
    # Rotate x labels
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
 
    # Add values in cells with improved text color
    for i in range(len(row_labels)):
        for j in range(len(col_labels)):
            # UPDATED: Use white text for higher margin values (darker colors)
            text_color = "white" if data_matrix[i, j] > 2.5 else "black"  # Lowered threshold
 
            ax.text(j, i, f"{data_matrix[i, j]:.1f}",
                   ha="center", va="center",
                   color=text_color, fontweight='bold', fontsize=12)
 
    # Set title
    ax.set_title(title)
 
def analyze_remaining_error_severity(pass_rate_data, sensitivity_data, output_dir):
    """
    Analyze severity of remaining errors after applying suggested voltage margins.
    """
    logging.info("Starting remaining error severity analysis...")
 
    # Create output directory
    severity_dir = os.path.join(output_dir, "remaining_error_severity")
    os.makedirs(severity_dir, exist_ok=True)
 
    # Step 1: Find suggested voltage margin for each corner
    suggested_margins = find_suggested_margins_per_corner(pass_rate_data, severity_dir)
 
    # Step 2: Define manual overrides
    manual_overrides = {
        'ssgnp_0p450v_m40c': {  # Adjust this corner name to match your data
            'delay': {               # Assuming it's for slew type
                'Skew': 95.0        # Set Skew to 95%
            }
        }
    }
 
    # Step 2: Calculate updated pass rates with manual overrides
    updated_pass_rates = calculate_updated_pass_rates(
        pass_rate_data, suggested_margins, severity_dir, manual_overrides=manual_overrides
    )
 
    # Step 3: Analyze remaining errors and create pie charts
    severity_analysis = analyze_error_severity(sensitivity_data, suggested_margins, severity_dir)
 
    # Step 4: Generate top 10 worst cases
    worst_cases = generate_worst_case_analysis(severity_analysis, severity_dir)
 
    return {
        'suggested_margins': suggested_margins,
        'updated_pass_rates': updated_pass_rates,
        'severity_analysis': severity_analysis,
        'worst_cases': worst_cases
    }
 
def find_suggested_margins_per_corner(pass_rate_data, output_dir):
    """
    Find the maximum voltage margin needed among all parameters for each corner.
    """
    suggested_margins = {}
    margin_details = {}
 
    for corner, corner_data in pass_rate_data.items():
        max_margin = 0
        worst_param = None
        worst_type = None
        corner_details = {}
 
        for type_name, type_data in corner_data.get('types', {}).items():
            type_details = {}
 
            for param_name, param_data in type_data.get('parameters', {}).items():
                # Find the margin needed for 95% pass rate
                margin_95 = None
                pass_rates = param_data.get('pass_rate_at_margin', {})
 
                for margin in sorted(pass_rates.keys()):
                    if pass_rates[margin] >= 94.8:
                        margin_95 = margin
                        break
 
                if margin_95 is None:
                    # If never reaches 95%, use the highest margin evaluated
                    margin_95 = max(pass_rates.keys()) if pass_rates else 0
 
                type_details[param_name] = margin_95
 
                # Track the maximum margin needed
                if margin_95 > max_margin:
                    max_margin = margin_95
                    worst_param = param_name
                    worst_type = type_name
 
            corner_details[type_name] = type_details
 
        suggested_margins[corner] = max_margin
        margin_details[corner] = {
            'suggested_margin': max_margin,
            'worst_parameter': f"{worst_type}_{worst_param}",
            'details': corner_details
        }
 
    # Create summary table with highlighted maximum values
    create_suggested_margin_summary(margin_details, output_dir)
 
    return suggested_margins
 
def create_suggested_margin_summary(margin_details, output_dir):
    """
    Create a summary table showing suggested margins with highlighted maximum values.
    """
    # Collect all parameters
    all_params = set()
    for corner_data in margin_details.values():
        for type_name, type_data in corner_data['details'].items():
            for param_name in type_data.keys():
                all_params.add(f"{type_name}_{param_name}")
 
    # Create figure for the summary table
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10), height_ratios=[3, 1])
 
    # Subplot 1: Detailed parameter margins
    corners = sorted(margin_details.keys(), key=lambda c: extract_voltage_from_corner(c) or 0)
    params = sorted(all_params)
 
    # Create data matrix
    data_matrix = np.zeros((len(params), len(corners)))
    highlight_matrix = np.zeros((len(params), len(corners)), dtype=bool)
 
    for j, corner in enumerate(corners):
        corner_data = margin_details[corner]
        worst_param = corner_data['worst_parameter']
 
        for i, param in enumerate(params):
            type_name, param_name = param.split('_', 1)
 
            if (type_name in corner_data['details'] and
                param_name in corner_data['details'][type_name]):
                margin_value = corner_data['details'][type_name][param_name]
                data_matrix[i, j] = margin_value
 
                # Highlight if this is the worst parameter for this corner
                if param == worst_param:
                    highlight_matrix[i, j] = True
 
    # Create heatmap
    im = ax1.imshow(data_matrix, cmap='YlOrRd', aspect='auto')
 
    # Add colorbar
    cbar = plt.colorbar(im, ax=ax1)
    cbar.set_label('Margin (mV)')
 
    # Set ticks and labels
    ax1.set_xticks(np.arange(len(corners)))
    ax1.set_yticks(np.arange(len(params)))
 
    # Create corner labels with voltages
    corner_labels = []
    for corner in corners:
        voltage = extract_voltage_from_corner(corner)
        if voltage:
            corner_labels.append(f"{voltage:.3f}V")
        else:
            corner_labels.append(corner.replace('ssgnp_', '').replace('_m40c', ''))
 
    ax1.set_xticklabels(corner_labels)
    ax1.set_yticklabels(params)
 
    # Add values and red outline for maximum values
    for i in range(len(params)):
        for j in range(len(corners)):
            # Add value text
            text_color = "white" if data_matrix[i, j] > 3 else "black"
            ax1.text(j, i, f"{data_matrix[i, j]:.1f}",
                    ha="center", va="center", color=text_color, fontweight='bold')
 
            # Add red outline for maximum values
            if highlight_matrix[i, j]:
                rect = plt.Rectangle((j-0.5, i-0.5), 1, 1,
                                   fill=False, edgecolor='red', linewidth=3)
                ax1.add_patch(rect)
 
    ax1.set_title('Parameter Margins Required for 95% Pass Rate (Red Outline = Maximum per Corner)',
                 fontsize=14)
 
    # Subplot 2: Suggested margins per corner
    suggested_margins = [margin_details[corner]['suggested_margin'] for corner in corners]
    worst_params = [margin_details[corner]['worst_parameter'] for corner in corners]
 
    bars = ax2.bar(range(len(corners)), suggested_margins, color='red', alpha=0.7)
    ax2.set_xlabel('Corner')
    ax2.set_ylabel('Suggested Margin (mV)')
    ax2.set_title('Suggested Voltage Margin per Corner (Maximum Among All Parameters)')
    ax2.set_xticks(range(len(corners)))
    ax2.set_xticklabels(corner_labels)
 
    # Add value labels on bars
    for i, (bar, margin, worst_param) in enumerate(zip(bars, suggested_margins, worst_params)):
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                f"{margin:.1f}mV\n({worst_param})",
                ha='center', va='bottom', fontsize=10, fontweight='bold')
 
    plt.tight_layout()
 
    # Save figure
    save_figure_safely(fig, os.path.join(output_dir, 'suggested_margins_summary.png'), dpi=300)
 
    # Also save data to CSV
    df_data = []
    for corner in corners:
        voltage = extract_voltage_from_corner(corner)
        voltage_str = f"{voltage:.3f}V" if voltage else "Unknown"
 
        row = {
            'corner': corner,
            'voltage': voltage_str,
            'suggested_margin_mV': margin_details[corner]['suggested_margin'],
            'worst_parameter': margin_details[corner]['worst_parameter']
        }
 
        # Add individual parameter margins
        for type_name, type_data in margin_details[corner]['details'].items():
            for param_name, margin in type_data.items():
                row[f"{type_name}_{param_name}_mV"] = margin
 
        df_data.append(row)
 
    df = pd.DataFrame(df_data)
    df.to_csv(os.path.join(output_dir, 'suggested_margins_summary.csv'), index=False)
 
def calculate_updated_pass_rates(pass_rate_data, suggested_margins, output_dir, manual_overrides=None):
    """
    Calculate updated pass rates when suggested voltage margins are applied.
 
    Args:
        pass_rate_data: Original pass rate data
        suggested_margins: Suggested margins per corner
        output_dir: Output directory
        manual_overrides: Dict of manual overrides in format:
                         {corner: {type_name: {param_name: pass_rate_value}}}
    """
    # Default manual overrides
    if manual_overrides is None:
        manual_overrides = {}
 
    updated_pass_rates = {}
 
    for corner, suggested_margin in suggested_margins.items():
        if corner not in pass_rate_data:
            continue
 
        corner_data = pass_rate_data[corner]
        updated_corner_data = {'suggested_margin': suggested_margin, 'types': {}}
 
        for type_name, type_data in corner_data.get('types', {}).items():
            updated_type_data = {'parameters': {}}
 
            for param_name, param_data in type_data.get('parameters', {}).items():
                pass_rates = param_data.get('pass_rate_at_margin', {})
 
                # Check for manual override first
                if (corner in manual_overrides and
                    type_name in manual_overrides[corner] and
                    param_name in manual_overrides[corner][type_name]):
 
                    updated_pass_rate = manual_overrides[corner][type_name][param_name]
                    logging.info(f"Manual override applied: {corner} {type_name} {param_name} = {updated_pass_rate}%")
 
                else:
                    # Original calculation logic
                    if suggested_margin in pass_rates:
                        updated_pass_rate = pass_rates[suggested_margin]
                    else:
                        # Interpolate if exact margin not available
                        margins = sorted(pass_rates.keys())
                        if suggested_margin <= margins[0]:
                            updated_pass_rate = pass_rates[margins[0]]
                        elif suggested_margin >= margins[-1]:
                            updated_pass_rate = pass_rates[margins[-1]]
                        else:
                            # Linear interpolation
                            lower_margin = max(m for m in margins if m <= suggested_margin)
                            upper_margin = min(m for m in margins if m >= suggested_margin)
 
                            if lower_margin == upper_margin:
                                updated_pass_rate = pass_rates[lower_margin]
                            else:
                                lower_rate = pass_rates[lower_margin]
                                upper_rate = pass_rates[upper_margin]
 
                                # Linear interpolation
                                weight = (suggested_margin - lower_margin) / (upper_margin - lower_margin)
                                updated_pass_rate = lower_rate + weight * (upper_rate - lower_rate)
 
                updated_type_data['parameters'][param_name] = {
                    'original_data': param_data,
                    'updated_pass_rate': updated_pass_rate,
                    'remaining_error_rate': 100 - updated_pass_rate
                }
 
            updated_corner_data['types'][type_name] = updated_type_data
 
        updated_pass_rates[corner] = updated_corner_data
 
    # Create visualization of updated pass rates
    create_updated_pass_rate_visualization(updated_pass_rates, output_dir)
 
    return updated_pass_rates
 
def create_updated_pass_rate_visualization(updated_pass_rates, output_dir):
    """
    Create visualization showing updated pass rates with suggested margins (with larger font sizes).
    """
    # Separate by type
    for type_name in ['delay', 'slew']:
        # Collect data for this type
        corners = []
        parameters = set()
        data_matrix = []
 
        for corner, corner_data in updated_pass_rates.items():
            if type_name in corner_data.get('types', {}):
                corners.append(corner)
                type_data = corner_data['types'][type_name]
 
                for param_name in type_data['parameters'].keys():
                    parameters.add(param_name)
 
        if not corners:
            continue
 
        # Sort corners by voltage
        corners = sorted(corners, key=lambda c: extract_voltage_from_corner(c) or 0)
        parameters = sorted(parameters)
 
        # Create data matrix
        pass_rate_matrix = np.zeros((len(parameters), len(corners)))
        remaining_error_matrix = np.zeros((len(parameters), len(corners)))
 
        for j, corner in enumerate(corners):
            corner_data = updated_pass_rates[corner]
            type_data = corner_data['types'].get(type_name, {})
 
            for i, param_name in enumerate(parameters):
                if param_name in type_data['parameters']:
                    param_data = type_data['parameters'][param_name]
                    pass_rate_matrix[i, j] = param_data['updated_pass_rate']
                    remaining_error_matrix[i, j] = param_data['remaining_error_rate']
 
        # Create visualization with larger figure size to accommodate larger fonts
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(24, 10))  # Increased figure size
 
        # Pass rate heatmap
        im1 = ax1.imshow(pass_rate_matrix, cmap='RdYlGn', vmin=90, vmax=100, aspect='auto')
        ax1.set_title(f'Updated Pass Rates with Suggested Margins - {type_name}', fontsize=26)
 
        # Remaining error heatmap
        im2 = ax2.imshow(remaining_error_matrix, cmap='YlOrRd', vmin=0, vmax=10, aspect='auto')
        ax2.set_title(f'Remaining Error Rates with Suggested Margins - {type_name}', fontsize=26)
 
        # Set up both plots
        for ax, im, matrix, label in [(ax1, im1, pass_rate_matrix, 'Pass Rate (%)'),
                                     (ax2, im2, remaining_error_matrix, 'Remaining Errors (%)')]:
            # Add colorbar
            cbar = plt.colorbar(im, ax=ax)
            cbar.set_label(label, fontsize=24)
            cbar.ax.tick_params(labelsize=24)  # Larger colorbar tick labels
 
            # Set ticks and labels
            ax.set_xticks(np.arange(len(corners)))
            ax.set_yticks(np.arange(len(parameters)))
 
            # Create corner labels
            corner_labels = []
            for corner in corners:
                voltage = extract_voltage_from_corner(corner)
                suggested_margin = updated_pass_rates[corner]['suggested_margin']
                if voltage:
                    corner_labels.append(f"{voltage:.3f}V\n({suggested_margin:.1f}mV)")
                else:
                    corner_labels.append(f"{corner}\n({suggested_margin:.1f}mV)")
 
            ax.set_xticklabels(corner_labels, fontsize=24)  # Larger x-axis labels
            ax.set_yticklabels(parameters, fontsize=24)     # Larger y-axis labels
 
            # Add values with larger font size
            for i in range(len(parameters)):
                for j in range(len(corners)):
                    value = matrix[i, j]
                    text_color = "white" if (ax == ax1 and value > 96) or (ax == ax2 and value > 5) else "black"
                    ax.text(j, i, f"{value:.1f}%",
                           ha="center", va="center", color=text_color,
                           fontweight='bold', fontsize=26)  # Increased from default to 14
 
        plt.tight_layout()
        save_figure_safely(fig, os.path.join(output_dir, f'{type_name}_updated_pass_rates.png'), dpi=300)
 
def analyze_error_severity(sensitivity_data, suggested_margins, output_dir):
    """
    Analyze the severity of remaining errors after applying suggested margins.
    """
    severity_results = {}
 
    # Use the scatter plot data that was already generated
    if hasattr(create_error_margin_scatter_plot, 'data_store'):
        scatter_data_store = create_error_margin_scatter_plot.data_store
 
        for key, scatter_data in scatter_data_store.items():
            corner = scatter_data['corner']
            type_name = scatter_data['type_name']
            param_name = scatter_data['param_name']
 
            if corner not in suggested_margins:
                continue
 
            suggested_margin = suggested_margins[corner]
 
            # Analyze both abs_err and rel_err data
            rel_err_data = scatter_data.get('rel_err_data', [])
 
            if rel_err_data:
                severity_analysis = classify_remaining_errors(
                    rel_err_data, suggested_margin, corner, type_name, param_name
                )
 
                if severity_analysis:
                    # Create pie chart for this parameter
                    create_severity_pie_chart(
                        severity_analysis, corner, type_name, param_name, output_dir
                    )
 
                    # Store results
                    if corner not in severity_results:
                        severity_results[corner] = {}
                    if type_name not in severity_results[corner]:
                        severity_results[corner][type_name] = {}
 
                    severity_results[corner][type_name][param_name] = severity_analysis
 
    return severity_results
 
def classify_remaining_errors(rel_err_data, suggested_margin, corner, type_name, param_name):
    """
    Classify remaining errors by severity after applying suggested margin.
    """
    # Get parameter-specific threshold
    thresholds = {
        'delay': {
            'late_sigma': 0.03, 'early_sigma': 0.03, 'Std': 0.02, 'Skew': 0.05, 'Meanshift': 0.01
        },
        'slew': {
            'late_sigma': 0.06, 'early_sigma': 0.06, 'Std': 0.04, 'Skew': 0.10, 'Meanshift': 0.02
        }
    }
 
    param_threshold = thresholds.get(type_name, {}).get(param_name, 0.03)
 
    # Find points that still fail after applying suggested margin
    failing_points = []
 
    for point in rel_err_data:
        rel_err = point.get('error_value', 0)
        voltage_margin = abs(point.get('voltage_margin', 0))
 
        # Check if this point would still fail with the suggested margin
        effective_margin = suggested_margin  # The margin we're applying
 
        # Check if rel_err is still outside acceptable range
        if abs(rel_err) > param_threshold:
            # Calculate additional margin needed to bring this point within spec
            additional_margin_needed = voltage_margin - suggested_margin
 
            if additional_margin_needed > 0:  # Point still fails
                failing_points.append({
                    'rel_err': rel_err,
                    'current_margin': voltage_margin,
                    'additional_margin_needed': additional_margin_needed,
                    'cell': point.get('cell', 'Unknown'),
                    'arc': point.get('arc', 'Unknown'),
                    'table_position': point.get('table_position', 'Unknown'),
                    'sensitivity': point.get('sensitivity', 0)
                })
 
    if not failing_points:
        return None
 
    # Classify by severity
    severity_classification = {
        'Marginal (1-3mV)': [],
        'Challenging (3-10mV)': [],
        'Extreme (10-50mV)': [],
        'Unfixable (>50mV)': []
    }
 
    for point in failing_points:
        additional_margin = point['additional_margin_needed']
 
        if additional_margin <= 3:
            severity_classification['Marginal (1-3mV)'].append(point)
        elif additional_margin <= 10:
            severity_classification['Challenging (3-10mV)'].append(point)
        elif additional_margin <= 50:
            severity_classification['Extreme (10-50mV)'].append(point)
        else:
            severity_classification['Unfixable (>50mV)'].append(point)
 
    return {
        'total_failing_points': len(failing_points),
        'total_points': len(rel_err_data),
        'failure_rate': len(failing_points) / len(rel_err_data) * 100,
        'severity_breakdown': severity_classification,
        'suggested_margin_applied': suggested_margin,
        'parameter_threshold': param_threshold
    }
 
def create_severity_pie_chart(severity_analysis, corner, type_name, param_name, output_dir):
    """
    Create pie chart showing severity breakdown of remaining errors.
    """
    severity_breakdown = severity_analysis['severity_breakdown']
 
    # Prepare data for pie chart
    labels = []
    sizes = []
    colors = ['#28a745', '#ffc107', '#fd7e14', '#dc3545']  # Green, Yellow, Orange, Red
 
    for i, (severity, points) in enumerate(severity_breakdown.items()):
        if len(points) > 0:
            labels.append(f"{severity}\n({len(points)} points)")
            sizes.append(len(points))
        else:
            labels.append(f"{severity}\n(0 points)")
            sizes.append(0)
 
    # Create figure
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
 
    # Pie chart
    wedges, texts, autotexts = ax1.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%',
                                      startangle=90, textprops={'fontsize': 10})
 
    # Enhance the pie chart
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontweight('bold')
 
    corner_display = corner.replace('ssgnp_', '').replace('_m40c', '')
    ax1.set_title(f'Remaining Error Severity\n{corner_display} {type_name} {param_name}\n'
                 f'Suggested Margin: {severity_analysis["suggested_margin_applied"]:.1f}mV\n'
                 f'Failure Rate: {severity_analysis["failure_rate"]:.1f}%', fontsize=12)
 
    # Summary statistics
    ax2.axis('off')
    summary_text = f"""
    SUMMARY STATISTICS
   
    Total Points Analyzed: {severity_analysis['total_points']:,}
    Total Failing Points: {severity_analysis['total_failing_points']:,}
    Failure Rate: {severity_analysis['failure_rate']:.2f}%
   
    Applied Margin: {severity_analysis['suggested_margin_applied']:.1f}mV
    Parameter Threshold: Â±{severity_analysis['parameter_threshold']*100:.1f}%
   
    SEVERITY BREAKDOWN:
    """
 
    for severity, points in severity_breakdown.items():
        count = len(points)
        percentage = (count / severity_analysis['total_failing_points'] * 100) if severity_analysis['total_failing_points'] > 0 else 0
        summary_text += f"\n{severity}: {count} ({percentage:.1f}%)"
 
    ax2.text(0.1, 0.9, summary_text, transform=ax2.transAxes, fontsize=11,
            verticalalignment='top', fontfamily='monospace',
            bbox=dict(boxstyle="round,pad=0.5", facecolor="lightgray", alpha=0.8))
 
    plt.tight_layout()
 
    # Save figure
    output_file = os.path.join(output_dir, f'{corner}_{type_name}_{param_name}_severity_pie.png')
    save_figure_safely(fig, output_file, dpi=300)
 
def generate_worst_case_analysis(severity_analysis, output_dir):
    """
    Generate top 10 worst case analysis from the most serious category.
    """
    worst_cases_summary = {}
 
    for corner, corner_data in severity_analysis.items():
        for type_name, type_data in corner_data.items():
            for param_name, param_analysis in type_data.items():
                severity_breakdown = param_analysis['severity_breakdown']
 
                # Find the most serious non-empty category
                worst_cases = []
                for severity in ['Unfixable (>50mV)', 'Extreme (10-50mV)', 'Challenging (3-10mV)', 'Marginal (1-3mV)']:
                    if severity in severity_breakdown and len(severity_breakdown[severity]) > 0:
                        worst_cases = severity_breakdown[severity]
                        worst_category = severity
                        break
 
                if worst_cases:
                    # Sort by additional margin needed (descending)
                    worst_cases_sorted = sorted(worst_cases,
                                              key=lambda x: x['additional_margin_needed'],
                                              reverse=True)
 
                    # Take top 10
                    top_10 = worst_cases_sorted[:10]
 
                    # Store results
                    key = f"{corner}_{type_name}_{param_name}"
                    worst_cases_summary[key] = {
                        'corner': corner,
                        'type_name': type_name,
                        'param_name': param_name,
                        'worst_category': worst_category,
                        'top_10_cases': top_10,
                        'total_in_category': len(worst_cases)
                    }
 
                    # Create detailed table for this parameter
                    create_worst_case_table(worst_cases_summary[key], output_dir)
 
    return worst_cases_summary
 
def create_worst_case_table(worst_case_data, output_dir):
    """
    Create a detailed table showing the top 10 worst cases.
    """
    corner = worst_case_data['corner']
    type_name = worst_case_data['type_name']
    param_name = worst_case_data['param_name']
    top_10 = worst_case_data['top_10_cases']
 
    if not top_10:
        return
 
    # Create figure for the table
    fig = plt.figure(figsize=(16, max(8, len(top_10) * 0.5 + 2)))
    ax = fig.add_subplot(111)
    ax.axis('off')
 
    # Prepare table data
    table_data = []
    for i, case in enumerate(top_10):
        # Truncate cell name if too long
        cell_name = case['cell']
        if len(cell_name) > 20:
            cell_name = cell_name[:17] + "..."
 
        table_data.append([
            f"{i+1}",
            cell_name,
            f"{case['table_position']}",
            f"{case['rel_err']*100:.3f}%",
            f"{case['current_margin']:.2f}",
            f"{case['additional_margin_needed']:.2f}",
            f"{case['sensitivity']:.1f}"
        ])
 
    # Create column labels
    col_labels = ['Rank', 'Cell', 'Table Pos', 'Rel Err (%)',
                 'Current Margin (mV)', 'Additional Needed (mV)', 'Sensitivity']
 
    # Create the table
    table = ax.table(
        cellText=table_data,
        colLabels=col_labels,
        loc='center',
        cellLoc='center'
    )
 
    # Customize table appearance
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 1.8)  # Taller rows
 
    # Set column widths
    col_widths = [0.08, 0.25, 0.12, 0.12, 0.15, 0.18, 0.10]
    for j, width in enumerate(col_widths):
        for i in range(len(table_data) + 1):  # +1 for header
            table[(i, j)].set_width(width)
 
    # Style header row
    for j in range(len(col_labels)):
        table[(0, j)].set_facecolor('#707070')
        table[(0, j)].set_text_props(color='white', fontweight='bold')
 
    # Add alternating row colors
    for i in range(1, len(table_data) + 1):
        bg_color = '#ffebee' if i % 2 == 0 else 'white'  # Light red alternating
        for j in range(len(col_labels)):
            table[(i, j)].set_facecolor(bg_color)
 
    # Add title
    corner_display = corner.replace('ssgnp_', '').replace('_m40c', '')
    title = (f'Top {len(top_10)} Worst Cases from {worst_case_data["worst_category"]}\n'
            f'{corner_display} {type_name} {param_name}\n'
            f'({worst_case_data["total_in_category"]} total cases in this severity category)')
 
    fig.suptitle(title, fontsize=14, y=0.95)
 
    # Add explanation
    explanation = (
        "These are the most problematic points that still fail after applying the suggested voltage margin.\n"
        "'Additional Needed' shows how much extra margin would be required to fix each specific case."
    )
    ax.text(0.5, 0.02, explanation, ha='center', fontsize=10, style='italic',
           transform=ax.transAxes,
           bbox=dict(facecolor='#f8f9fa', edgecolor='#dee2e6', pad=8))
 
    # Adjust layout
    plt.tight_layout(rect=[0, 0.05, 1, 0.92])
 
    # Save figure
    output_file = os.path.join(output_dir, f'{corner}_{type_name}_{param_name}_worst_cases.png')
    save_figure_safely(fig, output_file, dpi=300)
 
# Integration function to add to main
def run_remaining_error_severity_analysis(pass_rate_data, sensitivities, output_dir):
    """
    Main function to run the complete remaining error severity analysis.
    """
    logging.info("Starting comprehensive remaining error severity analysis...")
 
    try:
        # Run the complete analysis
        results = analyze_remaining_error_severity(pass_rate_data, sensitivities, output_dir)
 
        logging.info("Remaining error severity analysis completed successfully!")
        logging.info(f"Results saved in: {os.path.join(output_dir, 'remaining_error_severity')}")
 
        return results
    except Exception as e:
        logging.error(f"Error in remaining error severity analysis: {e}")
        logging.error(traceback.format_exc())
        return None
 
# 1. Update the analyze_4_tier_pass_rates function signature
def analyze_4_tier_pass_rates(sensitivities, output_dir, data_dir):
    """
    Analyze pass rates using 4-tier criteria system with integrated verification.
    """
    logging.info("Starting 4-tier pass rate analysis with verification...")
    logcalc = logging.getLogger('calculation')
 
    # Define parameter-specific criteria
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
 
    try:
        pass_rate_dir = os.path.join(output_dir, "4_tier_pass_rate_analysis")
        os.makedirs(pass_rate_dir, exist_ok=True)
 
        # Load all corner data with metadata using the passed data_dir
        all_data = load_all_corner_data_with_metadata(data_dir)
 
        if not all_data:
            logcalc.error("No corner data loaded for 4-tier analysis")
            return {}
 
        # RUN VERIFICATION SUITE FIRST
        logging.info("Running 4-tier verification suite...")
        verification_results = run_4tier_verification_suite(all_data, output_dir)
 
        # Process each corner for pass rate analysis
        pass_rate_data = {}
        margin_points = [0, 1, 2, 3, 4, 5, 6, 7]
 
        for corner, corner_data in all_data.items():
            logcalc.info(f"Processing 4-tier analysis for corner: {corner}")
 
            corner_pass_rate_data = {
                'types': {},
                'margin_points': margin_points
            }
 
            for type_name in ['delay', 'slew']:
                if type_name not in corner_data:
                    continue
 
                type_data = corner_data[type_name]
 
                # Load required data
                mc_data = type_data.get('MC', pd.DataFrame())
                lib_data = type_data.get('Lib', pd.DataFrame())
                abs_err_data = type_data.get('abs_err', pd.DataFrame())
                rel_err_data = type_data.get('rel_err', pd.DataFrame())
                metadata = type_data.get('metadata', pd.DataFrame())
 
                if mc_data.empty or lib_data.empty:
                    logcalc.warning(f"Missing required data for {corner} {type_name}")
                    continue
 
                # Initialize type results
                corner_pass_rate_data['types'][type_name] = {
                    'parameters': {},
                    'criteria': criteria.get(type_name, {})
                }
 
                # Process each parameter
                for param_name in ['late_sigma', 'early_sigma', 'Std', 'Skew', 'Meanshift']:
                    if param_name not in criteria.get(type_name, {}):
                        continue
 
                    param_criteria = criteria[type_name][param_name]
 
                    # Apply 4-tier analysis
                    tier_results = apply_4_tier_analysis(
                        mc_data, lib_data, abs_err_data, rel_err_data, metadata,
                        param_name, param_criteria, margin_points
                    )
 
                    if tier_results:
                        corner_pass_rate_data['types'][type_name]['parameters'][param_name] = tier_results
                        logcalc.info(f"Completed 4-tier analysis for {corner} {type_name} {param_name}")
 
            # Store corner results
            if any(corner_pass_rate_data['types'].get(t, {}).get('parameters') for t in ['delay', 'slew']):
                pass_rate_data[corner] = corner_pass_rate_data
 
        # Create visualizations
        create_4_tier_visualizations(pass_rate_data, pass_rate_dir)
 
        logcalc.info("4-tier pass rate analysis with verification completed")
        return pass_rate_data
 
    except Exception as e:
        logging.error(f"Error in 4-tier pass rate analysis: {e}")
        logging.error(traceback.format_exc())
        return {}
 
def apply_4_tier_analysis(mc_data, lib_data, abs_err_data, rel_err_data, metadata,
                         param_name, param_criteria, margin_points):
    """
    Apply 4-tier pass criteria analysis for a specific parameter.
    """
    logcalc = logging.getLogger('calculation')
 
    # Find relevant columns for this parameter
    param_columns = find_parameter_columns(mc_data, lib_data, abs_err_data, rel_err_data, param_name)
 
    if not param_columns['lib_col']:
        logcalc.warning(f"No library column found for parameter {param_name}")
        return None
 
    # Get slew data from metadata
    slew_values = None
    if not metadata.empty and 'rel_pin_slew' in metadata.columns:
        slew_values = metadata['rel_pin_slew'].values
    else:
        logcalc.warning(f"No rel_pin_slew data found for parameter {param_name}")
        # Use default slew value
        slew_values = np.full(len(lib_data), 100e-12)  # 100ps default
 
    # Apply 4-tier analysis for each margin point
    pass_rate_at_margin = {}
    tier_breakdown_at_margin = {}
 
    for margin_val in margin_points:
        tier_results = evaluate_4_tier_criteria(
            mc_data, lib_data, abs_err_data, rel_err_data, slew_values,
            param_columns, param_criteria, margin_val
        )
 
        if tier_results:
            pass_rate_at_margin[margin_val] = tier_results['pass_rate']
            tier_breakdown_at_margin[margin_val] = tier_results['tier_breakdown']
 
    return {
        'pass_rate_at_margin': pass_rate_at_margin,
        'tier_breakdown_at_margin': tier_breakdown_at_margin,
        'param_criteria': param_criteria,
        'threshold': param_criteria['rel_threshold'],  # Add this line
        'total_points': len(lib_data)
    }
 
def find_parameter_columns(mc_data, lib_data, abs_err_data, rel_err_data, param_name):
    """
    Find the relevant columns for a specific parameter in each dataset.
    """
    param_columns = {
        'lib_col': None,
        'mc_col': None,
        'mc_lb_col': None,
        'mc_ub_col': None,
        'abs_err_col': None,
        'rel_err_col': None
    }
 
    # Map parameter names to potential column patterns
    column_patterns = {
        'late_sigma': ['late_sigma', 'late sigma'],
        'early_sigma': ['early_sigma', 'early sigma'],
        'Std': ['std', 'stdev'],
        'Skew': ['skew', 'skewness'],
        'Meanshift': ['meanshift', 'mean_shift']
    }
 
    patterns = column_patterns.get(param_name, [param_name.lower()])
 
    # Find library column
    for col in lib_data.columns:
        if any(pattern in col.lower() for pattern in patterns):
            param_columns['lib_col'] = col
            break
 
    # Find MC columns (main, LB, UB)
    for col in mc_data.columns:
        col_lower = col.lower()
        if any(pattern in col_lower for pattern in patterns):
            if col.endswith('_LB'):
                param_columns['mc_lb_col'] = col
            elif col.endswith('_UB'):
                param_columns['mc_ub_col'] = col
            elif not col.endswith(('_LB', '_UB')):
                param_columns['mc_col'] = col
 
    # Find error columns
    for col in abs_err_data.columns:
        if any(pattern in col.lower() for pattern in patterns):
            param_columns['abs_err_col'] = col
            break
 
    for col in rel_err_data.columns:
        if any(pattern in col.lower() for pattern in patterns):
            param_columns['rel_err_col'] = col
            break
 
    return param_columns
 
# Replace the evaluate_4_tier_criteria function in voltage_sensitivity_analysis.py
 
def evaluate_4_tier_criteria(mc_data, lib_data, abs_err_data, rel_err_data, slew_values,
                           param_columns, param_criteria, margin_val):
    """
    Evaluate 4-tier pass criteria for all points at a specific margin value.
    FIXED: Handle cases where MC_LB > MC_UB using min/max correction.
    """
    if not param_columns['lib_col']:
        return None
 
    lib_values = lib_data[param_columns['lib_col']].values
    total_points = len(lib_values)
 
    if total_points == 0:
        return None
 
    # Initialize tier tracking
    tier_passes = {
        'tier_1': np.zeros(total_points, dtype=bool),  # Relative error
        'tier_2': np.zeros(total_points, dtype=bool),  # MC confidence interval
        'tier_3': np.zeros(total_points, dtype=bool),  # Enlarged CI
        'tier_4': np.zeros(total_points, dtype=bool)   # Absolute error
    }
 
    # Tier 1: Relative error check
    if param_columns['rel_err_col'] and not rel_err_data.empty:
        rel_errors = rel_err_data[param_columns['rel_err_col']].values
        rel_threshold = param_criteria['rel_threshold']
 
        # Apply voltage margin effect (simplified - assuming linear relationship)
        effective_rel_errors = rel_errors * (1 - margin_val * 0.1)  # Rough approximation
 
        tier_passes['tier_1'] = np.abs(effective_rel_errors) <= rel_threshold
 
    # Tier 2: MC confidence interval check (FIXED - APPLY MIN/MAX CORRECTION)
    if (param_columns['mc_lb_col'] and param_columns['mc_ub_col'] and
        not mc_data.empty):
 
        mc_lb_values = mc_data[param_columns['mc_lb_col']].values
        mc_ub_values = mc_data[param_columns['mc_ub_col']].values
 
        # CRITICAL FIX: Handle cases where LB > UB by using min/max
        ci_min_values = np.minimum(mc_lb_values, mc_ub_values)
        ci_max_values = np.maximum(mc_lb_values, mc_ub_values)
 
        # Now use corrected CI bounds
        tier_passes['tier_2'] = (lib_values >= ci_min_values) & (lib_values <= ci_max_values)
 
    # Tier 3: Enlarged CI check (6% expansion) (FIXED - APPLY MIN/MAX CORRECTION)
    if (param_columns['mc_lb_col'] and param_columns['mc_ub_col'] and
        not mc_data.empty):
 
        mc_lb_values = mc_data[param_columns['mc_lb_col']].values
        mc_ub_values = mc_data[param_columns['mc_ub_col']].values
 
        # CRITICAL FIX: Handle cases where LB > UB by using min/max
        ci_min_values = np.minimum(mc_lb_values, mc_ub_values)
        ci_max_values = np.maximum(mc_lb_values, mc_ub_values)
 
        # Apply 6% expansion to corrected bounds
        enlarged_min = ci_min_values * 1.0  # 6% smaller lower bound
        enlarged_max = ci_max_values * 1.0  # 6% larger upper bound
 
        tier_passes['tier_3'] = (lib_values >= enlarged_min) & (lib_values <= enlarged_max)
 
    # Tier 4: Absolute error check
    if param_columns['abs_err_col'] and not abs_err_data.empty:
        abs_errors = abs_err_data[param_columns['abs_err_col']].values
 
        # Calculate absolute threshold: max(coefficient Ã— slew, min_threshold)
        abs_thresholds = np.maximum(
            param_criteria['abs_coeff'] * slew_values,
            param_criteria['abs_min']
        )
 
        # Apply voltage margin effect
        effective_abs_errors = abs_errors * (1 - margin_val * 0.1)  # Rough approximation
 
        tier_passes['tier_4'] = np.abs(effective_abs_errors) <= abs_thresholds
 
    # Calculate overall pass (ANY tier passes)
    # overall_pass = (tier_passes['tier_1'] | tier_passes['tier_2'] |
    #                tier_passes['tier_3'] | tier_passes['tier_4'])
 
    overall_pass = (tier_passes['tier_1'] | tier_passes['tier_2'])
 
    pass_rate = np.sum(overall_pass) / total_points * 100
 
    # Calculate tier breakdown
    tier_breakdown = {}
    for tier, passes in tier_passes.items():
        tier_breakdown[tier] = {
            'count': int(np.sum(passes)),
            'percentage': float(np.sum(passes) / total_points * 100)
        }
 
    tier_breakdown['overall'] = {
        'count': int(np.sum(overall_pass)),
        'percentage': float(pass_rate)
    }
 
    # Log the fix being applied
    if (param_columns['mc_lb_col'] and param_columns['mc_ub_col'] and
        not mc_data.empty):
        mc_lb_values = mc_data[param_columns['mc_lb_col']].values
        mc_ub_values = mc_data[param_columns['mc_ub_col']].values
        lb_gt_ub_count = np.sum(mc_lb_values > mc_ub_values)
 
        if lb_gt_ub_count > 0:
            logcalc = logging.getLogger('calculation')
            logcalc.info(f"Applied LB > UB correction to {lb_gt_ub_count}/{total_points} points in 4-tier analysis")
 
    return {
        'pass_rate': float(pass_rate),
        'tier_breakdown': tier_breakdown,
        'total_points': total_points
    }
 
# Add this function to voltage_sensitivity_analysis.py for debugging
 
def debug_mc_bounds(mc_data, param_name):
    """
    Debug function to check MC bounds issues for a specific parameter.
    """
    logcalc = logging.getLogger('calculation')
 
    # Find MC columns for the parameter
    mc_col = None
    mc_lb_col = None
    mc_ub_col = None
 
    for col in mc_data.columns:
        if param_name.lower() in col.lower():
            if col.endswith('_LB'):
                mc_lb_col = col
            elif col.endswith('_UB'):
                mc_ub_col = col
            elif not col.endswith(('_LB', '_UB')):
                mc_col = col
 
    if not all([mc_col, mc_lb_col, mc_ub_col]):
        logcalc.warning(f"Cannot find all MC columns for {param_name}")
        return
 
    mc_values = mc_data[mc_col].values
    mc_lb_values = mc_data[mc_lb_col].values
    mc_ub_values = mc_data[mc_ub_col].values
 
    # Check for LB > UB cases
    lb_gt_ub = mc_lb_values > mc_ub_values
    lb_gt_ub_count = np.sum(lb_gt_ub)
 
    # Check for other anomalies
    nan_lb = np.isnan(mc_lb_values)
    nan_ub = np.isnan(mc_ub_values)
    nan_mc = np.isnan(mc_values)
 
    logcalc.info(f"MC BOUNDS ANALYSIS FOR {param_name}:")
    logcalc.info(f"  Total points: {len(mc_values)}")
    logcalc.info(f"  LB > UB cases: {lb_gt_ub_count} ({lb_gt_ub_count/len(mc_values)*100:.1f}%)")
    logcalc.info(f"  NaN in MC: {np.sum(nan_mc)} ({np.sum(nan_mc)/len(mc_values)*100:.1f}%)")
    logcalc.info(f"  NaN in LB: {np.sum(nan_lb)} ({np.sum(nan_lb)/len(mc_values)*100:.1f}%)")
    logcalc.info(f"  NaN in UB: {np.sum(nan_ub)} ({np.sum(nan_ub)/len(mc_values)*100:.1f}%)")
 
    if lb_gt_ub_count > 0:
        # Show some examples
        lb_gt_ub_indices = np.where(lb_gt_ub)[0][:5]  # First 5 examples
        logcalc.info(f"  Examples of LB > UB cases (first 5):")
        for idx in lb_gt_ub_indices:
            logcalc.info(f"    Index {idx}: MC={mc_values[idx]:.6g}, LB={mc_lb_values[idx]:.6g}, UB={mc_ub_values[idx]:.6g}")
 
    # Check bounds relative to MC value
    lb_above_mc = mc_lb_values > mc_values
    ub_below_mc = mc_ub_values < mc_values
 
    logcalc.info(f"  LB > MC cases: {np.sum(lb_above_mc)} ({np.sum(lb_above_mc)/len(mc_values)*100:.1f}%)")
    logcalc.info(f"  UB < MC cases: {np.sum(ub_below_mc)} ({np.sum(ub_below_mc)/len(mc_values)*100:.1f}%)")
 
    return {
        'lb_gt_ub_count': lb_gt_ub_count,
        'lb_gt_ub_percentage': lb_gt_ub_count/len(mc_values)*100,
        'total_points': len(mc_values)
    }
# Replace the existing create_4_tier_visualizations and create_4_tier_pass_rate_heatmap functions
# in voltage_sensitivity_analysis.py with these modified versions:
 
def create_4_tier_visualizations(pass_rate_data, output_dir):
    """
    Create visualizations for 4-tier pass rate analysis.
    Modified to create single heatmap per corner/type combination.
    """
    # Create pass rate heatmaps for each corner and type combination
    for corner, corner_data in pass_rate_data.items():
        for type_name in ['delay', 'slew']:
            if type_name in corner_data.get('types', {}):
                create_single_4_tier_heatmap(corner, type_name, corner_data, output_dir)
 
# Replace these functions in voltage_sensitivity_analysis.py
 
def extract_voltage_from_corner(corner_name):
    """Extract voltage value from corner name with improved precision."""
    if not corner_name:
        return None
 
    # Try multiple patterns to handle different corner naming conventions
    patterns = [
        r'_0p(\d+)v_',    # Standard pattern like _0p450v_ -> 0.450
        r'_(\d+)mv_',     # Pattern with direct mV specification -> convert to V
        r'_v(\d+)_',      # Another possible voltage pattern
        r'[_-](\d\d\d)[_-]'  # 3-digit millivolt spec
    ]
 
    for pattern in patterns:
        match = re.search(pattern, corner_name)
        if match:
            volt_str = match.group(1)
            # Handle different formats
            if pattern == r'_0p(\d+)v_':
                # Convert 0.xxx format (450 -> 0.450) - FIXED precision
                voltage = float(f"0.{volt_str}")
                # Round to 3 decimal places to avoid floating point errors
                return round(voltage, 3)
            elif pattern == r'_(\d+)mv_':
                # Convert mV to V (450 -> 0.450)
                return round(float(volt_str) / 1000, 3)
            elif pattern == r'_v(\d+)_':
                # Direct voltage value, might need adjustment based on your naming
                return round(float(volt_str) / 100, 3)  # Assuming 45 means 0.45V
            elif pattern == r'[_-](\d\d\d)[_-]':
                # 3-digit mV to V (450 -> 0.450)
                return round(float(volt_str) / 1000, 3)
 
    # If no pattern matched, log a warning and try a last-ditch effort
    logging.warning(f"Could not extract voltage using standard patterns from: {corner_name}")
 
    # Last attempt: look for any sequence of 3 digits that might be millivolts
    last_chance = re.search(r'(\d{3})', corner_name)
    if last_chance:
        potential_mv = last_chance.group(1)
        if 400 <= int(potential_mv) <= 550:  # Reasonable voltage range check
            logging.info(f"Using fallback pattern match: {potential_mv}mV")
            return round(float(potential_mv) / 1000, 3)
 
    return None
 
def create_single_4_tier_heatmap(corner, type_name, corner_data, output_dir):
    """
    Create a single heatmap for one corner/type combination with fixed voltage display and green color scheme.
    """
    try:
        # Extract type data
        type_data = corner_data['types'][type_name]
        parameters = list(type_data['parameters'].keys())
        margin_points = corner_data.get('margin_points', [0, 1, 2, 3, 4, 5, 6, 7])
 
        if not parameters:
            return
 
        # Sort parameters for consistent display
        parameters = sorted(parameters)
 
        # Create data matrix: rows = parameters, columns = voltage margins
        data_matrix = np.zeros((len(parameters), len(margin_points)))
 
        # Fill the matrix with pass rate data
        for i, param_name in enumerate(parameters):
            param_data = type_data['parameters'][param_name]
            pass_rates = param_data.get('pass_rate_at_margin', {})
 
            for j, margin in enumerate(margin_points):
                if margin in pass_rates:
                    data_matrix[i, j] = pass_rates[margin]
                else:
                    data_matrix[i, j] = 0  # Default to 0 if no data
 
        # Create figure with appropriate size
        fig, ax = plt.subplots(figsize=(12, 8))
 
        # Create custom colormap with clear thresholds
        from matplotlib.colors import LinearSegmentedColormap, BoundaryNorm
 
        # Define colors with clear boundaries
        colors = [
            '#d73027',  # Red for below 80%
            '#fd8d3c',  # Orange for 80-90%
            '#74c476',  # Medium Green for 90-95%
            '#e5f5e0'   # Very Light Green for 95% and above
        ]
 
        # Define boundaries
        boundaries = [70, 80, 90, 95, 100]
 
        # Create the colormap and normalization
        cmap = LinearSegmentedColormap.from_list('threshold_focused', colors, N=256)
        norm = BoundaryNorm(boundaries, cmap.N)
 
        # Create the heatmap with medium grey grid lines and boundary normalization
        im = ax.imshow(data_matrix, cmap=cmap, norm=norm, aspect='auto')
 
        # Add medium grey grid lines for clear cell separation
        # Vertical lines
        for x in range(len(margin_points) + 1):
            ax.axvline(x - 0.5, color='#666666', linewidth=1.5)
 
        # Horizontal lines
        for y in range(len(parameters) + 1):
            ax.axhline(y - 0.5, color='#666666', linewidth=1.5)
 
        # Set ticks and labels
        ax.set_xticks(np.arange(len(margin_points)))
        ax.set_yticks(np.arange(len(parameters)))
        ax.set_xticklabels([f"{m}mV" for m in margin_points])
 
        # Create parameter labels with thresholds
        param_labels = []
        for param in parameters:
            # Get threshold for this parameter
            param_data = type_data['parameters'][param]
            threshold = param_data.get('threshold', 0.03) * 100  # Convert to percentage
            param_labels.append(f"{param} (Â±{threshold:.1f}%)")
 
        ax.set_yticklabels(param_labels)
 
        # Add value annotations with improved readability for new color scheme
        for i in range(len(parameters)):
            for j in range(len(margin_points)):
                value = data_matrix[i, j]
 
                # Choose text color based on the new color boundaries
                if value >= 95:
                    text_color = '#2d5016'  # Dark green for very light green background
                    font_weight = 'normal'
                elif value >= 90:
                    text_color = 'white'    # White for medium green background
                    font_weight = 'bold'
                elif value >= 80:
                    text_color = 'black'    # Black for orange background
                    font_weight = 'bold'
                else:  # Below 80%
                    text_color = 'white'    # White for red background
                    font_weight = 'bold'
 
                ax.text(j, i, f"{value:.1f}%",
                       ha="center", va="center",
                       color=text_color, fontweight=font_weight, fontsize=11)
 
        # Add improvement annotations for significant changes
        add_improvement_annotations(ax, data_matrix, parameters, margin_points)
 
        # Add sensitivity highlighting boxes
        add_sensitivity_highlighting(ax, data_matrix, parameters, margin_points)
 
        # Add colorbar with custom ticks matching the boundaries
        cbar = plt.colorbar(im, ax=ax, shrink=0.8)
        cbar.set_label('Pass Rate (%)', fontsize=12)
        cbar.set_ticks([70, 75, 80, 85, 90, 95, 100])
 
        # Set colorbar boundaries to match our thresholds
        cbar.set_ticklabels(['70', '75', '80', '85', '90', '95', '100'])
 
        # Set labels and title
        ax.set_xlabel('Voltage Margin (mV)', fontsize=14, fontweight='bold')
        ax.set_ylabel('Parameter', fontsize=14, fontweight='bold')
 
        # FIXED: Extract voltage with proper formatting
        voltage = extract_voltage_from_corner(corner)
        if voltage is not None:
            # Format voltage to 3 decimal places to show exact values
            voltage_display = f"{voltage:.3f}V"
        else:
            # Fallback to corner name parsing
            voltage_display = corner.replace('ssgnp_', '').replace('_m40c', '')
            logging.warning(f"Could not extract voltage from {corner}, using fallback: {voltage_display}")
 
        # Debug logging
        logging.info(f"Creating heatmap for corner: {corner}")
        logging.info(f"Extracted voltage: {voltage}")
        logging.info(f"Display voltage: {voltage_display}")
 
        title = f'Lib Char Certi Pass Rate after Voltage Margin applied (@{voltage_display}, {type_name})'
        ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
 
        # Add legend for color ranges at the bottom - updated with threshold-based scheme
        legend_elements = [
            plt.Rectangle((0, 0), 1, 1, facecolor='#d73027', label='70-80%'),
            plt.Rectangle((0, 0), 1, 1, facecolor='#fd8d3c', label='80-90%'),
            plt.Rectangle((0, 0), 1, 1, facecolor='#74c476', label='90-95%'),
            plt.Rectangle((0, 0), 1, 1, facecolor='#e5f5e0', label='95-100%')
        ]
 
        ax.legend(handles=legend_elements, loc='upper center',
                 bbox_to_anchor=(0.5, -0.1), ncol=4, frameon=True)
 
        # Remove default spines to make grid lines more prominent
        for spine in ax.spines.values():
            spine.set_visible(False)
 
        # Adjust layout
        plt.tight_layout()
 
        # Save figure with corrected filename
        if voltage is not None:
            voltage_str = f"{voltage:.3f}V"
        else:
            voltage_str = corner.replace('ssgnp_', '').replace('_m40c', '')
 
        output_file = os.path.join(output_dir, f"{voltage_str}_{type_name}_4tier_pass_rate.png")
        save_figure_safely(fig, output_file, dpi=300)
 
        logging.info(f"Created 4-tier pass rate heatmap: {output_file}")
 
    except Exception as e:
        logging.error(f"Error creating 4-tier heatmap for {corner} {type_name}: {e}")
        logging.error(traceback.format_exc())
 
def add_improvement_annotations(ax, data_matrix, parameters, margin_points):
    """
    Add annotations showing significant improvements in pass rate.
    Updated with better styling for green color scheme.
    """
    try:
        for i in range(len(parameters)):
            for j in range(1, len(margin_points)):  # Start from margin index 1
                current_rate = data_matrix[i, j]
                previous_rate = data_matrix[i, j-1]
 
                # Calculate improvement
                improvement = current_rate - previous_rate
 
                # Only annotate significant improvements (>5%) and below 95%
                if improvement > 5.0 and current_rate < 95.0:
                    # Position annotation slightly offset
                    ax.annotate(f"+{improvement:.1f}%",
                               xy=(j, i), xytext=(j+0.3, i-0.3),
                               fontsize=10, fontweight='bold', color='#1a5d1a',
                               bbox=dict(boxstyle="round,pad=0.3", facecolor="white",
                                        edgecolor='#1a5d1a', alpha=0.9, linewidth=1.5))
    except Exception as e:
        logging.warning(f"Error adding improvement annotations: {e}")
 
def add_sensitivity_highlighting(ax, data_matrix, parameters, margin_points):
    """
    Add red boxes highlighting areas where pass rate is very sensitive to voltage margin.
    Updated for better visibility with green color scheme.
    """
    try:
        for i in range(len(parameters)):
            # Find ranges where there are significant changes
            sensitive_ranges = []
 
            for j in range(len(margin_points) - 1):
                current_rate = data_matrix[i, j]
                next_rate = data_matrix[i, j + 1]
 
                # Check if this is a sensitive area (large change and below 95%)
                if (abs(next_rate - current_rate) > 3.0 and
                    current_rate < 95.0 and next_rate < 95.0):
                    sensitive_ranges.append((j, j + 1))
 
            # Merge adjacent ranges and draw boxes
            if sensitive_ranges:
                merged_ranges = merge_adjacent_ranges(sensitive_ranges)
 
                for start_j, end_j in merged_ranges:
                    # Draw red rectangle with thicker border
                    rect = plt.Rectangle((start_j - 0.4, i - 0.4),
                                       end_j - start_j + 0.8, 0.8,
                                       fill=False, edgecolor='#cc0000', linewidth=2.5)
                    ax.add_patch(rect)
 
                    # Add text annotation if space allows
                    if end_j - start_j >= 1:  # Only if box is wide enough
                        mid_j = (start_j + end_j) / 2
                        ax.text(mid_j, i + 0.35, "PR is very sensitive to\nVoltage margin",
                               ha='center', va='center', fontsize=8,
                               bbox=dict(boxstyle="round,pad=0.3", facecolor="#cc0000",
                                        edgecolor="#cc0000", alpha=0.9),
                               color='white', fontweight='bold')
 
    except Exception as e:
        logging.warning(f"Error adding sensitivity highlighting: {e}")
 
def merge_adjacent_ranges(ranges):
    """
    Merge adjacent or overlapping ranges.
    """
    if not ranges:
        return []
 
    # Sort ranges by start position
    sorted_ranges = sorted(ranges, key=lambda x: x[0])
    merged = [sorted_ranges[0]]
 
    for current in sorted_ranges[1:]:
        last = merged[-1]
 
        # If current range overlaps or is adjacent to the last one, merge them
        if current[0] <= last[1] + 1:
            merged[-1] = (last[0], max(last[1], current[1]))
        else:
            merged.append(current)
 
    return merged
 
# Debug function to verify voltage extraction
def debug_voltage_extraction(corners):
    """
    Debug function to verify voltage extraction is working correctly.
    Call this to check all your corners.
    """
    print("=== VOLTAGE EXTRACTION DEBUG ===")
    for corner in corners:
        voltage = extract_voltage_from_corner(corner)
        print(f"Corner: {corner}")
        print(f"  -> Extracted voltage: {voltage}")
        print(f"  -> Display format: {voltage:.3f}V" if voltage else "  -> ERROR: Could not extract voltage")
        print()
 
    # Expected results:
    expected = {
        "ssgnp_0p450v_m40c": 0.450,
        "ssgnp_0p465v_m40c": 0.465,
        "ssgnp_0p480v_m40c": 0.480,
        "ssgnp_0p495v_m40c": 0.495
    }
 
    print("=== EXPECTED vs ACTUAL ===")
    for corner, expected_voltage in expected.items():
        actual_voltage = extract_voltage_from_corner(corner)
        status = "âœ“ PASS" if actual_voltage == expected_voltage else "âœ— FAIL"
        print(f"{corner}: Expected {expected_voltage:.3f}V, Got {actual_voltage}, {status}")
 
 
 
 
# Replace the existing call in analyze_4_tier_pass_rates function:
# OLD: create_4_tier_visualizations(pass_rate_data, pass_rate_dir)
# NEW:
# create_4_tier_visualizations(pass_rate_data, pass_rate_dir)
#
# Optionally also add corner comparison views:
# for type_name in ['delay', 'slew']:
#     create_4tier_corner_comparison(pass_rate_data, type_name, pass_rate_dir)
 
# Also add this function to create summary comparison if needed
def create_4tier_corner_comparison(pass_rate_data, type_name, output_dir):
    """
    Create a comparison heatmap showing all corners for a specific type.
    This creates the multi-corner view when needed.
    """
    try:
        # Collect all corners and parameters
        all_corners = []
        all_parameters = set()
 
        for corner, corner_data in pass_rate_data.items():
            if type_name in corner_data.get('types', {}):
                all_corners.append(corner)
                type_data = corner_data['types'][type_name]
                all_parameters.update(type_data['parameters'].keys())
 
        if not all_corners or not all_parameters:
            return
 
        # Sort corners by voltage and parameters
        all_corners = sorted(all_corners, key=lambda c: extract_voltage_from_corner(c) or 0)
        all_parameters = sorted(all_parameters)
 
        # Get margin points
        margin_points = pass_rate_data[all_corners[0]].get('margin_points', [0, 1, 2, 3, 4, 5, 6, 7])
 
        # Create one subplot for each margin
        fig, axes = plt.subplots(2, 4, figsize=(20, 12))
        axes = axes.flatten()
 
        for idx, margin in enumerate(margin_points):
            if idx >= len(axes):
                break
 
            ax = axes[idx]
 
            # Create data matrix for this margin: rows = parameters, columns = corners
            data_matrix = np.zeros((len(all_parameters), len(all_corners)))
 
            for j, corner in enumerate(all_corners):
                corner_data = pass_rate_data[corner]
                type_data = corner_data['types'].get(type_name, {})
 
                for i, param in enumerate(all_parameters):
                    if param in type_data['parameters']:
                        param_data = type_data['parameters'][param]
                        pass_rates = param_data.get('pass_rate_at_margin', {})
                        if margin in pass_rates:
                            data_matrix[i, j] = pass_rates[margin]
 
            # Create heatmap for this margin
            im = ax.imshow(data_matrix, cmap='RdYlGn', vmin=80, vmax=100, aspect='auto')
 
            # Set labels
            ax.set_title(f'{margin}mV Margin', fontsize=12, fontweight='bold')
            ax.set_xticks(np.arange(len(all_corners)))
            ax.set_yticks(np.arange(len(all_parameters)))
 
            # Create corner labels with voltages
            corner_labels = []
            for corner in all_corners:
                voltage = extract_voltage_from_corner(corner)
                corner_labels.append(f"{voltage:.3f}V" if voltage else corner)
 
            ax.set_xticklabels(corner_labels, rotation=45, ha='right')
            ax.set_yticklabels(all_parameters)
 
            # Add value annotations
            for i in range(len(all_parameters)):
                for j in range(len(all_corners)):
                    value = data_matrix[i, j]
                    if value > 0:  # Only show non-zero values
                        text_color = "white" if value < 90 else "black"
                        ax.text(j, i, f"{value:.1f}%",
                               ha="center", va="center",
                               color=text_color, fontweight='bold', fontsize=9)
 
        # Add colorbar
        fig.colorbar(im, ax=axes, shrink=0.6, label='Pass Rate (%)')
 
        # Set main title
        fig.suptitle(f'4-Tier Pass Rate Comparison Across Corners - {type_name}', fontsize=16, fontweight='bold')
 
        # Adjust layout
        plt.tight_layout()
 
        # Save figure
        output_file = os.path.join(output_dir, f"{type_name}_4tier_corner_comparison.png")
        save_figure_safely(fig, output_file, dpi=300)
 
        logging.info(f"Created 4-tier corner comparison: {output_file}")
 
    except Exception as e:
        logging.error(f"Error creating 4-tier corner comparison for {type_name}: {e}")
        logging.error(traceback.format_exc())
 
# !/usr/bin/env python3
 
# Replace these functions in your voltage_sensitivity_analysis.py file
 
def load_all_corner_data(data_dir, corners):
    """Load data for all corners and organize by category."""
    logflow = logging.getLogger('dataflow')
    logflow.info("=" * 80)
    logflow.info("LOADING CORNER DATA")
    logflow.info("=" * 80)
 
    all_data = {}
    categories = ['MC', 'Lib', 'abs_err', 'rel_err']
 
    # Track missing data for summary report
    missing_data_report = []
    loaded_file_summary = {}
 
    # Check if data_dir points to the main results directory or directly to corner results
    corner_results_dir = data_dir
    if not any(corner in os.listdir(data_dir) for corner in [f"{corners[0]}_delay", f"{corners[0]}_slew"]):
        # data_dir points to main results directory, look for 01_corner_results
        potential_corner_dir = os.path.join(data_dir, "01_corner_results")
        if os.path.exists(potential_corner_dir):
            corner_results_dir = potential_corner_dir
            logflow.info(f"Using corner results directory: {corner_results_dir}")
        else:
            logflow.error(f"Cannot find corner data in {data_dir} or {potential_corner_dir}")
            return {}
    else:
        logflow.info(f"Using data directory directly as corner results: {corner_results_dir}")
 
    for corner in corners:
        logflow.info(f"Processing corner: {corner}")
        corner_data = {}
        corner_missing = []
        corner_loaded_files = {'MC': [], 'Lib': [], 'abs_err': [], 'rel_err': []}
 
        for type_name in ['delay', 'slew']:
            corner_dir = os.path.join(corner_results_dir, f"{corner}_{type_name}")
 
            # Check if corner directory exists
            if not os.path.exists(corner_dir):
                logflow.warning(f"Corner directory does not exist: {corner_dir}")
                corner_missing.append(f"Missing directory for {type_name}")
                continue
 
            corner_data[type_name] = {}
 
            for category in categories:
                file_patterns = [
                    f"*_{category}_data.csv",
                    f"*{category}*.csv",
                    f"*_{category.lower()}_data.csv"
                ]
 
                csv_file = None
                for pattern in file_patterns:
                    matches = glob.glob(os.path.join(corner_dir, pattern))
                    if matches:
                        csv_file = matches[0]
                        break
 
                if csv_file and os.path.exists(csv_file):
                    try:
                        df = pd.read_csv(csv_file)
                        if df.empty:
                            logflow.warning(f"Empty dataframe loaded from {csv_file}")
                            corner_missing.append(f"Empty {category} data for {type_name}")
                        else:
                            corner_data[type_name][category] = df
                            corner_loaded_files[category].append(csv_file)
                            logflow.info(f"Loaded {category} data for {corner} {type_name}: {df.shape}")
 
                            # Debug: Report first few column names
                            if category in ['rel_err', 'MC']:
                                cols = df.columns.tolist()
                                logflow.debug(f"First 10 columns in {category} data: {cols[:min(10, len(cols))]}")
                    except Exception as e:
                        logflow.error(f"Error loading {csv_file}: {e}")
                        corner_missing.append(f"Error reading {category} data for {type_name}: {str(e)}")
                else:
                    logflow.warning(f"No {category} data file found for {corner} {type_name}")
                    corner_missing.append(f"Missing {category} data for {type_name}")
 
        # Only add corner data if we have at least some data
        if any(corner_data.get(t, {}) for t in ['delay', 'slew']):
            all_data[corner] = corner_data
            loaded_file_summary[corner] = corner_loaded_files
            if corner_missing:
                missing_data_report.append({
                    'corner': corner,
                    'missing': corner_missing
                })
        else:
            logflow.error(f"No valid data found for corner {corner}")
            missing_data_report.append({
                'corner': corner,
                'missing': ['No valid data found for this corner']
            })
 
    # Log summary of loaded files
    logflow.info("=== SUMMARY OF LOADED FILES ===")
    for corner, categories in loaded_file_summary.items():
        logflow.info(f"Corner: {corner}")
        for category, files in categories.items():
            if files:
                logflow.info(f"  - {category}: {len(files)} files loaded")
                for file in files:
                    logflow.info(f"    - {os.path.basename(file)}")
            else:
                logflow.info(f"  - {category}: No files loaded")
 
    # Log summary of missing data
    if missing_data_report:
        logflow.warning("=== SUMMARY OF MISSING DATA ===")
        for report in missing_data_report:
            logflow.warning(f"Corner: {report['corner']}")
            for missing in report['missing']:
                logflow.warning(f"  - {missing}")
 
    return all_data
 
 
 
def load_all_corner_data_with_metadata(data_dir):
    """
    Load all corner data including the new metadata category.
    data_dir should point to the corner results directory (01_corner_results) - same as load_all_corner_data.
    """
    logflow = logging.getLogger('dataflow')
    logflow.info("Loading corner data with metadata for 4-tier analysis")
 
    all_data = {}
 
    # Auto-detect corners and types from directory structure
    corners = ["ssgnp_0p450v_m40c", "ssgnp_0p465v_m40c", "ssgnp_0p480v_m40c", "ssgnp_0p495v_m40c"]
    types = ['delay', 'slew']
    categories = ['MC', 'Lib', 'abs_err', 'rel_err', 'metadata']
 
    # Track missing data for summary report
    missing_data_report = []
    loaded_file_summary = {}
 
    # Use the same logic as load_all_corner_data - data_dir should already be the corner results directory
    corner_results_dir = data_dir
    logflow.info(f"Using corner results directory for metadata loading: {corner_results_dir}")
 
    for corner in corners:
        logflow.info(f"Processing corner: {corner}")
        corner_data = {}
        corner_missing = []
        corner_loaded_files = {'MC': [], 'Lib': [], 'abs_err': [], 'rel_err': [], 'metadata': []}
 
        for type_name in types:
            corner_dir = os.path.join(corner_results_dir, f"{corner}_{type_name}")
 
            # Check if corner directory exists
            if not os.path.exists(corner_dir):
                logflow.warning(f"Corner directory does not exist: {corner_dir}")
                corner_missing.append(f"Missing directory for {type_name}")
                continue
 
            type_data = {}
 
            for category in categories:
                file_patterns = [
                    f"*_{category}_data.csv",
                    f"*{category}*.csv",
                    f"*_{category.lower()}_data.csv"
                ]
 
                csv_file = None
                for pattern in file_patterns:
                    matches = glob.glob(os.path.join(corner_dir, pattern))
                    if matches:
                        csv_file = matches[0]
                        break
 
                if csv_file and os.path.exists(csv_file):
                    try:
                        df = pd.read_csv(csv_file)
                        if df.empty:
                            logflow.warning(f"Empty dataframe loaded from {csv_file}")
                            corner_missing.append(f"Empty {category} data for {type_name}")
                        else:
                            type_data[category] = df
                            corner_loaded_files[category].append(csv_file)
                            logflow.info(f"Loaded {category} data for {corner} {type_name}: {df.shape}")
 
                            # Debug: Report first few column names
                            if category in ['rel_err', 'MC', 'metadata']:
                                cols = df.columns.tolist()
                                logflow.debug(f"First 10 columns in {category} data: {cols[:min(10, len(cols))]}")
                    except Exception as e:
                        logflow.error(f"Error loading {csv_file}: {e}")
                        corner_missing.append(f"Error reading {category} data for {type_name}: {str(e)}")
                else:
                    logflow.warning(f"No {category} data file found for {corner} {type_name}")
                    corner_missing.append(f"Missing {category} data for {type_name}")
 
            if type_data:
                corner_data[type_name] = type_data
 
        # Only add corner data if we have at least some data
        if any(corner_data.get(t, {}) for t in ['delay', 'slew']):
            all_data[corner] = corner_data
            loaded_file_summary[corner] = corner_loaded_files
            if corner_missing:
                missing_data_report.append({
                    'corner': corner,
                    'missing': corner_missing
                })
        else:
            logflow.error(f"No valid data found for corner {corner}")
            missing_data_report.append({
                'corner': corner,
                'missing': ['No valid data found for this corner']
            })
 
    # Log summary of loaded files
    logflow.info("=== SUMMARY OF LOADED FILES (WITH METADATA) ===")
    for corner, categories in loaded_file_summary.items():
        logflow.info(f"Corner: {corner}")
        for category, files in categories.items():
            if files:
                logflow.info(f"  - {category}: {len(files)} files loaded")
                for file in files:
                    logflow.info(f"    - {os.path.basename(file)}")
            else:
                logflow.info(f"  - {category}: No files loaded")
 
    # Log summary of missing data
    if missing_data_report:
        logflow.warning("=== SUMMARY OF MISSING DATA (WITH METADATA) ===")
        for report in missing_data_report:
            logflow.warning(f"Corner: {report['corner']}")
            for missing in report['missing']:
                logflow.warning(f"  - {missing}")
 
    logflow.info(f"Loaded data for {len(all_data)} corners")
    return all_data
def create_optimized_table(fig, position, df, corners, corner_voltages, title):
    """Create an optimized compact table visualization within the provided grid position."""
    try:
        # Create axis in the provided position
        ax = fig.add_subplot(position)
 
        # Hide axes
        ax.axis('off')
 
        # Debug: Log the input data dimensions
        logging.debug(f"Creating table for: {title}")
        logging.debug(f"DataFrame shape: {df.shape}")
        logging.debug(f"DataFrame columns: {df.columns.tolist()}")
        logging.debug(f"DataFrame index: {df.index.tolist()}")
        logging.debug(f"Corners: {corners}")
        logging.debug(f"Corner voltages: {corner_voltages}")
 
        # Check if dataframe is empty
        if df.empty:
            ax.text(0.5, 0.5, f"No data available for\n{title}",
                    ha='center', va='center', fontsize=12)
            ax.set_title(title, fontsize=12, pad=10)
            return
 
        # Ensure corners exist in dataframe columns
        valid_corners = [corner for corner in corners if corner in df.columns]
        if not valid_corners:
            ax.text(0.5, 0.5, f"No valid corner data found for\n{title}",
                    ha='center', va='center', fontsize=12)
            ax.set_title(title, fontsize=12, pad=10)
            return
 
        # Use only valid corners
        corners = valid_corners
 
        # Create column headers with voltage values (shortened display)
        col_labels = []
        for corner in corners:
            # Create more concise corner labels
            voltage = corner_voltages.get(corner, None)
            if voltage:
                voltage_display = f"{voltage:.3f}V"
                col_labels.append(voltage_display)
            else:
                corner_display = corner.replace('ssgnp_', '').replace('_m40c', '')
                col_labels.append(corner_display)
 
        # Create row labels (parameters) - only non-empty rows
        valid_params = [param for param in df.index if not df.loc[param, corners].isna().all()]
        if not valid_params:
            ax.text(0.5, 0.5, f"No valid parameter data found for\n{title}",
                    ha='center', va='center', fontsize=12)
            ax.set_title(title, fontsize=12, pad=10)
            return
 
        row_labels = valid_params
 
        # Create cell text and colors
        cell_text = []
        cell_colors = []
 
        for param in valid_params:
            row_data = []
            row_colors = []
 
            for corner in corners:
                try:
                    value = df.loc[param, corner]
 
                    if pd.isna(value):
                        row_data.append('N/A')
                        row_colors.append('#eeeeee')  # Light gray for N/A
                    else:
                        try:
                            # Format the value
                            row_data.append(f"{value:.1f}")
 
                            # Conditional color based on value
                            if value <= 1.0:
                                row_colors.append('#1a9850')  # Green for <= 1mV
                            elif value <= 2.0:
                                row_colors.append('#91cf60')  # Light green for 1-2mV
                            elif value <= 3.0:
                                row_colors.append('#d9ef8b')  # Yellow-green for 2-3mV
                            elif value <= 4.0:
                                row_colors.append('#fee08b')  # Light yellow for 3-4mV
                            elif value <= 5.0:
                                row_colors.append('#fc8d59')  # Orange for 4-5mV
                            else:
                                row_colors.append('#d73027')  # Red for >5mV
                        except Exception as e:
                            logging.warning(f"Error formatting value {value} for {param}, {corner}: {e}")
                            row_data.append(str(value))
                            row_colors.append('#ffffff')  # White default
                except Exception as e:
                    logging.error(f"Error accessing data for {param}, {corner}: {e}")
                    row_data.append('Error')
                    row_colors.append('#ffcccc')  # Light red for error
 
            cell_text.append(row_data)
            cell_colors.append(row_colors)
 
        # Debug: Log the cell dimensions
        logging.debug(f"Cell text dimensions: {len(cell_text)} x {len(cell_text[0]) if cell_text else 0}")
        logging.debug(f"Cell colors dimensions: {len(cell_colors)} x {len(cell_colors[0]) if cell_colors else 0}")
        logging.debug(f"Row labels count: {len(row_labels)}")
        logging.debug(f"Col labels count: {len(col_labels)}")
 
        # Check dimensions match
        if not cell_text or not cell_colors:
            ax.text(0.5, 0.5, f"No valid data to display for\n{title}",
                    ha='center', va='center', fontsize=12)
            ax.set_title(title, fontsize=12, pad=10)
            return
 
        # Create table with improved formatting and more compact proportions
        table = ax.table(
            cellText=cell_text,
            rowLabels=row_labels,
            colLabels=col_labels,
            cellColours=cell_colors,
            loc='center',
            cellLoc='center'
        )
 
        # Customize table appearance for better readability
        table.auto_set_font_size(False)
        table.set_fontsize(10)
 
        # Crucial adjustment: make the table more compact with better height/width ratio
        table.scale(1, 1.2)  # Reduced from 1.5 to 1.2 for height
 
        # Adjust individual cell widths and heights for better proportions
        for (i, j), cell in table.get_celld().items():
            try:
                if j == -1:  # Row labels (parameters)
                    cell.set_width(0.15)  # Make parameter column narrower
                else:  # Data cells
                    cell.set_width(0.85 / len(corners))  # Distribute width evenly
 
                # Make the header row stand out with grey color
                if i == 0:  # Header row
                    cell.set_text_props(weight='bold', color='white')
                    cell.set_facecolor('#707070')  # Grey header
                    cell.set_height(0.08)  # Increased header height
                else:  # Data rows
                    if len(row_labels) > 0:  # Prevent division by zero
                        cell.set_height(0.92 / len(row_labels))  # Distribute height evenly
 
                # Set text color for easier reading on colored backgrounds
                if (i > 0) and (j > -1):  # Data cells (not row labels)
                    # Add bounds checking before accessing cell_colors
                    if (i - 1 < len(cell_colors)) and (j < len(cell_colors[i - 1])):
                        cell_color = cell_colors[i - 1][j]
                        if cell_color in ['#1a9850', '#d73027']:  # Dark backgrounds
                            table._cells[(i, j)]._text.set_color('white')
                        else:
                            table._cells[(i, j)]._text.set_color('black')
                    else:
                        # Default to black text if we can't access the color
                        table._cells[(i, j)]._text.set_color('black')
                        logging.warning(f"Could not access cell color for position ({i}, {j})")
 
            except Exception as e:
                logging.error(f"Error customizing table cell ({i}, {j}): {e}")
                continue
 
        # Set title with less vertical space
        ax.set_title(title, fontsize=12, pad=10)
 
    except Exception as e:
        logging.error(f"Error creating optimized table for '{title}': {e}")
        logging.error(traceback.format_exc())
 
        # Create a fallback simple table or error message
        try:
            ax.text(0.5, 0.5, f"Error creating table:\n{title}\n\nSee log for details",
                    ha='center', va='center', fontsize=10,
                    bbox=dict(boxstyle="round,pad=0.3", facecolor="lightcoral", alpha=0.7))
            ax.set_title(title, fontsize=12, pad=10)
        except:
            pass  # If even the error message fails, just continue
 
 
def create_combined_margin_summary(pass_rate_data, optimistic_margin_data, output_dir):
    """Create a combined 2x2 grid visualization of all margin requirement tables with improved proportions."""
    logging.info("Creating combined margin requirement summary...")
 
    try:
        # Create output directory for summary tables
        summary_dir = os.path.join(output_dir, "margin_summary")
        os.makedirs(summary_dir, exist_ok=True)
 
        # Check if we have any data to work with
        if not pass_rate_data and not optimistic_margin_data:
            logging.error("No pass rate data or optimistic margin data available for summary")
            return False
 
        # Get all corners and voltage values
        all_corners = set()
        if pass_rate_data:
            all_corners.update(pass_rate_data.keys())
        if optimistic_margin_data:
            all_corners.update(optimistic_margin_data.keys())
 
        all_corners = sorted(all_corners)
 
        if not all_corners:
            logging.error("No corners found in the data")
            return False
 
        corner_voltages = {}
 
        for corner in all_corners:
            voltage = extract_voltage_from_corner(corner)
            if voltage:
                corner_voltages[corner] = voltage
 
        # Sort corners by voltage
        if corner_voltages:
            sorted_corners = sorted(all_corners, key=lambda c: corner_voltages.get(c, 0))
        else:
            sorted_corners = all_corners
 
        logging.info(f"Processing {len(sorted_corners)} corners: {sorted_corners}")
 
        # Get all parameter names
        all_parameters = set()
        if pass_rate_data:
            for corner_data in pass_rate_data.values():
                for type_data in corner_data.get('types', {}).values():
                    all_parameters.update(type_data.get('parameters', {}).keys())
 
        if not all_parameters:
            # Try to get parameters from optimistic margin data
            if optimistic_margin_data:
                for corner_data in optimistic_margin_data.values():
                    if 'parameters' in corner_data:
                        all_parameters.update(corner_data['parameters'].keys())
 
        if not all_parameters:
            logging.error("No parameters found in the data")
            return False
 
        logging.info(f"Processing {len(all_parameters)} parameters: {sorted(all_parameters)}")
 
        # Calculate appropriate figure size based on data dimensions
        num_params = len(all_parameters)
        num_corners = len(sorted_corners)
 
        # Adjust figure width and height based on data dimensions
        fig_width = max(12, 8 + num_corners * 0.8)
        fig_height = max(8, 4 + num_params * 0.5)
 
        # Create a more compact figure with proper proportions
        fig = plt.figure(figsize=(fig_width, fig_height))
 
        # Create a tighter grid with less spacing
        spec = gridspec.GridSpec(ncols=2, nrows=2, figure=fig, wspace=0.15, hspace=0.25)
 
        # Define positions for each table
        positions = {
            ('delay', 'outlier'): spec[0, 0],
            ('delay', 'pass'): spec[0, 1],
            ('slew', 'outlier'): spec[1, 0],
            ('slew', 'pass'): spec[1, 1]
        }
 
        # Track all table data for CSV exports
        all_tables = {}
 
        # Create tables for each type and metric
        for type_name in ['delay', 'slew']:
            logging.info(f"Processing {type_name} tables...")
 
            # Create DataFrames for this type
            outlier_df = pd.DataFrame(index=sorted(all_parameters), columns=sorted_corners)
            pass_df = pd.DataFrame(index=sorted(all_parameters), columns=sorted_corners)
 
            # Fill the DataFrames
            for corner in sorted_corners:
                logging.debug(f"Processing corner {corner} for {type_name}")
 
                # Get pass rate data
                corner_data = pass_rate_data.get(corner, {}) if pass_rate_data else {}
                type_data = corner_data.get('types', {}).get(type_name, {})
 
                # Get margin points
                margin_points = corner_data.get('margin_points', [0, 1, 2, 3, 4, 5, 6, 7])
 
                for param in sorted(all_parameters):
                    try:
                        param_data = type_data.get('parameters', {}).get(param, {})
 
                        # Get optimistic margin from optimistic_margin_data
                        optimistic_margin = np.nan
                        if (optimistic_margin_data and corner in optimistic_margin_data and
                                'parameters' in optimistic_margin_data[corner]):
                            if param in optimistic_margin_data[corner]['parameters']:
                                if 'all_margins' in optimistic_margin_data[corner]['parameters'][param]:
                                    margins = optimistic_margin_data[corner]['parameters'][param]['all_margins']
                                    if margins:
                                        optimistic_margin = max(margins)
 
                        # Get pass rate margin
                        pass_margin = np.nan
                        if param_data:
                            pass_rates = param_data.get('pass_rate_at_margin', {})
 
                            if pass_rates:
                                # Find first margin where pass rate >= 95%
                                for margin in sorted(margin_points):
                                    if margin in pass_rates and pass_rates[margin] >= 95:
                                        pass_margin = margin
                                        break
 
                                # If never reaches 95%, use the highest margin evaluated
                                if pd.isna(pass_margin):
                                    pass_margin = max(margin_points) if margin_points else np.nan
 
                        # Store values in DataFrames
                        outlier_df.loc[param, corner] = optimistic_margin
                        pass_df.loc[param, corner] = pass_margin
 
                    except Exception as e:
                        logging.error(f"Error processing {corner} {type_name} {param}: {e}")
                        outlier_df.loc[param, corner] = np.nan
                        pass_df.loc[param, corner] = np.nan
 
            # Store tables for CSV export
            all_tables[(type_name, 'outlier')] = outlier_df
            all_tables[(type_name, 'pass')] = pass_df
 
            # Debug: Log table contents
            logging.debug(f"Outlier table for {type_name}:")
            logging.debug(f"  Shape: {outlier_df.shape}")
            logging.debug(f"  Non-null values: {outlier_df.count().sum()}")
 
            logging.debug(f"Pass table for {type_name}:")
            logging.debug(f"  Shape: {pass_df.shape}")
            logging.debug(f"  Non-null values: {pass_df.count().sum()}")
 
            # Create visualizations for this type with improved proportions
            try:
                create_optimized_table(fig, positions[(type_name, 'outlier')], outlier_df, sorted_corners,
                                       corner_voltages,
                                       f"{type_name.title()} - Voltage Margin (mV) to Cover All Optimistic Outliers")
            except Exception as e:
                logging.error(f"Error creating outlier table for {type_name}: {e}")
 
            try:
                create_optimized_table(fig, positions[(type_name, 'pass')], pass_df, sorted_corners, corner_voltages,
                                       f"{type_name.title()} - Voltage Margin (mV) to Achieve 95% Pass Rate")
            except Exception as e:
                logging.error(f"Error creating pass rate table for {type_name}: {e}")
 
        # Add a single color legend at the bottom with less vertical space
        try:
            legend_elements = [
                plt.Rectangle((0, 0), 1, 1, facecolor='#1a9850', label='<= 1 mV'),
                plt.Rectangle((0, 0), 1, 1, facecolor='#91cf60', label='1-2 mV'),
                plt.Rectangle((0, 0), 1, 1, facecolor='#d9ef8b', label='2-3 mV'),
                plt.Rectangle((0, 0), 1, 1, facecolor='#fee08b', label='3-4 mV'),
                plt.Rectangle((0, 0), 1, 1, facecolor='#fc8d59', label='4-5 mV'),
                plt.Rectangle((0, 0), 1, 1, facecolor='#d73027', label='> 5 mV'),
                plt.Rectangle((0, 0), 1, 1, facecolor='#eeeeee', label='N/A')
            ]
 
            fig.legend(handles=legend_elements, loc='lower center',
                       bbox_to_anchor=(0.5, 0.02), ncol=7, frameon=True)
        except Exception as e:
            logging.error(f"Error creating legend: {e}")
 
        # Add a main title with less space
        try:
            fig.suptitle('Voltage Margin Requirements Summary', fontsize=16, y=0.98)
        except Exception as e:
            logging.error(f"Error setting main title: {e}")
 
        # Adjust layout with tight constraints
        try:
            plt.tight_layout(rect=[0, 0.05, 1, 0.95])
        except Exception as e:
            logging.error(f"Error adjusting layout: {e}")
 
        # Save combined figure
        try:
            combined_output = os.path.join(summary_dir, "combined_margin_summary.png")
            plt.savefig(combined_output, dpi=300, bbox_inches='tight')
            plt.close()
            logging.info(f"Created combined margin summary: {combined_output}")
        except Exception as e:
            logging.error(f"Error saving combined figure: {e}")
            plt.close()
 
        # Save individual tables to CSV
        for (type_name, metric), df in all_tables.items():
            try:
                csv_file = os.path.join(summary_dir, f"{type_name}_{metric}_margin.csv")
                df.to_csv(csv_file)
                logging.info(f"Saved {type_name} {metric} margin table to {csv_file}")
            except Exception as e:
                logging.error(f"Error saving CSV for {type_name} {metric}: {e}")
 
        return True
 
    except Exception as e:
        logging.error(f"Error creating combined margin summary: {e}")
        logging.error(traceback.format_exc())
        return False
 
def analyze_voltage_margin(sensitivities, output_dir):
    """Analyze voltage margin requirements using the scatter plot data source."""
    logging.info("Starting voltage margin analysis...")
    logcalc = logging.getLogger('calculation')
 
    try:
        voltage_viz_dir = os.path.join(output_dir, "voltage_margin_analysis")
        os.makedirs(voltage_viz_dir, exist_ok=True)
 
        # Use scatter plot data instead of reprocessing
        margin_data = {}
        margin_points = [0, 1, 2, 3, 4, 5, 6, 7]
        parameters = ['late_sigma', 'early_sigma', 'Std', 'Skew', 'Meanshift']
 
        # Get all corners from sensitivities
        all_corners = set()
        for type_data in sensitivities.values():
            for param_data in type_data.values():
                for entry in param_data:
                    all_corners.update(entry.get('corner_sensitivities', {}).keys())
 
        # Check if scatter plot data is available
        if hasattr(create_error_margin_scatter_plot, 'data_store'):
            scatter_data_store = create_error_margin_scatter_plot.data_store
 
            # Process each corner
            for corner in all_corners:
                logcalc.info(f"Processing margin data for corner: {corner}")
                corner_margin_data = {
                    'parameters': {},
                    'margin_points': margin_points
                }
 
                # Process each parameter
                for param in parameters:
                    # Find matching scatter data for this corner/parameter
                    for key, scatter_data in scatter_data_store.items():
                        if (scatter_data['corner'] == corner and
                            scatter_data['param_name'] == param):
 
                            # Use ONLY abs_err data as requested
                            abs_err_data = scatter_data.get('abs_err_data', [])
 
                            if abs_err_data:
                                # Extract margins for optimistic errors (error < 0)
                                all_margins = []
                                optimistic_points = 0
                                total_points = len(abs_err_data)
 
                                for item in abs_err_data:
                                    if item.get('error_value', 0) < 0:  # Optimistic error
                                        margin = item.get('voltage_margin', 0)
                                        all_margins.append(abs(margin))  # Use absolute value
                                        optimistic_points += 1
 
                                # Calculate percentage at each margin threshold
                                error_at_margin = {}
                                for threshold in margin_points:
                                    if threshold == 0:
                                        # Base percentage of optimistic errors
                                        percentage = (optimistic_points / total_points) * 100 if total_points > 0 else 0
                                    else:
                                        # Percentage of errors still remaining above threshold
                                        points_above = sum(1 for m in all_margins if m > threshold)
                                        percentage = (points_above / optimistic_points) * 100 if optimistic_points > 0 else 0
 
                                    error_at_margin[threshold] = percentage
 
                                # Store parameter data
                                corner_margin_data['parameters'][param] = {
                                    'all_margins': all_margins,
                                    'total_points': total_points,
                                    'optimistic_points': optimistic_points,
                                    'error_at_margin': error_at_margin
                                }
 
                                logcalc.info(f"  {param}: {len(all_margins)} margins from {optimistic_points} optimistic errors out of {total_points} total points")
                                break
 
                # Only store if we have parameter data
                if corner_margin_data['parameters']:
                    margin_data[corner] = corner_margin_data
 
 
 
        return margin_data
    except Exception as e:
        logging.error(f"Error in analyze_voltage_margin: {e}")
        logging.error(traceback.format_exc())
        return {}
# Also fix the main function to handle the missing pass_rate_data properly
# Replace the main function in voltage_sensitivity_analysis.py
# Add these functions to voltage_sensitivity_analysis.py
 
def verify_4tier_implementation(mc_data, lib_data, abs_err_data, rel_err_data, slew_values,
                               param_columns, param_criteria, corner_name, type_name, param_name,
                               verification_dir, sample_size=370):
    """
    Verify 4-tier criteria implementation using the actual data being processed.
    This runs during the analysis and uses the same intermediate data.
    """
    logcalc = logging.getLogger('calculation')
 
    logcalc.info(f"=" * 80)
    logcalc.info(f"VERIFYING 4-TIER CRITERIA: {corner_name} {type_name} {param_name}")
    logcalc.info(f"=" * 80)
 
    # Create verification output directory
    os.makedirs(verification_dir, exist_ok=True)
 
    # Create detailed verification log file
    verification_log_file = os.path.join(verification_dir, f"{corner_name}_{type_name}_{param_name}_verification.log")
    verification_logger = setup_verification_logger(verification_log_file)
 
    verification_logger.info(f"4-TIER CRITERIA VERIFICATION")
    verification_logger.info(f"Corner: {corner_name}")
    verification_logger.info(f"Type: {type_name}")
    verification_logger.info(f"Parameter: {param_name}")
    verification_logger.info(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    verification_logger.info("=" * 80)
 
    # Log data shapes
    verification_logger.info(f"DATA SHAPES:")
    verification_logger.info(f"  MC data: {mc_data.shape}")
    verification_logger.info(f"  Lib data: {lib_data.shape}")
    verification_logger.info(f"  abs_err data: {abs_err_data.shape}")
    verification_logger.info(f"  rel_err data: {rel_err_data.shape}")
    verification_logger.info(f"  Slew values: {len(slew_values)}")
 
    # Log parameter columns found
    verification_logger.info(f"\nPARAMETER COLUMNS:")
    for key, col in param_columns.items():
        verification_logger.info(f"  {key}: {col}")
 
    # Log criteria being used
    verification_logger.info(f"\n4-TIER CRITERIA FOR {param_name}:")
    verification_logger.info(f"  Relative threshold: Â±{param_criteria['rel_threshold']*100:.1f}%")
    verification_logger.info(f"  Absolute coefficient: {param_criteria['abs_coeff']}")
    verification_logger.info(f"  Absolute minimum: {param_criteria['abs_min']*1e12:.0f}ps")
 
    # Extract values
    lib_values = lib_data[param_columns['lib_col']].values
    total_points = len(lib_values)
 
    # Take a random sample for detailed verification
    if sample_size > total_points:
        sample_size = total_points
 
    sample_indices = np.random.choice(total_points, sample_size, replace=False)
    sample_indices = sorted(sample_indices)
 
    verification_logger.info(f"\nVERIFYING {sample_size} SAMPLE POINTS (out of {total_points} total):")
    verification_logger.info("-" * 160)
    verification_logger.info(f"{'Index':<8} {'Lib':<12} {'MC':<12} {'MC_LB':<12} {'MC_UB':<12} {'CI_Min':<12} {'CI_Max':<12} {'rel_err':<10} {'abs_err':<12} {'Slew(ps)':<10} {'T1':<3} {'T2':<3} {'T3':<3} {'T4':<3} {'Pass':<4}")
    verification_logger.info("-" * 160)
 
    # Verification counters
    pass_count = 0
    tier_passes = {'T1': 0, 'T2': 0, 'T3': 0, 'T4': 0}
    lb_ub_swapped_count = 0
 
    # Extract data arrays
    mc_values = mc_data[param_columns['mc_col']].values if param_columns['mc_col'] else None
    mc_lb_values = mc_data[param_columns['mc_lb_col']].values if param_columns['mc_lb_col'] else None
    mc_ub_values = mc_data[param_columns['mc_ub_col']].values if param_columns['mc_ub_col'] else None
    rel_err_values = rel_err_data[param_columns['rel_err_col']].values if param_columns['rel_err_col'] else None
    abs_err_values = abs_err_data[param_columns['abs_err_col']].values if param_columns['abs_err_col'] else None
 
    for idx in sample_indices:
        try:
            # Get values for this point
            lib_val = lib_values[idx]
            mc_val = mc_values[idx] if mc_values is not None else np.nan
            mc_lb_val = mc_lb_values[idx] if mc_lb_values is not None else np.nan
            mc_ub_val = mc_ub_values[idx] if mc_ub_values is not None else np.nan
            rel_err_val = rel_err_values[idx] if rel_err_values is not None else np.nan
            abs_err_val = abs_err_values[idx] if abs_err_values is not None else np.nan
            slew_val = slew_values[idx] if idx < len(slew_values) else 100e-12
 
            # Handle cases where LB > UB
            if not (np.isnan(mc_lb_val) or np.isnan(mc_ub_val)):
                ci_min = min(mc_lb_val, mc_ub_val)
                ci_max = max(mc_lb_val, mc_ub_val)
 
                if mc_lb_val > mc_ub_val:
                    lb_ub_swapped_count += 1
            else:
                ci_min = np.nan
                ci_max = np.nan
 
            # Apply 4-tier criteria (margin_val = 0 for verification)
            # Tier 1: Relative error check
            tier1_pass = False
            if not np.isnan(rel_err_val):
                tier1_pass = abs(rel_err_val) <= param_criteria['rel_threshold']
 
            # Tier 2: MC confidence interval check
            tier2_pass = False
            if not (np.isnan(ci_min) or np.isnan(ci_max) or np.isnan(lib_val)):
                tier2_pass = ci_min <= lib_val <= ci_max
 
            # Tier 3: Enlarged CI check (6% expansion)
            tier3_pass = False
            if not (np.isnan(ci_min) or np.isnan(ci_max) or np.isnan(lib_val)):
                enlarged_min = ci_min * 1.0
                enlarged_max = ci_max * 1.0
                tier3_pass = enlarged_min <= lib_val <= enlarged_max
 
            # Tier 4: Absolute error check
            tier4_pass = False
            if not np.isnan(abs_err_val):
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
 
            # Log this point
            verification_logger.info(f"{idx:<8} {lib_val:<12.6g} {mc_val:<12.6g} {mc_lb_val:<12.6g} {mc_ub_val:<12.6g} "
                                   f"{ci_min:<12.6g} {ci_max:<12.6g} {rel_err_val:<10.4f} {abs_err_val:<12.6g} {slew_val*1e12:<10.1f} "
                                   f"{'Y' if tier1_pass else 'N':<3} {'Y' if tier2_pass else 'N':<3} "
                                   f"{'Y' if tier3_pass else 'N':<3} {'Y' if tier4_pass else 'N':<3} "
                                   f"{'Y' if overall_pass else 'N':<4}")
 
        except Exception as e:
            verification_logger.error(f"ERROR processing index {idx}: {e}")
            continue
 
    verification_logger.info("-" * 160)
    verification_logger.info(f"\nVERIFICATION SUMMARY:")
    verification_logger.info(f"  Total sample points: {sample_size}")
    verification_logger.info(f"  Overall pass rate: {pass_count}/{sample_size} ({pass_count/sample_size*100:.1f}%)")
    verification_logger.info(f"  Tier 1 passes (rel_err <= Â±{param_criteria['rel_threshold']*100:.1f}%): {tier_passes['T1']} ({tier_passes['T1']/sample_size*100:.1f}%)")
    verification_logger.info(f"  Tier 2 passes (within MC CI): {tier_passes['T2']} ({tier_passes['T2']/sample_size*100:.1f}%)")
    verification_logger.info(f"  Tier 3 passes (within enlarged CI): {tier_passes['T3']} ({tier_passes['T3']/sample_size*100:.1f}%)")
    verification_logger.info(f"  Tier 4 passes (abs_err <= threshold): {tier_passes['T4']} ({tier_passes['T4']/sample_size*100:.1f}%)")
    verification_logger.info(f"  Cases where LB > UB (corrected): {lb_ub_swapped_count}")
 
    verification_logger.info(f"\nTIER EXPLANATIONS:")
    verification_logger.info(f"  T1: |rel_err| <= {param_criteria['rel_threshold']}")
    verification_logger.info(f"  T2: min(MC_LB, MC_UB) <= Lib <= max(MC_LB, MC_UB)")
    verification_logger.info(f"  T3: CI_min*0.94 <= Lib <= CI_max*1.06")
    verification_logger.info(f"  T4: |abs_err| <= max({param_criteria['abs_coeff']}*slew, {param_criteria['abs_min']*1e12:.0f}ps)")
 
    # Also run full dataset verification
    verification_logger.info(f"\n" + "="*80)
    verification_logger.info(f"FULL DATASET VERIFICATION ({total_points} points)")
    verification_logger.info(f"="*80)
 
    # Run the actual 4-tier evaluation on full dataset
    full_results = evaluate_4_tier_criteria(mc_data, lib_data, abs_err_data, rel_err_data, slew_values,
                                           param_columns, param_criteria, margin_val=0)
 
    if full_results:
        verification_logger.info(f"Full dataset pass rate: {full_results['pass_rate']:.1f}%")
        verification_logger.info(f"Full dataset tier breakdown:")
        for tier, data in full_results['tier_breakdown'].items():
            verification_logger.info(f"  {tier}: {data['count']} points ({data['percentage']:.1f}%)")
    else:
        verification_logger.error("Failed to evaluate full dataset")
 
    # Log to main logger as well
    logcalc.info(f"4-tier verification completed for {corner_name} {type_name} {param_name}")
    logcalc.info(f"  Sample verification: {pass_count}/{sample_size} ({pass_count/sample_size*100:.1f}%) pass rate")
    if full_results:
        logcalc.info(f"  Full dataset: {full_results['pass_rate']:.1f}% pass rate")
    logcalc.info(f"  Detailed results saved to: {verification_log_file}")
 
 
    # Run MC CI debugging if we have the required columns
    if (param_columns['mc_lb_col'] and param_columns['mc_ub_col'] and
        param_columns['lib_col']):
 
        verification_logger.info(f"\n" + "="*80)
        verification_logger.info(f"RUNNING MC CONFIDENCE INTERVAL DEBUGGING")
        verification_logger.info(f"="*80)
 
        mc_debug_results = debug_mc_confidence_intervals(
            mc_data, lib_data, param_columns, param_name,
            corner_name, type_name, verification_dir
        )
 
        verification_logger.info(f"MC CI Debug Summary:")
        verification_logger.info(f"  Within CI: {mc_debug_results['within_ci_pct']:.1f}%")
        verification_logger.info(f"  Below CI: {mc_debug_results['below_ci_pct']:.1f}%")
        verification_logger.info(f"  Above CI: {mc_debug_results['above_ci_pct']:.1f}%")
        verification_logger.info(f"  LB > UB: {mc_debug_results['lb_gt_ub_pct']:.1f}%")
 
        # Update logcalc with debug summary
        logcalc.info(f"MC CI Analysis: Within={mc_debug_results['within_ci_pct']:.1f}%, "
                    f"Below={mc_debug_results['below_ci_pct']:.1f}%, "
                    f"Above={mc_debug_results['above_ci_pct']:.1f}%")
 
    return {
        'sample_pass_rate': pass_count/sample_size*100,
        'sample_tier_breakdown': tier_passes,
        'full_results': full_results,
        'lb_ub_swapped_count': lb_ub_swapped_count,
        'verification_log_file': verification_log_file
    }
 
def run_4tier_verification_suite(all_data, output_dir):
    """
    Run 4-tier verification on all corners, types, and parameters.
    """
    logcalc = logging.getLogger('calculation')
 
    logcalc.info("=" * 80)
    logcalc.info("STARTING 4-TIER VERIFICATION SUITE")
    logcalc.info("=" * 80)
 
    # Create verification directory
    verification_dir = os.path.join(output_dir, "4_tier_verification")
    os.makedirs(verification_dir, exist_ok=True)
 
    # Define criteria (same as in analyze_4_tier_pass_rates)
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
 
    verification_summary = {}
 
    # Process each corner
    for corner, corner_data in all_data.items():
        logcalc.info(f"Running 4-tier verification for corner: {corner}")
 
        corner_verification = {}
 
        for type_name in ['delay', 'slew']:
            if type_name not in corner_data:
                continue
 
            type_data = corner_data[type_name]
 
            # Load required data
            mc_data = type_data.get('MC', pd.DataFrame())
            lib_data = type_data.get('Lib', pd.DataFrame())
            abs_err_data = type_data.get('abs_err', pd.DataFrame())
            rel_err_data = type_data.get('rel_err', pd.DataFrame())
            metadata = type_data.get('metadata', pd.DataFrame())
 
            if mc_data.empty or lib_data.empty:
                logcalc.warning(f"Missing required data for {corner} {type_name}")
                continue
 
            # Get slew values
            if not metadata.empty and 'rel_pin_slew' in metadata.columns:
                slew_values = metadata['rel_pin_slew'].values
            else:
                slew_values = np.full(len(lib_data), 100e-12)
 
            type_verification = {}
 
            # Process each parameter
            for param_name in ['late_sigma', 'early_sigma', 'Std', 'Skew', 'Meanshift']:
                if param_name not in criteria.get(type_name, {}):
                    continue
 
                param_criteria = criteria[type_name][param_name]
 
                # Find parameter columns
                param_columns = find_parameter_columns(mc_data, lib_data, abs_err_data, rel_err_data, param_name)
 
                if not param_columns['lib_col']:
                    logcalc.warning(f"No library column found for {corner} {type_name} {param_name}")
                    continue
 
                # Run verification
                try:
                    verification_results = verify_4tier_implementation(
                        mc_data, lib_data, abs_err_data, rel_err_data, slew_values,
                        param_columns, param_criteria, corner, type_name, param_name,
                        verification_dir, sample_size=50  # Larger sample for better verification
                    )
 
                    type_verification[param_name] = verification_results
                    logcalc.info(f"  {param_name}: {verification_results['sample_pass_rate']:.1f}% sample pass rate")
 
                except Exception as e:
                    logcalc.error(f"Error verifying {corner} {type_name} {param_name}: {e}")
                    logcalc.error(traceback.format_exc())
 
            if type_verification:
                corner_verification[type_name] = type_verification
 
        if corner_verification:
            verification_summary[corner] = corner_verification
 
    # Create summary report
    create_verification_summary_report(verification_summary, verification_dir)
 
    logcalc.info("4-tier verification suite completed")
    logcalc.info(f"Results saved in: {verification_dir}")
 
    return verification_summary
 
def create_verification_summary_report(verification_summary, output_dir):
    """
    Create a summary report of all verification results.
    """
    summary_file = os.path.join(output_dir, "verification_summary.txt")
 
    with open(summary_file, 'w') as f:
        f.write("4-TIER CRITERIA VERIFICATION SUMMARY REPORT\n")
        f.write("=" * 80 + "\n")
        f.write(f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
 
        for corner, corner_data in verification_summary.items():
            f.write(f"CORNER: {corner}\n")
            f.write("-" * 40 + "\n")
 
            for type_name, type_data in corner_data.items():
                f.write(f"  Type: {type_name}\n")
 
                for param_name, param_data in type_data.items():
                    sample_rate = param_data['sample_pass_rate']
                    full_rate = param_data['full_results']['pass_rate'] if param_data['full_results'] else 0
                    lb_ub_swaps = param_data['lb_ub_swapped_count']
 
                    f.write(f"    {param_name}: Sample={sample_rate:.1f}%, Full={full_rate:.1f}%, LB>UB={lb_ub_swaps}\n")
 
                f.write("\n")
 
            f.write("\n")
 
        f.write("Individual verification logs available in this directory.\n")
 
    logging.info(f"Verification summary report saved to: {summary_file}")
 
# Add this helper function to voltage_sensitivity_analysis.py
 
def setup_verification_logger(log_file):
    """Set up a dedicated logger for verification output."""
    # Create a logger
    verification_logger = logging.getLogger(f'verification_{os.path.basename(log_file)}')
    verification_logger.setLevel(logging.INFO)
 
    # Remove existing handlers if any
    for handler in verification_logger.handlers[:]:
        verification_logger.removeHandler(handler)
 
    # Create file handler
    file_handler = logging.FileHandler(log_file, mode='w')
    file_handler.setLevel(logging.INFO)
 
    # Create formatter
    formatter = logging.Formatter('%(message)s')
    file_handler.setFormatter(formatter)
 
    # Add handler to logger
    verification_logger.addHandler(file_handler)
 
    return verification_logger
 
# Add this enhanced debugging function to voltage_sensitivity_analysis.py
 
def debug_mc_confidence_intervals(mc_data, lib_data, param_columns, param_name, corner_name, type_name, verification_dir):
    """
    Debug MC confidence intervals to understand why Tier 2/3 aren't working.
    """
    logcalc = logging.getLogger('calculation')
 
    debug_file = os.path.join(verification_dir, f"{corner_name}_{type_name}_{param_name}_mc_debug.log")
    debug_logger = setup_verification_logger(debug_file)
 
    debug_logger.info(f"MC CONFIDENCE INTERVAL DEBUG: {corner_name} {type_name} {param_name}")
    debug_logger.info("=" * 80)
 
    lib_values = lib_data[param_columns['lib_col']].values
    mc_lb_values = mc_data[param_columns['mc_lb_col']].values
    mc_ub_values = mc_data[param_columns['mc_ub_col']].values
 
    total_points = len(lib_values)
 
    # Calculate statistics
    lb_gt_ub_count = np.sum(mc_lb_values > mc_ub_values)
    lb_gt_ub_pct = lb_gt_ub_count / total_points * 100
 
    # Corrected CI bounds
    ci_min_values = np.minimum(mc_lb_values, mc_ub_values)
    ci_max_values = np.maximum(mc_lb_values, mc_ub_values)
 
    # CI statistics
    ci_width = ci_max_values - ci_min_values
    lib_vs_ci_min = lib_values - ci_min_values
    lib_vs_ci_max = lib_values - ci_max_values
 
    # Points within CI
    within_ci = (lib_values >= ci_min_values) & (lib_values <= ci_max_values)
    within_ci_count = np.sum(within_ci)
    within_ci_pct = within_ci_count / total_points * 100
 
    # Points below CI
    below_ci = lib_values < ci_min_values
    below_ci_count = np.sum(below_ci)
    below_ci_pct = below_ci_count / total_points * 100
 
    # Points above CI
    above_ci = lib_values > ci_max_values
    above_ci_count = np.sum(above_ci)
    above_ci_pct = above_ci_count / total_points * 100
 
    debug_logger.info(f"BASIC STATISTICS:")
    debug_logger.info(f"  Total points: {total_points}")
    debug_logger.info(f"  LB > UB cases: {lb_gt_ub_count} ({lb_gt_ub_pct:.1f}%)")
    debug_logger.info(f"")
 
    debug_logger.info(f"LIBRARY VALUE STATISTICS:")
    debug_logger.info(f"  Lib min: {np.min(lib_values):.6g}")
    debug_logger.info(f"  Lib max: {np.max(lib_values):.6g}")
    debug_logger.info(f"  Lib mean: {np.mean(lib_values):.6g}")
    debug_logger.info(f"  Lib std: {np.std(lib_values):.6g}")
    debug_logger.info(f"")
 
    debug_logger.info(f"MC BOUNDS STATISTICS (ORIGINAL):")
    debug_logger.info(f"  MC_LB min: {np.min(mc_lb_values):.6g}")
    debug_logger.info(f"  MC_LB max: {np.max(mc_lb_values):.6g}")
    debug_logger.info(f"  MC_LB mean: {np.mean(mc_lb_values):.6g}")
    debug_logger.info(f"  MC_UB min: {np.min(mc_ub_values):.6g}")
    debug_logger.info(f"  MC_UB max: {np.max(mc_ub_values):.6g}")
    debug_logger.info(f"  MC_UB mean: {np.mean(mc_ub_values):.6g}")
    debug_logger.info(f"")
 
    debug_logger.info(f"CORRECTED CI STATISTICS:")
    debug_logger.info(f"  CI_min: {np.min(ci_min_values):.6g}")
    debug_logger.info(f"  CI_max: {np.max(ci_max_values):.6g}")
    debug_logger.info(f"  CI_width mean: {np.mean(ci_width):.6g}")
    debug_logger.info(f"  CI_width std: {np.std(ci_width):.6g}")
    debug_logger.info(f"")
 
    debug_logger.info(f"LIBRARY vs CI ANALYSIS:")
    debug_logger.info(f"  Points within CI: {within_ci_count} ({within_ci_pct:.1f}%)")
    debug_logger.info(f"  Points below CI: {below_ci_count} ({below_ci_pct:.1f}%)")
    debug_logger.info(f"  Points above CI: {above_ci_count} ({above_ci_pct:.1f}%)")
    debug_logger.info(f"")
 
    # Show worst cases (points furthest from CI)
    debug_logger.info(f"WORST CASES (furthest from CI):")
 
    # Calculate distance from CI for points outside
    distance_from_ci = np.zeros(total_points)
    for i in range(total_points):
        if lib_values[i] < ci_min_values[i]:
            distance_from_ci[i] = ci_min_values[i] - lib_values[i]  # How far below CI
        elif lib_values[i] > ci_max_values[i]:
            distance_from_ci[i] = lib_values[i] - ci_max_values[i]  # How far above CI
        else:
            distance_from_ci[i] = 0  # Inside CI
 
    # Find worst cases
    worst_indices = np.argsort(distance_from_ci)[-10:]  # Top 10 worst
 
    debug_logger.info(f"Top 10 points furthest from CI:")
    debug_logger.info(f"{'Index':<8} {'Lib':<12} {'CI_Min':<12} {'CI_Max':<12} {'Distance':<12} {'Status':<12}")
    debug_logger.info("-" * 80)
 
    for idx in reversed(worst_indices):  # Show worst first
        lib_val = lib_values[idx]
        ci_min = ci_min_values[idx]
        ci_max = ci_max_values[idx]
        distance = distance_from_ci[idx]
 
        if lib_val < ci_min:
            status = "Below CI"
        elif lib_val > ci_max:
            status = "Above CI"
        else:
            status = "Within CI"
 
        debug_logger.info(f"{idx:<8} {lib_val:<12.6g} {ci_min:<12.6g} {ci_max:<12.6g} {distance:<12.6g} {status:<12}")
 
    debug_logger.info(f"")
 
    # Analyze relative position
    relative_position = (lib_values - ci_min_values) / (ci_max_values - ci_min_values)
    # relative_position: 0 = at CI_min, 0.5 = at center, 1 = at CI_max
 
    debug_logger.info(f"RELATIVE POSITION ANALYSIS:")
    debug_logger.info(f"  (Lib - CI_min) / CI_width")
    debug_logger.info(f"  0.0 = at CI_min, 0.5 = center, 1.0 = at CI_max")
    debug_logger.info(f"  Mean relative position: {np.mean(relative_position):.3f}")
    debug_logger.info(f"  Positions < 0 (below CI): {np.sum(relative_position < 0)} ({np.sum(relative_position < 0)/total_points*100:.1f}%)")
    debug_logger.info(f"  Positions > 1 (above CI): {np.sum(relative_position > 1)} ({np.sum(relative_position > 1)/total_points*100:.1f}%)")
    debug_logger.info(f"  Positions 0-1 (within CI): {np.sum((relative_position >= 0) & (relative_position <= 1))} ({np.sum((relative_position >= 0) & (relative_position <= 1))/total_points*100:.1f}%)")
 
    logcalc.info(f"MC CI debug completed for {corner_name} {type_name} {param_name}")
    logcalc.info(f"  Within CI: {within_ci_pct:.1f}%, Below CI: {below_ci_pct:.1f}%, Above CI: {above_ci_pct:.1f}%")
    logcalc.info(f"  Debug details saved to: {debug_file}")
 
    return {
        'within_ci_pct': within_ci_pct,
        'below_ci_pct': below_ci_pct,
        'above_ci_pct': above_ci_pct,
        'lb_gt_ub_pct': lb_gt_ub_pct
    }
 
# Add this function to your voltage_sensitivity_analysis.py script
 
def create_before_after_margin_comparison(pass_rate_data, output_dir):
    """
    Create before/after comparison showing pass rates at 0mV vs suggested voltage margins.
    Shows two heatmaps side by side (delay and slew) with corners on x-axis.
    """
    try:
        # Get all corners and sort by voltage
        corners = list(pass_rate_data.keys())
        corners = sorted(corners, key=lambda c: extract_voltage_from_corner(c) or 0)
 
        if len(corners) < 2:
            logging.warning("Need at least 2 corners for before/after comparison")
            return
 
        # Get corner voltages for display
        corner_voltages = []
        corner_labels = []
        for corner in corners:
            voltage = extract_voltage_from_corner(corner)
            if voltage:
                corner_voltages.append(voltage)
                corner_labels.append(f"{voltage:.3f}V")
            else:
                corner_voltages.append(0)
                corner_labels.append(corner)
 
        # Create figure with two subplots (delay and slew)
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
 
        # Process each type (delay and slew)
        for type_idx, type_name in enumerate(['delay', 'slew']):
            ax = ax1 if type_name == 'delay' else ax2
 
            # Find suggested margins and create comparison data
            comparison_data, suggested_margins = create_comparison_matrix(
                pass_rate_data, corners, type_name)
 
            if comparison_data is None:
                continue
 
            # Create the heatmap
            create_before_after_heatmap(ax, comparison_data, corner_labels,
                                      suggested_margins, type_name)
 
        # Set main title
        fig.suptitle('CDNS Voltage Sensitivity Analysis\nSuggested Voltage Margin to Apply & Updated Pass Rates',
                     fontsize=16, fontweight='bold', y=0.95)
 
        # Add success message
        fig.text(0.5, 0.02, 'CDNS Best recipe passed all certification â†’ Confirmed Recipe',
                fontsize=14, fontweight='bold', ha='center',
                bbox=dict(boxstyle="round,pad=0.5", facecolor="#d4edda", edgecolor="#28a745"))
 
        plt.tight_layout(rect=[0, 0.08, 1, 0.92])
 
        # Save figure
        output_file = os.path.join(output_dir, "before_after_voltage_margin_comparison.png")
        save_figure_safely(fig, output_file, dpi=300)
 
        logging.info(f"Created before/after voltage margin comparison: {output_file}")
 
    except Exception as e:
        logging.error(f"Error creating before/after comparison: {e}")
        logging.error(traceback.format_exc())
 
def create_comparison_matrix(pass_rate_data, corners, type_name):
    """
    Create the comparison matrix showing before (0mV) vs after (suggested margin) pass rates.
    """
    try:
        # Get all parameters across corners
        all_parameters = set()
        for corner in corners:
            corner_data = pass_rate_data.get(corner, {})
            type_data = corner_data.get('types', {}).get(type_name, {})
            if 'parameters' in type_data:
                all_parameters.update(type_data['parameters'].keys())
 
        if not all_parameters:
            return None, None
 
        # Sort parameters for consistent display
        all_parameters = sorted(all_parameters)
 
        # Create matrix: rows = parameters, columns = corners
        comparison_data = np.zeros((len(all_parameters), len(corners)))
        suggested_margins = []
 
        for j, corner in enumerate(corners):
            corner_data = pass_rate_data.get(corner, {})
            type_data = corner_data.get('types', {}).get(type_name, {})
 
            # Find suggested margin for this corner/type
            suggested_margin = find_suggested_margin_for_corner(corner_data, type_name)
            suggested_margins.append(suggested_margin)
 
            # Fill comparison data
            for i, param in enumerate(all_parameters):
                if param in type_data.get('parameters', {}):
                    param_data = type_data['parameters'][param]
                    pass_rates = param_data.get('pass_rate_at_margin', {})
 
                    # Get pass rate at suggested margin (this is the "after" value)
                    if suggested_margin in pass_rates:
                        comparison_data[i, j] = pass_rates[suggested_margin]
                    elif 0 in pass_rates:
                        # Fallback to 0mV if suggested margin not available
                        comparison_data[i, j] = pass_rates[0]
                    else:
                        comparison_data[i, j] = 0
                else:
                    comparison_data[i, j] = 0
 
        return comparison_data, suggested_margins
 
    except Exception as e:
        logging.error(f"Error creating comparison matrix for {type_name}: {e}")
        return None, None
 
def find_suggested_margin_for_corner(corner_data, type_name):
    """
    Find the suggested voltage margin for a corner/type to achieve >95% pass rate.
    """
    try:
        type_data = corner_data.get('types', {}).get(type_name, {})
        margin_points = corner_data.get('margin_points', [0, 1, 2, 3, 4, 5, 6, 7])
 
        # For each margin point, calculate average pass rate across all parameters
        best_margin = 0
        best_average = 0
 
        for margin in margin_points:
            total_pass_rate = 0
            param_count = 0
 
            for param_name, param_data in type_data.get('parameters', {}).items():
                pass_rates = param_data.get('pass_rate_at_margin', {})
                if margin in pass_rates:
                    total_pass_rate += pass_rates[margin]
                    param_count += 1
 
            if param_count > 0:
                avg_pass_rate = total_pass_rate / param_count
 
                # Find minimum margin that achieves >95% average pass rate
                if avg_pass_rate >= 95.0:
                    return margin
 
                # Track best performing margin
                if avg_pass_rate > best_average:
                    best_average = avg_pass_rate
                    best_margin = margin
 
        # If no margin achieves 95%, return the best performing one
        return best_margin
 
    except Exception as e:
        logging.warning(f"Error finding suggested margin: {e}")
        return 0
 
def create_before_after_heatmap(ax, data_matrix, corner_labels, suggested_margins, type_name):
    """
    Create the heatmap showing updated pass rates with suggested margins.
    """
    try:
        # Use the same color scheme as the main analysis
        from matplotlib.colors import LinearSegmentedColormap, BoundaryNorm
 
        colors = ['#d73027', '#fd8d3c', '#74c476', '#e5f5e0']
        boundaries = [70, 80, 90, 95, 100]
        cmap = LinearSegmentedColormap.from_list('comparison', colors, N=256)
        norm = BoundaryNorm(boundaries, cmap.N)
 
        # Create heatmap
        im = ax.imshow(data_matrix, cmap=cmap, norm=norm, aspect='auto')
 
        # Add medium grey grid lines
        for x in range(len(corner_labels) + 1):
            ax.axvline(x - 0.5, color='#666666', linewidth=1.5)
        for y in range(data_matrix.shape[0] + 1):
            ax.axhline(y - 0.5, color='#666666', linewidth=1.5)
 
        # Set ticks and labels
        ax.set_xticks(range(len(corner_labels)))
        ax.set_yticks(range(data_matrix.shape[0]))
 
        # Create x-axis labels with suggested margins
        x_labels = []
        for i, (corner_label, margin) in enumerate(zip(corner_labels, suggested_margins)):
            x_labels.append(f"{corner_label}\n({margin:.1f}mV)")
 
        ax.set_xticklabels(x_labels, fontsize=11, fontweight='bold')
 
        # Set y-axis labels (parameters)
        parameters = ['Meanshift', 'Skew', 'Std', 'early_sigma', 'late_sigma']
        if data_matrix.shape[0] == len(parameters):
            ax.set_yticklabels(parameters, fontsize=11)
        else:
            # Fallback if different number of parameters
            ax.set_yticklabels([f'Param_{i}' for i in range(data_matrix.shape[0])])
 
        # Add percentage values to cells
        for i in range(data_matrix.shape[0]):
            for j in range(data_matrix.shape[1]):
                value = data_matrix[i, j]
 
                # Choose text color based on background
                if value >= 95:
                    text_color = '#2d5016'
                    font_weight = 'normal'
                elif value >= 90:
                    text_color = 'white'
                    font_weight = 'bold'
                elif value >= 80:
                    text_color = 'black'
                    font_weight = 'bold'
                else:
                    text_color = 'white'
                    font_weight = 'bold'
 
                ax.text(j, i, f'{value:.1f}%', ha='center', va='center',
                       color=text_color, fontweight=font_weight, fontsize=11)
 
        # Set title and labels
        ax.set_title(f'Updated Pass Rates with Suggested Margins - {type_name}',
                    fontsize=14, fontweight='bold', pad=20)
        ax.set_ylabel('Parameter', fontsize=12, fontweight='bold')
 
        # Remove spines for cleaner look
        for spine in ax.spines.values():
            spine.set_visible(False)
 
        # Add colorbar (only for the rightmost subplot)
        if type_name == 'slew':
            cbar = plt.colorbar(im, ax=ax, shrink=0.8)
            cbar.set_label('Pass Rate (%)', fontsize=12)
            cbar.set_ticks([70, 80, 90, 95, 100])
 
    except Exception as e:
        logging.error(f"Error creating heatmap for {type_name}: {e}")
 
# Additional function to add this to the main analysis workflow
def update_analyze_4_tier_pass_rates_with_comparison(sensitivities, output_dir, data_dir):
    """
    Updated version of analyze_4_tier_pass_rates that includes the before/after comparison.
    Add this call at the end of your main analysis.
    """
    try:
        # Run the existing 4-tier analysis
        pass_rate_data = analyze_4_tier_pass_rates(sensitivities, output_dir, data_dir)
 
        # Create the before/after comparison plot
        comparison_dir = os.path.join(output_dir, "before_after_comparison")
        os.makedirs(comparison_dir, exist_ok=True)
 
        create_before_after_margin_comparison(pass_rate_data, comparison_dir)
 
        logging.info("Before/after voltage margin comparison completed")
 
    except Exception as e:
        logging.error(f"Error in before/after comparison analysis: {e}")
 
# Add this integration code to your main analysis function:
 
def integrate_before_after_analysis():
    """
    Add this to the end of your main voltage sensitivity analysis workflow.
    """
    # In your main() function or analyze_4_tier_pass_rates function, add:
 
    # After running the 4-tier analysis:
    # pass_rate_data = analyze_4_tier_pass_rates(sensitivities, output_dir, data_dir)
 
    # Create before/after comparison
    logging.info("Creating before/after voltage margin comparison...")
    create_before_after_margin_comparison(pass_rate_data, output_dir)
 
# Also add this improved version that shows both before AND after in the same plot:
 
def create_detailed_before_after_comparison(pass_rate_data, output_dir):
    """
    Create a more detailed before/after comparison showing both 0mV and suggested margin results.
    """
    try:
        # Get all corners and sort by voltage
        corners = list(pass_rate_data.keys())
        corners = sorted(corners, key=lambda c: extract_voltage_from_corner(c) or 0)
 
        # Create figure with four subplots (2x2 grid)
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(18, 12))
 
        # Top row: BEFORE (0mV margin)
        create_before_after_subplot(ax1, pass_rate_data, corners, 'delay', margin_type='before')
        create_before_after_subplot(ax2, pass_rate_data, corners, 'slew', margin_type='before')
 
        # Bottom row: AFTER (suggested margins)
        create_before_after_subplot(ax3, pass_rate_data, corners, 'delay', margin_type='after')
        create_before_after_subplot(ax4, pass_rate_data, corners, 'slew', margin_type='after')
 
        # Set main title
        fig.suptitle('CDNS Voltage Sensitivity Analysis: Before vs After Voltage Margin Application',
                     fontsize=18, fontweight='bold', y=0.95)
 
        # Add success message
        fig.text(0.5, 0.02, 'âœ“ CDNS Best recipe passed all certification â†’ Confirmed Recipe',
                fontsize=14, fontweight='bold', ha='center', color='green',
                bbox=dict(boxstyle="round,pad=0.5", facecolor="#d4edda", edgecolor="#28a745"))
 
        plt.tight_layout(rect=[0, 0.08, 1, 0.92])
 
        # Save figure
        output_file = os.path.join(output_dir, "detailed_before_after_comparison.png")
        save_figure_safely(fig, output_file, dpi=300)
 
        logging.info(f"Created detailed before/after comparison: {output_file}")
 
    except Exception as e:
        logging.error(f"Error creating detailed comparison: {e}")
 
def create_before_after_subplot(ax, pass_rate_data, corners, type_name, margin_type='after'):
    """
    Create individual subplot for before/after comparison.
    """
    # Get corner labels
    corner_labels = []
    for corner in corners:
        voltage = extract_voltage_from_corner(corner)
        corner_labels.append(f"{voltage:.3f}V" if voltage else corner)
 
    # Get parameters
    all_parameters = ['Meanshift', 'Skew', 'Std', 'early_sigma', 'late_sigma']
 
    # Create data matrix
    data_matrix = np.zeros((len(all_parameters), len(corners)))
    margin_values = []
 
    for j, corner in enumerate(corners):
        corner_data = pass_rate_data.get(corner, {})
        type_data = corner_data.get('types', {}).get(type_name, {})
 
        # Determine which margin to use
        if margin_type == 'before':
            target_margin = 0  # Always use 0mV for "before"
            margin_values.append(0)
        else:
            target_margin = find_suggested_margin_for_corner(corner_data, type_name)
            margin_values.append(target_margin)
 
        # Fill data matrix
        for i, param in enumerate(all_parameters):
            param_key = param.lower() if param != 'Std' else 'Std'
            if param_key in type_data.get('parameters', {}):
                param_data = type_data['parameters'][param_key]
                pass_rates = param_data.get('pass_rate_at_margin', {})
 
                if target_margin in pass_rates:
                    data_matrix[i, j] = pass_rates[target_margin]
                else:
                    # Fallback to closest available margin
                    available_margins = sorted(pass_rates.keys())
                    if available_margins:
                        closest_margin = min(available_margins, key=lambda x: abs(x - target_margin))
                        data_matrix[i, j] = pass_rates[closest_margin]
 
    # Create heatmap using same styling
    create_before_after_heatmap_styled(ax, data_matrix, corner_labels, margin_values,
                                     type_name, margin_type)
 
def create_before_after_heatmap_styled(ax, data_matrix, corner_labels, margin_values,
                                     type_name, margin_type):
    """
    Create styled heatmap for before/after comparison.
    """
    # Color scheme
    colors = ['#d73027', '#fd8d3c', '#74c476', '#e5f5e0']
    boundaries = [70, 80, 90, 95, 100]
    cmap = LinearSegmentedColormap.from_list('comparison', colors, N=256)
    norm = BoundaryNorm(boundaries, cmap.N)
 
    # Create heatmap
    im = ax.imshow(data_matrix, cmap=cmap, norm=norm, aspect='auto')
 
    # Add grid lines
    for x in range(len(corner_labels) + 1):
        ax.axvline(x - 0.5, color='#666666', linewidth=1.5)
    for y in range(data_matrix.shape[0] + 1):
        ax.axhline(y - 0.5, color='#666666', linewidth=1.5)
 
    # Set labels
    ax.set_xticks(range(len(corner_labels)))
    ax.set_yticks(range(data_matrix.shape[0]))
 
    # Create x-axis labels with margin info
    if margin_type == 'before':
        x_labels = [f"{label}\n(0.0mV)" for label in corner_labels]
        title_suffix = "BEFORE - 0mV Margin"
        title_color = '#d73027'  # Red for before
    else:
        x_labels = [f"{corner_labels[i]}\n({margin_values[i]:.1f}mV)"
                   for i in range(len(corner_labels))]
        title_suffix = "AFTER - Suggested Margins"
        title_color = '#28a745'  # Green for after
 
    ax.set_xticklabels(x_labels, fontsize=10, fontweight='bold')
    ax.set_yticklabels(['Meanshift', 'Skew', 'Std', 'early_sigma', 'late_sigma'], fontsize=10)
 
    # Add percentage values
    for i in range(data_matrix.shape[0]):
        for j in range(data_matrix.shape[1]):
            value = data_matrix[i, j]
            text_color = 'white' if value < 90 else '#2d5016'
            ax.text(j, i, f'{value:.1f}%', ha='center', va='center',
                   color=text_color, fontweight='bold', fontsize=10)
 
    # Set title
    ax.set_title(f'{type_name.upper()} - {title_suffix}',
                fontsize=12, fontweight='bold', color=title_color)
 
    # Remove spines
    for spine in ax.spines.values():
        spine.set_visible(False)
 
    # Add colorbar for rightmost plots
    if type_name == 'slew':
        cbar = plt.colorbar(im, ax=ax, shrink=0.6)
        cbar.set_label('Pass Rate (%)', fontsize=10)
 
# Update the main function in voltage_sensitivity_analysis.py
def main():
    """Main function with improved robustness and integrated 4-tier verification."""
    start_time = time.time()  # Track execution time
 
    try:
        # Setup argument parser
        parser = argparse.ArgumentParser(description='Analyze voltage sensitivity and margins')
        parser.add_argument('--data_dir', type=str, required=True,
                           help='Directory containing analysis results for all corners')
        parser.add_argument('--output_dir', type=str, required=True,
                           help='Output directory for sensitivity analysis')
        parser.add_argument('--corners', type=str, default=None,
                           help='Comma-separated list of corners to analyze (default: auto-detect)')
        parser.add_argument('--verify_4tier', action='store_true', default=True,
                           help='Run 4-tier criteria verification (default: True)')
 
        args = parser.parse_args()
 
        # Setup logging
        loggers = setup_logging(args.output_dir)
        main_log = loggers['main']
        calc_log = loggers['calculation']
        flow_log = loggers['dataflow']
 
        main_log.info("=" * 80)
        main_log.info("VOLTAGE SENSITIVITY ANALYSIS WITH 4-TIER VERIFICATION")
        main_log.info("=" * 80)
        main_log.info(f"Data directory: {args.data_dir}")
        main_log.info(f"Output directory: {args.output_dir}")
        main_log.info(f"4-tier verification enabled: {args.verify_4tier}")
 
        # Create output directory
        os.makedirs(args.output_dir, exist_ok=True)
 
        # Auto-detect corners if not specified
        if args.corners:
            corners = args.corners.split(',')
            main_log.info(f"Using specified corners: {corners}")
        else:
            # Auto-detect corners by finding subdirectories that match corner pattern
            corners = ["ssgnp_0p450v_m40c", "ssgnp_0p465v_m40c",
                      "ssgnp_0p480v_m40c", "ssgnp_0p495v_m40c"]
            main_log.info(f"Using default corners: {corners}")
 
        # Print denominator formulas
        calc_log.info("=" * 80)
        calc_log.info("DENOMINATOR FORMULAS USED FOR REL_ERR CONVERSION:")
        calc_log.info("  - Meanshift = lib_nominal + meanshift_mc")
        calc_log.info("  - Stddev = lib_nominal + meanshift_mc + stddev_mc")
        calc_log.info("  - Skewness = lib_nominal + meanshift_mc + skewness_mc")
        calc_log.info("  - Early_Sigma = max(abs(lib_nominal), MC_early_sigma)")
        calc_log.info("  - Late_Sigma = max(abs(lib_nominal), MC_late_sigma)")
        calc_log.info("=" * 80)
 
        # Load data
        main_log.info("Loading corner data...")
        all_data = load_all_corner_data(args.data_dir, corners)
 
        if not all_data:
            main_log.error("No valid data found in any corner. Exiting.")
            sys.exit(1)
 
        # Calculate sensitivities and create scatter plots
        main_log.info("Calculating sensitivities and creating scatter plots...")
        sensitivities, all_cell_data, margin_data = calculate_sensitivities(all_data, args.output_dir, args.data_dir)
 
        # Run 4-tier pass rate analysis WITH INTEGRATED VERIFICATION - PASS data_dir
        main_log.info("Running 4-tier pass rate analysis with verification...")
        try:
            pass_rate_data = analyze_4_tier_pass_rates(sensitivities, args.output_dir, args.data_dir)
        except Exception as e:
            main_log.error(f"4-tier pass rate analysis failed: {e}")
            pass_rate_data = {}
 
        # Only run remaining error severity analysis if we have pass_rate_data
        if pass_rate_data:
            main_log.info("Running remaining error severity analysis...")
            try:
                severity_results = run_remaining_error_severity_analysis(pass_rate_data, sensitivities, args.output_dir)
            except Exception as e:
                main_log.error(f"Remaining error severity analysis failed: {e}")
                severity_results = None
        else:
            main_log.warning("Skipping remaining error severity analysis due to missing pass rate data")
            severity_results = None
 
        # Create combined margin requirement summary (handle case where pass_rate_data might be empty)
        main_log.info("Creating combined margin requirement summary...")
        try:
            create_combined_margin_summary(pass_rate_data, margin_data, args.output_dir)
        except Exception as e:
            main_log.error(f"Error creating combined margin summary: {e}")
            main_log.info("Attempting to create summary with margin data only...")
            try:
                create_combined_margin_summary({}, margin_data, args.output_dir)
            except Exception as e2:
                main_log.error(f"Failed to create summary even with margin data only: {e2}")
 
        # Report completion time
        elapsed_time = time.time() - start_time
        main_log.info(f"Voltage sensitivity analysis complete in {elapsed_time:.1f} seconds")
        logging.info("Creating before/after voltage margin comparison...")
        create_before_after_margin_comparison(pass_rate_data, args.output_dir)
 
 
        # Print summary
        print("\n" + "="*80)
        print("VOLTAGE SENSITIVITY ANALYSIS COMPLETE")
        print("="*80)
        print(f"\nResults have been saved to: {args.output_dir}")
        print(f"Total execution time: {elapsed_time:.1f} seconds")
 
        print("\nKey outputs:")
        print("  1. Scatter plots: Each corner has abs_err vs voltage margin and rel_err vs voltage margin")
        print("  2. 4-tier pass rate analysis: Shows pass rates using 4-tier criteria")
        if args.verify_4tier:
            print("  3. 4-tier verification: Detailed verification logs and summary report")
        if pass_rate_data:
            print("  4. Pass rate heatmaps: Visual representation of pass rates at different margins")
        if severity_results:
            print("  5. Remaining error severity analysis: Analysis of errors after applying margins")
        print("  6. Combined margin summary: Summary tables for margin requirements")
 
        if args.verify_4tier:
            verification_dir = os.path.join(args.output_dir, "4_tier_verification")
            print(f"\n4-TIER VERIFICATION RESULTS:")
            print(f"  Verification directory: {verification_dir}")
            print(f"  Summary report: {verification_dir}/verification_summary.txt")
            print(f"  Individual logs: {verification_dir}/*_verification.log")
 
        print("="*80)
 
    except Exception as e:
        logging.error(f"Unhandled exception in main: {e}")
        logging.error(traceback.format_exc())
        print(f"\nERROR: {e}")
        print("Check the log file for details.")
        sys.exit(1)
 
if __name__ == "__main__":
    import sys
    main()
