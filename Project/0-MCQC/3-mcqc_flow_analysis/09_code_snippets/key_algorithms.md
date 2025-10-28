# MCQC Key Algorithms and Code Snippets

**Analysis Date:** October 28, 2025
**Purpose:** Critical algorithms extracted from MCQC codebase for understanding and refactoring

## Template Mapping Algorithm

### Current Implementation (Simplified from 18K lines)
**Location:** `2-flow/funcs.py:100-18500`

```python
def cellName_to_templateDeckName(cell_name, arc_info, user_options):
    """
    Maps cell names to template deck files through extensive pattern matching.
    WARNING: This is a simplified version - actual file has 18,624 lines.
    """
    arc_type = arc_info.get('ARC_TYPE', '')

    # Pattern 1: SYNC2 cells
    if (arc_type == "min_pulse_width" and
        fnmatch.fnmatch(cell_name, "*SYNC2*")):
        template_name = "min_pulse_width/template__sync2__CP__rise__fall__1.sp"
        return template_name

    # Pattern 2: ASYNC cells
    elif (arc_type == "min_pulse_width" and
          fnmatch.fnmatch(cell_name, "*ASYNC*")):
        template_name = "min_pulse_width/template__async__D__rise__fall__1.sp"
        return template_name

    # Pattern 3: ICG (Integrated Clock Gating) cells
    elif (arc_type == "min_pulse_width" and
          fnmatch.fnmatch(cell_name, "ICG*")):
        template_name = "min_pulse_width/template__icg__CP__rise__fall__1.sp"
        return template_name

    # Pattern 4: MB*AN2 cells (Multi-bit AND2)
    elif (arc_type == "min_pulse_width" and
          re.match(r"MB.*AN2", cell_name)):
        template_name = "min_pulse_width/template__mb_an2__A__rise__fall__1.sp"
        return template_name

    # ... 96+ more patterns follow this structure

    # Default fallback
    else:
        template_name = "min_pulse_width/template__default__CP__rise__fall__1.sp"
        return template_name
```

### Proposed Refactored Algorithm
```python
class TemplateMapper:
    def __init__(self, config_file):
        self.patterns = self.load_patterns(config_file)

    def get_template(self, cell_name, arc_type):
        """
        Configuration-driven template mapping.
        Reduces 18K lines to <100 lines + config file.
        """
        for pattern_rule in self.patterns:
            if self.matches_pattern(cell_name, arc_type, pattern_rule):
                return pattern_rule['template']

        return self.get_default_template(arc_type)

    def matches_pattern(self, cell_name, arc_type, rule):
        # Arc type match
        if rule['arc_type'] != arc_type:
            return False

        # Cell pattern match (supports multiple patterns)
        for pattern in rule['cell_patterns']:
            if fnmatch.fnmatch(cell_name, pattern):
                return True

        return False

    def load_patterns(self, config_file):
        """Load patterns from YAML configuration"""
        import yaml
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)
        return config['template_mapping']
```

## Final-State Logic Algorithm

### Current Implementation Pattern FS_02 (SE/SA/C Logic)
**Location:** `spiceDeckMaker/funcs.py:408-500`

```python
def add_SE_SA_C_final_state_logic(when, vector, probe_pin, dpins_settings):
    """
    Embedded final-state logic for scan enable, save, and clock conditions.
    This is one of 7 final-state patterns found in the codebase.
    """
    if 'SE' in when or '!SA' in when or 'C' in when:
        if 'SE' in when:
            # Complex logic for SE (Scan Enable) conditions
            dpin_idx = get_data_pin_index(vector)

            if vector[dpin_idx] == '0':
                if not is_E_dominates(arc_info):
                    if 'QN' in probe_pin:
                        # Expect QN high (0.95) when data is 0
                        dpins_settings.append('.meas final_state find v(' + probe_pin + ') at=50u\n')
                        dpins_settings.append(".meas final_state_check find par('1') at='final_state/vdd_value > 0.95 ? 0 : -1'\n")
                    elif 'Q' in probe_pin:
                        # Expect Q low (0.05) when data is 0
                        dpins_settings.append('.meas final_state find v(' + probe_pin + ') at=50u\n')
                        dpins_settings.append(".meas final_state_check find par('1') at='final_state/vdd_value < 0.05 ? 0 : -1'\n")

            elif vector[dpin_idx] == '1':
                # Opposite expectations for data = 1
                if 'QN' in probe_pin:
                    dpins_settings.append('.meas final_state find v(' + probe_pin + ') at=50u\n')
                    dpins_settings.append(".meas final_state_check find par('1') at='final_state/vdd_value < 0.05 ? 0 : -1'\n")
                elif 'Q' in probe_pin:
                    dpins_settings.append('.meas final_state find v(' + probe_pin + ') at=50u\n')
                    dpins_settings.append(".meas final_state_check find par('1') at='final_state/vdd_value > 0.95 ? 0 : -1'\n")

        # Similar logic for !SA and C conditions...

    return dpins_settings
```

### Current Implementation Pattern FS_05 (MB_AN2 Correction)
**Location:** `post_helper/post_mb_an2.py:41-73`

```python
def fix_final_state_check(write_list, pinlist, vector):
    """
    Vector-based correction for MB*AN2 (Multi-bit AND2) cells.
    Corrects final-state expectations based on gate logic.
    """
    qpin = None

    for i, line in enumerate(write_list):
        if line.startswith('.meas final_state '):
            # Extract pin name from measurement statement
            left = line.find('v(') + 2
            right = line.find(')', left)
            qpin = line[left:right]

        elif line.startswith('.meas final_state_check '):
            if qpin:
                qidx = pinlist.index(qpin)
                qvec = vector[qidx]

                if qvec == 'F':  # Falling transition expected
                    write_list[i] = line.replace('> 0.95', '< 0.05')
                elif qvec == 'R':  # Rising transition expected
                    write_list[i] = line.replace('< 0.05', '> 0.95')
                else:
                    # Complex DA/DB pin analysis for multi-input AND gates
                    da_idx = get_pin_index(pinlist, 'DA')
                    db_idx = get_pin_index(pinlist, 'DB')

                    if da_idx >= 0 and db_idx >= 0:
                        da_vec = vector[da_idx]
                        db_vec = vector[db_idx]

                        # AND gate logic: output low if any input is low
                        if da_vec == '0' or db_vec == '0':
                            write_list[i] = line.replace('> 0.95', '< 0.05')
                        else:
                            write_list[i] = line.replace('< 0.05', '> 0.95')

    return write_list
```

### Proposed Unified Final-State Engine
```python
class FinalStateEngine:
    def __init__(self, config):
        self.rules = self.load_rules(config)
        self.thresholds = config['thresholds']

    def process_arc(self, arc_info, write_list):
        """
        Unified final-state processing replacing 7 scattered patterns.
        """
        applicable_rules = self.find_applicable_rules(arc_info)

        # Process rules in priority order
        for rule in sorted(applicable_rules, key=lambda r: r.priority):
            write_list = self.apply_rule(rule, arc_info, write_list)

        return write_list

    def find_applicable_rules(self, arc_info):
        """Determine which rules apply to current arc"""
        applicable = []

        for rule in self.rules:
            if self.rule_matches(rule, arc_info):
                applicable.append(rule)

        return applicable

    def rule_matches(self, rule, arc_info):
        """Check if rule conditions are met"""
        # Cell pattern matching
        if 'cell_pattern' in rule['trigger']:
            if not fnmatch.fnmatch(arc_info['CELL_NAME'], rule['trigger']['cell_pattern']):
                return False

        # When condition matching
        if 'when_contains' in rule['trigger']:
            when = arc_info.get('WHEN', '')
            for condition in rule['trigger']['when_contains']:
                if condition in when:
                    return True
            return False

        # Vector-based matching
        if 'has_data_vectors' in rule['trigger']:
            if rule['trigger']['has_data_vectors']:
                return self.has_data_vectors(arc_info)

        return True

    def apply_rule(self, rule, arc_info, write_list):
        """Apply specific rule action"""
        action = rule['action']

        if action == 'add_vector_based_measurements':
            return self.add_vector_measurements(arc_info, write_list, rule)
        elif action == 'modify_thresholds':
            return self.modify_thresholds(write_list, rule)
        elif action == 'remove_measurements':
            return self.remove_measurements(write_list)
        elif action == 'add_comprehensive_checks':
            return self.add_comprehensive_checks(arc_info, write_list, rule)

        return write_list

    def add_vector_measurements(self, arc_info, write_list, rule):
        """Add measurements based on vector analysis"""
        vector = arc_info.get('VECTOR', '')
        probe_pins = arc_info.get('PROBE_PINS', [])

        for probe_pin in probe_pins:
            expected_state = self.calculate_expected_state(vector, probe_pin, arc_info)
            threshold = self.get_threshold(expected_state, rule)

            # Add measurement statements
            write_list.append(f'.meas final_state find v({probe_pin}) at={self.thresholds["time"]}\n')
            write_list.append(f'.meas final_state_check find par(\'1\') at=\'final_state/vdd_value {threshold["condition"]} {threshold["value"]} ? 0 : -1\'\n')

        return write_list
```

## MPW Threshold Calculation Algorithm

### Current Implementation
**Location:** `timingArcInfo/funcs.py:150-200`

```python
def calculate_mpw_threshold(input_threshold, user_options):
    """
    Calculates MPW (Min Pulse Width) threshold from input threshold.
    Uses hardcoded formula that should be configurable.
    """
    # Hardcoded formula - should be externalized
    base_offset = 0.5
    multiplier = 2.5

    # Formula: mpw_threshold = 2.5 * (input_threshold - 0.5)
    mpw_threshold = multiplier * (input_threshold - base_offset)

    # Clamp to reasonable bounds
    if mpw_threshold < 0.1:
        mpw_threshold = 0.1
    elif mpw_threshold > 2.0:
        mpw_threshold = 2.0

    return mpw_threshold

def populate_spice_info(arc_info, chartcl_vars, user_options):
    """
    Populates SPICE simulation information dictionary.
    """
    spice_info = {}

    # Extract input threshold from chartcl variables
    cell_name = arc_info['CELL_NAME']
    pin_name = arc_info['RELATED_PIN']

    if cell_name in chartcl_vars['mpw_input_threshold']:
        if pin_name in chartcl_vars['mpw_input_threshold'][cell_name]:
            input_threshold = chartcl_vars['mpw_input_threshold'][cell_name][pin_name]
        else:
            input_threshold = 0.5  # Default
    else:
        input_threshold = 0.5  # Default

    # Calculate MPW threshold
    mpw_threshold = calculate_mpw_threshold(input_threshold, user_options)

    # Populate spice_info dictionary
    spice_info['INPUT_THRESHOLD'] = input_threshold
    spice_info['MPW_THRESHOLD'] = mpw_threshold
    spice_info['VDD_VALUE'] = user_options.get('vdd_value', 1.0)
    spice_info['TEMPERATURE'] = user_options.get('temperature', 25)

    return spice_info
```

### Proposed Configurable Algorithm
```python
class MPWCalculator:
    def __init__(self, config):
        self.formulas = config['formulas']
        self.defaults = config['defaults']

    def calculate_threshold(self, input_threshold, library_name=None, cell_name=None):
        """
        Configurable MPW threshold calculation.
        """
        formula = self.get_formula(library_name, cell_name)

        # Apply formula
        result = self.apply_formula(formula, input_threshold)

        # Apply bounds checking
        return self.apply_bounds(result, formula.get('bounds', self.defaults['bounds']))

    def get_formula(self, library_name, cell_name):
        """Get appropriate formula based on context"""
        # Cell-specific formulas first
        if cell_name:
            for cell_formula in self.formulas.get('cell_specific', []):
                if fnmatch.fnmatch(cell_name, cell_formula['pattern']):
                    return cell_formula

        # Library-specific formulas
        if library_name in self.formulas.get('library_specific', {}):
            return self.formulas['library_specific'][library_name]

        # Default formula
        return self.formulas['default']

    def apply_formula(self, formula, input_threshold):
        """Apply mathematical formula"""
        formula_type = formula['type']

        if formula_type == 'linear':
            # Linear: result = multiplier * (input - offset) + base
            return (formula['multiplier'] *
                   (input_threshold - formula['offset']) +
                   formula.get('base', 0))

        elif formula_type == 'polynomial':
            # Polynomial: result = a*x^2 + b*x + c
            x = input_threshold
            return (formula['a'] * x**2 +
                   formula['b'] * x +
                   formula['c'])

        elif formula_type == 'lookup':
            # Lookup table with interpolation
            return self.interpolate_lookup(formula['table'], input_threshold)

        else:
            raise ValueError(f"Unknown formula type: {formula_type}")
```

## Post-Processing Chain Algorithm

### Current Implementation
**Location:** `spiceDeckMaker/funcs.py:330-340`

```python
def run_post_processing_chain(arc_info, write_list):
    """
    Runs all post-processors in fixed order.
    All processors run regardless of applicability.
    """
    # Post-processor chain (fixed order)
    write_list = post_icg_ov.post_process(arc_info, write_list)      # 1
    write_list = post_lnd2sr.post_process(arc_info, write_list)      # 2
    write_list = post_mb_an2.post_process(arc_info, write_list)      # 3
    write_list = post_sdfmoq.post_process(arc_info, write_list)      # 4
    write_list = remove_final_state.post_process(arc_info, write_list)  # 5

    # Conditional final processor
    if '_AMD_' in arc_info['TEMPLATE_DECK_PATH']:
        write_list = post_final_state.post_process(arc_info, write_list)  # 6

    return write_list
```

### Proposed Optimized Algorithm
```python
class PostProcessingChain:
    def __init__(self, config):
        self.processors = self.load_processors(config)

    def process(self, arc_info, write_list):
        """
        Optimized post-processing with conditional execution.
        """
        applicable_processors = self.find_applicable_processors(arc_info)

        for processor in applicable_processors:
            if processor.should_run(arc_info):
                write_list = processor.process(arc_info, write_list)

        return write_list

    def find_applicable_processors(self, arc_info):
        """Only run processors that apply to current arc"""
        applicable = []

        for processor in self.processors:
            if processor.is_applicable(arc_info):
                applicable.append(processor)

        return sorted(applicable, key=lambda p: p.priority)

class ConditionalProcessor:
    def __init__(self, name, trigger_conditions, priority):
        self.name = name
        self.trigger_conditions = trigger_conditions
        self.priority = priority

    def is_applicable(self, arc_info):
        """Check if processor should run for this arc"""
        for condition in self.trigger_conditions:
            if condition['type'] == 'cell_pattern':
                if fnmatch.fnmatch(arc_info['CELL_NAME'], condition['pattern']):
                    return True
            elif condition['type'] == 'template_path':
                if condition['substring'] in arc_info['TEMPLATE_DECK_PATH']:
                    return True

        return False
```

## Configuration Loading Algorithm

### Proposed Unified Configuration Loader
```python
class ConfigurationLoader:
    def __init__(self):
        self.config_cache = {}
        self.precedence_order = [
            'command_line',
            'globals_file',
            'chartcl_file',
            'template_file',
            'defaults'
        ]

    def load_unified_config(self, sources):
        """
        Load and merge configuration from multiple sources with precedence.
        """
        unified_config = {}

        # Load each source in reverse precedence order
        for source_type in reversed(self.precedence_order):
            if source_type in sources:
                source_config = self.load_source(source_type, sources[source_type])
                unified_config = self.merge_configs(unified_config, source_config)

        # Validate final configuration
        self.validate_config(unified_config)

        return unified_config

    def merge_configs(self, base_config, override_config):
        """Deep merge configuration dictionaries"""
        merged = copy.deepcopy(base_config)

        for key, value in override_config.items():
            if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
                merged[key] = self.merge_configs(merged[key], value)
            else:
                merged[key] = value

        return merged

    def validate_config(self, config):
        """Validate configuration consistency and completeness"""
        validation_rules = [
            self.validate_paths_exist,
            self.validate_threshold_ranges,
            self.validate_pattern_syntax,
            self.validate_template_references
        ]

        for rule in validation_rules:
            rule(config)
```

These algorithms represent the core computational logic of the MCQC tool and demonstrate both the current complexity and the proposed simplification through configuration-driven approaches.