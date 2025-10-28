#!/bin/csh -f
source /tools/dotfile_new/cshrc.liberate 23.1.3.028.isr3
 
setenv ALTOS_MEMORY_OPTIMIZATION_OFF 1
 
liberate --trio run_ldbx.tcl get_cell_attr.py \
         #-in /SIM/DFDS_20211231/Personal/ritaliu/LDBX_rewrite_lib/test_inp/c200701_051a \
         #-out /SIM/DFDS_20211231/Personal/ritaliu/LDBX_rewrite_lib/test_out/c200701_051a \
         #-unit_type_list "time, capacitance, voltage" \
         #-from_unit_list "nS, pF, V" \
         #-to_unit_list "pS, fF, V"  \
            | tee run_args.log
 
 
 
