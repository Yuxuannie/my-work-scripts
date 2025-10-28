 
import os
import sys
import shutil
 
def read_common_arcs(file_path):
    """
    Read common arc list from the .txt file.
    """
    common_arcs = set()
    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip()
            # Extract only the arc names from lines that start with numbers and a period
            if line and line[0].isdigit() and '.' in line:
                arc_name = line.split('. ', 1)[-1]
                common_arcs.add(arc_name)
    return common_arcs
 
def find_unmatched_arc_folders(selected_type_path, common_arcs):
    """
    Traverse the selected corner/type path and find arc folders not in the common arc list.
    """
    unmatched_folders = []
    decks_folder_path = os.path.join(selected_type_path, "DECKS")
    if not os.path.isdir(decks_folder_path):
        print(f"DECKS folder not found in path: {selected_type_path}")
        return unmatched_folders
 
    for arc_folder in os.listdir(decks_folder_path):
        arc_folder_path = os.path.join(decks_folder_path, arc_folder)
        # Skip non-folder paths
        if not os.path.isdir(arc_folder_path):
            continue
 
        # Check if the arc folder name is NOT in the common_arc_list
        if arc_folder not in common_arcs:
            unmatched_folders.append(arc_folder_path)
 
    return unmatched_folders
 
def remove_folders(folders_to_remove):
    """
    Remove folders after user confirmation.
    """
    print("\nUnmatched Arc Folders Found:")
    for folder in folders_to_remove:
        print(f"  - {folder}")
 
    print(f"\nTotal unmatched folders: {len(folders_to_remove)}")
    confirmation = input("\nDo you want to delete these folders? (yes/no): ").strip().lower()
    if confirmation == "yes":
        for folder in folders_to_remove:
            print(f"Removing folder: {folder}")
            shutil.rmtree(folder)
        print("All unmatched folders have been removed.")
    else:
        print("No folders were removed.")
 
def main():
    # Ensure correct number of arguments
    if len(sys.argv) != 3:
        print("Usage: python3 find_and_remove_unmatched_arcs.py <common_arc_file> <selected_type_path>")
        sys.exit(1)
 
    # Get parameters from the shell script
    common_arc_file_path = sys.argv[1]
    selected_type_path = sys.argv[2]
 
    # Validate paths
    if not os.path.isfile(common_arc_file_path):
        print(f"Error: Common arcs file not found: {common_arc_file_path}")
        sys.exit(1)
 
    if not os.path.isdir(selected_type_path):
        print(f"Error: Selected type directory not found: {selected_type_path}")
        sys.exit(1)
 
    # Read the common arc list
    common_arc_list = read_common_arcs(common_arc_file_path)
 
    # Find unmatched arc folders
    unmatched_folders = find_unmatched_arc_folders(selected_type_path, common_arc_list)
 
    if unmatched_folders:
        # Provide a summary and ask for user confirmation before removing
        remove_folders(unmatched_folders)
    else:
        print("No unmatched arc folders found. No action taken.")
 
if __name__ == "__main__":
    main()
 
