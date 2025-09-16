#!/bin/bash
 
# Parameters
SOURCE_PATH="/SIM/DFDS_20211231/Personal/ynie/3-LibCharCerti/2024/N2P/0-delivery/0-12_2024_Char_Collaterals/to_CDNS/Netlist/src"
TARGET_PATH="/SIM/DFDS_20211231/Personal/ynie/3-LibCharCerti/2024/N2P/0-delivery/0-12_2024_Char_Collaterals/to_CDNS/Netlist/"
TCL_TARGET_PATH="/SIM/DFDS_20211231/Personal/ynie/3-LibCharCerti/2024/N2P/0-delivery/3-full_netlist_for_runtime_test/cells.tcl"
COPY_FILES=false # Set to true if you want to enable copying files
 
SPECIFIC_SPI_FILES=(
    # Add specific files or keep it empty for all files
    #"INVMDLIMZD0P7BWP130HPNPN3P48CPD.spi"
    #"ND2MDLIMZD0P7BWP130HPNPN3P48CPD.spi"
    #"AOI33M1LIMZD0P7BWP130HPNPN3P48CPD.spi"
)
 
# Convert SPECIFIC_SPI_FILES array to a comma-separated string
SPECIFIC_SPI_FILES_STR=$(IFS=,; echo "${SPECIFIC_SPI_FILES[*]}")
 
# Run the Python script with arguments
/usr/local/python/3.9.10/bin/python3 generate_cells_tcl.py "$SOURCE_PATH" "$TARGET_PATH" "$TCL_TARGET_PATH" "$COPY_FILES" "$SPECIFIC_SPI_FILES_STR"
 
