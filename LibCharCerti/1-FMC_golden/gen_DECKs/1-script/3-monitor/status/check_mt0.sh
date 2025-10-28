#!/bin/bash
 
working_path="/SIM/DFDS_20211231/Personal/ynie/3-LibCharCerti/2025/N2P_v1.0/1-MC_golden/0-FMC_golden/gen_DECKs/"
corners=("ssgnp_0p450v_m40c" "ssgnp_0p465v_m40c" "ssgnp_0p480v_m40c" "ssgnp_0p495v_m40c")
 
# Arrays to store summary counts
corner_names=()
existing_mt0_counts=()
missing_mt0_counts=()
 
for corner in "${corners[@]}"; do
    #search_path="${working_path}/${corner}_DECKS/delay/DECKS/"
    search_path="${working_path}/${corner}_DECKS/hold/DECKS/"
    #search_path="${working_path}/${corner}_DECKS/mpw/DECKS/"
   
    # Debug: Print the constructed search path
    echo "Constructed search path: $search_path"
 
    echo "Checking ${search_path} directory..."
    echo "Folders containing .mt0 files:"
   
    # Check if directory exists
    if [ ! -d "$search_path" ]; then
        echo "Directory $search_path does not exist!"
        echo "----------------------------------------"
        corner_names+=("$corner")
        existing_mt0_counts+=(0)
        missing_mt0_counts+=(0)
        continue
    fi
   
    # Find all .mt0 files in the immediate subdirectories, get their parent directories, and count unique directories
    folders_with_mt0=$(find "$search_path" -maxdepth 2 -type f -name "*.mt0" -exec dirname {} \; | sort | uniq)
    echo "$folders_with_mt0"
   
    # Count the number of unique directories with .mt0 files
    folder_count=$(echo "$folders_with_mt0" | wc -l)
    echo "Total number of folders containing .mt0 files: $folder_count"
   
    # Find all immediate subdirectories and check for missing .mt0 files
    all_folders=$(find "$search_path" -maxdepth 1 -type d)
    folders_without_mt0=""
    missing_count=0
   
    for folder in $all_folders; do
        if [ "$folder" != "$search_path" ]; then
            if ! find "$folder" -maxdepth 1 -type f -name "*.mt0" | grep -q .; then
                folders_without_mt0+="$folder"$'\n'
                missing_count=$((missing_count + 1))
            fi
        fi
    done
   
    echo "Folders missing .mt0 files:"
    echo "$folders_without_mt0"
   
    # Add counts to summary arrays
    corner_names+=("$corner")
    existing_mt0_counts+=("$folder_count")
    missing_mt0_counts+=("$missing_count")
 
    echo "---------------------------------------"
done
 
# Print summary table
echo "Summary Table:"
echo "---------------------------------------"
printf "%-25s %-20s %-20s\n" "Corner" "Folders with .mt0" "Folders missing .mt0"
echo "---------------------------------------"
 
for i in "${!corner_names[@]}"; do
    printf "%-25s %-20d %-20d\n" "${corner_names[$i]}" "${existing_mt0_counts[$i]}" "${missing_mt0_counts[$i]}"
done
echo "---------------------------------------"
 
