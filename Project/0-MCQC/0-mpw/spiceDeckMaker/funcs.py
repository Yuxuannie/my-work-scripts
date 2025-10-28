import sys
import re
import fix_cklnenq
from post_helper import post_icg_ov, post_lnd2sr, post_mb_an2, post_sdfmoq, post_final_state, remove_final_state
 
 
def getFileLines(input_file):
    with open(input_file, 'r') as f:
        file_lines = f.readlines()
    return file_lines
 
 
def writeFile(file_buffer, output_file):
    with open(output_file, 'w') as f:
        f.write(''.join(file_buffer))
 
 
def getDontTouchPins(template_deck):
    template_deck_lines = getFileLines(template_deck)
    dt_line_index = 1
    dt_line = template_deck_lines[dt_line_index]
 
    dt_pins_str = dt_line.strip().split('DONT_TOUCH_PINS')[1]
    dt_pins_list = [x.strip() for x in dt_pins_str.split(',')]
 
    return dt_pins_list
 
 
def which_internal_clk(netlist_path):
    with open(netlist_path, 'r') as f:
        netlist = f.read()
        if 'clkbb' in netlist:
            return 'clkbb'
        elif 'clkb' in netlist:
            return 'clkb'
    return None
 
 
def overwrite_SYNC1P5_CPN_fall_t0(arc_info, template_line):
    if 'SYNC1P5' in arc_info['CELL_NAME'] and (
        (arc_info['REL_PIN'] == 'CPN' and arc_info['REL_PIN_DIR'] == 'fall')
    ):
        # Remove postprocess constrainted time 16 21
        # By HS
        # 20250826 remove notSE when gating by HS
        if '.meas cp2q_del1' in template_line and arc_info['PROBE_PIN_1'] == 'Q':
            template_line = template_line.replace('cross=3', 'cross=4')
            template_line = template_line.replace('related_pin_t02', 'related_pin_t03')
    return template_line
 
 
def overwrite_SYNC1P5_CP_rise_t0(arc_info, template_line):
 
    if 'SYNC1P5' in arc_info['CELL_NAME'] and (
        (arc_info['REL_PIN'] == 'CP' and arc_info['REL_PIN_DIR'] == 'rise')
    ):
        # Remove postprocess constrainted time 16 21
        # By HS
        # 20250826 remove notSE when gating by HS
        if '.meas cp2q_del1' in template_line and arc_info['PROBE_PIN_1'] == 'Q':
            template_line = template_line.replace('cross=3', 'cross=4')
            template_line = template_line.replace('related_pin_t02', 'related_pin_t03')
    return template_line
 
 
def overwrite_SYNC234_CP_fall_t0(arc_info, template_line):
    if is_SYNC234(arc_info) and arc_info['REL_PIN'] == 'CP' and arc_info[
            'REL_PIN_DIR'] == 'fall':
        if ".param constrained_pin_t0" in template_line:
            if '!D' in arc_info['WHEN'] and arc_info['VECTOR'][-1] == '0':
                if 't01' in template_line:
                    template_line = ".param constrained_pin_t01 = '0 * max_slew'\n"
                elif 't02' in template_line:
                    template_line = ".param constrained_pin_t02 = '16 * max_slew'\n"
            elif ('&D' in arc_info['WHEN'] or 'D' == arc_info['WHEN'][0]) and arc_info['VECTOR'][-1] == '1':
                if 't01' in template_line:
                    template_line = ".param constrained_pin_t01 = '0 * max_slew'\n"
                elif 't02' in template_line:
                    template_line = ".param constrained_pin_t02 = '16 * max_slew'\n"
    return template_line
 
 
def getNominalSpiceDeckBuffer(template_deck, arc_info):
    """
    This function creates a SPICE deck buffer (list of strings that can be written to
    a file) for a uniquely defined table point
 
    Args:
        template_deck (str): The path to the template deck
        arc_info (dict): Dictionary of options for the SPICE deck
 
    arc_info required fields:
        HEADER_INFO (str):
            The string that is set as the header of the SPICE deck
        CELL_NAME (str):
            The name of the cell
        REL_PIN (str):
            The name of the related pin
        CONSTR_PIN (str):
            The name of the constrained pin
        OUTPUT_PINS (list):
            A list of the output pins of the cell
        PROBE_PIN_i (str):
            The name of probe pin i where i = 1, 2, ..., N
        WHEN (str):
            The when condition in logical format (e.g., !SE&SI)
        OUTPUT_LOAD (str):
            The output load containing units (e.g., 0.00117p)
        TEMPLATE_PINLIST (str):
            The list of pins from the define_cell block of the template.tcl file
        MAX_SLEW (str):
            The maximum slew of the corner containing units (e.g., 2.5478n)
        NETLIST_PINS (str):
            The list of pins from the LPE netlist of the current cell
        CONSTR_PIN_SLEW (str):
            The slew for the constrained pin containing units (e.g., 2.5478n)
        REL_PIN_SLEW (str):
            The slew for the related pin containing units (e.g., 1.2739n)
        VDD_VALUE (str):
            The VDD value for the current corner (e.g., 0.510)
        TEMPERATURE (str):
            The temperature for the current corner (e.g., -25)
        WAVEFORM_FILE (str):
            The path to the waveform file to use
        INCLUDE_FILE (str):
            The path to the model include file to use
        NETLIST_PATH (str):
            The path to the LPE netlist to use
        PUSHOUT_PER (str):
            The pushout percentage to use (e.g., 0.4)
        PUSHOUT_DIR (str):
            The pushout direction to use (e.g., POSITIVE)
        VECTOR (str):
            pinlist to condition(R00000000FFFFF)
        SIDE_PIN_STATES (list((str,str)))
            The side pins specified by the user in a specific state e.g. ('CP', 'high')
 
    Returns:
        write_list (list): The SPICE deck buffer that can be written
 
    """
    netlist_path = arc_info['NETLIST_PATH']
    internal_clks = search_templatetcl_for_internal_clk(arc_info)
    template_deck_lines = getFileLines(template_deck)
    output_load_header = '* Output Load'
    when_condition_header = '* Pin definitions'
    voltages_header = '* Voltage'
    write_list = list()
    is_fmc = False
    vector = [char for char in arc_info['VECTOR']]
    when = arc_info['WHEN'].split('&')
    dpins_settings = []
    probe_pin = arc_info['PROBE_PIN_1']
    rel_pin = arc_info['REL_PIN']
    rel_pin_dir = arc_info['REL_PIN_DIR']
    cell_name = arc_info['CELL_NAME']
    for template_line in template_deck_lines:
        if 'SYNC1P5' in arc_info['CELL_NAME'] and (
            (arc_info['REL_PIN'] == 'CP' and arc_info['REL_PIN_DIR'] == 'fall')
            or (
                arc_info['REL_PIN'] == 'CPN' and
                arc_info['REL_PIN_DIR'] == 'rise'
            )
        ):
            if ".param constrained_pin_t0" in template_line:
                if '!D' in arc_info['WHEN'] and arc_info['VECTOR'][-1] == '1':
                    if 't01' in template_line:
                        template_line = ".param constrained_pin_t01 = '16 * max_slew'\n"
                    elif 't02' in template_line:
                        template_line = ".param constrained_pin_t02 = '26 * max_slew'\n"
                elif 'D' in arc_info['WHEN'] and '!D' not in arc_info[
                        'WHEN'] and arc_info['VECTOR'][-1] == '0':
                    if 't01' in template_line:
                        template_line = ".param constrained_pin_t01 = '16 * max_slew'\n"
                    elif 't02' in template_line:
                        template_line = ".param constrained_pin_t02 = '26 * max_slew'\n"
        template_line = overwrite_SYNC1P5_CPN_fall_t0(arc_info, template_line)
        template_line = overwrite_SYNC1P5_CP_rise_t0(arc_info, template_line)
        if is_SYNC234(arc_info) and arc_info['REL_PIN'] == 'CP' and arc_info[
                'REL_PIN_DIR'] == 'rise':
            if ".param constrained_pin_t0" in template_line:
                if '!D' in arc_info['WHEN'] and arc_info['VECTOR'][-1] == '1':
                    if 't01' in template_line:
                        template_line = ".param constrained_pin_t01 = '16 * max_slew'\n"
                    elif 't02' in template_line:
                        template_line = ".param constrained_pin_t02 = '36 * max_slew'\n"
                elif 'D' in arc_info['WHEN'] and '!D' not in arc_info[
                        'WHEN'] and arc_info['VECTOR'][-1] == '0':
                    if 't01' in template_line:
                        template_line = ".param constrained_pin_t01 = '16 * max_slew'\n"
                    elif 't02' in template_line:
                        template_line = ".param constrained_pin_t02 = '36 * max_slew'\n"
        if 'THANOS Headers' in template_line:
            is_fmc = True
        if '$' in template_line:
            filled_line = fillTemplateLine(template_line, arc_info)
            if '.meas cp2q_del1 trig v' in filled_line:
                filled_line = get_cp2q_del1_cross(filled_line, arc_info)
            if '.meas cp2q_del1 trig v' in filled_line and (
                is_special_CKLN(cell_name, rel_pin, rel_pin_dir, vector)
            ):
                filled_line = get_special_CLK_cp2q_del1_cross(
                    filled_line, arc_info
                )
 
            elif '.meas cp2q_del1 trig v' in filled_line and (
                is_special_CKLH(arc_info)
            ):
                filled_line = get_special_CLK_cp2q_del1_cross(
                    filled_line, arc_info
                )
 
            write_list.append(filled_line)
 
            if 'XV$REL_PIN' in template_line:
 
                dpins_settings = get_dpins_settings(arc_info)
                if fix_cklnenq.is_cklnenq_TEN(cell_name, when):
                    setting = fix_cklnenq.get_cklnenq_EN_setting(when)
                    added = False
                    for ds in dpins_settings:
                        if setting.strip() == ds.strip():
                            added = True
 
                    if arc_info['VECTOR'][-1] != '0':
                        if not added:
                            dpins_settings.insert(0, setting)
                    else:
                        if added:
                            dpins_settings.remove(setting)
 
                write_list.extend(dpins_settings)
 
        elif output_load_header in template_line:
            write_list.append(template_line)
            output_load_line = getOutputLoadLines(arc_info)
            write_list.append(output_load_line)
 
        elif voltages_header in template_line:
            write_list.append(template_line)
            extra_power_pins_lines = getExtraPowerPinsLines(arc_info)
            write_list.append(extra_power_pins_lines)
 
        elif when_condition_header in template_line:
            write_list.append(template_line)
            when_cond_line, when_pins = getWhenConditionLines(arc_info)
            write_list.append(when_cond_line)
            unspecified_pins_lines = getUnspecifiedPinsLines(
                when_pins, arc_info
            )
            write_list.append(unspecified_pins_lines)
            pins_fixed_state_lines = getUserFixedStatePinsLines(arc_info)
            write_list.append(pins_fixed_state_lines)
 
        elif 'glitch__minq' in arc_info['HEADER_INFO']:
            glitch_minq_line = get_glitch_minq_line(template_line, arc_info)
            write_list.append(glitch_minq_line)
 
        elif 'glitch__maxq' in arc_info['HEADER_INFO']:
            glitch_maxq_line = get_glitch_maxq_line(template_line, arc_info)
            write_list.append(glitch_maxq_line)
 
        elif 'pushout_per' in template_line:
            equals_idx = template_line.index('=')
            pushout_idx = template_line.index('pushout=')
            metric_thresh = str(arc_info['PUSHOUT_PER'])
            pushout_per_line = template_line[:equals_idx + 1
                                             ] + ' ' + metric_thresh + ' ' + template_line[
                pushout_idx:]
            write_list.append(pushout_per_line)
 
        elif '.tran' in template_line and not is_fmc and arc_info['CELL_NAME'][:2] != 'MB' and not is_SYNC234(arc_info)\
                and not is_special_CKLN(cell_name, rel_pin, rel_pin_dir, vector) and not is_special_CKLH(arc_info) and not ('SYNC1P5' in arc_info['CELL_NAME']):
            new_item = get_new_tran_item(arc_info)
            need_to_add = False
            for line in write_list:
                if '.meas' in line and new_item in line:
                    need_to_add = True
                    break
 
            if need_to_add:
                model_idx = template_line.index('model=')
                template_line = template_line[:model_idx
                                              ] + ', ' + new_item + ' ' + template_line[
                    model_idx:]
 
        elif '* OPT_RESULTS ' in template_line:
            new_tran_item = get_new_tran_item(arc_info)
            if new_tran_item == 'cp2q_del2' and not is_special_CKLN(
                cell_name, rel_pin, rel_pin_dir, vector
            ) and not is_special_CKLH(arc_info):
                template_line = template_line.strip(
                ) + ' ' + new_tran_item + '\n'
            elif is_CKL_notE_and_notTE(arc_info):
                template_line = template_line.strip(
                ) + ' ' + new_tran_item + '\n'
            if 'clkbb' in internal_clks:
                template_line = template_line.strip() + ' cp2clkb cp2clkbb\n'
            elif 'clkb' in internal_clks:
                template_line = template_line.strip() + ' cp2clkb\n'
 
            if ('SE' in when or '!SA' in when or 'C' in when) and new_tran_item == 'cp2q_del2':
                template_line = template_line.strip(
                ) + ' ' + new_tran_item + '\n'
 
            write_list.append(template_line)
        else:
            if not (
                ".tran" in template_line and "model=optmod" in template_line
            ):
                write_list.append(template_line)
 
        if '.meas cp2cp trig' in template_line and internal_clks:
            cross = get_cp2cp_fisrt_cross(template_line)
            internal_clk_line = get_internal_clk_meas(
                internal_clks, rel_pin, rel_pin_dir, cross
            )
            write_list.append(internal_clk_line)
        if '.tran' in template_line and not is_fmc:
            if 'clkbb' in internal_clks:
                new_item = 'cp2clkb, cp2clkbb'
            elif 'clkb' in internal_clks:
                new_item = 'cp2clkb'
            if internal_clks:
                model_idx = template_line.index('model=')
                template_line = template_line[:model_idx
                                              ] + ', ' + new_item + ' ' + template_line[
                    model_idx:]
 
            write_list.append(template_line)
 
    write_list = post_icg_ov.post_process(arc_info, write_list)
    write_list = post_lnd2sr.post_process(arc_info, write_list)
    write_list = post_mb_an2.post_process(arc_info, write_list)
    write_list = post_sdfmoq.post_process(arc_info, write_list)
    write_list = remove_final_state.post_process(arc_info, write_list)
    if '_AMD_' in arc_info['TEMPLATE_DECK_PATH']:
        write_list = post_final_state.post_process(arc_info, write_list)
    return write_list
 
 
def get_cp2cp_fisrt_cross(template_line):
    cross_idx = template_line.index('cross')
    targ_after_cross = template_line.index('targ')
    _, cross = template_line[cross_idx:targ_after_cross].split('=')
    return cross
 
 
def search_templatetcl_for_internal_clk(arc_info):
    template_tcl_path = arc_info['TEMPLATE_TCL']
    with open(template_tcl_path, 'r') as f:
        template_tcl = f.readlines()
    cell = arc_info['CELL_NAME']
    rel_pin = arc_info['REL_PIN']
    defined_values = None
    for line in template_tcl:
        if 'set_constraint_criteria' in line and cell in line and rel_pin in line:
            try:
                defined_values = line.split('check_voltage_swing')[1].strip(
                ).replace('{', '').replace('}', '').split()
            except IndexError:
                continue
            if 'clkb' in line:
                break
    if defined_values is None:
        return {}
    internal_clks = {}
    for val in defined_values:
        if val.isalpha():
            key = val
        else:
            if 'clkb' in key:
                internal_clks[key] = val
    return internal_clks
 
 
def is_CKG_cell(arc_info):
    if 'CKG' in arc_info['CELL_NAME']:
        return True
    return False
 
 
def is_SYNC234(arc_info):
    if 'SYNC2' in arc_info['CELL_NAME'] or 'SYNC3' in arc_info[
            'CELL_NAME'] or 'SYNC4' in arc_info['CELL_NAME']:
        return True
    return False
 
 
def get_new_tran_item(arc_info):
    when = arc_info['WHEN'].split('&')
    if 'SE' in when or '!SA' in when or 'C' in when:
        return 'final_state_check'
    if (is_E_dominates(arc_info) or
            is_CKG_cell(arc_info)) and not is_CKL_notE_and_notTE(arc_info):
        return 'cp2q_del2'
    return 'final_state_check'
 
 
def get_dpins_settings(arc_info):
    pinlist = arc_info['TEMPLATE_PINLIST'].split()
    vector = [char for char in arc_info['VECTOR']]
    when = arc_info['WHEN'].split('&')
    dpins_settings = []
    probe_pin = arc_info['PROBE_PIN_1']
    rel_pin = arc_info['REL_PIN']
    rel_pin_dir = arc_info['REL_PIN_DIR']
    if 'SE' in when or '!SA' in when or 'C' in when:
        if 'SE' in when:
            if 'SI' in when:
                dpins_settings.append(
                    "XVSI SI 0 stdvs_fall_rise VDD='vdd_value' slew='constr_pin_slew' t01='constrained_pin_t01' t02='constrained_pin_t02'\n")
            elif '!SI' in when:
                dpins_settings.append(
                    "XVSI SI 0 stdvs_rise_fall VDD='vdd_value' slew='constr_pin_slew' t01='constrained_pin_t01' t02='constrained_pin_t02'\n")
        elif '!SA' in when:
            if 'DB' in when:
                dpins_settings.append(
                    "XVDB DB 0 stdvs_fall_rise VDD='vdd_value' slew='constr_pin_slew' t01='constrained_pin_t01' t02='constrained_pin_t02'\n")
            elif '!DB' in when:
                dpins_settings.append(
                    "XVDB DB 0 stdvs_rise_fall VDD='vdd_value' slew='constr_pin_slew' t01='constrained_pin_t01' t02='constrained_pin_t02'\n")
        elif 'C' in when:
            dpins_settings.append(
                "XVC C 0 stdvs_fall_rise VDD='vdd_value' slew='constr_pin_slew' t01='constrained_pin_t01' t02='constrained_pin_t02'\n")
    else:
        if arc_info['CELL_NAME'][:2] == 'MB':
            for idx, pin in enumerate(pinlist):
                if pin[0] == 'D':
                    qpin_idx = get_qpin_idx(pinlist, pin)
                    if vector[
                            idx] == '0' and not is_q_vector_numeric(qpin_idx, vector):
                        dpins_settings.append('XV'+pin+' '+pin
                                              + " 0 stdvs_rise_fall VDD='vdd_value' slew='constr_pin_slew' t01='constrained_pin_t01' t02='constrained_pin_t02'\n")
                    elif vector[
                            idx] == '1' and not is_q_vector_numeric(qpin_idx, vector):
                        dpins_settings.append('XV'+pin+' '+pin
                                              + " 0 stdvs_fall_rise VDD='vdd_value' slew='constr_pin_slew' t01='constrained_pin_t01' t02='constrained_pin_t02'\n")
            if is_E_dominates(arc_info):
                if rel_pin_dir == 'fall':
                    if probe_pin == 'ZN' or 'QN' in probe_pin or 'YN' in probe_pin:
                        dpins_settings.append(
                            ".meas cp2q_del2 trig v(" + rel_pin +
                            ") val='vdd_value/2' cross=3 targ v(" + probe_pin +
                            ") val='0.95*vdd_value' cross=1 td='related_pin_t03'\n"
                        )
                    elif probe_pin == 'Z' or 'Q' in probe_pin or 'Y' in probe_pin:
                        dpins_settings.append(
                            ".meas cp2q_del2 trig v(" + rel_pin +
                            ") val='vdd_value/2' cross=3 targ v(" + probe_pin +
                            ") val='0.05*vdd_value' cross=1 td='related_pin_t03'\n"
                        )
 
                elif rel_pin_dir == 'rise':
                    if probe_pin == 'ZN' or 'QN' in probe_pin or 'YN' in probe_pin:
                        dpins_settings.append(
                            ".meas cp2q_del2 trig v(" + rel_pin +
                            ") val='vdd_value/2' cross=3 targ v(" + probe_pin +
                            ") val='0.05*vdd_value' cross=1 td='related_pin_t03'\n"
                        )
                    elif probe_pin == 'Z' or 'Q' in probe_pin or 'Y' in probe_pin:
                        dpins_settings.append(
                            ".meas cp2q_del2 trig v(" + rel_pin +
                            ") val='vdd_value/2' cross=3 targ v(" + probe_pin +
                            ") val='0.95*vdd_value' cross=1 td='related_pin_t03'\n"
                        )
            else:
                dpin_idx = get_dpin_idx(pinlist, probe_pin)
                if dpin_idx is not None:
                    if vector[dpin_idx] == '0':
                        if not is_E_dominates(arc_info):
                            if 'QN' in probe_pin:
                                dpins_settings.append(
                                    '.meas final_state find v(' + probe_pin +
                                    ') at=50u\n'
                                )
                                dpins_settings.append(
                                    ".meas final_state_check find par('1') at='final_state/vdd_value > 0.95 ? 0 : -1'\n"
                                )
                            elif 'Q' in probe_pin:
                                dpins_settings.append(
                                    '.meas final_state find v(' + probe_pin +
                                    ') at=50u\n'
                                )
                                dpins_settings.append(
                                    ".meas final_state_check find par('1') at='final_state/vdd_value < 0.05 ? 0 : -1'\n"
                                )
 
                    elif vector[dpin_idx] == '1':
                        if not is_E_dominates(arc_info):
                            if 'QN' in probe_pin:
                                dpins_settings.append(
                                    '.meas final_state find v(' + probe_pin +
                                    ') at=50u\n'
                                )
                                dpins_settings.append(
                                    ".meas final_state_check find par('1') at='final_state/vdd_value < 0.05 ? 0 : -1'\n"
                                )
                            elif 'Q' in probe_pin:
                                dpins_settings.append(
                                    '.meas final_state find v(' + probe_pin +
                                    ') at=50u\n'
                                )
                                dpins_settings.append(
                                    ".meas final_state_check find par('1') at='final_state/vdd_value > 0.95 ? 0 : -1'\n"
                                )
        elif is_LHAO_cell(arc_info['CELL_NAME']):
            pin_setting = get_LHAO_pins_setting(arc_info, probe_pin)
            dpins_settings.extend(pin_setting)
        else:
            for pin_condition in when:
                cell_name = arc_info['CELL_NAME']
                if is_SDF_OR_cell(cell_name):
                    pin_setting = get_OR_dpins_setting(
                        pin_condition, probe_pin, arc_info
                    )
                    if pin_setting:
                        dpins_settings.extend(pin_setting)
 
                elif is_SDF_OA_cell(cell_name):
                    pin_setting = get_OA_dpins_setting(
                        pin_condition, probe_pin, arc_info
                    )
                    if pin_setting:
                        dpins_settings.extend(pin_setting)
 
                elif is_SDF_AO_cell(cell_name):
                    pin_setting = get_AO_dpins_setting(
                        pin_condition, probe_pin, arc_info
                    )
                    if pin_setting:
                        dpins_settings.extend(pin_setting)
 
                elif is_AN_DFM_cell(cell_name):
                    pin_setting = get_AN_DFM_dpins_setting(
                        pin_condition, probe_pin, arc_info
                    )
                    if pin_setting:
                        dpins_settings.extend(pin_setting)
 
                elif is_CKL_cell(cell_name):
                    if is_special_CKLH(arc_info) and pin_condition == 'E':
                        pin_setting = get_CKLH_setting()
                    elif is_special_CKLN(
                        cell_name, rel_pin, rel_pin_dir, vector
                    ) and pin_condition == 'E':
                        pin_setting = get_CKLN_setting()
                    else:
                        pin_setting = get_CKL_pins_setting(
                            pin_condition, probe_pin, arc_info
                        )
                    if pin_setting:
                        dpins_settings.extend(pin_setting)
 
                if pin_condition == '!D':
                    dpins_settings.append('XV'+pin_condition[1:]+' '+pin_condition[1:]
                                          + " 0 stdvs_rise_fall VDD='vdd_value' slew='constr_pin_slew' t01='constrained_pin_t01' t02='constrained_pin_t02'\n")
                    if not is_E_dominates(arc_info) and not is_SYNC234(arc_info):
                        if 'QN' in probe_pin:
                            dpins_settings.append(
                                '.meas final_state find v(' +
                                probe_pin + ') at=50u\n'
                            )
                            dpins_settings.append(
                                ".meas final_state_check find par('1') at='final_state/vdd_value > 0.95 ? 0 : -1'\n"
                            )
                        elif 'Q' in probe_pin:
                            dpins_settings.append(
                                '.meas final_state find v(' +
                                probe_pin + ') at=50u\n'
                            )
                            dpins_settings.append(
                                ".meas final_state_check find par('1') at='final_state/vdd_value < 0.05 ? 0 : -1'\n"
                            )
 
                elif pin_condition == 'D':
                    dpins_settings.append('XV'+pin_condition+' '+pin_condition
                                          + " 0 stdvs_fall_rise VDD='vdd_value' slew='constr_pin_slew' t01='constrained_pin_t01' t02='constrained_pin_t02'\n")
                    if not is_E_dominates(arc_info) and not is_SYNC234(arc_info):
                        if 'QN' in probe_pin:
                            dpins_settings.append(
                                '.meas final_state find v(' +
                                probe_pin + ') at=50u\n'
                            )
                            dpins_settings.append(
                                ".meas final_state_check find par('1') at='final_state/vdd_value < 0.05 ? 0 : -1'\n"
                            )
                        elif 'Q' in probe_pin:
                            dpins_settings.append(
                                '.meas final_state find v(' +
                                probe_pin + ') at=50u\n'
                            )
                            dpins_settings.append(
                                ".meas final_state_check find par('1') at='final_state/vdd_value > 0.95 ? 0 : -1'\n"
                            )
 
            if (is_E_dominates(arc_info) or is_CKG_cell(arc_info)) and not is_special_CKLN(cell_name, rel_pin, rel_pin_dir, vector) and not is_special_CKLH(arc_info)\
                    and not is_CKL_notE_and_notTE(arc_info):
                if rel_pin_dir == 'fall':
                    if probe_pin == 'ZN' or 'QN' in probe_pin or 'YN' in probe_pin:
                        dpins_settings.append(
                            ".meas cp2q_del2 trig v(" + rel_pin +
                            ") val='vdd_value/2' cross=3 targ v(" + probe_pin +
                            ") val='0.95*vdd_value' cross=1 td='related_pin_t03'\n"
                        )
                    elif probe_pin == 'Z' or 'Q' in probe_pin or 'Y' in probe_pin:
                        dpins_settings.append(
                            ".meas cp2q_del2 trig v(" + rel_pin +
                            ") val='vdd_value/2' cross=3 targ v(" + probe_pin +
                            ") val='0.05*vdd_value' cross=1 td='related_pin_t03'\n"
                        )
 
                elif rel_pin_dir == 'rise':
                    if probe_pin == 'ZN' or 'QN' in probe_pin or 'YN' in probe_pin:
                        dpins_settings.append(
                            ".meas cp2q_del2 trig v(" + rel_pin +
                            ") val='vdd_value/2' cross=3 targ v(" + probe_pin +
                            ") val='0.05*vdd_value' cross=1 td='related_pin_t03'\n"
                        )
                    elif probe_pin == 'Z' or 'Q' in probe_pin or 'Y' in probe_pin:
                        dpins_settings.append(
                            ".meas cp2q_del2 trig v(" + rel_pin +
                            ") val='vdd_value/2' cross=3 targ v(" + probe_pin +
                            ") val='0.95*vdd_value' cross=1 td='related_pin_t03'\n"
                        )
 
    return dpins_settings
 
 
def is_special_CKLH(arc_info):
    vector = [char for char in arc_info['VECTOR']]
    when = arc_info['WHEN'].split('&')
    dpins_settings = []
    probe_pin = arc_info['PROBE_PIN_1']
    rel_pin = arc_info['REL_PIN']
    rel_pin_dir = arc_info['REL_PIN_DIR']
    cell_name = arc_info['CELL_NAME']
    if 'CKLH' in cell_name and rel_pin == 'CPN' and rel_pin_dir == 'rise' and vector[
            -1] == '0':
        return True
    return False
 
 
def is_special_CKLN(cell_name, rel_pin, rel_pin_dir, vector):
    if 'CKLN' in cell_name and rel_pin == 'CP' and rel_pin_dir == 'fall' and vector[
            -1] == '1':
        return True
    return False
 
 
def get_AN_DFM_dpins_setting(pin_condition, probe_pin, arc_info):
    pin_setting = []
    if '!DA' == pin_condition:
        pin_setting.append(
            'XV' + pin_condition[1:] + ' ' + pin_condition[1:] +
            " 0 stdvs_rise_fall VDD='vdd_value' slew='constr_pin_slew' t01='constrained_pin_t01' t02='constrained_pin_t02'\n"
        )
        if not is_E_dominates(arc_info):
            if 'QN' in probe_pin:
                pin_setting.append(
                    '.meas final_state find v(' + probe_pin + ') at=50u\n'
                )
                pin_setting.append(
                    ".meas final_state_check find par('1') at='final_state/vdd_value > 0.95 ? 0 : -1'\n"
                )
            elif 'Q' in probe_pin:
                pin_setting.append(
                    '.meas final_state find v(' + probe_pin + ') at=50u\n'
                )
                pin_setting.append(
                    ".meas final_state_check find par('1') at='final_state/vdd_value < 0.05 ? 0 : -1'\n"
                )
 
    elif 'DA' == pin_condition:
        pin_setting.append(
            'XV' + pin_condition + ' ' + pin_condition +
            " 0 stdvs_fall_rise VDD='vdd_value' slew='constr_pin_slew' t01='constrained_pin_t01' t02='constrained_pin_t02'\n"
        )
        if not is_E_dominates(arc_info):
            if 'QN' in probe_pin:
                pin_setting.append(
                    '.meas final_state find v(' + probe_pin + ') at=50u\n'
                )
                pin_setting.append(
                    ".meas final_state_check find par('1') at='final_state/vdd_value < 0.05 ? 0 : -1'\n"
                )
            elif 'Q' in probe_pin:
                pin_setting.append(
                    '.meas final_state find v(' + probe_pin + ') at=50u\n'
                )
                pin_setting.append(
                    ".meas final_state_check find par('1') at='final_state/vdd_value > 0.95 ? 0 : -1'\n"
                )
 
    return pin_setting
 
 
def get_LHAO_pins_setting(arc_info, probe_pin):
    pinlist = arc_info['TEMPLATE_PINLIST'].split()
    vector = [char for char in arc_info['VECTOR']]
    pin_setting = []
 
    if arc_info['REL_PIN'] == 'E':
        pin_setting.append(
            "XVA1 A1 0 stdvs_fall_rise VDD='vdd_value' slew='constr_pin_slew' t01='constrained_pin_t01' t02='constrained_pin_t02'\n"
        )
        pin_setting.append(
            "XVB2 B2 0 stdvs_fall_rise VDD='vdd_value' slew='constr_pin_slew' t01='constrained_pin_t01' t02='constrained_pin_t02'\n"
        )
        EN_idx = pinlist.index('EN')
        if vector[EN_idx] == 'F':
            pin_setting.append(
                "XVEN EN 0 stdvs_fall VDD='vdd_value' slew='constr_pin_slew' t01='constrained_pin_t01'\n"
            )
        elif vector[EN_idx] == 'R':
            pin_setting.append(
                "XVEN EN 0 stdvs_rise VDD='vdd_value' slew='constr_pin_slew' t01='constrained_pin_t01'\n"
            )
        if not is_E_dominates(arc_info):
            if 'QN' in probe_pin:
                pin_setting.append(
                    '.meas final_state find v(' + probe_pin +
                    ') at=50u\n'
                )
                pin_setting.append(
                    ".meas final_state_check find par('1') at='final_state/vdd_value < 0.05 ? 0 : -1'\n"
                )
            elif 'Q' in probe_pin:
                pin_setting.append(
                    '.meas final_state find v(' + probe_pin +
                    ') at=50u\n'
                )
                pin_setting.append(
                    ".meas final_state_check find par('1') at='final_state/vdd_value > 0.95 ? 0 : -1'\n"
                )
    elif arc_info['REL_PIN'] == 'EN':
        pin_setting.append(
            "XVA1 A1 0 stdvs_rise_fall VDD='vdd_value' slew='constr_pin_slew' t01='constrained_pin_t01' t02='constrained_pin_t02'\n"
        )
        pin_setting.append(
            "XVB2 B2 0 stdvs_rise_fall VDD='vdd_value' slew='constr_pin_slew' t01='constrained_pin_t01' t02='constrained_pin_t02'\n"
        )
        E_idx = pinlist.index('E')
        if vector[E_idx] == 'F':
            pin_setting.append(
                "XVE E 0 stdvs_fall VDD='vdd_value' slew='constr_pin_slew' t01='constrained_pin_t01'\n"
            )
        elif vector[E_idx] == 'R':
            pin_setting.append(
                "XVE E 0 stdvs_rise VDD='vdd_value' slew='constr_pin_slew' t01='constrained_pin_t01'\n"
            )
 
        if not is_E_dominates(arc_info):
            if 'QN' in probe_pin:
                pin_setting.append(
                    '.meas final_state find v(' + probe_pin + ') at=50u\n'
                )
                pin_setting.append(
                    ".meas final_state_check find par('1') at='final_state/vdd_value > 0.95 ? 0 : -1'\n"
                )
            elif 'Q' in probe_pin:
                pin_setting.append(
                    '.meas final_state find v(' + probe_pin + ') at=50u\n'
                )
                pin_setting.append(
                    ".meas final_state_check find par('1') at='final_state/vdd_value < 0.05 ? 0 : -1'\n"
                )
 
    return pin_setting
 
 
def get_AO_dpins_setting(pin_condition, probe_pin, arc_info):
    pin_setting = []
    if '!DA' == pin_condition or '!DD' in pin_condition:
        pin_setting.append(
            'XV' + pin_condition[1:] + ' ' + pin_condition[1:] +
            " 0 stdvs_rise_fall VDD='vdd_value' slew='constr_pin_slew' t01='constrained_pin_t01' t02='constrained_pin_t02'\n"
        )
        if '!DD' == pin_condition:
            if not is_E_dominates(arc_info):
                if 'QN' in probe_pin:
                    pin_setting.append(
                        '.meas final_state find v(' + probe_pin + ') at=50u\n'
                    )
                    pin_setting.append(
                        ".meas final_state_check find par('1') at='final_state/vdd_value > 0.95 ? 0 : -1'\n"
                    )
                elif 'Q' in probe_pin:
                    pin_setting.append(
                        '.meas final_state find v(' + probe_pin + ') at=50u\n'
                    )
                    pin_setting.append(
                        ".meas final_state_check find par('1') at='final_state/vdd_value < 0.05 ? 0 : -1'\n"
                    )
 
    elif 'DA' == pin_condition or 'DD' == pin_condition:
        pin_setting.append(
            'XV' + pin_condition + ' ' + pin_condition +
            " 0 stdvs_fall_rise VDD='vdd_value' slew='constr_pin_slew' t01='constrained_pin_t01' t02='constrained_pin_t02'\n"
        )
        if 'DD' == pin_condition:
            if not is_E_dominates(arc_info):
                if 'QN' in probe_pin:
                    pin_setting.append(
                        '.meas final_state find v(' + probe_pin + ') at=50u\n'
                    )
                    pin_setting.append(
                        ".meas final_state_check find par('1') at='final_state/vdd_value < 0.05 ? 0 : -1'\n"
                    )
                elif 'Q' in probe_pin:
                    pin_setting.append(
                        '.meas final_state find v(' + probe_pin + ') at=50u\n'
                    )
                    pin_setting.append(
                        ".meas final_state_check find par('1') at='final_state/vdd_value > 0.95 ? 0 : -1'\n"
                    )
 
    return pin_setting
 
 
def get_OA_dpins_setting(pin_condition, probe_pin, arc_info):
    pin_setting = []
    if '!DA' == pin_condition or '!DB' in pin_condition:
        pin_setting.append(
            'XV' + pin_condition[1:] + ' ' + pin_condition[1:] +
            " 0 stdvs_rise_fall VDD='vdd_value' slew='constr_pin_slew' t01='constrained_pin_t01' t02='constrained_pin_t02'\n"
        )
        if '!DB' == pin_condition:
            if not is_E_dominates(arc_info):
                if 'QN' in probe_pin:
                    pin_setting.append(
                        '.meas final_state find v(' + probe_pin + ') at=50u\n'
                    )
                    pin_setting.append(
                        ".meas final_state_check find par('1') at='final_state/vdd_value > 0.95 ? 0 : -1'\n"
                    )
                elif 'Q' in probe_pin:
                    pin_setting.append(
                        '.meas final_state find v(' + probe_pin + ') at=50u\n'
                    )
                    pin_setting.append(
                        ".meas final_state_check find par('1') at='final_state/vdd_value < 0.05 ? 0 : -1'\n"
                    )
 
    elif 'DA' == pin_condition or 'DB' == pin_condition:
        pin_setting.append(
            'XV' + pin_condition + ' ' + pin_condition +
            " 0 stdvs_fall_rise VDD='vdd_value' slew='constr_pin_slew' t01='constrained_pin_t01' t02='constrained_pin_t02'\n"
        )
        if 'DB' == pin_condition:
            if not is_E_dominates(arc_info):
                if 'QN' in probe_pin:
                    pin_setting.append(
                        '.meas final_state find v(' + probe_pin + ') at=50u\n'
                    )
                    pin_setting.append(
                        ".meas final_state_check find par('1') at='final_state/vdd_value < 0.05 ? 0 : -1'\n"
                    )
                elif 'Q' in probe_pin:
                    pin_setting.append(
                        '.meas final_state find v(' + probe_pin + ') at=50u\n'
                    )
                    pin_setting.append(
                        ".meas final_state_check find par('1') at='final_state/vdd_value > 0.95 ? 0 : -1'\n"
                    )
 
    return pin_setting
 
 
def get_OR_dpins_setting(pin_condition, probe_pin, arc_info):
    pin_setting = []
    if '!D' in pin_condition:
        pin_setting.append(
            'XV' + pin_condition[1:] + ' ' + pin_condition[1:] +
            " 0 stdvs_rise_fall VDD='vdd_value' slew='constr_pin_slew' t01='constrained_pin_t01' t02='constrained_pin_t02'\n"
        )
        if '!DB' == pin_condition:
            if not is_E_dominates(arc_info):
                if 'QN' in probe_pin:
                    pin_setting.append(
                        '.meas final_state find v(' + probe_pin + ') at=50u\n'
                    )
                    pin_setting.append(
                        ".meas final_state_check find par('1') at='final_state/vdd_value > 0.95 ? 0 : -1'\n"
                    )
                elif 'Q' in probe_pin:
                    pin_setting.append(
                        '.meas final_state find v(' + probe_pin + ') at=50u\n'
                    )
                    pin_setting.append(
                        ".meas final_state_check find par('1') at='final_state/vdd_value < 0.05 ? 0 : -1'\n"
                    )
 
    elif 'D' in pin_condition:
        pin_setting.append(
            'XV' + pin_condition + ' ' + pin_condition +
            " 0 stdvs_fall_rise VDD='vdd_value' slew='constr_pin_slew' t01='constrained_pin_t01' t02='constrained_pin_t02'\n"
        )
        if 'DB' == pin_condition:
            if not is_E_dominates(arc_info):
                if 'QN' in probe_pin:
                    pin_setting.append(
                        '.meas final_state find v(' + probe_pin + ') at=50u\n'
                    )
                    pin_setting.append(
                        ".meas final_state_check find par('1') at='final_state/vdd_value < 0.05 ? 0 : -1'\n"
                    )
                elif 'Q' in probe_pin:
                    pin_setting.append(
                        '.meas final_state find v(' + probe_pin + ') at=50u\n'
                    )
                    pin_setting.append(
                        ".meas final_state_check find par('1') at='final_state/vdd_value > 0.95 ? 0 : -1'\n"
                    )
 
    return pin_setting
 
 
def get_CKLN_setting():
    pin_setting = []
    pin_setting.append(
        "XVE E 0 stdvs_fall_rise VDD='vdd_value' slew='constr_pin_slew' t01='constrained_pin_t01' t02='constrained_pin_t02'\n"
    )
    return pin_setting
 
 
def get_CKLH_setting():
    pin_setting = []
    pin_setting.append(
        "XVE E 0 stdvs_fall_rise VDD='vdd_value' slew='constr_pin_slew' t01='constrained_pin_t01' t02='constrained_pin_t02'\n"
    )
    return pin_setting
 
 
def get_CKL_pins_setting(pin_condition, probe_pin, arc_info):
    pin_setting = []
    rel_pin = arc_info['REL_PIN']
    if '!E' in pin_condition:
        pin_setting.append(
            'XV' + pin_condition[1:] + ' ' + pin_condition[1:] +
            " 0 stdvs_rise_fall VDD='vdd_value' slew='constr_pin_slew' t01='constrained_pin_t01' t02='constrained_pin_t02'\n"
        )
        if not is_E_dominates(arc_info) or is_CKL_notE_and_notTE(arc_info):
            if is_CKL_notE_and_notTE(arc_info):
                if arc_info['REL_PIN'] == 'CP' and arc_info['REL_PIN_DIR'
                                                            ] == 'fall':
                    if 'QN' in probe_pin:
                        pin_setting.append(
                            '.meas final_state find v(' + probe_pin + ') at=50u\n'
                        )
                        pin_setting.append(
                            ".meas final_state_check find par('1') at='final_state/vdd_value > 0.95 ? 0 : -1'\n"
                        )
                    elif 'Q' in probe_pin:
                        pin_setting.append(
                            '.meas final_state find v(' + probe_pin + ') at=50u\n'
                        )
                        pin_setting.append(
                            ".meas final_state_check find par('1') at='final_state/vdd_value < 0.05 ? 0 : -1'\n"
                        )
                elif arc_info['REL_PIN'] == 'CPN' and arc_info['REL_PIN_DIR'
                                                               ] == 'rise':
                    if 'QN' in probe_pin:
                        pin_setting.append(
                            '.meas final_state find v(' + probe_pin + ') at=50u\n'
                        )
                        pin_setting.append(
                            ".meas final_state/vdd_value < 0.05 ? 0 : -1'\n"
                        )
                    elif 'Q' in probe_pin:
                        pin_setting.append(
                            '.meas final_state find v(' + probe_pin + ') at=50u\n'
                        )
                        pin_setting.append(
                            ".meas final_state_check find par('1') at='final_state/vdd_value > 0.95 ? 0 : -1'\n"
                        )
            else:
                if 'QN' in probe_pin:
                    pin_setting.append(
                        '.meas final_state find v(' + probe_pin + ') at=50u\n'
                    )
                    pin_setting.append(
                        ".meas final_state_check find par('1') at='final_state/vdd_value < 0.05 ? 0 : -1'\n"
                    )
                elif 'Q' in probe_pin:
                    pin_setting.append(
                        '.meas final_state find v(' + probe_pin + ') at=50u\n'
                    )
                    pin_setting.append(
                        ".meas final_state_check find par('1') at='final_state/vdd_value > 0.95 ? 0 : -1'\n"
                    )
 
    return pin_setting
 
 
def is_CKL_cell(cell_name):
    if 'CKL' == cell_name[:3] or 'GCKL' == cell_name[:4] or 'PTCKL' == cell_name[:5] or cell_name.startswith('GPTCKL'):
        return True
    return False
 
 
def is_LHAO_cell(cell_name):
    if 'LHAO' == cell_name[:4]:
        return True
    return False
 
 
def is_AN_DFM_cell(cell_name):
    if 'DFM' in cell_name:
        return True
    if 'AN' in cell_name:
        return True
    return False
 
 
def is_SDF_AO_cell(cell_name):
    if 'SDF' not in cell_name:
        return False
    if 'AO' in cell_name:
        return True
    return False
 
 
def is_SDF_OA_cell(cell_name):
    if 'SDF' not in cell_name:
        return False
    if 'OA' in cell_name:
        return True
    return False
 
 
def is_SDF_OR_cell(cell_name):
    if 'SDF' not in cell_name:
        return False
    if 'OR' in cell_name and not cell_name.startswith('SDFQNSXG0OPPCNORIGMEGSFOC'):
        return True
    return False
 
 
def get_dpin_idx(pinlist, qpin):
    q_first_numeric_idx = get_first_numeric_idx(qpin)
    if q_first_numeric_idx != -1:
        for idx, pin in enumerate(pinlist):
            if pin[0] == 'D':
                d_first_numeric_idx = get_first_numeric_idx(pin)
                if pin[d_first_numeric_idx:] == qpin[q_first_numeric_idx:]:
                    return idx
 
 
def get_qpin_idx(pinlist, dpin):
    d_first_numeric_idx = get_first_numeric_idx(dpin)
    if d_first_numeric_idx != -1:
        for idx, pin in enumerate(pinlist):
            if pin[0] == 'Q':
                q_first_numeric_idx = get_first_numeric_idx(pin)
 
                if pin[q_first_numeric_idx:] == dpin[d_first_numeric_idx:]:
                    return idx
 
 
def get_first_numeric_idx(pin):
    for i, char in enumerate(pin):
        if char.isnumeric():
            return i
    return -1
 
 
def is_E_dominates(arc_info):
    pinlist = arc_info['TEMPLATE_PINLIST'].split()
    if 'D' in pinlist or 'DA' in pinlist or 'A1' in pinlist or 'D1' in pinlist:
        return False
    if 'E' in pinlist or 'EN' in pinlist:
        return True
    return False
 
 
def is_CKL_notE_and_notTE(arc_info):
    when = arc_info['WHEN'].split('&')
    if '!E' in when and '!TE' in when:
        return True
    return False
 
 
def get_internal_clk_meas(internal_clks, rel_pin, rel_pin_dir, cross):
    for internal_clk, val in internal_clks.items():
        if internal_clk == 'clkbb':
            if rel_pin_dir == 'fall':
                line = ".meas cp2clkb trig v("+rel_pin + ") val='vdd_value/2' cross="+cross + " targ v(X1.clkb) val='vdd_value*"+str(1-float(val))+"' cross="+cross+"\n" +\
                    ".meas cp2clkbb trig v("+rel_pin+") val='vdd_value/2' cross="+cross + \
                    " targ v(X1.clkbb) val='vdd_value*" + \
                    val+"' cross="+cross + "\n"
 
            elif rel_pin_dir == 'rise':
                line = ".meas cp2clkb trig v("+rel_pin+") val='vdd_value/2' cross="+cross + " targ v(X1.clkb) val='vdd_value*"+val+"' cross="+cross + "\n" +\
                    ".meas cp2clkbb trig v("+rel_pin+") val='vdd_value/2' cross="+cross + \
                    " targ v(X1.clkbb) val='vdd_value*" + \
                    str(1-float(val))+"' cross="+cross + "\n"
            break
        elif internal_clk == 'clkb':
            if rel_pin_dir == 'fall':
                line = ".meas cp2clkb trig v(" + rel_pin + ") val='vdd_value/2' cross=" + cross + " targ v(X1.clkb) val='vdd_value*" + str(
                    1 - float(val)
                ) + "' cross=" + cross + "\n"
            elif rel_pin_dir == 'rise':
                line = ".meas cp2clkb trig v(" + rel_pin + ") val='vdd_value/2' cross=" + \
                    cross + " targ v(X1.clkb) val='vdd_value*" + \
                    val + "' cross=" + cross + "\n"
    return line
 
 
def get_special_CLK_cp2q_del1_cross(cp2q_del1_line, arc_info):
    try:
        cross4 = cp2q_del1_line.index('cross=3')
    except ValueError:
        return cp2q_del1_line
    cp2q_del1_line = cp2q_del1_line[:cross4] + "cross=4 " + cp2q_del1_line[
        cross4 + 7:]
    return cp2q_del1_line
 
 
def get_cp2q_del1_cross(cp2q_del1_line, arc_info):
    rel_pin = arc_info['REL_PIN']
    rel_pin_dir = arc_info['REL_PIN_DIR']
    if is_E_dominates(arc_info) or is_CKG_cell(arc_info):
        try:
            cross4 = cp2q_del1_line.index('cross=4')
        except ValueError:
            return cp2q_del1_line
        cp2q_del1_line = cp2q_del1_line[:cross4] + "cross=3 " + cp2q_del1_line[
            cross4 + 7:]
    return cp2q_del1_line
 
 
def getExtraPowerPinsLines(input_options):
    template_deck_powerpins = ["VDD", "VSS", "VPP", "VBB"]
    new_power_pin_list = list()
    for cell_pin in input_options['NETLIST_PINS'].split():
        if not cell_pin in input_options['TEMPLATE_PINLIST'].split():
            if not cell_pin in template_deck_powerpins:
                new_power_pin_list.append(cell_pin)
 
    write_list = list()
    for power_pin in new_power_pin_list:
        write_list.append("V%s %s 0 'vdd_value'" % (power_pin, power_pin))
    write_line = '\n'.join(write_list) + '\n'
    return write_line
 
 
def getWhenConditionLines(input_options):
    vector = [char for char in input_options['VECTOR']]
    probe_pin = input_options['PROBE_PIN_1']
    when = input_options['WHEN'].split('&')
    rel_pin = input_options['REL_PIN']
    rel_pin_dir = input_options['REL_PIN_DIR']
    cell_name = input_options['CELL_NAME']
    when_cond = input_options['WHEN']
    dont_touch_pins = input_options['DONT_TOUCH_PINS']
    cell_name = input_options['CELL_NAME']
    if when_cond == "NO_CONDITION":
        write_line = "* No Condition\n"
        when_pins = []
    else:
        when_cond_tuple = parseLogicalWhenCondition(when_cond)
        splited_when = when_cond.split('&')
        when_pins = [x[0] for x in when_cond_tuple]
        write_list = list()
        for item in when_cond_tuple:
            if fix_cklnenq.is_cklnenq_TEN(cell_name, splited_when) and item[0] == 'EN' and vector[-1] != '0':
                continue
 
            if 'SE' in splited_when or '!SA' in splited_when or 'C' in splited_when:
                if 'SE' in splited_when and item[0] == 'SI':
                    continue
                if 'C' in splited_when and 'SE' not in splited_when and item[0] == 'C':
                    continue
                if '!SA' in splited_when and item[0] == 'DB':
                    continue
                else:
                    if str(item[1]) == '0':
                        value = 'vss_value'
                    else:
                        value = 'vdd_value'
                    line = "V%s %s 0 '%s'" % (item[0], item[0], value)
                    write_list.append(line)
            else:
                if (
                    is_special_CKLN(cell_name, rel_pin, rel_pin_dir, vector) or
                    is_special_CKLH(input_options)
                ) and item[0] == 'E':
                    continue
                if (is_SDF_OR_cell(cell_name) or is_SDF_OA_cell(cell_name))\
                        and (item[0] == 'DA' or item[0] == 'DB'):
                    continue
                if is_SDF_AO_cell(cell_name
                                  ) and (item[0] == 'DA' or item[0] == 'DD'):
                    continue
                if is_AN_DFM_cell(cell_name) and item[0] == 'DA':
                    continue
                if is_CKL_cell(cell_name) and item[0] == 'E' and item[1] == 0:
                    continue
                if item[0] in dont_touch_pins or item[0] == 'D' or item[0] == 'DA':
                    continue
                else:
                    if str(item[1]) == '0':
                        value = 'vss_value'
                    else:
                        value = 'vdd_value'
                    line = "V%s %s 0 '%s'" % (item[0], item[0], value)
                    write_list.append(line)
        write_line = '\n'.join(write_list) + '\n'
    return write_line, when_pins
 
 
def parseLogicalWhenCondition(when_cond):
    when_list = list()
    when_info = when_cond.split('&')
    for item in when_info:
        if item[0] == '!':
            value = 0
            pin_name = item[1:]
        else:
            value = 1
            pin_name = item
        when_list.append((pin_name, value))
    return when_list
 
 
def is_q_vector_numeric(qpin_idx, vector):
    if vector[qpin_idx].isnumeric():
        return True
    return False
 
 
def is_q_d_the_same(dpin_idx, qpin_idx, vector):
    if vector[dpin_idx] == vector[qpin_idx]:
        return True
    return False
 
 
def is_vector_numeric(pin_idx, vector):
    if vector[pin_idx].isnumeric():
        return True
    return False
 
 
def getUnspecifiedPinsLines(when_pins, input_options):
    pinlist = [x.strip() for x in input_options['TEMPLATE_PINLIST'].split()]
    vector = [char for char in input_options['VECTOR']]
    pins_vals_tuples = getUnspecifiedPinAssignments(when_pins, input_options)
    rel_pin = input_options['REL_PIN']
    probe_pin = input_options['PROBE_PIN_1']
    when = input_options['WHEN'].split('&')
    rel_pin = input_options['REL_PIN']
    rel_pin_dir = input_options['REL_PIN_DIR']
    cell_name = input_options['CELL_NAME']
    write_list = list()
    write_list.append("\n* Unspecified pins")
    for item in pins_vals_tuples:
        if 'CKLN' in cell_name and rel_pin == 'CP' and rel_pin_dir == 'fall':
            continue
        if 'CKLH' in cell_name and rel_pin == 'CPN' and rel_pin_dir == 'rise':
            continue
        if input_options['CELL_NAME'][:2] == 'MB' and item[0][0] == 'D':
            if 'bl' not in probe_pin and 'al' not in probe_pin and 'clkb' not in probe_pin:
                rel_pin_idx = pinlist.index(rel_pin)
                dpin_idx = get_dpin_idx(pinlist, probe_pin)
                after_rel_pin_vector = vector[rel_pin_idx + 1:]
                del after_rel_pin_vector[dpin_idx - rel_pin_idx - 1]
                after_rel_pin_vector = set(after_rel_pin_vector)
                if 'x' in after_rel_pin_vector and len(
                    after_rel_pin_vector
                ) == 1 and item[0] != pinlist[dpin_idx]:
                    value = 'vdd_value'
                else:
                    qpin_idx = get_qpin_idx(pinlist, item[0])
                    dpin_idx = pinlist.index(item[0])
                    if not is_q_vector_numeric(qpin_idx, vector):
                        continue
            else:
                qpin_idx = get_qpin_idx(pinlist, item[0])
                dpin_idx = pinlist.index(item[0])
                if not is_q_vector_numeric(qpin_idx, vector):
                    continue
        if input_options['CELL_NAME'][:2] == 'MB' and item[0][0] == 'Q':
            qpin_idx = pinlist.index(item[0])
            if not is_q_vector_numeric(qpin_idx, vector):
                continue
        if input_options['CELL_NAME'][:2] != 'MB' and item[0] in input_options[
                'OUTPUT_PINS']:
            pin_idx = pinlist.index(item[0])
            if not is_vector_numeric(pin_idx, vector):
                continue
        if is_LHAO_cell(input_options['CELL_NAME']) and (
            item[0] == 'A1' or item[0] == 'B2' or item[0] == 'EN' or
            item[0] == 'E'
        ):
            continue
        if is_SYNC234(input_options
                      ) and input_options['REL_PIN'] == 'CP' and input_options[
                'REL_PIN_DIR'] == 'rise' and item[0] == 'Q':
            continue
        if 'SYNC1P5' in input_options['CELL_NAME'] and (
            (
                input_options['REL_PIN'] == 'CP' and
                input_options['REL_PIN_DIR'] == 'fall'
            ) or (
                input_options['REL_PIN'] == 'CPN' and
                input_options['REL_PIN_DIR'] == 'rise'
            )
        ) and item[0] == 'Q':
            continue
        if str(item[1]) == '0':
            value = 'vss_value'
        else:
            value = 'vdd_value'
        line = "V%s %s 0 '%s'" % (item[0], item[0], value)
        write_list.append(line)
    write_line = '\n'.join(write_list) + '\n\n'
    return write_line
 
 
def getUserFixedStatePinsLines(input_options):
    pinlist = [x.strip() for x in input_options['TEMPLATE_PINLIST'].split()]
    vector = [char for char in input_options['VECTOR']]
    pins_vals_tuples = input_options['SIDE_PIN_STATES']
    dont_touch_pins = input_options['DONT_TOUCH_PINS']
    output_pins = input_options['OUTPUT_PINS']
    if len(pins_vals_tuples) > 0:
        write_list = list()
        write_list.append("\n* User specified fixed state pins")
        for item in pins_vals_tuples:
            if input_options['CELL_NAME'][:2] == 'MB' and item[0][0] == 'D':
                qpin_idx = get_qpin_idx(pinlist, item[0])
                dpin_idx = pinlist.index(item[0])
                if not is_q_vector_numeric(qpin_idx, vector):
                    continue
            if input_options['CELL_NAME'][:2] == 'MB' and item[0][0] == 'Q':
                qpin_idx = pinlist.index(item[0])
                if not is_q_vector_numeric(qpin_idx, vector):
                    continue
            if item[0] in dont_touch_pins:
                continue
            else:
                if str(item[1]) == 'low':
                    value = 'vss_value'
                else:
                    value = 'vdd_value'
                line = "V%s %s 0 '%s'" % (item[0], item[0], value)
                write_list.append(line)
        write_line = '\n'.join(write_list) + '\n\n'
        return write_line
    else:
        write_line = '\n'
        return write_line
 
 
def getUnspecifiedPinAssignments(when_pins, input_options):
    pin_list = [x.strip() for x in input_options['TEMPLATE_PINLIST'].split()]
    dont_touch_pins = input_options['DONT_TOUCH_PINS']
    constr_pin = input_options['CONSTR_PIN']
    rel_pin = input_options['REL_PIN']
    output_pins = input_options['OUTPUT_PINS']
    side_pin_states = input_options['SIDE_PIN_STATES']
    vector = input_options['VECTOR']
    vector_hash = {}
    if vector:
        for i in range(len(pin_list)):
            vector_hash[pin_list[i]] = vector[i]
    pins_with_assignments = list()
    for pin in pin_list:
        if pin in dont_touch_pins:
            continue
        if pin in when_pins:
            continue
        if pin in output_pins and input_options['CELL_NAME'
                                                ][:2] != 'MB' and pin[0] == 'Q':
            qpin_idx = pin_list.index(pin)
            if not is_q_vector_numeric(qpin_idx, vector):
                continue
        if pin == rel_pin:
            continue
        if pin == constr_pin:
            continue
        user_defined_side_pin = False
        for i in range(len(side_pin_states)):
            if pin == side_pin_states[i][0]:
                user_defined_side_pin = True
                break
        if user_defined_side_pin == True:
            continue
 
        if pin in vector_hash:
            if vector_hash[pin] == "0":
                pins_with_assignments.append((pin, '0'))
                continue
            elif vector_hash[pin] == "1":
                pins_with_assignments.append((pin, '1'))
                continue
        pins_with_assignments.append((pin, '1'))
    return pins_with_assignments
 
 
def getOutputLoadLines(input_options):
    output_pin_list = input_options['OUTPUT_PINS']
    dont_touch_pins = input_options['DONT_TOUCH_PINS']
    write_list = list()
    for pin in output_pin_list:
        #        if pin in dont_touch_pins:
        #            continue
        line = "C%s %s 0 'cl'" % (pin, pin)
        write_list.append(line)
    write_line = '\n'.join(write_list) + '\n'
    return write_line
 
 
def splitDollarNames(template_line):
    line_info = template_line.split('$')
    var_name_list = list()
    for item in line_info[1:]:
        var_name = item.split()[0].strip("'").strip(")").strip("(")
        var_name_list.append(var_name)
 
    return var_name_list
 
 
def fillTemplateLine(template_line, input_options):
    var_names = splitDollarNames(template_line)
    var_values = getDollarValues(var_names, input_options)
 
    is_negative = False
    if 'MEAS_DEGRADE_PER' in template_line and 'PUSHOUT_PER' in var_names:
        meas_item = template_line.split()[2]
        if float(var_values[0]) < 0:
            var_values[0] = var_values[0].strip('-')
            is_negative = True
 
    filled_line = fillValuesInLine(var_names, var_values, template_line) + '\n'
 
    if is_negative:
        filled_line = filled_line + '* MEAS_PUSHOUT_DIR ' + meas_item + ' | NEGATIVE\n'
 
    return filled_line
 
 
def getDollarValues(var_names, input_options):
    var_value_list = list()
    for item in var_names:
        var_value = getSingleFillValue(item, input_options)
        var_value_list.append(var_value)
    return var_value_list
 
 
def fillValuesInLine(var_names, var_values, template_line):
    filled_line = template_line.strip('\n')
    for count in range(0, len(var_names)):
        raw_name = var_names[count]
        dollar_name = "$%s" % raw_name
        dollar_value = var_values[count]
        filled_line = filled_line.replace(dollar_name, dollar_value)
    return filled_line
 
 
def old_fillValuesInLine(unfilled_line, fill_value_list):
    unfilled_line_info = unfilled_line.split('%s')
    filled_line_list = list()
    for count in range(0, len(unfilled_line_info) - 1):
        substr = unfilled_line_info[count]
        filled_line_list.append(substr)
        fill_value = fill_value_list[count]
        filled_line_list.append(fill_value)
    filled_line_list.append(unfilled_line_info[-1])
 
    filled_line = ''.join(filled_line_list)
    return filled_line
 
 
def parseFillSpecs(fill_names, input_options):
    fill_value_list = list()
    # Math evaluation
    if fill_names[0] == '[':
        fill_value = evaluateMathFillValue(fill_names, input_options)
        fill_value_list.append(fill_value)
 
    # Multiple values
    elif fill_names[0] == '(':
        fill_value_list = getMultipleFillValues(fill_names, input_options)
 
    # Single entry
    else:
        fill_value = getSingleFillValue(fill_names, input_options)
        fill_value_list.append(fill_value)
 
    return fill_value_list
 
 
def evaluateMathFillValue(math_fill_func, input_options):
    math_fill_info = math_fill_func[1:-1].split(' x ')
    prod_list = list()
    for item in math_fill_info:
        try:
            prod_list.append(float(item))
        except ValueError:
            variable_name = item
            variable_value = getSingleFillValue(variable_name, input_options)
            prod_list.append(float(variable_value))
    math_fill_value = product(prod_list)
    return str(math_fill_value)
 
 
def product(my_iterable):
    prod = 1
    for item in my_iterable:
        prod *= float(item)
    return prod
 
 
def getMultipleFillValues(fill_names, input_options):
    fill_name_list = [x.strip() for x in fill_names[1:-1].split(',')]
    fill_value_list = list()
    for fill_name in fill_name_list:
        if fill_name[0] == '[':
            fill_value = evaluateMathFillValue(fill_name, input_options)
        else:
            fill_value = getSingleFillValue(fill_name, input_options)
        fill_value_list.append(fill_value)
    return fill_value_list
 
 
def getSingleFillValue(fill_name, input_options):
    if fill_name not in input_options:
        print(
            "ERROR: Tried to fill template with option %s but it doesn't exist."
            % fill_name
        )
        sys.exit(0)
    else:
        fill_value = input_options[fill_name]
    return fill_value
 
 
def get_glitch_minq_line(template_line, arc_info):
    glitch_minq_line = template_line
    if '* MEAS_GLITCH_PER minq' in template_line or '* MEAS_GLITCH_PER glitch_minq' in template_line:
 
        vertical_bar_idx = template_line.index('|')
        metric_thresh = str(1 - float(arc_info['GLITCH']))
        glitch_minq_line = template_line[:vertical_bar_idx +
                                         1] + ' ' + metric_thresh + '\n'
    elif '.meas glitch_minq_check' in template_line or '.meas glitch_20_percent_minq_check' in template_line:
        try:
            greater_idx = template_line.index('>')
        except ValueError:
            print('-------glich sign incorret-------')
            print(
                '{template_name}'.format(
                    template_name=arc_info['TEMPLATE_DECK']
                )
            )
            print('---------------------------------')
            return template_line
        question_idx = template_line.index('?')
        metric_thresh = str(1 - float(arc_info['GLITCH']))
        glitch_minq_line = template_line[:greater_idx + 1
                                         ] + ' ' + metric_thresh + ' ' + template_line[
            question_idx:]
 
    elif '.meas tran minq' in template_line and 'goal=' in template_line:
        apostrophe_idx = template_line.index('\'')
        asterisk_idx = template_line.index('*')
        metric_thresh = str(arc_info['GLITCH'])
        glitch_minq_line = template_line[:apostrophe_idx + 1
                                         ] + ' ' + metric_thresh + template_line[
            asterisk_idx:]
 
    return glitch_minq_line
 
 
def get_glitch_maxq_line(template_line, arc_info):
    glitch_maxq_line = template_line
    if '* MEAS_GLITCH_PER maxq' in template_line or '* MEAS_GLITCH_PER maxq' in template_line:
        vertical_bar_idx = template_line.index('|')
        metric_thresh = str(arc_info['GLITCH'])
        glitch_maxq_line = template_line[:vertical_bar_idx +
                                         1] + ' ' + metric_thresh + '\n'
 
    elif '.meas glitch_maxq_check' in template_line or '.meas glitch_20_percent_maxq_check' in template_line:
        try:
            greater_idx = template_line.index('<')
        except ValueError:
            print('-------glich sign incorret-------')
            print(
                '{template_name}'.format(
                    template_name=arc_info['TEMPLATE_DECK']
                )
            )
            print('---------------------------------')
            return template_line
        question_idx = template_line.index('?')
        metric_thresh = str(float(arc_info['GLITCH']))
        glitch_maxq_line = template_line[:greater_idx + 1
                                         ] + ' ' + metric_thresh + ' ' + template_line[
            question_idx:]
 
    elif '.meas tran maxq' in template_line and 'goal=' in template_line:
        apostrophe_idx = template_line.index('\'')
        asterisk_idx = template_line.index('*')
        metric_thresh = str(arc_info['GLITCH'])
        glitch_maxq_line = template_line[:apostrophe_idx + 1
                                         ] + ' ' + metric_thresh + template_line[
            asterisk_idx:]
 
    return glitch_maxq_line
 
