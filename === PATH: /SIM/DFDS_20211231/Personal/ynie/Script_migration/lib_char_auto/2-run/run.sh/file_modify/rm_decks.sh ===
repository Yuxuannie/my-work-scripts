#!/bin/bash
 
# List of paths
paths=(
    "/SIM/DFSD_20250430_C651_chamber/N2_Tanager_LVF/./tcbn02_bwph130nppnl3p48cpd_base_elvt_c230828_094a/LVF/Char"
    "/SIM/DFSD_20250430_C651_chamber/N2_Tanager_LVF/./tcbn02_bwph130nppnl3p48cpd_base_lvt_c230828_094a/LVF/Char"
    "/SIM/DFSD_20250430_C651_chamber/N2_Tanager_LVF/./tcbn02_bwph130nppnl3p48cpd_base_lvtll_c230828_094a/LVF/Char"
    "/SIM/DFSD_20250430_C651_chamber/N2_Tanager_LVF/./tcbn02_bwph130nppnl3p48cpd_base_svt_c230828_094a/LVF/Char"
    "/SIM/DFSD_20250430_C651_chamber/N2_Tanager_LVF/./tcbn02_bwph130nppnl3p48cpd_base_ulvt_c230828_094a/LVF/Char"
    "/SIM/DFSD_20250430_C651_chamber/N2_Tanager_LVF/./tcbn02_bwph130nppnl3p48cpd_base_ulvtll_c230828_094a/LVF/Char"
)
 
# Iterate over each path
for path in "${paths[@]}"; do
    # Find directories matching 'deck*' and print them
    find "$path" -type d -name 'deck*' -print -exec rm -rf {} +
   #find "$path" -type d -name 'deck*' -print
done
 
 
