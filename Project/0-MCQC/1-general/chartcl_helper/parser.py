import os
import re
 
 
class ChartclParser:
    def __init__(self, filepath=None):
        self.filepath = filepath
        self.filename = os.path.split(filepath)
        self.vars = dict()
        self.conditions = dict()
        self.amd_glitch = dict()
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
        for line in self.content_lines[::-1]:
            if 'constraint_glitch_peak' in self.vars and 'constraint_delay_degrade' in self.vars and\
            'constraint_output_load' in self.vars:
                break
            if 'set_var constraint_glitch_peak ' in line or 'set_var -stage variation constraint_delay_degrade ' in line:
                splited = line.split()
                var_name = splited[-2]
                var_value = splited[-1]
                self.vars[var_name] = var_value
            elif 'set_var constraint_glitch_peak ' in line or 'set_var constraint_delay_degrade ' in line:
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
 
        for cell, index in re.findall(condition, self.content_raw, flags=re.DOTALL):
            if cell not in self.conditions:
                self.conditions[cell] = dict()
                self.conditions[cell]['OUTPUT_LOAD'] = index
            else:
                self.conditions[cell]['OUTPUT_LOAD'] = index
 
    def parse_condition_glitch(self):
        condition = 'if.{0,50}{.{0,10}string compare.{0,10}"(\w{0,50})".{0,50}constraint_glitch_peak ([0-9\.\-\+e]{0,4})'
        for cell, value in re.findall(condition, self.content_raw, flags=re.DOTALL):
            if cell not in self.conditions:
                self.conditions[cell] = dict()
                self.conditions[cell]['GLITCH'] = value
            else:
                self.conditions[cell]['GLITCH'] = value
 
    def parse_condition_delay_degrade(self):
        condition = 'if.{0,50}{.{0,10}string compare.{0,10}"(\w{0,50})".{0,50}constraint_delay_degrade ([0-9\.\-\+e]{0,4})'
        for cell, value in re.findall(condition, self.content_raw, flags=re.DOTALL):
            if cell not in self.conditions:
                self.conditions[cell] = dict()
                self.conditions[cell]['PUSHOUT_PER'] = value
            else:
                self.conditions[cell]['PUSHOUT_PER'] = value
 
    def parse_amd_smc_degrade(self):
        for line in self.content_lines:
            if 'set_config_opt -type lvf smc_degrade' in line:
                self.vars['smc_degrade'] = line.split()[-1].strip()
 
    def parse_amd_glitch_high_threshold(self):
        glitch_pattern = re.compile(
            r'set_config_opt -type \{\*hold\*\}(.*\n){1,2}.*glitch_high_threshold([ \w\.]+\n)+\}')
        glitches = glitch_pattern.finditer(self.content_raw)
        for glitch in glitches:
            if 'amd_glitch' not in self.vars:
                self.vars['amd_glitch'] = dict()
            self.process_amd_raw_glitch(glitch.group(0))
 
        for line in self.content_lines:
            if 'set glitch_low_threshold' in line:
                if 'amd_glitch' not in self.vars:
                    self.vars['amd_glitch'] = dict()
                self.vars['amd_glitch']['default_glitch'] = line.split()[-1]
        if 'amd_glitch' in self.vars:
            if 'cells' not in self.vars['amd_glitch']:
                self.vars['amd_glitch']['cells'] = []
 
    def process_amd_raw_glitch(self, glitch):
        glitch = map(str.strip, glitch.split('\n'))
        is_cell_glitch = False
        for line in glitch:
            if '-cell' in line:
                self.process_amd_glitch_cell(line)
                self.vars['amd_glitch']['cells'] = self.process_amd_glitch_cell(
                    line)
                is_cell_glitch = True
            elif 'glitch_low_threshold' in line and is_cell_glitch:
                self.vars['amd_glitch']['cell_glitch'] = line.split()[-1]
 
            elif 'glitch_low_threshold' in line and not is_cell_glitch:
                self.vars['amd_glitch']['hold_glitch'] = line.split()[-1]
 
    def process_amd_glitch_cell(self, line):
        left_curly = line.index('{')
        right_curly = line.index('}')
        cells = line[left_curly+1:right_curly].strip().split()
        return cells
 
