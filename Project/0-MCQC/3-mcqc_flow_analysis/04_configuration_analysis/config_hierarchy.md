# MCQC Configuration Hierarchy Analysis

**Analysis Date:** October 28, 2025
**Configuration Complexity:** 6 distinct configuration layers
**Primary Issue:** No unified configuration management

## Configuration Layer Analysis

### Layer 1: Command Line Arguments (Highest Precedence)
**Purpose:** Runtime overrides and user-specific parameters
**Location:** `scld__mcqc.py` parseInputArgs()
**Variables:**
```python
--lib_type        # Library type (SNPS, CDNS)
--lg              # Length gate parameter
--vt              # Voltage threshold
--corner          # Process corner
--output_path     # Output directory path
--globals_file    # Globals configuration file path
--template_lut_path  # Template lookup table path
--kit_path        # Kit library path
```

### Layer 2: Globals File (Primary Configuration)
**Purpose:** Tool-wide settings and path configurations
**Location:** `mcqc_globals_hspice.txt`
**Key Settings:**
```ini
template_deck_path = /path/to/templates/
template_lut_path = /path/to/lut/
valid_arc_types_list = ["min_pulse_width", "setup_rising", "hold_falling"]
cell_pattern_list = ["*SYNC*", "*ASYNC*", "*FF*", "*LATCH*"]
num_samples = 1000
table_points_list = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
```

### Layer 3: Chartcl File (Library-Specific Configuration)
**Purpose:** Library characterization parameters
**Location:** `char_*.tcl` (varies by library)
**Key Variables:**
```tcl
set mpw_input_threshold {
    SYNC2_0 {in1 {1.0} in2 {1.5}}
    ASYNC_FF {D {0.8} CLK {1.2}}
}
set constraint_glitch_peak {
    default: 0.05
    sensitive_cells: 0.02
}
set constraint_delay_degrade {
    max_degrade_percent: 10
    warning_threshold: 5
}
```

### Layer 4: Template File (Arc Definitions)
**Purpose:** Cell and timing arc metadata
**Location:** `template_*.tcl` (varies by library)
**Structure:**
```tcl
cell(SYNC2_X1) {
    pin(CP) {
        direction: input;
        capacitance: 0.01;
    }
    pin(Q) {
        direction: output;
        timing() {
            timing_type: min_pulse_width;
            related_pin: "CP";
            when: "!RESET & !SET";
        }
    }
}
```

### Layer 5: Template SPICE Decks (Simulation Templates)
**Purpose:** Base SPICE circuit structures
**Location:** Template deck directory (per globals file)
**Variables:**
```spice
* Template variables for substitution
$probe_pin
$vdd_value
$temperature
$model_file
$vector_settings
$timing_measurements
```

### Layer 6: Hardcoded Python Logic (Implementation Rules)
**Purpose:** Business logic and pattern matching
**Location:** Multiple Python files
**Examples:**
```python
# In flow/funcs.py (18K lines of mappings)
if fnmatch.fnmatch(cell_name, "*SYNC2*"):
    template_name = "min_pulse_width/template__sync2__CP__rise__fall__1.sp"

# In spiceDeckMaker/funcs.py (final-state thresholds)
THRESHOLD_LOW = "0.05"
THRESHOLD_HIGH = "0.95"
MEASUREMENT_TIME = "50u"

# Cell pattern matching
ICG_PATTERNS = ["ICG*", "*CLK_GATE*"]
MB_AN2_PATTERN = "MB.*AN2"
```

## Configuration Interaction Matrix

| Layer | Type | Precedence | Override Capability | Validation | Error Handling |
|-------|------|-----------|-------------------|------------|----------------|
| 1. Command Line | Runtime | Highest | Can override all | None | Basic argparse |
| 2. Globals File | File-based | High | Overrides 3-6 | File existence | FileNotFound |
| 3. Chartcl File | File-based | Medium | Overrides 4-6 | TCL syntax | Parse errors |
| 4. Template File | File-based | Medium-Low | Overrides 5-6 | TCL syntax | Parse errors |
| 5. Template Decks | File-based | Low | Template only | File existence | Missing templates |
| 6. Python Logic | Hardcoded | Lowest | None | None | Runtime errors |

## Configuration Conflicts & Issues

### Issue 1: No Precedence Resolution
**Problem:** Multiple layers can define the same parameter
**Example:**
```
Command line: --num_samples 500
Globals file: num_samples = 1000
Chartcl file: num_samples = 2000
```
**Impact:** Undefined behavior, last-wins semantics

### Issue 2: Missing Validation
**Problem:** No consistency checking between layers
**Example:**
```
Globals: template_deck_path = /invalid/path/
Python: Expects specific template files to exist
```
**Impact:** Runtime failures with unclear error messages

### Issue 3: Scattered Magic Numbers
**Problem:** Critical values hardcoded in Python
**Examples:**
```python
# spiceDeckMaker/funcs.py
final_state_time = "50u"        # Should be configurable
threshold_low = "0.05"          # Should be in globals
threshold_high = "0.95"         # Should be in globals

# timingArcInfo/funcs.py
mpw_multiplier = 2.5            # Should be in chartcl
base_offset = 0.5               # Should be in chartcl
```

### Issue 4: Path Dependencies
**Problem:** Complex path resolution with no validation
**Chain:**
```
Command line --template_lut_path
  ↓
Globals file template_deck_path
  ↓
Template file references
  ↓
Template deck file locations
  ↓
Python hardcoded patterns
```

## Current Configuration Flow

```
Application Start
├─> Parse command line arguments
├─> Load globals file (if specified)
├─> Resolve template_lut_path and kit_path
├─> Load chartcl file from kit_path
├─> Parse template file from kit_path
├─> Load template deck files from template_deck_path
├─> Apply hardcoded Python logic
└─> Begin processing (no validation step)
```

## Proposed Configuration Schema

### Unified Configuration Structure
```yaml
mcqc_config:
  version: "1.0"

  # Environment settings
  paths:
    template_deck_path: "/path/to/templates/"
    template_lut_path: "/path/to/lut/"
    kit_path: "/path/to/kit/"
    output_path: "./output/"

  # Simulation parameters
  simulation:
    num_samples: 1000
    temperature: 25
    vdd_value: 1.0
    timing:
      measurement_time: "50u"
      threshold_low: 0.05
      threshold_high: 0.95

  # Arc processing
  arc_types:
    - "min_pulse_width"
    - "setup_rising"
    - "hold_falling"

  # Cell patterns (externalized from Python)
  cell_patterns:
    sync_cells: ["*SYNC*", "*FF*"]
    async_cells: ["*ASYNC*", "*LATCH*"]
    icg_cells: ["ICG*", "*CLK_GATE*"]
    mb_an2_cells: ["MB.*AN2"]

  # Final-state logic (externalized from Python)
  final_state_rules:
    - name: "SE_SA_C_conditions"
      trigger:
        when_contains: ["SE", "!SA", "C"]
      action: "add_vector_based_measurements"
      priority: 1

    - name: "Q_QN_vector_logic"
      trigger:
        has_data_vectors: true
        probe_pins: ["Q*", "QN*"]
      action: "add_complementary_measurements"
      priority: 1

    - name: "ICG_override"
      trigger:
        cell_pattern: "ICG*"
      action: "modify_and_add_measurements"
      threshold_override: 0.95
      priority: 2

  # Template mapping (externalized from 18K line file)
  template_mapping:
    - cell_pattern: "*SYNC2*"
      arc_type: "min_pulse_width"
      template: "min_pulse_width/template__sync2__CP__rise__fall__1.sp"

    - cell_pattern: "*ASYNC*"
      arc_type: "min_pulse_width"
      template: "min_pulse_width/template__async__D__rise__fall__1.sp"
```

### Configuration Validation Rules
```yaml
validation_rules:
  - check: "path_existence"
    paths: ["template_deck_path", "template_lut_path", "kit_path"]

  - check: "threshold_ranges"
    constraints:
      threshold_low: [0.0, 0.5]
      threshold_high: [0.5, 1.0]

  - check: "template_file_existence"
    templates: ["all_referenced_templates"]

  - check: "pattern_syntax"
    patterns: ["all_cell_patterns"]
```

## Migration Strategy

### Phase 1: Configuration Consolidation (2 weeks)
1. **Audit current configuration sources**
2. **Extract all hardcoded values to temporary config files**
3. **Create configuration loader with validation**
4. **Implement backward compatibility layer**

### Phase 2: Schema Implementation (2 weeks)
1. **Design unified YAML schema**
2. **Implement configuration parser with precedence rules**
3. **Add comprehensive validation**
4. **Create configuration migration tools**

### Phase 3: Gradual Migration (2 weeks)
1. **Migrate globals file settings first**
2. **Externalize Python hardcoded patterns**
3. **Consolidate chartcl and template configurations**
4. **Remove backward compatibility layer**

## Benefits of Unified Configuration

### Maintainability
- **Single source of truth** for all configuration
- **Version control** for configuration changes
- **Clear precedence rules** prevent conflicts

### Reliability
- **Comprehensive validation** catches errors early
- **Better error messages** with configuration context
- **Consistent behavior** across environments

### Extensibility
- **Easy addition** of new cell types via configuration
- **No code changes** required for pattern updates
- **Template mapping** becomes data-driven

This configuration analysis reveals that moving from 6 scattered configuration layers to a unified, validated schema would dramatically improve tool maintainability and reliability.