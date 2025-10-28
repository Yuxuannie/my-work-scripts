class ArcInfo(object):
    def __init__(
        self,
        cell=None,
        arc_type=None,
        pin=None,
        pin_dir=None,
        rel_pin=None,
        rel_pin_dir=None,
        when=None,
        cell_pinlist=None,
        output_pinlist=None,
        index_1=None,
        probe_list=None,
        index_2=None,
        index_3_idx=None,
        output_load=None,
        side_pin_states=None,
        template_deck=None,
        metric=None,
        metric_thresh=None,
        vector=None,
        constraint_define_template=None
    ):
 
        # Init
        self._cell = cell
        self._arc_type = arc_type
        self._pin = pin
        self._pin_dir = pin_dir
        self._rel_pin = rel_pin
        self._rel_pin_dir = rel_pin_dir
        self._when = when
        self._cell_pinlist = cell_pinlist
        self._output_pinlist = output_pinlist
        self._index_1 = index_1
        self._probe_list = probe_list
        self._index_2 = index_2
        self._output_load = output_load
        self._index_3_idx = index_3_idx
        self._side_pin_states = side_pin_states
        self._template_deck = template_deck
        self._metric = metric
        self._metric_thresh = metric_thresh
        self._vector = vector
        self._constraint_define_template = constraint_define_template
 
    def cell(self):
        return self._cell
 
    def arcType(self):
        return self._arc_type
 
    def pin(self):
        return self._pin
 
    def pinDir(self):
        return self._pin_dir
 
    def relPin(self):
        return self._rel_pin
 
    def relPinDir(self):
        return self._rel_pin_dir
 
    def when(self):
        return self._when
 
    def cellPinlist(self):
        return self._cell_pinlist
 
    def outputPinlist(self):
        return self._output_pinlist
 
    def index_1(self):
        return self._index_1
 
    def probeList(self):
        return self._probe_list
 
    def index_2(self):
        return self._index_2
 
    def index_3_idx(self):
        return self._index_3_idx
 
    def outputLoad(self):
        return self._output_load
 
    def sidePinStates(self):
        return self._side_pin_states
 
    def templateDeck(self):
        return self._template_deck
 
    def metric(self):
        return self._metric
 
    def metric_thresh(self):
        return self._metric_thresh
 
    def vector(self):
        return self._vector
 
    def constraint_define_template(self):
        return self._constraint_define_template
 
