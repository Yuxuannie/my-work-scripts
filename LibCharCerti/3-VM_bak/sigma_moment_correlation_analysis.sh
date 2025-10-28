#!/bin/bash
 
# Set parameters
run_dir=$(pwd)
# CDNS best recipe
#input_file_path="/SIM/DFDS_20211231/Personal/ynie/3-LibCharCerti/2024/N2P/7-final_results/1-CDNS/R5/moments"
# SNPS best recipe
input_file_path="/SIM/DFDS_20211231/Personal/ynie/3-LibCharCerti/2024/N2P/7-final_results/2-SNPS/R4/moments/"
#corners=("ssgnp_0p450v_m40c" "ssgnp_0p465v_m40c" "ssgnp_0p480v_m40c" "ssgnp_0p495v_m40c")
corners=("ssgnp_0p465v_m40c")
types=("delay" "slew")
 
# Create main output directory with better structure
output_dir="${run_dir}/timing_analysis_results_enhanced"
mkdir -p ${output_dir}
 
# Create subdirectories for better organization
corner_results_dir="${output_dir}/01_corner_results"
voltage_sensitivity_dir="${output_dir}/02_voltage_sensitivity"  # NEW: Phase 1
cross_corner_dir="${output_dir}/03_cross_corner_analysis"
voltage_trend_dir="${output_dir}/04_voltage_trends"
corner_outlier_dir="${output_dir}/05_corner_outlier_analysis"
final_report_dir="${output_dir}/06_final_report"
 
mkdir -p ${corner_results_dir}
mkdir -p ${voltage_sensitivity_dir}
mkdir -p ${cross_corner_dir}
mkdir -p ${voltage_trend_dir}
mkdir -p ${corner_outlier_dir}
mkdir -p ${final_report_dir}
 
# Phase 0: Run original analysis for each corner and type
echo "Phase 0: Running original corner analysis..."
for corner in "${corners[@]}"; do
    for type_name in "${types[@]}"; do
        echo "Processing ${corner} - ${type_name}"
 
        # Create directory for this corner-type combination
        result_dir="${corner_results_dir}/${corner}_${type_name}"
        mkdir -p ${result_dir}
 
        # Parse files and generate data
#        /usr/local/python/3.9.10/bin/python3 parse_timing_files.py\
#            --input_path "${input_file_path}" \
#            --corner "${corner}" \
#            --type "${type_name}" \
#            --output_dir "${result_dir}"
#
#        # Parse files and generate visualizations
#        /usr/local/python/3.9.10/bin/python3 generate_visualizations.py\
#            --data_dir "${result_dir}" \
#            --output_dir "${result_dir}/plots"
    done
done
 
# Phase 1: Run voltage sensitivity analysis (FIXED - now uses main output directory)
echo "Phase 1: Running voltage sensitivity analysis..."
/usr/local/python/3.9.10/bin/python3 voltage_sensitivity_analysis.py \
    --data_dir "${corner_results_dir}" \
    --output_dir "${voltage_sensitivity_dir}"
 
 
# Phase 2: Run voltage trend analysis
#echo "Phase 2: Running voltage trend analysis..."
#/usr/local/python/3.9.10/bin/python3 voltage_trend_analysis.py \
#    --data_dir "${corner_results_dir}" \
#    --output_dir "${voltage_trend_dir}"
 
# Phase 3: Run corner-specific outlier analysis
#echo "Phase 3: Running corner-specific outlier analysis..."
#/usr/local/python/3.9.10/bin/python3 corner_outlier_analysis.py \
#    --data_dir "${corner_results_dir}" \
#    --output_dir "${corner_outlier_dir}"
#
## Phase 5: Generate final HTML report (updated to include Phase 1 results)
#echo "Phase 5: Generating final report..."
#/usr/local/python/3.9.10/bin/python3 generate_report.py \
#    --data_dir "${corner_results_dir}" \
#    --output_dir "${final_report_dir}" \
#    --voltage_sensitivity_dir "${voltage_sensitivity_dir}" \
#    --cross_corner_dir "${cross_corner_dir}" \
#    --voltage_trends_dir "${voltage_trend_dir}" \
#    --corner_outlier_dir "${corner_outlier_dir}"
 
#echo "Analysis complete!"
#echo "Results structure:"
#echo "  - Corner-specific results: ${corner_results_dir}"
#echo "  - Voltage sensitivity analysis: ${voltage_sensitivity_dir}"
#echo "  - Cross-corner analysis: ${cross_corner_dir}"
#echo "  - Voltage trend analysis: ${voltage_trend_dir}"
#echo "  - Corner outlier analysis: ${corner_outlier_dir}"
#echo "  - Final report: ${final_report_dir}/index.html"
 
