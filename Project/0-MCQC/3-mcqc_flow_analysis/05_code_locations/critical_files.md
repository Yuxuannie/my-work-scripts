# MCQC Critical Code Locations Reference

**Analysis Date:** October 28, 2025
**Total Files Analyzed:** 50+ Python files
**Critical Files Identified:** 12 files containing core logic

## Core Processing Files

### 1. Main Entry Point
**File:** `/Users/nieyuxuan/Downloads/Work/Code/1-Work-Scripts/Project/0-MCQC/0-mpw/scld__mcqc.py`
**Purpose:** Application entry point and high-level orchestration
**Key Functions:**
- `parseInputArgs()` - Command line argument processing
- `main()` - Application orchestration
**Lines of Code:** ~200
**Modification Frequency:** Low
**Critical Sections:**
```python
# Line 45-80: Argument parsing
def parseInputArgs():
    parser.add_argument('--lib_type', required=True)
    parser.add_argument('--lg', required=True)
    parser.add_argument('--vt', required=True)

# Line 120-150: Main orchestration
def main():
    user_options = parseInputArgs()
    user_options = globalsFileReader.funcs.read_globals_file(user_options)
    runMonteCarlo.main(user_options)
```

### 2. Core Processing Pipeline
**File:** `/Users/nieyuxuan/Downloads/Work/Code/1-Work-Scripts/Project/0-MCQC/0-mpw/runMonteCarlo.py`
**Purpose:** Main processing pipeline orchestration
**Key Functions:**
- `main()` - Pipeline coordination
- `estimate_runtime()` - Resource planning
**Lines of Code:** ~800
**Modification Frequency:** Medium
**Critical Sections:**
```python
# Line 50-100: Template parsing
template_info = charTemplateParser.funcs.extract_info_from_template(
    user_options["template_file_path"])

# Line 150-200: Arc generation
qa_arcs = qaTemplateMaker.funcs.generate_qa_arc_list(
    user_options, template_info, chartcl_vars)

# Line 250-300: SPICE deck creation
spiceDeckMaker.funcs.make_spice_decks(user_options, qa_arcs)
```

## Template Mapping Engine

### 3. Template Mapping Logic (CRITICAL)
**File:** `/Users/nieyuxuan/Downloads/Work/Code/1-Work-Scripts/Project/0-MCQC/2-flow/funcs.py`
**Purpose:** Maps cell patterns to template files
**Key Functions:**
- `cellName_to_templateDeckName()` - Core mapping logic
**Lines of Code:** 18,624 (EXTREMELY LARGE)
**Modification Frequency:** High (new cells require changes)
**Critical Sections:**
```python
# Line 100-18500: Massive template mapping logic
def cellName_to_templateDeckName(cell_name, arc_info, user_options):
    if fnmatch.fnmatch(cell_name, "*SYNC2*"):
        if arc_type == "min_pulse_width":
            template_name = "min_pulse_width/template__sync2__CP__rise__fall__1.sp"

    # 18,000+ lines of similar pattern matching
    elif fnmatch.fnmatch(cell_name, "MB*AN2*"):
        # More complex logic
    # ... hundreds more patterns
```

## SPICE Deck Generation

### 4. SPICE Deck Maker (CRITICAL)
**File:** `/Users/nieyuxuan/Downloads/Work/Code/1-Work-Scripts/Project/0-MCQC/0-mpw/spiceDeckMaker/funcs.py`
**Purpose:** Generates final SPICE simulation decks
**Key Functions:**
- `make_spice_decks()` - Main deck generation
- `substitute_template_variables()` - Variable substitution
**Lines of Code:** ~2,000
**Modification Frequency:** High (final-state logic changes)
**Critical Sections:**
```python
# Line 100-200: Template loading and substitution
def make_spice_decks(user_options, qa_arcs):
    for arc_info in qa_arcs:
        template_content = load_template(arc_info['TEMPLATE_DECK_PATH'])
        write_list = substitute_variables(template_content, arc_info)

# Line 400-500: Embedded final-state logic (FS_02)
if 'SE' in when or '!SA' in when or 'C' in when:
    if 'SE' in when:
        # Complex SE logic with Q/QN pin handling

# Line 600-990: Q/QN vector logic (FS_03)
if vector[dpin_idx] == '0':
    if 'QN' in probe_pin:
        dpins_settings.append('.meas final_state find v(' + probe_pin + ') at=50u\n')
        dpins_settings.append(".meas final_state_check find par('1') at='final_state/vdd_value > 0.95 ? 0 : -1'\n")
```

## Final-State Logic Files

### 5. Post Final-State Processor
**File:** `/Users/nieyuxuan/Downloads/Work/Code/1-Work-Scripts/Project/0-MCQC/0-mpw/post_helper/post_final_state.py`
**Purpose:** Adds comprehensive final-state measurements (FS_01 pattern)
**Key Functions:**
- `post_process()` - Main processing function
**Lines of Code:** ~300
**Modification Frequency:** Low
**Critical Sections:**
```python
# Line 50-150: Final-state measurement addition
def post_process(arc_info, write_list):
    if '_AMD_' in arc_info['TEMPLATE_DECK_PATH']:
        write_list = add_comprehensive_final_state_measurements(write_list)
```

### 6. Remove Final-State Processor
**File:** `/Users/nieyuxuan/Downloads/Work/Code/1-Work-Scripts/Project/0-MCQC/0-mpw/post_helper/remove_final_state.py`
**Purpose:** Removes existing final-state measurements (FS_06 pattern)
**Key Functions:**
- `post_process()` - Cleanup function
**Lines of Code:** ~100
**Modification Frequency:** Low
**Critical Sections:**
```python
# Line 20-80: Final-state cleanup logic
def post_process(arc_info, write_list):
    cleaned_list = []
    for line in write_list:
        if not line.startswith('.meas final_state'):
            cleaned_list.append(line)
    return cleaned_list
```

### 7. ICG Override Processor
**File:** `/Users/nieyuxuan/Downloads/Work/Code/1-Work-Scripts/Project/0-MCQC/0-mpw/post_helper/post_icg_ov.py`
**Purpose:** ICG cell-specific final-state modifications (FS_04 pattern)
**Key Functions:**
- `post_process()` - ICG-specific processing
**Lines of Code:** ~150
**Modification Frequency:** Low
**Critical Sections:**
```python
# Line 30-40: ICG override logic
def post_process(arc_info, write_list):
    cell_name = arc_info['CELL_NAME']
    if any(fnmatch.fnmatch(cell_name, pattern) for pattern in ICG_PATTERNS):
        write_list = post_helper.replace_final_state_check(write_list, '0.95')
        write_list = post_helper.add_meas_final_state(write_list)
```

### 8. MB_AN2 Correction Processor
**File:** `/Users/nieyuxuan/Downloads/Work/Code/1-Work-Scripts/Project/0-MCQC/0-mpw/post_helper/post_mb_an2.py`
**Purpose:** MB_AN2 cell vector-based corrections (FS_05 pattern)
**Key Functions:**
- `post_process()` - Vector analysis and correction
- `fix_final_state_check()` - Core correction logic
**Lines of Code:** ~200
**Modification Frequency:** Medium
**Critical Sections:**
```python
# Line 40-75: Vector-based final-state correction
def fix_final_state_check(write_list, pinlist, vector):
    for i, line in enumerate(write_list):
        if line.startswith('.meas final_state_check'):
            qidx = pinlist.index(qpin)
            qvec = vector[qidx]
            if qvec == 'F':
                write_list[i] = line.replace('> 0.95', '< 0.05')
            elif qvec == 'R':
                write_list[i] = line.replace('< 0.05', '> 0.95')
```

### 9. Post-Processing Helper Functions
**File:** `/Users/nieyuxuan/Downloads/Work/Code/1-Work-Scripts/Project/0-MCQC/0-mpw/post_helper/post_helper.py`
**Purpose:** Shared helper functions for final-state manipulation (FS_07 pattern)
**Key Functions:**
- `add_meas_final_state()` - Standard measurement addition
- `replace_final_state_check()` - Threshold modification
**Lines of Code:** ~400
**Modification Frequency:** Medium
**Critical Sections:**
```python
# Line 230-260: Final-state addition helper
def add_meas_final_state(write_list):
    final_state_line = '.meas final_state find v('+probe+') at=50u\n'
    final_state_check_line = ".meas final_state_check find par('1') at='final_state/vdd_value < 0.05 ? 0 : -1'\n\n"

# Line 270-290: Final-state criteria replacement
def replace_final_state_check(write_list, check_ratio):
    keyword = "final_state/vdd_value"
    for i, line in enumerate(write_list):
        if keyword in line:
            if check_ratio == '0.95':
                write_list[i] = line.replace('< 0.05', '> 0.95')
```

## Configuration and Parsing Files

### 10. Globals File Reader
**File:** `/Users/nieyuxuan/Downloads/Work/Code/1-Work-Scripts/Project/0-MCQC/globalsFileReader/funcs.py`
**Purpose:** Reads and processes globals configuration file
**Key Functions:**
- `read_globals_file()` - Main configuration loading
**Lines of Code:** ~200
**Modification Frequency:** Low
**Critical Sections:**
```python
# Line 50-100: Globals file parsing
def read_globals_file(user_options):
    globals_content = read_file(user_options['globals_file'])
    parsed_config = parse_globals_format(globals_content)
    return merge_configs(user_options, parsed_config)
```

### 11. Chartcl Parser
**File:** `/Users/nieyuxuan/Downloads/Work/Code/1-Work-Scripts/Project/0-MCQC/chartcl_helper/parser.py`
**Purpose:** Parses chartcl files for library-specific parameters
**Key Functions:**
- `extract_chartcl_variables()` - Variable extraction
**Lines of Code:** ~300
**Modification Frequency:** Medium
**Critical Sections:**
```python
# Line 100-200: Chartcl variable extraction
def extract_chartcl_variables(chartcl_path):
    variables = {}
    variables['mpw_input_threshold'] = parse_mpw_thresholds(content)
    variables['constraint_glitch_peak'] = parse_constraints(content)
    return variables
```

### 12. Template Parser
**File:** `/Users/nieyuxuan/Downloads/Work/Code/1-Work-Scripts/Project/0-MCQC/charTemplateParser/funcs.py`
**Purpose:** Parses template.tcl files for arc definitions
**Key Functions:**
- `extract_info_from_template()` - Template parsing
**Lines of Code:** ~500
**Modification Frequency:** Low
**Critical Sections:**
```python
# Line 200-300: Template arc extraction
def extract_info_from_template(template_path):
    template_info = {}
    template_info['cells'] = parse_cell_definitions(content)
    template_info['arcs'] = parse_timing_arcs(content)
    return template_info
```

## File Dependency Map

```
scld__mcqc.py (Entry Point)
├── globalsFileReader/funcs.py
└── runMonteCarlo.py
    ├── chartcl_helper/parser.py
    ├── charTemplateParser/funcs.py
    ├── qaTemplateMaker/funcs.py
    │   └── 2-flow/funcs.py (18K lines!)
    └── spiceDeckMaker/funcs.py
        ├── post_helper/post_icg_ov.py
        ├── post_helper/post_lnd2sr.py
        ├── post_helper/post_mb_an2.py
        ├── post_helper/post_sdfmoq.py
        ├── post_helper/remove_final_state.py
        ├── post_helper/post_final_state.py
        └── post_helper/post_helper.py
```

## Modification Risk Assessment

### CRITICAL RISK (Changes likely to break production)
- `/2-flow/funcs.py` - 18K lines of template mapping
- `/spiceDeckMaker/funcs.py` - Core deck generation with embedded logic

### HIGH RISK (Changes require extensive testing)
- `/runMonteCarlo.py` - Main processing pipeline
- `/post_helper/post_mb_an2.py` - Complex vector logic

### MEDIUM RISK (Changes manageable with unit tests)
- `/chartcl_helper/parser.py` - Well-defined parsing
- `/post_helper/post_helper.py` - Helper functions

### LOW RISK (Changes unlikely to affect core functionality)
- `/scld__mcqc.py` - Entry point wrapper
- `/globalsFileReader/funcs.py` - Simple configuration reading

## Refactoring Priority Order

1. **Phase 1:** Extract patterns from `/2-flow/funcs.py` (18K lines → config file)
2. **Phase 2:** Consolidate final-state logic in `/spiceDeckMaker/funcs.py`
3. **Phase 3:** Unified configuration loading
4. **Phase 4:** Post-processor optimization

This code location reference provides the essential roadmap for understanding and maintaining the MCQC tool's complex codebase.