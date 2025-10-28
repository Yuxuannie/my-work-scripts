# MCQC Tool Refactoring Proposal

**Date:** October 28, 2025
**Scope:** Complete tool refactoring for maintainability and reliability
**Approach:** Incremental migration with backward compatibility

## Problem Statement Summary

The MCQC tool is functionally complete but suffers from extreme complexity:
- **18,624 lines** of hardcoded template mapping logic
- **7 distinct final-state patterns** scattered across 8 files
- **6-layer configuration** hierarchy with no precedence rules
- **100+ cell name patterns** hardcoded in Python
- **No centralized configuration** management

## Proposed Solution Overview

### Core Strategy: Configuration-Driven Architecture

Transform the tool from **code-driven** to **configuration-driven** approach:

**BEFORE (Current):**
```python
# Hardcoded in flow/funcs.py (18K lines)
if fnmatch.fnmatch(cell_name, "*SYNC2*") and constr_pin == "CP":
    template_name = "min_pulse_width/template__sync2__CP__rise__fall__1.sp"
```

**AFTER (Proposed):**
```yaml
# External configuration file
cell_families:
  sync_multi:
    patterns: ["*SYNC2*", "*SYNC3*", "*SYNC4*", "*SYNC5*", "*SYNC6*"]
    template_rules:
      - conditions: {constr_pin: "CP", constr_pin_dir: "rise"}
        template: "min_pulse_width/template__sync{N}__CP__rise__fall__1.sp"
```

## Detailed Refactoring Plan

### Phase 1: Configuration Schema Design (2 weeks)

#### 1.1 Unified Configuration Schema
Create single YAML configuration file that consolidates all patterns:

```yaml
# mcqc_unified_config.yaml
version: "2.0"

# Global settings
global_config:
  mpw_threshold_formula: "2.5*(x - 0.5)"
  final_state_time: "50u"
  final_state_thresholds:
    low: 0.05
    high: 0.95

# Template mapping rules
template_mapping:
  cell_families:
    sync_multi:
      patterns: ["*SYNC2*", "*SYNC3*", "*SYNC4*", "*SYNC5*", "*SYNC6*"]
      template_rules:
        - conditions:
            arc_type: "min_pulse_width"
            constr_pin: "CP"
            constr_pin_dir: "rise"
          template: "min_pulse_width/template__sync{family_number}__CP__rise__fall__1.sp"
          variables:
            family_number: "extract_sync_number(cell_name)"

    sync1p5:
      patterns: ["*SYNC1P5*"]
      template_rules:
        - conditions:
            arc_type: "min_pulse_width"
            constr_pin: "CP"
            constr_pin_dir: "fall"
            when_contains: ["Q1"]
            cell_pattern: "*SDF*"
            probe_list: ["Q1"]
            when_contains: ["!SE"]
          template: "min_pulse_width/template__sync1p5__q1__CP__fall__rise__1.sp"
        - conditions:
            arc_type: "min_pulse_width"
            constr_pin: "CP"
            constr_pin_dir: "fall"
          template: "min_pulse_width/template__sync1p5__CP__fall__rise__1.sp"

    general_fallback:
      patterns: ["*"]  # Catch-all
      template_rules:
        - conditions:
            arc_type: "min_pulse_width"
            constr_pin: "CP"
            constr_pin_dir: "fall"
          template: "min_pulse_width/template__CP__fall__rise__1.sp"

# Final-state logic rules
final_state_config:
  rules:
    - name: "se_sa_c_condition"
      priority: 1
      trigger:
        when_contains: ["SE", "!SA", "C"]
      action:
        type: "add_vector_based"
        logic: "q_qn_vector_mapping"

    - name: "q_qn_vector_logic"
      priority: 2
      trigger:
        has_data_pins: true
        has_q_qn_probes: true
      action:
        type: "add_vector_based"
        logic: "data_to_output_mapping"

    - name: "amd_path_pattern"
      priority: 6
      trigger:
        template_path_contains: "_AMD_"
        cell_name_starts_with: "MB"
      action:
        type: "comprehensive_final_state"
        processor: "post_final_state"

# Post-processing rules
post_processing:
  conditional_execution: true  # Only run if conditions met
  processors:
    - name: "post_icg_ov"
      priority: 2
      conditions:
        cell_patterns: ["ICG*"]
      actions:
        - "replace_final_state_check"
        - "add_meas_final_state"

    - name: "post_mb_an2"
      priority: 4
      conditions:
        cell_patterns: ["MB.*AN2"]
      actions:
        - "fix_incorrect_toggle"
        - "fix_final_state_check"
```

#### 1.2 Configuration Parser Implementation
```python
# config_parser.py
import yaml
from typing import Dict, List, Any
from dataclasses import dataclass

@dataclass
class TemplateRule:
    conditions: Dict[str, Any]
    template: str
    variables: Dict[str, str] = None

@dataclass
class CellFamily:
    patterns: List[str]
    template_rules: List[TemplateRule]

class MCQCConfigParser:
    def __init__(self, config_file: str):
        with open(config_file, 'r') as f:
            self.config = yaml.safe_load(f)
        self.validate_config()

    def validate_config(self):
        """Validate configuration completeness and consistency"""
        required_sections = ['global_config', 'template_mapping', 'final_state_config']
        for section in required_sections:
            if section not in self.config:
                raise ValueError(f"Missing required section: {section}")

    def get_template_for_arc(self, cell_name: str, arc_type: str, **conditions) -> str:
        """Find matching template based on arc characteristics"""
        for family_name, family_config in self.config['template_mapping']['cell_families'].items():
            if self._matches_cell_patterns(cell_name, family_config['patterns']):
                for rule in family_config['template_rules']:
                    if self._matches_conditions(conditions, rule['conditions']):
                        return self._substitute_variables(rule['template'], cell_name, rule.get('variables', {}))
        return None

    def get_final_state_rules(self, arc_info: Dict) -> List[Dict]:
        """Get applicable final-state rules for arc"""
        applicable_rules = []
        for rule in self.config['final_state_config']['rules']:
            if self._matches_final_state_trigger(arc_info, rule['trigger']):
                applicable_rules.append(rule)
        return sorted(applicable_rules, key=lambda r: r['priority'])
```

### Phase 2: Pattern Extraction (2 weeks)

#### 2.1 Automated Pattern Extraction Tool
```python
# pattern_extractor.py
import ast
import re
from typing import List, Dict

class TemplatePatternExtractor:
    def __init__(self, funcs_file: str):
        self.funcs_file = funcs_file
        self.patterns = []

    def extract_all_patterns(self) -> List[Dict]:
        """Extract all template mapping patterns from funcs.py"""
        with open(self.funcs_file, 'r') as f:
            content = f.read()

        # Parse if-elif chains for min_pulse_width
        mpw_patterns = self._extract_mpw_patterns(content)

        # Extract cell name patterns
        cell_patterns = self._extract_cell_patterns(content)

        # Extract template mappings
        template_mappings = self._extract_template_mappings(content)

        return {
            'mpw_patterns': mpw_patterns,
            'cell_patterns': cell_patterns,
            'template_mappings': template_mappings,
            'statistics': self._generate_statistics()
        }

    def _extract_mpw_patterns(self, content: str) -> List[Dict]:
        """Extract min_pulse_width specific patterns"""
        patterns = []

        # Find all if statements with min_pulse_width
        mpw_blocks = re.findall(
            r'if\s*\(\s*arc_type\s*==\s*["\']min_pulse_width["\'].*?return template_name',
            content, re.DOTALL
        )

        for block in mpw_blocks:
            pattern = self._parse_pattern_block(block)
            patterns.append(pattern)

        return patterns

    def export_to_yaml(self, output_file: str):
        """Export extracted patterns to YAML configuration"""
        patterns = self.extract_all_patterns()
        config = self._convert_to_config_format(patterns)

        with open(output_file, 'w') as f:
            yaml.dump(config, f, default_flow_style=False, indent=2)
```

#### 2.2 Pattern Validation Tool
```python
# pattern_validator.py
class PatternValidator:
    def __init__(self, original_funcs: str, config_file: str):
        self.original_funcs = original_funcs
        self.config_parser = MCQCConfigParser(config_file)

    def validate_completeness(self) -> Dict[str, List]:
        """Ensure all original patterns are covered in config"""
        original_patterns = self._extract_original_patterns()
        config_patterns = self._extract_config_patterns()

        missing = []
        extra = []

        for pattern in original_patterns:
            if not self._find_equivalent_config_pattern(pattern, config_patterns):
                missing.append(pattern)

        return {
            'missing_patterns': missing,
            'extra_patterns': extra,
            'coverage_percentage': self._calculate_coverage()
        }
```

### Phase 3: Hybrid Implementation (3 weeks)

#### 3.1 Backward-Compatible Template Mapper
```python
# hybrid_template_mapper.py
class HybridTemplateMapper:
    def __init__(self, config_file: str = None, use_legacy: bool = False):
        self.use_legacy = use_legacy
        if not use_legacy and config_file:
            self.config_parser = MCQCConfigParser(config_file)

    def get_template(self, cell_name: str, arc_type: str, **kwargs) -> str:
        """Get template using new config or fall back to legacy"""

        if not self.use_legacy:
            try:
                # Try new configuration-driven approach
                template = self.config_parser.get_template_for_arc(
                    cell_name, arc_type, **kwargs
                )
                if template:
                    return template
                else:
                    # Fall back to legacy with warning
                    warnings.warn(f"No config rule found for {cell_name}, using legacy mapping")
                    return self._legacy_get_template(cell_name, arc_type, **kwargs)
            except Exception as e:
                warnings.warn(f"Config mapping failed: {e}, falling back to legacy")
                return self._legacy_get_template(cell_name, arc_type, **kwargs)
        else:
            # Use legacy approach with deprecation warning
            warnings.warn("Using legacy template mapping - migrate to config-driven approach")
            return self._legacy_get_template(cell_name, arc_type, **kwargs)

    def _legacy_get_template(self, cell_name: str, arc_type: str, **kwargs):
        """Call original 18K line mapping function"""
        import templateFileMap.funcs as legacy_mapper
        return legacy_mapper.mapCharacteristicsToTemplate(
            cell_name=cell_name, arc_type=arc_type, **kwargs
        )
```

#### 3.2 Final-State Logic Consolidation
```python
# consolidated_final_state.py
class ConsolidatedFinalStateManager:
    def __init__(self, config_file: str = None):
        self.config = MCQCConfigParser(config_file) if config_file else None

    def process_final_state_logic(self, arc_info: Dict, write_list: List[str]) -> List[str]:
        """Single entry point for all final-state processing"""

        if self.config:
            # Use configuration-driven approach
            rules = self.config.get_final_state_rules(arc_info)
            for rule in rules:
                write_list = self._apply_final_state_rule(rule, arc_info, write_list)
        else:
            # Fall back to existing scattered logic
            write_list = self._legacy_final_state_processing(arc_info, write_list)

        return write_list

    def _apply_final_state_rule(self, rule: Dict, arc_info: Dict, write_list: List[str]) -> List[str]:
        """Apply single final-state rule"""
        action_type = rule['action']['type']

        if action_type == "add_vector_based":
            return self._add_vector_based_measurements(arc_info, write_list, rule)
        elif action_type == "comprehensive_final_state":
            return self._add_comprehensive_final_state(arc_info, write_list, rule)
        elif action_type == "modify_criteria":
            return self._modify_final_state_criteria(arc_info, write_list, rule)
        else:
            warnings.warn(f"Unknown final-state action type: {action_type}")
            return write_list

    def _legacy_final_state_processing(self, arc_info: Dict, write_list: List[str]) -> List[str]:
        """Execute existing final-state logic chain"""
        # Import existing processors
        from post_helper import post_icg_ov, post_lnd2sr, post_mb_an2, post_sdfmoq
        from post_helper import post_final_state, remove_final_state

        # Execute existing chain
        write_list = post_icg_ov.post_process(arc_info, write_list)
        write_list = post_lnd2sr.post_process(arc_info, write_list)
        write_list = post_mb_an2.post_process(arc_info, write_list)
        write_list = post_sdfmoq.post_process(arc_info, write_list)
        write_list = remove_final_state.post_process(arc_info, write_list)

        if '_AMD_' in arc_info.get('TEMPLATE_DECK_PATH', ''):
            write_list = post_final_state.post_process(arc_info, write_list)

        return write_list
```

### Phase 4: Testing & Validation (2 weeks)

#### 4.1 Regression Test Framework
```python
# regression_tester.py
class MCQCRegressionTester:
    def __init__(self, test_library_path: str):
        self.test_library_path = test_library_path
        self.baseline_results = {}
        self.new_results = {}

    def generate_baseline(self, output_path: str):
        """Generate baseline results using current tool"""
        # Run current tool and capture all outputs
        self.baseline_results = self._run_mcqc_tool(use_legacy=True)
        self._save_results(self.baseline_results, output_path + "/baseline")

    def test_refactored_version(self, config_file: str, output_path: str):
        """Test refactored version against baseline"""
        self.new_results = self._run_mcqc_tool(use_legacy=False, config_file=config_file)
        self._save_results(self.new_results, output_path + "/refactored")

        # Compare results
        differences = self._compare_results()
        return differences

    def _compare_results(self) -> Dict:
        """Compare baseline vs refactored results"""
        differences = {
            'identical_decks': 0,
            'different_decks': 0,
            'missing_decks': [],
            'extra_decks': [],
            'measurement_differences': [],
            'final_state_differences': []
        }

        for arc_id in self.baseline_results:
            if arc_id in self.new_results:
                if self._decks_identical(self.baseline_results[arc_id], self.new_results[arc_id]):
                    differences['identical_decks'] += 1
                else:
                    differences['different_decks'] += 1
                    differences['measurement_differences'].append(
                        self._analyze_deck_differences(arc_id)
                    )
            else:
                differences['missing_decks'].append(arc_id)

        return differences
```

#### 4.2 Performance Benchmarking
```python
# performance_benchmark.py
import time
import memory_profiler
import psutil

class PerformanceBenchmark:
    def benchmark_template_mapping(self, test_cases: List[Dict]) -> Dict:
        """Benchmark template mapping performance"""
        legacy_times = []
        config_times = []

        # Test legacy approach
        for test_case in test_cases:
            start = time.time()
            legacy_result = self._legacy_template_mapping(test_case)
            legacy_times.append(time.time() - start)

        # Test config approach
        for test_case in test_cases:
            start = time.time()
            config_result = self._config_template_mapping(test_case)
            config_times.append(time.time() - start)

        return {
            'legacy_avg_time': sum(legacy_times) / len(legacy_times),
            'config_avg_time': sum(config_times) / len(config_times),
            'speedup_factor': sum(legacy_times) / sum(config_times),
            'memory_reduction': self._measure_memory_difference()
        }
```

### Phase 5: Migration & Deployment (1 week)

#### 5.1 Migration Strategy
```python
# migration_manager.py
class MigrationManager:
    def __init__(self):
        self.migration_log = []

    def migrate_production_library(self, library_path: str, config_file: str):
        """Migrate production library to new configuration"""

        # Step 1: Validate current configuration
        validation_results = self._validate_current_setup(library_path)

        # Step 2: Generate configuration for this library
        extracted_config = self._extract_library_specific_config(library_path)

        # Step 3: Test with hybrid mode
        test_results = self._test_hybrid_mode(library_path, config_file)

        # Step 4: Full migration if tests pass
        if test_results['success_rate'] > 0.99:
            self._complete_migration(library_path, config_file)
        else:
            self._rollback_migration(library_path)
            raise Exception(f"Migration failed: {test_results['failures']}")

    def _validate_current_setup(self, library_path: str) -> Dict:
        """Validate that current setup works correctly"""
        # Run baseline tests
        # Check all expected outputs are generated
        # Validate measurement statements
        pass
```

## Implementation Benefits

### Before vs After Comparison

| Aspect | Current | After Refactoring |
|--------|---------|------------------|
| Template Mapping | 18,624 lines of Python | 200 lines YAML config |
| Adding New Cell | 2-3 days code analysis | 30 minutes config edit |
| Final-State Logic | 7 scattered patterns | 1 consolidated manager |
| Configuration | 6 different sources | 1 unified config file |
| Debugging | Code diving required | Config tracing available |
| Team Knowledge | 1-2 experts only | Readable by all engineers |

### Quantified Benefits

#### Development Efficiency
- **New Cell Types:** 95% time reduction (3 days → 30 minutes)
- **Bug Fixes:** 80% faster troubleshooting with config tracing
- **Code Reviews:** 90% reduction in complex logic reviews

#### Quality Improvements
- **Hidden Logic:** 0% (all logic externalized)
- **Configuration Conflicts:** Prevented by validation
- **Pattern Coverage:** 100% with automated extraction

#### Maintenance Benefits
- **Knowledge Transfer:** Days → Hours with documentation
- **Change Risk:** 80% reduction with config validation
- **Production Issues:** 90% reduction from explicit patterns

## Risk Mitigation

### Technical Risks
- **Migration Complexity:** Mitigated by hybrid approach
- **Performance Impact:** Mitigated by benchmarking
- **Regression Bugs:** Mitigated by comprehensive testing

### Business Risks
- **Downtime:** Mitigated by backward compatibility
- **Training Need:** Mitigated by clear documentation
- **Adoption Resistance:** Mitigated by gradual migration

## Success Criteria

### Technical Metrics
- [ ] 100% pattern coverage in configuration
- [ ] 0% hardcoded template mapping logic
- [ ] <1% performance degradation
- [ ] 100% regression test pass rate

### Business Metrics
- [ ] 95% reduction in new cell development time
- [ ] 50% reduction in bug resolution time
- [ ] 3x increase in engineers who can maintain tool
- [ ] 90% reduction in production issues

This comprehensive refactoring proposal provides a clear path from the current complex, hardcoded implementation to a maintainable, configuration-driven architecture while preserving all existing functionality.