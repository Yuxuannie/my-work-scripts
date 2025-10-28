import subprocess
import fnmatch
 
import utilities.fileIO as ioutils
 
 
def createLPEWithParams(input_lpe, output_lpe, parameter_list):
    """
    A function that will accept an input LPE netlist file and then isnert the random
    variables for each transistor in the LPE.
    The random variables for each transistor will correspond to the "parameters"
    argument of this function.
    The new LPE file will be written to the "output_lpe" argument
    """
 
    # Get the list of XTORs in the current LPE
    xtor_list = getXTORsInLPE(input_lpe)
 
    # Create the LPE header with the random variables
    output_lpe_header = createOutputLPEHeader(xtor_list, parameter_list)
 
    # Start reading/copying the input LPE
    input_lpe_lines = ioutils.readFile(input_lpe)
    output_lpe_buffer = createOutputLPEBuffer(
        input_lpe_lines, xtor_list, parameter_list, output_lpe_header
    )
 
    # Write file
    ioutils.writeBufferToFile(output_lpe_buffer, output_lpe)
 
 
def getXTORsInLPE(input_lpe):
    # Grep only non-PODE MOS
    grep_cmd1 = ["bash", "-c", "grep 'ch_' %s" % input_lpe]
    p1 = subprocess.Popen(
        grep_cmd1, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    grep_cmd2 = ["bash", "-c", "grep '_mac'"]
    p2 = subprocess.Popen(
        grep_cmd2,
        stdin=p1.stdout,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    # Grep out any commented-out MOS
    grep_cmd3 = ["bash", "-c", "grep -v '*'"]
    p3 = subprocess.Popen(
        grep_cmd3,
        stdin=p2.stdout,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    stdout, stderr = p3.communicate(timeout=60)
    # Extract the XTORs
    xtor_list = list(
        set([x.split()[0] for x in stdout.decode().strip().split('\n')])
    )
    return xtor_list
 
 
def createOutputLPEHeader(xtor_list, parameter_list):
    header_buff = list()
    for xtor in xtor_list:
        xtor_buff = list()
        _ = [
            xtor_buff.append("%s__%s=agauss(0,1,1)" % (xtor, parameter))
            for parameter in parameter_list
        ]
        header_buff.append("+ %s" % ' '.join(xtor_buff))
    header_line = "%s\n" % '\n'.join(header_buff)
    return header_line
 
 
def createOutputLPEBuffer(
    input_lpe_lines, xtor_list, parameter_list, output_lpe_header
):
    # Initialize the buffer
    output_lpe_buff = list()
 
    # Set some headers and flags
    subckt_header = ".subckt*"
    insert_lpe_header = False
 
    # Loop
    for line in input_lpe_lines:
        # Check if we saw the subckt, which is where we insert the header
        if fnmatch.fnmatch(line.lower(), subckt_header):
            output_lpe_buff.append(line)
            insert_lpe_header = True
 
        # Check if we should insert the header
        elif ('+' not in line) and insert_lpe_header:
            output_lpe_buff.append(output_lpe_header)
            output_lpe_buff.append(line)
            insert_lpe_header = False
 
        # Check if the current line has a MOS device
        elif line[0] == 'X':
            output_lpe_buff.append(line)
            # Check if the current MOS is in the LPE, which means we insert RV's
            if line.strip().split()[0] in xtor_list:
                xtor_name = line.strip().split()[0]
                xtor_random_vars_line = formRVForXTOR(xtor_name, parameter_list)
                output_lpe_buff.append(xtor_random_vars_line)
 
        # Just append
        else:
            output_lpe_buff.append(line)
 
    return output_lpe_buff
 
 
def formRVForXTOR(xtor, parameter_list):
    line_buff = list()
    _ = [line_buff.append("%s=%s__%s" % (p, xtor, p)) for p in parameter_list]
    random_vars_line = "+ %s\n" % ' '.join(line_buff)
    return random_vars_line
 
