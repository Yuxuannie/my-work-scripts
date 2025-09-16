#!/bin/csh
 
if ($#argv != 1) then
    echo "Usage: $0 <keyword_file>"
    exit 1
endif
 
set keyword_file = $argv[1]
 
if (! -e $keyword_file) then
    echo "Error: File '$keyword_file' does not exist."
    exit 1
endif
 
foreach keyword (`cat $keyword_file`)
    echo "Searching for keyword: $keyword"
 
    foreach file (`find . -type f`)
        grep -q "$keyword" $file
        if ($status == 0) then
            echo "Match found in file: $file"
        endif
    end
end
 
echo "Search complete."
 
 
