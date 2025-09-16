import ldbx
import os
 
def get_cell_hierarchy_with_attributes(lib_path, cell_name):
 
    # Check if the file exists
    if not os.path.isfile(lib_path):
        print(f"Error: The file '{lib_path}' does not exist.")
        return {}
 
    try:
        # Read the library
        lib = ldbx.read_db(lib_path)
    except Exception as e:
        print(f"Error reading the library file: {str(e)}")
        return {}
   
 
 
    # Find the specified cell
    cell = lib.getChildren("cell", cell_name)
   
    if not cell:
        print(f"Cell '{cell_name}' not found in the library.")
        return {}
   
    def extract_hierarchy(group, indent=""):
        result = {}
       
        # Get group header and name
        header = group.getHeader()
        name = group.getName()
        group_key = f"{header}({name})" if name else f"{header}"
       
        # Get simple attributes
        simple_attrs = group.getAttr()
        for attr, value in simple_attrs:
            result[f"{attr} : {value};"] = None
 
        # Get complex attributes
        complex_attrs = group.getCAttr()
        for attr, values in complex_attrs:
            result[f"{attr}({', '.join(map(str, values))});"] = None
       
        # Recursively process child groups
        for child in group.getChildren():
            child_result = extract_hierarchy(child, indent + "  ")
            if child_result:
                result[child.getHeader() + ("(" + child.getName() + ")" if child.getName() else "")] = child_result
       
        return result
 
    # Start the recursive extraction from the cell
    hierarchy = {cell_name: extract_hierarchy(cell[0])}
   
    return hierarchy
 
def print_hierarchy(hierarchy, indent=""):
    for key, value in hierarchy.items():
        print(f"{indent}{key}")
        if isinstance(value, dict):
            print(f"{indent}{{")
            print_hierarchy(value, indent + "  ")
            print(f"{indent}}}")
        elif value is not None:
            print(f"{indent}  {value}")
 
 
# Example usage
lib_path = "/SIM/DFDS_20211231/Personal/rbpittu/Lib_char/N3EP/c230425_106a/sens_char_kits/c230705_103a_sdk/tcbn03ep_bwp143mh117l3p48cpd_base_elvt_c230705ssgnp_0p530v_m25c_cworst_T_sdk_new.lib"
cell_name = "AIOI21_NOM_D0P5_143MH117_L3_P48_EL"
 
cell_hierarchy = get_cell_hierarchy_with_attributes(lib_path, cell_name)
 
print(f"Hierarchy and attributes for cell '{cell_name}':")
print_hierarchy(cell_hierarchy)
 
