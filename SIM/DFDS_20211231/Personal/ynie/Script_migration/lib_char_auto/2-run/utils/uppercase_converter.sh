#!/bin/bash
 
# Check if a directory path is provided
if [ $# -eq 0 ]; then
    echo "Usage: $0 directory_path"
    exit 1
fi
 
WORKING_PATH="$1"
 
# Check if the directory exists
if [ ! -d "$WORKING_PATH" ]; then
    echo "Error: Directory '$WORKING_PATH' does not exist"
    exit 1
fi
 
# Change to the working directory
cd "$WORKING_PATH" || exit 1
 
# Process all files with .spi extension
for file in *.spi; do
    # Skip if no .spi files found
    if [ "$file" = "*.spi" ]; then
        echo "No .spi files found in the directory"
        exit 0
    fi
   
    # Get the filename without the .spi extension
    filename="${file%.spi}"
   
    # Convert filename to uppercase and append .spi
    newname="$(echo "$filename" | tr '[:lower:]' '[:upper:]').spi"
   
    # Skip if the file is already in uppercase
    if [ "$file" != "$newname" ]; then
        # Rename the file
        mv -i "$file" "$newname"
        echo "Renamed: $file -> $newname"
    else
        echo "Skipped: $file (already in uppercase)"
    fi
done
 
echo "Conversion complete!"
 
