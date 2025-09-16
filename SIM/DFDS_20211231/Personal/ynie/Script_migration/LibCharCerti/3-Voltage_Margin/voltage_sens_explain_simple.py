import matplotlib.pyplot as plt
import numpy as np
import os
import matplotlib.gridspec as gridspec
from matplotlib.patches import FancyBboxPatch, Rectangle
import matplotlib.patches as mpatches
 
def create_basic_tutorial_plots(output_dir=".", save_format='png'):
    """
    Generate basic level voltage sensitivity explanation plots using inverter example.
    """
    os.makedirs(output_dir, exist_ok=True)
    generated_files = {}
 
    # Plot 1: Library Characterization Basics
    generated_files[1] = create_plot1_library_basics(output_dir, save_format)
 
    # Plot 2: Monte Carlo vs Library Problem
    generated_files[2] = create_plot2_mc_vs_library(output_dir, save_format)
 
    # Plot 3: Voltage Sensitivity Calculation
    generated_files[3] = create_plot3_sensitivity_calculation(output_dir, save_format)
 
    # Plot 4: Voltage Adjustment Solution
    generated_files[4] = create_plot4_voltage_adjustment(output_dir, save_format)
 
    # Plot 5: Complete Solution Overview
    generated_files[5] = create_plot5_complete_solution(output_dir, save_format)
 
    return generated_files
 
def create_plot1_library_basics(output_dir=".", save_format='png'):
    """Plot 1: Basic library characterization with two voltage points."""
    fig, ax = plt.subplots(figsize=(12, 8))
 
    # Library data points
    voltages = np.array([0.45, 0.465])
    delays = np.array([90, 10])  # Using user's exact numbers
 
    # Plot the two library points
    ax.plot(voltages, delays, 'bo-', linewidth=4, markersize=15, label='Library Data Points')
 
    # Add point annotations
    ax.annotate('Library Point 1:\n90ps @ 0.45V',
                xy=(0.45, 90), xytext=(0.435, 110),
                arrowprops=dict(arrowstyle='->', lw=2, color='blue'),
                fontsize=14, fontweight='bold', color='blue',
                bbox=dict(boxstyle="round,pad=0.5", facecolor="lightblue", alpha=0.8))
 
    ax.annotate('Library Point 2:\n10ps @ 0.465V',
                xy=(0.465, 10), xytext=(0.475, 30),
                arrowprops=dict(arrowstyle='->', lw=2, color='blue'),
                fontsize=14, fontweight='bold', color='blue',
                bbox=dict(boxstyle="round,pad=0.5", facecolor="lightblue", alpha=0.8))
 
    # Styling
    ax.set_xlabel('Supply Voltage (V)', fontsize=16, fontweight='bold')
    ax.set_ylabel('Delay (ps)', fontsize=16, fontweight='bold')
    ax.set_title('Step 1: Library Characterization - Inverter Example\nTwo Voltage Points Available',
                fontsize=18, fontweight='bold', pad=20)
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=14)
 
    # Add explanation box
    explanation = """LIBRARY CHARACTERIZATION BASICS:
 
ðŸ“š What we have: Two characterized points for an inverter
â€¢ Point 1: 90ps delay at 0.45V (ULV scenario)
â€¢ Point 2: 10ps delay at 0.465V (higher voltage)
 
ðŸŽ¯ Challenge: Production characterization is expensive
â€¢ Cannot easily re-characterize entire library
â€¢ Need to work with existing data points
â€¢ Must find ways to address potential inaccuracies"""
 
    ax.text(0.02, 0.98, explanation, transform=ax.transAxes, fontsize=11,
            verticalalignment='top', fontfamily='monospace',
            bbox=dict(boxstyle='round,pad=0.8', facecolor='#fff2cc', edgecolor='#d6b656', linewidth=2))
 
    plt.tight_layout()
    filename = os.path.join(output_dir, f"basic_step1_library_characterization.{save_format}")
    plt.savefig(filename, bbox_inches='tight', facecolor='white', dpi=300)
    plt.close()
    return filename
 
def create_plot2_mc_vs_library(output_dir=".", save_format='png'):
    """Plot 2: Monte Carlo vs Library comparison showing the problem."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
 
    # Left plot: The problem visualization
    voltages = [0.45]
    lib_delays = [90]
    mc_delays = [100]
 
    x_pos = np.arange(len(voltages))
    width = 0.35
 
    bars1 = ax1.bar(x_pos - width/2, lib_delays, width, label='Library Value',
                    color='lightblue', edgecolor='blue', linewidth=2)
    bars2 = ax1.bar(x_pos + width/2, mc_delays, width, label='Monte Carlo (Golden)',
                    color='lightcoral', edgecolor='red', linewidth=2)
 
    # Add value labels on bars
    ax1.text(x_pos[0] - width/2, lib_delays[0] + 2, '90ps', ha='center', va='bottom',
             fontsize=14, fontweight='bold', color='blue')
    ax1.text(x_pos[0] + width/2, mc_delays[0] + 2, '100ps', ha='center', va='bottom',
             fontsize=14, fontweight='bold', color='red')
 
    # Highlight the error
    error_arrow = ax1.annotate('', xy=(x_pos[0] + width/2, 90), xytext=(x_pos[0] + width/2, 100),
                              arrowprops=dict(arrowstyle='<->', lw=3, color='red'))
    ax1.text(x_pos[0] + width/2 + 0.1, 95, '10ps\nOptimistic\nError', ha='left', va='center',
             fontsize=12, fontweight='bold', color='red',
             bbox=dict(boxstyle="round,pad=0.3", facecolor="white", edgecolor="red"))
 
    ax1.set_xlabel('Voltage Point', fontsize=14, fontweight='bold')
    ax1.set_ylabel('Delay (ps)', fontsize=14, fontweight='bold')
    ax1.set_title('The Problem: Library vs Reality\n@ 0.45V (ULV Scenario)',
                 fontsize=16, fontweight='bold')
    ax1.set_xticks(x_pos)
    ax1.set_xticklabels(['0.45V'])
    ax1.legend(fontsize=12)
    ax1.grid(True, alpha=0.3)
 
    # Right plot: Problem explanation
    ax2.axis('off')
    problem_text = """THE OPTIMISTIC ERROR PROBLEM:
 
ðŸš¨ WHAT HAPPENED:
â€¢ Library says: 90ps delay @ 0.45V
â€¢ Monte Carlo (actual): 100ps delay @ 0.45V
â€¢ Result: 10ps optimistic error in library
 
âš ï¸ WHY THIS MATTERS:
â€¢ Library is too optimistic about performance
â€¢ Real silicon may not meet timing expectations
â€¢ Designs based on library may fail in production
 
ðŸ’° WHY WE CAN'T JUST RE-CHARACTERIZE:
â€¢ Production characterization is extremely expensive
â€¢ Requires extensive silicon testing and measurements
â€¢ Time-consuming process affecting product schedules
â€¢ Need alternative solution using existing data
 
ðŸŽ¯ VOLTAGE SENSITIVITY SOLUTION:
â€¢ Use existing voltage data points to understand trends
â€¢ Calculate how voltage changes affect delay
â€¢ Apply voltage adjustments instead of re-characterization
â€¢ Cost-effective way to address library inaccuracies"""
 
    ax2.text(0.05, 0.95, problem_text, ha='left', va='top', fontsize=12,
             transform=ax2.transAxes, fontfamily='monospace',
             bbox=dict(boxstyle="round,pad=0.8", facecolor="#ffe6e6", edgecolor="#cc0000", linewidth=2))
 
    plt.suptitle('Step 2: Identifying the Library vs Monte Carlo Problem',
                fontsize=20, fontweight='bold', y=0.95)
    plt.tight_layout()
    filename = os.path.join(output_dir, f"basic_step2_mc_vs_library.{save_format}")
    plt.savefig(filename, bbox_inches='tight', facecolor='white', dpi=300)
    plt.close()
    return filename
 
def create_plot3_sensitivity_calculation(output_dir=".", save_format='png'):
    """Plot 3: Voltage sensitivity calculation step by step."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 10))
 
    # Left plot: Voltage sensitivity visualization
    voltages = np.array([0.45, 0.465])
    delays = np.array([90, 10])
 
    # Plot the line and points
    ax1.plot(voltages, delays, 'bo-', linewidth=4, markersize=12, label='Library Points')
 
    # Add annotations for each point
    ax1.annotate('Point 1: (0.45V, 90ps)', xy=(0.45, 90), xytext=(0.435, 110),
                arrowprops=dict(arrowstyle='->', lw=2, color='blue'),
                fontsize=12, fontweight='bold', color='blue')
 
    ax1.annotate('Point 2: (0.465V, 10ps)', xy=(0.465, 10), xytext=(0.475, 30),
                arrowprops=dict(arrowstyle='->', lw=2, color='blue'),
                fontsize=12, fontweight='bold', color='blue')
 
    # Draw delta annotations
    # Voltage delta
    ax1.annotate('', xy=(0.465, 5), xytext=(0.45, 5),
                arrowprops=dict(arrowstyle='<->', lw=3, color='green'))
    ax1.text(0.4575, -5, 'Î”V = +15mV', ha='center', va='top',
             fontsize=12, fontweight='bold', color='green')
 
    # Delay delta
    ax1.annotate('', xy=(0.44, 10), xytext=(0.44, 90),
                arrowprops=dict(arrowstyle='<->', lw=3, color='red'))
    ax1.text(0.435, 50, 'Î”Delay = -80ps', ha='center', va='center', rotation=90,
             fontsize=12, fontweight='bold', color='red')
 
    ax1.set_xlabel('Supply Voltage (V)', fontsize=14, fontweight='bold')
    ax1.set_ylabel('Delay (ps)', fontsize=14, fontweight='bold')
    ax1.set_title('Voltage Sensitivity Calculation\nUsing Two Library Points',
                 fontsize=16, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.legend(fontsize=12)
 
    # Right plot: Calculation details
    ax2.axis('off')
    calc_text = """VOLTAGE SENSITIVITY CALCULATION:
 
ðŸ“Š DATA POINTS:
â€¢ Point 1: 90ps @ 0.45V
â€¢ Point 2: 10ps @ 0.465V
 
ðŸ“ STEP-BY-STEP CALCULATION:
 
1ï¸âƒ£ Calculate voltage difference:
   Î”V = 0.465V - 0.45V = 0.015V = 15mV
 
2ï¸âƒ£ Calculate delay difference:
   Î”Delay = 10ps - 90ps = -80ps
 
3ï¸âƒ£ Calculate voltage sensitivity:
   Sensitivity = Î”V / Î”Delay
   Sensitivity = 15mV / (-80ps)
   Sensitivity = -0.1875 mV/ps
 
4ï¸âƒ£ INTERPRETATION:
   â€¢ Negative sensitivity means:
     Higher voltage â†’ Lower delay
   â€¢ Magnitude: 0.1875 mV voltage change
     needed per 1ps delay change
 
ðŸŽ¯ PHYSICAL MEANING:
   For every 1ps delay reduction needed,
   we must increase voltage by 0.1875mV"""
 
    ax2.text(0.05, 0.95, calc_text, ha='left', va='top', fontsize=11,
             transform=ax2.transAxes, fontfamily='monospace',
             bbox=dict(boxstyle="round,pad=0.8", facecolor="#e8f4fd", edgecolor="#1f77b4", linewidth=2))
 
    plt.suptitle('Step 3: Voltage Sensitivity Calculation',
                fontsize=20, fontweight='bold', y=0.95)
    plt.tight_layout()
    filename = os.path.join(output_dir, f"basic_step3_sensitivity_calculation.{save_format}")
    plt.savefig(filename, bbox_inches='tight', facecolor='white', dpi=300)
    plt.close()
    return filename
 
def create_plot4_voltage_adjustment(output_dir=".", save_format='png'):
    """Plot 4: Applying voltage adjustment to fix the error."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 10))
 
    # Left plot: Before and after comparison
    scenarios = ['Original\n(0.45V)', 'After Voltage\nAdjustment\n(0.452V)']
    lib_values = [90, 90]  # Library stays the same
    mc_original = [100, 100]  # Original MC
    mc_adjusted = [100, 90]   # MC after voltage adjustment
 
    x_pos = np.arange(len(scenarios))
    width = 0.25
 
    # Plot bars
    bars1 = ax1.bar(x_pos - width, lib_values, width, label='Library Value',
                    color='lightblue', edgecolor='blue', linewidth=2)
    bars2 = ax1.bar(x_pos, mc_original, width, label='MC Original',
                    color='lightcoral', edgecolor='red', linewidth=2)
    bars3 = ax1.bar(x_pos + width, mc_adjusted, width, label='MC Adjusted',
                    color='lightgreen', edgecolor='green', linewidth=2)
 
    # Add value labels
    for i, (lib, mc_orig, mc_adj) in enumerate(zip(lib_values, mc_original, mc_adjusted)):
        ax1.text(x_pos[i] - width, lib + 2, f'{lib}ps', ha='center', va='bottom',
                fontsize=11, fontweight='bold', color='blue')
        ax1.text(x_pos[i], mc_orig + 2, f'{mc_orig}ps', ha='center', va='bottom',
                fontsize=11, fontweight='bold', color='red')
        ax1.text(x_pos[i] + width, mc_adj + 2, f'{mc_adj}ps', ha='center', va='bottom',
                fontsize=11, fontweight='bold', color='green')
 
    # Show error elimination
    ax1.annotate('10ps Error\nEliminated!', xy=(1 + width, 90), xytext=(1.5, 70),
                arrowprops=dict(arrowstyle='->', lw=2, color='green'),
                fontsize=12, fontweight='bold', color='green',
                bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgreen", alpha=0.8))
 
    ax1.set_xlabel('Scenario', fontsize=14, fontweight='bold')
    ax1.set_ylabel('Delay (ps)', fontsize=14, fontweight='bold')
    ax1.set_title('Before vs After Voltage Adjustment', fontsize=16, fontweight='bold')
    ax1.set_xticks(x_pos)
    ax1.set_xticklabels(scenarios)
    ax1.legend(fontsize=12)
    ax1.grid(True, alpha=0.3)
 
    # Right plot: Calculation explanation
    ax2.axis('off')
    adjustment_text = """VOLTAGE ADJUSTMENT CALCULATION:
 
ðŸŽ¯ GOAL: Reduce MC delay from 100ps to 90ps
   Target delay reduction = 10ps
 
ðŸ“Š USING VOLTAGE SENSITIVITY:
   Sensitivity = -0.1875 mV/ps
   (from previous calculation)
 
ðŸ”§ REQUIRED VOLTAGE ADJUSTMENT:
   Voltage adjustment = Sensitivity Ã— Delay change
   Voltage adjustment = (-0.1875 mV/ps) Ã— (-10ps)
   Voltage adjustment = +1.875mV â‰ˆ +2mV
 
ðŸ’¡ INTERPRETATION:
   â€¢ Need to INCREASE voltage by 2mV
   â€¢ Original voltage: 0.45V
   â€¢ Adjusted voltage: 0.45V + 0.002V = 0.452V
 
âœ… RESULT:
   â€¢ At 0.452V, MC delay becomes â‰ˆ 90ps
   â€¢ Matches library value exactly!
   â€¢ 10ps optimistic error eliminated
 
ðŸ† CUSTOMER BENEFIT:
   â€¢ No need for expensive re-characterization
   â€¢ 2mV voltage increase is typically acceptable
   â€¢ Design timing requirements can be met"""
 
    ax2.text(0.05, 0.95, adjustment_text, ha='left', va='top', fontsize=11,
             transform=ax2.transAxes, fontfamily='monospace',
             bbox=dict(boxstyle="round,pad=0.8", facecolor="#e8ffe8", edgecolor="#00aa00", linewidth=2))
 
    plt.suptitle('Step 4: Applying Voltage Adjustment Solution',
                fontsize=20, fontweight='bold', y=0.95)
    plt.tight_layout()
    filename = os.path.join(output_dir, f"basic_step4_voltage_adjustment.{save_format}")
    plt.savefig(filename, bbox_inches='tight', facecolor='white', dpi=300)
    plt.close()
    return filename
 
def create_plot5_complete_solution(output_dir=".", save_format='png'):
    """Plot 5: Complete solution overview and benefits."""
    fig = plt.figure(figsize=(16, 12))
    gs = gridspec.GridSpec(3, 2, height_ratios=[1, 1, 1.2], hspace=0.3, wspace=0.2)
 
    # Top left: Problem summary
    ax1 = fig.add_subplot(gs[0, 0])
    ax1.axis('off')
    ax1.text(0.5, 0.9, 'âŒ THE PROBLEM', ha='center', va='top', fontsize=16,
             fontweight='bold', color='red', transform=ax1.transAxes)
 
    problem_summary = """â€¢ Library: 90ps @ 0.45V
â€¢ Monte Carlo: 100ps @ 0.45V
â€¢ 10ps optimistic error
â€¢ Re-characterization too expensive"""
 
    ax1.text(0.1, 0.7, problem_summary, ha='left', va='top', fontsize=12,
             transform=ax1.transAxes, fontfamily='monospace',
             bbox=dict(boxstyle="round,pad=0.5", facecolor="#ffe6e6", edgecolor="#cc0000"))
 
    # Top right: Solution summary
    ax2 = fig.add_subplot(gs[0, 1])
    ax2.axis('off')
    ax2.text(0.5, 0.9, 'âœ… THE SOLUTION', ha='center', va='top', fontsize=16,
             fontweight='bold', color='green', transform=ax2.transAxes)
 
    solution_summary = """â€¢ Use voltage sensitivity analysis
â€¢ Calculate: -0.1875 mV/ps
â€¢ Apply +2mV voltage adjustment
â€¢ MC becomes 90ps (matches library)"""
 
    ax2.text(0.1, 0.7, solution_summary, ha='left', va='top', fontsize=12,
             transform=ax2.transAxes, fontfamily='monospace',
             bbox=dict(boxstyle="round,pad=0.5", facecolor="#e8ffe8", edgecolor="#00aa00"))
 
    # Middle: Complete workflow
    ax3 = fig.add_subplot(gs[1, :])
    ax3.axis('off')
 
    # Workflow diagram
    workflow_steps = [
        "1. Library\nCharacterization\n(2 voltage points)",
        "2. Identify\nMC vs Lib\nDiscrepancy",
        "3. Calculate\nVoltage\nSensitivity",
        "4. Apply Voltage\nAdjustment\n(+2mV)",
        "5. Verify\nError\nElimination"
    ]
 
    # Draw workflow boxes and arrows
    box_width = 0.15
    box_height = 0.6
    y_center = 0.5
 
    for i, step in enumerate(workflow_steps):
        x_center = 0.1 + i * 0.18
 
        # Draw box
        color = ['lightblue', 'lightcoral', 'lightyellow', 'lightgreen', 'lightcyan'][i]
        box = FancyBboxPatch((x_center - box_width/2, y_center - box_height/2),
                            box_width, box_height, boxstyle="round,pad=0.02",
                            facecolor=color, edgecolor='black', linewidth=2)
        ax3.add_patch(box)
 
        # Add text
        ax3.text(x_center, y_center, step, ha='center', va='center', fontsize=10,
                fontweight='bold', transform=ax3.transAxes)
 
        # Add arrow (except for last box)
        if i < len(workflow_steps) - 1:
            ax3.annotate('', xy=(x_center + box_width/2 + 0.01, y_center),
                        xytext=(x_center + box_width/2 + 0.05, y_center),
                        arrowprops=dict(arrowstyle='->', lw=3, color='blue'),
                        transform=ax3.transAxes)
 
    ax3.text(0.5, 0.9, 'Complete Voltage Sensitivity Workflow', ha='center', va='top',
             fontsize=18, fontweight='bold', transform=ax3.transAxes)
 
    # Bottom: Key benefits and insights
    ax4 = fig.add_subplot(gs[2, :])
    ax4.axis('off')
 
    benefits_text = """ðŸ† KEY BENEFITS & CUSTOMER VALUE:
 
ðŸ’° COST SAVINGS:
   â€¢ Avoids expensive production re-characterization
   â€¢ Uses existing library data points efficiently
   â€¢ Minimal additional validation required
 
âš¡ QUICK SOLUTION:
   â€¢ Immediate actionable results
   â€¢ No need to wait for new silicon characterization
   â€¢ Fast turnaround for customer concerns
 
ðŸŽ¯ PRACTICAL APPLICATION:
   â€¢ 2mV voltage adjustment is typically acceptable in most designs
   â€¢ Small voltage increase vs major timing failure
   â€¢ Maintains design performance with minor power trade-off
 
ðŸ” BROADER IMPLICATIONS:
   â€¢ Enables confident use of ULV (Ultra-Low Voltage) libraries
   â€¢ Provides quantitative risk assessment for library accuracy
   â€¢ Supports aggressive low-power design strategies
 
ðŸ“Š SCALABILITY:
   â€¢ Same methodology applies to any library cell
   â€¢ Can be automated across entire cell library
   â€¢ Builds confidence in library accuracy across process corners
 
ðŸš€ COMPETITIVE ADVANTAGE:
   â€¢ Unique capability to address library vs silicon mismatches
   â€¢ Enables customers to push performance boundaries safely
   â€¢ Differentiates our libraries with voltage sensitivity data"""
 
    ax4.text(0.05, 0.95, benefits_text, ha='left', va='top', fontsize=11,
             transform=ax4.transAxes, fontfamily='monospace',
             bbox=dict(boxstyle="round,pad=0.8", facecolor="#f0f8ff", edgecolor="#4682b4", linewidth=3))
 
    plt.suptitle('Step 5: Complete Voltage Sensitivity Solution Overview',
                fontsize=20, fontweight='bold', y=0.95)
    plt.tight_layout()
    filename = os.path.join(output_dir, f"basic_step5_complete_solution.{save_format}")
    plt.savefig(filename, bbox_inches='tight', facecolor='white', dpi=300)
    plt.close()
    return filename
 
# Main execution function
def main():
    """Generate basic voltage sensitivity tutorial plots."""
    import argparse
 
    parser = argparse.ArgumentParser(description='Generate basic voltage sensitivity tutorial plots')
    parser.add_argument('--output_dir', type=str, default='basic_voltage_tutorial',
                       help='Output directory for plots (default: basic_voltage_tutorial)')
    parser.add_argument('--format', type=str, default='png', choices=['png', 'pdf', 'svg'],
                       help='Output format (default: png)')
 
    args = parser.parse_args()
 
    print("Generating basic voltage sensitivity tutorial plots...")
    print(f"Output directory: {args.output_dir}")
    print(f"Format: {args.format}")
    print("-" * 50)
 
    generated_files = create_basic_tutorial_plots(args.output_dir, args.format)
 
    print("\nSUMMARY:")
    print(f"Generated {len(generated_files)} tutorial plots in {args.output_dir}/")
    for step_num, filename in generated_files.items():
        print(f"  Step {step_num}: {os.path.basename(filename)}")
 
    print("\n" + "="*60)
    print("BASIC VOLTAGE SENSITIVITY TUTORIAL COMPLETE!")
    print("="*60)
    print("\nPlots explain:")
    print("- How to identify library vs Monte Carlo discrepancies")
    print("- How to calculate voltage sensitivity from two data points")
    print("- How to apply voltage adjustments to fix timing errors")
    print("- Why this beats expensive re-characterization")
    print("- Customer benefits and practical applications")
 
if __name__ == "__main__":
    main()
