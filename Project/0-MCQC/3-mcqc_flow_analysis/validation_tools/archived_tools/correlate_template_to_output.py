#!/usr/bin/env python3
"""
Template-to-Output Correlation Analyzer

Analyzes the correlation between template files and actual SPICE deck characteristics.
Discovers which templates produce final-state checks, cp2q_del2, internal nodes, etc.

Usage:
    python correlate_template_to_output.py --analysis_csv deck_analysis.csv --output template_correlation.json
    python correlate_template_to_output.py --analysis_csv deck_analysis.csv --output correlation.json --verbose

Example:
    python correlate_template_to_output.py --analysis_csv /work/analysis/deck_analysis.csv --output template_patterns.json

Author: MCQC Validation Team
Date: October 2025
"""

import csv
import json
import argparse
import sys
from pathlib import Path
from collections import defaultdict, Counter
from typing import Dict, List, Any, Tuple

class TemplateCorrelationAnalyzer:
    """Analyzes correlations between template files and deck characteristics."""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.template_stats = defaultdict(lambda: {
            'total_uses': 0,
            'final_state_count': 0,
            'cp2q_del2_count': 0,
            'internal_node_count': 0,
            'glitch_check_count': 0,
            'cells_using': set(),
            'arc_types': set(),
            'measurement_profiles': Counter(),
            'complexity_scores': [],
            'post_processors': Counter(),
            'threshold_patterns': Counter(),
            'errors': [],
            'sample_arcs': []
        })

        self.global_stats = {
            'total_arcs': 0,
            'templates_found': 0,
            'correlation_strength': {},
            'pattern_discoveries': []
        }

    def load_analysis_data(self, csv_file: Path) -> List[Dict[str, Any]]:
        """Load deck analysis data from CSV file."""
        if self.verbose:
            print(f"Loading analysis data from: {csv_file}")

        data = []
        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Convert string representations back to appropriate types
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

    def analyze_correlations(self, analysis_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze correlations between templates and deck characteristics."""
        if self.verbose:
            print("Analyzing template-to-output correlations...")

        self.global_stats['total_arcs'] = len(analysis_data)

        # Process each deck analysis
        for i, deck_data in enumerate(analysis_data):
            if self.verbose and i % 1000 == 0:
                print(f"Processing arc {i}/{len(analysis_data)}")

            self._process_deck_for_template(deck_data)

        # Calculate correlation statistics
        self._calculate_correlations()
        self._discover_patterns()

        if self.verbose:
            print(f"Analysis complete. Found {self.global_stats['templates_found']} unique templates")

        return self._compile_results()

    def _process_deck_for_template(self, deck_data: Dict[str, Any]):
        """Process a single deck analysis for template correlation."""
        template_used = deck_data.get('template_used')
        if not template_used:
            template_used = 'UNKNOWN_TEMPLATE'

        stats = self.template_stats[template_used]

        # Basic counts
        stats['total_uses'] += 1
        if deck_data.get('has_final_state', False):
            stats['final_state_count'] += 1
        if deck_data.get('has_cp2q_del2', False):
            stats['cp2q_del2_count'] += 1
        if deck_data.get('uses_internal_nodes', False):
            stats['internal_node_count'] += 1
        if deck_data.get('has_glitch_check', False):
            stats['glitch_check_count'] += 1

        # Collect metadata
        if deck_data.get('cell_name'):
            stats['cells_using'].add(deck_data['cell_name'])
        if deck_data.get('arc_type'):
            stats['arc_types'].add(deck_data['arc_type'])

        # Profile and complexity
        if deck_data.get('measurement_profile'):
            stats['measurement_profiles'][deck_data['measurement_profile']] += 1
        if deck_data.get('complexity_score') is not None:
            stats['complexity_scores'].append(deck_data['complexity_score'])

        # Post-processors
        for processor in deck_data.get('post_processors_detected', []):
            stats['post_processors'][processor] += 1

        # Threshold patterns
        for threshold in deck_data.get('threshold_values', []):
            stats['threshold_patterns'][threshold] += 1

        # Errors
        if deck_data.get('error_indicators'):
            stats['errors'].extend(deck_data['error_indicators'])

        # Sample arcs (keep up to 5 examples per template)
        if len(stats['sample_arcs']) < 5:
            stats['sample_arcs'].append({
                'arc_folder': deck_data.get('arc_folder'),
                'cell_name': deck_data.get('cell_name'),
                'measurement_profile': deck_data.get('measurement_profile')
            })

    def _calculate_correlations(self):
        """Calculate correlation statistics for each template."""
        self.global_stats['templates_found'] = len(self.template_stats)

        # Calculate percentages and correlations for each template
        for template_name, stats in self.template_stats.items():
            total = stats['total_uses']
            if total == 0:
                continue

            # Calculate percentages
            stats['final_state_percentage'] = (stats['final_state_count'] / total) * 100
            stats['cp2q_del2_percentage'] = (stats['cp2q_del2_count'] / total) * 100
            stats['internal_node_percentage'] = (stats['internal_node_count'] / total) * 100
            stats['glitch_check_percentage'] = (stats['glitch_check_count'] / total) * 100

            # Calculate average complexity
            if stats['complexity_scores']:
                stats['avg_complexity'] = sum(stats['complexity_scores']) / len(stats['complexity_scores'])
                stats['min_complexity'] = min(stats['complexity_scores'])
                stats['max_complexity'] = max(stats['complexity_scores'])
            else:
                stats['avg_complexity'] = 0
                stats['min_complexity'] = 0
                stats['max_complexity'] = 0

            # Convert sets to lists for JSON serialization
            stats['cells_using'] = sorted(list(stats['cells_using']))
            stats['arc_types'] = sorted(list(stats['arc_types']))

        # Calculate global correlation strength
        self._calculate_global_correlations()

    def _calculate_global_correlations(self):
        """Calculate global correlation strength metrics."""
        # Find templates with strong correlations (>90% or <10% for binary features)
        strong_correlations = {}

        for template_name, stats in self.template_stats.items():
            template_correlations = []

            # Final-state correlation
            fs_pct = stats.get('final_state_percentage', 0)
            if fs_pct > 90:
                template_correlations.append(f"ALWAYS final-state ({fs_pct:.1f}%)")
            elif fs_pct < 10:
                template_correlations.append(f"NEVER final-state ({fs_pct:.1f}%)")

            # CP2Q_DEL2 correlation
            del2_pct = stats.get('cp2q_del2_percentage', 0)
            if del2_pct > 90:
                template_correlations.append(f"ALWAYS cp2q_del2 ({del2_pct:.1f}%)")
            elif del2_pct < 10:
                template_correlations.append(f"NEVER cp2q_del2 ({del2_pct:.1f}%)")

            # Internal nodes correlation
            in_pct = stats.get('internal_node_percentage', 0)
            if in_pct > 90:
                template_correlations.append(f"ALWAYS internal nodes ({in_pct:.1f}%)")
            elif in_pct < 10:
                template_correlations.append(f"NEVER internal nodes ({in_pct:.1f}%)")

            if template_correlations:
                strong_correlations[template_name] = template_correlations

        self.global_stats['correlation_strength'] = strong_correlations

    def _discover_patterns(self):
        """Discover interesting patterns in the data."""
        patterns = []

        # Pattern 1: Templates that always have final-state
        always_fs_templates = []
        never_fs_templates = []

        for template_name, stats in self.template_stats.items():
            if stats['total_uses'] >= 10:  # Only consider templates with significant usage
                fs_pct = stats.get('final_state_percentage', 0)
                if fs_pct >= 95:
                    always_fs_templates.append((template_name, fs_pct, stats['total_uses']))
                elif fs_pct <= 5:
                    never_fs_templates.append((template_name, fs_pct, stats['total_uses']))

        if always_fs_templates:
            patterns.append({
                'pattern_type': 'ALWAYS_FINAL_STATE',
                'description': 'Templates that always generate final-state checks',
                'templates': always_fs_templates,
                'significance': 'HIGH - Predictable behavior'
            })

        if never_fs_templates:
            patterns.append({
                'pattern_type': 'NEVER_FINAL_STATE',
                'description': 'Templates that never generate final-state checks',
                'templates': never_fs_templates,
                'significance': 'HIGH - Predictable behavior'
            })

        # Pattern 2: CP2Q_DEL2 correlations
        cp2q_del2_patterns = []
        for template_name, stats in self.template_stats.items():
            if stats['total_uses'] >= 10:
                del2_pct = stats.get('cp2q_del2_percentage', 0)
                if del2_pct >= 50:  # Significant cp2q_del2 usage
                    cp2q_del2_patterns.append((template_name, del2_pct, stats['total_uses']))

        if cp2q_del2_patterns:
            patterns.append({
                'pattern_type': 'CP2Q_DEL2_CORRELATION',
                'description': 'Templates with significant cp2q_del2 usage',
                'templates': cp2q_del2_patterns,
                'significance': 'MEDIUM - May indicate pattern'
            })

        # Pattern 3: Template naming patterns
        template_names = list(self.template_stats.keys())
        naming_patterns = self._analyze_template_naming(template_names)
        if naming_patterns:
            patterns.append({
                'pattern_type': 'NAMING_PATTERNS',
                'description': 'Template naming conventions discovered',
                'patterns': naming_patterns,
                'significance': 'LOW - Documentation aid'
            })

        # Pattern 4: Post-processor correlations
        processor_patterns = []
        for template_name, stats in self.template_stats.items():
            if stats['total_uses'] >= 10:
                dominant_processors = [proc for proc, count in stats['post_processors'].most_common(2)]
                if dominant_processors:
                    processor_patterns.append((template_name, dominant_processors, stats['total_uses']))

        if processor_patterns:
            patterns.append({
                'pattern_type': 'POST_PROCESSOR_CORRELATION',
                'description': 'Templates correlated with specific post-processors',
                'correlations': processor_patterns,
                'significance': 'HIGH - Indicates processing logic'
            })

        self.global_stats['pattern_discoveries'] = patterns

    def _analyze_template_naming(self, template_names: List[str]) -> List[Dict[str, Any]]:
        """Analyze template naming patterns."""
        naming_patterns = []

        # Look for common naming components
        components = defaultdict(int)
        for template_name in template_names:
            if template_name == 'UNKNOWN_TEMPLATE':
                continue

            # Split on common delimiters
            parts = template_name.replace('/', '_').replace('.', '_').split('_')
            for part in parts:
                if part and len(part) > 1:
                    components[part] += 1

        # Find significant components (appear in multiple templates)
        significant_components = {comp: count for comp, count in components.items()
                                if count >= 3}

        if significant_components:
            naming_patterns.append({
                'type': 'COMMON_COMPONENTS',
                'components': significant_components,
                'description': 'Components that appear in multiple template names'
            })

        # Look for naming conventions
        conventions = []
        if any('AMD' in name for name in template_names):
            conventions.append('AMD naming convention found')
        if any('sync' in name.lower() for name in template_names):
            conventions.append('sync/SYNC naming convention found')
        if any('template__' in name for name in template_names):
            conventions.append('template__ prefix convention found')

        if conventions:
            naming_patterns.append({
                'type': 'NAMING_CONVENTIONS',
                'conventions': conventions,
                'description': 'Naming convention patterns detected'
            })

        return naming_patterns

    def _compile_results(self) -> Dict[str, Any]:
        """Compile all results into a comprehensive report."""
        # Convert defaultdict to regular dict and process Counter objects
        template_results = {}
        for template_name, stats in self.template_stats.items():
            processed_stats = dict(stats)

            # Convert Counter objects to dicts
            processed_stats['measurement_profiles'] = dict(stats['measurement_profiles'])
            processed_stats['post_processors'] = dict(stats['post_processors'])
            processed_stats['threshold_patterns'] = dict(stats['threshold_patterns'])

            # Remove complexity_scores list (keep summary stats)
            if 'complexity_scores' in processed_stats:
                del processed_stats['complexity_scores']

            template_results[template_name] = processed_stats

        return {
            'analysis_metadata': {
                'total_arcs_analyzed': self.global_stats['total_arcs'],
                'unique_templates_found': self.global_stats['templates_found'],
                'analysis_date': str(Path(__file__).stat().st_mtime)
            },
            'template_statistics': template_results,
            'global_correlations': self.global_stats['correlation_strength'],
            'pattern_discoveries': self.global_stats['pattern_discoveries'],
            'summary_insights': self._generate_summary_insights()
        }

    def _generate_summary_insights(self) -> List[str]:
        """Generate high-level insights from the analysis."""
        insights = []

        # Calculate overall statistics
        total_templates = len([t for t in self.template_stats.keys() if t != 'UNKNOWN_TEMPLATE'])
        if total_templates == 0:
            insights.append("WARNING: No valid templates found in analysis")
            return insights

        # Final-state insights
        fs_templates = [t for t, s in self.template_stats.items()
                       if s.get('final_state_percentage', 0) > 50]
        fs_percentage = (len(fs_templates) / total_templates) * 100
        insights.append(f"{len(fs_templates)} of {total_templates} templates ({fs_percentage:.1f}%) "
                       f"frequently generate final-state checks")

        # CP2Q_DEL2 insights
        del2_templates = [t for t, s in self.template_stats.items()
                         if s.get('cp2q_del2_percentage', 0) > 10]
        if del2_templates:
            insights.append(f"{len(del2_templates)} templates show significant cp2q_del2 usage")

        # Correlation insights
        strong_corr_count = len(self.global_stats.get('correlation_strength', {}))
        if strong_corr_count > 0:
            insights.append(f"{strong_corr_count} templates show strong behavioral correlations")

        # Pattern insights
        pattern_count = len(self.global_stats.get('pattern_discoveries', []))
        if pattern_count > 0:
            insights.append(f"{pattern_count} significant patterns discovered in template behavior")

        return insights

    def write_results(self, output_file: Path, results: Dict[str, Any]):
        """Write results to JSON file."""
        try:
            with open(output_file, 'w') as f:
                json.dump(results, f, indent=2, default=str)

            if self.verbose:
                print(f"Correlation analysis written to: {output_file}")

        except Exception as e:
            print(f"Error writing results: {e}")

    def write_human_readable_report(self, output_file: Path, results: Dict[str, Any]):
        """Write a human-readable summary report."""
        try:
            with open(output_file, 'w') as f:
                f.write("MCQC Template-to-Output Correlation Analysis\n")
                f.write("=" * 50 + "\n\n")

                # Metadata
                metadata = results['analysis_metadata']
                f.write(f"Total arcs analyzed: {metadata['total_arcs_analyzed']}\n")
                f.write(f"Unique templates found: {metadata['unique_templates_found']}\n\n")

                # Summary insights
                f.write("Key Insights:\n")
                for insight in results['summary_insights']:
                    f.write(f"  • {insight}\n")
                f.write("\n")

                # Strong correlations
                if results['global_correlations']:
                    f.write("Strong Template Correlations:\n")
                    for template, correlations in results['global_correlations'].items():
                        f.write(f"  {template}:\n")
                        for corr in correlations:
                            f.write(f"    - {corr}\n")
                    f.write("\n")

                # Pattern discoveries
                if results['pattern_discoveries']:
                    f.write("Pattern Discoveries:\n")
                    for pattern in results['pattern_discoveries']:
                        f.write(f"  {pattern['pattern_type']}: {pattern['description']}\n")
                        f.write(f"    Significance: {pattern['significance']}\n")
                    f.write("\n")

                # Top templates by usage
                f.write("Top Templates by Usage:\n")
                template_usage = [(name, stats['total_uses'])
                                for name, stats in results['template_statistics'].items()
                                if name != 'UNKNOWN_TEMPLATE']
                template_usage.sort(key=lambda x: x[1], reverse=True)

                for i, (template, usage) in enumerate(template_usage[:10]):
                    stats = results['template_statistics'][template]
                    fs_pct = stats.get('final_state_percentage', 0)
                    del2_pct = stats.get('cp2q_del2_percentage', 0)
                    f.write(f"  {i+1}. {template}: {usage} arcs "
                           f"(FS: {fs_pct:.1f}%, DEL2: {del2_pct:.1f}%)\n")

            if self.verbose:
                print(f"Human-readable report written to: {output_file}")

        except Exception as e:
            print(f"Error writing human-readable report: {e}")


def main():
    """Main function with command line interface."""
    parser = argparse.ArgumentParser(
        description='Analyze correlations between template files and SPICE deck characteristics',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --analysis_csv deck_analysis.csv --output template_correlation.json
  %(prog)s --analysis_csv deck_analysis.csv --output correlation.json --verbose
  %(prog)s --analysis_csv analysis.csv --output corr.json --human_report summary.txt
        """
    )

    parser.add_argument('--analysis_csv', type=Path, required=True,
                        help='CSV file from validate_deck_structure.py analysis')
    parser.add_argument('--output', type=Path, required=True,
                        help='Output JSON file for correlation results')
    parser.add_argument('--human_report', type=Path,
                        help='Optional human-readable summary report file')
    parser.add_argument('--verbose', action='store_true',
                        help='Enable verbose output')

    args = parser.parse_args()

    try:
        if not args.analysis_csv.exists():
            print(f"Error: Analysis CSV file not found: {args.analysis_csv}")
            return 1

        # Run correlation analysis
        analyzer = TemplateCorrelationAnalyzer(verbose=args.verbose)
        analysis_data = analyzer.load_analysis_data(args.analysis_csv)

        if not analysis_data:
            print("Error: No analysis data loaded")
            return 1

        results = analyzer.analyze_correlations(analysis_data)

        # Write results
        analyzer.write_results(args.output, results)

        # Write human-readable report if requested
        if args.human_report:
            analyzer.write_human_readable_report(args.human_report, results)

        # Print summary
        print(f"\nCorrelation Analysis Summary:")
        print(f"  Templates analyzed: {results['analysis_metadata']['unique_templates_found']}")
        print(f"  Strong correlations: {len(results['global_correlations'])}")
        print(f"  Patterns discovered: {len(results['pattern_discoveries'])}")

        return 0

    except Exception as e:
        print(f"Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())