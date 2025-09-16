#!/bin/bash
 
#=============================================================================
# Arc CSV Cleanup Configuration Script for Full MC
#
# Edit the variables below to configure your analysis:
#=============================================================================
 
# CONFIGURATION - EDIT THESE VARIABLES
#=============================================================================
 
# TARGET DIRECTORY - Path where your corner folders are located
TARGET_DIR="/SIM/DFDS_20211231/Personal/ynie/3-LibCharCerti/2025/N2P_v1.0/1-MC_golden/1-Full_MC_golden"
 
# Available corners (comment out lines with # to exclude them)
CORNERS=(
    "ssgnp_0p450v_m40c"
    "ssgnp_0p465v_m40c"
    "ssgnp_0p480v_m40c"
    "ssgnp_0p495v_m40c"
)
 
# ACTION TO PERFORM - Choose ONE by uncommenting it:
#ACTION="--analyze-only"     # Only analyze, no cleanup
ACTION="--dry-run"          # Show what would be deleted (SAFE)
#ACTION="--cleanup"          # Actually delete directories (DANGEROUS!)
 
#=============================================================================
# END CONFIGURATION
#=============================================================================
 
# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color
 
# Script info
SCRIPT_NAME="arc_cleanup.py"
 
echo -e "${BLUE}======================================${NC}"
echo -e "${BLUE}  Arc CSV Cleanup Configuration${NC}"
echo -e "${BLUE}======================================${NC}"
echo ""
 
# Check if Python script exists in current directory
if [ ! -f "$SCRIPT_NAME" ]; then
    echo -e "${RED}ERROR: $SCRIPT_NAME not found in current directory!${NC}"
    exit 1
fi
 
# Check if target directory exists
if [ ! -d "$TARGET_DIR" ]; then
    echo -e "${RED}ERROR: Target directory '$TARGET_DIR' does not exist!${NC}"
    exit 1
fi
 
# Build corners string
CORNERS_STR=""
for corner in "${CORNERS[@]}"; do
    if [[ ! "$corner" =~ ^[[:space:]]*# ]]; then
        if [ -z "$CORNERS_STR" ]; then
            CORNERS_STR="$corner"
        else
            CORNERS_STR="$CORNERS_STR,$corner"
        fi
    fi
done
 
# Display configuration
echo -e "${GREEN}Configuration:${NC}"
echo "  Script Directory: $(pwd)"
echo "  Target Directory: $TARGET_DIR"
echo "  Corners: $CORNERS_STR"
echo "  Action: $ACTION"
echo ""
 
# Validate configuration
if [ -z "$CORNERS_STR" ]; then
    echo -e "${RED}ERROR: No corners selected!${NC}"
    exit 1
fi
 
# Build and execute command
CMD="/usr/local/python/3.9.10/bin/python3 $SCRIPT_NAME --target-dir \"$TARGET_DIR\" --corners \"$CORNERS_STR\" $ACTION"
 
echo -e "${BLUE}Executing command:${NC}"
echo "  $CMD"
echo ""
 
# Execute the Python script
eval $CMD
exit_code=$?
 
echo ""
if [ $exit_code -eq 0 ]; then
    echo -e "${GREEN}âœ” Script completed successfully${NC}"
else
    echo -e "${RED}âœ— Script completed with errors (exit code: $exit_code)${NC}"
fi
 
exit $exit_code
 
