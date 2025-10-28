import glob
import os
import subprocess
 
import lineParser.funcs as line_parser
 
 
class Library(object):
    # Class attributes
 
    def __init__(self, lib_type, lgvt, corner, kit_path):
        self.lib_type = lib_type
        self.lgvt = lgvt
        self.corner = corner
        self.kit_path = kit_path
        self.valid_lib = False
        self.kit_template_file = None
        self.kit_include_file = None
        self.kit_char_file = None
        self.lib_output_path = None
        self.output_include_file = None
        self.vdd_value = None
        self.temper = None
        self.netlist_subdir = None
        self.script_output_path = None
        self.globals_file = None
 
 
def pygrep(in_file, pattern, count=1, proc_in=None):
    sys_cmd = ["bash", "-c", "grep -m %s '%s' %s" % (count, pattern, in_file)]
    if proc_in is None:
        proc = subprocess.Popen(sys_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stdin = proc.communicate(timeout=60)
    else:
        proc = subprocess.Popen(sys_cmd, stdin=proc_in.stdout, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        stdout, stdin = proc.communicate(timeout=60)
    return stdout, stdin
 
 
def getValidLibGenerator(lib_objs_list):
    """
    A function that returns a generator for the lib objects that are "valid libs"
    """
    valid_lib_gen = (lib_obj for lib_obj in lib_objs_list if lib_obj.valid_lib is True)
    return valid_lib_gen
 
 
def getUserLibraryCombinations(user_lib_file, user_star_file, user_exceptions_file):
    with open(user_lib_file, 'r') as f:
        user_lib_file_lines = f.readlines()
 
    user_stardict = parseUserStarFile(user_star_file)
    user_exceptions = parseUserExceptionsFile(user_exceptions_file)
 
    combinations = list()
    for input_line in user_lib_file_lines[1:]:
        line_combinations = line_parser.parseLine(input_line.strip(),
                                                  user_stardict,
                                                  user_exceptions)
 
        [combinations.append(x) for x in line_combinations]
 
    return combinations
 
 
def parseUserExceptionsFile(user_exceptions_file):
    with open(user_exceptions_file, 'r') as f:
        except_lines = f.readlines()
 
    except_dict = dict()
    except_list = [x.strip() for x in except_lines]
    except_dict['all'] = except_list
 
    return except_dict
 
 
def parseUserStarFile(user_star_file):
 
    with open(user_star_file, 'r') as f:
        star_file_lines = f.readlines()
 
    star_dict = dict()
    for line in star_file_lines:
        line_info = line.strip().split(',')
        var_type = line_info[0]
        var_val = line_info[1].split('"')[1].split()
 
        star_dict[var_type] = var_val
 
    return star_dict
 
 
def printKitLibTypes(lib_objs_list):
    print("The following library types were detected in the LVF kit:")
    a = [x.lib_type for x in lib_objs_list]
    print(list(set(a)))
 
 
def getLVFKitInfo(kit_path, user_lib_combos):
    lib_objs_list = createAvailLibObjs(kit_path)
    printKitLibTypes(lib_objs_list)
    filterLibObjs(lib_objs_list, user_lib_combos)
    printFinalLibraryInfo(lib_objs_list)
 
    # Get the template, char.tcl, and corner.inc files for each valid library
    valid_lib_objs_gen = getValidLibGenerator(lib_objs_list)
    for lib_obj in valid_lib_objs_gen:
        populateLibObjFilePaths(lib_obj)
 
    # Get the VDD value for each valid library
    valid_lib_objs_gen = getValidLibGenerator(lib_objs_list)
    for lib_obj in valid_lib_objs_gen:
        populateLibObjVDD(lib_obj)
 
    # Get the Temperature value for each valid library
    valid_lib_objs_gen = getValidLibGenerator(lib_objs_list)
    for lib_obj in valid_lib_objs_gen:
        populateLibObjTemper(lib_obj)
 
    # Get the Netlist subdirectory name (e.g., LPE_cworst_T_m25c) for each valid library
    valid_lib_objs_gen = getValidLibGenerator(lib_objs_list)
    for lib_obj in valid_lib_objs_gen:
        populateLibObjNetlistSubdirs(lib_obj)
 
    return lib_objs_list
 
 
def createAvailLibObjs(kit_path):
 
    lib_objs_list = list()
    available_libs = glob.glob(os.path.join(kit_path, "*/*/Char/*.inc"))
 
    for library in available_libs:
        subpath, corner_name = os.path.split(library)
        corner = corner_name.split('.inc')[0]
        subpath, char_name = os.path.split(subpath)
        subpath, lgvt = os.path.split(subpath)
        subpath, lib_type = os.path.split(subpath)
 
        libobj = Library(lib_type, lgvt, corner, kit_path)
        lib_objs_list.append(libobj)
 
    return lib_objs_list
 
 
def filterLibObjs(lib_objs_list, user_lib_combos):
    # Generator of user's combinations
    combos_gen = (formLibCombo(combination) for combination in user_lib_combos)
 
    # Iterate over items from the generator
    for lib_type, lib_lgvt, lib_corner in combos_gen:
        # Iterate over the library objects from the list of them
        for lib_obj in lib_objs_list:
            # Mark them as a valid library if their attributes match the combination
            if (lib_obj.lib_type == lib_type) and \
                (lib_obj.lgvt == lib_lgvt) and \
                (lib_corner in lib_obj.corner):
 
                lib_obj.valid_lib = True
 
 
def printFinalLibraryInfo(lib_objs_list):
    print("Found the following valid libraries.")
    for x in (lib_obj for lib_obj in lib_objs_list if lib_obj.valid_lib is True):
        print('{0:<10} {1:<10} {2:<40}'.format(x.lib_type, x.lgvt, x.corner))
 
 
def populateLibObjFilePaths(lib_obj):
    # Template
    template_file = getLibTemplateFile(lib_obj)
    if template_file is not None:
        lib_obj.kit_template_file = template_file
 
    # Char.tcl
    char_file = getLibCharFile(lib_obj)
    if char_file is not None:
        lib_obj.kit_char_file = char_file
 
    # Corner.inc
    inc_file = getLibIncFile(lib_obj)
    if inc_file is not None:
        lib_obj.kit_include_file = inc_file
 
 
def populateLibObjVDD(lib_obj):
    stdout, stdin = pygrep(lib_obj.kit_char_file, "set VOLT")
    lib_obj_vdd = stdout.decode().strip().split()[-1]
    lib_obj.vdd_value = lib_obj_vdd
 
 
def populateLibObjTemper(lib_obj):
    stdout, stdin = pygrep(lib_obj.kit_char_file, "set TEMP")
    lib_obj_temper = stdout.decode().strip().split()[-1]
    lib_obj.temper = lib_obj_temper
 
 
def populateLibObjNetlistSubdirs(lib_obj):
    stdout, stdin = pygrep(lib_obj.kit_char_file, "Netlist")
    netlist_subdir = os.path.dirname(stdout.decode().strip().split('Netlist/')[1])
    lib_obj.netlist_subdir = netlist_subdir
 
 
def getLibTemplateFile(lib_obj):
    try:
        template_file = glob.glob(os.path.join(lib_obj.kit_path, lib_obj.lib_type,
                                               lib_obj.lgvt, "Template",
                                               "*%s*.template.tcl" % lib_obj.corner))[0]
    except IndexError as _:
        print("Couldn't find a template file for library %s %s %s" % (
            lib_obj.lib_type, lib_obj.lgvt, lib_obj.corner))
        print("Marking this library as invalid.")
        lib_obj.valid_lib = False
        template_file = None
 
    return template_file
 
 
def getLibCharFile(lib_obj):
    try:
       char_file = glob.glob(os.path.join(lib_obj.kit_path, lib_obj.lib_type,
                                          lib_obj.lgvt, "Char", "char_%s.tcl" %
                                          lib_obj.corner))[0]
    except IndexError as _:
        print("Couldn't find a char file for library %s %s %s" % (
            lib_obj.lib_type, lib_obj.lgvt, lib_obj.corner))
        print("Marking this library as invalid.")
        lib_obj.valid_lib = False
        char_file = None
 
    return char_file
 
 
def getLibIncFile(lib_obj):
    try:
        inc_file = glob.glob(os.path.join(lib_obj.kit_path, lib_obj.lib_type,
                                          lib_obj.lgvt, "Char", "%s.inc" %
                                          lib_obj.corner))[0]
    except IndexError as _:
        print("Couldn't find an include file for library %s %s %s" % (
            lib_obj.lib_type, lib_obj.lgvt, lib_obj.corner))
        print("Marking this library as invalid.")
        lib_obj.valid_lib = False
        inc_file = None
 
    return inc_file
 
 
def formLibCombo(combination):
    lib_type = combination[0]
    lib_lg = combination[1]
    lib_vt = combination[2]
    lib_process = combination[3]
    raw_voltages = combination[4].split('_')
    lib_voltage = '_'.join(['p'.join(('%sv' % x).split('.')) for x in raw_voltages])
    raw_temper = combination[5]
    if float(raw_temper) < 0:
        lib_temper = "m%sc" % raw_temper[1:]
    else:
        lib_temper = "%sc" % raw_temper
 
    lib_lgvt = lib_lg + lib_vt
    lib_corner = "%s_%s_%s" % (lib_process, lib_voltage, lib_temper)
 
    return lib_type, lib_lgvt, lib_corner
 
 
