#!/bin/bash
#=============================================================
# Monte Carlo Sampling Analysis Shell Script
#=============================================================
 
# Create a log file in the current directory
LOG_FILE="$(pwd)/mc_analysis.log"
echo "==============================================" > "$LOG_FILE"
echo "  MONTE CARLO SAMPLING ANALYSIS LOG" >> "$LOG_FILE"
echo "  $(date "+%Y-%m-%d %H:%M:%S")" >> "$LOG_FILE"
echo "==============================================" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"
 
# Log function with dividers for better readability
log() {
    local timestamp=$(date "+%Y-%m-%d %H:%M:%S")
    echo "[$timestamp] $1" >> "$LOG_FILE"
}
 
log_section() {
    echo "" >> "$LOG_FILE"
    echo "----------------------------------------------" >> "$LOG_FILE"
    echo "  $1" >> "$LOG_FILE"
    echo "----------------------------------------------" >> "$LOG_FILE"
}
 
log_section "INITIALIZATION"
log "Starting Monte Carlo analysis script"
 
# Source necessary commands/environment
log_section "ENVIRONMENT SETUP"
log "Setting up environment"
 
# Try to source csh files using bash's source equivalent (.)
log "Attempting to source C shell environment files"
 
# Set environment variables indicating what files should be sourced
# These will be used by Python if direct sourcing fails
export ENV_CSHRC_LSFC2="/tools/dotfile_new/cshrc.lsfc2"
export ENV_CSHRC_HSPICE="/tools/dotfile_new/cshrc.hspice"
export ENV_HSPICE_VERSION="127"
 
# Attempt to source using bash techniques
if [ -f "$ENV_CSHRC_LSFC2" ] && [ -f "$ENV_CSHRC_HSPICE" ]; then
    # Try method 1: Using bash's source equivalent
    log "Attempting to source using bash dot notation"
    (. "$ENV_CSHRC_LSFC2" && . "$ENV_CSHRC_HSPICE" "$ENV_HSPICE_VERSION") > /dev/null 2>&1
   
    # Check if HSPICE is in path after sourcing
    if command -v hspice >/dev/null 2>&1; then
        log "Successfully set up environment in shell"
        ENV_SETUP_IN_SHELL=1
    else
        # Try method 2: Using csh to source and export variables
        log "Attempting to extract environment variables using csh"
        ENV_SETUP_IN_SHELL=0
        log "Will attempt environment setup in Python"
    fi
else
    log "WARNING: Environment files not found"
    ENV_SETUP_IN_SHELL=0
fi
 
export ENV_SETUP_IN_SHELL
 
# Path to the reference SPICE netlist
MC_SIM_NETLIST="/SIM/DFDS_20211231/Personal/ynie/3-LibCharCerti/2024/N2P/1-FMC_Golden/gen_DECKs/ssgnp_0p450v_m40c_DECKS/delay/DECKS/combinational_INVMDLIMZD0P7BWP130HPNPN3P48CPD_ZN_fall_I_rise_NO_CONDITION_3-5/test_full_MC/mc_sim.sp" 
log "Using netlist: $MC_SIM_NETLIST"
 
# Define sample sizes to test (comma-separated list)
SAMPLE_SIZES="25000,50000, 75000,100000,150000"
log "Sample sizes: $SAMPLE_SIZES"
 
# Define sampling methods to test (comma-separated list)
# Options: lhs, sobol, mc
SAMPLING_METHODS="lhs,sobol"
log "Sampling methods: $SAMPLING_METHODS"
 
# Define the Python script path
SCRIPT_DIR="$(dirname "$(realpath "$0")")"
PYTHON_SCRIPT="$SCRIPT_DIR/process_mc_analysis.py"
log "Python script path: $PYTHON_SCRIPT"
 
# Make sure Python script exists
if [ ! -f "$PYTHON_SCRIPT" ]; then
    log "ERROR: Python script not found at $PYTHON_SCRIPT"
    echo "ERROR: Python script not found at $PYTHON_SCRIPT"
    exit 1
fi
 
# Execute the Python script with arguments
log_section "EXECUTING PYTHON SCRIPT"
log "Running: python3 $PYTHON_SCRIPT $MC_SIM_NETLIST $SAMPLE_SIZES $SAMPLING_METHODS --logfile \"$LOG_FILE\""
log "MC_SIM_NETLIST is : $MC_SIM_NETLIST"
 
/usr/local/python/3.9.10/bin/python3 $PYTHON_SCRIPT --netlist "$MC_SIM_NETLIST" --sample_sizes "$SAMPLE_SIZES" --sampling_methods "$SAMPLING_METHODS" --logfile "$LOG_FILE"
 
if [ $? -eq 0 ]; then
    log_section "COMPLETION"
    log "MC analysis completed successfully. Check the results in output folders."
    echo "MC analysis completed successfully. Check the results in output folders."
else
    log_section "ERROR"
    log "MC analysis failed. Check the log file for details: $LOG_FILE"
    echo "ERROR: MC analysis failed. Check the log file for details: $LOG_FILE"
    exit 1
fi
 
# Usage examples:
#
# Run with default parameters:
# ./run_mc_analysis.sh
#
# Run with custom sample sizes:
# SAMPLE_SIZES="1000,10000,100000" ./run_mc_analysis.sh
#
# Run with custom sampling methods:
# SAMPLING_METHODS="lhs,sobol" ./run_mc_analysis.sh
#
# Run with both custom parameters:
# SAMPLE_SIZES="1000,10000,100000" SAMPLING_METHODS="lhs,sobol" ./run_mc_analysis.sh
#
# Disable debug mode:
# DEBUG_MODE=0 ./run_mc_analysis.sh
 
