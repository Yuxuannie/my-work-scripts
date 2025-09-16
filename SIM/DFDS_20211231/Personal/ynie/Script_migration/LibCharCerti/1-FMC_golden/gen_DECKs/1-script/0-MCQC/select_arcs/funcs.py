import fnmatch
 
# Globals
delay_arc_types = ["combinational",
                   "combinational_fall", "combinational_rise",
                   "edge", "falling_edge", "rising_edge",
                   "three_state_disable", "three_state_enable",
                   "clear", "preset"]
 
 
def mapCharacteristicsToTemplate(arc_type=None,
                                 cell_name=None,
                                 pin=None,
                                 pin_dir=None,
                                 rel_pin=None,
                                 rel_pin_dir=None,
                                 act_pin=None,
                                 act_pin_dir=None,
                                 when=None,
                                 probe_list=None,
                                 template_type=None):
 
    template_name = None
    if template_type.upper() == "HSPICE":
        template_name = getHspiceTemplateName(cell_name, arc_type,
                                              pin, pin_dir, rel_pin, rel_pin_dir, act_pin, act_pin_dir,
                                              when, probe_list)
    elif template_type.upper() == "THANOS":
        template_name = getThanosTemplateName(cell_name, arc_type,
                                              pin, pin_dir, rel_pin, rel_pin_dir,
                                              when, probe_list)
    return template_name
 
 
def getHspiceTemplateName(cell_name, arc_type, constr_pin, constr_pin_dir, rel_pin,
                          rel_pin_dir, activ_pin, activ_pin_dir, when, probe_list):
 
########################################################################################################################
### Modified by : Yuxuan Nie
### Modified at : 13/12/2024
### Purpose: For 1st phase N2P v0.9 Lib char certi
#########################################################################################################################
 
 
###     INVMDLIMZD0P7BWP130HPNPN3P48CPD
    if( arc_type in delay_arc_types and
            fnmatch.fnmatch(cell_name, "INVMDLIMZD0P7BWP130HPNPN3P48CPD") and
            constr_pin == "ZN" and
            constr_pin_dir == "fall" and
            rel_pin == "I" and
            rel_pin_dir == "rise"):
 
        template_name = "hack_template_v2/template__invdX__fall.sp"
        return template_name
 
 
    if( arc_type in delay_arc_types and
            fnmatch.fnmatch(cell_name, "INVMDLIMZD0P7BWP130HPNPN3P48CPD") and
            constr_pin == "ZN" and
            constr_pin_dir == "rise" and
            rel_pin == "I" and
            rel_pin_dir == "fall"):
 
        template_name = "hack_template_v2/template__invdX__rise.sp"
        return template_name
 
###     INVMDLIMZD4BWP130HPNPN3P48CPD
    if( arc_type in delay_arc_types and
            fnmatch.fnmatch(cell_name, "INVMDLIMZD4BWP130HPNPN3P48CPD") and
            constr_pin == "ZN" and
            constr_pin_dir == "fall" and
            rel_pin == "I" and
            rel_pin_dir == "rise"):
 
        template_name = "hack_template_v2/template__invdX__fall.sp"
        return template_name
 
   
    if( arc_type in delay_arc_types and
            fnmatch.fnmatch(cell_name, "INVMDLIMZD4BWP130HPNPN3P48CPD") and
            constr_pin == "ZN" and
            constr_pin_dir == "rise" and
            rel_pin == "I" and
            rel_pin_dir == "fall"):
 
        template_name = "hack_template_v2/template__invdX__rise.sp"
        return template_name
 
###     ND2MDLIMZD0P7BWP130HPNPN3P48CPD
    if( arc_type in delay_arc_types and
            fnmatch.fnmatch(cell_name, "ND2MDLIMZD0P7BWP130HPNPN3P48CPD") and
            constr_pin == "ZN" and
            constr_pin_dir == "fall" and
            rel_pin == "A1" and
            rel_pin_dir == "rise"):
 
        template_name = "hack_template_v2/template__ND2_inpin_rise_delay_fall.sp"
        return template_name
 
 
    if( arc_type in delay_arc_types and
            fnmatch.fnmatch(cell_name, "ND2MDLIMZD0P7BWP130HPNPN3P48CPD") and
            constr_pin == "ZN" and
            constr_pin_dir == "rise" and
            rel_pin == "A1" and
            rel_pin_dir == "fall"):
 
        template_name = "hack_template_v2/template__ND2_inpin_fall_delay_rise.sp"
        return template_name
 
###     ND2MDLIMZD4BWP130HPNPN3P48CPD
    if( arc_type in delay_arc_types and
            fnmatch.fnmatch(cell_name, "ND2MDLIMZD4BWP130HPNPN3P48CPD") and
            constr_pin == "ZN" and
            constr_pin_dir == "fall" and
            rel_pin == "A1" and
            rel_pin_dir == "rise"):
 
        template_name = "hack_template_v2/template__ND2_inpin_rise_delay_fall.sp"
        return template_name
 
 
    if( arc_type in delay_arc_types and
            fnmatch.fnmatch(cell_name, "ND2MDLIMZD4BWP130HPNPN3P48CPD") and
            constr_pin == "ZN" and
            constr_pin_dir == "rise" and
            rel_pin == "A1" and
            rel_pin_dir == "fall"):
 
        template_name = "hack_template_v2/template__ND2_inpin_fall_delay_rise.sp"
        return template_name
 
###     ND4MDLIMZD0P7BWP130HPNPN3P48CPD
    if( arc_type in delay_arc_types and
            fnmatch.fnmatch(cell_name, "ND4MDLIMZD0P7BWP130HPNPN3P48CPD") and
            constr_pin == "ZN" and
            constr_pin_dir == "fall" and
            rel_pin == "A1" and
            rel_pin_dir == "rise"):
 
        template_name = "hack_template_v2/template__ND4_inpin_rise_delay_fall.sp"
        return template_name
 
 
    if( arc_type in delay_arc_types and
            fnmatch.fnmatch(cell_name, "ND4MDLIMZD0P7BWP130HPNPN3P48CPD") and
            constr_pin == "ZN" and
            constr_pin_dir == "rise" and
            rel_pin == "A1" and
            rel_pin_dir == "fall"):
 
        template_name = "hack_template_v2/template__ND4_inpin_fall_delay_rise.sp"
        return template_name
 
###     ND4MDLIMZD4BWP130HPNPN3P48CPD
    if( arc_type in delay_arc_types and
            fnmatch.fnmatch(cell_name, "ND4MDLIMZD4BWP130HPNPN3P48CPD") and
            constr_pin == "ZN" and
            constr_pin_dir == "fall" and
            rel_pin == "A1" and
            rel_pin_dir == "rise"):
 
        template_name = "hack_template_v2/template__ND4_inpin_rise_delay_fall.sp"
        return template_name
 
 
    if( arc_type in delay_arc_types and
            fnmatch.fnmatch(cell_name, "ND4MDLIMZD4BWP130HPNPN3P48CPD") and
            constr_pin == "ZN" and
            constr_pin_dir == "rise" and
            rel_pin == "A1" and
            rel_pin_dir == "fall"):
 
        template_name = "hack_template_v2/template__ND4_inpin_fall_delay_rise.sp"
        return template_name
 
###     CKLHQOPPLCHMZD4BWP130HPNPN3P48CPD
    if( arc_type in delay_arc_types and
            fnmatch.fnmatch(cell_name, "CKLHQOPPLCHMZD4BWP130HPNPN3P48CPD") and
            constr_pin == "Q" and
            constr_pin_dir == "fall" and
            rel_pin == "CPN" and
            rel_pin_dir == "fall" and
            "!E&TE" in when):
 
        template_name = "hack_template_v2/template__CKLHQD_inpin_fall_delay_fall.sp"
        return template_name
 
    if( arc_type in delay_arc_types and
        fnmatch.fnmatch(cell_name, "CKLHQOPPLCHMZD4BWP130HPNPN3P48CPD") and
        constr_pin == "Q" and
        constr_pin_dir == "rise" and
        rel_pin == "CPN" and
        rel_pin_dir == "rise" and
        "!E&TE" in when):
   
        template_name = "hack_template_v2/template__CKLHQD_inpin_rise_delay_rise.sp"
        return template_name
 
###     CKLHQOPPLCHMZD1BWP130HPNPN3P48CPD
    if( arc_type in delay_arc_types and
            fnmatch.fnmatch(cell_name, "CKLHQOPPLCHMZD1BWP130HPNPN3P48CPD") and
            constr_pin == "Q" and
            constr_pin_dir == "fall" and
            rel_pin == "CPN" and
            rel_pin_dir == "fall" and
            "!E&TE" in when):
 
        template_name = "hack_template_v2/template__CKLHQD_inpin_fall_delay_fall.sp"
        return template_name
 
    if( arc_type in delay_arc_types and
        fnmatch.fnmatch(cell_name, "CKLHQOPPLCHMZD1BWP130HPNPN3P48CPD") and
        constr_pin == "Q" and
        constr_pin_dir == "rise" and
        rel_pin == "CPN" and
        rel_pin_dir == "rise" and
        "!E&TE" in when):
   
        template_name = "hack_template_v2/template__CKLHQD_inpin_rise_delay_rise.sp"
        return template_name
 
###     AOI33M1LIMZD0P7BWP130HPNPN3P48CPD
    if( arc_type in delay_arc_types and
                fnmatch.fnmatch(cell_name, "AOI33M1LIMZD0P7BWP130HPNPN3P48CPD") and
                constr_pin == "ZN" and
                constr_pin_dir == "rise" and
                rel_pin == "A1" and
                rel_pin_dir == "fall" and
                "A2&A3&!B1&!B2&!B3" in when):
   
        template_name = "hack_template_v2/template__AOI33D_inpin_fall_delay_rise.sp"
        return template_name
   
    ## AOI33 delay_fall ZN,A1,A2&A3&!B1&!B2&!B3
    if( arc_type in delay_arc_types and
                fnmatch.fnmatch(cell_name, "AOI33M1LIMZD0P7BWP130HPNPN3P48CPD") and
                constr_pin == "ZN" and
                constr_pin_dir == "fall" and
                rel_pin == "A1" and
                rel_pin_dir == "rise" and
                "A2&A3&!B1&!B2&!B3" in when):
   
        template_name = "hack_template_v2/template__AOI33D_inpin_rise_delay_fall.sp"
        return template_name
 
###     AOI33M1LIMZD4BWP130HPNPN3P48CPD
    if( arc_type in delay_arc_types and
                fnmatch.fnmatch(cell_name, "AOI33M1LIMZD4BWP130HPNPN3P48CPD") and
                constr_pin == "ZN" and
                constr_pin_dir == "rise" and
                rel_pin == "A1" and
                rel_pin_dir == "fall" and
                "A2&A3&!B1&!B2&!B3" in when):
   
        template_name = "hack_template_v2/template__AOI33D_inpin_fall_delay_rise.sp"
        return template_name
   
    ## AOI33 delay_fall ZN,A1,A2&A3&!B1&!B2&!B3
    if( arc_type in delay_arc_types and
                fnmatch.fnmatch(cell_name, "AOI33M1LIMZD4BWP130HPNPN3P48CPD") and
                constr_pin == "ZN" and
                constr_pin_dir == "fall" and
                rel_pin == "A1" and
                rel_pin_dir == "rise" and
                "A2&A3&!B1&!B2&!B3" in when):
   
        template_name = "hack_template_v2/template__AOI33D_inpin_rise_delay_fall.sp"
        return template_name
 
###     AOI222MDLIMZD0P7BWP130HPNPN3P48CPD
    # AOI222 cell_rise arc
    if (arc_type in delay_arc_types and
            fnmatch.fnmatch(cell_name, "AOI222MDLIMZD0P7BWP130HPNPN3P48CPD") and
            constr_pin == "ZN" and
            constr_pin_dir == "rise" and
            rel_pin == "B1" and
            rel_pin_dir == "fall" and
            "A1&!A2&B2&!C1&C2" in when):
   
        template_name = "hack_template_v2/template__AOI222OPTPBD_inpin_fall_delay_rise.sp"
        return template_name
   
    # AOI222 cell_fall arc
    if (arc_type in delay_arc_types and
            fnmatch.fnmatch(cell_name, "AOI222MDLIMZD0P7BWP130HPNPN3P48CPD") and
            constr_pin == "ZN" and
            constr_pin_dir == "fall" and
            rel_pin == "B1" and
            rel_pin_dir == "rise" and
            "A1&!A2&B2&!C1&C2" in when):
   
        template_name = "hack_template_v2/template__AOI222OPTPBD_inpin_rise_delay_fall.sp"
        return template_name
 
###     AOI222M1LIMZD4BWP130HPNPN3P48CPD
    # AOI222 cell_rise arc
    if (arc_type in delay_arc_types and
            fnmatch.fnmatch(cell_name, "AOI222M1LIMZD4BWP130HPNPN3P48CPD") and
            constr_pin == "ZN" and
            constr_pin_dir == "rise" and
            rel_pin == "B1" and
            rel_pin_dir == "fall" and
            "A1&!A2&B2&!C1&C2" in when):
   
        template_name = "hack_template_v2/template__AOI222OPTPBD_inpin_fall_delay_rise.sp"
        return template_name
   
    # AOI222 cell_fall arc
    if (arc_type in delay_arc_types and
            fnmatch.fnmatch(cell_name, "AOI222M1LIMZD4BWP130HPNPN3P48CPD") and
            constr_pin == "ZN" and
            constr_pin_dir == "fall" and
            rel_pin == "B1" and
            rel_pin_dir == "rise" and
            "A1&!A2&B2&!C1&C2" in when):
   
        template_name = "hack_template_v2/template__AOI222OPTPBD_inpin_rise_delay_fall.sp"
        return template_name
 
###     XOR4MDLIMZD0P8BWP130HPNPN3P48CPD
    if( arc_type in delay_arc_types and
            fnmatch.fnmatch(cell_name, "XOR4MDLIMZD0P8BWP130HPNPN3P48CPD") and
            constr_pin == "Z" and
            constr_pin_dir == "rise" and
            rel_pin == "A2" and
            rel_pin_dir == "rise" and
            "!A1&!A3&!A4" in when):
 
        template_name = "hack_template_v2/template__common_inpin_rise_delay_rise.sp"
        return template_name
 
    if( arc_type in delay_arc_types and
            fnmatch.fnmatch(cell_name, "XOR4MDLIMZD0P8BWP130HPNPN3P48CPD") and
            constr_pin == "Z" and
            constr_pin_dir == "fall" and
            rel_pin == "A2" and
            rel_pin_dir == "fall" and
            "!A1&!A3&!A4" in when):
 
        template_name = "hack_template_v2/template__common_inpin_fall_delay_fall.sp"
        return template_name
 
###     XOR4MDLIMZD4BWP130HPNPN3P48CPD
    if( arc_type in delay_arc_types and
            fnmatch.fnmatch(cell_name, "XOR4MDLIMZD4BWP130HPNPN3P48CPD") and
            constr_pin == "Z" and
            constr_pin_dir == "rise" and
            rel_pin == "A2" and
            rel_pin_dir == "rise" and
            "!A1&!A3&!A4" in when):
 
        template_name = "hack_template_v2/template__common_inpin_rise_delay_rise.sp"
        return template_name
 
    if( arc_type in delay_arc_types and
            fnmatch.fnmatch(cell_name, "XOR4MDLIMZD4BWP130HPNPN3P48CPD") and
            constr_pin == "Z" and
            constr_pin_dir == "fall" and
            rel_pin == "A2" and
            rel_pin_dir == "fall" and
            "!A1&!A3&!A4" in when):
 
        template_name = "hack_template_v2/template__common_inpin_fall_delay_fall.sp"
        return template_name
 
###     MUX2MDLIMZD0P7BWP130HPNPN3P48CPD
    ## MUX2 delay_rise Z,I0,!I1&!S
    if( arc_type in delay_arc_types and
                fnmatch.fnmatch(cell_name, "MUX2MDLIMZD0P7BWP130HPNPN3P48CPD") and
                constr_pin == "Z" and
                constr_pin_dir == "rise" and
                rel_pin == "I0" and
                rel_pin_dir == "rise" and
                "!I1&!S" in when):
 
        template_name = "hack_template_v2/template__common_inpin_rise_delay_rise.sp"
        return template_name
 
    ## MUX2 delay_fall Z,I0,!I1&!S
    if( arc_type in delay_arc_types and
            fnmatch.fnmatch(cell_name, "MUX2MDLIMZD0P7BWP130HPNPN3P48CPD") and
            constr_pin == "Z" and
            constr_pin_dir == "fall" and
            rel_pin == "I0" and
            rel_pin_dir == "fall" and
            "!I1&!S" in when):
 
        template_name = "hack_template_v2/template__common_inpin_fall_delay_fall.sp"
        return template_name
 
###     MUX2MDLIMZD4BWP130HPNPN3P48CPD
    ## MUX2 delay_rise Z,I0,!I1&!S
    if( arc_type in delay_arc_types and
                fnmatch.fnmatch(cell_name, "MUX2MDLIMZD4BWP130HPNPN3P48CPD") and
                constr_pin == "Z" and
                constr_pin_dir == "rise" and
                rel_pin == "I0" and
                rel_pin_dir == "rise" and
                "!I1&!S" in when):
 
        template_name = "hack_template_v2/template__common_inpin_rise_delay_rise.sp"
        return template_name
 
    ## MUX2 delay_fall Z,I0,!I1&!S
    if( arc_type in delay_arc_types and
            fnmatch.fnmatch(cell_name, "MUX2MDLIMZD4BWP130HPNPN3P48CPD") and
            constr_pin == "Z" and
            constr_pin_dir == "fall" and
            rel_pin == "I0" and
            rel_pin_dir == "fall" and
            "!I1&!S" in when):
 
        template_name = "hack_template_v2/template__common_inpin_fall_delay_fall.sp"
        return template_name
 
 
###     IIND4MDLIMZD0P7BWP130HPNPN3P48CPD
    if( arc_type in delay_arc_types and
            fnmatch.fnmatch(cell_name, "IIND4MDLIMZD0P7BWP130HPNPN3P48CPD") and
            constr_pin == "ZN" and
            constr_pin_dir == "fall" and
            rel_pin == "A1" and
            rel_pin_dir == "fall"):
 
        template_name = "hack_template_v2/template__IIND4D_inpin_fall_delay_fall.sp"
        return template_name
 
    if( arc_type in delay_arc_types and
            fnmatch.fnmatch(cell_name, "IIND4MDLIMZD0P7BWP130HPNPN3P48CPD") and
            constr_pin == "ZN" and
            constr_pin_dir == "rise" and
            rel_pin == "A1" and
            rel_pin_dir == "rise"):
 
        template_name = "hack_template_v2/template__IIND4D_inpin_rise_delay_rise.sp"
        return template_name
 
###     IIND4MDLIMZD4BWP130HPNPN3P48CPD
 
    if( arc_type in delay_arc_types and
            fnmatch.fnmatch(cell_name, "IIND4MDLIMZD4BWP130HPNPN3P48CPD") and
            constr_pin == "ZN" and
            constr_pin_dir == "fall" and
            rel_pin == "A1" and
            rel_pin_dir == "fall"):
 
        template_name = "hack_template_v2/template__IIND4D_inpin_fall_delay_fall.sp"
        return template_name
 
    if( arc_type in delay_arc_types and
            fnmatch.fnmatch(cell_name, "IIND4MDLIMZD4BWP130HPNPN3P48CPD") and
            constr_pin == "ZN" and
            constr_pin_dir == "rise" and
            rel_pin == "A1" and
            rel_pin_dir == "rise"):
 
        template_name = "hack_template_v2/template__IIND4D_inpin_rise_delay_rise.sp"
        return template_name
 
###     FA1MDLIMZD0P7BWP130HPNPN3P48CPD
    if( arc_type in delay_arc_types and
            fnmatch.fnmatch(cell_name, "FA1MDLIMZD0P7BWP130HPNPN3P48CPD") and
            constr_pin == "S" and
            constr_pin_dir == "rise" and
            rel_pin == "CI" and
            rel_pin_dir == "rise" and
            "A&B" in when):
 
        template_name = "hack_template_v2/template__FA1OPTSD_inpin_rise_delay_rise.sp"
        return template_name
 
    if (arc_type in delay_arc_types and
            fnmatch.fnmatch(cell_name, "FA1MDLIMZD0P7BWP130HPNPN3P48CPD") and
            constr_pin == "S" and
            constr_pin_dir == "fall" and 
            rel_pin == "CI" and
            rel_pin_dir == "fall" and 
            "A&B" in when):
   
        template_name = "hack_template_v2/template__common_inpin_fall_delay_fall.sp" 
        return template_name
 
###     FA1MDLIMZD4BWP130HPNPN3P48CPD
    if( arc_type in delay_arc_types and
            fnmatch.fnmatch(cell_name, "FA1MDLIMZD4BWP130HPNPN3P48CPD") and
            constr_pin == "S" and
            constr_pin_dir == "rise" and
            rel_pin == "CI" and
            rel_pin_dir == "rise" and
            "A&B" in when):
 
        template_name = "hack_template_v2/template__FA1OPTSD_inpin_rise_delay_rise.sp"
        return template_name
 
    if (arc_type in delay_arc_types and
            fnmatch.fnmatch(cell_name, "FA1MDLIMZD4BWP130HPNPN3P48CPD") and
            constr_pin == "S" and
            constr_pin_dir == "fall" and 
            rel_pin == "CI" and
            rel_pin_dir == "fall" and 
            "A&B" in when):
   
        template_name = "hack_template_v2/template__common_inpin_fall_delay_fall.sp" 
        return template_name
 
###     BUFFMDLIMZD0P7BWP130HPNPN3P48CPD
    ## BUFF delay_rise Z,I
    if( arc_type in delay_arc_types and
                fnmatch.fnmatch(cell_name, "BUFFMDLIMZD0P7BWP130HPNPN3P48CPD") and
                constr_pin == "Z" and
                constr_pin_dir == "rise" and
                rel_pin == "I" and
                rel_pin_dir == "rise"):
 
        template_name = "hack_template_v2/template__common_inpin_rise_delay_rise.sp"
        return template_name
 
    ## BUFF delay_fall Z,I
    if( arc_type in delay_arc_types and
                fnmatch.fnmatch(cell_name, "BUFFMDLIMZD0P7BWP130HPNPN3P48CPD") and
                constr_pin == "Z" and
                constr_pin_dir == "fall" and
                rel_pin == "I" and
                rel_pin_dir == "fall"):
 
        template_name = "hack_template_v2/template__common_inpin_fall_delay_fall.sp"
        return template_name
 
###     BUFFMDLIMZD4BWP130HPNPN3P48CPD
    ## BUFF delay_rise Z,I
    if( arc_type in delay_arc_types and
                fnmatch.fnmatch(cell_name, "BUFFMDLIMZD4BWP130HPNPN3P48CPD") and
                constr_pin == "Z" and
                constr_pin_dir == "rise" and
                rel_pin == "I" and
                rel_pin_dir == "rise"):
 
        template_name = "hack_template_v2/template__common_inpin_rise_delay_rise.sp"
        return template_name
 
    ## BUFF delay_fall Z,I
    if( arc_type in delay_arc_types and
                fnmatch.fnmatch(cell_name, "BUFFMDLIMZD4BWP130HPNPN3P48CPD") and
                constr_pin == "Z" and
                constr_pin_dir == "fall" and
                rel_pin == "I" and
                rel_pin_dir == "fall"):
 
        template_name = "hack_template_v2/template__common_inpin_fall_delay_fall.sp"
        return template_name
 
###     NR2MDLIMZD0P7BWP130HPNPN3P48CPD
    if( arc_type in delay_arc_types and
                fnmatch.fnmatch(cell_name, "NR2MDLIMZD0P7BWP130HPNPN3P48CPD") and
                constr_pin == "ZN" and
                constr_pin_dir == "rise" and
                rel_pin == "A1" and
                rel_pin_dir == "fall"):
 
        template_name = "hack_template_v2/template__NR2_inpin_fall_delay_rise.sp"
        return template_name
   
    ## NR2 delay_fall ZN,A1
    if( arc_type in delay_arc_types and
            fnmatch.fnmatch(cell_name, "NR2MDLIMZD0P7BWP130HPNPN3P48CPD") and
            constr_pin == "ZN" and
            constr_pin_dir == "fall" and
            rel_pin == "A1" and
            rel_pin_dir == "rise"):
 
        template_name = "hack_template_v2/template__NR2_inpin_rise_delay_fall.sp"
        return template_name
 
###     NR2MDLIMZD4BWP130HPNPN3P48CPD
    if( arc_type in delay_arc_types and
                fnmatch.fnmatch(cell_name, "NR2MDLIMZD4BWP130HPNPN3P48CPD") and
                constr_pin == "ZN" and
                constr_pin_dir == "rise" and
                rel_pin == "A1" and
                rel_pin_dir == "fall"):
 
        template_name = "hack_template_v2/template__NR2_inpin_fall_delay_rise.sp"
        return template_name
   
    ## NR2 delay_fall ZN,A1
    if( arc_type in delay_arc_types and
            fnmatch.fnmatch(cell_name, "NR2MDLIMZD4BWP130HPNPN3P48CPD") and
            constr_pin == "ZN" and
            constr_pin_dir == "fall" and
            rel_pin == "A1" and
            rel_pin_dir == "rise"):
 
        template_name = "hack_template_v2/template__NR2_inpin_rise_delay_fall.sp"
        return template_name
 
###     NR4MDLIMZD0P7BWP130HPNPN3P48CPD
    if( arc_type in delay_arc_types and
                fnmatch.fnmatch(cell_name, "NR4MDLIMZD0P7BWP130HPNPN3P48CPD") and
                constr_pin == "ZN" and
                constr_pin_dir == "rise" and
                rel_pin == "A1" and
                rel_pin_dir == "fall"):
 
        template_name = "hack_template_v2/template__NR4_inpin_fall_delay_rise.sp"
        return template_name
 
    ## NR4 delay_fall ZN,A1
    if( arc_type in delay_arc_types and
            fnmatch.fnmatch(cell_name, "NR4MDLIMZD0P7BWP130HPNPN3P48CPD") and
            constr_pin == "ZN" and
            constr_pin_dir == "fall" and
            rel_pin == "A1" and
            rel_pin_dir == "rise"):
 
        template_name = "hack_template_v2/template__NR4_inpin_rise_delay_fall.sp"
        return template_name
 
###     NR4MDLIMZD4BWP130HPNPN3P48CPD
    if( arc_type in delay_arc_types and
                fnmatch.fnmatch(cell_name, "NR4MDLIMZD4BWP130HPNPN3P48CPD") and
                constr_pin == "ZN" and
                constr_pin_dir == "rise" and
                rel_pin == "A1" and
                rel_pin_dir == "fall"):
 
        template_name = "hack_template_v2/template__NR4_inpin_fall_delay_rise.sp"
        return template_name
 
    ## NR4 delay_fall ZN,A1
    if( arc_type in delay_arc_types and
            fnmatch.fnmatch(cell_name, "NR4MDLIMZD4BWP130HPNPN3P48CPD") and
            constr_pin == "ZN" and
            constr_pin_dir == "fall" and
            rel_pin == "A1" and
            rel_pin_dir == "rise"):
 
        template_name = "hack_template_v2/template__NR4_inpin_rise_delay_fall.sp"
        return template_name
 
###     CKLNQOPPLCHMZD1BWP130HPNPN3P48CPD
    if( arc_type in delay_arc_types and
            fnmatch.fnmatch(cell_name, "CKLNQOPPLCHMZD1BWP130HPNPN3P48CPD") and
            constr_pin == "Q" and
            constr_pin_dir == "fall" and
            rel_pin == "CP" and
            rel_pin_dir == "fall" and
            "!E&!TE" in when):
 
        template_name = "hack_template_v2/template__CKLNQD_inpin_fall_delay_fall.sp"
        return template_name
 
    if( arc_type in delay_arc_types and
            fnmatch.fnmatch(cell_name, "CKLNQOPPLCHMZD1BWP130HPNPN3P48CPD") and
            constr_pin == "Q" and
            constr_pin_dir == "rise" and
            rel_pin == "CP" and
            rel_pin_dir == "rise" and
            "!E&TE" in when):
   
        template_name = "hack_template_v2/template__CKLNQD_inpin_rise_delay_rise.sp"
        return template_name
 
    ## CKLNQ* hold
#    if( arc_type == "hold" and
#           fnmatch.fnmatch(cell_name, "CKLNQOPPLCHMZD1BWP130HPNPN3P48CPD") and
#                constr_pin == "E" and
#                constr_pin_dir == "rise" and
#                rel_pin == "CP" and
#                rel_pin_dir == "rise" ):
#
#        template_name = "hold/template__latch__rise__rise__glitch__maxq__1.sp"
#        return template_name
#
#
#    if( arc_type == "hold" and
#           fnmatch.fnmatch(cell_name, "CKLNQOPPLCHMZD1BWP130HPNPN3P48CPD") and
#                constr_pin == "E" and
#                constr_pin_dir == "fall" and
#                rel_pin == "CP" and
#                rel_pin_dir == "rise" ):
#
#        template_name = "hold/template__latch__rise__fall__pushout__1.sp"
 
###     CKLNQOPPLCHMZD4BWP130HPNPN3P48CPD
    if( arc_type in delay_arc_types and
            fnmatch.fnmatch(cell_name, "CKLNQOPPLCHMZD4BWP130HPNPN3P48CPD") and
            constr_pin == "Q" and
            constr_pin_dir == "fall" and
            rel_pin == "CP" and
            rel_pin_dir == "fall" and
            "!E&!TE" in when):
 
        template_name = "hack_template_v2/template__CKLNQD_inpin_fall_delay_fall.sp"
        return template_name
 
    if( arc_type in delay_arc_types and
            fnmatch.fnmatch(cell_name, "CKLNQOPPLCHMZD4BWP130HPNPN3P48CPD") and
            constr_pin == "Q" and
            constr_pin_dir == "rise" and
            rel_pin == "CP" and
            rel_pin_dir == "rise" and
            "!E&TE" in when):
   
        template_name = "hack_template_v2/template__CKLNQD_inpin_rise_delay_rise.sp"
        return template_name
 
    ## CKLNQ* hold
#    if( arc_type == "hold" and
#           fnmatch.fnmatch(cell_name, "CKLNQOPPLCHMZD4BWP130HPNPN3P48CPD") and
#                constr_pin == "E" and
#                constr_pin_dir == "rise" and
#                rel_pin == "CP" and
#                rel_pin_dir == "rise" ):
#
#        template_name = "hold/template__latch__rise__rise__glitch__maxq__1.sp"
#        return template_name
#
#
#    if( arc_type == "hold" and
#           fnmatch.fnmatch(cell_name, "CKLNQOPPLCHMZD4BWP130HPNPN3P48CPD") and
#                constr_pin == "E" and
#                constr_pin_dir == "fall" and
#                rel_pin == "CP" and
#                rel_pin_dir == "rise" ):
#
#        template_name = "hold/template__latch__rise__fall__pushout__1.sp"
#
 
###     OAI33M1LIMZD0P7BWP130HPNPN3P48CPD
    if( arc_type in delay_arc_types and
            fnmatch.fnmatch(cell_name, "OAI33M1LIMZD0P7BWP130HPNPN3P48CPD") and
            constr_pin == "ZN" and
            constr_pin_dir == "rise" and
            rel_pin == "B1" and
            rel_pin_dir == "fall" and
            "!A1&!A2&A3&!B2&!B3" in when):
 
        template_name = "hack_template_v2/template__OAI33D_inpin_fall_delay_rise.sp"
        return template_name
 
    if( arc_type in delay_arc_types and
            fnmatch.fnmatch(cell_name, "OAI33M1LIMZD0P7BWP130HPNPN3P48CPD") and
            constr_pin == "ZN" and
            constr_pin_dir == "fall" and
            rel_pin == "B1" and
            rel_pin_dir == "rise" and
            "!A1&!A2&A3&!B2&!B3" in when):
 
        template_name = "hack_template_v2/template__common_inpin_rise_delay_fall.sp"
        return template_name
 
###     OAI33M1LIMZD4BWP130HPNPN3P48CPD
    if( arc_type in delay_arc_types and
            fnmatch.fnmatch(cell_name, "OAI33M1LIMZD4BWP130HPNPN3P48CPD") and
            constr_pin == "ZN" and
            constr_pin_dir == "rise" and
            rel_pin == "B1" and
            rel_pin_dir == "fall" and
            "!A1&!A2&A3&!B2&!B3" in when):
 
        template_name = "hack_template_v2/template__OAI33D_inpin_fall_delay_rise.sp"
        return template_name
 
    if( arc_type in delay_arc_types and
            fnmatch.fnmatch(cell_name, "OAI33M1LIMZD4BWP130HPNPN3P48CPD") and
            constr_pin == "ZN" and
            constr_pin_dir == "fall" and
            rel_pin == "B1" and
            rel_pin_dir == "rise" and
            "!A1&!A2&A3&!B2&!B3" in when):
 
        template_name = "hack_template_v2/template__common_inpin_rise_delay_fall.sp"
        return template_name
 
###     OAI222MDLIMZD0P7BWP130HPNPN3P48CPD
    if( arc_type in delay_arc_types and
            fnmatch.fnmatch(cell_name, "OAI222MDLIMZD0P7BWP130HPNPN3P48CPD") and
            constr_pin == "ZN" and
            constr_pin_dir == "fall" and
            rel_pin == "A2" and
            rel_pin_dir == "rise" and
            "!A1&!B1&B2&C1&!C2" in when):
 
        template_name = "hack_template_v2/template__OAI222OPTPBD_inpin_rise_delay_fall.sp"
        return template_name
 
    if( arc_type in delay_arc_types and
            fnmatch.fnmatch(cell_name, "OAI222MDLIMZD0P7BWP130HPNPN3P48CPD") and
            constr_pin == "ZN" and
            constr_pin_dir == "rise" and
            rel_pin == "A2" and
            rel_pin_dir == "fall" and
            "!A1&!B1&B2&C1&!C2" in when):
 
        template_name = "hack_template_v2/template__common_inpin_fall_delay_rise.sp"
        return template_name
 
###     OAI222M1LIMZD4BWP130HPNPN3P48CPD
    if( arc_type in delay_arc_types and
            fnmatch.fnmatch(cell_name, "OAI222M1LIMZD4BWP130HPNPN3P48CPD") and
            constr_pin == "ZN" and
            constr_pin_dir == "fall" and
            rel_pin == "A2" and
            rel_pin_dir == "rise" and
            "!A1&!B1&B2&C1&!C2" in when):
 
        template_name = "hack_template_v2/template__OAI222OPTPBD_inpin_rise_delay_fall.sp"
        return template_name
 
    if( arc_type in delay_arc_types and
            fnmatch.fnmatch(cell_name, "OAI222M1LIMZD4BWP130HPNPN3P48CPD") and
            constr_pin == "ZN" and
            constr_pin_dir == "rise" and
            rel_pin == "A2" and
            rel_pin_dir == "fall" and
            "!A1&!B1&B2&C1&!C2" in when):
 
        template_name = "hack_template_v2/template__common_inpin_fall_delay_rise.sp"
        return template_name
 
###     XNR4MDLIMZD0P7BWP130HPNPN3P48CPD
    if( arc_type in delay_arc_types and
            fnmatch.fnmatch(cell_name, "XNR4MDLIMZD0P7BWP130HPNPN3P48CPD") and
            constr_pin == "ZN" and
            constr_pin_dir == "rise" and
            rel_pin == "A2" and
            rel_pin_dir == "fall" and
            "!A1&!A3&!A4" in when):
 
        template_name = "hack_template_v2/template__XNR4D__rise.sp"
        return template_name
 
    if( arc_type in delay_arc_types and
            fnmatch.fnmatch(cell_name, "XNR4MDLIMZD0P7BWP130HPNPN3P48CPD") and
            constr_pin == "ZN" and
            constr_pin_dir == "fall" and
            rel_pin == "A2" and
            rel_pin_dir == "rise" and
            "!A1&!A3&!A4" in when):
 
        template_name = "hack_template_v2/template__common_inpin_rise_delay_fall.sp"
        return template_name
 
###     XNR4MDLIMZD4BWP130HPNPN3P48CPD
    if( arc_type in delay_arc_types and
            fnmatch.fnmatch(cell_name, "XNR4MDLIMZD4BWP130HPNPN3P48CPD") and
            constr_pin == "ZN" and
            constr_pin_dir == "rise" and
            rel_pin == "A2" and
            rel_pin_dir == "fall" and
            "!A1&!A3&!A4" in when):
 
        template_name = "hack_template_v2/template__XNR4D__rise.sp"
        return template_name
 
    if( arc_type in delay_arc_types and
            fnmatch.fnmatch(cell_name, "XNR4MDLIMZD4BWP130HPNPN3P48CPD") and
            constr_pin == "ZN" and
            constr_pin_dir == "fall" and
            rel_pin == "A2" and
            rel_pin_dir == "rise" and
            "!A1&!A3&!A4" in when):
 
        template_name = "hack_template_v2/template__common_inpin_rise_delay_fall.sp"
        return template_name
 
###     MUX4MDLIMZD0P7BWP130HPNPN3P48CPD
    if( arc_type in delay_arc_types and
            fnmatch.fnmatch(cell_name, "MUX4MDLIMZD0P7BWP130HPNPN3P48CPD") and
            constr_pin == "Z" and
            constr_pin_dir == "rise" and
            rel_pin == "S1" and
            rel_pin_dir == "rise" and
            "!I0&!I1&!I2&I3&S0" in when):
 
        template_name = "hack_template_v2/template__MUX4OPTD_inpin_rise_delay_rise.sp"
        return template_name
 
    if( arc_type in delay_arc_types and
            fnmatch.fnmatch(cell_name, "MUX4MDLIMZD0P7BWP130HPNPN3P48CPD") and
            constr_pin == "Z" and
            constr_pin_dir == "fall" and
            rel_pin == "S1" and
            rel_pin_dir == "fall" and
            "!I0&!I1&!I2&I3&S0" in when):
 
        template_name = "hack_template_v2/template__common_inpin_fall_delay_fall.sp"
        return template_name
 
###     MUX4MDLIMZD4BWP130HPNPN3P48CPD
    if( arc_type in delay_arc_types and
            fnmatch.fnmatch(cell_name, "MUX4MDLIMZD4BWP130HPNPN3P48CPD") and
            constr_pin == "Z" and
            constr_pin_dir == "rise" and
            rel_pin == "S1" and
            rel_pin_dir == "rise" and
            "!I0&!I1&!I2&I3&S0" in when):
 
        template_name = "hack_template_v2/template__MUX4OPTD_inpin_rise_delay_rise.sp"
        return template_name
 
    if( arc_type in delay_arc_types and
            fnmatch.fnmatch(cell_name, "MUX4MDLIMZD4BWP130HPNPN3P48CPD") and
            constr_pin == "Z" and
            constr_pin_dir == "fall" and
            rel_pin == "S1" and
            rel_pin_dir == "fall" and
            "!I0&!I1&!I2&I3&S0" in when):
 
        template_name = "hack_template_v2/template__common_inpin_fall_delay_fall.sp"
        return template_name
 
###     IINR4MDLIMZD0P7BWP130HPNPN3P48CPD
 
    if( arc_type in delay_arc_types and
            fnmatch.fnmatch(cell_name, "IINR4MDLIMZD0P7BWP130HPNPN3P48CPD") and
            constr_pin == "ZN" and
            constr_pin_dir == "fall" and
            rel_pin == "A1" and
            rel_pin_dir == "fall"):
 
        template_name = "hack_template_v2/template__IINR4D_inpin_fall_delay_fall.sp"
        return template_name
 
    if( arc_type in delay_arc_types and
            fnmatch.fnmatch(cell_name, "IINR4MDLIMZD0P7BWP130HPNPN3P48CPD") and
            constr_pin == "ZN" and
            constr_pin_dir == "rise" and
            rel_pin == "A1" and
            rel_pin_dir == "rise"):
 
        template_name = "hack_template_v2/template__IINR4D_inpin_rise_delay_rise.sp"
        return template_name
 
 
###     IINR4MDLIMZD4BWP130HPNPN3P48CPD
 
    if( arc_type in delay_arc_types and
            fnmatch.fnmatch(cell_name, "IINR4MDLIMZD4BWP130HPNPN3P48CPD") and
            constr_pin == "ZN" and
            constr_pin_dir == "fall" and
            rel_pin == "A1" and
            rel_pin_dir == "fall"):
 
        template_name = "hack_template_v2/template__IINR4D_inpin_fall_delay_fall.sp"
        return template_name
 
    if( arc_type in delay_arc_types and
            fnmatch.fnmatch(cell_name, "IINR4MDLIMZD4BWP130HPNPN3P48CPD") and
            constr_pin == "ZN" and
            constr_pin_dir == "rise" and
            rel_pin == "A1" and
            rel_pin_dir == "rise"):
 
        template_name = "hack_template_v2/template__IINR4D_inpin_rise_delay_rise.sp"
        return template_name
 
###     FCICOMDLIMZD0P7BWP130HPNPN3P48CPD
    if( arc_type in delay_arc_types and
            fnmatch.fnmatch(cell_name, "FCICOMDLIMZD0P7BWP130HPNPN3P48CPD") and
            constr_pin == "CO" and
            constr_pin_dir == "rise" and
            rel_pin == "B" and
            rel_pin_dir == "rise" and
            "A&!CI" in when):
 
        template_name = "hack_template_v2/template__FCICOD_inpin_rise_delay_rise.sp"
        return template_name
 
    if( arc_type in delay_arc_types and
            fnmatch.fnmatch(cell_name, "FCICOMDLIMZD0P7BWP130HPNPN3P48CPD") and
            constr_pin == "CO" and
            constr_pin_dir == "fall" and
            rel_pin == "B" and
            rel_pin_dir == "fall" and
            "A&!CI" in when):
 
        template_name = "hack_template_v2/template__common_inpin_fall_delay_fall.sp"
        return template_name
 
###     FCICOMDLIMZD4BWP130HPNPN3P48CPD
    if( arc_type in delay_arc_types and
            fnmatch.fnmatch(cell_name, "FCICOMDLIMZD4BWP130HPNPN3P48CPD") and
            constr_pin == "CO" and
            constr_pin_dir == "rise" and
            rel_pin == "B" and
            rel_pin_dir == "rise" and
            "A&!CI" in when):
 
        template_name = "hack_template_v2/template__FCICOD_inpin_rise_delay_rise.sp"
        return template_name
 
    if( arc_type in delay_arc_types and
            fnmatch.fnmatch(cell_name, "FCICOMDLIMZD4BWP130HPNPN3P48CPD") and
            constr_pin == "CO" and
            constr_pin_dir == "fall" and
            rel_pin == "B" and
            rel_pin_dir == "fall" and
            "A&!CI" in when):
 
        template_name = "hack_template_v2/template__common_inpin_fall_delay_fall.sp"
        return template_name
 
###     DELEULPMZD1BWP130HPNPN3P48CPD
    if( arc_type in delay_arc_types and
            fnmatch.fnmatch(cell_name, "DELEULPMZD1BWP130HPNPN3P48CPD") and
            constr_pin == "Z" and
            constr_pin_dir == "rise" and
            rel_pin == "I" and
            rel_pin_dir == "rise"):
 
        template_name = "hack_template_v2/template__DELED_inpin_rise_delay_rise.sp"
        return template_name
 
    if( arc_type in delay_arc_types and
            fnmatch.fnmatch(cell_name, "DELEULPMZD1BWP130HPNPN3P48CPD") and
            constr_pin == "Z" and
            constr_pin_dir == "fall" and
            rel_pin == "I" and
            rel_pin_dir == "fall"):
 
        template_name = "hack_template_v2/template__common_inpin_fall_delay_fall.sp"
        return template_name
 
###     SDFQSXG0MZD1BWP130HPNPN3P48CPD
    if( arc_type in delay_arc_types and
                fnmatch.fnmatch(cell_name, "SDFQSXG0MZD1BWP130HPNPN3P48CPD") and
                constr_pin == "Q" and
                constr_pin_dir == "fall" and
                rel_pin == "CP" and
                rel_pin_dir == "rise"and
                "!SE" in when):
 
        template_name = "hack_template_v2/template__seq_inpin_rise_delay_fall.sp"
        return template_name
 
    if( arc_type in delay_arc_types and
                fnmatch.fnmatch(cell_name, "SDFQSXG0MZD1BWP130HPNPN3P48CPD") and
                constr_pin == "Q" and
                constr_pin_dir == "rise" and
                rel_pin == "CP" and
                rel_pin_dir == "rise"and
                "!SE" in when):
 
        template_name = "hack_template_v2/template__seq_inpin_rise_delay_rise.sp"
        return template_name
 
 
###     SDFQSXG0MZD4BWP130HPNPN3P48CPD
    if( arc_type in delay_arc_types and
                fnmatch.fnmatch(cell_name, "SDFQSXG0MZD4BWP130HPNPN3P48CPD") and
                constr_pin == "Q" and
                constr_pin_dir == "fall" and
                rel_pin == "CP" and
                rel_pin_dir == "rise"and
                "!SE" in when):
 
        template_name = "hack_template_v2/template__seq_inpin_rise_delay_fall.sp"
        return template_name
 
    if( arc_type in delay_arc_types and
                fnmatch.fnmatch(cell_name, "SDFQSXG0MZD4BWP130HPNPN3P48CPD") and
                constr_pin == "Q" and
                constr_pin_dir == "rise" and
                rel_pin == "CP" and
                rel_pin_dir == "rise"and
                "!SE" in when):
 
        template_name = "hack_template_v2/template__seq_inpin_rise_delay_rise.sp"
        return template_name
 
###     SDFNQSXG0MZD1BWP130HPNPN3P48CPD
    if( arc_type in delay_arc_types and
                fnmatch.fnmatch(cell_name, "SDFNQSXG0MZD1BWP130HPNPN3P48CPD") and
                constr_pin == "Q" and
                constr_pin_dir == "fall" and
                rel_pin == "CPN" and
                rel_pin_dir == "fall"and
                "!SE" in when):
 
        template_name = "hack_template_v2/template__seq_inpin_fall_delay_fall.sp"
        return template_name
 
    if( arc_type in delay_arc_types and
                fnmatch.fnmatch(cell_name, "SDFNQSXG0MZD1BWP130HPNPN3P48CPD") and
                constr_pin == "Q" and
                constr_pin_dir == "rise" and
                rel_pin == "CPN" and
                rel_pin_dir == "fall"and
                "!SE" in when):
 
        template_name = "hack_template_v2/template__seq_inpin_fall_delay_rise.sp"
        return template_name
 
###     SDFNQSXG0FLODMZD4BWP130HPNPN3P48CPD
    if( arc_type in delay_arc_types and
                fnmatch.fnmatch(cell_name, "SDFNQSXG0FLODMZD4BWP130HPNPN3P48CPD") and
                constr_pin == "Q" and
                constr_pin_dir == "fall" and
                rel_pin == "CPN" and
                rel_pin_dir == "fall"and
                "!SE" in when):
 
        template_name = "hack_template_v2/template__seq_inpin_fall_delay_fall.sp"
        return template_name
 
    if( arc_type in delay_arc_types and
                fnmatch.fnmatch(cell_name, "SDFNQSXG0FLODMZD4BWP130HPNPN3P48CPD") and
                constr_pin == "Q" and
                constr_pin_dir == "rise" and
                rel_pin == "CPN" and
                rel_pin_dir == "fall"and
                "!SE" in when):
 
        template_name = "hack_template_v2/template__seq_inpin_fall_delay_rise.sp"
        return template_name
 
 
 
###     SDFQNSXG0MZD1BWP130HPNPN3P48CPD
    if( arc_type in delay_arc_types and
                fnmatch.fnmatch(cell_name, "SDFQNSXG0MZD1BWP130HPNPN3P48CPD") and
                constr_pin == "QN" and
                constr_pin_dir == "rise" and
                rel_pin == "CP" and
                rel_pin_dir == "rise"and
                "!SE" in when):
 
        template_name = "hack_template_v2/template__seq_inpin_rise_delay_rise.sp"
        return template_name
 
    if( arc_type in delay_arc_types and
                fnmatch.fnmatch(cell_name, "SDFQNSXG0MZD1BWP130HPNPN3P48CPD") and
                constr_pin == "QN" and
                constr_pin_dir == "fall" and
                rel_pin == "CP" and
                rel_pin_dir == "rise"and
                "!SE" in when):
 
        template_name = "hack_template_v2/template__seq_inpin_rise_delay_fall.sp"
        return template_name
 
 
 
###     SDFQNTXGLVAMZD4BWP130HPNPN3P48CPD
    if( arc_type in delay_arc_types and
                fnmatch.fnmatch(cell_name, "SDFQNTXGLVAMZD4BWP130HPNPN3P48CPD") and
                constr_pin == "QN" and
                constr_pin_dir == "rise" and
                rel_pin == "CP" and
                rel_pin_dir == "rise"and
                "!SE" in when):
 
        template_name = "hack_template_v2/template__seq_inpin_rise_delay_rise.sp"
        return template_name
 
    if( arc_type in delay_arc_types and
                fnmatch.fnmatch(cell_name, "SDFQNTXGLVAMZD4BWP130HPNPN3P48CPD") and
                constr_pin == "QN" and
                constr_pin_dir == "fall" and
                rel_pin == "CP" and
                rel_pin_dir == "rise"and
                "!SE" in when):
 
        template_name = "hack_template_v2/template__seq_inpin_rise_delay_fall.sp"
        return template_name
 
 
###     SDFSRPQSXGMZD1BWP130HPNPN3P48CPD
    if( arc_type in delay_arc_types and
            fnmatch.fnmatch(cell_name, "SDFSRPQSXGMZD1BWP130HPNPN3P48CPD") and
            constr_pin == "Q" and
            constr_pin_dir == "fall" and
            rel_pin == "CP" and
            rel_pin_dir == "rise" and
            "!CD&SDN&!SE" in when):
 
        template_name = "hack_template_v2/template__seq_inpin_rise_delay_fall.sp"
        return template_name
 
    if( arc_type in delay_arc_types and
            fnmatch.fnmatch(cell_name, "SDFSRPQSXGMZD1BWP130HPNPN3P48CPD") and
            constr_pin == "Q" and
            constr_pin_dir == "rise" and
            rel_pin == "CP" and
            rel_pin_dir == "rise" and
            "!CD&SDN&!SE" in when):
 
        template_name = "hack_template_v2/template__seq_inpin_rise_delay_rise.sp"
        return template_name
 
###     SDFSRPQSXGMZD4BWP130HPNPN3P48CPD
    if( arc_type in delay_arc_types and
            fnmatch.fnmatch(cell_name, "SDFSRPQSXGMZD4BWP130HPNPN3P48CPD") and
            constr_pin == "Q" and
            constr_pin_dir == "fall" and
            rel_pin == "CP" and
            rel_pin_dir == "rise" and
            "!CD&SDN&!SE" in when):
 
        template_name = "hack_template_v2/template__seq_inpin_rise_delay_fall.sp"
        return template_name
 
    if( arc_type in delay_arc_types and
            fnmatch.fnmatch(cell_name, "SDFSRPQSXGMZD4BWP130HPNPN3P48CPD") and
            constr_pin == "Q" and
            constr_pin_dir == "rise" and
            rel_pin == "CP" and
            rel_pin_dir == "rise" and
            "!CD&SDN&!SE" in when):
 
        template_name = "hack_template_v2/template__seq_inpin_rise_delay_rise.sp"
        return template_name
 
 
###    SDFKRPQSXG0FLODMZD1BWP130HPNPN3P48CPD
 
 
