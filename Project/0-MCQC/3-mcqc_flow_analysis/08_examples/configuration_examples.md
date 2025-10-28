# MCQC Configuration Examples and Use Cases

**Date:** October 28, 2025
**Purpose:** Practical examples showing current configuration complexity and proposed improvements

## Current Configuration Complexity Examples

### Example 1: Adding a New Cell Type (Current Process)

#### Scenario: Adding "ULTRA_SYNC3_X1" cell support

**Step 1: Analyze existing patterns in flow/funcs.py (18K lines)**
```python
# Search through 18,624 lines to find similar patterns
# Current code in 2-flow/funcs.py around line 8,450:

if( arc_type == "min_pulse_width" and
    fnmatch.fnmatch(cell_name, "*SYNC2*")):
    template_name = "min_pulse_width/template__sync2__CP__rise__fall__1.sp"
    return template_name

elif( arc_type == "min_pulse_width" and
      fnmatch.fnmatch(cell_name, "*SYNC3*")):
    template_name = "min_pulse_width/template__sync3__CP__rise__fall__1.sp"
    return template_name

# Need to add new pattern for ULTRA_SYNC3:
elif( arc_type == "min_pulse_width" and
      fnmatch.fnmatch(cell_name, "*ULTRA_SYNC3*")):
    template_name = "min_pulse_width/template__ultra_sync3__CP__rise__fall__1.sp"
    return template_name
```

**Step 2: Understand final-state requirements**
```python
# Check spiceDeckMaker/funcs.py for special logic needed
# Lines 400-500 contain SE/SA/C logic
# Lines 600-990 contain Q/QN vector logic
# May need additional logic in post-processors

# If ULTRA_SYNC3 has scan enable, it triggers FS_02 pattern automatically
if 'SE' in when or '!SA' in when or 'C' in when:
    # This will automatically apply to ULTRA_SYNC3 if it has SE pins
```

**Step 3: Create template file**
```spice
* template__ultra_sync3__CP__rise__fall__1.sp
* Template for ULTRA_SYNC3 MPW characterization

.subckt ULTRA_SYNC3_X1 D CP Q QN SE VDD VSS
    * Circuit description
    * ... (complex SPICE netlist)

.ends

* Test circuit
X1 $data_pin $clock_pin $q_pin $qn_pin $scan_enable_pin VDD VSS ULTRA_SYNC3_X1

* Measurements
.meas tran $measurement_name trig v($clock_pin) val=$trigger_threshold
+                            targ v($data_pin) val=$target_threshold

* Final-state will be added automatically by patterns
.end
```

**Current Time Investment:** 2-3 days to analyze patterns, test, and validate

### Example 2: Configuring Final-State Thresholds (Current Process)

#### Scenario: Changing final-state criteria from 0.05/0.95 to 0.1/0.9

**Current Requirements:** Code changes in multiple files
```python
# File 1: spiceDeckMaker/funcs.py - Multiple locations
# Line ~450:
dpins_settings.append(".meas final_state_check find par('1') at='final_state/vdd_value < 0.05 ? 0 : -1'\n")
# Change to:
dpins_settings.append(".meas final_state_check find par('1') at='final_state/vdd_value < 0.1 ? 0 : -1'\n")

# Line ~470:
dpins_settings.append(".meas final_state_check find par('1') at='final_state/vdd_value > 0.95 ? 0 : -1'\n")
# Change to:
dpins_settings.append(".meas final_state_check find par('1') at='final_state/vdd_value > 0.9 ? 0 : -1'\n")

# File 2: post_helper/post_helper.py
def replace_final_state_check(write_list, check_ratio):
    if check_ratio == '0.95':  # Change to '0.9'
        write_list[i] = line.replace('< 0.05', '> 0.95')  # Change both values

# File 3: post_helper/post_icg_ov.py
write_list = post_helper.replace_final_state_check(write_list, '0.95')  # Change to '0.9'

# File 4: post_helper/post_mb_an2.py
if qvec == 'F':
    write_list[i] = line.replace('> 0.95', '< 0.05')  # Change both values
```

**Risk:** Missing one location breaks final-state logic
**Current Time Investment:** 1-2 days to find all occurrences and test

### Example 3: Library-Specific Configuration (Current Process)

#### Scenario: Different MPW thresholds for different libraries

**Current Configuration Scattered Across Files:**

**chartcl file (char_library_A.tcl):**
```tcl
set mpw_input_threshold {
    SYNC2_X1 {CP {1.2}}
    SYNC2_X2 {CP {1.0}}
    ASYNC_X1 {D {0.8}}
}
```

**Python code modifications needed:**
```python
# timingArcInfo/funcs.py - hardcoded formula
def calculate_mpw_threshold(input_threshold):
    # Current: mpw_threshold = 2.5 * (input_threshold - 0.5)
    # Library A needs: mpw_threshold = 3.0 * (input_threshold - 0.4)
    # Requires code change!
```

**Current Limitation:** No way to configure formulas per library

## Proposed Configuration Examples

### Example 1: Adding New Cell Type (Proposed Configuration-Driven)

#### Unified Configuration File (mcqc_config.yaml):
```yaml
# Add new cell type in 30 seconds
template_mapping:
  cell_patterns:
    - pattern: "*ULTRA_SYNC3*"
      arc_type: "min_pulse_width"
      template: "min_pulse_width/template__ultra_sync3__CP__rise__fall__1.sp"
      description: "Ultra high-speed synchronous 3-input cell"

final_state_rules:
  # ULTRA_SYNC3 automatically inherits existing SE/SA/C rules
  - name: "SE_SA_C_conditions"
    trigger:
      when_contains: ["SE", "!SA", "C"]
    applies_to: ["*SYNC*", "*ULTRA_SYNC3*"]  # Explicit inclusion
    action: "add_vector_based_measurements"
```

**New Time Investment:** 30 seconds to edit config file

### Example 2: Configurable Final-State Thresholds (Proposed)

#### Configuration-Driven Thresholds:
```yaml
final_state_config:
  measurement_time: "50u"

  thresholds:
    default:
      low: 0.1    # Changed from 0.05
      high: 0.9   # Changed from 0.95

    # Library-specific overrides
    library_overrides:
      "high_speed_lib":
        low: 0.05
        high: 0.95
      "low_power_lib":
        low: 0.15
        high: 0.85

  # Cell-specific overrides
  cell_overrides:
    "ICG*":
      threshold_behavior: "invert_low_high"
      low: 0.1
      high: 0.9
```

**Generated Code (automatic):**
```python
# Automatically generated based on config
def get_final_state_threshold(cell_name, library_name, threshold_type):
    config = load_config()

    # Check cell-specific overrides first
    for pattern, override in config['cell_overrides'].items():
        if fnmatch.fnmatch(cell_name, pattern):
            return override[threshold_type]

    # Check library-specific overrides
    if library_name in config['library_overrides']:
        return config['library_overrides'][library_name][threshold_type]

    # Use default
    return config['thresholds']['default'][threshold_type]
```

### Example 3: Complete Library Configuration (Proposed)

#### Library-Specific Configuration Package:
```yaml
# library_configs/high_speed_16nm.yaml
library_info:
  name: "high_speed_16nm"
  technology: "16nm"
  vendor: "FOUNDRY_A"
  version: "v2.1"

simulation_parameters:
  default_temperature: 25
  voltage_nominal: 0.8
  timing:
    measurement_time: "25u"  # Faster for high-speed
    setup_time: "5u"

mpw_calculations:
  formula: "3.5 * (input_threshold - 0.3)"  # Different formula
  base_offset: 0.3
  multiplier: 3.5

cell_patterns:
  high_speed_sync:
    patterns: ["HS_SYNC*", "ULTRA_SYNC*"]
    template: "templates/high_speed_sync_template.sp"
    special_handling:
      - "requires_fast_final_state_check"
      - "uses_differential_probing"

final_state_rules:
  # High-speed specific rules
  - name: "high_speed_differential"
    trigger:
      cell_pattern: "HS_*"
      has_differential_outputs: true
    action: "add_differential_final_state"
    thresholds:
      differential_low: 0.02
      differential_high: 0.78
```

#### Usage in Code:
```python
# Simple library loading
def process_library(library_name, chartcl_file):
    config = load_library_config(library_name)

    # All parameters now come from config
    mpw_calculator = MPWCalculator(config['mpw_calculations'])
    final_state_processor = FinalStateProcessor(config['final_state_rules'])
    template_mapper = TemplateMapper(config['cell_patterns'])

    # Process with configuration-driven logic
    return run_pipeline(config, chartcl_file)
```

## Migration Examples

### Example 1: Gradual Pattern Migration

#### Current Pattern (in Python code):
```python
# 2-flow/funcs.py - line 8,450
if( arc_type == "min_pulse_width" and
    fnmatch.fnmatch(cell_name, "*SYNC2*")):
    template_name = "min_pulse_width/template__sync2__CP__rise__fall__1.sp"
    return template_name
```

#### Migration Step 1: Extract to Config
```yaml
# patterns_config.yaml
extracted_patterns:
  - pattern: "*SYNC2*"
    arc_type: "min_pulse_width"
    template: "min_pulse_width/template__sync2__CP__rise__fall__1.sp"
    source: "flow/funcs.py:8450"
    migration_date: "2025-10-28"
```

#### Migration Step 2: Hybrid Code
```python
# Load config and check there first, fallback to hardcoded
def cellName_to_templateDeckName(cell_name, arc_info, user_options):
    # Try config-driven mapping first
    config_result = check_config_mapping(cell_name, arc_info)
    if config_result:
        return config_result

    # Fallback to legacy hardcoded patterns
    return legacy_cellName_to_templateDeckName(cell_name, arc_info, user_options)
```

#### Migration Step 3: Complete Migration
```python
# Pure config-driven approach
def cellName_to_templateDeckName(cell_name, arc_info, user_options):
    return config_mapper.get_template(cell_name, arc_info['ARC_TYPE'])
```

### Example 2: Final-State Logic Consolidation

#### Current State (7 scattered patterns):
```python
# Pattern in spiceDeckMaker/funcs.py
if 'SE' in when or '!SA' in when or 'C' in when:
    # Embedded logic

# Pattern in post_icg_ov.py
if cell_matches_icg_pattern(cell_name):
    # ICG-specific logic

# Pattern in post_mb_an2.py
if re.match("MB.*AN2", cell_name):
    # MB_AN2-specific logic
```

#### Consolidated Decision Engine:
```python
class FinalStateDecisionEngine:
    def __init__(self, config):
        self.rules = load_final_state_rules(config)

    def process_arc(self, arc_info, write_list):
        applicable_rules = self.find_applicable_rules(arc_info)

        for rule in sorted(applicable_rules, key=lambda r: r.priority):
            if rule.action == "add_measurements":
                write_list = self.add_measurements(write_list, rule, arc_info)
            elif rule.action == "modify_thresholds":
                write_list = self.modify_thresholds(write_list, rule, arc_info)
            elif rule.action == "remove_measurements":
                write_list = self.remove_measurements(write_list, rule)

        return write_list
```

## Real-World Usage Scenarios

### Scenario 1: New Engineer Onboarding
**Current:** 2 weeks to understand hardcoded patterns
**Proposed:** 2 hours to read configuration files

### Scenario 2: Production Debugging
**Current:** Search through 18K lines to find why cell failed
**Proposed:** Check configuration and logs for exact rule applied

### Scenario 3: Process Node Migration
**Current:** Modify Python code in multiple files
**Proposed:** Create new library configuration file

### Scenario 4: Customer-Specific Requirements
**Current:** Branch code and maintain separate versions
**Proposed:** Override specific configuration sections

This configuration transformation dramatically reduces complexity while maintaining full backward compatibility and improving maintainability.