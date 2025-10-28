import os
import re
 
 
class ChartclParser:
    def __init__(self, filepath=None):
        self.filepath = filepath
        self.filename = os.path.split(filepath)
        self.vars = dict()
        self.conditions = dict()
        self.set_cells = []
 
        self.content_lines = None
        self.content_raw = None
        self.load()
 
    def load(self):
        with open(self.filepath, 'r') as f:
            self.content_lines = f.readlines()
        with open(self.filepath, 'r') as f:
            self.content_raw = f.read()
 
    def parse_set_var(self):
        for line in self.content_lines:
            if 'cell setting depend on' in line:
                break
            if 'set_var constraint_glitch_peak ' in line or 'set_var -stage variation constraint_delay_degrade ' in line\
                    or line.startswith('set_var mpw_input_threshold'):
                splited = line.split()
                var_name = splited[-2]
                var_value = splited[-1]
                self.vars[var_name] = var_value
            elif 'set_var constraint_glitch_peak ' in line or 'set_var constraint_delay_degrade ' in line\
                    or line.startswith('set_var mpw_input_threshold'):
                splited = line.split()
                var_name = splited[1]
                var_value = splited[2]
                self.vars[var_name] = var_value
            elif 'set_var constraint_output_load ' in line:
                splited = line.split()
                var_name = splited[1]
                var_value = splited[2]
                self.vars[var_name] = var_value.replace('index_', '')
 
    def parse_condition_load(self):
        condition = 'if.{0,50}{.{0,10}string compare.{0,10}"(\w{0,50})".{0,50}constraint_output_load.{0,10}index_(\w{0,2})'
 
        for cell, index in re.findall(
            condition, self.content_raw, flags=re.DOTALL
        ):
            if cell not in self.conditions:
                self.conditions[cell] = dict()
                self.conditions[cell]['OUTPUT_LOAD'] = index
            else:
                self.conditions[cell]['OUTPUT_LOAD'] = index
 
    def parse_condition_glitch(self):
        condition = 'if.{0,50}{.{0,10}string compare.{0,10}"(\w{0,50})".{0,50}constraint_glitch_peak ([0-9\.\-\+e]{0,4})'
        for cell, value in re.findall(
            condition, self.content_raw, flags=re.DOTALL
        ):
            if cell not in self.conditions:
                self.conditions[cell] = dict()
                self.conditions[cell]['GLITCH'] = value
            else:
                self.conditions[cell]['GLITCH'] = value
 
    def parse_condition_delay_degrade(self):
        condition = 'if.{0,50}{.{0,10}string compare.{0,10}"(\w{0,50})".{0,50}constraint_delay_degrade ([0-9\.\-\+e]{0,4})'
        for cell, value in re.findall(
            condition, self.content_raw, flags=re.DOTALL
        ):
            if cell not in self.conditions:
                self.conditions[cell] = dict()
                self.conditions[cell]['PUSHOUT_PER'] = value
            else:
                self.conditions[cell]['PUSHOUT_PER'] = value
 
