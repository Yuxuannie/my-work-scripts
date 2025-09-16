#!/bin/csh -f
 
#!/bin/tcsh -f
/CAD/stdcell/DesignKits/SCLD_OBF_2013.06/STD_CORE_CHAR/Script/replace_constraint.pl %non_cons.lib% %cons.lib%
mv constraint_replaced/%non_cons.lib% %ccs.lib%
 
 
