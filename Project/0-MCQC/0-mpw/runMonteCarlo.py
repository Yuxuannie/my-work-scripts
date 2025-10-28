import datetime
import fnmatch
import os
import sys
import json
sys.path.insert(0, os.path.split(__file__)[0])  # noqa
 
import qaTemplateMaker.funcs as createQATemplate
import arcFilters.funcs as arcFilters
import spiceDeckMaker.funcs as spiceDeckMaker
import timingArcInfo.funcs as timingArcInfo
import charTemplateParser.funcs as templateParser
import runtime.funcs as runtimeEstimate
import hybrid_char_helper
 
from chartcl_helper.parser import ChartclParser
from chartcl_helper import sis_chartcl_helper
from pathlib import Path
 
 
def dump_ref(dic, name):
    print("\"%s\"" % name)
    print(json.dumps(dic, indent=4, separators=(',', ':')))
 
 
def printUserOptions(user_options):
    print("User options were defined as follows:")
    for opt in sorted(user_options.keys()):
        print(
            '\t{0:<30} {1:<5} {2:<100}'.format(
                opt, "::", str(user_options[opt])
            )
        )
 
 
def getPinIndices(table_point):
    point_info = table_point.strip('(').strip(')').split(',')
    index_1_index = point_info[0]
    index_2_index = point_info[1]
    return index_1_index, index_2_index
 
 
def templateParsing(user_options, slew_derate=1, chartcl_parser=None):
    # Template parsing
    print("Parsing template file")
    template_file = user_options['TEMPLATE_FILE']
    template_info = templateParser.parseTemplateFile(
        template_file, slew_derate, chartcl_parser)
    return template_info
 
 
def chartcl_parsing(user_options):
    print("Parsing chartcl file")
    chartcl_file = user_options['CHARTCL_FILE']
    chartcl_parser = ChartclParser(chartcl_file)
    chartcl_parser.parse_set_var()
    chartcl_parser.parse_condition_glitch()
    chartcl_parser.parse_condition_load()
    chartcl_parser.parse_condition_delay_degrade()
    chartcl_parser.set_cells = hybrid_char_helper.parse_chartcl_for_cells(
        chartcl_file)
    if 'sis' in Path(os.path.realpath(chartcl_file)).name:
        sis_vars = sis_chartcl_helper.parse_sis_vars(chartcl_file)
        chartcl_parser.set_cells = hybrid_char_helper.parse_sis_chartcl_for_cells(
            chartcl_file)
        for name, value in sis_vars.items():
            chartcl_parser.vars[name] = value
 
    return chartcl_parser
 
 
def arcExtraction(user_options, template_info):
    # Arc extraction and QA Template creation
    print("Extracting arcs")
    valid_arc_types = user_options['VALID_ARC_TYPES_LIST']
    cell_pattern_list = user_options['CELL_PATTERN_LIST']
 
    max_num_when = user_options['MAX_NUM_WHEN']
    template_deck_type = user_options['SPICE_DECK_FORMAT']
    chartcl_file = user_options['CHARTCL_FILE']
    qa_arcs, num_arcs_identified = createQATemplate.getQAArcCharacteristics(
        template_info,
        valid_arc_types,
        cell_pattern_list,
        template_deck_type,
        max_num_when=max_num_when,
        chartcl_file=chartcl_file
    )
    return qa_arcs
 
 
def spiceInfoCreation(user_options, qa_arcs, chartcl_parser=None, template_info=None):
    print("Extracting information for SPICE deck.")
    spice_info = dict()
    # SPICE info creation
    root_netlist_path = user_options['ROOT_NETLIST_PATH']
    table_points_list = user_options['TABLE_POINTS_LIST']
    vdd_value = user_options['VDD_VALUE']
    temperature = user_options['TEMPERATURE']
    waveform_file = user_options['WAVEFORM_FILE']
    include_file_lookup = user_options['INCLUDE_FILE_LOOKUP']
    pushout_per = user_options['PUSHOUT_PER']
    pushout_dir = user_options['PUSHOUT_DIR']
    chartcl_vars = chartcl_parser.vars
    chartcl_condtions = chartcl_parser.conditions
 
    for table_point in table_points_list:
        spice_info[table_point] = dict()
 
        index_1_index, index_2_index = getPinIndices(table_point)
 
        current_info = timingArcInfo.parseQACharacteristicsInfo(
            qa_arcs, root_netlist_path, index_1_index, index_2_index, vdd_value,
            temperature, waveform_file, include_file_lookup, pushout_per, pushout_dir,
            chartcl_vars, chartcl_condtions, user_options['TEMPLATE_FILE'], template_info
        )
 
        spice_info[table_point] = current_info
 
    return spice_info
 
 
def getOutputPathName(arc_info, table_point):
    arc_type = arc_info['ARC_TYPE'].lower()
    cell = arc_info['CELL_NAME']
    constr_pin = arc_info['CONSTR_PIN'].upper()
    constr_pin_dir = arc_info['CONSTR_PIN_DIR'].lower()
    rel_pin = arc_info['REL_PIN'].upper()
    rel_pin_dir = arc_info['REL_PIN_DIR'].lower()
    lit_when = arc_info['LIT_WHEN']
    table_point_str = '-'.join(table_point.strip('(').strip(')').split(','))
    if arc_info['INDEX_3_INDEX'] is not None:
        table_point_str += "-" + str(arc_info['INDEX_3_INDEX'] + 1)
 
    output_deck_name = '_'.join(
        [
            arc_type, cell, constr_pin, constr_pin_dir, rel_pin, rel_pin_dir,
            lit_when, table_point_str
        ]
    )
    return output_deck_name
 
 
def createNominalSpiceDeck(
    arc_info, table_point, template_deck_path, root_output_path
):
    template_deck_name = arc_info['TEMPLATE_DECK']
    template_deck = os.path.join(template_deck_path, template_deck_name)
    dt_pin_list = spiceDeckMaker.getDontTouchPins(template_deck)
    arc_info['DONT_TOUCH_PINS'] = dt_pin_list
    arc_info['TEMPLATE_DECK_PATH'] = os.path.join(
        template_deck_path, arc_info['TEMPLATE_DECK'])
    arc_info['HEADER_INFO'] = arc_info['HEADER_INFO'] + '\n' + \
        '* TEMPLATE_DECK_PATH ' + arc_info['TEMPLATE_DECK_PATH']
    nominal_buffer = spiceDeckMaker.getNominalSpiceDeckBuffer(
        template_deck, arc_info
    )
 
    output_pathname = getOutputPathName(arc_info, table_point)
 
    output_path = os.path.join(root_output_path, output_pathname)
    output_path = output_path + '_' + arc_info['VECTOR']
    createPath(output_path)
    nominal_deck = os.path.join(output_path, "nominal_sim.sp")
    spiceDeckMaker.writeFile(nominal_buffer, nominal_deck)
    #print("Wrote nominal deck to %s" % nominal_deck)
    return nominal_buffer, output_path
 
 
def createMCSpiceDeckFromNominalBuffer(
    nominal_buffer, output_path, num_samples
):
    mc_buffer = list()
    for line in nominal_buffer:
        if fnmatch.fnmatch(line, ".tran *"):
            newline = line.strip()
            if not "sweep" in newline:
                newline += " sweep"
            newline += " monte=%s\n" % num_samples
            mc_buffer.append(newline)
        else:
            mc_buffer.append(line)
 
    mc_deck = os.path.join(output_path, "mc_sim.sp")
    spiceDeckMaker.writeFile(mc_buffer, mc_deck)
    #print("Wrote MC spice deck to %s" % mc_deck)
 
 
def createPath(mypath):
    if not os.path.exists(mypath):
        os.makedirs(mypath)
        #print("Created path at %s" % mypath)
 
 
def getArcCSVFilterFile(user_options):
    try:
        arc_csv_filter_file = user_options['ARC_CSV_FILTER_FILE']
    except KeyError as _:
        arc_csv_filter_file = None
    return arc_csv_filter_file
 
 
def applyArcFilter(spice_info, arc_filter):
    for table_point in spice_info:
        for arc_num in spice_info[table_point]:
            arc_info = spice_info[table_point][arc_num]
            valid_arc = arcFilters.checkArcInFilter(
                table_point, arc_info, arc_filter
            )
 
            if not valid_arc:
                arc_info['VALID_ARC'] = False
            else:
                arc_info['VALID_ARC'] = True
 
 
def getCPUEstimate(spice_info):
    min_effort = 1e99
    deck_counter = 0
    for table_point in spice_info:
        for arc_num in spice_info[table_point]:
            arc_info = spice_info[table_point][arc_num]
            if arc_info['VALID_ARC'] is False:
                print("Filtered arc")
                continue
 
            nxtor, _ = runtimeEstimate.getXTORandPODECounts(
                arc_info['NETLIST_PATH']
            )
            current_effort = runtimeEstimate.getApproxEffort(nxtor)
 
            arc_info['APPROXIMATE_EFFORT'] = current_effort
            min_effort = min(current_effort, min_effort)
            deck_counter += 1
 
    runtimeEstimate.populateReqCPUs(spice_info, min_effort)
    lb_req_cpus, ub_req_cpus = runtimeEstimate.getReqCPURange(spice_info)
    lb_req_cpus += deck_counter
    ub_req_cpus += deck_counter
    return lb_req_cpus, ub_req_cpus, min_effort
 
 
def createSPICEdecks(
    spice_info, template_deck_path, root_output_path, num_samples,
    template_deck_type
):
    count = 0
    for table_point in spice_info:
        for arc_num in spice_info[table_point]:
            arc_info = spice_info[table_point][arc_num]
            if arc_info['VALID_ARC'] is False:
                print("Filtered arc")
                continue
            nominal_buffer, output_path = createNominalSpiceDeck(
                arc_info, table_point, template_deck_path, root_output_path
            )
            count += 1
            if template_deck_type.upper() == "THANOS":
                continue
 
            createMCSpiceDeckFromNominalBuffer(
                nominal_buffer, output_path, num_samples
            )
    return count
 
 
def main(user_options):
    arc_csv_filter_file = getArcCSVFilterFile(user_options)
    printUserOptions(user_options)
 
    start = datetime.datetime.now()
    chartcl_parser = chartcl_parsing(user_options)
    print("takes {time} s".format(time=datetime.datetime.now() - start))
    start = datetime.datetime.now()
    template_info = templateParsing(
        user_options, chartcl_parser.vars.get('slew_derate', '1'), chartcl_parser)
    print("takes {time} s".format(time=datetime.datetime.now() - start))
    start = datetime.datetime.now()
    chartcl_cells = chartcl_parser.set_cells
    if len(chartcl_cells) != 0:
        template_info._tcl_vars['cells'] = chartcl_cells
    qa_arcs = arcExtraction(user_options, template_info)
    print("takes {time} s".format(time=datetime.datetime.now() - start))
    spice_info = spiceInfoCreation(
        user_options, qa_arcs, chartcl_parser, template_info)
    arc_filter = arcFilters.createFilterFromCSVFile(arc_csv_filter_file)
 
    # Apply arc filter
    applyArcFilter(spice_info, arc_filter)
 
    if user_options['ESTIMATE_CPUS']:
        print("\n\n### COMPUTING CPU ESTIMATES ###")
        lb_req_cpus, ub_req_cpus, _ = getCPUEstimate(spice_info)
        print(
            "Estimated CPU range is %s-%s CPUs to finish SPICE simulations in 24 "
            "hours." % (lb_req_cpus, ub_req_cpus)
        )
 
    else:
        # Create spice decks
        root_output_path = user_options['ROOT_OUTPUT_PATH']
        num_samples = user_options['NUM_SAMPLES']
        template_deck_path = user_options['TEMPLATE_DECK_PATH']
        template_deck_type = user_options['SPICE_DECK_FORMAT']
        print("Creating SPICE decks")
        count = createSPICEdecks(
            spice_info, template_deck_path, root_output_path, num_samples,
            template_deck_type
        )
        print("Created %s paths with SPICE decks." % count)
 
    return spice_info
 
