#!/bin/tcsh -f
source /CAD/stdcell/DesignKits/SCLD_OBF_2013.06/STD_CORE_CHAR/../OBF.cshrc
set template=/SIM/stdcell_mdy_3_debug_C651_chamber/jwlinu/toEmma/tcbn02p_bwph156dpnpnl3p48cpd_mbrff_lvt_c250321ffgnp_0p450v_125c_cbest.template.tcl
set seed_lib=/PROJ/sclpd_char_C651_chamber/stdcell_source/tcbn02p_bwph156dpnpnl3p48cpd_mbrff_lvt_c250321_093a/FE/lib//tcbn02p_bwph156dpnpnl3p48cpd_mbrff_lvt_c987654ss0p765vm40c.lib
 
perl /CAD/stdcell/DesignKits/Sponsor/Script/OBF/step2/sdk_mb_sis_template_transformer.pl $template
mv -f "${template}_sis" "${template}.sis"
perl /CAD/stdcell/DesignKits/Sponsor/Script/OBF/step2/sdk_sis_template_special_setting.pl ${template}.sis /CAD/stdcell/DesignKits/Sponsor/Script/OBF/step3/PrimeLib_char_template/tcbn02/C651_n02_v3/sdk/special_settings.tcl_v12 $seed_lib
perl /CAD/stdcell/DesignKits/Sponsor/Script/OBF/step2/sdk_modify_multiswitch_to_singleswitch.pl ${template}.sis
 
 
perl /CAD/stdcell/DesignKits/Sponsor/Script/OBF/step2/sdk_sis_template_inQC.pl ${template}.sis
 
## hard code fixing for base
 
## hard code fixing for pm
 
 
echo done
 
