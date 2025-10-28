#!/bin/bash
 
# =============================================================================
# Library Characterization Certification - Collateral Generation Shell Script
# Step 1: Collecting Collaterals for EDA Vendors (CDNS and SNPS)
# =============================================================================
 
# Set parameters
working_dir="/SIM/DFDS_20211231/Personal/ynie/3-LibCharCerti/2025/N2P_v1.0/0-Collateral"
python_script="/SIM/DFDS_20211231/Personal/ynie/Scripts/LibCharCerti/0-Collaterals/gen_collaterals_for_eda.py"
python_cmd="/usr/local/python/3.9.10/bin/python3"
 
# EDA vendor configuration
eda_vendor="CDNS"
process_snps="false"  # Set to "true" to also generate SNPS collaterals
 
# Target corners for N2P v1.0 certification
corners=("ssgnp_0p450v_m40c" "ssgnp_0p465v_m40c" "ssgnp_0p480v_m40c" "ssgnp_0p495v_m40c")
lpe_type="cworst_CCworst_T"
 
# Create a timestamp for logging
timestamp=$(date +"%Y%m%d_%H%M%S")
log_dir="$working_dir/logs"
mkdir -p "$log_dir"
main_log="$log_dir/gen_collaterals_${timestamp}.log"
 
# Export variables for the Python script
export working_dir
export eda_vendor
export lpe_type
export timestamp
export log_dir
export process_snps
 
# Print configuration and log it
{
    echo "================================================================="
    echo "Starting Collateral Generation for Library Characterization"
    echo "================================================================="
    echo "Timestamp: $(date)"
    echo "Working Directory: $working_dir"
    echo "Python Script: $python_script"
    echo "EDA Vendor: $eda_vendor"
    echo "Target Corners: ${corners[*]}"
    echo "LPE Type: $lpe_type"
    echo "Log Directory: $log_dir"
    echo "Main Log File: $main_log"
    echo "================================================================="
 
    # Check if working directory exists
    if [ ! -d "$working_dir" ]; then
        echo "ERROR: Working directory does not exist: $working_dir"
        exit 1
    fi
 
    # Check if 0-from_SCLD folder exists
    scld_dir="$working_dir/0-from_SCLD"
    if [ ! -d "$scld_dir" ]; then
        echo "ERROR: SCLD source directory does not exist: $scld_dir"
        echo "Please ensure the 0-from_SCLD folder contains the original collaterals"
        exit 1
    fi
 
    # Check if Python script exists
    if [ ! -f "$python_script" ]; then
        echo "ERROR: Python script does not exist: $python_script"
        exit 1
    fi
 
    # Check required folders in SCLD directory
    echo "Checking SCLD collateral structure..."
    required_folders=("Netlist" "Template" "Char")
    for folder in "${required_folders[@]}"; do
        if [ -d "$scld_dir/$folder" ]; then
            echo "  Found: $folder"
        else
            echo "  Missing: $folder"
            echo "ERROR: Required folder missing in SCLD directory: $folder"
            exit 1
        fi
    done
 
    # Check for optional Model folder
    if [ -d "$scld_dir/Model" ]; then
        echo "  Found: Model (will be copied to both vendors)"
    else
        echo "  Note: Model folder not found (optional)"
    fi
 
    echo "================================================================="
    echo "Calling Python script for CDNS collateral generation..."
    echo "================================================================="
 
    # Change to working directory
    cd "$working_dir" || {
        echo "ERROR: Failed to change to working directory: $working_dir"
        exit 1
    }
 
    # Call the Python script with arguments
    if $python_cmd "$python_script" \
        --working_dir "$working_dir" \
        --eda_vendor "$eda_vendor" \
        --corners "${corners[@]}" \
        --lpe_type "$lpe_type" \
        --log_level "INFO"; then
       
        echo "================================================================="
        echo "CDNS collateral generation completed successfully!"
        echo "================================================================="
       
        # Check if delivery folder was created
        delivery_dir="$working_dir/1-for_${eda_vendor}"
        if [ -d "$delivery_dir" ]; then
            echo "CDNS delivery folder created: $delivery_dir"
           
            # Show structure of created delivery folder
            echo "CDNS folder structure:"
            tree "$delivery_dir" -L 3 2>/dev/null || ls -la "$delivery_dir"
           
            # Ask user about SNPS processing
            echo "================================================================="
            echo "CDNS collaterals ready!"
            echo "Do you want to generate SNPS collaterals as well? (y/n)"
            echo "Note: SNPS requires translation from CDNS templates"
            read -p "Generate SNPS collaterals? [y/N]: " generate_snps
           
            if [[ "$generate_snps" =~ ^[Yy]$ ]]; then
                echo "================================================================="
                echo "Starting SNPS collateral generation..."
                echo "================================================================="
               
                # Call Python script again for SNPS processing
                if $python_cmd "$python_script" \
                    --working_dir "$working_dir" \
                    --eda_vendor "SNPS" \
                    --corners "${corners[@]}" \
                    --lpe_type "$lpe_type" \
                    --process_snps \
                    --log_level "INFO"; then
                   
                    echo "================================================================="
                    echo "SNPS collateral generation completed successfully!"
                    echo "================================================================="
                   
                    # Check SNPS delivery folder
                    snps_delivery_dir="$working_dir/2-for_SNPS"
                    if [ -d "$snps_delivery_dir" ]; then
                        echo "SNPS delivery folder created: $snps_delivery_dir"
                        echo "SNPS folder structure:"
                        tree "$snps_delivery_dir" -L 3 2>/dev/null || ls -la "$snps_delivery_dir"
                    fi
                else
                    echo "================================================================="
                    echo "ERROR: SNPS collateral generation failed!"
                    echo "================================================================="
                fi
            else
                echo "Skipping SNPS generation."
            fi
           
            # Ask user if they want to create tar archive(s)
            echo "================================================================="
            echo "Collateral generation completed!"
            echo "Do you want to create tar archive(s) for delivery? (y/n)"
            echo "Note: You may want to manually check the contents first."
            read -p "Create tar archive(s)? [y/N]: " create_tar
           
            if [[ "$create_tar" =~ ^[Yy]$ ]]; then
                echo "Creating tar archives..."
                cd "$working_dir" || exit 1
               
                # Create CDNS tar
                cdns_tar="collaterals_for_CDNS_$(date +%Y%m%d_%H%M%S).tar.gz"
                if tar -czf "$cdns_tar" -C "$working_dir" "1-for_CDNS"; then
                    echo "CDNS tar archive created: $working_dir/$cdns_tar"
                    ls -lh "$working_dir/$cdns_tar"
                fi
               
                # Create SNPS tar if folder exists
                if [ -d "$snps_delivery_dir" ]; then
                    snps_tar="collaterals_for_SNPS_$(date +%Y%m%d_%H%M%S).tar.gz"
                    if tar -czf "$snps_tar" -C "$working_dir" "2-for_SNPS"; then
                        echo "SNPS tar archive created: $working_dir/$snps_tar"
                        ls -lh "$working_dir/$snps_tar"
                    fi
                fi
            else
                echo "Skipping tar creation. You can manually create them later with:"
                echo "  cd $working_dir"
                echo "  tar -czf collaterals_for_CDNS_\$(date +%Y%m%d_%H%M%S).tar.gz 1-for_CDNS"
                if [ -d "$snps_delivery_dir" ]; then
                    echo "  tar -czf collaterals_for_SNPS_\$(date +%Y%m%d_%H%M%S).tar.gz 2-for_SNPS"
                fi
            fi
        else
            echo "WARNING: CDNS delivery folder was not created"
        fi
       
        echo "================================================================="
        echo "Summary:"
        echo "  - Source: $scld_dir"
        echo "  - CDNS delivery: $delivery_dir"
        if [ -d "$working_dir/2-for_SNPS" ]; then
            echo "  - SNPS delivery: $working_dir/2-for_SNPS"
        fi
        echo "  - Target corners: ${#corners[@]} corners"
        echo "  - Vendors processed: CDNS$([ -d "$working_dir/2-for_SNPS" ] && echo ", SNPS")"
        echo "================================================================="
       
    else
        echo "================================================================="
        echo "ERROR: Python script execution failed with status code $?"
        echo "================================================================="
        exit 1
    fi
 
    echo "================================================================="
    echo "Collateral generation script completed at $(date)"
    echo "================================================================="
    echo "Next step: Provide the delivery folder(s) to EDA vendor(s) for characterization"
   
} 2>&1 | tee "$main_log"
 
echo "Log file saved to: $main_log"
 
