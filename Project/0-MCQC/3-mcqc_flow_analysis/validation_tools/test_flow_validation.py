#!/usr/bin/env python3
"""
MCQC Flow Validation Test Suite

Comprehensive test suite to validate that discovered patterns match actual tool behavior
and ensure consistency across the entire MCQC flow.

Usage:
    python test_flow_validation.py --deck_dir /path/to/DECKS/ --test_type all
    python test_flow_validation.py --deck_dir /path/to/DECKS/ --test_type coverage
    python test_flow_validation.py --analysis_csv deck_analysis.csv --test_type patterns

Example:
    python test_flow_validation.py --deck_dir /work/MCQC_RUN/DECKS/ --test_type all --verbose

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
from typing import Dict, List, Any, Set, Tuple, Optional
import fnmatch

class FlowValidator:
    """Validates MCQC flow patterns and consistency."""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.test_results = {
            'coverage_tests': {},
            'pattern_tests': {},
            'consistency_tests': {},
            'template_tests': {},
            'specification_tests': {}
        }
        self.validation_errors = []
        self.validation_warnings = []

    def load_analysis_data(self, source: Path, source_type: str = 'auto') -> List[Dict[str, Any]]:
        """Load analysis data from CSV file or directory scan."""
        if source_type == 'auto':
            source_type = 'csv' if source.suffix == '.csv' else 'directory'

        if source_type == 'csv':
            return self._load_from_csv(source)
        elif source_type == 'directory':
            return self._load_from_directory(source)
        else:
            raise ValueError(f"Unknown source type: {source_type}")

    def _load_from_csv(self, csv_file: Path) -> List[Dict[str, Any]]:
        """Load analysis data from CSV file."""
        if self.verbose:
            print(f"Loading analysis data from CSV: {csv_file}")

        data = []
        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    processed_row = self._process_csv_row(row)
                    data.append(processed_row)

            if self.verbose:
                print(f"Loaded {len(data)} records from CSV")

            return data

        except Exception as e:
            print(f"Error loading CSV file: {e}")
            return []

    def _load_from_directory(self, deck_dir: Path) -> List[Dict[str, Any]]:
        """Load analysis data by scanning deck directory."""
        if self.verbose:
            print(f"Scanning deck directory: {deck_dir}")

        # Import the deck analyzer
        from validate_deck_structure import DeckCollectionAnalyzer

        analyzer = DeckCollectionAnalyzer(verbose=self.verbose)
        results = analyzer.analyze_deck_directory(deck_dir)

        if self.verbose:
            print(f"Scanned {len(results)} decks")

        return results

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

    def run_all_tests(self, analysis_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Run comprehensive validation test suite."""
        if self.verbose:
            print("Running comprehensive validation test suite...")

        # Test coverage expectations
        self.test_final_state_coverage(analysis_data)
        self.test_cp2q_del2_coverage(analysis_data)
        self.test_measurement_profile_distribution(analysis_data)

        # Test pattern consistency
        self.test_pattern_consistency(analysis_data)
        self.test_template_correlation(analysis_data)
        self.test_cell_pattern_consistency(analysis_data)

        # Test data integrity
        self.test_data_integrity(analysis_data)
        self.test_measurement_completeness(analysis_data)

        # Test specification compliance
        self.test_specification_gaps(analysis_data)

        # Compile results
        return self._compile_test_results()

    def test_final_state_coverage(self, analysis_data: List[Dict[str, Any]]):
        """Test: 74% of arcs should have final-state checks."""
        if self.verbose:
            print("  Testing final-state coverage...")

        total_arcs = len(analysis_data)
        final_state_arcs = sum(1 for arc in analysis_data if arc.get('has_final_state', False))
        coverage_percentage = (final_state_arcs / total_arcs) * 100 if total_arcs > 0 else 0

        # Expected range: 70-78% based on observations
        expected_min = 70.0
        expected_max = 78.0

        test_result = {
            'test_name': 'final_state_coverage',
            'expected_range': f'{expected_min}-{expected_max}%',
            'actual_percentage': coverage_percentage,
            'actual_count': final_state_arcs,
            'total_arcs': total_arcs,
            'passed': expected_min <= coverage_percentage <= expected_max,
            'deviation': abs(coverage_percentage - 74.0)  # Expected center point
        }

        if not test_result['passed']:
            self.validation_errors.append(
                f"Final-state coverage {coverage_percentage:.1f}% outside expected range {expected_min}-{expected_max}%"
            )

        self.test_results['coverage_tests']['final_state'] = test_result

    def test_cp2q_del2_coverage(self, analysis_data: List[Dict[str, Any]]):
        """Test: 14.9% of arcs should have cp2q_del2 measurements."""
        if self.verbose:
            print("  Testing cp2q_del2 coverage...")

        total_arcs = len(analysis_data)
        cp2q_del2_arcs = sum(1 for arc in analysis_data if arc.get('has_cp2q_del2', False))
        coverage_percentage = (cp2q_del2_arcs / total_arcs) * 100 if total_arcs > 0 else 0

        # Expected range: 12-18% based on observations
        expected_min = 12.0
        expected_max = 18.0

        test_result = {
            'test_name': 'cp2q_del2_coverage',
            'expected_range': f'{expected_min}-{expected_max}%',
            'actual_percentage': coverage_percentage,
            'actual_count': cp2q_del2_arcs,
            'total_arcs': total_arcs,
            'passed': expected_min <= coverage_percentage <= expected_max,
            'deviation': abs(coverage_percentage - 14.9)  # Expected center point
        }

        if not test_result['passed']:
            self.validation_errors.append(
                f"CP2Q_DEL2 coverage {coverage_percentage:.1f}% outside expected range {expected_min}-{expected_max}%"
            )

        self.test_results['coverage_tests']['cp2q_del2'] = test_result

    def test_measurement_profile_distribution(self, analysis_data: List[Dict[str, Any]]):
        """Test distribution of measurement profiles."""
        if self.verbose:
            print("  Testing measurement profile distribution...")

        profile_counts = Counter(arc.get('measurement_profile', 'UNKNOWN') for arc in analysis_data)
        total_arcs = len(analysis_data)

        # Expected profiles and approximate distributions
        expected_profiles = {
            'FINAL_STATE_SINGLE': (60, 80),  # 60-80% of arcs
            'DUAL_DELAY_ONLY': (5, 20),      # 5-20% of arcs
            'BASIC_DELAY': (10, 30),         # 10-30% of arcs
            'FULL_MONITORING': (0, 10)       # 0-10% of arcs
        }

        test_result = {
            'test_name': 'measurement_profile_distribution',
            'actual_distribution': {},
            'expected_ranges': expected_profiles,
            'passed': True,
            'profile_issues': []
        }

        for profile, count in profile_counts.items():
            percentage = (count / total_arcs) * 100
            test_result['actual_distribution'][profile] = {
                'count': count,
                'percentage': percentage
            }

            if profile in expected_profiles:
                min_pct, max_pct = expected_profiles[profile]
                if not (min_pct <= percentage <= max_pct):
                    test_result['passed'] = False
                    test_result['profile_issues'].append(
                        f"{profile}: {percentage:.1f}% (expected {min_pct}-{max_pct}%)"
                    )

        if not test_result['passed']:
            self.validation_errors.append(
                f"Measurement profile distribution issues: {test_result['profile_issues']}"
            )

        self.test_results['coverage_tests']['measurement_profiles'] = test_result

    def test_pattern_consistency(self, analysis_data: List[Dict[str, Any]]):
        """Test: Same cell+arc+when should produce same deck structure."""
        if self.verbose:
            print("  Testing pattern consistency...")

        # Group by cell name, arc type, and when condition
        pattern_groups = defaultdict(list)
        for arc in analysis_data:
            key = (
                arc.get('cell_name', 'UNKNOWN'),
                arc.get('arc_type', 'UNKNOWN'),
                arc.get('when_condition', 'NONE')
            )
            pattern_groups[key].append(arc)

        test_result = {
            'test_name': 'pattern_consistency',
            'total_patterns': len(pattern_groups),
            'consistent_patterns': 0,
            'inconsistent_patterns': 0,
            'inconsistencies': [],
            'passed': True
        }

        for pattern_key, arcs in pattern_groups.items():
            if len(arcs) < 2:
                continue  # Skip single-arc patterns

            # Check consistency of key behaviors
            fs_behaviors = set(arc.get('has_final_state', False) for arc in arcs)
            del2_behaviors = set(arc.get('has_cp2q_del2', False) for arc in arcs)
            profile_behaviors = set(arc.get('measurement_profile', 'UNKNOWN') for arc in arcs)

            inconsistent = False
            issues = []

            if len(fs_behaviors) > 1:
                inconsistent = True
                issues.append(f"final_state: {fs_behaviors}")

            if len(del2_behaviors) > 1:
                inconsistent = True
                issues.append(f"cp2q_del2: {del2_behaviors}")

            if len(profile_behaviors) > 1:
                inconsistent = True
                issues.append(f"profiles: {profile_behaviors}")

            if inconsistent:
                test_result['inconsistent_patterns'] += 1
                test_result['inconsistencies'].append({
                    'pattern': pattern_key,
                    'arc_count': len(arcs),
                    'issues': issues,
                    'sample_arcs': [arc.get('arc_folder', '') for arc in arcs[:3]]
                })
                test_result['passed'] = False
            else:
                test_result['consistent_patterns'] += 1

        if not test_result['passed']:
            self.validation_errors.append(
                f"Found {test_result['inconsistent_patterns']} inconsistent patterns"
            )

        self.test_results['consistency_tests']['pattern_consistency'] = test_result

    def test_template_correlation(self, analysis_data: List[Dict[str, Any]]):
        """Test: Same template should produce consistent patterns."""
        if self.verbose:
            print("  Testing template correlation...")

        # Group by template
        template_groups = defaultdict(list)
        for arc in analysis_data:
            template = arc.get('template_used', 'UNKNOWN')
            template_groups[template].append(arc)

        test_result = {
            'test_name': 'template_correlation',
            'total_templates': len(template_groups),
            'consistent_templates': 0,
            'inconsistent_templates': 0,
            'template_issues': [],
            'passed': True
        }

        for template, arcs in template_groups.items():
            if len(arcs) < 5:  # Need sufficient sample size
                continue

            # Calculate behavior percentages
            fs_count = sum(1 for arc in arcs if arc.get('has_final_state', False))
            del2_count = sum(1 for arc in arcs if arc.get('has_cp2q_del2', False))

            fs_percentage = (fs_count / len(arcs)) * 100
            del2_percentage = (del2_count / len(arcs)) * 100

            # Check for strong correlation (>90% or <10%)
            inconsistent = False
            issues = []

            # Templates should show consistent behavior patterns
            if 10 < fs_percentage < 90:
                inconsistent = True
                issues.append(f"final_state inconsistent: {fs_percentage:.1f}%")

            if 10 < del2_percentage < 90:
                # More tolerance for del2 as it's less common
                if del2_percentage > 25:  # Only flag if significantly inconsistent
                    inconsistent = True
                    issues.append(f"cp2q_del2 inconsistent: {del2_percentage:.1f}%")

            if inconsistent:
                test_result['inconsistent_templates'] += 1
                test_result['template_issues'].append({
                    'template': template,
                    'arc_count': len(arcs),
                    'final_state_percentage': fs_percentage,
                    'cp2q_del2_percentage': del2_percentage,
                    'issues': issues
                })
                test_result['passed'] = False
            else:
                test_result['consistent_templates'] += 1

        if not test_result['passed']:
            self.validation_warnings.append(
                f"Found {test_result['inconsistent_templates']} templates with inconsistent behavior"
            )

        self.test_results['consistency_tests']['template_correlation'] = test_result

    def test_cell_pattern_consistency(self, analysis_data: List[Dict[str, Any]]):
        """Test cell name pattern consistency."""
        if self.verbose:
            print("  Testing cell pattern consistency...")

        # Test known patterns
        known_patterns = [
            ('*SYNC*', 'SYNC cells should have consistent behavior'),
            ('*ASYNC*', 'ASYNC cells should have consistent behavior'),
            ('*ICG*', 'ICG cells should have consistent behavior'),
            ('*FF*', 'FF cells should have consistent behavior'),
            ('MB*AN2*', 'MB*AN2 cells should have consistent behavior')
        ]

        test_result = {
            'test_name': 'cell_pattern_consistency',
            'tested_patterns': [],
            'passed': True,
            'pattern_issues': []
        }

        for pattern, description in known_patterns:
            matching_arcs = [arc for arc in analysis_data
                           if fnmatch.fnmatch(arc.get('cell_name', ''), pattern)]

            if len(matching_arcs) < 5:
                continue  # Skip patterns with insufficient data

            # Check behavior consistency
            fs_count = sum(1 for arc in matching_arcs if arc.get('has_final_state', False))
            fs_percentage = (fs_count / len(matching_arcs)) * 100

            pattern_result = {
                'pattern': pattern,
                'description': description,
                'matching_count': len(matching_arcs),
                'final_state_percentage': fs_percentage,
                'consistent': 90 <= fs_percentage or fs_percentage <= 10
            }

            if not pattern_result['consistent']:
                test_result['passed'] = False
                test_result['pattern_issues'].append(f"{pattern}: {fs_percentage:.1f}% final-state")

            test_result['tested_patterns'].append(pattern_result)

        if not test_result['passed']:
            self.validation_warnings.append(
                f"Cell pattern inconsistencies: {test_result['pattern_issues']}"
            )

        self.test_results['consistency_tests']['cell_patterns'] = test_result

    def test_data_integrity(self, analysis_data: List[Dict[str, Any]]):
        """Test data integrity and completeness."""
        if self.verbose:
            print("  Testing data integrity...")

        test_result = {
            'test_name': 'data_integrity',
            'total_arcs': len(analysis_data),
            'integrity_issues': [],
            'passed': True
        }

        missing_cell_names = 0
        missing_arc_types = 0
        invalid_measurements = 0
        error_arcs = 0

        for arc in analysis_data:
            # Check for missing essential data
            if not arc.get('cell_name') or arc.get('cell_name') == 'UNKNOWN':
                missing_cell_names += 1

            if not arc.get('arc_type') or arc.get('arc_type') == 'UNKNOWN':
                missing_arc_types += 1

            # Check for measurement inconsistencies
            if arc.get('has_final_state', False):
                if arc.get('num_final_state_meas', 0) == 0:
                    invalid_measurements += 1

            # Check for errors
            if arc.get('error_indicators'):
                error_arcs += 1

        # Calculate percentages
        total = len(analysis_data)
        if total > 0:
            missing_cell_pct = (missing_cell_names / total) * 100
            missing_arc_pct = (missing_arc_types / total) * 100
            invalid_meas_pct = (invalid_measurements / total) * 100
            error_pct = (error_arcs / total) * 100

            # Set thresholds for acceptable data quality
            if missing_cell_pct > 5:
                test_result['integrity_issues'].append(f"Missing cell names: {missing_cell_pct:.1f}%")
                test_result['passed'] = False

            if missing_arc_pct > 5:
                test_result['integrity_issues'].append(f"Missing arc types: {missing_arc_pct:.1f}%")
                test_result['passed'] = False

            if invalid_meas_pct > 2:
                test_result['integrity_issues'].append(f"Invalid measurements: {invalid_meas_pct:.1f}%")
                test_result['passed'] = False

            if error_pct > 10:
                test_result['integrity_issues'].append(f"Error indicators: {error_pct:.1f}%")
                test_result['passed'] = False

            test_result['data_quality'] = {
                'missing_cell_names_pct': missing_cell_pct,
                'missing_arc_types_pct': missing_arc_pct,
                'invalid_measurements_pct': invalid_meas_pct,
                'error_arcs_pct': error_pct
            }

        if not test_result['passed']:
            self.validation_errors.append(f"Data integrity issues: {test_result['integrity_issues']}")

        self.test_results['consistency_tests']['data_integrity'] = test_result

    def test_measurement_completeness(self, analysis_data: List[Dict[str, Any]]):
        """Test measurement completeness and logical consistency."""
        if self.verbose:
            print("  Testing measurement completeness...")

        test_result = {
            'test_name': 'measurement_completeness',
            'completeness_issues': [],
            'passed': True
        }

        measurement_issues = 0
        logic_issues = 0

        for arc in analysis_data:
            # Test final-state measurement completeness
            if arc.get('has_final_state', False):
                fs_meas = arc.get('num_final_state_meas', 0)
                fs_check = arc.get('num_final_state_check_meas', 0)

                # Should have both measurements and checks
                if fs_meas > 0 and fs_check == 0:
                    measurement_issues += 1

                # Should have threshold values if has final-state
                if not arc.get('threshold_values'):
                    measurement_issues += 1

            # Test logical consistency
            if arc.get('measurement_profile') == 'FINAL_STATE_SINGLE':
                if not arc.get('has_final_state', False) or not arc.get('has_cp2q_del1', False):
                    logic_issues += 1

            if arc.get('measurement_profile') == 'DUAL_DELAY_ONLY':
                if not arc.get('has_cp2q_del1', False) or not arc.get('has_cp2q_del2', False):
                    logic_issues += 1

        total = len(analysis_data)
        if total > 0:
            measurement_pct = (measurement_issues / total) * 100
            logic_pct = (logic_issues / total) * 100

            if measurement_pct > 5:
                test_result['completeness_issues'].append(f"Measurement issues: {measurement_pct:.1f}%")
                test_result['passed'] = False

            if logic_pct > 5:
                test_result['completeness_issues'].append(f"Logic issues: {logic_pct:.1f}%")
                test_result['passed'] = False

            test_result['measurement_statistics'] = {
                'measurement_issues_pct': measurement_pct,
                'logic_issues_pct': logic_pct
            }

        if not test_result['passed']:
            self.validation_errors.append(f"Measurement completeness issues: {test_result['completeness_issues']}")

        self.test_results['consistency_tests']['measurement_completeness'] = test_result

    def test_specification_gaps(self, analysis_data: List[Dict[str, Any]]):
        """Test for specification gaps based on behavior patterns."""
        if self.verbose:
            print("  Testing specification gaps...")

        test_result = {
            'test_name': 'specification_gaps',
            'gaps_detected': [],
            'gap_severity': 'NONE',
            'passed': True
        }

        total_arcs = len(analysis_data)

        # Critical gap: Final-state without specification
        fs_count = sum(1 for arc in analysis_data if arc.get('has_final_state', False))
        fs_percentage = (fs_count / total_arcs) * 100 if total_arcs > 0 else 0

        if fs_percentage > 50:
            test_result['gaps_detected'].append({
                'gap_type': 'FINAL_STATE_SPECIFICATION_GAP',
                'affected_percentage': fs_percentage,
                'affected_count': fs_count,
                'severity': 'CRITICAL',
                'description': f"{fs_percentage:.1f}% of arcs have final-state checks without specification"
            })
            test_result['gap_severity'] = 'CRITICAL'
            test_result['passed'] = False

        # High gap: CP2Q_DEL2 without clear specification
        del2_count = sum(1 for arc in analysis_data if arc.get('has_cp2q_del2', False))
        del2_percentage = (del2_count / total_arcs) * 100 if total_arcs > 0 else 0

        if del2_percentage > 10:
            test_result['gaps_detected'].append({
                'gap_type': 'CP2Q_DEL2_SPECIFICATION_GAP',
                'affected_percentage': del2_percentage,
                'affected_count': del2_count,
                'severity': 'HIGH',
                'description': f"{del2_percentage:.1f}% of arcs have cp2q_del2 without clear specification"
            })
            if test_result['gap_severity'] != 'CRITICAL':
                test_result['gap_severity'] = 'HIGH'

        # Post-processor gaps
        pp_count = sum(1 for arc in analysis_data if arc.get('post_processors_detected'))
        pp_percentage = (pp_count / total_arcs) * 100 if total_arcs > 0 else 0

        if pp_percentage > 20:
            test_result['gaps_detected'].append({
                'gap_type': 'POST_PROCESSOR_SPECIFICATION_GAP',
                'affected_percentage': pp_percentage,
                'affected_count': pp_count,
                'severity': 'MEDIUM',
                'description': f"{pp_percentage:.1f}% of arcs use post-processors without specification"
            })

        if test_result['gaps_detected']:
            self.validation_warnings.append(f"Specification gaps detected: {test_result['gap_severity']}")

        self.test_results['specification_tests']['specification_gaps'] = test_result

    def _compile_test_results(self) -> Dict[str, Any]:
        """Compile all test results into a comprehensive report."""
        # Count passed/failed tests
        all_tests = []
        for category, tests in self.test_results.items():
            for test_name, result in tests.items():
                all_tests.append(result)

        passed_tests = sum(1 for test in all_tests if test.get('passed', False))
        failed_tests = len(all_tests) - passed_tests

        return {
            'validation_summary': {
                'total_tests': len(all_tests),
                'passed_tests': passed_tests,
                'failed_tests': failed_tests,
                'pass_rate': (passed_tests / len(all_tests)) * 100 if all_tests else 0,
                'overall_status': 'PASSED' if failed_tests == 0 else 'FAILED'
            },
            'test_results': self.test_results,
            'validation_errors': self.validation_errors,
            'validation_warnings': self.validation_warnings,
            'recommendations': self._generate_test_recommendations()
        }

    def _generate_test_recommendations(self) -> List[str]:
        """Generate recommendations based on test results."""
        recommendations = []

        if self.validation_errors:
            recommendations.append(
                f"CRITICAL: {len(self.validation_errors)} validation errors found. "
                f"These indicate fundamental issues that need immediate attention."
            )

        if self.validation_warnings:
            recommendations.append(
                f"WARNING: {len(self.validation_warnings)} validation warnings found. "
                f"These indicate potential issues that should be investigated."
            )

        # Specific recommendations based on test results
        coverage_tests = self.test_results.get('coverage_tests', {})
        if 'final_state' in coverage_tests and not coverage_tests['final_state'].get('passed', True):
            recommendations.append(
                "Final-state coverage outside expected range. "
                "Verify that pattern discovery is working correctly."
            )

        consistency_tests = self.test_results.get('consistency_tests', {})
        if 'pattern_consistency' in consistency_tests and not consistency_tests['pattern_consistency'].get('passed', True):
            recommendations.append(
                "Pattern consistency issues found. "
                "Some identical configurations produce different results."
            )

        return recommendations

    def write_results(self, output_file: Path, results: Dict[str, Any]):
        """Write test results to JSON file."""
        try:
            with open(output_file, 'w') as f:
                json.dump(results, f, indent=2, default=str)

            if self.verbose:
                print(f"Validation test results written to: {output_file}")

        except Exception as e:
            print(f"Error writing test results: {e}")

    def write_human_readable_report(self, output_file: Path, results: Dict[str, Any]):
        """Write a human-readable test report."""
        try:
            with open(output_file, 'w') as f:
                f.write("MCQC Flow Validation Test Report\n")
                f.write("=" * 40 + "\n\n")

                # Summary
                summary = results['validation_summary']
                f.write(f"Test Summary:\n")
                f.write(f"  Total tests: {summary['total_tests']}\n")
                f.write(f"  Passed: {summary['passed_tests']}\n")
                f.write(f"  Failed: {summary['failed_tests']}\n")
                f.write(f"  Pass rate: {summary['pass_rate']:.1f}%\n")
                f.write(f"  Overall status: {summary['overall_status']}\n\n")

                # Errors
                if results['validation_errors']:
                    f.write("Validation Errors:\n")
                    for error in results['validation_errors']:
                        f.write(f"  ❌ {error}\n")
                    f.write("\n")

                # Warnings
                if results['validation_warnings']:
                    f.write("Validation Warnings:\n")
                    for warning in results['validation_warnings']:
                        f.write(f"  ⚠️  {warning}\n")
                    f.write("\n")

                # Test category results
                for category, tests in results['test_results'].items():
                    f.write(f"{category.replace('_', ' ').title()}:\n")
                    for test_name, result in tests.items():
                        status = "✅ PASS" if result.get('passed', False) else "❌ FAIL"
                        f.write(f"  {status} {test_name}\n")
                    f.write("\n")

                # Recommendations
                if results['recommendations']:
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
        description='Validate MCQC flow patterns and consistency',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Test Types:
  coverage    - Test coverage expectations (74% final-state, 14.9% cp2q_del2)
  patterns    - Test pattern consistency and correlation
  integrity   - Test data integrity and completeness
  gaps        - Test for specification gaps
  all         - Run all tests (default)

Examples:
  %(prog)s --deck_dir /work/MCQC_RUN/DECKS/ --test_type all
  %(prog)s --analysis_csv deck_analysis.csv --test_type coverage
  %(prog)s --deck_dir /work/DECKS/ --test_type patterns --verbose
        """
    )

    # Input options
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--deck_dir', type=Path,
                       help='Directory containing SPICE decks to analyze')
    group.add_argument('--analysis_csv', type=Path,
                       help='CSV file from validate_deck_structure.py')

    # Test options
    parser.add_argument('--test_type', choices=['coverage', 'patterns', 'integrity', 'gaps', 'all'],
                        default='all', help='Type of tests to run (default: all)')
    parser.add_argument('--output', type=Path,
                        help='Output JSON file for test results')
    parser.add_argument('--human_report', type=Path,
                        help='Optional human-readable test report file')
    parser.add_argument('--verbose', action='store_true',
                        help='Enable verbose output')

    args = parser.parse_args()

    try:
        # Determine source
        if args.deck_dir:
            if not args.deck_dir.exists():
                print(f"Error: Directory not found: {args.deck_dir}")
                return 1
            source = args.deck_dir
            source_type = 'directory'
        else:
            if not args.analysis_csv.exists():
                print(f"Error: CSV file not found: {args.analysis_csv}")
                return 1
            source = args.analysis_csv
            source_type = 'csv'

        # Run validation
        validator = FlowValidator(verbose=args.verbose)
        analysis_data = validator.load_analysis_data(source, source_type)

        if not analysis_data:
            print("Error: No analysis data loaded")
            return 1

        # Run selected tests
        if args.test_type == 'all':
            results = validator.run_all_tests(analysis_data)
        elif args.test_type == 'coverage':
            validator.test_final_state_coverage(analysis_data)
            validator.test_cp2q_del2_coverage(analysis_data)
            validator.test_measurement_profile_distribution(analysis_data)
            results = validator._compile_test_results()
        elif args.test_type == 'patterns':
            validator.test_pattern_consistency(analysis_data)
            validator.test_template_correlation(analysis_data)
            validator.test_cell_pattern_consistency(analysis_data)
            results = validator._compile_test_results()
        elif args.test_type == 'integrity':
            validator.test_data_integrity(analysis_data)
            validator.test_measurement_completeness(analysis_data)
            results = validator._compile_test_results()
        elif args.test_type == 'gaps':
            validator.test_specification_gaps(analysis_data)
            results = validator._compile_test_results()

        # Write results
        if args.output:
            validator.write_results(args.output, results)

        if args.human_report:
            validator.write_human_readable_report(args.human_report, results)

        # Print summary
        summary = results['validation_summary']
        print(f"\nValidation Summary:")
        print(f"  Tests run: {summary['total_tests']}")
        print(f"  Passed: {summary['passed_tests']}")
        print(f"  Failed: {summary['failed_tests']}")
        print(f"  Overall: {summary['overall_status']}")

        if results['validation_errors']:
            print(f"  Errors: {len(results['validation_errors'])}")

        return 0 if summary['overall_status'] == 'PASSED' else 1

    except Exception as e:
        print(f"Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())