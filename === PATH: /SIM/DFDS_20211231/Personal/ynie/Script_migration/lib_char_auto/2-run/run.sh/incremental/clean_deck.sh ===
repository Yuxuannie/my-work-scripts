#!/bin/bash
 
# Name of the Python script
PYTHON_SCRIPT="../../run.py/cleanup_script.py"
 
# Check if the Python script exists
if [ ! -f "$PYTHON_SCRIPT" ]; then
    echo "Error: $PYTHON_SCRIPT not found!"
    exit 1
fi
 
# Check for the input files
if [ ! -f "failed_simulations.txt" ]; then
    echo "Error: failed_simulations.txt not found!"
    exit 1
fi
 
if [ ! -f "not_started_simulations.txt" ]; then
    echo "Error: not_started_simulations.txt not found!"
    exit 1
fi
 
# Run the Python script
echo "Running the cleanup script..."
/usr/local/python/3.9.10/bin/python3 "$PYTHON_SCRIPT"
 
echo "Script execution completed."
 
 
