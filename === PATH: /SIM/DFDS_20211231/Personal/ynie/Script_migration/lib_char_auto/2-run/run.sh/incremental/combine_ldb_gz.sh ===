#!/bin/bash
 
# Paths to your folders
folderA="/TIER3/DFSD_C651_chamber/Personal/ynie/0-lib_char/2025/Internal/N2_Tanager/3_25c_cworst_T/ttg_0p445v/tcbn02_bwph130pnpnl3p48cpd_base_svt_c230828_094b/LVF/Char/altos.f15p7r4m24a28.T20250203143322783474S0040625.ldb.gz"
folderB="/TIER3/DFSD_C651_chamber/Personal/ynie/0-lib_char/2025/Internal/N2_Tanager/3_25c_cworst_T/ttg_0p445v/tcbn02_bwph130pnpnl3p48cpd_base_svt_c230828_094b/LVF/Char/altos.f15p7r4m24a28.T20250205004116178192S0002695.ldb.gz"
# Remove empty directories in folder A
find "$folderA" -type d -empty -delete
 
 
 
# Track if any folders were copied
copied_any=false
 
# Loop through each item in folder B
for dir in "$folderB"/*; do
  # Check if it is a directory
  if [ -d "$dir" ]; then
    # Get the basename of the directory
    dirname=$(basename "$dir")
    # Check if the directory does not exist in folder A
    if [ ! -d "$folderA/$dirname" ]; then
      # Copy the directory from B to A
      cp -r "$dir" "$folderA"
      echo "Copied $dirname to $folderA"
      copied_any=true
    fi
  fi
done
 
# Inform if all folders in B already exist in A
if [ "$copied_any" = false ]; then
  echo "All folders in B already exist in A. No new folders were copied."
fi
 
 
