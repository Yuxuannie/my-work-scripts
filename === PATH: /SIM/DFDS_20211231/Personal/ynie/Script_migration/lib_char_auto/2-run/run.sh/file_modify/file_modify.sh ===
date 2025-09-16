#!/bin/bash
 
# File name replacement
## Replace "TTGGlobal" with "TTGlobal" in all .inc files
find . -name "*.inc" -exec sed -i 's/TTGGlobal/TTGlobal/g' {} \;
 
## Replace "ssgnp" with "ttg" in filenames (including subdirectories)
find . -type f -name "*ssgnp*" -exec bash -c 'mv "$1" "${1//ssgnp/ttg}"' _ {} \;
find . -type f -name "*m25c*" -exec bash -c 'mv "$1" "${1//m25c/25c}"' _ {} \;
find . -type f -name "*cworst_T*" -exec bash -c 'mv "$1" "${1//cworst_T/typical}"' _ {} \;
 
# LSF Job Management
## Kill all your jobs
bkill 0
 
## Kill specific jobs containing "25c_typical"
bjobs -J "*25c_typical*" | awk 'NR>1 {print $1}' | xargs bkill
 
## Stop new job submissions (using alias method)
alias bsub="echo 'Job submissions temporarily disabled'"
# To re-enable: unalias bsub
 
# Directory Operations
## Delete all folders starting with "altos" in current directory and subdirectories
find . -type d -name "altos*" -exec rm -rf {} +
 
# Search Operations
## Search for "cworst_T" in all .tcl files with highlighting
grep -r --color=always "cworst_T" --include="*.tcl" .
 
# Efficient File Operations for Large Directories
## Quick find and replace in files containing "0p800"
find . -name "*0p800*" -type f -exec sed -i 's/cworst_T/typical/g' {} +
 
## Alternative two-step approach for very large directories
find . -name "*0p800*" -type f > matching_files.txt
sed -i 's/cworst_T/typical/g' $(cat matching_files.txt)
 
# Warning: Always test these commands with a small subset of files first
# Use with caution as some commands like rm -rf and sed -i make permanent changes
 
 
