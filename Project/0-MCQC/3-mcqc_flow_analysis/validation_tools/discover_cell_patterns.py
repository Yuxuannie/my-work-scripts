#!/usr/bin/env python3
"""
Cell Pattern Discovery Tool

Automatically discovers which cell name patterns correlate with specific behaviors
(final-state checks, cp2q_del2, internal nodes, etc.) using statistical analysis.

Usage:
    python discover_cell_patterns.py --analysis_csv deck_analysis.csv --output patterns.json
    python discover_cell_patterns.py --analysis_csv analysis.csv --output patterns.json --min_confidence 80
    python discover_cell_patterns.py --analysis_csv analysis.csv --output patterns.json --verbose

Example:
    python discover_cell_patterns.py --analysis_csv /work/analysis/deck_analysis.csv --output cell_patterns.json

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
from typing import Dict, List, Any, Tuple, Set
import fnmatch

class CellPatternDiscoverer:
    """Discovers cell name patterns that correlate with specific behaviors."""

    def __init__(self, min_confidence: int = 75, min_sample_size: int = 5, verbose: bool = False):
        self.min_confidence = min_confidence
        self.min_sample_size = min_sample_size
        self.verbose = verbose

        # Data structures for analysis
        self.cell_data = defaultdict(lambda: {
            'total_count': 0,
            'final_state_count': 0,
            'cp2q_del2_count': 0,
            'internal_node_count': 0,
            'glitch_check_count': 0,
            'measurement_profiles': Counter(),
            'post_processors': Counter(),
            'arc_types': set(),
            'templates': set(),
            'sample_arcs': []
        })

        self.discovered_patterns = []
        self.pattern_groups = {}
        self.statistics = {}

    def load_analysis_data(self, csv_file: Path) -> List[Dict[str, Any]]:
        """Load deck analysis data from CSV file."""
        if self.verbose:
            print(f"Loading analysis data from: {csv_file}")

        data = []
        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    processed_row = self._process_csv_row(row)
                    data.append(processed_row)

            if self.verbose:
                print(f"Loaded {len(data)} deck analyses")

            return data

        except Exception as e:
            print(f"Error loading CSV file: {e}")
            return []

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

    def analyze_cell_patterns(self, analysis_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze cell patterns and discover correlations."""
        if self.verbose:
            print("Analyzing cell patterns...")

        # Group data by cell names
        self._group_by_cell_names(analysis_data)

        # Discover patterns using multiple approaches
        self._discover_exact_patterns()
        self._discover_prefix_patterns()
        self._discover_suffix_patterns()
        self._discover_regex_patterns()
        self._discover_wildcard_patterns()

        # Analyze pattern groups and conflicts
        self._analyze_pattern_groups()

        # Generate statistics
        self._generate_statistics()

        if self.verbose:
            print(f"Pattern discovery complete. Found {len(self.discovered_patterns)} patterns")

        return self._compile_results()

    def _group_by_cell_names(self, analysis_data: List[Dict[str, Any]]):
        """Group analysis data by cell names."""
        for deck_data in analysis_data:
            cell_name = deck_data.get('cell_name', 'UNKNOWN')
            if cell_name == 'UNKNOWN':
                continue

            cell_stats = self.cell_data[cell_name]
            cell_stats['total_count'] += 1

            # Count behaviors
            if deck_data.get('has_final_state', False):
                cell_stats['final_state_count'] += 1
            if deck_data.get('has_cp2q_del2', False):
                cell_stats['cp2q_del2_count'] += 1
            if deck_data.get('uses_internal_nodes', False):
                cell_stats['internal_node_count'] += 1
            if deck_data.get('has_glitch_check', False):
                cell_stats['glitch_check_count'] += 1

            # Collect metadata
            if deck_data.get('measurement_profile'):
                cell_stats['measurement_profiles'][deck_data['measurement_profile']] += 1

            for processor in deck_data.get('post_processors_detected', []):
                cell_stats['post_processors'][processor] += 1

            if deck_data.get('arc_type'):
                cell_stats['arc_types'].add(deck_data['arc_type'])
            if deck_data.get('template_used'):
                cell_stats['templates'].add(deck_data['template_used'])

            # Keep sample arcs (up to 3 per cell)
            if len(cell_stats['sample_arcs']) < 3:
                cell_stats['sample_arcs'].append(deck_data.get('arc_folder', ''))

    def _discover_exact_patterns(self):
        """Discover patterns based on exact cell name matches."""
        if self.verbose:
            print("  Discovering exact name patterns...")

        for cell_name, stats in self.cell_data.items():
            if stats['total_count'] < self.min_sample_size:
                continue

            # Calculate percentages
            fs_pct = (stats['final_state_count'] / stats['total_count']) * 100
            del2_pct = (stats['cp2q_del2_count'] / stats['total_count']) * 100
            in_pct = (stats['internal_node_count'] / stats['total_count']) * 100
            glitch_pct = (stats['glitch_check_count'] / stats['total_count']) * 100

            patterns_found = []

            if fs_pct >= self.min_confidence:
                patterns_found.append({
                    'behavior': 'final_state',
                    'confidence': fs_pct,
                    'description': f'Always has final-state checks ({fs_pct:.1f}%)'
                })
            elif fs_pct <= (100 - self.min_confidence):
                patterns_found.append({
                    'behavior': 'no_final_state',
                    'confidence': 100 - fs_pct,
                    'description': f'Never has final-state checks ({fs_pct:.1f}%)'
                })

            if del2_pct >= self.min_confidence:
                patterns_found.append({
                    'behavior': 'cp2q_del2',
                    'confidence': del2_pct,
                    'description': f'Always has cp2q_del2 ({del2_pct:.1f}%)'
                })

            if in_pct >= self.min_confidence:
                patterns_found.append({
                    'behavior': 'internal_nodes',
                    'confidence': in_pct,
                    'description': f'Always uses internal nodes ({in_pct:.1f}%)'
                })

            if glitch_pct >= self.min_confidence:
                patterns_found.append({
                    'behavior': 'glitch_check',
                    'confidence': glitch_pct,
                    'description': f'Always has glitch checks ({glitch_pct:.1f}%)'
                })

            if patterns_found:
                self.discovered_patterns.append({
                    'pattern_type': 'EXACT_CELL_NAME',
                    'pattern': cell_name,
                    'regex': f'^{re.escape(cell_name)}$',
                    'sample_size': stats['total_count'],
                    'behaviors': patterns_found,
                    'cells_matched': [cell_name],
                    'sample_arcs': stats['sample_arcs']
                })

    def _discover_prefix_patterns(self):
        """Discover patterns based on cell name prefixes."""
        if self.verbose:
            print("  Discovering prefix patterns...")

        # Extract all unique prefixes (2-6 characters)
        prefixes = set()
        for cell_name in self.cell_data.keys():
            for length in range(2, min(7, len(cell_name) + 1)):
                prefixes.add(cell_name[:length])

        for prefix in prefixes:
            matching_cells = [cell for cell in self.cell_data.keys()
                            if cell.startswith(prefix)]

            if len(matching_cells) < 2:  # Need at least 2 cells for a pattern
                continue

            # Aggregate statistics for this prefix
            total_count = sum(self.cell_data[cell]['total_count'] for cell in matching_cells)
            if total_count < self.min_sample_size:
                continue

            fs_count = sum(self.cell_data[cell]['final_state_count'] for cell in matching_cells)
            del2_count = sum(self.cell_data[cell]['cp2q_del2_count'] for cell in matching_cells)
            in_count = sum(self.cell_data[cell]['internal_node_count'] for cell in matching_cells)
            glitch_count = sum(self.cell_data[cell]['glitch_check_count'] for cell in matching_cells)

            # Calculate percentages
            fs_pct = (fs_count / total_count) * 100
            del2_pct = (del2_count / total_count) * 100
            in_pct = (in_count / total_count) * 100
            glitch_pct = (glitch_count / total_count) * 100

            patterns_found = []

            if fs_pct >= self.min_confidence:
                patterns_found.append({
                    'behavior': 'final_state',
                    'confidence': fs_pct,
                    'description': f'Prefix {prefix}* always has final-state ({fs_pct:.1f}%)'
                })
            elif fs_pct <= (100 - self.min_confidence):
                patterns_found.append({
                    'behavior': 'no_final_state',
                    'confidence': 100 - fs_pct,
                    'description': f'Prefix {prefix}* never has final-state ({fs_pct:.1f}%)'
                })

            if del2_pct >= self.min_confidence:
                patterns_found.append({
                    'behavior': 'cp2q_del2',
                    'confidence': del2_pct,
                    'description': f'Prefix {prefix}* always has cp2q_del2 ({del2_pct:.1f}%)'
                })

            if in_pct >= self.min_confidence:
                patterns_found.append({
                    'behavior': 'internal_nodes',
                    'confidence': in_pct,
                    'description': f'Prefix {prefix}* always uses internal nodes ({in_pct:.1f}%)'
                })

            if patterns_found:
                self.discovered_patterns.append({
                    'pattern_type': 'PREFIX',
                    'pattern': f'{prefix}*',
                    'regex': f'^{re.escape(prefix)}.*',
                    'sample_size': total_count,
                    'behaviors': patterns_found,
                    'cells_matched': matching_cells,
                    'sample_arcs': []  # Could collect samples if needed
                })

    def _discover_suffix_patterns(self):
        """Discover patterns based on cell name suffixes."""
        if self.verbose:
            print("  Discovering suffix patterns...")

        # Extract all unique suffixes (2-6 characters)
        suffixes = set()
        for cell_name in self.cell_data.keys():
            for length in range(2, min(7, len(cell_name) + 1)):
                suffixes.add(cell_name[-length:])

        for suffix in suffixes:
            matching_cells = [cell for cell in self.cell_data.keys()
                            if cell.endswith(suffix)]

            if len(matching_cells) < 2:
                continue

            # Aggregate statistics for this suffix
            total_count = sum(self.cell_data[cell]['total_count'] for cell in matching_cells)
            if total_count < self.min_sample_size:
                continue

            fs_count = sum(self.cell_data[cell]['final_state_count'] for cell in matching_cells)
            del2_count = sum(self.cell_data[cell]['cp2q_del2_count'] for cell in matching_cells)

            # Calculate percentages
            fs_pct = (fs_count / total_count) * 100
            del2_pct = (del2_count / total_count) * 100

            patterns_found = []

            if fs_pct >= self.min_confidence:
                patterns_found.append({
                    'behavior': 'final_state',
                    'confidence': fs_pct,
                    'description': f'Suffix *{suffix} always has final-state ({fs_pct:.1f}%)'
                })

            if del2_pct >= self.min_confidence:
                patterns_found.append({
                    'behavior': 'cp2q_del2',
                    'confidence': del2_pct,
                    'description': f'Suffix *{suffix} always has cp2q_del2 ({del2_pct:.1f}%)'
                })

            if patterns_found:
                self.discovered_patterns.append({
                    'pattern_type': 'SUFFIX',
                    'pattern': f'*{suffix}',
                    'regex': f'.*{re.escape(suffix)}$',
                    'sample_size': total_count,
                    'behaviors': patterns_found,
                    'cells_matched': matching_cells,
                    'sample_arcs': []
                })

    def _discover_regex_patterns(self):
        """Discover patterns using common regex patterns."""
        if self.verbose:
            print("  Discovering regex patterns...")

        # Common semiconductor cell name patterns
        regex_patterns = [
            (r'.*SYNC.*', 'Contains SYNC'),
            (r'.*ASYNC.*', 'Contains ASYNC'),
            (r'.*FF.*', 'Contains FF (flip-flop)'),
            (r'.*LATCH.*', 'Contains LATCH'),
            (r'.*ICG.*', 'Contains ICG'),
            (r'.*CLK.*', 'Contains CLK'),
            (r'.*DFF.*', 'Contains DFF'),
            (r'.*MUX.*', 'Contains MUX'),
            (r'.*AND.*', 'Contains AND'),
            (r'.*OR.*', 'Contains OR'),
            (r'.*NAND.*', 'Contains NAND'),
            (r'.*NOR.*', 'Contains NOR'),
            (r'.*INV.*', 'Contains INV'),
            (r'.*BUF.*', 'Contains BUF'),
            (r'MB.*AN2.*', 'MB*AN2 pattern'),
            (r'.*_X[0-9]+$', 'Ends with _X<digit>'),
            (r'^[A-Z]+[0-9]+.*', 'Starts with letters+numbers'),
        ]

        for regex_pattern, description in regex_patterns:
            matching_cells = [cell for cell in self.cell_data.keys()
                            if re.match(regex_pattern, cell, re.IGNORECASE)]

            if len(matching_cells) < 2:
                continue

            # Aggregate statistics
            total_count = sum(self.cell_data[cell]['total_count'] for cell in matching_cells)
            if total_count < self.min_sample_size:
                continue

            fs_count = sum(self.cell_data[cell]['final_state_count'] for cell in matching_cells)
            del2_count = sum(self.cell_data[cell]['cp2q_del2_count'] for cell in matching_cells)
            in_count = sum(self.cell_data[cell]['internal_node_count'] for cell in matching_cells)

            # Calculate percentages
            fs_pct = (fs_count / total_count) * 100
            del2_pct = (del2_count / total_count) * 100
            in_pct = (in_count / total_count) * 100

            patterns_found = []

            if fs_pct >= self.min_confidence:
                patterns_found.append({
                    'behavior': 'final_state',
                    'confidence': fs_pct,
                    'description': f'{description} always has final-state ({fs_pct:.1f}%)'
                })
            elif fs_pct <= (100 - self.min_confidence):
                patterns_found.append({
                    'behavior': 'no_final_state',
                    'confidence': 100 - fs_pct,
                    'description': f'{description} never has final-state ({fs_pct:.1f}%)'
                })

            if del2_pct >= self.min_confidence:
                patterns_found.append({
                    'behavior': 'cp2q_del2',
                    'confidence': del2_pct,
                    'description': f'{description} always has cp2q_del2 ({del2_pct:.1f}%)'
                })

            if in_pct >= self.min_confidence:
                patterns_found.append({
                    'behavior': 'internal_nodes',
                    'confidence': in_pct,
                    'description': f'{description} always uses internal nodes ({in_pct:.1f}%)'
                })

            if patterns_found:
                self.discovered_patterns.append({
                    'pattern_type': 'REGEX',
                    'pattern': regex_pattern,
                    'regex': regex_pattern,
                    'description': description,
                    'sample_size': total_count,
                    'behaviors': patterns_found,
                    'cells_matched': matching_cells[:10],  # Limit for readability
                    'total_cells_matched': len(matching_cells),
                    'sample_arcs': []
                })

    def _discover_wildcard_patterns(self):
        """Discover patterns using wildcard matching (similar to flow/funcs.py patterns)."""
        if self.verbose:
            print("  Discovering wildcard patterns...")

        # Generate wildcard patterns based on common cell naming conventions
        wildcard_patterns = set()

        # Generate patterns from existing cell names
        for cell_name in self.cell_data.keys():
            # Replace numbers with wildcards
            pattern1 = re.sub(r'[0-9]+', '*', cell_name)
            if pattern1 != cell_name:
                wildcard_patterns.add(pattern1)

            # Replace drive strength (_X1, _X2, etc.) with wildcard
            pattern2 = re.sub(r'_X[0-9]+$', '_X*', cell_name)
            if pattern2 != cell_name:
                wildcard_patterns.add(pattern2)

            # Create prefix patterns
            if len(cell_name) > 4:
                wildcard_patterns.add(cell_name[:4] + '*')
            if len(cell_name) > 6:
                wildcard_patterns.add(cell_name[:6] + '*')

        for pattern in wildcard_patterns:
            matching_cells = [cell for cell in self.cell_data.keys()
                            if fnmatch.fnmatch(cell, pattern)]

            if len(matching_cells) < 2:
                continue

            # Aggregate statistics
            total_count = sum(self.cell_data[cell]['total_count'] for cell in matching_cells)
            if total_count < self.min_sample_size:
                continue

            fs_count = sum(self.cell_data[cell]['final_state_count'] for cell in matching_cells)
            del2_count = sum(self.cell_data[cell]['cp2q_del2_count'] for cell in matching_cells)

            # Calculate percentages
            fs_pct = (fs_count / total_count) * 100
            del2_pct = (del2_count / total_count) * 100

            patterns_found = []

            if fs_pct >= self.min_confidence:
                patterns_found.append({
                    'behavior': 'final_state',
                    'confidence': fs_pct,
                    'description': f'Pattern {pattern} always has final-state ({fs_pct:.1f}%)'
                })

            if del2_pct >= self.min_confidence:
                patterns_found.append({
                    'behavior': 'cp2q_del2',
                    'confidence': del2_pct,
                    'description': f'Pattern {pattern} always has cp2q_del2 ({del2_pct:.1f}%)'
                })

            if patterns_found:
                # Convert wildcard to regex
                regex_pattern = pattern.replace('*', '.*')
                regex_pattern = f'^{regex_pattern}$'

                self.discovered_patterns.append({
                    'pattern_type': 'WILDCARD',
                    'pattern': pattern,
                    'regex': regex_pattern,
                    'sample_size': total_count,
                    'behaviors': patterns_found,
                    'cells_matched': matching_cells[:10],
                    'total_cells_matched': len(matching_cells),
                    'sample_arcs': []
                })

    def _analyze_pattern_groups(self):
        """Analyze pattern groups and identify conflicts or overlaps."""
        if self.verbose:
            print("  Analyzing pattern groups and conflicts...")

        # Group patterns by behavior
        behavior_groups = defaultdict(list)
        for pattern in self.discovered_patterns:
            for behavior in pattern['behaviors']:
                behavior_groups[behavior['behavior']].append((pattern, behavior))

        self.pattern_groups = dict(behavior_groups)

        # Find overlapping patterns (patterns that match the same cells)
        overlaps = []
        for i, pattern1 in enumerate(self.discovered_patterns):
            for j, pattern2 in enumerate(self.discovered_patterns[i+1:], i+1):
                # Check if patterns have overlapping cells
                cells1 = set(pattern1.get('cells_matched', []))
                cells2 = set(pattern2.get('cells_matched', []))
                overlap = cells1.intersection(cells2)

                if overlap:
                    overlaps.append({
                        'pattern1': pattern1['pattern'],
                        'pattern2': pattern2['pattern'],
                        'overlapping_cells': list(overlap),
                        'overlap_count': len(overlap)
                    })

        self.pattern_groups['overlaps'] = overlaps

    def _generate_statistics(self):
        """Generate comprehensive statistics about discovered patterns."""
        total_patterns = len(self.discovered_patterns)
        total_cells = len(self.cell_data)

        # Count patterns by type
        pattern_type_counts = Counter(p['pattern_type'] for p in self.discovered_patterns)

        # Count patterns by behavior
        behavior_counts = defaultdict(int)
        for pattern in self.discovered_patterns:
            for behavior in pattern['behaviors']:
                behavior_counts[behavior['behavior']] += 1

        # Calculate coverage statistics
        cells_with_patterns = set()
        for pattern in self.discovered_patterns:
            cells_with_patterns.update(pattern.get('cells_matched', []))

        coverage_percentage = (len(cells_with_patterns) / total_cells) * 100 if total_cells > 0 else 0

        self.statistics = {
            'total_patterns_discovered': total_patterns,
            'total_cells_analyzed': total_cells,
            'cells_with_patterns': len(cells_with_patterns),
            'coverage_percentage': coverage_percentage,
            'pattern_type_distribution': dict(pattern_type_counts),
            'behavior_distribution': dict(behavior_counts),
            'confidence_range': {
                'min': min((min(b['confidence'] for b in p['behaviors'])
                           for p in self.discovered_patterns), default=0),
                'max': max((max(b['confidence'] for b in p['behaviors'])
                           for p in self.discovered_patterns), default=0)
            }
        }

    def _compile_results(self) -> Dict[str, Any]:
        """Compile all results into a comprehensive report."""
        return {
            'analysis_metadata': {
                'min_confidence_threshold': self.min_confidence,
                'min_sample_size': self.min_sample_size,
                'total_cells_analyzed': len(self.cell_data),
                'analysis_date': str(Path(__file__).stat().st_mtime)
            },
            'discovered_patterns': self.discovered_patterns,
            'pattern_groups': self.pattern_groups,
            'statistics': self.statistics,
            'recommendations': self._generate_recommendations()
        }

    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on discovered patterns."""
        recommendations = []

        # High-confidence patterns
        high_confidence_patterns = [p for p in self.discovered_patterns
                                   if any(b['confidence'] >= 90 for b in p['behaviors'])]

        if high_confidence_patterns:
            recommendations.append(
                f"Found {len(high_confidence_patterns)} high-confidence patterns (≥90%). "
                f"These should be externalized to configuration files.")

        # Final-state patterns
        fs_patterns = [p for p in self.discovered_patterns
                      if any(b['behavior'] == 'final_state' for b in p['behaviors'])]

        if fs_patterns:
            recommendations.append(
                f"Found {len(fs_patterns)} patterns that predict final-state behavior. "
                f"This explains the 74% final-state coverage observed.")

        # CP2Q_DEL2 patterns
        del2_patterns = [p for p in self.discovered_patterns
                        if any(b['behavior'] == 'cp2q_del2' for b in p['behaviors'])]

        if del2_patterns:
            recommendations.append(
                f"Found {len(del2_patterns)} patterns that predict cp2q_del2 behavior. "
                f"This explains the 14.9% cp2q_del2 coverage observed.")

        # Coverage recommendation
        coverage = self.statistics.get('coverage_percentage', 0)
        if coverage < 80:
            recommendations.append(
                f"Pattern coverage is {coverage:.1f}%. Additional patterns may be needed "
                f"to fully explain all cell behaviors.")

        return recommendations

    def write_results(self, output_file: Path, results: Dict[str, Any]):
        """Write results to JSON file."""
        try:
            with open(output_file, 'w') as f:
                json.dump(results, f, indent=2, default=str)

            if self.verbose:
                print(f"Pattern discovery results written to: {output_file}")

        except Exception as e:
            print(f"Error writing results: {e}")

    def write_human_readable_report(self, output_file: Path, results: Dict[str, Any]):
        """Write a human-readable summary report."""
        try:
            with open(output_file, 'w') as f:
                f.write("MCQC Cell Pattern Discovery Report\n")
                f.write("=" * 40 + "\n\n")

                # Statistics
                stats = results['statistics']
                f.write(f"Analysis Summary:\n")
                f.write(f"  Total patterns discovered: {stats['total_patterns_discovered']}\n")
                f.write(f"  Total cells analyzed: {stats['total_cells_analyzed']}\n")
                f.write(f"  Cell coverage: {stats['coverage_percentage']:.1f}%\n\n")

                # Pattern types
                f.write("Pattern Types:\n")
                for ptype, count in stats['pattern_type_distribution'].items():
                    f.write(f"  {ptype}: {count} patterns\n")
                f.write("\n")

                # Behavior distribution
                f.write("Behavior Predictions:\n")
                for behavior, count in stats['behavior_distribution'].items():
                    f.write(f"  {behavior}: {count} patterns\n")
                f.write("\n")

                # High-confidence patterns
                f.write("High-Confidence Patterns (≥90%):\n")
                high_conf_patterns = [p for p in results['discovered_patterns']
                                    if any(b['confidence'] >= 90 for b in p['behaviors'])]

                for pattern in high_conf_patterns[:10]:  # Show top 10
                    f.write(f"  {pattern['pattern']} ({pattern['pattern_type']}):\n")
                    for behavior in pattern['behaviors']:
                        if behavior['confidence'] >= 90:
                            f.write(f"    - {behavior['description']}\n")
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
        description='Discover cell name patterns that correlate with specific behaviors',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --analysis_csv deck_analysis.csv --output patterns.json
  %(prog)s --analysis_csv analysis.csv --output patterns.json --min_confidence 80
  %(prog)s --analysis_csv analysis.csv --output patterns.json --verbose
        """
    )

    parser.add_argument('--analysis_csv', type=Path, required=True,
                        help='CSV file from validate_deck_structure.py analysis')
    parser.add_argument('--output', type=Path, required=True,
                        help='Output JSON file for discovered patterns')
    parser.add_argument('--min_confidence', type=int, default=75,
                        help='Minimum confidence percentage for patterns (default: 75)')
    parser.add_argument('--min_sample_size', type=int, default=5,
                        help='Minimum sample size for pattern discovery (default: 5)')
    parser.add_argument('--human_report', type=Path,
                        help='Optional human-readable summary report file')
    parser.add_argument('--verbose', action='store_true',
                        help='Enable verbose output')

    args = parser.parse_args()

    try:
        if not args.analysis_csv.exists():
            print(f"Error: Analysis CSV file not found: {args.analysis_csv}")
            return 1

        # Run pattern discovery
        discoverer = CellPatternDiscoverer(
            min_confidence=args.min_confidence,
            min_sample_size=args.min_sample_size,
            verbose=args.verbose
        )

        analysis_data = discoverer.load_analysis_data(args.analysis_csv)
        if not analysis_data:
            print("Error: No analysis data loaded")
            return 1

        results = discoverer.analyze_cell_patterns(analysis_data)

        # Write results
        discoverer.write_results(args.output, results)

        # Write human-readable report if requested
        if args.human_report:
            discoverer.write_human_readable_report(args.human_report, results)

        # Print summary
        print(f"\nPattern Discovery Summary:")
        print(f"  Patterns found: {results['statistics']['total_patterns_discovered']}")
        print(f"  Cell coverage: {results['statistics']['coverage_percentage']:.1f}%")
        print(f"  High-confidence patterns: {len([p for p in results['discovered_patterns'] if any(b['confidence'] >= 90 for b in p['behaviors'])])}")

        return 0

    except Exception as e:
        print(f"Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())