#!/usr/bin/env python3
"""
SPICE Deck Structure Validator

Analyzes generated SPICE decks to identify patterns and validate completeness.
This tool discovers the actual behavior patterns in MCQC-generated decks.

Usage:
    python validate_deck_structure.py --deck_dir /path/to/DECKS/ --output report.csv
    python validate_deck_structure.py --deck_dir /path/to/DECKS/ --output report.csv --verbose
    python validate_deck_structure.py --single_deck /path/to/nominal_sim.sp --output single_analysis.json

Example:
    python validate_deck_structure.py --deck_dir /work/MCQC_RUN/DECKS/ --output deck_analysis.csv

Author: MCQC Validation Team
Date: October 2025
"""

import os
import re
import csv
import json
import argparse
import sys
from pathlib import Path
from collections import defaultdict, Counter
from typing import Dict, List, Any, Optional

class DeckAnalyzer:
    """Analyzes a single SPICE deck to extract all patterns and characteristics."""

    def __init__(self):
        self.reset_patterns()

    def reset_patterns(self):
        """Reset analysis patterns for a new deck."""
        self.patterns = {
            # Basic measurements
            'has_final_state': False,
            'num_final_state_meas': 0,
            'num_final_state_check_meas': 0,
            'has_cp2q_del1': False,
            'has_cp2q_del2': False,
            'has_glitch_check': False,

            # Node analysis
            'measurement_nodes': [],
            'output_pins_measured': [],
            'internal_nodes_measured': [],
            'uses_internal_nodes': False,

            # Template and processing info
            'template_used': None,
            'template_type': None,
            'post_processors_detected': [],

            # Measurement characteristics
            'measurement_time': None,
            'threshold_values': [],
            'measurement_types': [],

            # Vector and condition analysis
            'vector_detected': None,
            'when_condition': None,
            'probe_pin_types': [],

            # File characteristics
            'file_size': 0,
            'line_count': 0,
            'error_indicators': []
        }

    def analyze_deck(self, deck_file: Path) -> Dict[str, Any]:
        """
        Extract all patterns from a single SPICE deck.

        Args:
            deck_file: Path to the SPICE deck file

        Returns:
            Dictionary containing all discovered patterns
        """
        self.reset_patterns()

        if not deck_file.exists():
            self.patterns['error_indicators'].append(f"File not found: {deck_file}")
            return self.patterns

        try:
            with open(deck_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except Exception as e:
            self.patterns['error_indicators'].append(f"Read error: {str(e)}")
            return self.patterns

        # Basic file characteristics
        self.patterns['file_size'] = len(content)
        self.patterns['line_count'] = content.count('\n')

        # Analyze content
        self._analyze_measurements(content)
        self._analyze_nodes(content)
        self._analyze_template_info(content)
        self._analyze_conditions(content)
        self._analyze_post_processing(content)
        self._detect_errors(content)

        return self.patterns.copy()

    def _analyze_measurements(self, content: str):
        """Analyze all measurement statements in the deck."""
        lines = content.split('\n')

        for line in lines:
            line = line.strip()

            # Final-state measurements
            if line.startswith('.meas') and 'final_state' in line:
                self.patterns['has_final_state'] = True
                if 'final_state_check' in line:
                    self.patterns['num_final_state_check_meas'] += 1
                else:
                    self.patterns['num_final_state_meas'] += 1

                # Extract threshold values from final_state_check
                threshold_match = re.search(r'(< |> )([0-9.]+)', line)
                if threshold_match:
                    operator = threshold_match.group(1).strip()
                    value = float(threshold_match.group(2))
                    self.patterns['threshold_values'].append(f"{operator}{value}")

            # CP2Q delay measurements
            if line.startswith('.meas') and 'cp2q_del1' in line:
                self.patterns['has_cp2q_del1'] = True
                self.patterns['measurement_types'].append('cp2q_del1')

            if line.startswith('.meas') and 'cp2q_del2' in line:
                self.patterns['has_cp2q_del2'] = True
                self.patterns['measurement_types'].append('cp2q_del2')

            # Glitch measurements
            if line.startswith('.meas') and 'glitch' in line:
                self.patterns['has_glitch_check'] = True
                self.patterns['measurement_types'].append('glitch')

            # Extract measurement time
            time_match = re.search(r'at=([0-9.]+[a-zA-Z]*)', line)
            if time_match and not self.patterns['measurement_time']:
                self.patterns['measurement_time'] = time_match.group(1)

    def _analyze_nodes(self, content: str):
        """Analyze nodes being measured."""
        # Find all measurement node references
        meas_pattern = r'\.meas\s+\w+\s+.*?v\(([^)]+)\)'
        nodes = re.findall(meas_pattern, content, re.IGNORECASE)

        self.patterns['measurement_nodes'] = list(set(nodes))  # Remove duplicates

        # Classify nodes
        for node in self.patterns['measurement_nodes']:
            if '.' in node:
                # Internal node (e.g., X1.Q1)
                self.patterns['internal_nodes_measured'].append(node)
                self.patterns['uses_internal_nodes'] = True
            else:
                # Output pin (e.g., Q, QN)
                self.patterns['output_pins_measured'].append(node)

            # Classify probe pin types
            if 'Q' in node.upper() and 'QN' not in node.upper():
                self.patterns['probe_pin_types'].append('Q')
            elif 'QN' in node.upper():
                self.patterns['probe_pin_types'].append('QN')
            elif any(pin in node.upper() for pin in ['OUT', 'Y', 'Z']):
                self.patterns['probe_pin_types'].append('OUTPUT')
            else:
                self.patterns['probe_pin_types'].append('OTHER')

    def _analyze_template_info(self, content: str):
        """Extract template and path information."""
        lines = content.split('\n')

        for line in lines:
            # Template deck path
            if 'TEMPLATE_DECK_PATH' in line:
                template_match = re.search(r'TEMPLATE_DECK_PATH\s+(\S+)', line)
                if template_match:
                    self.patterns['template_used'] = template_match.group(1)

                    # Classify template type
                    template_path = self.patterns['template_used']
                    if '_AMD_' in template_path:
                        self.patterns['template_type'] = 'AMD'
                    elif 'sync2' in template_path.lower():
                        self.patterns['template_type'] = 'SYNC2'
                    elif 'async' in template_path.lower():
                        self.patterns['template_type'] = 'ASYNC'
                    elif 'icg' in template_path.lower():
                        self.patterns['template_type'] = 'ICG'
                    else:
                        self.patterns['template_type'] = 'OTHER'
                break

    def _analyze_conditions(self, content: str):
        """Analyze when conditions and vector information."""
        lines = content.split('\n')

        for line in lines:
            # Vector information
            if 'VECTOR' in line:
                vector_match = re.search(r'VECTOR\s+(\S+)', line)
                if vector_match:
                    self.patterns['vector_detected'] = vector_match.group(1)

            # When conditions
            if 'WHEN' in line:
                when_match = re.search(r'WHEN\s+(.+)', line)
                if when_match:
                    self.patterns['when_condition'] = when_match.group(1).strip()

    def _analyze_post_processing(self, content: str):
        """Detect evidence of post-processing modifications."""
        # Look for signatures of different post-processors

        # ICG post-processor signature
        if ('icg' in content.lower() and
            self.patterns['has_final_state'] and
            '> 0.95' in content):
            self.patterns['post_processors_detected'].append('post_icg_ov')

        # MB_AN2 post-processor signature
        if ('mb' in content.lower() and 'an2' in content.lower()):
            self.patterns['post_processors_detected'].append('post_mb_an2')

        # AMD post-processor signature
        if ('_AMD_' in content and
            self.patterns['num_final_state_meas'] > 1):
            self.patterns['post_processors_detected'].append('post_final_state')

        # SE/SA/C embedded logic signature
        if (self.patterns['when_condition'] and
            any(cond in self.patterns['when_condition']
                for cond in ['SE', '!SA', 'C'])):
            self.patterns['post_processors_detected'].append('embedded_SE_SA_C')

        # Vector-based logic signature
        if (self.patterns['vector_detected'] and
            self.patterns['has_final_state'] and
            any(ptype in ['Q', 'QN'] for ptype in self.patterns['probe_pin_types'])):
            self.patterns['post_processors_detected'].append('embedded_Q_QN_vector')

    def _detect_errors(self, content: str):
        """Detect potential errors or issues in the deck."""
        # Check for incomplete measurements
        if '.meas final_state ' in content and '.meas final_state_check ' not in content:
            self.patterns['error_indicators'].append('Final state without check')

        # Check for syntax issues
        if content.count('.meas') != content.count('\n.meas') + content.startswith('.meas'):
            # This is a rough check for malformed .meas statements
            pass  # Could add more sophisticated syntax checking


class DeckCollectionAnalyzer:
    """Analyzes a collection of SPICE decks to discover patterns."""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.analyzer = DeckAnalyzer()
        self.results = []
        self.statistics = {}

    def analyze_deck_directory(self, deck_root_dir: Path) -> List[Dict[str, Any]]:
        """
        Analyze all decks in a directory structure.

        Args:
            deck_root_dir: Root directory containing arc folders with decks

        Returns:
            List of analysis results for all decks
        """
        if self.verbose:
            print(f"Analyzing decks in: {deck_root_dir}")

        self.results = []
        deck_count = 0

        # Find all nominal_sim.sp files
        for deck_path in deck_root_dir.glob("**/nominal_sim.sp"):
            deck_count += 1
            if self.verbose and deck_count % 100 == 0:
                print(f"Processed {deck_count} decks...")

            # Analyze individual deck
            deck_info = self.analyzer.analyze_deck(deck_path)

            # Extract arc information from path
            arc_folder = deck_path.parent.name
            result = self._extract_arc_info(arc_folder, deck_path, deck_info)

            self.results.append(result)

        if self.verbose:
            print(f"Completed analysis of {deck_count} decks")

        # Generate statistics
        self._generate_statistics()

        return self.results

    def _extract_arc_info(self, arc_folder: str, deck_path: Path, deck_info: Dict) -> Dict[str, Any]:
        """Extract arc information from folder name and combine with deck analysis."""
        # Parse arc folder name
        # Format: arctype_cell_pin_dir_relpin_reldir_when_tablepoint_vector
        parts = arc_folder.split('_')

        result = {
            # Arc identification
            'arc_folder': arc_folder,
            'deck_path': str(deck_path),
            'cell_name': parts[1] if len(parts) > 1 else 'UNKNOWN',
            'arc_type': parts[0] if len(parts) > 0 else 'UNKNOWN',
            'pin': parts[2] if len(parts) > 2 else 'UNKNOWN',
            'related_pin': parts[4] if len(parts) > 4 else 'UNKNOWN',

            # Add all deck analysis results
            **deck_info
        }

        # Additional derived fields
        result['measurement_profile'] = self._classify_measurement_profile(deck_info)
        result['complexity_score'] = self._calculate_complexity_score(deck_info)

        return result

    def _classify_measurement_profile(self, deck_info: Dict) -> str:
        """Classify the measurement profile of a deck."""
        has_fs = deck_info['has_final_state']
        has_del2 = deck_info['has_cp2q_del2']
        has_del1 = deck_info['has_cp2q_del1']

        if has_fs and has_del2:
            return 'FULL_MONITORING'  # Final-state + dual delay
        elif has_fs and has_del1:
            return 'FINAL_STATE_SINGLE'  # Final-state + single delay
        elif has_del2 and has_del1:
            return 'DUAL_DELAY_ONLY'  # Dual delay without final-state
        elif has_del1:
            return 'BASIC_DELAY'  # Basic delay only
        else:
            return 'MINIMAL'  # Very basic or error case

    def _calculate_complexity_score(self, deck_info: Dict) -> int:
        """Calculate a complexity score for the deck."""
        score = 0

        # Base measurements
        score += deck_info['num_final_state_meas'] * 2
        score += deck_info['num_final_state_check_meas'] * 2
        score += len(deck_info['measurement_types'])

        # Node complexity
        score += len(deck_info['internal_nodes_measured']) * 3
        score += len(deck_info['output_pins_measured'])

        # Processing complexity
        score += len(deck_info['post_processors_detected']) * 2

        # Error penalty
        score -= len(deck_info['error_indicators']) * 5

        return max(0, score)

    def _generate_statistics(self):
        """Generate comprehensive statistics from all analyzed decks."""
        if not self.results:
            return

        total_decks = len(self.results)

        self.statistics = {
            'total_decks': total_decks,
            'final_state_coverage': {
                'count': sum(1 for r in self.results if r['has_final_state']),
                'percentage': 0
            },
            'cp2q_del2_coverage': {
                'count': sum(1 for r in self.results if r['has_cp2q_del2']),
                'percentage': 0
            },
            'measurement_profiles': Counter(r['measurement_profile'] for r in self.results),
            'template_types': Counter(r['template_type'] for r in self.results if r['template_type']),
            'post_processors': Counter(),
            'complexity_distribution': {},
            'error_summary': Counter()
        }

        # Calculate percentages
        fs_count = self.statistics['final_state_coverage']['count']
        del2_count = self.statistics['cp2q_del2_coverage']['count']

        self.statistics['final_state_coverage']['percentage'] = (fs_count / total_decks) * 100
        self.statistics['cp2q_del2_coverage']['percentage'] = (del2_count / total_decks) * 100

        # Post-processor statistics
        for result in self.results:
            for processor in result['post_processors_detected']:
                self.statistics['post_processors'][processor] += 1

        # Complexity distribution
        complexity_scores = [r['complexity_score'] for r in self.results]
        if complexity_scores:
            self.statistics['complexity_distribution'] = {
                'min': min(complexity_scores),
                'max': max(complexity_scores),
                'average': sum(complexity_scores) / len(complexity_scores)
            }

        # Error summary
        for result in self.results:
            for error in result['error_indicators']:
                self.statistics['error_summary'][error] += 1

    def write_csv_report(self, output_file: Path):
        """Write detailed CSV report of all deck analyses."""
        if not self.results:
            print("No results to write")
            return

        # Define CSV columns
        columns = [
            'arc_folder', 'cell_name', 'arc_type', 'pin', 'related_pin',
            'has_final_state', 'num_final_state_meas', 'num_final_state_check_meas',
            'has_cp2q_del1', 'has_cp2q_del2', 'has_glitch_check',
            'measurement_profile', 'complexity_score',
            'uses_internal_nodes', 'measurement_nodes', 'output_pins_measured', 'internal_nodes_measured',
            'template_used', 'template_type', 'measurement_time',
            'threshold_values', 'vector_detected', 'when_condition',
            'post_processors_detected', 'error_indicators',
            'file_size', 'line_count'
        ]

        try:
            with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=columns)
                writer.writeheader()

                for result in self.results:
                    # Convert lists to strings for CSV
                    csv_row = result.copy()
                    for key, value in csv_row.items():
                        if isinstance(value, list):
                            csv_row[key] = ';'.join(map(str, value))

                    writer.writerow(csv_row)

            print(f"CSV report written to: {output_file}")

        except Exception as e:
            print(f"Error writing CSV report: {e}")

    def write_statistics_report(self, output_file: Path):
        """Write human-readable statistics report."""
        try:
            with open(output_file, 'w') as f:
                f.write("MCQC SPICE Deck Analysis Statistics\n")
                f.write("=" * 50 + "\n\n")

                f.write(f"Total Decks Analyzed: {self.statistics['total_decks']}\n\n")

                # Coverage statistics
                fs_pct = self.statistics['final_state_coverage']['percentage']
                fs_count = self.statistics['final_state_coverage']['count']
                f.write(f"Final-State Coverage: {fs_count} decks ({fs_pct:.1f}%)\n")

                del2_pct = self.statistics['cp2q_del2_coverage']['percentage']
                del2_count = self.statistics['cp2q_del2_coverage']['count']
                f.write(f"CP2Q_DEL2 Coverage: {del2_count} decks ({del2_pct:.1f}%)\n\n")

                # Measurement profiles
                f.write("Measurement Profiles:\n")
                for profile, count in self.statistics['measurement_profiles'].most_common():
                    percentage = (count / self.statistics['total_decks']) * 100
                    f.write(f"  {profile}: {count} decks ({percentage:.1f}%)\n")
                f.write("\n")

                # Template types
                f.write("Template Types:\n")
                for template_type, count in self.statistics['template_types'].most_common():
                    percentage = (count / self.statistics['total_decks']) * 100
                    f.write(f"  {template_type}: {count} decks ({percentage:.1f}%)\n")
                f.write("\n")

                # Post-processors
                f.write("Post-Processors Detected:\n")
                for processor, count in self.statistics['post_processors'].most_common():
                    percentage = (count / self.statistics['total_decks']) * 100
                    f.write(f"  {processor}: {count} decks ({percentage:.1f}%)\n")
                f.write("\n")

                # Complexity
                if self.statistics['complexity_distribution']:
                    comp = self.statistics['complexity_distribution']
                    f.write(f"Complexity Distribution:\n")
                    f.write(f"  Min: {comp['min']}\n")
                    f.write(f"  Max: {comp['max']}\n")
                    f.write(f"  Average: {comp['average']:.1f}\n\n")

                # Errors
                if self.statistics['error_summary']:
                    f.write("Error Summary:\n")
                    for error, count in self.statistics['error_summary'].most_common():
                        f.write(f"  {error}: {count} decks\n")

            print(f"Statistics report written to: {output_file}")

        except Exception as e:
            print(f"Error writing statistics report: {e}")


def main():
    """Main function with command line interface."""
    parser = argparse.ArgumentParser(
        description='Analyze SPICE deck structure to discover patterns',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --deck_dir /work/MCQC_RUN/DECKS/ --output analysis.csv
  %(prog)s --deck_dir /work/MCQC_RUN/DECKS/ --output analysis.csv --verbose
  %(prog)s --single_deck /work/MCQC_RUN/DECKS/arc1/nominal_sim.sp --output single.json
        """
    )

    # Input options
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--deck_dir', type=Path,
                       help='Directory containing arc folders with SPICE decks')
    group.add_argument('--single_deck', type=Path,
                       help='Single SPICE deck file to analyze')

    # Output options
    parser.add_argument('--output', type=Path, required=True,
                        help='Output file (.csv for deck_dir, .json for single_deck)')
    parser.add_argument('--stats_output', type=Path,
                        help='Optional statistics report file (for deck_dir mode)')

    # Control options
    parser.add_argument('--verbose', action='store_true',
                        help='Enable verbose output')

    args = parser.parse_args()

    try:
        if args.single_deck:
            # Single deck analysis
            analyzer = DeckAnalyzer()
            result = analyzer.analyze_deck(args.single_deck)

            with open(args.output, 'w') as f:
                json.dump(result, f, indent=2)
            print(f"Single deck analysis written to: {args.output}")

        else:
            # Directory analysis
            if not args.deck_dir.exists():
                print(f"Error: Directory not found: {args.deck_dir}")
                return 1

            analyzer = DeckCollectionAnalyzer(verbose=args.verbose)
            results = analyzer.analyze_deck_directory(args.deck_dir)

            if not results:
                print("No SPICE decks found in directory")
                return 1

            # Write CSV report
            analyzer.write_csv_report(args.output)

            # Write statistics report
            stats_file = args.stats_output or args.output.with_suffix('.stats.txt')
            analyzer.write_statistics_report(stats_file)

            # Print key statistics
            print(f"\nKey Statistics:")
            print(f"  Total decks: {analyzer.statistics['total_decks']}")
            print(f"  Final-state coverage: {analyzer.statistics['final_state_coverage']['percentage']:.1f}%")
            print(f"  CP2Q_DEL2 coverage: {analyzer.statistics['cp2q_del2_coverage']['percentage']:.1f}%")

        return 0

    except Exception as e:
        print(f"Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())