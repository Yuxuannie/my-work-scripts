import ldbx, sys, os
 
lib_name = sys.argv[1]
remove_cell_file = sys.argv[2]
output_lib = sys.argv[3]
 
with open(remove_cell_file, "r") as file:
    remove_list = [line.strip() for line in file.readlines()]
 
target_lib = ldbx.read_db(lib_name)
 
all_cell_groups = target_lib.getChildren()
 
remove_object = list()
for each_cell in all_cell_groups:
    if each_cell.getHeader() == "cell":
        each_cell_name = each_cell.getName()
        if each_cell_name in remove_list:
            print("[INFO] Remove Cell : ", each_cell_name)
        #if each_cell_name in ['AIOI21M1LISFOCMZD3BWP130HNPPN3P48CPDELVT','AIOI21M1LISFOCMZD6BWP130HNPPN3P48CPDELVT']:
            remove_object.append( each_cell )
 
target_lib.delGroup(remove_object)
 
folder_path = "after_remove_cell"
 
if not os.path.exists(folder_path):
    os.makedirs(folder_path)
    print(f"folder '{folder_path}' created")
else:
    print(f"folder '{folder_path}' existed")
 
OUTPUT = "after_remove_cell" + '/' + output_lib
 
target_lib.writeDb(OUTPUT, False, False)
 
 
