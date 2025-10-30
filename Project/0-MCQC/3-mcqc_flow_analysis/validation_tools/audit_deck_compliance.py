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
from pathlib import Path
from collections import defaultdict, Counter
from typing import Dict, List, Tuple, Optional, Any, Set
import logging

# Optional YAML support
try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False
    print("⚠️  PyYAML not available - YAML reports will be disabled")

# Add the MCQC parsers to Python path
MCQC_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(MCQC_ROOT / "2-flow"))

try:
    from charTemplateParser import ChartemplateParser
    from chartcl_parser import ChartclParser
    from globalsFileReader import GlobalsFileReader
    PARSERS_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  MCQC parsers not available: {e}")
    print("⚠️  Continuing with basic file parsing...")
    PARSERS_AVAILABLE = False


class InputTraceabilityEngine:
    """
    Traces EVERY input that contributed to deck generation.

    Demonstrates complete understanding by mapping:
    - template.tcl specifications → SPICE deck content
    - chartcl.tcl configurations → measurement setups
    - globals files → parameter values
    - Python logic → final-state patterns
    """

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.logger = self._setup_logging()

        # Input source tracking
        self.template_inputs = {}
        self.chartcl_inputs = {}
        self.globals_inputs = {}
        self.python_logic_signatures = {}

        # Traceability mappings
        self.input_to_output_map = defaultdict(list)
        self.missing_specifications = defaultdict(list)

    def _setup_logging(self) -> logging.Logger:
        """Setup logging for traceability analysis."""
        logger = logging.getLogger('InputTraceability')
        logger.setLevel(logging.DEBUG if self.verbose else logging.INFO)

        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        return logger

    def trace_arc_inputs(self, arc_folder: Path) -> Dict[str, Any]:
        """
        Trace ALL inputs that contributed to this arc's deck generation.

        Returns complete input traceability mapping showing:
        - Which template.tcl lines influenced each SPICE measurement
        - Which chartcl.tcl settings affected measurement setup
        - Which globals values were used
        - Which Python logic patterns were applied
        """

        arc_name = arc_folder.name
        self.logger.info(f"Tracing inputs for arc: {arc_name}")

        traceability = {
            'arc_name': arc_name,
            'arc_folder': str(arc_folder),
            'input_sources': {},
            'output_mappings': {},
            'missing_specs': [],
            'python_signatures': []
        }

        # Find and parse all input files
        template_file = self._find_template_file(arc_folder)
        chartcl_file = self._find_chartcl_file(arc_folder)
        globals_files = self._find_globals_files(arc_folder)

        # Parse each input source
        if template_file:
            traceability['input_sources']['template'] = self._parse_template_inputs(template_file)

        if chartcl_file:
            traceability['input_sources']['chartcl'] = self._parse_chartcl_inputs(chartcl_file)

        for globals_file in globals_files:
            globals_key = f"globals_{globals_file.name}"
            traceability['input_sources'][globals_key] = self._parse_globals_inputs(globals_file)

        # Analyze mc_sim.sp to identify output patterns
        mc_sim_file = arc_folder / "mc_sim.sp"
        if mc_sim_file.exists():
            traceability['output_mappings'] = self._analyze_mc_sim_outputs(mc_sim_file)

        # Map inputs to outputs
        traceability['input_to_output_correlation'] = self._correlate_inputs_to_outputs(
            traceability['input_sources'],
            traceability['output_mappings']
        )

        # Identify missing specifications
        traceability['missing_specs'] = self._identify_missing_specifications(
            traceability['output_mappings'],
            traceability['input_sources']
        )

        return traceability

    def _find_template_file(self, arc_folder: Path) -> Optional[Path]:
        """Find template.tcl file for this arc."""
        candidates = [
            arc_folder / "template.tcl",
            arc_folder.parent / "template.tcl",
            arc_folder.parent.parent / "template.tcl"
        ]

        for candidate in candidates:
            if candidate.exists():
                self.logger.debug(f"Found template file: {candidate}")
                return candidate

        self.logger.warning(f"No template.tcl found for {arc_folder}")
        return None

    def _find_chartcl_file(self, arc_folder: Path) -> Optional[Path]:
        """Find chartcl.tcl file for this arc."""
        candidates = [
            arc_folder / "chartcl.tcl",
            arc_folder.parent / "chartcl.tcl",
            arc_folder.parent.parent / "chartcl.tcl"
        ]

        for candidate in candidates:
            if candidate.exists():
                self.logger.debug(f"Found chartcl file: {candidate}")
                return candidate

        self.logger.warning(f"No chartcl.tcl found for {arc_folder}")
        return None

    def _find_globals_files(self, arc_folder: Path) -> List[Path]:
        """Find all globals files that might affect this arc."""
        globals_files = []

        # Search in arc folder and parent directories
        search_dirs = [arc_folder, arc_folder.parent, arc_folder.parent.parent]

        for search_dir in search_dirs:
            if search_dir.exists():
                for globals_file in search_dir.glob("*globals*.txt"):
                    globals_files.append(globals_file)
                    self.logger.debug(f"Found globals file: {globals_file}")

        return globals_files

    def _parse_template_inputs(self, template_file: Path) -> Dict[str, Any]:
        """Parse template.tcl to extract all specifications."""

        if PARSERS_AVAILABLE:
            try:
                parser = ChartemplateParser(str(template_file))
                parsed_data = parser.parse()

                return {
                    'file_path': str(template_file),
                    'parser_used': 'ChartemplateParser',
                    'parsed_content': parsed_data,
                    'raw_lines': self._extract_key_template_lines(template_file)
                }
            except Exception as e:
                self.logger.warning(f"ChartemplateParser failed: {e}, falling back to basic parsing")

        # Fallback to basic parsing
        return {
            'file_path': str(template_file),
            'parser_used': 'basic_file_parsing',
            'raw_lines': self._extract_key_template_lines(template_file),
            'measurements_found': self._extract_template_measurements(template_file),
            'arc_specifications': self._extract_arc_specs(template_file)
        }

    def _parse_chartcl_inputs(self, chartcl_file: Path) -> Dict[str, Any]:
        """Parse chartcl.tcl to extract configuration settings."""

        if PARSERS_AVAILABLE:
            try:
                parser = ChartclParser(str(chartcl_file))
                parsed_data = parser.parse()

                return {
                    'file_path': str(chartcl_file),
                    'parser_used': 'ChartclParser',
                    'parsed_content': parsed_data,
                    'raw_lines': self._extract_key_chartcl_lines(chartcl_file)
                }
            except Exception as e:
                self.logger.warning(f"ChartclParser failed: {e}, falling back to basic parsing")

        # Fallback to basic parsing
        return {
            'file_path': str(chartcl_file),
            'parser_used': 'basic_file_parsing',
            'raw_lines': self._extract_key_chartcl_lines(chartcl_file),
            'measurements_config': self._extract_chartcl_measurements(chartcl_file),
            'timing_config': self._extract_chartcl_timing(chartcl_file)
        }

    def _parse_globals_inputs(self, globals_file: Path) -> Dict[str, Any]:
        """Parse globals file to extract parameter values."""

        if PARSERS_AVAILABLE:
            try:
                parser = GlobalsFileReader(str(globals_file))
                parsed_data = parser.read()

                return {
                    'file_path': str(globals_file),
                    'parser_used': 'GlobalsFileReader',
                    'parsed_content': parsed_data,
                    'raw_lines': self._extract_globals_lines(globals_file)
                }
            except Exception as e:
                self.logger.warning(f"GlobalsFileReader failed: {e}, falling back to basic parsing")

        # Fallback to basic parsing
        return {
            'file_path': str(globals_file),
            'parser_used': 'basic_file_parsing',
            'raw_lines': self._extract_globals_lines(globals_file),
            'parameters': self._extract_globals_parameters(globals_file)
        }

    def _extract_key_template_lines(self, template_file: Path) -> List[str]:
        """Extract key lines from template.tcl that affect deck generation."""
        key_lines = []

        try:
            with open(template_file, 'r') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()

                    # Look for measurement-related lines
                    if any(keyword in line.lower() for keyword in [
                        'meas', 'measure', 'final_state', 'cp2q', 'delay',
                        'when', 'cross', 'rise', 'fall', 'tran'
                    ]):
                        key_lines.append(f"Line {line_num}: {line}")

        except Exception as e:
            self.logger.error(f"Error reading template file {template_file}: {e}")

        return key_lines

    def _extract_template_measurements(self, template_file: Path) -> List[Dict[str, str]]:
        """Extract measurement specifications from template.tcl."""
        measurements = []

        try:
            with open(template_file, 'r') as f:
                content = f.read()

                # Look for .meas statements
                meas_pattern = r'\.meas\s+\w+\s+(\w+)\s+.*'
                for match in re.finditer(meas_pattern, content, re.IGNORECASE):
                    measurements.append({
                        'type': 'meas_statement',
                        'measurement_name': match.group(1),
                        'full_line': match.group(0).strip()
                    })

        except Exception as e:
            self.logger.error(f"Error extracting measurements from {template_file}: {e}")

        return measurements

    def _extract_arc_specs(self, template_file: Path) -> Dict[str, List[str]]:
        """Extract arc-specific specifications from template.tcl."""
        arc_specs = defaultdict(list)

        try:
            with open(template_file, 'r') as f:
                for line in f:
                    line = line.strip()

                    # Look for arc-specific patterns
                    if 'arc' in line.lower() or 'when' in line.lower():
                        if 'rise' in line.lower():
                            arc_specs['rise_arcs'].append(line)
                        elif 'fall' in line.lower():
                            arc_specs['fall_arcs'].append(line)
                        else:
                            arc_specs['general_arcs'].append(line)

        except Exception as e:
            self.logger.error(f"Error extracting arc specs from {template_file}: {e}")

        return dict(arc_specs)

    def _extract_key_chartcl_lines(self, chartcl_file: Path) -> List[str]:
        """Extract key configuration lines from chartcl.tcl."""
        key_lines = []

        try:
            with open(chartcl_file, 'r') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()

                    # Look for configuration-related lines
                    if any(keyword in line.lower() for keyword in [
                        'set_', 'char_', 'meas_', 'timing_', 'delay_',
                        'slew_', 'load_', 'voltage_', 'temperature_'
                    ]):
                        key_lines.append(f"Line {line_num}: {line}")

        except Exception as e:
            self.logger.error(f"Error reading chartcl file {chartcl_file}: {e}")

        return key_lines

    def _extract_chartcl_measurements(self, chartcl_file: Path) -> List[Dict[str, str]]:
        """Extract measurement configuration from chartcl.tcl."""
        measurements = []

        try:
            with open(chartcl_file, 'r') as f:
                content = f.read()

                # Look for measurement setup
                meas_pattern = r'set_measurement\s+(\w+)\s+.*'
                for match in re.finditer(meas_pattern, content, re.IGNORECASE):
                    measurements.append({
                        'type': 'measurement_setup',
                        'measurement_name': match.group(1),
                        'full_line': match.group(0).strip()
                    })

        except Exception as e:
            self.logger.error(f"Error extracting measurements from {chartcl_file}: {e}")

        return measurements

    def _extract_chartcl_timing(self, chartcl_file: Path) -> Dict[str, List[str]]:
        """Extract timing configuration from chartcl.tcl."""
        timing_config = defaultdict(list)

        try:
            with open(chartcl_file, 'r') as f:
                for line in f:
                    line = line.strip()

                    # Look for timing-related settings
                    if 'slew' in line.lower():
                        timing_config['slew_settings'].append(line)
                    elif 'load' in line.lower():
                        timing_config['load_settings'].append(line)
                    elif 'delay' in line.lower():
                        timing_config['delay_settings'].append(line)

        except Exception as e:
            self.logger.error(f"Error extracting timing config from {chartcl_file}: {e}")

        return dict(timing_config)

    def _extract_globals_lines(self, globals_file: Path) -> List[str]:
        """Extract all parameter lines from globals file."""
        lines = []

        try:
            with open(globals_file, 'r') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if line and not line.startswith('#'):
                        lines.append(f"Line {line_num}: {line}")

        except Exception as e:
            self.logger.error(f"Error reading globals file {globals_file}: {e}")

        return lines

    def _extract_globals_parameters(self, globals_file: Path) -> Dict[str, str]:
        """Extract parameter=value pairs from globals file."""
        parameters = {}

        try:
            with open(globals_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if '=' in line and not line.startswith('#'):
                        key, value = line.split('=', 1)
                        parameters[key.strip()] = value.strip()

        except Exception as e:
            self.logger.error(f"Error extracting parameters from {globals_file}: {e}")

        return parameters

    def _analyze_mc_sim_outputs(self, mc_sim_file: Path) -> Dict[str, Any]:
        """
        Analyze mc_sim.sp to identify all output patterns.

        Why mc_sim.sp?
        --------------
        The mc_sim.sp file contains the ACTUAL Monte Carlo simulation setup that includes:
        - All measurements (cp2q_del1, final-state checks, etc.)
        - All post-processing modifications
        - Complete measurement setup that actually runs in simulation

        nominal_sim.sp is the base template before Monte Carlo additions and post-processing.
        """

        output_analysis = {
            'file_path': str(mc_sim_file),
            'measurements_found': [],
            'final_state_checks': [],
            'cp2q_patterns': [],
            'internal_nodes': [],
            'post_processing_signatures': [],
            'total_lines': 0,
            'measurement_count': 0
        }

        try:
            with open(mc_sim_file, 'r') as f:
                lines = f.readlines()
                output_analysis['total_lines'] = len(lines)

                for line_num, line in enumerate(lines, 1):
                    line = line.strip()

                    # Identify measurements
                    if line.lower().startswith('.meas'):
                        output_analysis['measurements_found'].append({
                            'line_number': line_num,
                            'measurement': line
                        })
                        output_analysis['measurement_count'] += 1

                        # Categorize measurements
                        if 'final_state' in line.lower():
                            output_analysis['final_state_checks'].append(line)
                        elif 'cp2q' in line.lower():
                            output_analysis['cp2q_patterns'].append(line)

                    # Identify internal node references
                    elif any(pattern in line.lower() for pattern in ['x.', 'net', 'internal']):
                        if not line.startswith('*'):  # Skip comments
                            output_analysis['internal_nodes'].append({
                                'line_number': line_num,
                                'content': line
                            })

                    # Identify post-processing signatures
                    elif any(pattern in line for pattern in ['POST_PROC', 'PYTHON_GEN', 'AUTO_GEN']):
                        output_analysis['post_processing_signatures'].append({
                            'line_number': line_num,
                            'signature': line
                        })

        except Exception as e:
            self.logger.error(f"Error analyzing mc_sim file {mc_sim_file}: {e}")

        return output_analysis

    def _correlate_inputs_to_outputs(self, input_sources: Dict, output_mappings: Dict) -> Dict[str, Any]:
        """Correlate input specifications to actual output patterns."""

        correlations = {
            'direct_mappings': [],
            'missing_specifications': [],
            'unexpected_outputs': [],
            'confidence_scores': {}
        }

        # Check if template measurements match output measurements
        template_meas = []
        if 'template' in input_sources:
            template_meas = input_sources['template'].get('measurements_found', [])

        output_meas = output_mappings.get('measurements_found', [])

        # Map template to output measurements
        template_names = {m.get('measurement_name', '') for m in template_meas}
        output_names = {self._extract_measurement_name(m.get('measurement', '')) for m in output_meas}

        # Direct mappings
        for name in template_names.intersection(output_names):
            if name:
                correlations['direct_mappings'].append({
                    'measurement_name': name,
                    'found_in_template': True,
                    'found_in_output': True,
                    'confidence': 'high'
                })

        # Missing specifications (in output but not template)
        for name in output_names - template_names:
            if name:
                correlations['missing_specifications'].append({
                    'measurement_name': name,
                    'found_in_template': False,
                    'found_in_output': True,
                    'issue': 'output_without_specification'
                })

        # Unexpected outputs (in template but not output)
        for name in template_names - output_names:
            if name:
                correlations['unexpected_outputs'].append({
                    'measurement_name': name,
                    'found_in_template': True,
                    'found_in_output': False,
                    'issue': 'specification_without_output'
                })

        # Calculate confidence scores
        total_template = len(template_names)
        total_output = len(output_names)
        total_mapped = len(correlations['direct_mappings'])

        if total_template > 0:
            correlations['confidence_scores']['template_coverage'] = total_mapped / total_template
        if total_output > 0:
            correlations['confidence_scores']['output_coverage'] = total_mapped / total_output

        return correlations

    def _identify_missing_specifications(self, output_mappings: Dict, input_sources: Dict) -> List[Dict[str, Any]]:
        """Identify patterns in output that have no corresponding input specification."""

        missing_specs = []

        # Check for final-state patterns without specification
        final_state_outputs = output_mappings.get('final_state_checks', [])
        if final_state_outputs:
            # Check if any input source specifies final-state behavior
            has_final_state_spec = False

            for source_name, source_data in input_sources.items():
                if isinstance(source_data, dict):
                    content = str(source_data)
                    if 'final_state' in content.lower():
                        has_final_state_spec = True
                        break

            if not has_final_state_spec:
                missing_specs.append({
                    'pattern_type': 'final_state_checks',
                    'occurrences': len(final_state_outputs),
                    'impact': 'high',
                    'description': 'Final-state checks found in output but not specified in any input',
                    'examples': final_state_outputs[:3]  # First 3 examples
                })

        # Check for cp2q patterns without specification
        cp2q_outputs = output_mappings.get('cp2q_patterns', [])
        if cp2q_outputs:
            has_cp2q_spec = False

            for source_name, source_data in input_sources.items():
                if isinstance(source_data, dict):
                    content = str(source_data)
                    if 'cp2q' in content.lower():
                        has_cp2q_spec = True
                        break

            if not has_cp2q_spec:
                missing_specs.append({
                    'pattern_type': 'cp2q_measurements',
                    'occurrences': len(cp2q_outputs),
                    'impact': 'medium',
                    'description': 'CP2Q measurements found in output but not specified in any input',
                    'examples': cp2q_outputs[:3]
                })

        # Check for post-processing signatures
        post_proc_outputs = output_mappings.get('post_processing_signatures', [])
        if post_proc_outputs:
            missing_specs.append({
                'pattern_type': 'post_processing',
                'occurrences': len(post_proc_outputs),
                'impact': 'critical',
                'description': 'Post-processing signatures indicate Python-generated content not in specifications',
                'examples': [sig.get('signature', '') for sig in post_proc_outputs[:3]]
            })

        return missing_specs

    def _extract_measurement_name(self, measurement_line: str) -> str:
        """Extract measurement name from SPICE .meas line."""
        # Pattern: .meas tran measurement_name ...
        match = re.search(r'\.meas\s+\w+\s+(\w+)', measurement_line, re.IGNORECASE)
        if match:
            return match.group(1)
        return ""


class SPICEDeckAnalyzer:
    """
    Analyzes mc_sim.sp files to extract comprehensive measurement patterns.

    Critical Focus: Analyze mc_sim.sp (NOT nominal_sim.sp) because it contains
    the actual Monte Carlo simulation setup with all measurements and post-processing.
    """

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.logger = self._setup_logging()

    def _setup_logging(self) -> logging.Logger:
        """Setup logging for SPICE analysis."""
        logger = logging.getLogger('SPICEAnalyzer')
        logger.setLevel(logging.DEBUG if self.verbose else logging.INFO)

        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        return logger

    def analyze_deck(self, deck_path: Path) -> Dict[str, Any]:
        """
        Comprehensive analysis of mc_sim.sp file.

        Returns detailed analysis including:
        - All measurements found
        - Final-state patterns
        - CP2Q monitoring patterns
        - Internal node usage
        - Post-processing signatures
        - Measurement timing analysis
        """

        if not deck_path.exists():
            return {
                'error': f"Deck file not found: {deck_path}",
                'file_path': str(deck_path)
            }

        self.logger.info(f"Analyzing SPICE deck: {deck_path}")

        analysis = {
            'file_path': str(deck_path),
            'file_size_bytes': deck_path.stat().st_size,
            'analysis_timestamp': str(Path(__file__).stat().st_mtime),

            # Basic structure
            'total_lines': 0,
            'comment_lines': 0,
            'measurement_lines': 0,

            # Measurements
            'measurements': [],
            'measurement_types': Counter(),
            'measurement_timing': [],

            # Patterns
            'final_state_patterns': [],
            'cp2q_patterns': [],
            'delay_patterns': [],
            'power_patterns': [],

            # Technical details
            'internal_nodes': [],
            'subcircuit_calls': [],
            'post_processing_signatures': [],

            # Analysis summary
            'summary': {}
        }

        try:
            with open(deck_path, 'r') as f:
                lines = f.readlines()
                analysis['total_lines'] = len(lines)

                # Analyze each line
                for line_num, line in enumerate(lines, 1):
                    self._analyze_line(line, line_num, analysis)

                # Generate summary statistics
                analysis['summary'] = self._generate_summary(analysis)

        except Exception as e:
            self.logger.error(f"Error analyzing deck {deck_path}: {e}")
            analysis['error'] = str(e)

        return analysis

    def _analyze_line(self, line: str, line_num: int, analysis: Dict[str, Any]) -> None:
        """Analyze individual line for patterns and measurements."""

        original_line = line
        line = line.strip()

        # Skip empty lines
        if not line:
            return

        # Count comment lines
        if line.startswith('*'):
            analysis['comment_lines'] += 1

            # Check for post-processing signatures in comments
            if any(sig in line for sig in ['POST_PROC', 'PYTHON_GEN', 'AUTO_GEN', 'MCQC_TOOL']):
                analysis['post_processing_signatures'].append({
                    'line_number': line_num,
                    'signature': line,
                    'type': 'comment_signature'
                })
            return

        # Analyze measurement lines
        if line.lower().startswith('.meas'):
            analysis['measurement_lines'] += 1
            self._analyze_measurement(line, line_num, analysis)

        # Analyze subcircuit calls
        elif line.lower().startswith('x'):
            self._analyze_subcircuit_call(line, line_num, analysis)

        # Analyze internal node references
        elif '.' in line and not line.startswith('.'):
            self._analyze_internal_nodes(line, line_num, analysis)

    def _analyze_measurement(self, line: str, line_num: int, analysis: Dict[str, Any]) -> None:
        """Detailed analysis of .meas statements."""

        measurement = {
            'line_number': line_num,
            'full_line': line,
            'measurement_name': self._extract_measurement_name(line),
            'measurement_type': self._classify_measurement_type(line),
            'timing_points': self._extract_timing_points(line),
            'target_signals': self._extract_target_signals(line),
            'when_conditions': self._extract_when_conditions(line)
        }

        analysis['measurements'].append(measurement)
        analysis['measurement_types'][measurement['measurement_type']] += 1

        # Categorize by pattern type
        if 'final_state' in line.lower():
            analysis['final_state_patterns'].append(measurement)

        elif 'cp2q' in line.lower():
            analysis['cp2q_patterns'].append(measurement)

        elif any(keyword in line.lower() for keyword in ['delay', 'tpd', 'tplh', 'tphl']):
            analysis['delay_patterns'].append(measurement)

        elif any(keyword in line.lower() for keyword in ['power', 'current', 'energy']):
            analysis['power_patterns'].append(measurement)

        # Extract timing information
        if any(keyword in line.lower() for keyword in ['when', 'cross', 'rise', 'fall']):
            timing_info = {
                'measurement_name': measurement['measurement_name'],
                'timing_events': self._extract_timing_events(line),
                'cross_points': self._extract_cross_points(line)
            }
            analysis['measurement_timing'].append(timing_info)

    def _analyze_subcircuit_call(self, line: str, line_num: int, analysis: Dict[str, Any]) -> None:
        """Analyze subcircuit instantiation lines."""

        # Extract subcircuit name and connections
        parts = line.split()
        if len(parts) >= 2:
            instance_name = parts[0]
            subckt_name = parts[-1]

            subckt_call = {
                'line_number': line_num,
                'instance_name': instance_name,
                'subcircuit_name': subckt_name,
                'connections': parts[1:-1]
            }

            analysis['subcircuit_calls'].append(subckt_call)

    def _analyze_internal_nodes(self, line: str, line_num: int, analysis: Dict[str, Any]) -> None:
        """Analyze lines that reference internal nodes."""

        # Look for node references like x.net, x.internal, etc.
        node_patterns = re.findall(r'\b\w+\.\w+', line)

        if node_patterns:
            for pattern in node_patterns:
                analysis['internal_nodes'].append({
                    'line_number': line_num,
                    'node_reference': pattern,
                    'context_line': line
                })

    def _extract_measurement_name(self, line: str) -> str:
        """Extract measurement name from .meas line."""
        # Pattern: .meas [analysis] measurement_name ...
        match = re.search(r'\.meas\s+(?:\w+\s+)?(\w+)', line, re.IGNORECASE)
        return match.group(1) if match else "unknown"

    def _classify_measurement_type(self, line: str) -> str:
        """Classify the type of measurement."""
        line_lower = line.lower()

        if 'final_state' in line_lower:
            return 'final_state'
        elif 'cp2q' in line_lower:
            return 'cp2q_monitoring'
        elif any(keyword in line_lower for keyword in ['delay', 'tpd', 'tplh', 'tphl']):
            return 'delay_measurement'
        elif any(keyword in line_lower for keyword in ['power', 'current', 'energy']):
            return 'power_measurement'
        elif 'when' in line_lower:
            return 'conditional_measurement'
        elif any(keyword in line_lower for keyword in ['max', 'min', 'avg']):
            return 'statistical_measurement'
        else:
            return 'basic_measurement'

    def _extract_timing_points(self, line: str) -> List[str]:
        """Extract timing reference points from measurement."""
        timing_points = []

        # Look for common timing keywords
        timing_keywords = ['rise', 'fall', 'cross', 'when', 'delay']

        for keyword in timing_keywords:
            if keyword in line.lower():
                timing_points.append(keyword)

        return timing_points

    def _extract_target_signals(self, line: str) -> List[str]:
        """Extract target signal names from measurement."""
        signals = []

        # Look for signal patterns like v(signal_name) or i(device)
        signal_patterns = re.findall(r'[vi]\(([^)]+)\)', line, re.IGNORECASE)
        signals.extend(signal_patterns)

        return signals

    def _extract_when_conditions(self, line: str) -> List[str]:
        """Extract WHEN conditions from measurement."""
        conditions = []

        # Find WHEN clauses
        when_match = re.search(r'when\s+([^=]+=[^=\s]+)', line, re.IGNORECASE)
        if when_match:
            conditions.append(when_match.group(1))

        return conditions

    def _extract_timing_events(self, line: str) -> List[Dict[str, str]]:
        """Extract timing events like rise/fall transitions."""
        events = []

        # Look for rise/fall patterns
        rise_pattern = r'rise=(\d+)'
        fall_pattern = r'fall=(\d+)'

        for pattern, event_type in [(rise_pattern, 'rise'), (fall_pattern, 'fall')]:
            matches = re.findall(pattern, line, re.IGNORECASE)
            for match in matches:
                events.append({
                    'type': event_type,
                    'occurrence': match
                })

        return events

    def _extract_cross_points(self, line: str) -> List[Dict[str, str]]:
        """Extract cross-point specifications."""
        cross_points = []

        # Look for cross specifications
        cross_pattern = r'cross=([0-9.]+)'
        matches = re.findall(cross_pattern, line, re.IGNORECASE)

        for match in matches:
            cross_points.append({
                'value': match,
                'type': 'voltage_cross'
            })

        return cross_points

    def _generate_summary(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate analysis summary statistics."""

        total_lines = analysis['total_lines']
        measurement_count = len(analysis['measurements'])

        summary = {
            'file_statistics': {
                'total_lines': total_lines,
                'comment_lines': analysis['comment_lines'],
                'measurement_lines': analysis['measurement_lines'],
                'measurement_density': measurement_count / total_lines if total_lines > 0 else 0
            },

            'measurement_statistics': {
                'total_measurements': measurement_count,
                'final_state_count': len(analysis['final_state_patterns']),
                'cp2q_count': len(analysis['cp2q_patterns']),
                'delay_count': len(analysis['delay_patterns']),
                'power_count': len(analysis['power_patterns'])
            },

            'pattern_percentages': {},

            'complexity_indicators': {
                'internal_node_references': len(analysis['internal_nodes']),
                'subcircuit_calls': len(analysis['subcircuit_calls']),
                'post_processing_signatures': len(analysis['post_processing_signatures']),
                'unique_measurement_types': len(analysis['measurement_types'])
            }
        }

        # Calculate pattern percentages
        if measurement_count > 0:
            summary['pattern_percentages'] = {
                'final_state_percentage': (len(analysis['final_state_patterns']) / measurement_count) * 100,
                'cp2q_percentage': (len(analysis['cp2q_patterns']) / measurement_count) * 100,
                'delay_percentage': (len(analysis['delay_patterns']) / measurement_count) * 100,
                'power_percentage': (len(analysis['power_patterns']) / measurement_count) * 100
            }

        return summary


class ComplianceValidator:
    """
    Validates SPICE deck compliance against input specifications.

    Determines PASS/FAIL status based on:
    - Input-to-output traceability completeness
    - Specification coverage
    - Pattern consistency
    - Missing specification severity
    """

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.logger = self._setup_logging()

        # Compliance thresholds
        self.thresholds = {
            'minimum_traceability': 0.7,    # 70% of outputs must trace to inputs
            'maximum_missing_critical': 2,   # Max 2 critical missing specifications
            'minimum_specification_coverage': 0.6,  # 60% of template specs must appear in output
            'maximum_inconsistencies': 5     # Max 5 pattern inconsistencies
        }

    def _setup_logging(self) -> logging.Logger:
        """Setup logging for compliance validation."""
        logger = logging.getLogger('ComplianceValidator')
        logger.setLevel(logging.DEBUG if self.verbose else logging.INFO)

        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        return logger

    def validate_compliance(self, traceability_data: Dict[str, Any], deck_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Comprehensive compliance validation.

        Returns detailed validation results with PASS/FAIL status and reasons.
        """

        self.logger.info(f"Validating compliance for arc: {traceability_data.get('arc_name', 'unknown')}")

        validation_result = {
            'arc_name': traceability_data.get('arc_name'),
            'overall_status': 'UNKNOWN',
            'validation_timestamp': str(Path(__file__).stat().st_mtime),

            # Individual test results
            'tests': {
                'traceability_test': self._test_input_traceability(traceability_data),
                'specification_coverage_test': self._test_specification_coverage(traceability_data),
                'missing_specifications_test': self._test_missing_specifications(traceability_data),
                'pattern_consistency_test': self._test_pattern_consistency(deck_analysis),
                'deck_structure_test': self._test_deck_structure(deck_analysis)
            },

            # Summary counts
            'test_summary': {},
            'critical_issues': [],
            'recommendations': []
        }

        # Determine overall status
        validation_result['overall_status'] = self._determine_overall_status(validation_result['tests'])
        validation_result['test_summary'] = self._generate_test_summary(validation_result['tests'])
        validation_result['critical_issues'] = self._identify_critical_issues(validation_result['tests'])
        validation_result['recommendations'] = self._generate_recommendations(validation_result['tests'])

        return validation_result

    def _test_input_traceability(self, traceability_data: Dict[str, Any]) -> Dict[str, Any]:
        """Test completeness of input-to-output traceability."""

        test_result = {
            'test_name': 'Input Traceability',
            'status': 'UNKNOWN',
            'score': 0.0,
            'details': {},
            'issues': []
        }

        try:
            correlation_data = traceability_data.get('input_to_output_correlation', {})

            # Calculate traceability metrics
            direct_mappings = len(correlation_data.get('direct_mappings', []))
            missing_specs = len(correlation_data.get('missing_specifications', []))
            unexpected_outputs = len(correlation_data.get('unexpected_outputs', []))

            confidence_scores = correlation_data.get('confidence_scores', {})
            template_coverage = confidence_scores.get('template_coverage', 0.0)
            output_coverage = confidence_scores.get('output_coverage', 0.0)

            # Calculate overall traceability score
            traceability_score = (template_coverage + output_coverage) / 2.0
            test_result['score'] = traceability_score

            # Determine status
            if traceability_score >= self.thresholds['minimum_traceability']:
                test_result['status'] = 'PASS'
            else:
                test_result['status'] = 'FAIL'
                test_result['issues'].append(
                    f"Traceability score {traceability_score:.1%} below threshold {self.thresholds['minimum_traceability']:.1%}"
                )

            # Add detailed metrics
            test_result['details'] = {
                'direct_mappings': direct_mappings,
                'missing_specifications': missing_specs,
                'unexpected_outputs': unexpected_outputs,
                'template_coverage': template_coverage,
                'output_coverage': output_coverage,
                'traceability_score': traceability_score
            }

        except Exception as e:
            test_result['status'] = 'ERROR'
            test_result['issues'].append(f"Traceability test error: {e}")

        return test_result

    def _test_specification_coverage(self, traceability_data: Dict[str, Any]) -> Dict[str, Any]:
        """Test how well specifications cover actual outputs."""

        test_result = {
            'test_name': 'Specification Coverage',
            'status': 'UNKNOWN',
            'score': 0.0,
            'details': {},
            'issues': []
        }

        try:
            input_sources = traceability_data.get('input_sources', {})
            output_mappings = traceability_data.get('output_mappings', {})

            # Count specifications in inputs
            total_input_specs = 0
            for source_name, source_data in input_sources.items():
                if isinstance(source_data, dict):
                    measurements = source_data.get('measurements_found', [])
                    total_input_specs += len(measurements)

            # Count actual outputs
            output_measurements = len(output_mappings.get('measurements_found', []))

            # Calculate coverage
            if total_input_specs > 0:
                coverage_score = min(1.0, output_measurements / total_input_specs)
            else:
                coverage_score = 0.0 if output_measurements > 0 else 1.0

            test_result['score'] = coverage_score

            # Determine status
            if coverage_score >= self.thresholds['minimum_specification_coverage']:
                test_result['status'] = 'PASS'
            else:
                test_result['status'] = 'FAIL'
                test_result['issues'].append(
                    f"Specification coverage {coverage_score:.1%} below threshold {self.thresholds['minimum_specification_coverage']:.1%}"
                )

            test_result['details'] = {
                'total_input_specifications': total_input_specs,
                'total_output_measurements': output_measurements,
                'coverage_score': coverage_score
            }

        except Exception as e:
            test_result['status'] = 'ERROR'
            test_result['issues'].append(f"Coverage test error: {e}")

        return test_result

    def _test_missing_specifications(self, traceability_data: Dict[str, Any]) -> Dict[str, Any]:
        """Test severity of missing specifications."""

        test_result = {
            'test_name': 'Missing Specifications',
            'status': 'UNKNOWN',
            'score': 0.0,
            'details': {},
            'issues': []
        }

        try:
            missing_specs = traceability_data.get('missing_specs', [])

            # Count by severity
            critical_missing = 0
            high_missing = 0
            medium_missing = 0

            for spec in missing_specs:
                impact = spec.get('impact', 'unknown').lower()
                if impact == 'critical':
                    critical_missing += 1
                elif impact == 'high':
                    high_missing += 1
                elif impact == 'medium':
                    medium_missing += 1

            # Determine status based on critical missing specs
            if critical_missing <= self.thresholds['maximum_missing_critical']:
                test_result['status'] = 'PASS'
                test_result['score'] = 1.0 - (critical_missing / 10.0)  # Penalty for missing specs
            else:
                test_result['status'] = 'FAIL'
                test_result['score'] = 0.0
                test_result['issues'].append(
                    f"Critical missing specifications ({critical_missing}) exceeds threshold ({self.thresholds['maximum_missing_critical']})"
                )

            # Add warnings for high/medium missing specs
            if high_missing > 0:
                test_result['issues'].append(f"{high_missing} high-impact missing specifications detected")
            if medium_missing > 0:
                test_result['issues'].append(f"{medium_missing} medium-impact missing specifications detected")

            test_result['details'] = {
                'total_missing': len(missing_specs),
                'critical_missing': critical_missing,
                'high_missing': high_missing,
                'medium_missing': medium_missing,
                'missing_specifications': missing_specs
            }

        except Exception as e:
            test_result['status'] = 'ERROR'
            test_result['issues'].append(f"Missing specifications test error: {e}")

        return test_result

    def _test_pattern_consistency(self, deck_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Test consistency of measurement patterns."""

        test_result = {
            'test_name': 'Pattern Consistency',
            'status': 'UNKNOWN',
            'score': 0.0,
            'details': {},
            'issues': []
        }

        try:
            measurements = deck_analysis.get('measurements', [])
            inconsistencies = []

            # Check for inconsistent measurement naming
            measurement_names = [m.get('measurement_name', '') for m in measurements]
            name_patterns = {}

            for name in measurement_names:
                if name:
                    # Extract pattern (remove numbers, suffixes)
                    pattern = re.sub(r'\d+$', '', name)
                    pattern = re.sub(r'_\d+$', '', pattern)

                    if pattern in name_patterns:
                        name_patterns[pattern].append(name)
                    else:
                        name_patterns[pattern] = [name]

            # Look for inconsistent patterns
            for pattern, names in name_patterns.items():
                if len(set(names)) > 1:  # Different variations of same pattern
                    inconsistencies.append({
                        'type': 'naming_inconsistency',
                        'pattern': pattern,
                        'variations': list(set(names))
                    })

            # Check measurement type consistency
            measurement_types = Counter(m.get('measurement_type', '') for m in measurements)
            expected_types = ['delay_measurement', 'final_state', 'cp2q_monitoring']

            for meas_type in measurement_types:
                if meas_type not in expected_types:
                    inconsistencies.append({
                        'type': 'unexpected_measurement_type',
                        'measurement_type': meas_type,
                        'count': measurement_types[meas_type]
                    })

            # Determine status
            inconsistency_count = len(inconsistencies)
            if inconsistency_count <= self.thresholds['maximum_inconsistencies']:
                test_result['status'] = 'PASS'
                test_result['score'] = 1.0 - (inconsistency_count / 20.0)  # Penalty for inconsistencies
            else:
                test_result['status'] = 'FAIL'
                test_result['score'] = 0.0
                test_result['issues'].append(
                    f"Pattern inconsistencies ({inconsistency_count}) exceed threshold ({self.thresholds['maximum_inconsistencies']})"
                )

            test_result['details'] = {
                'total_inconsistencies': inconsistency_count,
                'inconsistencies': inconsistencies,
                'measurement_type_distribution': dict(measurement_types)
            }

        except Exception as e:
            test_result['status'] = 'ERROR'
            test_result['issues'].append(f"Pattern consistency test error: {e}")

        return test_result

    def _test_deck_structure(self, deck_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Test basic SPICE deck structure validity."""

        test_result = {
            'test_name': 'Deck Structure',
            'status': 'UNKNOWN',
            'score': 0.0,
            'details': {},
            'issues': []
        }

        try:
            if 'error' in deck_analysis:
                test_result['status'] = 'FAIL'
                test_result['score'] = 0.0
                test_result['issues'].append(f"Deck analysis error: {deck_analysis['error']}")
                return test_result

            # Check basic structure requirements
            total_lines = deck_analysis.get('total_lines', 0)
            measurement_count = len(deck_analysis.get('measurements', []))

            structure_score = 1.0

            # Minimum line requirement
            if total_lines < 10:
                test_result['issues'].append(f"Deck too short: {total_lines} lines")
                structure_score -= 0.3

            # Minimum measurement requirement
            if measurement_count < 1:
                test_result['issues'].append("No measurements found in deck")
                structure_score -= 0.5

            # Check for essential SPICE elements
            has_subcircuits = len(deck_analysis.get('subcircuit_calls', [])) > 0
            if not has_subcircuits:
                test_result['issues'].append("No subcircuit calls found")
                structure_score -= 0.2

            test_result['score'] = max(0.0, structure_score)

            # Determine status
            if structure_score >= 0.7:
                test_result['status'] = 'PASS'
            else:
                test_result['status'] = 'FAIL'

            test_result['details'] = {
                'total_lines': total_lines,
                'measurement_count': measurement_count,
                'subcircuit_calls': len(deck_analysis.get('subcircuit_calls', [])),
                'structure_score': structure_score
            }

        except Exception as e:
            test_result['status'] = 'ERROR'
            test_result['issues'].append(f"Deck structure test error: {e}")

        return test_result

    def _determine_overall_status(self, tests: Dict[str, Dict]) -> str:
        """Determine overall compliance status from individual tests."""

        statuses = [test.get('status', 'UNKNOWN') for test in tests.values()]

        # If any test failed, overall fails
        if 'FAIL' in statuses:
            return 'FAIL'

        # If any test errored, overall is error
        if 'ERROR' in statuses:
            return 'ERROR'

        # If all tests passed, overall passes
        if all(status == 'PASS' for status in statuses):
            return 'PASS'

        # Otherwise unknown
        return 'UNKNOWN'

    def _generate_test_summary(self, tests: Dict[str, Dict]) -> Dict[str, Any]:
        """Generate summary statistics for all tests."""

        statuses = [test.get('status', 'UNKNOWN') for test in tests.values()]
        scores = [test.get('score', 0.0) for test in tests.values()]

        return {
            'total_tests': len(tests),
            'passed_tests': statuses.count('PASS'),
            'failed_tests': statuses.count('FAIL'),
            'error_tests': statuses.count('ERROR'),
            'average_score': sum(scores) / len(scores) if scores else 0.0,
            'pass_rate': statuses.count('PASS') / len(statuses) if statuses else 0.0
        }

    def _identify_critical_issues(self, tests: Dict[str, Dict]) -> List[str]:
        """Identify critical issues from test results."""

        critical_issues = []

        for test_name, test_result in tests.items():
            if test_result.get('status') == 'FAIL':
                issues = test_result.get('issues', [])
                for issue in issues:
                    critical_issues.append(f"{test_name}: {issue}")

        return critical_issues

    def _generate_recommendations(self, tests: Dict[str, Dict]) -> List[str]:
        """Generate recommendations based on test results."""

        recommendations = []

        # Traceability recommendations
        traceability_test = tests.get('traceability_test', {})
        if traceability_test.get('status') == 'FAIL':
            recommendations.append("Improve input-to-output traceability by adding specification comments in templates")

        # Coverage recommendations
        coverage_test = tests.get('specification_coverage_test', {})
        if coverage_test.get('status') == 'FAIL':
            recommendations.append("Add missing specifications to template files or document intentional omissions")

        # Missing specifications recommendations
        missing_test = tests.get('missing_specifications_test', {})
        if missing_test.get('status') == 'FAIL':
            recommendations.append("Document Python logic patterns in template specifications or configuration files")

        # Pattern consistency recommendations
        consistency_test = tests.get('pattern_consistency_test', {})
        if consistency_test.get('status') == 'FAIL':
            recommendations.append("Standardize measurement naming patterns and types across all decks")

        # Structure recommendations
        structure_test = tests.get('deck_structure_test', {})
        if structure_test.get('status') == 'FAIL':
            recommendations.append("Validate SPICE deck generation process for completeness and correctness")

        return recommendations


class ReportGenerator:
    """
    Generates structured reports for specification compliance validation.

    Outputs:
    - Structured YAML reports with clear section headers
    - Simple CSV summaries for pass/fail status
    - Human-readable documentation
    """

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.logger = self._setup_logging()

    def _setup_logging(self) -> logging.Logger:
        """Setup logging for report generation."""
        logger = logging.getLogger('ReportGenerator')
        logger.setLevel(logging.DEBUG if self.verbose else logging.INFO)

        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        return logger

    def generate_structured_report(self, validation_data: Dict[str, Any], output_path: Path) -> None:
        """
        Generate structured YAML report with clear section headers.

        Report includes complete traceability information and validation results.
        """

        self.logger.info(f"Generating structured report: {output_path}")

        # Structure the report with clear sections
        report = {
            '# MCQC Specification Compliance Report': None,

            '## Arc Information': {
                'Arc Name': validation_data.get('arc_name', 'unknown'),
                'Arc Folder': validation_data.get('arc_folder', 'unknown'),
                'Validation Timestamp': validation_data.get('validation_timestamp', 'unknown')
            },

            '## Compliance Status': {
                'Overall Status': validation_data.get('overall_status', 'UNKNOWN'),
                'Pass Rate': f"{validation_data.get('test_summary', {}).get('pass_rate', 0.0):.1%}",
                'Tests Passed': f"{validation_data.get('test_summary', {}).get('passed_tests', 0)}/{validation_data.get('test_summary', {}).get('total_tests', 0)}",
                'Average Score': f"{validation_data.get('test_summary', {}).get('average_score', 0.0):.2f}"
            },

            '## Input Traceability Analysis': self._format_traceability_section(validation_data),

            '## SPICE Deck Analysis': self._format_deck_analysis_section(validation_data),

            '## Validation Test Results': self._format_test_results_section(validation_data),

            '## Critical Issues': validation_data.get('critical_issues', []),

            '## Recommendations': validation_data.get('recommendations', []),

            '## Detailed Data': self._format_detailed_data_section(validation_data)
        }

        # Write structured report (YAML if available, JSON fallback)
        try:
            if YAML_AVAILABLE:
                with open(output_path, 'w') as f:
                    yaml.dump(report, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
                self.logger.info(f"Structured YAML report written to: {output_path}")
            else:
                # Fallback to JSON format
                json_path = output_path.with_suffix('.json')
                with open(json_path, 'w') as f:
                    json.dump(report, f, indent=2, default=str)
                self.logger.info(f"Structured JSON report written to: {json_path} (YAML not available)")

        except Exception as e:
            self.logger.error(f"Error writing structured report: {e}")

    def generate_csv_summary(self, validation_results: List[Dict[str, Any]], output_path: Path) -> None:
        """
        Generate simple CSV summary with pass/fail status.

        Format: ArcName,OverallStatus,PassRate,CriticalIssueCount,RecommendationCount
        """

        self.logger.info(f"Generating CSV summary: {output_path}")

        try:
            with open(output_path, 'w', newline='') as f:
                writer = csv.writer(f)

                # Write header
                writer.writerow([
                    'ArcName',
                    'OverallStatus',
                    'PassRate',
                    'TestsPassed',
                    'TotalTests',
                    'AverageScore',
                    'CriticalIssueCount',
                    'RecommendationCount',
                    'TracingScore',
                    'CoverageScore',
                    'MissingSpecs',
                    'PatternInconsistencies'
                ])

                # Write data rows
                for result in validation_results:
                    test_summary = result.get('test_summary', {})

                    # Extract specific test scores
                    tests = result.get('tests', {})
                    tracing_score = tests.get('traceability_test', {}).get('score', 0.0)
                    coverage_score = tests.get('specification_coverage_test', {}).get('score', 0.0)

                    missing_test = tests.get('missing_specifications_test', {})
                    missing_specs = missing_test.get('details', {}).get('total_missing', 0)

                    consistency_test = tests.get('pattern_consistency_test', {})
                    inconsistencies = consistency_test.get('details', {}).get('total_inconsistencies', 0)

                    writer.writerow([
                        result.get('arc_name', 'unknown'),
                        result.get('overall_status', 'UNKNOWN'),
                        f"{test_summary.get('pass_rate', 0.0):.1%}",
                        test_summary.get('passed_tests', 0),
                        test_summary.get('total_tests', 0),
                        f"{test_summary.get('average_score', 0.0):.2f}",
                        len(result.get('critical_issues', [])),
                        len(result.get('recommendations', [])),
                        f"{tracing_score:.2f}",
                        f"{coverage_score:.2f}",
                        missing_specs,
                        inconsistencies
                    ])

            self.logger.info(f"CSV summary written to: {output_path}")

        except Exception as e:
            self.logger.error(f"Error writing CSV summary: {e}")

    def _format_traceability_section(self, validation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Format input traceability section for report."""

        traceability = validation_data.get('traceability_data', {})

        section = {
            'Input Sources Found': {},
            'Output Mappings': {},
            'Correlation Analysis': {},
            'Missing Specifications': []
        }

        # Input sources summary
        input_sources = traceability.get('input_sources', {})
        for source_name, source_data in input_sources.items():
            if isinstance(source_data, dict):
                file_path = source_data.get('file_path', 'unknown')
                parser_used = source_data.get('parser_used', 'unknown')

                section['Input Sources Found'][source_name] = {
                    'File Path': file_path,
                    'Parser Used': parser_used,
                    'Content Summary': self._summarize_input_content(source_data)
                }

        # Output mappings summary
        output_mappings = traceability.get('output_mappings', {})
        section['Output Mappings'] = {
            'Total Measurements': len(output_mappings.get('measurements_found', [])),
            'Final State Checks': len(output_mappings.get('final_state_checks', [])),
            'CP2Q Patterns': len(output_mappings.get('cp2q_patterns', [])),
            'Internal Nodes': len(output_mappings.get('internal_nodes', [])),
            'Post Processing Signatures': len(output_mappings.get('post_processing_signatures', []))
        }

        # Correlation analysis
        correlation = traceability.get('input_to_output_correlation', {})
        section['Correlation Analysis'] = {
            'Direct Mappings': len(correlation.get('direct_mappings', [])),
            'Missing Specifications': len(correlation.get('missing_specifications', [])),
            'Unexpected Outputs': len(correlation.get('unexpected_outputs', [])),
            'Confidence Scores': correlation.get('confidence_scores', {})
        }

        # Missing specifications
        section['Missing Specifications'] = traceability.get('missing_specs', [])

        return section

    def _format_deck_analysis_section(self, validation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Format SPICE deck analysis section for report."""

        deck_analysis = validation_data.get('deck_analysis', {})

        section = {
            'File Information': {
                'File Path': deck_analysis.get('file_path', 'unknown'),
                'File Size (bytes)': deck_analysis.get('file_size_bytes', 0),
                'Total Lines': deck_analysis.get('total_lines', 0),
                'Comment Lines': deck_analysis.get('comment_lines', 0),
                'Measurement Lines': deck_analysis.get('measurement_lines', 0)
            },

            'Measurement Analysis': {
                'Total Measurements': len(deck_analysis.get('measurements', [])),
                'Measurement Types': dict(deck_analysis.get('measurement_types', {})),
                'Final State Patterns': len(deck_analysis.get('final_state_patterns', [])),
                'CP2Q Patterns': len(deck_analysis.get('cp2q_patterns', [])),
                'Delay Patterns': len(deck_analysis.get('delay_patterns', [])),
                'Power Patterns': len(deck_analysis.get('power_patterns', []))
            },

            'Technical Details': {
                'Internal Nodes': len(deck_analysis.get('internal_nodes', [])),
                'Subcircuit Calls': len(deck_analysis.get('subcircuit_calls', [])),
                'Post Processing Signatures': len(deck_analysis.get('post_processing_signatures', []))
            },

            'Summary Statistics': deck_analysis.get('summary', {})
        }

        return section

    def _format_test_results_section(self, validation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Format validation test results section for report."""

        tests = validation_data.get('tests', {})

        section = {}

        for test_name, test_result in tests.items():
            section[test_name] = {
                'Status': test_result.get('status', 'UNKNOWN'),
                'Score': f"{test_result.get('score', 0.0):.2f}",
                'Issues': test_result.get('issues', []),
                'Details': test_result.get('details', {})
            }

        return section

    def _format_detailed_data_section(self, validation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Format detailed data section for report (limited to prevent huge reports)."""

        # Include only essential detailed data, not full raw content
        section = {
            'Note': 'This section contains summarized detailed data. Full raw data available in source analysis.',

            'Input File Paths': [],
            'Key Measurements Found': [],
            'Pattern Examples': {}
        }

        # Extract input file paths
        traceability = validation_data.get('traceability_data', {})
        input_sources = traceability.get('input_sources', {})

        for source_name, source_data in input_sources.items():
            if isinstance(source_data, dict):
                file_path = source_data.get('file_path')
                if file_path:
                    section['Input File Paths'].append(f"{source_name}: {file_path}")

        # Extract key measurements (first 5)
        deck_analysis = validation_data.get('deck_analysis', {})
        measurements = deck_analysis.get('measurements', [])[:5]

        for meas in measurements:
            section['Key Measurements Found'].append({
                'Name': meas.get('measurement_name', 'unknown'),
                'Type': meas.get('measurement_type', 'unknown'),
                'Line': meas.get('line_number', 0)
            })

        # Extract pattern examples
        final_states = deck_analysis.get('final_state_patterns', [])[:3]
        if final_states:
            section['Pattern Examples']['Final State'] = [
                meas.get('measurement_name', 'unknown') for meas in final_states
            ]

        cp2q_patterns = deck_analysis.get('cp2q_patterns', [])[:3]
        if cp2q_patterns:
            section['Pattern Examples']['CP2Q'] = [
                meas.get('measurement_name', 'unknown') for meas in cp2q_patterns
            ]

        return section

    def _summarize_input_content(self, source_data: Dict[str, Any]) -> Dict[str, Any]:
        """Summarize input source content for report."""

        summary = {}

        # Count measurements
        measurements = source_data.get('measurements_found', [])
        if measurements:
            summary['Measurements Count'] = len(measurements)

        # Count raw lines
        raw_lines = source_data.get('raw_lines', [])
        if raw_lines:
            summary['Key Lines Count'] = len(raw_lines)

        # Count parameters
        parameters = source_data.get('parameters', {})
        if parameters:
            summary['Parameters Count'] = len(parameters)

        return summary


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
  # Audit single arc
  python audit_deck_compliance.py --arc_folder /work/MCQC_RUN/DECKS/mpw_SDFQTXG_X1/ --output_dir ./results/

  # Audit multiple arcs
  python audit_deck_compliance.py --deck_dir /work/MCQC_RUN/DECKS/ --output_dir ./results/

  # Verbose analysis with detailed logging
  python audit_deck_compliance.py --deck_dir /work/DECKS/ --output_dir ./results/ --verbose

  # Generate only CSV summary
  python audit_deck_compliance.py --deck_dir /work/DECKS/ --output_dir ./results/ --csv_only
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

    # Output arguments
    parser.add_argument(
        '--output_dir',
        type=Path,
        required=True,
        help='Directory to write validation reports'
    )

    # Control arguments
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    parser.add_argument(
        '--csv_only',
        action='store_true',
        help='Generate only CSV summary, skip detailed YAML reports'
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
            print(f"❌ Arc folder not found: {args.arc_folder}")
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
                print(f"❌ No arc folders with mc_sim.sp found in: {args.deck_dir}")
                return 1
        else:
            print(f"❌ Deck directory not found: {args.deck_dir}")
            return 1

    print(f"🔍 Processing {len(arc_folders)} arc folders...")

    # Process each arc folder
    validation_results = []

    for i, arc_folder in enumerate(arc_folders, 1):
        print(f"[{i}/{len(arc_folders)}] Processing: {arc_folder.name}")

        try:
            # Step 1: Trace inputs
            traceability_data = tracer.trace_arc_inputs(arc_folder)

            # Step 2: Analyze mc_sim.sp deck
            mc_sim_file = arc_folder / "mc_sim.sp"
            deck_analysis = analyzer.analyze_deck(mc_sim_file)

            # Step 3: Validate compliance
            validation_result = validator.validate_compliance(traceability_data, deck_analysis)

            # Add source data to validation result
            validation_result['traceability_data'] = traceability_data
            validation_result['deck_analysis'] = deck_analysis

            validation_results.append(validation_result)

            # Step 4: Generate individual report (unless CSV only)
            if not args.csv_only:
                report_file = args.output_dir / f"{arc_folder.name}_compliance_report.yaml"
                reporter.generate_structured_report(validation_result, report_file)

            print(f"  ✅ Status: {validation_result['overall_status']}")

        except Exception as e:
            print(f"  ❌ Error processing {arc_folder.name}: {e}")

            # Create error result
            error_result = {
                'arc_name': arc_folder.name,
                'overall_status': 'ERROR',
                'error': str(e),
                'test_summary': {'total_tests': 0, 'passed_tests': 0, 'failed_tests': 0, 'error_tests': 1, 'pass_rate': 0.0, 'average_score': 0.0},
                'critical_issues': [f"Processing error: {e}"],
                'recommendations': ['Check arc folder structure and file accessibility']
            }
            validation_results.append(error_result)

    # Step 5: Generate CSV summary
    csv_file = args.output_dir / "compliance_summary.csv"
    reporter.generate_csv_summary(validation_results, csv_file)

    # Print summary
    print(f"\n📊 Validation Summary:")
    print(f"   Total arcs processed: {len(validation_results)}")

    statuses = [result.get('overall_status', 'UNKNOWN') for result in validation_results]
    print(f"   PASS: {statuses.count('PASS')}")
    print(f"   FAIL: {statuses.count('FAIL')}")
    print(f"   ERROR: {statuses.count('ERROR')}")

    pass_rate = statuses.count('PASS') / len(statuses) if statuses else 0.0
    print(f"   Overall pass rate: {pass_rate:.1%}")

    print(f"\n📁 Reports generated in: {args.output_dir}")
    print(f"   CSV summary: {csv_file}")

    if not args.csv_only:
        yaml_count = len([f for f in args.output_dir.glob("*_compliance_report.yaml")])
        print(f"   YAML reports: {yaml_count} files")

    return 0


if __name__ == "__main__":
    exit(main())