#!/bin/bash
 
# Preprocessed target search strings
SEARCH_STRINGS=(
    "_T/ttg_0p445v/tcbn02_bwph130nppnl3p48cpd_base_lvt"
    "_T/ttg_0p445v/tcbn02_bwph130nppnl3p48cpd_base_ulvt"
    "_T/ttg_0p445v/tcbn02_bwph130nppnl3p48cpd_base_ulvtll"
    "_T/ttg_0p445v/tcbn02_bwph130pnnpl3p48cpd_base_lvtll"
    "_T/ttg_0p445v/tcbn02_bwph130pnnpl3p48cpd_base_ulvt"
)
# Define a temporary file to store job IDs
TEMP_FILE="$(pwd)/job_ids_to_check_and_kill.txt"
LOG_FILE="$(pwd)/job_kill_log.txt"
 
# Clear the temporary file, log file, and filtered file
> "$TEMP_FILE"
> "$LOG_FILE"
> "${TEMP_FILE}.filtered"
 
# Iterate through the list of search strings
for search_string in "${SEARCH_STRINGS[@]}"; do
    # Add an awk command to extract Job ID and matching lines
    bjobs -l | awk -v search_string="$search_string" '
    /Job </ {job_id=$2}
    $0 ~ search_string {
        job_id_cleaned = gensub(/<([^>]+)>,?/, \\1, "g", job_id)
        print "Job ID:", job_id_cleaned
        print
    }' >> "$TEMP_FILE"
done
 
# Filter out the Job IDs
awk '/Job ID:/ {print $3}' "$TEMP_FILE" > "${TEMP_FILE}.filtered"
 
# Print job IDs for double-checking and log this information
echo "Job IDs containing the specified strings:" | tee -a "$LOG_FILE"
cat "${TEMP_FILE}.filtered" | tee -a "$LOG_FILE"
 
# Test Mode: Confirm before killing any jobs
read -p "Would you like to proceed with killing these jobs? (yes/no): " confirm
 
if [[ "$confirm" == "yes" ]]; then
    # Kill the jobs
    while read -r job_id; do
        echo "Killing job ID $job_id" | tee -a "$LOG_FILE"
        bkill "$job_id"
    done < "${TEMP_FILE}.filtered"
else
    echo "Test mode: No jobs were killed." | tee -a "$LOG_FILE"
fi
 
# Clean up temporary files
#rm "$TEMP_FILE" "${TEMP_FILE}.filtered"
 
 
