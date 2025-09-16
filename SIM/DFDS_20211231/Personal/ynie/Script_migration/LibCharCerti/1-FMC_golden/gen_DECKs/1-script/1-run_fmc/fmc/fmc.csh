#!/bin/csh -f
source /CAD/stdcell/DesignKits/Sponsor/Script/MCQC_automation/Tool_home/cshrc.fmc 17
setenv SNPSLMD_LICENSE_FILE 27020@sjlic5:27020@lic20:27020@f15p7lic20:27020@f15lic3:27020@f15lic4:27020@linux96
setenv LM_LICENSE_FILE 27020@sjlic5:27020@lic20:27020@f15p7lic20:27020@f15lic4:27020@f15lic3:27020@linux96
 
fmc -i ./mc_sim.sp -o ./ -t delay -ns 25000 -ncpu_sens 10 -relin 1.0e-13 -mos_prefix "XM" -finfet 1 -node n2 -hspice_cshrc /tools/dotfile_new/cshrc.hspice -hspice_ver S-2021.09-SP2-1
#fmc -i ./nominal_sim.sp -o ./ -t delay -ns 25000 -ncpu_sens 5 -ncpu_retrain 5 -sim_type 'bisect' -mos_prefix "XM" -relin 1.0e-13 -finfet true -node n2 -u /FSIM/PPA_C651_chamber/DFSD/Personal/ylliuzx/N2_reduced_param_LVF/FMC/previous_run/N12/Vtgm-75mV/c210129_100a/slew/DECKS_FINAL/user_options_file_swp.txt -lsf_q DMKD_DFSD -hspice_cshrc /tools/dotfile_new/cshrc.hspice -hspice_ver S-2021.09-1 -dbg 1
 
 
 
 
