__version__ = "1.0.0"
__date__ = "2016-08-04"
__author__ = "rahulk"
__maintainer__ = "rahulk"
__email__ = rahulk@tsmc.com
__name__ = "fileIO"
 
import fnmatch
 
 
def findMatchesInBuffer(input_buffer, pattern, starting_idx=0):
    """
    A function that searches through the entries in the 'input_buffer' and returns
    indices of all entries that matches 'pattern'.
    This function is typically used to "position" yourself at a specific point in the
    write buffer without cluttering up the user's functions.
 
    Input:
        input_buffer (list):
            A list of strings, typically corresponding to the lines of a file
        pattern (str):
            A single string, with possible wildcards, that is used to identify the
            desired position in the input_buffer
    Returns:
        buffer_indices (list):
            A list of integers representing the entries of 'input_buffer' that match
            'pattern'.
            If there are no matches, an empty list is returned.
 
    Examples:
        >> findFirstMatchInBuffer(input_buffer, pattern)
        [53]
    """
 
    buffer_indices = list()
    for count in range(starting_idx, len(input_buffer)):
        if fnmatch.fnmatch(input_buffer[count], pattern):
            buffer_indices.append(count)
    return buffer_indices
 
 
def readFile(input_file):
    with open(input_file, 'r') as f:
        f_lines = f.readlines()
    return f_lines
 
 
def writeBufferToFile(write_buffer, output_file, delimeter='', mode='w'):
    with open(output_file, mode) as f:
        f.write(delimeter.join(write_buffer))
 
