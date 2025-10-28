import math
import os
import glob
import subprocess
import sys
 
sys.path.insert(0, os.path.split(__file__)[0])  # noqa
import runtime.funcs as runtimeEstimate
import utilities.fileIO as fileIO
 
 
def createLaunchScript(root_output_path, lsf_cfg_file, min_effort):
    header_buffer = formHeaderBuffer()
    header_buffer.append('\n')
    nom_buffer = ['\n']
    mc_buffer = ['\n']
    launch_script = os.path.join(
        os.path.dirname(root_output_path), "launch_all.csh"
    )
 
    for deck_path in glob.glob(os.path.join(root_output_path, "*")):
        nominal_deck = os.path.join(deck_path, "nominal_sim.sp")
        netlist_path = getNetlistPathFromNominalSpiceDeck(nominal_deck)
        nxtor, _ = runtimeEstimate.getXTORandPODECounts(netlist_path)
        current_effort = runtimeEstimate.getApproxEffort(nxtor)
        req_cpus = math.ceil(current_effort / min_effort)
 
        nom_launch_cmd = formNomLaunchCmd(deck_path)
        mc_launch_cmd = formMCLaunchCmd(deck_path, req_cpus, lsf_cfg_file)
 
        nom_buffer.append(nom_launch_cmd)
        mc_buffer.append(mc_launch_cmd)
 
    # Write
    fileIO.writeBufferToFile(
        header_buffer, launch_script, delimeter='\n', mode='w'
    )
    fileIO.writeBufferToFile(
        nom_buffer, launch_script, delimeter='\n', mode='a'
    )
    fileIO.writeBufferToFile(mc_buffer, launch_script, delimeter='\n', mode='a')
 
    return launch_script
 
 
def formHeaderBuffer():
    header_buffer = list()
    hb_line = "#!/bin/tcsh -f"
    tool_line = "source /tools/dotfile_new/cshrc.hspice L-2016.03"
    header_buffer.append(hb_line)
    header_buffer.append(tool_line)
    return header_buffer
 
 
def formNomLaunchCmd(deck_path):
    output_log = os.path.join(deck_path, "nominal.log")
    output_err = os.path.join(deck_path, "nominal.err")
    input_deck = os.path.join(deck_path, "nominal_sim.sp")
    output_lis = os.path.join(deck_path, "nominal_sim.lis")
    nom_launch_cmd = "bsub -q all.q -R \"select[ostype=any]\" -J nominal_mcqc -o %s " \
                     "-e %s hspice -i %s -o %s" % \
                     (output_log, output_err, input_deck, output_lis)
    return nom_launch_cmd
 
 
def formMCLaunchCmd(deck_path, cpu_num, lsf_dp_cfg):
    output_log = os.path.join(deck_path, "mc.log")
    output_err = os.path.join(deck_path, "mc.err")
    input_deck = os.path.join(deck_path, "mc_sim.sp")
    mc_launch_cmd = "bsub -q all.q -R \"select[ostype=any]\" -J mc_mcqc -o %s -e %s " \
                    "hspice64 -dp %s -dpconfig %s -i %s -o %s" % \
                    (output_log, output_err, cpu_num, lsf_dp_cfg, input_deck, deck_path)
    return mc_launch_cmd
 
 
def getNetlistPathFromNominalSpiceDeck(nominal_deck):
    grep_cmd1 = ["bash", "-c", "grep '.inc' %s" % nominal_deck]
    p1 = subprocess.Popen(
        grep_cmd1, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    grep_cmd2 = ["bash", "-c", "grep BWP"]
    p2 = subprocess.Popen(
        grep_cmd2,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        stdin=p1.stdout
    )
    stdout, stderr = p2.communicate()
    netlist_path = stdout.decode().strip().split("'")[1]
    return netlist_path
 
