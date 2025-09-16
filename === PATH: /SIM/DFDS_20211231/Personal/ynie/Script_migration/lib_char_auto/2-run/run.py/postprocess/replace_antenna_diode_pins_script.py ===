import logging
import os
 
def setup_logging(log_file):
    """Set up logging configuration"""
    logger = logging.getLogger('replace_antenna_diode_pins')
    logger.setLevel(logging.INFO)
 
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
 
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)
 
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
 
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
 
    return logger
 
def replace_antenna_diode_pins(lib_file, log_file):
    """Replace antenna_diode_related_ground_pins in specified lib files"""
    logger = setup_logging(log_file)
   
    logger.info("===================================================")
    logger.info("Starting the replacement of antenna_diode_related_ground_pins in lib file: %s", lib_file)
   
    try:
        with open(lib_file, 'r') as f:
            content = f.read()
 
        if "antenna_diode_related_ground_pins : VSS VBB;" in content:
            new_content = content.replace("antenna_diode_related_ground_pins : VSS VBB;", 'antenna_diode_related_ground_pins : "VSS VBB";')
            with open(lib_file, 'w') as f:
                f.write(new_content)
            logger.info("Replaced antenna_diode_related_ground_pins in file: %s", lib_file)
        else:
            logger.info("No replacement needed for file: %s", lib_file)
    except Exception as e:
        logger.error("Error processing file %s: %s", lib_file, str(e))
 
    logger.info("Completed the replacement of antenna_diode_related_ground_pins in lib file")
    logger.info("===================================================")
 
if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage: python replace_antenna_diode_pins_script.py <lib_file> <log_file>")
        sys.exit(1)
 
    lib_file = sys.argv[1]
    log_file = sys.argv[2]
    replace_antenna_diode_pins(lib_file, log_file)
 
 
