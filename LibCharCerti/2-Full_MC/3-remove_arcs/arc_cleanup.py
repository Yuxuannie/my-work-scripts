#!/usr/bin/env python3
"""
Script to analyze arc directories across selected corners and find common arcs with CSV files.
Directory structure: corner/arc/
Usage: python arc_cleanup.py --corners corner1,corner2 [--dry-run|--cleanup]
"""
 
import os
import glob
import shutil
import argparse
import sys
from pathlib import Path
 
def find_arcs_with_csv_in_corner(target_dir, corner):
    """Find all arc directories that contain CSV files in a given corner."""
    arcs_with_csv = set()
   
    corner_path = os.path.join(target_dir, corner)
   
    if not os.path.exists(corner_path):
        print(f"Warning: {corner_path} does not exist!")
        return arcs_with_csv
   
    # Get all subdirectories (arcs) in the corner folder
    try:
        for arc_dir in os.listdir(corner_path):
            arc_path = os.path.join(corner_path, arc_dir)
           
            # Check if it's a directory
            if os.path.isdir(arc_path):
                # Check if there are any CSV files in this arc
                csv_files = glob.glob(os.path.join(arc_path, "*.csv"))
                if csv_files:
                    arcs_with_csv.add(arc_dir)
    except PermissionError:
        print(f"Warning: Permission denied accessing {corner_path}")
    except Exception as e:
        print(f"Warning: Error accessing {corner_path}: {e}")
   
    return arcs_with_csv
 
def analyze_corners(target_dir, corners):
    """Analyze selected corners to find common arcs with CSV files."""
   
    print(f"Target Directory: {target_dir}")
    print(f"Analyzing corners: {', '.join(corners)}")
    print("=" * 60)
   
    # Store arcs with CSV for each corner
    corner_arcs = {}
 
    # Find arcs with CSV files in each corner
    for corner in corners:
        print(f"\n{corner}:")
        arcs_with_csv = find_arcs_with_csv_in_corner(target_dir, corner)
        corner_arcs[corner] = arcs_with_csv
        print(f"  Total unique arcs in {corner}: {len(arcs_with_csv)}")
   
    print("\n" + "=" * 60)
   
    # Find intersection - arcs that have CSV files in ALL corners
    if corner_arcs:
        common_arcs = set.intersection(*corner_arcs.values())
    else:
        common_arcs = set()
   
    print(f"\nArcs with CSV files in ALL {len(corners)} corners: {len(common_arcs)}")
    print("-" * 40)
   
    # Sort for better readability
    common_arcs_sorted = sorted(list(common_arcs))
    for i, arc in enumerate(common_arcs_sorted, 1):
        print(f"{i:3d}. {arc}")
   
    print("\nGRAND TOTAL TO REMOVE: {len(common_arcs_sorted)}")
   
    return common_arcs_sorted, corner_arcs
 
def cleanup_directories(common_arcs, target_dir, corners, dry_run=True):
    """Remove arc directories that are not in the common_arcs list."""
   
    common_arcs_set = set(common_arcs)
    removed_count = 0
   
    print("\n" + "=" * 60)
    if dry_run:
        print("DRY RUN - No files will actually be deleted")
    else:
        print("ACTUAL CLEANUP - Directories will be deleted!")
    print("=" * 60)
   
    for corner in corners:
        corner_path = os.path.join(target_dir, corner)
        if not os.path.exists(corner_path):
            print(f"Skipping {corner} - directory does not exist")
            continue
           
        print(f"\nProcessing {corner}...")
        corner_removed = 0
       
        try:
            all_arcs = os.listdir(corner_path)
           
            for arc in all_arcs:
                arc_path = os.path.join(corner_path, arc)
               
                # Only process directories
                if os.path.isdir(arc_path):
                    if arc not in common_arcs_set:
                        if dry_run:
                            print(f"    [DRY RUN] Would remove: {arc}")
                        else:
                            try:
                                shutil.rmtree(arc_path)
                                print(f"    Removed: {arc}")
                            except Exception as e:
                                print(f"    Error removing {arc}: {e}")
                       
                        corner_removed += 1
                        removed_count += 1
           
            print(f"    {corner_removed} directories {'would be' if dry_run else ''} removed from {corner}")
           
        except Exception as e:
            print(f"    Error processing {corner_path}: {e}")
   
    print(f"\nGRAND TOTAL: {removed_count} directories {'would be' if dry_run else ''} removed")
   
    return removed_count
 
def save_arc_list(common_arcs, filename="common_arcs_list.txt"):
    """Save the list of common arcs to a text file."""
    with open(filename, 'w') as f:
        f.write("Arcs with CSV files in all selected corners:\n")
        f.write("=" * 40 + "\n\n")
        for i, arc in enumerate(common_arcs, 1):
            f.write(f"{i:3d}. {arc}\n")
        f.write(f"\nTotal: {len(common_arcs)} arcs\n")
    print(f"\nCommon arcs list saved to: {filename}")
 
def main():
    parser = argparse.ArgumentParser(description='Analyze and cleanup arc directories with CSV files')
    parser.add_argument('--target-dir', required=True,
                       help='Path to the directory containing corner folders')
    parser.add_argument('--corners', required=True,
                       help='Comma-separated list of corners (e.g., ssgnp_0p450v_m40c_DECKS,ssgnp_0p465v_m40c_DECKS)')
   
    action_group = parser.add_mutually_exclusive_group(required=True)
    action_group.add_argument('--dry-run', action='store_true',
                             help='Show what would be deleted without actually deleting')
    action_group.add_argument('--cleanup', action='store_true',
                             help='Actually delete the directories')
    action_group.add_argument('--analyze-only', action='store_true',
                             help='Only analyze and generate reports, no cleanup')
   
    args = parser.parse_args()
   
    # Parse corners
    corners = [c.strip() for c in args.corners.split(',')]
    target_dir = args.target_dir
   
    print("Arc CSV Analysis and Cleanup Tool")
    print("Directory structure: corner/arc/")
    print("=" * 60)
   
    # Check if target directory exists
    if not os.path.exists(target_dir):
        print(f"ERROR: Target directory '{target_dir}' does not exist!")
        return 1
   
    # Analyze the directories
    common_arcs, corner_arcs = analyze_corners(target_dir, corners)
   
    # Save the list to a file
    if common_arcs:
        save_arc_list(common_arcs)
        print(f"Analysis complete. Found {len(common_arcs)} common arcs.")
    else:
        print("\nNo common arcs found across all selected corners!")
        return 1
   
    # Perform action based on arguments
    if args.analyze_only:
        print("\nAnalysis complete. No cleanup performed.")
        return 0
    elif args.dry_run:
        print("\nPerforming dry run...")
        cleanup_directories(common_arcs, target_dir, corners, dry_run=True)
        return 0
    elif args.cleanup:
        print("\nPerforming actual cleanup...")
        cleanup_directories(common_arcs, target_dir, corners, dry_run=False)
        print("\nCleanup completed!")
        return 0
 
if __name__ == "__main__":
    sys.exit(main())
 
