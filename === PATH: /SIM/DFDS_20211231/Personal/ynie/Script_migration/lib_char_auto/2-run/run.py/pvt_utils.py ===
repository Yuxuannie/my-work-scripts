#!/usr/bin/env python3
#==============================================================================#
# PVT Utilities
# Owner: Yuxuan Nie
# Last Modified: April 20, 2025
# Version: 1.0
#
# Description: Utility functions for accessing PVT configuration data.
#              Provides a clean API for shell scripts to retrieve PVT mappings.
#
# Usage: ./pvt_utils.py <command> [arguments]
#   Commands:
#     list                  - List all available PVT corners
#     info <corner>         - Get complete information for a corner
#     work_dir <corner>     - Get work directory for a corner
#     dirs <corner>         - Get comma-separated directories for a corner
#     libs [group]          - List libraries in a specific group
#==============================================================================#
import sys
import pvt_config
 
def get_directories(corner):
    """Get all directories for a specific corner"""
    if corner not in pvt_config.PVT_CORNERS:
        return None
 
    corner_config = pvt_config.PVT_CORNERS[corner]
    directories = []
 
    # Process library selections
    for selection in corner_config.get('library_selections', []):
        if isinstance(selection, str):
            # Use all libraries from this group
            if selection in pvt_config.LIBRARY_GROUPS:
                directories.extend(pvt_config.LIBRARY_GROUPS[selection])
        elif isinstance(selection, tuple) and len(selection) == 2:
            # Use specific indexes from this group
            group_name, indexes = selection
            if group_name in pvt_config.LIBRARY_GROUPS:
                group_libs = pvt_config.LIBRARY_GROUPS[group_name]
                for idx in indexes:
                    if 0 <= idx < len(group_libs):
                        directories.append(group_libs[idx])
 
    # Add additional directories
    directories.extend(corner_config.get('additional_dirs', []))
 
    return directories
 
def get_work_dir(corner):
    """Get work directory for a specific corner"""
    if corner not in pvt_config.PVT_CORNERS:
        return None
    return pvt_config.PVT_CORNERS[corner]['work_dir']
 
def list_corners():
    """List all available PVT corners"""
    return list(pvt_config.PVT_CORNERS.keys())
 
def get_corner_info(corner):
    """Get all information for a specific corner"""
    if corner not in pvt_config.PVT_CORNERS:
        return None
 
    return {
        'work_dir': get_work_dir(corner),
        'directories': get_directories(corner)
    }
 
def list_libraries(group=None):
    """List all available libraries or libraries in a specific group"""
    if group:
        if group in pvt_config.LIBRARY_GROUPS:
            print(f"Libraries in {group}:")
            for i, lib in enumerate(pvt_config.LIBRARY_GROUPS[group]):
                print(f"  [{i}] {lib}")
        else:
            print(f"Error: Library group '{group}' not found")
    else:
        print("Available library groups:")
        for group_name, libs in pvt_config.LIBRARY_GROUPS.items():
            print(f"  {group_name} ({len(libs)} libraries)")
 
# Command-line interface
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  ./pvt_utils.py list                    # List all corners")
        print("  ./pvt_utils.py info <corner>           # Get info for a corner")
        print("  ./pvt_utils.py work_dir <corner>       # Get work directory")
        print("  ./pvt_utils.py dirs <corner>           # Get directories (space-separated)")
        print("  ./pvt_utils.py libs [group]            # List libraries")
        sys.exit(1)
 
    command = sys.argv[1]
 
    if command == "list":
        corners = list_corners()
        for corner in corners:
            print(corner)
 
    elif command == "libs":
        if len(sys.argv) > 2:
            list_libraries(sys.argv[2])
        else:
            list_libraries()
 
    elif command in ["info", "work_dir", "dirs"]:
        if len(sys.argv) < 3:
            print(f"Error: Corner name required for {command}")
            sys.exit(1)
 
        corner = sys.argv[2]
 
        if command == "info":
            info = get_corner_info(corner)
            if info:
                print(f"Work Directory: {info['work_dir']}")
                print("Directories:")
                for dir in info['directories']:
                    print(f"  - {dir}")
            else:
                print(f"Error: Corner '{corner}' not found")
                sys.exit(1)
 
        elif command == "work_dir":
            work_dir = get_work_dir(corner)
            if work_dir:
                print(work_dir)
            else:
                print(f"Error: Corner '{corner}' not found")
                sys.exit(1)
 
        elif command == "dirs":
            dirs = get_directories(corner)
            if dirs:
                # Output directories with proper quoting
                for i, dir in enumerate(dirs):
                    if i > 0:
                        print(" ", end="")
                    print(f'"{dir}"', end="")
                print()  # Add newline at the end
            else:
                print(f"Error: Corner '{corner}' not found")
                sys.exit(1)
 
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
