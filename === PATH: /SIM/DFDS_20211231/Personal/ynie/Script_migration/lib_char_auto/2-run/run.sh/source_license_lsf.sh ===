#!/bin/bash
 
# -----------------------------------------------------
# Source License & LSF
# -----------------------------------------------------
 
echo "Sourcing LSF..."
csh -c 'source /tools/dotfile_new/cshrc.lsfc2'
if [ $? -ne 0 ]; then
    echo "Error: Failed to source the LSF."
    exit 1
fi
 
echo "Sourcing license..."
./altos_init # Adjust the path to your license initialization script
if [ $? -ne 0 ]; then
    echo "Error: Failed to source the license file."
    exit 1
fi
 
 
