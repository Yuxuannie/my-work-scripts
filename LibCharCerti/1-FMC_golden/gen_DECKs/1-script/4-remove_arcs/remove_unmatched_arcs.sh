#!/bin/bash
 
# COMMON ARCS FILE PATH
COMMON_ARC_FILE="/SIM/DFDS_20211231/Personal/ynie/3-LibCharCerti/2025/N2P_v1.0/2-select_2nd_round/2-Full_MC_golden/0-script/3-remove_arcs/common_arcs_list.txt"
 
# ROOT WORKING DIRECTORY
ROOT_DIR="/SIM/DFDS_20211231/Personal/ynie/3-LibCharCerti/2025/N2P_v1.0/2-select_2nd_round/1-FMC_golden/gen_DECKs"
 
# Path to the Python script
PYTHON_SCRIPT="./remove_unmatched_arcs.py"
 
# Validate COMMON_ARC_FILE
if [[ ! -f "$COMMON_ARC_FILE" ]]; then
    echo "Error: Common arcs file not found: $COMMON_ARC_FILE"
    exit 1
fi
 
# Validate ROOT_DIR
if [[ ! -d "$ROOT_DIR" ]]; then
    echo "Error: Root directory not found: $ROOT_DIR"
    exit 1
fi
 
# Directly specify corners and types as variables in the shell script.
# Set CORNER_SELECTION to "ALL" for processing all corners, or specify a single corner.
CORNER_SELECTION="ALL"  # Options: "ALL", "ssgnp_0p450v_m40c_DECKS", "ssgnp_0p465v_m40c_DECKS", etc.
 
# Set TYPE_SELECTION to "ALL" for processing all types, or specify a single type.
TYPE_SELECTION="ALL"  # Options: "ALL", "delay", "hold", "mpw"
 
# Define all available corners and types for validation purposes.
CORNERS=(
            "ssgnp_0p450v_m40c_DECKS"
            "ssgnp_0p465v_m40c_DECKS"
            "ssgnp_0p480v_m40c_DECKS"
            "ssgnp_0p495v_m40c_DECKS")
 
TYPES=("delay")
 
# Process corner selection
if [[ "$CORNER_SELECTION" == "ALL" ]]; then
    SELECTED_CORNERS=("${CORNERS[@]}")
else
    if [[ ! " ${CORNERS[@]} " =~ " ${CORNER_SELECTION} " ]]; then
        echo "Error: Invalid corner selection: $CORNER_SELECTION"
        exit 1
    fi
    SELECTED_CORNERS=("$CORNER_SELECTION")
fi
 
# Process type selection
if [[ "$TYPE_SELECTION" == "ALL" ]]; then
    SELECTED_TYPES=("${TYPES[@]}")
else
    if [[ ! " ${TYPES[@]} " =~ " ${TYPE_SELECTION} " ]]; then
        echo "Error: Invalid type selection: $TYPE_SELECTION"
        exit 1
    fi
    SELECTED_TYPES=("$TYPE_SELECTION")
fi
 
# Process all combinations of corners and types
for CORNER in "${SELECTED_CORNERS[@]}"; do
    CORNER_PATH="${ROOT_DIR}/${CORNER}"
    if [[ ! -d "$CORNER_PATH" ]]; then
        echo "Error: Corner directory not found: $CORNER_PATH"
        continue
    fi
 
    for TYPE in "${SELECTED_TYPES[@]}"; do
        TYPE_PATH="${CORNER_PATH}/${TYPE}"
        if [[ ! -d "$TYPE_PATH" ]]; then
            echo "Warning: Type directory not found: $TYPE_PATH"
            continue
        fi
 
        # Call the Python script with parameters for this corner/type combination
        python3 "$PYTHON_SCRIPT" "$COMMON_ARC_FILE" "$TYPE_PATH"
    done
done
 
echo "Processing completed."
 
