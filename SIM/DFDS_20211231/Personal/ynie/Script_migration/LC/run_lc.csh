#! /bin/csh
 
 
setenv SNPSLMD_LICENSE_FILE 27020@sjlic5:27020@sjlic3:27020@tsmc8
setenv LM_LICENSE_FILE 27020@sjlic5:27020@sjlic3:27020@tsmc8
setenv LC_ENABLE_LCA_BETA_LICENSE_CHECK true
setenv LC_DISABLE_TECH1_SENSITIVITY true
 
 
setenv META_QUEUE 1
setenv META_QUEUE_TIME -1 
setenv CDPL_DEBUG_SUBMIT_TIMEOUT  3600
 
setenv LC_ENABLE_LCA_BETA_LICENSE_CHECK true
setenv LC_DISABLE_TECH1_SENSITIVITY true
 
 
/SIM/DFDS_20211231/Personal/ynie/0-lib_char/2025/External/sens_char/Liberate/01_sens_lib_lccheck/LC_build/V-2023.12-SP5-6/install/lc/V-2023.12-SP5-6/bin/lc_shell -f  lc_check.tcl
 
echo done
 
