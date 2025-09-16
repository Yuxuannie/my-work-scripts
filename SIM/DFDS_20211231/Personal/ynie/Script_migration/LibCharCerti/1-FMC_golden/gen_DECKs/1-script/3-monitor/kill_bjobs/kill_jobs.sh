#!/bin/bash
 
# LSF Job Killer - Personal Use with Detailed Search
# Usage: ./kill_jobs.sh [options]
 
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SCRIPT="$SCRIPT_DIR/job_filter.py"
 
# Default settings
PREVIEW=false
INCLUDE="all.q"
EXCLUDE=""
FIELD="QUEUE"
DETAILED=false
BEFORE_DATE=""
AFTER_DATE=""
 
usage() {
    cat << EOF
Usage: $0 [OPTIONS]
 
Kill LSF jobs based on string matching criteria
 
Options:
  -i STRING    Include jobs containing this string (supports wildcards: *, ?, [])
  -e STRING    Exclude jobs containing this string (supports wildcards: *, ?, []) 
  -f FIELD     Filter field: JOB_NAME, QUEUE, USER, EXEC_HOST (default: JOB_NAME)
  -d           Use detailed search (bjobs -l) - searches in full job details
  --before DATE Kill jobs submitted before this date (e.g., "Jul 5", "2025-07-05")
  --after DATE  Kill jobs submitted after this date (e.g., "Jul 5", "2025-07-05")
  -p           Preview only - don't actually kill jobs
  -h           Show this help
 
Filter Fields (for -f option):
  JOB_NAME     Job name/command (default)
  QUEUE        Queue name
  USER         Username 
  EXEC_HOST    Execution host
  DETAILED     Full job details (same as -d flag)
 
Wildcard Patterns:
  *            Matches any number of characters
  ?            Matches any single character
  [abc]        Matches any character in the set
  [!abc]       Matches any character not in the set
 
Date Formats (for --before/--after):
  Jul 5        Month day (current year)
  July 5       Full month name
  2025-07-05   ISO format
  07/05        MM/DD (current year)
  Jul 5 2025   Month day year
 
Examples:
  $0 -i golden -e test -p              # Preview jobs with 'golden' but not 'test'
  $0 -i N2P -i MC                      # Kill jobs containing both 'N2P' and 'MC'
  $0 -f QUEUE -i all.q -p              # Preview jobs in 'all.q' queue
  $0 -f USER -i \$(whoami) -p           # Preview all your jobs
  $0 -d -i "LibCharCert1/2025" -p      # Search in detailed job info
  $0 -i "golden" -d -e "script" -p     # Detailed search for golden runs, exclude scripts
  $0 -i "ssgnp*" -p                    # Preview jobs starting with 'ssgnp'
  $0 -i "*_test_*" -e "*important*" -p # Jobs with '_test_' but not 'important'
  $0 --before "Jul 5" -p               # Preview jobs submitted before July 5
  $0 --after "Jul 3" --before "Jul 7" -p # Jobs submitted between Jul 3 and Jul 7
  $0 -i "test*" --before "Jul 5" -p    # Test jobs submitted before July 5
 
EOF
}
 
# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -i) INCLUDE="$INCLUDE,$2"; shift 2 ;;
        -e) EXCLUDE="$EXCLUDE,$2"; shift 2 ;;
        -f) FIELD="$2"; shift 2 ;;
        -d) DETAILED=true; shift ;;
        --before) BEFORE_DATE="$2"; shift 2 ;;
        --after) AFTER_DATE="$2"; shift 2 ;;
        -p) PREVIEW=true; shift ;;
        -h) usage; exit 0 ;;
        *) echo "Unknown option: $1"; usage; exit 1 ;;
    esac
done
 
# Remove leading commas
INCLUDE="${INCLUDE#,}"
EXCLUDE="${EXCLUDE#,}"
 
# Check if filtering criteria provided
if [[ -z "$INCLUDE" && -z "$EXCLUDE" && -z "$BEFORE_DATE" && -z "$AFTER_DATE" ]]; then
    echo "Error: Must specify at least one filtering option (-i, -e, --before, --after)"
    usage
    exit 1
fi
 
# Set detailed mode if FIELD is DETAILED
if [[ "$FIELD" == "DETAILED" ]]; then
    DETAILED=true
fi
 
# Check dependencies
if ! command -v bjobs &> /dev/null; then
    echo "Error: bjobs command not found"
    exit 1
fi
 
if [[ ! -f "$PYTHON_SCRIPT" ]]; then
    echo "Error: $PYTHON_SCRIPT not found"
    exit 1
fi
 
echo "=== LSF Job Killer ==="
if [[ "$DETAILED" == true ]]; then
    echo "Mode: Detailed search (bjobs -l)"
else
    echo "Mode: Standard search"
    echo "Filter: $FIELD"
fi
[[ -n "$INCLUDE" ]] && echo "Include: $INCLUDE"
[[ -n "$EXCLUDE" ]] && echo "Exclude: $EXCLUDE"
[[ -n "$BEFORE_DATE" ]] && echo "Before: $BEFORE_DATE"
[[ -n "$AFTER_DATE" ]] && echo "After: $AFTER_DATE"
echo ""
 
# Show progress for detailed mode (can be slow)
if [[ "$DETAILED" == true ]]; then
    echo "Fetching detailed job information... (this may take a moment)"
fi
 
# Get filtered job IDs
TEMP_FILE=$(mktemp)
ARGS="--field '$FIELD' --include '$INCLUDE' --exclude '$EXCLUDE' --output '$TEMP_FILE'"
if [[ "$DETAILED" == true ]]; then
    ARGS="$ARGS --detailed"
fi
if [[ -n "$BEFORE_DATE" ]]; then
    ARGS="$ARGS --before '$BEFORE_DATE'"
fi
if [[ -n "$AFTER_DATE" ]]; then
    ARGS="$ARGS --after '$AFTER_DATE'"
fi
 
eval python3 "$PYTHON_SCRIPT" $ARGS
 
if [[ $? -ne 0 ]]; then
    echo "Error: Failed to filter jobs"
    rm -f "$TEMP_FILE"
    exit 1
fi
 
if [[ ! -s "$TEMP_FILE" ]]; then
    echo "No jobs found matching criteria"
    rm -f "$TEMP_FILE"
    exit 0
fi
 
JOB_COUNT=$(wc -l < "$TEMP_FILE")
echo "Found $JOB_COUNT matching jobs:"
echo ""
 
# Show jobs with details
echo "JOBID      USER     STAT QUEUE      JOB_NAME"
echo "---------- -------- ---- ---------- --------"
while IFS= read -r jobid; do
    bjobs "$jobid" 2>/dev/null | tail -n +2
done < "$TEMP_FILE"
echo ""
 
if [[ "$PREVIEW" == true ]]; then
    echo "Preview mode - no jobs killed"
    if [[ "$DETAILED" == true ]]; then
        echo ""
        echo "Note: Detailed mode searched through full job information including:"
        echo "  - Complete job names/commands"
        echo "  - Working directories" 
        echo "  - Project paths"
        echo "  - Resource requirements"
        echo "  - Submit/execution details"
    fi
    if [[ -n "$BEFORE_DATE" || -n "$AFTER_DATE" ]]; then
        echo ""
        echo "Note: Time-based filtering was applied based on job submission times"
    fi
    rm -f "$TEMP_FILE"
    exit 0
fi
 
# Confirm action
echo "Kill these $JOB_COUNT jobs? (y/N): "
read -r response
if [[ ! "$response" =~ ^[Yy]$ ]]; then
    echo "Cancelled"
    rm -f "$TEMP_FILE"
    exit 0
fi
 
# Kill jobs
echo "Killing jobs..."
killed=0
failed=0
 
while IFS= read -r jobid; do
    if bkill "$jobid" &> /dev/null; then
        echo "âœ“ Killed $jobid"
        ((killed++))
    else
        echo "âœ— Failed $jobid"
        ((failed++))
    fi
done < "$TEMP_FILE"
 
rm -f "$TEMP_FILE"
 
echo ""
echo "Summary: Killed $killed, Failed $failed"
 
