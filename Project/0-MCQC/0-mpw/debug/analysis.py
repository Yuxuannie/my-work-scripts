import glob
import os
import sys
 
argv = sys.argv
ref_path = argv[1]
cmp_path = argv[2]
 
write_buffer = list()
for ref_deck_path in glob.glob(os.path.join(ref_path, "*")):
    # Comparison path
    deck_path_name = os.path.basename(ref_deck_path)
    cmp_deck_path = os.path.join(cmp_path, deck_path_name)
 
    # Comparison value
    if not os.path.exists(cmp_deck_path):
        cmp_value = ''
    else:
        cmp_mt0 = os.path.join(cmp_deck_path, "nominal_sim.mt0")
        with open(cmp_mt0, 'r') as f:
            cmp_lines = f.readlines()
        cmp_cp2d_index = [x.strip()
                          for x in cmp_lines[3].strip().split()].index('cp2d')
        cmp_value = [x.strip()
                     for x in cmp_lines[-1].strip().split()][cmp_cp2d_index]
 
    # Reference value
    ref_mt0 = os.path.join(ref_deck_path, "nominal_sim.mt0")
    if not os.path.exists(ref_mt0):
        ref_value = ''
    else:
        with open(ref_mt0, 'r') as f:
            ref_lines = f.readlines()
 
        ref_cp2d_index = [x.strip()
                          for x in ref_lines[3].strip().split()].index('cp2d')
        ref_value = [x.strip()
                     for x in ref_lines[-1].strip().split()][ref_cp2d_index]
 
    # Store
    write_buffer.append((deck_path_name, ref_value, cmp_value))
 
#[print(x) for x in write_buffer]
[print("%s,%s,%s" % (x[0], x[1], x[2])) for x in write_buffer]
 
