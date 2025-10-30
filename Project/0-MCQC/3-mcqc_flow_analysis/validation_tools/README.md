# MCQC Specification Compliance Validation Tool

**Primary Tool:** `audit_deck_compliance.py`

## 🎯 **Critical Focus**

This tool demonstrates **complete understanding of the MCQC flow** by tracing EVERY input that contributed to each deck's generation and validating specification compliance with comprehensive pass/fail analysis.

## 🔧 **Core Capabilities**

### **Complete Input Traceability**
- **template.tcl** specifications → SPICE deck content mapping
- **chartcl.tcl** configurations → measurement setup correlation
- **globals files** → parameter value tracking
- **Python logic patterns** → final-state behavior identification

### **mc_sim.sp Analysis**
**Critical Distinction:** Analyzes `mc_sim.sp` files (actual Monte Carlo simulation setup) rather than `nominal_sim.sp` (base templates).

- All measurements and timing patterns
- Final-state checks (74% of arcs affected)
- CP2Q monitoring patterns (14.9% coverage)
- Internal node usage and references
- Post-processing signatures from Python logic

### **Specification Compliance Validation**
- Input-to-output traceability completeness scoring
- Specification coverage analysis
- Missing specification severity assessment
- Pattern consistency validation across decks
- Pass/fail determination with detailed metrics

### **Structured Reporting**
- **YAML reports** with clear section headers (fallback to JSON)
- **CSV summaries** with simple pass/fail status
- **Complete traceability documentation**
- **Critical issues** and **recommendations**

## 🚀 **Quick Start**

### **Single Arc Analysis with Explicit Input Files**
```bash
python audit_deck_compliance.py \
  --arc_folder /work/MCQC_RUN/DECKS/mpw_SDFQTXG_X1/ \
  --template_file /work/lib/template_mpw.tcl \
  --chartcl_file /work/lib/chartcl.tcl \
  --globals_file /work/lib/mcqc_globals_hspice.txt \
  --output_dir ./results/
```

### **Bulk Analysis (Auto-discover Input Files)**
```bash
python audit_deck_compliance.py \
  --deck_dir /work/MCQC_RUN/DECKS/ \
  --output_dir ./results/ \
  --verbose
```

### **With Specific Configuration Files**
```bash
python audit_deck_compliance.py \
  --deck_dir /work/DECKS/ \
  --template_file ./template.tcl \
  --globals_file ./globals.txt \
  --output_dir ./results/ \
  --verbose
```

### **CSV Summary Only**
```bash
python audit_deck_compliance.py \
  --deck_dir /work/DECKS/ \
  --output_dir ./results/ \
  --csv_only
```

## 📊 **Expected Output**

### **YAML/JSON Report Structure**
```yaml
## Arc Information:
  Arc Name: mpw_SDFQTXG_X1
  Overall Status: PASS/FAIL

## Compliance Status:
  Pass Rate: 85.0%
  Tests Passed: 4/5

## Input Traceability Analysis:
  Input Sources Found:
    template: template.tcl → ChartemplateParser
    chartcl: chartcl.tcl → ChartclParser
    globals_hspice: mcqc_globals_hspice.txt → GlobalsFileReader

## SPICE Deck Analysis:
  Total Measurements: 12
  Final State Patterns: 8 (74% expected)
  CP2Q Patterns: 2 (14.9% expected)

## Validation Test Results:
  traceability_test: PASS (0.89 score)
  specification_coverage_test: PASS (0.76 score)
  missing_specifications_test: FAIL (3 critical missing)
```

### **CSV Summary Format**
```csv
ArcName,OverallStatus,PassRate,TestsPassed,TotalTests,CriticalIssueCount,TracingScore,CoverageScore
mpw_SDFQTXG_X1,PASS,80.0%,4,5,1,0.89,0.76
mpw_SDFQD_X2,FAIL,60.0%,3,5,3,0.65,0.45
```

### **Output Structure**
```
work_directory/
├── results/                          # Summary reports (--output_dir)
│   └── compliance_summary.csv        # Overall CSV summary
└── DECKS/                            # Arc directories
    ├── mpw_SDFQTXG_X1/
    │   ├── mc_sim.sp                  # Analyzed SPICE deck
    │   └── compliance_validation_report.json  # Individual arc report
    └── mpw_SDFQD_X2/
        ├── mc_sim.sp
        └── compliance_validation_report.json
```

## 🛡️ **Robust Design Features**

### **Graceful Dependency Handling**
- Works with or without PyYAML (JSON fallback)
- Integrates with MCQC parsers when available
- Basic file parsing fallback for standalone operation

### **Error Resilience**
- Continues processing when individual arcs fail
- Detailed error reporting with context
- Comprehensive logging with verbose option

### **Input Discovery**
- Automatic template.tcl, chartcl.tcl, and globals file discovery
- Multi-level directory search (arc, parent, grandparent)
- Flexible input source handling

## 🔍 **Key Technical Insights**

### **Why mc_sim.sp Analysis?**
The `mc_sim.sp` file contains the **ACTUAL** Monte Carlo simulation setup including:
- All measurements (cp2q_del1, final-state checks, etc.)
- Post-processing modifications from Python logic
- Complete measurement setup that runs in simulation

`nominal_sim.sp` is only the base template before Monte Carlo additions.

### **Hidden Pattern Discovery**
- **74% final-state coverage** → Validates against expected statistical patterns
- **14.9% cp2q_del2 coverage** → Correlates with specific template/cell combinations
- **Python logic signatures** → Identifies post-processing that lacks specification
- **EDA tool compatibility gaps** → Documents missing specifications for tool migration

## 📋 **Requirements**

### **Python Dependencies (Standard Library)**
- `csv`, `json`, `re`, `pathlib`, `collections`, `argparse`, `logging`

### **Optional Dependencies**
- `PyYAML` → Enhanced YAML report formatting (graceful fallback to JSON)

### **Input Requirements**

#### **Required Inputs**
- **Arc directories** containing `mc_sim.sp` files
- **Output directory** for summary reports

#### **Configuration Files (Optional but Recommended)**
- **template.tcl** → SPICE deck generation specifications
- **chartcl.tcl** → Characterization configuration settings
- **globals files** → Parameter values and model information (e.g., `mcqc_globals_hspice.txt`)

#### **File Discovery Behavior**
- **Explicit paths:** Use `--template_file`, `--chartcl_file`, `--globals_file` for precise control
- **Auto-discovery:** If not specified, searches in arc folder → parent → grandparent hierarchy
- **Multiple globals:** Automatically finds all `*globals*.txt` files in hierarchy

#### **Data Requirements**
- **Sufficient arcs** for statistical validation (recommended 10+ arcs)
- **Complete mc_sim.sp files** with measurement statements

## 🎯 **Validation Tests**

### **1. Input Traceability Test**
- **Threshold:** 70% minimum traceability score
- **Measures:** Input-to-output correlation completeness

### **2. Specification Coverage Test**
- **Threshold:** 60% minimum specification coverage
- **Measures:** Template specifications vs actual outputs

### **3. Missing Specifications Test**
- **Threshold:** Maximum 2 critical missing specifications
- **Measures:** Severity of gaps in specification documentation

### **4. Pattern Consistency Test**
- **Threshold:** Maximum 5 pattern inconsistencies
- **Measures:** Measurement naming and type consistency

### **5. Deck Structure Test**
- **Threshold:** 70% minimum structure score
- **Measures:** Basic SPICE deck validity and completeness

## 📁 **Archive Information**

Previous validation tools have been archived in `archived_tools/`:
- `validate_deck_structure.py` → Basic deck analysis (superseded)
- `correlate_template_to_output.py` → Template correlation (integrated)
- `discover_cell_patterns.py` → Pattern discovery (integrated)
- `validate_specification_completeness.py` → Gap analysis (integrated)
- `test_flow_validation.py` → Test validation (integrated)

The new `audit_deck_compliance.py` provides all functionality in a unified, comprehensive tool.

## ⚡ **Performance Notes**

- **Processing speed:** ~1-2 seconds per arc (typical)
- **Memory usage:** Efficient streaming for large deck directories
- **Parallel processing:** Designed for easy batch processing integration
- **Output size:** Structured reports sized for readability (~10-50KB per arc)

## 🎖️ **Success Criteria**

✅ **Immediate usability** - Works on existing decks without modification
✅ **Complete traceability** - Every input mapped to outputs
✅ **Pattern documentation** - All hidden logic becomes visible
✅ **EDA compatibility assessment** - Clear specification gaps identified
✅ **Validation framework** - Prevents regressions during refactoring

This tool provides the essential foundation for understanding MCQC flow behavior before any refactoring attempts.