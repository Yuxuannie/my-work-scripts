import fnmatch
import re
import csv
import os
 
def extract_pin_direction(pin_dir):
    """Convert pin direction to single letter format"""
    return 'F' if pin_dir.lower() == 'fall' else 'R' if pin_dir.lower() == 'rise' else pin_dir
 
def preprocess_content(content):
    """Split content into separate if blocks based on indentation, handling arbitrary whitespace"""
    blocks = []
    current_block = []
    lines = content.split('\n')
    in_block = False
   
    for line in lines:
        stripped_line = line.strip()
       
        # Start of a new block - match 'if' with any leading whitespace
        if stripped_line.startswith('if ') or stripped_line.startswith('if('):
            if current_block:  # Save previous block if exists
                if any('return template_name' in line for line in current_block):
                    blocks.append('\n'.join(current_block))
            current_block = [line]
            in_block = True
            continue
       
        # Within a block
        if in_block:
            current_block.append(line)
            if 'return template_name' in line:
                blocks.append('\n'.join(current_block))
                current_block = []
                in_block = False
   
    # Add the last block if it exists and has a return statement
    if current_block and any('return template_name' in line for line in current_block):
        blocks.append('\n'.join(current_block))
   
    print(f"Debug: Found {len(blocks)} blocks after preprocessing")
    # Print first few characters of each block for debugging
    for i, block in enumerate(blocks[:3]):
        print(f"Debug: Block {i+1} starts with: {block[:100]}...")
   
    return blocks
 
def extract_constraint_info(file_path):
    """Extract constraint information from the target file"""
    constraints = []
   
    print(f"\nDebug: Opening file {file_path}")
    with open(file_path, 'r') as file:
        content = file.read()
        print(f"Debug: File content length: {len(content)} characters")
       
        # Split into blocks based on indentation
        blocks = preprocess_content(content)
       
        for i, block_text in enumerate(blocks):
            print(f"\nDebug: Processing block {i+1}:")
            print("Debug: Block content:")
            print("-" * 50)
            print(block_text)
            print("-" * 50)
           
            constraint = {
                'cell_name': '',
                'pin': '',
                'pin_dir': '',
                'rel_pin': '',
                'rel_pin_dir': '',
                'when': ''
            }
           
            # Extract cell_name
            cell_match = re.search(r'fnmatch\.fnmatch\(cell_name,\s*"([^"]*)"', block_text)
            if cell_match:
                constraint['cell_name'] = cell_match.group(1)
                print(f"Debug: Found cell_name: {constraint['cell_name']}")
           
            # Extract pin
            pin_match = re.search(r'constr_pin\s*==\s*"([^"]*)"', block_text)
            if pin_match:
                constraint['pin'] = pin_match.group(1)
                print(f"Debug: Found pin: {constraint['pin']}")
           
            # Extract pin_dir
            pin_dir_match = re.search(r'constr_pin_dir\s*==\s*"([^"]*)"', block_text)
            if pin_dir_match:
                constraint['pin_dir'] = extract_pin_direction(pin_dir_match.group(1))
                print(f"Debug: Found pin_dir: {constraint['pin_dir']}")
           
            # Extract rel_pin
            rel_pin_match = re.search(r'rel_pin\s*==\s*"([^"]*)"', block_text)
            if rel_pin_match:
                constraint['rel_pin'] = rel_pin_match.group(1)
                print(f"Debug: Found rel_pin: {constraint['rel_pin']}")
           
            # Extract rel_pin_dir
            rel_pin_dir_match = re.search(r'rel_pin_dir\s*==\s*"([^"]*)"', block_text)
            if rel_pin_dir_match:
                dir_value = rel_pin_dir_match.group(1)
                if 'fall/rise' in dir_value:
                    constraint['rel_pin_dir'] = 'F/R'
                else:
                    constraint['rel_pin_dir'] = extract_pin_direction(dir_value)
                print(f"Debug: Found rel_pin_dir: {constraint['rel_pin_dir']}")
           
            # Extract when condition
            when_match = re.search(r'"([^"]*)"\s+in\s+when', block_text)
            if when_match:
                constraint['when'] = when_match.group(1)
                print(f"Debug: Found when: {constraint['when']}")
           
            # Add constraint if we found any data
            if any(constraint.values()):
                constraints.append(constraint)
                print("Debug: Added constraint to list")
           
    print(f"\nDebug: Total constraints found: {len(constraints)}")
    return constraints
 
def write_to_csv(constraints, output_file):
    """Write extracted constraints to CSV file"""
    fieldnames = ['cell_name', 'pin', 'pin_dir', 'rel_pin', 'rel_pin_dir', 'when']
   
    print(f"\nDebug: Writing to CSV file: {output_file}")
    print(f"Debug: Number of constraints to write: {len(constraints)}")
   
    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(constraints)
        print("Debug: CSV file written successfully")
 
def main():
    current_dir = os.getcwd()
    target_file = 'funcs.py'
    output_file = 'constraint_info.csv'
   
    print(f"Debug: Current directory: {current_dir}")
    print(f"Debug: Target file: {target_file}")
   
    file_path = os.path.join(current_dir, target_file)
    if os.path.exists(file_path):
        print(f"Debug: Found target file at {file_path}")
        constraints = extract_constraint_info(file_path)
        if constraints:
            write_to_csv(constraints, output_file)
            print(f"\nExtraction complete. Results written to {output_file}")
        else:
            print("\nError: No constraints were found in the file")
    else:
        print(f"Error: Could not find {target_file} in the current directory")
 
if __name__ == "__main__":
    main()
 
