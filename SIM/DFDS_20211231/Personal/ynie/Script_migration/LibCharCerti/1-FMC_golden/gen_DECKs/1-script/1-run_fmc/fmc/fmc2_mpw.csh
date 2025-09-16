#!/bin/csh -f
#source /tools/dotfile_new/cshrc.hspice S-2021.09-1
source /CAD/stdcell/DesignKits/Sponsor/Script/MCQC_automation/Tool_home/cshrc.fmc 20
setenv SNPSLMD_LICENSE_FILE 27020@sjlic5:27020@lic20:27020@f15p7lic20:27020@f15lic3:27020@f15lic4:27020@linux96
setenv LM_LICENSE_FILE 27020@sjlic5:27020@lic20:27020@f15p7lic20:27020@f15lic4:27020@f15lic3:27020@linux96
 
#fmc -i ./nominal_sim.sp -o ./ -t delay -ns 5 -ncpu_sens 1 -relin 1.0e-13 -mos_prefix "XM" -finfet 1 -node n6e -hspice_cshrc /tools/dotfile_new/cshrc.hspice -hspice_ver S-2021.09-1 -u /CAD/stdcell/DesignKits/Sponsor/Script/MCQC_automation/Template/user_options_file_swp.txt -dbg 1
fmc -i ./mc_sim.sp -o ./ -t constraint -ns 100000 -ncpu_sens 5 -ncpu_retrain 5 -opt_meas_name "cp2cp" -mos_prefix "X" -sim_type 'bisect' -relin 1.0e-13 -finfet 1 -node n2 -lsf_q all -hspice_cshrc /tools/dotfile_new/cshrc.hspice -hspice_ver V-2023.12-SP2-2
 
 
 
 
