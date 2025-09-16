#!/bin/bash
# save as: package_text_scripts.sh
 
SCRIPTS_DIR="/SIM/DFDS_20211231/Personal/ynie/Script_migration/"  # Change this to your actual path
OUTPUT_FILE="text_scripts_archive.txt"
SKIPPED_FILE="skipped_files_report.txt"
 
echo "=== TEXT SCRIPTS ARCHIVE CREATED $(date) ===" > "$OUTPUT_FILE"
echo "=== BASE_DIR: $SCRIPTS_DIR ===" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"
 
echo "=== SKIPPED FILES REPORT $(date) ===" > "$SKIPPED_FILE"
echo "=== Files skipped due to binary/encrypted content ===" >> "$SKIPPED_FILE"
echo "" >> "$SKIPPED_FILE"
 
processed_count=0
skipped_count=0
 
# Find all files and check each one
find "$SCRIPTS_DIR" -type f -print0 | while IFS= read -r -d '' file; do
    relative_path="${file#$SCRIPTS_DIR/}"
    file_size=$(wc -c < "$file")
   
    # Check if file is text-based
    file_type=$(file -b "$file")
    mime_type=$(file -b --mime-type "$file")
   
    # Skip if binary, encrypted, or other non-text formats
    if [[ $mime_type == text/* ]] || [[ $file_type == *"ASCII text"* ]] || [[ $file_type == *"UTF-8"* ]] || [[ $file_type == *"empty"* ]]; then
        # Additional check for encrypted content (common patterns)
        if head -c 100 "$file" | grep -qE "BEGIN (ENCRYPTED|PRIVATE KEY|CERTIFICATE)" 2>/dev/null; then
            echo "$relative_path - ENCRYPTED/CERTIFICATE FILE ($file_size bytes)" >> "$SKIPPED_FILE"
            ((skipped_count++))
        else
            # It's a text file, include it
            echo "=== FILE_START ===" >> "$OUTPUT_FILE"
            echo "=== PATH: $relative_path ===" >> "$OUTPUT_FILE"
            echo "=== SIZE: $file_size bytes ===" >> "$OUTPUT_FILE"
            echo "=== TYPE: $file_type ===" >> "$OUTPUT_FILE"
            echo "=== PERMISSIONS: $(stat -c '%a' "$file") ===" >> "$OUTPUT_FILE"
            echo "=== CONTENT_START ===" >> "$OUTPUT_FILE"
           
            cat "$file" >> "$OUTPUT_FILE"
           
            echo "" >> "$OUTPUT_FILE"
            echo "=== CONTENT_END ===" >> "$OUTPUT_FILE"
            echo "=== FILE_END ===" >> "$OUTPUT_FILE"
            echo "" >> "$OUTPUT_FILE"
           
            ((processed_count++))
            echo "Processed: $relative_path"
        fi
    else
        # Skip binary/non-text files
        echo "$relative_path - $file_type ($file_size bytes)" >> "$SKIPPED_FILE"
        ((skipped_count++))
        echo "Skipped: $relative_path (binary/non-text)"
    fi
done
 
# Add directory structure
echo "=== DIRECTORY_STRUCTURE ===" >> "$OUTPUT_FILE"
find "$SCRIPTS_DIR" -type d | sed "s|$SCRIPTS_DIR|.|" >> "$OUTPUT_FILE"
echo "=== STRUCTURE_END ===" >> "$OUTPUT_FILE"
 
# Add summary to skipped file
echo "" >> "$SKIPPED_FILE"
echo "=== SUMMARY ===" >> "$SKIPPED_FILE"
echo "Total files processed: $processed_count" >> "$SKIPPED_FILE"
echo "Total files skipped: $skipped_count" >> "$SKIPPED_FILE"
 
echo ""
echo "========================================="
echo "Archive created: $OUTPUT_FILE"
echo "Skipped files report: $SKIPPED_FILE"
echo "Text files processed: $processed_count"
echo "Files skipped: $skipped_count"
echo "Archive size: $(du -h "$OUTPUT_FILE" | cut -f1)"
echo "========================================="
 
