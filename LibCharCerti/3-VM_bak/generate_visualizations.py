#!/usr/bin/env python3
 
import os
import json
import pandas as pd
import numpy as np
import glob
import logging
import traceback
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.colors import LinearSegmentedColormap
from sklearn.cluster import KMeans
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)
 
def setup_logging(output_dir):
    """Set up logging to file."""
    os.makedirs(output_dir, exist_ok=True)
    log_file = os.path.join(output_dir, "visualize.log")
 
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s',
        filename=log_file,
        filemode='w'
    )
 
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
    logging.getLogger('').addHandler(console)
 
def parse_args():
    """Parse command-line arguments."""
    import argparse
    parser = argparse.ArgumentParser(description='Generate visualizations for timing analysis results')
    parser.add_argument('--data_dir', type=str, required=True, help='Directory with analysis data')
    parser.add_argument('--output_dir', type=str, required=True, help='Output directory for visualizations')
    return parser.parse_args()
 
def load_correlation_data(data_dir):
    """Load correlation data from JSON files."""
    correlation_files = glob.glob(os.path.join(data_dir, "*_correlations.json"))
 
    all_correlations = {}
    for file in correlation_files:
        file_name = os.path.basename(file).replace("_correlations.json", "")
        try:
            with open(file, 'r') as f:
                correlations = json.load(f)
            all_correlations[file_name] = correlations
        except Exception as e:
            logging.error(f"Error loading correlations from {file}: {e}")
 
    return all_correlations
 
def load_outliers_data(data_dir):
    """Load outliers data from JSON files."""
    outlier_files = glob.glob(os.path.join(data_dir, "*_outliers.json"))
 
    all_outliers = {}
    for file in outlier_files:
        file_name = os.path.basename(file).replace("_outliers.json", "")
        try:
            with open(file, 'r') as f:
                outliers = json.load(f)
            all_outliers[file_name] = outliers
        except Exception as e:
            logging.error(f"Error loading outliers from {file}: {e}")
 
    return all_outliers
 
def load_metadata(data_dir):
    """Load metadata from JSON files."""
    metadata_files = glob.glob(os.path.join(data_dir, "*_metadata.json"))
 
    all_metadata = {}
    for file in metadata_files:
        file_name = os.path.basename(file).replace("_metadata.json", "")
        try:
            with open(file, 'r') as f:
                metadata = json.load(f)
            all_metadata[file_name] = metadata
        except Exception as e:
            logging.error(f"Error loading metadata from {file}: {e}")
 
    return all_metadata
 
def load_sigma_info(data_dir):
    """Load sigma column information from JSON files."""
    sigma_files = glob.glob(os.path.join(data_dir, "*_sigma_info.json"))
 
    all_sigma_info = {}
    for file in sigma_files:
        file_name = os.path.basename(file).replace("_sigma_info.json", "")
        try:
            with open(file, 'r') as f:
                sigma_info = json.load(f)
            all_sigma_info[file_name] = sigma_info
        except Exception as e:
            logging.error(f"Error loading sigma info from {file}: {e}")
 
    return all_sigma_info
 
 
 
 
 
def create_correlation_bar_chart(correlations, category, sigma_type, moment_type, output_dir, title, filename):
    """Create a bar chart of correlations for a specific category and moment type."""
    try:
        # Filter correlations for the specified category and moment type
        items = []
        for col, corr in correlations.items():
            # Check if column matches the moment type
            if (moment_type == 'STD' and 'std' in col.lower()) or \
               (moment_type == 'SKEW' and 'skew' in col.lower()) or \
               (moment_type == 'MEANSHIFT' and 'meanshift' in col.lower()):
                items.append((col, corr))
 
        if not items:
            logging.warning(f"No {moment_type} correlations found for {category} {sigma_type}")
            return None
 
        # Convert to DataFrame
        df = pd.DataFrame(items, columns=['Column', 'Correlation'])
 
        # Sort by correlation value
        df = df.sort_values('Correlation', ascending=False)
 
        # Create bar chart
        plt.figure(figsize=(12, 6))
        colors = ['#1976D2' if c >= 0 else '#D32F2F' for c in df['Correlation']]
        ax = sns.barplot(x='Column', y='Correlation', data=df, palette=colors)
 
        # Set title and labels
        plt.title(title, fontsize=14)
        plt.xticks(rotation=45, ha='right')
        plt.axhline(y=0, color='black', linestyle='-', alpha=0.3)
 
        # Add value labels on top of bars
        for i, v in enumerate(df['Correlation']):
            ax.text(i, v + (0.02 if v >= 0 else -0.08), f"{v:.4f}",
                    ha='center', va='center', fontsize=9)
 
        plt.ylim(-1.05, 1.05)  # Set y-axis limits
        plt.tight_layout()
 
        # Save figure
        output_path = os.path.join(output_dir, filename)
        plt.savefig(output_path, dpi=150)
        plt.close()
 
        logging.info(f"Created bar chart: {output_path}")
        return output_path
 
    except Exception as e:
        logging.error(f"Error creating bar chart {filename}: {e}")
        logging.error(traceback.format_exc())
        return None
 
 
def create_outlier_analysis_plot(df, x_col, y_col, metadata_col, output_dir, title, filename, z_threshold=2.0):
    """Create a scatter plot highlighting outliers and annotating with metadata."""
    try:
        # Calculate linear regression
        X = df[x_col].values.reshape(-1, 1)
        y = df[y_col].values
 
        valid_mask = ~np.isnan(X.flatten()) & ~np.isnan(y)
        if sum(valid_mask) <= 1:
            logging.warning(f"Not enough valid data points for {filename}")
            return None
 
        X_valid = X[valid_mask].reshape(-1, 1)
        y_valid = y[valid_mask]
 
        # Simple linear regression
        from sklearn.linear_model import LinearRegression
        reg = LinearRegression().fit(X_valid, y_valid)
        y_pred = reg.predict(X_valid)
        residuals = y_valid - y_pred
 
        # Identify outliers in residuals
        z_scores = np.abs(residuals - np.mean(residuals)) / np.std(residuals)
        outlier_mask = z_scores > z_threshold
 
        # Get indices for original dataframe
        original_indices = np.where(valid_mask)[0]
        outlier_indices = original_indices[outlier_mask]
 
        # Create figure
        plt.figure(figsize=(12, 10))
 
        # Plot all points
        plt.scatter(X_valid, y_valid, alpha=0.5, label='Normal points')
 
        # Highlight outliers
        if sum(outlier_mask) > 0:
            plt.scatter(
                X_valid[outlier_mask], y_valid[outlier_mask],
                color='red', s=100, alpha=0.7, label=f'Outliers (z > {z_threshold})'
            )
 
            # Annotate outliers with metadata
            for i, idx in enumerate(outlier_indices):
                if metadata_col in df.columns:
                    label = str(df[metadata_col].iloc[idx])
                    if len(label) > 20:  # Truncate long labels
                        label = label[:17] + "..."
                    plt.annotate(
                        label,
                        (X[idx][0], y[idx]),
                        xytext=(5, 5), textcoords='offset points',
                        bbox=dict(boxstyle='round,pad=0.3', fc='yellow', alpha=0.3)
                    )
 
        # Plot regression line
        plt.plot(X_valid, y_pred, color='green', linewidth=2, label='Regression line')
 
        # Add title and labels
        plt.title(title, fontsize=14)
        plt.xlabel(x_col)
        plt.ylabel(y_col)
        plt.legend()
 
        # Add correlation info
        corr = df[x_col].corr(df[y_col])
        plt.text(0.05, 0.95, f"Correlation: {corr:.4f}\nOutliers: {sum(outlier_mask)}/{len(y_valid)}",
               transform=plt.gca().transAxes, fontsize=12,
               verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.7))
 
        plt.tight_layout()
 
        # Save figure
        output_path = os.path.join(output_dir, filename)
        plt.savefig(output_path, dpi=150)
        plt.close()
 
        logging.info(f"Created outlier analysis plot: {output_path}")
        return output_path
 
    except Exception as e:
        logging.error(f"Error creating outlier plot {filename}: {e}")
        logging.error(traceback.format_exc())
        return None
 
def generate_correlation_summary_heatmap(all_correlations, all_sigma_info, corners, types, moment_type, output_dir):
    """Generate heatmap for summary of correlations across corners and types."""
    try:
        # Prepare data structures
        late_sigma_data = {}
        early_sigma_data = {}
 
        # Categories
        categories = ['MC', 'Lib', 'abs_err', 'rel_err']
 
        # Iterate through corners and types
        for corner in corners:
            for type_name in types:
                # Generate key for results
                result_key = f"{corner}_{type_name}"
 
                # Check if we have correlations and sigma info for this key
                if result_key not in all_correlations or result_key not in all_sigma_info:
                    continue
 
                correlations = all_correlations[result_key]
                sigma_info = all_sigma_info[result_key]
 
                # Get sigma column names
                late_sigma = sigma_info.get('late_sigma')
                early_sigma = sigma_info.get('early_sigma')
 
                # Process late sigma correlations
                if late_sigma and 'late_sigma' in correlations:
                    # Initialize with empty values
                    if result_key not in late_sigma_data:
                        late_sigma_data[result_key] = {}
 
                    # Process each category
                    for category in categories:
                        if category in correlations['late_sigma']:
                            # Filter correlations for the specified moment type
                            avg_corr = np.mean([
                                v for k, v in correlations['late_sigma'][category].items()
                                if (moment_type == 'STD' and 'std' in k.lower()) or
                                   (moment_type == 'SKEW' and 'skew' in k.lower()) or
                                   (moment_type == 'MEANSHIFT' and 'meanshift' in k.lower())
                            ])
                            late_sigma_data[result_key][category] = avg_corr
 
                # Process early sigma correlations
                if early_sigma and 'early_sigma' in correlations:
                    # Initialize with empty values
                    if result_key not in early_sigma_data:
                        early_sigma_data[result_key] = {}
 
                    # Process each category
                    for category in categories:
                        if category in correlations['early_sigma']:
                            # Filter correlations for the specified moment type
                            avg_corr = np.mean([
                                v for k, v in correlations['early_sigma'][category].items()
                                if (moment_type == 'STD' and 'std' in k.lower()) or
                                   (moment_type == 'SKEW' and 'skew' in k.lower()) or
                                   (moment_type == 'MEANSHIFT' and 'meanshift' in k.lower())
                            ])
                            early_sigma_data[result_key][category] = avg_corr
 
        # Convert to DataFrames
        late_df = pd.DataFrame(late_sigma_data).T
        early_df = pd.DataFrame(early_sigma_data).T
 
        # Add corner and type columns
        late_df['corner'] = late_df.index.map(lambda x: x.split('_')[0])
        late_df['type'] = late_df.index.map(lambda x: x.split('_')[1])
        early_df['corner'] = early_df.index.map(lambda x: x.split('_')[0])
        early_df['type'] = early_df.index.map(lambda x: x.split('_')[1])
 
        # Create heatmaps
        if not late_df.empty:
            # Create a pivot table for late sigma
            late_pivot = late_df.pivot_table(
                index='corner',
                columns=['type'],
                values=categories
            )
 
            # Create heatmap
            plt.figure(figsize=(5 * len(types), 5 * len(categories)))
            ax = sns.heatmap(late_pivot, annot=True, cmap='coolwarm', center=0,
                             fmt='.4f', linewidths=0.5, vmin=-1, vmax=1)
            plt.title(f'Late Sigma vs {moment_type} Correlations', fontsize=16)
            plt.tight_layout()
 
            # Save figure
            output_path = os.path.join(output_dir, f"late_sigma_{moment_type}_correlations_heatmap.png")
            plt.savefig(output_path, dpi=150)
            plt.close()
            logging.info(f"Created late sigma correlation heatmap: {output_path}")
 
        if not early_df.empty:
            # Create a pivot table for early sigma
            early_pivot = early_df.pivot_table(
                index='corner',
                columns=['type'],
                values=categories
            )
 
            # Create heatmap
            plt.figure(figsize=(5 * len(types), 5 * len(categories)))
            ax = sns.heatmap(early_pivot, annot=True, cmap='coolwarm', center=0,
                             fmt='.4f', linewidths=0.5, vmin=-1, vmax=1)
            plt.title(f'Early Sigma vs {moment_type} Correlations', fontsize=16)
            plt.tight_layout()
 
            # Save figure
            output_path = os.path.join(output_dir, f"early_sigma_{moment_type}_correlations_heatmap.png")
            plt.savefig(output_path, dpi=150)
            plt.close()
            logging.info(f"Created early sigma correlation heatmap: {output_path}")
 
        # Create compact summary tables for report
        late_summary = pd.DataFrame(index=corners, columns=pd.MultiIndex.from_product([types, categories]))
        early_summary = pd.DataFrame(index=corners, columns=pd.MultiIndex.from_product([types, categories]))
 
        for corner in corners:
            for type_name in types:
                result_key = f"{corner}_{type_name}"
                for category in categories:
                    if result_key in late_sigma_data and category in late_sigma_data[result_key]:
                        late_summary.loc[corner, (type_name, category)] = late_sigma_data[result_key][category]
                    if result_key in early_sigma_data and category in early_sigma_data[result_key]:
                        early_summary.loc[corner, (type_name, category)] = early_sigma_data[result_key][category]
 
        # Save summary tables to CSV
        late_summary.to_csv(os.path.join(output_dir, f"late_sigma_{moment_type}_summary.csv"))
        early_summary.to_csv(os.path.join(output_dir, f"early_sigma_{moment_type}_summary.csv"))
 
        return {
            'late_sigma': output_path if not late_df.empty else None,
            'early_sigma': output_path if not early_df.empty else None,
            'late_summary': late_summary,
            'early_summary': early_summary
        }
 
    except Exception as e:
        logging.error(f"Error generating correlation summary heatmap for {moment_type}: {e}")
        logging.error(traceback.format_exc())
        return None
 
def analyze_outliers_by_metadata(all_outliers, metadata_field, output_dir):
    """Analyze outliers by a specific metadata field and create visualizations."""
    try:
        # Collect all outliers
        all_outlier_data = []
 
        for file_name, file_outliers in all_outliers.items():
            # Process late sigma outliers
            if 'late_sigma' in file_outliers:
                for category, category_outliers in file_outliers['late_sigma'].items():
                    for column, outliers in category_outliers.items():
                        for outlier in outliers:
                            if metadata_field in outlier:
                                outlier_info = {
                                    'file_name': file_name,
                                    'sigma_type': 'late_sigma',
                                    'category': category,
                                    'column': column,
                                    'residual': outlier.get('residual', 0),
                                    'x_value': outlier.get('x_value', 0),
                                    'y_value': outlier.get('y_value', 0),
                                    metadata_field: outlier.get(metadata_field, 'Unknown')
                                }
                                all_outlier_data.append(outlier_info)
 
            # Process early sigma outliers
            if 'early_sigma' in file_outliers:
                for category, category_outliers in file_outliers['early_sigma'].items():
                    for column, outliers in category_outliers.items():
                        for outlier in outliers:
                            if metadata_field in outlier:
                                outlier_info = {
                                    'file_name': file_name,
                                    'sigma_type': 'early_sigma',
                                    'category': category,
                                    'column': column,
                                    'residual': outlier.get('residual', 0),
                                    'x_value': outlier.get('x_value', 0),
                                    'y_value': outlier.get('y_value', 0),
                                    metadata_field: outlier.get(metadata_field, 'Unknown')
                                }
                                all_outlier_data.append(outlier_info)
 
        if not all_outlier_data:
            logging.warning(f"No outliers found with {metadata_field} information")
            return None
 
        # Convert to DataFrame
        outlier_df = pd.DataFrame(all_outlier_data)
 
        # Save outlier data to CSV
        outlier_df.to_csv(os.path.join(output_dir, f"outliers_by_{metadata_field}.csv"), index=False)
 
        # Count outliers by metadata field
        counts = outlier_df[metadata_field].value_counts()
 
        # Create bar chart of outlier counts
        plt.figure(figsize=(14, 8))
        ax = counts.plot(kind='bar', color='crimson')
        plt.title(f'Outlier Count by {metadata_field}', fontsize=14)
        plt.xlabel(metadata_field)
        plt.ylabel('Number of Outliers')
        plt.xticks(rotation=45, ha='right')
 
        # Add value labels on top of bars
        for i, v in enumerate(counts):
            ax.text(i, v + 0.1, str(v), ha='center')
 
        plt.tight_layout()
 
        # Save figure
        count_plot_path = os.path.join(output_dir, f"outlier_count_by_{metadata_field}.png")
        plt.savefig(count_plot_path, dpi=150)
        plt.close()
        logging.info(f"Created outlier count plot: {count_plot_path}")
 
        # Analyze outliers by category and sigma type
        pivot = pd.pivot_table(
            outlier_df,
            index=metadata_field,
            columns=['sigma_type', 'category'],
            values='residual',
            aggfunc='count',
            fill_value=0
        )
 
        # Create heatmap
        plt.figure(figsize=(12, max(8, len(counts) * 0.4)))
        sns.heatmap(pivot, annot=True, cmap='YlOrRd', fmt='d')
        plt.title(f'Outlier Distribution by {metadata_field}, Sigma Type and Category', fontsize=14)
        plt.tight_layout()
 
        # Save figure
        heatmap_path = os.path.join(output_dir, f"outlier_heatmap_by_{metadata_field}.png")
        plt.savefig(heatmap_path, dpi=150)
        plt.close()
        logging.info(f"Created outlier heatmap: {heatmap_path}")
 
        # Cluster analysis if we have enough unique values
        if len(counts) >= 5:
            try:
                # Prepare data for clustering
                pivot_for_cluster = pivot.fillna(0)
 
                # Determine optimal number of clusters using silhouette score
                from sklearn.metrics import silhouette_score
 
                max_clusters = min(10, len(pivot_for_cluster) - 1)
                if max_clusters >= 2:
                    silhouette_scores = []
                    for k in range(2, max_clusters + 1):
                        kmeans = KMeans(n_clusters=k, n_init=10, random_state=42)
                        cluster_labels = kmeans.fit_predict(pivot_for_cluster)
                        if len(set(cluster_labels)) > 1:  # Check if we have more than 1 cluster
                            silhouette_avg = silhouette_score(pivot_for_cluster, cluster_labels)
                            silhouette_scores.append((k, silhouette_avg))
 
                    # Find optimal number of clusters
                    if silhouette_scores:
                        optimal_k = max(silhouette_scores, key=lambda x: x[1])[0]
 
                        # Apply KMeans with optimal clusters
                        kmeans = KMeans(n_clusters=optimal_k,n_init=10, random_state=42)
                        pivot_for_cluster['cluster'] = kmeans.fit_predict(pivot_for_cluster)
 
                        # Create visualization of clusters
                        plt.figure(figsize=(12, 10))
 
                        # Use PCA to visualize in 2D
                        from sklearn.decomposition import PCA
                        pca = PCA(n_components=2)
                        pca_result = pca.fit_transform(pivot_for_cluster.drop('cluster', axis=1))
 
                        # Create DataFrame for plotting
                        pca_df = pd.DataFrame({
                            'x': pca_result[:, 0],
                            'y': pca_result[:, 1],
                            'cluster': pivot_for_cluster['cluster'],
                            metadata_field: pivot_for_cluster.index
                        })
 
                        # Plot clusters
                        sns.scatterplot(x='x', y='y', hue='cluster', data=pca_df, palette='tab10', s=100)
 
                        # Add labels
                        for i, row in pca_df.iterrows():
                            label = str(row[metadata_field])
                            if len(label) > 15:  # Truncate long labels
                                label = label[:12] + "..."
                            plt.text(row['x'] + 0.02, row['y'] + 0.02, label, fontsize=9)
 
                        plt.title(f'Cluster Analysis of Outliers by {metadata_field} (k={optimal_k})', fontsize=14)
                        plt.xlabel('Principal Component 1')
                        plt.ylabel('Principal Component 2')
                        plt.tight_layout()
 
                        # Save figure
                        cluster_path = os.path.join(output_dir, f"outlier_clusters_by_{metadata_field}.png")
                        plt.savefig(cluster_path, dpi=150)
                        plt.close()
                        logging.info(f"Created outlier cluster analysis: {cluster_path}")
 
                        # Save cluster assignments
                        pivot_for_cluster.to_csv(os.path.join(output_dir, f"outlier_clusters_by_{metadata_field}.csv"))
 
                        # Create table with cluster summaries
                        cluster_summary = pd.DataFrame(index=range(optimal_k))
                        cluster_summary['cluster_size'] = pivot_for_cluster.groupby('cluster').size()
                        cluster_summary['top_items'] = [
                            ', '.join(pivot_for_cluster[pivot_for_cluster['cluster'] == i].index[:3].tolist())
                            for i in range(optimal_k)
                        ]
 
                        cluster_summary.to_csv(os.path.join(output_dir, f"outlier_cluster_summary_by_{metadata_field}.csv"))
 
            except Exception as e:
                logging.error(f"Error in cluster analysis for {metadata_field}: {e}")
                logging.error(traceback.format_exc())
 
        return {
            'count_plot': count_plot_path,
            'heatmap': heatmap_path,
            'data': outlier_df
        }
 
    except Exception as e:
        logging.error(f"Error analyzing outliers by {metadata_field}: {e}")
        logging.error(traceback.format_exc())
        return None
 
def create_table_position_heatmap(outlier_df, output_dir):
    """Create a heatmap showing distribution of outliers by table position."""
    try:
        if 'table_position' not in outlier_df.columns:
            logging.warning("No table_position column in outlier data")
            return None
 
        # Extract indices from table positions
        outlier_df['index_1'] = outlier_df['table_position'].str.split('-').str[0].astype(float)
        outlier_df['index_2'] = outlier_df['table_position'].str.split('-').str[1].astype(float)
 
        # Create 2D histogram
        hist, x_edges, y_edges = np.histogram2d(
            outlier_df['index_1'], outlier_df['index_2'],
            bins=[10, 10]
        )
 
        # Create heatmap
        plt.figure(figsize=(12, 10))
        plt.imshow(hist.T, origin='lower', aspect='auto', cmap='YlOrRd',
                   extent=[x_edges[0], x_edges[-1], y_edges[0], y_edges[-1]])
 
        plt.colorbar(label='Number of Outliers')
        plt.title('Outlier Distribution by Table Position', fontsize=14)
        plt.xlabel('Index 1')
        plt.ylabel('Index 2')
 
        # Add grid
        plt.grid(color='black', linestyle='-', linewidth=0.5, alpha=0.3)
 
        # Add values in cells
        for i in range(len(x_edges)-1):
            for j in range(len(y_edges)-1):
                count = hist[i, j]
                if count > 0:
                    plt.text(
                        (x_edges[i] + x_edges[i+1])/2,
                        (y_edges[j] + y_edges[j+1])/2,
                        int(count),
                        ha='center', va='center',
                        color='black' if count < np.max(hist)/2 else 'white'
                    )
 
        plt.tight_layout()
 
        # Save figure
        output_path = os.path.join(output_dir, "outlier_distribution_by_table_position.png")
        plt.savefig(output_path, dpi=150)
        plt.close()
        logging.info(f"Created table position heatmap: {output_path}")
 
        return output_path
 
    except Exception as e:
        logging.error(f"Error creating table position heatmap: {e}")
        logging.error(traceback.format_exc())
        return None
 
def create_corner_type_correlation_table(all_correlations, all_sigma_info, corners, types, moment_type, output_dir):
    """Create a tabular summary of correlations for each corner and type."""
    try:
        # Initialize structures for late and early sigma data
        late_sigma_table = {}
        early_sigma_table = {}
 
        # Categories
        categories = ['MC', 'Lib', 'abs_err', 'rel_err']
 
        # Iterate through corners and types
        for corner in corners:
            for type_name in types:
                # Generate key for results
                result_key = f"{corner}_{type_name}"
 
                # Check if we have correlations and sigma info for this key
                if result_key not in all_correlations or result_key not in all_sigma_info:
                    continue
 
                correlations = all_correlations[result_key]
                sigma_info = all_sigma_info[result_key]
 
                # Get sigma column names
                late_sigma = sigma_info.get('late_sigma')
                early_sigma = sigma_info.get('early_sigma')
 
                # Initialize table entries
                row_key = (corner, type_name)
                late_sigma_table[row_key] = {}
                early_sigma_table[row_key] = {}
 
                # Process late sigma correlations
                if late_sigma and 'late_sigma' in correlations:
                    for category in categories:
                        if category in correlations['late_sigma']:
                            # Filter correlations for the specified moment type
                            moment_corrs = [
                                v for k, v in correlations['late_sigma'][category].items()
                                if (moment_type == 'STD' and 'std' in k.lower()) or
                                   (moment_type == 'SKEW' and 'skew' in k.lower()) or
                                   (moment_type == 'MEANSHIFT' and 'meanshift' in k.lower())
                            ]
 
                            if moment_corrs:
                                late_sigma_table[row_key][category] = np.mean(moment_corrs)
                            else:
                                late_sigma_table[row_key][category] = np.nan
 
                # Process early sigma correlations
                if early_sigma and 'early_sigma' in correlations:
                    for category in categories:
                        if category in correlations['early_sigma']:
                            # Filter correlations for the specified moment type
                            moment_corrs = [
                                v for k, v in correlations['early_sigma'][category].items()
                                if (moment_type == 'STD' and 'std' in k.lower()) or
                                   (moment_type == 'SKEW' and 'skew' in k.lower()) or
                                   (moment_type == 'MEANSHIFT' and 'meanshift' in k.lower())
                            ]
 
                            if moment_corrs:
                                early_sigma_table[row_key][category] = np.mean(moment_corrs)
                            else:
                                early_sigma_table[row_key][category] = np.nan
 
        # Convert to DataFrames correctly, preserving the multi-index
        late_df = pd.DataFrame.from_dict(late_sigma_table, orient='index')
        early_df = pd.DataFrame.from_dict(early_sigma_table, orient='index')
 
        # Create MultiIndex correctly
        late_df.index = pd.MultiIndex.from_tuples(late_df.index, names=['corner', 'type'])
        early_df.index = pd.MultiIndex.from_tuples(early_df.index, names=['corner', 'type'])
 
        # Save to CSV
        late_df.to_csv(os.path.join(output_dir, f"late_sigma_{moment_type}_correlations.csv"))
        early_df.to_csv(os.path.join(output_dir, f"early_sigma_{moment_type}_correlations.csv"))
 
        return {
            'late_sigma': late_df,
            'early_sigma': early_df
        }
 
    except Exception as e:
        logging.error(f"Error creating corner-type correlation table for {moment_type}: {e}")
        logging.error(traceback.format_exc())
        return None
 
def load_csv_data(data_dir):
    """Load CSV data files with improved file parsing."""
    csv_files = glob.glob(os.path.join(data_dir, "*.csv"))
 
    logging.info(f"Found {len(csv_files)} CSV files")
 
    all_data = {}
    for file in csv_files:
        file_base = os.path.basename(file)
        logging.debug(f"Processing CSV file: {file_base}")
 
        # First, remove the .csv extension
        file_without_ext = file_base.replace('.csv', '')
 
        # Try to identify the pattern
        if file_without_ext.endswith('_data'):
            # Remove '_data' suffix
            file_without_data = file_without_ext[:-5]
            parts = file_without_data.split('_')
 
            if parts[-1] in ['MC', 'Lib', 'abs_err', 'rel_err']:
                category = parts[-1]
                file_name = '_'.join(parts[:-1])
            else:
                category = parts[-1]
                file_name = '_'.join(parts[:-1])
 
        elif file_without_ext.endswith('_abs'):
            category = 'abs_err'
            file_name = file_without_ext[:-4]  # Remove '_abs'
 
        elif file_without_ext.endswith('_rel'):
            category = 'rel_err'
            file_name = file_without_ext[:-4]  # Remove '_rel'
 
        elif 'err' in file_without_ext.split('_')[-1]:
            # Handle case where category is just 'err'
            category = file_without_ext.split('_')[-1]
            file_name = '_'.join(file_without_ext.split('_')[:-1])
 
        else:
            # Default parsing
            parts = file_without_ext.split('_')
            category = parts[-1]
            file_name = '_'.join(parts[:-1])
 
        logging.info(f"  Parsed file_name: {file_name}, category: {category}")
 
        if file_name not in all_data:
            all_data[file_name] = {}
 
        try:
            df = pd.read_csv(file)
            all_data[file_name][category] = df
            logging.info(f"  Loaded DataFrame with shape: {df.shape}")
            logging.debug(f"  Columns: {df.columns.tolist()[:10]}...")
        except Exception as e:
            logging.error(f"Error loading data from {file}: {e}")
 
    return all_data
 
 
 
 
 
def create_scatter_plot(df, x_col, y_col, hue_col, output_dir, title, filename):
    """Create a scatter plot with points colored by a categorical variable."""
    try:
        plt.figure(figsize=(10, 8))
 
        # Check if hue column exists and has many unique values
        if hue_col and hue_col in df.columns:
            n_unique = df[hue_col].nunique()
            if n_unique > 10:  # Too many unique values for discrete colors
                # Use continuous coloring instead
                scatter = plt.scatter(
                    df[x_col], df[y_col],
                    c=pd.factorize(df[hue_col])[0],
                    alpha=0.7,
                    cmap='tab20'
                )
                # Add legend with fewer items
                top_categories = df[hue_col].value_counts().head(10).index
                handles, labels = scatter.legend_elements()
                legend_dict = {cat: handles[i % len(handles)] for i, cat in enumerate(top_categories)}
                plt.legend(
                    [legend_dict[cat] for cat in top_categories],
                    [f"{cat} (+ others)" if i == len(top_categories)-1 else cat for i, cat in enumerate(top_categories)],
                    title=hue_col, loc="best"
                )
            else:
                # Use discrete coloring
                sns.scatterplot(x=x_col, y=y_col, hue=hue_col, data=df, alpha=0.7)
        else:
            # No hue column or hue_col is None
            sns.scatterplot(x=x_col, y=y_col, data=df, alpha=0.7)
 
        # Add title and labels
        plt.title(title, fontsize=14)
        plt.xlabel(x_col)
        plt.ylabel(y_col)
 
        # Add reference lines
        plt.axhline(y=0, color='gray', linestyle='-', alpha=0.3)
        plt.axvline(x=0, color='gray', linestyle='-', alpha=0.3)
 
        # Add linear regression line
        if len(df.dropna(subset=[x_col, y_col])) > 1:
            sns.regplot(x=x_col, y=y_col, data=df, scatter=False,
                       line_kws={"color": "red"})
 
            # Calculate correlation coefficient
            corr = df[x_col].corr(df[y_col])
            plt.text(0.05, 0.95, f"Correlation: {corr:.4f}",
                   transform=plt.gca().transAxes, fontsize=12,
                   verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.7))
 
        plt.tight_layout()
 
        # Save figure
        output_path = os.path.join(output_dir, filename)
        plt.savefig(output_path, dpi=150)
        plt.close()
 
        logging.info(f"Created scatter plot: {output_path}")
        return output_path
 
    except Exception as e:
        logging.error(f"Error creating scatter plot {filename}: {e}")
        logging.error(traceback.format_exc())
        return None
 
def create_centered_scatter_plot(df, x_col, y_col, output_dir, title, filename, category=None):
    """Create a scatter plot with top 10 outliers and aligned table in bottom right corner for cell labels."""
    try:
        # Suppress matplotlib warnings
        import warnings
        warnings.filterwarnings('ignore', message='This figure includes Axes that are not compatible')
 
        logging.debug(f"Creating centered scatter plot: {filename}")
        logging.debug(f"  x_col: {x_col}, y_col: {y_col}")
 
        # Check if columns exist
        if x_col not in df.columns or y_col not in df.columns:
            logging.error(f"Column not found. x_col: {x_col}, y_col: {y_col}")
            return None
 
        # Get valid data
        valid_data = df[[x_col, y_col]].dropna()
        if len(valid_data) < 2:
            logging.warning(f"Not enough valid data points to create scatter plot")
            return None
 
        # Create figure with just two plots side by side
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(24, 10))
 
        # Calculate outliers using z-score method
        from scipy import stats
        z_scores_x = np.abs(stats.zscore(valid_data[x_col]))
        z_scores_y = np.abs(stats.zscore(valid_data[y_col]))
        z_scores_combined = np.maximum(z_scores_x, z_scores_y)
        outliers = z_scores_combined > 2
 
        # Sort outliers by z-score and get top 10 only
        outlier_indices = valid_data.index[outliers].tolist()
        outlier_scores = z_scores_combined[outliers]
 
        # FORCE ONLY TOP 10 OUTLIERS
        max_outliers = 10
        if len(outlier_indices) > max_outliers:
            # Get top 10 outliers based on z-score
            top_outlier_mask = np.argsort(outlier_scores)[-max_outliers:]
            top_outlier_indices = [outlier_indices[i] for i in top_outlier_mask]
            other_outlier_indices = [idx for idx in outlier_indices if idx not in top_outlier_indices]
        else:
            top_outlier_indices = outlier_indices
            other_outlier_indices = []
 
        # Separate data
        normal_data = valid_data[~outliers]
        top_outlier_data = valid_data.loc[top_outlier_indices]
        other_outlier_data = valid_data.loc[other_outlier_indices] if other_outlier_indices else pd.DataFrame()
 
        # Save all outlier information to CSV
        outlier_info = []
        for idx in outlier_indices:
            info = {
                'index': idx,
                x_col: df.loc[idx, x_col],
                y_col: df.loc[idx, y_col],
                'z_score_x': z_scores_x[valid_data.index.get_loc(idx)],
                'z_score_y': z_scores_y[valid_data.index.get_loc(idx)],
                'z_score_combined': z_scores_combined[valid_data.index.get_loc(idx)]
            }
 
            # Add cell and table position if available
            if 'cell' in df.columns:
                info['cell'] = df.loc[idx, 'cell']
            if 'table_position' in df.columns:
                info['table_position'] = df.loc[idx, 'table_position']
 
            outlier_info.append(info)
 
        # Save to CSV
        if outlier_info:
            outlier_df = pd.DataFrame(outlier_info)
            outlier_filename = filename.replace('.png', '_outliers.csv')
            outlier_df.to_csv(os.path.join(output_dir, outlier_filename), index=False)
            logging.info(f"Saved outlier information to {outlier_filename}")
 
        # Calculate regression line parameters once
        from sklearn.linear_model import LinearRegression
        reg = None
        slope = None
        intercept = None
 
        if len(valid_data) > 2:
            X = valid_data[x_col].values.reshape(-1, 1)
            y = valid_data[y_col].values
            reg = LinearRegression().fit(X, y)
            slope = reg.coef_[0]
            intercept = reg.intercept_
 
        # Plot function for both subplots
        def plot_scatter(ax, label_type='cell'):
            # Plot normal points
            ax.scatter(normal_data[x_col], normal_data[y_col], alpha=0.6, s=50, color='blue', label='Normal points')
 
            # Plot other outliers (not in top 10)
            if len(other_outlier_data) > 0:
                ax.scatter(other_outlier_data[x_col], other_outlier_data[y_col],
                          alpha=0.6, s=80, color='orange', marker='s', label=f'Other outliers ({len(other_outlier_data)})')
 
            # Plot top 10 outliers
            table_data = []
            if len(top_outlier_data) > 0:
                for i, (idx, row) in enumerate(top_outlier_data.iterrows()):
                    # Plot the point
                    ax.scatter(row[x_col], row[y_col], alpha=0.8, s=100, color='red', marker='^')
 
                    # Get label
                    if label_type == 'cell' and 'cell' in df.columns and pd.notna(df.loc[idx, 'cell']):
                        label = df.loc[idx, 'cell']
                    elif label_type == 'table_position' and 'table_position' in df.columns and pd.notna(df.loc[idx, 'table_position']):
                        label = df.loc[idx, 'table_position']
                    else:
                        label = f"Point {idx}"
 
                    # Different labeling for cell vs table_position
                    if label_type == 'table_position':
                        # Direct labeling for table positions (short labels)
                        ax.annotate(label,
                                   xy=(row[x_col], row[y_col]),
                                   xytext=(0, 0),
                                   textcoords='offset points',
                                   fontsize=9,
                                   fontweight='bold',
                                   color='white',
                                   ha='center',
                                   va='center',
                                   bbox=dict(boxstyle='round,pad=0.2', fc='red', alpha=0.8))
                    else:
                        # Numbered approach for cell labels (potentially longer)
                        ax.annotate(str(i+1),
                                   xy=(row[x_col], row[y_col]),
                                   xytext=(5, 5),
                                   textcoords='offset points',
                                   fontsize=10,
                                   fontweight='bold',
                                   color='white',
                                   bbox=dict(boxstyle='circle,pad=0.3', fc='red', alpha=0.8))
 
                    # Add to table data (for cell labels only)
                    if label_type == 'cell':
                        table_data.append([str(i+1), label])
 
                # Add legend entry for outliers
                ax.scatter([], [], alpha=0.8, s=100, color='red', marker='^', label=f'Top 10 outliers')
 
            # Add title and labels
            ax.set_title(f"{title} - {label_type.replace('_', ' ').title()} Labels", fontsize=14, pad=20)
            ax.set_xlabel(x_col, fontsize=12)
            ax.set_ylabel(y_col, fontsize=12)
 
            # Set equal aspect ratio
            ax.set_aspect('equal', adjustable='box')
 
            # Find the maximum absolute value for setting equal ranges
            x_max = max(abs(valid_data[x_col].min()), abs(valid_data[x_col].max()))
            y_max = max(abs(valid_data[y_col].min()), abs(valid_data[y_col].max()))
            max_val = max(x_max, y_max) * 1.2
 
            # Set equal ranges for both axes
            ax.set_xlim(-max_val, max_val)
            ax.set_ylim(-max_val, max_val)
 
            # Draw axes through origin
            ax.axhline(y=0, color='k', linestyle='-', alpha=0.3, linewidth=1)
            ax.axvline(x=0, color='k', linestyle='-', alpha=0.3, linewidth=1)
 
            # Add y=x baseline
            x_range = np.linspace(-max_val, max_val, 100)
            ax.plot(x_range, x_range, 'g--', alpha=0.8, linewidth=2, label='y=x baseline')
 
            # Add grid
            ax.grid(True, alpha=0.3)
 
            # Add regression line if calculated
            if reg is not None:
                y_pred = reg.predict(x_range.reshape(-1, 1))
                ax.plot(x_range, y_pred, 'r-', alpha=0.8, linewidth=2, label='Regression line')
 
                # Calculate and display correlation
                corr = valid_data[x_col].corr(valid_data[y_col])
 
                # Add RÂ² value
                r2 = reg.score(X, y)
 
                # Create text box with highlighted correlation and RÂ² values
                textstr = '\n'.join([
                    f'Category: {category if category else "N/A"}',
                    f'Correlation: {corr:.4f}',
                    f'RÂ²: {r2:.4f}',
                    f'Total outliers: {len(outlier_indices)}',
                    f'Shown outliers: {len(top_outlier_indices)}'
                ])
 
                # Add text box with styled background
                props = dict(boxstyle='round', facecolor='lightblue', alpha=0.9, edgecolor='navy')
                ax.text(0.05, 0.95, textstr, transform=ax.transAxes, fontsize=11,
                       verticalalignment='top', bbox=props, fontweight='bold')
 
            # Add legend
            ax.legend(loc='upper right', fontsize=9)
 
            # Add table in bottom right corner for cell labels only
            if table_data and label_type == 'cell':
                # Calculate maximum width for cell names
                max_cell_width = max(len(row[1]) for row in table_data)
                max_cell_width = min(max_cell_width, 30)  # Cap at 30 characters
 
                # Create properly aligned table
                table_lines = []
                table_lines.append("Outlier Labels:")
                table_lines.append("")
 
                # Header with proper formatting
                header_format = f"{{:<3}}  {{:<{max_cell_width}}}"
                table_lines.append(header_format.format("#", "Cell"))
                table_lines.append("-" * (5 + max_cell_width))
 
                # Data rows with consistent formatting
                for row in table_data:
                    # Truncate cell name if too long
                    cell_name = row[1]
                    if len(cell_name) > max_cell_width:
                        cell_name = cell_name[:max_cell_width-3] + "..."
 
                    table_lines.append(header_format.format(row[0], cell_name))
 
                table_text = "\n".join(table_lines)
 
                # Position in bottom right corner
                ax.text(0.98, 0.02, table_text, transform=ax.transAxes,
                       fontsize=9, verticalalignment='bottom', horizontalalignment='right',
                       fontfamily='monospace',
                       bbox=dict(boxstyle='round', facecolor='white', alpha=0.9,
                                edgecolor='black', linewidth=0.5))
 
        # Create plots
        plot_scatter(ax1, label_type='cell')
        plot_scatter(ax2, label_type='table_position')
 
        # Use tight_layout
        plt.tight_layout()
 
        # Save figure
        output_path = os.path.join(output_dir, filename)
        plt.savefig(output_path, dpi=150, bbox_inches='tight',
                   facecolor='white', edgecolor='none')
 
        # Clear the figure to free memory
        plt.close(fig)
        plt.close('all')
 
        logging.debug(f"  Saved scatter plot to: {output_path}")
        return output_path
 
    except Exception as e:
        logging.error(f"Error creating centered scatter plot {filename}: {e}")
        import traceback
        logging.error(traceback.format_exc())
        plt.close('all')  # Ensure all figures are closed on error
        return None
 
def run_visualizations(data_dir, output_dir):
    """Run all visualizations with optimized scatter plots."""
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
 
    # [Previous loading code remains the same...]
 
    # Load data
    correlations = load_correlation_data(data_dir)
    outliers = load_outliers_data(data_dir)
    metadata = load_metadata(data_dir)
    sigma_info = load_sigma_info(data_dir)
    csv_data = load_csv_data(data_dir)
 
    logging.info(f"Loaded data: {len(correlations)} correlation files, {len(outliers)} outlier files")
 
    # [Previous matching and analysis code remains the same until scatter plot generation...]
 
    # Create individual visualizations for each corner and type
    logging.info("=== Starting Scatter Plot Generation ===")
 
    scatter_plot_count = 0
 
    for file_name, file_data in csv_data.items():
        logging.info(f"\nProcessing file: {file_name}")
        logging.info(f"Categories available: {list(file_data.keys())}")
 
        # Create subdirectory for this file
        file_output_dir = os.path.join(output_dir, file_name)
        os.makedirs(file_output_dir, exist_ok=True)
 
        # Process each category - NOW INCLUDING ALL CATEGORIES
        for category, df in file_data.items():
            logging.info(f"\n  Processing category: {category}")
            logging.info(f"  DataFrame shape: {df.shape}")
            logging.info(f"  Columns in DataFrame: {df.columns.tolist()[:10]}...")
 
            # Find sigma columns for this specific category
            late_sigma_candidates = [col for col in df.columns if
                                   'late' in col.lower() and 'sigma' in col.lower() and
                                   category.lower() in col.lower() and
                                   not col.endswith('_UB') and not col.endswith('_LB')]
 
            early_sigma_candidates = [col for col in df.columns if
                                    'early' in col.lower() and 'sigma' in col.lower() and
                                    category.lower() in col.lower() and
                                    not col.endswith('_UB') and not col.endswith('_LB')]
 
            # If no category-specific sigma columns found, try generic ones
            if not late_sigma_candidates:
                late_sigma_candidates = [col for col in df.columns if
                                       'late' in col.lower() and 'sigma' in col.lower() and
                                       not col.endswith('_UB') and not col.endswith('_LB')]
 
            if not early_sigma_candidates:
                early_sigma_candidates = [col for col in df.columns if
                                        'early' in col.lower() and 'sigma' in col.lower() and
                                        not col.endswith('_UB') and not col.endswith('_LB')]
 
            late_sigma = late_sigma_candidates[0] if late_sigma_candidates else None
            early_sigma = early_sigma_candidates[0] if early_sigma_candidates else None
 
            logging.info(f"  Category-specific sigma columns:")
            logging.info(f"    late_sigma: {late_sigma}")
            logging.info(f"    early_sigma: {early_sigma}")
 
            # Find moment columns for this specific category
            std_cols = [col for col in df.columns if
                       'std' in col.lower() and category.lower() in col.lower() and
                       not col.endswith('_UB') and not col.endswith('_LB')]
 
            skew_cols = [col for col in df.columns if
                        'skew' in col.lower() and category.lower() in col.lower() and
                        not col.endswith('_UB') and not col.endswith('_LB')]
 
            meanshift_cols = [col for col in df.columns if
                             'meanshift' in col.lower() and category.lower() in col.lower() and
                             not col.endswith('_UB') and not col.endswith('_LB')]
 
            logging.info(f"  Category-specific moment columns:")
            logging.info(f"    STD: {std_cols}")
            logging.info(f"    SKEW: {skew_cols}")
            logging.info(f"    MEANSHIFT: {meanshift_cols}")
 
            all_moment_cols = std_cols + skew_cols + meanshift_cols
 
            # Create late sigma scatter plots
            if late_sigma and late_sigma in df.columns:
                logging.info(f"  Creating late_sigma scatter plots for {category}")
 
                for col in all_moment_cols:
                    if col in df.columns:
                        logging.info(f"    Creating plot for {late_sigma} vs {col}")
 
                        # Check for valid data
                        valid_data = df[[late_sigma, col]].dropna()
                        logging.info(f"    Valid data points: {len(valid_data)}")
 
                        if len(valid_data) > 1:
                            try:
                                plot_path = create_centered_scatter_plot(
                                    df, late_sigma, col,
                                    file_output_dir,
                                    f"{file_name} - {category} - {late_sigma} vs {col}",
                                    f"{category}_late_sigma_{col}.png",
                                    category=category  # Pass category for legend
                                )
                                if plot_path:
                                    scatter_plot_count += 1
                                    logging.info(f"    Successfully created scatter plot: {plot_path}")
                            except Exception as e:
                                logging.error(f"    Error creating scatter plot: {e}")
                                import traceback
                                logging.error(traceback.format_exc())
 
            # Create early sigma scatter plots
            if early_sigma and early_sigma in df.columns:
                logging.info(f"  Creating early_sigma scatter plots for {category}")
 
                for col in all_moment_cols:
                    if col in df.columns:
                        logging.info(f"    Creating plot for {early_sigma} vs {col}")
 
                        # Check for valid data
                        valid_data = df[[early_sigma, col]].dropna()
                        logging.info(f"    Valid data points: {len(valid_data)}")
 
                        if len(valid_data) > 1:
                            try:
                                plot_path = create_centered_scatter_plot(
                                    df, early_sigma, col,
                                    file_output_dir,
                                    f"{file_name} - {category} - {early_sigma} vs {col}",
                                    f"{category}_early_sigma_{col}.png",
                                    category=category  # Pass category for legend
                                )
                                if plot_path:
                                    scatter_plot_count += 1
                                    logging.info(f"    Successfully created scatter plot: {plot_path}")
                            except Exception as e:
                                logging.error(f"    Error creating scatter plot: {e}")
                                import traceback
                                logging.error(traceback.format_exc())
 
    logging.info(f"\n=== Scatter Plot Generation Complete ===")
    logging.info(f"Total scatter plots created: {scatter_plot_count}")
    logging.info("Visualization generation complete")
 
# Add debugging to the scatter plot creation function
def create_scatter_plot(df, x_col, y_col, hue_col, output_dir, title, filename):
    """Create a scatter plot with enhanced debugging."""
    try:
        logging.debug(f"Creating scatter plot: {filename}")
        logging.debug(f"  x_col: {x_col}, y_col: {y_col}, hue_col: {hue_col}")
        logging.debug(f"  Data shape: {df.shape}")
 
        # Check if columns exist
        if x_col not in df.columns:
            logging.error(f"  x_col '{x_col}' not found in DataFrame columns")
            return None
        if y_col not in df.columns:
            logging.error(f"  y_col '{y_col}' not found in DataFrame columns")
            return None
 
        # Check for non-null data
        valid_data = df[[x_col, y_col]].dropna()
        logging.debug(f"  Valid data points after removing NaN: {len(valid_data)}")
 
        if len(valid_data) < 2:
            logging.warning(f"  Not enough valid data points to create scatter plot")
            return None
 
        plt.figure(figsize=(10, 8))
 
        # Rest of the scatter plot creation code...
 
        # Save figure
        output_path = os.path.join(output_dir, filename)
        plt.savefig(output_path, dpi=150)
        plt.close()
 
        logging.debug(f"  Saved scatter plot to: {output_path}")
        return output_path
 
    except Exception as e:
        logging.error(f"Error creating scatter plot {filename}: {e}")
        logging.error(traceback.format_exc())
        return None
 
 
def main():
    try:
        args = parse_args()
        setup_logging(args.output_dir)
 
        logging.info(f"Starting visualization generation")
 
        # Create output directory
        os.makedirs(args.output_dir, exist_ok=True)
 
        # Run visualizations
        run_visualizations(args.data_dir, args.output_dir)
 
        logging.info(f"Visualization generation complete")
    except Exception as e:
        logging.error(f"Unhandled exception in main: {e}")
        logging.error(traceback.format_exc())
        sys.exit(1)
 
if __name__ == "__main__":
    main()
