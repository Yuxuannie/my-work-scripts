"""
This module contains functions to parse the output of the QA template (either file or
python data structure), take some other user inputs and return a "spice deck info"
data structure.
 
The spice deck info data structure can then be filtered (specific points from a cell,
specific arcs, random cell, etc.) for use down the flow.
"""
 
import fnmatch
import os
import qaTemplateMaker.funcs as createQATemplate
 
 
def parseQACharacteristicsInfo(arc_list, root_netlist_path,
                               index_1_index, index_2_index, vdd_value,
                               temperature, waveform_file, include_file_lookup, pushout_per,
                               pushout_dir, chartcl_vars=None, chartcl_condtions=None, template_info=None):
 
    spice_deck_info = dict()
    arc_count = 0
    for arc in arc_list:
        if arc.templateDeck() is None:
            continue
 
        addKeyToDict(spice_deck_info, arc_count)
        arc_type = arcCharacteristics__getArcType(arc)
        spice_deck_info[arc_count]['ARC_TYPE'] = arc_type
        try:
            if arc_type in ('min_pulse_width', 'mpw'):
                tmp_arc_type = 'mpw'
            elif arc_type.startswith('nochange'):
                tmp_arc_type = 'nochange'
            elif arc_type in ('combinational', 'edge'):
                tmp_arc_type = 'delay'
            else:
                tmp_arc_type = arc_type
 
            if tmp_arc_type not in include_file_lookup and len(include_file_lookup) == 1:
                include_file = include_file_lookup['traditional']
            else:
                include_file = include_file_lookup[tmp_arc_type]
        except KeyError:
            raise ValueError(
                'Can NOT find matched %s .inc file, Please check char tcl.' % arc_type)
 
        template_deck = arcCharacteristics__getTemplateDeck(arc)
        spice_deck_info[arc_count]['TEMPLATE_DECK'] = template_deck
 
        header_info = arcCharacteristics__getHeaderInfo(arc)
        spice_deck_info[arc_count]['HEADER_INFO'] = header_info
 
        cell_name = arcCharacteristics__getCellName(arc)
        spice_deck_info[arc_count]['CELL_NAME'] = cell_name
 
        netlist_path = getNetlistPath(root_netlist_path, cell_name)
        spice_deck_info[arc_count]['NETLIST_PATH'] = netlist_path
 
        rel_pin = arcCharacteristics__getRelPin(arc)
        spice_deck_info[arc_count]['REL_PIN'] = rel_pin
 
        rel_pin_dir = arcCharacteristics__getRelPinDir(arc)
        spice_deck_info[arc_count]['REL_PIN_DIR'] = rel_pin_dir
 
        constr_pin = arcCharacteristics__getConstrPin(arc)
        spice_deck_info[arc_count]['CONSTR_PIN'] = constr_pin
 
        constr_pin_dir = arcCharacteristics__getConstrPinDir(arc)
        spice_deck_info[arc_count]['CONSTR_PIN_DIR'] = constr_pin_dir
 
        output_pins = arcCharacteristics__getOutputPins(arc)
        spice_deck_info[arc_count]['OUTPUT_PINS'] = output_pins
 
        side_pin_states = arcCharacteristics__getSidePinStates(arc)
        spice_deck_info[arc_count]['SIDE_PIN_STATES'] = side_pin_states
 
        # Store probe pins directly
        arcCharacteristics__storeProbePins(arc, spice_deck_info[arc_count],
                                           output_pins)
 
        log_when, lit_when = arcCharacteristics__getLogWhen(arc)
        spice_deck_info[arc_count]['WHEN'] = log_when
        spice_deck_info[arc_count]['LIT_WHEN'] = lit_when
 
        output_load = arcCharacteristics__getOutputLoad(arc)
        spice_deck_info[arc_count]['OUTPUT_LOAD'] = output_load
 
        template_pinlist_str = arcCharacteristics__getTemplatePinlistStr(arc)
        spice_deck_info[arc_count]['TEMPLATE_PINLIST'] = template_pinlist_str
 
        max_slew = arcCharacteristics__getMaxSlew(arc)
        spice_deck_info[arc_count]['MAX_SLEW'] = max_slew
 
        netlist_pins_str = getNetlistPinsStr(netlist_path)
        spice_deck_info[arc_count]['NETLIST_PINS'] = netlist_pins_str
 
        # Constr pin slew for constraints
        spice_deck_info[arc_count]['INDEX_1_INDEX'] = index_1_index
        index_1_value = arcCharacteristics__getIndex1Value(arc, index_1_index)
        spice_deck_info[arc_count]['INDEX_1_VALUE'] = index_1_value
 
        # Related pin slew for constraints
        spice_deck_info[arc_count]['INDEX_2_INDEX'] = index_2_index
        index_2_value = arcCharacteristics__getIndex2Value(arc, index_2_index)
        spice_deck_info[arc_count]['INDEX_2_VALUE'] = index_2_value
 
        # Enhance for 3D constraint
        spice_deck_info[arc_count]['INDEX_3_INDEX'] = arc.index_3_idx()
 
        spice_deck_info[arc_count]['VDD_VALUE'] = "%s" % vdd_value
        spice_deck_info[arc_count]['TEMPERATURE'] = "%s" % temperature
        spice_deck_info[arc_count]['WAVEFORM_FILE'] = "%s" % waveform_file
        spice_deck_info[arc_count]['INCLUDE_FILE'] = "%s" % include_file
        spice_deck_info[arc_count]['PUSHOUT_PER'] = "%s" % pushout_per
        spice_deck_info[arc_count]['PUSHOUT_DIR'] = "%s" % pushout_dir
 
        # Enhance for constraint metric measurement
        if 'constraint_glitch_peak' in chartcl_vars:
            spice_deck_info[arc_count]['GLITCH'] = chartcl_vars['constraint_glitch_peak']
 
        elif 'amd_glitch' in chartcl_vars:
            if 'hold' in arc_type:
                if is_glitch_cell(cell_name, chartcl_vars['amd_glitch']['cells']):
                    spice_deck_info[arc_count]['GLITCH'] = chartcl_vars['amd_glitch']['cell_glitch']
                else:
                    spice_deck_info[arc_count]['GLITCH'] = chartcl_vars['amd_glitch']['hold_glitch']
            else:
                spice_deck_info[arc_count]['GLITCH'] = chartcl_vars['amd_glitch']['default_glitch']
 
        if 'constraint_delay_degrade' in chartcl_vars:
            spice_deck_info[arc_count]['PUSHOUT_PER'] = chartcl_vars['constraint_delay_degrade']
        elif 'smc_degrade' in chartcl_vars:
            spice_deck_info[arc_count]['PUSHOUT_PER'] = chartcl_vars['smc_degrade']
 
        if arc.cell() in chartcl_condtions and 'GLITCH' in chartcl_condtions[arc.cell()]:
            spice_deck_info[arc_count]['GLITCH'] = chartcl_condtions[arc.cell(
            )]['GLITCH']
 
        if arc.metric_thresh() is not None:
            split_metric = list(map(str.strip, arc.metric().split()))
            split_metric_thresh = list(
                map(str.strip, arc.metric_thresh().split()))
 
            if 'glitch' in split_metric:
                idx = split_metric.index('glitch')
                spice_deck_info[arc_count]['GLITCH'] = split_metric_thresh[idx]
 
            if 'constraint_delay_degrade' in split_metric:
                idx = split_metric.index('constraint_delay_degrade')
                if str(split_metric_thresh[idx]) != '0':
                    spice_deck_info[arc_count]['PUSHOUT_PER'] = split_metric_thresh[idx]
        for key, val in template_info._sis_template.items():
            spice_deck_info[arc_count][key] = val
 
        # Enhance for vector
        spice_deck_info[arc_count]['VECTOR'] = arc.vector()
        arc_count += 1
 
    return spice_deck_info
 
 
def is_glitch_cell(cell, glitch_cells):
    from qaTemplateMaker.funcs import checkValidCell
    return checkValidCell(cell, glitch_cells)
 
 
def arcCharacteristics__getArcType(arc_info):
    """
 
    Args:
        arc_info (qaTemplateMaker.classes.ArcInfo):
    """
    arc_type = arc_info.arcType()
    return arc_type
 
 
def arcCharacteristics__getTemplateDeck(arc_info):
    """
 
    Args:
        arc_info (qaTemplateMaker.classes.ArcInfo):
    """
    template_deck = arc_info.templateDeck()
    return template_deck
 
 
def arcCharacteristics__getHeaderInfo(arc_info):
    """
 
    Args:
        arc_info (qaTemplateMaker.classes.ArcInfo):
    """
    arc_info_line = "* " + createQATemplate.getArcInfoLine(arc_info)
    slew_info_line = "* " + createQATemplate.getSlewInfoLine(arc_info)
    template_deck_info_line = "* " + \
        createQATemplate.getTemplateDeckLine(arc_info)
    header_line = '\n'.join(
        [arc_info_line, slew_info_line, template_deck_info_line])
    return header_line
 
 
def arcCharacteristics__getCellName(arc_info):
    """
 
    Args:
        arc_info (qaTemplateMaker.classes.ArcInfo):
    """
    cell_name = arc_info.cell()
    return cell_name
 
 
def arcCharacteristics__getRelPin(arc_info):
    """
 
    Args:
        arc_info (qaTemplateMaker.classes.ArcInfo):
    """
    rel_pin = arc_info.relPin()
    return rel_pin
 
 
def arcCharacteristics__getRelPinDir(arc_info):
    """
 
    Args:
        arc_info (qaTemplateMaker.classes.ArcInfo):
    """
    rel_pin_dir = arc_info.relPinDir()
    return rel_pin_dir
 
 
def arcCharacteristics__getConstrPin(arc_info):
    """
 
    Args:
        arc_info (qaTemplateMaker.classes.ArcInfo):
    """
    constr_pin = arc_info.pin()
    return constr_pin
 
 
def arcCharacteristics__getConstrPinDir(arc_info):
    """
 
    Args:
        arc_info (qaTemplateMaker.classes.ArcInfo):
    """
    constr_pin_dir = arc_info.pinDir()
    return constr_pin_dir
 
 
def arcCharacteristics__getSidePinStates(arc_info):
    """
 
    Args:
        arc_info (qaTemplateMaker.classes.ArcInfo):
    """
    side_pin_states = arc_info.sidePinStates()
    return side_pin_states
 
 
def arcCharacteristics__getOutputPins(arc_info):
    """
 
    Args:
        arc_info (qaTemplateMaker.classes.ArcInfo):
    """
    output_pins_list = arc_info.outputPinlist()
    return output_pins_list
 
 
def arcCharacteristics__storeProbePins(arc_info, spice_deck_info, output_pins):
    """
 
    Args:
        arc_info (qaTemplateMaker.classes.ArcInfo):
    """
    count = 1
    if arc_info.probeList() is None:
        for probe_pin in output_pins:
            spice_deck_info["PROBE_PIN_%s" % count] = probe_pin
            count += 1
    else:
        for probe_pin in arc_info.probeList():
            if probe_pin in output_pins:
                spice_deck_info["PROBE_PIN_%s" % count] = probe_pin
            else:
                spice_deck_info["PROBE_PIN_%s" % count] = "X1.%s" % probe_pin
            count += 1
 
 
def arcCharacteristics__getLogWhen(arc_info):
    """
 
    Args:
        arc_info (qaTemplateMaker.classes.ArcInfo):
    """
    lit_when = arc_info.when()
    log_when = arc_info.log_when()
    return log_when, lit_when
 
 
def arcCharacteristics__getOutputLoad(arc_info):
    """
 
    Args:
        arc_info (qaTemplateMaker.classes.ArcInfo):
    """
    output_load = arc_info.outputLoad()
    output_load += 'p'
    return output_load
 
 
def arcCharacteristics__getTemplatePinlistStr(arc_info):
    """
 
    Args:
        arc_info (qaTemplateMaker.classes.ArcInfo):
    """
    template_pinlist = arc_info.cellPinlist()
    template_pinlist_str = ' '.join(template_pinlist)
    return template_pinlist_str
 
 
def arcCharacteristics__getMaxSlew(arc_info):
    """
 
    Args:
        arc_info (qaTemplateMaker.classes.ArcInfo):
    """
    rel_pin_slew_list = arc_info.index_2()
    constr_pin_slew_list = arc_info.index_1()
    max_slew = createQATemplate.getMaxSlew(
        rel_pin_slew_list, constr_pin_slew_list)
    max_slew += "n"
    return max_slew
 
 
def arcCharacteristics__getIndex1Value(arc_info, constr_pin_index):
    """
 
    Args:
        arc_info (qaTemplateMaker.classes.ArcInfo):
    """
    constr_pin_slew_list = arc_info.index_1()
    constr_pin_slew = constr_pin_slew_list[int(constr_pin_index)-1]
    constr_pin_slew += 'n'
    return constr_pin_slew
 
 
def arcCharacteristics__getIndex2Value(arc_info, rel_pin_index):
    """
 
    Args:
        arc_info (qaTemplateMaker.classes.ArcInfo):
    """
    rel_pin_slew_list = arc_info.index_2()
    rel_pin_slew = rel_pin_slew_list[int(rel_pin_index)-1]
 
    # If non-constraint arc, it's a load
    delay_arc_types = ["combinational",
                       "combinational_fall", "combinational_rise",
                       "falling_edge", "rising_edge",
                       "three_state_disable", "three_state_enable",
                       "clear", "preset", "edge"]
    if arc_info.arcType() in delay_arc_types:
        rel_pin_slew += 'p'
    else:
        rel_pin_slew += 'n'
    return rel_pin_slew
 
 
def getNetlistPinsStr(netlist_path):
    with open(netlist_path) as f:
        netlist_lines = f.readlines()
 
    subckt_header = ".subckt*"
    netlist_pins_str = ''
 
    for line in netlist_lines:
        if fnmatch.fnmatch(line.lower(), subckt_header):
            split_line = line.strip().split()
            netlist_pins = split_line[2:]
            netlist_pins_str = ' '.join(netlist_pins)
            break
 
    return netlist_pins_str
 
 
def getNetlistPath(root_netlist_path, cell_name):
    # Search for different versions of LPE netlist
    # Compacted QA
    netlist_path = os.path.join(root_netlist_path, "%s_c_qa.spi" % cell_name)
    if not os.path.exists(netlist_path):
        # QA
        netlist_path = os.path.join(root_netlist_path, "%s_c.spi" % cell_name)
        if not os.path.exists(netlist_path):
            # Original
            netlist_path = os.path.join(
                root_netlist_path, "%s.spi" % cell_name)
 
    return netlist_path
 
 
def addKeyToDict(mydict, mykey):
    if not mykey in mydict:
        mydict[mykey] = dict()
 
 
