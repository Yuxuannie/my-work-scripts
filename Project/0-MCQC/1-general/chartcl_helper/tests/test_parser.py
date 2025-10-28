import sys
sys.path.append('./')
from chartcl_helper.parser import ChartclParser
 
class TestParser:
    def test_parse_set_env(self):
        cp = ChartclParser('D:\Code\deck_integration\output_dev_base_char_ffgnp0p55vm40c.tcl')
        cp.parse_set_var()
        assert cp.vars=={'constraint_delay_degrade': 0.4, 'constraint_glitch_peak': 0.1, 'constraint_output_load': 2}
        cp.parse_condition_load()
        assert len(list(cp.conditions.keys())) == 37
        cp = ChartclParser('D:\Code\deck_integration\condition_glitch_char_ssgnp_0p585v_m40c_cworst_CCworst_T.tcl')
        cp.parse_condition_glitch()
        assert len(list(cp.conditions.keys())) == 14
