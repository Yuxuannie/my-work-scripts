#!/bin/bash
 
/bin/csh /tools/dotfile_new/cshrc.lsfc2
# Default parameters
working_path="/SIM/DFDS_20211231/Personal/ynie/3-LibCharCerti/2025/N2P_v1.0/1-MC_golden/1-Full_MC_golden/"
corners=("ssgnp_0p450v_m40c")
 
timestamp=$(date +%Y%m%d_%H%M%S)
log_file="$PWD/run_parallel_${timestamp}.log"
 
# Function to log messages
log() {
    echo "$@" >> "$log_file"
    echo "$@"
}
 
# Initialize log file with a header
echo "=======================================================" > "$log_file"
echo "Starting simulation runner: $(date)" >> "$log_file"
echo "=======================================================" >> "$log_file"
 
# Log the startup info
log ""
log "Log file: $log_file"
 
# Verify working path exists
if [ ! -d "$working_path" ]; then
    log "Error: Working path $working_path does not exist"
    exit 1
fi
 
# Verify corners exist
for corner in "${corners[@]}"; do
    if [ ! -d "$working_path/$corner" ]; then
        log "Error: Corner $corner does not exist in $working_path"
        exit 1
    fi
done
 
# Display run configuration
log "======================================================="
log "Run Configuration:"
log "Working Path: $working_path"
log "Corners to Run: ${corners[*]}"
log "======================================================="
log ""
 
# Function to check system resource availability based on predefined rules
check_cpu_availability() {
    # Use fixed resource check logic (predefined threshold for CPU usage)
    busers_output=$(busers)
    njobs=$(echo "$busers_output" | awk 'NR==2 {print $4}')
 
    # Predefined threshold for CPU availability
    max_cpus=8000
    available_cpus=$((max_cpus - njobs))
 
    log "Checking CPU availability: Available CPUs = $available_cpus (using $njobs jobs of $max_cpus)"
   
    if [ "$available_cpus" -ge 400 ]; then
        return 0  # Sufficient CPUs available
    else
        return 1  # Not enough CPUs available
    fi
}
 
# Function to retry jobs if they fail
retry_job() {
    local subdir=$1
    local retry_count=3  # Maximum retry attempts
   
    for attempt in $(seq 1 $retry_count); do
        log "Retrying job for $subdir (Attempt $attempt of $retry_count)"
        if (cd "$subdir" && bsub -J "job_$(basename "$subdir")" -o "$log_file" ./run.sh); then
            log "Job successfully completed on retry $attempt: $subdir"
            return 0
        fi
        sleep 30  # Wait before retrying
    done
   
    log "Error: Failed to complete job after $retry_count attempts: $subdir"
    return 1
}
 
# Function to run jobs
run_jobs() {
    local corner=$1
   
    log "Processing corner: $corner"
    log "======================================================="
   
    # Get all subdirectories with run.sh
    subdirs=()
    while IFS= read -r -d '' subdir; do
        if [ -f "$subdir/run.sh" ]; then
            subdirs+=("$subdir")
        fi
    done < <(find "$working_path/$corner" -type d -maxdepth 1 -print0 2>/dev/null)
   
    total_jobs=${#subdirs[@]}
    completed_jobs=0
   
    log "Found $total_jobs simulation directories to run"
    log ""
   
    # Run each job with predefined CPU resource check
    for subdir in "${subdirs[@]}"; do
        sim_name=$(basename "$subdir")
        full_path="$subdir"
       
        # Check for existing *ava.report files
        ava_report_files_found=$(find "$full_path" -maxdepth 2 -type f -name '*ava.report' | wc -l)
        if [ "$ava_report_files_found" -gt 0 ]; then
            log "Simulation for directory $full_path is already completed. *ava.report files found."
            completed_jobs=$((completed_jobs + 1))
            progress=$((completed_jobs * 100 / total_jobs))
            log "Progress: $completed_jobs/$total_jobs ($progress%)"
            continue
        else
            log "No *ava_report files found in $full_path. Proceeding with job execution."
        fi
 
        # Wait until enough CPU resources are available
        while ! check_cpu_availability; do
            log "Waiting for CPU resources to become available (need at least 400 CPUs)..."
            sleep 30  # Wait before checking again
        done
       
        # Launch the job using bsub
        log "Submitting job for directory: $full_path"
        if (cd "$subdir" && bsub -J "job_$sim_name" -o "$log_file" ./run.sh); then
            log "Job submitted successfully for directory: $full_path"
            completed_jobs=$((completed_jobs + 1))
            progress=$((completed_jobs * 100 / total_jobs))
            log "Progress: $completed_jobs/$total_jobs ($progress%)"
        else
            log "Error: Failed to submit job for directory: $full_path"
            # Retry the job
            retry_job "$subdir"
        fi
       
        # Brief pause to allow job registration in the system
        sleep 5
    done
   
    log "======================================================="
    log "All jobs submitted for corner $corner!"
    log "======================================================="
    log ""
}
 
# Main execution
start_time=$(date +%s)
 
# Run each corner sequentially
for corner in "${corners[@]}"; do
    run_jobs "$corner"
done
 
end_time=$(date +%s)
duration=$((end_time - start_time))
hours=$((duration / 3600))
minutes=$(((duration % 3600) / 60))
seconds=$((duration % 60))
 
log "======================================================="
log "All requested corners processed!"
log "Total runtime: ${hours}h ${minutes}m ${seconds}s"
log "Main log file: $log_file"
log "Finished at: $(date)"
log "======================================================="
 
echo "Script completed! Full log available at: $log_file"
 
