import pandas as pd
import os
 
def read_csv_files(arc_pattern_mapping_path, arc_headers_mapping_path):
    try:
        arc_pattern_mapping = pd.read_csv(arc_pattern_mapping_path)
        arc_headers_mapping = pd.read_csv(arc_headers_mapping_path)
 
        # Strip whitespace and replace ^M with newline characters in column headers
        arc_headers_mapping.columns = arc_headers_mapping.columns.str.strip().str.replace('\r', '')
 
        # Replace ^M with newline in data
        arc_headers_mapping = arc_headers_mapping.applymap(lambda x: x.replace('\r', '\n') if isinstance(x, str) else x)
 
        print("CSV files read successfully.")
        print("arc_pattern_mapping columns:", arc_pattern_mapping.columns)
        print("arc_headers_mapping columns:", arc_headers_mapping.columns)
        return arc_pattern_mapping, arc_headers_mapping
    except Exception as e:
        print(f"Error reading CSV files: {e}")
        return None, None
 
def find_headers(arc_pattern_mapping, arc_headers_mapping):
    headers_dict = {}
    for index, row in arc_pattern_mapping.iterrows():
        arc_path = row['Arc Path']
        matched_pattern = row['Matched Pattern']
 
        # Find corresponding header in arc_headers_mapping
        header_row = arc_headers_mapping[arc_headers_mapping['Matched Pattern'] == matched_pattern]
        if not header_row.empty:
            headers = header_row.iloc[0]['Headers']
            headers_dict[arc_path] = headers
            print(f"Found header for arc path '{arc_path}': {headers}")
        else:
            print(f"No header found for matched pattern '{matched_pattern}' in arc path '{arc_path}'")
 
    return headers_dict
 
def write_headers_to_file(arc_path, headers):
    try:
        mc_sim_path = os.path.join(arc_path, 'mc_sim.sp')
        if not os.path.exists(mc_sim_path):
            print(f"File not found: {mc_sim_path}")
            return
 
        with open(mc_sim_path, 'r') as file:
            lines = file.readlines()
 
        # Identify the location of "* SPICE options"
        spice_option_index = next((i for i, line in enumerate(lines) if "* SPICE options" in line), None)
 
        # Identify start and end of headers to remove
        thanos_header_index = next((i for i, line in enumerate(lines) if "* THANOS Headers" in line), None)
        constr_pin_param_index = None
 
        if thanos_header_index is not None:
            for i in range(thanos_header_index + 1, len(lines)):
                if lines[i].strip().startswith("* CONSTR_PIN_PARAM"):
                    constr_pin_param_index = i
                    break
 
            # Determine the range of lines to remove
            if constr_pin_param_index is not None:
                # Remove lines from * THANOS Headers to * CONSTR_PIN_PARAM (inclusive)
                lines = lines[:thanos_header_index] + lines[constr_pin_param_index + 1:]
            else:
                # Remove only the * THANOS Headers line
                lines = lines[:thanos_header_index] + lines[thanos_header_index + 1:]
 
        # Prepare new headers to be inserted
        header_lines = [line.strip() + '\n' for line in headers.split('*') if line.strip()]
        new_lines = lines[:spice_option_index] + ['* ' + line for line in header_lines] + lines[spice_option_index:]
 
        with open(mc_sim_path, 'w') as file:
            file.writelines(new_lines)
 
        print(f"Headers written to '{mc_sim_path}' successfully.")
 
    except Exception as e:
        print(f"Error processing file {mc_sim_path}: {e}")
 
def main():
    arc_pattern_mapping_path = 'arc_pattern_mapping.csv'
    arc_headers_mapping_path = 'arc_headers_mapping.csv'
 
    arc_pattern_mapping, arc_headers_mapping = read_csv_files(arc_pattern_mapping_path, arc_headers_mapping_path)
 
    if arc_pattern_mapping is not None and arc_headers_mapping is not None:
        headers_dict = find_headers(arc_pattern_mapping, arc_headers_mapping)
 
        for arc_path, headers in headers_dict.items():
            write_headers_to_file(arc_path, headers)
 
if __name__ == "__main__":
    # Redirect output to a log file
    import sys
    log_file = open('debug.log', 'w')
    sys.stdout = log_file
    sys.stderr = log_file
 
    main()
 
    # Close the log file when done
    log_file.close()
 
