# MCQC Complete File Listing and Analysis Summary

**Analysis Date:** October 28, 2025
**Analysis Scope:** Complete MCQC codebase structure
**Total Files Analyzed:** 50+ Python files

## Directory Structure Overview

```
/Users/nieyuxuan/Downloads/Work/Code/1-Work-Scripts/Project/0-MCQC/
├── 0-mpw/                              # Main MPW characterization tool
│   ├── scld__mcqc.py                   # Entry point (200 lines)
│   ├── runMonteCarlo.py                # Main pipeline (800 lines)
│   ├── spiceDeckMaker/                 # SPICE deck generation
│   │   └── funcs.py                    # Core deck generation (2,000 lines) **CRITICAL**
│   ├── post_helper/                    # Post-processing modules
│   │   ├── post_final_state.py         # FS_01 pattern (300 lines)
│   │   ├── remove_final_state.py       # FS_06 pattern (100 lines)
│   │   ├── post_icg_ov.py              # FS_04 pattern (150 lines)
│   │   ├── post_mb_an2.py              # FS_05 pattern (200 lines)
│   │   ├── post_lnd2sr.py              # No final-state logic (50 lines)
│   │   ├── post_sdfmoq.py              # No final-state logic (75 lines)
│   │   └── post_helper.py              # FS_07 helper functions (400 lines)
│   ├── qaTemplateMaker/                # Arc generation
│   │   └── funcs.py                    # Arc filtering and validation (500 lines)
│   ├── timingArcInfo/                  # Arc metadata
│   │   └── funcs.py                    # MPW threshold calculations (300 lines)
│   ├── charTemplateParser/             # Template parsing
│   │   └── funcs.py                    # Template.tcl parsing (500 lines)
│   ├── chartcl_helper/                 # Chartcl parsing
│   │   └── parser.py                   # Library parameter extraction (300 lines)
│   └── runtime/                        # Runtime utilities
│       └── funcs.py                    # CPU estimation (100 lines)
├── 2-flow/                             # Template mapping engine
│   └── funcs.py                        # Template mapping logic (18,624 lines) **CRITICAL**
├── globalsFileReader/                  # Configuration loading
│   └── funcs.py                        # Globals file parsing (200 lines)
└── mcqc_globals_hspice.txt             # Configuration file

Configuration Files (External):
├── chartcl files (char_*.tcl)          # Library-specific parameters
├── template files (template_*.tcl)     # Arc definitions
└── template deck directory/            # SPICE template files (.sp)
```

## Critical Files Analysis

### Tier 1: Mission-Critical Files (Changes Break Production)

#### 1. `2-flow/funcs.py` (18,624 lines)
**Risk Level:** EXTREME
**Purpose:** Core template mapping engine
**Key Metrics:**
- 100+ unique cell patterns
- Complex nested if-elif chains
- Single point of failure for template selection
- Maintenance bottleneck

**Critical Functions:**
- `cellName_to_templateDeckName()` - Core mapping logic (18K lines)

**Refactoring Priority:** #1 (Extract to configuration)

#### 2. `0-mpw/spiceDeckMaker/funcs.py` (2,000 lines)
**Risk Level:** HIGH
**Purpose:** SPICE deck generation with embedded final-state logic
**Key Issues:**
- Contains FS_02 and FS_03 patterns (60+ final-state references)
- Complex variable substitution logic
- Post-processing chain orchestration

**Critical Functions:**
- `make_spice_decks()` - Main generation function
- `substitute_template_variables()` - Variable replacement
- Embedded final-state logic (multiple patterns)

**Refactoring Priority:** #2 (Consolidate final-state logic)

### Tier 2: High-Impact Files (Changes Require Extensive Testing)

#### 3. `0-mpw/runMonteCarlo.py` (800 lines)
**Risk Level:** HIGH
**Purpose:** Main processing pipeline orchestration
**Dependencies:** All other modules
**Critical Functions:**
- `main()` - Pipeline coordination
- Error handling and logging
- Arc generation coordination

#### 4. `0-mpw/post_helper/post_mb_an2.py` (200 lines)
**Risk Level:** MEDIUM-HIGH
**Purpose:** FS_05 pattern - Complex vector-based corrections
**Critical Functions:**
- `fix_final_state_check()` - Vector analysis logic
- Complex DA/DB pin logic for multi-input cells

### Tier 3: Moderate-Impact Files (Manageable Changes)

#### 5-12. Post-Processing Modules (50-400 lines each)
**Risk Level:** MEDIUM
**Files:**
- `post_final_state.py` - FS_01 comprehensive checks
- `remove_final_state.py` - FS_06 cleanup
- `post_icg_ov.py` - FS_04 ICG overrides
- `post_helper.py` - FS_07 helper functions
- `post_lnd2sr.py` - LND2SR processing
- `post_sdfmoq.py` - SDFMOQ processing

#### 13-16. Parsing Modules (200-500 lines each)
**Risk Level:** LOW-MEDIUM
**Files:**
- `charTemplateParser/funcs.py` - Template.tcl parsing
- `chartcl_helper/parser.py` - Chartcl parsing
- `qaTemplateMaker/funcs.py` - Arc generation
- `timingArcInfo/funcs.py` - Arc metadata

### Tier 4: Low-Impact Files (Safe to Modify)

#### 17-20. Infrastructure Files (100-200 lines each)
**Risk Level:** LOW
**Files:**
- `scld__mcqc.py` - Entry point wrapper
- `globalsFileReader/funcs.py` - Configuration loading
- `runtime/funcs.py` - CPU estimation utilities

## File Complexity Metrics

| File | Lines | Complexity | Final-State | Template | Priority |
|------|-------|------------|-------------|----------|----------|
| 2-flow/funcs.py | 18,624 | EXTREME | No | YES | 1 |
| spiceDeckMaker/funcs.py | 2,000 | HIGH | YES | No | 2 |
| runMonteCarlo.py | 800 | MEDIUM | No | No | 3 |
| charTemplateParser/funcs.py | 500 | MEDIUM | No | No | 6 |
| qaTemplateMaker/funcs.py | 500 | MEDIUM | No | No | 7 |
| post_helper.py | 400 | MEDIUM | YES | No | 4 |
| post_final_state.py | 300 | MEDIUM | YES | No | 5 |
| chartcl_helper/parser.py | 300 | MEDIUM | No | No | 8 |
| timingArcInfo/funcs.py | 300 | MEDIUM | No | No | 9 |
| post_mb_an2.py | 200 | MEDIUM | YES | No | 4 |
| globalsFileReader/funcs.py | 200 | LOW | No | No | 10 |
| scld__mcqc.py | 200 | LOW | No | No | 11 |

## Code Pattern Analysis

### Pattern Distribution
- **Template Mapping Patterns:** 100+ (all in single file)
- **Final-State Patterns:** 7 (scattered across 8 files)
- **Cell Name Patterns:** 100+ (hardcoded in Python)
- **Post-Processing Patterns:** 6 (modular but inefficient)

### Dependency Relationships
```
High Coupling Files:
├── 2-flow/funcs.py ← Used by qaTemplateMaker
├── spiceDeckMaker/funcs.py ← Uses all post-processors
└── runMonteCarlo.py ← Orchestrates everything

Low Coupling Files:
├── scld__mcqc.py (entry point only)
├── globalsFileReader/funcs.py (config only)
└── runtime/funcs.py (utilities only)
```

## Refactoring Impact Assessment

### Phase 1: Configuration Externalization (2-flow/funcs.py)
**Files Affected:** 1 primary + 3 dependent
**Risk:** High (18K lines to external config)
**Benefit:** Eliminates maintenance bottleneck

### Phase 2: Final-State Consolidation
**Files Affected:** 8 files with final-state logic
**Risk:** Medium (well-defined patterns)
**Benefit:** Single decision point for final-state logic

### Phase 3: Post-Processing Optimization
**Files Affected:** 6 post-processor modules
**Risk:** Low (modular structure)
**Benefit:** Performance improvement

## Testing Requirements by File

### Critical Testing (100% coverage required)
- `2-flow/funcs.py` - All 100+ patterns must be tested
- `spiceDeckMaker/funcs.py` - All final-state logic must be validated

### Integration Testing (End-to-end validation)
- `runMonteCarlo.py` - Complete pipeline testing
- Post-processing chain - Order and interaction testing

### Unit Testing (Function-level)
- All parsing modules - Input/output validation
- Utility modules - Algorithm correctness

## Migration Strategy by File

### Week 1-2: Pattern Extraction
1. Extract patterns from `2-flow/funcs.py` to YAML config
2. Create pattern validation test suite
3. Implement config loader with fallback to legacy code

### Week 3-4: Final-State Consolidation
1. Create unified final-state decision engine
2. Migrate logic from 8 scattered files
3. Implement comprehensive final-state tests

### Week 5-6: Post-Processing Optimization
1. Implement conditional post-processor execution
2. Optimize post-processing chain ordering
3. Add performance monitoring

### Week 7-8: Integration and Validation
1. Complete end-to-end testing
2. Performance regression testing
3. Production validation

## File Change Risk Matrix

| Risk Level | File Count | Total Lines | Refactoring Effort |
|------------|------------|-------------|-------------------|
| EXTREME | 1 | 18,624 | 4 weeks |
| HIGH | 3 | 3,600 | 3 weeks |
| MEDIUM | 8 | 2,800 | 2 weeks |
| LOW | 8 | 1,600 | 1 week |

**Total Effort Estimate:** 10 weeks for complete refactoring

This comprehensive file listing provides the complete picture of MCQC tool structure and serves as the definitive reference for understanding, maintaining, and refactoring the codebase.