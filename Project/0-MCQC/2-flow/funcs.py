

import fnmatch

import re

# Globals

delay_arc_types = ["combinational",

                   "combinational_fall", "combinational_rise",

                   "falling_edge", "rising_edge",

                   "three_state_disable", "three_state_enable",

                   "clear", "preset"]

 

def mapCharacteristicsToTemplate(arc_type=None,

                                 cell_name=None,

                                 pin=None,

                                 pin_dir=None,

                                 rel_pin=None,

                                 rel_pin_dir=None,

                                 when=None,

                                 probe_list=None,

                                 template_type=None):

 

    template_name = None

    if template_type.upper() == "HSPICE":

        template_name = getHspiceTemplateName(cell_name, arc_type, pin,

                                              pin_dir, rel_pin, rel_pin_dir,

                                              when, probe_list)

    elif template_type.upper() == "THANOS":

        template_name = getThanosTemplateName(cell_name, arc_type, pin,

                                              pin_dir, rel_pin, rel_pin_dir,

                                              when, probe_list)

    return template_name

 

 

 

def getHspiceTemplateName(cell_name, arc_type, constr_pin, constr_pin_dir, rel_pin,

                          rel_pin_dir, when, probe_list):

 

    # Ignore SYNC 2 removal arcs

    if( arc_type == "removal" and

                fnmatch.fnmatch(cell_name, "*SYNC2*Q*")):

 

        template_name = None

        return template_name

 

    # Ignore SYNC 3 removal arcs

    if( arc_type == "removal" and

            fnmatch.fnmatch(cell_name, "*SYNC3*Q*")):

 

        template_name = None

        return template_name

 

    # Ignore SYNC 4 removal arcs

    if( arc_type == "removal" and

            fnmatch.fnmatch(cell_name, "*SYNC4*Q*")):

 

        template_name = None

        return template_name

 

    # SYNC2 cell for constr_pin = D, rel_pin = CP, fall_constraint, Q1 internal probe

    if( arc_type == "hold" and

                fnmatch.fnmatch(cell_name, "*SYNC2*Q*") and

                constr_pin == "D" and

                constr_pin_dir == "fall" and

                rel_pin == "CP" and

                rel_pin_dir == "rise" and

                "Q1" in probe_list):

 

        template_name = "hold/template__sync2__q1__rise__fall__1.sp"

        return template_name

 

    # SYNC2 cell for constr_pin = D, rel_pin = CP, rise_constraint, Q1 internal probe

    if( arc_type == "hold" and

                fnmatch.fnmatch(cell_name, "*SYNC2*Q*") and

                constr_pin == "D" and

                constr_pin_dir == "rise" and

                rel_pin == "CP" and

                rel_pin_dir == "rise" and

                "Q1" in probe_list):

 

        template_name = "hold/template__sync2__q1__rise__rise__1.sp"

        return template_name

 

    # SYNC3 cell for constr_pin = D, rel_pin = CP, fall_constraint, Q1 internal probe

    if( arc_type == "hold" and

                fnmatch.fnmatch(cell_name, "*SYNC3*Q*") and

                constr_pin == "D" and

                constr_pin_dir == "fall" and

                rel_pin == "CP" and

                rel_pin_dir == "rise" and

                "Q1" in probe_list):

 

        template_name = "hold/template__sync3__q1__rise__fall__1.sp"

        return template_name

 

    # SYNC3 cell for constr_pin = D, rel_pin = CP, rise_constraint, Q1 internal probe

    if( arc_type == "hold" and

                fnmatch.fnmatch(cell_name, "*SYNC3*Q*") and

                constr_pin == "D" and

                constr_pin_dir == "rise" and

                rel_pin == "CP" and

                rel_pin_dir == "rise" and

                "Q1" in probe_list):

 

        template_name = "hold/template__sync3__q1__rise__rise__1.sp"

        return template_name

 

    # SYNC4 cell for constr_pin = D, rel_pin = CP, fall_constraint, Q1 internal probe

    if( arc_type == "hold" and

                fnmatch.fnmatch(cell_name, "*SYNC4*Q*") and

                constr_pin == "D" and

                constr_pin_dir == "fall" and

                rel_pin == "CP" and

                rel_pin_dir == "rise" and

                "Q1" in probe_list):

 

        template_name = "hold/template__sync4__q1__rise__fall__1.sp"

        return template_name

 

    # SYNC4 cell for constr_pin = D, rel_pin = CP, rise_constraint, Q1 internal probe

    if( arc_type == "hold" and

                fnmatch.fnmatch(cell_name, "*SYNC4*Q*") and

                constr_pin == "D" and

                constr_pin_dir == "rise" and

                rel_pin == "CP" and

                rel_pin_dir == "rise" and

                "Q1" in probe_list):

 

        template_name = "hold/template__sync4__q1__rise__rise__1.sp"

        return template_name

 

    # SYNC5 cell for constr_pin = D, rel_pin = CP, fall_constraint, Q1 internal probe

    if( arc_type == "hold" and

                fnmatch.fnmatch(cell_name, "*SYNC5*Q*") and

                constr_pin == "D" and

                constr_pin_dir == "fall" and

                rel_pin == "CP" and

                rel_pin_dir == "rise" and

                "Q1" in probe_list):

 

        template_name = "hold/template__sync5__q1__rise__fall__1.sp"

        return template_name

 

    # SYNC5 cell for constr_pin = D, rel_pin = CP, rise_constraint, Q1 internal probe

    if( arc_type == "hold" and

                fnmatch.fnmatch(cell_name, "*SYNC5*Q*") and

                constr_pin == "D" and

                constr_pin_dir == "rise" and

                rel_pin == "CP" and

                rel_pin_dir == "rise" and

                "Q1" in probe_list):

 

        template_name = "hold/template__sync5__q1__rise__rise__1.sp"

        return template_name

 

    # SYNC6 cell for constr_pin = D, rel_pin = CP, fall_constraint, Q1 internal probe

    if( arc_type == "hold" and

                fnmatch.fnmatch(cell_name, "*SYNC6*Q*") and

                constr_pin == "D" and

                constr_pin_dir == "fall" and

                rel_pin == "CP" and

                rel_pin_dir == "rise" and

                "Q1" in probe_list):

 

        template_name = "hold/template__sync6__q1__rise__fall__1.sp"

        return template_name

 

    # SYNC6 cell for constr_pin = D, rel_pin = CP, rise_constraint, Q1 internal probe

    if( arc_type == "hold" and

                fnmatch.fnmatch(cell_name, "*SYNC6*Q*") and

                constr_pin == "D" and

                constr_pin_dir == "rise" and

                rel_pin == "CP" and

                rel_pin_dir == "rise" and

                "Q1" in probe_list):

 

        template_name = "hold/template__sync6__q1__rise__rise__1.sp"

        return template_name

 

    #DCCKSDIV2RPMXLNQ *CLKEN* related deck defined --- 2021/8/13

    if( arc_type == "hold" and

                fnmatch.fnmatch(cell_name, "DCCK*DIV*LN*") and

                (fnmatch.fnmatch(constr_pin, "CLKEN*") or fnmatch.fnmatch(constr_pin, "F*CLKEN*")) and

                rel_pin == "nx" and

                rel_pin_dir == "rise" and

                len(probe_list) == 1):

        if(constr_pin_dir == "rise"):

                template_name = "hold/template__ckg__nx__rise__clken__rise__glitch__maxq__1.sp"

                return template_name

        if(constr_pin_dir == "fall"):

                template_name = "hold/template__ckg__nx__rise__clken__fall__pushout__1.sp"

                return template_name

 

    if( arc_type == "nochange_high_high" and

                fnmatch.fnmatch(cell_name, "DCCK*DIV*LN*") and

                fnmatch.fnmatch(constr_pin, "*CLKEN*") and

                constr_pin_dir == "rise" and

                rel_pin_dir == "rise"):

        if(fnmatch.fnmatch(rel_pin, "nx")):

                template_name = "nochange/template__ckg__setup__nx__rise__en__rise__pushout__minq__1.sp"

                return template_name

        if(fnmatch.fnmatch(rel_pin, "CLKIN")):

                template_name = "nochange/template__ckg__setup__rise__en__rise__pushout__minq__1.sp"

                return template_name

 

    if( arc_type == "nochange_high_high" and

                fnmatch.fnmatch(cell_name, "DCCK*DIV*LN*") and

                fnmatch.fnmatch(constr_pin, "*CLKEN*") and

                constr_pin_dir == "fall" and

                rel_pin_dir == "fall"):

        if(fnmatch.fnmatch(rel_pin, "nx")):

                template_name = "nochange/template__ckg__hold__nx__fall__en__fall__pushout__maxq__1.sp"

                return template_name

        if(fnmatch.fnmatch(rel_pin, "CLKIN")):

                template_name = "nochange/template__ckg__hold__fall__en__fall__pushout__maxq__1.sp"

                return template_name

 

    if( arc_type == "nochange_low_high" and

                fnmatch.fnmatch(cell_name, "DCCK*DIV*LN*") and

                fnmatch.fnmatch(constr_pin, "*CLKEN*") and

                constr_pin_dir == "fall" and

                rel_pin_dir == "rise"):

        if(fnmatch.fnmatch(rel_pin, "nx")):

                template_name = "nochange/template__ckg__setup__nx__rise__en__fall__20__percent__glitch__minq__1.sp"

                return template_name

        if(fnmatch.fnmatch(rel_pin, "CLKIN")):

                template_name = "nochange/template__ckg__setup__rise__en__fall__20__percent__glitch__minq__1.sp"

                return template_name

 

    if( arc_type == "nochange_low_high" and

                fnmatch.fnmatch(cell_name, "DCCK*DIV*LN*") and

                fnmatch.fnmatch(constr_pin, "*CLKEN*") and

                constr_pin_dir == "rise" and

                rel_pin_dir == "fall"):

        if(fnmatch.fnmatch(rel_pin, "nx")):

                template_name = "nochange/template__ckg__hold__nx__fall__clken__rise__glitch__minq.sp"

                return template_name

        if(fnmatch.fnmatch(rel_pin, "CLKIN")):

                template_name = "nochange/template__ckg__hold__fall__en__rise__20__percent__glitch__minq__1.sp"

                return template_name

 

    # DCCK*MX cell 2020/8/3

    if( arc_type == "hold" and

                (fnmatch.fnmatch(cell_name, "DCCKSDIV2MX*") or fnmatch.fnmatch(cell_name, "DCCKSDIV2RPMX*") or fnmatch.fnmatch(cell_name, "DCCKDIV2*") or fnmatch.fnmatch(cell_name, "DCCKSDIV2*")) and

                constr_pin == "SCANMODE" and

                constr_pin_dir == "rise" and

                rel_pin == "nx" and

                rel_pin_dir == "rise" and

                fnmatch.fnmatch(when, "FPM_CLKEN&!FSCAN_CLKEN")):

 

        template_name = "hold/template__gclk__nx__rise__scanmode__rise__glitch__minq__1.sp"

        return template_name

    

    if( arc_type == "hold" and

                (fnmatch.fnmatch(cell_name, "DCCKSDIV2MX*") or fnmatch.fnmatch(cell_name, "DCCKSDIV2RPMX*") or fnmatch.fnmatch(cell_name, "DCCKDIV2*") or fnmatch.fnmatch(cell_name, "DCCKSDIV2*")) and

                constr_pin == "SCANMODE" and

                constr_pin_dir == "fall" and

                rel_pin == "nx" and

                rel_pin_dir == "rise" and

                fnmatch.fnmatch(when, "!FPM_CLKEN&FSCAN_CLKEN")):

 

        template_name = "hold/template__gclk__nx__rise__scanmode__fall__glitch__minq__1.sp"

        return template_name

 

    if( arc_type == "hold" and

                (fnmatch.fnmatch(cell_name, "DCCKSDIV2MX*") or fnmatch.fnmatch(cell_name, "DCCKSDIV2RPMX*") or fnmatch.fnmatch(cell_name, "DCCKDIV2*") or fnmatch.fnmatch(cell_name, "DCCKSDIV2*")) and

                fnmatch.fnmatch(constr_pin, "F*_CLKEN") and

                constr_pin_dir == "rise" and

                rel_pin == "nx" and

                rel_pin_dir == "rise" and

                len(probe_list) == 2):

 

        template_name = "hold/template__gclk__nx__rise__clken__rise__glitch__maxq__ml_b.sp"

        return template_name

 

    if( arc_type == "hold" and

                (fnmatch.fnmatch(cell_name, "DCCKSDIV2MX*") or fnmatch.fnmatch(cell_name, "DCCKSDIV2RPMX*") or fnmatch.fnmatch(cell_name, "DCCKDIV2*") or fnmatch.fnmatch(cell_name, "DCCKSDIV2*")) and

                fnmatch.fnmatch(constr_pin, "F*_CLKEN") and

                constr_pin_dir == "fall" and

                rel_pin == "nx" and

                rel_pin_dir == "rise" and

                len(probe_list) == 2):

 

        template_name = "hold/template__gclk__nx__rise__clken__fall__glitch__minq__ml_b.sp"

        return template_name

 

    if( arc_type == "hold" and

                (fnmatch.fnmatch(cell_name, "DCCKSDIV2MX*") or fnmatch.fnmatch(cell_name, "DCCKSDIV2RPMX*") or fnmatch.fnmatch(cell_name, "DCCKDIV2*") or fnmatch.fnmatch(cell_name, "DCCKSDIV2*")) and

                constr_pin == "SCANMODE" and

                constr_pin_dir == "rise" and

                rel_pin == "CLKIN" and

                rel_pin_dir == "rise" and

                fnmatch.fnmatch(when, "!FPM_CLKDIVRST&FSCAN_CLKDIVRST") and

                len(probe_list) == 3):

 

        template_name = "hold/template__gclk__rise__scanmode__rise__pushout__3.sp"

        return template_name

 

    if( arc_type == "hold" and

                (fnmatch.fnmatch(cell_name, "DCCKSDIV2MX*") or fnmatch.fnmatch(cell_name, "DCCKSDIV2RPMX*") or fnmatch.fnmatch(cell_name, "DCCKDIV2*") or fnmatch.fnmatch(cell_name, "DCCKSDIV2*")) and

                constr_pin == "SCANMODE" and

                constr_pin_dir == "fall" and

                rel_pin == "CLKIN" and

                rel_pin_dir == "rise" and

                fnmatch.fnmatch(when, "FPM_CLKDIVRST&!FSCAN_CLKDIVRST") and

                len(probe_list) == 3):

 

        template_name = "hold/template__gclk__rise__scanmode__fall__pushout__3.sp"

        return template_name

 

    if( arc_type == "hold" and

                (fnmatch.fnmatch(cell_name, "DCCKSDIV2MX*") or fnmatch.fnmatch(cell_name, "DCCKSDIV2RPMX*") or fnmatch.fnmatch(cell_name, "DCCKDIV2*") or fnmatch.fnmatch(cell_name, "DCCKSDIV2*")) and

                constr_pin == "SCANMODE" and

                constr_pin_dir == "rise" and

                rel_pin == "CLKIN" and

                rel_pin_dir == "rise" and

                fnmatch.fnmatch(when, "!FPM_CLKDIVRST&FSCAN_CLKDIVRST") and

                len(probe_list) == 2):

 

        template_name = "hold/template__gclk__rise__scanmode__rise__pushout__2.sp"

        return template_name

 

    if( arc_type == "hold" and

                (fnmatch.fnmatch(cell_name, "DCCKSDIV2MX*") or fnmatch.fnmatch(cell_name, "DCCKSDIV2RPMX*") or fnmatch.fnmatch(cell_name, "DCCKDIV2*") or fnmatch.fnmatch(cell_name, "DCCKSDIV2*")) and

                constr_pin == "SCANMODE" and

                constr_pin_dir == "fall" and

                rel_pin == "CLKIN" and

                rel_pin_dir == "rise" and

                fnmatch.fnmatch(when, "FPM_CLKDIVRST&!FSCAN_CLKDIVRST") and

                len(probe_list) == 2):

 

        template_name = "hold/template__gclk__rise__scanmode__fall__pushout__2.sp"

        return template_name

 

    if( arc_type == "hold" and

                (fnmatch.fnmatch(cell_name, "DCCKSDIV2MX*") or fnmatch.fnmatch(cell_name, "DCCKSDIV2RPMX*") or fnmatch.fnmatch(cell_name, "DCCKDIV2*") or fnmatch.fnmatch(cell_name, "DCCKSDIV2*")) and

                fnmatch.fnmatch(constr_pin, "F*_CLKDIVRST") and

                constr_pin_dir == "rise" and

                rel_pin == "CLKIN" and

                rel_pin_dir == "rise" and

                len(probe_list) == 3):

 

        template_name = "hold/template__gclk__rise__clkdivrst__rise__pushout__3.sp"

        return template_name

 

    if( arc_type == "hold" and

                (fnmatch.fnmatch(cell_name, "DCCKSDIV2MX*") or fnmatch.fnmatch(cell_name, "DCCKSDIV2RPMX*") or fnmatch.fnmatch(cell_name, "DCCKDIV2*") or fnmatch.fnmatch(cell_name, "DCCKSDIV2*")) and

                fnmatch.fnmatch(constr_pin, "F*_CLKDIVRST") and

                constr_pin_dir == "fall" and

                rel_pin == "CLKIN" and

                rel_pin_dir == "rise" and

                len(probe_list) == 3):

 

        template_name = "hold/template__gclk__rise__clkdivrst__fall__glitch__maxq__3.sp"

        return template_name

 

    if( arc_type == "hold" and

                (fnmatch.fnmatch(cell_name, "DCCKSDIV2MX*") or fnmatch.fnmatch(cell_name, "DCCKSDIV2RPMX*") or fnmatch.fnmatch(cell_name, "DCCKDIV2*") or fnmatch.fnmatch(cell_name, "DCCKSDIV2*")) and

                fnmatch.fnmatch(constr_pin, "F*_CLKDIVRST") and

                constr_pin_dir == "rise" and

                rel_pin == "CLKIN" and

                rel_pin_dir == "rise" and

                len(probe_list) == 2):

        if(fnmatch.fnmatch(when, "FPM_CLKDIVRST")):

                template_name = "hold/template__gclk__rise__clkdivrst__rise__pushout__2.sp"

                return template_name

        else:

                template_name = "hold/template__gclk__rise__fpm__clkdivrst__rise__pushout__2.sp"

                return template_name

 

    if( arc_type == "hold" and

                (fnmatch.fnmatch(cell_name, "DCCKSDIV2MX*") or fnmatch.fnmatch(cell_name, "DCCKSDIV2RPMX*") or fnmatch.fnmatch(cell_name, "DCCKDIV2*") or fnmatch.fnmatch(cell_name, "DCCKSDIV2*")) and

                fnmatch.fnmatch(constr_pin, "F*_CLKDIVRST") and

                constr_pin_dir == "fall" and

                rel_pin == "CLKIN" and

                rel_pin_dir == "rise" and

                len(probe_list) == 2):

        if(fnmatch.fnmatch(when, "FPM_CLKDIVRST")):

                template_name = "hold/template__gclk__rise__clkdivrst__fall__glitch__maxq__2.sp"

                return template_name

        else:

                template_name = "hold/template__gclk__rise__fpm__clkdivrst__fall__glitch__maxq__2.sp"

                return template_name

 

    # DCCL cell 2020/3/16

    if( arc_type == "hold" and

                fnmatch.fnmatch(cell_name, "DCCK*DIV*") and

                constr_pin == "CLKDIVRST" and

                constr_pin_dir == "rise" and

                rel_pin == "CLKIN" and

                rel_pin_dir == "rise" and

                "CLKEN" in when and

                len(probe_list) == 1):

 

        template_name = "hold/template__gclk__rise__clkdivrst__rise__pushout__1.sp"

        return template_name

 

    if( arc_type == "hold" and

                fnmatch.fnmatch(cell_name, "DCCK*DIV*") and

                constr_pin == "CLKDIVRST" and

                constr_pin_dir == "fall" and

                rel_pin == "CLKIN" and

                rel_pin_dir == "rise" and

                "CLKEN" in when and

                len(probe_list) == 1):

 

        template_name = "hold/template__gclk__rise__clkdivrst__fall__glitch__maxq__1.sp"

        return template_name

 

    if( arc_type == "hold" and

                fnmatch.fnmatch(cell_name, "DCCKSDIV2*") and

                constr_pin == "CLKDIVRST" and

                constr_pin_dir == "rise" and

                rel_pin == "CLKIN" and

                rel_pin_dir == "rise" and

                "CLKEN&!SCANCLK" in when and

                len(probe_list) == 1):

 

        template_name = "hold/template__gclk__rise__clkdivrst__rise__pushout__1.sp"

        return template_name

 

    if( arc_type == "hold" and

                fnmatch.fnmatch(cell_name, "DCCKSDIV2*") and

                constr_pin == "CLKDIVRST" and

                constr_pin_dir == "fall" and

                rel_pin == "CLKIN" and

                rel_pin_dir == "rise" and

                "CLKEN&!SCANCLK" in when and

                len(probe_list) == 1):

 

        template_name = "hold/template__gclk__rise__clkdivrst__fall__glitch__maxq__1.sp"

        return template_name

 

    if( arc_type == "hold" and

                fnmatch.fnmatch(cell_name, "DCCK*DIV2O4*") and

                constr_pin == "CLKDIVRST" and

                constr_pin_dir == "rise" and

                rel_pin == "CLKIN" and

                rel_pin_dir == "rise" and

                "!CLKEN&!DIVS&!SCANCLK" in when and

                len(probe_list) == 2):

 

        template_name = "hold/template__gclk__rise__clkdivrst__rise__nx__pushout__1.sp"

        return template_name

 

    if( arc_type == "hold" and

                fnmatch.fnmatch(cell_name, "DCCK*DIV2O4*") and

                constr_pin == "CLKDIVRST" and

                constr_pin_dir == "fall" and

                rel_pin == "CLKIN" and

                rel_pin_dir == "rise" and

                "CLKEN&!DIVS&!SCANCLK" in when and

                len(probe_list) == 2):

 

        template_name = "hold/template__gclk__rise__clkdivrst__fall__pushout__maxq__2.sp"

        return template_name

 

    if( arc_type == "hold" and

                fnmatch.fnmatch(cell_name, "DCCKDIV2*") and

                constr_pin == "CLKEN" and

                constr_pin_dir == "rise" and

                rel_pin == "CLKIN" and

                rel_pin_dir == "rise" and

                "!CLKDIVRST" in when and

                len(probe_list) == 1):

 

        template_name = "hold/template__gclk__rise__clken__rise__glitch__maxq__1.sp"

        return template_name

 

    if( arc_type == "hold" and

                fnmatch.fnmatch(cell_name, "DCCKDIV2*") and

                constr_pin == "CLKEN" and

                constr_pin_dir == "fall" and

                rel_pin == "CLKIN" and

                rel_pin_dir == "rise" and

                "!CLKDIVRST" in when and

                len(probe_list) == 1):

 

        template_name = "hold/template__gclk__rise__clken__fall__pushout__1.sp"

        return template_name

 

    if( arc_type == "hold" and

                fnmatch.fnmatch(cell_name, "DCCKSDIV2*") and

                constr_pin == "CLKEN" and

                constr_pin_dir == "rise" and

                rel_pin == "CLKIN" and

                rel_pin_dir == "rise" and

                "!CLKDIVRST&!SCANCLK" in when and

                len(probe_list) == 1):

 

        template_name = "hold/template__gclk__rise__clken__rise__glitch__maxq__1.sp"

        return template_name

 

    if( arc_type == "hold" and

                fnmatch.fnmatch(cell_name, "DCCKSDIV2O4*") and

                constr_pin == "CLKEN" and

                constr_pin_dir == "rise" and

                rel_pin == "CLKIN" and

                rel_pin_dir == "rise" and

                "!CLKDIVRST&!DIVS&!SCANCLK" in when and

                len(probe_list) == 1):

 

        template_name = "hold/template__gclk__rise__clken__rise__glitch__maxq__1.sp"

        return template_name

 

    if( arc_type == "hold" and

                fnmatch.fnmatch(cell_name, "DCCKSDIV2O4*") and

                constr_pin == "CLKEN" and

                constr_pin_dir == "fall" and

                rel_pin == "CLKIN" and

                rel_pin_dir == "rise" and

                "!CLKDIVRST&!DIVS&!SCANCLK" in when and

                len(probe_list) == 1):

 

        template_name = "hold/template__gclk__rise__clken__fall__pushout__1.sp"

        return template_name

 

    if( arc_type == "hold" and

                fnmatch.fnmatch(cell_name, "DCCKSDIV2*") and

                constr_pin == "CLKEN" and

                constr_pin_dir == "fall" and

                rel_pin == "CLKIN" and

                rel_pin_dir == "rise" and

                "!CLKDIVRST&!SCANCLK" in when and                                                                                     

                len(probe_list) == 1):

 

        template_name = "hold/template__gclk__rise__clken__fall__pushout__1.sp"

        return template_name

 

    if( arc_type == "hold" and

                fnmatch.fnmatch(cell_name, "DCCKSDIV2O4*") and

                constr_pin == "DIVS" and

                constr_pin_dir == "rise" and

                rel_pin == "CLKIN" and

                rel_pin_dir == "rise" and

                (("!CLKDIVRST&CLKEN&!SCANCLK" in when) or ("!CLKDIVRST&CLKEN&SCANCLK" in when)) and

                len(probe_list) == 1):

 

        template_name = "hold/template__gclk__rise__divs__rise__glitch__maxq__1.sp"

        return template_name

 

    if( arc_type == "hold" and

                fnmatch.fnmatch(cell_name, "DCCKSDIV2O4*") and

                constr_pin == "DIVS" and

                constr_pin_dir == "fall" and

                rel_pin == "CLKIN" and

                rel_pin_dir == "rise" and

                (("!CLKDIVRST&CLKEN&!SCANCLK" in when) or ("!CLKDIVRST&CLKEN&SCANCLK" in when)) and

                len(probe_list) == 1):

 

        template_name = "hold/template__gclk__rise__divs__fall__pushout__1.sp"

        return template_name

    # DCCK cell CDN->CP 2020/10/12

    if( arc_type == "removal" and

                fnmatch.fnmatch(cell_name, "DCCKDIV*") and

                constr_pin == "CDN" and

                constr_pin_dir == "rise" and

                rel_pin == "CP" and

                rel_pin_dir == "rise" and

                "!D" in when and

                len(probe_list) == 1):

 

        template_name = "hold/template__gclk__rise__clken__rise__glitch__maxq__1.sp"

        return template_name

 

    # DCCK cell D->CP  2020/12/28

    if( arc_type == "hold" and

                fnmatch.fnmatch(cell_name, "DCCKDIV4*") and

        fnmatch.fnmatch(constr_pin, "D*") and

                constr_pin_dir == "rise" and

                fnmatch.fnmatch(rel_pin, "CP") and

                rel_pin_dir == "rise" and

                len(probe_list) == 1):

 

        template_name = "hold/template__DIV4__rise__rise__1.sp"

        return template_name

 

    if( arc_type == "hold" and

                fnmatch.fnmatch(cell_name, "DCCKDIV4*") and

        fnmatch.fnmatch(constr_pin, "D*") and

                constr_pin_dir == "fall" and

                fnmatch.fnmatch(rel_pin, "CP") and

                rel_pin_dir == "rise" and

                len(probe_list) == 1):

 

        template_name = "hold/template__DIV4__rise__fall__1.sp"

        return template_name

 

    # DCCK cell CLKEN->nx  2020/7/31

    if( arc_type == "hold" and

                fnmatch.fnmatch(cell_name, "DCCK*DIV*") and

                (fnmatch.fnmatch(constr_pin, "CLKEN*") or fnmatch.fnmatch(constr_pin, "F*CLKEN*")) and

                constr_pin_dir == "rise" and

                rel_pin == "nx" and

                rel_pin_dir == "rise" and

                len(probe_list) == 1):

 

        template_name = "hold/template__gclk__nx__rise__clken__rise__glitch__maxq__1.sp"

        return template_name

 

    if( arc_type == "hold" and

                fnmatch.fnmatch(cell_name, "DCCK*DIV*") and

                (fnmatch.fnmatch(constr_pin, "CLKEN*") or fnmatch.fnmatch(constr_pin, "F*CLKEN*")) and

                constr_pin_dir == "fall" and

                rel_pin == "nx" and

                rel_pin_dir == "rise" and

                len(probe_list) == 1):

 

        template_name = "hold/template__gclk__nx__rise__clken__fall__pushout__1.sp"

        return template_name

 

    if( arc_type == "hold" and

                fnmatch.fnmatch(cell_name, "DCCKLNQ*") and

                constr_pin == "CLKEN" and

                constr_pin_dir == "rise" and

                rel_pin == "CLKIN" and

                rel_pin_dir == "rise"):

 

        template_name = "hold/template__latch__rise__rise__glitch__maxq__1.sp"

        return template_name

 

    if( arc_type == "hold" and

                fnmatch.fnmatch(cell_name, "DCCKLNQ*") and

                constr_pin == "CLKEN" and

                constr_pin_dir == "fall" and

                rel_pin == "CLKIN" and

                rel_pin_dir == "rise"):

 

        template_name = "hold/template__latch__rise__fall__pushout__1.sp"

        return template_name

 

    if( arc_type == "hold" and

                fnmatch.fnmatch(cell_name, "DCCKSLNQ*") and

                constr_pin == "CLKEN" and

                constr_pin_dir == "rise" and

                rel_pin == "CLKIN" and

                rel_pin_dir == "rise" and

                "!SCANCLK" in when):

 

        template_name = "hold/template__latch__rise__rise__glitch__maxq__1.sp"

        return template_name

 

    if( arc_type == "hold" and

                fnmatch.fnmatch(cell_name, "DCCKSLNQ*") and

                constr_pin == "CLKEN" and

                constr_pin_dir == "fall" and

                rel_pin == "CLKIN" and

                rel_pin_dir == "rise" and

                "!SCANCLK" in when):

 

        template_name = "hold/template__latch__rise__fall__pushout__1.sp"

        return template_name

    #DCCKANSLNQ* for N3 new cell 2021/1/26 from CW

    if( arc_type == "hold" and

                fnmatch.fnmatch(cell_name, "DCCKANSLNQ*") and

                constr_pin == "CLKEN" and

                constr_pin_dir == "rise" and

                rel_pin == "CLKIN" and

                rel_pin_dir == "rise" and

                                (("CLKOUT" in probe_list) or ("ml_b" in probe_list))):

 

        template_name = "hold/template__latch__rise__rise__glitch__maxq__1.sp"

        return template_name

 

    if( arc_type == "hold" and

                fnmatch.fnmatch(cell_name, "DCCKANSLNQ*") and

                constr_pin == "CLKEN" and

                constr_pin_dir == "fall" and

                rel_pin == "CLKIN" and

                rel_pin_dir == "rise" and

                                "CLKOUT" in probe_list):

 

        template_name = "hold/template__latch__rise__fall__pushout__1.sp"

        return template_name

 

    if( arc_type == "hold" and

                fnmatch.fnmatch(cell_name, "DCCKANSLNQ*") and

                constr_pin == "CLKEN" and

                constr_pin_dir == "fall" and

                rel_pin == "CLKIN" and

                rel_pin_dir == "rise" and

                                "ml_b" in probe_list):

 

        template_name = "hold/template__latch__rise__fall__glitch__minq__1.sp"

        return template_name

   

    # CKLNT*/EDFKCNQ* 2021/1/28 from CW

    if( arc_type == "hold" and

                (fnmatch.fnmatch(cell_name, "CKLNTSRQ*") or fnmatch.fnmatch(cell_name, "CKLNTRPQ*") or fnmatch.fnmatch(cell_name, "CKLNTQ*")) and

                constr_pin == "EN" and

                constr_pin_dir == "rise" and

                rel_pin == "CLK" and

                rel_pin_dir == "rise" ):

 

        template_name = "hold/template__latch__rise__rise__glitch__maxq__1.sp"

        return template_name

  

    if( arc_type == "hold" and

                (fnmatch.fnmatch(cell_name, "CKLNTSRQ*") or fnmatch.fnmatch(cell_name, "CKLNTRPQ*") or fnmatch.fnmatch(cell_name, "CKLNTQ*")) and

                constr_pin == "EN" and

                constr_pin_dir == "fall" and

                rel_pin == "CLK" and

                rel_pin_dir == "rise" ):

 

        template_name = "hold/template__latch__rise__fall__glitch__minq__1.sp"

        return template_name

 

    if( arc_type == "hold" and

                fnmatch.fnmatch(cell_name, "EDFKCNQ*") and

                        fnmatch.fnmatch(constr_pin, "CN") and

                constr_pin_dir == "rise" and

                fnmatch.fnmatch(rel_pin, "CP") and

                rel_pin_dir == "rise"):

 

        template_name = "hold/template__SLH__rise__SE__rise__pushout__1.sp"

        return template_name

 

    if( arc_type == "hold" and

                fnmatch.fnmatch(cell_name, "EDFKCNQ*") and

                        fnmatch.fnmatch(constr_pin, "CN") and

                constr_pin_dir == "fall" and

                fnmatch.fnmatch(rel_pin, "CP") and

                rel_pin_dir == "rise"):

 

        template_name = "hold/template__SLH__rise__SE__fall__pushout__1.sp"

        return template_name

 

    #EDFCNSPQ*D* for N3 new cell 2021/1/19 from CW

    if( arc_type == "hold" and

                fnmatch.fnmatch(cell_name, "*EDFCNSPQ*D*") and

                constr_pin == "E" and

                constr_pin_dir == "rise" and

                rel_pin == "CP" and

                rel_pin_dir == "rise" and

                "D" in when and

                not "!D" in when and

                len(probe_list) == 1):

 

        template_name = "hold/template__EDF__D__rise__rise__glitch__minq__1.sp"

        return template_name

 

    if( arc_type == "removal" and

                fnmatch.fnmatch(cell_name, "*EDFCNSPQ*D*") and

                                constr_pin == "CDN" and

                constr_pin_dir == "rise" and

                rel_pin == "CP" and

                rel_pin_dir == "rise" and

                len(probe_list) == 1):

 

        template_name = "hold/template__latch__rise__rise__glitch__maxq__1.sp"

        return template_name

 

    if( arc_type == "removal" and

                fnmatch.fnmatch(cell_name, "*EDFCNSPQ*D*") and

                                constr_pin == "SD" and

                constr_pin_dir == "fall" and

                rel_pin == "CP" and

                rel_pin_dir == "rise" and

                len(probe_list) == 1):

 

        template_name = "hold/template__latch__rise__fall__glitch__minq__1.sp"

        return template_name

    # CKG*AN/CKG*ND without probe 2021/2/22 => 2021/3/4 hard code fix

    if( arc_type == "nochange_high_high" and

                (fnmatch.fnmatch(cell_name, "CKGND2CCHD2BWP143M169H3P45CPD*") or fnmatch.fnmatch(cell_name, "CKGND2CCHEQAD1BWP143M169H3P45CPD*")) and

                constr_pin == "EN" and

                constr_pin_dir == "rise" and

                rel_pin == "CP" and

                rel_pin_dir == "rise"):

 

        template_name = "nochange/template__ckgn__setup__rise__en__rise__pushout__0.sp"

        return template_name

 

    if( arc_type == "nochange_high_high" and

                (fnmatch.fnmatch(cell_name, "CKGAN2CCHD1BWP143M169H3P45CPD*") or fnmatch.fnmatch(cell_name, "CKGAN2CCHEQAD2BWP143M169H3P45CPD*")) and

                constr_pin == "EN" and

                constr_pin_dir == "rise" and

                rel_pin == "CP" and

                rel_pin_dir == "rise"):

 

        template_name = "nochange/template__ckg__setup__rise__en__rise__pushout__0.sp"

        return template_name

 

    if( arc_type == "nochange_high_high" and

                (fnmatch.fnmatch(cell_name, "CKGND2CCHD2BWP143M169H3P45CPD*") or fnmatch.fnmatch(cell_name, "CKGND2CCHEQAD1BWP143M169H3P45CPD*")) and

                constr_pin == "EN" and

                constr_pin_dir == "fall" and

                rel_pin == "CP" and

                rel_pin_dir == "fall"):

 

        template_name = "nochange/template__ckgn__hold__fall__en__fall__pushout__negative__0.sp"

        return template_name

 

    if( arc_type == "nochange_high_high" and

                (fnmatch.fnmatch(cell_name, "CKGAN2CCHD1BWP143M169H3P45CPD*") or fnmatch.fnmatch(cell_name, "CKGAN2CCHEQAD2BWP143M169H3P45CPD*")) and

                constr_pin == "EN" and

                constr_pin_dir == "fall" and

                rel_pin == "CP" and

                rel_pin_dir == "fall"):

 

        template_name = "nochange/template__ckg__hold__fall__en__fall__pushout__negative__0.sp"

        return template_name

 

    if( arc_type == "nochange_low_high" and

                (fnmatch.fnmatch(cell_name, "CKGND2CCHD2BWP143M169H3P45CPD*") or fnmatch.fnmatch(cell_name, "CKGND2CCHEQAD1BWP143M169H3P45CPD*")) and

                constr_pin == "EN" and

                constr_pin_dir == "fall" and

                rel_pin == "CP" and

                rel_pin_dir == "rise"):

 

        template_name = "nochange/template__ckg__setup__rise__en__fall__20__percent__glitch__minq__0.sp"

        return template_name

 

    if( arc_type == "nochange_low_high" and

                (fnmatch.fnmatch(cell_name, "CKGND2CCHD2BWP143M169H3P45CPD*") or fnmatch.fnmatch(cell_name, "CKGND2CCHEQAD1BWP143M169H3P45CPD*")) and

                constr_pin == "EN" and

                constr_pin_dir == "rise" and

                rel_pin == "CP" and

                rel_pin_dir == "fall"):

 

        template_name = "nochange/template__ckg__hold__fall__en__rise__20__percent__glitch__minq__0.sp"

        return template_name

    #CKG update for CKG*NR/CKG*ND 2021/3/4 add preZ

    if( arc_type == "nochange_high_high" and

                (fnmatch.fnmatch(cell_name, "*CKG*AN*") or fnmatch.fnmatch(cell_name, "*CKG*OR*"))and

                (constr_pin == "EN" or constr_pin == "ISO") and

                constr_pin_dir == "rise" and

                (rel_pin == "CP" or rel_pin == "I" or rel_pin == "CLK") and

                rel_pin_dir == "rise"): #and

                #"preZ" in probe_list):

 

        template_name = "nochange/template__ckg__setup__rise__en__rise__pushout__maxq__1.sp"

        return template_name

 

    if( arc_type == "nochange_high_high" and

                (fnmatch.fnmatch(cell_name, "*CKG*AN*") or fnmatch.fnmatch(cell_name, "*CKG*OR*"))and

                (constr_pin == "EN" or constr_pin == "ISO") and

                constr_pin_dir == "fall" and

                (rel_pin == "CP" or rel_pin == "I" or rel_pin == "CLK") and

                rel_pin_dir == "fall"): #and

                #"preZ" in probe_list):

 

        template_name = "nochange/template__ckg__hold__fall__en__fall__pushout__minq__negative__1.sp"

        return template_name

 

    if( arc_type == "nochange_low_low" and

                (fnmatch.fnmatch(cell_name, "*CKG*AN*") or fnmatch.fnmatch(cell_name, "*CKG*OR*"))and

                (constr_pin == "EN" or constr_pin == "ISO") and

                constr_pin_dir == "fall" and

                (rel_pin == "CP" or rel_pin == "I" or rel_pin == "CLK") and

                rel_pin_dir == "fall" and

                "preZ" in probe_list):

 

        template_name = "nochange/template__ckg__setup__fall__en__fall__pushout__minq__1.sp"

        return template_name

 

    if( arc_type == "nochange_low_low" and

                (fnmatch.fnmatch(cell_name, "*CKG*AN*") or fnmatch.fnmatch(cell_name, "*CKG*OR*"))and

                (constr_pin == "EN" or constr_pin == "ISO") and

                constr_pin_dir == "rise" and

                (rel_pin == "CP" or rel_pin == "I" or rel_pin == "CLK") and

                rel_pin_dir == "rise" and

                "preZ" in probe_list):

 

        template_name = "nochange/template__ckg__hold__rise__en__rise__pushout__maxq__negative__1.sp"

        return template_name

 

    if( arc_type == "nochange_high_high" and

                (fnmatch.fnmatch(cell_name, "CK*RCB*D*") or fnmatch.fnmatch(cell_name, "DCCK*RCB*D*")) and

                constr_pin == "EN" and

                constr_pin_dir == "rise" and

                rel_pin == "CLK" and

                rel_pin_dir == "rise" and

                "FD&RD" in when and

                "preZ" in probe_list):

 

        template_name = "nochange/template__ckg__setup__rise__en__rise__pushout__maxq__1.sp"

        return template_name

 

    if( arc_type == "nochange_high_high" and

                (fnmatch.fnmatch(cell_name, "CK*RCB*D*") or fnmatch.fnmatch(cell_name, "DCCK*RCB*D*")) and

                constr_pin == "EN" and

                constr_pin_dir == "fall" and

                rel_pin == "CLK" and

                rel_pin_dir == "fall" and

                "!FD&!RD" in when and

                "preZ" in probe_list):

 

        template_name = "nochange/template__ckg__hold__fall__en__fall__pushout__minq__negative__1.sp"

        return template_name

 

    if( arc_type == "nochange_low_low" and

                (fnmatch.fnmatch(cell_name, "CK*RCB*D*") or fnmatch.fnmatch(cell_name, "DCCK*RCB*D*")) and

                constr_pin == "EN" and

                constr_pin_dir == "fall" and

                rel_pin == "CLK" and

                rel_pin_dir == "fall" and

                "FD&RD" in when and

                "preZ" in probe_list):

 

        template_name = "nochange/template__ckg__setup__fall__en__fall__pushout__minq__1.sp"

        return template_name

 

    if( arc_type == "nochange_low_low" and

                (fnmatch.fnmatch(cell_name, "CK*RCB*D*") or fnmatch.fnmatch(cell_name, "DCCK*RCB*D*")) and

                constr_pin == "EN" and

                constr_pin_dir == "rise" and

                rel_pin == "CLK" and

                rel_pin_dir == "rise" and

                "!FD&!RD" in when and

                "preZ" in probe_list):

 

        template_name = "nochange/template__ckg__hold__rise__en__rise__pushout__maxq__negative__1.sp"

        return template_name

 

    if( arc_type == "nochange_high_high" and

                fnmatch.fnmatch(cell_name, "CK*MUX2GF*") and

                constr_pin == "S1" and

                constr_pin_dir == "rise" and

                rel_pin == "CLK1" and

                rel_pin_dir == "rise" and

                "CLK2&!S2" in when and

                "iq3" in probe_list):

 

        template_name = "nochange/template__ckg__setup__rise__en__rise__pushout__maxq__1.sp"

        return template_name

 

    if( arc_type == "nochange_high_high" and

                fnmatch.fnmatch(cell_name, "CK*MUX2GF*") and

                constr_pin == "S1" and

                constr_pin_dir == "fall" and

                rel_pin == "CLK1" and

                rel_pin_dir == "fall" and

                "CLK2&!S2" in when and

                "iq3" in probe_list):

 

        template_name = "nochange/template__ckg__hold__fall__en__fall__pushout__minq__negative__1.sp"

        return template_name

 

    if( arc_type == "nochange_low_low" and

                fnmatch.fnmatch(cell_name, "CK*MUX2GF*") and

                constr_pin == "S1" and

                constr_pin_dir == "fall" and

                rel_pin == "CLK1" and

                rel_pin_dir == "fall" and

                "CLK2&!S2" in when and

                "iq3" in probe_list):

 

        template_name = "nochange/template__ckg__setup__fall__en__fall__pushout__minq__1.sp"

        return template_name

 

    if( arc_type == "nochange_low_low" and

                fnmatch.fnmatch(cell_name, "CK*MUX2GF*") and

                constr_pin == "S1" and

                constr_pin_dir == "rise" and

                rel_pin == "CLK1" and

                rel_pin_dir == "rise" and

                "CLK2&!S2" in when and

                "iq3" in probe_list):

 

        template_name = "nochange/template__ckg__hold__rise__en__rise__pushout__maxq__negative__1.sp"

        return template_name

 

    if( arc_type == "nochange_high_high" and

                fnmatch.fnmatch(cell_name, "CK*MUX2GF*") and

                constr_pin == "S2" and

                constr_pin_dir == "rise" and

                rel_pin == "CLK2" and

                rel_pin_dir == "rise" and

                "CLK1&!S1" in when and

                "iq4" in probe_list):

 

        template_name = "nochange/template__ckg__setup__rise__en__rise__pushout__maxq__1.sp"

        return template_name

 

    if( arc_type == "nochange_high_high" and

                fnmatch.fnmatch(cell_name, "CK*MUX2GF*") and

                constr_pin == "S2" and

                constr_pin_dir == "fall" and

                rel_pin == "CLK2" and

                rel_pin_dir == "fall" and

                "CLK1&!S1" in when and

                "iq4" in probe_list):

 

        template_name = "nochange/template__ckg__hold__fall__en__fall__pushout__minq__negative__1.sp"

        return template_name

 

    if( arc_type == "nochange_low_low" and

                fnmatch.fnmatch(cell_name, "CK*MUX2GF*") and

                constr_pin == "S2" and

                constr_pin_dir == "fall" and

                rel_pin == "CLK2" and

                rel_pin_dir == "fall" and

                "CLK1&!S1" in when and

                "iq4" in probe_list):

 

        template_name = "nochange/template__ckg__setup__fall__en__fall__pushout__minq__1.sp"

        return template_name

 

    if( arc_type == "nochange_low_low" and

                fnmatch.fnmatch(cell_name, "CK*MUX2GF*") and

                constr_pin == "S2" and

                constr_pin_dir == "rise" and

                rel_pin == "CLK2" and

                rel_pin_dir == "rise" and

                "CLK1&!S1" in when and

                "iq4" in probe_list):

 

        template_name = "nochange/template__ckg__hold__rise__en__rise__pushout__maxq__negative__1.sp"

        return template_name

 

    #CKG update for CKG*NR/CKG*ND 2020/7/31

    if( arc_type == "nochange_high_high" and

                (fnmatch.fnmatch(cell_name, "*CKG*NR*") or fnmatch.fnmatch(cell_name, "*CKG*ND*")) and

                constr_pin == "EN" and

                constr_pin_dir == "rise" and

                rel_pin == "CP" and

                rel_pin_dir == "rise"):

 

        template_name = "nochange/template__ckgn__setup__rise__en__rise__pushout__1.sp"

        return template_name

 

    if( arc_type == "nochange_high_high" and

                (fnmatch.fnmatch(cell_name, "*CKG*AN*") or fnmatch.fnmatch(cell_name, "*CKG*OR*"))and

                (constr_pin == "EN" or constr_pin == "ISO") and

                constr_pin_dir == "rise" and

                (rel_pin == "CP" or rel_pin == "I") and

                rel_pin_dir == "rise"):

 

        template_name = "nochange/template__ckg__setup__rise__en__rise__pushout__1.sp"

        return template_name

 

    if( arc_type == "nochange_high_high" and

                (fnmatch.fnmatch(cell_name, "*CKG*NR*") or fnmatch.fnmatch(cell_name, "*CKG*ND*")) and

                constr_pin == "EN" and

                constr_pin_dir == "fall" and

                rel_pin == "CP" and

                rel_pin_dir == "fall"):

 

        template_name = "nochange/template__ckgn__hold__fall__en__fall__pushout__negative__1.sp"

        return template_name

 

    if( arc_type == "nochange_high_high" and

                (fnmatch.fnmatch(cell_name, "*CKG*AN*") or fnmatch.fnmatch(cell_name, "*CKG*OR*"))and

                (constr_pin == "EN" or constr_pin == "ISO") and

                constr_pin_dir == "fall" and

                (rel_pin == "CP" or rel_pin == "I") and

                rel_pin_dir == "fall"):

 

        template_name = "nochange/template__ckg__hold__fall__en__fall__pushout__negative__1.sp"

        return template_name

 

    if( arc_type == "nochange_low_high" and

                (fnmatch.fnmatch(cell_name, "DC*CKG*") or fnmatch.fnmatch(cell_name, "CKG*") or fnmatch.fnmatch(cell_name, "PTCKG*ISO*")) and

                (constr_pin == "EN" or constr_pin == "ISO") and

                constr_pin_dir == "fall" and

                (rel_pin == "CP" or rel_pin == "I") and

                rel_pin_dir == "rise"):

 

        template_name = "nochange/template__ckg__setup__rise__en__fall__20__percent__glitch__minq__1.sp"

        return template_name

 

    if( arc_type == "nochange_low_high" and

                (fnmatch.fnmatch(cell_name, "DC*CKG*") or fnmatch.fnmatch(cell_name, "CKG*") or fnmatch.fnmatch(cell_name, "PTCKG*ISO*")) and

                (constr_pin == "EN" or constr_pin == "ISO") and

                constr_pin_dir == "rise" and

                (rel_pin == "CP" or rel_pin == "I") and

                rel_pin_dir == "fall"):

 

        template_name = "nochange/template__ckg__hold__fall__en__rise__20__percent__glitch__minq__1.sp"

        return template_name

 

    if( arc_type == "nochange_low_low" and

                (fnmatch.fnmatch(cell_name, "*CKG*NR*") or fnmatch.fnmatch(cell_name, "*CKG*ND*")) and

                constr_pin == "EN" and

                constr_pin_dir == "fall" and

                rel_pin == "CP" and

                rel_pin_dir == "fall"):

 

        template_name = "nochange/template__ckgn__setup__fall__en__fall__pushout__1.sp"

        return template_name

 

    if( arc_type == "nochange_low_low" and

                (fnmatch.fnmatch(cell_name, "*CKG*AN*") or fnmatch.fnmatch(cell_name, "*CKG*OR*"))and

                (constr_pin == "EN" or constr_pin == "ISO") and

                constr_pin_dir == "fall" and

                (rel_pin == "CP" or rel_pin == "I") and

                rel_pin_dir == "fall"):

 

        template_name = "nochange/template__ckg__setup__fall__en__fall__pushout__1.sp"

        return template_name

 

    if( arc_type == "nochange_low_low" and

                (fnmatch.fnmatch(cell_name, "*CKG*NR*") or fnmatch.fnmatch(cell_name, "*CKG*ND*")) and

                constr_pin == "EN" and

                constr_pin_dir == "rise" and

                rel_pin == "CP" and

                rel_pin_dir == "rise"):

 

        template_name = "nochange/template__ckgn__hold__rise__en__rise__pushout__negative__1.sp"

        return template_name

 

    if( arc_type == "nochange_low_low" and

                (fnmatch.fnmatch(cell_name, "*CKG*AN*") or fnmatch.fnmatch(cell_name, "*CKG*OR*"))and

                (constr_pin == "EN" or constr_pin == "ISO") and

                constr_pin_dir == "rise" and

                (rel_pin == "CP" or rel_pin == "I") and

                rel_pin_dir == "rise"):

 

        template_name = "nochange/template__ckg__hold__rise__en__rise__pushout__negative__1.sp"

        return template_name

 

    if( arc_type == "nochange_high_low" and

                (fnmatch.fnmatch(cell_name, "DC*CKG*") or fnmatch.fnmatch(cell_name, "CKG*") or fnmatch.fnmatch(cell_name, "PTCKG*ISO*")) and

                (constr_pin == "EN" or constr_pin == "ISO") and

                constr_pin_dir == "rise" and

                (rel_pin == "CP" or rel_pin == "I") and

                rel_pin_dir == "fall"):

 

        template_name = "nochange/template__ckg__setup__fall__en__rise__20__percent__glitch__maxq__1.sp"

        return template_name

 

    if( arc_type == "nochange_high_low" and

                (fnmatch.fnmatch(cell_name, "DC*CKG*") or fnmatch.fnmatch(cell_name, "CKG*") or fnmatch.fnmatch(cell_name, "PTCKG*ISO*")) and

                (constr_pin == "EN" or constr_pin == "ISO") and

                constr_pin_dir == "fall" and

                (rel_pin == "CP" or rel_pin == "I") and

                rel_pin_dir == "rise"):

 

        template_name = "nochange/template__ckg__hold__rise__en__fall__20__percent__glitch__maxq__1.sp"

        return template_name

 

    if( arc_type == "nochange_high_high" and

                (fnmatch.fnmatch(cell_name, "CK*RCB*D*") or fnmatch.fnmatch(cell_name, "DCCK*RCB*D*")) and

                constr_pin == "EN" and

                constr_pin_dir == "rise" and

                rel_pin == "CLK" and

                rel_pin_dir == "rise" and

                "FD&RD" in when):

 

        template_name = "nochange/template__ckg__setup__rise__en__rise__pushout__1.sp"

        return template_name

 

    if( arc_type == "nochange_high_high" and

                (fnmatch.fnmatch(cell_name, "CK*RCB*D*") or fnmatch.fnmatch(cell_name, "DCCK*RCB*D*")) and

                constr_pin == "EN" and

                constr_pin_dir == "fall" and

                rel_pin == "CLK" and

                rel_pin_dir == "fall" and

                "!FD&!RD" in when):

 

        template_name = "nochange/template__ckg__hold__fall__en__fall__pushout__negative__1.sp"

        return template_name

 

    if( arc_type == "nochange_low_high" and

                (fnmatch.fnmatch(cell_name, "CK*RCB*D*") or fnmatch.fnmatch(cell_name, "DCCK*RCB*D*")) and

                constr_pin == "EN" and

                constr_pin_dir == "fall" and

                rel_pin == "CLK" and

                rel_pin_dir == "rise" and

                "!FD&!RD" in when):

 

        template_name = "nochange/template__ckg__setup__rise__en__fall__20__percent__glitch__minq__1.sp"

        return template_name

 

    if( arc_type == "nochange_low_high" and

                (fnmatch.fnmatch(cell_name, "CK*RCB*D*") or fnmatch.fnmatch(cell_name, "DCCK*RCB*D*")) and

                constr_pin == "EN" and

                constr_pin_dir == "rise" and

                rel_pin == "CLK" and

                rel_pin_dir == "fall" and

                "!FD&!RD" in when):

 

        template_name = "nochange/template__ckg__hold__fall__en__rise__20__percent__glitch__minq__1.sp"

        return template_name

 

    if( arc_type == "nochange_low_low" and

                (fnmatch.fnmatch(cell_name, "CK*RCB*D*") or fnmatch.fnmatch(cell_name, "DCCK*RCB*D*")) and

                constr_pin == "EN" and

                constr_pin_dir == "fall" and

                rel_pin == "CLK" and

                rel_pin_dir == "fall" and

                "FD&RD" in when):

 

        template_name = "nochange/template__ckg__setup__fall__en__fall__pushout__1.sp"

        return template_name

 

    if( arc_type == "nochange_low_low" and

                (fnmatch.fnmatch(cell_name, "CK*RCB*D*") or fnmatch.fnmatch(cell_name, "DCCK*RCB*D*")) and

                constr_pin == "EN" and

                constr_pin_dir == "rise" and

                rel_pin == "CLK" and

                rel_pin_dir == "rise" and

                "!FD&!RD" in when):

 

        template_name = "nochange/template__ckg__hold__rise__en__rise__pushout__negative__1.sp"

        return template_name

 

    if( arc_type == "nochange_high_low" and

                (fnmatch.fnmatch(cell_name, "CK*RCB*D*") or fnmatch.fnmatch(cell_name, "DCCK*RCB*D*")) and

                constr_pin == "EN" and

                constr_pin_dir == "rise" and

                rel_pin == "CLK" and

                rel_pin_dir == "fall" and

                "FD&RD" in when):

 

        template_name = "nochange/template__ckg__setup__fall__en__rise__20__percent__glitch__maxq__1.sp"

        return template_name

 

    if( arc_type == "nochange_high_low" and

                (fnmatch.fnmatch(cell_name, "CK*RCB*D*") or fnmatch.fnmatch(cell_name, "DCCK*RCB*D*")) and

                constr_pin == "EN" and

                constr_pin_dir == "fall" and

                rel_pin == "CLK" and

                rel_pin_dir == "rise" and

                "FD&RD" in when):

 

        template_name = "nochange/template__ckg__hold__rise__en__fall__20__percent__glitch__maxq__1.sp"

        return template_name

 

    if( arc_type == "nochange_high_high" and

                fnmatch.fnmatch(cell_name, "CK*MUX2GF*") and

                constr_pin == "S1" and

                constr_pin_dir == "rise" and

                rel_pin == "CLK1" and

                rel_pin_dir == "rise" and

                "CLK2&!S2" in when):

 

        template_name = "nochange/template__ckg__setup__rise__en__rise__pushout__1.sp"

        return template_name

 

    if( arc_type == "nochange_high_high" and

                fnmatch.fnmatch(cell_name, "CK*MUX2GF*") and

                constr_pin == "S1" and

                constr_pin_dir == "fall" and

                rel_pin == "CLK1" and

                rel_pin_dir == "fall" and

                "CLK2&!S2" in when):

 

        template_name = "nochange/template__ckg__hold__fall__en__fall__pushout__negative__1.sp"

        return template_name

 

    if( arc_type == "nochange_low_high" and

                fnmatch.fnmatch(cell_name, "CK*MUX2GF*") and

                constr_pin == "S1" and

                constr_pin_dir == "fall" and

                rel_pin == "CLK1" and

                rel_pin_dir == "rise" and

                "CLK2&!S2" in when):

 

        template_name = "nochange/template__ckg__setup__rise__en__fall__20__percent__glitch__minq__1.sp"

        return template_name

 

    if( arc_type == "nochange_low_high" and

                fnmatch.fnmatch(cell_name, "CK*MUX2GF*") and

                constr_pin == "S1" and

                constr_pin_dir == "rise" and

                rel_pin == "CLK1" and

                rel_pin_dir == "fall" and

                "CLK2&!S2" in when):

 

        template_name = "nochange/template__ckg__hold__fall__en__rise__20__percent__glitch__minq__1.sp"

        return template_name

 

    if( arc_type == "nochange_low_low" and

                fnmatch.fnmatch(cell_name, "CK*MUX2GF*") and

                constr_pin == "S1" and

                constr_pin_dir == "fall" and

                rel_pin == "CLK1" and

                rel_pin_dir == "fall" and

                "CLK2&!S2" in when):

 

        template_name = "nochange/template__ckg__setup__fall__en__fall__pushout__1.sp"

        return template_name

 

    if( arc_type == "nochange_low_low" and

                fnmatch.fnmatch(cell_name, "CK*MUX2GF*") and

                constr_pin == "S1" and

                constr_pin_dir == "rise" and

                rel_pin == "CLK1" and

                rel_pin_dir == "rise" and

                "CLK2&!S2" in when):

 

        template_name = "nochange/template__ckg__hold__rise__en__rise__pushout__negative__1.sp"

        return template_name

 

    if( arc_type == "nochange_high_low" and

                fnmatch.fnmatch(cell_name, "CK*MUX2GF*") and

                constr_pin == "S1" and

                constr_pin_dir == "rise" and

                rel_pin == "CLK1" and

                rel_pin_dir == "fall" and

                "CLK2&!S2" in when):

 

        template_name = "nochange/template__ckg__setup__fall__en__rise__20__percent__glitch__maxq__1.sp"

        return template_name

 

    if( arc_type == "nochange_high_low" and

                fnmatch.fnmatch(cell_name, "CK*MUX2GF*") and

                constr_pin == "S1" and

                constr_pin_dir == "fall" and

                rel_pin == "CLK1" and

                rel_pin_dir == "rise" and

                "CLK2&!S2" in when):

 

        template_name = "nochange/template__ckg__hold__rise__en__fall__20__percent__glitch__maxq__1.sp"

        return template_name

 

    if( arc_type == "nochange_high_high" and

                fnmatch.fnmatch(cell_name, "CK*MUX2GF*") and

                constr_pin == "S2" and

                constr_pin_dir == "rise" and

                rel_pin == "CLK2" and

                rel_pin_dir == "rise" and

                "CLK1&!S1" in when):

 

        template_name = "nochange/template__ckg__setup__rise__en__rise__pushout__1.sp"

        return template_name

 

    if( arc_type == "nochange_high_high" and

                fnmatch.fnmatch(cell_name, "CK*MUX2GF*") and

                constr_pin == "S2" and

                constr_pin_dir == "fall" and

                rel_pin == "CLK2" and

                rel_pin_dir == "fall" and

                "CLK1&!S1" in when):

 

        template_name = "nochange/template__ckg__hold__fall__en__fall__pushout__negative__1.sp"

        return template_name

 

    if( arc_type == "nochange_low_high" and

                fnmatch.fnmatch(cell_name, "CK*MUX2GF*") and

                constr_pin == "S2" and

                constr_pin_dir == "fall" and

                rel_pin == "CLK2" and

                rel_pin_dir == "rise" and

                "CLK1&!S1" in when):

 

        template_name = "nochange/template__ckg__setup__rise__en__fall__20__percent__glitch__minq__1.sp"

        return template_name

 

    if( arc_type == "nochange_low_high" and

                fnmatch.fnmatch(cell_name, "CK*MUX2GF*") and

                constr_pin == "S2" and

                constr_pin_dir == "rise" and

                rel_pin == "CLK2" and

                rel_pin_dir == "fall" and

                "CLK1&!S1" in when):

 

        template_name = "nochange/template__ckg__hold__fall__en__rise__20__percent__glitch__minq__1.sp"

        return template_name

 

    if( arc_type == "nochange_low_low" and

                fnmatch.fnmatch(cell_name, "CK*MUX2GF*") and

                constr_pin == "S2" and

                constr_pin_dir == "fall" and

                rel_pin == "CLK2" and

                rel_pin_dir == "fall" and

                "CLK1&!S1" in when):

 

        template_name = "nochange/template__ckg__setup__fall__en__fall__pushout__1.sp"

        return template_name

 

    if( arc_type == "nochange_low_low" and

                fnmatch.fnmatch(cell_name, "CK*MUX2GF*") and

                constr_pin == "S2" and

                constr_pin_dir == "rise" and

                rel_pin == "CLK2" and

                rel_pin_dir == "rise" and

                "CLK1&!S1" in when):

 

        template_name = "nochange/template__ckg__hold__rise__en__rise__pushout__negative__1.sp"

        return template_name

 

    if( arc_type == "nochange_high_low" and

                fnmatch.fnmatch(cell_name, "CK*MUX2GF*") and

                constr_pin == "S2" and

                constr_pin_dir == "rise" and

                rel_pin == "CLK2" and

                rel_pin_dir == "fall" and

                "CLK1&!S1" in when):

 

        template_name = "nochange/template__ckg__setup__fall__en__rise__20__percent__glitch__maxq__1.sp"

        return template_name

 

    if( arc_type == "nochange_high_low" and

                fnmatch.fnmatch(cell_name, "CK*MUX2GF*") and

                constr_pin == "S2" and

                constr_pin_dir == "fall" and

                rel_pin == "CLK2" and

                rel_pin_dir == "rise" and

                "CLK1&!S1" in when):

 

        template_name = "nochange/template__ckg__hold__rise__en__fall__20__percent__glitch__maxq__1.sp"

        return template_name

    # CKGMUX2* arc add probe preZ from CW 2021/3/4, add probe tgo from CW 2021/3/5

    if( arc_type == "nochange_high_high" and

                (fnmatch.fnmatch(cell_name, "DC*CKG*MUX2*") or fnmatch.fnmatch(cell_name, "CKGMUX2*") or fnmatch.fnmatch(cell_name, "CKG3DMUX2*")) and

                constr_pin == "S" and

                constr_pin_dir == "rise" and

                rel_pin == "I0" and

                rel_pin_dir == "rise" and

                "!I1" in when and

                        ("preZ" in probe_list or "tgo" in probe_list or "iq3" in probe_list or "iq4" in probe_list)):

 

        template_name = "nochange/template__ckgmux2__setup__rise__s__rise__20__percent__glitch__minq__1.sp"

        return template_name

 

    if( arc_type == "nochange_high_high" and

                (fnmatch.fnmatch(cell_name, "DC*CKG*MUX2*") or fnmatch.fnmatch(cell_name, "CKGMUX2*") or fnmatch.fnmatch(cell_name, "CKG3DMUX2*")) and

                constr_pin == "S" and

                constr_pin_dir == "fall" and

                rel_pin == "I0" and

                rel_pin_dir == "fall" and

                "!I1" in when and

                        ("preZ" in probe_list or "tgo" in probe_list or "iq3" in probe_list or "iq4" in probe_list)):

 

        template_name = "nochange/template__ckgmux2__hold__fall__s__fall__20__percent__glitch__minq__1.sp"

        return template_name

 

    if( arc_type == "nochange_high_high" and

                (fnmatch.fnmatch(cell_name, "DC*CKG*MUX2*") or fnmatch.fnmatch(cell_name, "CKGMUX2*") or fnmatch.fnmatch(cell_name, "CKG3DMUX2*")) and

                constr_pin == "I1" and

                constr_pin_dir == "rise" and

                rel_pin == "S" and

                rel_pin_dir == "rise" and

                "I0" in when and

                        ("preZ" in probe_list or "tgo" in probe_list or "iq3" in probe_list or "iq4" in probe_list)):

 

        template_name = "nochange/template__ckgmux2__setup__rise__s__rise__20__percent__glitch__maxq__1.sp"

        return template_name

 

    if( arc_type == "nochange_high_high" and

                (fnmatch.fnmatch(cell_name, "DC*CKG*MUX2*") or fnmatch.fnmatch(cell_name, "CKGMUX2*") or fnmatch.fnmatch(cell_name, "CKG3DMUX2*")) and

                constr_pin == "I1" and

                constr_pin_dir == "fall" and

                rel_pin == "S" and

                rel_pin_dir == "fall" and

                "I0" in when and

                        ("preZ" in probe_list or "tgo" in probe_list or "iq3" in probe_list or "iq4" in probe_list)):

 

        template_name = "nochange/template__ckgmux2__hold__fall__s__fall__20__percent__glitch__maxq__1.sp"

        return template_name

 

    if( arc_type == "nochange_high_low" and

                (fnmatch.fnmatch(cell_name, "DC*CKG*MUX2*") or fnmatch.fnmatch(cell_name, "CKGMUX2*") or fnmatch.fnmatch(cell_name, "CKG3DMUX2*")) and

                constr_pin == "S" and

                constr_pin_dir == "rise" and

                rel_pin == "I0" and

                rel_pin_dir == "fall" and

                "I1" in when and

                        ("preZ" in probe_list or "tgo" in probe_list or "iq3" in probe_list or "iq4" in probe_list)):

 

        template_name = "nochange/template__ckgmux2__setup__fall__s__rise__20__percent__glitch__maxq__1.sp"

        return template_name

 

    if( arc_type == "nochange_high_low" and

                (fnmatch.fnmatch(cell_name, "DC*CKG*MUX2*") or fnmatch.fnmatch(cell_name, "CKGMUX2*") or fnmatch.fnmatch(cell_name, "CKG3DMUX2*")) and

                constr_pin == "S" and

                constr_pin_dir == "fall" and

                rel_pin == "I0" and

                rel_pin_dir == "rise" and

                "I1" in when and

                        ("preZ" in probe_list or "tgo" in probe_list or "iq3" in probe_list or "iq4" in probe_list)):

 

        template_name = "nochange/template__ckgmux2__hold__rise__s__fall__20__percent__glitch__maxq__1.sp"

        return template_name

 

    if( arc_type == "nochange_high_low" and

                (fnmatch.fnmatch(cell_name, "DC*CKG*MUX2*") or fnmatch.fnmatch(cell_name, "CKGMUX2*") or fnmatch.fnmatch(cell_name, "CKG3DMUX2*")) and

                constr_pin == "I0" and

                constr_pin_dir == "rise" and

                rel_pin == "S" and

                rel_pin_dir == "fall" and

                "I1" in when and

                        ("preZ" in probe_list or "tgo" in probe_list or "iq3" in probe_list or "iq4" in probe_list)):

 

        template_name = "nochange/template__ckgmux2__setup__fall__s__rise__20__percent__glitch__maxq__1.sp"

        return template_name

 

    if( arc_type == "nochange_high_low" and

                (fnmatch.fnmatch(cell_name, "DC*CKG*MUX2*") or fnmatch.fnmatch(cell_name, "CKGMUX2*") or fnmatch.fnmatch(cell_name, "CKG3DMUX2*")) and

                constr_pin == "I0" and

                constr_pin_dir == "fall" and

                rel_pin == "S" and

                rel_pin_dir == "rise" and

                "I1" in when and

                        ("preZ" in probe_list or "tgo" in probe_list or "iq3" in probe_list or "iq4" in probe_list)):

 

        template_name = "nochange/template__ckgmux2__hold__rise__s__fall__20__percent__glitch__maxq__1.sp"

        return template_name

 

    if( arc_type == "nochange_low_high" and

                (fnmatch.fnmatch(cell_name, "DC*CKG*MUX2*") or fnmatch.fnmatch(cell_name, "CKGMUX2*") or fnmatch.fnmatch(cell_name, "CKG3DMUX2*")) and

                constr_pin == "S" and

                constr_pin_dir == "fall" and

                rel_pin == "I1" and

                rel_pin_dir == "rise" and

                "!I0" in when and

                        ("preZ" in probe_list or "tgo" in probe_list or "iq3" in probe_list or "iq4" in probe_list)):

 

        template_name = "nochange/template__ckgmux2__setup__rise__s__fall__20__percent__glitch__minq__1.sp"

        return template_name

 

    if( arc_type == "nochange_low_high" and

                (fnmatch.fnmatch(cell_name, "DC*CKG*MUX2*") or fnmatch.fnmatch(cell_name, "CKGMUX2*") or fnmatch.fnmatch(cell_name, "CKG3DMUX2*")) and

                constr_pin == "S" and

                constr_pin_dir == "rise" and

                rel_pin == "I1" and

                rel_pin_dir == "fall" and

                "!I0" in when and

                        ("preZ" in probe_list or "tgo" in probe_list or "iq3" in probe_list or "iq4" in probe_list)):

 

        template_name = "nochange/template__ckgmux2__hold__fall__s__rise__20__percent__glitch__minq__1.sp"

        return template_name

 

    if( arc_type == "nochange_low_high" and

                (fnmatch.fnmatch(cell_name, "DC*CKG*MUX2*") or fnmatch.fnmatch(cell_name, "CKGMUX2*") or fnmatch.fnmatch(cell_name, "CKG3DMUX2*")) and

                constr_pin == "I1" and

                constr_pin_dir == "fall" and

                rel_pin == "S" and

                rel_pin_dir == "rise" and

                "!I0" in when and

                        ("preZ" in probe_list or "tgo" in probe_list or "iq3" in probe_list or "iq4" in probe_list)):

 

        template_name = "nochange/template__ckgmux2__setup__rise__s__fall__20__percent__glitch__minq__1.sp"

        return template_name

 

    if( arc_type == "nochange_low_high" and

                (fnmatch.fnmatch(cell_name, "DC*CKG*MUX2*") or fnmatch.fnmatch(cell_name, "CKGMUX2*") or fnmatch.fnmatch(cell_name, "CKG3DMUX2*")) and

                constr_pin == "I1" and

                constr_pin_dir == "rise" and

                rel_pin == "S" and

                rel_pin_dir == "fall" and

                "!I0" in when and

                        ("preZ" in probe_list or "tgo" in probe_list or "iq3" in probe_list or "iq4" in probe_list)):

 

        template_name = "nochange/template__ckgmux2__hold__fall__s__rise__20__percent__glitch__minq__1.sp"

        return template_name

 

    if( arc_type == "nochange_low_low" and

                (fnmatch.fnmatch(cell_name, "DC*CKG*MUX2*") or fnmatch.fnmatch(cell_name, "CKGMUX2*") or fnmatch.fnmatch(cell_name, "CKG3DMUX2*")) and

                constr_pin == "I0" and

                constr_pin_dir == "fall" and

                rel_pin == "S" and

                rel_pin_dir == "fall" and

                "!I1" in when and

                        ("preZ" in probe_list or "tgo" in probe_list or "iq3" in probe_list or "iq4" in probe_list)):

 

        template_name = "nochange/template__ckgmux2__setup__fall__s__fall__20__percent__glitch__minq__1.sp"

        return template_name

 

    if( arc_type == "nochange_low_low" and

                (fnmatch.fnmatch(cell_name, "DC*CKG*MUX2*") or fnmatch.fnmatch(cell_name, "CKGMUX2*") or fnmatch.fnmatch(cell_name, "CKG3DMUX2*")) and

                constr_pin == "I0" and

                constr_pin_dir == "rise" and

                rel_pin == "S" and

                rel_pin_dir == "rise" and

                "!I1" in when and

                        ("preZ" in probe_list or "tgo" in probe_list or "iq3" in probe_list or "iq4" in probe_list)):

 

        template_name = "nochange/template__ckgmux2__hold__rise__s__rise__20__percent__glitch__minq__1.sp"

        return template_name

 

    if( arc_type == "nochange_low_low" and

                (fnmatch.fnmatch(cell_name, "DC*CKG*MUX2*") or fnmatch.fnmatch(cell_name, "CKGMUX2*") or fnmatch.fnmatch(cell_name, "CKG3DMUX2*")) and

                constr_pin == "S" and

                constr_pin_dir == "fall" and

                rel_pin == "I1" and

                rel_pin_dir == "fall" and

                "I0" in when and

                        ("preZ" in probe_list or "tgo" in probe_list or "iq3" in probe_list or "iq4" in probe_list)):

 

        template_name = "nochange/template__ckgmux2__setup__fall__s__fall__20__percent__glitch__maxq__1.sp"

        return template_name

 

    if( arc_type == "nochange_low_low" and

                (fnmatch.fnmatch(cell_name, "DC*CKG*MUX2*") or fnmatch.fnmatch(cell_name, "CKGMUX2*") or fnmatch.fnmatch(cell_name, "CKG3DMUX2*")) and

                constr_pin == "S" and

                constr_pin_dir == "rise" and

                rel_pin == "I1" and

                rel_pin_dir == "rise" and

                "I0" in when and

                        ("preZ" in probe_list or "tgo" in probe_list or "iq3" in probe_list or "iq4" in probe_list)):

 

        template_name = "nochange/template__ckgmux2__hold__rise__s__rise__20__percent__glitch__maxq__1.sp"

        return template_name

 

    # CKGMUX2* arc from CW 2020/3/5

    if( arc_type == "nochange_high_high" and

                (fnmatch.fnmatch(cell_name, "DC*CKG*MUX2*") or fnmatch.fnmatch(cell_name, "CKGMUX2*") or fnmatch.fnmatch(cell_name, "CKG3DMUX2*")) and

                constr_pin == "I0" and

                constr_pin_dir == "rise" and

                rel_pin == "S" and

                rel_pin_dir == "rise" and

                "I1" in when and

                        ("preZ" in probe_list or "tgo" in probe_list or "iq3" in probe_list or "iq4" in probe_list)):

 

        template_name = "nochange/template__ckgmux2__setup__s__rise__rise__pushout__maxq__1.sp"

        return template_name

 

    if( arc_type == "nochange_high_high" and

                (fnmatch.fnmatch(cell_name, "DC*CKG*MUX2*") or fnmatch.fnmatch(cell_name, "CKGMUX2*") or fnmatch.fnmatch(cell_name, "CKG3DMUX2*")) and

                constr_pin == "I0" and

                constr_pin_dir == "fall" and

                rel_pin == "S" and

                rel_pin_dir == "fall" and

                "I1" in when and

                        ("preZ" in probe_list or "tgo" in probe_list or "iq3" in probe_list or "iq4" in probe_list)):

 

        template_name = "nochange/template__ckgmux2__hold__s__fall__fall__pushout__minq__1.sp"

        return template_name

 

    if( arc_type == "nochange_high_high" and

                (fnmatch.fnmatch(cell_name, "DC*CKG*MUX2*") or fnmatch.fnmatch(cell_name, "CKGMUX2*") or fnmatch.fnmatch(cell_name, "CKG3DMUX2*")) and

                constr_pin == "S" and

                constr_pin_dir == "rise" and

                rel_pin == "I1" and

                rel_pin_dir == "rise" and

                "!I0" in when and

                        ("preZ" in probe_list or "tgo" in probe_list or "iq3" in probe_list or "iq4" in probe_list)):

 

        template_name = "nochange/template__ckgmux2__setup__rise__s__rise__pushout__maxq__1.sp"

        return template_name

 

    if( arc_type == "nochange_high_high" and

                (fnmatch.fnmatch(cell_name, "DC*CKG*MUX2*") or fnmatch.fnmatch(cell_name, "CKGMUX2*") or fnmatch.fnmatch(cell_name, "CKG3DMUX2*")) and

                constr_pin == "S" and

                constr_pin_dir == "fall" and

                rel_pin == "I1" and

                rel_pin_dir == "fall" and

                "!I0" in when and

                        ("preZ" in probe_list or "tgo" in probe_list or "iq3" in probe_list or "iq4" in probe_list)):

 

        template_name = "nochange/template__ckgmux2__hold__fall__s__fall__pushout__minq__1.sp"

        return template_name

 

    if( arc_type == "nochange_high_low" and

                (fnmatch.fnmatch(cell_name, "DC*CKG*MUX2*") or fnmatch.fnmatch(cell_name, "CKGMUX2*") or fnmatch.fnmatch(cell_name, "CKG3DMUX2*")) and

                constr_pin == "S" and

                constr_pin_dir == "rise" and

                rel_pin == "I1" and

                rel_pin_dir == "fall" and

                "I0" in when and

                        ("preZ" in probe_list or "tgo" in probe_list or "iq3" in probe_list or "iq4" in probe_list)):

 

        template_name = "nochange/template__ckgmux2__setup__fall__s__rise__pushout__minq__1.sp"

        return template_name

 

    if( arc_type == "nochange_high_low" and

                (fnmatch.fnmatch(cell_name, "DC*CKG*MUX2*") or fnmatch.fnmatch(cell_name, "CKGMUX2*") or fnmatch.fnmatch(cell_name, "CKG3DMUX2*")) and

                constr_pin == "S" and

                constr_pin_dir == "fall" and

                rel_pin == "I1" and

                rel_pin_dir == "rise" and

                "I0" in when and

                        ("preZ" in probe_list or "tgo" in probe_list or "iq3" in probe_list or "iq4" in probe_list)):

 

        template_name = "nochange/template__ckgmux2__hold__rise__s__fall__pushout__maxq__1.sp"

        return template_name

 

    if( arc_type == "nochange_high_low" and

                (fnmatch.fnmatch(cell_name, "DC*CKG*MUX2*") or fnmatch.fnmatch(cell_name, "CKGMUX2*") or fnmatch.fnmatch(cell_name, "CKG3DMUX2*")) and

                constr_pin == "I1" and

                constr_pin_dir == "rise" and

                rel_pin == "S" and

                rel_pin_dir == "fall" and

                "I0" in when and

                        ("preZ" in probe_list or "tgo" in probe_list or "iq3" in probe_list or "iq4" in probe_list)):

 

        template_name = "nochange/template__ckgmux2__setup__s__fall__rise__pushout__maxq__1.sp"

        return template_name

 

    if( arc_type == "nochange_high_low" and

                (fnmatch.fnmatch(cell_name, "DC*CKG*MUX2*") or fnmatch.fnmatch(cell_name, "CKGMUX2*") or fnmatch.fnmatch(cell_name, "CKG3DMUX2*")) and

                constr_pin == "I1" and

                constr_pin_dir == "fall" and

                rel_pin == "S" and

                rel_pin_dir == "rise" and

                "I0" in when and

                        ("preZ" in probe_list or "tgo" in probe_list or "iq3" in probe_list or "iq4" in probe_list)):

 

        template_name = "nochange/template__ckgmux2__hold__s__rise__fall__pushout__minq__1.sp"

        return template_name

 

    if( arc_type == "nochange_low_high" and

                (fnmatch.fnmatch(cell_name, "DC*CKG*MUX2*") or fnmatch.fnmatch(cell_name, "CKGMUX2*") or fnmatch.fnmatch(cell_name, "CKG3DMUX2*")) and

                constr_pin == "S" and

                constr_pin_dir == "fall" and

                rel_pin == "I0" and

                rel_pin_dir == "rise" and

                "!I1" in when and

                        ("preZ" in probe_list or "tgo" in probe_list or "iq3" in probe_list or "iq4" in probe_list)):

 

        template_name = "nochange/template__ckgmux2__setup__rise__s__fall__pushout__maxq__1.sp"

        return template_name

 

    if( arc_type == "nochange_low_high" and

                (fnmatch.fnmatch(cell_name, "DC*CKG*MUX2*") or fnmatch.fnmatch(cell_name, "CKGMUX2*") or fnmatch.fnmatch(cell_name, "CKG3DMUX2*")) and

                constr_pin == "S" and

                constr_pin_dir == "rise" and

                rel_pin == "I0" and

                rel_pin_dir == "fall" and

                "!I1" in when and

                        ("preZ" in probe_list or "tgo" in probe_list or "iq3" in probe_list or "iq4" in probe_list)):

 

        template_name = "nochange/template__ckgmux2__hold__fall__s__rise__pushout__minq__1.sp"

        return template_name

 

    if( arc_type == "nochange_low_high" and

                (fnmatch.fnmatch(cell_name, "DC*CKG*MUX2*") or fnmatch.fnmatch(cell_name, "CKGMUX2*") or fnmatch.fnmatch(cell_name, "CKG3DMUX2*")) and

                constr_pin == "I0" and

                constr_pin_dir == "fall" and

                rel_pin == "S" and

                rel_pin_dir == "rise" and

                "!I1" in when and

                        ("preZ" in probe_list or "tgo" in probe_list or "iq3" in probe_list or "iq4" in probe_list)):

 

        template_name = "nochange/template__ckgmux2__setup__s__rise__fall__pushout__minq__1.sp"

        return template_name

 

    if( arc_type == "nochange_low_high" and

                (fnmatch.fnmatch(cell_name, "DC*CKG*MUX2*") or fnmatch.fnmatch(cell_name, "CKGMUX2*") or fnmatch.fnmatch(cell_name, "CKG3DMUX2*")) and

                constr_pin == "I0" and

                constr_pin_dir == "rise" and

                rel_pin == "S" and

                rel_pin_dir == "fall" and

                "!I1" in when and

                        ("preZ" in probe_list or "tgo" in probe_list or "iq3" in probe_list or "iq4" in probe_list)):

 

        template_name = "nochange/template__ckgmux2__hold__s__fall__rise__pushout__maxq__1.sp"

        return template_name

 

    if( arc_type == "nochange_low_low" and

                (fnmatch.fnmatch(cell_name, "DC*CKG*MUX2*") or fnmatch.fnmatch(cell_name, "CKGMUX2*") or fnmatch.fnmatch(cell_name, "CKG3DMUX2*")) and

                constr_pin == "S" and

                constr_pin_dir == "fall" and

                rel_pin == "I0" and

                rel_pin_dir == "fall" and

                "I1" in when and

                        ("preZ" in probe_list or "tgo" in probe_list or "iq3" in probe_list or "iq4" in probe_list)):

 

        template_name = "nochange/template__ckgmux2__setup__fall__s__fall__pushout__minq__1.sp"

        return template_name

 

    if( arc_type == "nochange_low_low" and

                (fnmatch.fnmatch(cell_name, "DC*CKG*MUX2*") or fnmatch.fnmatch(cell_name, "CKGMUX2*") or fnmatch.fnmatch(cell_name, "CKG3DMUX2*")) and

                constr_pin == "S" and

                constr_pin_dir == "rise" and

                rel_pin == "I0" and

                rel_pin_dir == "rise" and

                "I1" in when and

                        ("preZ" in probe_list or "tgo" in probe_list or "iq3" in probe_list or "iq4" in probe_list)):

 

        template_name = "nochange/template__ckgmux2__hold__rise__s__rise__pushout__maxq__1.sp"

        return template_name

 

    if( arc_type == "nochange_low_low" and

                (fnmatch.fnmatch(cell_name, "DC*CKG*MUX2*") or fnmatch.fnmatch(cell_name, "CKGMUX2*") or fnmatch.fnmatch(cell_name, "CKG3DMUX2*")) and

                constr_pin == "I1" and

                constr_pin_dir == "fall" and

                rel_pin == "S" and

                rel_pin_dir == "fall" and

                "!I0" in when and

                        ("preZ" in probe_list or "tgo" in probe_list or "iq3" in probe_list or "iq4" in probe_list)):

 

        template_name = "nochange/template__ckgmux2__setup__s__fall__fall__pushout__minq__1.sp"

        return template_name

 

    if( arc_type == "nochange_low_low" and

                (fnmatch.fnmatch(cell_name, "DC*CKG*MUX2*") or fnmatch.fnmatch(cell_name, "CKGMUX2*") or fnmatch.fnmatch(cell_name, "CKG3DMUX2*")) and

                constr_pin == "I1" and

                constr_pin_dir == "rise" and

                rel_pin == "S" and

                rel_pin_dir == "rise" and

                "!I0" in when and

                        ("preZ" in probe_list or "tgo" in probe_list or "iq3" in probe_list or "iq4" in probe_list)):

 

        template_name = "nochange/template__ckgmux2__hold__s__rise__rise__pushout__maxq__1.sp"

        return template_name

 

 

    # CKGMUX2* arc from CW 2020/9/24

    if( arc_type == "nochange_high_high" and

                (fnmatch.fnmatch(cell_name, "DC*CKG*MUX2*") or fnmatch.fnmatch(cell_name, "CKGMUX2*") or fnmatch.fnmatch(cell_name, "CKG3DMUX2*")) and

                constr_pin == "S" and

                constr_pin_dir == "rise" and

                rel_pin == "I0" and

                rel_pin_dir == "rise" and

                "!I1" in when):

 

        template_name = "nochange/template__ckgmux2__setup__rise__s__rise__20__percent__glitch__maxq__1.sp"

        return template_name

 

    if( arc_type == "nochange_high_high" and

                (fnmatch.fnmatch(cell_name, "DC*CKG*MUX2*") or fnmatch.fnmatch(cell_name, "CKGMUX2*") or fnmatch.fnmatch(cell_name, "CKG3DMUX2*")) and

                constr_pin == "S" and

                constr_pin_dir == "fall" and

                rel_pin == "I0" and

                rel_pin_dir == "fall" and

                "!I1" in when):

 

        template_name = "nochange/template__ckgmux2__hold__fall__s__fall__20__percent__glitch__maxq__1.sp"

        return template_name

 

    if( arc_type == "nochange_high_high" and

                (fnmatch.fnmatch(cell_name, "DC*CKG*MUX2*") or fnmatch.fnmatch(cell_name, "CKGMUX2*") or fnmatch.fnmatch(cell_name, "CKG3DMUX2*")) and

                constr_pin == "I0" and

                constr_pin_dir == "rise" and

                rel_pin == "S" and

                rel_pin_dir == "rise" and

                "I1" in when):

 

        template_name = "nochange/template__ckgmux2__setup__s__rise__rise__pushout__1.sp"

        return template_name

 

    if( arc_type == "nochange_high_high" and

                (fnmatch.fnmatch(cell_name, "DC*CKG*MUX2*") or fnmatch.fnmatch(cell_name, "CKGMUX2*") or fnmatch.fnmatch(cell_name, "CKG3DMUX2*")) and

                constr_pin == "I0" and

                constr_pin_dir == "fall" and

                rel_pin == "S" and

                rel_pin_dir == "fall" and

                "I1" in when):

 

        template_name = "nochange/template__ckgmux2__hold__s__fall__fall__pushout__1.sp"

        return template_name

 

    if( arc_type == "nochange_high_high" and

                (fnmatch.fnmatch(cell_name, "DC*CKG*MUX2*") or fnmatch.fnmatch(cell_name, "CKGMUX2*") or fnmatch.fnmatch(cell_name, "CKG3DMUX2*")) and

                constr_pin == "S" and

                constr_pin_dir == "rise" and

                rel_pin == "I1" and

                rel_pin_dir == "rise" and

                "!I0" in when):

 

        template_name = "nochange/template__ckgmux2__setup__rise__s__rise__pushout__1.sp"

        return template_name

 

    if( arc_type == "nochange_high_high" and

                (fnmatch.fnmatch(cell_name, "DC*CKG*MUX2*") or fnmatch.fnmatch(cell_name, "CKGMUX2*") or fnmatch.fnmatch(cell_name, "CKG3DMUX2*")) and

                constr_pin == "S" and

                constr_pin_dir == "fall" and

                rel_pin == "I1" and

                rel_pin_dir == "fall" and

                "!I0" in when):

 

        template_name = "nochange/template__ckgmux2__hold__fall__s__fall__pushout__1.sp"

        return template_name

 

    if( arc_type == "nochange_high_high" and

                (fnmatch.fnmatch(cell_name, "DC*CKG*MUX2*") or fnmatch.fnmatch(cell_name, "CKGMUX2*") or fnmatch.fnmatch(cell_name, "CKG3DMUX2*")) and

                constr_pin == "I1" and

                constr_pin_dir == "rise" and

                rel_pin == "S" and

                rel_pin_dir == "rise" and

                "I0" in when):

 

        template_name = "nochange/template__ckgmux2__setup__rise__s__rise__20__percent__glitch__minq__1.sp"

        return template_name

 

    if( arc_type == "nochange_high_high" and

                (fnmatch.fnmatch(cell_name, "DC*CKG*MUX2*") or fnmatch.fnmatch(cell_name, "CKGMUX2*") or fnmatch.fnmatch(cell_name, "CKG3DMUX2*")) and

                constr_pin == "I1" and

                constr_pin_dir == "fall" and

                rel_pin == "S" and

                rel_pin_dir == "fall" and

                "I0" in when):

 

        template_name = "nochange/template__ckgmux2__hold__fall__s__fall__20__percent__glitch__minq__1.sp"

        return template_name

 

    if( arc_type == "nochange_high_low" and

                (fnmatch.fnmatch(cell_name, "DC*CKG*MUX2*") or fnmatch.fnmatch(cell_name, "CKGMUX2*") or fnmatch.fnmatch(cell_name, "CKG3DMUX2*")) and

                constr_pin == "S" and

                constr_pin_dir == "rise" and

                rel_pin == "I0" and

                rel_pin_dir == "fall" and

                "I1" in when):

 

        template_name = "nochange/template__ckgmux2__setup__fall__s__rise__20__percent__glitch__minq__1.sp"

        return template_name

 

    if( arc_type == "nochange_high_low" and

                (fnmatch.fnmatch(cell_name, "DC*CKG*MUX2*") or fnmatch.fnmatch(cell_name, "CKGMUX2*") or fnmatch.fnmatch(cell_name, "CKG3DMUX2*")) and

                constr_pin == "S" and

                constr_pin_dir == "fall" and

                rel_pin == "I0" and

                rel_pin_dir == "rise" and

                "I1" in when):

 

        template_name = "nochange/template__ckgmux2__hold__rise__s__fall__20__percent__glitch__minq__1.sp"

        return template_name

 

    if( arc_type == "nochange_high_low" and

                (fnmatch.fnmatch(cell_name, "DC*CKG*MUX2*") or fnmatch.fnmatch(cell_name, "CKGMUX2*") or fnmatch.fnmatch(cell_name, "CKG3DMUX2*")) and

                constr_pin == "I0" and

                constr_pin_dir == "rise" and

                rel_pin == "S" and

                rel_pin_dir == "fall" and

                "I1" in when):

 

        template_name = "nochange/template__ckgmux2__setup__fall__s__rise__20__percent__glitch__minq__1.sp"

        return template_name

 

    if( arc_type == "nochange_high_low" and

                (fnmatch.fnmatch(cell_name, "DC*CKG*MUX2*") or fnmatch.fnmatch(cell_name, "CKGMUX2*") or fnmatch.fnmatch(cell_name, "CKG3DMUX2*")) and

                constr_pin == "I0" and

                constr_pin_dir == "fall" and

                rel_pin == "S" and

                rel_pin_dir == "rise" and

                "I1" in when):

 

        template_name = "nochange/template__ckgmux2__hold__rise__s__fall__20__percent__glitch__minq__1.sp"

        return template_name

 

    if( arc_type == "nochange_high_low" and

                (fnmatch.fnmatch(cell_name, "DC*CKG*MUX2*") or fnmatch.fnmatch(cell_name, "CKGMUX2*") or fnmatch.fnmatch(cell_name, "CKG3DMUX2*")) and

                constr_pin == "S" and

                constr_pin_dir == "rise" and

                rel_pin == "I1" and

                rel_pin_dir == "fall" and

                "I0" in when):

 

        template_name = "nochange/template__ckgmux2__setup__fall__s__rise__pushout__1.sp"

        return template_name

 

    if( arc_type == "nochange_high_low" and

                (fnmatch.fnmatch(cell_name, "DC*CKG*MUX2*") or fnmatch.fnmatch(cell_name, "CKGMUX2*") or fnmatch.fnmatch(cell_name, "CKG3DMUX2*")) and

                constr_pin == "S" and

                constr_pin_dir == "fall" and

                rel_pin == "I1" and

                rel_pin_dir == "rise" and

                "I0" in when):

 

        template_name = "nochange/template__ckgmux2__hold__rise__s__fall__pushout__1.sp"

        return template_name

 

    if( arc_type == "nochange_high_low" and

                (fnmatch.fnmatch(cell_name, "DC*CKG*MUX2*") or fnmatch.fnmatch(cell_name, "CKGMUX2*") or fnmatch.fnmatch(cell_name, "CKG3DMUX2*")) and

                constr_pin == "I1" and

                constr_pin_dir == "rise" and

                rel_pin == "S" and

                rel_pin_dir == "fall" and

                "I0" in when):

 

        template_name = "nochange/template__ckgmux2__setup__s__fall__rise__pushout__1.sp"

        return template_name

 

    if( arc_type == "nochange_high_low" and

                (fnmatch.fnmatch(cell_name, "DC*CKG*MUX2*") or fnmatch.fnmatch(cell_name, "CKGMUX2*") or fnmatch.fnmatch(cell_name, "CKG3DMUX2*")) and

                constr_pin == "I1" and

                constr_pin_dir == "fall" and

                rel_pin == "S" and

                rel_pin_dir == "rise" and

                "I0" in when):

 

        template_name = "nochange/template__ckgmux2__hold__s__rise__fall__pushout__1.sp"

        return template_name

 

    if( arc_type == "nochange_low_high" and

                (fnmatch.fnmatch(cell_name, "DC*CKG*MUX2*") or fnmatch.fnmatch(cell_name, "CKGMUX2*") or fnmatch.fnmatch(cell_name, "CKG3DMUX2*")) and

                constr_pin == "S" and

                constr_pin_dir == "fall" and

                rel_pin == "I0" and

                rel_pin_dir == "rise" and

                "!I1" in when):

 

        template_name = "nochange/template__ckgmux2__setup__rise__s__fall__pushout__1.sp"

        return template_name

 

    if( arc_type == "nochange_low_high" and

                (fnmatch.fnmatch(cell_name, "DC*CKG*MUX2*") or fnmatch.fnmatch(cell_name, "CKGMUX2*") or fnmatch.fnmatch(cell_name, "CKG3DMUX2*")) and

                constr_pin == "S" and

                constr_pin_dir == "rise" and

                rel_pin == "I0" and

                rel_pin_dir == "fall" and

                "!I1" in when):

 

        template_name = "nochange/template__ckgmux2__hold__fall__s__rise__pushout__1.sp"

        return template_name

 

    if( arc_type == "nochange_low_high" and

                (fnmatch.fnmatch(cell_name, "DC*CKG*MUX2*") or fnmatch.fnmatch(cell_name, "CKGMUX2*") or fnmatch.fnmatch(cell_name, "CKG3DMUX2*")) and

                constr_pin == "I0" and

                constr_pin_dir == "fall" and

                rel_pin == "S" and

                rel_pin_dir == "rise" and

                "!I1" in when):

 

        template_name = "nochange/template__ckgmux2__setup__s__rise__fall__pushout__1.sp"

        return template_name

 

    if( arc_type == "nochange_low_high" and

                (fnmatch.fnmatch(cell_name, "DC*CKG*MUX2*") or fnmatch.fnmatch(cell_name, "CKGMUX2*") or fnmatch.fnmatch(cell_name, "CKG3DMUX2*")) and

                constr_pin == "I0" and

                constr_pin_dir == "rise" and

                rel_pin == "S" and

                rel_pin_dir == "fall" and

                "!I1" in when):

 

        template_name = "nochange/template__ckgmux2__hold__s__fall__rise__pushout__1.sp"

        return template_name

 

    if( arc_type == "nochange_low_high" and

                (fnmatch.fnmatch(cell_name, "DC*CKG*MUX2*") or fnmatch.fnmatch(cell_name, "CKGMUX2*") or fnmatch.fnmatch(cell_name, "CKG3DMUX2*")) and

                constr_pin == "S" and

                constr_pin_dir == "fall" and

                rel_pin == "I1" and

                rel_pin_dir == "rise" and

                "!I0" in when):

 

        template_name = "nochange/template__ckgmux2__setup__rise__s__fall__20__percent__glitch__maxq__1.sp"

        return template_name

 

    if( arc_type == "nochange_low_high" and

                (fnmatch.fnmatch(cell_name, "DC*CKG*MUX2*") or fnmatch.fnmatch(cell_name, "CKGMUX2*") or fnmatch.fnmatch(cell_name, "CKG3DMUX2*")) and

                constr_pin == "S" and

                constr_pin_dir == "rise" and

                rel_pin == "I1" and

                rel_pin_dir == "fall" and

                "!I0" in when):

 

        template_name = "nochange/template__ckgmux2__hold__fall__s__rise__20__percent__glitch__maxq__1.sp"

        return template_name

 

    if( arc_type == "nochange_low_high" and

                (fnmatch.fnmatch(cell_name, "DC*CKG*MUX2*") or fnmatch.fnmatch(cell_name, "CKGMUX2*") or fnmatch.fnmatch(cell_name, "CKG3DMUX2*")) and

                constr_pin == "I1" and

                constr_pin_dir == "fall" and

                rel_pin == "S" and

                rel_pin_dir == "rise" and

                "!I0" in when):

 

        template_name = "nochange/template__ckgmux2__setup__rise__s__fall__20__percent__glitch__maxq__1.sp"

        return template_name

 

    if( arc_type == "nochange_low_high" and

                (fnmatch.fnmatch(cell_name, "DC*CKG*MUX2*") or fnmatch.fnmatch(cell_name, "CKGMUX2*") or fnmatch.fnmatch(cell_name, "CKG3DMUX2*")) and

                constr_pin == "I1" and

                constr_pin_dir == "rise" and

                rel_pin == "S" and

                rel_pin_dir == "fall" and

                "!I0" in when):

 

        template_name = "nochange/template__ckgmux2__hold__fall__s__rise__20__percent__glitch__maxq__1.sp"

        return template_name

 

    if( arc_type == "nochange_low_low" and

                (fnmatch.fnmatch(cell_name, "DC*CKG*MUX2*") or fnmatch.fnmatch(cell_name, "CKGMUX2*") or fnmatch.fnmatch(cell_name, "CKG3DMUX2*")) and

                constr_pin == "S" and

                constr_pin_dir == "fall" and

                rel_pin == "I0" and

                rel_pin_dir == "fall" and

                "I1" in when):

 

        template_name = "nochange/template__ckgmux2__setup__fall__s__fall__pushout__1.sp"

        return template_name

 

    if( arc_type == "nochange_low_low" and

                (fnmatch.fnmatch(cell_name, "DC*CKG*MUX2*") or fnmatch.fnmatch(cell_name, "CKGMUX2*") or fnmatch.fnmatch(cell_name, "CKG3DMUX2*")) and

                constr_pin == "S" and

                constr_pin_dir == "rise" and

                rel_pin == "I0" and

                rel_pin_dir == "rise" and

                "I1" in when):

 

        template_name = "nochange/template__ckgmux2__hold__rise__s__rise__pushout__1.sp"

        return template_name

 

    if( arc_type == "nochange_low_low" and

                (fnmatch.fnmatch(cell_name, "DC*CKG*MUX2*") or fnmatch.fnmatch(cell_name, "CKGMUX2*") or fnmatch.fnmatch(cell_name, "CKG3DMUX2*")) and

                constr_pin == "I0" and

                constr_pin_dir == "fall" and

                rel_pin == "S" and

                rel_pin_dir == "fall" and

                "!I1" in when):

 

        template_name = "nochange/template__ckgmux2__setup__fall__s__fall__20__percent__glitch__maxq__1.sp"

        return template_name

 

    if( arc_type == "nochange_low_low" and

                (fnmatch.fnmatch(cell_name, "DC*CKG*MUX2*") or fnmatch.fnmatch(cell_name, "CKGMUX2*") or fnmatch.fnmatch(cell_name, "CKG3DMUX2*")) and

                constr_pin == "I0" and

                constr_pin_dir == "rise" and

                rel_pin == "S" and

                rel_pin_dir == "rise" and

                "!I1" in when):

 

        template_name = "nochange/template__ckgmux2__hold__rise__s__rise__20__percent__glitch__maxq__1.sp"

        return template_name

 

    if( arc_type == "nochange_low_low" and

                (fnmatch.fnmatch(cell_name, "DC*CKG*MUX2*") or fnmatch.fnmatch(cell_name, "CKGMUX2*") or fnmatch.fnmatch(cell_name, "CKG3DMUX2*")) and

                constr_pin == "S" and

                constr_pin_dir == "fall" and

                rel_pin == "I1" and

                rel_pin_dir == "fall" and

                "I0" in when):

 

        template_name = "nochange/template__ckgmux2__setup__fall__s__fall__20__percent__glitch__minq__1.sp"

        return template_name

 

    if( arc_type == "nochange_low_low" and

                (fnmatch.fnmatch(cell_name, "DC*CKG*MUX2*") or fnmatch.fnmatch(cell_name, "CKGMUX2*") or fnmatch.fnmatch(cell_name, "CKG3DMUX2*")) and

                constr_pin == "S" and

                constr_pin_dir == "rise" and

                rel_pin == "I1" and

                rel_pin_dir == "rise" and

                "I0" in when):

 

        template_name = "nochange/template__ckgmux2__hold__rise__s__rise__20__percent__glitch__minq__1.sp"

        return template_name

 

    if( arc_type == "nochange_low_low" and

                (fnmatch.fnmatch(cell_name, "DC*CKG*MUX2*") or fnmatch.fnmatch(cell_name, "CKGMUX2*") or fnmatch.fnmatch(cell_name, "CKG3DMUX2*")) and

                constr_pin == "I1" and

                constr_pin_dir == "fall" and

                rel_pin == "S" and

                rel_pin_dir == "fall" and

                "!I0" in when):

 

        template_name = "nochange/template__ckgmux2__setup__s__fall__fall__pushout__1.sp"

        return template_name

 

    if( arc_type == "nochange_low_low" and

                (fnmatch.fnmatch(cell_name, "DC*CKG*MUX2*") or fnmatch.fnmatch(cell_name, "CKGMUX2*") or fnmatch.fnmatch(cell_name, "CKG3DMUX2*")) and

                constr_pin == "I1" and

                constr_pin_dir == "rise" and

                rel_pin == "S" and

                rel_pin_dir == "rise" and

                "!I0" in when):

 

        template_name = "nochange/template__ckgmux2__hold__s__rise__rise__pushout__1.sp"

        return template_name

 

    # CK*MUX2 arc from CW 1209 => 12/17 update all

    if( arc_type == "nochange_high_high" and

                fnmatch.fnmatch(cell_name, "DC*CK*AOMUX2*") and

                constr_pin == "S1" and

                constr_pin_dir == "rise" and

                (rel_pin == "CP1" or rel_pin == "CLK1") and

                rel_pin_dir == "rise"):

 

        template_name = "nochange/template__ckg__setup__rise__en__rise__pushout__1.sp"

        return template_name

 

    if( arc_type == "nochange_high_high" and

                fnmatch.fnmatch(cell_name, "DC*CK*AOMUX2*") and

                constr_pin == "S1" and

                constr_pin_dir == "fall" and

                (rel_pin == "CP1" or rel_pin == "CLK1") and

                rel_pin_dir == "fall"):

 

        template_name = "nochange/template__ckg__hold__fall__en__fall__pushout__negative__1.sp"

        return template_name

 

    if( arc_type == "nochange_low_high" and

                fnmatch.fnmatch(cell_name, "DC*CK*AOMUX2*") and

                constr_pin == "S1" and

                constr_pin_dir == "fall" and

                (rel_pin == "CP1" or rel_pin == "CLK1") and

                rel_pin_dir == "rise"):

 

        template_name = "nochange/template__ckg__setup__rise__en__fall__20__percent__glitch__minq__1.sp"

        return template_name

 

    if( arc_type == "nochange_low_high" and

                fnmatch.fnmatch(cell_name, "DC*CK*AOMUX2*") and

                constr_pin == "S1" and

                constr_pin_dir == "rise" and

                (rel_pin == "CP1" or rel_pin == "CLK1") and

                rel_pin_dir == "fall"):

 

        template_name = "nochange/template__ckg__hold__fall__en__rise__20__percent__glitch__minq__1.sp"

        return template_name

 

    if( arc_type == "nochange_high_high" and

                fnmatch.fnmatch(cell_name, "DC*CKAOMUX2*") and

                constr_pin == "S2" and

                constr_pin_dir == "rise" and

                rel_pin == "CP2" and

                rel_pin_dir == "rise"):

 

        template_name = "nochange/template__ckg__setup__rise__en__rise__pushout__1.sp"

        return template_name

 

    if( arc_type == "nochange_high_high" and

                fnmatch.fnmatch(cell_name, "DC*CKAOMUX2*") and

                constr_pin == "S2" and

                constr_pin_dir == "fall" and

                rel_pin == "CP2" and

                rel_pin_dir == "fall"):

 

        template_name = "nochange/template__ckg__hold__fall__en__fall__pushout__negative__1.sp"

        return template_name

 

    if( arc_type == "nochange_low_high" and

                fnmatch.fnmatch(cell_name, "DC*CKAOMUX2*") and

                constr_pin == "S2" and

                constr_pin_dir == "fall" and

                rel_pin == "CP2" and

                rel_pin_dir == "rise"):

 

        template_name = "nochange/template__ckg__setup__rise__en__fall__20__percent__glitch__minq__1.sp"

        return template_name

 

    if( arc_type == "nochange_low_high" and

                fnmatch.fnmatch(cell_name, "DC*CKAOMUX2*") and

                constr_pin == "S2" and

                constr_pin_dir == "rise" and

                rel_pin == "CP2" and

                rel_pin_dir == "fall"):

 

        template_name = "nochange/template__ckg__hold__fall__en__rise__20__percent__glitch__minq__1.sp"

        return template_name

 

    if( arc_type == "nochange_high_high" and

                (fnmatch.fnmatch(cell_name, "DC*CKPGMUX2*") or fnmatch.fnmatch(cell_name, "CKPGMUX2*")) and

                constr_pin == "S" and

                constr_pin_dir == "rise" and

                rel_pin == "CP1" and

                rel_pin_dir == "rise"):

 

        template_name = "nochange/template__ckgmux2__setup__rise__s__rise__20__percent__glitch__minq__1.sp"

        return template_name

 

    if( arc_type == "nochange_high_high" and

                (fnmatch.fnmatch(cell_name, "DC*CKPGMUX2*") or fnmatch.fnmatch(cell_name, "CKPGMUX2*")) and

                constr_pin == "S" and

                constr_pin_dir == "fall" and

                rel_pin == "CP1" and

                rel_pin_dir == "fall"):

 

        template_name = "nochange/template__ckgmux2__hold__fall__s__fall__20__percent__glitch__minq__1.sp"

        return template_name

 

    if( arc_type == "nochange_low_high" and

                (fnmatch.fnmatch(cell_name, "DC*CKPGMUX2*") or fnmatch.fnmatch(cell_name, "CKPGMUX2*")) and

                constr_pin == "S" and

                constr_pin_dir == "fall" and

                rel_pin == "CP1" and

                rel_pin_dir == "rise"):

 

        template_name = "nochange/template__ckgmux2__setup__rise__s__fall__pushout__1.sp"

        return template_name

 

    if( arc_type == "nochange_low_high" and

                (fnmatch.fnmatch(cell_name, "DC*CKPGMUX2*") or fnmatch.fnmatch(cell_name, "CKPGMUX2*")) and

                constr_pin == "S" and

                constr_pin_dir == "rise" and

                rel_pin == "CP1" and

                rel_pin_dir == "fall"):

 

        template_name = "nochange/template__ckgmux2__hold__fall__s__rise__pushout__1.sp"

        return template_name

 

    if( arc_type == "nochange_high_high" and

                (fnmatch.fnmatch(cell_name, "DC*CKPGMUX2*") or fnmatch.fnmatch(cell_name, "CKPGMUX2*")) and

                constr_pin == "S" and

                constr_pin_dir == "rise" and

                rel_pin == "CP2" and

                rel_pin_dir == "rise"):

 

        template_name = "nochange/template__ckgmux2__setup__rise__s__rise__pushout__1.sp"

        return template_name

 

    if( arc_type == "nochange_high_high" and

                (fnmatch.fnmatch(cell_name, "DC*CKPGMUX2*") or fnmatch.fnmatch(cell_name, "CKPGMUX2*")) and

                constr_pin == "S" and

                constr_pin_dir == "fall" and

                rel_pin == "CP2" and

                rel_pin_dir == "fall"):

 

        template_name = "nochange/template__ckgmux2__hold__fall__s__fall__pushout__1.sp"

        return template_name

 

    if( arc_type == "nochange_low_high" and

                (fnmatch.fnmatch(cell_name, "DC*CKPGMUX2*") or fnmatch.fnmatch(cell_name, "CKPGMUX2*")) and

                constr_pin == "S" and

                constr_pin_dir == "fall" and

                rel_pin == "CP2" and

                rel_pin_dir == "rise"):

 

        template_name = "nochange/template__ckgmux2__setup__rise__s__fall__20__percent__glitch__minq__1.sp"

        return template_name

 

    if( arc_type == "nochange_low_high" and

                (fnmatch.fnmatch(cell_name, "DC*CKPGMUX2*") or fnmatch.fnmatch(cell_name, "CKPGMUX2*")) and

                constr_pin == "S" and

                constr_pin_dir == "rise" and

                rel_pin == "CP2" and

                rel_pin_dir == "fall"):

 

        template_name = "nochange/template__ckgmux2__hold__fall__s__rise__20__percent__glitch__minq__1.sp"

        return template_name

 

    if( arc_type == "nochange_low_low" and

                (fnmatch.fnmatch(cell_name, "DC*CKPGMUX2*") or fnmatch.fnmatch(cell_name, "CKPGMUX2*")) and

                constr_pin == "S" and

                constr_pin_dir == "fall" and

                rel_pin == "CP1" and

                rel_pin_dir == "fall"):

 

        template_name = "nochange/template__ckgmux2__setup__fall__s__fall__pushout__1.sp"

        return template_name

 

    if( arc_type == "nochange_low_low" and

                (fnmatch.fnmatch(cell_name, "DC*CKPGMUX2*") or fnmatch.fnmatch(cell_name, "CKPGMUX2*")) and

                constr_pin == "S" and

                constr_pin_dir == "fall" and

                rel_pin == "CP2" and

                rel_pin_dir == "fall"):

 

        template_name = "nochange/template__ckgmux2__setup__fall__s__fall__20__percent__glitch__maxq__1.sp"

        return template_name

 

    if( arc_type == "nochange_low_low" and

                (fnmatch.fnmatch(cell_name, "DC*CKPGMUX2*") or fnmatch.fnmatch(cell_name, "CKPGMUX2*")) and

                constr_pin == "S" and

                constr_pin_dir == "rise" and

                rel_pin == "CP1" and

                rel_pin_dir == "rise"):

 

        template_name = "nochange/template__ckgmux2__hold__rise__s__rise__pushout__1.sp"

        return template_name

 

    if( arc_type == "nochange_low_low" and

                (fnmatch.fnmatch(cell_name, "DC*CKPGMUX2*") or fnmatch.fnmatch(cell_name, "CKPGMUX2*")) and

                constr_pin == "S" and

                constr_pin_dir == "rise" and

                rel_pin == "CP2" and

                rel_pin_dir == "rise"):

 

        template_name = "nochange/template__ckgmux2__hold__rise__s__rise__20__percent__glitch__maxq__1.sp"

        return template_name

 

    if( arc_type == "nochange_high_low" and

                (fnmatch.fnmatch(cell_name, "DC*CKPGMUX2*") or fnmatch.fnmatch(cell_name, "CKPGMUX2*")) and

                constr_pin == "S" and

                constr_pin_dir == "rise" and

                rel_pin == "CP1" and

                rel_pin_dir == "fall"):

 

        template_name = "nochange/template__ckgmux2__setup__fall__s__rise__20__percent__glitch__maxq__1.sp"

        return template_name

 

    if( arc_type == "nochange_high_low" and

                (fnmatch.fnmatch(cell_name, "DC*CKPGMUX2*") or fnmatch.fnmatch(cell_name, "CKPGMUX2*")) and

                constr_pin == "S" and

                constr_pin_dir == "rise" and

                rel_pin == "CP2" and

                rel_pin_dir == "fall"):

 

        template_name = "nochange/template__ckgmux2__setup__fall__s__rise__pushout__1.sp"

        return template_name

 

    if( arc_type == "nochange_high_low" and

                (fnmatch.fnmatch(cell_name, "DC*CKPGMUX2*") or fnmatch.fnmatch(cell_name, "CKPGMUX2*")) and

                constr_pin == "S" and

                constr_pin_dir == "fall" and

                rel_pin == "CP1" and

                rel_pin_dir == "rise"):

 

        template_name = "nochange/template__ckgmux2__hold__rise__s__fall__20__percent__glitch__maxq__1.sp"

        return template_name

 

    if( arc_type == "nochange_high_low" and

                (fnmatch.fnmatch(cell_name, "DC*CKPGMUX2*") or fnmatch.fnmatch(cell_name, "CKPGMUX2*")) and

                constr_pin == "S" and

                constr_pin_dir == "fall" and

                rel_pin == "CP2" and

                rel_pin_dir == "rise"):

 

        template_name = "nochange/template__ckgmux2__hold__rise__s__fall__pushout__1.sp"

        return template_name

 

    # CKGMUX3* arc from CW 2021/1/28

    if( arc_type == "nochange_high_high" and

                fnmatch.fnmatch(cell_name, "CKGMUX3*") and

                        (constr_pin == "S0" or constr_pin == "S1") and

                constr_pin_dir == "fall" and

                rel_pin == "I0" and

                rel_pin_dir == "fall"):

 

        template_name = "nochange/template__ckgmux3__hold__fall__s__fall__10__percent__glitch__minq__1.sp"

        return template_name

 

    if( arc_type == "nochange_high_high" and

                fnmatch.fnmatch(cell_name, "CKGMUX3*") and

                        constr_pin == "S1" and

                constr_pin_dir == "fall" and

                rel_pin == "I1" and

                rel_pin_dir == "fall"):

 

        template_name = "nochange/template__ckgmux3__hold__fall__s__fall__10__percent__glitch__minq__1.sp"

        return template_name

 

    if( arc_type == "nochange_high_high" and

                fnmatch.fnmatch(cell_name, "CKGMUX3*") and

                constr_pin == "S0" and

                constr_pin_dir == "fall" and

                rel_pin == "I1" and

                rel_pin_dir == "fall"):

 

        template_name = "nochange/template__ckgmux2__hold__fall__s__fall__pushout__1.sp"

        return template_name

 

    if( arc_type == "nochange_high_high" and

                fnmatch.fnmatch(cell_name, "CKGMUX3*") and

                constr_pin == "S1" and

                constr_pin_dir == "fall" and

                rel_pin == "I2" and

                rel_pin_dir == "fall"):

 

        template_name = "nochange/template__ckgmux2__hold__fall__s__fall__pushout__1.sp"

        return template_name

 

    if( arc_type == "nochange_high_high" and

                fnmatch.fnmatch(cell_name, "CKGMUX3*") and

                (constr_pin == "S0" or constr_pin == "S1") and

                constr_pin_dir == "rise" and

                rel_pin == "I0" and

                rel_pin_dir == "rise"):

 

        template_name = "nochange/template__ckgmux3__setup__rise__s__rise__10__percent__glitch__minq__1.sp"

        return template_name

 

    if( arc_type == "nochange_high_high" and

                fnmatch.fnmatch(cell_name, "CKGMUX3*") and

                constr_pin == "S1" and

                constr_pin_dir == "rise" and

                rel_pin == "I1" and

                rel_pin_dir == "rise"):

 

        template_name = "nochange/template__ckgmux3__setup__rise__s__rise__10__percent__glitch__minq__1.sp"

        return template_name

 

    if( arc_type == "nochange_high_high" and

                fnmatch.fnmatch(cell_name, "CKGMUX3*") and

                constr_pin == "S0" and

                constr_pin_dir == "rise" and

                rel_pin == "I1" and

                rel_pin_dir == "rise"):

 

        template_name = "nochange/template__ckgmux2__setup__rise__s__rise__pushout__1.sp"

        return template_name

 

    if( arc_type == "nochange_high_high" and

                fnmatch.fnmatch(cell_name, "CKGMUX3*") and

                constr_pin == "S1" and

                constr_pin_dir == "rise" and

                rel_pin == "I2" and

                rel_pin_dir == "rise"):

 

        template_name = "nochange/template__ckgmux2__setup__rise__s__rise__pushout__1.sp"

        return template_name

 

    if( arc_type == "nochange_low_high" and

                fnmatch.fnmatch(cell_name, "CKGMUX3*") and

                (constr_pin == "S0" or constr_pin == "S1") and

                constr_pin_dir == "fall" and

                rel_pin == "I0" and

                rel_pin_dir == "rise"):

 

        template_name = "nochange/template__ckgmux2__setup__rise__s__fall__pushout__1.sp"

        return template_name

 

    if( arc_type == "nochange_low_high" and

                fnmatch.fnmatch(cell_name, "CKGMUX3*") and

                constr_pin == "S1" and

                constr_pin_dir == "fall" and

                rel_pin == "I1" and

                rel_pin_dir == "rise"):

 

        template_name = "nochange/template__ckgmux2__setup__rise__s__fall__pushout__1.sp"

        return template_name

 

    if( arc_type == "nochange_low_high" and

                fnmatch.fnmatch(cell_name, "CKGMUX3*") and

                constr_pin == "S0" and

                constr_pin_dir == "fall" and

                rel_pin == "I1" and

                rel_pin_dir == "rise"):

 

        template_name = "nochange/template__ckgmux3__setup__rise__s__fall__10__percent__glitch__minq__1.sp"

        return template_name

 

    if( arc_type == "nochange_low_high" and

                fnmatch.fnmatch(cell_name, "CKGMUX3*") and

                constr_pin == "S1" and

                constr_pin_dir == "fall" and

                rel_pin == "I2" and

                rel_pin_dir == "rise"):

 

        template_name = "nochange/template__ckgmux3__setup__rise__s__fall__10__percent__glitch__minq__1.sp"

        return template_name

 

    if( arc_type == "nochange_low_high" and

                fnmatch.fnmatch(cell_name, "CKGMUX3*") and

                (constr_pin == "S0" or constr_pin == "S1") and

                constr_pin_dir == "rise" and

                rel_pin == "I0" and

                rel_pin_dir == "fall"):

 

        template_name = "nochange/template__ckgmux2__hold__fall__s__rise__pushout__1.sp"

        return template_name

 

    if( arc_type == "nochange_low_high" and

                fnmatch.fnmatch(cell_name, "CKGMUX3*") and

                constr_pin == "S1" and

                constr_pin_dir == "rise" and

                rel_pin == "I1" and

                rel_pin_dir == "fall"):

 

        template_name = "nochange/template__ckgmux2__hold__fall__s__rise__pushout__1.sp"

        return template_name

 

    if( arc_type == "nochange_low_high" and

                fnmatch.fnmatch(cell_name, "CKGMUX3*") and

                constr_pin == "S0" and

                constr_pin_dir == "rise" and

                rel_pin == "I1" and

                rel_pin_dir == "fall"):

 

        template_name = "nochange/template__ckgmux3__hold__fall__s__rise__10__percent__glitch__minq__1.sp"

        return template_name

 

    if( arc_type == "nochange_low_high" and

                fnmatch.fnmatch(cell_name, "CKGMUX3*") and

                constr_pin == "S1" and

                constr_pin_dir == "rise" and

                rel_pin == "I2" and

                rel_pin_dir == "fall"):

 

        template_name = "nochange/template__ckgmux3__hold__fall__s__rise__10__percent__glitch__minq__1.sp"

        return template_name

 

    # DCCKGIAN2* arc from CW 0824

    if( arc_type == "nochange_high_high" and

                fnmatch.fnmatch(cell_name, "*CKGIAN*")and

                constr_pin == "ENB" and

                constr_pin_dir == "rise" and

                rel_pin == "CP" and

                rel_pin_dir == "rise"):

 

        template_name = "nochange/template__ckgian__setup__rise__enb__rise__20__percent__glitch__minq__1.sp"

        return template_name

    if( arc_type == "nochange_high_high" and

                fnmatch.fnmatch(cell_name, "*CKGIAN*")and

                constr_pin == "ENB" and

                constr_pin_dir == "fall" and

                rel_pin == "CP" and

                rel_pin_dir == "fall"):

 

        template_name = "nochange/template__ckgian__hold__fall__enb__fall__20__percent__glitch__minq__1.sp"

        return template_name

 

    if( arc_type == "nochange_low_high" and

                fnmatch.fnmatch(cell_name, "*CKGIAN*") and

                constr_pin == "ENB" and

                constr_pin_dir == "fall" and

                rel_pin == "CP" and

                rel_pin_dir == "rise"):

 

        template_name = "nochange/template__ckgian__setup__rise__enb__fall__pushout__1.sp"

        return template_name

 

    if( arc_type == "nochange_low_high" and

                fnmatch.fnmatch(cell_name, "*CKGIAN*") and

                constr_pin == "ENB" and

                constr_pin_dir == "rise" and

                rel_pin == "CP" and

                rel_pin_dir == "fall"):

 

        template_name = "nochange/template__ckgian__hold__fall__enb__rise__pushout__negative__1.sp"

        return template_name

   

    #CKAOI21/CKOAI21/CKND3/CKNR3 2021/1/12

    if( arc_type == "nochange_high_high" and

                fnmatch.fnmatch(cell_name, "CK*ND3*") and

                constr_pin == "EN1" and

                constr_pin_dir == "rise" and

                rel_pin == "CLK" and

                rel_pin_dir == "rise"):

 

        template_name = "nochange/template__ck__setup__EN2__EN1__rise__rise__pushout__1.sp"

        return template_name

 

    if( arc_type == "nochange_high_high" and

                fnmatch.fnmatch(cell_name, "CK*OAI21*") and

                constr_pin == "EN1" and

                constr_pin_dir == "rise" and

                rel_pin == "CLK" and

                rel_pin_dir == "rise"):

 

        template_name = "nochange/template__ck__setup__notEN2__EN1__rise__rise__pushout__1.sp"

        return template_name

 

    if( arc_type == "nochange_high_high" and

                fnmatch.fnmatch(cell_name, "CK*ND3*") and

                constr_pin == "EN2" and

                constr_pin_dir == "rise" and

                rel_pin == "CLK" and

                rel_pin_dir == "rise"):

 

        template_name = "nochange/template__ck__setup__EN1__EN2__rise__rise__pushout__1.sp"

        return template_name

 

    if( arc_type == "nochange_high_high" and

                fnmatch.fnmatch(cell_name, "CK*OAI21*") and

                constr_pin == "EN2" and

                constr_pin_dir == "rise" and

                rel_pin == "CLK" and

                rel_pin_dir == "rise"):

 

        template_name = "nochange/template__ck__setup__notEN1__EN2__rise__rise__pushout__1.sp"

        return template_name

 

    if( arc_type == "nochange_high_high" and

                fnmatch.fnmatch(cell_name, "CK*ND3*") and

                constr_pin == "EN1" and

                constr_pin_dir == "fall" and

                rel_pin == "CLK" and

                rel_pin_dir == "fall"):

 

        template_name = "nochange/template__ck__hold__EN2__fall__EN1__fall__pushout__negative__1.sp"

        return template_name

 

    if( arc_type == "nochange_high_high" and

                fnmatch.fnmatch(cell_name, "CK*OAI21*") and

                constr_pin == "EN1" and

                constr_pin_dir == "fall" and

                rel_pin == "CLK" and

                rel_pin_dir == "fall"):

 

        template_name = "nochange/template__ck__hold__notEN2__fall__EN1__fall__pushout__negative__1.sp"

        return template_name

 

    if( arc_type == "nochange_high_high" and

                fnmatch.fnmatch(cell_name, "CK*ND3*") and

                constr_pin == "EN2" and

                constr_pin_dir == "fall" and

                rel_pin == "CLK" and

                rel_pin_dir == "fall"):

 

        template_name = "nochange/template__ck__hold__EN1__fall__EN2__fall__pushout__negative__1.sp"

        return template_name

 

    if( arc_type == "nochange_high_high" and

                fnmatch.fnmatch(cell_name, "CK*OAI21*") and

                constr_pin == "EN2" and

                constr_pin_dir == "fall" and

                rel_pin == "CLK" and

                rel_pin_dir == "fall"):

 

        template_name = "nochange/template__ck__hold__notEN1__fall__EN2__fall__pushout__negative__1.sp"

        return template_name

 

    if( arc_type == "nochange_low_high" and

                fnmatch.fnmatch(cell_name, "CK*ND3*") and

                constr_pin == "EN1" and

                constr_pin_dir == "fall" and

                rel_pin == "CLK" and

                rel_pin_dir == "rise"):

 

        template_name = "nochange/template__ck__setup__EN2__EN1__fall__rise__20__percent__glitch__minq__1.sp"

        return template_name

 

    if( arc_type == "nochange_low_high" and

                fnmatch.fnmatch(cell_name, "CK*OAI21*") and

                constr_pin == "EN1" and

                constr_pin_dir == "fall" and

                rel_pin == "CLK" and

                rel_pin_dir == "rise"):

 

        template_name = "nochange/template__ck__setup__notEN2__EN1__fall__rise__20__percent__glitch__minq__1.sp"

        return template_name

 

    if( arc_type == "nochange_low_high" and

                fnmatch.fnmatch(cell_name, "CK*ND3*") and

                constr_pin == "EN2" and

                constr_pin_dir == "fall" and

                rel_pin == "CLK" and

                rel_pin_dir == "rise"):

 

        template_name = "nochange/template__ck__setup__EN1__EN2__fall__rise__20__percent__glitch__minq__1.sp"

        return template_name

 

    if( arc_type == "nochange_low_high" and

                fnmatch.fnmatch(cell_name, "CK*OAI21*") and

                constr_pin == "EN2" and

                constr_pin_dir == "fall" and

                rel_pin == "CLK" and

                rel_pin_dir == "rise"):

 

        template_name = "nochange/template__ck__setup__notEN1__EN2__fall__rise__20__percent__glitch__minq__1.sp"

        return template_name

 

    if( arc_type == "nochange_low_high" and

                fnmatch.fnmatch(cell_name, "CK*ND3*") and

                constr_pin == "EN1" and

                constr_pin_dir == "rise" and

                rel_pin == "CLK" and

                rel_pin_dir == "fall"):

 

        template_name = "nochange/template__ck__hold__EN2__fall__EN1__rise__20__percent__glitch__minq__1.sp"

        return template_name

 

    if( arc_type == "nochange_low_high" and

                fnmatch.fnmatch(cell_name, "CK*OAI21*") and

                constr_pin == "EN1" and

                constr_pin_dir == "rise" and

                rel_pin == "CLK" and

                rel_pin_dir == "fall"):

 

        template_name = "nochange/template__ck__hold__notEN2__fall__EN1__rise__20__percent__glitch__minq__1.sp"

        return template_name

 

    if( arc_type == "nochange_low_high" and

                fnmatch.fnmatch(cell_name, "CK*ND3*") and

                constr_pin == "EN2" and

                constr_pin_dir == "rise" and

                rel_pin == "CLK" and

                rel_pin_dir == "fall"):

 

        template_name = "nochange/template__ck__hold__EN1__fall__EN2__rise__20__percent__glitch__minq__1.sp"

        return template_name

 

    if( arc_type == "nochange_low_high" and

                fnmatch.fnmatch(cell_name, "CK*OAI21*") and

                constr_pin == "EN2" and

                constr_pin_dir == "rise" and

                rel_pin == "CLK" and

                rel_pin_dir == "fall"):

 

        template_name = "nochange/template__ck__hold__notEN1__fall__EN2__rise__20__percent__glitch__minq__1.sp"

        return template_name

 

    if( arc_type == "nochange_low_low" and

                fnmatch.fnmatch(cell_name, "CK*NR3*") and

                constr_pin == "EN1" and

                constr_pin_dir == "fall" and

                rel_pin == "CLK" and

                rel_pin_dir == "fall"):

 

        template_name = "nochange/template__ck__setup__notEN2__EN1__fall__fall__pushout__1.sp"

        return template_name

 

    if( arc_type == "nochange_low_low" and

                fnmatch.fnmatch(cell_name, "CK*AOI21*") and

                constr_pin == "EN1" and

                constr_pin_dir == "fall" and

                rel_pin == "CLK" and

                rel_pin_dir == "fall"):

 

        template_name = "nochange/template__ck__setup__EN2__EN1__fall__fall__pushout__1.sp"

        return template_name

 

    if( arc_type == "nochange_low_low" and

                fnmatch.fnmatch(cell_name, "CK*NR3*") and

                constr_pin == "EN2" and

                constr_pin_dir == "fall" and

                rel_pin == "CLK" and

                rel_pin_dir == "fall"):

 

        template_name = "nochange/template__ck__setup__notEN1__EN2__fall__fall__pushout__1.sp"

        return template_name

 

    if( arc_type == "nochange_low_low" and

                fnmatch.fnmatch(cell_name, "CK*AOI21*") and

                constr_pin == "EN2" and

                constr_pin_dir == "fall" and

                rel_pin == "CLK" and

                rel_pin_dir == "fall"):

 

        template_name = "nochange/template__ck__setup__EN1__EN2__fall__fall__pushout__1.sp"

        return template_name

 

    if( arc_type == "nochange_low_low" and

                fnmatch.fnmatch(cell_name, "CK*NR3*") and

                constr_pin == "EN1" and

                constr_pin_dir == "rise" and

                rel_pin == "CLK" and

                rel_pin_dir == "rise"):

 

        template_name = "nochange/template__ck__hold__notEN2__rise__EN1__rise__pushout__negative__1.sp"

        return template_name

 

    if( arc_type == "nochange_low_low" and

                fnmatch.fnmatch(cell_name, "CK*AOI21*") and

                constr_pin == "EN1" and

                constr_pin_dir == "rise" and

                rel_pin == "CLK" and

                rel_pin_dir == "rise"):

 

        template_name = "nochange/template__ck__hold__EN2__rise__EN1__rise__pushout__negative__1.sp"

        return template_name

 

    if( arc_type == "nochange_low_low" and

                fnmatch.fnmatch(cell_name, "CK*NR3*") and

                constr_pin == "EN2" and

                constr_pin_dir == "rise" and

                rel_pin == "CLK" and

                rel_pin_dir == "rise"):

 

        template_name = "nochange/template__ck__hold__notEN1__rise__EN2__rise__pushout__negative__1.sp"

        return template_name

 

    if( arc_type == "nochange_low_low" and

                fnmatch.fnmatch(cell_name, "CK*AOI21*") and

                constr_pin == "EN2" and

                constr_pin_dir == "rise" and

                rel_pin == "CLK" and

                rel_pin_dir == "rise"):

 

        template_name = "nochange/template__ck__hold__EN1__rise__EN2__rise__pushout__negative__1.sp"

        return template_name

 

    if( arc_type == "nochange_high_low" and

                fnmatch.fnmatch(cell_name, "CK*NR3*") and

                constr_pin == "EN1" and

                constr_pin_dir == "rise" and

                rel_pin == "CLK" and

                rel_pin_dir == "fall"):

 

        template_name = "nochange/template__ck__setup__notEN2__EN1__rise__fall__20__percent__glitch__maxq__1.sp"

        return template_name

 

    if( arc_type == "nochange_high_low" and

                fnmatch.fnmatch(cell_name, "CK*AOI21*") and

                constr_pin == "EN1" and

                constr_pin_dir == "rise" and

                rel_pin == "CLK" and

                rel_pin_dir == "fall"):

 

        template_name = "nochange/template__ck__setup__EN2__EN1__rise__fall__20__percent__glitch__maxq__1.sp"

        return template_name

 

    if( arc_type == "nochange_high_low" and

                fnmatch.fnmatch(cell_name, "CK*NR3*") and

                constr_pin == "EN2" and

                constr_pin_dir == "rise" and

                rel_pin == "CLK" and

                rel_pin_dir == "fall"):

 

        template_name = "nochange/template__ck__setup__notEN1__EN2__rise__fall__20__percent__glitch__maxq__1.sp"

        return template_name

 

    if( arc_type == "nochange_high_low" and

                fnmatch.fnmatch(cell_name, "CK*AOI21*") and

                constr_pin == "EN2" and

                constr_pin_dir == "rise" and

                rel_pin == "CLK" and

                rel_pin_dir == "fall"):

 

        template_name = "nochange/template__ck__setup__EN1__EN2__rise__fall__20__percent__glitch__maxq__1.sp"

        return template_name

 

    if( arc_type == "nochange_high_low" and

                fnmatch.fnmatch(cell_name, "CK*NR3*") and

                constr_pin == "EN1" and

                constr_pin_dir == "fall" and

                rel_pin == "CLK" and

                rel_pin_dir == "rise"):

 

        template_name = "nochange/template__ck__hold__notEN2__rise__EN1__fall__20__percent__glitch__maxq__1.sp"

        return template_name

 

    if( arc_type == "nochange_high_low" and

                fnmatch.fnmatch(cell_name, "CK*AOI21*") and

                constr_pin == "EN1" and

                constr_pin_dir == "fall" and

                rel_pin == "CLK" and

                rel_pin_dir == "rise"):

 

        template_name = "nochange/template__ck__hold__EN2__rise__EN1__fall__20__percent__glitch__maxq__1.sp"

        return template_name

 

    if( arc_type == "nochange_high_low" and

                fnmatch.fnmatch(cell_name, "CK*NR3*") and

                constr_pin == "EN2" and

                constr_pin_dir == "fall" and

                rel_pin == "CLK" and

                rel_pin_dir == "rise"):

 

        template_name = "nochange/template__ck__hold__notEN1__rise__EN2__fall__20__percent__glitch__maxq__1.sp"

        return template_name

 

    if( arc_type == "nochange_high_low" and

                fnmatch.fnmatch(cell_name, "CK*AOI21*") and

                constr_pin == "EN2" and

                constr_pin_dir == "fall" and

                rel_pin == "CLK" and

                rel_pin_dir == "rise"):

 

        template_name = "nochange/template__ck__hold__EN1__rise__EN2__fall__20__percent__glitch__maxq__1.sp"

        return template_name

 

    # CKG*AO22* from CW 2021/1/21

    if( arc_type == "nochange_high_high" and

                fnmatch.fnmatch(cell_name, "CKG*AO22*") and

                fnmatch.fnmatch(constr_pin, "SEL*") and

                constr_pin_dir == "rise" and

                fnmatch.fnmatch(rel_pin, "CLK*") and

                rel_pin_dir == "rise"):

 

        template_name = "nochange/template__ckg__setup__rise__en__rise__pushout__1.sp"

        return template_name

 

    if( arc_type == "nochange_high_high" and

                fnmatch.fnmatch(cell_name, "CKG*AO22*") and

                fnmatch.fnmatch(constr_pin, "SEL*") and

                constr_pin_dir == "fall" and

                fnmatch.fnmatch(rel_pin, "CLK*") and

                rel_pin_dir == "fall"):

 

        template_name = "nochange/template__ckg__hold__fall__en__fall__pushout__negative__1.sp"

        return template_name

 

    if( arc_type == "nochange_low_high" and

                fnmatch.fnmatch(cell_name, "CKG*AO22*") and

                fnmatch.fnmatch(constr_pin, "SEL*") and

                constr_pin_dir == "fall" and

                fnmatch.fnmatch(rel_pin, "CLK*") and

                rel_pin_dir == "rise" and

                                "preZ" in probe_list):

 

        template_name = "nochange/template__ckg__setup__rise__en__fall__20__percent__glitch__minq__1.sp"

        return template_name

 

    if( arc_type == "nochange_low_high" and

                fnmatch.fnmatch(cell_name, "CKG*AO22*") and

                fnmatch.fnmatch(constr_pin, "SEL*") and

                constr_pin_dir == "rise" and

                fnmatch.fnmatch(rel_pin, "CLK*") and

                rel_pin_dir == "fall" and

                                "preZ" in probe_list):

 

        template_name = "nochange/template__ckg__hold__fall__en__rise__20__percent__glitch__minq__1.sp"

        return template_name

    if( arc_type == "nochange_low_high" and

                fnmatch.fnmatch(cell_name, "CKG*AO22*") and

                fnmatch.fnmatch(constr_pin, "SEL*") and

                constr_pin_dir == "fall" and

                fnmatch.fnmatch(rel_pin, "CLK*") and

                rel_pin_dir == "rise"):

 

        template_name = "nochange/template__ckg__setup__rise__en__fall__20__percent__glitch__maxq__1.sp"

        return template_name

 

    if( arc_type == "nochange_low_high" and

                fnmatch.fnmatch(cell_name, "CKG*AO22*") and

                fnmatch.fnmatch(constr_pin, "SEL*") and

                constr_pin_dir == "rise" and

                fnmatch.fnmatch(rel_pin, "CLK*") and

                rel_pin_dir == "fall"):

 

        template_name = "nochange/template__ckg__hold__fall__en__rise__20__percent__glitch__maxq__1.sp"

        return template_name

 

    #SLEEP-related arc from Jarvis 0414

    if( arc_type == "non_seq_hold" and

                (fnmatch.fnmatch(cell_name, "RLH*") or fnmatch.fnmatch(cell_name, "RSVNBSP*")) and

                constr_pin == "SLEEP" and

                constr_pin_dir == "rise" and

                rel_pin == "CDN" and

                rel_pin_dir == "fall" and

                len(probe_list) == 1):

 

        template_name = "non_seq_hold/template__latch__fall__rise__pushout__maxq__1.sp"

        return template_name

 

    if( arc_type == "non_seq_hold" and

                (fnmatch.fnmatch(cell_name, "RLH*") or fnmatch.fnmatch(cell_name, "RSVNBSP*")) and

                constr_pin == "CDN" and

                constr_pin_dir == "fall" and

                rel_pin == "SLEEP" and

                rel_pin_dir == "fall" and

                len(probe_list) == 1):

 

        template_name = "non_seq_hold/template__latch__fall__fall__pushout__maxq__1.sp"

        return template_name

 

    if( arc_type == "non_seq_hold" and

                (fnmatch.fnmatch(cell_name, "RLH*") or fnmatch.fnmatch(cell_name, "RSVNBSP*")) and

                constr_pin == "SLEEP" and

                constr_pin_dir == "fall" and

                rel_pin == "CDN" and

                rel_pin_dir == "rise" and

                len(probe_list) == 1):

 

        template_name = "non_seq_hold/template__latch__rise__fall__glitch__minq__1.sp"

        return template_name

       

    if( arc_type == "non_seq_hold" and

                (fnmatch.fnmatch(cell_name, "RLH*") or fnmatch.fnmatch(cell_name, "RSVNBSP*")) and

                constr_pin == "CDN" and

                constr_pin_dir == "fall" and

                rel_pin == "SLEEP" and

                rel_pin_dir == "rise" and

                len(probe_list) == 1):

 

        template_name = "non_seq_hold/template__latch__rise__fall__glitch__minq__1.sp"

        return template_name

       

    if( arc_type == "non_seq_hold" and

                (fnmatch.fnmatch(cell_name, "RLH*") or fnmatch.fnmatch(cell_name, "RSVNBSP*")) and

                constr_pin == "SLEEP" and

                constr_pin_dir == "rise" and

                rel_pin == "SDN" and

                rel_pin_dir == "fall" and

                len(probe_list) == 1):

 

        template_name = "non_seq_hold/template__latch__fall__rise__pushout__minq__1.sp"

        return template_name

 

    if( arc_type == "non_seq_hold" and

                (fnmatch.fnmatch(cell_name, "RLH*SCN*") or fnmatch.fnmatch(cell_name, "RSVNBSP*SCN*")) and

                constr_pin == "SDN" and

                constr_pin_dir == "fall" and

                rel_pin == "SLEEP" and

                rel_pin_dir == "fall" and

                len(probe_list) == 1):

 

        template_name = "non_seq_hold/template__latch__CDN__fall__fall__pushout__minq__1.sp"

        return template_name

 

    if( arc_type == "non_seq_hold" and

                (fnmatch.fnmatch(cell_name, "RLH*") or fnmatch.fnmatch(cell_name, "RSVNBSP*")) and

                constr_pin == "SDN" and

                constr_pin_dir == "fall" and

                rel_pin == "SLEEP" and

                rel_pin_dir == "fall" and

                len(probe_list) == 1):

 

        template_name = "non_seq_hold/template__latch__fall__fall__pushout__minq__1.sp"

        return template_name

 

    if( arc_type == "non_seq_hold" and

                (fnmatch.fnmatch(cell_name, "RLH*") or fnmatch.fnmatch(cell_name, "RSVNBSP*")) and

                constr_pin == "SLEEP" and

                constr_pin_dir == "fall" and

                rel_pin == "SDN" and

                rel_pin_dir == "rise" and

                len(probe_list) == 1):

 

        template_name = "non_seq_hold/template__latch__rise__fall__glitch__maxq__1.sp"

        return template_name

 

    if( arc_type == "non_seq_hold" and

                fnmatch.fnmatch(cell_name, "RSVNBSP*SCN*") and

                constr_pin == "SDN" and

                constr_pin_dir == "fall" and

                rel_pin == "SLEEP" and

                rel_pin_dir == "rise" and

                len(probe_list) == 1):

 

        template_name = "non_seq_hold/template__latch__CDN__rise__fall__glitch__maxq__1.sp"

        return template_name

       

    if( arc_type == "non_seq_hold" and

                (fnmatch.fnmatch(cell_name, "RLH*") or fnmatch.fnmatch(cell_name, "RSVNBSP*SN*")) and

                constr_pin == "SDN" and

                constr_pin_dir == "fall" and

                rel_pin == "SLEEP" and

                rel_pin_dir == "rise" and

                len(probe_list) == 1):

 

        template_name = "non_seq_hold/template__latch__rise__fall__glitch__maxq__1.sp"

        return template_name

 

    if( arc_type == "non_seq_hold" and

                fnmatch.fnmatch(cell_name, "RSVNBSP*SYNC2*") and

                constr_pin == "SLEEP" and

                constr_pin_dir == "rise" and

                rel_pin == "CDN" and

                rel_pin_dir == "fall" and

                len(probe_list) == 2):

 

        template_name = "non_seq_hold/template__latch__fall__rise__pushout__maxq__2.sp"

        return template_name

 

    if( arc_type == "non_seq_hold" and

                fnmatch.fnmatch(cell_name, "RSVNBSP*SYNC2*") and

                constr_pin == "CDN" and

                constr_pin_dir == "fall" and

                rel_pin == "SLEEP" and

                rel_pin_dir == "fall" and

                len(probe_list) == 2):

 

        template_name = "non_seq_hold/template__latch__fall__fall__pushout__maxq__2.sp"

        return template_name

 

    if( arc_type == "non_seq_hold" and

                fnmatch.fnmatch(cell_name, "RSVNBSP*SYNC2*") and

                constr_pin == "SLEEP" and

                constr_pin_dir == "fall" and

                rel_pin == "CDN" and

                rel_pin_dir == "rise" and

                len(probe_list) == 2):

 

        template_name = "non_seq_hold/template__latch__rise__fall__glitch__minq__2.sp"

        return template_name

       

    if( arc_type == "non_seq_hold" and

                fnmatch.fnmatch(cell_name, "RSVNBSP*SYNC2*") and

                constr_pin == "CDN" and

                constr_pin_dir == "fall" and

                rel_pin == "SLEEP" and

                rel_pin_dir == "rise" and

                len(probe_list) == 2):

 

        template_name = "non_seq_hold/template__latch__rise__fall__glitch__minq__2.sp"

        return template_name

       

    if( arc_type == "non_seq_hold" and

                fnmatch.fnmatch(cell_name, "RSVNBSP*SYNC2*") and

                constr_pin == "SLEEP" and

                constr_pin_dir == "rise" and

                rel_pin == "SDN" and

                rel_pin_dir == "fall" and

                len(probe_list) == 2):

 

        template_name = "non_seq_hold/template__latch__fall__rise__pushout__minq__2.sp"

        return template_name

 

    if( arc_type == "non_seq_hold" and

                fnmatch.fnmatch(cell_name, "RSVNBSP*SYNC2*") and

                constr_pin == "SDN" and

                constr_pin_dir == "fall" and

                rel_pin == "SLEEP" and

                rel_pin_dir == "fall" and

                len(probe_list) == 2):

 

        template_name = "non_seq_hold/template__latch__fall__fall__pushout__minq__2.sp"

        return template_name

 

    if( arc_type == "non_seq_hold" and

                fnmatch.fnmatch(cell_name, "RSVNBSP*SYNC2*") and

                constr_pin == "SLEEP" and

                constr_pin_dir == "fall" and

                rel_pin == "SDN" and

                rel_pin_dir == "rise" and

                len(probe_list) == 2):

 

        template_name = "non_seq_hold/template__latch__rise__fall__glitch__maxq__2.sp"

        return template_name

       

    if( arc_type == "non_seq_hold" and

                fnmatch.fnmatch(cell_name, "RSVNBSP*SYNC2*") and

                constr_pin == "SDN" and

                constr_pin_dir == "fall" and

                rel_pin == "SLEEP" and

                rel_pin_dir == "rise" and

                len(probe_list) == 2):

 

        template_name = "non_seq_hold/template__latch__rise__fall__glitch__maxq__2.sp"

        return template_name

 

    # 21/1/7 SLEEP arc from CW

    if( arc_type == "nochange_low_high" and

 

                fnmatch.fnmatch(cell_name, "RLH*") and

                constr_pin == "SLEEP" and

                constr_pin_dir == "fall" and

                rel_pin == "CP" and

                rel_pin_dir == "rise"):

 

        template_name = "nochange/template__retn__latch__setup__notD__CDN__SDN__sleep__fall__rise__pushout__maxq__1.sp"

        return template_name

 

    if( arc_type == "nochange_high_high" and

                fnmatch.fnmatch(cell_name, "RLH*") and

                constr_pin == "SLEEP" and

                constr_pin_dir == "fall" and

                rel_pin == "CP" and

                rel_pin_dir == "fall"):

 

        template_name = "nochange/template__retn__latch__hold__notD__CDN__SDN__fall__sleep__fall__glitch__minq__1.sp"

        return template_name

 

    # 21/1/8 SLEEP arc from CW

    if( arc_type == "nochange_low_high" and

 

                fnmatch.fnmatch(cell_name, "RLH*") and

                constr_pin == "SLEEP" and

                constr_pin_dir == "rise" and

                rel_pin == "CP" and

                rel_pin_dir == "fall"):

 

        template_name = "nochange/template__retn__latch__hold__notD__CDN__SDN__fall__sleep__rise__glitch__maxq__1.sp"

        return template_name

 

    if( arc_type == "nochange_high_high" and

                fnmatch.fnmatch(cell_name, "RLH*") and

                constr_pin == "SLEEP" and

                constr_pin_dir == "rise" and

                rel_pin == "CP" and

                rel_pin_dir == "rise"):

 

        template_name = "nochange/template__retn__latch__setup__D__CDN__SDN__sleep__rise__rise__glitch__maxq__1.sp"

        return template_name

 

    if( arc_type == "removal" and

                fnmatch.fnmatch(cell_name, "RS*NBNSP*") and

                constr_pin == "NSLEEP" and

                constr_pin_dir == "fall" and

                rel_pin == "CP" and

                rel_pin_dir == "rise"):

 

        template_name = "hold/template__retn__flop__removal__notD__CDN__SDN__rise__nsleep__fall__pushout__maxq__1.sp"

        return template_name

 

    if( arc_type == "nochange_high_high" and

                fnmatch.fnmatch(cell_name, "RS*NBNSP*") and

                constr_pin == "NSLEEP" and

                constr_pin_dir == "rise" and

                rel_pin == "CP" and

                rel_pin_dir == "rise"):

 

        template_name = "nochange/template__retn__flop__setup__notD__CDN__SDN__nsleep__rise__rise__pushout__maxq__1.sp"

        return template_name

 

    if( arc_type == "nochange_high_high" and

                fnmatch.fnmatch(cell_name, "RS*NBNSP*") and

                constr_pin == "NSLEEP" and

                constr_pin_dir == "fall" and

                rel_pin == "CP" and

                rel_pin_dir == "fall"):

 

        template_name = "nochange/template__retn__flop__hold__notD__CDN__SDN__fall__nsleep__fall__glitch__minq__1.sp"

        return template_name

 

    if( arc_type == "nochange_high_high" and

                fnmatch.fnmatch(cell_name, "RS*NBSP*") and

                constr_pin == "SLEEP" and

                constr_pin_dir == "rise" and

                rel_pin == "CP" and

                rel_pin_dir == "rise"):

 

        template_name = "nochange/template__retn__flop__setup__notD__CDN__SDN__sleep__rise__rise__glitch__minq__1.sp"

        return template_name

 

    if( arc_type == "nochange_high_high" and

                fnmatch.fnmatch(cell_name, "RS*NBSP*") and

                constr_pin == "SLEEP" and

                constr_pin_dir == "fall" and

                rel_pin == "CP" and

                rel_pin_dir == "fall"):

 

        template_name = "nochange/template__retn__flop__hold__notD__CDN__SDN__fall__sleep__fall__glitch__minq__1.sp"

        return template_name

 

    if( arc_type == "nochange_low_high" and

                fnmatch.fnmatch(cell_name, "RS*NBNSP*") and

                constr_pin == "NSLEEP" and

                constr_pin_dir == "rise" and

                rel_pin == "CP" and

                rel_pin_dir == "fall"):

 

        template_name = "nochange/template__retn__flop__hold__notD__CDN__SDN__fall__nsleep__rise__glitch__minq__1.sp"

        return template_name

 

    if( arc_type == "nochange_low_high" and

                fnmatch.fnmatch(cell_name, "RS*NBNSP*") and

                constr_pin == "NSLEEP" and

                constr_pin_dir == "fall" and

                rel_pin == "CP" and

                rel_pin_dir == "rise"):

 

        template_name = "nochange/template__retn__flop__setup__notD__CDN__SDN__nsleep__fall__rise__glitch__minq__1.sp"

        return template_name

 

    if( arc_type == "nochange_low_high" and

                fnmatch.fnmatch(cell_name, "RS*NBSP*") and

                constr_pin == "SLEEP" and

                constr_pin_dir == "rise" and

                rel_pin == "CP" and

                rel_pin_dir == "fall"):

 

        template_name = "nochange/template__retn__flop__hold__notD__CDN__SDN__fall__sleep__rise__glitch__minq__1.sp"

        return template_name

 

    if( arc_type == "nochange_low_high" and

                fnmatch.fnmatch(cell_name, "RS*NBSP*") and

                constr_pin == "SLEEP" and

                constr_pin_dir == "fall" and

                rel_pin == "CP" and

                rel_pin_dir == "rise"):

 

        template_name = "nochange/template__retn__flop__setup__notD__CDN__SDN__sleep__fall__rise__pushout__maxq__1.sp"

        return template_name

 

    if( arc_type == "removal" and

                fnmatch.fnmatch(cell_name, "SLH*") and

                constr_pin == "CDN" and

                constr_pin_dir == "rise" and

                rel_pin == "CLK" and

                rel_pin_dir == "fall" and

                "D&SDN&!SE&!SI" in when):

 

        template_name = "hold/template__latch__fall__rise__glitch__maxq__1.sp"

        return template_name

 

    if( arc_type == "removal" and

                fnmatch.fnmatch(cell_name, "SLH*") and

                constr_pin == "SDN" and

                constr_pin_dir == "rise" and

                rel_pin == "CLK" and

                rel_pin_dir == "fall" and

                "CDN&!D&!SE&SI" in when):

 

        template_name = "hold/template__latch__fall__rise__glitch__minq__1.sp"

        return template_name

 

    # 21/1/8 CDN/SDN arc from CW

    if( arc_type == "removal" and

                fnmatch.fnmatch(cell_name, "MB*SLH*") and

                constr_pin == "CDN" and

                constr_pin_dir == "rise" and

                (rel_pin == "CLK" or rel_pin == "E") and

                rel_pin_dir == "fall"):

 

        template_name = "hold/template__latch__fall__rise__glitch__maxq__1.sp"

        return template_name

 

    if( arc_type == "removal" and

                fnmatch.fnmatch(cell_name, "MB*SLH*") and

                constr_pin == "SDN" and

                constr_pin_dir == "rise" and

                (rel_pin == "CLK" or rel_pin == "E") and

                rel_pin_dir == "fall"):

 

        template_name = "hold/template__SLH__fall__SDN__rise__glitch__minq__1.sp"

        return template_name

 

    if( arc_type == "removal" and

                fnmatch.fnmatch(cell_name, "RLH*") and

                constr_pin == "CDN" and

                constr_pin_dir == "rise" and

                rel_pin == "CP" and

                rel_pin_dir == "fall"):

 

        template_name = "hold/template__latch__fall__rise__glitch__maxq__1.sp"

        return template_name

 

    if( arc_type == "removal" and

                fnmatch.fnmatch(cell_name, "RLH*") and

                constr_pin == "SDN" and

                constr_pin_dir == "rise" and

                rel_pin == "CP" and

                rel_pin_dir == "fall"):

 

        template_name = "hold/template__latch__fall__rise__glitch__minq__1.sp"

        return template_name

 

    if( arc_type == "removal" and

                fnmatch.fnmatch(cell_name, "RSVNB*") and

                constr_pin == "CDN" and

                constr_pin_dir == "rise" and

                rel_pin == "CP" and

                rel_pin_dir == "rise"):

 

        template_name = "hold/template__latch__rise__rise__glitch__maxq__1.sp"

        return template_name

 

    if( arc_type == "removal" and

                fnmatch.fnmatch(cell_name, "RSVNB*") and

                constr_pin == "SDN" and

                constr_pin_dir == "rise" and

                rel_pin == "CP" and

                rel_pin_dir == "rise"):

 

        template_name = "hold/template__latch__rise__rise__glitch__minq__1.sp"

        return template_name

 

    if( arc_type == "removal" and

                fnmatch.fnmatch(cell_name, "RLH*") and

                constr_pin == "SLEEP" and

                constr_pin_dir == "rise" and

                rel_pin == "CP" and

                rel_pin_dir == "rise"):

 

        template_name = "hold/template__retn__latch__removal__notD__CDN__SDN__rise__sleep__rise__pushout__maxq__1.sp"

        return template_name

 

    if( arc_type == "removal" and

                fnmatch.fnmatch(cell_name, "RS*NBSP*") and

                constr_pin == "SLEEP" and

                constr_pin_dir == "rise" and

                rel_pin == "CP" and

                rel_pin_dir == "rise" and

                len(probe_list) == 1):

 

        template_name = "hold/template__retn__flop__removal__notD__CDN__SDN__rise__sleep__rise__pushout__maxq__1.sp"

        return template_name

 

    if( arc_type == "removal" and

                fnmatch.fnmatch(cell_name, "RS*NBSP*SYNC2*") and

                constr_pin == "SLEEP" and

                constr_pin_dir == "rise" and

                rel_pin == "CP" and

                rel_pin_dir == "rise" and

                len(probe_list) == 2):

 

        template_name = "hold/template__retn__flop__removal__notD__CDN__SDN__rise__sleep__rise__pushout__maxq__minq__2.sp"

        return template_name

 

 

 

 

    # *EDF*Q cell for constr_pin = E, rel_pin = CP, D=1 in when, fall_constraint

    if( arc_type == "hold" and

                fnmatch.fnmatch(cell_name, "*EDF*D*") and

                constr_pin == "E" and

                constr_pin_dir == "fall" and

                rel_pin == "CP" and

                rel_pin_dir == "rise" and

                "D" in when and

                not "!D" in when and

                len(probe_list) == 1):

 

        template_name = "hold/template__EDF__D__rise__fall__pushout__1.sp"

        return template_name

 

    # *EDF*Q cell for constr_pin = E, rel_pin = CP and D=0 in when, fall_constraint

    if( arc_type == "hold" and

                fnmatch.fnmatch(cell_name, "*EDF*D*") and

                constr_pin == "E" and

                constr_pin_dir == "fall" and

                rel_pin == "CP" and

                rel_pin_dir == "rise" and

                "!D" in when and

                len(probe_list) == 1):

 

        template_name = "hold/template__EDF__notD__rise__fall__pushout__1.sp"

        return template_name

 

    # *EDF*Q cell for constr_pin = E, rel_pin = CP, and D=1 in when, rise_constraint

    if( arc_type == "hold" and

                fnmatch.fnmatch(cell_name, "*EDF*D*") and

                constr_pin == "E" and

                constr_pin_dir == "rise" and

                rel_pin == "CP" and

                rel_pin_dir == "rise" and

                "D" in when and

                not "!D" in when and

                len(probe_list) == 1):

 

        template_name = "hold/template__EDF__D__rise__rise__glitch__1.sp"

        return template_name

 

    # *EDF*Q cell for constr_pin = E, rel_pin = CP and D=0 in when, rise_constraint

    if( arc_type == "hold" and

                fnmatch.fnmatch(cell_name, "*EDF*D*") and

                constr_pin == "E" and

                constr_pin_dir == "rise" and

                rel_pin == "CP" and

                rel_pin_dir == "rise" and

                "!D" in when and

                len(probe_list) == 1):

 

        template_name = "hold/template__EDF__notD__rise__rise__glitch__1.sp"

        return template_name

 

    # MB*SRLSEDF* cell for constr_pin = E*, rel_pin = CP

    if( arc_type == "hold" and

                fnmatch.fnmatch(cell_name, "MB*EDF*ITL*") and

                (fnmatch.fnmatch(constr_pin, "E1") or fnmatch.fnmatch(constr_pin, "E2") or fnmatch.fnmatch(constr_pin, "E3") or fnmatch.fnmatch(constr_pin, "E4")) and

                constr_pin_dir == "rise" and

                rel_pin == "CP" and

                rel_pin_dir == "rise" and

                len(probe_list) == 1):

 

        template_name = "hold/template__EDF__rise__E__rise__glitch__maxq__1.sp"

        return template_name

 

    # MB*SRLSEDF* arc from CW 1214  => 0115

    if( arc_type == "hold" and

                fnmatch.fnmatch(cell_name, "MB*SRLSEDF*ITL*") and

                (fnmatch.fnmatch(constr_pin, "E1") or fnmatch.fnmatch(constr_pin, "E2") or fnmatch.fnmatch(constr_pin, "E3") or fnmatch.fnmatch(constr_pin, "E4")) and

                constr_pin_dir == "fall" and

                rel_pin == "CP" and

                rel_pin_dir == "rise" and

                len(probe_list) == 1):

 

        template_name = "hold/template__MB__EDF__rise__E__fall__pushout__maxq__1.sp"

        return template_name

 

    if( arc_type == "hold" and

                fnmatch.fnmatch(cell_name, "MB*EDF*ITL*") and

                (fnmatch.fnmatch(constr_pin, "E1") or fnmatch.fnmatch(constr_pin, "E2") or fnmatch.fnmatch(constr_pin, "E3") or fnmatch.fnmatch(constr_pin, "E4")) and

                constr_pin_dir == "fall" and

                rel_pin == "CP" and

                rel_pin_dir == "rise" and

                len(probe_list) == 1):

 

        template_name = "hold/template__MB__EDF__rise__E__fall__pushout__minq__1.sp"

        return template_name

    ## mb retention notNRESTORE_notSAVE is forbidden arc##

    if( arc_type == "hold" and

                (fnmatch.fnmatch(cell_name, "MB*LPV*")) and

                "!NRESTORE" in when and "!SAVE" in when):

        return None

    if( arc_type == "min_pulse_width"  and

                (fnmatch.fnmatch(cell_name, "MB*LPV*")) and

                "!NRESTORE" in when and "!SAVE" in when):

        return None

    # SI to CP

    if( arc_type == "hold" and

                (fnmatch.fnmatch(constr_pin, "SI")) and

                constr_pin_dir == "rise" and

                (fnmatch.fnmatch(rel_pin, "CP") or fnmatch.fnmatch(rel_pin, "CLK")) and

                rel_pin_dir == "rise" and

                len(probe_list) == 1):

 

        template_name = "hold/template__common__rise__rise__1.sp"

        return template_name

 

    if( arc_type == "hold" and

                (fnmatch.fnmatch(constr_pin, "SI") ) and

                constr_pin_dir == "fall" and

                (fnmatch.fnmatch(rel_pin, "CP") or fnmatch.fnmatch(rel_pin, "CLK") ) and

                rel_pin_dir == "rise" and

                len(probe_list) == 1):

 

        template_name = "hold/template__common__rise__fall__1.sp"

        return \

            template_name

 

    if( arc_type == "hold" and

                (fnmatch.fnmatch(constr_pin, "SI") ) and

                constr_pin_dir == "rise" and

                (fnmatch.fnmatch(rel_pin, "CP") ) and

                rel_pin_dir == "rise" and

                len(probe_list) == 2):

 

        template_name = "hold/template__common__rise__rise__2.sp"

        return template_name

 

    if( arc_type == "hold" and

                (fnmatch.fnmatch(constr_pin, "SI") ) and

                constr_pin_dir == "fall" and

                (fnmatch.fnmatch(rel_pin, "CP") ) and

                rel_pin_dir == "rise" and

                len(probe_list) == 2):

 

        template_name = "hold/template__common__rise__fall__2.sp"

        return \

            template_name

 

    if( arc_type == "hold" and

                fnmatch.fnmatch(constr_pin, "NRESTORE") and

                constr_pin_dir == "rise" and

                fnmatch.fnmatch(rel_pin, "CP") and

                rel_pin_dir == "fall" and

#                "Q" in probe_list and

                len(probe_list) == 1):

 

        template_name = "hold/template__rsdf__Q__fall__rise__pushout__1.sp"

        return template_name

 

    if( arc_type == "hold" and

                fnmatch.fnmatch(constr_pin, "SAVE") and

                constr_pin_dir == "fall" and

                fnmatch.fnmatch(rel_pin, "CP") and

                rel_pin_dir == "rise" and

#                "Q" in probe_list and

                len(probe_list) == 1):

 

        template_name = "hold/template__rsdf__Q__rise__fall__pushout__1.sp"

        return \

            template_name

 

    # SE to CP

    if( arc_type == "hold" and

                fnmatch.fnmatch(constr_pin, "SE") and

                constr_pin_dir == "rise" and

                (fnmatch.fnmatch(rel_pin, "CP") or fnmatch.fnmatch(rel_pin, "CLK")) and

                rel_pin_dir == "rise" and

                len(probe_list) == 1):

 

        template_name = "hold/template__common__rise__rise__1.sp"

        return template_name

 

    if( arc_type == "hold" and

                fnmatch.fnmatch(constr_pin, "SE") and

                constr_pin_dir == "fall" and

                (fnmatch.fnmatch(rel_pin, "CP") or fnmatch.fnmatch(rel_pin, "CLK")) and

                rel_pin_dir == "rise" and

                len(probe_list) == 1):

 

        template_name = "hold/template__common__rise__fall__1.sp"

        return \

            template_name

 

    if( arc_type == "hold" and

                fnmatch.fnmatch(constr_pin, "SE") and

                constr_pin_dir == "rise" and

                fnmatch.fnmatch(rel_pin, "CP") and

                rel_pin_dir == "rise" and

                len(probe_list) == 2):

 

        template_name = "hold/template__common__rise__rise__2.sp"

        return template_name

 

    if( arc_type == "hold" and

                fnmatch.fnmatch(constr_pin, "SE") and

                constr_pin_dir == "fall" and

                fnmatch.fnmatch(rel_pin, "CP") and

                rel_pin_dir == "rise" and

                len(probe_list) == 2):

 

        template_name = "hold/template__common__rise__fall__2.sp"

        return \

            template_name

 

    if( arc_type == "hold" and

                fnmatch.fnmatch(cell_name, "MB*") and

                fnmatch.fnmatch(constr_pin, "SE") and

                constr_pin_dir == "rise" and

                fnmatch.fnmatch(rel_pin, "CP") and

                rel_pin_dir == "rise" and

                len(probe_list) == 1):

 

        template_name = "hold/template__MB__common__rise__rise__2.sp"

        return template_name

 

    if( arc_type == "hold" and

                fnmatch.fnmatch(cell_name, "MB*") and

                fnmatch.fnmatch(constr_pin, "SE") and

                constr_pin_dir == "fall" and

                fnmatch.fnmatch(rel_pin, "CP") and

                rel_pin_dir == "rise" and

                len(probe_list) == 1):

 

        template_name = "hold/template__MB__common__rise__fall__2.sp"

        return \

            template_name

   

    # 2021/1/6 Intel N3 SE->CPN form CW

    if( arc_type == "hold" and

                fnmatch.fnmatch(cell_name, "SDFN*") and

                (fnmatch.fnmatch(constr_pin, "SE") or fnmatch.fnmatch(constr_pin, "SI") or fnmatch.fnmatch(constr_pin, "C") or fnmatch.fnmatch(constr_pin, "SN") or fnmatch.fnmatch(constr_pin, "CN") or fnmatch.fnmatch(constr_pin, "S")) and

                constr_pin_dir == "rise" and

                fnmatch.fnmatch(rel_pin, "CPN") and

                rel_pin_dir == "fall" ):

 

        template_name = "hold/template__common__fall__rise__1.sp"

        return template_name

 

 

    if( arc_type == "hold" and

                fnmatch.fnmatch(cell_name, "SDFN*") and

                (fnmatch.fnmatch(constr_pin, "SE") or fnmatch.fnmatch(constr_pin, "SI") or fnmatch.fnmatch(constr_pin, "C") or fnmatch.fnmatch(constr_pin, "SN") or fnmatch.fnmatch(constr_pin, "CN") or fnmatch.fnmatch(constr_pin, "S")) and

                constr_pin_dir == "fall" and

                fnmatch.fnmatch(rel_pin, "CPN") and

                rel_pin_dir == "fall" ):

 

        template_name = "hold/template__common__fall__fall__1.sp"

        return template_name

 

    # 2023/2/21 DFDETRPQ* SE->CP

    if( arc_type == "hold" and

                fnmatch.fnmatch(cell_name, "*DET*") and

                (fnmatch.fnmatch(constr_pin, "SE") or fnmatch.fnmatch(constr_pin, "SI")) and

                constr_pin_dir == "rise" and

                fnmatch.fnmatch(rel_pin, "CP") and

                rel_pin_dir == "fall" ):

 

        template_name = "hold/template__common__fall__rise__3.sp"

        return template_name

 

 

    if( arc_type == "hold" and

                fnmatch.fnmatch(cell_name, "*DET*") and

                (fnmatch.fnmatch(constr_pin, "SE") or fnmatch.fnmatch(constr_pin, "SI")) and

                constr_pin_dir == "fall" and

                fnmatch.fnmatch(rel_pin, "CP") and

                rel_pin_dir == "fall" ):

 

        template_name = "hold/template__common__fall__fall__3.sp"

        return template_name

 

    # 2021/2/24 SE->E Intel N3 from CW

    if( arc_type == "hold" and

                fnmatch.fnmatch(cell_name, "SLH*QSO*") and

                        fnmatch.fnmatch(constr_pin, "SE") and

                constr_pin_dir == "rise" and

                fnmatch.fnmatch(rel_pin, "E") and

                rel_pin_dir == "rise" and

                len(probe_list) == 2):

 

        template_name = "hold/template__SLH__rise__SE__rise__pushout__2.sp"

        return template_name

 

    if( arc_type == "hold" and

                fnmatch.fnmatch(cell_name, "SLH*QSO*") and

                        fnmatch.fnmatch(constr_pin, "SE") and

                constr_pin_dir == "fall" and

                fnmatch.fnmatch(rel_pin, "E") and

                rel_pin_dir == "rise" and

                len(probe_list) == 2):

 

        template_name = "hold/template__SLH__rise__SE__fall__pushout__2.sp"

        return template_name

 

    if( arc_type == "hold" and

                (fnmatch.fnmatch(cell_name, "SLH*QNSON*") or fnmatch.fnmatch(cell_name, "MB*SLH*QNSON*")) and

                        fnmatch.fnmatch(constr_pin, "SE") and

                constr_pin_dir == "rise" and

                fnmatch.fnmatch(rel_pin, "E") and

                rel_pin_dir == "rise" and

                len(probe_list) == 1):

 

        template_name = "hold/template__SLH__rise__SE__rise__pushout__1.sp"

        return template_name

 

    if( arc_type == "hold" and

                (fnmatch.fnmatch(cell_name, "SLH*QNSON*") or fnmatch.fnmatch(cell_name, "MB*SLH*QNSON*")) and

                        fnmatch.fnmatch(constr_pin, "SE") and

                constr_pin_dir == "fall" and

                fnmatch.fnmatch(rel_pin, "E") and

                rel_pin_dir == "rise" and

                len(probe_list) == 1):

 

        template_name = "hold/template__SLH__rise__SE__fall__pushout__1.sp"

        return template_name

 

    if( arc_type == "hold" and

                fnmatch.fnmatch(cell_name, "SLH*QNSON*") and

                constr_pin == "SE" and

                constr_pin_dir == "rise" and

                (rel_pin == "E" or rel_pin == "CLK") and

                rel_pin_dir == "fall" and

                        "D" in when and

                        not "!D" in when and

                        len(probe_list) == 1):

 

        template_name = "hold/template__SLH__QN__fall__SE__rise__glitch__maxq__1.sp"

        return template_name

 

    if( arc_type == "hold" and

                fnmatch.fnmatch(cell_name, "SLH*QNSON*") and

                constr_pin == "SE" and

                constr_pin_dir == "rise" and

                (rel_pin == "E" or rel_pin == "CLK") and

                rel_pin_dir == "fall" and

                        "!D" in when and

                        len(probe_list) == 1):

 

        template_name = "hold/template__SLH__QN__fall__SE__rise__glitch__minq__1.sp"

        return template_name

 

    if( arc_type == "hold" and

                fnmatch.fnmatch(cell_name, "SLH*QNSON*") and

                constr_pin == "SE" and

                constr_pin_dir == "fall" and

                (rel_pin == "E" or rel_pin == "CLK") and

                rel_pin_dir == "fall" and

                        "D" in when and

                        not "!D" in when and

                        len(probe_list) == 1):

 

        template_name = "hold/template__SLH__QN__fall__SE__fall__glitch__minq__1.sp"

        return template_name   

 

    if( arc_type == "hold" and

                fnmatch.fnmatch(cell_name, "SLH*QNSON*") and

                constr_pin == "SE" and

                constr_pin_dir == "fall" and

                (rel_pin == "E" or rel_pin == "CLK") and

                rel_pin_dir == "fall" and

                        "!D" in when and

                        len(probe_list) == 1):

 

        template_name = "hold/template__SLH__QN__fall__SE__fall__glitch__maxq__1.sp"

        return template_name   

 

    if( arc_type == "hold" and

                fnmatch.fnmatch(cell_name, "SLH*QSO*") and

                constr_pin == "SE" and

                constr_pin_dir == "rise" and

                (rel_pin == "E" or rel_pin == "CLK") and

                rel_pin_dir == "fall" and

                        "D" in when and

                        not "!D" in when and

                        len(probe_list) == 2):

 

        template_name = "hold/template__SLH__fall__SE__rise__glitch__minq__2.sp"

        return template_name

 

    if( arc_type == "hold" and

                fnmatch.fnmatch(cell_name, "SLH*QSO*") and

                constr_pin == "SE" and

                constr_pin_dir == "rise" and

                (rel_pin == "E" or rel_pin == "CLK") and

                rel_pin_dir == "fall" and

                        "!D" in when and

                        len(probe_list) == 2):

 

        template_name = "hold/template__SLH__fall__SE__rise__glitch__maxq__2.sp"

        return template_name

 

    if( arc_type == "hold" and

                fnmatch.fnmatch(cell_name, "SLH*QSO*") and

                constr_pin == "SE" and

                constr_pin_dir == "rise" and

                (rel_pin == "E" or rel_pin == "CLK") and

                rel_pin_dir == "rise" and

                        "D" in when and

                        not "!D" in when and

                        len(probe_list) == 2):

 

        template_name = "hold/template__SLH__rise__SE__rise__pushout__2.sp"

        return template_name

 

    if( arc_type == "hold" and

                fnmatch.fnmatch(cell_name, "SLH*QSO*") and

                constr_pin == "SE" and

                constr_pin_dir == "rise" and

                (rel_pin == "E" or rel_pin == "CLK") and

                rel_pin_dir == "rise" and

                        "!D" in when and

                        len(probe_list) == 2):

 

        template_name = "hold/template__SLH__rise__SE__rise__pushout__2.sp"

        return template_name

 

    if( arc_type == "hold" and

                fnmatch.fnmatch(cell_name, "SLH*QSO*") and

                constr_pin == "SE" and

                constr_pin_dir == "fall" and

                (rel_pin == "E" or rel_pin == "CLK") and

                rel_pin_dir == "fall" and

                        "D" in when and

                        not "!D" in when and

                        len(probe_list) == 2):

 

        template_name = "hold/template__SLH__fall__SE__fall__glitch__maxq__2.sp"

        return template_name

 

    if( arc_type == "hold" and

                fnmatch.fnmatch(cell_name, "SLH*QSO*") and

                constr_pin == "SE" and

                constr_pin_dir == "fall" and

                (rel_pin == "E" or rel_pin == "CLK") and

                rel_pin_dir == "fall" and

                        "!D" in when and

                        len(probe_list) == 2):

 

        template_name = "hold/template__SLH__fall__SE__fall__glitch__minq__2.sp"

        return template_name

 

    # SDFKSNQSO* CP->S from CW 2021/1/26 + SDFKCNQSO* & SEDFKCNQSO* 2021/1/27

    if( arc_type == "hold" and

                (fnmatch.fnmatch(cell_name, "SDFKSPQSO*") or fnmatch.fnmatch(cell_name, "SDFKCNQSO*") or fnmatch.fnmatch(cell_name, "SEDFKCNQSO*")) and

                                (fnmatch.fnmatch(constr_pin, "S") or fnmatch.fnmatch(constr_pin, "CN")) and

                constr_pin_dir == "rise" and

                fnmatch.fnmatch(rel_pin, "CP") and

                rel_pin_dir == "rise" and

                len(probe_list) == 2):

 

        template_name = "hold/template__SLH__rise__SE__rise__pushout__2.sp"

        return template_name

 

    if( arc_type == "hold" and

                (fnmatch.fnmatch(cell_name, "SDFKSPQSO*") or fnmatch.fnmatch(cell_name, "SDFKCNQSO*") or fnmatch.fnmatch(cell_name, "SEDFKCNQSO*")) and

                                (fnmatch.fnmatch(constr_pin, "S") or fnmatch.fnmatch(constr_pin, "CN")) and

                constr_pin_dir == "fall" and

                fnmatch.fnmatch(rel_pin, "CP") and

                rel_pin_dir == "rise" and

                len(probe_list) == 2):

 

        template_name = "hold/template__SLH__rise__SE__fall__pushout__2.sp"

        return \

            template_name

 

    # DIV2DFCNQ* CP->CDN from CW 2021/1/26 + MB*SRLSDFCNQ* 2021/1/27

    if( arc_type == "removal" and

                fnmatch.fnmatch(cell_name, "DIV2DFCNQ*") and

                                constr_pin == "CDN" and

                constr_pin_dir == "rise" and

                rel_pin == "CP" and

                rel_pin_dir == "rise" and

                len(probe_list) == 1):

 

        template_name = "hold/template__latch__rise__rise__glitch__maxq__1.sp"

        return template_name

 

    # DA/DB -> CP (OR2)

    if( arc_type == "hold" and

            fnmatch.fnmatch(cell_name, "MB8SRLSDFOR2*") and

            fnmatch.fnmatch(constr_pin, "DA*") and

            constr_pin_dir == "rise" and

            fnmatch.fnmatch(rel_pin, "CP") and

            rel_pin_dir == "rise" and

            len(probe_list) == 1):

       

        template_name = "hold/template__common__rise__DA__rise__1.sp"

        return template_name

 

    if( arc_type == "hold" and

            fnmatch.fnmatch(cell_name, "MB8SRLSDFOR2*") and

            fnmatch.fnmatch(constr_pin, "DA*") and

            constr_pin_dir == "fall" and

            fnmatch.fnmatch(rel_pin, "CP") and

            rel_pin_dir == "rise" and

            len(probe_list) == 1):

 

        template_name = "hold/template__common__rise__DA__fall__1.sp"

        return template_name

 

    if( arc_type == "hold" and

            fnmatch.fnmatch(cell_name, "MB8SRLSDFOR2*") and

            fnmatch.fnmatch(constr_pin, "DB*") and

            constr_pin_dir == "rise" and

            fnmatch.fnmatch(rel_pin, "CP") and

            rel_pin_dir == "rise" and

            len(probe_list) == 1):

 

        template_name = "hold/template__common__rise__DB__rise__1.sp"

        return template_name

 

    if( arc_type == "hold" and

            fnmatch.fnmatch(cell_name, "MB8SRLSDFOR2*") and

            fnmatch.fnmatch(constr_pin, "DB*") and

            constr_pin_dir == "fall" and

            fnmatch.fnmatch(rel_pin, "CP") and

            rel_pin_dir == "rise" and

            len(probe_list) == 1):

 

        template_name = "hold/template__common__rise__DB__fall__1.sp"

        return template_name

 

    # AOI22 (DA1....)

    if( arc_type == "hold" and

            fnmatch.fnmatch(cell_name, "MB2SRLSDFAO22*") and

            fnmatch.fnmatch(constr_pin, "DA1") and

            constr_pin_dir == "rise" and

            fnmatch.fnmatch(rel_pin, "CP") and

            rel_pin_dir == "rise" and

            len(probe_list) == 1):

 

        template_name = "hold/template__AO22__rise__DA1__rise__1.sp"

        return template_name

       

    if( arc_type == "hold" and

            fnmatch.fnmatch(cell_name, "MB2SRLSDFAO22*") and

            fnmatch.fnmatch(constr_pin, "DA2") and

            constr_pin_dir == "rise" and

            fnmatch.fnmatch(rel_pin, "CP") and

            rel_pin_dir == "rise" and

            len(probe_list) == 1):

 

        template_name = "hold/template__AO22__rise__DA2__rise__1.sp"

        return template_name

 

    if( arc_type == "hold" and

            fnmatch.fnmatch(cell_name, "MB2SRLSDFAO22*") and

            fnmatch.fnmatch(constr_pin, "DB1") and

            constr_pin_dir == "rise" and

            fnmatch.fnmatch(rel_pin, "CP") and

            rel_pin_dir == "rise" and

            len(probe_list) == 1):

 

        template_name = "hold/template__AO22__rise__DB1__rise__1.sp"

        return template_name

       

    if( arc_type == "hold" and

            fnmatch.fnmatch(cell_name, "MB2SRLSDFAO22*") and

            fnmatch.fnmatch(constr_pin, "DB2") and

            constr_pin_dir == "rise" and

            fnmatch.fnmatch(rel_pin, "CP") and

            rel_pin_dir == "rise" and

            len(probe_list) == 1):

 

        template_name = "hold/template__AO22__rise__DB2__rise__1.sp"

        return template_name

 

    if( arc_type == "hold" and

            fnmatch.fnmatch(cell_name, "MB2SRLSDFAO22*") and

            fnmatch.fnmatch(constr_pin, "DC1") and

            constr_pin_dir == "rise" and

            fnmatch.fnmatch(rel_pin, "CP") and

            rel_pin_dir == "rise" and

            len(probe_list) == 1):

 

        template_name = "hold/template__AO22__rise__DC1__rise__1.sp"

        return template_name

       

    if( arc_type == "hold" and

            fnmatch.fnmatch(cell_name, "MB2SRLSDFAO22*") and

            fnmatch.fnmatch(constr_pin, "DC2") and

            constr_pin_dir == "rise" and

            fnmatch.fnmatch(rel_pin, "CP") and

            rel_pin_dir == "rise" and

            len(probe_list) == 1):

 

        template_name = "hold/template__AO22__rise__DC2__rise__1.sp"

        return template_name

 

    if( arc_type == "hold" and

            fnmatch.fnmatch(cell_name, "MB2SRLSDFAO22*") and

            fnmatch.fnmatch(constr_pin, "DD1") and

            constr_pin_dir == "rise" and

            fnmatch.fnmatch(rel_pin, "CP") and

            rel_pin_dir == "rise" and

            len(probe_list) == 1):

 

        template_name = "hold/template__AO22__rise__DD1__rise__1.sp"

        return template_name

       

    if( arc_type == "hold" and

            fnmatch.fnmatch(cell_name, "MB2SRLSDFAO22*") and

            fnmatch.fnmatch(constr_pin, "DD2") and

            constr_pin_dir == "rise" and

            fnmatch.fnmatch(rel_pin, "CP") and

            rel_pin_dir == "rise" and

            len(probe_list) == 1):

 

        template_name = "hold/template__AO22__rise__DD2__rise__1.sp"

        return template_name

 

    if( arc_type == "hold" and

            fnmatch.fnmatch(cell_name, "MB2SRLSDFAO22*") and

            fnmatch.fnmatch(constr_pin, "DA1") and

            constr_pin_dir == "fall" and

            fnmatch.fnmatch(rel_pin, "CP") and

            rel_pin_dir == "rise" and

            len(probe_list) == 1):

 

        template_name = "hold/template__AO22__rise__DA1__fall__1.sp"

        return template_name

       

    if( arc_type == "hold" and

            fnmatch.fnmatch(cell_name, "MB2SRLSDFAO22*") and

            fnmatch.fnmatch(constr_pin, "DA2") and

            constr_pin_dir == "fall" and

            fnmatch.fnmatch(rel_pin, "CP") and

            rel_pin_dir == "rise" and

            len(probe_list) == 1):

 

        template_name = "hold/template__AO22__rise__DA2__fall__1.sp"

        return template_name

 

    if( arc_type == "hold" and

            fnmatch.fnmatch(cell_name, "MB2SRLSDFAO22*") and

            fnmatch.fnmatch(constr_pin, "DB1") and

            constr_pin_dir == "fall" and

            fnmatch.fnmatch(rel_pin, "CP") and

            rel_pin_dir == "rise" and

            len(probe_list) == 1):

 

        template_name = "hold/template__AO22__rise__DB1__fall__1.sp"

        return template_name

       

    if( arc_type == "hold" and

            fnmatch.fnmatch(cell_name, "MB2SRLSDFAO22*") and

            fnmatch.fnmatch(constr_pin, "DB2") and

            constr_pin_dir == "fall" and

            fnmatch.fnmatch(rel_pin, "CP") and

            rel_pin_dir == "rise" and

            len(probe_list) == 1):

 

        template_name = "hold/template__AO22__rise__DB2__fall__1.sp"

        return template_name

 

    if( arc_type == "hold" and

            fnmatch.fnmatch(cell_name, "MB2SRLSDFAO22*") and

            fnmatch.fnmatch(constr_pin, "DC1") and

            constr_pin_dir == "fall" and

            fnmatch.fnmatch(rel_pin, "CP") and

            rel_pin_dir == "rise" and

            len(probe_list) == 1):

 

        template_name = "hold/template__AO22__rise__DC1__fall__1.sp"

        return template_name

       

    if( arc_type == "hold" and

            fnmatch.fnmatch(cell_name, "MB2SRLSDFAO22*") and

            fnmatch.fnmatch(constr_pin, "DC2") and

            constr_pin_dir == "fall" and

            fnmatch.fnmatch(rel_pin, "CP") and

            rel_pin_dir == "rise" and

            len(probe_list) == 1):

 

        template_name = "hold/template__AO22__rise__DC2__fall__1.sp"

        return template_name

 

    if( arc_type == "hold" and

            fnmatch.fnmatch(cell_name, "MB2SRLSDFAO22*") and

            fnmatch.fnmatch(constr_pin, "DD1") and

            constr_pin_dir == "fall" and

            fnmatch.fnmatch(rel_pin, "CP") and

            rel_pin_dir == "rise" and

            len(probe_list) == 1):

 

        template_name = "hold/template__AO22__rise__DD1__fall__1.sp"

        return template_name

       

    if( arc_type == "hold" and

            fnmatch.fnmatch(cell_name, "MB2SRLSDFAO22*") and

            fnmatch.fnmatch(constr_pin, "DD2") and

            constr_pin_dir == "fall" and

            fnmatch.fnmatch(rel_pin, "CP") and

            rel_pin_dir == "rise" and

            len(probe_list) == 1):

 

        template_name = "hold/template__AO22__rise__DD2__fall__1.sp"

        return template_name

 

    # OA22 (DA1....)

    if( arc_type == "hold" and

            fnmatch.fnmatch(cell_name, "MB2SRLSDFOA22*") and

            fnmatch.fnmatch(constr_pin, "DA1") and

            constr_pin_dir == "rise" and

            fnmatch.fnmatch(rel_pin, "CP") and

            rel_pin_dir == "rise" and

            len(probe_list) == 1):

 

        template_name = "hold/template__OA22__rise__DA1__rise__1.sp"

        return template_name

       

    if( arc_type == "hold" and

            fnmatch.fnmatch(cell_name, "MB2SRLSDFOA22*") and

            fnmatch.fnmatch(constr_pin, "DA2") and

            constr_pin_dir == "rise" and

            fnmatch.fnmatch(rel_pin, "CP") and

            rel_pin_dir == "rise" and

            len(probe_list) == 1):

 

        template_name = "hold/template__OA22__rise__DA2__rise__1.sp"

        return template_name

 

    if( arc_type == "hold" and

            fnmatch.fnmatch(cell_name, "MB2SRLSDFOA22*") and

            fnmatch.fnmatch(constr_pin, "DB1") and

            constr_pin_dir == "rise" and

            fnmatch.fnmatch(rel_pin, "CP") and

            rel_pin_dir == "rise" and

            len(probe_list) == 1):

 

        template_name = "hold/template__OA22__rise__DB1__rise__1.sp"

        return template_name

       

    if( arc_type == "hold" and

            fnmatch.fnmatch(cell_name, "MB2SRLSDFOA22*") and

            fnmatch.fnmatch(constr_pin, "DB2") and

            constr_pin_dir == "rise" and

            fnmatch.fnmatch(rel_pin, "CP") and

            rel_pin_dir == "rise" and

            len(probe_list) == 1):

 

        template_name = "hold/template__OA22__rise__DB2__rise__1.sp"

        return template_name

 

    if( arc_type == "hold" and

            fnmatch.fnmatch(cell_name, "MB2SRLSDFOA22*") and

            fnmatch.fnmatch(constr_pin, "DC1") and

            constr_pin_dir == "rise" and

            fnmatch.fnmatch(rel_pin, "CP") and

            rel_pin_dir == "rise" and

            len(probe_list) == 1):

 

        template_name = "hold/template__OA22__rise__DC1__rise__1.sp"

        return template_name

       

    if( arc_type == "hold" and

            fnmatch.fnmatch(cell_name, "MB2SRLSDFOA22*") and

            fnmatch.fnmatch(constr_pin, "DC2") and

            constr_pin_dir == "rise" and

            fnmatch.fnmatch(rel_pin, "CP") and

            rel_pin_dir == "rise" and

            len(probe_list) == 1):

 

        template_name = "hold/template__OA22__rise__DC2__rise__1.sp"

        return template_name

 

    if( arc_type == "hold" and

            fnmatch.fnmatch(cell_name, "MB2SRLSDFOA22*") and

            fnmatch.fnmatch(constr_pin, "DD1") and

            constr_pin_dir == "rise" and

            fnmatch.fnmatch(rel_pin, "CP") and

            rel_pin_dir == "rise" and

            len(probe_list) == 1):

 

        template_name = "hold/template__OA22__rise__DD1__rise__1.sp"

        return template_name

       

    if( arc_type == "hold" and

            fnmatch.fnmatch(cell_name, "MB2SRLSDFOA22*") and

            fnmatch.fnmatch(constr_pin, "DD2") and

            constr_pin_dir == "rise" and

            fnmatch.fnmatch(rel_pin, "CP") and

            rel_pin_dir == "rise" and

            len(probe_list) == 1):

 

        template_name = "hold/template__OA22__rise__DD2__rise__1.sp"

        return template_name

 

    if( arc_type == "hold" and

            fnmatch.fnmatch(cell_name, "MB2SRLSDFOA22*") and

            fnmatch.fnmatch(constr_pin, "DA1") and

            constr_pin_dir == "fall" and

            fnmatch.fnmatch(rel_pin, "CP") and

            rel_pin_dir == "rise" and

            len(probe_list) == 1):

 

        template_name = "hold/template__OA22__rise__DA1__fall__1.sp"

        return template_name

       

    if( arc_type == "hold" and

            fnmatch.fnmatch(cell_name, "MB2SRLSDFOA22*") and

            fnmatch.fnmatch(constr_pin, "DA2") and

            constr_pin_dir == "fall" and

            fnmatch.fnmatch(rel_pin, "CP") and

            rel_pin_dir == "rise" and

            len(probe_list) == 1):

 

        template_name = "hold/template__OA22__rise__DA2__fall__1.sp"

        return template_name

 

    if( arc_type == "hold" and

            fnmatch.fnmatch(cell_name, "MB2SRLSDFOA22*") and

            fnmatch.fnmatch(constr_pin, "DB1") and

            constr_pin_dir == "fall" and

            fnmatch.fnmatch(rel_pin, "CP") and

            rel_pin_dir == "rise" and

            len(probe_list) == 1):

 

        template_name = "hold/template__OA22__rise__DB1__fall__1.sp"

        return template_name

       

    if( arc_type == "hold" and

            fnmatch.fnmatch(cell_name, "MB2SRLSDFOA22*") and

            fnmatch.fnmatch(constr_pin, "DB2") and

            constr_pin_dir == "fall" and

            fnmatch.fnmatch(rel_pin, "CP") and

            rel_pin_dir == "rise" and

            len(probe_list) == 1):

 

        template_name = "hold/template__OA22__rise__DB2__fall__1.sp"

        return template_name

 

    if( arc_type == "hold" and

            fnmatch.fnmatch(cell_name, "MB2SRLSDFOA22*") and

            fnmatch.fnmatch(constr_pin, "DC1") and

            constr_pin_dir == "fall" and

            fnmatch.fnmatch(rel_pin, "CP") and

            rel_pin_dir == "rise" and

            len(probe_list) == 1):

 

        template_name = "hold/template__OA22__rise__DC1__fall__1.sp"

        return template_name

       

    if( arc_type == "hold" and

            fnmatch.fnmatch(cell_name, "MB2SRLSDFOA22*") and

            fnmatch.fnmatch(constr_pin, "DC2") and

            constr_pin_dir == "fall" and

            fnmatch.fnmatch(rel_pin, "CP") and

            rel_pin_dir == "rise" and

            len(probe_list) == 1):

 

        template_name = "hold/template__OA22__rise__DC2__fall__1.sp"

        return template_name

 

    if( arc_type == "hold" and

            fnmatch.fnmatch(cell_name, "MB2SRLSDFOA22*") and

            fnmatch.fnmatch(constr_pin, "DD1") and

            constr_pin_dir == "fall" and

            fnmatch.fnmatch(rel_pin, "CP") and

            rel_pin_dir == "rise" and

            len(probe_list) == 1):

 

        template_name = "hold/template__OA22__rise__DD1__fall__1.sp"

        return template_name

       

    if( arc_type == "hold" and

            fnmatch.fnmatch(cell_name, "MB2SRLSDFOA22*") and

            fnmatch.fnmatch(constr_pin, "DD2") and

            constr_pin_dir == "fall" and

            fnmatch.fnmatch(rel_pin, "CP") and

            rel_pin_dir == "rise" and

            len(probe_list) == 1):

 

        template_name = "hold/template__OA22__rise__DD2__fall__1.sp"

        return template_name

 

    # MB*SRLSDF* cell for constr_pin = D*, rel_pin = CP 2021/1/14 from CW

    if( arc_type == "hold" and

            fnmatch.fnmatch(cell_name, "MB*SRLSDF*") and

            fnmatch.fnmatch(constr_pin, "D*") and

            constr_pin_dir == "rise" and

            fnmatch.fnmatch(rel_pin, "CP") and

            rel_pin_dir == "rise" and

            (("ml1_ax" in probe_list) or ("ml2_ax" in probe_list) or ("ml3_ax" in probe_list) or ("ml4_ax" in probe_list))):

       

        template_name = "hold/template__MB__rise__rise__20__percent__glitch__minq__1.sp"

        return template_name

   

    if( arc_type == "hold" and

            fnmatch.fnmatch(cell_name, "MB*SRLSDF*") and

            fnmatch.fnmatch(constr_pin, "D*") and

            constr_pin_dir == "rise" and

            fnmatch.fnmatch(rel_pin, "CP") and

            rel_pin_dir == "rise" and

            (("ml1_a" in probe_list) or ("ml2_a" in probe_list) or ("ml3_a" in probe_list) or ("ml4_a" in probe_list))):

 

        template_name = "hold/template__MB__rise__rise__20__percent__glitch__maxq__1.sp"

        return template_name

 

    if( arc_type == "hold" and

            fnmatch.fnmatch(cell_name, "MB*SRLSDF*") and

            fnmatch.fnmatch(constr_pin, "D*") and

            constr_pin_dir == "fall" and

            fnmatch.fnmatch(rel_pin, "CP") and

            rel_pin_dir == "rise" and

            (("ml1_ax" in probe_list) or ("ml2_ax" in probe_list) or ("ml3_ax" in probe_list) or ("ml4_ax" in probe_list))):

 

        template_name = "hold/template__MB__rise__fall__20__percent__glitch__maxq__1.sp"

        return template_name

 

    if( arc_type == "hold" and

            fnmatch.fnmatch(cell_name, "MB*SRLSDF*") and

            fnmatch.fnmatch(constr_pin, "D*") and

            constr_pin_dir == "fall" and

            fnmatch.fnmatch(rel_pin, "CP") and

            rel_pin_dir == "rise" and

            (("ml1_a" in probe_list) or ("ml2_a" in probe_list) or ("ml3_a" in probe_list) or ("ml4_a" in probe_list))):

 

        template_name = "hold/template__MB__rise__fall__20__percent__glitch__minq__1.sp"

        return template_name

   

    # DFDETRPQ (CP pin)

    if( arc_type == "hold" and

                fnmatch.fnmatch(cell_name, "*DFDETQNRESO*") and

                fnmatch.fnmatch(constr_pin, "D*") and

                constr_pin_dir == "rise" and

                fnmatch.fnmatch(rel_pin, "CP") and

                rel_pin_dir == "rise" and

                len(probe_list) == 2):

 

        template_name = "hold/template__DETRESO__rise__rise__2.sp"

        return template_name

 

    if( arc_type == "hold" and

            fnmatch.fnmatch(cell_name, "*DFDET*") and

            fnmatch.fnmatch(constr_pin, "D*") and

            constr_pin_dir == "rise" and

            fnmatch.fnmatch(rel_pin, "CP") and

            rel_pin_dir == "rise" and

            len(probe_list) == 1):

 

        template_name = "hold/template__SLH__rise__SE__rise__pushout__3.sp"

        return template_name

 

    if( arc_type == "hold" and

                fnmatch.fnmatch(cell_name, "*DFDETQNRESO*") and

                fnmatch.fnmatch(constr_pin, "D*") and

                constr_pin_dir == "fall" and

                fnmatch.fnmatch(rel_pin, "CP") and

                rel_pin_dir == "rise" and

                len(probe_list) == 2):

 

        template_name = "hold/template__DETRESO__rise__fall__2.sp"

        return template_name

 

    if( arc_type == "hold" and

            fnmatch.fnmatch(cell_name, "*DFDET*") and

            fnmatch.fnmatch(constr_pin, "D*") and

            constr_pin_dir == "fall" and

            fnmatch.fnmatch(rel_pin, "CP") and

            rel_pin_dir == "rise" and

            len(probe_list) == 1):

 

        template_name = "hold/template__SLH__rise__SE__fall__pushout__3.sp"

        return template_name

 

    if( arc_type == "hold" and

            (fnmatch.fnmatch(cell_name, "*DFDETQNRESO*") or fnmatch.fnmatch(cell_name, "*DFDETQNLTSO*")) and

            fnmatch.fnmatch(constr_pin, "D*") and

            constr_pin_dir == "rise" and

            fnmatch.fnmatch(rel_pin, "CP") and

            rel_pin_dir == "fall" ):

 

        template_name = "hold/template__DET__fall__SE__rise__pushout__1.sp"

        return template_name

 

    if( arc_type == "hold" and

            fnmatch.fnmatch(cell_name, "*DFDET*") and

            fnmatch.fnmatch(constr_pin, "D*") and

            constr_pin_dir == "rise" and

            fnmatch.fnmatch(rel_pin, "CP") and

            rel_pin_dir == "fall" and

            len(probe_list) == 1):

 

        template_name = "hold/template__SLH__fall__SE__rise__pushout__3.sp"

        return template_name

 

    if( arc_type == "hold" and

            fnmatch.fnmatch(cell_name, "*DFDETQNLTSO*") and

            fnmatch.fnmatch(constr_pin, "D*") and

            constr_pin_dir == "fall" and

            fnmatch.fnmatch(rel_pin, "CP") and

            rel_pin_dir == "fall"):

 

        template_name = "hold/template__DETLTSO__D__fall__CP__fall__pushout__1.sp"

        return template_name

 

    if( arc_type == "hold" and

            fnmatch.fnmatch(cell_name, "*DFDETQNRESO*") and

            fnmatch.fnmatch(constr_pin, "D*") and

            constr_pin_dir == "fall" and

            fnmatch.fnmatch(rel_pin, "CP") and

            rel_pin_dir == "fall" and

            len(probe_list) == 1):

 

        template_name = "hold/template__DET__fall__SE__fall__pushout__1.sp"

        return template_name

 

    if( arc_type == "hold" and

            fnmatch.fnmatch(cell_name, "*DFDET*") and

            fnmatch.fnmatch(constr_pin, "D*") and

            constr_pin_dir == "fall" and

            fnmatch.fnmatch(rel_pin, "CP") and

            rel_pin_dir == "fall" and

            len(probe_list) == 1):

 

        template_name = "hold/template__SLH__fall__SE__fall__pushout__3.sp"

        return template_name

 

    # Common (CP pins) template

    if( arc_type == "hold" and

                (fnmatch.fnmatch(constr_pin, "D*") or fnmatch.fnmatch(constr_pin, "S*") or fnmatch.fnmatch(constr_pin, "CN*")) and

                constr_pin_dir == "rise" and

                fnmatch.fnmatch(rel_pin, "CP") and

                rel_pin_dir == "rise" and

                len(probe_list) == 1):

 

        template_name = "hold/template__common__rise__rise__1.sp"

        return template_name

 

 

    if( arc_type == "hold" and

                fnmatch.fnmatch(constr_pin, "D*") and

                constr_pin_dir == "rise" and

                fnmatch.fnmatch(rel_pin, "CP") and

                rel_pin_dir == "rise" and

                len(probe_list) == 2):

 

        template_name = "hold/template__common__rise__rise__2.sp"

        return template_name

 

 

    if( arc_type == "hold" and

                (fnmatch.fnmatch(constr_pin, "D*") or fnmatch.fnmatch(constr_pin, "S*") or fnmatch.fnmatch(constr_pin, "CN*")) and

                constr_pin_dir == "fall" and

                fnmatch.fnmatch(rel_pin, "CP") and

                rel_pin_dir == "rise" and

                len(probe_list) == 1):

 

        template_name = "hold/template__common__rise__fall__1.sp"

        return template_name

 

    if( arc_type == "hold" and

                fnmatch.fnmatch(constr_pin, "D*") and

                constr_pin_dir == "fall" and

                fnmatch.fnmatch(rel_pin, "CP") and

                rel_pin_dir == "rise" and

                len(probe_list) == 2):

 

        template_name = "hold/template__common__rise__fall__2.sp"

        return template_name

 

    # CP -> C/SN

    if( arc_type == "hold" and

                fnmatch.fnmatch(constr_pin, "C") and

                constr_pin_dir == "rise" and

                fnmatch.fnmatch(rel_pin, "CP") and

                rel_pin_dir == "rise" and

                len(probe_list) == 1):

 

        template_name = "hold/template__common__rise__rise__1.sp"

        return template_name

 

 

    if( arc_type == "hold" and

                fnmatch.fnmatch(constr_pin, "C") and

                constr_pin_dir == "rise" and

                fnmatch.fnmatch(rel_pin, "CP") and

                rel_pin_dir == "rise" and

                len(probe_list) == 2):

 

        template_name = "hold/template__common__rise__rise__2.sp"

        return template_name

 

 

    if( arc_type == "hold" and

                fnmatch.fnmatch(constr_pin, "C") and

                constr_pin_dir == "fall" and

                fnmatch.fnmatch(rel_pin, "CP") and

                rel_pin_dir == "rise" and

                len(probe_list) == 1):

 

        template_name = "hold/template__common__rise__fall__1.sp"

        return \

            template_name

 

    if( arc_type == "hold" and

                fnmatch.fnmatch(constr_pin, "C") and

                constr_pin_dir == "fall" and

                fnmatch.fnmatch(rel_pin, "CP") and

                rel_pin_dir == "rise" and

                len(probe_list) == 2):

 

        template_name = "hold/template__common__rise__fall__2.sp"

        return template_name

 

    if( arc_type == "hold" and

                fnmatch.fnmatch(constr_pin, "SN") and

                constr_pin_dir == "rise" and

                fnmatch.fnmatch(rel_pin, "CP") and

                rel_pin_dir == "rise" and

                len(probe_list) == 1):

 

        template_name = "hold/template__common__rise__rise__1.sp"

        return template_name

 

 

    if( arc_type == "hold" and

                fnmatch.fnmatch(constr_pin, "SN") and

                constr_pin_dir == "rise" and

                fnmatch.fnmatch(rel_pin, "CP") and

                rel_pin_dir == "rise" and

                len(probe_list) == 2):

 

        template_name = "hold/template__common__rise__rise__2.sp"

        return template_name

 

 

    if( arc_type == "hold" and

                fnmatch.fnmatch(constr_pin, "SN") and

                constr_pin_dir == "fall" and

                fnmatch.fnmatch(rel_pin, "CP") and

                rel_pin_dir == "rise" and

                len(probe_list) == 1):

 

        template_name = "hold/template__common__rise__fall__1.sp"

        return \

            template_name

 

    if( arc_type == "hold" and

                fnmatch.fnmatch(constr_pin, "SN") and

                constr_pin_dir == "fall" and

                fnmatch.fnmatch(rel_pin, "CP") and

                rel_pin_dir == "rise" and

                len(probe_list) == 2):

 

        template_name = "hold/template__common__rise__fall__2.sp"

        return template_name

 

    # CPN->D SYNC* cell from CW 2021/1/21

#    if( arc_type == "hold" and

#                fnmatch.fnmatch(cell_name, "DFNSYNC1P5*Q*") and

#                constr_pin == "D" and

#                constr_pin_dir == "rise" and

#                rel_pin == "CPN" and

#                rel_pin_dir == "fall" and

#                "Q1" in probe_list):

#

#        template_name = "hold/template__latch__fall__rise__glitch__maxq__1.sp"

#        return template_name

 

    if( arc_type == "hold" and

                fnmatch.fnmatch(cell_name, "DFNSYNC1P5*Q*") and

                constr_pin == "D" and

                constr_pin_dir == "fall" and

                rel_pin == "CPN" and

                rel_pin_dir == "fall" and

                "Q1" in probe_list):

 

        template_name = "hold/template__latch__fall__fall__glitch__minq__1.sp"

        return template_name

 

    # Common (CPN pins) template

    if( arc_type == "hold" and

                (fnmatch.fnmatch(constr_pin, "D*") or fnmatch.fnmatch(constr_pin, "CN") or fnmatch.fnmatch(constr_pin, "S")) and

                constr_pin_dir == "rise" and

                fnmatch.fnmatch(rel_pin, "CPN") and

                rel_pin_dir == "fall" ):

 

        template_name = "hold/template__common__fall__rise__1.sp"

        return template_name

 

 

    if( arc_type == "hold" and

                (fnmatch.fnmatch(constr_pin, "D*") or fnmatch.fnmatch(constr_pin, "CN") or fnmatch.fnmatch(constr_pin, "S")) and

                constr_pin_dir == "fall" and

                fnmatch.fnmatch(rel_pin, "CPN") and

                rel_pin_dir == "fall" ):

 

        template_name = "hold/template__common__fall__fall__1.sp"

        return template_name

 

    # WWL -> D

    if( arc_type == "hold" and

                fnmatch.fnmatch(cell_name, "*QN*") and

                fnmatch.fnmatch(constr_pin, "D*") and

                constr_pin_dir == "rise" and

                (fnmatch.fnmatch(rel_pin, "WWL") or fnmatch.fnmatch(rel_pin, "WWL0")) and

                rel_pin_dir == "fall"):

 

        template_name = "hold/template__basemeg__fall__rise__WWL__QN__glitch__maxq__1.sp"

        return template_name

 

 

    if( arc_type == "hold" and

                fnmatch.fnmatch(cell_name, "*QN*") and

                fnmatch.fnmatch(constr_pin, "D*") and

                constr_pin_dir == "fall" and

                (fnmatch.fnmatch(rel_pin, "WWL") or fnmatch.fnmatch(rel_pin, "WWL0")) and

                rel_pin_dir == "fall"):

 

        template_name = "hold/template__basemeg__fall__rise__WWL__QN__glitch__minq__1.sp"

        return template_name

 

    # basemeg WWL* -> D  06/24 update for N3

    if( arc_type == "hold" and

                fnmatch.fnmatch(constr_pin, "D*") and

                constr_pin_dir == "rise" and

                fnmatch.fnmatch(rel_pin, "WWL") and

                rel_pin_dir == "fall" ):

 

        template_name = "hold/template__basemeg__WWL__fall__rise__glitch__maxq__1.sp"

        return template_name

 

    if( arc_type == "hold" and

                fnmatch.fnmatch(constr_pin, "D*") and

                constr_pin_dir == "rise" and

                fnmatch.fnmatch(rel_pin, "WWL_N") and

                rel_pin_dir == "rise" ):

 

        template_name = "hold/template__basemeg__WWL_N__rise__rise__glitch__maxq__1.sp"

        return template_name

 

    if( arc_type == "hold" and

                fnmatch.fnmatch(constr_pin, "D*") and

                constr_pin_dir == "fall" and

                fnmatch.fnmatch(rel_pin, "WWL") and

                rel_pin_dir == "fall" ):

 

        template_name = "hold/template__basemeg__WWL__fall__fall__glitch__minq__1.sp"

        return template_name

 

    if( arc_type == "hold" and

                fnmatch.fnmatch(constr_pin, "D*") and

                constr_pin_dir == "fall" and

                (fnmatch.fnmatch(rel_pin, "WWL_N")) and

                rel_pin_dir == "rise" ):

 

        template_name = "hold/template__basemeg__WWL_N__rise__fall__glitch__minq__1.sp"

        return template_name

 

    if( arc_type == "hold" and

                fnmatch.fnmatch(constr_pin, "D*") and

                constr_pin_dir == "rise" and

                fnmatch.fnmatch(rel_pin, "WWL0") and

                rel_pin_dir == "fall" ):

 

        template_name = "hold/template__basemeg__WWL0__fall__rise__glitch__maxq__1.sp"

        return template_name

 

    if( arc_type == "hold" and

                fnmatch.fnmatch(constr_pin, "D*") and

                constr_pin_dir == "rise" and

                fnmatch.fnmatch(rel_pin, "WWL0_N") and

                rel_pin_dir == "rise" and

                ("QN" in probe_list or "QN1" in probe_list or "QN0" in probe_list)):

 

        template_name = "hold/template__basemeg__WWL0_N__rise__rise__glitch__minq__1.sp"

        return template_name

 

    if( arc_type == "hold" and

                fnmatch.fnmatch(constr_pin, "D*") and

                constr_pin_dir == "rise" and

                fnmatch.fnmatch(rel_pin, "WWL0_N") and

                rel_pin_dir == "rise" ):

 

        template_name = "hold/template__basemeg__WWL0_N__rise__rise__glitch__maxq__1.sp"

        return template_name

 

    if( arc_type == "hold" and

                fnmatch.fnmatch(constr_pin, "D*") and

                constr_pin_dir == "fall" and

                fnmatch.fnmatch(rel_pin, "WWL0") and

                rel_pin_dir == "fall" ):

 

        template_name = "hold/template__basemeg__WWL0__fall__fall__glitch__minq__1.sp"

        return template_name

 

    if( arc_type == "hold" and

                fnmatch.fnmatch(constr_pin, "D*") and

                constr_pin_dir == "fall" and

                (fnmatch.fnmatch(rel_pin, "WWL0_N")) and

                rel_pin_dir == "rise" and

                ("QN" in probe_list or "QN1" in probe_list or "QN0" in probe_list)):

 

        template_name = "hold/template__basemeg__WWL0_N__rise__fall__glitch__maxq__1.sp"

        return template_name

 

    if( arc_type == "hold" and

                fnmatch.fnmatch(constr_pin, "D*") and

                constr_pin_dir == "fall" and

                (fnmatch.fnmatch(rel_pin, "WWL0_N")) and

                rel_pin_dir == "rise" ):

 

        template_name = "hold/template__basemeg__WWL0_N__rise__fall__glitch__minq__1.sp"

        return template_name

 

    if( arc_type == "hold" and

                fnmatch.fnmatch(constr_pin, "D*") and

                constr_pin_dir == "rise" and

                fnmatch.fnmatch(rel_pin, "WWL1") and

                rel_pin_dir == "fall" and

                ("QN" in probe_list or "QN1" in probe_list or "QN0" in probe_list)):

 

        template_name = "hold/template__basemeg__WWL1__fall__rise__glitch__minq__1.sp"

        return template_name

 

    if( arc_type == "hold" and

                fnmatch.fnmatch(constr_pin, "D*") and

                constr_pin_dir == "rise" and

                fnmatch.fnmatch(rel_pin, "WWL1") and

                rel_pin_dir == "fall" ):

 

        template_name = "hold/template__basemeg__WWL1__fall__rise__glitch__maxq__1.sp"

        return template_name

 

    if( arc_type == "hold" and

                fnmatch.fnmatch(constr_pin, "D*") and

                constr_pin_dir == "rise" and

                fnmatch.fnmatch(rel_pin, "WWL1_N") and

                rel_pin_dir == "rise" and

                ("QN" in probe_list or "QN1" in probe_list or "QN0" in probe_list)):

 

        template_name = "hold/template__basemeg__WWL1_N__rise__rise__glitch__minq__1.sp"

 

    if( arc_type == "hold" and

                fnmatch.fnmatch(constr_pin, "D*") and

                constr_pin_dir == "rise" and

                fnmatch.fnmatch(rel_pin, "WWL1_N") and

                rel_pin_dir == "rise" ):

 

        template_name = "hold/template__basemeg__WWL1_N__rise__rise__glitch__maxq__1.sp"

        return template_name

   

    if( arc_type == "hold" and

                fnmatch.fnmatch(constr_pin, "D*") and

                constr_pin_dir == "fall" and

                fnmatch.fnmatch(rel_pin, "WWL1") and

                rel_pin_dir == "fall" and

                ("QN" in probe_list or "QN1" in probe_list or "QN0" in probe_list)):

 

        template_name = "hold/template__basemeg__WWL1__fall__fall__glitch__maxq__1.sp"

 

    if( arc_type == "hold" and

                fnmatch.fnmatch(constr_pin, "D*") and

                constr_pin_dir == "fall" and

                fnmatch.fnmatch(rel_pin, "WWL1") and

                rel_pin_dir == "fall" ):

 

        template_name = "hold/template__basemeg__WWL1__fall__fall__glitch__minq__1.sp"

        return template_name

 

    if( arc_type == "hold" and

                fnmatch.fnmatch(constr_pin, "D*") and

                constr_pin_dir == "fall" and

                (fnmatch.fnmatch(rel_pin, "WWL1_N")) and

                rel_pin_dir == "rise" and

                ("QN" in probe_list or "QN1" in probe_list or "QN0" in probe_list)):

 

        template_name = "hold/template__basemeg__WWL1_N__rise__fall__glitch__maxq__1.sp"

        return template_name

 

    if( arc_type == "hold" and

                fnmatch.fnmatch(constr_pin, "D*") and

                constr_pin_dir == "fall" and

                (fnmatch.fnmatch(rel_pin, "WWL1_N")) and

                rel_pin_dir == "rise" ):

 

        template_name = "hold/template__basemeg__WWL1_N__rise__fall__glitch__minq__1.sp"

        return template_name

 

    # basemeg LHAO22 E&EN -> A*/B* (differential enable)

    if( arc_type == "hold" and

                fnmatch.fnmatch(constr_pin, "A*") and

                constr_pin_dir == "rise" and

                rel_pin == "E" and

                rel_pin_dir == "fall"):

 

        template_name = "hold/template__basemeg__E__fall__A__rise__glitch__maxq__1.sp"

        return template_name

 

    if( arc_type == "hold" and

                fnmatch.fnmatch(constr_pin, "A*") and

                constr_pin_dir == "rise" and

                rel_pin == "EN" and

                rel_pin_dir == "rise"):

 

        template_name = "hold/template__basemeg__EN__rise__A__rise__glitch__maxq__1.sp"

        return template_name

 

    if( arc_type == "hold" and

                fnmatch.fnmatch(constr_pin, "A*") and

                constr_pin_dir == "fall" and

                rel_pin == "E" and

                rel_pin_dir == "fall"):

 

        template_name = "hold/template__basemeg__E__fall__A__fall__glitch__minq__1.sp"

        return template_name

 

    if( arc_type == "hold" and

                fnmatch.fnmatch(constr_pin, "A*") and

                constr_pin_dir == "fall" and

                rel_pin == "EN" and

                rel_pin_dir == "rise"):

 

        template_name = "hold/template__basemeg__EN__rise__A__fall__glitch__minq__1.sp"

        return template_name

 

    if( arc_type == "hold" and

                fnmatch.fnmatch(constr_pin, "B*") and

                constr_pin_dir == "rise" and

                rel_pin == "E" and

                rel_pin_dir == "fall"):

 

        template_name = "hold/template__basemeg__E__fall__B__rise__glitch__maxq__1.sp"

        return template_name

 

    if( arc_type == "hold" and

                fnmatch.fnmatch(constr_pin, "B*") and

                constr_pin_dir == "rise" and

                rel_pin == "EN" and

                rel_pin_dir == "rise"):

 

        template_name = "hold/template__basemeg__EN__rise__B__rise__glitch__maxq__1.sp"

        return template_name

 

    if( arc_type == "hold" and

                fnmatch.fnmatch(constr_pin, "B*") and

                constr_pin_dir == "fall" and

                rel_pin == "E" and

                rel_pin_dir == "fall"):

 

        template_name = "hold/template__basemeg__E__fall__B__fall__glitch__minq__1.sp"

        return template_name

 

    if( arc_type == "hold" and

                fnmatch.fnmatch(constr_pin, "B*") and

                constr_pin_dir == "fall" and

                rel_pin == "EN" and

                rel_pin_dir == "rise"):

 

        template_name = "hold/template__basemeg__EN__rise__B__fall__glitch__minq__1.sp"

        return template_name

 

    # base3p

    if( arc_type == "hold" and

                fnmatch.fnmatch(constr_pin, "SA") and

                constr_pin_dir == "rise" and

                fnmatch.fnmatch(rel_pin, "CP") and

                rel_pin_dir == "rise" and

                len(probe_list) == 1):

 

        template_name = "hold/template__common__rise__rise__1.sp"

        return template_name

 

    if( arc_type == "hold" and

                fnmatch.fnmatch(constr_pin, "SA") and

                constr_pin_dir == "fall" and

                fnmatch.fnmatch(rel_pin, "CP") and

                rel_pin_dir == "rise" and

                len(probe_list) == 1):

 

        template_name = "hold/template__common__rise__fall__1.sp"

        return template_name

 

    # MBMEG Latch 2021/1/21 update for LN/LH difference deck from CW

    if( arc_type == "hold" and

                fnmatch.fnmatch(cell_name, "MB*LN*QN*") and

                fnmatch.fnmatch(constr_pin, "D*") and

                constr_pin_dir == "rise" and

                (rel_pin == "EN") and

                rel_pin_dir == "rise"):

 

        template_name = "hold/template__latch__rise__rise__glitch__minq__1.sp"

        return template_name

 

    if( arc_type == "hold" and

                fnmatch.fnmatch(cell_name, "MB*LN*QN*") and

                fnmatch.fnmatch(constr_pin, "D*") and

                constr_pin_dir == "fall" and

                (rel_pin == "EN") and

                rel_pin_dir == "rise"):

 

        template_name = "hold/template__latch__rise__fall__glitch__maxq__1.sp"

        return template_name

 

    if( arc_type == "hold" and

                fnmatch.fnmatch(cell_name, "MB*LH*QN*") and

                fnmatch.fnmatch(constr_pin, "D*") and

                constr_pin_dir == "rise" and

                (rel_pin == "E") and

                rel_pin_dir == "fall"):

 

        template_name = "hold/template__latch__fall__rise__glitch__minq__1.sp"

        return template_name

 

    if( arc_type == "hold" and

                fnmatch.fnmatch(cell_name, "MB*LH*QN*") and

                fnmatch.fnmatch(constr_pin, "D*") and

                constr_pin_dir == "fall" and

                (rel_pin == "E") and

                rel_pin_dir == "fall"):

 

        template_name = "hold/template__latch__fall__fall__glitch__maxq__1.sp"

        return template_name

 

    # MB*SRLSDFQN* cell for constr_pin = E/TE, rel_pin = CP 1/18 from CW for mbficg

    if( arc_type == "hold" and

                fnmatch.fnmatch(cell_name, "MB*SRLSDFQN*") and

                (fnmatch.fnmatch(constr_pin, "E") or fnmatch.fnmatch(constr_pin, "TE")) and

                constr_pin_dir == "fall" and

                rel_pin == "CP" and

                rel_pin_dir == "rise" and

                len(probe_list) == 1):

 

        template_name = "hold/template__MB__rise__E__fall__pushout__maxq__1.sp"

        return template_name

 

    if( arc_type == "hold" and

                fnmatch.fnmatch(cell_name, "MB*SRLSDFQN*") and

                (fnmatch.fnmatch(constr_pin, "E") or fnmatch.fnmatch(constr_pin, "TE")) and

                constr_pin_dir == "rise" and

                rel_pin == "CP" and

                rel_pin_dir == "rise" and

                len(probe_list) == 1):

 

        template_name = "hold/template__MB__rise__E__rise__glitch__minq__1.sp"

        return template_name

 

    # MB*SRLSDF* cell for constr_pin = E/TE, rel_pin = CP 2021/1/14 from CW

    if( arc_type == "hold" and

                fnmatch.fnmatch(cell_name, "MB*SRLSDFKRP*") and

                (fnmatch.fnmatch(constr_pin, "E") or fnmatch.fnmatch(constr_pin, "TE")) and

                constr_pin_dir == "fall" and

                rel_pin == "CP" and

                rel_pin_dir == "rise" and

                len(probe_list) == 1):

 

        template_name = "hold/template__MB__rise__E__fall__pushout__maxq__1.sp"

        return template_name

 

    if( arc_type == "hold" and

                fnmatch.fnmatch(cell_name, "MB*SRLSDF*") and

                (fnmatch.fnmatch(constr_pin, "E") or fnmatch.fnmatch(constr_pin, "TE")) and

                constr_pin_dir == "fall" and

                rel_pin == "CP" and

                rel_pin_dir == "rise" and

                len(probe_list) == 1):

 

        template_name = "hold/template__MB__rise__E__fall__pushout__minq__1.sp"

        return template_name

 

    if( arc_type == "hold" and

                fnmatch.fnmatch(cell_name, "MB*SRLSDFKRP*") and

                (fnmatch.fnmatch(constr_pin, "E") or fnmatch.fnmatch(constr_pin, "TE")) and

                constr_pin_dir == "rise" and

                rel_pin == "CP" and

                rel_pin_dir == "rise" and

                len(probe_list) == 1):

 

        template_name = "hold/template__MB__rise__E__rise__glitch__minq__1.sp"

        return template_name

 

    if( arc_type == "hold" and

                fnmatch.fnmatch(cell_name, "MB*SRLSDF*ICG*") and

                (fnmatch.fnmatch(constr_pin, "E") or fnmatch.fnmatch(constr_pin, "TE")) and

                constr_pin_dir == "rise" and

                rel_pin == "CP" and

                rel_pin_dir == "rise" and

                len(probe_list) == 1):

 

        template_name = "hold/template__MB__notD__rise__E__rise__glitch__minq__1.sp"

        return template_name

 

    if( arc_type == "hold" and

                fnmatch.fnmatch(cell_name, "MB*SRLSDF*") and

                (fnmatch.fnmatch(constr_pin, "E") or fnmatch.fnmatch(constr_pin, "TE")) and

                constr_pin_dir == "rise" and

                rel_pin == "CP" and

                rel_pin_dir == "rise" and

                len(probe_list) == 1):

 

        template_name = "hold/template__MB__rise__E__rise__glitch__maxq__1.sp"

        return template_name

 

    # CKLHQRCB/CKLNQRCB/SLHQ*ITL 2020/12/18 update from CW

    if( arc_type == "hold" and

                constr_pin == "TE" and

                constr_pin_dir == "rise" and

                rel_pin == "CPN" and

                rel_pin_dir == "fall"):

 

        template_name = "hold/template__latch__fall__rise__glitch__minq__1.sp"

        return template_name

 

    if( arc_type == "hold" and

                constr_pin == "OV" and

                constr_pin_dir == "rise" and

                rel_pin == "CPN" and

                rel_pin_dir == "fall"):

 

        template_name = "hold/template__latch__fall__rise__glitch__minq__1.sp"

        return template_name

 

 

    if( arc_type == "hold" and

                constr_pin == "TE" and

                constr_pin_dir == "fall" and

                rel_pin == "CPN" and

                rel_pin_dir == "fall"):

 

        template_name = "hold/template__latch__fall__fall__pushout__1.sp"

        return template_name

 

    if( arc_type == "hold" and

                constr_pin == "TE" and

                constr_pin_dir == "rise" and

                rel_pin == "CP" and

                rel_pin_dir == "rise"):

 

        template_name = "hold/template__latch__rise__rise__glitch__maxq__1.sp"

        return template_name

 

    if( arc_type == "hold" and

                constr_pin == "TE" and

                constr_pin_dir == "fall" and

                rel_pin == "CP" and

                rel_pin_dir == "rise"):

 

        template_name = "hold/template__latch__rise__fall__pushout__1.sp"

        return template_name

 

    # MB*SLH SE->E from CW 2021/2/24 for vector data = 1

    if( arc_type == "hold" and

                fnmatch.fnmatch(cell_name, "MB*SRLSLH*QNSON*") and

                constr_pin == "SE" and

                constr_pin_dir == "rise" and

                (rel_pin == "E" or rel_pin == "CLK") and

                rel_pin_dir == "fall" and

                        len(probe_list) == 1):

 

        template_name = "hold/template__SLH__QN__fall__SE__rise__glitch__maxq__1.sp"

        return template_name

 

    if( arc_type == "hold" and

                fnmatch.fnmatch(cell_name, "MB*SRLSLH*QNSON*") and

                constr_pin == "SE" and

                constr_pin_dir == "fall" and

                (rel_pin == "E" or rel_pin == "CLK") and

                rel_pin_dir == "fall" and

                        len(probe_list) == 1):

 

        template_name = "hold/template__SLH__QN__fall__SE__fall__glitch__minq__1.sp"

        return template_name

 

    # MB*SRLSLH SE->E 2021/3/29 for vector different condition to consider MB*SRLSLH/MB*SRLSLHSCN

    if( arc_type == "hold" and

                fnmatch.fnmatch(cell_name, "MB*SRLSLH*") and

                constr_pin == "SE" and

                constr_pin_dir == "rise" and

                rel_pin == "E" and

                rel_pin_dir == "fall"):

 

        template_name = "hold/template__SLH__fall__SE__rise__glitch__maxq__1.sp"

        return template_name

 

    if( arc_type == "hold" and

                fnmatch.fnmatch(cell_name, "MB*SRLSLH*") and

                constr_pin == "SE" and

                constr_pin_dir == "rise" and

                rel_pin == "E" and

                rel_pin_dir == "rise"):

 

        template_name = "hold/template__SLH__rise__SE__rise__pushout__1.sp"

        return template_name

 

    # 0105 SLH SE->E from CW

    if( arc_type == "hold" and

                (fnmatch.fnmatch(cell_name, "SLH*") or fnmatch.fnmatch(cell_name, "MB*SLH*")) and

                constr_pin == "SE" and

                constr_pin_dir == "rise" and

                (rel_pin == "E" or rel_pin == "CLK") and

                rel_pin_dir == "fall"):

 

        template_name = "hold/template__SLH__fall__SE__rise__glitch__minq__1.sp"

        return template_name

 

    if( arc_type == "hold" and

                (fnmatch.fnmatch(cell_name, "SLH*") or fnmatch.fnmatch(cell_name, "MB*SLH*")) and

                constr_pin == "SE" and

                constr_pin_dir == "fall" and

                (rel_pin == "E" or rel_pin == "CLK") and

                rel_pin_dir == "fall"):

 

        template_name = "hold/template__SLH__fall__SE__fall__glitch__maxq__1.sp"

        return template_name   

 

    if( arc_type == "hold" and

                (fnmatch.fnmatch(cell_name, "SLH*") or fnmatch.fnmatch(cell_name, "MB*SLH*")) and

                constr_pin == "SE" and

                constr_pin_dir == "rise" and

                (rel_pin == "E" or rel_pin == "CLK") and

                rel_pin_dir == "rise"):

 

        template_name = "hold/template__SLH__rise__SE__rise__pushout__1.sp"

        return template_name

 

    # 0108 ESLH SE->CLK from CW

    if( arc_type == "hold" and

                fnmatch.fnmatch(cell_name, "ESLH*") and

                constr_pin == "SE" and

                constr_pin_dir == "rise" and

                rel_pin == "CLK" and

                rel_pin_dir == "rise"):

 

        template_name = "hold/template__SLH__rise__SE__rise__pushout__1.sp"

        return template_name

 

    if( arc_type == "hold" and

                fnmatch.fnmatch(cell_name, "ESLH*") and

                constr_pin == "SE" and

                constr_pin_dir == "fall" and

                rel_pin == "CLK" and

                rel_pin_dir == "fall"):

 

        template_name = "hold/template__SLH__fall__SE__fall__glitch__maxq__1.sp"

        return template_name   

 

    if( arc_type == "hold" and

                fnmatch.fnmatch(cell_name, "ESLH*") and

                constr_pin == "SE" and

                constr_pin_dir == "rise" and

                rel_pin == "CLK" and

                rel_pin_dir == "fall"):

 

        template_name = "hold/template__SLH__fall__SE__rise__glitch__minq__1.sp"

        return template_name

 

    if( arc_type == "hold" and

                fnmatch.fnmatch(cell_name, "ESLH*") and

                constr_pin == "SE" and

                constr_pin_dir == "fall" and

                rel_pin == "CLK" and

                rel_pin_dir == "rise"):

 

        template_name = "hold/template__SLH__rise__SE__fall__pushout__1.sp"

        return template_name   

 

    if( arc_type == "hold" and

                constr_pin == "SE" and

                constr_pin_dir == "rise" and

                rel_pin == "E" and

                rel_pin_dir == "fall"):

 

        template_name = "hold/template__common__fall__rise__1.sp"

        return template_name

 

    if( arc_type == "hold" and

                constr_pin == "SE" and

                constr_pin_dir == "fall" and

                rel_pin == "E" and

                rel_pin_dir == "fall"):

 

        template_name = "hold/template__common__fall__fall__1.sp"

        return template_name

 

    if( arc_type == "hold" and

                constr_pin == "SI" and

                constr_pin_dir == "rise" and

                rel_pin == "E" and

                rel_pin_dir == "rise"):

 

        template_name = "hold/template__common__rise__rise__1.sp"

        return template_name

 

    if( arc_type == "hold" and

                constr_pin == "SI" and

                constr_pin_dir == "fall" and

                rel_pin == "E" and

                rel_pin_dir == "rise"):

 

        template_name = "hold/template__common__rise__fall__1.sp"

        return template_name

 

    # LH latches (MB) 2020/3/5

    if( arc_type == "hold" and

                (fnmatch.fnmatch(cell_name, "MB*LHQN*") or fnmatch.fnmatch(cell_name, "MB*LNQN*")) and

                (fnmatch.fnmatch(constr_pin, "D*") or fnmatch.fnmatch(constr_pin, "B*")) and

                constr_pin_dir == "rise" and

                (rel_pin == "E" or rel_pin == "CLK") and

                rel_pin_dir == "fall" ):

 

        template_name = "hold/template__latch__fall__rise__glitch__minq__1.sp"

        return template_name

 

 

    if( arc_type == "hold" and

                (fnmatch.fnmatch(cell_name, "MB*LHQN*") or fnmatch.fnmatch(cell_name, "MB*LNQN*")) and

                (fnmatch.fnmatch(constr_pin, "D*") or fnmatch.fnmatch(constr_pin, "A*")) and

                constr_pin_dir == "fall" and

                (rel_pin == "E" or rel_pin == "CLK") and

                rel_pin_dir == "fall" ):

 

        template_name = "hold/template__latch__fall__fall__glitch__maxq__1.sp"

        return template_name

 

    # LH latches 2021/2/21 update for SEL1/2 related

    if( arc_type == "hold" and

                (fnmatch.fnmatch(cell_name,"PTISOLHRP*")) and

                (fnmatch.fnmatch(constr_pin, "D*") or fnmatch.fnmatch(constr_pin, "B*") or fnmatch.fnmatch(constr_pin, "CN") or fnmatch.fnmatch(constr_pin, "S")) and

                constr_pin_dir == "rise" and

                (rel_pin == "E" or fnmatch.fnmatch(rel_pin, "CLK*") or rel_pin == "ISO") and

                rel_pin_dir == "fall" and

                "QN" in probe_list):

 

        template_name = "hold/template__latch__fall__rise__glitch__maxq__1.sp"

        return template_name

 

    if( arc_type == "hold" and

                (fnmatch.fnmatch(constr_pin, "D*") or fnmatch.fnmatch(constr_pin, "B*") or fnmatch.fnmatch(constr_pin, "CN") or fnmatch.fnmatch(constr_pin, "S")) and

                constr_pin_dir == "rise" and

                (rel_pin == "E" or fnmatch.fnmatch(rel_pin, "CLK*") or rel_pin == "ISO") and

                rel_pin_dir == "fall" and

                "Q" in probe_list):

 

        template_name = "hold/template__latch__fall__rise__glitch__maxq__1.sp"

        return template_name

 

    if( arc_type == "hold" and

                (fnmatch.fnmatch(constr_pin, "D*") or fnmatch.fnmatch(constr_pin, "B*") or fnmatch.fnmatch(constr_pin, "CN") or fnmatch.fnmatch(constr_pin, "S")) and

                constr_pin_dir == "rise" and

                (rel_pin == "E" or fnmatch.fnmatch(rel_pin, "CLK*") or rel_pin == "ISO") and

                rel_pin_dir == "fall" and

                "QN" in probe_list):

 

        template_name = "hold/template__latch__fall__rise__glitch__minq__1.sp"

        return template_name

 

    if( arc_type == "hold" and

                (fnmatch.fnmatch(cell_name,"PTISOLHRP*")) and

                (fnmatch.fnmatch(constr_pin, "D*") or fnmatch.fnmatch(constr_pin, "A*") or fnmatch.fnmatch(constr_pin, "CN") or fnmatch.fnmatch(constr_pin, "S")) and

                constr_pin_dir == "fall" and

                (rel_pin == "E" or fnmatch.fnmatch(rel_pin, "CLK*") or rel_pin == "ISO") and

                rel_pin_dir == "fall" and

                "QN" in probe_list):

 

        template_name = "hold/template__latch__fall__fall__glitch__minq__1.sp"

        return template_name

 

    if( arc_type == "hold" and

                (fnmatch.fnmatch(constr_pin, "D*") or fnmatch.fnmatch(constr_pin, "A*") or fnmatch.fnmatch(constr_pin, "CN") or fnmatch.fnmatch(constr_pin, "S")) and

                constr_pin_dir == "fall" and

                (rel_pin == "E" or fnmatch.fnmatch(rel_pin, "CLK*") or rel_pin == "ISO") and

                rel_pin_dir == "fall" and

                "Q" in probe_list):

 

        template_name = "hold/template__latch__fall__fall__glitch__minq__1.sp"

        return template_name

 

    if( arc_type == "hold" and

                (fnmatch.fnmatch(constr_pin, "D*") or fnmatch.fnmatch(constr_pin, "A*") or fnmatch.fnmatch(constr_pin, "CN") or fnmatch.fnmatch(constr_pin, "S")) and

                constr_pin_dir == "fall" and

                (rel_pin == "E" or fnmatch.fnmatch(rel_pin, "CLK*") or rel_pin == "ISO") and

                rel_pin_dir == "fall" and

                "QN" in probe_list):

 

        template_name = "hold/template__latch__fall__fall__glitch__maxq__1.sp"

        return template_name

 

    if( arc_type == "hold" and

                (fnmatch.fnmatch(constr_pin, "D*") or fnmatch.fnmatch(constr_pin, "B*") or fnmatch.fnmatch(constr_pin, "CN") or fnmatch.fnmatch(constr_pin, "S")) and

                constr_pin_dir == "rise" and

                (rel_pin == "E" or fnmatch.fnmatch(rel_pin, "CLK*") or rel_pin == "ISO") and

                rel_pin_dir == "fall" ):

 

        template_name = "hold/template__latch__fall__rise__glitch__maxq__1.sp"

        return template_name

 

 

    if( arc_type == "hold" and

                (fnmatch.fnmatch(constr_pin, "D*") or fnmatch.fnmatch(constr_pin, "A*") or fnmatch.fnmatch(constr_pin, "CN") or fnmatch.fnmatch(constr_pin, "S")) and

                constr_pin_dir == "fall" and

                (rel_pin == "E" or fnmatch.fnmatch(rel_pin, "CLK*") or rel_pin == "ISO") and

                rel_pin_dir == "fall" ):

 

        template_name = "hold/template__latch__fall__fall__glitch__minq__1.sp"

        return template_name

 

    #SEDFKCNQSO E->CP 2021/2/2 from CW

    if( arc_type == "hold" and

                fnmatch.fnmatch(cell_name, "SEDFKCNQSO*") and

        fnmatch.fnmatch(constr_pin, "E") and

                constr_pin_dir == "rise" and

                fnmatch.fnmatch(rel_pin, "CP") and

                rel_pin_dir == "rise" and

                len(probe_list) == 2):

 

        template_name = "hold/template__EDF__rise__E__rise__glitch__maxq__2.sp"

        return template_name

 

    if( arc_type == "hold" and

                fnmatch.fnmatch(cell_name, "SEDFKCNQSO*") and

        fnmatch.fnmatch(constr_pin, "E") and

                constr_pin_dir == "fall" and

                fnmatch.fnmatch(rel_pin, "CP") and

                rel_pin_dir == "rise" and

                len(probe_list) == 2):

 

        template_name = "hold/template__EDF__rise__E__fall__pushout__minq__2.sp"

        return template_name

 

    #RLH 

    if( arc_type == "hold" and

                fnmatch.fnmatch(cell_name, "RLH*") and

                fnmatch.fnmatch(constr_pin, "D*")  and

                constr_pin_dir == "rise" and

                (rel_pin == "CP" or rel_pin == "CLK") and

                rel_pin_dir == "fall" ):

 

        template_name = "hold/template__latch__fall__rise__glitch__maxq__1.sp"

        return template_name

 

 

    if( arc_type == "hold" and

                fnmatch.fnmatch(cell_name, "RLH*") and

                fnmatch.fnmatch(constr_pin, "D*")  and

                constr_pin_dir == "fall" and

                (rel_pin == "CP" or rel_pin == "CLK") and

                rel_pin_dir == "fall" ):

 

        template_name = "hold/template__latch__fall__fall__glitch__minq__1.sp"

        return template_name

 

    # LN latches 2021/2/21 update for SEL1/2 related

    if( arc_type == "hold" and

                                (fnmatch.fnmatch(constr_pin, "D*") or fnmatch.fnmatch(constr_pin, "CN*") or fnmatch.fnmatch(constr_pin, "S*")) and

                constr_pin_dir == "rise" and

                (fnmatch.fnmatch(rel_pin, "EN") or fnmatch.fnmatch(rel_pin, "CLK*") or fnmatch.fnmatch(rel_pin, "ISO")) and

                rel_pin_dir == "rise" and

                                "Q" in probe_list):

 

        template_name = "hold/template__latch__rise__rise__glitch__maxq__1.sp"

        return template_name

 

    if( arc_type == "hold" and

                                (fnmatch.fnmatch(constr_pin, "D*") or fnmatch.fnmatch(constr_pin, "CN*") or fnmatch.fnmatch(constr_pin, "S*")) and

                constr_pin_dir == "rise" and

                (fnmatch.fnmatch(rel_pin, "EN") or fnmatch.fnmatch(rel_pin, "CLK*") or fnmatch.fnmatch(rel_pin, "ISO")) and

                rel_pin_dir == "rise" and

                                "QN" in probe_list):

 

        template_name = "hold/template__latch__rise__rise__glitch__minq__1.sp"

        return template_name

 

    if( arc_type == "hold" and

                                (fnmatch.fnmatch(constr_pin, "D*") or fnmatch.fnmatch(constr_pin, "CN*") or fnmatch.fnmatch(constr_pin, "S*")) and

                constr_pin_dir == "fall" and

                (fnmatch.fnmatch(rel_pin, "EN") or fnmatch.fnmatch(rel_pin, "CLK*") or fnmatch.fnmatch(rel_pin, "ISO")) and

                rel_pin_dir == "rise" and

                                "Q" in probe_list):

 

        template_name = "hold/template__latch__rise__fall__glitch__minq__1.sp"

        return template_name

 

    if( arc_type == "hold" and

                                (fnmatch.fnmatch(constr_pin, "D*") or fnmatch.fnmatch(constr_pin, "CN*") or fnmatch.fnmatch(constr_pin, "S*")) and

                constr_pin_dir == "fall" and

                (fnmatch.fnmatch(rel_pin, "EN") or fnmatch.fnmatch(rel_pin, "CLK*") or fnmatch.fnmatch(rel_pin, "ISO")) and

                rel_pin_dir == "rise" and

                                "QN" in probe_list):

 

        template_name = "hold/template__latch__rise__fall__glitch__maxq__1.sp"

        return template_name

 

    if( arc_type == "hold" and

                (fnmatch.fnmatch(constr_pin, "D*") or fnmatch.fnmatch(constr_pin, "CN*") or fnmatch.fnmatch(constr_pin, "S*")) and

                constr_pin_dir == "rise" and

                (fnmatch.fnmatch(rel_pin, "EN") or fnmatch.fnmatch(rel_pin, "CLK*") or fnmatch.fnmatch(rel_pin, "ISO")) and

                rel_pin_dir == "rise" ):

 

        template_name = "hold/template__latch__rise__rise__glitch__maxq__1.sp"

        return template_name

 

    if( arc_type == "hold" and

                (fnmatch.fnmatch(constr_pin, "D*") or fnmatch.fnmatch(constr_pin, "CN*") or fnmatch.fnmatch(constr_pin, "S*")) and

                constr_pin_dir == "fall" and

                (fnmatch.fnmatch(rel_pin, "EN") or fnmatch.fnmatch(rel_pin, "CLK*") or fnmatch.fnmatch(rel_pin, "ISO")) and

                rel_pin_dir == "rise" ):

 

        template_name = "hold/template__latch__rise__fall__glitch__minq__1.sp"

        return template_name

 

    # CKLHQ 2020/3/26 add ESLH E rise CLK fall

    if( arc_type == "hold" and

                constr_pin == "E" and

                constr_pin_dir == "rise" and

                rel_pin == "CPN" and

                rel_pin_dir == "fall" ):

 

        template_name = "hold/template__latch__fall__rise__glitch__minq__1.sp"

        return template_name

 

 

    if( arc_type == "hold" and

                constr_pin == "E" and

                constr_pin_dir == "fall" and

                rel_pin == "CPN" and

                rel_pin_dir == "fall" ):

 

        template_name = "hold/template__latch__fall__fall__pushout__1.sp"

        return template_name

 

    if( arc_type == "hold" and

                constr_pin == "OV" and

                constr_pin_dir == "fall" and

                rel_pin == "CPN" and

                rel_pin_dir == "fall" ):

 

        template_name = "hold/template__latch__fall__fall__pushout__1.sp"

        return template_name

   

    if( arc_type == "hold" and

                fnmatch.fnmatch(cell_name, "ESLH*") and

                constr_pin == "E" and

                constr_pin_dir == "fall" and

                rel_pin == "CLK" and

                rel_pin_dir == "rise" and

                "Q" in probe_list):

 

        template_name = "hold/template__ESLH__latch__rise__fall__pushout__1.sp"

        return template_name

   

    if( arc_type == "hold" and

                fnmatch.fnmatch(cell_name, "ESLH*") and

                constr_pin == "E" and

                constr_pin_dir == "rise" and

                rel_pin == "CLK" and

                rel_pin_dir == "fall" and

                not "!D" in when and

                "Q" in probe_list):

 

        template_name = "hold/template__ESLH__latch__fall__rise__glitch__maxq__1.sp"

        return template_name

 

    # CKLNQ (for SA/SB add .ic 2021/3/26)

    if( arc_type == "hold" and

                (fnmatch.fnmatch(constr_pin, "SA") or fnmatch.fnmatch(constr_pin, "SB")) and

                constr_pin_dir == "rise" and

                (fnmatch.fnmatch(rel_pin, "CP") or fnmatch.fnmatch(rel_pin, "CLK*")) and

                rel_pin_dir == "rise" and

                ("Q" in probe_list or "CLKOUT" in probe_list)):

 

        template_name = "hold/template__latch__S__rise__rise__glitch__maxq__1.sp"

        return template_name

 

 

    if( arc_type == "hold" and

                (fnmatch.fnmatch(constr_pin, "SA") or fnmatch.fnmatch(constr_pin, "SB")) and

                constr_pin_dir == "fall" and

                (fnmatch.fnmatch(rel_pin, "CP") or fnmatch.fnmatch(rel_pin, "CLK*")) and

                rel_pin_dir == "rise" and

                ("Q" in probe_list or "CLKOUT" in probe_list)):

 

        template_name = "hold/template__latch__S__rise__fall__pushout__1.sp"

        return template_name

 

    # CKLNQ

    #HS modified

    if( arc_type == "hold" and

                (fnmatch.fnmatch(constr_pin, "E") or fnmatch.fnmatch(constr_pin, "S") or fnmatch.fnmatch(constr_pin, "OV")) and

                constr_pin_dir == "rise" and

                (fnmatch.fnmatch(rel_pin, "CP") or fnmatch.fnmatch(rel_pin, "CLK*")) and

                rel_pin_dir == "rise" and

                ("Q" in probe_list or "CLKOUT" in probe_list)):

 

        template_name = "hold/template__latch__rise__rise__glitch__maxq__1.sp"

        return template_name

 

    #HS modified

    if( arc_type == "hold" and

                (fnmatch.fnmatch(constr_pin, "E") or fnmatch.fnmatch(constr_pin, "S") or fnmatch.fnmatch(constr_pin, "OV")) and

                constr_pin_dir == "fall" and

                (fnmatch.fnmatch(rel_pin, "CP") or fnmatch.fnmatch(rel_pin, "CLK*")) and

                rel_pin_dir == "rise" and

                ("Q" in probe_list or "CLKOUT" in probe_list)):

 

        template_name = "hold/template__latch__rise__fall__pushout__1.sp"

        return template_name

 

   # CKLNQAO22

    if( arc_type == "hold" and

            fnmatch.fnmatch(cell_name, "CKLNQAO22*") and

            (fnmatch.fnmatch(constr_pin, "A*") or fnmatch.fnmatch(constr_pin, "B*") or fnmatch.fnmatch(constr_pin, "TE")) and

            constr_pin_dir == "rise" and

            fnmatch.fnmatch(rel_pin, "CP") and

            rel_pin_dir == "rise" and

            len(probe_list) == 1):

 

        template_name = "hold/template__latch__rise__rise__glitch__maxq__1.sp"

        return template_name

 

    if( arc_type == "hold" and

            fnmatch.fnmatch(cell_name, "CKLNQAO22*") and

            (fnmatch.fnmatch(constr_pin, "A*") or fnmatch.fnmatch(constr_pin, "B*") or fnmatch.fnmatch(constr_pin, "TE")) and

            constr_pin_dir == "fall" and

            fnmatch.fnmatch(rel_pin, "CP") and

            rel_pin_dir == "rise" and

            len(probe_list) == 1):

 

        template_name = "hold/template__latch__rise__fall__pushout__1.sp"

        return template_name

 

    # CKLNQN

    if( arc_type == "hold" and

                constr_pin == "E" and

                constr_pin_dir == "rise" and

                rel_pin == "CP" and

                rel_pin_dir == "rise" and

                "QN" in probe_list):

 

        template_name = "hold/template__latch__rise__rise__glitch__minq__1.sp"

        return template_name

 

 

    if( arc_type == "hold" and

                constr_pin == "E" and

                constr_pin_dir == "fall" and

                rel_pin == "CP" and

                rel_pin_dir == "rise" and

                "QN" in probe_list):

 

        template_name = "hold/template__latch__rise__fall__pushout__1.sp"

        return template_name

 

    #CKLNENEPQRCBCCH RD/FD min(3p,max(5%,1p)) 2021/8/9

    if( arc_type == "hold" and

                constr_pin == "FD" and

                constr_pin_dir == "fall" and

                (rel_pin == "CP" or rel_pin == "CLK") and

                rel_pin_dir == "fall" ):

 

        template_name = "hold/template__RCB__fall__fall__pushout__minq__negative__1.sp"

        return template_name

 

    if( arc_type == "hold" and

                constr_pin == "RD" and

                constr_pin_dir == "rise" and

                (rel_pin == "CP" or rel_pin == "CLK") and

                rel_pin_dir == "rise" ):

 

        template_name = "hold/template__RCB__rise__rise__pushout__maxq__negative__1.sp"

        return template_name

 

    if( arc_type == "hold" and

                fnmatch.fnmatch(constr_pin, "RD") and

                constr_pin_dir == "fall" and

                (fnmatch.fnmatch(rel_pin, "CP") or fnmatch.fnmatch(rel_pin, "CLK")) and

                rel_pin_dir == "rise" ):

 

        template_name = "hold/template__RCB__rise__fall__pushout__maxq__1.sp"

        return template_name

 

    if( arc_type == "hold" and

                fnmatch.fnmatch(constr_pin, "FD") and

                constr_pin_dir == "rise" and

                (fnmatch.fnmatch(rel_pin, "CP") or fnmatch.fnmatch(rel_pin, "CLK")) and

                rel_pin_dir == "fall" ):

 

        template_name = "hold/template__RCB__fall__rise__pushout__minq__1.sp"

        return template_name

 

    # CKLNENQ 2020/3/25 add CKLNTRPQ

    if( arc_type == "hold" and

                (fnmatch.fnmatch(cell_name, "CKLNTSRQ*") or fnmatch.fnmatch(cell_name, "CKLNTRPQ*")) and

                constr_pin == "EN" and

                constr_pin_dir == "rise" and

                rel_pin == "CLK" and

                rel_pin_dir == "rise" ):

 

        template_name = "hold/template__latch__rise__rise__glitch__maxq__1.sp"

        return template_name

 

    if( arc_type == "hold" and

                (constr_pin == "EN" or constr_pin == "EB" or constr_pin == "TEB") and

                constr_pin_dir == "rise" and

                rel_pin == "CP" and

                rel_pin_dir == "rise" ):

 

        template_name = "hold/template__latch__rise__rise__pushout__1.sp"

        return template_name

   

    if( arc_type == "hold" and

                (fnmatch.fnmatch(cell_name, "CKLNTSRQ*") or fnmatch.fnmatch(cell_name, "CKLNTRPQ*")) and

                constr_pin == "EN" and

                constr_pin_dir == "fall" and

                rel_pin == "CLK" and

                rel_pin_dir == "rise" ):

 

        template_name = "hold/template__latch__rise__fall__glitch__minq__1.sp"

        return template_name

 

    if( arc_type == "hold" and

                (constr_pin == "EN" or constr_pin == "EB" or constr_pin == "TEB") and

                constr_pin_dir == "fall" and

                rel_pin == "CP" and

                rel_pin_dir == "rise" ):

 

        template_name = "hold/template__latch__rise__fall__glitch__maxq__1.sp"

        return template_name

 

    # non_seq_hold (Latch) 2020/1/14 add LHSCN for N5/N6 intel new cell

    if( arc_type == "non_seq_hold" and

                fnmatch.fnmatch(cell_name, "LHSCN*") and

                constr_pin == "SDN" and

                constr_pin_dir == "rise" and

                rel_pin == "CDN" and

                rel_pin_dir == "rise"):

 

        template_name = "non_seq_hold/template__latch__rise__rise__pushout__1.sp"

        return template_name

 

    if( arc_type == "non_seq_hold" and

                fnmatch.fnmatch(cell_name, "LHSCN*") and

                constr_pin == "CDN" and

                constr_pin_dir == "rise" and

                rel_pin == "SDN" and

                rel_pin_dir == "rise"):

 

        template_name = "non_seq_hold/template__latch__rise__rise__glitch__maxq__1.sp"

        return template_name

 

    if( arc_type == "non_seq_hold" and

                fnmatch.fnmatch(cell_name, "L*") and

                constr_pin == "SDN" and

                constr_pin_dir == "rise" and

                rel_pin == "CDN" and

                rel_pin_dir == "rise"):

 

        template_name = "non_seq_hold/template__latch__rise__rise__glitch__minq__1.sp"

        return template_name

 

    if( arc_type == "non_seq_hold" and

                fnmatch.fnmatch(cell_name, "L*") and

                constr_pin == "CDN" and

                constr_pin_dir == "rise" and

                rel_pin == "SDN" and

                rel_pin_dir == "rise"):

 

        template_name = "non_seq_hold/template__latch__rise__rise__pushout__1.sp"

        return template_name

 

    # non_seq_hold (Flop for N22ULL/N12/N40) ---- 2019/12/20 flop deck from from HC

    if( arc_type == "non_seq_hold" and

                fnmatch.fnmatch(cell_name, "*CSN*") and

                constr_pin == "CDN" and

                constr_pin_dir == "rise" and

                rel_pin == "SDN" and

                rel_pin_dir == "rise"):

 

        template_name = "non_seq_hold/template__latch__rise__rise__glitch__maxq__1.sp"

        return template_name

 

    if( arc_type == "non_seq_hold" and

                fnmatch.fnmatch(cell_name, "*CSN*") and

                constr_pin == "SDN" and

                constr_pin_dir == "rise" and

                rel_pin == "CDN" and

                rel_pin_dir == "rise"):

 

        template_name = "non_seq_hold/template__flop__rise__rise__pushout__1.sp"

        return template_name

       

    # non_seq_hold (Flop) -- 2019/09/26 SDN > CDN

    if( arc_type == "non_seq_hold" and

                constr_pin == "SDN" and

                constr_pin_dir == "rise" and

                rel_pin == "CDN" and

                rel_pin_dir == "rise"):

 

        template_name = "non_seq_hold/template__latch__rise__rise__pushout__1.sp"

        return template_name

 

    if( arc_type == "non_seq_hold" and

                constr_pin == "CDN" and

                constr_pin_dir == "rise" and

                rel_pin == "SDN" and

                rel_pin_dir == "rise"):

 

        template_name = "non_seq_hold/template__latch__rise__rise__glitch__maxq__1.sp"

        return template_name

 

    # Double probe, non_seq_hold arcs for SDN->CD with "bl_bx" probe, which requires mixed

    if( arc_type == "non_seq_hold" and

                fnmatch.fnmatch(cell_name, "*SDRPQ*") and

                constr_pin == "SDN" and

                constr_pin_dir == "rise" and

                rel_pin == "CD" and

                rel_pin_dir == "fall" and

                "Q" in probe_list and

                "bl_bx" in probe_list and

                len(probe_list) == 2):

        template_name = "non_seq_hold/template__latch__fall__rise__glitch__minq_maxbl_bx__2.sp"

        return template_name

   

    if( arc_type == "non_seq_hold" and

                fnmatch.fnmatch(cell_name, "*SDRPQ*") and

                constr_pin == "SDN" and

                constr_pin_dir == "rise" and

                rel_pin == "CD" and

                rel_pin_dir == "fall" and

                "Q" in probe_list and

                "sl_ax" in probe_list and

                len(probe_list) == 2):

        template_name = "non_seq_hold/template__latch__fall__rise__glitch__minq_maxsl_ax__2.sp"

        return template_name

 

    if( arc_type == "non_seq_hold" and

                fnmatch.fnmatch(cell_name, "*SDRPQ*") and

                constr_pin == "CD" and

                constr_pin_dir == "fall" and

                rel_pin == "SDN" and

                rel_pin_dir == "rise" and

                "Q" in probe_list and

                len(probe_list) == 2):

        template_name = "non_seq_hold/template__latch__rise__fall__pushout__2.sp"

        return template_name

 

    if( arc_type == "non_seq_hold" and

                fnmatch.fnmatch(cell_name, "*SDRPQ*") and

                constr_pin == "SDN" and

                constr_pin_dir == "rise" and

                rel_pin == "CD" and

                rel_pin_dir == "fall" and

                "Q" in probe_list and

                len(probe_list) == 2):

        template_name = "non_seq_hold/template__latch__fall__rise__glitch__minq__2.sp"

        return template_name

 

    if( arc_type == "non_seq_hold" and

                constr_pin == "CD" and

                constr_pin_dir == "fall" and

                rel_pin == "SDN" and

                rel_pin_dir == "rise" and

                "Q" in probe_list and

                "bl_bx" in probe_list and

                len(probe_list) == 2):

        template_name = "non_seq_hold/template__latch__rise__fall__glitch__maxq_minbl_bx__2.sp"

        return template_name

 

    if( arc_type == "non_seq_hold" and

                constr_pin == "CD" and

                constr_pin_dir == "fall" and

                rel_pin == "SDN" and

                rel_pin_dir == "rise" and

                "Q" in probe_list and

                "sl_ax" in probe_list and

                len(probe_list) == 2):

        template_name = "non_seq_hold/template__latch__rise__fall__glitch__maxq_minsl_ax__2.sp"

        return template_name

 

    if( arc_type == "non_seq_hold" and

                constr_pin == "CD" and

                constr_pin_dir == "fall" and

                rel_pin == "SDN" and

                rel_pin_dir == "rise" and

                "Q" in probe_list and

                len(probe_list) == 2):

        template_name = "non_seq_hold/template__latch__rise__fall__glitch__maxq__2.sp"

        return template_name

 

    if( arc_type == "non_seq_hold" and

                constr_pin == "SDN" and

                constr_pin_dir == "rise" and

                rel_pin == "CD" and

                rel_pin_dir == "fall" and

                "Q" in probe_list and

                len(probe_list) == 2):

        template_name = "non_seq_hold/template__latch__fall__rise__pushout__2.sp"

        return template_name

 

    # non_seq_hold (SDRPQ)

    if( arc_type == "non_seq_hold" and

                fnmatch.fnmatch(cell_name, "*SDRPQ*") and

                constr_pin == "CD" and

                constr_pin_dir == "fall" and

                rel_pin == "SDN" and

                rel_pin_dir == "rise"):

 

        template_name = "non_seq_hold/template__latch__rise__fall__pushout__1.sp"

        return template_name

 

    if( arc_type == "non_seq_hold" and

                fnmatch.fnmatch(cell_name, "*SDRPQ*")and

                constr_pin == "SDN" and

                constr_pin_dir == "rise" and

                rel_pin == "CD" and

                rel_pin_dir == "fall"):

 

        template_name = "non_seq_hold/template__latch__fall__rise__glitch__minq__1.sp"

        return template_name

 

    # non_seq_hold (flop)

    if( arc_type == "non_seq_hold" and

                constr_pin == "CD" and

                constr_pin_dir == "fall" and

                rel_pin == "SDN" and

                rel_pin_dir == "rise"):

 

        template_name = "non_seq_hold/template__latch__rise__fall__glitch__maxq__1.sp"

        return template_name

 

    if( arc_type == "non_seq_hold" and

                constr_pin == "SDN" and

                constr_pin_dir == "rise" and

                rel_pin == "CD" and

                rel_pin_dir == "fall"):

 

        template_name = "non_seq_hold/template__latch__fall__rise__pushout__1.sp"

        return template_name

 

    #non_seq_hold (RETN default)

    if( arc_type == "non_seq_hold" and

                fnmatch.fnmatch(cell_name, "*RSSDF*")and

                constr_pin == "SDN" and

                constr_pin_dir == "fall" and

                rel_pin == "RETN" and

                rel_pin_dir == "fall" and

                "Q" in probe_list and

                "bl_b" in probe_list and

                len(probe_list) == 2):

        template_name = "non_seq_hold/template__retn__nonseq__RETN__fall__SDN__fall__glitch__maxq__maxbl_b__2.sp"

        return template_name

 

    if( arc_type == "non_seq_hold" and

                fnmatch.fnmatch(cell_name, "*RSSDF*")and

                constr_pin == "CD" and

                constr_pin_dir == "rise" and

                rel_pin == "RETN" and

                rel_pin_dir == "fall" and

                "Q" in probe_list and

                "bl_b" in probe_list and

                len(probe_list) == 2):

        template_name = "non_seq_hold/template__retn__nonseqhold__RETN__fall__CD__rise__glitch__minq__minbl_b__2.sp"

        return template_name

 

    if( arc_type == "non_seq_hold" and

                (fnmatch.fnmatch(cell_name, "*RSSDFSYNC2*") or fnmatch.fnmatch(cell_name, "*RSCDFSYNC2*"))and

                constr_pin == "CD" and

                constr_pin_dir == "rise" and

                rel_pin == "RETN" and

                rel_pin_dir == "fall" and

                "Q" in probe_list and

                "bl_b" in probe_list and

                len(probe_list) == 4):

        template_name = "non_seq_hold/template__retn__nonseqhold__RETN__fall__CD__rise__glitch__minq__minbl_b__4.sp"

        return template_name

   

    if( arc_type == "non_seq_hold" and

                (fnmatch.fnmatch(cell_name, "*RSSDFSYNC3*") or fnmatch.fnmatch(cell_name, "*RSCDFSYNC3*"))and

                constr_pin == "CD" and

                constr_pin_dir == "rise" and

                rel_pin == "RETN" and

                rel_pin_dir == "fall" and

                "Q" in probe_list and

                "bl_b" in probe_list and

                len(probe_list) == 4):

        template_name = "non_seq_hold/template__syn3__retn__nonseqhold__RETN__fall__CD__rise__glitch__minq__minbl_b__4.sp"

        return template_name

 

    if( arc_type == "non_seq_hold" and

                (fnmatch.fnmatch(cell_name, "*RSSDFSYNC4*") or fnmatch.fnmatch(cell_name, "*RSCDFSYNC4*"))and

                constr_pin == "CD" and

                constr_pin_dir == "rise" and

                rel_pin == "RETN" and

                rel_pin_dir == "fall" and

                "Q" in probe_list and

                "bl_b" in probe_list and

                len(probe_list) == 4):

        template_name = "non_seq_hold/template__syn4__retn__nonseqhold__RETN__fall__CD__rise__glitch__minq__minbl_b__4.sp"

        return template_name

   

    if( arc_type == "non_seq_hold" and

                (fnmatch.fnmatch(cell_name, "*RSSDFSYNC5*") or fnmatch.fnmatch(cell_name, "*RSCDFSYNC5*"))and

                constr_pin == "CD" and

                constr_pin_dir == "rise" and

                rel_pin == "RETN" and

                rel_pin_dir == "fall" and

                "Q" in probe_list and

                "bl_b" in probe_list and

                len(probe_list) == 4):

        template_name = "non_seq_hold/template__syn5__retn__nonseqhold__RETN__fall__CD__rise__glitch__minq__minbl_b__4.sp"

        return template_name

   

    if( arc_type == "non_seq_hold" and

                (fnmatch.fnmatch(cell_name, "*RSSDFSYNC6*") or fnmatch.fnmatch(cell_name, "*RSCDFSYNC6*"))and

                constr_pin == "CD" and

                constr_pin_dir == "rise" and

                rel_pin == "RETN" and

                rel_pin_dir == "fall" and

                "Q" in probe_list and

                "bl_b" in probe_list and

                len(probe_list) == 4):

        template_name = "non_seq_hold/template__syn6__retn__nonseqhold__RETN__fall__CD__rise__glitch__minq__minbl_b__4.sp"

        return template_name

   

    if( arc_type == "non_seq_hold" and

                fnmatch.fnmatch(cell_name, "*RSVNB*")and

                constr_pin == "CD" and

                constr_pin_dir == "rise" and

                rel_pin == "RETN" and

                rel_pin_dir == "fall" and

                "Q" in probe_list and

                "sl_b" in probe_list and

                len(probe_list) == 2):

        template_name = "non_seq_hold/template__retn__nonseq__RETN__fall__CD__rise__glitch__minq__minsl_b__2.sp"

        return template_name

 

    if( arc_type == "non_seq_hold" and

                fnmatch.fnmatch(cell_name, "*RSVNB*")and

                constr_pin == "CD" and

                constr_pin_dir == "fall" and

                rel_pin == "RETN" and

                rel_pin_dir == "rise" and

                "Q" in probe_list and

                "sl_b" in probe_list and

                len(probe_list) == 2):

        template_name = "non_seq_hold/template__retn__nonseq__RETN__rise__CD__fall__glitch__minq__minsl_b__2.sp"

        return template_name

 

    #non_seq_hold (RETN nochange mapping)

    if( arc_type == "nochange_low_low" and

                constr_pin == "CD" and

                constr_pin_dir == "rise" and

                rel_pin == "RETN" and

                rel_pin_dir == "rise" and

                "Q" in probe_list and

                "bl_b" in probe_list and

                len(probe_list) == 2):

        template_name = "nochange_low_low/template__retn__nonseq__RETN__rise__CD__rise__pushout__2.sp"

        return template_name

 

    if( arc_type == "nochange_low_low" and

                (fnmatch.fnmatch(cell_name, "*RSSDFSYNC2*") or fnmatch.fnmatch(cell_name, "*RSCDFSYNC2*"))and

                constr_pin == "CD" and

                constr_pin_dir == "rise" and

                rel_pin == "RETN" and

                rel_pin_dir == "rise" and

                "Q" in probe_list and

                "bl_b" in probe_list and

                len(probe_list) == 4):

        template_name = "nochange_low_low/template__retn__nonseqhold__RETN__rise__CD__rise__pushout__4.sp"

        return template_name

 

    if( arc_type == "nochange_low_low" and

                (fnmatch.fnmatch(cell_name, "*RSSDFSYNC3*") or fnmatch.fnmatch(cell_name, "*RSCDFSYNC3*"))and

                constr_pin == "CD" and

                constr_pin_dir == "rise" and

                rel_pin == "RETN" and

                rel_pin_dir == "rise" and

                "Q" in probe_list and

                "bl_b" in probe_list and

                len(probe_list) == 4):

        template_name = "nochange_low_low/template__syn3_retn__nonseqhold__RETN__rise__CD__rise__pushout__4.sp"

        return template_name

 

    if( arc_type == "nochange_low_low" and

                (fnmatch.fnmatch(cell_name, "*RSSDFSYNC4*") or fnmatch.fnmatch(cell_name, "*RSCDFSYNC4*"))and

                constr_pin == "CD" and

                constr_pin_dir == "rise" and

                rel_pin == "RETN" and

                rel_pin_dir == "rise" and

                "Q" in probe_list and

                "bl_b" in probe_list and

                len(probe_list) == 4):

        template_name = "nochange_low_low/template__syn4_retn__nonseqhold__RETN__rise__CD__rise__pushout__4.sp"

        return template_name

 

    if( arc_type == "nochange_low_low" and

                (fnmatch.fnmatch(cell_name, "*RSSDFSYNC5*") or fnmatch.fnmatch(cell_name, "*RSCDFSYNC5*"))and

                constr_pin == "CD" and

                constr_pin_dir == "rise" and

                rel_pin == "RETN" and

                rel_pin_dir == "rise" and

                "Q" in probe_list and

                "bl_b" in probe_list and

                len(probe_list) == 4):

        template_name = "nochange_low_low/template__syn5_retn__nonseqhold__RETN__rise__CD__rise__pushout__4.sp"

        return template_name

 

    if( arc_type == "nochange_low_low" and

                (fnmatch.fnmatch(cell_name, "*RSSDFSYNC6*") or fnmatch.fnmatch(cell_name, "*RSCDFSYNC6*"))and

                constr_pin == "CD" and

                constr_pin_dir == "rise" and

                rel_pin == "RETN" and

                rel_pin_dir == "rise" and

                "Q" in probe_list and

                "bl_b" in probe_list and

                len(probe_list) == 4):

        template_name = "nochange_low_low/template__syn6_retn__nonseqhold__RETN__rise__CD__rise__pushout__4.sp"

        return template_name

 

    if( arc_type == "nochange_low_high" and

                constr_pin == "SDN" and

                constr_pin_dir == "fall" and

                rel_pin == "RETN" and

                rel_pin_dir == "rise" and

                "Q" in probe_list and

                "bl_b" in probe_list and

                len(probe_list) == 2):

        template_name = "nochange_low_high/template__retn__nonseqsetup__RETN__rise__SDN__fall__pushout__2.sp"

        return template_name

 

    if( arc_type == "non_seq_setup" and

                constr_pin == "SDN" and

                constr_pin_dir == "fall" and

                rel_pin == "RETN" and

                rel_pin_dir == "fall" and

                "Q" in probe_list and

                "bl_b" in probe_list and

                len(probe_list) == 2):

        template_name = "non_seq_setup/template__retn__nonseqsetup__RETN__fall__SDN__fall__pushout__2.sp"

        return template_name

 

    if( arc_type == "non_seq_setup" and

                constr_pin == "SDN" and

                constr_pin_dir == "rise" and

                rel_pin == "RETN" and

                rel_pin_dir == "rise" and

                "Q" in probe_list and

                "bl_b" in probe_list and

                len(probe_list) == 2):

        template_name = "non_seq_setup/template__retn__nonseqsetup__RETN__rise__SDN__rise__glitch__maxq__maxbl_b__2.sp"

        return template_name

 

    if( arc_type == "non_seq_setup" and

                constr_pin == "CD" and

                constr_pin_dir == "rise" and

                rel_pin == "RETN" and

                rel_pin_dir == "fall" and

                "Q" in probe_list and

                "bl_b" in probe_list and

                len(probe_list) == 2):

        template_name = "non_seq_setup/template__retn__nonseqsetup__RETN__fall__CD__rise__pushout__2.sp"

        return template_name

 

    if( arc_type == "non_seq_setup" and

                constr_pin == "CD" and

                constr_pin_dir == "fall" and

                rel_pin == "RETN" and

                rel_pin_dir == "rise" and

                "Q" in probe_list and

                "bl_b" in probe_list and

                len(probe_list) == 2):

        template_name = "non_seq_setup/template__retn__nonseqsetup__RETN__rise__CD__fall__glitch__minq__minbl_b__2.sp"

        return template_name

 

 

    if( arc_type == "non_seq_setup" and

                constr_pin == "SDN" and

                constr_pin_dir == "rise" and

                rel_pin == "RETN" and

                rel_pin_dir == "rise" and

                "Q" in probe_list and

                "sl_b" in probe_list and

                len(probe_list) == 2):

        template_name = "non_seq_setup/template__retn__nonseqsetup__RETN__rise__SDN__rise__glitch__maxq__maxsl_b__2.sp"

        return template_name

 

    if( arc_type == "non_seq_setup" and

                constr_pin == "CD" and

                constr_pin_dir == "rise" and

                rel_pin == "RETN" and

                rel_pin_dir == "fall" and

                "Q" in probe_list and

                "sl_b" in probe_list and

                len(probe_list) == 2):

        template_name = "non_seq_setup/template__retn__nonseqsetup__RETN__fall__CD__rise__pushout__2.sp"

        return template_name

 

    if( arc_type == "non_seq_setup" and

                constr_pin == "CD" and

                constr_pin_dir == "fall" and

                rel_pin == "RETN" and

                rel_pin_dir == "rise" and

                "Q" in probe_list and

                "sl_b" in probe_list and

                len(probe_list) == 2):

        template_name = "non_seq_setup/template__retn__nonseqsetup__RETN__rise__CD__fall__glitch__minq__minsl_b__2.sp"

        return template_name

 

    if( arc_type == "non_seq_setup" and

                fnmatch.fnmatch(cell_name, "*RSNBSDF*")and

                constr_pin == "SDN" and

                constr_pin_dir == "rise" and

                rel_pin == "RETN" and

                rel_pin_dir == "rise" and

                "Q" in probe_list and

                "sl_ax" in probe_list and

                len(probe_list) == 2):

        template_name = "non_seq_setup/template__retn__nonseqsetup__RSNB__RETN__rise__SDN__rise__pushout__2.sp"

        return template_name

 

    if( arc_type == "non_seq_setup" and

                fnmatch.fnmatch(cell_name, "*RSNBSDF*")and

                constr_pin == "CD" and

                constr_pin_dir == "fall" and

                rel_pin == "RETN" and

                rel_pin_dir == "rise" and

                "Q" in probe_list and

                "sl_ax" in probe_list and

                len(probe_list) == 2):

        template_name = "non_seq_setup/template__retn__nonseqsetup__RSNB__RETN__rise__CD__fall__pushout__2.sp"

        return template_name

 

    #2020/8/3 RETN's arc enhance

    if( arc_type == "non_seq_hold" and

                constr_pin == "SDN" and

                constr_pin_dir == "fall" and

                rel_pin == "RETN" and

                rel_pin_dir == "fall" and

                "Q" in probe_list and

                ("sl_ax" in probe_list or "sl_bx" in probe_list) and

                len(probe_list) == 2):

        template_name = "non_seq_hold/template__retn__nonseqhold__RETN__fall__SDN__fall__notCD__glitch__maxq__minqx__2.sp"

        return template_name

 

    if( arc_type == "non_seq_hold" and

                constr_pin == "CD" and

                constr_pin_dir == "rise" and

                rel_pin == "RETN" and

                rel_pin_dir == "fall" and

                "Q" in probe_list and

                ("sl_ax" in probe_list or "sl_bx" in probe_list) and

                len(probe_list) == 2):

        template_name = "non_seq_hold/template__retn__nonseqhold__RETN__fall__CD__rise__SDN__glitch__minq__maxqx__2.sp"

        return template_name

 

    if( arc_type == "nochange_low_low" and

                constr_pin == "CD" and

                constr_pin_dir == "rise" and

                rel_pin == "RETN" and

                rel_pin_dir == "rise" and

                "Q" in probe_list):

 

        if(("sl_ax" in probe_list or "sl_bx" in probe_list) and

                len(probe_list) == 2):

            template_name = "nochange_low_low/template__retn__nonseqhold__RETN__rise__CD__rise__SDN__pushout__maxq__minqx__2.sp"

            return template_name

        if(("bl_b" in probe_list or "sl_a" in probe_list or "sl_b" in probe_list) and

                len(probe_list) == 2):

            template_name = "nochange_low_low/template__retn__nonseqhold__RETN__rise__CD__rise__SDN__pushout__2.sp"

            return template_name

        if(fnmatch.fnmatch(cell_name, "*RSSDFSYNC*")and

                 "bl_b" in probe_list and

                 len(probe_list) == 4):

            template_name = "nochange_low_low/template__retn__nonseqhold__RETN__rise__CD__rise__pushout__4.sp"

            return template_name

 

    if( arc_type == "nochange_high_low" and

                constr_pin == "SDN" and

                constr_pin_dir == "fall" and

                rel_pin == "RETN" and

                rel_pin_dir == "rise" and

                "Q" in probe_list and

                len(probe_list) == 2):

        if("sl_ax" in probe_list or "sl_bx" in probe_list):

            template_name = "nochange_high_low/template__retn__nonseqhold__RETN__rise__SDN__fall__notCD__pushout__minq__maxqx__2.sp"

            return template_name

        if("bl_b" in probe_list or "sl_a" in probe_list or "sl_b" in probe_list):

            template_name = "nochange_high_low/template__retn__nonseqhold__RETN__rise__SDN__fall__notCD__pushout__2.sp"

            return template_name

 

    if( arc_type == "removal" and

                constr_pin == "RETN" and

                constr_pin_dir == "rise" and

                rel_pin == "CP" and

                rel_pin_dir == "fall" and

                "Q" in probe_list):

 

        if(("sl_ax" in probe_list or "sl_bx" in probe_list) and

                len(probe_list) == 2):

            template_name = "hold/template__retn__removal__fall__rise__glitch__maxq__minqx__2.sp"

            return template_name

        if(("bl_b" in probe_list or "sl_a" in probe_list or "sl_b" in probe_list) and

                len(probe_list) == 2):

            template_name = "hold/template__retn__removal__fall__rise__glitch__minq__2.sp"

            return template_name

 

    #2018/2/23 new arc

    if( arc_type == "removal" and

                fnmatch.fnmatch(cell_name, "*MB*")and

                constr_pin == "RETN" and

                constr_pin_dir == "rise" and

                rel_pin == "CP" and

                rel_pin_dir == "fall" and

                "Q2" in probe_list and

                "bl2_b" in probe_list and

                len(probe_list) == 2):

        template_name = "hold/template__retn__removal__fall__rise__glitch__minq__2.sp"

        return template_name

 

    if( arc_type == "removal" and

                fnmatch.fnmatch(cell_name, "*MB*")and

                constr_pin == "RETN" and

                constr_pin_dir == "rise" and

                rel_pin == "CP" and

                rel_pin_dir == "fall" and

                "Q1" in probe_list and

                "bl1_b" in probe_list and

                len(probe_list) == 2):

        template_name = "hold/template__retn__removal__fall__rise__glitch__minq__2.sp"

        return template_name

 

    if( arc_type == "removal" and

                fnmatch.fnmatch(cell_name, "*MB*")and

                constr_pin == "RETN" and

                constr_pin_dir == "rise" and

                rel_pin == "CP" and

                rel_pin_dir == "fall" and

                "Q3" in probe_list and

                "bl3_b" in probe_list and

                len(probe_list) == 2):

        template_name = "hold/template__retn__removal__fall__rise__glitch__minq__2.sp"

        return template_name

 

    if( arc_type == "removal" and

                fnmatch.fnmatch(cell_name, "*MB*")and

                constr_pin == "RETN" and

                constr_pin_dir == "rise" and

                rel_pin == "CP" and

                rel_pin_dir == "fall" and

                "Q4" in probe_list and

                "bl4_b" in probe_list and

                len(probe_list) == 2):

        template_name = "hold/template__retn__removal__fall__rise__glitch__minq__2.sp"

        return template_name

 

    if( arc_type == "removal" and

                fnmatch.fnmatch(cell_name, "*MB*")and

                constr_pin == "RETN" and

                constr_pin_dir == "fall" and

                rel_pin == "CP" and

                rel_pin_dir == "rise" and

                len(probe_list) == 2):

        template_name = "hold/template__retn__removal__notD__rise__fall__pushout__2.sp"

        return template_name

 

    # Removal

    if( arc_type == "removal" and

                constr_pin == "CD" and

                constr_pin_dir == "fall" and

                rel_pin == "CPN" and

                rel_pin_dir == "fall" and

                "Q" in probe_list and

                len(probe_list) == 1):

 

        if(fnmatch.fnmatch(cell_name, "*CKLH*")):

            template_name = "hold/template__latch__fall__fall__glitch__minq__1.sp"

            return template_name

        else:

            template_name = "hold/template__latch__fall__fall__glitch__maxq__1.sp"

            return template_name

 

    # DFDETRPQ removal

    if( arc_type == "removal" and

                fnmatch.fnmatch(cell_name, "*DFDET*") and

                constr_pin == "CD" and

                constr_pin_dir == "fall" and

                rel_pin == "CP" and

                rel_pin_dir == "fall" and

                "Q" in probe_list and

                len(probe_list) == 1):

 

        template_name = "hold/template__latch__fall__fall__glitch__maxq__1.sp"

        return template_name

 

    if( arc_type == "removal" and

                constr_pin == "CD" and

                constr_pin_dir == "fall" and

                rel_pin == "CPN" and

                rel_pin_dir == "fall" and

                "Q" in probe_list and

                len(probe_list) == 2):

 

        template_name = "hold/template__latch__fall__fall__glitch__maxq__2.sp"

        return template_name

 

 

    if( arc_type == "removal" and

                constr_pin == "CD" and

                constr_pin_dir == "fall" and

                rel_pin == "CPN" and

                rel_pin_dir == "fall" and

                "QN" in probe_list and

                len(probe_list) == 1):

 

        template_name = "hold/template__latch__fall__fall__glitch__minq__1.sp"

        return template_name

 

 

    if( arc_type == "removal" and

                constr_pin == "CD" and

                constr_pin_dir == "fall" and

                rel_pin == "CPN" and

                rel_pin_dir == "fall" and

                "QN" in probe_list and

                len(probe_list) == 2):

 

        template_name = "hold/template__latch__fall__fall__glitch__minq__2.sp"

        return template_name

 

 

 

    #Removal SDN->CPN

    if( arc_type == "removal" and

                constr_pin == "CD" and

                constr_pin_dir == "fall" and

                rel_pin == "E" and

                rel_pin_dir == "fall" and

                "Q" in probe_list and

                len(probe_list) == 2):

 

        template_name = "hold/template__latch__fall__fall__glitch__minq_maxq__2.sp"

        return template_name

 

    #HS for PTISO lactch

    if( arc_type == "removal" and

                constr_pin == "CD" and

                constr_pin_dir == "fall" and

                rel_pin == "E" and

                rel_pin_dir == "fall" and

                "Q" in probe_list and

                len(probe_list) == 1):

 

        template_name = "hold/template__latch__fall__fall__glitch__minq_maxq__1.sp"

        return template_name

 

    if( arc_type == "removal" and

                constr_pin == "CD" and

                constr_pin_dir == "fall" and

                rel_pin == "E" and

                rel_pin_dir == "fall" and

                "QN" in probe_list and

                len(probe_list) == 1):

 

        template_name = "hold/template__latch__fall__fall__glitch__minq__1.sp"

        return template_name

 

 

    if( arc_type == "removal" and

                constr_pin == "CD" and

                constr_pin_dir == "fall" and

                rel_pin == "E" and

                rel_pin_dir == "fall" and

                "QN" in probe_list and

                len(probe_list) == 2):

 

        template_name = "hold/template__latch__fall__fall__glitch__minq__2.sp"

        return template_name

 

    #Removal SDN->CPN

    if( arc_type == "removal" and

                constr_pin == "SDN" and

                constr_pin_dir == "rise" and

                rel_pin == "CPN" and

                rel_pin_dir == "fall" and

                "Q" in probe_list and

                len(probe_list) == 1):

 

        template_name = "hold/template__latch__fall__rise__glitch__minq__1.sp"

        return template_name

 

 

    if( arc_type == "removal" and

                constr_pin == "SDN" and

                constr_pin_dir == "rise" and

                rel_pin == "CPN" and

                rel_pin_dir == "fall" and

                "Q" in probe_list and

                len(probe_list) == 2):

 

        template_name = "hold/template__latch__fall__rise__glitch__minq__2.sp"

        return template_name

 

 

    if( arc_type == "removal" and

                constr_pin == "SDN" and

                constr_pin_dir == "rise" and

                rel_pin == "CPN" and

                rel_pin_dir == "fall" and

                "QN" in probe_list and

                len(probe_list) == 1):

 

        template_name = "hold/template__latch__fall__rise__glitch__maxq__1.sp"

        return template_name

 

 

    if( arc_type == "removal" and

                constr_pin == "SDN" and

                constr_pin_dir == "rise" and

                rel_pin == "CPN" and

                rel_pin_dir == "fall" and

                "QN" in probe_list and

                len(probe_list) == 2):

 

        template_name = "hold/template__latch__fall__rise__glitch__maxq__2.sp"

        return template_name

 

    # Double probe, removal arcs for CP->CD with "bl_bx" probe, which requires mixed

    # glitch criteria (bl_bx switches opposite way of Q)

    if( arc_type == "removal" and

                constr_pin == "CD" and

                constr_pin_dir == "fall" and

                rel_pin == "CP" and

                rel_pin_dir == "rise" and

                "Q" in probe_list and

                "bl_bx" in probe_list and

                len(probe_list) == 2):

        template_name = "hold/template__latch__rise__fall__glitch__maxq__minbl_bx__2.sp"

        return template_name

 

    # Double probe, removal arcs for CP->SDN with "bl_bx" probe, which requires mixed

    # glitch criteria (bl_bx switches opposite way of Q)

    if( arc_type == "removal" and

                constr_pin == "SDN" and

                constr_pin_dir == "rise" and

                rel_pin == "CP" and

                rel_pin_dir == "rise" and

                "Q" in probe_list and

                "bl_bx" in probe_list and

                len(probe_list) == 2):

        template_name = "hold/template__latch__rise__rise__glitch__minq__maxbl_bx__2.sp"

        return template_name

 

    # glitch criteria (bl_bx switches opposite way of Q)

    if( arc_type == "removal" and

                constr_pin == "RETN" and

                constr_pin_dir == "rise" and

                rel_pin == "CP" and

                rel_pin_dir == "fall" and

                "Q" in probe_list and

                "bl_bx" in probe_list and

                len(probe_list) == 2):

        template_name = "hold/template__retn__removal__fall__rise__glitch__minq__maxbl_bx__2.sp"

        return template_name

 

    if( arc_type == "removal" and

                constr_pin == "RETN" and

                constr_pin_dir == "fall" and

                rel_pin == "CP" and

                rel_pin_dir == "rise" and

                "Q" in probe_list and

                len(probe_list) == 2):

        template_name = "hold/template__retn__removal__notD__rise__fall__pushout__2.sp"

        return template_name

 

    # Double probe, removal arcs for CP->CD with "sl_ax" probe, which requires mixed  # N3 probe change => add sl_bx & bl_b

    # glitch criteria (sl_ax switches opposite way of Q)

    if( arc_type == "removal" and

                constr_pin == "CD" and

                constr_pin_dir == "fall" and

                rel_pin == "CP" and

                rel_pin_dir == "rise" and

                "Q" in probe_list and

                "sl_ax" in probe_list and

                len(probe_list) == 2):

        template_name = "hold/template__latch__rise__fall__glitch__maxq__minsl_ax__2.sp"

        return template_name

   

    if( arc_type == "removal" and

                constr_pin == "CD" and

                constr_pin_dir == "fall" and

                rel_pin == "CP" and

                rel_pin_dir == "rise" and

                "Q" in probe_list and

                "sl_bx" in probe_list and

                len(probe_list) == 2):

        template_name = "hold/template__latch__rise__fall__glitch__maxq__minsl_bx__2.sp"

        return template_name

 

    if( arc_type == "removal" and

                constr_pin == "CD" and

                constr_pin_dir == "fall" and

                rel_pin == "CP" and

                rel_pin_dir == "rise" and

                "Q" in probe_list and

                "bl_b" in probe_list and

                len(probe_list) == 2):

        template_name = "hold/template__latch__rise__fall__glitch__maxq__maxbl_b__2.sp"

        return template_name

   

    # Double probe, removal arcs for SDN->CD with "sl_ax" probe, which requires mixed

    # glitch criteria (sl_ax switches opposite way of Q)

    if( arc_type == "removal" and

                constr_pin == "SDN" and

                constr_pin_dir == "rise" and

                rel_pin == "CP" and

                rel_pin_dir == "rise" and

                "Q" in probe_list and

                "sl_ax" in probe_list and

                len(probe_list) == 2):

        template_name = "hold/template__latch__rise__rise__glitch__minq__maxsl_ax__2.sp"

        return template_name

   

    # glitch criteria (sl_ax switches opposite way of Q)

    if( arc_type == "removal" and

                constr_pin == "RETN" and

                constr_pin_dir == "rise" and

                rel_pin == "CP" and

                rel_pin_dir == "fall" and

                "Q" in probe_list and

                "sl_ax" in probe_list and

                len(probe_list) == 2):

        template_name = "hold/template__retn__removal__fall__rise__glitch__minq__maxsl_ax__2.sp"

        return template_name

 

    # Single probe, removal arcs for CP->CD

    if( arc_type == "removal" and

                constr_pin == "CD" and

                constr_pin_dir == "fall" and

                rel_pin == "CP" and

                rel_pin_dir == "rise" and

                "Q" in probe_list and

                len(probe_list) == 1):

 

        template_name = "hold/template__latch__rise__fall__glitch__maxq__1.sp"

        return template_name

 

    # Single probe, removal arcs for SDN->CP

    if( arc_type == "removal" and

                fnmatch.fnmatch(cell_name, "*MB*") and

                constr_pin == "SDN" and

                constr_pin_dir == "rise" and

                rel_pin == "CP" and

                rel_pin_dir == "rise"):

 

        template_name = "hold/template__MB__latch__rise__rise__glitch__minq__1.sp"

        return template_name

 

    # Single probe, removal arcs for CDN->CP

    if( arc_type == "removal" and

                fnmatch.fnmatch(cell_name, "*MB*") and

                constr_pin == "CDN" and

                constr_pin_dir == "rise" and

                rel_pin == "CP" and

                rel_pin_dir == "rise"):

 

        template_name = "hold/template__MB__latch__rise__rise__glitch__maxq__1.sp"

        return template_name

 

    # Single probe, removal arcs for CP->CDN 2022/7/18 from LC

    if( arc_type == "removal" and

                constr_pin == "CDN" and

                constr_pin_dir == "rise" and

                rel_pin == "CPN" and

                rel_pin_dir == "fall" and

                "Q" in probe_list and

                len(probe_list) == 1):

 

        template_name = "hold/template__latch__fall__rise__glitch__maxq__1.sp"

        return template_name

    if( arc_type == "removal" and

                constr_pin == "CDN" and

                constr_pin_dir == "rise" and

                rel_pin == "CPN" and

                rel_pin_dir == "fall" and

                "QN" in probe_list and

                len(probe_list) == 1):

 

        template_name = "hold/template__latch__fall__rise__glitch__minq__1.sp"

        return template_name

 

    if( arc_type == "removal" and

                constr_pin == "CDN" and

                constr_pin_dir == "rise" and

                rel_pin == "CP" and

                rel_pin_dir == "rise" and

                "Q" in probe_list and

                len(probe_list) == 1):

 

        template_name = "hold/template__latch__rise__rise__glitch__maxq__1.sp"

        return template_name

 

    if( arc_type == "removal" and

                constr_pin == "CDN" and

                constr_pin_dir == "rise" and

                rel_pin == "CP" and

                rel_pin_dir == "rise" and

                "QN" in probe_list and

                len(probe_list) == 1):

 

        template_name = "hold/template__latch__rise__rise__glitch__minq__1.sp"

        return template_name

 

    # Single probe, removal arcs for SDN->CD

    if( arc_type == "removal" and

                constr_pin == "SDN" and

                constr_pin_dir == "rise" and

                rel_pin == "CP" and

                rel_pin_dir == "rise" and

                "Q" in probe_list and

                len(probe_list) == 1):

 

        template_name = "hold/template__latch__rise__rise__glitch__minq__1.sp"

        return template_name

 

    # Single probe for MB, removal arcs for CP->CD

    if( arc_type == "removal" and

                fnmatch.fnmatch(cell_name, "*MB*") and

                constr_pin == "CD" and

                constr_pin_dir == "fall" and

                rel_pin == "CP" and

                rel_pin_dir == "rise" and

                any(item.startswith('QN') for item in probe_list)):

 

        template_name = "hold/template__MB__latch__rise__fall__glitch__minq__1.sp"

        return template_name

 

    # Single probe for MB, removal arcs for CP->CD

    if( arc_type == "removal" and

                fnmatch.fnmatch(cell_name, "*MB*") and

                constr_pin == "CD" and

                constr_pin_dir == "fall" and

                rel_pin == "CP" and

                rel_pin_dir == "rise" and

                any(item.startswith('Q') for item in probe_list)):

#                filter(re.compile("Q").match, probe_list)):

 

        template_name = "hold/template__MB__latch__rise__fall__glitch__maxq__1.sp"

        return template_name

    # Single probe for MB, removal arcs for CP->CD

    if( arc_type == "removal" and

                fnmatch.fnmatch(cell_name, "*MB*") and

                constr_pin == "CD" and

                constr_pin_dir == "fall" and

                rel_pin == "CP" and

                rel_pin_dir == "rise" and

                any(item.startswith('bl1_b') for item in probe_list)):

#                filter(re.compile("Q").match, probe_list)):

 

        template_name = "hold/template__MB__latch__rise__fall__glitch__maxq__1.sp"

        return template_name

 

    # Double probe, removal arcs for CP->CD

    if( arc_type == "removal" and

                constr_pin == "CD" and

                constr_pin_dir == "fall" and

                rel_pin == "CP" and

                rel_pin_dir == "rise" and

                "Q" in probe_list and

                len(probe_list) == 2):

 

        template_name = "hold/template__latch__rise__fall__glitch__maxq__2.sp"

        return template_name

 

 

    if( arc_type == "removal" and

                constr_pin == "CD" and

                constr_pin_dir == "fall" and

                rel_pin == "CP" and

                rel_pin_dir == "rise" and

                "QN" in probe_list and

                len(probe_list) == 1):

 

        template_name = "hold/template__latch__rise__fall__glitch__minq__1.sp"

        return template_name

 

 

    if( arc_type == "removal" and

                constr_pin == "CD" and

                constr_pin_dir == "fall" and

                rel_pin == "CP" and

                rel_pin_dir == "rise" and

                "QN" in probe_list and

                len(probe_list) == 2):

 

        template_name = "hold/template__latch__rise__fall__glitch__minq__2.sp"

        return template_name

 

    # Double probe, removal arcs for SDN->CP

    if( arc_type == "removal" and

                constr_pin == "SDN" and

                constr_pin_dir == "rise" and

                rel_pin == "CP" and

                rel_pin_dir == "rise" and

                "Q" in probe_list and

                len(probe_list) == 2):

 

        template_name = "hold/template__latch__rise__rise__glitch__minq__2.sp"

        return template_name

 

 

    if( arc_type == "removal" and

                constr_pin == "SDN" and

                constr_pin_dir == "rise" and

                rel_pin == "CP" and

                rel_pin_dir == "rise" and

                "QN" in probe_list and

                len(probe_list) == 1):

 

        template_name = "hold/template__latch__rise__rise__glitch__maxq__1.sp"

        return template_name

 

 

    if( arc_type == "removal" and

                constr_pin == "SDN" and

                constr_pin_dir == "rise" and

                rel_pin == "CP" and

                rel_pin_dir == "rise" and

                "QN" in probe_list and

                len(probe_list) == 2):

 

        template_name = "hold/template__latch__rise__rise__glitch__maxq__2.sp"

        return template_name

 

 

    # CD(N) -> E(N)

    if( arc_type == "removal" and

                constr_pin == "CDN" and

                constr_pin_dir == "rise" and

                rel_pin == "E" and

                rel_pin_dir == "fall" and

                len(probe_list) == 1):

 

        template_name = "hold/template__latch__fall__rise__glitch__maxq__1.sp"

        return template_name

 

 

    if( arc_type == "removal" and

                constr_pin == "CDN" and

                constr_pin_dir == "rise" and

                rel_pin == "E" and

                rel_pin_dir == "fall" and

                len(probe_list) == 2):

 

        template_name = "hold/template__latch__fall__rise__glitch__maxq__2.sp"

        return template_name

 

 

    if( arc_type == "removal" and

                constr_pin == "CDN" and

                constr_pin_dir == "rise" and

                rel_pin == "EN" and

                rel_pin_dir == "rise" and

                len(probe_list) == 1):

 

        template_name = "hold/template__latch__rise__rise__glitch__maxq__1.sp"

        return template_name

 

 

    if( arc_type == "removal" and

                constr_pin == "CDN" and

                constr_pin_dir == "rise" and

                rel_pin == "EN" and

                rel_pin_dir == "rise" and

                len(probe_list) == 2):

 

        template_name = "hold/template__latch__rise__rise__glitch__maxq__2.sp"

        return template_name

 

    #SDN->E(N)

    if( arc_type == "removal" and

                constr_pin == "SDN" and

                constr_pin_dir == "rise" and

                rel_pin == "E" and

                rel_pin_dir == "fall" and

                len(probe_list) == 1):

 

        template_name = "hold/template__latch__fall__rise__glitch__minq__1.sp"

        return template_name

 

 

    if( arc_type == "removal" and

                constr_pin == "SDN" and

                constr_pin_dir == "rise" and

                rel_pin == "E" and

                rel_pin_dir == "fall" and

                len(probe_list) == 2):

 

        template_name = "hold/template__latch__fall__rise__glitch__minq__2.sp"

        return template_name

 

 

    if( arc_type == "removal" and

                constr_pin == "SDN" and

                constr_pin_dir == "rise" and

                rel_pin == "EN" and

                rel_pin_dir == "rise" and

                len(probe_list) == 1):

 

        template_name = "hold/template__latch__rise__rise__glitch__minq__1.sp"

        return template_name

 

 

    if( arc_type == "removal" and

                constr_pin == "SDN" and

                constr_pin_dir == "rise" and

                rel_pin == "EN" and

                rel_pin_dir == "rise" and

                len(probe_list) == 2):

 

        template_name = "hold/template__latch__rise__rise__glitch__minq__2.sp"

        return template_name

    ## LND2SR mpw (clockpin SDN and CDN)

    if( arc_type == "min_pulse_width" and

                (constr_pin == "CDN" or constr_pin == "SDN") and

                constr_pin_dir == "fall" and

                fnmatch.fnmatch(cell_name, "*LND2SR*")):

                template_name = "min_pulse_width/template__LND2SR__fall_rise__1.sp"

                return template_name

 

 

    ## min_pulse_width DECK mapping rule (2023/1/17) ##

 

    if( arc_type == "min_pulse_width" and

                constr_pin == "CP" and

                constr_pin_dir == "rise"):

        if(fnmatch.fnmatch(cell_name, "*SYNC2*")):

                template_name = "min_pulse_width/template__sync2__CP__rise__fall__1.sp"

                return template_name

        if(fnmatch.fnmatch(cell_name, "*SYNC3*")):

                template_name = "min_pulse_width/template__sync3__CP__rise__fall__1.sp"

                return template_name

        if(fnmatch.fnmatch(cell_name, "*SYNC4*")):

                template_name = "min_pulse_width/template__sync4__CP__rise__fall__1.sp"

                return template_name

        if(fnmatch.fnmatch(cell_name, "*SYNC5*")):

                template_name = "min_pulse_width/template__sync5__CP__rise__fall__1.sp"

                return template_name

        if(fnmatch.fnmatch(cell_name, "*SYNC6*")):

                template_name = "min_pulse_width/template__sync6__CP__rise__fall__1.sp"

                return template_name

 

    if( arc_type == "min_pulse_width" and

                fnmatch.fnmatch(cell_name, "*SYNC1P5*")):

        if(constr_pin == "CP" and constr_pin_dir == "rise"):

                template_name = "min_pulse_width/template__sync1p5__CP__rise__fall__1.sp"

                return template_name

        if(constr_pin == "CP" and constr_pin_dir == "fall"):

            if len(probe_list) == 1 and 'Q1' in probe_list and fnmatch.fnmatch(cell_name, "*SDF*") and '!SE' in when :

                template_name = "min_pulse_width/template__sync1p5__q1__CP__fall__rise__1.sp"

                return template_name

            else:

                template_name = "min_pulse_width/template__sync1p5__CP__fall__rise__1.sp"

                return template_name

        if(constr_pin == "CPN" and constr_pin_dir == "rise"):

            if len(probe_list) == 1 and 'Q1' in probe_list and fnmatch.fnmatch(cell_name, "*SDF*") and '!SE' in when :

                template_name = "min_pulse_width/template__sync1p5__q1__CPN__rise__fall__1.sp"

                return template_name

            else:

                template_name = "min_pulse_width/template__sync1p5__CPN__rise__fall__1.sp"

                return template_name

        if(constr_pin == "CPN" and constr_pin_dir == "fall"):

                template_name = "min_pulse_width/template__sync1p5__CPN__fall__rise__1.sp"

                return template_name

 

    if( arc_type == "min_pulse_width" and

                fnmatch.fnmatch(constr_pin, "CP") and

                constr_pin_dir == "fall" ):

 

        if(fnmatch.fnmatch(cell_name, "*SYNC2*")):

                template_name = "min_pulse_width/template__CP__sync2__D__fall__rise__1.sp"

                return template_name

        if(fnmatch.fnmatch(cell_name, "*SYNC3*")):

                template_name = "min_pulse_width/template__CP__sync3__D__fall__rise__1.sp"

                return template_name

        if(fnmatch.fnmatch(cell_name, "*SYNC4*")):

                template_name = "min_pulse_width/template__CP__sync4__D__fall__rise__1.sp"

                return template_name

        if(fnmatch.fnmatch(cell_name, "*SYNC5*")):

                template_name = "min_pulse_width/template__CP__sync5__D__fall__rise__1.sp"

                return template_name

        if(fnmatch.fnmatch(cell_name, "*SYNC6*")):

                template_name = "min_pulse_width/template__CP__sync6__D__fall__rise__1.sp"

                return template_name

 

    if( arc_type == "min_pulse_width" and

                fnmatch.fnmatch(constr_pin, "WWL") and

                constr_pin_dir == "rise" and

                fnmatch.fnmatch(rel_pin, "WWL") and

                when == "D"):

 

        template_name = "min_pulse_width/template__WWL__rise__fall__1.sp"

        return template_name

 

    if( arc_type == "min_pulse_width" and

                fnmatch.fnmatch(constr_pin, "WWL0") and

                constr_pin_dir == "rise" and

                fnmatch.fnmatch(rel_pin, "WWL0") and

                when == "D"):

 

        template_name = "min_pulse_width/template__WWL0__rise__fall__1.sp"

        return template_name

 

    if( arc_type == "min_pulse_width" and

                fnmatch.fnmatch(constr_pin, "WWL1") and

                constr_pin_dir == "rise" and

                fnmatch.fnmatch(rel_pin, "WWL1") and

                 when == "D"):

 

        template_name = "min_pulse_width/template__WWL1__rise__fall__1.sp"

        return template_name

 

    if( arc_type == "min_pulse_width" and

                fnmatch.fnmatch(constr_pin, "WWL_N") and

                constr_pin_dir == "fall" and

                fnmatch.fnmatch(rel_pin, "WWL_N") and

                "!D" in when):

 

        template_name = "min_pulse_width/template__WWLN__fall__rise__1.sp"

        return template_name

 

    if( arc_type == "min_pulse_width" and

                fnmatch.fnmatch(constr_pin, "WWL0_N") and

                constr_pin_dir == "fall" and

                fnmatch.fnmatch(rel_pin, "WWL0_N") and

                "!D" in when):

 

        template_name = "min_pulse_width/template__WWL0N__fall__rise__1.sp"

        return template_name

 

    if( arc_type == "min_pulse_width" and

                fnmatch.fnmatch(constr_pin, "WWL1_N") and

                constr_pin_dir == "fall" and

                fnmatch.fnmatch(rel_pin, "WWL1_N") and

                "!D" in when):

 

        template_name = "min_pulse_width/template__WWL1N__fall__rise__1.sp"

        return template_name

 

    if( arc_type == "min_pulse_width" and

                (fnmatch.fnmatch(cell_name, "CKGOR*") or fnmatch.fnmatch(cell_name, "CKGOA*") or fnmatch.fnmatch(cell_name, "CKGNR*")) and

                fnmatch.fnmatch(constr_pin, "CP") and

                constr_pin_dir == "fall" and

                fnmatch.fnmatch(rel_pin, "CP")):

 

        template_name = "min_pulse_width/template__CKGOR2__fall__rise__1.sp"

        return template_name

 

    if( arc_type == "min_pulse_width" and

                fnmatch.fnmatch(cell_name, "PTCKG*") and

                fnmatch.fnmatch(constr_pin, "CP") and

                constr_pin_dir == "rise" and

                fnmatch.fnmatch(rel_pin, "CP")):

 

        template_name = "min_pulse_width/template__PTCKG__CP__rise__fall__1.sp"

        return template_name

 

    if( arc_type == "min_pulse_width" and

                fnmatch.fnmatch(cell_name, "PTCKG*") and

                fnmatch.fnmatch(constr_pin, "CP") and

                constr_pin_dir == "fall" and

                fnmatch.fnmatch(rel_pin, "CP")):

 

        template_name = "min_pulse_width/template__PTCKG__CP__fall__rise__1.sp"

        return template_name

 

    if( arc_type == "min_pulse_width" and

                (fnmatch.fnmatch(cell_name, "CKGOR*") or fnmatch.fnmatch(cell_name, "CKGOA*") or fnmatch.fnmatch(cell_name, "CKGNR*")) and

                fnmatch.fnmatch(constr_pin, "CP") and

                constr_pin_dir == "rise" and

                fnmatch.fnmatch(rel_pin, "CP")):

 

        template_name = "min_pulse_width/template__CKGOR2__rise__fall__1.sp"

        return template_name

 

    if( arc_type == "min_pulse_width" and

                fnmatch.fnmatch(cell_name, "CKGMUX3*") and

                (fnmatch.fnmatch(constr_pin, "I0") or fnmatch.fnmatch(constr_pin, "I1") or fnmatch.fnmatch(constr_pin, "I2")) and

                constr_pin_dir == "fall"):

 

        template_name = "min_pulse_width/template__CKGMUX3__fall__rise__1.sp"

        return template_name

 

    if( arc_type == "min_pulse_width" and

                fnmatch.fnmatch(cell_name, "CKGMUX3*") and

                (fnmatch.fnmatch(constr_pin, "I0") or fnmatch.fnmatch(constr_pin, "I1") or fnmatch.fnmatch(constr_pin, "I2")) and

                constr_pin_dir == "rise"):

 

        template_name = "min_pulse_width/template__CKGMUX3__rise__fall__1.sp"

        return template_name

 

    if( arc_type == "min_pulse_width" and

                fnmatch.fnmatch(cell_name, "CKGMUX*") and

                (fnmatch.fnmatch(constr_pin, "S") or fnmatch.fnmatch(constr_pin, "I1")) and

                constr_pin_dir == "fall"):

 

        template_name = "min_pulse_width/template__S__fall__rise__1.sp"

        return template_name

 

    if( arc_type == "min_pulse_width" and

                fnmatch.fnmatch(cell_name, "CKGMUX*") and

                (fnmatch.fnmatch(constr_pin, "S") or fnmatch.fnmatch(constr_pin, "I1")) and

                constr_pin_dir == "rise"):

 

        template_name = "min_pulse_width/template__S__rise__fall__1.sp"

        return template_name

 

    if( arc_type == "min_pulse_width" and

                fnmatch.fnmatch(cell_name, "CKGMUX*") and

                fnmatch.fnmatch(constr_pin, "I0") and

                constr_pin_dir == "fall" and

                fnmatch.fnmatch(rel_pin, "I0")):

 

        template_name = "min_pulse_width/template__I0__fall__rise__1.sp"

        return template_name

 

    if( arc_type == "min_pulse_width" and

                fnmatch.fnmatch(cell_name, "CKGMUX*") and

                fnmatch.fnmatch(constr_pin, "I0") and

                constr_pin_dir == "rise" and

                fnmatch.fnmatch(rel_pin, "I0")):

 

        template_name = "min_pulse_width/template__I0__rise__fall__1.sp"

        return template_name

 

    if( arc_type == "min_pulse_width" and

                (fnmatch.fnmatch(cell_name, "*OR2*") or fnmatch.fnmatch(cell_name, "*OA2*")) and

                fnmatch.fnmatch(constr_pin, "CP") and

                constr_pin_dir == "fall" and

                fnmatch.fnmatch(rel_pin, "CP")):

 

        template_name = "min_pulse_width/template__OR2__fall__rise__1.sp"

        return template_name

 

    if( arc_type == "min_pulse_width" and

                (fnmatch.fnmatch(cell_name, "*OR2*") or fnmatch.fnmatch(cell_name, "*OA2*")) and

                fnmatch.fnmatch(constr_pin, "CP") and

                constr_pin_dir == "rise" and

                fnmatch.fnmatch(rel_pin, "CP")):

 

        template_name = "min_pulse_width/template__OR2__rise__fall__1.sp"

        return template_name

 

    if( arc_type == "min_pulse_width" and

                fnmatch.fnmatch(cell_name, "*AO2*") and

                fnmatch.fnmatch(constr_pin, "CP") and

                constr_pin_dir == "fall" and

                fnmatch.fnmatch(rel_pin, "CP")):

 

        template_name = "min_pulse_width/template__AO2__fall__rise__1.sp"

        return template_name

 

    if( arc_type == "min_pulse_width" and

                fnmatch.fnmatch(cell_name, "*AO2*") and

                fnmatch.fnmatch(constr_pin, "CP") and

                constr_pin_dir == "rise" and

                fnmatch.fnmatch(rel_pin, "CP")):

 

        template_name = "min_pulse_width/template__AO2__rise__fall__1.sp"

        return template_name

 

    if( arc_type == "min_pulse_width" and

                fnmatch.fnmatch(constr_pin, "CP") and

                constr_pin_dir == "fall" and

                fnmatch.fnmatch(rel_pin, "CP") and

                "DA" in when):

 

        template_name = "min_pulse_width/template__DA__fall__rise__1.sp"

        return template_name

 

    if( arc_type == "min_pulse_width" and

                fnmatch.fnmatch(constr_pin, "CP") and

                constr_pin_dir == "rise" and

                fnmatch.fnmatch(rel_pin, "CP") and

                "DA" in when):

 

        template_name = "min_pulse_width/template__DA__rise__rise__1.sp"

        return template_name

 

    # multi-probe for RETN

    if( arc_type == "min_pulse_width" and

                fnmatch.fnmatch(constr_pin, "CP") and

                constr_pin_dir == "fall" and

                fnmatch.fnmatch(rel_pin, "CP") and

                len(probe_list) == 2):

 

        if(fnmatch.fnmatch(cell_name, "*DRDF*")):

            template_name = "min_pulse_width/template__DRDF__CP__fall__rise__2.sp"

            return template_name

        else:

            template_name = "min_pulse_width/template__retn__CP__fall__rise__2.sp"

            return template_name

 

    if( arc_type == "min_pulse_width" and

                fnmatch.fnmatch(constr_pin, "CP") and

                constr_pin_dir == "rise" and

                fnmatch.fnmatch(rel_pin, "CP") and

                len(probe_list) == 2):

 

        if(fnmatch.fnmatch(cell_name, "*DRDF*")):

            template_name = "min_pulse_width/template__DRDF__CP__rise__fall__2.sp"

            return template_name

        else:

            template_name = "min_pulse_width/template__retn__CP__rise__fall__2.sp"

            return template_name

 

    if( arc_type == "min_pulse_width" and

                fnmatch.fnmatch(cell_name, "*DETQNLTSO*") and

                fnmatch.fnmatch(constr_pin, "CP") and

                constr_pin_dir == "rise" and

                fnmatch.fnmatch(rel_pin, "CP") and

                "!D" not in when):

 

        template_name = "min_pulse_width/template__DET__LP__D__CP__rise__fall__1.sp"

        return template_name

 

    if( arc_type == "min_pulse_width" and

                fnmatch.fnmatch(cell_name, "*DETQNRESO*") and

                fnmatch.fnmatch(constr_pin, "CP") and

                constr_pin_dir == "rise" and

                fnmatch.fnmatch(rel_pin, "CP") and

                "!D" not in when):

 

        template_name = "min_pulse_width/template__DET__RE__D__CP__rise__fall__1.sp"

        return template_name

 

    if( arc_type == "min_pulse_width" and

                fnmatch.fnmatch(cell_name, "*DETQNLTSO*")  and

                fnmatch.fnmatch(constr_pin, "CP") and

                constr_pin_dir == "rise" and

                fnmatch.fnmatch(rel_pin, "CP") and

                "!D" in when):

 

        template_name = "min_pulse_width/template__DET__LP__notD__CP__rise__fall__1.sp"

        return template_name

 

    if( arc_type == "min_pulse_width" and

                fnmatch.fnmatch(cell_name, "*DETQNRESO*") and

                fnmatch.fnmatch(constr_pin, "CP") and

                constr_pin_dir == "rise" and

                fnmatch.fnmatch(rel_pin, "CP") and

                "!D" in when):

 

        template_name = "min_pulse_width/template__DET__RE__notD__CP__rise__fall__1.sp"

        return template_name

 

    if( arc_type == "min_pulse_width" and

                fnmatch.fnmatch(cell_name, "*DETQNLTSO*")  and

                fnmatch.fnmatch(constr_pin, "CP") and

                constr_pin_dir == "fall" and

                fnmatch.fnmatch(rel_pin, "CP") and

                "!D" not in when):

 

            template_name = "min_pulse_width/template__DET__LP__D__CP__fall__rise__1.sp"

            return template_name

 

    if( arc_type == "min_pulse_width" and

                fnmatch.fnmatch(cell_name, "*DETQNRESO*") and

                fnmatch.fnmatch(constr_pin, "CP") and

                constr_pin_dir == "fall" and

                fnmatch.fnmatch(rel_pin, "CP") and

                "!D" not in when):

 

            template_name = "min_pulse_width/template__DET__RE__D__CP__fall__rise__1.sp"

            return template_name

 

    if( arc_type == "min_pulse_width" and

                fnmatch.fnmatch(cell_name, "*DETQNLTSO*")  and

                fnmatch.fnmatch(constr_pin, "CP") and

                constr_pin_dir == "fall" and

                fnmatch.fnmatch(rel_pin, "CP") and

                "!D" in when):

 

            template_name = "min_pulse_width/template__DET__LP__notD__CP__fall__rise__1.sp"

            return template_name

 

    if( arc_type == "min_pulse_width" and

                fnmatch.fnmatch(cell_name, "*DETQNRESO*") and

                fnmatch.fnmatch(constr_pin, "CP") and

                constr_pin_dir == "fall" and

                fnmatch.fnmatch(rel_pin, "CP") and

                "!D" in when):

 

            template_name = "min_pulse_width/template__DET__RE__notD__CP__fall__rise__1.sp"

            return template_name

 

    if( arc_type == "min_pulse_width" and

                fnmatch.fnmatch(constr_pin, "CP") and

                constr_pin_dir == "fall" and

                fnmatch.fnmatch(rel_pin, "CP")):

       

        if(fnmatch.fnmatch(cell_name, "*DET*")):

            template_name = "min_pulse_width/template__DET__CP__fall__rise__1.sp"

            return template_name

        else:

            template_name = "min_pulse_width/template__CP__fall__rise__1.sp"

            return template_name

 

    if( arc_type == "min_pulse_width" and

                fnmatch.fnmatch(constr_pin, "CP") and

                constr_pin_dir == "rise" and

                fnmatch.fnmatch(rel_pin, "CP")):

 

        template_name = "min_pulse_width/template__CP__rise__fall__1.sp"

        return template_name

 

    if( arc_type == "min_pulse_width" and

                fnmatch.fnmatch(constr_pin, "CPN") and

                constr_pin_dir == "fall" and

                fnmatch.fnmatch(rel_pin, "CPN")):

 

        template_name = "min_pulse_width/template__CPN__fall__rise__1.sp"

        return template_name

 

    if( arc_type == "min_pulse_width" and

                fnmatch.fnmatch(constr_pin, "CPN") and

                constr_pin_dir == "rise" and

                fnmatch.fnmatch(rel_pin, "CPN")):

 

        template_name = "min_pulse_width/template__CPN__rise__fall__1.sp"

        return template_name

 

    if( arc_type == "min_pulse_width" and

                fnmatch.fnmatch(constr_pin, "EN") and

                constr_pin_dir == "fall" and

                fnmatch.fnmatch(rel_pin, "EN") and

                "D" in when):

 

        template_name = "min_pulse_width/template__EN__fall__rise__1.sp"

        return template_name

 

    if( arc_type == "min_pulse_width" and

                fnmatch.fnmatch(constr_pin, "E") and

                constr_pin_dir == "rise" and

                fnmatch.fnmatch(rel_pin, "E") and

                "D" in when):

 

        template_name = "min_pulse_width/template__E__rise__rise__1.sp"

        return template_name

 

    if( arc_type == "setup" and

                fnmatch.fnmatch(constr_pin, "D*") and

                constr_pin_dir == "rise" and

                fnmatch.fnmatch(rel_pin, "CP") and

                rel_pin_dir == "rise" and

                len(probe_list) == 1):

 

        template_name = "setup/template__common__rise__rise__1.sp"

        return template_name

 

 

    if( arc_type == "setup" and

                fnmatch.fnmatch(constr_pin, "D*") and

                constr_pin_dir == "rise" and

                fnmatch.fnmatch(rel_pin, "CP") and

                rel_pin_dir == "rise" and

                len(probe_list) == 2):

 

        template_name = "setup/template__common__rise__rise__2.sp"

        return template_name

 

 

    if( arc_type == "setup" and

                fnmatch.fnmatch(constr_pin, "D*") and

                constr_pin_dir == "fall" and

                fnmatch.fnmatch(rel_pin, "CP") and

                rel_pin_dir == "rise" and

                len(probe_list) == 1):

 

        template_name = "setup/template__common__rise__fall__1.sp"

        return template_name

 

 

    if( arc_type == "setup" and

                fnmatch.fnmatch(constr_pin, "D*") and

                constr_pin_dir == "fall" and

                fnmatch.fnmatch(rel_pin, "CP") and

                rel_pin_dir == "rise" and

                len(probe_list) == 2):

 

        template_name = "setup/template__common__rise__fall__2.sp"

        return template_name

 

    # Common (CPN pins) template - 2019/09/05 Ray Jr. update

    if( arc_type == "setup" and

                fnmatch.fnmatch(constr_pin, "D*") and

                constr_pin_dir == "rise" and

                fnmatch.fnmatch(rel_pin, "CPN") and

                rel_pin_dir == "fall" ):

 

        template_name = "setup/template__common__fall__rise__1.sp"

        return template_name

 

 

    if( arc_type == "setup" and

                fnmatch.fnmatch(constr_pin, "D*") and

                constr_pin_dir == "fall" and

                fnmatch.fnmatch(rel_pin, "CPN") and

                rel_pin_dir == "fall" ):

 

        template_name = "setup/template__common__fall__fall__1.sp"

        return template_name

 

    # LH latches

    if( arc_type == "setup" and

                fnmatch.fnmatch(constr_pin, "D*") and

                constr_pin_dir == "rise" and

                rel_pin == "E" and

                rel_pin_dir == "fall" ):

 

        template_name = "setup/template__common__LH__fall__rise__1.sp"

        return template_name

 

 

    if( arc_type == "setup" and

                fnmatch.fnmatch(constr_pin, "D*") and

                constr_pin_dir == "fall" and

                rel_pin == "E" and

                rel_pin_dir == "fall" ):

 

        template_name = "setup/template__common__LH__fall__fall__1.sp"

        return template_name

 

 

    # LN latches

    if( arc_type == "setup" and

                fnmatch.fnmatch(constr_pin, "D*") and

                constr_pin_dir == "rise" and

                rel_pin == "EN" and

                rel_pin_dir == "rise" ):

 

        template_name = "setup/template__common__LN__rise__rise__1.sp"

        return template_name

 

    if( arc_type == "setup" and

                fnmatch.fnmatch(constr_pin, "D*") and

                constr_pin_dir == "fall" and

                rel_pin == "EN" and

                rel_pin_dir == "rise" ):

 

        template_name = "setup/template__common__LN__rise__fall__1.sp"

        return template_name

 

    if( arc_type in delay_arc_types and

                fnmatch.fnmatch(cell_name, "INVD*") and

                constr_pin == "ZN" and

                rel_pin == "I" and

                rel_pin_dir == "rise"):

 

        template_name = "delay/template__invdX__fall.sp"

        return template_name

 

    if( arc_type in delay_arc_types and

                fnmatch.fnmatch(cell_name, "INVD*") and

                constr_pin == "ZN" and

                rel_pin == "I" and

                rel_pin_dir == "fall"):

 

        template_name = "delay/template__invdX__rise.sp"

        return template_name

 

    return None

 

 

def getThanosTemplateName(cell_name, arc_type, constr_pin, constr_pin_dir, rel_pin,

                          rel_pin_dir, when, probe_list):

 

    # Ignore SYNC 2 removal arcs

    if( arc_type == "removal" and

            fnmatch.fnmatch(cell_name, "*SYNC2*Q*")):

 

        template_name = None

        return template_name

 

    # Ignore SYNC 3 removal arcs

    if( arc_type == "removal" and

            fnmatch.fnmatch(cell_name, "*SYNC3*Q*")):

 

        template_name = None

        return template_name

 

    # Ignore SYNC 4 removal arcs

    if( arc_type == "removal" and

            fnmatch.fnmatch(cell_name, "*SYNC4*Q*")):

 

        template_name = None

        return template_name

 

    # SYNC2 cell for constr_pin = D, rel_pin = CP, fall_constraint, Q1 internal probe

    if( arc_type == "hold" and

                fnmatch.fnmatch(cell_name, "*SYNC2*Q*") and

                constr_pin == "D" and

                constr_pin_dir == "fall" and

                rel_pin == "CP" and

                rel_pin_dir == "rise" and

                "Q1" in probe_list):

 

        template_name = "hold/template__sync2__q1__rise__fall__1.thanos.sp"

        return template_name

 

    # SYNC2 cell for constr_pin = D, rel_pin = CP, rise_constraint, Q1 internal probe

    if( arc_type == "hold" and

                fnmatch.fnmatch(cell_name, "*SYNC2*Q*") and

                constr_pin == "D" and

                constr_pin_dir == "rise" and

                rel_pin == "CP" and

                rel_pin_dir == "rise" and

                "Q1" in probe_list):

 

        template_name = "hold/template__sync2__q1__rise__rise__1.thanos.sp"

        return template_name

 

    # SYNC3 cell for constr_pin = D, rel_pin = CP, fall_constraint, Q1 internal probe

    if( arc_type == "hold" and

                fnmatch.fnmatch(cell_name, "*SYNC3*Q*") and

                constr_pin == "D" and

                constr_pin_dir == "fall" and

                rel_pin == "CP" and

                rel_pin_dir == "rise" and

                "Q1" in probe_list):

 

        template_name = "hold/template__sync3__q1__rise__fall__1.thanos.sp"

        return template_name

 

    # SYNC3 cell for constr_pin = D, rel_pin = CP, rise_constraint, Q1 internal probe

    if( arc_type == "hold" and

                fnmatch.fnmatch(cell_name, "*SYNC3*Q*") and

                constr_pin == "D" and

                constr_pin_dir == "rise" and

                rel_pin == "CP" and

                rel_pin_dir == "rise" and

                "Q1" in probe_list):

 

        template_name = "hold/template__sync3__q1__rise__rise__1.thanos.sp"

        return template_name

 

    # SYNC4 cell for constr_pin = D, rel_pin = CP, fall_constraint, Q1 internal probe

    if( arc_type == "hold" and

                fnmatch.fnmatch(cell_name, "*SYNC4*Q*") and

                constr_pin == "D" and

                constr_pin_dir == "fall" and

                rel_pin == "CP" and

                rel_pin_dir == "rise" and

                "Q1" in probe_list):

 

        template_name = "hold/template__sync4__q1__rise__fall__1.thanos.sp"

        return template_name

 

    # SYNC4 cell for constr_pin = D, rel_pin = CP, rise_constraint, Q1 internal probe

    if( arc_type == "hold" and

                fnmatch.fnmatch(cell_name, "*SYNC4*Q*") and

                constr_pin == "D" and

                constr_pin_dir == "rise" and

                rel_pin == "CP" and

                rel_pin_dir == "rise" and

                "Q1" in probe_list):

 

        template_name = "hold/template__sync4__q1__rise__rise__1.thanos.sp"

        return template_name

 

    # *EDF*Q cell for constr_pin = E, rel_pin = CP, and D=1 in when condition

    if( arc_type == "hold" and

                fnmatch.fnmatch(cell_name, "*EDF*D*") and

                constr_pin == "E" and

                constr_pin_dir == "fall" and

                rel_pin == "CP" and

                rel_pin_dir == "rise" and

                "D" in when and

                not "!D" in when and

                len(probe_list) == 1):

 

        template_name = "hold/template__EDF__D__rise__fall__pushout__1.thanos.sp"

        return template_name

 

    # *EDF*Q cell for constr_pin = E, rel_pin = CP and D=0 in when condition

    if( arc_type == "hold" and

                fnmatch.fnmatch(cell_name, "*EDF*D*") and

                constr_pin == "E" and

                constr_pin_dir == "fall" and

                rel_pin == "CP" and

                rel_pin_dir == "rise" and

                "!D" in when and

                len(probe_list) == 1):

 

        template_name = "hold/template__EDF__notD__rise__fall__pushout__1.thanos.sp"

        return template_name

 

    # *EDF*Q cell for constr_pin = E, rel_pin = CP, and D=1 in when, rise_constraint

    if( arc_type == "hold" and

            fnmatch.fnmatch(cell_name, "*EDF*D*") and

                constr_pin == "E" and

                constr_pin_dir == "rise" and

                rel_pin == "CP" and

                rel_pin_dir == "rise" and

                "D" in when and

            not "!D" in when and

                len(probe_list) == 1):

 

        template_name = "hold/template__EDF__D__rise__rise__glitch__1.thanos.sp"

        return template_name

 

    # *EDF*Q cell for constr_pin = E, rel_pin = CP and D=0 in when, rise_constraint

    if( arc_type == "hold" and

            fnmatch.fnmatch(cell_name, "*EDF*D*") and

                constr_pin == "E" and

                constr_pin_dir == "rise" and

                rel_pin == "CP" and

                rel_pin_dir == "rise" and

                "!D" in when and

                len(probe_list) == 1):

 

        template_name = "hold/template__EDF__notD__rise__rise__glitch__1.thanos.sp"

        return template_name

 

    # SI->CP

    if( arc_type == "hold" and

                fnmatch.fnmatch(constr_pin, "SI") and

                constr_pin_dir == "rise" and

                fnmatch.fnmatch(rel_pin, "CP") and

                rel_pin_dir == "rise" and

                len(probe_list) == 1):

 

        template_name = "hold/template__common__rise__rise__1.thanos.sp"

        return template_name

 

    if( arc_type == "hold" and

                fnmatch.fnmatch(constr_pin, "SI") and

                constr_pin_dir == "fall" and

                fnmatch.fnmatch(rel_pin, "CP") and

                rel_pin_dir == "rise" and

                len(probe_list) == 1):

 

        template_name = "hold/template__common__rise__fall__1.thanos.sp"

        return \

            template_name

 

    if( arc_type == "hold" and

                fnmatch.fnmatch(constr_pin, "SI") and

                constr_pin_dir == "rise" and

                fnmatch.fnmatch(rel_pin, "CP") and

                rel_pin_dir == "rise" and

                len(probe_list) == 2):

 

        template_name = "hold/template__common__rise__rise__2.thanos.sp"

        return template_name

 

    if( arc_type == "hold" and

                fnmatch.fnmatch(constr_pin, "SI") and

                constr_pin_dir == "fall" and

                fnmatch.fnmatch(rel_pin, "CP") and

                rel_pin_dir == "rise" and

                len(probe_list) == 2):

 

        template_name = "hold/template__common__rise__fall__2.thanos.sp"

        return \

            template_name

 

 

    if( arc_type == "hold" and

                fnmatch.fnmatch(constr_pin, "NRESTORE") and

                constr_pin_dir == "rise" and

                fnmatch.fnmatch(rel_pin, "CP") and

                rel_pin_dir == "fall" and

#                "Q" in probe_list and

                len(probe_list) == 1):

 

        template_name = "hold/template__rsdf__Q__fall__rise__pushout__1.thanos.sp"

        return template_name

 

    if( arc_type == "hold" and

                fnmatch.fnmatch(constr_pin, "SAVE") and

                constr_pin_dir == "fall" and

                fnmatch.fnmatch(rel_pin, "CP") and

                rel_pin_dir == "rise" and

#                "Q" in probe_list and

                len(probe_list) == 1):

 

        template_name = "hold/template__rsdf__Q__rise__fall__pushout__1.thanos.sp"

        return \

            template_name

 

 

    # SE to CP

    if( arc_type == "hold" and

                fnmatch.fnmatch(constr_pin, "SE") and

                constr_pin_dir == "rise" and

                (fnmatch.fnmatch(rel_pin, "CP") or fnmatch.fnmatch(rel_pin, "CLK")) and

                rel_pin_dir == "rise" and

                len(probe_list) == 1):

 

        template_name = "hold/template__common__rise__rise__1.thanos.sp"

        return template_name

 

    if( arc_type == "hold" and

                fnmatch.fnmatch(constr_pin, "SE") and

                constr_pin_dir == "fall" and

                (fnmatch.fnmatch(rel_pin, "CP") or fnmatch.fnmatch(rel_pin, "CLK")) and

                rel_pin_dir == "rise" and

                len(probe_list) == 1):

 

        template_name = "hold/template__common__rise__fall__1.thanos.sp"

        return \

            template_name

 

    if( arc_type == "hold" and

                fnmatch.fnmatch(constr_pin, "SE") and

                constr_pin_dir == "rise" and

                fnmatch.fnmatch(rel_pin, "CP") and

                rel_pin_dir == "rise" and

                len(probe_list) == 2):

 

        template_name = "hold/template__common__rise__rise__2.thanos.sp"

        return template_name

 

    if( arc_type == "hold" and

                fnmatch.fnmatch(constr_pin, "SE") and

                constr_pin_dir == "fall" and

                fnmatch.fnmatch(rel_pin, "CP") and

                rel_pin_dir == "rise" and

                len(probe_list) == 2):

 

        template_name = "hold/template__common__rise__fall__2.thanos.sp"

        return \

            template_name

 

    # DA/DB -> CP (OR2)

    if( arc_type == "hold" and

            fnmatch.fnmatch(cell_name, "MB8SRLSDFOR2*") and

            fnmatch.fnmatch(constr_pin, "DA*") and

            constr_pin_dir == "rise" and

            fnmatch.fnmatch(rel_pin, "CP") and

            rel_pin_dir == "rise" and

            len(probe_list) == 1):

       

        template_name = "hold/template__common__rise__DA__rise__1.thanos.sp"

        return template_name

 

    if( arc_type == "hold" and

            fnmatch.fnmatch(cell_name, "MB8SRLSDFOR2*") and

            fnmatch.fnmatch(constr_pin, "DA*") and

            constr_pin_dir == "fall" and

            fnmatch.fnmatch(rel_pin, "CP") and

            rel_pin_dir == "rise" and

            len(probe_list) == 1):

 

        template_name = "hold/template__common__rise__DA__fall__1.thanos.sp"

        return template_name

 

    if( arc_type == "hold" and

            fnmatch.fnmatch(cell_name, "MB8SRLSDFOR2*") and

            fnmatch.fnmatch(constr_pin, "DB*") and

            constr_pin_dir == "rise" and

            fnmatch.fnmatch(rel_pin, "CP") and

            rel_pin_dir == "rise" and

            len(probe_list) == 1):

 

        template_name = "hold/template__common__rise__DB__rise__1.thanos.sp"

        return template_name

 

    if( arc_type == "hold" and

            fnmatch.fnmatch(cell_name, "MB8SRLSDFOR2*") and

            fnmatch.fnmatch(constr_pin, "DB*") and

            constr_pin_dir == "fall" and

            fnmatch.fnmatch(rel_pin, "CP") and

            rel_pin_dir == "rise" and

            len(probe_list) == 1):

 

        template_name = "hold/template__common__rise__DB__fall__1.thanos.sp"

        return template_name

 

    # AOI22 (DA1....)

    if( arc_type == "hold" and

            fnmatch.fnmatch(cell_name, "MB2SRLSDFAO22*") and

            fnmatch.fnmatch(constr_pin, "DA1") and

            constr_pin_dir == "rise" and

            fnmatch.fnmatch(rel_pin, "CP") and

            rel_pin_dir == "rise" and

            len(probe_list) == 1):

 

        template_name = "hold/template__AO22__rise__DA1__rise__1.thanos.sp"

        return template_name

       

    if( arc_type == "hold" and

            fnmatch.fnmatch(cell_name, "MB2SRLSDFAO22*") and

            fnmatch.fnmatch(constr_pin, "DA2") and

            constr_pin_dir == "rise" and

            fnmatch.fnmatch(rel_pin, "CP") and

            rel_pin_dir == "rise" and

            len(probe_list) == 1):

 

        template_name = "hold/template__AO22__rise__DA2__rise__1.thanos.sp"

        return template_name

 

    if( arc_type == "hold" and

            fnmatch.fnmatch(cell_name, "MB2SRLSDFAO22*") and

            fnmatch.fnmatch(constr_pin, "DB1") and

            constr_pin_dir == "rise" and

            fnmatch.fnmatch(rel_pin, "CP") and

            rel_pin_dir == "rise" and

            len(probe_list) == 1):

 

        template_name = "hold/template__AO22__rise__DB1__rise__1.thanos.sp"

        return template_name

       

    if( arc_type == "hold" and

            fnmatch.fnmatch(cell_name, "MB2SRLSDFAO22*") and

            fnmatch.fnmatch(constr_pin, "DB2") and

            constr_pin_dir == "rise" and

            fnmatch.fnmatch(rel_pin, "CP") and

            rel_pin_dir == "rise" and

            len(probe_list) == 1):

 

        template_name = "hold/template__AO22__rise__DB2__rise__1.thanos.sp"

        return template_name

 

    if( arc_type == "hold" and

            fnmatch.fnmatch(cell_name, "MB2SRLSDFAO22*") and

            fnmatch.fnmatch(constr_pin, "DC1") and

            constr_pin_dir == "rise" and

            fnmatch.fnmatch(rel_pin, "CP") and

            rel_pin_dir == "rise" and

            len(probe_list) == 1):

 

        template_name = "hold/template__AO22__rise__DC1__rise__1.thanos.sp"

        return template_name

       

    if( arc_type == "hold" and

            fnmatch.fnmatch(cell_name, "MB2SRLSDFAO22*") and

            fnmatch.fnmatch(constr_pin, "DC2") and

            constr_pin_dir == "rise" and

            fnmatch.fnmatch(rel_pin, "CP") and

            rel_pin_dir == "rise" and

            len(probe_list) == 1):

 

        template_name = "hold/template__AO22__rise__DC2__rise__1.thanos.sp"

        return template_name

 

    if( arc_type == "hold" and

            fnmatch.fnmatch(cell_name, "MB2SRLSDFAO22*") and

            fnmatch.fnmatch(constr_pin, "DD1") and

            constr_pin_dir == "rise" and

            fnmatch.fnmatch(rel_pin, "CP") and

            rel_pin_dir == "rise" and

            len(probe_list) == 1):

 

        template_name = "hold/template__AO22__rise__DD1__rise__1.thanos.sp"

        return template_name

       

    if( arc_type == "hold" and

            fnmatch.fnmatch(cell_name, "MB2SRLSDFAO22*") and

            fnmatch.fnmatch(constr_pin, "DD2") and

            constr_pin_dir == "rise" and

            fnmatch.fnmatch(rel_pin, "CP") and

            rel_pin_dir == "rise" and

            len(probe_list) == 1):

 

        template_name = "hold/template__AO22__rise__DD2__rise__1.thanos.sp"

        return template_name

 

    if( arc_type == "hold" and

            fnmatch.fnmatch(cell_name, "MB2SRLSDFAO22*") and

            fnmatch.fnmatch(constr_pin, "DA1") and

            constr_pin_dir == "fall" and

            fnmatch.fnmatch(rel_pin, "CP") and

            rel_pin_dir == "rise" and

            len(probe_list) == 1):

 

        template_name = "hold/template__AO22__rise__DA1__fall__1.thanos.sp"

        return template_name

       

    if( arc_type == "hold" and

            fnmatch.fnmatch(cell_name, "MB2SRLSDFAO22*") and

            fnmatch.fnmatch(constr_pin, "DA2") and

            constr_pin_dir == "fall" and

            fnmatch.fnmatch(rel_pin, "CP") and

            rel_pin_dir == "rise" and

            len(probe_list) == 1):

 

        template_name = "hold/template__AO22__rise__DA2__fall__1.thanos.sp"

        return template_name

 

    if( arc_type == "hold" and

            fnmatch.fnmatch(cell_name, "MB2SRLSDFAO22*") and

            fnmatch.fnmatch(constr_pin, "DB1") and

            constr_pin_dir == "fall" and

            fnmatch.fnmatch(rel_pin, "CP") and

            rel_pin_dir == "rise" and

            len(probe_list) == 1):

 

        template_name = "hold/template__AO22__rise__DB1__fall__1.thanos.sp"

        return template_name

       

    if( arc_type == "hold" and

            fnmatch.fnmatch(cell_name, "MB2SRLSDFAO22*") and

            fnmatch.fnmatch(constr_pin, "DB2") and

            constr_pin_dir == "fall" and

            fnmatch.fnmatch(rel_pin, "CP") and

            rel_pin_dir == "rise" and

            len(probe_list) == 1):

 

        template_name = "hold/template__AO22__rise__DB2__fall__1.thanos.sp"

        return template_name

 

    if( arc_type == "hold" and

            fnmatch.fnmatch(cell_name, "MB2SRLSDFAO22*") and

            fnmatch.fnmatch(constr_pin, "DC1") and

            constr_pin_dir == "fall" and

            fnmatch.fnmatch(rel_pin, "CP") and

            rel_pin_dir == "rise" and

            len(probe_list) == 1):

 

        template_name = "hold/template__AO22__rise__DC1__fall__1.thanos.sp"

        return template_name

       

    if( arc_type == "hold" and

            fnmatch.fnmatch(cell_name, "MB2SRLSDFAO22*") and

            fnmatch.fnmatch(constr_pin, "DC2") and

            constr_pin_dir == "fall" and

            fnmatch.fnmatch(rel_pin, "CP") and

            rel_pin_dir == "rise" and

            len(probe_list) == 1):

 

        template_name = "hold/template__AO22__rise__DC2__fall__1.thanos.sp"

        return template_name

 

    if( arc_type == "hold" and

            fnmatch.fnmatch(cell_name, "MB2SRLSDFAO22*") and

            fnmatch.fnmatch(constr_pin, "DD1") and

            constr_pin_dir == "fall" and

            fnmatch.fnmatch(rel_pin, "CP") and

            rel_pin_dir == "rise" and

            len(probe_list) == 1):

 

        template_name = "hold/template__AO22__rise__DD1__fall__1.thanos.sp"

        return template_name

       

    if( arc_type == "hold" and

            fnmatch.fnmatch(cell_name, "MB2SRLSDFAO22*") and

            fnmatch.fnmatch(constr_pin, "DD2") and

            constr_pin_dir == "fall" and

            fnmatch.fnmatch(rel_pin, "CP") and

            rel_pin_dir == "rise" and

            len(probe_list) == 1):

 

        template_name = "hold/template__AO22__rise__DD2__fall__1.thanos.sp"

        return template_name

 

    # OA22 (DA1....)

    if( arc_type == "hold" and

            fnmatch.fnmatch(cell_name, "MB2SRLSDFOA22*") and

            fnmatch.fnmatch(constr_pin, "DA1") and

            constr_pin_dir == "rise" and

            fnmatch.fnmatch(rel_pin, "CP") and

            rel_pin_dir == "rise" and

            len(probe_list) == 1):

 

        template_name = "hold/template__OA22__rise__DA1__rise__1.thanos.sp"

        return template_name

       

    if( arc_type == "hold" and

            fnmatch.fnmatch(cell_name, "MB2SRLSDFOA22*") and

            fnmatch.fnmatch(constr_pin, "DA2") and

            constr_pin_dir == "rise" and

            fnmatch.fnmatch(rel_pin, "CP") and

            rel_pin_dir == "rise" and

            len(probe_list) == 1):

 

        template_name = "hold/template__OA22__rise__DA2__rise__1.thanos.sp"

        return template_name

 

    if( arc_type == "hold" and

            fnmatch.fnmatch(cell_name, "MB2SRLSDFOA22*") and

            fnmatch.fnmatch(constr_pin, "DB1") and

            constr_pin_dir == "rise" and

            fnmatch.fnmatch(rel_pin, "CP") and

            rel_pin_dir == "rise" and

            len(probe_list) == 1):

 

        template_name = "hold/template__OA22__rise__DB1__rise__1.thanos.sp"

        return template_name

       

    if( arc_type == "hold" and

            fnmatch.fnmatch(cell_name, "MB2SRLSDFOA22*") and

            fnmatch.fnmatch(constr_pin, "DB2") and

            constr_pin_dir == "rise" and

            fnmatch.fnmatch(rel_pin, "CP") and

            rel_pin_dir == "rise" and

            len(probe_list) == 1):

 

        template_name = "hold/template__OA22__rise__DB2__rise__1.thanos.sp"

        return template_name

 

    if( arc_type == "hold" and

            fnmatch.fnmatch(cell_name, "MB2SRLSDFOA22*") and

            fnmatch.fnmatch(constr_pin, "DC1") and

            constr_pin_dir == "rise" and

            fnmatch.fnmatch(rel_pin, "CP") and

            rel_pin_dir == "rise" and

            len(probe_list) == 1):

 

        template_name = "hold/template__OA22__rise__DC1__rise__1.thanos.sp"

        return template_name

       

    if( arc_type == "hold" and

            fnmatch.fnmatch(cell_name, "MB2SRLSDFOA22*") and

            fnmatch.fnmatch(constr_pin, "DC2") and

            constr_pin_dir == "rise" and

            fnmatch.fnmatch(rel_pin, "CP") and

            rel_pin_dir == "rise" and

            len(probe_list) == 1):

 

        template_name = "hold/template__OA22__rise__DC2__rise__1.thanos.sp"

        return template_name

 

    if( arc_type == "hold" and

            fnmatch.fnmatch(cell_name, "MB2SRLSDFOA22*") and

            fnmatch.fnmatch(constr_pin, "DD1") and

            constr_pin_dir == "rise" and

            fnmatch.fnmatch(rel_pin, "CP") and

            rel_pin_dir == "rise" and

            len(probe_list) == 1):

 

        template_name = "hold/template__OA22__rise__DD1__rise__1.thanos.sp"

        return template_name

       

    if( arc_type == "hold" and

            fnmatch.fnmatch(cell_name, "MB2SRLSDFOA22*") and

            fnmatch.fnmatch(constr_pin, "DD2") and

            constr_pin_dir == "rise" and

            fnmatch.fnmatch(rel_pin, "CP") and

            rel_pin_dir == "rise" and

            len(probe_list) == 1):

 

        template_name = "hold/template__OA22__rise__DD2__rise__1.thanos.sp"

        return template_name

 

    if( arc_type == "hold" and

            fnmatch.fnmatch(cell_name, "MB2SRLSDFOA22*") and

            fnmatch.fnmatch(constr_pin, "DA1") and

            constr_pin_dir == "fall" and

            fnmatch.fnmatch(rel_pin, "CP") and

            rel_pin_dir == "rise" and

            len(probe_list) == 1):

 

        template_name = "hold/template__OA22__rise__DA1__fall__1.thanos.sp"

        return template_name

       

    if( arc_type == "hold" and

            fnmatch.fnmatch(cell_name, "MB2SRLSDFOA22*") and

            fnmatch.fnmatch(constr_pin, "DA2") and

            constr_pin_dir == "fall" and

            fnmatch.fnmatch(rel_pin, "CP") and

            rel_pin_dir == "rise" and

            len(probe_list) == 1):

 

        template_name = "hold/template__OA22__rise__DA2__fall__1.thanos.sp"

        return template_name

 

    if( arc_type == "hold" and

            fnmatch.fnmatch(cell_name, "MB2SRLSDFOA22*") and

            fnmatch.fnmatch(constr_pin, "DB1") and

            constr_pin_dir == "fall" and

            fnmatch.fnmatch(rel_pin, "CP") and

            rel_pin_dir == "rise" and

            len(probe_list) == 1):

 

        template_name = "hold/template__OA22__rise__DB1__fall__1.thanos.sp"

        return template_name

       

    if( arc_type == "hold" and

            fnmatch.fnmatch(cell_name, "MB2SRLSDFOA22*") and

            fnmatch.fnmatch(constr_pin, "DB2") and

            constr_pin_dir == "fall" and

            fnmatch.fnmatch(rel_pin, "CP") and

            rel_pin_dir == "rise" and

            len(probe_list) == 1):

 

        template_name = "hold/template__OA22__rise__DB2__fall__1.thanos.sp"

        return template_name

 

    if( arc_type == "hold" and

            fnmatch.fnmatch(cell_name, "MB2SRLSDFOA22*") and

            fnmatch.fnmatch(constr_pin, "DC1") and

            constr_pin_dir == "fall" and

            fnmatch.fnmatch(rel_pin, "CP") and

            rel_pin_dir == "rise" and

            len(probe_list) == 1):

 

        template_name = "hold/template__OA22__rise__DC1__fall__1.thanos.sp"

        return template_name

       

    if( arc_type == "hold" and

            fnmatch.fnmatch(cell_name, "MB2SRLSDFOA22*") and

            fnmatch.fnmatch(constr_pin, "DC2") and

            constr_pin_dir == "fall" and

            fnmatch.fnmatch(rel_pin, "CP") and

            rel_pin_dir == "rise" and

            len(probe_list) == 1):

 

        template_name = "hold/template__OA22__rise__DC2__fall__1.thanos.sp"

        return template_name

 

    if( arc_type == "hold" and

            fnmatch.fnmatch(cell_name, "MB2SRLSDFOA22*") and

            fnmatch.fnmatch(constr_pin, "DD1") and

            constr_pin_dir == "fall" and

            fnmatch.fnmatch(rel_pin, "CP") and

            rel_pin_dir == "rise" and

            len(probe_list) == 1):

 

        template_name = "hold/template__OA22__rise__DD1__fall__1.thanos.sp"

        return template_name

       

    if( arc_type == "hold" and

            fnmatch.fnmatch(cell_name, "MB2SRLSDFOA22*") and

            fnmatch.fnmatch(constr_pin, "DD2") and

            constr_pin_dir == "fall" and

            fnmatch.fnmatch(rel_pin, "CP") and

            rel_pin_dir == "rise" and

            len(probe_list) == 1):

 

        template_name = "hold/template__OA22__rise__DD2__fall__1.thanos.sp"

        return template_name

 

    # Common (CP pins) template

    if( arc_type == "hold" and

                fnmatch.fnmatch(constr_pin, "D*") and

                constr_pin_dir == "rise" and

                fnmatch.fnmatch(rel_pin, "CP") and

                rel_pin_dir == "rise" and

                len(probe_list) == 1):

 

        template_name = "hold/template__common__rise__rise__1.thanos.sp"

        return template_name

 

 

    if( arc_type == "hold" and

                fnmatch.fnmatch(constr_pin, "D*") and

                constr_pin_dir == "rise" and

                fnmatch.fnmatch(rel_pin, "CP") and

                rel_pin_dir == "rise" and

                len(probe_list) == 2):

 

        template_name = "hold/template__common__rise__rise__2.thanos.sp"

        return template_name

 

 

    if( arc_type == "hold" and

                fnmatch.fnmatch(constr_pin, "D*") and

                constr_pin_dir == "fall" and

                fnmatch.fnmatch(rel_pin, "CP") and

                rel_pin_dir == "rise" and

                len(probe_list) == 1):

 

        template_name = "hold/template__common__rise__fall__1.thanos.sp"

        return \

            template_name

 

    if( arc_type == "hold" and

                fnmatch.fnmatch(constr_pin, "D*") and

                constr_pin_dir == "fall" and

                fnmatch.fnmatch(rel_pin, "CP") and

                rel_pin_dir == "rise" and

                len(probe_list) == 2):

 

        template_name = "hold/template__common__rise__fall__2.thanos.sp"

        return template_name

 

    # CP -> C/SN

    if( arc_type == "hold" and

                fnmatch.fnmatch(constr_pin, "C") and

                constr_pin_dir == "rise" and

                fnmatch.fnmatch(rel_pin, "CP") and

                rel_pin_dir == "rise" and

                len(probe_list) == 1):

 

        template_name = "hold/template__common__rise__rise__1.thanos.sp"

        return template_name

 

 

    if( arc_type == "hold" and

                fnmatch.fnmatch(constr_pin, "C") and

                constr_pin_dir == "rise" and

                fnmatch.fnmatch(rel_pin, "CP") and

                rel_pin_dir == "rise" and

                len(probe_list) == 2):

 

        template_name = "hold/template__common__rise__rise__2.thanos.sp"

        return template_name

 

 

    if( arc_type == "hold" and

                fnmatch.fnmatch(constr_pin, "C") and

                constr_pin_dir == "fall" and

                fnmatch.fnmatch(rel_pin, "CP") and

                rel_pin_dir == "rise" and

                len(probe_list) == 1):

 

        template_name = "hold/template__common__rise__fall__1.thanos.sp"

        return \

            template_name

 

    if( arc_type == "hold" and

                fnmatch.fnmatch(constr_pin, "C") and

                constr_pin_dir == "fall" and

                fnmatch.fnmatch(rel_pin, "CP") and

                rel_pin_dir == "rise" and

                len(probe_list) == 2):

 

        template_name = "hold/template__common__rise__fall__2.thanos.sp"

        return template_name

 

    if( arc_type == "hold" and

                fnmatch.fnmatch(constr_pin, "SN") and

                constr_pin_dir == "rise" and

                fnmatch.fnmatch(rel_pin, "CP") and

                rel_pin_dir == "rise" and

                len(probe_list) == 1):

 

        template_name = "hold/template__common__rise__rise__1.thanos.sp"

        return template_name

 

 

    if( arc_type == "hold" and

                fnmatch.fnmatch(constr_pin, "SN") and

                constr_pin_dir == "rise" and

                fnmatch.fnmatch(rel_pin, "CP") and

                rel_pin_dir == "rise" and

                len(probe_list) == 2):

 

        template_name = "hold/template__common__rise__rise__2.thanos.sp"

        return template_name

 

 

    if( arc_type == "hold" and

                fnmatch.fnmatch(constr_pin, "SN") and

                constr_pin_dir == "fall" and

                fnmatch.fnmatch(rel_pin, "CP") and

                rel_pin_dir == "rise" and

                len(probe_list) == 1):

 

        template_name = "hold/template__common__rise__fall__1.thanos.sp"

        return \

            template_name

 

    if( arc_type == "hold" and

                fnmatch.fnmatch(constr_pin, "SN") and

                constr_pin_dir == "fall" and

                fnmatch.fnmatch(rel_pin, "CP") and

                rel_pin_dir == "rise" and

                len(probe_list) == 2):

 

        template_name = "hold/template__common__rise__fall__2.thanos.sp"

        return template_name

 

    # Common (CPN pins) template

    if( arc_type == "hold" and

                fnmatch.fnmatch(constr_pin, "D*") and

                constr_pin_dir == "rise" and

                fnmatch.fnmatch(rel_pin, "CPN") and

                rel_pin_dir == "fall" ):

 

        template_name = "hold/template__common__fall__rise__1.thanos.sp"

        return template_name

 

 

    if( arc_type == "hold" and

            fnmatch.fnmatch(constr_pin, "D*") and

                constr_pin_dir == "fall" and

                fnmatch.fnmatch(rel_pin, "CPN") and

                rel_pin_dir == "fall" ):

 

        template_name = "hold/template__common__fall__fall__1.thanos.sp"

        return template_name

 

    # WWL -> D

    if( arc_type == "hold" and

                fnmatch.fnmatch(cell_name, "*QN*") and

                fnmatch.fnmatch(constr_pin, "D*") and

                constr_pin_dir == "rise" and

                (fnmatch.fnmatch(rel_pin, "WWL") or fnmatch.fnmatch(rel_pin, "WWL0") or fnmatch.fnmatch(rel_pin, "WWL1")) and

                rel_pin_dir == "fall"):

 

        template_name = "hold/template__basemeg__fall__rise__WWL__glitch__minq__1.thanos.sp"

        return template_name

 

 

    if( arc_type == "hold" and

                fnmatch.fnmatch(cell_name, "*QN*") and

                fnmatch.fnmatch(constr_pin, "D*") and

                constr_pin_dir == "fall" and

                (fnmatch.fnmatch(rel_pin, "WWL") or fnmatch.fnmatch(rel_pin, "WWL0") or fnmatch.fnmatch(rel_pin, "WWL1")) and

                rel_pin_dir == "fall"):

 

        template_name = "hold/template__basemeg__fall__rise__WWL__glitch__maxq__1.thanos.sp"

        return template_name

 

    if( arc_type == "hold" and

                fnmatch.fnmatch(constr_pin, "D*") and

                constr_pin_dir == "rise" and

                (fnmatch.fnmatch(rel_pin, "WWL") or fnmatch.fnmatch(rel_pin, "WWL0")) and

                rel_pin_dir == "fall" ):

 

        template_name = "hold/template__basemeg__fall__rise__WWL__glitch__maxq__1.thanos.sp"

        return template_name

 

 

    if( arc_type == "hold" and

                fnmatch.fnmatch(constr_pin, "D*") and

                constr_pin_dir == "fall" and

                (fnmatch.fnmatch(rel_pin, "WWL") or fnmatch.fnmatch(rel_pin, "WWL0")) and

                rel_pin_dir == "fall" ):

 

        template_name = "hold/template__basemeg__fall__rise__WWL__glitch__minq__1.thanos.sp"

        return template_name

 

    if( arc_type == "hold" and

                fnmatch.fnmatch(constr_pin, "D*") and

                constr_pin_dir == "rise" and

                (fnmatch.fnmatch(rel_pin, "WWL*_N")) and

                rel_pin_dir == "rise" ):

 

        template_name = "hold/template__basemeg__fall__rise__WWL__glitch__maxq__1.sp"

        return template_name

 

    if( arc_type == "hold" and

                fnmatch.fnmatch(constr_pin, "D*") and

                constr_pin_dir == "fall" and

                (fnmatch.fnmatch(rel_pin, "WWL*_N")) and

                rel_pin_dir == "rise" ):

 

        template_name = "hold/template__basemeg__fall__rise__WWL__glitch__minq__1.sp"

        return template_name

 

    # LH latches

    if( arc_type == "hold" and

                fnmatch.fnmatch(constr_pin, "D*") and

                constr_pin_dir == "rise" and

                rel_pin == "E" and

                rel_pin_dir == "fall" ):

 

        template_name = "hold/template__latch__fall__rise__glitch__maxq__1.thanos.sp"

        return template_name

 

 

    if( arc_type == "hold" and

                fnmatch.fnmatch(constr_pin, "D*") and

                constr_pin_dir == "fall" and

                rel_pin == "E" and

                rel_pin_dir == "fall" ):

 

        template_name = "hold/template__latch__fall__fall__glitch__minq__1.thanos.sp"

        return template_name

 

 

    # LN latches

    if( arc_type == "hold" and

                fnmatch.fnmatch(constr_pin, "D*") and

                constr_pin_dir == "rise" and

                (fnmatch.fnmatch(rel_pin, "EN") or fnmatch.fnmatch(rel_pin, "ISO")) and

                rel_pin_dir == "rise" ):

 

        template_name = "hold/template__latch__rise__rise__glitch__maxq__1.thanos.sp"

        return template_name

 

 

    if( arc_type == "hold" and

                fnmatch.fnmatch(constr_pin, "D*") and

                constr_pin_dir == "fall" and

                (fnmatch.fnmatch(rel_pin, "EN") or fnmatch.fnmatch(rel_pin, "ISO")) and

                rel_pin_dir == "rise" ):

 

        template_name = "hold/template__latch__rise__fall__glitch__minq__1.thanos.sp"

        return template_name

 

 

    # CKLHQ

    if( arc_type == "hold" and

                constr_pin == "E" and

                constr_pin_dir == "rise" and

                rel_pin == "CPN" and

                rel_pin_dir == "fall" ):

 

        template_name = "hold/template__latch__fall__rise__glitch__minq__1.thanos.sp"

        return template_name

 

 

    if( arc_type == "hold" and

                constr_pin == "E" and

                constr_pin_dir == "fall" and

                rel_pin == "CPN" and

                rel_pin_dir == "fall" ):

 

        template_name = "hold/template__latch__fall__fall__pushout__1.thanos.sp"

        return template_name

 

 

    # CKLNQ

    if( arc_type == "hold" and

                constr_pin == "E" and

                constr_pin_dir == "rise" and

                rel_pin == "CP" and

                rel_pin_dir == "rise" and

                "Q" in probe_list):

 

        template_name = "hold/template__latch__rise__rise__glitch__maxq__1.thanos.sp"

        return template_name

 

 

    if( arc_type == "hold" and

                constr_pin == "E" and

                constr_pin_dir == "fall" and

                rel_pin == "CP" and

                rel_pin_dir == "rise" and

                "Q" in probe_list):

 

        template_name = "hold/template__latch__rise__fall__pushout__1.thanos.sp"

        return template_name

 

 

    # CKLNQN

    if( arc_type == "hold" and

                constr_pin == "E" and

                constr_pin_dir == "rise" and

                rel_pin == "CP" and

                rel_pin_dir == "rise" and

                "QN" in probe_list):

 

        template_name = "hold/template__latch__rise__rise__glitch__minq__1.thanos.sp"

        return template_name

 

 

    if( arc_type == "hold" and

                constr_pin == "E" and

                constr_pin_dir == "fall" and

                rel_pin == "CP" and

                rel_pin_dir == "rise" and

                "QN" in probe_list):

 

        template_name = "hold/template__latch__rise__fall__pushout__1.thanos.sp"

        return template_name

 

 

    # CKLNENQ

    if( arc_type == "hold" and

                constr_pin == "EN" and

                constr_pin_dir == "rise" and

                rel_pin == "CP" and

                rel_pin_dir == "rise" ):

 

        template_name = "hold/template__latch__rise__rise__pushout__1.thanos.sp"

        return template_name

 

 

    if( arc_type == "hold" and

                constr_pin == "EN" and

                constr_pin_dir == "fall" and

                rel_pin == "CP" and

                rel_pin_dir == "rise" ):

 

        template_name = "hold/template__latch__rise__fall__glitch__maxq__1.thanos.sp"

        return template_name

 

    # non_seq_hold (Latch)

    if( arc_type == "non_seq_hold" and

                fnmatch.fnmatch(cell_name, "L*") and

                constr_pin == "SDN" and

                constr_pin_dir == "rise" and

                rel_pin == "CDN" and

                rel_pin_dir == "rise"):

 

        template_name = "non_seq_hold/template__latch__rise__rise__glitch__minq__1.thanos.sp"

        return template_name

 

    if( arc_type == "non_seq_hold" and

                fnmatch.fnmatch(cell_name, "L*") and

                constr_pin == "CDN" and

                constr_pin_dir == "rise" and

                rel_pin == "SDN" and

                rel_pin_dir == "rise"):

 

        template_name = "non_seq_hold/template__latch__rise__rise__pushout__1.thanos.sp"

        return template_name

 

    # non_seq_hold (Flop for N22ULL/N12/N40) ---- 2019/12/20 hack from hspice's flop by YK

    if( arc_type == "non_seq_hold" and

                fnmatch.fnmatch(cell_name, "*CSN*") and

                constr_pin == "CDN" and

                constr_pin_dir == "rise" and

                rel_pin == "SDN" and

                rel_pin_dir == "rise"):

 

        template_name = "non_seq_hold/template__latch__rise__rise__glitch__maxq__1.thanos.sp"

        return template_name

 

    if( arc_type == "non_seq_hold" and

                fnmatch.fnmatch(cell_name, "*CSN*") and

                constr_pin == "SDN" and

                constr_pin_dir == "rise" and

                rel_pin == "CDN" and

                rel_pin_dir == "rise"):

 

        template_name = "non_seq_hold/template__flop__rise__rise__pushout__1.thanos.sp"

        return template_name

 

    # non_seq_hold (Flop) 2019/09/26

    if( arc_type == "non_seq_hold" and

                constr_pin == "SDN" and

                constr_pin_dir == "rise" and

                rel_pin == "CDN" and

                rel_pin_dir == "rise"):

 

        template_name = "non_seq_hold/template__latch__rise__rise__pushout__1.thanos.sp"

        return template_name

 

    if( arc_type == "non_seq_hold" and

                constr_pin == "CDN" and

                constr_pin_dir == "rise" and

                rel_pin == "SDN" and

                rel_pin_dir == "rise"):

 

        template_name = "non_seq_hold/template__latch__rise__rise__glitch__maxq__1.thanos.sp"

        return template_name

 

    # Double probe, non_seq_hold arcs for SDN->CD with "bl_bx" probe, which requires mixed

    if( arc_type == "non_seq_hold" and

                fnmatch.fnmatch(cell_name, "*SDRPQ*") and

                constr_pin == "SDN" and

                constr_pin_dir == "rise" and

                rel_pin == "CD" and

                rel_pin_dir == "fall" and

                "Q" in probe_list and

                "bl_bx" in probe_list and

                len(probe_list) == 2):

        template_name = "non_seq_hold/template__latch__fall__rise__glitch__minq_maxbl_bx__2.thanos.sp"

        return template_name

   

    if( arc_type == "non_seq_hold" and

                fnmatch.fnmatch(cell_name, "*SDRPQ*") and

                constr_pin == "SDN" and

                constr_pin_dir == "rise" and

                rel_pin == "CD" and

                rel_pin_dir == "fall" and

                "Q" in probe_list and

                "sl_ax" in probe_list and

                len(probe_list) == 2):

        template_name = "non_seq_hold/template__latch__fall__rise__glitch__minq_maxsl_ax__2.thanos.sp"

        return template_name

 

    if( arc_type == "non_seq_hold" and

                fnmatch.fnmatch(cell_name, "*SDRPQ*") and

                constr_pin == "CD" and

                constr_pin_dir == "fall" and

                rel_pin == "SDN" and

                rel_pin_dir == "rise" and

                "Q" in probe_list and

                len(probe_list) == 2):

        template_name = "non_seq_hold/template__latch__rise__fall__pushout__1.thanos.sp"

        return template_name

 

    if( arc_type == "non_seq_hold" and

                fnmatch.fnmatch(cell_name, "*SDRPQ*") and

                constr_pin == "SDN" and

                constr_pin_dir == "rise" and

                rel_pin == "CD" and

                rel_pin_dir == "fall" and

                "Q" in probe_list and

                len(probe_list) == 2):

        template_name = "non_seq_hold/template__latch__fall__rise__glitch__minq__2.thanos.sp"

        return template_name

 

    if( arc_type == "non_seq_hold" and

                constr_pin == "CD" and

                constr_pin_dir == "fall" and

                rel_pin == "SDN" and

                rel_pin_dir == "rise" and

                "Q" in probe_list and

                "bl_bx" in probe_list and

                len(probe_list) == 2):

        template_name = "non_seq_hold/template__latch__rise__fall__glitch__maxq_minbl_bx__2.thanos.sp"

        return template_name

 

    if( arc_type == "non_seq_hold" and

                constr_pin == "CD" and

                constr_pin_dir == "fall" and

                rel_pin == "SDN" and

                rel_pin_dir == "rise" and

                "Q" in probe_list and

                "sl_ax" in probe_list and

                len(probe_list) == 2):

        template_name = "non_seq_hold/template__latch__rise__fall__glitch__maxq_minsl_ax__2.thanos.sp"

        return template_name

 

    if( arc_type == "non_seq_hold" and

                constr_pin == "CD" and

                constr_pin_dir == "fall" and

                rel_pin == "SDN" and

                rel_pin_dir == "rise" and

                "Q" in probe_list and

                len(probe_list) == 2):

        template_name = "non_seq_hold/template__latch__rise__fall__glitch__maxq__2.thanos.sp"

        return template_name

 

    if( arc_type == "non_seq_hold" and

                constr_pin == "SDN" and

                constr_pin_dir == "rise" and

                rel_pin == "CD" and

                rel_pin_dir == "fall" and

                "Q" in probe_list and

                len(probe_list) == 2):

        template_name = "non_seq_hold/template__latch__fall__rise__pushout__1.thanos.sp"

        return template_name

 

 

    # non_seq_hold (SDRPQ)

    if( arc_type == "non_seq_hold" and

                fnmatch.fnmatch(cell_name, "*SDRPQ*") and

                constr_pin == "CD" and

                constr_pin_dir == "fall" and

                rel_pin == "SDN" and

                rel_pin_dir == "rise"):

 

        template_name = "non_seq_hold/template__latch__rise__fall__pushout__1.thanos.sp"

        return template_name

 

    if( arc_type == "non_seq_hold" and

                fnmatch.fnmatch(cell_name, "*SDRPQ*")and

                constr_pin == "SDN" and

                constr_pin_dir == "rise" and

                rel_pin == "CD" and

                rel_pin_dir == "fall"):

 

        template_name = "non_seq_hold/template__latch__fall__rise__glitch__minq__1.thanos.sp"

        return template_name

 

    # non_seq_hold (flop)

    if( arc_type == "non_seq_hold" and

                constr_pin == "CD" and

                constr_pin_dir == "fall" and

                rel_pin == "SDN" and

                rel_pin_dir == "rise"):

 

        template_name = "non_seq_hold/template__latch__rise__fall__glitch__maxq__1.thanos.sp"

        return template_name

 

    if( arc_type == "non_seq_hold" and

                constr_pin == "SDN" and

                constr_pin_dir == "rise" and

                rel_pin == "CD" and

                rel_pin_dir == "fall"):

 

        template_name = "non_seq_hold/template__latch__fall__rise__pushout__1.thanos.sp"

        return template_name

 

    #non_seq_hold (RETN default)

    if( arc_type == "non_seq_hold" and

                fnmatch.fnmatch(cell_name, "*RSSDF*")and

                constr_pin == "SDN" and

                constr_pin_dir == "fall" and

                rel_pin == "RETN" and

                rel_pin_dir == "fall" and

                "Q" in probe_list and

                "bl_b" in probe_list and

                len(probe_list) == 2):

        template_name = "non_seq_hold/template__retn__nonseqhold__RETN__fall__SDN__fall__glitch__maxq__maxbl_b__2.thanos.sp"

        return template_name

 

    if( arc_type == "non_seq_hold" and

                fnmatch.fnmatch(cell_name, "*RSSDF*")and

                constr_pin == "CD" and

                constr_pin_dir == "rise" and

                rel_pin == "RETN" and

                rel_pin_dir == "fall" and

                "Q" in probe_list and

                "bl_b" in probe_list and

                len(probe_list) == 2):

        template_name = "non_seq_hold/template__retn__nonseqhold__RETN__fall__CD__rise__glitch__minq__minbl_b__2.thanos.sp"

        return template_name

 

    if( arc_type == "non_seq_hold" and

                fnmatch.fnmatch(cell_name, "*RSSDFSYNC*")and

                constr_pin == "CD" and

                constr_pin_dir == "rise" and

                rel_pin == "RETN" and

                rel_pin_dir == "fall" and

                "Q" in probe_list and

                "bl_b" in probe_list and

                len(probe_list) == 4):

        template_name = "non_seq_hold/template__retn__nonseqhold__RETN__fall__CD__rise__glitch__minq__minbl_b__4.thanos.sp"

        return template_name

 

    if( arc_type == "non_seq_hold" and

                fnmatch.fnmatch(cell_name, "*RSVNB*")and

                constr_pin == "CD" and

                constr_pin_dir == "rise" and

                rel_pin == "RETN" and

                rel_pin_dir == "fall" and

                "Q" in probe_list and

                "sl_b" in probe_list and

                len(probe_list) == 2):

        template_name = "non_seq_hold/template__retn__nonseqhold__RETN__fall__CD__rise__glitch__minq__minsl_b__2.thanos.sp"

        return template_name

 

    if( arc_type == "non_seq_hold" and

                fnmatch.fnmatch(cell_name, "*RSVNB*")and

                constr_pin == "CD" and

                constr_pin_dir == "fall" and

                rel_pin == "RETN" and

                rel_pin_dir == "rise" and

                "Q" in probe_list and

                "sl_b" in probe_list and

                len(probe_list) == 2):

        template_name = "non_seq_hold/template__retn__nonseqhold__RETN__rise__CD__fall__glitch__minq__minsl_b__2.thanos.sp"

        return template_name

 

    #non_seq_hold (RETN nochange mapping)

    if( arc_type == "nochange_low_low" and

                constr_pin == "CD" and

                constr_pin_dir == "rise" and

                rel_pin == "RETN" and

                rel_pin_dir == "rise" and

                "Q" in probe_list and

                "bl_b" in probe_list and

                len(probe_list) == 2):

        template_name = "nochange_low_low/template__retn__nonseqhold__RETN__rise__CD__rise__pushout__2.thanos.sp"

        return template_name

 

    if( arc_type == "nochange_low_low" and

                fnmatch.fnmatch(cell_name, "*RSSDFSYNC*")and

                constr_pin == "CD" and

                constr_pin_dir == "rise" and

                rel_pin == "RETN" and

                rel_pin_dir == "rise" and

                "Q" in probe_list and

                "bl_b" in probe_list and

                len(probe_list) == 4):

        template_name = "nochange_low_low/template__retn__nonseqhold__RETN__rise__CD__rise__pushout__4.thanos.sp"

        return template_name

 

    if( arc_type == "nochange_low_high" and

                constr_pin == "SDN" and

                constr_pin_dir == "fall" and

                rel_pin == "RETN" and

                rel_pin_dir == "rise" and

                "Q" in probe_list and

                "bl_b" in probe_list and

                len(probe_list) == 2):

        template_name = "nochange_low_high/template__retn__nonseqsetup__RETN__rise__SDN__fall__pushout__2.thanos.sp"

        return template_name

 

    if( arc_type == "non_seq_setup" and

                constr_pin == "SDN" and

                constr_pin_dir == "fall" and

                rel_pin == "RETN" and

                rel_pin_dir == "fall" and

                "Q" in probe_list and

                "bl_b" in probe_list and

                len(probe_list) == 2):

        template_name = "non_seq_setup/template__retn__nonseqsetup__RETN__fall__SDN__fall__pushout__2.thanos.sp"

        return template_name

 

    if( arc_type == "non_seq_setup" and

                constr_pin == "SDN" and

                constr_pin_dir == "rise" and

                rel_pin == "RETN" and

                rel_pin_dir == "rise" and

                "Q" in probe_list and

                "bl_b" in probe_list and

                len(probe_list) == 2):

        template_name = "non_seq_setup/template__retn__nonseqsetup__RETN__rise__SDN__rise__glitch__maxq__maxbl_b__2.thanos.sp"

        return template_name

 

    if( arc_type == "non_seq_setup" and

                constr_pin == "CD" and

                constr_pin_dir == "rise" and

                rel_pin == "RETN" and

                rel_pin_dir == "fall" and

                "Q" in probe_list and

                "bl_b" in probe_list and

                len(probe_list) == 2):

        template_name = "non_seq_setup/template__retn__nonseqsetup__RETN__fall__CD__rise__pushout__2.thanos.sp"

        return template_name

 

    if( arc_type == "non_seq_setup" and

                constr_pin == "CD" and

                constr_pin_dir == "fall" and

                rel_pin == "RETN" and

                rel_pin_dir == "rise" and

                "Q" in probe_list and

                "bl_b" in probe_list and

                len(probe_list) == 2):

        template_name = "non_seq_setup/template__retn__nonseqsetup__RETN__rise__CD__fall__glitch__minq__minbl_b__2.thanos.sp"

        return template_name

 

 

    if( arc_type == "non_seq_setup" and

                constr_pin == "SDN" and

                constr_pin_dir == "rise" and

                rel_pin == "RETN" and

                rel_pin_dir == "rise" and

                "Q" in probe_list and

                "sl_b" in probe_list and

                len(probe_list) == 2):

        template_name = "non_seq_setup/template__retn__nonseqsetup__RETN__rise__SDN__rise__glitch__maxq__maxsl_b__2.thanos.sp"

        return template_name

 

    if( arc_type == "non_seq_setup" and

                constr_pin == "CD" and

                constr_pin_dir == "rise" and

                rel_pin == "RETN" and

                rel_pin_dir == "fall" and

                "Q" in probe_list and

                "sl_b" in probe_list and

                len(probe_list) == 2):

        template_name = "non_seq_setup/template__retn__nonseqsetup__RETN__fall__CD__rise__pushout__2.thanos.sp"

        return template_name

 

    if( arc_type == "non_seq_setup" and

                constr_pin == "CD" and

                constr_pin_dir == "fall" and

                rel_pin == "RETN" and

                rel_pin_dir == "rise" and

                "Q" in probe_list and

                "sl_b" in probe_list and

                len(probe_list) == 2):

        template_name = "non_seq_setup/template__retn__nonseqsetup__RETN__rise__CD__fall__glitch__minq__minsl_b__2.thanos.sp"

        return template_name

 

    if( arc_type == "non_seq_setup" and

                fnmatch.fnmatch(cell_name, "*RSNBSDF*")and

                constr_pin == "SDN" and

                constr_pin_dir == "rise" and

                rel_pin == "RETN" and

                rel_pin_dir == "rise" and

                "Q" in probe_list and

                "sl_ax" in probe_list and

                len(probe_list) == 2):

        template_name = "non_seq_setup/template__retn__nonseqsetup__RSNB__RETN__rise__SDN__rise__pushout__2.thanos.sp"

        return template_name

 

    if( arc_type == "non_seq_setup" and

                fnmatch.fnmatch(cell_name, "*RSNBSDF*")and

                constr_pin == "CD" and

                constr_pin_dir == "fall" and

                rel_pin == "RETN" and

                rel_pin_dir == "rise" and

                "Q" in probe_list and

                "sl_ax" in probe_list and

                len(probe_list) == 2):

        template_name = "non_seq_setup/template__retn__nonseqsetup__RSNB__RETN__rise__CD__fall__pushout__2.thanos.sp"

        return template_name

 

    # glitch criteria (bl_bx switches opposite way of Q)

    if( arc_type == "removal" and

                constr_pin == "RETN" and

                constr_pin_dir == "rise" and

                rel_pin == "CP" and

                rel_pin_dir == "fall" and

                "Q" in probe_list and

                "bl_bx" in probe_list and

                len(probe_list) == 2):

        template_name = "hold/template__retn__removal__fall__rise__glitch__minq__maxbl_bx__2.thanos.sp"

        return template_name

 

    #2018/2/23 new arc

    if( arc_type == "removal" and

                constr_pin == "RETN" and

                constr_pin_dir == "rise" and

                rel_pin == "CP" and

                rel_pin_dir == "fall" and

                "Q" in probe_list and

                "bl_b" in probe_list and

                len(probe_list) == 2):

        template_name = "hold/template__retn__removal__fall__rise__glitch__minq__2.thanos.sp"

        return template_name

 

    if( arc_type == "removal" and

                fnmatch.fnmatch(cell_name, "*MB*")and

                constr_pin == "RETN" and

                constr_pin_dir == "rise" and

                rel_pin == "CP" and

                rel_pin_dir == "fall" and

                "Q2" in probe_list and

                "bl2_b" in probe_list and

                len(probe_list) == 2):

        template_name = "hold/template__retn__removal__fall__rise__glitch__minq__2.thanos.sp"

        return template_name

 

    if( arc_type == "removal" and

                fnmatch.fnmatch(cell_name, "*MB*")and

                constr_pin == "RETN" and

                constr_pin_dir == "rise" and

                rel_pin == "CP" and

                rel_pin_dir == "fall" and

                "Q1" in probe_list and

                "bl1_b" in probe_list and

                len(probe_list) == 2):

        template_name = "hold/template__retn__removal__fall__rise__glitch__minq__2.thanos.sp"

        return template_name

 

    if( arc_type == "removal" and

                fnmatch.fnmatch(cell_name, "*MB*")and

                constr_pin == "RETN" and

                constr_pin_dir == "rise" and

                rel_pin == "CP" and

                rel_pin_dir == "fall" and

                "Q3" in probe_list and

                "bl3_b" in probe_list and

                len(probe_list) == 2):

        template_name = "hold/template__retn__removal__fall__rise__glitch__minq__2.thanos.sp"

        return template_name

    if( arc_type == "removal" and

                fnmatch.fnmatch(cell_name, "*MB*")and

                constr_pin == "RETN" and

                constr_pin_dir == "rise" and

                rel_pin == "CP" and

                rel_pin_dir == "fall" and

                "Q4" in probe_list and

                "bl4_b" in probe_list and

                len(probe_list) == 2):

        template_name = "hold/template__retn__removal__fall__rise__glitch__minq__2.thanos.sp"

        return template_name

 

 

    if( arc_type == "removal" and

                constr_pin == "RETN" and

                constr_pin_dir == "fall" and

                rel_pin == "CP" and

                rel_pin_dir == "rise" and

                "Q" in probe_list and

                len(probe_list) == 2):

        template_name = "hold/template__retn__removal__notD__rise__fall__pushout__2.thanos.sp"

        return template_name

   

    if( arc_type == "removal" and

                fnmatch.fnmatch(cell_name, "*MB*")and

                constr_pin == "RETN" and

                constr_pin_dir == "fall" and

                rel_pin == "CP" and

                rel_pin_dir == "rise" and

                len(probe_list) == 2):

        template_name = "hold/template__retn__removal__notD__rise__fall__pushout__2.thanos.sp"

        return template_name

 

    # Removal

    if( arc_type == "removal" and

                constr_pin == "CD" and

                constr_pin_dir == "fall" and

                rel_pin == "CPN" and

                rel_pin_dir == "fall" and

                "Q" in probe_list and

                len(probe_list) == 1):

 

        template_name = "hold/template__latch__fall__fall__glitch__maxq__1.thanos.sp"

        return template_name

 

 

    if( arc_type == "removal" and

                constr_pin == "CD" and

                constr_pin_dir == "fall" and

                rel_pin == "CPN" and

                rel_pin_dir == "fall" and

                "Q" in probe_list and

                len(probe_list) == 2):

 

        template_name = "hold/template__latch__fall__fall__glitch__maxq__2.thanos.sp"

        return template_name

 

 

    if( arc_type == "removal" and

                constr_pin == "CD" and

                constr_pin_dir == "fall" and

                rel_pin == "CPN" and

                rel_pin_dir == "fall" and

                "QN" in probe_list and

                len(probe_list) == 1):

 

        template_name = "hold/template__latch__fall__fall__glitch__minq__1.thanos.sp"

        return template_name

 

 

    if( arc_type == "removal" and

                constr_pin == "CD" and

                constr_pin_dir == "fall" and

                rel_pin == "CPN" and

                rel_pin_dir == "fall" and

                "QN" in probe_list and

                len(probe_list) == 2):

 

        template_name = "hold/template__latch__fall__fall__glitch__minq__2.thanos.sp"

        return template_name

 

    #Removal SDN->CPN

    if( arc_type == "removal" and

                constr_pin == "SDN" and

                constr_pin_dir == "rise" and

                rel_pin == "CPN" and

                rel_pin_dir == "fall" and

                "Q" in probe_list and

                len(probe_list) == 1):

 

        template_name = "hold/template__latch__fall__rise__glitch__minq__1.thanos.sp"

        return template_name

 

 

    if( arc_type == "removal" and

                constr_pin == "SDN" and

                constr_pin_dir == "rise" and

                rel_pin == "CPN" and

                rel_pin_dir == "fall" and

                "Q" in probe_list and

                len(probe_list) == 2):

 

        template_name = "hold/template__latch__fall__rise__glitch__minq__2.thanos.sp"

        return template_name

 

 

    if( arc_type == "removal" and

                constr_pin == "SDN" and

                constr_pin_dir == "rise" and

                rel_pin == "CPN" and

                rel_pin_dir == "fall" and

                "QN" in probe_list and

                len(probe_list) == 1):

 

        template_name = "hold/template__latch__fall__rise__glitch__maxq__1.thanos.sp"

        return template_name

 

 

    if( arc_type == "removal" and

                constr_pin == "SDN" and

                constr_pin_dir == "rise" and

                rel_pin == "CPN" and

                rel_pin_dir == "fall" and

                "QN" in probe_list and

                len(probe_list) == 2):

 

        template_name = "hold/template__latch__fall__rise__glitch__maxq__2.thanos.sp"

        return template_name

 

    # Double probe, removal arcs for CP->CD with "bl_bx" probe, which requires mixed

    # glitch criteria (bl_bx switches opposite way of Q)

    if( arc_type == "removal" and

                constr_pin == "CD" and

                constr_pin_dir == "fall" and

                rel_pin == "CP" and

                rel_pin_dir == "rise" and

                "Q" in probe_list and

                "bl_bx" in probe_list and

                len(probe_list) == 2):

        template_name = \

            "hold/template__latch__rise__fall__glitch__maxq__minbl_bx__2.thanos.sp"

        return template_name

 

    # Double probe, removal arcs for CP->SDN with "bl_bx" probe, which requires mixed

    # glitch criteria (bl_bx switches opposite way of Q)

    if( arc_type == "removal" and

                constr_pin == "SDN" and

                constr_pin_dir == "rise" and

                rel_pin == "CP" and

                rel_pin_dir == "rise" and

                "Q" in probe_list and

                "bl_bx" in probe_list and

                len(probe_list) == 2):

        template_name = "hold/template__latch__rise__rise__glitch__minq__maxbl_bx__2.thanos.sp"

        return template_name

 

    # Double probe, removal arcs for CP->CD with "sl_ax" probe, which requires mixed

    # glitch criteria (sl_ax switches opposite way of Q)

    if( arc_type == "removal" and

                constr_pin == "CD" and

                constr_pin_dir == "fall" and

                rel_pin == "CP" and

                rel_pin_dir == "rise" and

                "Q" in probe_list and

                "sl_ax" in probe_list and

                len(probe_list) == 2):

        template_name = \

            "hold/template__latch__rise__fall__glitch__maxq__minsl_ax__2.thanos.sp"

        return template_name

 

    if( arc_type == "removal" and

                constr_pin == "CD" and

                constr_pin_dir == "fall" and

                rel_pin == "CP" and

                rel_pin_dir == "rise" and

                "Q" in probe_list and

                "sl_bx" in probe_list and

                len(probe_list) == 2):

        template_name = \

            "hold/template__latch__rise__fall__glitch__maxq__minsl_bx__2.thanos.sp"

        return template_name

 

    if( arc_type == "removal" and

                constr_pin == "CD" and

                constr_pin_dir == "fall" and

                rel_pin == "CP" and

                rel_pin_dir == "rise" and

                "Q" in probe_list and

                "bl_b" in probe_list and

                len(probe_list) == 2):

        template_name = \

            "hold/template__latch__rise__fall__glitch__maxq__maxbl_b__2.thanos.sp"

        return template_name

 

    # Double probe, removal arcs for SDN->CD with "sl_ax" probe, which requires mixed

    # glitch criteria (sl_ax switches opposite way of Q)

    if( arc_type == "removal" and

                constr_pin == "SDN" and

                constr_pin_dir == "rise" and

                rel_pin == "CP" and

                rel_pin_dir == "rise" and

                "Q" in probe_list and

                "sl_ax" in probe_list and

                len(probe_list) == 2):

        template_name = "hold/template__latch__rise__rise__glitch__minq__maxsl_ax__2.thanos.sp"

        return template_name

 

    # Single probe, removal arcs for CP->CD

    if( arc_type == "removal" and

                constr_pin == "CD" and

                constr_pin_dir == "fall" and

                rel_pin == "CP" and

                rel_pin_dir == "rise" and

                "Q" in probe_list and

                len(probe_list) == 1):

 

        template_name = "hold/template__latch__rise__fall__glitch__maxq__1.thanos.sp"

        return template_name

 

    # Single probe, removal arcs for SDN->CD

    if( arc_type == "removal" and

                constr_pin == "SDN" and

                constr_pin_dir == "rise" and

                rel_pin == "CP" and

                rel_pin_dir == "rise" and

                "Q" in probe_list and

                len(probe_list) == 1):

 

        template_name = "hold/template__latch__rise__rise__glitch__minq__1.thanos.sp"

        return template_name

 

    # Single probe for MB, removal arcs for CP->CD

    if( arc_type == "removal" and

                fnmatch.fnmatch(cell_name, "*MB*") and

                constr_pin == "CD" and

                constr_pin_dir == "fall" and

                rel_pin == "CP" and

                rel_pin_dir == "rise" and

                any(item.startswith('QN') for item in probe_list)):

 

        template_name = "hold/template__MB__latch__rise__fall__glitch__minq__1.thanos.sp"

        return template_name

   

    # Single probe for MB, removal arcs for CP->CD

    if( arc_type == "removal" and

                fnmatch.fnmatch(cell_name, "*MB*") and

                constr_pin == "CD" and

                constr_pin_dir == "fall" and

                rel_pin == "CP" and

                rel_pin_dir == "rise" and

                any(item.startswith('Q') for item in probe_list)):

 

        template_name = "hold/template__MB__latch__rise__fall__glitch__maxq__1.thanos.sp"

        return template_name

 

    # Single probe, removal arcs for SDN->CD

    if( arc_type == "removal" and

                fnmatch.fnmatch(cell_name, "*MB*") and

                constr_pin == "SDN" and

                constr_pin_dir == "rise" and

                rel_pin == "CP" and

                rel_pin_dir == "rise"):

 

        template_name = "hold/template__MB__latch__rise__rise__glitch__minq__1.thanos.sp"

        return template_name

 

    # Double probe, removal arcs for CP-> CD

    if( arc_type == "removal" and

                constr_pin == "CD" and

                constr_pin_dir == "fall" and

                rel_pin == "CP" and

                rel_pin_dir == "rise" and

                "Q" in probe_list and

                len(probe_list) == 2):

 

        template_name = "hold/template__latch__rise__fall__glitch__maxq__2.thanos.sp"

        return template_name

 

 

    if( arc_type == "removal" and

                constr_pin == "CD" and

                constr_pin_dir == "fall" and

                rel_pin == "CP" and

                rel_pin_dir == "rise" and

                "QN" in probe_list and

                len(probe_list) == 1):

 

        template_name = "hold/template__latch__rise__fall__glitch__minq__1.thanos.sp"

        return template_name

 

 

    if( arc_type == "removal" and

                constr_pin == "CD" and

                constr_pin_dir == "fall" and

                rel_pin == "CP" and

                rel_pin_dir == "rise" and

                "QN" in probe_list and

                len(probe_list) == 2):

 

        template_name = "hold/template__latch__rise__fall__glitch__minq__2.thanos.sp"

        return template_name

 

    # Double probe, removal arcs for SDN->CP

    if( arc_type == "removal" and

                constr_pin == "SDN" and

                constr_pin_dir == "rise" and

                rel_pin == "CP" and

                rel_pin_dir == "rise" and

                "Q" in probe_list and

                len(probe_list) == 2):

 

        template_name = "hold/template__latch__rise__rise__glitch__minq__2.thanos.sp"

        return template_name

 

 

    if( arc_type == "removal" and

                constr_pin == "SDN" and

                constr_pin_dir == "rise" and

                rel_pin == "CP" and

                rel_pin_dir == "rise" and

                "QN" in probe_list and

                len(probe_list) == 1):

 

        template_name = "hold/template__latch__rise__rise__glitch__maxq__1.thanos.sp"

        return template_name

 

 

    if( arc_type == "removal" and

                constr_pin == "SDN" and

                constr_pin_dir == "rise" and

                rel_pin == "CP" and

                rel_pin_dir == "rise" and

                "QN" in probe_list and

                len(probe_list) == 2):

 

        template_name = "hold/template__latch__rise__rise__glitch__maxq__2.thanos.sp"

        return template_name

 

    #CD(N) -> E(N)

    if( arc_type == "removal" and

                constr_pin == "CDN" and

                constr_pin_dir == "rise" and

                rel_pin == "E" and

                rel_pin_dir == "fall" and

                len(probe_list) == 1):

 

        template_name = "hold/template__latch__fall__rise__glitch__maxq__1.thanos.sp"

        return template_name

 

 

    if( arc_type == "removal" and

                constr_pin == "CDN" and

                constr_pin_dir == "rise" and

                rel_pin == "E" and

                rel_pin_dir == "fall" and

                len(probe_list) == 2):

 

        template_name = "hold/template__latch__fall__rise__glitch__maxq__2.thanos.sp"

        return template_name

 

 

    if( arc_type == "removal" and

                constr_pin == "CDN" and

                constr_pin_dir == "rise" and

                rel_pin == "EN" and

                rel_pin_dir == "rise" and

                len(probe_list) == 1):

 

        template_name = "hold/template__latch__rise__rise__glitch__maxq__1.thanos.sp"

        return template_name

 

 

    if( arc_type == "removal" and

                constr_pin == "CDN" and

                constr_pin_dir == "rise" and

                rel_pin == "EN" and

                rel_pin_dir == "rise" and

                len(probe_list) == 2):

 

        template_name = "hold/template__latch__rise__rise__glitch__maxq__2.thanos.sp"

        return template_name

 

    #SDN->E(N)

    if( arc_type == "removal" and

                constr_pin == "SDN" and

                constr_pin_dir == "rise" and

                rel_pin == "E" and

                rel_pin_dir == "fall" and

                len(probe_list) == 1):

 

        template_name = "hold/template__latch__fall__rise__glitch__minq__1.thanos.sp"

        return template_name

 

 

    if( arc_type == "removal" and

                constr_pin == "SDN" and

                constr_pin_dir == "rise" and

                rel_pin == "E" and

                rel_pin_dir == "fall" and

                len(probe_list) == 2):

 

        template_name = "hold/template__latch__fall__rise__glitch__minq__2.thanos.sp"

        return template_name

 

 

    if( arc_type == "removal" and

                constr_pin == "SDN" and

                constr_pin_dir == "rise" and

                rel_pin == "EN" and

                rel_pin_dir == "rise" and

                len(probe_list) == 1):

 

        template_name = "hold/template__latch__rise__rise__glitch__minq__1.thanos.sp"

        return template_name

 

 

    if( arc_type == "removal" and

                constr_pin == "SDN" and

                constr_pin_dir == "rise" and

                rel_pin == "EN" and

                rel_pin_dir == "rise" and

                len(probe_list) == 2):

 

        template_name = "hold/template__latch__rise__rise__glitch__minq__2.thanos.sp"

        return template_name

 

    if( arc_type == "setup" and

                constr_pin == "D*" and

                constr_pin_dir == "rise" and

                rel_pin == "CP" and

                rel_pin_dir == "rise" and

                len(probe_list) == 1):

 

        template_name = "setup/template__common__rise__rise__1.thanos.sp"

        return template_name

 

 

    if( arc_type == "setup" and

                constr_pin == "D*" and

                constr_pin_dir == "rise" and

                rel_pin == "CP" and

                rel_pin_dir == "rise" and

                len(probe_list) == 2):

 

        template_name = "setup/template__common__rise__rise__2.thanos.sp"

        return template_name

 

 

    if( arc_type == "setup" and

                constr_pin == "D*" and

                constr_pin_dir == "fall" and

                rel_pin == "CP" and

                rel_pin_dir == "rise" and

                len(probe_list) == 1):

 

        template_name = "setup/template__common__rise__fall__1.thanos.sp"

        return template_name

 

 

    if( arc_type == "setup" and

                constr_pin == "D*" and

                constr_pin_dir == "fall" and

                rel_pin == "CP" and

                rel_pin_dir == "rise" and

                len(probe_list) == 2):

 

        template_name = "setup/template__common__rise__fall__2.thanos.sp"

        return template_name

 

 

    if( arc_type in delay_arc_types and

                fnmatch.fnmatch(cell_name, "INVD*") and

                constr_pin == "ZN" and

                rel_pin == "I" and

                rel_pin_dir == "rise"):

 

        template_name = "delay/template__invdX__fall.thanos.sp"

        return template_name

 

    if( arc_type in delay_arc_types and

                fnmatch.fnmatch(cell_name, "INVD*") and

                constr_pin == "ZN" and

                rel_pin == "I" and

                rel_pin_dir == "fall"):

 

        template_name = "delay/template__invdX__rise.thanos.sp"

        return template_name

 

    return None

