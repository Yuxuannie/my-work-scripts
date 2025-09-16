import os
import re
import sys
import csv
from fnmatch import fnmatch
import random
 
def extract_arc_pattern(folder_name):
    # Remove the 'hold_' prefix
    pattern = folder_name[5:]
 
    # Match the pattern with the specific cellname criteria
    cellname_match = re.match(r'([A-Z0-9]+D)([0-9]+)([A-Z0-9]+)', pattern)
    if cellname_match:
        prefix, number, suffix = cellname_match.groups()
        # Use wildcard for the number portion, but keep the "D"
        cellname_pattern = f"{prefix}*{suffix}"
        cellname_length = len(cellname_match.group(0))
    else:
        cellname_pattern = pattern
        cellname_length = len(cellname_pattern)
 
    # Remove 'cellname_' from the pattern
    remaining_pattern = pattern[cellname_length+1:]  # +1 for the underscore following cellname
 
    # Match the rest of the folder name pattern
    rest_match = re.match(
        r'([A-Z0-9]+)_(rise|fall)_([A-Z0-9]+)_(rise|fall)_([A-Za-z0-9_]+)_(\d+-\d+)',
        remaining_pattern
    )
 
    if rest_match:
        cstr_pin, cstr_pin_dir, rel_pin, rel_pin_dir, when_cond, index_range = rest_match.groups()
 
        # Construct the pattern using the extracted parts
        arc_pattern = f"{cellname_pattern}_{cstr_pin}_{cstr_pin_dir}_{rel_pin}_{rel_pin_dir}_{when_cond}"
 
        # Print each component of the arc pattern
        print(f"[DEBUG] Extracted parts for '{folder_name}':")
        print(f"  Cell Name Pattern: {cellname_pattern}")
        print(f"  Constraint Pin: {cstr_pin}")
        print(f"  Constraint Pin Direction: {cstr_pin_dir}")
        print(f"  Related Pin: {rel_pin}")
        print(f"  Related Pin Direction: {rel_pin_dir}")
        print(f"  When Condition: {when_cond}")
        print(f"  Index1-Index2: {index_range}")
        print(f"  Final arc pattern is {arc_pattern}")
        print("-" * 60)  # Divider between arcs
    else:
        # Fallback if the folder name doesn't match the expected pattern
        arc_pattern = pattern
        print(f"the folder name doesn't match the expected pattern for '{folder_name}'")
        print(f"[Cellname pattern]: {cellname_pattern}")
        print(f"[remaining_pattern]: {remaining_pattern}")
    return arc_pattern
 
def list_to_pattern(folder_path):
    arc_patterns = set()
    duplicate_patterns = set()  # Track duplicates
 
    for root, dirs, files in os.walk(folder_path):
        for dir_name in dirs:
            if dir_name.startswith("hold_"):
                arc_pattern = extract_arc_pattern(dir_name)
                if arc_pattern not in arc_patterns:
                    arc_patterns.add(arc_pattern)
                else:
                    duplicate_patterns.add(arc_pattern)
 
    return list(arc_patterns)
 
def extract_headers(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
 
    # Find indices for the header section
    start_index = None
    end_index = None
    for i, line in enumerate(lines):
        if "* THANOS Headers" in line:
            start_index = i
        elif "* SPICE options" in line:
            end_index = i
            break
 
    # Extract headers if valid indices are found
    if start_index is not None and end_index is not None:
        return lines[start_index:end_index]
    else:
        return []
 
def create_csv(matched_arcs, target_deck_path, arc_pattern_list):
    with open('arc_pattern_mapping.csv', 'w', newline='') as csvfile:
        fieldnames = ['Arc Path', 'Matched Pattern']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
 
        writer.writeheader()
 
        for arc in matched_arcs:
            arc_path = os.path.join(target_deck_path, arc)
 
            # Find the pattern this arc corresponds to
            matching_pattern = next((pattern for pattern in arc_pattern_list if fnmatch(arc, f"hold_{pattern}_*")), None)
 
            writer.writerow({
                'Arc Path': arc_path,
                'Matched Pattern': matching_pattern,
            })
 
 
def pattern_to_list_matching(arc_pattern_list, target_deck_path):
    matched_arcs = []  # Use a list to store the final matched arcs
    total_matched_arcs = []
 
    for arc_pattern in arc_pattern_list:
        # Create a pattern to match, excluding the index range
        pattern_without_index = f"hold_{arc_pattern}_*"
        print(f"[DEBUG] Searching for pattern: '{pattern_without_index}'")
 
        # Find all directories that match the pattern
        matching_dirs = []
        total_matching_dirs = []
 
        for root, dirs, files in os.walk(target_deck_path):
            for dir_name in dirs:
                if fnmatch(dir_name, pattern_without_index):
                    matching_dirs.append(dir_name)
                    total_matching_dirs.append(dir_name)
                    print(f"[DEBUG] Found match: '{dir_name}' for pattern '{pattern_without_index}'")
 
        # Choose one unique directory among them to add to the matched arcs list
        if matching_dirs:
            chosen_dir = random.choice(matching_dirs)
            matched_arcs.append(chosen_dir)
            for dir_name in matching_dirs:
                total_matched_arcs.append(dir_name)
            print(f"[DEBUG] Selected '{chosen_dir}' for pattern '{arc_pattern}'")
        else:
            print(f"[DEBUG] No matches found for pattern '{pattern_without_index}'")
 
    # Print each matched arc line by line
    for arc in matched_arcs:
        print(arc)
    # Print the total number of matched arcs
    print(f"Total number of matched arcs: {len(matched_arcs)}")
    print(f"Total number of all matched arcs: {len(total_matched_arcs)}")
 
    return matched_arcs
 
def pattern_to_list_matching_all(arc_pattern_list, target_deck_path):
    matched_arcs = []  # Use a list to store the final matched arcs
    total_matched_arcs = []
 
    for arc_pattern in arc_pattern_list:
        # Create a pattern to match, excluding the index range
        pattern_without_index = f"hold_{arc_pattern}_*"
        print(f"[DEBUG] Searching for pattern: '{pattern_without_index}'")
 
        # Find all directories that match the pattern
        matching_dirs = []
        total_matching_dirs = []
 
        for root, dirs, files in os.walk(target_deck_path):
            for dir_name in dirs:
                if fnmatch(dir_name, pattern_without_index):
                    matching_dirs.append(dir_name)
                    total_matching_dirs.append(dir_name)
                    print(f"[DEBUG] Found match: '{dir_name}' for pattern '{pattern_without_index}'")
 
        # Choose one unique directory among them to add to the matched arcs list
        if matching_dirs:
            for dir_name in matching_dirs:
                matched_arcs.append(dir_name)
        else:
            print(f"[DEBUG] No matches found for pattern '{pattern_without_index}'")
 
    # Print each matched arc line by line
    for arc in matched_arcs:
        print(arc)
    # Print the total number of matched arcs
    print(f"Total number of matched arcs: {len(matched_arcs)}")
 
    return matched_arcs
 
def main():
    if len(sys.argv) < 5:
        print("Usage: python script.py <folder_path> <target_deck_path> <operation_mode>")
        print("operation_mode: list_to_pattern, pattern_to_list, all")
        sys.exit(1)
 
    folder_path = sys.argv[1]
    target_deck_path = sys.argv[2]
    operation_mode = sys.argv[3]
    arc_patterns_str = sys.argv[4]
 
    # Split the string back into a list
    arc_patterns = arc_patterns_str.split()
 
    if operation_mode in ['pattern_to_list', 'all']:
        #matched_arcs = pattern_to_list_matching(arc_patterns, target_deck_path)
        matched_arcs = pattern_to_list_matching_all(arc_patterns, target_deck_path)
        print("Matched Arcs:", matched_arcs)
        create_csv(matched_arcs, target_deck_path, arc_patterns)
 
    if operation_mode in ['list_to_pattern', 'all']:
        arc_patterns = list_to_pattern(folder_path)
        print("Arc Patterns:", arc_patterns)
 
if __name__ == "__main__":
    main()
 
