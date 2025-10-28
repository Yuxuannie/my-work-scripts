 
class TemplateInfo(object):
    def __init__(self, template_file):
        # Init
        self.template_file = template_file
 
        # Common
        self._tool_vars = dict()
        self._tcl_vars = dict()
        self._define_template_list = dict()
        self._cell_list = dict()
        # SIS template var
        self._sis_template = dict()
 
 
    # Setters
    def addToolVar(self, var_name, var_value):
        self._tool_vars[var_name] = var_value
 
    def addTclVar(self, var_name, var_value):
        self._tcl_vars[var_name] =  var_value
 
    def addDefineTemplate(self, define_template):
        self._define_template_list[define_template.name()] = define_template
 
    def addCell(self, cell):
        """
 
        Args:
            cell (Cell):
        """
        self._cell_list[cell.name()]=cell
 
    def getAllDefineTemplates(self):
        return self._define_template_list
 
    def getDefineTemplate(self, template_name):
        """
 
        Args:
            template_name (str):
        Returns:
            define_template_obj (DefineTemplateInfo):
        """
        return self._define_template_list[template_name] if template_name in self._define_template_list else None
 
    def getAllCells(self):
        return list(self._cell_list.values())
 
    def getCell(self, cell_name):
        """
        Args:
            cell_name (str):
        Returns:
            cell (Cell):
        """
        return self._cell_list[cell_name] if cell_name in self._cell_list else None
 
 
class DefineTemplateInfo(object):
    def __init__(self,
                 type=None,
                 index_1=None,
                 index_2=None,
                 index_3=None,
                 name=None):
        # Common
        self._type = type
        self._index_1 = index_1
        self._index_2 = index_2
        self._index_3 = index_3
        self._name = name
 
    # Getters
    def type(self):
        return self._type
 
    def name(self):
        return self._name
 
    def index_1(self):
        return self._index_1
 
    def index_2(self):
        return self._index_2
 
    def index_3(self):
        return self._index_3
 
 
 
class Cell(object):
    def __init__(self,
                 aasync=None,
                 bidi=None,
                 clock=None,
                 constraint=None,
                 delay=None,
                 harness=None,
                 ignore_input_for_auto_cap=None,
                 ignore_pin_for_ccsn=None,
                 input=None,
                 internal=None,
                 internal_supply=None,
                 mpw=None,
                 output=None,
                 pinlist=None,
                 power=None,
                 scan=None,
                 scan_cell_postfix=None,
                 scan_cell_prefix=None,
                 si_immunity=None,
                 type=None,
                 user_arcs_only=None,
                 when=None,
                 name=None):
 
        # Common to define_cell
        self._async = aasync
        self._bidi = bidi
        self._clock = clock
        self._constraint = constraint
        self._delay = delay
        self._harness = harness
        self._ignore_input_for_auto_cap = ignore_input_for_auto_cap
        self._ignore_pin_for_ccsn = ignore_pin_for_ccsn
        self._input = input
        self._internal = internal
        self._internal_supply = internal_supply
        self._mpw = mpw
        self._output = output
        self._pinlist = pinlist
        self._power = power
        self._scan = scan
        self._scan_cell_postfix = scan_cell_postfix
        self._scan_cell_prefix = scan_cell_prefix
        self._si_immunity = si_immunity
        self._type = type
        self._user_arcs_only = user_arcs_only
        self._when = when
        self._name = name
 
        # Track the define_arc for the cells
        self._n_arcs = 0
        self._arc_list = list()
        self._define_index_list = list()
 
    # Setters
    def addArc(self, arc_obj):
        """
        Args:
            arc_obj (Arc):
        """
        # Set the arc ID
        arc_id = self.nArcs()
        arc_obj.setArcID(arc_id)
 
        # Store
        self._arc_list.append(arc_obj)
 
        # Increment nArcs
        self._n_arcs += 1
 
    def addIndex(self, define_index_obj):
        """
 
        Args:
            define_index_obj (Index):
        """
        # Store
        self._define_index_list.append(define_index_obj)
 
    # Getters
    def getAllIndexOverrides(self):
        return self._define_index_list
 
    def arcList(self):
        return self._arc_list
 
    def nArcs(self):
        return self._n_arcs
 
    def aasync(self):
        return self._async
 
    def bidi(self):
        return self._bidi
 
    def clock(self):
        return self._clock
 
    def constraint(self):
        return self._constraint
 
    def delay(self):
        return self._delay
 
    def harness(self):
        return self._harness
 
    def ignoreInputForAutoCap(self):
        return self._ignore_input_for_auto_cap
 
    def ignorePinForCCSN(self):
        return self._ignore_pin_for_ccsn
 
    def input(self):
        return self._input
 
    def internal(self):
        return self._internal
 
    def internalSupply(self):
        return self._internal_supply
 
    def mpw(self):
        return self._mpw
 
    def output(self):
        return self._output
 
    def pinlist(self):
        return self._pinlist
 
    def power(self):
        return self._power
 
    def scan(self):
        return self._scan
 
    def scanCellPostfix(self):
        return self._scan_cell_postfix
 
    def scanCellPrefix(self):
        return self._scan_cell_prefix
 
    def siImmunity(self):
        return self._si_immunity
 
    def type(self):
        return self._type
 
    def when(self):
        return self._when
 
    def name(self):
        return self._name
 
 
class Arc(object):
    def __init__(self,
                 attribute=None,
                 ccsn_stage=None,
                 ccsn_probe=None,
                 delay_threshold=None,
                 dependent_load=None,
                 dual_dir=None,
                 dual_pin=None,
                 dual_related=None,
                 extsim_deck_header=None,
                 ic=None,
                 ignore=None,
                 load_dir=None,
                 logic_condition=None,
                 margin=None,
                 metric=None,
                 metric_thresh=None,
                 pin=None,
                 pin_dir=None,
                 pin_gnd=None,
                 pin_load=None,
                 pin_load_dir=None,
                 pin_probe=None,
                 pin_probe_dir=None,
                 pin_probe_threshold=None,
                 pin_vdd=None,
                 pinlist=None,
                 pg_pin=None,
                 prevector_pinlist=None,
                 prevector_slew=None,
                 prevector=None,
                 probe=None,
                 probe_dir=None,
                 related_pin=None,
                 related_pin_dir=None,
                 related_probe=None,
                 related_probe_dir=None,
                 related_probe_threshold=None,
                 sdf_cond=None,
                 slew_threshold=None,
                 type=None,
                 value=None,
                 value_trans=None,
                 vector=None,
                 when=None,
                 cell=None
                 ):
 
        # Common to define_arc
        self._attribute = attribute
        self._ccsn_stage = ccsn_stage
        self._ccsn_probe = ccsn_probe
        self._delay_threshold = delay_threshold
        self._dependent_load = dependent_load
        self._dual_dir = dual_dir
        self._dual_pin = dual_pin
        self._dual_related = dual_related
        self._extsim_deck_header = extsim_deck_header
        self._ic = ic
        self._ignore = ignore
        self._load_dir = load_dir
        self._logic_condition = logic_condition
        self._margin = margin
        self._metric = metric
        self._metric_thresh = metric_thresh
        self._pin = pin
        self._pin_dir = pin_dir
        self._pin_gnd = pin_gnd
        self._pin_load = pin_load
        self._pin_load_dir = pin_load_dir
        self._pin_probe = pin_probe
        self._pin_probe_dir= pin_probe_dir
        self._pin_probe_threshold = pin_probe_threshold
        self._pin_vdd = pin_vdd
        self._pinlist = pinlist
        self._pg_pin = pg_pin
        self._prevector_pinlist = prevector_pinlist
        self._prevector_slew = prevector_slew
        self._prevector = prevector
        self._probe = probe
        self._probe_dir = probe_dir
        self._related_pin = related_pin
        self._related_pin_dir = related_pin_dir
        self._related_probe = related_probe
        self._related_probe_dir = related_probe_dir
        self._related_probe_threshold = related_probe_threshold
        self._sdf_cond =sdf_cond
        self._slew_threshold = slew_threshold
        self._type = type
        self._value = value
        self._value_trans = value_trans
        self._vector = vector
        self._when = when
        self._cell = cell
 
        # Other descriptive attributes
        self._arc_id = None
 
    # Setters
    def setArcID(self, arc_id):
        self._arc_id = arc_id
 
    # Getters
    def arcId(self):
        return self._arc_id
 
    def attribute(self):
        return self._attribute
 
    def ccsnStage(self):
        return self._ccsn_stage
 
    def ccsnProbe(self):
        return self._ccsn_probe
 
    def delayThreshold(self):
        return self._delay_threshold
 
    def dependentLoad(self):
        return self._dependent_load
 
    def dualDir(self):
        return self._dual_dir
 
    def dualPin(self):
        return self._dual_pin
 
    def dualRelated(self):
        return self._dual_related
 
    def extsimDeckHeader(self):
        return self._extsim_deck_header
 
    def ic(self):
        return self._ic
 
    def ignore(self):
        return self._ignore
 
    def loadDir(self):
        return self._load_dir
 
    def logicCondition(self):
        return self._logic_condition
 
    def margin(self):
        return self._margin
 
    def metric(self):
        return self._metric
 
    def metric_thresh(self):
        return self._metric_thresh
 
    def pin(self):
        return self._pin
 
    def pinDir(self):
        return self._pin_dir
 
    def pinGnd(self):
        return self._pin_gnd
 
    def pinLoad(self):
        return self._pin_load
 
    def pinLoadDir(self):
        return self._pin_load_dir
 
    def pinProbe(self):
        return self._pin_probe
 
    def pinProbeDir(self):
        return self._pin_probe_dir
 
    def pinProbeThreshold(self):
        return self._pin_probe_threshold
 
    def pinVdd(self):
        return self._pin_vdd
 
    def pinlist(self):
        return self._pinlist
 
    def pgPin(self):
        return self._pg_pin
 
    def prevectorPinlist(self):
        return self._prevector_pinlist
 
    def prevectorSlew(self):
        return self._prevector_slew
 
    def prevector(self):
        return self._prevector
 
    def probe(self):
        return self._probe
 
    def probeDir(self):
        return self._probe_dir
 
    def relatedPin(self):
        return self._related_pin
 
    def relatedPinDir(self):
        return self._related_pin_dir
 
    def relatedProbe(self):
        return self._related_probe
 
    def relatedProbeDir(self):
        return self._related_probe_dir
 
    def relatedProbeThreshold(self):
        return self._related_probe_threshold
 
    def sdfCond(self):
        return self._sdf_cond
 
    def slewThreshold(self):
        return self._slew_threshold
 
    def type(self):
        return self._type
 
    def value(self):
        return self._value
 
    def valueTrans(self):
        return self._value_trans
 
    def vector(self):
        return self._vector
 
    def when(self):
        return self._when
 
    def cell(self):
        return self._cell
 
 
class Index(object):
    def __init__(self,
                 index_1=None,
                 index_2=None,
                 pin=None,
                 related_pin=None,
                 type=None,
                 when=None,
                 cell=None):
 
        # Common to define_index
        self._index_1 = index_1
        self._index_2 = index_2
        self._pin = pin
        self._related_pin = related_pin
        self._type = type
        self._when = when
        self._cell = cell
 
    # Getters
    def index_1(self):
        return self._index_1
 
    def index_2(self):
        return self._index_2
 
    def pin(self):
        return self._pin
 
    def relatedPin(self):
        return self._related_pin
 
    def type(self):
        return self._type
 
    def when(self):
        return self._when
 
    def cell(self):
        return self._cell
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
