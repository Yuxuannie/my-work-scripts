import os
import sys
import shutil
 
def parse_lib_base(lib_name):
    parts = lib_name.split('_')
    if len(parts) > 2:
        return '_'.join(parts[:-2]) + '_'
    return lib_name
 
def parse_lib_base_1(lib_name):
    parts = lib_name.split('_')
    if len(parts) > 1:
        return '_'.join(parts[:-1])
    return lib_name
 
def main(target_root_path, rc_type, source_path, corners):
    for corner in corners:
        corner_path = os.path.join(target_root_path, corner)
        if not os.path.exists(corner_path):
            print(f"Corner directory {corner_path} does not exist. Skipping.")
            continue
       
        for lib_base_dir in os.listdir(corner_path):
            lib_base = parse_lib_base(lib_base_dir)
            lib_base_1 = parse_lib_base_1(lib_base_dir)
            print (f"lib_base_1 is {lib_base_1}, it is extacted from {lib_base_dir}")
            target_dir = os.path.join(corner_path, lib_base_dir, "Postprocess")
            if not os.path.exists(target_dir):
                print(f"Target directory {target_dir} does not exist. Skipping.")
                continue
           
            for lib_file in os.listdir(source_path):
                if lib_file.endswith(".lib") and rc_type in lib_file and corner in lib_file:
                    if lib_base in lib_file:
                        for subdir in os.listdir(target_dir):
                            input_source_dir = os.path.join(target_dir, subdir, "input_source")
                            if not os.path.exists(input_source_dir):
                                print(f"input_source_dir does not exist")
                               
                            source_file_path = os.path.join(source_path, lib_file)
                            target_file_path = os.path.join(input_source_dir, lib_file)
                            print(f"Copying from {source_file_path} to {target_file_path}")
                            shutil.copy(source_file_path, target_file_path)
                           
                            # Renaming the copied file
                            pvt_corner = f"{corner}_25c_{rc_type}"
                            new_file_name = f"{lib_base_1}{pvt_corner}_ccs_lib2lib.lib"
                            new_file_path = os.path.join(input_source_dir, new_file_name)
                            print(f"Renaming {target_file_path} to {new_file_path}")
                            os.rename(target_file_path, new_file_path)
 
if __name__ == "__main__":
    if len(sys.argv) < 5:
        print("Usage: merge_script.py <target_root_path> <rc_type> <source_path> <corner1> <corner2> ... <cornerN>")
        sys.exit(1)
 
    target_root_path = sys.argv[1]
    rc_type = sys.argv[2]
    source_path = sys.argv[3]
    corners = sys.argv[4:]
 
    main(target_root_path, rc_type, source_path, corners)
 
 
