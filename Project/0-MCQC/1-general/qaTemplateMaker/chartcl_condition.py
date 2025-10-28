import os
import re
 
def generate_char_path(template_path):
    splited = os.path.split(template_path)
    basepath = splited[0].replace('Template', 'Char')
    template_name = splited[1]
    pvt = find_pvt(template_name)
    return os.path.normpath(os.path.join(basepath, 'char_'+pvt+'.tcl'))
 
def find_pvt(template_name):
    pvt_pattern = 'c\d+([a-zA-Z]+\w*).template'
    found = re.search(pvt_pattern, template_name)
    if found is None:
        raise Exception("Cant find pvt from template name")
    return found.group(1)
 
def read_chartcl(filepath):
    content = None
    with open(filepath, 'r') as f:
        content = f.read()
    return content
 
def parse_condition_load(content):
    condition = 'if.{0,50}{.{0,10}string compare.{0,10}"(\w{0,50})".{0,50}constraint_output_load.{0,10}index_(\w{0,2})'
    return re.findall(condition, content, flags=re.DOTALL)
 
