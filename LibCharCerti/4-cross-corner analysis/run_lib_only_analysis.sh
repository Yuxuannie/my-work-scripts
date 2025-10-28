#!/bin/bash
 
# Script to run library-only sigma analysis
 
# Default values
INPUT_PATH="/SIM/DFDS_20211231/Personal/ynie/3-LibCharCerti/2024/N2P/7-final_results/0-scripts/Moments/corr_check/lib_only_corr/input_rpt"
OUTPUT_DIR="/SIM/DFDS_20211231/Personal/ynie/3-LibCharCerti/2024/N2P/7-final_results/0-scripts/Moments/corr_check/lib_only_corr/output"
 
 
# Parse command line arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --input_path)
      INPUT_PATH="$2"
      shift 2
      ;;
    --output_dir)
      OUTPUT_DIR="$2"
      shift 2
      ;;
    *)
      echo "Unknown option: $1"
      echo "Usage: $0 --input_path <path> --output_dir <dir>"
      exit 1
      ;;
  esac
done
 
# Check required arguments
if [ -z "$INPUT_PATH" ]; then
  echo "Error: --input_path is required"
  exit 1
fi
 
if [ -z "$OUTPUT_DIR" ]; then
  echo "Error: --output_dir is required"
  exit 1
fi
 
# Create timestamp for this run
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
RUN_DIR="${OUTPUT_DIR}/run_${TIMESTAMP}"
 
# Create directory structure
echo "Creating output directory structure..."
mkdir -p "${RUN_DIR}"
mkdir -p "${RUN_DIR}/intermediate_data/delay"
mkdir -p "${RUN_DIR}/intermediate_data/slew"
mkdir -p "${RUN_DIR}/visualizations/delay"
mkdir -p "${RUN_DIR}/visualizations/slew"
mkdir -p "${RUN_DIR}/delay_analysis/correlations"
mkdir -p "${RUN_DIR}/slew_analysis/correlations"
mkdir -p "${RUN_DIR}/tables"
mkdir -p "${RUN_DIR}/logs"
 
# Log file for this run
LOG_FILE="${RUN_DIR}/logs/run_log.txt"
 
# Echo start message
echo "Starting library-only sigma analysis at $(date)" | tee -a "$LOG_FILE"
echo "Input path: ${INPUT_PATH}" | tee -a "$LOG_FILE"
echo "Output directory: ${RUN_DIR}" | tee -a "$LOG_FILE"
 
# Run the analysis script
echo "Running library sigma correlation analysis..." | tee -a "$LOG_FILE"
/usr/local/python/3.9.10/bin/python3 Lib_sigma_moment_analysis.py --input_path "${INPUT_PATH}" --output_dir "${RUN_DIR}" 2>&1 | tee -a "$LOG_FILE"
 
# Check if script execution was successful
if [ $? -eq 0 ]; then
  echo "Analysis completed successfully!" | tee -a "$LOG_FILE"
 
  # Move result files to their proper directories for better organization
  echo "Organizing result files..." | tee -a "$LOG_FILE"
 
  # Move table files to tables directory
  find "${RUN_DIR}" -name "*_correlations.csv" -exec mv {} "${RUN_DIR}/tables/" \; 2>/dev/null
 
  # Create a summary of results
  echo "Summary of Results:" | tee -a "$LOG_FILE"
  echo "-----------------" | tee -a "$LOG_FILE"
 
  # Count the number of files analyzed by type
  DELAY_FILES=$(find "${RUN_DIR}/intermediate_data/delay" -name "*_delay_data.csv" 2>/dev/null | wc -l)
  SLEW_FILES=$(find "${RUN_DIR}/intermediate_data/slew" -name "*_slew_data.csv" 2>/dev/null | wc -l)
  echo "Files analyzed: ${DELAY_FILES} delay instances, ${SLEW_FILES} slew instances" | tee -a "$LOG_FILE"
 
  # List the correlation tables generated
  TABLES=$(find "${RUN_DIR}/tables" -name "*_correlations.csv" 2>/dev/null)
  if [ -n "$TABLES" ]; then
    echo "Correlation tables generated:" | tee -a "$LOG_FILE"
    echo "$TABLES" | xargs -n1 basename | tee -a "$LOG_FILE"
  else
    echo "Warning: No correlation tables were generated." | tee -a "$LOG_FILE"
  fi
 
  # Create a simple HTML report
  HTML_REPORT="${RUN_DIR}/report.html"
 
  echo "<!DOCTYPE html>
<html>
<head>
  <title>Library Sigma Analysis Results</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 20px; }
    h1, h2, h3 { color: #333366; }
    .visualization { margin: 20px 0; }
    table { border-collapse: collapse; width: 100%; }
    th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
    th { background-color: #f2f2f2; }
    tr:nth-child(even) { background-color: #f9f9f9; }
    .warning { color: #cc3300; background-color: #fff3e0; padding: 10px; border-left: 4px solid #ff9800; }
    .section { margin: 20px 0; padding: 15px; background-color: #f8f9fa; border-radius: 5px; }
    .delay-section { border-left: 5px solid #4285f4; }
    .slew-section { border-left: 5px solid #ea4335; }
  </style>
</head>
<body>
  <h1>Library Sigma Correlation Analysis Results</h1>
  <p>Analysis run on: $(date)</p>" > "$HTML_REPORT"
 
  # Check for errors in the log file
  if grep -q "ERROR" "$LOG_FILE"; then
    echo "  <div class='warning'>
    <h3>âš ï¸ Warnings/Errors Detected</h3>
    <p>The following issues were detected during analysis:</p>
    <pre>" >> "$HTML_REPORT"
 
    grep "ERROR\|WARNING" "$LOG_FILE" | tail -n 10 >> "$HTML_REPORT"
 
    echo "    </pre>
    <p>See the full log file for more details.</p>
  </div>" >> "$HTML_REPORT"
  fi
 
  # Summary
  echo "  <div class='section'>
    <h2>Summary</h2>
    <p>Files analyzed: <strong>${DELAY_FILES}</strong> delay instances, <strong>${SLEW_FILES}</strong> slew instances</p>
  </div>" >> "$HTML_REPORT"
 
  # Create separate sections for delay and slew
  echo "  <div class='section delay-section'>
    <h2>Delay Analysis</h2>
    <h3>Correlation Tables</h3>" >> "$HTML_REPORT"
 
  # Add delay table visualizations
  for IMG in $(find "${RUN_DIR}/visualizations" -name "delay_*_heatmap.png" 2>/dev/null | sort); do
    BASE=$(basename "$IMG" .png)
    echo "    <div class='visualization'>
      <h4>$BASE</h4>
      <img src='visualizations/$(basename "$IMG")' alt='$BASE' style='max-width:800px;'>
    </div>" >> "$HTML_REPORT"
  done
 
  echo "  </div>
 
  <div class='section slew-section'>
    <h2>Slew Analysis</h2>
    <h3>Correlation Tables</h3>" >> "$HTML_REPORT"
 
  # Add slew table visualizations
  for IMG in $(find "${RUN_DIR}/visualizations" -name "slew_*_heatmap.png" 2>/dev/null | sort); do
    BASE=$(basename "$IMG" .png)
    echo "    <div class='visualization'>
      <h4>$BASE</h4>
      <img src='visualizations/$(basename "$IMG")' alt='$BASE' style='max-width:800px;'>
    </div>" >> "$HTML_REPORT"
  done
 
  echo "  </div>
 
  <h2>Raw Correlation Tables</h2>" >> "$HTML_REPORT"
 
  # Add raw table data
  for TABLE in $(find "${RUN_DIR}/tables" -name "*_correlations.csv" 2>/dev/null | sort); do
    if [ -f "$TABLE" ]; then
      BASE=$(basename "$TABLE" .csv)
      echo "  <h3>$BASE</h3>
  <table>" >> "$HTML_REPORT"
 
      # Add table header
      HEADER=$(head -1 "$TABLE" 2>/dev/null)
      if [ ! -z "$HEADER" ]; then
        echo "    <tr>
      <th>Corner</th>" >> "$HTML_REPORT"
 
        for COL in $(echo "$HEADER" | sed 's/^,//g' | tr ',' ' '); do
          echo "      <th>$COL</th>" >> "$HTML_REPORT"
        done
 
        echo "    </tr>" >> "$HTML_REPORT"
 
        # Add table rows
        tail -n +2 "$TABLE" 2>/dev/null | while read LINE; do
          if [ ! -z "$LINE" ]; then
            CORNER=$(echo "$LINE" | cut -d, -f1)
            VALUES=$(echo "$LINE" | sed 's/^[^,]*,//')
 
            echo "    <tr>
      <td>$CORNER</td>" >> "$HTML_REPORT"
 
            for VAL in $(echo "$VALUES" | tr ',' ' '); do
              echo "      <td>$VAL</td>" >> "$HTML_REPORT"
            done
 
            echo "    </tr>" >> "$HTML_REPORT"
          fi
        done
      else
        echo "    <tr><td>No data available</td></tr>" >> "$HTML_REPORT"
      fi
 
      echo "  </table>" >> "$HTML_REPORT"
    fi
  done
 
  # Add scatter plot section for delay
  DELAY_SCATTER_PLOTS=$(find "${RUN_DIR}/visualizations/delay" -name "*scatter_plots/*" -type f 2>/dev/null | head -4)
 
  if [ ! -z "$DELAY_SCATTER_PLOTS" ]; then
    echo "<h3>Delay Scatter Plots</h3>" >> "$HTML_REPORT"
    echo "<p>Sample scatter plots showing correlations between sigma and moments:</p>" >> "$HTML_REPORT"
 
    echo "<div style='display: flex; flex-wrap: wrap;'>" >> "$HTML_REPORT"
    for PLOT in $DELAY_SCATTER_PLOTS; do
      PLOT_NAME=$(basename "$PLOT")
      PLOT_DIR=$(basename $(dirname "$PLOT"))
      echo "<div style='margin: 10px; flex: 1;'>
    <img src='visualizations/delay/$PLOT_DIR/$PLOT_NAME' alt='$PLOT_NAME' style='max-width:400px;'>
    <p>$PLOT_NAME</p>
  </div>" >> "$HTML_REPORT"
    done
    echo "</div>" >> "$HTML_REPORT"
  fi
 
  # Add scatter plot section for slew
  SLEW_SCATTER_PLOTS=$(find "${RUN_DIR}/visualizations/slew" -name "*scatter_plots/*" -type f 2>/dev/null | head -4)
 
  if [ ! -z "$SLEW_SCATTER_PLOTS" ]; then
    echo "<h3>Slew Scatter Plots</h3>" >> "$HTML_REPORT"
    echo "<p>Sample scatter plots showing correlations between sigma and moments:</p>" >> "$HTML_REPORT"
 
    echo "<div style='display: flex; flex-wrap: wrap;'>" >> "$HTML_REPORT"
    for PLOT in $SLEW_SCATTER_PLOTS; do
      PLOT_NAME=$(basename "$PLOT")
      PLOT_DIR=$(basename $(dirname "$PLOT"))
      echo "<div style='margin: 10px; flex: 1;'>
    <img src='visualizations/slew/$PLOT_DIR/$PLOT_NAME' alt='$PLOT_NAME' style='max-width:400px;'>
    <p>$PLOT_NAME</p>
  </div>" >> "$HTML_REPORT"
    done
    echo "</div>" >> "$HTML_REPORT"
  fi
 
  echo "</body>
</html>" >> "$HTML_REPORT"
 
  echo "HTML report generated at: ${HTML_REPORT}" | tee -a "$LOG_FILE"
  echo "Analysis results are available at: ${RUN_DIR}" | tee -a "$LOG_FILE"
else
  echo "Error during analysis. Check the log file for details." | tee -a "$LOG_FILE"
  exit 1
fi
