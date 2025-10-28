PMC_IC_TEMPLATE = '/CAD/stdcell/DesignKits/Sponsor/Script/MCQC_automation/Template/v1.6.10/SPICE_Templates/'
PMC_WO_IC_TEMPLATE = '/CAD/stdcell/DesignKits/Sponsor/Script/MCQC_automation/Template/v1.6.10/SPICE_Templates_PMC_woic/'
 
 
VCP_DECK = {
    'non_seq_hold/template__retn__nonseqhold__RETN__fall__CD__rise__glitch__minq__minbl_b__2.sp',
    'non_seq_hold/template__retn__nonseq__RETN__fall__SDN__fall__glitch__maxq__maxbl_b__2.sp',
    'non_seq_setup/template__retn__nonseqsetup__RETN__fall__CD__rise__pushout__2.sp',
    'non_seq_setup/template__retn__nonseqsetup__RETN__fall__SDN__fall__pushout__2.sp',
    'non_seq_hold/template__retn__nonseqhold__RETN__fall__CD__rise__SDN__glitch__minq__maxqx__2.sp',
    'non_seq_hold/template__retn__nonseqhold__RETN__fall__SDN__fall__notCD__glitch__maxq__minqx__2.sp',
    'non_seq_hold/template__retn__nonseqhold__RETN__fall__CD__rise__glitch__minq__minbl_b__4.sp',
    'non_seq_hold/template__syn3__retn__nonseqhold__RETN__fall__CD__rise__glitch__minq__minbl_b__4.sp',
    'non_seq_hold/template__syn4__retn__nonseqhold__RETN__fall__CD__rise__glitch__minq__minbl_b__4.sp',
    'non_seq_hold/template__syn5__retn__nonseqhold__RETN__fall__CD__rise__glitch__minq__minbl_b__4.sp',
    'non_seq_hold/template__syn6__retn__nonseqhold__RETN__fall__CD__rise__glitch__minq__minbl_b__4.sp'
}
 
 
def replace_vcp_value(nominal_buffer, to_be='vss_value'):
    for idx,  value in enumerate(nominal_buffer.copy()):
        if 'VCP CP' in value:
            value = value.replace("VCP CP 0 'vss_value'",
                                  "VCP CP 0 '{to_be}'".format(to_be=to_be))
            value = value.replace("VCP CP 0 'vdd_value'",
                                  "VCP CP 0 '{to_be}'".format(to_be=to_be))
            nominal_buffer[idx] = value
            break
    return nominal_buffer
 
 
def decide_pmc_template_deck_path(template_deck_path):
    if 'woic' in template_deck_path:
        return PMC_WO_IC_TEMPLATE
    else:
        return PMC_IC_TEMPLATE
 
 
def has_initail_condition(template_deck_path):
    return 'woic' not in template_deck_path
 
 
def replace_template_deck_name(nominal_buffer, template_deck_name, to_be='_Vss.sp'):
    for i in range(len(nominal_buffer)):
        if template_deck_name in nominal_buffer[i]:
            nominal_buffer[i] = nominal_buffer[i].replace(
                template_deck_name, template_deck_name.replace('.sp', to_be))
    return nominal_buffer
 
