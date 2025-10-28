import subprocess
import math
 
def getXTORandPODECounts(netlist_path):
    #2018/10/30 fix lvt's launch.csh generation failed
    if "vtll" in netlist_path:
        sys_cmd = ["bash", "-c", "grep vtll_mac %s" % netlist_path]
    else:
        sys_cmd = ["bash", "-c", "grep vt_mac %s" % netlist_path]
    #sys_cmd = ["bash", "-c", "grep vt_mac %s" % netlist_path]
    #sys_cmd = ["bash", "-c", "grep vtll_mac %s" % netlist_path]
    p = subprocess.Popen(sys_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, _ = p.communicate()
 
    npode = 0
    nxtor = 0
    for line in stdout.decode().strip().split('\n'):
        if "pode" in line:
            npode += 1
        else:
            nxtor += 1
 
    return nxtor, npode
 
 
def getApproxEffort(nxtor):
    # Use a 4th order polynominal to predict runtime
    nxtor = float(nxtor) / 100
    a4 = -3.9016
    a3 = 29.476
    a2 = -52.403
    a1 = 79.826
    a0 = 0
 
    effort = a4*pow(nxtor,4) + \
             a3*pow(nxtor,3) + \
             a2*pow(nxtor,2) + \
             a1*pow(nxtor,1) + \
             a0*pow(nxtor,0)
 
    return effort
 
 
def populateReqCPUs(spice_info, min_effort):
    for table_point in spice_info:
        for arc_num in spice_info[table_point]:
            arc_info = spice_info[table_point][arc_num]
            if arc_info['VALID_ARC'] is False:
                continue
            arc_info['LB_REQ_CPUS'] = math.floor(arc_info['APPROXIMATE_EFFORT'] /
                                                 min_effort)
            arc_info['UB_REQ_CPUS'] = math.ceil(arc_info['APPROXIMATE_EFFORT'] /
                                                min_effort)
 
 
def getReqCPURange(spice_info):
    lb_req_cpus = 0
    ub_req_cpus = 0
    for table_point in spice_info:
        for arc_num in spice_info[table_point]:
            arc_info = spice_info[table_point][arc_num]
            if arc_info['VALID_ARC'] is False:
                continue
 
            lb_req_cpus += arc_info['LB_REQ_CPUS']
            ub_req_cpus += arc_info['UB_REQ_CPUS']
 
    return lb_req_cpus, ub_req_cpus
 
 
