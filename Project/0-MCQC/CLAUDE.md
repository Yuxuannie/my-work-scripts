# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is the MCQC (Monte Carlo QC) tool for semiconductor library characterization, specifically focused on MPW (min_pulse_width) timing characterization. The tool generates SPICE simulation decks for library validation and timing analysis.

## Architecture

### Core Processing Pipeline
The MCQC tool follows a pipeline architecture:

1. **Entry Point**: `0-mpw/scld__mcqc.py` - Main CLI interface
2. **Pipeline Orchestrator**: `0-mpw/runMonteCarlo.py` - Coordinates all processing stages
3. **Template Mapping Engine**: `2-flow/funcs.py` - **CRITICAL 18,624-line file** that maps cell patterns to SPICE templates
4. **SPICE Deck Generation**: `0-mpw/spiceDeckMaker/funcs.py` - Generates final simulation decks
5. **Post-Processing Chain**: `0-mpw/post_helper/` - Applies cell-specific modifications

### Key Data Structures
- **arc_info**: Dictionary containing arc metadata (cell_name, timing_type, related_pin, when conditions)
- **template_info**: Parsed template.tcl data with cell and timing arc definitions
- **write_list**: Buffer for SPICE deck content that gets modified through post-processing
- **qa_arcs**: List of arcs to be characterized after filtering

### Critical Discovery: Hidden Final-State Logic
The tool contains **7 distinct final-state logic patterns** affecting 74% of generated arcs:
- **FS_01**: AMD template path pattern (`_AMD_` in template path)
- **FS_02**: SE/SA/C when condition logic (embedded in main generation)
- **FS_03**: Q/QN vector-based logic (embedded in main generation)
- **FS_04**: ICG cell override pattern
- **FS_05**: MB_AN2 correction pattern
- **FS_06**: Remove/cleanup pattern
- **FS_07**: Helper function patterns

## Running the Tool

### Basic MPW Characterization
```bash
cd 0-mpw/
python scld__mcqc.py \
    --globals_file ../2-flow/mcqc_globals_hspice.txt \
    --lib_type SNPS \
    --lg 16 \
    --vt SVT \
    --corner TT \
    --output_path ./output/
```

### Configuration Files Required
- **Globals file**: `2-flow/mcqc_globals_hspice.txt` - Tool-wide settings
- **Chartcl file**: Library-specific characterization parameters
- **Template file**: Arc definitions and timing specifications
- **Template decks**: SPICE template files in `2-flow/min_pulse_width/`

## Validation and Analysis Tools

### Critical: Use Validation Tools Before Modifying
Located in `3-mcqc_flow_analysis/validation_tools/`, these tools are essential for understanding current behavior:

```bash
cd 3-mcqc_flow_analysis/validation_tools/

# Analyze generated SPICE decks to discover patterns
python validate_deck_structure.py --deck_dir /path/to/DECKS/ --output deck_analysis.csv

# Discover cell name patterns that correlate with behaviors
python discover_cell_patterns.py --analysis_csv deck_analysis.csv --output patterns.json

# Map template usage to actual behaviors
python correlate_template_to_output.py --analysis_csv deck_analysis.csv --output correlation.json

# Validate discovered patterns match expected statistics
python test_flow_validation.py --analysis_csv deck_analysis.csv --test_type all
```

## Critical Files and Risk Assessment

### EXTREME RISK (Breaks production if modified incorrectly)
- `2-flow/funcs.py` - 18,624 lines of template mapping logic
- `0-mpw/spiceDeckMaker/funcs.py` - Core deck generation with embedded final-state logic

### HIGH RISK (Requires extensive testing)
- `0-mpw/runMonteCarlo.py` - Main processing pipeline
- `0-mpw/post_helper/post_mb_an2.py` - Complex vector-based corrections

### Known Issues and Patterns

#### Template Mapping Complexity
- **18,624 lines** of hardcoded cell-to-template mapping in `2-flow/funcs.py`
- 100+ unique cell patterns using fnmatch expressions
- Adding new cell types requires deep code analysis (currently 2-3 days)

#### Configuration Chaos
- **6 configuration layers** with no unified management
- Potential conflicts between command line, globals file, chartcl, and hardcoded logic
- No validation of configuration consistency

#### Final-State Logic Distribution
- 74% of arcs get final-state measurements through 7 different patterns
- Logic scattered across 8 files without centralized control
- No documentation of when each pattern applies

## Development Guidelines

### Before Making Changes
1. **ALWAYS** run validation tools first to understand current behavior
2. Use `3-mcqc_flow_analysis/05_code_locations/critical_files.md` to assess modification risk
3. Review `3-mcqc_flow_analysis/03_pattern_analysis/final_state_patterns.md` for final-state impacts

### Adding New Cell Types
1. **Current Process**: Modify `2-flow/funcs.py` (high risk, 2-3 days)
2. **Recommended**: Use validation tools to understand existing patterns first
3. **Future**: Follow refactoring proposal to externalize patterns to configuration

### Testing Requirements
- **No formal test framework exists** - this is a critical gap
- Use validation tools in `3-mcqc_flow_analysis/validation_tools/` for regression testing
- Always validate that final-state coverage remains at expected ~74%

## Architecture Analysis

The complete architectural analysis is available in `3-mcqc_flow_analysis/` with:
- **Executive summary** of findings and business impact
- **Detailed architecture** documentation with data flow
- **Issue catalog** with 16 identified issues (7 critical)
- **Refactoring proposal** with phase-by-phase approach
- **Pattern analysis** documenting all hidden logic
- **EDA tool compatibility** assessment

### Key Insight: Specification Gap
The tool contains significant behavior (74% final-state logic, 14.9% cp2q_del2) that has no specification in template*.tcl files and cannot be reproduced by industry-standard EDA tools (CDNS Liberate, SiliconSmart).

## Common Patterns

### Cell Name Pattern Matching
```python
# From 2-flow/funcs.py - one of 100+ patterns
if fnmatch.fnmatch(cell_name, "*SYNC2*"):
    template_name = "min_pulse_width/template__sync2__CP__rise__fall__1.sp"
```

### Final-State Logic Patterns
```python
# Embedded in spiceDeckMaker/funcs.py
if 'SE' in when or '!SA' in when or 'C' in when:
    # Complex vector-dependent final-state logic
    if vector[dpin_idx] == '0':
        if 'QN' in probe_pin:
            # Add final-state measurements
```

### Post-Processing Chain
```python
# Sequential modification of write_list
write_list = post_icg_ov.post_process(arc_info, write_list)
write_list = post_mb_an2.post_process(arc_info, write_list)
write_list = remove_final_state.post_process(arc_info, write_list)
```

This codebase requires careful analysis before modification due to complex interdependencies and hidden logic patterns. Use the validation tools extensively to understand behavior before making changes.