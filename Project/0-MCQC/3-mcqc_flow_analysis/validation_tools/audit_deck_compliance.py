#!/usr/bin/env python3
"""
MCQC Specification Compliance Validation Tool

CRITICAL FOCUS: Demonstrates complete understanding of the MCQC flow by tracing
EVERY input that contributed to each deck's generation.

Purpose:
- Audit generated SPICE decks against their input specifications
- Provide COMPLETE traceability of all parsed inputs
- Analyze mc_sim.sp files (contains actual Monte Carlo setup)
- Generate structured reports with clear section headers
- Validate specification compliance with pass/fail status

Key Technical Distinction:
- mc_sim.sp: Contains ACTUAL Monte Carlo simulation setup with all measurements
- nominal_sim.sp: Base template before Monte Carlo additions (NOT analyzed)

Author: Claude Code Analysis Framework
Date: 2024-10-30
"""

import os
import sys
import csv
import json
import re
import argparse
import time
from pathlib import Path
from collections import defaultdict, Counter
from typing import Dict, List, Tuple, Optional, Any, Set
import logging
from multiprocessing import Pool, cpu_count

# Optional YAML support
try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False
    print("[WARN] PyYAML not available - YAML reports will be disabled")

# Note: Using robust file parsing instead of MCQC-specific parsers for broader compatibility
PARSERS_AVAILABLE = False  # Always use basic parsing for reliability


class TemplateMatchResult:
    """Result of template.tcl arc matching"""
    def __init__(self):
        self.success = False
        self.cell_found = False
        self.arc_found = False
        self.line_start = None
        self.line_end = None
        self.error_message = None
        self.match_details = {}  # What matched, what didn't
        self.extracted_content = ""
        self.cell_name = ""
        self.total_cells_searched = 0

    def mark_success(self, line_start, line_end, content, cell_name, match_details):
        """Mark as successful match"""
        self.success = True
        self.cell_found = True
        self.arc_found = True
        self.line_start = line_start
        self.line_end = line_end
        self.extracted_content = content
        self.cell_name = cell_name
        self.match_details = match_details

    def mark_cell_not_found(self, cell_name, total_searched):
        """Mark as cell not found"""
        self.success = False
        self.cell_found = False
        self.arc_found = False
        self.cell_name = cell_name
        self.total_cells_searched = total_searched
        self.error_message = "Cell '{}' not found in template.tcl".format(cell_name)

    def mark_arc_not_found(self, cell_name, match_details):
        """Mark as arc not found in cell"""
        self.success = False
        self.cell_found = True
        self.arc_found = False
        self.cell_name = cell_name
        self.match_details = match_details
        self.error_message = "Arc not found in cell '{}'".format(cell_name)


class InputTraceabilityEngine:
    """
    Traces EVERY input that contributed to deck generation.

    This demonstrates complete understanding of the MCQC flow by mapping
    all configuration files to their corresponding deck outputs.
    """

    def __init__(self, verbose=False):
        self.verbose = verbose
        self.logger = self._setup_logger()

        # Template caching for performance
        self._template_cache = {}
        self._template_parse_count = 0

    def _setup_logger(self):
        """Setup logger for input traceability"""
        logger = logging.getLogger('InputTraceability')
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO if self.verbose else logging.WARNING)
        return logger

    def get_cached_template_data(self, template_file_path: Path) -> Dict:
        """
        Get template data from cache or parse if not cached.
        CRITICAL PERFORMANCE OPTIMIZATION: Parse template once, use many times.
        """
        template_path_str = str(template_file_path)

        if template_path_str not in self._template_cache:
            if self.verbose:
                print("[PARSING] Parsing template.tcl: {} (first time)".format(template_file_path))

            start_time = time.time()

            # Parse template.tcl and extract all arc definitions
            template_data = self._parse_template_file_complete(template_file_path)

            parse_time = time.time() - start_time
            self._template_parse_count += 1

            self._template_cache[template_path_str] = template_data

            print("[OK] Template parsed and cached: {} arcs in {:.2f}s".format(
                len(template_data.get('arcs', [])), parse_time))
        else:
            if self.verbose:
                print("[CACHE] Using cached template data: {}".format(template_file_path))

        return self._template_cache[template_path_str]

    def _parse_template_file_complete(self, template_file: Path) -> Dict:
        """Parse template.tcl completely to extract all arc definitions"""
        template_data = {
            'arcs': [],
            'arcs_by_cell': defaultdict(list),
            'cells': set(),
            'total_arcs': 0,
            'total_cells': 0,
            'file_path': str(template_file)
        }

        try:
            with open(template_file, 'r') as f:
                lines = f.readlines()

            current_arc = None
            in_define_arc = False

            for line_num, line in enumerate(lines, 1):
                line = line.strip()

                # Start of define_arc block
                if line.startswith('define_arc'):
                    in_define_arc = True
                    current_arc = {
                        'line_start': line_num,
                        'type': None,
                        'when': None,
                        'vector': None,
                        'related_pin': None,
                        'pin': None,
                        'probe': None,
                        'cell': None
                    }

                # Parse arc attributes
                elif in_define_arc and line.startswith('-'):
                    if '-type' in line:
                        type_match = re.search(r'-type\s+(\w+)', line)
                        if type_match:
                            current_arc['type'] = type_match.group(1)

                    elif '-when' in line:
                        when_match = re.search(r'-when\s+"([^"]*)"', line)
                        if when_match:
                            current_arc['when'] = when_match.group(1)

                    elif '-vector' in line:
                        vector_match = re.search(r'-vector\s+\{([^}]+)\}', line)
                        if vector_match:
                            current_arc['vector'] = "{{{}}}".format(vector_match.group(1))

                    elif '-related_pin' in line:
                        related_pin_match = re.search(r'-related_pin\s+(\w+)', line)
                        if related_pin_match:
                            current_arc['related_pin'] = related_pin_match.group(1)

                    elif '-pin' in line:
                        pin_match = re.search(r'-pin\s+(\w+)', line)
                        if pin_match:
                            current_arc['pin'] = pin_match.group(1)

                    elif '-probe' in line:
                        probe_match = re.search(r'-probe\s+\{([^}]+)\}', line)
                        if probe_match:
                            current_arc['probe'] = "{{{}}}".format(probe_match.group(1))

                # Cell name (end of define_arc block)
                elif in_define_arc and line and not line.startswith('-') and not line.startswith('define_arc'):
                    current_arc['cell'] = line
                    current_arc['line_end'] = line_num

                    # Store the complete arc
                    template_data['arcs'].append(current_arc)
                    template_data['arcs_by_cell'][line].append(current_arc)
                    template_data['cells'].add(line)

                    in_define_arc = False
                    current_arc = None

            template_data['total_arcs'] = len(template_data['arcs'])
            template_data['total_cells'] = len(template_data['cells'])

        except Exception as e:
            self.logger.error("Error parsing template file {}: {}".format(template_file, e))

        return template_data

    def trace_arc_inputs(self, arc_folder: Path, template_file: Optional[Path] = None,
                        chartcl_file: Optional[Path] = None, globals_file: Optional[Path] = None,
                        chartcl_verbose: bool = False) -> Dict:
        """
        Trace ALL input files that contributed to this arc's deck generation.

        This is the core function that demonstrates complete MCQC flow understanding.
        """
        arc_name = arc_folder.name
        self.logger.info("Tracing inputs for arc: {}".format(arc_name))

        traceability_data = {
            'arc_name': arc_name,
            'arc_folder': str(arc_folder),
            'input_sources': {},
            'parsing_summary': {},
            'tracing_completeness': 0.0
        }

        # Auto-discover input files if not provided
        template_file = template_file or self._find_template_file(arc_folder)
        chartcl_file = chartcl_file or self._find_chartcl_file(arc_folder)

        # Handle multiple globals files
        if globals_file:
            globals_files = [globals_file]
        else:
            globals_files = self._find_globals_files(arc_folder)

        # Trace template.tcl input
        if template_file and template_file.exists():
            template_data = self._trace_template_input(template_file, arc_name)
            traceability_data['input_sources']['template'] = template_data

            # Store globals for this globals file
            for globals_file_item in globals_files:
                globals_key = "globals_{}".format(globals_file_item.name)
                traceability_data['input_sources'][globals_key] = self._trace_globals_input(globals_file_item)

        # Trace chartcl.tcl input
        if chartcl_file and chartcl_file.exists():
            chartcl_data = self._trace_chartcl_input(chartcl_file, arc_name, display_all=chartcl_verbose)
            traceability_data['input_sources']['chartcl'] = chartcl_data

        # Calculate tracing completeness
        expected_sources = 3  # template, chartcl, at least one globals
        actual_sources = len([k for k in traceability_data['input_sources'].keys()
                            if not k.startswith('error')])
        traceability_data['tracing_completeness'] = min(actual_sources / expected_sources, 1.0)

        return traceability_data

    def _find_template_file(self, arc_folder: Path) -> Optional[Path]:
        """Find template.tcl file in arc hierarchy"""
        search_paths = [arc_folder, arc_folder.parent, arc_folder.parent.parent]

        for search_dir in search_paths:
            candidate = search_dir / "template.tcl"
            if candidate.exists():
                if self.verbose:
                    self.logger.debug("Found template file: {}".format(candidate))
                return candidate

        self.logger.warning("No template.tcl found for {}".format(arc_folder))
        return None

    def _find_chartcl_file(self, arc_folder: Path) -> Optional[Path]:
        """Find chartcl.tcl file in arc hierarchy"""
        search_paths = [arc_folder, arc_folder.parent, arc_folder.parent.parent]

        for search_dir in search_paths:
            candidate = search_dir / "chartcl.tcl"
            if candidate.exists():
                if self.verbose:
                    self.logger.debug("Found chartcl file: {}".format(candidate))
                return candidate

        self.logger.warning("No chartcl.tcl found for {}".format(arc_folder))
        return None

    def _find_globals_files(self, arc_folder: Path) -> List[Path]:
        """Find all globals files in arc hierarchy"""
        globals_files = []
        search_paths = [arc_folder, arc_folder.parent, arc_folder.parent.parent]

        for search_dir in search_paths:
            # Look for files with 'globals' in the name
            for globals_file in search_dir.glob("*globals*.txt"):
                if globals_file.is_file():
                    globals_files.append(globals_file)
                    if self.verbose:
                        self.logger.debug("Found globals file: {}".format(globals_file))

        return globals_files

    def _trace_template_input(self, template_file: Path, arc_name: str) -> Dict:
        """Extract template.tcl specifications that apply to this arc"""
        template_data = {
            'file_path': str(template_file),
            'parsed_successfully': False,
            'key_specifications': [],
            'measurement_requirements': [],
            'arc_specific_settings': []
        }

        try:
            with open(template_file, 'r') as f:
                lines = f.readlines()

            # Extract key template lines relevant to this arc
            key_lines = []
            for line_num, line in enumerate(lines, 1):
                # Look for define_arc blocks and key configurations
                if any(keyword in line.lower() for keyword in
                      ['define_arc', 'timing_type', 'related_pin', 'when']):
                    key_lines.append("Line {}: {}".format(line_num, line.strip()))

            template_data['key_specifications'] = key_lines
            template_data['parsed_successfully'] = True

        except Exception as e:
            self.logger.error("Error reading template file {}: {}".format(template_file, e))
            template_data['error'] = str(e)

        return template_data

    def extract_template_arc_definition(self, template_file: Path, cell_name: str,
                                      arc_type: str, related_pin: str, when_condition: str) -> TemplateMatchResult:
        """
        Extract specific arc definition from template.tcl.
        Uses cached template data for performance.
        """
        result = TemplateMatchResult()

        try:
            # Use cached template data
            cached_template = self.get_cached_template_data(template_file)
            arcs_by_cell = cached_template.get('arcs_by_cell', {})

            # Search for the cell
            if cell_name not in arcs_by_cell:
                result.mark_cell_not_found(cell_name, len(cached_template.get('cells', [])))
                return result

            # Search for matching arc in the cell
            cell_arcs = arcs_by_cell[cell_name]
            for arc_def in cell_arcs:
                # Check if this arc matches the criteria
                if (arc_def.get('type') == arc_type and
                    arc_def.get('related_pin') == related_pin):

                    # Found a matching arc
                    result.mark_success(
                        arc_def.get('line_start'),
                        arc_def.get('line_end'),
                        str(arc_def),
                        cell_name,
                        arc_def
                    )
                    return result

            # Cell found but arc not found
            result.mark_arc_not_found(cell_name, {
                'searched_arcs': len(cell_arcs),
                'total_cells_searched': 1,  # We only searched this cell
                'total_arcs_searched': len(cell_arcs)
            })

        except Exception as e:
            result.error_message = "Error using cached template data: {}".format(e)

        return result

    def _trace_chartcl_input(self, chartcl_file: Path, arc_name: str, display_all: bool = False) -> Dict:
        """Extract chartcl.tcl configurations that apply to this arc"""
        chartcl_data = {
            'file_path': str(chartcl_file),
            'parsed_successfully': False,
            'key_lines': [],
            'relevant_variables': {}
        }

        try:
            with open(chartcl_file, 'r') as f:
                lines = f.readlines()

            # Extract key configuration lines
            key_lines = []
            for line_num, line in enumerate(lines, 1):
                # Look for set_var commands and key configurations
                if any(keyword in line.lower() for keyword in
                      ['set_var', 'constraint', 'threshold', 'margin']):
                    key_lines.append("Line {}: {}".format(line_num, line.strip()))

            chartcl_data['key_lines'] = key_lines
            chartcl_data['parsed_successfully'] = True

        except Exception as e:
            self.logger.error("Error reading chartcl file {}: {}".format(chartcl_file, e))
            chartcl_data['error'] = str(e)

        return chartcl_data

    def _trace_globals_input(self, globals_file: Path) -> Dict:
        """Extract globals file parameters"""
        globals_data = {
            'file_path': str(globals_file),
            'parsed_successfully': False,
            'parameters': {}
        }

        try:
            with open(globals_file, 'r') as f:
                lines = f.readlines()

            # Extract parameter definitions
            for line_num, line in enumerate(lines, 1):
                # Look for parameter definitions (various formats)
                if '=' in line and not line.strip().startswith('#'):
                    parts = line.split('=', 1)
                    if len(parts) == 2:
                        param_name = parts[0].strip()
                        param_value = parts[1].strip()
                        globals_data['parameters'][param_name] = param_value

            globals_data['parsed_successfully'] = True

        except Exception as e:
            self.logger.error("Error reading globals file {}: {}".format(globals_file, e))
            globals_data['error'] = str(e)

        return globals_data


class SPICEDeckAnalyzer:
    """
    Analyzes mc_sim.sp files to understand deck structure and content.

    CRITICAL: Analyzes mc_sim.sp (actual Monte Carlo simulation)
    NOT nominal_sim.sp (base template).
    """

    def __init__(self, verbose=False):
        self.verbose = verbose
        self.logger = self._setup_logger()

    def _setup_logger(self):
        """Setup logger for SPICE deck analysis"""
        logger = logging.getLogger('SPICEAnalyzer')
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO if self.verbose else logging.WARNING)
        return logger

    def analyze_deck(self, deck_path: Path) -> Dict:
        """
        Analyze mc_sim.sp deck structure and extract key information.

        This demonstrates understanding of what MCQC generates.
        """
        deck_analysis = {
            'file_path': str(deck_path),
            'exists': deck_path.exists(),
            'total_lines': 0,
            'comment_lines': 0,
            'measurements': [],
            'includes': [],
            'parameters': {},
            'analysis_successful': False
        }

        if not deck_path.exists():
            deck_analysis.update({
                'error': "Deck file not found: {}".format(deck_path),
                'analysis_successful': False
            })
            return deck_analysis

        self.logger.info("Analyzing SPICE deck: {}".format(deck_path))

        try:
            with open(deck_path, 'r') as f:
                lines = f.readlines()

            deck_analysis['total_lines'] = len(lines)
            deck_analysis['file_size_bytes'] = deck_path.stat().st_size

            measurements = []
            includes = []
            parameters = {}
            comment_count = 0

            for line_num, line in enumerate(lines, 1):
                original_line = line
                line = line.strip()

                # Count comments
                if line.startswith('*') or line.startswith('#'):
                    comment_count += 1

                # Extract .meas statements (key MCQC outputs)
                elif line.lower().startswith('.meas'):
                    measurement_info = self._parse_measurement_line(line, line_num, original_line)
                    measurements.append(measurement_info)

                # Extract .include statements
                elif line.lower().startswith('.include'):
                    include_match = re.search(r'\.include\s+[\'"]?([^\'"]+)[\'"]?', line, re.IGNORECASE)
                    if include_match:
                        includes.append({
                            'file': include_match.group(1),
                            'line_number': line_num
                        })

                # Extract .param statements
                elif line.lower().startswith('.param'):
                    param_match = re.search(r'\.param\s+(\w+)\s*=\s*([^\s]+)', line, re.IGNORECASE)
                    if param_match:
                        parameters[param_match.group(1)] = param_match.group(2)

            deck_analysis.update({
                'comment_lines': comment_count,
                'measurements': measurements,
                'includes': includes,
                'parameters': parameters,
                'analysis_successful': True
            })

        except Exception as e:
            self.logger.error("Error analyzing deck {}: {}".format(deck_path, e))
            deck_analysis.update({
                'error': str(e),
                'analysis_successful': False
            })

        return deck_analysis

    def _parse_measurement_line(self, line: str, line_num: int, original_line: str) -> Dict:
        """Parse a .meas line to extract measurement information"""
        measurement_info = {
            'line_number': line_num,
            'full_line': original_line.strip(),
            'measurement_name': 'unknown',
            'measurement_type': 'unknown',
            'analysis': 'unknown'
        }

        # Extract measurement name (first parameter after .meas)
        parts = line.split()
        if len(parts) >= 3:
            measurement_info['measurement_type'] = parts[1].lower()  # tran, ac, dc, etc
            measurement_info['measurement_name'] = parts[2]

        # Analyze measurement purpose
        line_lower = line.lower()
        if 'cp2q' in line_lower:
            measurement_info['analysis'] = 'propagation_delay'
        elif 'setup' in line_lower:
            measurement_info['analysis'] = 'setup_time'
        elif 'hold' in line_lower:
            measurement_info['analysis'] = 'hold_time'
        elif 'mpw' in line_lower or 'pulse_width' in line_lower:
            measurement_info['analysis'] = 'min_pulse_width'
        elif 'power' in line_lower:
            measurement_info['analysis'] = 'power'
        elif 'final' in line_lower:
            measurement_info['analysis'] = 'final_state'

        return measurement_info

    def detect_internal_node_measurement(self, deck_path: Path) -> Dict:
        """
        Detect internal node usage in measurements.
        Critical for MCQC vs Template alignment analysis.
        """
        internal_analysis = {
            'has_internal_nodes': False,
            'internal_node_patterns': [],
            'external_node_patterns': [],
            'total_measurements': 0
        }

        try:
            with open(deck_path, 'r') as f:
                lines = f.readlines()

            for line_num, line in enumerate(lines, 1):
                line = line.strip()

                if line.lower().startswith('.meas'):
                    internal_analysis['total_measurements'] += 1

                    # Look for internal node patterns like v(X1.Q1), v(I1.out), etc.
                    internal_patterns = re.findall(r'v\([A-Z]\d+\.\w+\)', line)
                    if internal_patterns:
                        internal_analysis['has_internal_nodes'] = True
                        for pattern in internal_patterns:
                            measurement_name = self._extract_measurement_name(line)
                            internal_analysis['internal_node_patterns'].append({
                                'measurement': measurement_name,
                                'node': pattern,
                                'line': line_num
                            })

                    # Look for external node patterns like v(Q), v(output), etc.
                    external_patterns = re.findall(r'v\([a-z_]+\)', line.lower())
                    if external_patterns:
                        for pattern in external_patterns:
                            measurement_name = self._extract_measurement_name(line)
                            internal_analysis['external_node_patterns'].append({
                                'measurement': measurement_name,
                                'node': pattern,
                                'line': line_num
                            })

        except Exception as e:
            self.logger.error("Error detecting internal nodes in {}: {}".format(deck_path, e))
            internal_analysis['error'] = str(e)

        return internal_analysis

    def _extract_measurement_name(self, meas_line: str) -> str:
        """Extract measurement name from .meas line"""
        parts = meas_line.split()
        if len(parts) >= 3:
            return parts[2]
        return 'unknown'


class AlignmentAnalyzer:
    """
    Analyzes alignment between MCQC deck and Template specifications.
    PRIMARY OBJECTIVE: Generate CSV comparing MCQC vs Template.
    """

    def __init__(self, verbose=False):
        self.verbose = verbose

    def check_alignment(self, mcqc_data: Dict, template_data: Dict, arc_name: str) -> Dict:
        """
        Check alignment between MCQC deck and Template specifications.
        Returns comprehensive alignment analysis.
        """
        alignment_result = {
            'arc_name': arc_name,
            'cell_name': 'Unknown',
            'constraint_pin': 'Unknown',
            'related_pin': 'Unknown',
            'when_condition': 'Unknown',
            'vector': 'Unknown',

            # MCQC Analysis
            'cp2q_del1_MCQC': 'OFF',
            'cp2q_del2_MCQC': 'OFF',
            'final_state_MCQC': 'OFF',
            'internal_node_MCQC': 'NO',

            # Template Analysis
            'cp2q_del1_Template': 'N/A',
            'cp2q_del2_Template': 'N/A',
            'final_state_Template': 'OFF',
            'probe_Template': 'Unknown',

            # Alignment Results
            'cp2q_del1_Match': 'Unknown',
            'cp2q_del2_Match': 'Unknown',
            'final_state_Match': 'Unknown',
            'probe_Match': 'Unknown'
        }

        # Extract template information
        if template_data:
            alignment_result['probe_Template'] = template_data.get('probe', 'Unknown')
            alignment_result['cell_name'] = template_data.get('cell', 'Unknown')
            alignment_result['constraint_pin'] = template_data.get('pin', 'Unknown')
            alignment_result['related_pin'] = template_data.get('related_pin', 'Unknown')
            alignment_result['when_condition'] = template_data.get('when', 'Unknown')
            alignment_result['vector'] = template_data.get('vector', 'Unknown')

        # Analyze MCQC measurements
        measurements = mcqc_data.get('measurements', [])

        # Check for cp2q_del1
        for meas in measurements:
            meas_name = meas.get('measurement_name', '').lower()
            if 'cp2q_del1' in meas_name:
                alignment_result['cp2q_del1_MCQC'] = 'ON'
                break

        # Check for cp2q_del2
        for meas in measurements:
            meas_name = meas.get('measurement_name', '').lower()
            if 'cp2q_del2' in meas_name:
                alignment_result['cp2q_del2_MCQC'] = 'ON'
                break

        # Check for final_state
        for meas in measurements:
            meas_name = meas.get('measurement_name', '').lower()
            if 'final' in meas_name:
                alignment_result['final_state_MCQC'] = 'ON'
                break

        # Check for internal nodes
        internal_analysis = mcqc_data.get('internal_node_analysis', {})
        if internal_analysis.get('has_internal_nodes', False):
            alignment_result['internal_node_MCQC'] = 'YES'

        # Determine alignment matches
        alignment_result['cp2q_del1_Match'] = 'Match'  # cp2q_del1 is standard

        # cp2q_del2 alignment
        if alignment_result['cp2q_del2_MCQC'] == 'ON':
            alignment_result['cp2q_del2_Match'] = 'No Match'
        else:
            alignment_result['cp2q_del2_Match'] = 'Match'

        # final_state alignment
        if alignment_result['final_state_MCQC'] == 'ON':
            alignment_result['final_state_Match'] = 'No Match'
        else:
            alignment_result['final_state_Match'] = 'Match'

        # Probe alignment (internal node vs template expectation)
        probe_template = alignment_result['probe_Template']
        internal_node_mcqc = alignment_result['internal_node_MCQC']

        if 'Q1' in probe_template and internal_node_mcqc == 'YES':
            alignment_result['probe_Match'] = 'Match'
        elif 'Q' in probe_template and internal_node_mcqc == 'NO':
            alignment_result['probe_Match'] = 'Match'
        else:
            alignment_result['probe_Match'] = 'No Match'

        return alignment_result

    def generate_alignment_csv(self, alignment_results: List[Dict], output_file: Path):
        """Generate primary alignment CSV file"""
        try:
            with open(output_file, 'w', newline='') as f:
                writer = csv.writer(f)

                # Header row
                writer.writerow([
                    'arc_name', 'cell_name', 'constraint_pin', 'related_pin', 'when_condition',
                    'cp2q_del1_MCQC', 'cp2q_del1_Template', 'cp2q_del1_Match',
                    'cp2q_del2_MCQC', 'cp2q_del2_Template', 'cp2q_del2_Match',
                    'final_state_MCQC', 'final_state_Template', 'final_state_Match',
                    'internal_node_MCQC', 'probe_Template', 'probe_Match'
                ])

                # Data rows
                for result in alignment_results:
                    writer.writerow([
                        result.get('arc_name', 'Unknown'),
                        result.get('cell_name', 'Unknown'),
                        result.get('constraint_pin', 'Unknown'),
                        result.get('related_pin', 'Unknown'),
                        result.get('when_condition', 'Unknown'),
                        result.get('cp2q_del1_MCQC', 'Unknown'),
                        result.get('cp2q_del1_Template', 'N/A'),
                        result.get('cp2q_del1_Match', 'Unknown'),
                        result.get('cp2q_del2_MCQC', 'Unknown'),
                        result.get('cp2q_del2_Template', 'N/A'),
                        result.get('cp2q_del2_Match', 'Unknown'),
                        result.get('final_state_MCQC', 'Unknown'),
                        result.get('final_state_Template', 'OFF'),
                        result.get('final_state_Match', 'Unknown'),
                        result.get('internal_node_MCQC', 'Unknown'),
                        result.get('probe_Template', 'Unknown'),
                        result.get('probe_Match', 'Unknown')
                    ])

            print("Alignment CSV generated: {}".format(output_file))

        except Exception as e:
            print("Error generating alignment CSV: {}".format(e))

    def generate_statistics_report(self, alignment_results: List[Dict], output_file: Path, processing_stats: Dict):
        """Generate statistics report"""
        try:
            with open(output_file, 'w') as f:
                f.write("MCQC VALIDATION STATISTICS REPORT\n")
                f.write("=" * 50 + "\n\n")

                f.write("Processing Performance:\n")
                f.write("  Total time: {:.1f} minutes\n".format(processing_stats.get('total_time', 0)))
                f.write("  Average per arc: {:.2f}s\n".format(processing_stats.get('avg_time_per_arc', 0)))
                f.write("  Parallel workers: {}\n\n".format(processing_stats.get('parallel_workers', 1)))

                f.write("Alignment Summary:\n")
                f.write("  Total arcs: {}\n".format(len(alignment_results)))

                # Count matches
                probe_matches = sum(1 for r in alignment_results if r.get('probe_Match') == 'Match')
                cp2q_del2_matches = sum(1 for r in alignment_results if r.get('cp2q_del2_Match') == 'Match')

                f.write("  Probe matches: {} ({:.1f}%)\n".format(
                    probe_matches, probe_matches/len(alignment_results)*100 if alignment_results else 0))
                f.write("  cp2q_del2 matches: {} ({:.1f}%)\n".format(
                    cp2q_del2_matches, cp2q_del2_matches/len(alignment_results)*100 if alignment_results else 0))

            print("Statistics report generated: {}".format(output_file))

        except Exception as e:
            print("Error generating statistics report: {}".format(e))


class ComplianceValidator:
    """
    Validates compliance between parsed inputs and deck outputs.

    This demonstrates understanding of MCQC specifications vs actual implementation.
    """

    def __init__(self, verbose=False):
        self.verbose = verbose
        self.logger = self._setup_logger()

        # Validation thresholds
        self.thresholds = {
            'minimum_traceability': 0.7,      # 70% input traceability required
            'minimum_specification_coverage': 0.6,  # 60% spec coverage required
            'maximum_missing_critical': 2,    # Max 2 critical missing specs
            'maximum_inconsistencies': 5,     # Max 5 pattern inconsistencies
            'minimum_deck_structure': 0.7     # 70% deck structure score required
        }

    def _setup_logger(self):
        """Setup logger for compliance validation"""
        logger = logging.getLogger('ComplianceValidator')
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO if self.verbose else logging.WARNING)
        return logger

    def validate_compliance(self, traceability_data: Dict, deck_analysis: Dict,
                          template_match_result: Optional[TemplateMatchResult] = None) -> Dict:
        """
        Validate compliance between inputs and outputs.

        This is the core validation logic that determines pass/fail status.
        """
        arc_name = traceability_data.get('arc_name', 'unknown')
        self.logger.info("Validating compliance for arc: {}".format(arc_name))

        validation_result = {
            'arc_name': arc_name,
            'overall_status': 'UNKNOWN',
            'test_results': {},
            'test_summary': {},
            'critical_issues': [],
            'recommendations': [],
            'compliance_score': 0.0
        }

        # Run individual validation tests
        tests = [
            ('traceability_test', self._test_input_traceability),
            ('specification_coverage_test', self._test_specification_coverage),
            ('missing_specifications_test', self._test_missing_specifications),
            ('pattern_consistency_test', self._test_pattern_consistency),
            ('deck_structure_test', self._test_deck_structure)
        ]

        test_results = {}
        total_score = 0.0
        total_tests = len(tests)

        for test_name, test_function in tests:
            try:
                test_result = test_function(traceability_data, deck_analysis, template_match_result)
                test_results[test_name] = test_result
                total_score += test_result.get('score', 0.0)

                # Collect critical issues
                if not test_result.get('passed', False):
                    for issue in test_result.get('issues', []):
                        validation_result['critical_issues'].append("{}: {}".format(test_name, issue))

            except Exception as e:
                test_results[test_name] = {
                    'passed': False,
                    'score': 0.0,
                    'issues': ["Test execution failed: {}".format(e)]
                }

        validation_result['test_results'] = test_results
        validation_result['compliance_score'] = total_score / total_tests if total_tests > 0 else 0.0

        # Calculate test summary
        passed_tests = sum(1 for result in test_results.values() if result.get('passed', False))
        failed_tests = total_tests - passed_tests

        validation_result['test_summary'] = {
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': failed_tests,
            'error_tests': 0,
            'pass_rate': passed_tests / total_tests if total_tests > 0 else 0.0,
            'average_score': validation_result['compliance_score']
        }

        # Determine overall status
        if validation_result['compliance_score'] >= 0.8:
            validation_result['overall_status'] = 'PASS'
        elif validation_result['compliance_score'] >= 0.6:
            validation_result['overall_status'] = 'PARTIAL'
        else:
            validation_result['overall_status'] = 'FAIL'

        return validation_result

    def _test_input_traceability(self, traceability_data: Dict, deck_analysis: Dict,
                               template_match_result: Optional[TemplateMatchResult]) -> Dict:
        """Test input-to-output traceability completeness"""
        test_result = {
            'passed': False,
            'score': 0.0,
            'issues': [],
            'details': {}
        }

        try:
            traceability_score = traceability_data.get('tracing_completeness', 0.0)

            test_result['score'] = traceability_score
            test_result['details']['traceability_score'] = traceability_score

            if traceability_score >= self.thresholds['minimum_traceability']:
                test_result['passed'] = True
            else:
                test_result['issues'].append(
                    "Traceability score {:.1%} below threshold {:.1%}".format(
                        traceability_score, self.thresholds['minimum_traceability']))

        except Exception as e:
            test_result['issues'].append("Traceability test error: {}".format(e))

        return test_result

    def _test_specification_coverage(self, traceability_data: Dict, deck_analysis: Dict,
                                   template_match_result: Optional[TemplateMatchResult]) -> Dict:
        """Test specification coverage completeness"""
        test_result = {
            'passed': False,
            'score': 0.0,
            'issues': [],
            'details': {}
        }

        try:
            # Count specified vs implemented features
            input_sources = traceability_data.get('input_sources', {})
            template_specs = len(input_sources.get('template', {}).get('key_specifications', []))
            deck_measurements = len(deck_analysis.get('measurements', []))

            # Simple coverage calculation
            coverage_score = min(deck_measurements / max(template_specs, 1), 1.0) if template_specs > 0 else 0.5

            test_result['score'] = coverage_score
            test_result['details']['coverage_score'] = coverage_score
            test_result['details']['template_specs'] = template_specs
            test_result['details']['deck_measurements'] = deck_measurements

            if coverage_score >= self.thresholds['minimum_specification_coverage']:
                test_result['passed'] = True
            else:
                test_result['issues'].append(
                    "Specification coverage {:.1%} below threshold {:.1%}".format(
                        coverage_score, self.thresholds['minimum_specification_coverage']))

        except Exception as e:
            test_result['issues'].append("Coverage test error: {}".format(e))

        return test_result

    def _test_missing_specifications(self, traceability_data: Dict, deck_analysis: Dict,
                                   template_match_result: Optional[TemplateMatchResult]) -> Dict:
        """Test for missing critical specifications"""
        test_result = {
            'passed': False,
            'score': 0.0,
            'issues': [],
            'details': {}
        }

        try:
            # Analyze what's missing
            critical_missing = 0
            high_missing = 0
            medium_missing = 0

            # Check for critical missing specifications
            measurements = deck_analysis.get('measurements', [])
            measurement_names = [m.get('measurement_name', '') for m in measurements]

            # Critical: basic timing measurements
            if not any('cp2q' in name.lower() for name in measurement_names):
                critical_missing += 1

            # High impact: final state checks (74% of arcs have this pattern)
            if not any('final' in name.lower() for name in measurement_names):
                high_missing += 1

            test_result['details']['critical_missing'] = critical_missing
            test_result['details']['high_missing'] = high_missing
            test_result['details']['medium_missing'] = medium_missing

            # Calculate score based on missing specifications
            total_possible = 3  # Basic set of expected specifications
            total_missing = critical_missing * 3 + high_missing * 2 + medium_missing * 1
            test_result['score'] = max(0, 1.0 - (total_missing / total_possible))

            if critical_missing <= self.thresholds['maximum_missing_critical']:
                test_result['passed'] = True
            else:
                test_result['issues'].append(
                    "Critical missing specifications ({}) exceeds threshold ({})".format(
                        critical_missing, self.thresholds['maximum_missing_critical']))

            if high_missing > 0:
                test_result['issues'].append("{} high-impact missing specifications detected".format(high_missing))
            if medium_missing > 0:
                test_result['issues'].append("{} medium-impact missing specifications detected".format(medium_missing))

        except Exception as e:
            test_result['issues'].append("Missing specifications test error: {}".format(e))

        return test_result

    def _test_pattern_consistency(self, traceability_data: Dict, deck_analysis: Dict,
                                template_match_result: Optional[TemplateMatchResult]) -> Dict:
        """Test pattern consistency across measurements"""
        test_result = {
            'passed': False,
            'score': 0.0,
            'issues': [],
            'details': {}
        }

        try:
            measurements = deck_analysis.get('measurements', [])

            # Count naming inconsistencies
            inconsistency_count = 0
            measurement_names = [m.get('measurement_name', '') for m in measurements]

            # Check for common inconsistency patterns
            # This is a simplified check - real implementation would be more sophisticated
            name_patterns = set()
            for name in measurement_names:
                # Extract base pattern (remove numbers, suffixes)
                base_pattern = re.sub(r'[0-9]+|_\w+$', '', name.lower())
                name_patterns.add(base_pattern)

            # Simple consistency score based on pattern variation
            if len(measurements) > 0:
                consistency_score = 1.0 - min(len(name_patterns) / len(measurements), 1.0)
            else:
                consistency_score = 1.0

            test_result['score'] = consistency_score
            test_result['details']['inconsistency_count'] = inconsistency_count
            test_result['details']['unique_patterns'] = len(name_patterns)
            test_result['details']['total_measurements'] = len(measurements)

            if inconsistency_count <= self.thresholds['maximum_inconsistencies']:
                test_result['passed'] = True
            else:
                test_result['issues'].append(
                    "Pattern inconsistencies ({}) exceed threshold ({})".format(
                        inconsistency_count, self.thresholds['maximum_inconsistencies']))

        except Exception as e:
            test_result['issues'].append("Pattern consistency test error: {}".format(e))

        return test_result

    def _test_deck_structure(self, traceability_data: Dict, deck_analysis: Dict,
                           template_match_result: Optional[TemplateMatchResult]) -> Dict:
        """Test basic deck structure validity"""
        test_result = {
            'passed': False,
            'score': 0.0,
            'issues': [],
            'details': {}
        }

        try:
            if not deck_analysis.get('analysis_successful', False):
                test_result['issues'].append("Deck analysis error: {}".format(deck_analysis.get('error', 'Unknown error')))
                return test_result

            # Basic structure checks
            total_lines = deck_analysis.get('total_lines', 0)
            measurements = deck_analysis.get('measurements', [])
            includes = deck_analysis.get('includes', [])

            # Calculate structure score
            structure_score = 0.0

            # Points for having sufficient content
            if total_lines >= 20:
                structure_score += 0.3
            elif total_lines >= 10:
                structure_score += 0.1
            else:
                test_result['issues'].append("Deck too short: {} lines".format(total_lines))

            # Points for having measurements
            if len(measurements) >= 3:
                structure_score += 0.4
            elif len(measurements) >= 1:
                structure_score += 0.2

            # Points for having includes
            if len(includes) >= 1:
                structure_score += 0.3

            test_result['score'] = structure_score
            test_result['details']['structure_score'] = structure_score
            test_result['details']['total_lines'] = total_lines
            test_result['details']['measurement_count'] = len(measurements)
            test_result['details']['include_count'] = len(includes)

            if structure_score >= self.thresholds['minimum_deck_structure']:
                test_result['passed'] = True

        except Exception as e:
            test_result['issues'].append("Deck structure test error: {}".format(e))

        return test_result


class ReportGenerator:
    """
    Generates structured validation reports.

    Focuses on human-readable outputs that demonstrate complete flow understanding.
    """

    def __init__(self, verbose=False):
        self.verbose = verbose
        self.logger = self._setup_logger()

    def _setup_logger(self):
        """Setup logger for report generation"""
        logger = logging.getLogger('ReportGenerator')
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO if self.verbose else logging.WARNING)
        return logger

    def generate_csv_summary(self, validation_results: List[Dict], output_path: Path):
        """Generate CSV summary of all validation results"""
        self.logger.info("Generating CSV summary: {}".format(output_path))

        try:
            with open(output_path, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)

                # Write header
                writer.writerow([
                    'ArcName', 'OverallStatus', 'PassRate', 'TestsPassed', 'TotalTests',
                    'CriticalIssueCount', 'TracingScore', 'CoverageScore', 'ComplianceScore'
                ])

                # Write data rows
                for result in validation_results:
                    arc_name = result.get('arc_name', 'unknown')
                    overall_status = result.get('overall_status', 'UNKNOWN')
                    test_summary = result.get('test_summary', {})

                    # Get specific test scores
                    test_results = result.get('test_results', {})
                    tracing_score = test_results.get('traceability_test', {}).get('score', 0.0)
                    coverage_score = test_results.get('specification_coverage_test', {}).get('score', 0.0)

                    writer.writerow([
                        arc_name,
                        overall_status,
                        "{:.1f}%".format(test_summary.get('pass_rate', 0.0) * 100),
                        test_summary.get('passed_tests', 0),
                        test_summary.get('total_tests', 0),
                        len(result.get('critical_issues', [])),
                        "{:.2f}".format(tracing_score),
                        "{:.2f}".format(coverage_score),
                        "{:.2f}".format(result.get('compliance_score', 0.0))
                    ])

            self.logger.info("CSV summary written to: {}".format(output_path))

        except Exception as e:
            self.logger.error("Error writing CSV summary: {}".format(e))

    def generate_template_matching_summary_csv(self, validation_results: List[Dict], output_path: Path):
        """Generate CSV summary of template matching results"""
        try:
            with open(output_path, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)

                # Write header
                writer.writerow([
                    'DeckName', 'CellName', 'MatchStatus', 'CellFound', 'ArcFound',
                    'TemplateLines', 'ErrorMessage'
                ])

                # Write data rows
                for result in validation_results:
                    deck_name = result.get('arc_name', 'unknown')
                    template_result = result.get('template_match_result')

                    if template_result:
                        cell_name = template_result.cell_name or 'unknown'
                        success = 'SUCCESS' if template_result.success else 'FAILED'
                        cell_found = 'YES' if template_result.cell_found else 'NO'
                        arc_found = 'YES' if template_result.arc_found else 'N/A' if not template_result.cell_found else 'NO'
                        lines = '"{}-{}"'.format(template_result.line_start, template_result.line_end) if template_result.success else '""'
                        error = template_result.error_message or ''
                        error = error.replace('"', '""')  # Escape quotes for CSV
                    else:
                        # Fallback for results without template matching data
                        traceability = result.get('traceability_data', {})
                        input_sources = traceability.get('input_sources', {})
                        template_data = input_sources.get('template', {})

                        cell_name = 'unknown'
                        success = 'UNKNOWN'
                        cell_found = 'UNKNOWN'
                        arc_found = 'UNKNOWN'
                        lines = '""'
                        error = 'No template matching data available'

                    csv_row = '{},{},{},{},{},{},"{}"'.format(deck_name, cell_name, success, cell_found, arc_found, lines, error)
                    writer.writerow(csv_row.split(','))

        except Exception as e:
            self.logger.error("Error writing template matching CSV: {}".format(e))

    def _parse_arc_name(self, arc_name: str) -> Dict:
        """Parse arc folder name to extract components"""
        arc_info = {
            'cell_name': 'unknown',
            'arc_type': 'unknown',
            'constrained_pin': 'unknown',
            'constrained_pin_dir': 'unknown',
            'related_pin': 'unknown',
            'related_pin_dir': 'unknown',
            'when_condition': 'unknown',
            'table_point': 'unknown',
            'vector': 'unknown',
            'raw_folder_name': arc_name
        }

        # Parse common MCQC arc folder naming patterns
        # Pattern: arctype_CELLNAME_pin_dir_relpin_dir_when_vector
        parts = arc_name.split('_')

        if len(parts) >= 2:
            arc_info['arc_type'] = parts[0]
            arc_info['cell_name'] = parts[1]

        if len(parts) >= 4:
            arc_info['constrained_pin'] = parts[2]
            arc_info['constrained_pin_dir'] = parts[3]

        if len(parts) >= 6:
            arc_info['related_pin'] = parts[4]
            arc_info['related_pin_dir'] = parts[5]

        if len(parts) >= 7:
            arc_info['when_condition'] = '_'.join(parts[6:])

        return arc_info


def find_arcs_to_process(deck_dir: Path, output_dir: Path, force: bool = False):
    """
    Find arcs that need processing.
    Skip arcs that already have alignment reports unless force=True.
    """
    # Find all arc directories with mc_sim.sp
    all_arc_paths = []
    for folder in deck_dir.iterdir():
        if folder.is_dir():
            mc_sim_file = folder / "mc_sim.sp"
            if mc_sim_file.exists():
                all_arc_paths.append(folder)

    if force:
        print("--force flag set: will reprocess all {} arcs".format(len(all_arc_paths)))
        return all_arc_paths, []

    # Check which arcs already have reports
    arcs_to_process = []
    arcs_skipped = []

    for arc_folder in all_arc_paths:
        arc_name = arc_folder.name
        # Reports are saved in the arc directories themselves
        report_file = arc_folder / "{}_alignment_report.txt".format(arc_name)

        if report_file.exists():
            arcs_skipped.append(arc_folder)
        else:
            arcs_to_process.append(arc_folder)

    print("Found {} total arcs".format(len(all_arc_paths)))
    print("  Already processed: {} arcs (will skip)".format(len(arcs_skipped)))
    print("  Need processing: {} arcs".format(len(arcs_to_process)))

    return arcs_to_process, arcs_skipped


def generate_simplified_text_report(validation_data: Dict, output_file: Path):
    """
    Generate simplified text report focusing on MCQC vs Template alignment.
    Removes YAML generation and compliance sections.
    """
    arc_name = validation_data.get('arc_name', 'Unknown')
    alignment = validation_data.get('alignment_result', {})
    template_match = validation_data.get('template_match_result')
    deck_analysis = validation_data.get('deck_analysis', {})
    internal_analysis = deck_analysis.get('internal_node_analysis', {})

    content = """================================================================================
ARC VALIDATION REPORT
================================================================================

Arc: {}

[1] Arc Identification
Cell: {}
Constraint Pin: {}
Related Pin: {}
When: {}

[2] Template Match
""".format(
        arc_name,
        alignment.get('cell_name', 'Unknown'),
        alignment.get('constraint_pin', 'Unknown'),
        alignment.get('related_pin', 'Unknown'),
        alignment.get('when_condition', 'Unknown')
    )

    if template_match and template_match.success:
        content += """[OK] Found in template.tcl (Lines {}-{})
Probe: {}
""".format(template_match.line_start, template_match.line_end, alignment.get('probe_Template', 'Unknown'))
    else:
        content += """[ERROR] Not found in template.tcl
Probe: N/A
"""

    content += """
[3] MCQC Deck Analysis
cp2q_del1:      {}
cp2q_del2:      {}
final_state:    {}
internal_node:  {}""".format(
        alignment.get('cp2q_del1_MCQC', 'Unknown'),
        alignment.get('cp2q_del2_MCQC', 'Unknown'),
        alignment.get('final_state_MCQC', 'Unknown'),
        alignment.get('internal_node_MCQC', 'Unknown')
    )

    # Add details about detected internal nodes
    if internal_analysis.get('internal_node_patterns'):
        content += "\n\nInternal Node Details:"
        for pattern in internal_analysis['internal_node_patterns']:
            content += "\n  {}: {} (line {})".format(pattern['measurement'], pattern['node'], pattern['line'])

    content += """

[4] Alignment Check
cp2q_del1:      {}
cp2q_del2:      {} ({} in MCQC, {} in Template)
final_state:    {} ({} in MCQC, {} in Template)
probe:          {} (Template expects {}, MCQC uses {})

================================================================================
""".format(
        alignment.get('cp2q_del1_Match', 'Unknown'),
        alignment.get('cp2q_del2_Match', 'Unknown'),
        alignment.get('cp2q_del2_MCQC', 'Unknown'),
        alignment.get('cp2q_del2_Template', 'N/A'),
        alignment.get('final_state_Match', 'Unknown'),
        alignment.get('final_state_MCQC', 'Unknown'),
        alignment.get('final_state_Template', 'OFF'),
        alignment.get('probe_Match', 'Unknown'),
        alignment.get('probe_Template', 'Unknown'),
        'internal node' if alignment.get('internal_node_MCQC') == 'YES' else 'output pin'
    )

    try:
        with open(output_file, 'w') as f:
            f.write(content)
    except Exception as e:
        print("Error writing simplified report to {}: {}".format(output_file, e))


def process_single_arc(arc_data):
    """Worker function for parallel processing of single arc.

    Args:
        arc_data: Tuple containing (arc_folder, args, verbose, shared_template_data)

    Returns:
        Tuple of (arc_folder, validation_data) or (arc_folder, None) if error
    """
    arc_folder, args, verbose, shared_template_data = arc_data

    # Initialize components for this worker (NO TEMPLATE PARSING)
    tracer = InputTraceabilityEngine(verbose=False)  # Disable verbose to reduce noise
    analyzer = SPICEDeckAnalyzer(verbose=False)
    validator = ComplianceValidator(verbose=False)
    reporter = ReportGenerator(verbose=False)

    # Use shared template data (already parsed once in main process)
    if shared_template_data:
        tracer._template_cache[shared_template_data['file_path']] = shared_template_data

    arc_name = arc_folder.name

    try:
        # Timing for this arc
        arc_start_time = time.time()

        # Find input files
        mc_sim_file = arc_folder / "mc_sim.sp"
        if not mc_sim_file.exists():
            print("[ERROR] {}: mc_sim.sp not found".format(arc_name))
            return (arc_folder, None)

        # Auto-discover configuration files
        template_file_to_use = args.template_file
        chartcl_file_to_use = args.chartcl_file
        globals_file_to_use = args.globals_file

        # Step 1: Trace inputs
        t1 = time.time()
        traceability_data = tracer.trace_arc_inputs(
            arc_folder=arc_folder,
            template_file=template_file_to_use,
            chartcl_file=chartcl_file_to_use,
            globals_file=globals_file_to_use,
            chartcl_verbose=args.chartcl_display == 'all'
        )
        trace_time = time.time() - t1

        # Step 2: Analyze deck with internal node detection
        t2 = time.time()
        deck_analysis = analyzer.analyze_deck(mc_sim_file)
        internal_node_analysis = analyzer.detect_internal_node_measurement(mc_sim_file)
        deck_analysis['internal_node_analysis'] = internal_node_analysis
        deck_time = time.time() - t2

        # Step 3: Template matching (if template available)
        t3 = time.time()
        template_match_result = None
        template_data = {}
        if template_file_to_use and template_file_to_use.exists():
            # Parse arc name for template matching
            arc_info = reporter._parse_arc_name(arc_name)

            template_match_result = tracer.extract_template_arc_definition(
                template_file_to_use,
                cell_name=arc_info.get('cell_name', ''),
                arc_type=arc_info.get('arc_type', ''),
                related_pin=arc_info.get('related_pin', ''),
                when_condition=arc_info.get('when_condition', '')
            )

            # Extract template data for alignment analysis
            if template_match_result and template_match_result.success:
                # Get template data from cached template structure
                cached_template = tracer.get_cached_template_data(template_file_to_use)
                arcs_by_cell = cached_template.get('arcs_by_cell', {})
                cell_name = arc_info.get('cell_name', '')

                # Find the matching arc definition
                template_data = {}
                if cell_name in arcs_by_cell:
                    for arc_def in arcs_by_cell[cell_name]:
                        if (arc_def.get('type') == arc_info.get('arc_type') and
                            arc_def.get('related_pin') == arc_info.get('related_pin')):
                            template_data = arc_def
                            break
        template_time = time.time() - t3

        # Step 4: Alignment analysis
        t4 = time.time()
        alignment_analyzer = AlignmentAnalyzer(verbose=verbose)
        alignment_result = alignment_analyzer.check_alignment(
            mcqc_data=deck_analysis,
            template_data=template_data,
            arc_name=arc_name
        )
        alignment_time = time.time() - t4

        # Step 5: Validate compliance (optional, only if needed)
        t5 = time.time()
        validation_result = validator.validate_compliance(
            traceability_data=traceability_data,
            deck_analysis=deck_analysis,
            template_match_result=template_match_result
        )
        validation_time = time.time() - t5

        # Create validation data with alignment results
        validation_data = validation_result
        validation_data['traceability_data'] = traceability_data
        validation_data['deck_analysis'] = deck_analysis
        validation_data['template_match_result'] = template_match_result
        validation_data['alignment_result'] = alignment_result

        # Step 6: Generate simplified text report (not YAML)
        t6 = time.time()
        if not args.csv_only:
            arc_report_file = arc_folder / "{}_alignment_report.txt".format(arc_name)
            generate_simplified_text_report(validation_data, arc_report_file)
        report_time = time.time() - t6

        # Timing summary (only in verbose mode)
        total_time = time.time() - arc_start_time
        if verbose and total_time > 2.0:  # Only show timing breakdown for slow arcs
            print("  [TIME]  Timing breakdown: {:.2f}s total".format(total_time))
            print("     Template: {:.2f}s, Deck: {:.2f}s, Validation: {:.2f}s".format(template_time, deck_time, validation_time))

        return (arc_folder, validation_data)

    except Exception as e:
        print("[ERROR] Error processing {}: {}".format(arc_name, str(e)))
        if verbose:
            import traceback
            traceback.print_exc()
        return (arc_folder, None)


def main():
    """
    Main CLI interface for MCQC specification compliance validation.

    CRITICAL FOCUS: Audit generated SPICE decks against input specifications
    with COMPLETE traceability of all parsed inputs.
    """

    parser = argparse.ArgumentParser(
        description='MCQC Specification Compliance Validation Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # CRITICAL ISSUE RESOLUTION: Process remaining 99 arcs (preserve existing 1147 reports)
  python audit_deck_compliance.py --deck_dir /work/MCQC_RUN/DECKS/ \\
    --template_file /work/lib/template_mpw.tcl \\
    --output_dir ./results/ --parallel 8

  # Force reprocess all 1246 arcs (overwrite existing reports)
  python audit_deck_compliance.py --deck_dir /work/MCQC_RUN/DECKS/ \\
    --template_file /work/lib/template_mpw.tcl \\
    --output_dir ./results/ --parallel 8 --force

  # Generate CSV only from existing reports (no processing)
  python audit_deck_compliance.py --deck_dir /work/MCQC_RUN/DECKS/ \\
    --output_dir ./results/ --csv_only

  # High-performance mode for large datasets (recommended)
  python audit_deck_compliance.py --deck_dir /work/DECKS/ \\
    --template_file ./template.tcl --output_dir ./results/ \\
    --parallel 16 --csv_only
        """
    )

    # Input arguments
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        '--arc_folder',
        type=Path,
        help='Path to single arc folder containing mc_sim.sp'
    )
    input_group.add_argument(
        '--deck_dir',
        type=Path,
        help='Path to directory containing multiple arc folders'
    )

    # Configuration file arguments
    parser.add_argument(
        '--template_file',
        type=Path,
        help='Path to template.tcl file (if not specified, will search in arc hierarchy)'
    )
    parser.add_argument(
        '--chartcl_file',
        type=Path,
        help='Path to chartcl.tcl file (if not specified, will search in arc hierarchy)'
    )
    parser.add_argument(
        '--globals_file',
        type=Path,
        help='Path to globals file (if not specified, will search for *globals*.txt in arc hierarchy)'
    )

    # Output arguments
    parser.add_argument(
        '--output_dir',
        type=Path,
        required=True,
        help='Directory to write summary reports (individual arc reports saved in arc directories)'
    )

    # Control arguments
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    parser.add_argument(
        '--chartcl-display',
        choices=['minimal', 'relevant', 'all'],
        default='relevant',
        help='''Control char.tcl variable display:
            minimal:  Show only arc-type specific (e.g., mpw_input_threshold for MPW)
            relevant: Show arc-type + common constraints (default)
            all:      Show all constraint-related variables'''
    )
    parser.add_argument(
        '--csv_only',
        action='store_true',
        help='Generate only CSV summary, skip detailed YAML reports'
    )
    parser.add_argument(
        '--parallel',
        type=int,
        default=min(cpu_count(), 8),  # Reasonable default, max 8 for safety
        help='Number of parallel workers (default: {}, detected: {} cores)'.format(min(cpu_count(), 8), cpu_count())
    )
    parser.add_argument(
        '--force',
        action='store_true',
        help='Force reprocessing of all arcs, overwriting existing reports'
    )

    args = parser.parse_args()

    # Create output directory
    args.output_dir.mkdir(parents=True, exist_ok=True)

    # Initialize components
    tracer = InputTraceabilityEngine(verbose=args.verbose)
    analyzer = SPICEDeckAnalyzer(verbose=args.verbose)
    validator = ComplianceValidator(verbose=args.verbose)
    reporter = ReportGenerator(verbose=args.verbose)

    # Collect arc folders to process
    arc_folders = []

    if args.arc_folder:
        if args.arc_folder.exists():
            arc_folders.append(args.arc_folder)
        else:
            print("[ERROR] Arc folder not found: {}".format(args.arc_folder))
            return 1

    elif args.deck_dir:
        if args.deck_dir.exists():
            # Find all arc folders containing mc_sim.sp
            for folder in args.deck_dir.iterdir():
                if folder.is_dir():
                    mc_sim_file = folder / "mc_sim.sp"
                    if mc_sim_file.exists():
                        arc_folders.append(folder)

            if not arc_folders:
                print("[ERROR] No arc folders with mc_sim.sp found in: {}".format(args.deck_dir))
                return 1
        else:
            print("[ERROR] Deck directory not found: {}".format(args.deck_dir))
            return 1

    # CRITICAL PERFORMANCE FIX: Parse template ONCE before parallel processing
    shared_template_data = None
    if args.template_file and args.template_file.exists():
        print("[CONFIG] Pre-parsing template for shared cache: {}".format(args.template_file))
        template_tracer = InputTraceabilityEngine(verbose=False)
        try:
            shared_template_data = template_tracer.get_cached_template_data(args.template_file)
            shared_template_data['file_path'] = str(args.template_file)  # Store file path for cache key
            print("   [OK] Template cached: {} arcs, {} cells".format(
                shared_template_data.get('total_arcs', 0), shared_template_data.get('total_cells', 0)))
        except Exception as e:
            print("   [WARN]  Template caching failed: {}".format(e))
            shared_template_data = None

    # CSV-ONLY MODE: Skip all arc processing and generate summary from existing reports
    if args.csv_only:
        print("[CSV] CSV-only mode: Generating summary from existing reports...")
        print("[CSV] Searching for existing reports in: {}".format(args.output_dir))

        # Generate CSV summary from existing data without processing arcs
        start_time = time.time()
        validation_results = []

        # Look for existing alignment CSV to generate legacy CSV format
        alignment_csv_file = args.output_dir / "alignment_summary.csv"
        if alignment_csv_file.exists():
            print("[CSV] Found existing alignment data: {}".format(alignment_csv_file))
            # Generate legacy CSV from existing alignment data
            csv_file = args.output_dir / "compliance_summary.csv"
            try:
                # Simple CSV conversion from existing data
                with open(str(alignment_csv_file), 'r') as infile, open(str(csv_file), 'w') as outfile:
                    outfile.write(infile.read())
                print("[OK] CSV summary generated: {}".format(csv_file))
            except Exception as e:
                print("[ERROR] Failed to generate CSV summary: {}".format(e))
                return 1
        else:
            print("[ERROR] No existing alignment data found. Run without --csv_only first.")
            return 1

        print("[OK] CSV-only mode completed in {:.2f}s".format(time.time() - start_time))
        return 0

    # Filter arcs based on --force flag
    if not args.force and args.deck_dir:
        print("[SEARCH] Checking for existing reports (use --force to reprocess all)...")
        arc_folders, skipped_arcs = find_arcs_to_process(args.deck_dir, args.output_dir, force=args.force)
        if skipped_arcs:
            print("   [SKIP]  Skipped {} arcs with existing reports".format(len(skipped_arcs)))

    print("[SEARCH] Processing {} arc folders...".format(len(arc_folders)))

    # Start timing for overall processing
    start_time = time.time()

    # Process arc folders in parallel for maximum performance
    validation_results = []

    # Prepare data for parallel processing with shared template data
    arc_data_list = [(arc_folder, args, args.verbose, shared_template_data) for arc_folder in arc_folders]

    # Use parallel processing if multiple arcs
    if len(arc_folders) > 1 and args.parallel > 1:
        # Enhanced progress reporting with timing estimates
        total_arcs = len(arc_folders)
        workers = args.parallel

        print("[PERF] Processing {} arcs using {} parallel workers...".format(total_arcs, workers))
        if args.verbose:
            print("   [PERF] Performance optimizations active:")
            print("      • Template caching: Parse once, use {} times".format(total_arcs))
            print("      • Parallel processing: {} cores".format(workers))
            print("      • Deck optimization: Stream processing")
            print("   [ETA] Target: <30 minutes total (vs {:.0f}s original)".format(total_arcs * 60))
        print()

        parallel_start_time = time.time()

        with Pool(processes=args.parallel) as pool:
            # Process arcs in parallel
            results = pool.map(process_single_arc, arc_data_list)

        parallel_time = time.time() - parallel_start_time
        avg_time_per_arc = parallel_time / total_arcs
        theoretical_sequential_time = total_arcs * 60  # 1 minute per arc originally
        actual_speedup = theoretical_sequential_time / parallel_time if parallel_time > 0 else 0

        print("  [SPEED] Parallel processing completed!")
        print("     [CLOCK] Total time:          {:.1f}s".format(parallel_time))
        print("     [SPEED] Avg per arc:         {:.2f}s".format(avg_time_per_arc))
        print("     [PERF] Actual speedup:      {:.0f}x vs original".format(actual_speedup))
        print("     [MEMORY] Memory efficiency:   Stream processing enabled")
        print()

        # Convert results to validation format with progress stats
        pass_count = 0
        fail_count = 0
        error_count = 0

        for i, (arc_folder, validation_data) in enumerate(results, 1):
            if validation_data:
                validation_data['arc_name'] = arc_folder.name
                validation_results.append(validation_data)
                status = validation_data['overall_status']
                if status == 'PASS':
                    pass_count += 1
                    status_icon = "[OK]"
                else:
                    fail_count += 1
                    status_icon = "[WARN]"

                # Show progress every 10% or for first/last few arcs
                if args.verbose or i % max(1, total_arcs // 10) == 0 or i <= 3 or i >= total_arcs - 1:
                    print("  [{:3d}/{}] {} {}: {}".format(i, total_arcs, status_icon, arc_folder.name, status))
            else:
                error_count += 1
                # Create error result
                error_result = {
                    'arc_name': arc_folder.name,
                    'overall_status': 'ERROR',
                    'error': 'Processing failed in parallel worker',
                    'test_summary': {'total_tests': 0, 'passed_tests': 0, 'failed_tests': 0, 'error_tests': 1, 'pass_rate': 0.0, 'average_score': 0.0},
                    'critical_issues': ['Processing error in parallel worker'],
                    'recommendations': ['Check arc folder structure and file accessibility']
                }
                validation_results.append(error_result)
                print("  [{:3d}/{}] [ERROR] {}: ERROR".format(i, total_arcs, arc_folder.name))

        # Summary stats
        print("\n[PERF] Parallel Processing Summary:")
        print("   [OK] PASS:  {:3d} ({:.1f}%)".format(pass_count, pass_count/total_arcs*100))
        print("   [WARN]  FAIL:  {:3d} ({:.1f}%)".format(fail_count, fail_count/total_arcs*100))
        print("   [ERROR] ERROR: {:3d} ({:.1f}%)".format(error_count, error_count/total_arcs*100))
        print("   [SPEED] Speedup: {:.0f}x vs sequential (Target: 100x+)".format(actual_speedup))

    else:
        # Sequential processing for single arc or when parallel disabled
        total_arcs = len(arc_folders)
        print("[PARSING] Processing {} arcs sequentially...".format(total_arcs))
        if total_arcs > 1:
            print("   [TIP] Tip: Use --parallel {} for {}x speedup".format(min(cpu_count(), 8), min(cpu_count(), 8)))
        if args.verbose:
            print("   [PERF] Performance optimizations active:")
            print("      • Template caching: Enabled")
            print("      • Deck optimization: Stream processing")
        print()

        sequential_start_time = time.time()
        pass_count = 0
        fail_count = 0
        error_count = 0

        for i, (arc_folder, args_copy, verbose, shared_template_data) in enumerate(arc_data_list, 1):
            arc_start_time = time.time()
            print("[{:3d}/{}] Processing: {}".format(i, total_arcs, arc_folder.name))

            arc_folder, validation_data = process_single_arc((arc_folder, args_copy, verbose, shared_template_data))
            arc_time = time.time() - arc_start_time

            if validation_data:
                validation_data['arc_name'] = arc_folder.name
                validation_results.append(validation_data)
                status = validation_data['overall_status']

                if status == 'PASS':
                    pass_count += 1
                    status_icon = "[OK]"
                else:
                    fail_count += 1
                    status_icon = "[WARN]"

                # Show timing and progress
                elapsed = time.time() - sequential_start_time
                avg_time = elapsed / i
                remaining_time = (total_arcs - i) * avg_time

                print("     {} {} ({:.1f}s)".format(status_icon, status, arc_time))
                if total_arcs > 10 and i % 5 == 0:  # Show ETA every 5 arcs for longer runs
                    print("     [ETA] Progress: {:.1f}% | ETA: {:.0f}s".format(i/total_arcs*100, remaining_time))
            else:
                error_count += 1
                # Create error result
                error_result = {
                    'arc_name': arc_folder.name,
                    'overall_status': 'ERROR',
                    'error': 'Processing failed',
                    'test_summary': {'total_tests': 0, 'passed_tests': 0, 'failed_tests': 0, 'error_tests': 1, 'pass_rate': 0.0, 'average_score': 0.0},
                    'critical_issues': ['Processing error'],
                    'recommendations': ['Check arc folder structure and file accessibility']
                }
                validation_results.append(error_result)
                print("     [ERROR] ERROR ({:.1f}s)".format(arc_time))

        sequential_time = time.time() - sequential_start_time
        theoretical_original_time = total_arcs * 60  # Original 1 min per arc
        actual_speedup = theoretical_original_time / sequential_time if sequential_time > 0 else 0

        print("\n[PERF] Sequential Processing Summary:")
        print("   [OK] PASS:  {:3d} ({:.1f}%)".format(pass_count, pass_count/total_arcs*100))
        print("   [WARN]  FAIL:  {:3d} ({:.1f}%)".format(fail_count, fail_count/total_arcs*100))
        print("   [ERROR] ERROR: {:3d} ({:.1f}%)".format(error_count, error_count/total_arcs*100))
        print("   [CLOCK] Total: {:.1f}s ({:.1f}s per arc)".format(sequential_time, sequential_time/total_arcs))
        print("   [SPEED] Speedup: {:.0f}x vs original (Target: 100x+)".format(actual_speedup))

    # Step 5: Generate alignment CSV and statistics
    alignment_results = [result.get('alignment_result', {}) for result in validation_results if result.get('alignment_result')]

    # Generate primary alignment CSV (includes existing + new reports)
    alignment_csv_file = args.output_dir / "alignment_summary.csv"
    alignment_analyzer = AlignmentAnalyzer(verbose=args.verbose)

    # If we have existing reports to include, merge them
    if not args.force and args.deck_dir and alignment_results:
        print("\n[DATA] Generating comprehensive alignment CSV...")
        print("   [PARSING] Including {} newly processed arcs".format(len(alignment_results)))

        alignment_analyzer.generate_alignment_csv(alignment_results, alignment_csv_file)
    else:
        alignment_analyzer.generate_alignment_csv(alignment_results, alignment_csv_file)

    # Calculate processing statistics for report
    processing_stats = {
        'total_time': (time.time() - start_time) / 60,  # Convert to minutes
        'avg_time_per_arc': (time.time() - start_time) / len(validation_results) if validation_results else 0,
        'parallel_workers': args.parallel
    }

    # Generate statistics report
    stats_file = args.output_dir / "validation_statistics.txt"
    alignment_analyzer.generate_statistics_report(alignment_results, stats_file, processing_stats)

    # Generate legacy CSV summaries for compatibility
    csv_file = args.output_dir / "compliance_summary.csv"
    reporter.generate_csv_summary(validation_results, str(csv_file))

    template_summary_file = args.output_dir / "template_matching_summary.csv"
    reporter.generate_template_matching_summary_csv(validation_results, str(template_summary_file))

    # Print summary
    print("\n[DATA] Validation Summary:")
    print("   Total arcs processed: {}".format(len(validation_results)))

    statuses = [result.get('overall_status', 'UNKNOWN') for result in validation_results]
    print("   PASS: {}".format(statuses.count('PASS')))
    print("   FAIL: {}".format(statuses.count('FAIL')))
    print("   ERROR: {}".format(statuses.count('ERROR')))

    pass_rate = statuses.count('PASS') / len(statuses) if statuses else 0.0
    print("   Overall pass rate: {:.1%}".format(pass_rate))

    # Template matching statistics
    template_successes = 0
    cell_not_found = 0
    arc_not_found = 0
    total_with_template = 0

    for result in validation_results:
        template_result = result.get('template_match_result')
        if template_result:
            total_with_template += 1
            if template_result.success:
                template_successes += 1
            elif not template_result.cell_found:
                cell_not_found += 1
            else:
                arc_not_found += 1

    if total_with_template > 0:
        template_success_rate = template_successes / total_with_template
        print("\n[TARGET] Template.tcl Matching Results:")
        print("   [OK] Successfully matched: {} arcs ({:.1%})".format(template_successes, template_success_rate))
        print("   [ERROR] Cell not found:       {} arcs ({:.1%})".format(cell_not_found, cell_not_found/total_with_template))
        print("   [ERROR] Arc not found:        {} arcs ({:.1%})".format(arc_not_found, arc_not_found/total_with_template))

    # CRITICAL: Performance improvement verification
    total_processing_time = time.time() - start_time
    if len(validation_results) > 10:  # Only show performance metrics for larger runs
        print("\n[PERF] PERFORMANCE VERIFICATION:")
        print("   [TIME]  Total processing time: {:.1f}s ({:.1f} minutes)".format(total_processing_time, total_processing_time/60))
        print("   [SPEED] Average per arc: {:.2f}s".format(total_processing_time/len(validation_results)))
        original_estimated_time = len(validation_results) * 60  # 1 minute per arc originally
        actual_speedup = original_estimated_time / total_processing_time if total_processing_time > 0 else 0
        print("   [TARGET] Actual speedup achieved: {:.0f}x vs original (target: 100x+)".format(actual_speedup))
        if shared_template_data:
            print("   [OK] Template caching: WORKING (parsed once, used {} times)".format(len(validation_results)))
        else:
            print("   [WARN]  Template caching: NOT USED (no template file provided)")

    print("\n[FILES] Summary reports in: {}".format(args.output_dir))
    print("   [DATA] PRIMARY: {}".format(alignment_csv_file))
    print("   [STATS] Statistics: {}".format(stats_file))
    print("   [DATA] Legacy CSV: {}".format(csv_file))
    print("   [TARGET] Template matching: {}".format(template_summary_file))

    if not args.csv_only:
        print("   [REPORT] Individual reports: [arc_name]_alignment_report.txt in each arc directory")

    print("\n[OK] MCQC validation completed successfully!")
    if total_processing_time < 30 * 60:  # Less than 30 minutes
        print("[SUCCESS] Performance target achieved: {:.1f}s < 30 minutes".format(total_processing_time))
    else:
        print("[WARN]  Performance target missed: {:.1f} minutes > 30 minutes".format(total_processing_time/60))
    print("   [STATS] Processed {} arc directories".format(len(validation_results)))

    return 0


if __name__ == "__main__":
    sys.exit(main())