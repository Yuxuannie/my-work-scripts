#!/usr/bin/env python3
#==============================================================================#
# PVT Configuration File
# Owner: Yuxuan Nie
# Last Modified: April 20, 2025
# Version: 1.0
#
# Description: Centralized PVT corner configurations for library and directory
#              mappings. This file is shared across multiple characterization
#              scripts to maintain consistent library selections.
#
# Usage Notes:
#   - Users can easily add/remove directories by commenting/uncommenting lines
#   - Support for flexible library selection using indexes
#   - Common libraries are organized into groups for easier management
#==============================================================================#
 
# Define common library groups for easier management
# Note: Libraries are indexed starting from 0 for specific selection
LIBRARY_GROUPS = {
    'BASE_LIBS': [
        "tcbn03p_bwp143mh117l3p48cpd_base_lvt_100a",    # 0
        "tcbn03p_bwp143mh117l3p48cpd_base_lvtll_100a",  # 1
        # "tcbn03p_bwp143mh117l3p48cpd_base_svt_100a",    # 2
        # "tcbn03p_bwp143mh169l3p48cpd_base_lvt_100a",    # 3
        # "tcbn03p_bwp143mh169l3p48cpd_base_lvtll_100a",  # 4
        # "tcbn03p_bwp143mh169l3p48cpd_base_svt_100a",    # 5
        # "tcbn03p_bwp143mh286l3p48cpd_base_lvt_100a",    # 6
        # "tcbn03p_bwp143mh286l3p48cpd_base_lvtll_100a",  # 7
        # "tcbn03p_bwp143mh286l3p48cpd_base_svt_100a",    # 8
 
    ],
 
    'MB_LIBS': [
        # "tcbn02_bwph130pnpnl3p48cpd_mb_lvt_c230828_093a",       # 0
 
    ],
 
    'CUSTOM_LIBS': [
        # Add any custom libraries here
        # "custom_lib_1",
        # "custom_lib_2",
    ]
}
 
# PVT Corner configurations with flexible directory management
# Usage Examples:
#   - "BASE_LIBS"             : Use all libraries in BASE_LIBS
#   - ("BASE_LIBS", [0])      : Use only BASE_LIBS[0]
#   - ("BASE_LIBS", [0, 3, 5]): Use BASE_LIBS at indexes 0, 3, and 5
#   - ("MB_LIBS", [1, 2])     : Use MB_LIBS at indexes 1 and 2
PVT_CORNERS = {
    "ssgnp_0p54v_m40c_cworst_CCworst_T": {
        "work_dir": "/SIM/DFDS_20211231/Personal/ynie/0-lib_char/2025/Internal/N3P/0-VT_Skew/ssgnp_0p54v_m40c_cworst_CCworst_T/",
        "library_selections": [
            "BASE_LIBS",             # Use all BASE_LIBS
            # ("MB_LIBS", [0, 2]),     # Use only MB_LIBS indexes 0 and 2
            # "CUSTOM_LIBS",         # Uncomment to include all custom libraries
        ],
        "additional_dirs": [
            # Add any corner-specific directories here
            # "special_lib_for_this_corner",
        ]
    },
    "tt_0p54v_m40c_cworst_CCworst_T": {
        "work_dir": "/SIM/DFDS_20211231/Personal/ynie/0-lib_char/2025/Internal/N3P/0-VT_Skew/tt_0p54v_m40c_cworst_CCworst_T/",
        "library_selections": [
            "BASE_LIBS",             # Use all BASE_LIBS
            # ("MB_LIBS", [0, 2]),     # Use only MB_LIBS indexes 0 and 2
            # "CUSTOM_LIBS",         # Uncomment to include all custom libraries
        ],
        "additional_dirs": [
            # Add any corner-specific directories here
            # "special_lib_for_this_corner",
        ]
    },
 
}
