#!/bin/csh -f
 
#perl /CAD/stdcell/DesignKits/Sponsor/Script/OBF/step4/transform_trio2bundle.pl kit_gen_tcbn03a_bwph169l3p48cpd_base_ulvtll_c250516_090a.txt ../Char/char_trio_groupLPE_ssgnp_cworst_T_m25c.tcl
 
# For Base cell type
foreach folder (`\ls -d ../tcbn02p_bwph130*base*`)
    echo $folder
    set folder_1 = `basename $folder`
    set name = `basename $folder | sed 's#_093a##g'`
    echo $name
 
    cp -rf kit_template.txt ${name}.txt
 
    sed -i "s#%library_name%#${name}#g" ${name}.txt
    perl /CAD/stdcell/DesignKits/Sponsor/Script/OBF/step4/transform_trio2bundle.pl ${name}.txt ../$folder_1/Char/char_trio_groupLPE_ssgnp_cworst_T_m25c.tcl
end
 
 
# For MB cell type
foreach folder (`\ls -d ../tcbn02p_bwph130*mb*`)
    echo $folder
    set folder_1 = `basename $folder`
    set name = `basename $folder | sed 's#_093a##g'`
    echo $name
 
    cp -rf kit_template.txt ${name}.txt
 
    sed -i "s#%library_name%#${name}#g" ${name}.txt
    perl /CAD/stdcell/DesignKits/Sponsor/Script/OBF/step4/transform_trio2bundle.pl ${name}.txt ../$folder_1/Char/char_trio_groupLPE_ssgnp_cworst_T_m25c__cons.tcl
    perl /CAD/stdcell/DesignKits/Sponsor/Script/OBF/step4/transform_trio2bundle.pl ${name}.txt ../$folder_1/Char/char_trio_groupLPE_ssgnp_cworst_T_m25c__non_cons.tcl
end
 
 
