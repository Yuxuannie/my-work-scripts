#!/bin/sh
 
# Set parameters
TARGET_ROOT_PATH="/TIER3/DFSD_C651_chamber/Personal/ynie/0-lib_char/2025/Internal/N2_Tanager/3_25c_cworst_T"
SOURCE_PACKAGE_DIR="/SIM/DFSD_20250430_C651_chamber/N2_Tanager_LVF/1-lib_char_auto/run.sh/post_process_kits"
CORNERS="ttg_0p445v ttg_0p480v"
RC_TYPE="cworst_T"  # Replace with your actual RC type
LOG_FILE="Merge_cworst_T.log"
MAX_WORKERS=22  # Set your desired maximum number of workers
 
# Read the mapping file
MAPPING_FILE="dir_mapping.txt"
 
# Loop through each corner and submit the job to process it in sequence
for CORNER in $CORNERS; do
    LOG_DIR="$(pwd)/log_output/$RC_TYPE/$CORNER"  # Construct the log directory path for each corner
 
    # Create the log directory if it does not exist
    mkdir -p $LOG_DIR
 
    # Extract directories for the current corner from the mapping file
    DIRS=$(grep "^$CORNER:" $MAPPING_FILE | cut -d':' -f2)
 
    # Loop through each directory and submit the job for each directory
    for DIR in $DIRS; do
        # Extract the library name from the directory name or another source if needed
        LIB_NAME=$(basename $DIR)
 
        # Use bsub to submit the job to the DMKD_DFSD.q queue with priority 10
        bsub -q DMKD_DFSD.q -sp 10 -J "postprocess_${CORNER}_${LIB_NAME}" /usr/local/python/3.9.10/bin/python3 ../../run.py/postprocess/merge.py \
            --target_root_path $TARGET_ROOT_PATH \
            --source_package_dir $SOURCE_PACKAGE_DIR \
            --corner $CORNER \
            --rc_type $RC_TYPE \
            --log_file $LOG_DIR/$LOG_FILE \
            --log_dir $LOG_DIR \
            --max_workers $MAX_WORKERS \
            --dir $DIR \
            --lib_name $LIB_NAME
    done
 
    # Wait for all jobs for this corner to complete before proceeding to the next corner
    bwait -w "done(postprocess_${CORNER}_*)"
done
 
 
