import os
import sys
import glob
 
def clean_paths(input_file, cleaned_file_name, log_file_name):
    cleaned_paths = []
    with open(log_file_name, 'w') as log_file:
        if not os.path.isfile(input_file):
            log_file.write(f"Input file '{input_file}' not found!\n")
            return []
 
        with open(input_file, 'r') as file:
            for line_number, line in enumerate(file, start=1):
                path = line.strip()
                if " - " in path:
                    cleaned_path = path.split(" - ")[-1].strip()
                    cleaned_path = cleaned_path.lstrip('- ').strip()
                    log_file.write(f"Line {line_number}: Extracted path - {cleaned_path}\n")
                else:
                    log_file.write(f"Line {line_number}: Invalid path format detected. Skipping line.\n")
                    continue
 
                if not cleaned_path.endswith('/'):
                    cleaned_path += '/'
 
                log_file.write(f"Line {line_number}: Final cleaned path - {cleaned_path}\n")
                cleaned_paths.append(cleaned_path)
 
    with open(cleaned_file_name, 'w') as cleaned_file:
        for path in cleaned_paths:
            cleaned_file.write(f"{path}\n")
 
    return cleaned_paths
 
def process_paths(cleaned_paths, log_file_name):
    with open(log_file_name, 'a') as log_file:
        for line_number, cleaned_path in enumerate(cleaned_paths, start=1):
            if not os.path.isdir(cleaned_path):
                log_file.write(f"Line {line_number}: Directory does not exist: {cleaned_path}\n")
                continue
 
            try:
                os.chdir(cleaned_path)
                log_files = glob.glob('char*.log')
                if not log_files:
                    log_file.write(f"Line {line_number}: No char*.log files found in {cleaned_path}.\n")
                    continue
 
                for log_filename in log_files:
                    try:
                        with open(log_filename, 'r') as log_f:
                            lines = log_f.readlines()
                            finished_lines = [line for line in lines if "Finished" in line]
                            if finished_lines:
                                last_finished_line = finished_lines[-1].strip()
                                log_file.write(f"Line {line_number}: Last finished line in {log_filename}: {last_finished_line}\n")
                            else:
                                log_file.write(f"Line {line_number}: No 'Finished' string found in {log_filename}.\n")
                    except Exception as e:
                        log_file.write(f"Line {line_number}: Error reading {log_filename}: {e}\n")
 
            except Exception as e:
                log_file.write(f"Line {line_number}: Failed to process directory: {cleaned_path} with error: {e}\n")
            finally:
                os.chdir("..")
 
if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python process_paths.py <input_file> <cleaned_file> <log_file>")
        sys.exit(1)
 
    input_file = sys.argv[1]
    cleaned_file_name = sys.argv[2]
    log_file_name = sys.argv[3]
 
    cleaned_paths = clean_paths(input_file, cleaned_file_name, log_file_name)
    process_paths(cleaned_paths, log_file_name)
 
 
