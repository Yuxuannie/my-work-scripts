def createFilterFromCSVFile(csv_filter_file):
    if csv_filter_file is None:
        arc_filter = None
    else:
        required_list = [
            "CELL", "ARC TYPE", "PIN", "PIN TRANSITION", "REL PIN",
            "REL PIN TRAN", "WHEN", "POINT"
        ]
        file_lines = getLines(csv_filter_file)
        header_info = parseHeader(file_lines[0], required_list)
 
        arc_filter = dict()
        for line in file_lines[1:]:
            updateArcFilter(line, header_info, arc_filter, required_list)
 
    return arc_filter
 
 
def getLines(csv_filter_file):
    with open(csv_filter_file, 'r') as f:
        file_lines = f.readlines()
    return file_lines
 
 
def parseHeader(header_line, required_list):
    header_info = dict()
    line_info = header_line.strip().split(',')
    for x in line_info:
        if x.upper() in required_list:
            header_info[x.strip().upper()] = line_info.index(x)
    return header_info
 
 
def updateArcFilter(line, header_info, arc_filter, required_list):
    if not len(list(arc_filter.keys())):
        current_index = 1
    else:
        max_index = max([int(x) for x in list(arc_filter.keys())])
        current_index = max_index + 1
 
    arc_filter[current_index] = dict()
    line_info = line.strip().split(',')
 
    for att_name in required_list:
        att_index = header_info[att_name]
        temp_att_value = line_info[att_index].strip()
        if att_name == "ARC TYPE":
            att_value = temp_att_value.split('_')[0]
        elif att_name == "POINT":
            point_values = temp_att_value.split(';')
            att_value = "(%s,%s)" % (point_values[0], point_values[1])
        else:
            att_value = temp_att_value
 
        arc_filter[current_index][att_name] = att_value
 
 
def checkArcInFilter(arc_point, arc_info, arc_filter):
    if arc_filter is None:
        valid_arc = 1
    else:
        arc_cell = arc_info['CELL_NAME']
        arc_type = arc_info['ARC_TYPE']
        arc_pin = arc_info['CONSTR_PIN']
        arc_pin_tran = arc_info['CONSTR_PIN_DIR']
        arc_rel_pin = arc_info['REL_PIN']
        arc_rel_pin_tran = arc_info['REL_PIN_DIR']
        arc_log_when = arc_info['WHEN']
 
        valid_arc = 0
        for filter_index, filter_info in arc_filter.items():
            # If the points don't match, break immediately
            filter_point = filter_info['POINT']
            if not arc_point == filter_point:
                break
 
            filter_cell = filter_info['CELL']
            filter_type = filter_info['ARC TYPE']
            filter_pin = filter_info['PIN']
            filter_pin_tran = filter_info['PIN TRANSITION']
            filter_rel_pin = filter_info['REL PIN']
            filter_rel_pin_tran = filter_info['REL PIN TRAN']
            filter_log_when = arc_info['WHEN']
 
            # If everything matches, don't consider other arcs
            if (arc_cell == filter_cell) and \
                    (arc_type == filter_type) and \
                    (arc_pin == filter_pin) and \
                    (arc_pin_tran == filter_pin_tran) and \
                    (arc_rel_pin == filter_rel_pin) and \
                    (arc_rel_pin_tran == filter_rel_pin_tran) and \
                    (arc_log_when == filter_log_when):
                valid_arc = 1
                break
 
    return valid_arc
 
