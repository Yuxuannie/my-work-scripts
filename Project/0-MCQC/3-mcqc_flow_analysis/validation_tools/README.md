# MCQC Validation Tools Package

**Purpose:** Comprehensive validation framework to audit the MCQC flow's current behavior and discover all hidden patterns before refactoring.

**Critical Context:** Based on analysis, we've discovered that 74% of arcs have final-state checks and 14.9% have cp2q_del2 measurements, but the patterns determining these behaviors are hidden in Python code without specification in template*.tcl files.

## 🎯 Primary Objective

Create tools that can **verify the flow's current behavior** and **identify ALL patterns**, not fix them yet. Focus on making these tools **USABLE immediately** to audit the existing flow.

## 🔧 Tool Overview

### 1. SPICE Deck Structure Validator (`validate_deck_structure.py`)
**Purpose:** Analyzes generated SPICE decks to identify patterns and validate completeness.

**Key Capabilities:**
- Extracts all measurement patterns from SPICE decks
- Identifies final-state checks, cp2q_del2, internal nodes
- Discovers post-processor signatures
- Generates comprehensive CSV reports with statistics

**Usage:**
```bash
# Analyze entire deck directory
python validate_deck_structure.py --deck_dir /work/MCQC_RUN/DECKS/ --output deck_analysis.csv

# Analyze single deck
python validate_deck_structure.py --single_deck /path/to/nominal_sim.sp --output single_analysis.json

# Verbose analysis with statistics
python validate_deck_structure.py --deck_dir /work/DECKS/ --output analysis.csv --verbose
```

**Expected Output:**
```csv
ArcFolder,CellName,ArcType,HasFinalState,NumFinalStateMeas,HasCp2qDel2,MeasurementProfile,TemplateUsed
mpw_SDFQ...,SDFQTXG...,mpw,YES,2,NO,FINAL_STATE_SINGLE,template__CP__fall__rise__1.sp
```

### 2. Template-to-Output Correlation Analyzer (`correlate_template_to_output.py`)
**Purpose:** Maps template files to actual deck characteristics to discover correlations.

**Key Capabilities:**
- Correlates template usage with final-state patterns
- Identifies strong behavioral correlations (>90% or <10%)
- Discovers template naming patterns
- Maps post-processor usage to templates

**Usage:**
```bash
# Analyze template correlations
python correlate_template_to_output.py --analysis_csv deck_analysis.csv --output template_correlation.json

# Generate human-readable summary
python correlate_template_to_output.py --analysis_csv analysis.csv --output corr.json --human_report summary.txt
```

**Expected Output:**
```
Template: template__CP__fall__rise__1.sp
  Total uses: 450 arcs
  Final-state: 332 arcs (74%)
  CP2Q_DEL2: 67 arcs (14.9%)
  Strong correlation: ALWAYS final-state (98.2%)
```

### 3. Cell Pattern Discovery Tool (`discover_cell_patterns.py`)
**Purpose:** Automatically discovers which cell name patterns correlate with specific behaviors using statistical analysis.

**Key Capabilities:**
- Discovers exact cell name patterns
- Finds prefix/suffix patterns
- Tests regex and wildcard patterns
- Statistical confidence analysis
- Explains observed 74%/14.9% statistics

**Usage:**
```bash
# Discover patterns with default 75% confidence
python discover_cell_patterns.py --analysis_csv deck_analysis.csv --output patterns.json

# Higher confidence threshold
python discover_cell_patterns.py --analysis_csv analysis.csv --output patterns.json --min_confidence 90

# Generate pattern summary
python discover_cell_patterns.py --analysis_csv analysis.csv --output patterns.json --human_report pattern_summary.txt
```

**Expected Discoveries:**
```
Pattern: *SYNC2* → 100% final-state (confidence: 98.5%)
Pattern: ICG* → NEVER final-state (confidence: 95.2%)
Pattern: MB*AN2* → Special post-processing (confidence: 87.3%)
```

### 4. Specification Gap Analysis Tool (`validate_specification_completeness.py`)
**Purpose:** Compares template*.tcl specifications vs actual SPICE deck outputs to identify gaps.

**Key Capabilities:**
- Parses template*.tcl files for specifications
- Identifies behaviors present in decks but not specified
- Maps specification gaps to EDA tool compatibility
- Detects hidden logic embedded in Python code

**Usage:**
```bash
# Analyze specification gaps
python validate_specification_completeness.py --template_file template.tcl --analysis_csv deck_analysis.csv --output gaps.json

# Generate gap report
python validate_specification_completeness.py --template_file template.tcl --analysis_csv analysis.csv --output gaps.json --human_report gap_report.txt
```

**Expected Gap Report:**
```markdown
## Critical Gaps Found:

### Gap 1: Final-State Checks (74% of arcs affected)
**In Template.tcl:** No specification
**In Generated Deck:** .meas final_state checks added
**EDA Tool Impact:** ❌ Cannot reproduce without Python logic

### Gap 2: CP2Q_DEL2 Monitoring (14.9% of arcs affected)
**In Template.tcl:** No specification
**In Generated Deck:** Second monitoring cycle added
**EDA Tool Impact:** ❌ Unclear how to determine which arcs need this
```

### 5. Comprehensive Validation Test Suite (`test_flow_validation.py`)
**Purpose:** Validates that discovered patterns match actual tool behavior and ensures consistency.

**Key Capabilities:**
- Tests coverage expectations (74% final-state, 14.9% cp2q_del2)
- Validates pattern consistency across identical configurations
- Tests template correlation strength
- Detects data integrity issues

**Usage:**
```bash
# Run all validation tests
python test_flow_validation.py --deck_dir /work/MCQC_RUN/DECKS/ --test_type all

# Test specific patterns
python test_flow_validation.py --analysis_csv deck_analysis.csv --test_type coverage

# Generate test report
python test_flow_validation.py --deck_dir /work/DECKS/ --test_type all --human_report validation_report.txt
```

**Expected Validation:**
```
✅ PASS final_state_coverage (74.2% within expected 70-78%)
✅ PASS cp2q_del2_coverage (14.7% within expected 12-18%)
❌ FAIL pattern_consistency (12 inconsistent patterns found)
```

## 🚀 Quick Start Workflow

### Step 1: Basic Analysis
```bash
# Analyze all SPICE decks
python validate_deck_structure.py --deck_dir /work/MCQC_RUN/DECKS/ --output deck_analysis.csv --verbose
```

### Step 2: Pattern Discovery
```bash
# Discover cell patterns
python discover_cell_patterns.py --analysis_csv deck_analysis.csv --output cell_patterns.json --human_report patterns.txt

# Analyze template correlations
python correlate_template_to_output.py --analysis_csv deck_analysis.csv --output template_corr.json --human_report templates.txt
```

### Step 3: Gap Analysis
```bash
# Find specification gaps (requires template*.tcl file)
python validate_specification_completeness.py --template_file /work/lib/template_mpw.tcl --analysis_csv deck_analysis.csv --output gaps.json --human_report gaps.txt
```

### Step 4: Validation
```bash
# Validate discovered patterns
python test_flow_validation.py --analysis_csv deck_analysis.csv --test_type all --human_report validation.txt
```

## 📊 Expected Discoveries

### Pattern Types
- **Exact Cell Patterns:** `SYNC2_X1` → 100% final-state
- **Prefix Patterns:** `ICG*` → Always cp2q_del2
- **Regex Patterns:** `MB.*AN2.*` → Special post-processing
- **Template Patterns:** `template_*_AMD_*` → Comprehensive final-state

### Statistical Validation
- **74% final-state coverage** → Should match pattern predictions
- **14.9% cp2q_del2 coverage** → Should correlate with specific templates/cells
- **Pattern consistency** → Same cell+arc+when should produce identical results

### Critical Gaps
- **Final-state specification:** 74% of arcs affected, no EDA tool support
- **CP2Q_DEL2 criteria:** 14.9% of arcs affected, unclear specification
- **Internal node selection:** Pattern unknown
- **Post-processor triggers:** Hidden in Python logic

## 🎯 Success Criteria

### Technical Validation
✅ Tools can analyze ANY set of generated decks
✅ Discovered patterns match observed statistics (74%/14.9%)
✅ Gap analysis clearly documents missing specifications
✅ Test suite validates pattern consistency
✅ All tools output structured data (CSV/JSON)

### Business Value
✅ **Immediate usability** - Tools work on existing decks without modification
✅ **Pattern documentation** - All hidden logic becomes visible
✅ **EDA compatibility assessment** - Clear gaps identified
✅ **Validation framework** - Prevents regressions during refactoring

## 🔧 Tool Integration

### Workflow Integration
```bash
# Complete analysis pipeline
./run_complete_analysis.sh /work/MCQC_RUN/DECKS/ /work/lib/template_mpw.tcl

# This would run:
# 1. validate_deck_structure.py
# 2. discover_cell_patterns.py
# 3. correlate_template_to_output.py
# 4. validate_specification_completeness.py
# 5. test_flow_validation.py
# 6. Generate consolidated report
```

### Output Format
All tools output **structured data** for further analysis:
- **CSV files** for spreadsheet analysis
- **JSON files** for programmatic processing
- **Human-readable reports** for documentation
- **Statistical summaries** for validation

## 📋 Requirements

### Python Dependencies
- `csv`, `json`, `re`, `pathlib` (standard library)
- `collections.defaultdict`, `collections.Counter`
- `fnmatch` for pattern matching
- `argparse` for command line interfaces

### Input Requirements
- **SPICE deck directory:** Contains arc folders with `nominal_sim.sp` files
- **Template file:** `template*.tcl` with arc specifications (optional for some tools)
- **Sufficient data:** Minimum 50+ arcs for statistical pattern discovery

### Output Requirements
- **Structured data:** All outputs in CSV/JSON format
- **Human reports:** Readable summaries for documentation
- **Validation results:** Pass/fail status for all tests
- **Statistical confidence:** Confidence levels for all discovered patterns

## 🎯 Next Steps

1. **Deploy tools** on actual MCQC deck directories
2. **Validate discoveries** against known behavior patterns
3. **Document all patterns** found by automated discovery
4. **Create specification requirements** based on gap analysis
5. **Use test suite** to prevent regressions during refactoring

This validation framework provides the essential foundation for understanding the MCQC tool's current behavior before any refactoring attempts. Focus on **discovering what exists** rather than changing it.