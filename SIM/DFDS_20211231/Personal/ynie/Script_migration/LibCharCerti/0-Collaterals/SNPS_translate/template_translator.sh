#!/bin/tcsh -f
source /CAD/stdcell/DesignKits/SCLD_OBF_2013.06/STD_CORE_CHAR/../OBF.cshrc
set pwd=`pwd`
foreach liberate_template (`ls tcb*tcl`)
            cd $pwd
            #set lib = `echo $liberate_template | sed 's/c99.*//'`
            #set golden_lib=`ls seed_lib/${lib}*.lib`
            echo "$liberate_template"
            #echo "$golden_lib"
            perl /CAD/stdcell/DesignKits/Sponsor/Script/OBF/step3/sis_template_transformer.pl $pwd/$liberate_template /CAD/stdcell/DesignKits/Sponsor/Script/OBF/step3/PrimeLib_char_template/tcbn02/A341_n02_v5/map.file.v3_mdy $pwd/Template_sis /CAD/stdcell/DesignKits/Sponsor/Script/OBF/step3/sis_char_template/tcbn05/Formal/special_settings.tcl_v7 seed.lib
            cd $pwd/Template_sis
            perl /CAD/stdcell/DesignKits/Sponsor/Script/OBF/step3/sis_template_inQC.pl $liberate_template.sis
            #perl /SIM/cn_stdcell1/users/ylium/Script/replace_sp_all.pl $liberate_template.sis
            ## hard code fixing for base
            perl /CAD/stdcell/DesignKits/Sponsor/Script/OBF/step3/ff_hidden_specified_q.pl $liberate_template.sis
           
            ## hard code fixing for pm
            #perl /CAD/stdcell/DesignKits/Sponsor/Script/OBF/step3/pm_templ_fix.pl $liberate_template.sis
           
            ## post process for ALL TEMPLATE
/CAD/stdcell/DesignKits/Sponsor/Script/OBF/step3/post_processing_cus_setting.pl $liberate_template.sis
end
 
 
echo done
 
 
