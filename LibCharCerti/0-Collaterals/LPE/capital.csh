#!/bin/bash
 
# Loop through all files in the current directory
for file in *; do
    # Check if it's a regular file
    if [ -f "$file" ]; then
        # Get the extension
        ext="${file##*.}"
        # Get the basename (filename without extension)
        base="${file%.*}"
       
        # If the extension is "spi", keep it lowercase
        if [ "$ext" = "spi" ]; then
            # Convert only the base name to uppercase
            newname="$(echo "$base" | tr '[:lower:]' '[:upper:]').spi"
        else
            # Convert the entire filename to uppercase
            newname="$(echo "$file" | tr '[:lower:]' '[:upper:]')"
        fi
       
        # Rename the file if the name would change
        if [ "$file" != "$newname" ]; then
            mv "$file" "$newname"
            echo "Renamed: $file -> $newname"
        fi
    fi
done
 
