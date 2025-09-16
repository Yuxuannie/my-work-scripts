#!/bin/tcsh -f
 
#source /tools/dotfile_new/cshrc.liberate 21.1.2.270_7
 
source /tools/dotfile_new/cshrc.liberate 23.1.8.204
 
#run_create_ctpm
liberate --trio /FSIM/PPA_C651_chamber/DFSD/Personal/ylliuzx/Library_script/Remove_cell/run_ldbx.tcl /FSIM/PPA_C651_chamber/DFSD/Personal/ylliuzx/Library_script/Remove_cell/remove_cell.py \
    %input_lib% \
    %custom_cell_list% \
    %output_lib%
 
 
 
