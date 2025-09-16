#!/bin/bash
 
# Cell Selection Script fron Library Error Prediction Results
# Author: Yuxuan Nie
# Date: $(date)
# Version: 1.0 - Systematic selection with family allocation and pt pattern analysis
 
# =============================================================================
# CONFIGURATION PARAMETERS
# =============================================================================
 
# Working directory
WORK_DIR="/SIM/DFDS_20211231/Personal/ynie/3-LibCharCerti/2025/N2P_v1.0/2-select_2nd_round/0-script"
 
# Prediction files directory
#PRED_FILES_DIR="/FSIM/PPA_C651_chamber/DFSD/Personal/cyliubd/N2P_C651/Certification/MPW/PredictCell/phase_2/Result/"
PRED_FILES_DIR="/FSIM/PPA_C651_chamber/DFSD/Personal/cyliubd/N2P_C651/Certification/Hold/PredictCell/Result/"
 
# Corners to process
CORNERS=("ssgnp_0p450v_m40c" "ssgnp_0p465v_m40c" "ssgnp_0p480v_m40c" "ssgnp_0p495v_m40c")
 
# Processing parameters (single values - one per execution)
TYPE="hold"           # Single type per execution: delay, slew, hold, mpw
NODE="n2p_v1.0"  # Node identifier for output file naming
 
# Base output directory (will create subdirectory by type)
BASE_OUTPUT_DIR="$WORK_DIR/output"
 
# Systematic golden cell selection parameters (fixed criteria)
TOP_WORST_COUNT=25        # Fixed: Top 10 worst cases always selected
FAMILY_ALLOCATION_COUNT=20 # Fixed: 20 additional cells allocated by family ratio
 
# Processing options
POSITIVE_OUTLIERS_ONLY=true  # Set to true to remove positive margin entries
VERBOSE=true
 
# =============================================================================
# FUNCTIONS
# =============================================================================
 
# Print usage information
print_usage() {
    echo "Systematic Cell Selection for Timing Analysis"
    echo "============================================="
    echo ""
    echo "Usage: $0 -t TYPE [OPTIONS]"
    echo ""
    echo "Required Parameters:"
    echo "  -t, --type TYPE                Timing type: delay, slew, hold, or mpw"
    echo ""
    echo "Optional Parameters:"
    echo "  -n, --node NODE                Node identifier (default: n2p_v1.0)"
    echo "  -p, --positive-outliers-only   Remove positive margin entries"
    echo "  -o, --base-output-dir DIR      Base output directory (creates TYPE subdirectory)"
    echo "  -w, --top-worst-count NUM      Number of top worst cases (default: 10)"
    echo "  -f, --family-count NUM         Number of family-allocated cells (default: 20)"
    echo "  -v, --verbose                  Enable verbose output"
    echo "  -h, --help                     Show this help message"
    echo ""
    echo "Systematic Selection Criteria:"
    echo "  1. Top 10 worst case cells (by absolute margin) - ALWAYS selected"
    echo "  2. Analyze top 10 families by total violation count"
    echo "  3. Allocate 20 additional cells proportionally by family ratio"
    echo "  4. Avoid duplicates from top worst list"
    echo "  5. Total result: ~30 golden cells with systematic coverage"
    echo ""
    echo "Cell Family Definition:"
    echo "  - Remove everything from 'BWP' onwards"
    echo "  - Remove trailing drive strength (D + digits)"
    echo "  - Example: CKLNQOPPZPDMZD4BWP130... â†’ CKLNQOPPZPDMZ"
    echo ""
    echo "Output Structure:"
    echo "  output/TYPE/                    # TYPE subdirectory (delay/slew/hold/mpw)"
    echo "  â”œâ”€â”€ NODE_TYPE_cell_summary_report.csv"
    echo "  â”œâ”€â”€ NODE_TYPE_cell_detailed_report.csv"
    echo "  â”œâ”€â”€ NODE_TYPE_golden_cell_selection.csv"
    echo "  â”œâ”€â”€ NODE_TYPE_golden_cell_selection_family_allocation.csv"
    echo "  â”œâ”€â”€ NODE_TYPE_golden_cell_selection.txt"
    echo "  â”œâ”€â”€ NODE_TYPE_pt_pattern_summary.csv"
    echo "  â””â”€â”€ NODE_TYPE_processing.log"
    echo ""
    echo "Examples:"
    echo "  $0 -t delay                     # Standard delay analysis"
    echo "  $0 -t hold -p                   # Hold analysis, negative margins only"
    echo "  $0 -t mpw -n custom_v2.0        # MPW analysis with custom node"
    echo "  $0 -t slew -w 15 -f 25          # Slew: 15 worst + 25 family-allocated"
}
 
# Log function
log_message() {
    local message="$1"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] $message" | tee -a "$LOG_FILE"
}
 
# Check if required files exist
check_files() {
    log_message "Checking for prediction files in $PRED_FILES_DIR..."
   
    local file_count=0
    for corner in "${CORNERS[@]}"; do
        file_path="${PRED_FILES_DIR}/prediction_results.csv.${corner}"
        if [[ -f "$file_path" ]]; then
            file_count=$((file_count + 1))
            log_message "Found: $(basename "$file_path")"
        else
            log_message "Missing: $(basename "$file_path")"
        fi
    done
   
    if [[ $file_count -eq 0 ]]; then
        log_message "ERROR: No prediction result files found in $PRED_FILES_DIR!"
        log_message "Expected files: prediction_results.csv.<corner_name>"
        exit 1
    fi
   
    if [[ $file_count -lt ${#CORNERS[@]} ]]; then
        log_message "WARNING: Found $file_count files, expected ${#CORNERS[@]} files"
        log_message "Some corners may be missing from analysis"
    fi
   
    log_message "Found $file_count prediction files to process"
}
 
# Validate parameters
validate_parameters() {
    # Check required parameters
    if [[ -z "$TYPE" ]]; then
        echo "ERROR: Type parameter is required. Use -t to specify timing type."
        echo "Valid types: delay, slew, hold, mpw"
        exit 1
    fi
   
    # Validate type value
    case "$TYPE" in
        delay|slew|hold|mpw)
            # Valid type
            ;;
        *)
            echo "ERROR: Invalid type '$TYPE'. Valid types: delay, slew, hold, mpw"
            exit 1
            ;;
    esac
   
    # Validate node parameter
    if [[ -z "$NODE" ]]; then
        echo "ERROR: Node parameter cannot be empty"
        exit 1
    fi
   
    # Validate numerical parameters
    if [[ $TOP_WORST_COUNT -lt 1 ]]; then
        log_message "ERROR: Top worst count must be at least 1"
        exit 1
    fi
   
    if [[ $FAMILY_ALLOCATION_COUNT -lt 1 ]]; then
        log_message "ERROR: Family allocation count must be at least 1"
        exit 1
    fi
   
    if [[ $TOP_WORST_COUNT -gt 50 ]]; then
        log_message "WARNING: Top worst count ($TOP_WORST_COUNT) is quite high"
    fi
   
    if [[ $FAMILY_ALLOCATION_COUNT -gt 100 ]]; then
        log_message "WARNING: Family allocation count ($FAMILY_ALLOCATION_COUNT) is quite high"
    fi
}
 
# Setup output directory structure and file paths
setup_output_structure() {
    # Create type-specific output directory
    OUTPUT_DIR="$BASE_OUTPUT_DIR/$TYPE"
    mkdir -p "$OUTPUT_DIR"
   
    # Define output file paths with node and type information
    SUMMARY_REPORT="$OUTPUT_DIR/${NODE}_${TYPE}_cell_summary_report.csv"
    DETAILED_REPORT="$OUTPUT_DIR/${NODE}_${TYPE}_cell_detailed_report.csv"
    GOLDEN_CELL_LIST="$OUTPUT_DIR/${NODE}_${TYPE}_golden_cell_selection.csv"
    PT_PATTERN_REPORT="$OUTPUT_DIR/${NODE}_${TYPE}_pt_pattern_summary.csv"
    LOG_FILE="$OUTPUT_DIR/${NODE}_${TYPE}_processing.log"
   
    log_message "Output structure created:"
    log_message "  Directory: $OUTPUT_DIR"
    log_message "  Node: $NODE"
    log_message "  Type: $TYPE"
}
 
# =============================================================================
# MAIN SCRIPT
# =============================================================================
 
# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -t|--type)
            TYPE="$2"
            shift 2
            ;;
        -n|--node)
            NODE="$2"
            shift 2
            ;;
        -p|--positive-outliers-only)
            POSITIVE_OUTLIERS_ONLY=true
            shift
            ;;
        -o|--base-output-dir)
            BASE_OUTPUT_DIR="$2"
            shift 2
            ;;
        -w|--top-worst-count)
            TOP_WORST_COUNT="$2"
            shift 2
            ;;
        -f|--family-count)
            FAMILY_ALLOCATION_COUNT="$2"
            shift 2
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -h|--help)
            print_usage
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use -h or --help for usage information"
            exit 1
            ;;
    esac
done
 
# Validate parameters first
validate_parameters
 
# Setup output directory structure
setup_output_structure
 
# Initialize log file with comprehensive header
cat > "$LOG_FILE" << EOF
================================================================================
SYSTEMATIC CELL SELECTION PROCESSING LOG
================================================================================
Script Version: 1.0 - Family-based selection with pt pattern analysis
Execution Started: $(date)
Host: $(hostname)
User: $(whoami)
Working Directory: $WORK_DIR
 
CONFIGURATION PARAMETERS:
================================================================================
Node: $NODE
Type: $TYPE
Prediction Files Directory: $PRED_FILES_DIR
Output Directory: $OUTPUT_DIR
 
SELECTION CRITERIA:
================================================================================
Top Worst Cases: $TOP_WORST_COUNT (fixed selection by absolute margin)
Family Allocation: $FAMILY_ALLOCATION_COUNT (proportional by violation ratio)
Expected Total Golden Cells: ~$((TOP_WORST_COUNT + FAMILY_ALLOCATION_COUNT))
 
Cell Family Definition:
- Remove everything from 'BWP' onwards
- Remove trailing drive strength (D + digits)
- Example: CKLNQOPPZPDMZD4BWP130HPNPN3P48CPD â†’ CKLNQOPPZPDMZ
 
PROCESSING OPTIONS:
================================================================================
Positive Outliers Only: $POSITIVE_OUTLIERS_ONLY
Verbose Output: $VERBOSE
Corners: $(IFS=, ; echo "${CORNERS[*]}")
 
OUTPUT FILES:
================================================================================
Cell Summary: $SUMMARY_REPORT
Detailed Report: $DETAILED_REPORT 
Golden Cell Selection: $GOLDEN_CELL_LIST
PT Pattern Analysis: $PT_PATTERN_REPORT
Processing Log: $LOG_FILE
 
================================================================================
PROCESSING LOG:
================================================================================
 
EOF
 
log_message "Starting systematic cell selection processing..."
log_message "Configuration validated and output structure created"
 
# Change to working directory
cd "$WORK_DIR" || {
    log_message "ERROR: Cannot change to working directory: $WORK_DIR"
    exit 1
}
 
# Check for required files
check_files
 
# Check if Python script exists
PYTHON_SCRIPT="$WORK_DIR/select_cell.py"
if [[ ! -f "$PYTHON_SCRIPT" ]]; then
    log_message "ERROR: Python script not found: $PYTHON_SCRIPT"
    log_message "Please ensure select_cell.py is in the working directory"
    exit 1
fi
 
# Prepare arguments for Python script
PYTHON_ARGS=""
if [[ "$POSITIVE_OUTLIERS_ONLY" == "true" ]]; then
    PYTHON_ARGS="$PYTHON_ARGS --positive-outliers-only"
fi
 
if [[ "$VERBOSE" == "true" ]]; then
    PYTHON_ARGS="$PYTHON_ARGS --verbose"
fi
 
# Build corners argument (TYPE is now single value)
CORNERS_STR=$(IFS=,; echo "${CORNERS[*]}")
 
# Execute Python script
log_message "Executing systematic cell selection Python script..."
log_message "Python command: /usr/local/python/3.9.10/bin/python3 $PYTHON_SCRIPT"
 
/usr/local/python/3.9.10/bin/python3 "$PYTHON_SCRIPT" \
    --work-dir "$WORK_DIR" \
    --pred-files-dir "$PRED_FILES_DIR" \
    --output-dir "$OUTPUT_DIR" \
    --corners "$CORNERS_STR" \
    --type "$TYPE" \
    --node "$NODE" \
    --summary-report "$SUMMARY_REPORT" \
    --detailed-report "$DETAILED_REPORT" \
    --golden-cell-list "$GOLDEN_CELL_LIST" \
    --pt-pattern-report "$PT_PATTERN_REPORT" \
    --top-worst-count "$TOP_WORST_COUNT" \
    --family-allocation-count "$FAMILY_ALLOCATION_COUNT" \
    $PYTHON_ARGS
 
# Check if Python script executed successfully
PYTHON_EXIT_CODE=$?
if [[ $PYTHON_EXIT_CODE -eq 0 ]]; then
    log_message "Processing completed successfully!"
    log_message "Generated reports:"
    log_message "  - Summary report: $SUMMARY_REPORT"
    log_message "  - Detailed report: $DETAILED_REPORT"
    log_message "  - Golden cell list: $GOLDEN_CELL_LIST"
   
    # Check for additional output files
    FAMILY_ALLOCATION_FILE="${GOLDEN_CELL_LIST/_selection.csv/_family_allocation.csv}"
    GOLDEN_TEXT_FILE="${GOLDEN_CELL_LIST/.csv/.txt}"
   
    if [[ -f "$FAMILY_ALLOCATION_FILE" ]]; then
        log_message "  - Family allocation: $FAMILY_ALLOCATION_FILE"
    fi
   
    if [[ -f "$PT_PATTERN_REPORT" ]]; then
        log_message "  - PT pattern analysis: $PT_PATTERN_REPORT"
    fi
   
    if [[ -f "$GOLDEN_TEXT_FILE" ]]; then
        log_message "  - Golden cell text list: $GOLDEN_TEXT_FILE"
    fi
   
    # Display summary if verbose
    if [[ "$VERBOSE" == "true" ]]; then
        echo ""
        echo "==============================================="
        echo "SYSTEMATIC SELECTION RESULTS"
        echo "==============================================="
       
        if [[ -f "$SUMMARY_REPORT" ]]; then
            echo ""
            echo "=== TOP 10 WORST CASE CELLS ==="
            head -11 "$SUMMARY_REPORT" | column -t -s ","
        fi
       
        if [[ -f "$GOLDEN_CELL_LIST" ]]; then
            echo ""
            echo "=== SYSTEMATIC GOLDEN CELL SELECTION (First 15) ==="
            head -16 "$GOLDEN_CELL_LIST" | column -t -s ","
        fi
       
        if [[ -f "$FAMILY_ALLOCATION_FILE" ]]; then
            echo ""
            echo "=== FAMILY ALLOCATION SUMMARY ==="
            head -11 "$FAMILY_ALLOCATION_FILE" | column -t -s ","
        fi
       
        if [[ -f "$PT_PATTERN_REPORT" ]]; then
            echo ""
            echo "=== PT PATTERN ANALYSIS SUMMARY ==="
            head -11 "$PT_PATTERN_REPORT" | column -t -s ","
        fi
       
        if [[ -f "$GOLDEN_TEXT_FILE" ]]; then
            echo ""
            echo "=== GOLDEN CELL COUNT BY SELECTION METHOD ==="
            echo "Top worst cases: $TOP_WORST_COUNT"
            family_allocated=$(tail -n +5 "$GOLDEN_TEXT_FILE" | wc -l)
            family_allocated=$((family_allocated - TOP_WORST_COUNT))
            echo "Family allocated: $family_allocated"
            total_selected=$(tail -n +5 "$GOLDEN_TEXT_FILE" | wc -l)
            echo "Total selected: $total_selected"
        fi
       
        echo ""
        echo "==============================================="
    fi
   
    # Provide next steps guidance
    echo ""
    echo "Next Steps:"
    echo "1. Review golden cell selection: $GOLDEN_CELL_LIST"
    echo "2. Check family allocation ratios: $FAMILY_ALLOCATION_FILE"
    echo "3. Analyze PT pattern distribution: $PT_PATTERN_REPORT"
    echo "4. Use for simulation: $GOLDEN_TEXT_FILE"
    echo ""
    echo "For simulation, use the text file:"
    echo "  cat $GOLDEN_TEXT_FILE | grep -v '^#' | while read cell; do"
    echo "    echo \"Simulating \$TYPE analysis for: \$cell\""
    echo "    # Your simulation command here"
    echo "  done"
   
else
    log_message "ERROR: Python script execution failed with exit code $PYTHON_EXIT_CODE"
    log_message "Check the Python processing log for details"
    exit 1
fi
 
log_message "Script execution completed at: $(date)"
echo ""
echo "Systematic cell selection processing completed!"
echo "Check the log file for details: $LOG_FILE"
 
