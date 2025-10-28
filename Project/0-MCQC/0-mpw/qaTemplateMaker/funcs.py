import fnmatch
import re
 
from qaTemplateMaker.classes import ArcInfo
from qaTemplateMaker.chartcl_condition import generate_char_path, parse_condition_load, read_chartcl
import templateFileMap.funcs as templateFileMap
import fix_cklnenq
 
 
def getArcInfoLine(arc_info):
    """
    A function to create an entry in the QA Template file which represents the
    information necessary to fill in the template SPICE deck for a QA arc.
    This function is used to write a line in the QA template file which can be
    parsed later in a flow.
 
    Args:
        arc_info (ArcInfo): The dictionary representing the different attributes of the
        current arc of interest
    Returns:
        header_info (str): A string representing the different characteristics of the
        QA arc
    """
    cell_name = arc_info.cell()
    rel_pin = arc_info.relPin()
    rel_pin_dir = arc_info.relPinDir()
    constr_pin = arc_info.pin()
    constr_pin_dir = arc_info.pinDir()
    output_pins_list = arc_info.outputPinlist()
    output_pins_str = ' '.join(output_pins_list)
    probe_pins_list = arc_info.probeList()
    probe_pins_str = getProbePinsStr(probe_pins_list)
    when = arc_info.when()
    output_load = arc_info.outputLoad()
    template_pin_list = arc_info.cellPinlist()
    template_pin_str = ' '.join(template_pin_list)
    arc_type = arc_info.arcType()
    vector = arc_info.vector()
 
    header_info = ' | '.join(
        [
            "CELL %s" % cell_name,
            "REL_PIN %s" % rel_pin,
            "REL_PIN_DIR %s" % rel_pin_dir,
            "CONSTR_PIN %s" % constr_pin,
            "CONSTR_PIN_DIR %s" % constr_pin_dir,
            "OUTPUT_PINS %s" % output_pins_str,
            "%s" % probe_pins_str,
            "WHEN %s" % when,
            "OUTPUT_LOAD %s" % output_load,
            "TEMPLATE_PINLIST %s" % template_pin_str,
            "ARC_TYPE %s" % arc_type,
            "VECTOR %s" % vector
        ]
    )
    return header_info
 
 
def getSlewInfoLine(arc_info):
    """
    A function to get the line that contains the information about the slews for the
    current arc.
    This function is used to create the QA Template file
    Args:
        arc_info (ArcInfo): The dictionary that contains the information about the slews
        for the current arc
    Returns:
        slew_info (str): A string that contains the related pin slews,
        constrained pin slews, and the max slew all separated by the delimeter '|'
    """
    rel_pin_slew_list = arc_info.index_2()
    rel_pin_slew_str = ' '.join(rel_pin_slew_list)
    constr_pin_slew_list = arc_info.index_1()
    constr_pin_slew_str = ' '.join(constr_pin_slew_list)
    cons_cons_pin_slew_list = arc_info.constraint_define_template().index_1().split()
    cons_rel_pin_slew_list = arc_info.constraint_define_template().index_2().split()
    max_slew_str = getMaxSlew(cons_rel_pin_slew_list, cons_cons_pin_slew_list)
 
    slew_info = ' | '.join(
        [
            "REL_PIN_SLEWS %s" % rel_pin_slew_str,
            "CONSTR_PIN_SLEWS %s" % constr_pin_slew_str,
            "MAX_SLEW %s" % max_slew_str
        ]
    )
    return slew_info
 
 
def getTemplateDeckLine(arc_info):
    """
    A function that forms the line representing the name of the 'template deck' for
    the current arc.
    This function is used to help create the QA Template file.
 
    Args:
        arc_info (ArcInfo): The dictionary that contains information about the current arc
    Returns:
        template_deck_info (str): A string that represents the field for the
        "TEMPLATE_DECK" part of the current arc.
    """
    template_deck = arc_info.templateDeck()
 
    template_deck_info = ' | '.join(["TEMPLATE_DECK %s" % template_deck])
    return template_deck_info
 
 
def getMaxSlew(rel_pin_slew_list, constr_pin_slew_list):
    """
    A function that accepts both the related and constrained pin slews and computes
    the maximum slew value from the both of them.
    Args:
        rel_pin_slew_list (list): A list of strings representing the slews for the
        related pin
        constr_pin_slew_list (list): A list of strings representing the slews for the
        constrained pin
    Returns:
        max_slew_str (str): A string that represents the max slew out of the related
        and constrained pin slews
    """
    # Convert to floats to avoid rounding errors down the road then compute the max of
    # max slews
    rel_pin_slew_list_fl = [float(x) for x in rel_pin_slew_list]
    constr_pin_slew_list_fl = [float(x) for x in constr_pin_slew_list]
    max_rel_pin_slew_fl = max(rel_pin_slew_list_fl)
    max_constr_pin_slew_fl = max(constr_pin_slew_list_fl)
    max_slew_fl = max(max_rel_pin_slew_fl, max_constr_pin_slew_fl)
 
    # Explicitly look for the index of the float value and then pull the corresponding
    #  string to avoid any type of rounding errors
    if max_slew_fl in rel_pin_slew_list_fl:
        max_slew_index = rel_pin_slew_list_fl.index(max_slew_fl)
        max_slew_str = "%s" % rel_pin_slew_list[max_slew_index]
    else:
        max_slew_index = constr_pin_slew_list_fl.index(max_slew_fl)
        max_slew_str = "%s" % constr_pin_slew_list[max_slew_index]
    return max_slew_str
 
 
def getProbePinsStr(probe_list):
    """
    A function that creates the "PROBE_PIN_x" strings based on the probe pins in the
    input probe list.
    This function is created so we can individually mark the different probe pins and
    their string IDs (e.g., PROBE_PIN_1)
 
    Args:
        probe_list (list): A list (strings) of the probe points for the current arc
    Returns:
        probe_pin_str (str): A string that represents the different probe nodes and
        their probe IDs (e.g, PROBE_PIN_1, PROBE_PIN_2) which are separated by the
        deliemter '|'
    Examples:
        >> getProbePinsStr(["Q", "bl_b"])
        PROBE_PIN_1 Q | PROBE_PIN_2 bl_b
    """
    write_list = list()
    count = 1
    if probe_list is None:
        write_list = list()
    else:
        for probe_pin in probe_list:
            write_list.append("PROBE_PIN_%s %s" % (count, probe_pin))
            count += 1
    probe_pin_str = ' | '.join(write_list)
    return probe_pin_str
 
 
def skip_this_arc(cell, arc_when, cell_pinlist, vector, probe_list):
    splited_when = arc_when.strip('"').split('&')
    if 'CKLNQR' in cell or 'CKLHQR' in cell:
        if 'OV' in splited_when:
            return True
 
    if fix_cklnenq.is_cklnenq_notTEN(cell, splited_when):
        return True
    if '!CN' in splited_when:
        return True
    if 'CD' in splited_when or 'C' in splited_when:
        return True
    if 'SE' in splited_when or '!SI' in splited_when or '!SN' in splited_when or '!SA' in splited_when:
        return True
    if 'TE' in splited_when:
        return True
 
    if 'SDF' in cell and 'OR' in cell \
            and (('DA' in splited_when and '!DB' in splited_when)
                 or ('DB' in splited_when and '!DA' in splited_when)):
        return True
    if 'SDF' in cell and 'OA' in cell \
            and (('!DA' in splited_when and '!DA&!DB&DC&DD' not in arc_when)
                 or ('DA' in splited_when and 'DA&DB&DC&DD' not in arc_when)):
        return True
 
    if 'SDF' in cell and 'AO' in cell \
            and (('!DA' in splited_when and '!DA&DB&DC&!DD' not in arc_when)
                 or ('DA' in splited_when and 'DA&DB&DC&DD' not in arc_when)):
        return True
    if ('AN' in cell or 'DFM' in cell)\
            and (('!DA' in splited_when and '!DA&DB' not in arc_when)
                 or ('DA' in splited_when and 'DA&DB' not in arc_when)):
        return True
    if 'MB' in cell and 'ICG' in cell and 'CP' in cell_pinlist:
        CP_idx = cell_pinlist.index('CP')
        after_CP_vector = set([char for char in vector[CP_idx + 1:]])
        if len(after_CP_vector) == 1 and '0' in after_CP_vector:
            return True
    if is_rsdf(cell) and (
        'SAVE' in splited_when or '!NRESTORE' in splited_when
    ):
        return True
 
    if cell[:2] == 'MB' and probe_list is not None and probe_list[0] == 'clkb':
        True
    return False
 
 
def is_rsdf(cell):
    if cell.startswith('RSDF'):
        return True
    if cell.startswith('MB') and 'RSDF' in cell:
        return True
    return False
 
 
def getQAArcCharacteristics(
    template_info,
    valid_arc_types,
    cell_pattern_list,
    template_type,
    chartcl_file,
    max_num_when=1
):
    """
    A function that extracts the arc characteristics from the template information
    dictionary.
    Args:
        template_info (charTemplateParser.classes.TemplateInfo): The data
        structure storing the parsed template information
        valid_arc_types (list): A list of strings identifying the arc_types that are
        meant to be extracted
        cell_pattern_list (list): A list of strings identifying the cell patterns (
        strings w/ UNIX style wildcards) for the cells in the template we want to do
        QA for.
        max_num_when (int, default=1): An integer representing the maximum number of
        when conditions to store for different types of arcs
    Returns:
        arc_characteristics (dict): The dictionary which stores all of the
        characteristics for the arcs we want to do MC QA for
        num_arcs_identified (int): The number of arcs we were able to identify/understand
    """
    num_arcs_identified = 0
    arc_list = list()
    for cell_obj in template_info.getAllCells():
        # Common
        cell_name = cell_obj.name()
 
        # Skip if it is not a valid cell
        if not checkValidCell(
            cell_name, cell_pattern_list
        ) or cell_name not in template_info._tcl_vars['cells']:
            continue
 
        # Skip if we have no arcs in there
        if not cell_obj.nArcs():
            continue
 
        cell_pinlist = getCellPinlist(cell_obj)
        output_pinlist = getCellOutputPinlist(cell_obj)
        sorted_arc_list = getSortedArcList(cell_obj)
        existing_arcs = dict()
        constraint_template_name = cell_obj.constraint()
        constraint_define_template = template_info.getDefineTemplate(
            constraint_template_name)
        for arc_obj in sorted_arc_list:
            # Check if valid arc
            arc_type = getArcType(arc_obj)
            arc_when = arc_obj.when()
            pin, rel_pin, log_when, probe_list, vector = getArcAttributes(
                arc_obj
            )
            if '+' in arc_when:
                skip_binning = True
                for idx, when in enumerate(arc_when.split('+')):
                    when = when.strip('"').strip()
                    vector = arc_obj._vector
                    skip_binning = skip_binning and skip_this_arc(
                        cell_name, when, cell_pinlist, vector, probe_list
                    )
                    if idx == 0:
                        if skip_this_arc(
                            cell_name, when, cell_pinlist, vector, probe_list
                        ):
                            pin = arc_obj._pin
                            rel_pin = arc_obj._related_pin
                            pin_dir = getPinDir(pin, cell_pinlist, vector)
                            rel_pin_dir = getPinDir(
                                rel_pin, cell_pinlist, vector)
                            lit_when = parseLogicalWhenCondition(when)
                           # print(idx,arc_type+'_'+cell_name+'_'+pin +'_'+pin_dir+'_'+rel_pin+'_'+pin_dir+'_'+lit_when+'_*_'+vector)
 
                if not skip_binning:
                    arc_when = arc_when.split('+')[0].strip('"').strip()
                    arc_obj._when = arc_when
                else:
                    print('All Skip:', arc_type+'_'+cell_name+'_'+pin + '_' +
                          pin_dir+'_'+rel_pin+'_'+pin_dir+'_'+lit_when+'_*_'+vector)
                    continue
            else:
                if skip_this_arc(
                    cell_name, arc_when, cell_pinlist, arc_obj._vector, probe_list
                ):
                    continue
 
            pin, rel_pin, log_when, probe_list, vector = getArcAttributes(
                arc_obj
            )
            splited_when = arc_when.strip('"').split('&')
            if not checkValidArc(arc_type, valid_arc_types):
                continue
 
            # Common info
            index_1, index_2, index_3 = getIndexEntriesForArc(
                arc_obj, cell_obj, template_info
            )
 
            # Get load
            output_load = getCellOutputLoad(
                template_info, cell_obj, arc_obj, chartcl_file
            )
 
            # Get the attributes/conditions
            lit_when = parseLogicalWhenCondition(log_when)
 
            # Get pin and related pin directions
            pin_dir = getPinDir(pin, cell_pinlist, vector)
            rel_pin_dir = getPinDir(rel_pin, cell_pinlist, vector)
 
            # Get metric and metric_thresh
            metric = arc_obj.metric()
            metric_thresh = arc_obj.metric_thresh()
 
            # Get Vector
            vector = arc_obj.vector()
            if 'SYNC2' in arc_obj.cell() or 'SYNC3' in arc_obj.cell(
            ) or 'SYNC4' in arc_obj.cell() or 'SYNC1P5' in arc_obj.cell():
                if (rel_pin == 'CP' and rel_pin_dir == 'rise' and 'SYNC1P5' not in arc_obj.cell()) or \
                    ('SYNC1P5' in arc_obj.cell() and ((rel_pin == 'CP' and rel_pin_dir == 'fall') or
                                                      (rel_pin == 'CPN' and rel_pin_dir == 'rise')) and 'notSE' not in lit_when):
                    vector = vector[:-1] + '0'
                    if log_when.lower() == "no_condition":
                        side_pin_state = getSidePinState(
                            cell_pinlist, pin, rel_pin, vector
                        )
                    else:
                        side_pin_state = list()
 
                    template_deck = templateFileMap.mapCharacteristicsToTemplate(
                        cell_name=cell_name,
                        arc_type=arc_type,
                        pin=pin,
                        pin_dir=pin_dir,
                        rel_pin=rel_pin,
                        rel_pin_dir=rel_pin_dir,
                        probe_list=probe_list,
                        when=log_when,
                        template_type=template_type
                    )
 
                    # Check counts
                    if checkWhenCount(
                        arc_type, pin, rel_pin, vector, lit_when, max_num_when,
                        existing_arcs, template_deck
                    ):
                        continue
                    # Enhance for 3D constraint
                    if len(output_load) == 5:
                        for i in range(len(output_load)):
                            if i == 0 or i == 4:
                                continue
                            arc = createArcInfo(
                                cell_name, arc_type, pin, pin_dir, rel_pin,
                                rel_pin_dir, lit_when, probe_list,
                                cell_pinlist, output_pinlist, index_1.split(),
                                index_2.split(), i, output_load[i],
                                side_pin_state, template_deck, metric,
                                metric_thresh, vector, constraint_define_template
                            )
                            arc_list.append(arc)
                    else:
                        arc = createArcInfo(
                            cell_name, arc_type, pin, pin_dir, rel_pin,
                            rel_pin_dir, lit_when, probe_list,
                            cell_pinlist, output_pinlist, index_1.split(),
                            index_2.split(), None, output_load[0],
                            side_pin_state, template_deck, metric,
                            metric_thresh, vector, constraint_define_template
                        )
                        arc_list.append(arc)
                    if template_deck is not None:
                        num_arcs_identified += 1
                    vector = vector[:-1] + '1'
 
            if '!E' not in splited_when or '!TE' not in splited_when:
                if fix_cklnenq.is_cklnenq_EN(cell_name, splited_when):
                    pass
                elif ('CKLN' in arc_obj.cell() and rel_pin == 'CP' and rel_pin_dir == 'fall') or\
                        ('CKLH' in arc_obj.cell() and rel_pin == 'CPN' and rel_pin_dir == 'rise'):
                    vector = vector[:-1] + '0'
                    if log_when.lower() == "no_condition":
                        side_pin_state = getSidePinState(
                            cell_pinlist, pin, rel_pin, vector
                        )
                    else:
                        side_pin_state = list()
 
                    template_deck = templateFileMap.mapCharacteristicsToTemplate(
                        cell_name=cell_name,
                        arc_type=arc_type,
                        pin=pin,
                        pin_dir=pin_dir,
                        rel_pin=rel_pin,
                        rel_pin_dir=rel_pin_dir,
                        probe_list=probe_list,
                        when=log_when,
                        template_type=template_type
                    )
 
                    # Check counts
                    if checkWhenCount(
                        arc_type, pin, rel_pin, vector, lit_when, max_num_when,
                        existing_arcs, template_deck
                    ):
                        continue
                    # Enhance for 3D constraint
                    if len(output_load) == 5:
                        for i in range(len(output_load)):
                            if i == 0 or i == 4:
                                continue
                            arc = createArcInfo(
                                cell_name, arc_type, pin, pin_dir, rel_pin,
                                rel_pin_dir, lit_when, probe_list,
                                cell_pinlist, output_pinlist, index_1.split(),
                                index_2.split(), i, output_load[i],
                                side_pin_state, template_deck, metric,
                                metric_thresh, vector, constraint_define_template
                            )
                            arc_list.append(arc)
                    else:
                        arc = createArcInfo(
                            cell_name, arc_type, pin, pin_dir, rel_pin,
                            rel_pin_dir, lit_when, probe_list,
                            cell_pinlist, output_pinlist, index_1.split(),
                            index_2.split(), None, output_load[0],
                            side_pin_state, template_deck, metric,
                            metric_thresh, vector, constraint_define_template
                        )
                        arc_list.append(arc)
                    if template_deck is not None:
                        num_arcs_identified += 1
                    vector = vector[:-1] + '1'
            if arc_obj.cell()[:2] == 'MB':
                rel_pin_idx = cell_pinlist.index(rel_pin)
                after_rel_pin_vector = set(vector[rel_pin_idx + 1:])
                if 'x' in after_rel_pin_vector and len(
                    after_rel_pin_vector
                ) == 1 and probe_list[0] != 'clkb':
                    dpin_idx = get_dpin_idx(cell_pinlist, probe_list[0])
                    vector = vector[:dpin_idx] + '0' + vector[dpin_idx + 1:]
                    # if thereis no when condition, check if the user has specified states for the side pins
                    if log_when.lower() == "no_condition":
                        side_pin_state = getSidePinState(
                            cell_pinlist, pin, rel_pin, vector
                        )
                    else:
                        side_pin_state = list()
 
                    template_deck = templateFileMap.mapCharacteristicsToTemplate(
                        cell_name=cell_name,
                        arc_type=arc_type,
                        pin=pin,
                        pin_dir=pin_dir,
                        rel_pin=rel_pin,
                        rel_pin_dir=rel_pin_dir,
                        probe_list=probe_list,
                        when=log_when,
                        template_type=template_type
                    )
 
                    # Check counts
                    if checkWhenCount(
                        arc_type, pin, rel_pin, vector, lit_when, max_num_when,
                        existing_arcs, template_deck
                    ):
                        continue
                    # Enhance for 3D constraint
                    if len(output_load) == 5:
                        for i in range(len(output_load)):
                            if i == 0 or i == 4:
                                continue
                            arc = createArcInfo(
                                cell_name, arc_type, pin, pin_dir, rel_pin,
                                rel_pin_dir, lit_when, probe_list,
                                cell_pinlist, output_pinlist, index_1.split(),
                                index_2.split(), i, output_load[i],
                                side_pin_state, template_deck, metric,
                                metric_thresh, vector, constraint_define_template
                            )
                            arc_list.append(arc)
                    else:
                        arc = createArcInfo(
                            cell_name, arc_type, pin, pin_dir, rel_pin,
                            rel_pin_dir, lit_when, probe_list,
                            cell_pinlist, output_pinlist, index_1.split(),
                            index_2.split(), None, output_load[0],
                            side_pin_state, template_deck, metric,
                            metric_thresh, vector, constraint_define_template
                        )
                        arc_list.append(arc)
                    if template_deck is not None:
                        num_arcs_identified += 1
                    vector = vector[:dpin_idx] + '1' + vector[dpin_idx + 1:]
            # if thereis no when condition, check if the user has specified states for the side pins
            if log_when.lower() == "no_condition":
                side_pin_state = getSidePinState(
                    cell_pinlist, pin, rel_pin, vector
                )
            else:
                side_pin_state = list()
 
            template_deck = templateFileMap.mapCharacteristicsToTemplate(
                cell_name=cell_name,
                arc_type=arc_type,
                pin=pin,
                pin_dir=pin_dir,
                rel_pin=rel_pin,
                rel_pin_dir=rel_pin_dir,
                probe_list=probe_list,
                when=log_when,
                template_type=template_type
            )
            # Check counts
 
            if checkWhenCount(
                arc_type, pin, rel_pin, vector, lit_when, max_num_when,
                existing_arcs, template_deck
            ):
                continue
            # Enhance for 3D constraint
            if len(output_load) == 5:
                for i in range(len(output_load)):
                    if i == 0 or i == 4:
                        continue
                    arc = createArcInfo(
                        cell_name, arc_type, pin, pin_dir, rel_pin, rel_pin_dir,
                        lit_when, probe_list, cell_pinlist, output_pinlist,
                        index_1.split(), index_2.split(), i, output_load[i],
                        side_pin_state, template_deck, metric, metric_thresh,
                        vector, constraint_define_template
                    )
                    arc_list.append(arc)
            else:
                arc = createArcInfo(
                    cell_name, arc_type, pin, pin_dir, rel_pin, rel_pin_dir,
                    lit_when, probe_list, cell_pinlist, output_pinlist,
                    index_1.split(), index_2.split(), None, output_load[0],
                    side_pin_state, template_deck, metric, metric_thresh, vector, constraint_define_template
                )
                arc_list.append(arc)
            if template_deck is not None:
                num_arcs_identified += 1
            # else:
            #     print(arc_type+'_'+cell_name+'_'+pin +'_'+pin_dir+'_'+rel_pin+'_'+pin_dir+'_'+lit_when+'_*_'+vector)
    print("Extracted %s arcs" % num_arcs_identified)
    return arc_list, num_arcs_identified
 
 
def createArcInfo(
    cell_name, arc_type, pin, pin_dir, rel_pin, rel_pin_dir, when, probe_list,
    cell_pinlist, output_pinlist, index_1, index_2, index_3_idx, output_load,
    side_pin_state, template_deck, metric, metric_thresh, vector, constraint_define_template
):
    """
    A function that stores all of the current arc characteristics in a database.
 
    Args:
        cell_name (str): The cell name for the current arc
        arc_type (str): The arc type for the current arc
        pin (str): The name of the constrained pin for the current arc
        pin_dir (str): The direction of the constrained pin for the current arc
        rel_pin (str): The name of the related pin for the current arc
        rel_pin_dir (str): The direction of the related pin for the current arc
        when (str): The when condition for the current arc
        probe_list (list): A list (strings) of the probe points for the current arc
        cell_pinlist (list): A list (strings) of pins that correspond to the pinlist
        for the current cell for the current arc
        output_pinlist (list): Aarc_type,  list (strings) of pins that correspond to the output
        pins for the current cell for the current arc
        index_1 (list): A list (strings) of the slews corresponding to the
        constrained pin
        index_2 (list): A list (strings) of the slews corresponding to the
        related pin
        output_load (str): The output load for the current arc
        side_pin_state (list((str,str)): the pins specified by user in fixed states
        template_deck (str): The name of the template deck to use for the current arc
    Returns:
        arc (ArcInfo):
    """
 
    arc = ArcInfo(
        cell=cell_name,
        arc_type=arc_type,
        pin=pin,
        pin_dir=pin_dir,
        rel_pin=rel_pin,
        rel_pin_dir=rel_pin_dir,
        when=when,
        cell_pinlist=cell_pinlist,
        output_pinlist=output_pinlist,
        index_1=index_1,
        probe_list=probe_list,
        index_2=index_2,
        index_3_idx=index_3_idx,
        output_load=output_load,
        side_pin_states=side_pin_state,
        template_deck=template_deck,
        metric=metric,
        metric_thresh=metric_thresh,
        vector=vector,
        constraint_define_template=constraint_define_template
    )
    return arc
 
 
def parseLogicalWhenCondition(log_when):
    """
    A function to parse the logcail "when condition" of the current arc.
    This function transforms a when condition of the form "!SE&SI" to a string of the
    form "notSE_SI"
 
    Args:
        log_when (str): A logical representation of the when condition
    Returns:
        parsed_when (str): A literal representation of the when condition
    Examples:
        >> parseLogicalWhenCondition("!SE&SI")
        notSE_SI
    """
    when_list = list()
    when_info = log_when.split('&')
    for item in when_info:
        if item[0] == '!':
            lit_when = "not%s" % item[1:]
        else:
            lit_when = "%s" % item
        when_list.append(lit_when)
    parsed_when = '_'.join(when_list)
    return parsed_when
 
 
def checkWhenCount(
    arc_type, pin, rel_pin, vector, when, max_num_when, existing_arcs,
    template_deck
):
    """
    A function that checks whether the number of arcs with attributes representing the
    current arc were already stored in the QA arc characteristics data structure. If
    they were already stored and we have already hit the maximum number of "when"
    conditions for this type of arc, then don't store the current arc again.
 
    The purpose of this function is to avoid picking up the same type of arc with
    slightly different "when" conditions, e.g. CP->D with when1="!SE&SI" and
    when2="!SE&!SI".
 
    Args:
        arc_type (str): The arc_type of the current arc, e.g. 'hold'
        pin (str): The name of the pin for the current arc, e.g. 'D'
        rel_pin (str): The name of the related pin for the current arc, e.g. 'CP'
        vector (str): The vector for the current arc, e.g. 'RxxRxx'
        when (str): The when condition for the current arc
        max_num_when (int): The maximum number of when conditions to use per arc
        existing_arcs (dict): A dictionary of lists, whose keys are tuples of strings,
        that represents the arcs already stored.
        template_deck (str or None):
    Returns:
        count_reached (int): A variable that says whether the max number of when
        conditions for the current arc was reached (1) or not (0)
    """
 
    arc_tuple = (arc_type, pin, rel_pin, vector)
    num_when = 0
    if arc_tuple in existing_arcs:
        num_when = len(existing_arcs[arc_tuple])
        # Only add the when condition if we will create a SPICE deck
        if (not when
                in existing_arcs[arc_tuple]) and (template_deck is not None):
            existing_arcs[arc_tuple].append(when)
            num_when += 1
    else:
        # Only add the when condition if we will create a SPICE deck
        if template_deck is not None:
            existing_arcs[arc_tuple] = list()
            existing_arcs[arc_tuple].append(when)
            num_when = 1
 
    if num_when > max_num_when:
        count_reached = 1
    else:
        count_reached = 0
 
    return count_reached
 
 
def getCellPinlist(cell_obj):
    """
    A function that queries the Cell object to get the pinlist as it is defined in the
    template file
 
    Args:
        cell_obj (charTemplateParser.classes.Cell): The data structure storing the
        define_cell data
    Returns:
        cell_pinlist (list): A list of strings representing cell_name's pinlist
    Examples:
        >> getCellPinlist(cell_obj)
        ["CP", "D", "Q"]
    """
    return cell_obj.pinlist().split()
 
 
def getCellOutputPinlist(cell_obj):
    """
    A function that queries the Cell object to get the output pinlist as it is defined
    in the template file
 
    Args:
        cell_obj (charTemplateParser.classes.Cell): The data structure storing the
        define_cell data
    Returns:
        output_pinlist (list): A list of strings representing cell_name's output pins
    Examples:
        >> getCellOutputPinlist(cell_obj)
        ["Q"]
    """
    return cell_obj.output().split()
 
 
def getCellOutputLoad(
    template_info, cell_obj, arc_obj, chartcl_file, load_index=2
):
    """
    A function that queries the TemplateInfo data structure to get the input
    cell's output load, defaulting to the 3rd entry in the list, as it is defined in
    the template file.
    The function gets the name of the 'delay_template' for cell_name and
    cross-references the stored index_2 value for this delay template name; then,
    it extracts the 'load_index' entry of the index_2 list.
 
    Args:
        template_info (charTemplateParser.classes.TemplateInfo): The data structure
        storing the parsed template information
        cell_obj (charTemplateParser.classes.Cell): The data structure storing the
        define_cell data
        arc_obj (charTemplateParser.classes.Arc): The data structure storing the
        define_arc data
        load_index (int): The Python list entry of the output load to use (default = 2)
    Returns:
        output_load (str): The output load of cell_name
    Examples:
        >> getCellOutputLoad(template_info, cell_obj, arc_obj)
        0.00279
    """
    # Get the index2
    index_2 = ""
    if cell_obj.constraint() != None and re.search(
        '5x5x5', cell_obj.constraint()
    ):
        _, index_2, index_3 = getIndexEntriesForArc(
            arc_obj, cell_obj, template_info, arc_type="hold"
        )
    else:
        _, index_2, index_3 = getIndexEntriesForArc(
            arc_obj, cell_obj, template_info, arc_type="delay"
        )
 
 
#    _, index_2 = getIndexEntriesForArc(arc_obj, cell_obj, template_info,arc_type="delay")
    chartcl_content = read_chartcl(chartcl_file)
 
    # latch cell need change output load
    #    print("Cell OBJ %s" % cell_obj.name())
    #    print("ARC %s" %  arc_obj.type())
    output_load_change = parse_condition_load(chartcl_content)
 
    for bpat in output_load_change:
        if cell_obj.name() == bpat[0]:
            load_index = int(bpat[1])
            break
 
    # Get the load; default output load is 'index_2'. if constraint table is 3D table, output load is index_3
    output_load = []
    if cell_obj.constraint() != None and re.search(
        '5x5x5', cell_obj.constraint()
    ):
        output_load = [index_3.split()[i] for i in range(0, 5)]
    else:
        output_load.append(index_2.split()[load_index])
    return output_load
 
 
def getIndexEntriesForArc(arc_obj, cell_obj, template_info, arc_type=None):
    # Get arc_type if not specified
    if arc_type is None:
        arc_type = arc_obj.type()
    # Get the default index_1 and index_2
    # Constraint
    if arc_type in [
        "hold", "removal", "non_seq_hold", "setup", "recovery", "non_seq_setup",
        "nochange_low_low", "nochange_low_high", "nochange_high_low",
        "nochange_high_high"
    ]:
        template_name = cell_obj.constraint()
        override_list = getOverrideList(cell_obj, "constraint")
    # MPW
    elif arc_type in ["mpw", "min_pulse_width"]:
        override_list = getOverrideList(cell_obj, "mpw")
        template_name = cell_obj.mpw()
        if template_name is None:
            template_name = cell_obj.constraint()
 
    # SI
    elif arc_type in ["si_immunity"]:
        template_name = cell_obj.siImmunity()
        override_list = getOverrideList(cell_obj, "si_immunity")
 
    # Delay
    else:
        template_name = cell_obj.delay()
        override_list = getOverrideList(cell_obj, "delay")
 
    define_template = template_info.getDefineTemplate(template_name)
    index_1 = define_template.index_1()
    index_2 = define_template.index_2()
    index_3 = define_template.index_3()
 
    # Check if we are overriding
    pin = arc_obj.pin()
    related_pin = arc_obj.relatedPin()
    when = arc_obj.when()
 
    # First get all valid ones
    valid_define_index_list = getMatchingDefineIndexBlocks(
        override_list, pin, related_pin, when
    )
 
    # Get the best option
    n_index_1, n_index_2 = getOverridingDefineIndexBlock(
        valid_define_index_list, pin
    )
    # Override if necessary
 
    if n_index_1 is not None:
        index_1 = n_index_1
    if n_index_2 is not None:
        index_2 = n_index_2
 
    return index_1, index_2, index_3
 
 
def getMatchingDefineIndexBlocks(override_list, pin, related_pin, when):
    # Get the valid list first
    matching_indices = list()
    for define_index in override_list:
 
        # Init
        pin_match = True
        rel_pin_match = True
        when_match = True
 
        # '-pin' is always defined, it needs to match
        if pin not in define_index.pin().split() and define_index.pin().strip() != '*':
            pin_match = False
 
        # If there is a '-related_pin' in define_index, it needs to match
        if (define_index.relatedPin() is not None) and related_pin is not None:
            if re.search(r"\s+", define_index.relatedPin()):
                for rel_pin in define_index.relatedPin().split():
                    if fnmatch.fnmatch(related_pin, rel_pin):
                        rel_pin_match = True
                        break
                    rel_pin_match = False
            else:
                if not fnmatch.fnmatch(related_pin, define_index.relatedPin()):
                    rel_pin_match = False
 
        # If there is a '-when' in define_index, it needs to match
        if (define_index.when() is not None) and \
                (not fnmatch.fnmatch(when, define_index.when())):
            when_match = False
 
        if pin_match and rel_pin_match and when_match:
            matching_indices.append(define_index)
    return matching_indices
 
 
def getOverridingDefineIndexBlock(matching_list, pin):
    # Get best
    index_1 = None
    index_2 = None
 
    # Get matches (should only be 1 in each)
    exact_pin_match_list = []
    wildcard_pin_match_list = []
    for x in matching_list:
        xpins = x.pin().split()
        if pin in xpins:
            exact_pin_match_list.append(x)
        else:
            for xpin in xpins:
                if pin in xpin or xpin == '*':
                    wildcard_pin_match_list.append(x)
 
    if exact_pin_match_list:
        index_1 = exact_pin_match_list[0].index_1()
        index_2 = exact_pin_match_list[0].index_2()
    elif wildcard_pin_match_list:
        index_1 = wildcard_pin_match_list[0].index_1()
        index_2 = wildcard_pin_match_list[0].index_2()
 
    index_2 = index_1
    return index_1, index_2
 
 
def getOverrideList(cell_obj, override_type):
    """
    A function that gets the list of define_index blocks that may override an index value
    If a cell does not have any define_index blocks, it returns an empty list
    Args:
        cell_obj (charTemplateParser.classes.Cell): Data structure storing the
        define_cell data
        override_type (str): The type of template that may be overridden
    Returns:
        override_list (list): The list of define_index that may override
    """
 
    override_list = list()
    for x in cell_obj.getAllIndexOverrides():
        if x.type() == override_type:
            override_list.append(x)
    return override_list
 
 
def checkValidCell(cell_name, valid_cell_patterns_list):
    """
    A function to check whether the current cell (whose arcs are being extracted)
    matches the list of valid cell patterns for extraction.
    This function is used to filter out any unwanted cells, e.g. D2 size cells
 
    Args:
        cell_name (str): The name of the cell under examination
        valid_cell_patterns_list (list): The list of cell patterns (strings) which
        identify valid cells to be analyzed
    Returns:
        valid_cell (int): A variable marking the cell as valid (1) or invalid (0)
    Examples:
        >> checkValidCell("SDFQD1BWP360H10P66PD", ["*D1B*"])
        1
    """
 
    valid_cell = False
    for cell_pattern in valid_cell_patterns_list:
        if cell_pattern[0] != '*' and cell_pattern[-1] != '*':
            if cell_pattern == cell_name:
                valid_cell = True
                break
        elif cell_pattern[0] != '*' and cell_pattern[-1] == '*':
            if cell_pattern[0:-1] == cell_name[0:len(cell_pattern)-1]:
                valid_cell = True
                break
        elif cell_pattern[0] == '*' and cell_pattern[-1] != '*':
            start = len(cell_name) - len(cell_pattern[1:])
            if cell_pattern[1:] == cell_name[start:]:
                valid_cell = True
                break
        elif cell_pattern[0] == '*' and cell_pattern[-1] == '*':
            if cell_pattern[1:-1] in cell_name:
                valid_cell = True
                break
 
    return valid_cell
 
 
def getSortedArcList(cell_obj):
    """
    A function that returns a sorted version of the arc ID's for the input cell_name.
 
    Args:
        cell_obj (charTemplateParser.classes.Cell): Data structure storing the
        define_cell data
    Returns
        sorted_arc_list (list): A list of strings whose entries are the keys to the
        arcs attribute of the current cell
    Examples:
        >> getSortedArcList(template_info, "SDFQD1BWP360H10P66PD")
        ['arc_id_1', 'arc_id_2', 'arc_id_3', 'arc_id_4']
    """
    return cell_obj.arcList()
 
 
def checkValidArc(arc_type, valid_arc_types):
    """
    A function to check whether the current arc has an arc type that matches the list
    of valid arc types for extraction.
    This function is used to filter out any unwanted arc types, e.g. min_pulse_width arcs
 
    Args:
        arc_type (str): The arc_type of the current arc under analysis
        valid_arc_types (list): A list of arc types (strings) which identify valid
        arcs to be analyzed
    Returns:
        valid_arc (int): A variable marking the arc as valid (1) or invalid (0)
    Examples:
        >> checkValidArc("hold", ["hold", "removal"])
        1
    """
    # Include this map because there is no "delay" or "slew" type in the template.tcl
    # file, so we need to map it from a typical name into a template.tcl name
    # Transform
    valid_arc_types = set(valid_arc_types)
    if "delay" in valid_arc_types or "slew" in valid_arc_types:
        valid_arc_types.add("combinational")
        valid_arc_types.add("combinational_fall")
        valid_arc_types.add("combinational_rise")
        valid_arc_types.add("falling_edge")
        valid_arc_types.add("rising_edge")
        valid_arc_types.add("three_state_disable")
        valid_arc_types.add("three_state_enable")
        valid_arc_types.add("clear")
        valid_arc_types.add("preset")
 
    valid_arc = False
    if arc_type in valid_arc_types:
        valid_arc = True
 
    return valid_arc
 
 
def getArcType(arc_obj):
    """
    A function to get the arc's type
 
    Args:
        arc_obj (charTemplateParser.classes.Arc): The arc object
    Returns:
        arc_type (str): A string representing the arc type of the input arc ID
    Examples:
        >> getArcType(arc_obj)
        "hold"
    """
    return arc_obj.type()
 
 
def getArcAttributes(arc_obj):
    """
    A function to extract the various arc attributes such as the pin, related_pin,
    when condition, probes, and vector
 
    Args:
        arc_obj (charTemplateParser.classes.Arc): The data structure containing the
        define_arc information
    Returns:
        pin (str): The name of the "pin" for the current arc
        related_pin (str): The name of the "related pin" for the current arc
        when (str): The "when condition" for the current arc
        probe_list (list or None): The list of pins/nodes to probe for analysis.
        NOTE: probe_list will of None type if there is no 'probe' attribute for the
        current arc, e.g. for 'hidden' arcs
        vector (str): The input vector for the current arc
    Examples:
        >> getArcAttributes(arc_obj)
        D, CP, "NO_CONDITION", ["Q"], "RFx"
    """
    pin = arc_obj.pin()
    related_pin = arc_obj.relatedPin()
    when = arc_obj.when().strip('"').strip()
    vector = arc_obj.vector().strip()
    try:
        probe_list = arc_obj.probe().strip().split()
    except AttributeError as _:
        probe_list = None
    return pin, related_pin, when, probe_list, vector
 
 
def getPinDir(pin, pinlist, vector):
    """
    A function that extracts the direction of the input 'pin' variable from the input
    pinlist and vector variables.
    This function is used to determine the direction of the pin and related_pin for a
    given constraint arc.
    This function is also used to determine the state of a side pin for pins that are
    not defined in a "when" condition nor are pin or related_pin
 
    Args:
        pin (str): The name of the pin whose direction will be extracted
        pinlist (list): A list of strings that represent the pins of the cell for the
        current arc
        vector (str): A string representing the directions of the different pins of
        the pinlist, in the same order. Each pin can have 1 of 5 values: "x" (don't
        care), "R" (rise), "F" (fall), "1" (high) or "0" (low)
    Returns:
        pin_dir (str): A string representing the direction of the 'pin' variable
    Examples:
        >> getPinDir('D', ['D', 'CP', 'SE', 'SI'], 'RFxx')
        rise
    """
    pin_index = pinlist.index(pin)
    pin_dir_short = vector[pin_index]
    if pin_dir_short.lower() == 'r':
        pin_dir = "rise"
    elif pin_dir_short.lower() == 'f':
        pin_dir = "fall"
    elif pin_dir_short.lower() == '1':
        pin_dir = "high"
    elif pin_dir_short.lower() == '0':
        pin_dir = "low"
    else:
        pin_dir = None
    return pin_dir
 
 
def getSidePinState(pinlist, pin, rel_pin, vector):
    """
    A function that extracts the state of a side input pin from the vector defined by the user
    This function must be used only when there is  no_condition
 
    Args:
        pinlist (list(str)) all the pins defined for the cell
        pin (str) the pin
        rel_pin (str) the related pin
        vector (str): the user defined sequence of pin directions or states. pin and rel_pin
        are set to R or F, otehr pins defined by the when condition are set to "x". Side
        input pins with user defined states are set to 0 or 1 (no other state allowed)
    """
 
    side_pins = list()
    active_pins = 0
    inactive_pins = 0
    index = -1
    for pinname in pinlist:
        index = index + 1
        if pinname.lower() == pin.lower() or pinname.lower() == rel_pin.lower():
            # ignore this pin
            active_pins = active_pins + 1
        else:
            if vector[index] == '1':
                side_pins.append((pinname, 'high'))
            elif vector[index] == '0':
                side_pins.append((pinname, 'low'))
            else:
                inactive_pins = inactive_pins + 1
 
    return side_pins
 
 
def get_dpin_idx(pinlist, qpin):
    q_first_numeric_idx = get_first_numeric_idx(qpin)
    if q_first_numeric_idx != -1:
        for idx, pin in enumerate(pinlist):
            if pin[0] == 'D':
                d_first_numeric_idx = get_first_numeric_idx(pin)
                if pin[d_first_numeric_idx:] == qpin[q_first_numeric_idx:]:
                    return idx
 
 
def get_first_numeric_idx(pin):
    for i, char in enumerate(pin):
        if char.isnumeric():
            return i
    return -1
 
