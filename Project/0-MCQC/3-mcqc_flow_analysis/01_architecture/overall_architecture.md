# MCQC Tool Overall Architecture

**Analysis Date:** October 28, 2025
**Tool Version:** MPW 3.5.3
**Architecture Type:** Monolithic with pipeline processing

## High-Level Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    MCQC TOOL ARCHITECTURE                   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  INPUT LAYER                                                │
│  ├── Command Line Args (--globals_file, --lib_type, etc.)  │
│  ├── Globals File (mcqc_globals_hspice.txt)                │
│  ├── Chartcl File (char_*.tcl)                             │
│  ├── Template File (template_*.tcl)                        │
│  └── Template SPICE Decks (*.sp)                           │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  PROCESSING PIPELINE                                        │
│  ┌─────────────────────────────────────────────────────┐  │
│  │ 1. CONFIGURATION LOADING                            │  │
│  │    ├── globalsFileReader.py                         │  │
│  │    ├── Path resolution & validation                  │  │
│  │    └── User options dictionary creation              │  │
│  └─────────────────────────────────────────────────────┘  │
│  ┌─────────────────────────────────────────────────────┐  │
│  │ 2. CHARTCL PARSING                                  │  │
│  │    ├── chartcl_helper/parser.py                     │  │
│  │    ├── Variable extraction (mpw_input_threshold)     │  │
│  │    ├── Condition parsing (load, glitch, degrade)    │  │
│  │    └── Cell list extraction                         │  │
│  └─────────────────────────────────────────────────────┘  │
│  ┌─────────────────────────────────────────────────────┐  │
│  │ 3. TEMPLATE PARSING                                 │  │
│  │    ├── charTemplateParser/funcs.py                  │  │
│  │    ├── Arc definition extraction                     │  │
│  │    ├── Cell and pin relationship mapping            │  │
│  │    └── TemplateInfo object creation                 │  │
│  └─────────────────────────────────────────────────────┘  │
│  ┌─────────────────────────────────────────────────────┐  │
│  │ 4. ARC EXTRACTION                                   │  │
│  │    ├── qaTemplateMaker/funcs.py                     │  │
│  │    ├── Template mapping (flow/funcs.py 18K lines)   │  │
│  │    ├── Arc filtering & validation                    │  │
│  │    └── QA arcs list generation                      │  │
│  └─────────────────────────────────────────────────────┘  │
│  ┌─────────────────────────────────────────────────────┐  │
│  │ 5. SPICE INFO CREATION                              │  │
│  │    ├── timingArcInfo/funcs.py                       │  │
│  │    ├── MPW threshold calculation                     │  │
│  │    ├── Arc metadata population                       │  │
│  │    └── Spice_info dictionary creation               │  │
│  └─────────────────────────────────────────────────────┘  │
│  ┌─────────────────────────────────────────────────────┐  │
│  │ 6. SPICE DECK GENERATION                            │  │
│  │    ├── spiceDeckMaker/funcs.py                      │  │
│  │    ├── Template substitution ($-variables)           │  │
│  │    ├── Final-state logic (7 patterns)               │  │
│  │    └── Write_list buffer creation                    │  │
│  └─────────────────────────────────────────────────────┘  │
│  ┌─────────────────────────────────────────────────────┐  │
│  │ 7. POST-PROCESSING CHAIN                            │  │
│  │    ├── post_icg_ov (ICG cells)                      │  │
│  │    ├── post_lnd2sr (LND2SR cells)                   │  │
│  │    ├── post_mb_an2 (MB_AN2 cells)                   │  │
│  │    ├── post_sdfmoq (SDFMOQ cells)                   │  │
│  │    ├── remove_final_state (cleanup)                 │  │
│  │    └── post_final_state (conditional)               │  │
│  └─────────────────────────────────────────────────────┘  │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  OUTPUT LAYER                                               │
│  ├── SPICE Deck Files (nominal_sim.sp, mc_sim.sp)          │
│  ├── Directory Structure (arc-specific folders)             │
│  └── Header Information (metadata, paths, parameters)       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Component Details

### Core Components

#### 1. Main Orchestrator
**File:** `scld__mcqc.py`
**Function:** Entry point and high-level flow control
**Key Responsibilities:**
- Command line argument parsing
- Configuration loading and validation
- Library path resolution
- Main execution coordination

#### 2. Monte Carlo Runner
**File:** `runMonteCarlo.py`
**Function:** Core processing pipeline orchestration
**Key Responsibilities:**
- Pipeline stage coordination
- Error handling and logging
- CPU estimation logic
- Output file management

#### 3. Template Mapping Engine
**File:** `2-flow/funcs.py` (18,624 lines)
**Function:** Maps arc characteristics to template files
**Key Responsibilities:**
- Cell pattern matching (100+ patterns)
- Arc type classification
- Template selection logic
- Complex conditional mapping

#### 4. Final-State Logic Engine
**Files:** Multiple (8 files)
**Function:** Adds/modifies/removes final-state measurements
**Key Responsibilities:**
- Pattern detection (7 distinct patterns)
- Measurement generation
- Threshold management
- State validation

### Data Flow Architecture

#### Stage 1: Input Processing
```
Command Line Args → parseInputArgs() → user_options dict
Globals File → globalsFileReader → user_options (merged)
Library Paths → path resolution → validated paths
```

#### Stage 2: Library Analysis
```
Chartcl File → ChartclParser → variables + conditions
Template File → TemplateParser → template_info object
Cell/Arc definitions → extracted metadata
```

#### Stage 3: Arc Generation
```
template_info + filters → qaTemplateMaker → qa_arcs list
Template mapping → flow/funcs.py → template selection
Arc validation → filtering → final arc list
```

#### Stage 4: SPICE Deck Assembly
```
qa_arcs → timingArcInfo → spice_info dict
Template files → spiceDeckMaker → write_list buffers
Final-state logic → pattern matching → measurements added
Post-processing → modification chain → final buffers
```

#### Stage 5: Output Generation
```
write_list buffers → file writing → nominal/MC SPICE decks
Directory creation → organization → arc-specific folders
Metadata → header generation → documentation
```

## Architectural Patterns

### Design Patterns Used

#### 1. Pipeline Pattern
- Sequential processing stages
- Each stage transforms data for next stage
- Clear input/output interfaces

#### 2. Strategy Pattern (Implicit)
- Different template mapping strategies
- Multiple final-state logic strategies
- Post-processing strategy selection

#### 3. Builder Pattern (Implicit)
- SPICE deck construction via write_list
- Incremental buffer building
- Complex object assembly

### Anti-Patterns Present

#### 1. God Object
- `flow/funcs.py` with 18K lines
- `spiceDeckMaker/funcs.py` with complex logic
- Single files handling too many responsibilities

#### 2. Magic Numbers
- Hardcoded thresholds (0.05, 0.95)
- Hardcoded timing (50u)
- Hardcoded formulas (2.5*(x-0.5))

#### 3. Shotgun Surgery
- Final-state logic scattered across 8 files
- Pattern matching distributed throughout codebase
- No single point of control

## Configuration Architecture

### Current Configuration Sources (6 layers)
```
1. Command Line Arguments (highest precedence)
   ├── --lib_type, --lg, --vt, --corner
   └── --output_path, --globals_file

2. Globals File (mcqc_globals_hspice.txt)
   ├── template_deck_path, template_lut_path
   ├── valid_arc_types_list, cell_pattern_list
   └── num_samples, table_points_list

3. Chartcl File (char_*.tcl)
   ├── mpw_input_threshold
   ├── constraint_glitch_peak, constraint_delay_degrade
   └── Cell-specific conditions

4. Template File (template_*.tcl)
   ├── Arc definitions (timing_type, when, related_pin)
   ├── Cell and pin relationships
   └── Timing indices and tables

5. Template SPICE Decks (*.sp files)
   ├── Base SPICE structure
   ├── $-substitution variables
   └── Measurement statement templates

6. Hardcoded Python Logic (multiple files)
   ├── Cell name patterns
   ├── Final-state logic patterns
   └── Post-processing rules
```

### Configuration Precedence Issues
- No clear precedence order defined
- Potential conflicts between layers
- No validation of consistency
- Hidden dependencies on naming conventions

## Module Dependencies

### Core Dependency Graph
```
scld__mcqc.py
├── globalsFileReader.funcs
├── hybrid_char_helper
└── runMonteCarlo
    ├── qaTemplateMaker.funcs
    │   └── templateFileMap.funcs (→ 2-flow/funcs.py)
    ├── arcFilters.funcs
    ├── spiceDeckMaker.funcs
    │   ├── post_icg_ov
    │   ├── post_lnd2sr
    │   ├── post_mb_an2
    │   ├── post_sdfmoq
    │   ├── remove_final_state
    │   └── post_final_state
    ├── timingArcInfo.funcs
    ├── charTemplateParser.funcs
    ├── chartcl_helper.parser
    └── runtime.funcs
```

### External Dependencies
- Python standard library
- Template LUT path (external directory)
- Kit path (external library structure)
- Model files (external process technology)

## Performance Characteristics

### Bottlenecks Identified
1. **Template Mapping:** 18K line file parsing and pattern matching
2. **Final-State Logic:** Multiple pattern evaluations per arc
3. **Post-Processing Chain:** 6 processors run on every arc
4. **File I/O:** Template file reading and SPICE deck writing

### Scalability Limits
- **Cell Types:** Adding new cells requires code modification
- **Pattern Complexity:** No systematic pattern organization
- **Memory Usage:** Large template mapping loaded into memory
- **Processing Time:** Linear scaling with number of arcs

## Security & Reliability

### Security Considerations
- **Path Injection:** User-provided paths not validated
- **Code Injection:** Template files could contain malicious content
- **Resource Exhaustion:** No limits on output file generation

### Reliability Issues
- **Error Handling:** Inconsistent error reporting
- **Validation:** No input validation framework
- **Recovery:** No graceful degradation mechanisms
- **Logging:** Limited debugging information

## Architectural Debt

### Technical Debt Assessment
- **Complexity Debt:** Extremely high (18K line files)
- **Documentation Debt:** High (undocumented patterns)
- **Test Debt:** Critical (no visible test framework)
- **Configuration Debt:** High (scattered configuration)

### Refactoring Priorities
1. **Configuration Consolidation:** Unify all configuration sources
2. **Template Mapping Externalization:** Move patterns to config files
3. **Final-State Logic Consolidation:** Single decision point
4. **Post-Processing Optimization:** Conditional execution

This architectural analysis reveals a functionally complete but structurally complex system that would benefit significantly from systematic refactoring to improve maintainability and extensibility.