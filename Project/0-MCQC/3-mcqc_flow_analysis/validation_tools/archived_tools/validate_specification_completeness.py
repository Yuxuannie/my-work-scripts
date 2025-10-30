#!/usr/bin/env python3
"""
Specification Completeness Validator

Compares what's specified in template*.tcl files vs what actually gets generated
in SPICE decks. Identifies gaps where behavior exists without specification.

Usage:
    python validate_specification_completeness.py --template_file template.tcl --analysis_csv deck_analysis.csv --output gaps.json
    python validate_specification_completeness.py --template_file template.tcl --analysis_csv analysis.csv --output gaps.json --verbose

Example:
    python validate_specification_completeness.py --template_file /work/lib/template_mpw.tcl --analysis_csv deck_analysis.csv --output specification_gaps.json

Author: MCQC Validation Team
Date: October 2025
"""

import csv
import json
import argparse
import sys
import re
from pathlib import Path
from collections import defaultdict, Counter
from typing import Dict, List, Any, Set, Tuple

class SpecificationGapAnalyzer:
    """Analyzes gaps between template specifications and actual SPICE deck outputs."""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose

        # Template specification data
        self.template_arcs = {}
        self.template_cells = {}
        self.template_attributes = set()

        # Generated deck data
        self.deck_behaviors = {}
        self.behavior_patterns = defaultdict(set)

        # Gap analysis results
        self.gaps = {
            'missing_specifications': [],    # In deck but not in template
            'missing_implementations': [],   # In template but not in deck
            'ambiguous_mappings': [],       # Unclear how spec maps to output
            'hidden_logic_detected': [],    # Logic that exists only in Python
            'eda_tool_gaps': []             # Features EDA tools cannot reproduce
        }

        self.statistics = {}

    def load_template_specification(self, template_file: Path) -> bool:
        """Load and parse template*.tcl file to extract specifications."""
        if self.verbose:
            print(f"Loading template specification from: {template_file}")

        try:
            with open(template_file, 'r', encoding='utf-8') as f:
                content = f.read()

            self._parse_template_content(content)

            if self.verbose:
                print(f"Loaded {len(self.template_cells)} cells and {len(self.template_arcs)} arcs")

            return True

        except Exception as e:
            print(f"Error loading template file: {e}")
            return False

    def _parse_template_content(self, content: str):
        """Parse template.tcl content to extract cell and arc specifications."""
        lines = content.split('\n')
        current_cell = None
        current_pin = None
        current_timing = None

        i = 0
        while i < len(lines):
            line = lines[i].strip()

            # Skip comments and empty lines
            if not line or line.startswith('/*') or line.startswith('//'):
                i += 1
                continue

            # Cell definition
            cell_match = re.match(r'cell\s*\(\s*([^)]+)\s*\)\s*\{', line)
            if cell_match:
                current_cell = cell_match.group(1).strip()
                self.template_cells[current_cell] = {
                    'pins': {},
                    'timing_arcs': [],
                    'attributes': set()
                }
                i += 1
                continue

            # Pin definition
            if current_cell:
                pin_match = re.match(r'pin\s*\(\s*([^)]+)\s*\)\s*\{', line)
                if pin_match:
                    current_pin = pin_match.group(1).strip()
                    self.template_cells[current_cell]['pins'][current_pin] = {
                        'direction': None,
                        'capacitance': None,
                        'timing_arcs': []
                    }
                    i += 1
                    continue

                # Timing arc definition
                if current_pin:
                    timing_match = re.match(r'timing\s*\(\s*\)\s*\{', line)
                    if timing_match:
                        current_timing = {
                            'timing_type': None,
                            'related_pin': None,
                            'when': None,
                            'rise_constraint': None,
                            'fall_constraint': None,
                            'cell': current_cell,
                            'pin': current_pin
                        }
                        i += 1
                        continue

                    # Parse timing attributes
                    if current_timing:
                        timing_type_match = re.search(r'timing_type\s*:\s*([^;]+);', line)
                        if timing_type_match:
                            current_timing['timing_type'] = timing_type_match.group(1).strip().strip('"')
                            self.template_attributes.add('timing_type')

                        related_pin_match = re.search(r'related_pin\s*:\s*([^;]+);', line)
                        if related_pin_match:
                            current_timing['related_pin'] = related_pin_match.group(1).strip().strip('"')
                            self.template_attributes.add('related_pin')

                        when_match = re.search(r'when\s*:\s*([^;]+);', line)
                        if when_match:
                            current_timing['when'] = when_match.group(1).strip().strip('"')
                            self.template_attributes.add('when')

                        rise_constraint_match = re.search(r'rise_constraint\s*\(\s*([^)]+)\s*\)', line)
                        if rise_constraint_match:
                            current_timing['rise_constraint'] = rise_constraint_match.group(1).strip()
                            self.template_attributes.add('rise_constraint')

                        fall_constraint_match = re.search(r'fall_constraint\s*\(\s*([^)]+)\s*\)', line)
                        if fall_constraint_match:
                            current_timing['fall_constraint'] = fall_constraint_match.group(1).strip()
                            self.template_attributes.add('fall_constraint')

                        # End of timing block
                        if line.strip() == '}':
                            if current_timing['timing_type']:
                                arc_key = f"{current_cell}:{current_pin}:{current_timing['timing_type']}"
                                self.template_arcs[arc_key] = current_timing.copy()
                                self.template_cells[current_cell]['timing_arcs'].append(current_timing.copy())
                                self.template_cells[current_cell]['pins'][current_pin]['timing_arcs'].append(current_timing.copy())
                            current_timing = None

                # Pin attributes
                if current_pin and not current_timing:
                    direction_match = re.search(r'direction\s*:\s*([^;]+);', line)
                    if direction_match:
                        self.template_cells[current_cell]['pins'][current_pin]['direction'] = direction_match.group(1).strip()

                    capacitance_match = re.search(r'capacitance\s*:\s*([^;]+);', line)
                    if capacitance_match:
                        self.template_cells[current_cell]['pins'][current_pin]['capacitance'] = capacitance_match.group(1).strip()

                    # End of pin block
                    if line.strip() == '}':
                        current_pin = None

            # End of cell block
            if line.strip() == '}' and current_cell and not current_pin:
                current_cell = None

            i += 1

    def load_deck_analysis(self, csv_file: Path) -> bool:
        """Load deck analysis data from CSV file."""
        if self.verbose:
            print(f"Loading deck analysis from: {csv_file}")

        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    processed_row = self._process_csv_row(row)
                    arc_key = f"{processed_row['cell_name']}:{processed_row['pin']}:{processed_row['arc_type']}"
                    self.deck_behaviors[arc_key] = processed_row

            if self.verbose:
                print(f"Loaded {len(self.deck_behaviors)} deck behaviors")

            return True

        except Exception as e:
            print(f"Error loading deck analysis: {e}")
            return False

    def _process_csv_row(self, row: Dict[str, str]) -> Dict[str, Any]:
        """Convert CSV string values back to appropriate Python types."""
        processed = {}

        for key, value in row.items():
            if value == '':
                processed[key] = None
            elif key in ['has_final_state', 'has_cp2q_del1', 'has_cp2q_del2',
                        'has_glitch_check', 'uses_internal_nodes']:
                processed[key] = value.lower() == 'true'
            elif key in ['num_final_state_meas', 'num_final_state_check_meas',
                        'complexity_score', 'file_size', 'line_count']:
                processed[key] = int(value) if value.isdigit() else 0
            elif key in ['measurement_nodes', 'output_pins_measured', 'internal_nodes_measured',
                        'threshold_values', 'post_processors_detected', 'error_indicators']:
                processed[key] = value.split(';') if value else []
            else:
                processed[key] = value

        return processed

    def analyze_gaps(self) -> Dict[str, Any]:
        """Analyze gaps between template specifications and deck implementations."""
        if self.verbose:
            print("Analyzing specification gaps...")

        # Find missing specifications
        self._find_missing_specifications()

        # Find missing implementations
        self._find_missing_implementations()

        # Find ambiguous mappings
        self._find_ambiguous_mappings()

        # Detect hidden logic
        self._detect_hidden_logic()

        # Analyze EDA tool compatibility gaps
        self._analyze_eda_tool_gaps()

        # Generate statistics
        self._generate_statistics()

        if self.verbose:
            print(f"Gap analysis complete. Found {len(self.gaps['missing_specifications'])} missing specifications")

        return self._compile_results()

    def _find_missing_specifications(self):
        """Find behaviors in decks that are not specified in template."""
        if self.verbose:
            print("  Finding missing specifications...")

        for arc_key, deck_behavior in self.deck_behaviors.items():
            template_arc = self.template_arcs.get(arc_key)

            if not template_arc:
                # Arc exists in deck but not in template
                self.gaps['missing_specifications'].append({
                    'type': 'MISSING_ARC_SPECIFICATION',
                    'arc_key': arc_key,
                    'cell_name': deck_behavior['cell_name'],
                    'pin': deck_behavior['pin'],
                    'arc_type': deck_behavior['arc_type'],
                    'deck_behaviors': self._extract_deck_behaviors(deck_behavior),
                    'severity': 'HIGH',
                    'description': f"Arc {arc_key} exists in generated deck but not specified in template"
                })
                continue

            # Check for unspecified behaviors
            unspecified_behaviors = []

            # Final-state checks
            if deck_behavior.get('has_final_state', False):
                if not self._has_final_state_specification(template_arc):
                    unspecified_behaviors.append({
                        'behavior': 'final_state_checks',
                        'description': f"Final-state measurements present but not specified",
                        'count': deck_behavior.get('num_final_state_meas', 0),
                        'eda_impact': 'Cannot reproduce - no EDA tool support for final-state metrics'
                    })

            # CP2Q_DEL2 measurements
            if deck_behavior.get('has_cp2q_del2', False):
                if not self._has_cp2q_del2_specification(template_arc):
                    unspecified_behaviors.append({
                        'behavior': 'cp2q_del2_monitoring',
                        'description': f"Second monitoring cycle present but not specified",
                        'eda_impact': 'Unclear how EDA tools should determine when to add cp2q_del2'
                    })

            # Internal node measurements
            if deck_behavior.get('uses_internal_nodes', False):
                if not self._has_internal_node_specification(template_arc):
                    unspecified_behaviors.append({
                        'behavior': 'internal_node_probing',
                        'description': f"Internal nodes measured but not specified",
                        'nodes': deck_behavior.get('internal_nodes_measured', []),
                        'eda_impact': 'EDA tools cannot determine when to probe internal vs output nodes'
                    })

            # Post-processing behaviors
            if deck_behavior.get('post_processors_detected'):
                for processor in deck_behavior['post_processors_detected']:
                    if not self._has_post_processor_specification(template_arc, processor):
                        unspecified_behaviors.append({
                            'behavior': f'post_processing_{processor}',
                            'description': f"Post-processor {processor} applied but not specified",
                            'eda_impact': f'EDA tools have no specification for {processor} logic'
                        })

            if unspecified_behaviors:
                self.gaps['missing_specifications'].append({
                    'type': 'UNSPECIFIED_BEHAVIORS',
                    'arc_key': arc_key,
                    'template_arc': template_arc,
                    'unspecified_behaviors': unspecified_behaviors,
                    'severity': 'CRITICAL' if any(b['behavior'] == 'final_state_checks' for b in unspecified_behaviors) else 'HIGH',
                    'description': f"Arc {arc_key} has {len(unspecified_behaviors)} unspecified behaviors"
                })

    def _find_missing_implementations(self):
        """Find specifications in template that are not implemented in decks."""
        if self.verbose:
            print("  Finding missing implementations...")

        for arc_key, template_arc in self.template_arcs.items():
            deck_behavior = self.deck_behaviors.get(arc_key)

            if not deck_behavior:
                # Arc specified in template but no corresponding deck found
                self.gaps['missing_implementations'].append({
                    'type': 'MISSING_DECK_IMPLEMENTATION',
                    'arc_key': arc_key,
                    'template_arc': template_arc,
                    'severity': 'MEDIUM',
                    'description': f"Arc {arc_key} specified in template but no deck found"
                })
                continue

            # Check for specified but unimplemented features
            missing_implementations = []

            # Check if timing_type is implemented
            if template_arc.get('timing_type') == 'min_pulse_width':
                if deck_behavior.get('arc_type') != 'mpw' and deck_behavior.get('arc_type') != 'min_pulse_width':
                    missing_implementations.append({
                        'specification': 'timing_type: min_pulse_width',
                        'expected': 'MPW measurements',
                        'actual': f"Arc type: {deck_behavior.get('arc_type')}",
                        'severity': 'HIGH'
                    })

            # Check constraint implementations
            if template_arc.get('rise_constraint') or template_arc.get('fall_constraint'):
                if not deck_behavior.get('has_cp2q_del1', False):
                    missing_implementations.append({
                        'specification': 'rise/fall constraints',
                        'expected': 'Constraint measurements',
                        'actual': 'No constraint measurements found',
                        'severity': 'MEDIUM'
                    })

            if missing_implementations:
                self.gaps['missing_implementations'].append({
                    'type': 'UNIMPLEMENTED_SPECIFICATIONS',
                    'arc_key': arc_key,
                    'template_arc': template_arc,
                    'missing_implementations': missing_implementations,
                    'severity': 'MEDIUM',
                    'description': f"Arc {arc_key} has {len(missing_implementations)} unimplemented specifications"
                })

    def _find_ambiguous_mappings(self):
        """Find unclear mappings between specifications and implementations."""
        if self.verbose:
            print("  Finding ambiguous mappings...")

        # Group arcs by cell patterns to find inconsistencies
        cell_patterns = defaultdict(list)
        for arc_key, deck_behavior in self.deck_behaviors.items():
            cell_name = deck_behavior['cell_name']
            # Create cell pattern groups
            if 'SYNC' in cell_name:
                cell_patterns['SYNC_cells'].append((arc_key, deck_behavior))
            elif 'ASYNC' in cell_name:
                cell_patterns['ASYNC_cells'].append((arc_key, deck_behavior))
            elif 'ICG' in cell_name:
                cell_patterns['ICG_cells'].append((arc_key, deck_behavior))
            else:
                cell_patterns['OTHER_cells'].append((arc_key, deck_behavior))

        # Check for inconsistent behavior within patterns
        for pattern_name, arcs in cell_patterns.items():
            if len(arcs) < 2:
                continue

            # Check final-state consistency
            fs_behaviors = [deck['has_final_state'] for _, deck in arcs]
            if len(set(fs_behaviors)) > 1:  # Inconsistent behavior
                fs_true_count = sum(fs_behaviors)
                fs_false_count = len(fs_behaviors) - fs_true_count

                self.gaps['ambiguous_mappings'].append({
                    'type': 'INCONSISTENT_PATTERN_BEHAVIOR',
                    'pattern': pattern_name,
                    'behavior': 'final_state',
                    'inconsistency': f"{fs_true_count} arcs have final-state, {fs_false_count} do not",
                    'sample_arcs': [arc_key for arc_key, _ in arcs[:5]],
                    'severity': 'HIGH',
                    'description': f"Cells matching pattern {pattern_name} show inconsistent final-state behavior",
                    'eda_impact': 'EDA tools cannot predict behavior from cell name pattern alone'
                })

            # Check cp2q_del2 consistency
            del2_behaviors = [deck['has_cp2q_del2'] for _, deck in arcs]
            if len(set(del2_behaviors)) > 1:
                del2_true_count = sum(del2_behaviors)
                del2_false_count = len(del2_behaviors) - del2_true_count

                self.gaps['ambiguous_mappings'].append({
                    'type': 'INCONSISTENT_PATTERN_BEHAVIOR',
                    'pattern': pattern_name,
                    'behavior': 'cp2q_del2',
                    'inconsistency': f"{del2_true_count} arcs have cp2q_del2, {del2_false_count} do not",
                    'sample_arcs': [arc_key for arc_key, _ in arcs[:5]],
                    'severity': 'MEDIUM',
                    'description': f"Cells matching pattern {pattern_name} show inconsistent cp2q_del2 behavior"
                })

    def _detect_hidden_logic(self):
        """Detect logic that exists only in Python code, not in specifications."""
        if self.verbose:
            print("  Detecting hidden logic...")

        # Analyze patterns that indicate hardcoded logic
        post_processor_usage = Counter()
        threshold_patterns = Counter()
        measurement_time_patterns = Counter()

        for arc_key, deck_behavior in self.deck_behaviors.items():
            # Post-processor patterns
            for processor in deck_behavior.get('post_processors_detected', []):
                post_processor_usage[processor] += 1

            # Threshold patterns
            for threshold in deck_behavior.get('threshold_values', []):
                threshold_patterns[threshold] += 1

            # Measurement time patterns
            if deck_behavior.get('measurement_time'):
                measurement_time_patterns[deck_behavior['measurement_time']] += 1

        # Detect hidden logic from post-processor usage
        for processor, count in post_processor_usage.items():
            percentage = (count / len(self.deck_behaviors)) * 100
            self.gaps['hidden_logic_detected'].append({
                'type': 'POST_PROCESSOR_LOGIC',
                'processor': processor,
                'usage_count': count,
                'usage_percentage': percentage,
                'description': f"Post-processor {processor} used in {count} arcs ({percentage:.1f}%) but not specified",
                'hidden_in': 'Python post-processing chain',
                'eda_impact': f'EDA tools have no access to {processor} logic'
            })

        # Detect hardcoded thresholds
        for threshold, count in threshold_patterns.most_common(5):
            percentage = (count / len(self.deck_behaviors)) * 100
            if count > 10:  # Significant usage
                self.gaps['hidden_logic_detected'].append({
                    'type': 'HARDCODED_THRESHOLD',
                    'threshold': threshold,
                    'usage_count': count,
                    'usage_percentage': percentage,
                    'description': f"Threshold {threshold} used in {count} arcs but not configurable",
                    'hidden_in': 'Python final-state logic',
                    'eda_impact': 'EDA tools cannot reproduce threshold logic'
                })

        # Detect hardcoded measurement times
        for time, count in measurement_time_patterns.items():
            if time and count > 10:
                percentage = (count / len(self.deck_behaviors)) * 100
                self.gaps['hidden_logic_detected'].append({
                    'type': 'HARDCODED_TIMING',
                    'measurement_time': time,
                    'usage_count': count,
                    'usage_percentage': percentage,
                    'description': f"Measurement time {time} used in {count} arcs but not specified",
                    'hidden_in': 'Python measurement logic',
                    'eda_impact': 'EDA tools may use different default timing'
                })

    def _analyze_eda_tool_gaps(self):
        """Analyze gaps that prevent EDA tool compatibility."""
        if self.verbose:
            print("  Analyzing EDA tool compatibility gaps...")

        # Critical gaps for EDA tools
        final_state_count = sum(1 for deck in self.deck_behaviors.values()
                               if deck.get('has_final_state', False))
        final_state_percentage = (final_state_count / len(self.deck_behaviors)) * 100

        self.gaps['eda_tool_gaps'].append({
            'gap_type': 'FINAL_STATE_SPECIFICATION',
            'severity': 'CRITICAL',
            'affected_arcs': final_state_count,
            'affected_percentage': final_state_percentage,
            'description': f"{final_state_count} arcs ({final_state_percentage:.1f}%) have final-state checks with no specification",
            'eda_impact': 'CDNS Liberate and SiliconSmart cannot reproduce final-state logic',
            'specification_needed': 'define_arc -metrics final_state (not currently supported)',
            'workaround': 'Post-processing script or custom template extension needed'
        })

        # CP2Q_DEL2 gap
        del2_count = sum(1 for deck in self.deck_behaviors.values()
                        if deck.get('has_cp2q_del2', False))
        del2_percentage = (del2_count / len(self.deck_behaviors)) * 100

        if del2_count > 0:
            self.gaps['eda_tool_gaps'].append({
                'gap_type': 'CP2Q_DEL2_SPECIFICATION',
                'severity': 'HIGH',
                'affected_arcs': del2_count,
                'affected_percentage': del2_percentage,
                'description': f"{del2_count} arcs ({del2_percentage:.1f}%) have cp2q_del2 measurements with unclear specification",
                'eda_impact': 'EDA tools cannot determine when to add second monitoring cycle',
                'specification_needed': 'Clear criteria for cp2q_del2 in template or configuration',
                'workaround': 'Pattern-based post-processing or template modification'
            })

        # Internal node gap
        internal_count = sum(1 for deck in self.deck_behaviors.values()
                           if deck.get('uses_internal_nodes', False))
        internal_percentage = (internal_count / len(self.deck_behaviors)) * 100

        if internal_count > 0:
            self.gaps['eda_tool_gaps'].append({
                'gap_type': 'INTERNAL_NODE_SPECIFICATION',
                'severity': 'MEDIUM',
                'affected_arcs': internal_count,
                'affected_percentage': internal_percentage,
                'description': f"{internal_count} arcs ({internal_percentage:.1f}%) measure internal nodes without specification",
                'eda_impact': 'EDA tools may probe wrong nodes, affecting measurement accuracy',
                'specification_needed': 'Node specification in template or configuration',
                'workaround': 'Manual template modification or measurement node override'
            })

    def _has_final_state_specification(self, template_arc: Dict) -> bool:
        """Check if template arc has final-state specification."""
        # Currently, no template.tcl format supports final-state specification
        return False

    def _has_cp2q_del2_specification(self, template_arc: Dict) -> bool:
        """Check if template arc has cp2q_del2 specification."""
        # Currently, no clear specification for cp2q_del2 in template format
        return False

    def _has_internal_node_specification(self, template_arc: Dict) -> bool:
        """Check if template arc specifies internal node measurement."""
        # Currently, no template format specifies which nodes to measure
        return False

    def _has_post_processor_specification(self, template_arc: Dict, processor: str) -> bool:
        """Check if template arc specifies post-processor behavior."""
        # Currently, no template format specifies post-processing behavior
        return False

    def _extract_deck_behaviors(self, deck_behavior: Dict) -> Dict[str, Any]:
        """Extract key behaviors from deck analysis."""
        return {
            'has_final_state': deck_behavior.get('has_final_state', False),
            'has_cp2q_del2': deck_behavior.get('has_cp2q_del2', False),
            'uses_internal_nodes': deck_behavior.get('uses_internal_nodes', False),
            'measurement_profile': deck_behavior.get('measurement_profile'),
            'post_processors': deck_behavior.get('post_processors_detected', []),
            'complexity_score': deck_behavior.get('complexity_score', 0)
        }

    def _generate_statistics(self):
        """Generate comprehensive statistics about gaps."""
        total_arcs = len(self.deck_behaviors)
        total_template_arcs = len(self.template_arcs)

        self.statistics = {
            'total_analyzed_arcs': total_arcs,
            'total_template_arcs': total_template_arcs,
            'gap_summary': {
                'missing_specifications': len(self.gaps['missing_specifications']),
                'missing_implementations': len(self.gaps['missing_implementations']),
                'ambiguous_mappings': len(self.gaps['ambiguous_mappings']),
                'hidden_logic_instances': len(self.gaps['hidden_logic_detected']),
                'eda_tool_gaps': len(self.gaps['eda_tool_gaps'])
            },
            'critical_issues': {
                'final_state_gap': sum(1 for deck in self.deck_behaviors.values()
                                     if deck.get('has_final_state', False)),
                'cp2q_del2_gap': sum(1 for deck in self.deck_behaviors.values()
                                   if deck.get('has_cp2q_del2', False)),
                'post_processor_gap': sum(1 for deck in self.deck_behaviors.values()
                                        if deck.get('post_processors_detected'))
            }
        }

        # Calculate percentages
        if total_arcs > 0:
            self.statistics['critical_percentages'] = {
                'final_state_gap_percentage': (self.statistics['critical_issues']['final_state_gap'] / total_arcs) * 100,
                'cp2q_del2_gap_percentage': (self.statistics['critical_issues']['cp2q_del2_gap'] / total_arcs) * 100,
                'post_processor_gap_percentage': (self.statistics['critical_issues']['post_processor_gap'] / total_arcs) * 100
            }

    def _compile_results(self) -> Dict[str, Any]:
        """Compile all results into a comprehensive report."""
        return {
            'analysis_metadata': {
                'template_file_analyzed': True,
                'deck_analysis_loaded': len(self.deck_behaviors) > 0,
                'template_attributes_found': list(self.template_attributes),
                'analysis_date': str(Path(__file__).stat().st_mtime)
            },
            'template_summary': {
                'cells_found': len(self.template_cells),
                'arcs_found': len(self.template_arcs),
                'attributes_found': list(self.template_attributes)
            },
            'gap_analysis': self.gaps,
            'statistics': self.statistics,
            'recommendations': self._generate_recommendations()
        }

    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on gap analysis."""
        recommendations = []

        # Critical gaps
        fs_gap_pct = self.statistics.get('critical_percentages', {}).get('final_state_gap_percentage', 0)
        if fs_gap_pct > 50:
            recommendations.append(
                f"CRITICAL: {fs_gap_pct:.1f}% of arcs have final-state checks with no specification. "
                f"Add final-state specification to template format or create configuration files."
            )

        del2_gap_pct = self.statistics.get('critical_percentages', {}).get('cp2q_del2_gap_percentage', 0)
        if del2_gap_pct > 10:
            recommendations.append(
                f"HIGH: {del2_gap_pct:.1f}% of arcs have cp2q_del2 measurements with unclear specification. "
                f"Document criteria for when cp2q_del2 is needed."
            )

        # EDA tool compatibility
        eda_gaps = len(self.gaps['eda_tool_gaps'])
        if eda_gaps > 0:
            recommendations.append(
                f"EDA COMPATIBILITY: {eda_gaps} gap types prevent EDA tool reproduction. "
                f"Create specification extensions or post-processing scripts."
            )

        # Hidden logic
        hidden_logic_count = len(self.gaps['hidden_logic_detected'])
        if hidden_logic_count > 5:
            recommendations.append(
                f"MAINTENANCE: {hidden_logic_count} instances of hidden logic found. "
                f"Externalize hardcoded values to configuration files."
            )

        return recommendations

    def write_results(self, output_file: Path, results: Dict[str, Any]):
        """Write results to JSON file."""
        try:
            with open(output_file, 'w') as f:
                json.dump(results, f, indent=2, default=str)

            if self.verbose:
                print(f"Gap analysis results written to: {output_file}")

        except Exception as e:
            print(f"Error writing results: {e}")

    def write_human_readable_report(self, output_file: Path, results: Dict[str, Any]):
        """Write a human-readable gap analysis report."""
        try:
            with open(output_file, 'w') as f:
                f.write("MCQC Specification Completeness Gap Analysis\n")
                f.write("=" * 50 + "\n\n")

                # Summary
                stats = results['statistics']
                f.write(f"Analysis Summary:\n")
                f.write(f"  Template arcs: {stats['total_template_arcs']}\n")
                f.write(f"  Generated arcs: {stats['total_analyzed_arcs']}\n")
                f.write(f"  Gap categories: {len(results['gap_analysis'])}\n\n")

                # Critical issues
                if 'critical_percentages' in stats:
                    f.write("Critical Gaps:\n")
                    crit = stats['critical_percentages']
                    f.write(f"  Final-state gaps: {crit['final_state_gap_percentage']:.1f}% of arcs\n")
                    f.write(f"  CP2Q_DEL2 gaps: {crit['cp2q_del2_gap_percentage']:.1f}% of arcs\n")
                    f.write(f"  Post-processor gaps: {crit['post_processor_gap_percentage']:.1f}% of arcs\n\n")

                # EDA tool gaps
                f.write("EDA Tool Compatibility Gaps:\n")
                for gap in results['gap_analysis']['eda_tool_gaps']:
                    f.write(f"  {gap['gap_type']}: {gap['affected_percentage']:.1f}% of arcs\n")
                    f.write(f"    Impact: {gap['eda_impact']}\n")
                    f.write(f"    Needed: {gap['specification_needed']}\n")
                f.write("\n")

                # Recommendations
                f.write("Recommendations:\n")
                for rec in results['recommendations']:
                    f.write(f"  • {rec}\n")

            if self.verbose:
                print(f"Human-readable report written to: {output_file}")

        except Exception as e:
            print(f"Error writing human-readable report: {e}")


def main():
    """Main function with command line interface."""
    parser = argparse.ArgumentParser(
        description='Analyze gaps between template specifications and SPICE deck implementations',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --template_file template.tcl --analysis_csv deck_analysis.csv --output gaps.json
  %(prog)s --template_file template.tcl --analysis_csv analysis.csv --output gaps.json --verbose
        """
    )

    parser.add_argument('--template_file', type=Path, required=True,
                        help='Template*.tcl file with arc specifications')
    parser.add_argument('--analysis_csv', type=Path, required=True,
                        help='CSV file from validate_deck_structure.py analysis')
    parser.add_argument('--output', type=Path, required=True,
                        help='Output JSON file for gap analysis results')
    parser.add_argument('--human_report', type=Path,
                        help='Optional human-readable summary report file')
    parser.add_argument('--verbose', action='store_true',
                        help='Enable verbose output')

    args = parser.parse_args()

    try:
        if not args.template_file.exists():
            print(f"Error: Template file not found: {args.template_file}")
            return 1

        if not args.analysis_csv.exists():
            print(f"Error: Analysis CSV file not found: {args.analysis_csv}")
            return 1

        # Run gap analysis
        analyzer = SpecificationGapAnalyzer(verbose=args.verbose)

        if not analyzer.load_template_specification(args.template_file):
            print("Error: Failed to load template specification")
            return 1

        if not analyzer.load_deck_analysis(args.analysis_csv):
            print("Error: Failed to load deck analysis")
            return 1

        results = analyzer.analyze_gaps()

        # Write results
        analyzer.write_results(args.output, results)

        # Write human-readable report if requested
        if args.human_report:
            analyzer.write_human_readable_report(args.human_report, results)

        # Print summary
        print(f"\nGap Analysis Summary:")
        print(f"  Missing specifications: {len(results['gap_analysis']['missing_specifications'])}")
        print(f"  EDA tool gaps: {len(results['gap_analysis']['eda_tool_gaps'])}")
        print(f"  Hidden logic instances: {len(results['gap_analysis']['hidden_logic_detected'])}")

        return 0

    except Exception as e:
        print(f"Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())