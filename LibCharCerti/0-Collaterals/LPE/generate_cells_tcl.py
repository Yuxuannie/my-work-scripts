import os
import sys
import shutil
 
def main():
    # Fetch the command-line arguments
    source_path = sys.argv[1]
    target_path = sys.argv[2]
    tcl_target_path = sys.argv[3]
    copy_files = sys.argv[4].lower() == 'true'
    specific_spi_files = sys.argv[5].split(',')
 
    # Clean empty string from list if there is no specific file
    specific_spi_files = list(filter(None, specific_spi_files))
 
    if specific_spi_files:
        # Use specific selection
        spi_files = specific_spi_files
    else:
        # Default to using all .spi files in the source directory
        spi_files = [f for f in os.listdir(source_path) if f.endswith('.spi')]
 
    # Create a list to store the cell names
    cell_names = []
 
    # Process each .spi file to extract the cell name
    for spi_file in spi_files:
        # Remove the .spi extension to get the cell name
        cell_name = os.path.splitext(spi_file)[0]
        cell_names.append(cell_name)
 
    # Create the TCL file content
    tcl_content = "set cells {\n"
    for cell_name in cell_names:
        tcl_content += f"    {cell_name}\n"
    tcl_content += "}\n"
 
    # Write the TCL content to a file at the specified target path
    with open(tcl_target_path, 'w') as tcl_file:
        tcl_file.write(tcl_content)
 
    print(f"TCL file generated and saved to {tcl_target_path}.")
 
    # Copy .spi files if the flag is set
    if copy_files:
        print("Copying SPI files...")
        for spi_file in spi_files:
            src_file = os.path.join(source_path, spi_file)
            tgt_file = os.path.join(target_path, spi_file)
            if os.path.exists(src_file):
                shutil.copy(src_file, tgt_file)
                print(f"Copied {spi_file} to target directory.")
            else:
                print(f"File {spi_file} not found in source directory.")
        print("File copying completed.")
    else:
        print("File copying not enabled.")
 
if __name__ == "__main__":
    main()
 
