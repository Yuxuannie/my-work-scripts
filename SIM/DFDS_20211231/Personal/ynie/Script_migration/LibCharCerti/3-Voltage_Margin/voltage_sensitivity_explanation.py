#!/usr/bin/env python3
"""
Voltage Sensitivity Analysis Educational Plot Generator - Separate Plots Version
 
This script creates individual educational figures explaining
voltage sensitivity analysis from basic concepts to applications.
Each step is generated as a separate, optimized plot for presentation slides.
"""
 
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.colors import LinearSegmentedColormap, BoundaryNorm
import os
 
# Configure matplotlib for better quality
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['font.size'] = 12
plt.rcParams['axes.titlesize'] = 16
plt.rcParams['axes.labelsize'] = 14
plt.rcParams['xtick.labelsize'] = 12
plt.rcParams['ytick.labelsize'] = 12
 
def create_step1_lib_characterization(output_dir=".", save_format='png'):
    """Create Step 1: Library characterization vs voltage plot with swapped axes."""
    fig, ax = plt.subplots(figsize=(12, 10))
 
    # Sample voltage points and library values - adjusted for more realistic slope
    voltages = np.array([0.450, 0.465, 0.480, 0.495])
    lib_values = np.array([45.2, 47.8, 50.1, 52.9])  # ps, example delay values
 
    # SWAPPED: Plot lib_values on x-axis, voltages on y-axis
    ax.plot(lib_values, voltages, 'bo-', linewidth=3, markersize=10, label='Library Values')
 
    # Add regression line (swapped variables)
    z = np.polyfit(lib_values, voltages, 1)
    p = np.poly1d(z)
    x_line = np.linspace(44, 54, 100)
    ax.plot(x_line, p(x_line), 'r--', linewidth=3, alpha=0.8, label='Linear Fit')
 
    # SWAPPED: Annotations with corrected axes
    ax.set_xlabel('Library Delay (ps)', fontsize=16, fontweight='bold')
    ax.set_ylabel('Supply Voltage (V)', fontsize=16, fontweight='bold')
    ax.set_title('Step 1: Library Characterization\nacross Voltage Corners', fontsize=20, fontweight='bold', pad=20)
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=14, loc='center left')
 
    # Calculate slope in mv/ps units (swapped calculation)
    # Since we swapped axes: slope is now dV/dDelay instead of dDelay/dV
    voltage_sensitivity_mvps = z[0] * 1000  # Convert V/ps to mV/ps
    slope_text = f'Voltage Sensitivity = {voltage_sensitivity_mvps:.3f} mV/ps'
 
    # Position annotation on swapped plot
    mid_delay = (lib_values[0] + lib_values[-1]) / 2
    ax.annotate(slope_text,
                xy=(mid_delay, p(mid_delay)),
                xytext=(mid_delay + 2, p(mid_delay) + 0.01),
                arrowprops=dict(arrowstyle='->', color='red', lw=3),
                fontsize=14, fontweight='bold', color='red',
                bbox=dict(boxstyle="round,pad=0.5", facecolor="white", edgecolor="red", linewidth=2))
 
    # Updated explanation box
    explanation = """Key Concept: Voltage varies linearly with library delay
â€¢ Higher delay â†’ Higher voltage requirement
â€¢ Slope represents voltage sensitivity (mV/ps)
â€¢ Larger coverage beats EDA weakness by mapping
  voltage-delay relationships across full range"""
 
    ax.text(0.02, 0.98, explanation, transform=ax.transAxes, fontsize=12,
            verticalalignment='top', bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))
 
    plt.tight_layout()
    filename = os.path.join(output_dir, f"step1_library_characterization.{save_format}")
    plt.savefig(filename, bbox_inches='tight', facecolor='white')
    plt.close()
    return filename
 
def create_step2_sensitivity_calculation(output_dir=".", save_format='png'):
    """Create Step 2: Sensitivity calculation explanation with corrected mv/ps units."""
    fig, ax = plt.subplots(figsize=(14, 10))
    ax.axis('off')
 
    # Title
    ax.text(0.5, 0.95, 'Step 2: Voltage Sensitivity Calculation',
            ha='center', va='top', fontsize=22, fontweight='bold', transform=ax.transAxes)
 
    # Formula box with corrected units
    formula_lines = [
        "VOLTAGE SENSITIVITY CALCULATION WORKFLOW:",
        "",
        "1) Collect Library values at different voltages:",
        "   â€¢ Lib(0.450V), Lib(0.465V), Lib(0.480V), Lib(0.495V)",
        "",
        "2) Calculate voltage sensitivity using linear regression:",
        "   â€¢ With swapped axes: dV/dLib  [V/ps]",
        "   â€¢ Convert to practical units: dV/dLib Ã— 1000  [mV/ps]",
        "",
        "3) Physical interpretation (CORRECTED UNITS):",
        "   â€¢ Positive sensitivity: Higher delay â†’ Higher voltage needed",
        "   â€¢ Negative sensitivity: Higher delay â†’ Lower voltage needed",
        "   â€¢ Magnitude: How much voltage change needed per ps delay change",
        "",
        "MATHEMATICAL FORMULA (CORRECTED):",
        "   Voltage Sensitivity = (Vâ‚‚ - Vâ‚) / (Libâ‚‚ - Libâ‚) Ã— 1000 [mV/ps]",
        "",
        "LARGER COVERAGE BENEFIT:",
        "   â€¢ Maps voltage-delay relationship across FULL operating range",
        "   â€¢ Beats EDA weakness: No longer limited to discrete corner points"
    ]
 
    formula_text = '\n'.join(formula_lines)
 
    ax.text(0.05, 0.85, formula_text, ha='left', va='top', fontsize=14,
            transform=ax.transAxes, fontfamily='monospace',
            bbox=dict(boxstyle="round,pad=0.8", facecolor="#e8f4fd", edgecolor="#1f77b4", linewidth=3))
 
    # Example calculation with corrected units
    example_lines = [
        "PRACTICAL EXAMPLE (CORRECTED CALCULATION):",
        "",
        "Timing Arc: combinational_NAND2_Y_01_A_01_none_3-4",
        "",
        "Library Values across voltage corners:",
        "â€¢ 0.450V: 45.2 ps",
        "â€¢ 0.465V: 47.8 ps",
        "â€¢ 0.480V: 50.1 ps",
        "â€¢ 0.495V: 52.9 ps",
        "",
        "Voltage Sensitivity Calculation:",
        "Sensitivity = (0.495 - 0.450) / (52.9 - 45.2) Ã— 1000",
        "           = 0.045 / 7.7 Ã— 1000",
        "           = 5.84 mV/ps",
        "",
        "Interpretation: Every 1ps delay increase requires",
        "5.84mV additional voltage for this timing arc",
        "",
        "BEATING EDA WEAKNESS:",
        "â€¢ Traditional EDA: Only checks discrete voltage corners",
        "â€¢ Our approach: Continuous voltage-delay relationship mapping",
        "â€¢ Result: Larger coverage of voltage-dependent behavior"
    ]
 
    example_text = '\n'.join(example_lines)
 
    ax.text(0.05, 0.45, example_text, ha='left', va='top', fontsize=12,
            transform=ax.transAxes, fontfamily='monospace',
            bbox=dict(boxstyle="round,pad=0.8", facecolor="#fff2cc", edgecolor="#d6b656", linewidth=2))
 
    plt.tight_layout()
    filename = os.path.join(output_dir, f"step2_sensitivity_calculation.{save_format}")
    plt.savefig(filename, bbox_inches='tight', facecolor='white')
    plt.close()
    return filename
 
def create_step3_error_types(output_dir=".", save_format='png'):
    """Create Step 3: Error types explanation."""
    fig, ax = plt.subplots(figsize=(14, 10))
    ax.axis('off')
 
    # Title
    ax.text(0.5, 0.95, 'Step 3: Error Types & Calculations',
            ha='center', va='top', fontsize=22, fontweight='bold', transform=ax.transAxes)
 
    error_lines = [
        "ERROR TYPES IN TIMING ANALYSIS:",
        "",
        "ABSOLUTE ERROR (abs_err):",
        "â€¢ Definition: Direct difference between Library and Monte Carlo",
        "â€¢ Formula: abs_err = Lib_value - MC_value  [ps]",
        "â€¢ Usage: Shows actual timing difference in picoseconds",
        "",
        "RELATIVE ERROR (rel_err):",
        "â€¢ Definition: Normalized error by expected value",
        "â€¢ Formula: rel_err = abs_err / denominator  [ratio]",
        "â€¢ Usage: Percentage-based error for comparison across different arcs",
        "",
        "DENOMINATOR CALCULATION (Critical for rel_err):",
        "The denominator depends on the statistical moment being analyzed:",
        "",
        "â€¢ Meanshift: denominator = lib_nominal + MC_meanshift",
        "â€¢ Stddev: denominator = lib_nominal + MC_meanshift + MC_stddev",
        "â€¢ Skewness: denominator = lib_nominal + MC_meanshift + MC_skewness",
        "â€¢ Sigma: denominator = max(|lib_nominal|, MC_sigma)",
        "",
        "ERROR SIGN INTERPRETATION:",
        "â€¢ Negative error: Library < Monte Carlo (Optimistic - Dangerous!)",
        "â€¢ Positive error: Library > Monte Carlo (Pessimistic - Safe)",
        "",
        "WHY THIS MATTERS:",
        "Optimistic errors mean the library underestimates delay,",
        "which can cause timing failures in silicon!"
    ]
 
    error_text = '\n'.join(error_lines)
 
    ax.text(0.05, 0.90, error_text, ha='left', va='top', fontsize=13,
            transform=ax.transAxes, fontfamily='monospace',
            bbox=dict(boxstyle="round,pad=0.8", facecolor="#ffeaa7", edgecolor="#fdcb6e", linewidth=3))
 
    plt.tight_layout()
    filename = os.path.join(output_dir, f"step3_error_types.{save_format}")
    plt.savefig(filename, bbox_inches='tight', facecolor='white')
    plt.close()
    return filename
 
def create_step4_margin_calculation(output_dir=".", save_format='png'):
    """Create Step 4: Voltage margin calculation explanation."""
    fig, ax = plt.subplots(figsize=(14, 10))
    ax.axis('off')
 
    # Title
    ax.text(0.5, 0.95, 'Step 4: Voltage Margin Calculation',
            ha='center', va='top', fontsize=22, fontweight='bold', transform=ax.transAxes)
 
    margin_lines = [
        "VOLTAGE MARGIN CALCULATION:",
        "",
        "CORE FORMULA:",
        "   Voltage_Margin = Sensitivity Ã— |Error|",
        "",
        "WHERE:",
        "â€¢ Sensitivity: ps/mV (from Step 2 - slope calculation)",
        "â€¢ Error: ps (abs_err) or ratio (rel_err Ã— denominator)",
        "â€¢ Margin: mV needed to compensate for the timing error",
        "",
        "PHYSICAL INTERPRETATION:",
        "\"How much additional voltage margin is needed",
        " to compensate for this specific timing error?\"",
        "",
        "DETAILED EXAMPLE:",
        "Given:",
        "â€¢ Sensitivity = 0.171 ps/mV (from Step 2)",
        "â€¢ abs_err = -2.3 ps (optimistic error - library underestimates)",
        "",
        "Calculation:",
        "â€¢ Margin = 0.171 Ã— |âˆ’2.3| = 0.171 Ã— 2.3 = 0.393 mV",
        "",
        "BUSINESS IMPACT:",
        "â€¢ Need 0.393 mV extra voltage margin for this timing arc",
        "â€¢ This compensates for the 2.3 ps optimistic error",
        "â€¢ Ensures timing closure under process variation",
        "â€¢ Prevents potential silicon timing failures"
    ]
 
    margin_text = '\n'.join(margin_lines)
 
    ax.text(0.05, 0.90, margin_text, ha='left', va='top', fontsize=13,
            transform=ax.transAxes, fontfamily='monospace',
            bbox=dict(boxstyle="round,pad=0.8", facecolor="#d1f2eb", edgecolor="#00b894", linewidth=3))
 
    plt.tight_layout()
    filename = os.path.join(output_dir, f"step4_margin_calculation.{save_format}")
    plt.savefig(filename, bbox_inches='tight', facecolor='white')
    plt.close()
    return filename
 
def create_step5_pass_rate_vs_margin(output_dir=".", save_format='png'):
    """Create Step 5: Pass rate improvement vs applied voltage margin."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
 
    # Voltage margins applied
    margins = np.array([0, 1, 2, 3, 4, 5, 6, 7])
 
    # Realistic pass rate data based on actual analysis
    # Different parameters have different baseline pass rates and improvement curves
    late_sigma_pass_rates = np.array([87.6, 87.8, 94.3, 97.3, 98.9, 99.2, 99.7, 99.7])
    std_pass_rates = np.array([98.1, 98.1, 99.2, 99.7, 99.7, 99.7, 100, 100])
    skew_pass_rates = np.array([92.2, 92.2, 92.2, 94.9, 99.7, 100, 100, 100])
    meanshift_pass_rates = np.array([81.6, 82.7, 98.9, 99.7, 99.7, 99.7, 99.7, 99.7])
 
    # Plot pass rate curves
    ax1.plot(margins, late_sigma_pass_rates, 'o-', linewidth=3, markersize=8,
            label='late_sigma', color='#d73027')
    ax1.plot(margins, std_pass_rates, 's-', linewidth=3, markersize=8,
            label='Std', color='#1a9850')
    ax1.plot(margins, skew_pass_rates, '^-', linewidth=3, markersize=8,
            label='Skew', color='#fee08b')
    ax1.plot(margins, meanshift_pass_rates, 'D-', linewidth=3, markersize=8,
            label='Meanshift', color='#4575b4')
 
    # Add target pass rate line
    ax1.axhline(y=95, color='gray', linestyle='--', linewidth=2, alpha=0.7, label='95% Target')
 
    # Format left plot
    ax1.set_xlabel('Applied Voltage Margin (mV)', fontsize=14, fontweight='bold')
    ax1.set_ylabel('Pass Rate (%)', fontsize=14, fontweight='bold')
    ax1.set_title('Pass Rate Improvement with Voltage Margin', fontsize=16, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.legend(fontsize=12)
    ax1.set_ylim(75, 102)
 
    # Add annotations for key insights
    ax1.annotate('Sweet Spot:\n2-3mV achieves\n95% target',
                xy=(2.5, 95), xytext=(4.5, 88),
                arrowprops=dict(arrowstyle='->', color='darkgreen', lw=2),
                fontsize=11, fontweight='bold', color='darkgreen',
                bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgreen", alpha=0.8))
 
    # Right plot: Outliers remaining vs margin
    # Calculate remaining outliers (inverse of pass rate)
    late_sigma_outliers = 100 - late_sigma_pass_rates
    std_outliers = 100 - std_pass_rates
    skew_outliers = 100 - skew_pass_rates
    meanshift_outliers = 100 - meanshift_pass_rates
 
    ax2.plot(margins, late_sigma_outliers, 'o-', linewidth=3, markersize=8,
            label='late_sigma', color='#d73027')
    ax2.plot(margins, std_outliers, 's-', linewidth=3, markersize=8,
            label='Std', color='#1a9850')
    ax2.plot(margins, skew_outliers, '^-', linewidth=3, markersize=8,
            label='Skew', color='#fee08b')
    ax2.plot(margins, meanshift_outliers, 'D-', linewidth=3, markersize=8,
            label='Meanshift', color='#4575b4')
 
    # Add target outlier rate line
    ax2.axhline(y=5, color='gray', linestyle='--', linewidth=2, alpha=0.7, label='5% Target')
 
    # Format right plot
    ax2.set_xlabel('Applied Voltage Margin (mV)', fontsize=14, fontweight='bold')
    ax2.set_ylabel('Remaining Outliers (%)', fontsize=14, fontweight='bold')
    ax2.set_title('Outlier Reduction with Voltage Margin', fontsize=16, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    ax2.legend(fontsize=12)
    ax2.set_ylim(0, 25)
 
    # Add business insight annotation
    ax2.annotate('Meanshift most\nsensitive to\nvoltage margin',
                xy=(1.5, 17.3), xytext=(4, 20),
                arrowprops=dict(arrowstyle='->', color='darkblue', lw=2),
                fontsize=11, fontweight='bold', color='darkblue',
                bbox=dict(boxstyle="round,pad=0.3", facecolor="lightblue", alpha=0.8))
 
    plt.suptitle('Step 5: Quantifying Voltage Margin Benefits', fontsize=18, fontweight='bold', y=0.95)
    plt.tight_layout()
 
    filename = os.path.join(output_dir, f"step5_pass_rate_vs_margin.{save_format}")
    plt.savefig(filename, bbox_inches='tight', facecolor='white')
    plt.close()
    return filename
 
def create_step6_pass_rate_analysis(output_dir=".", save_format='png'):
    """Create Step 6: Pass rate analysis with voltage margin benefits."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 10))
 
    # Create sample pass rate data
    parameters = ['early_sigma', 'late_sigma', 'Std', 'Skew', 'Meanshift']
    margins = [0, 1, 2, 3, 4, 5, 6, 7]
 
    # Sample pass rate matrix (realistic values from actual analysis)
    pass_rates = np.array([
        [100, 100, 100, 100, 100, 100, 100, 100],  # early_sigma
        [87.6, 87.8, 94.3, 97.3, 98.9, 99.2, 99.7, 99.7],  # late_sigma
        [98.1, 98.1, 99.2, 99.7, 99.7, 99.7, 100, 100],  # Std
        [92.2, 92.2, 92.2, 94.9, 99.7, 100, 100, 100],  # Skew
        [81.6, 82.7, 98.9, 99.7, 99.7, 99.7, 99.7, 99.7]   # Meanshift
    ])
 
    # Create custom colormap matching voltage sensitivity analysis style
    # Green-focused colormap: Red -> Orange -> Light Green -> Green
    colors = [
        '#d73027',  # Dark Red for 70-85%
        '#fc8d59',  # Orange for 85-90%
        '#74c476',  # Medium Green for 90-95%
        '#a1d99b',  # Light Green for 95-98%
        '#e5f5e0'   # Very Light Green for 98-100%
    ]
 
    cmap = LinearSegmentedColormap.from_list('voltage_analysis', colors, N=256)
 
    # Create heatmap
    im1 = ax1.imshow(pass_rates, cmap=cmap, vmin=80, vmax=100, aspect='auto')
 
    # Add medium grey grid lines for clear cell separation
    for x in range(len(margins) + 1):
        ax1.axvline(x - 0.5, color='#666666', linewidth=1.5)
    for y in range(len(parameters) + 1):
        ax1.axhline(y - 0.5, color='#666666', linewidth=1.5)
 
    # Set ticks and labels
    ax1.set_xticks(range(len(margins)))
    ax1.set_yticks(range(len(parameters)))
    ax1.set_xticklabels([f'{m}mV' for m in margins])
    ax1.set_yticklabels(parameters)
 
    # Add percentage values with improved text color selection
    for i in range(len(parameters)):
        for j in range(len(margins)):
            value = pass_rates[i, j]
            # Choose text color based on background
            if value >= 95:
                text_color = '#2d5016'  # Dark green for very light backgrounds
                font_weight = 'normal'
            elif value >= 90:
                text_color = '#1a4d1a'  # Darker green for medium backgrounds
                font_weight = 'bold'
            elif value >= 85:
                text_color = 'black'
                font_weight = 'bold'
            else:
                text_color = 'white'  # White for dark backgrounds
                font_weight = 'bold'
 
            ax1.text(j, i, f'{value:.1f}%', ha='center', va='center',
                   color=text_color, fontweight=font_weight, fontsize=11)
 
    # Labels and title for heatmap
    ax1.set_xlabel('Applied Voltage Margin (mV)', fontsize=14, fontweight='bold')
    ax1.set_ylabel('Timing Parameters', fontsize=14, fontweight='bold')
    ax1.set_title('Pass Rate vs. Voltage Margin', fontsize=16, fontweight='bold')
 
    # Add colorbar
    cbar1 = plt.colorbar(im1, ax=ax1, shrink=0.8)
    cbar1.set_label('Pass Rate (%)', fontsize=12)
    cbar1.set_ticks([80, 85, 90, 95, 100])
 
    # Remove spines for cleaner look
    for spine in ax1.spines.values():
        spine.set_visible(False)
 
    # Right plot: Benefits analysis
    ax2.axis('off')
 
    benefits_text = """VOLTAGE MARGIN BENEFITS ANALYSIS:
 
PASS RATE INTERPRETATION:
â€¢ Red areas: Most arcs fail timing criteria (<85%)
â€¢ Orange areas: Moderate pass rate (85-90%) 
â€¢ Light Green: Good pass rate (90-95%)
â€¢ Green areas: Excellent pass rate (>95% - Target achieved)
 
KEY INSIGHTS:
 
1. BASELINE (0mV margin):
   â€¢ Shows natural pass rates without voltage assistance
   â€¢ Identifies problematic parameters (red/orange zones)
   â€¢ Meanshift and late_sigma need attention
 
2. SWEET SPOT (1-3mV):
   â€¢ Significant improvement for sensitive parameters
   â€¢ Cost-effective voltage margin investment
   â€¢ Biggest return on investment
   â€¢ Most parameters reach >95% target
 
3. DIMINISHING RETURNS (4-7mV):
   â€¢ Minimal additional improvement
   â€¢ May be needed for critical corner cases
   â€¢ Higher power/performance cost
 
DESIGN RECOMMENDATION:
â€¢ Target: 2-3mV voltage margin
â€¢ Achieves >95% pass rate for most parameters
â€¢ Optimal balance between timing closure and power
 
BUSINESS VALUE:
â€¢ Reduces silicon respins due to timing failures
â€¢ Enables aggressive performance targets
â€¢ Quantifies voltage margin requirements
â€¢ Data-driven decision making"""
 
    ax2.text(0.05, 0.95, benefits_text, transform=ax2.transAxes, fontsize=11.5,
            verticalalignment='top', fontfamily='monospace',
            bbox=dict(boxstyle="round,pad=0.8", facecolor="#f0f8ff", edgecolor="#4682b4", linewidth=2))
 
    plt.suptitle('Step 6: Pass Rate Analysis - Quantifying Voltage Margin Benefits',
                fontsize=20, fontweight='bold', y=0.95)
 
    plt.tight_layout()
    filename = os.path.join(output_dir, f"step6_pass_rate_analysis.{save_format}")
    plt.savefig(filename, bbox_inches='tight', facecolor='white')
    plt.close()
    return filename
 
def create_step7_paradigm_shift(output_dir=".", save_format='png'):
    """Create Step 7: Explaining the paradigm shift and business value with fixed priority alignment."""
    fig = plt.figure(figsize=(16, 12))
 
    # Create a complex layout with multiple sections
    gs = gridspec.GridSpec(3, 2, height_ratios=[1, 1.2, 1], width_ratios=[1, 1],
                          hspace=0.3, wspace=0.2)
 
    # Top section: Traditional vs New Approach - ALIGNED FLOWS
    ax1 = fig.add_subplot(gs[0, :])
    ax1.axis('off')
 
    # Clear flow comparison
    flow_comparison = """
    TRADITIONAL FLOW                                    NEW VOLTAGE SENSITIVITY FLOW
    ================                                    ============================
   
    1. Run timing analysis                              1. Run timing analysis + Extract voltage sensitivity
    2. Identify timing violations                       2. Calculate voltage margin required for each violation
    3. Prioritize by ERROR MAGNITUDE (ps)               3. Prioritize by VOLTAGE MARGIN NEEDED (mV)
    4. Work on largest errors first                     4. Work on highest voltage margin errors first
    5. Accept/reject based on absolute error            5. Accept/reject based on customer voltage tolerance
   
    LIMITATION: Large but easily fixable errors        ADVANTAGE: Focus engineering effort where it matters most
    get highest priority, wasting resources             and enable voltage-margin based waivers
    """
 
    ax1.text(0.05, 0.85, flow_comparison, ha='left', va='top', fontsize=11,
             transform=ax1.transAxes, fontfamily='monospace',
             bbox=dict(boxstyle="round,pad=0.8", facecolor="#f0f8ff", edgecolor="#4682b4", linewidth=2))
 
    # Middle section: FIXED Outlier reprioritization visualization
    ax2 = fig.add_subplot(gs[1, 0])
 
    # Sample data showing error vs voltage margin
    np.random.seed(42)
    error_magnitudes = np.array([5.2, 8.1, 3.7, 12.4, 6.8, 2.1, 15.7, 4.9])
    voltage_margins = np.array([0.8, 1.2, 2.1, 1.5, 4.8, 0.5, 2.3, 6.2])
 
    # NEW APPROACH: Priority by voltage margin (higher margin = higher priority number = worse)
    # Sort indices by voltage margin DESCENDING (highest margin gets priority 1, lowest gets priority 8)
    new_priority_indices = np.argsort(voltage_margins)[::-1]  # Descending order
 
    # Color coding for NEW approach based on voltage margin thresholds
    def get_color_by_voltage_margin(vm):
        if vm > 4:
            return 'red'      # Critical - very high voltage margin needed
        elif vm > 2:
            return 'orange'   # High voltage margin needed
        elif vm > 1:
            return 'yellow'   # Moderate voltage margin needed
        else:
            return 'green'    # Low voltage margin needed
 
    colors_new = [get_color_by_voltage_margin(vm) for vm in voltage_margins]
 
    # Create bubble chart for NEW approach
    scatter = ax2.scatter(error_magnitudes, voltage_margins,
                         s=300, c=colors_new, alpha=0.7, edgecolors='black', linewidth=2)
 
    # Add CORRECTED priority numbers for new approach
    # Priority 1 = highest voltage margin (worst), Priority 8 = lowest voltage margin (best)
    for i, (err, vm) in enumerate(zip(error_magnitudes, voltage_margins)):
        priority = np.where(new_priority_indices == i)[0][0] + 1  # +1 to start from 1
        text_color = 'white' if get_color_by_voltage_margin(vm) in ['red', 'orange'] else 'black'
        ax2.annotate(f'{priority}', (err, vm), ha='center', va='center',
                    fontsize=12, fontweight='bold', color=text_color)
 
    ax2.set_xlabel('Error Magnitude (ps)', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Voltage Margin Required (mV)', fontsize=12, fontweight='bold')
    ax2.set_title('NEW PRIORITIZATION:\nBy Voltage Margin\n(Lower number = Higher priority)',
                 fontsize=14, fontweight='bold', color='green')
    ax2.grid(True, alpha=0.3)
 
    # Add threshold lines and legend for NEW approach
    ax2.axhline(y=4, color='red', linestyle='--', alpha=0.7, linewidth=2)
    ax2.axhline(y=2, color='orange', linestyle='--', alpha=0.7, linewidth=1)
    ax2.axhline(y=1, color='gold', linestyle='--', alpha=0.7, linewidth=1)
    ax2.text(2, 4.2, 'Critical: >4mV', fontsize=9, color='red', fontweight='bold')
    ax2.text(2, 2.2, 'High: >2mV', fontsize=9, color='orange', fontweight='bold')
    ax2.text(2, 1.2, 'Moderate: >1mV', fontsize=9, color='gold', fontweight='bold')
 
    # Middle right section: FIXED Traditional prioritization
    ax3 = fig.add_subplot(gs[1, 1])
 
    # TRADITIONAL APPROACH: Priority by error magnitude (higher error = higher priority number = worse)
    traditional_priority_indices = np.argsort(error_magnitudes)[::-1]  # Descending order
 
    # Color coding for TRADITIONAL approach based on error magnitude thresholds
    def get_color_by_error_magnitude(err):
        if err > 12:
            return 'red'      # Critical - very large error
        elif err > 8:
            return 'orange'   # Large error
        elif err > 4:
            return 'yellow'   # Moderate error
        else:
            return 'green'    # Small error
 
    colors_trad = [get_color_by_error_magnitude(err) for err in error_magnitudes]
 
    # Create bubble chart for TRADITIONAL approach
    scatter2 = ax3.scatter(error_magnitudes, voltage_margins,
                          s=300, c=colors_trad, alpha=0.7, edgecolors='black', linewidth=2)
 
    # Add CORRECTED priority numbers for traditional approach
    # Priority 1 = highest error (worst), Priority 8 = lowest error (best)
    for i, (err, vm) in enumerate(zip(error_magnitudes, voltage_margins)):
        priority = np.where(traditional_priority_indices == i)[0][0] + 1  # +1 to start from 1
        text_color = 'white' if get_color_by_error_magnitude(err) in ['red', 'orange'] else 'black'
        ax3.annotate(f'{priority}', (err, vm), ha='center', va='center',
                    fontsize=12, fontweight='bold', color=text_color)
 
    ax3.set_xlabel('Error Magnitude (ps)', fontsize=12, fontweight='bold')
    ax3.set_ylabel('Voltage Margin Required (mV)', fontsize=12, fontweight='bold')
    ax3.set_title('TRADITIONAL PRIORITIZATION:\nBy Error Magnitude\n(Lower number = Higher priority)',
                 fontsize=14, fontweight='bold', color='red')
    ax3.grid(True, alpha=0.3)
 
    # Add threshold lines and legend for TRADITIONAL approach
    ax3.axvline(x=12, color='red', linestyle='--', alpha=0.7, linewidth=2)
    ax3.axvline(x=8, color='orange', linestyle='--', alpha=0.7, linewidth=1)
    ax3.axvline(x=4, color='gold', linestyle='--', alpha=0.7, linewidth=1)
    ax3.text(12.5, 5.5, 'Critical:\n>12ps', fontsize=9, color='red', fontweight='bold')
    ax3.text(8.5, 4.5, 'Large:\n>8ps', fontsize=9, color='orange', fontweight='bold')
    ax3.text(4.5, 3.5, 'Moderate:\n>4ps', fontsize=9, color='gold', fontweight='bold')
 
    # Bottom section: Enhanced Key insights with coverage and EDA benefits
    ax4 = fig.add_subplot(gs[2, :])
    ax4.axis('off')
 
    insights_text = """KEY BENEFITS: LARGER COVERAGE & BEATING EDA WEAKNESSES
 
LARGER COVERAGE BENEFITS:
â€¢ Voltage sensitivity analysis covers ALL voltage-delay relationships across full operating range
â€¢ Traditional EDA tools only check discrete corner points - miss intermediate voltage behavior
â€¢ Continuous voltage mapping reveals hidden sensitivities that corner-based analysis misses
â€¢ Enables comprehensive coverage of voltage-dependent timing behavior
 
BEATING EDA WEAKNESSES:
â€¢ Traditional EDA: Binary pass/fail decisions based on static margins
â€¢ New approach: Dynamic voltage-aware certification that adapts to actual design flexibility
â€¢ Overcomes static timing analysis limitations by incorporating voltage margin as design parameter
â€¢ Replaces conservative guard-banding with precise, data-driven voltage requirements
 
SMART ENGINEERING PRIORITIZATION:
â€¢ Traditional: Focus on 15.7ps error first (priority #1) â†’ May waste effort on easily fixable issues
â€¢ New Approach: Focus on 6.2mV margin error first (priority #1) â†’ Address truly difficult problems
â€¢ Engineering resources directed where voltage margins are hardest to achieve
â€¢ Quantifies exactly which errors are voltage-correctable vs requiring design changes
 
BUSINESS VALUE THROUGH VOLTAGE-AWARE CERTIFICATION:
â€¢ Enable aggressive performance targets with measurable voltage margin requirements
â€¢ Reduce silicon respins by identifying voltage-correctable vs design-critical timing issues 
â€¢ Support ultra-low voltage (ULV) designs with precise voltage sensitivity characterization
â€¢ Data-driven customer negotiations based on their actual voltage margin tolerance"""
 
    ax4.text(0.05, 0.95, insights_text, ha='left', va='top', fontsize=11,
             transform=ax4.transAxes, fontfamily='monospace',
             bbox=dict(boxstyle="round,pad=0.8", facecolor="#e8f4fd", edgecolor="#1f77b4", linewidth=3))
 
    plt.suptitle('Step 7: Voltage Sensitivity Analysis - Paradigm Shift in Timing Certification',
                fontsize=20, fontweight='bold', y=0.98)
 
    plt.tight_layout()
    filename = os.path.join(output_dir, f"step7_paradigm_shift.{save_format}")
    plt.savefig(filename, bbox_inches='tight', facecolor='white')
    plt.close()
    return filename
 
def generate_individual_plots(output_dir=".", steps_to_generate=None, save_format='png'):
    """
    Generate individual plots for voltage sensitivity analysis explanation.
 
    Args:
        output_dir: Directory to save the plots
        steps_to_generate: List of step numbers to generate (1-7). If None, generates all.
        save_format: File format ('png', 'pdf', 'svg')
 
    Returns:
        Dictionary mapping step numbers to generated filenames
    """
 
    if steps_to_generate is None:
        steps_to_generate = [1, 2, 3, 4, 5, 6, 7]
 
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
 
    generated_files = {}
 
    step_functions = {
        1: create_step1_lib_characterization,
        2: create_step2_sensitivity_calculation,
        3: create_step3_error_types,
        4: create_step4_margin_calculation,
        5: create_step5_pass_rate_vs_margin,  # Updated function name
        6: create_step6_pass_rate_analysis,
        7: create_step7_paradigm_shift       # New step
    }
 
    print("Generating voltage sensitivity analysis explanation plots...")
    print(f"Output directory: {output_dir}")
    print(f"Format: {save_format}")
    print(f"Steps to generate: {steps_to_generate}")
    print("-" * 50)
 
    for step_num in steps_to_generate:
        if step_num in step_functions:
            try:
                print(f"Generating Step {step_num}...")
                filename = step_functions[step_num](output_dir, save_format)
                generated_files[step_num] = filename
                print(f"Yes!Step {step_num} saved as: {filename}")
            except Exception as e:
                print(f"No! Error generating Step {step_num}: {str(e)}")
                import traceback
                traceback.print_exc()
        else:
            print(f"No! Invalid step number: {step_num}")
 
    print("-" * 50)
    print(f"Generated {len(generated_files)} plots successfully!")
 
    return generated_files
def main():
    """Generate voltage sensitivity explanation plots with user options."""
    import argparse
 
    parser = argparse.ArgumentParser(description='Generate voltage sensitivity analysis explanation plots')
    parser.add_argument('--output_dir', type=str, default='voltage_sensitivity_plots',
                       help='Output directory for plots (default: voltage_sensitivity_plots)')
    parser.add_argument('--steps', type=str, default='1,2,3,4,5,6,7',
                       help='Comma-separated list of steps to generate (default: 1,2,3,4,5,6,7)')
    parser.add_argument('--format', type=str, default='png', choices=['png', 'pdf', 'svg'],
                       help='Output format (default: png)')
    parser.add_argument('--dpi', type=int, default=300,
                       help='Resolution in DPI (default: 300)')
 
    args = parser.parse_args()
 
    # Set DPI
    plt.rcParams['figure.dpi'] = args.dpi
    plt.rcParams['savefig.dpi'] = args.dpi
 
    # Parse steps
    try:
        steps_to_generate = [int(s.strip()) for s in args.steps.split(',')]
    except ValueError:
        print("Error: Invalid steps format. Use comma-separated numbers (e.g., '1,2,3')")
        return
 
    # Generate plots
    generated_files = generate_individual_plots(
        output_dir=args.output_dir,
        steps_to_generate=steps_to_generate,
        save_format=args.format
    )
 
    # Print summary
    print(f"\nSUMMARY:")
    print(f"Generated {len(generated_files)} plots in {args.output_dir}/")
    for step_num, filename in generated_files.items():
        print(f"  Step {step_num}: {os.path.basename(filename)}")
 
if __name__ == "__main__":
    main()
