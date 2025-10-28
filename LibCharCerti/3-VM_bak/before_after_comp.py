import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.colors import LinearSegmentedColormap
import matplotlib.patches as patches
 
# Data extracted from TSMC tables
def create_data():
    """Create DataFrames for all 4 tables"""
   
    # Voltage levels
    voltages = ['0.45V', '0.465V', '0.48V', '0.495V']
    test_params = ['Meanshift', 'Skew', 'Std', 'early_sigma', 'late_sigma']
   
    # Table 1: Delay Before Voltage Margin
    delay_before_data = [
        [82.20, 91.10, 95.70, 98.90],  # Meanshift
        [92.20, 97.30, 98.40, 100.0],  # Skew
        [98.10, 97.60, 99.70, 100.0],  # Std
        [100.0, 100.0, 100.0, 100.0],  # early_sigma
        [83.50, 92.40, 93.20, 92.40]   # late_sigma
    ]
   
    # Table 2: Delay After Voltage Margin (with margins: +3.0mV, +2.0mV, +2.0mV, +1.0mV)
    delay_after_data = [
        [99.7, 98.9, 98.4, 98.9],      # Meanshift
        [95.0, 97.6, 98.4, 100.0],     # Skew
        [99.7, 98.6, 100.0, 100.0],    # Std
        [100.0, 100.0, 100.0, 100.0],  # early_sigma
        [97.3, 95.9, 95.7, 95.1]       # late_sigma
    ]
   
    # Table 3: Slew Before Voltage Margin
    slew_before_data = [
        [98.90, 100.0, 99.70, 99.20],  # Meanshift
        [100.0, 100.0, 99.70, 100.0],  # Skew
        [98.40, 99.50, 100.0, 99.0],   # Std
        [100.0, 100.0, 100.0, 100.0],  # early_sigma
        [100.0, 100.0, 100.0, 100.0]   # late_sigma
    ]
   
    # Table 4: Slew After Voltage Margin
    slew_after_data = [
        [99.2, 99.5, 100.0, 99.2],     # Meanshift
        [97.0, 100.0, 98.6, 100.0],    # Skew
        [100.0, 100.0, 99.7, 99.7],    # Std
        [100.0, 100.0, 100.0, 100.0],  # early_sigma
        [99.2, 100.0, 99.5, 99.5]      # late_sigma
    ]
   
    # Create DataFrames
    delay_before_df = pd.DataFrame(delay_before_data, columns=voltages, index=test_params)
    delay_after_df = pd.DataFrame(delay_after_data,
                                 columns=['0.450V\n(+3.0mV)', '0.465V\n(+2.0mV)',
                                         '0.480V\n(+2.0mV)', '0.495V\n(+1.0mV)'],
                                 index=test_params)
    slew_before_df = pd.DataFrame(slew_before_data, columns=voltages, index=test_params)
    slew_after_df = pd.DataFrame(slew_after_data,
                                columns=['0.450V\n(+3.0mV)', '0.465V\n(+2.0mV)',
                                        '0.480V\n(+2.0mV)', '0.495V\n(+1.0mV)'],
                                index=test_params)
   
    return delay_before_df, delay_after_df, slew_before_df, slew_after_df
 
def create_custom_colormap():
    """Create custom colormap where pass rates >= 95% are light colored"""
   
    # Define colors: Red for <90%, Orange for 90-95%, Light colors for >=95%
    colors = [
        '#d32f2f',  # Dark red for very low values (80-85%)
        '#f57c00',  # Orange for low values (85-90%)
        '#ff9800',  # Light orange for borderline (90-95%)
        '#e8f5e8',  # Very light green for passing (95-98%)
        '#f1f8e9',  # Very light green for good passing (98-99%)
        '#f9fbe7'   # Almost white for excellent (99-100%)
    ]
   
    # Define the positions for each color (normalized 0-1)
    # Map 80-100% range to 0-1
    positions = [0.0, 0.25, 0.5, 0.75, 0.9, 1.0]
   
    cmap = LinearSegmentedColormap.from_list("custom_pass_rate",
                                           list(zip(positions, colors)),
                                           N=256)
    return cmap
 
def plot_heatmap(data, title, ax, cmap, vmin=80, vmax=100):
    """Plot a single heatmap with custom styling"""
   
    # Create the heatmap
    sns.heatmap(data,
                annot=True,
                fmt='.1f',
                cmap=cmap,
                vmin=vmin,
                vmax=vmax,
                ax=ax,
                cbar_kws={'label': 'Pass Rate (%)', 'shrink': 0.9, 'pad': 0.02},
                linewidths=1.0,
                linecolor='white',
                annot_kws={'fontsize': 14, 'fontweight': 'bold'})
   
    # Customize the plot
    ax.set_title(title, fontsize=18, fontweight='bold', pad=25)
    ax.set_xlabel('Voltage Levels', fontsize=14, fontweight='bold')
    ax.set_ylabel('Test Parameters', fontsize=14, fontweight='bold')
   
    # Rotate x-axis labels for better readability
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right', fontsize=12)
    ax.set_yticklabels(ax.get_yticklabels(), rotation=0, fontsize=12)
   
    # Add certification threshold line visual indicator
    # Highlight cells that fail certification (< 95%)
    for i in range(len(data.index)):
        for j in range(len(data.columns)):
            value = data.iloc[i, j]
            if value < 95:
                # Add a red border for failing values
                rect = patches.Rectangle((j, i), 1, 1, linewidth=4,
                                       edgecolor='red', facecolor='none')
                ax.add_patch(rect)
 
def create_improvement_analysis(before_df, after_df):
    """Create improvement analysis DataFrame"""
    improvement = after_df.values - before_df.values
    improvement_df = pd.DataFrame(improvement,
                                 columns=after_df.columns,
                                 index=before_df.index)
    return improvement_df
 
def main():
    """Main function to create all visualizations"""
   
    # Create data
    delay_before_df, delay_after_df, slew_before_df, slew_after_df = create_data()
   
    # Create custom colormap
    cmap = create_custom_colormap()
   
    # Set up the plot with larger figure size
    fig = plt.figure(figsize=(24, 20))
   
    # Create a main title with larger font
    fig.suptitle('TSMC Pass Rate Analysis - CDNS Best Recipe Certification\n' +
                 'Pass Rates â‰¥95% (Light Colors) Pass Certification | <95% (Dark Colors) Fail',
                 fontsize=22, fontweight='bold', y=0.96)
   
    # Plot 1: Delay Before
    ax1 = plt.subplot(2, 3, 1)
    plot_heatmap(delay_before_df, 'Delay Test Results\n(Before Voltage Margin)', ax1, cmap)
   
    # Plot 2: Delay After 
    ax2 = plt.subplot(2, 3, 2)
    plot_heatmap(delay_after_df, 'Delay Test Results\n(After Voltage Margin)', ax2, cmap)
   
    # Plot 3: Delay Improvement
    ax3 = plt.subplot(2, 3, 3)
    delay_improvement = create_improvement_analysis(delay_before_df, delay_after_df)
    sns.heatmap(delay_improvement,
                annot=True,
                fmt='+.1f',
                cmap='RdYlGn',
                center=0,
                ax=ax3,
                cbar_kws={'label': 'Improvement (%)', 'shrink': 0.9, 'pad': 0.02},
                linewidths=1.0,
                linecolor='white',
                annot_kws={'fontsize': 14, 'fontweight': 'bold'})
    ax3.set_title('Delay Test Improvement\n(After - Before)', fontsize=18, fontweight='bold', pad=25)
    ax3.set_xlabel('Voltage Levels', fontsize=14, fontweight='bold')
    ax3.set_ylabel('Test Parameters', fontsize=14, fontweight='bold')
    ax3.set_xticklabels(ax3.get_xticklabels(), rotation=45, ha='right', fontsize=12)
    ax3.set_yticklabels(ax3.get_yticklabels(), rotation=0, fontsize=12)
   
    # Plot 4: Slew Before
    ax4 = plt.subplot(2, 3, 4)
    plot_heatmap(slew_before_df, 'Slew - Before)', ax4, cmap)
   
    # Plot 5: Slew After
    ax5 = plt.subplot(2, 3, 5)
    plot_heatmap(slew_after_df, 'Slew - After)', ax5, cmap)
   
    # Plot 6: Slew Improvement
    ax6 = plt.subplot(2, 3, 6)
    slew_improvement = create_improvement_analysis(slew_before_df, slew_after_df)
    sns.heatmap(slew_improvement,
                annot=True,
                fmt='+.1f',
                cmap='RdYlGn',
                center=0,
                ax=ax6,
                cbar_kws={'label': 'Improvement (%)', 'shrink': 0.9, 'pad': 0.02},
                linewidths=1.0,
                linecolor='white',
                annot_kws={'fontsize': 14, 'fontweight': 'bold'})
    #ax6.set_title('Slew Test Improvement\n(After - Before)', fontsize=18, fontweight='bold', pad=25)
    ax6.set_xlabel('Voltage Levels', fontsize=14, fontweight='bold')
    ax6.set_ylabel('Test Parameters', fontsize=14, fontweight='bold')
    ax6.set_xticklabels(ax6.get_xticklabels(), rotation=45, ha='right', fontsize=12)
    ax6.set_yticklabels(ax6.get_yticklabels(), rotation=0, fontsize=12)
   
    # Adjust layout with more spacing
    plt.tight_layout()
    plt.subplots_adjust(top=0.89, bottom=0.12, hspace=0.4, wspace=0.35)
   
    # Add certification threshold information with larger font
    #fig.text(0.5, 0.04, 'Red borders indicate values < 95% (Certification Failure)',
     #        ha='center', fontsize=16, color='red', fontweight='bold')
   
    # Show the plot
    plt.show()
   
    # Print summary statistics
    print("\n" + "="*80)
    print("TSMC CERTIFICATION SUMMARY")
    print("="*80)
   
    print("\nDELAY TEST RESULTS:")
    print("-" * 50)
   
    # Count failures before and after for delay
    delay_failures_before = (delay_before_df < 95).sum().sum()
    delay_failures_after = (delay_after_df < 95).sum().sum()
   
    print(f"Failures before voltage margin: {delay_failures_before}/20 cells")
    print(f"Failures after voltage margin:  {delay_failures_after}/20 cells")
    print(f"Improvement: {delay_failures_before - delay_failures_after} cells fixed")
   
    print("\nSLEW TEST RESULTS:")
    print("-" * 50)
   
    # Count failures before and after for slew
    slew_failures_before = (slew_before_df < 95).sum().sum()
    slew_failures_after = (slew_after_df < 95).sum().sum()
   
    print(f"Failures before voltage margin: {slew_failures_before}/20 cells")
    print(f"Failures after voltage margin:  {slew_failures_after}/20 cells")
    print(f"Improvement: {slew_failures_before - slew_failures_after} cells fixed")
   
    total_failures_before = delay_failures_before + slew_failures_before
    total_failures_after = delay_failures_after + slew_failures_after
   
    print(f"\nOVERALL CERTIFICATION STATUS:")
    print("-" * 50)
    print(f"Total failures before: {total_failures_before}/40 cells")
    print(f"Total failures after:  {total_failures_after}/40 cells")
   
    if total_failures_after == 0:
        print("âœ… CERTIFICATION PASSED - All tests above 95% threshold")
    else:
        print("âŒ CERTIFICATION FAILED - Some tests below 95% threshold")
   
    print("="*80)
 
if __name__ == "__main__":
    main()
 
