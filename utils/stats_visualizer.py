#!/usr/bin/env python3
"""
Repository Statistics Visualizer

This script generates visual charts based on repository statistics.
It works in conjunction with repo_stats.py to create visual representations
of repository activity.

Usage:
    python stats_visualizer.py --input stats_data.json --output charts_directory
"""

import argparse
import json
import os
import sys
from datetime import datetime, timedelta

try:
    import matplotlib.pyplot as plt
    import numpy as np
except ImportError:
    print("Error: This script requires matplotlib and numpy libraries.")
    print("Install them using: pip install matplotlib numpy")
    sys.exit(1)

class StatsVisualizer:
    """Generate visualizations from repository statistics data."""
    
    def __init__(self, stats_data, output_dir="."):
        """Initialize with statistics data and output directory."""
        self.stats = stats_data
        self.output_dir = output_dir
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
    
    def generate_commit_frequency_chart(self):
        """Generate a chart showing commit frequency over time."""
        # Extract data
        dates = list(self.stats["commit_frequency"].keys())
        counts = list(self.stats["commit_frequency"].values())
        
        # Sort dates
        date_count_pairs = sorted(zip(dates, counts), key=lambda x: x[0])
        dates = [pair[0] for pair in date_count_pairs]
        counts = [pair[1] for pair in date_count_pairs]
        
        # Create figure
        plt.figure(figsize=(12, 6))
        plt.bar(dates, counts, color='skyblue')
        plt.xlabel('Date')
        plt.ylabel('Number of Commits')
        plt.title(f'Commit Frequency for {self.stats["repository"]}')
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        # Save figure
        output_path = os.path.join(self.output_dir, 'commit_frequency.png')
        plt.savefig(output_path)
        plt.close()
        
        return output_path
    
    def generate_file_types_chart(self):
        """Generate a pie chart showing file type distribution."""
        # Extract data
        file_types = self.stats["file_types"]
        
        # Filter out types with very small counts for readability
        total_files = sum(file_types.values())
        threshold = total_files * 0.02  # 2% threshold
        
        # Group small categories as "Other"
        grouped_types = {}
        other_count = 0
        
        for ftype, count in file_types.items():
            if count >= threshold:
                grouped_types[ftype] = count
            else:
                other_count += count
        
        if other_count > 0:
            grouped_types["Other"] = other_count
        
        # Create pie chart
        plt.figure(figsize=(10, 8))
        plt.pie(grouped_types.values(), labels=grouped_types.keys(), autopct='%1.1f%%', 
                startangle=140, shadow=True)
        plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
        plt.title(f'File Type Distribution for {self.stats["repository"]}')
        
        # Save figure
        output_path = os.path.join(self.output_dir, 'file_types.png')
        plt.savefig(output_path)
        plt.close()
        
        return output_path
    
    def generate_contributors_chart(self):
        """Generate a horizontal bar chart showing top contributors."""
        # Extract data
        contributors = self.stats["contributors"]
        
        # Sort by contributions (descending)
        contributors.sort(key=lambda x: x["contributions"], reverse=True)
        
        # Limit to top 10 contributors
        top_contributors = contributors[:10]
        
        # Extract names and contribution counts
        names = [c["login"] for c in top_contributors]
        contributions = [c["contributions"] for c in top_contributors]
        
        # Create horizontal bar chart
        plt.figure(figsize=(10, 8))
        plt.barh(names, contributions, color='lightgreen')
        plt.xlabel('Number of Contributions')
        plt.ylabel('Contributor')
        plt.title(f'Top Contributors for {self.stats["repository"]}')
        plt.tight_layout()
        
        # Save figure
        output_path = os.path.join(self.output_dir, 'top_contributors.png')
        plt.savefig(output_path)
        plt.close()
        
        return output_path
    
    def generate_authors_activity_chart(self):
        """Generate a chart showing commit activity by author."""
        # Extract data
        authors = self.stats["authors"]
        
        # Sort by number of commits (descending)
        sorted_authors = sorted(authors.items(), key=lambda x: x[1], reverse=True)
        
        # Limit to top 8 authors for readability
        top_authors = sorted_authors[:8]
        
        # Extract names and commit counts
        names = [a[0] for a in top_authors]
        commits = [a[1] for a in top_authors]
        
        # Create bar chart
        plt.figure(figsize=(10, 6))
        plt.bar(names, commits, color='coral')
        plt.xlabel('Author')
        plt.ylabel('Number of Commits')
        plt.title(f'Author Activity for {self.stats["repository"]}')
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        # Save figure
        output_path = os.path.join(self.output_dir, 'author_activity.png')
        plt.savefig(output_path)
        plt.close()
        
        return output_path
    
    def generate_all_charts(self):
        """Generate all available charts and return paths."""
        print(f"Generating visualizations for {self.stats['repository']}")
        
        charts = {
            "commit_frequency": self.generate_commit_frequency_chart(),
            "file_types": self.generate_file_types_chart(),
            "contributors": self.generate_contributors_chart(),
            "author_activity": self.generate_authors_activity_chart()
        }
        
        print(f"Charts generated and saved to {self.output_dir}")
        return charts
    
    def generate_html_report(self):
        """Generate an HTML report with all charts embedded."""
        # Generate all charts first
        chart_paths = self.generate_all_charts()
        
        # Create HTML content
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Repository Statistics for {self.stats['repository']}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                h1, h2 {{ color: #333; }}
                .chart-container {{ margin: 30px 0; }}
                .chart {{ max-width: 100%; box-shadow: 0 4px 8px rgba(0,0,0,0.1); }}
                .summary {{ background-color: #f5f5f5; padding: 15px; border-radius: 5px; }}
            </style>
        </head>
        <body>
            <h1>Repository Statistics: {self.stats['repository']}</h1>
            <div class="summary">
                <h2>Summary</h2>
                <p>Analysis period: {self.stats['analysis_period_days']} days</p>
                <p>Total commits: {self.stats['total_commits']}</p>
                <p>Number of file types: {len(self.stats['file_types'])}</p>
                <p>Number of contributors: {len(self.stats['contributors'])}</p>
            </div>
            
            <div class="chart-container">
                <h2>Commit Frequency</h2>
                <img class="chart" src="commit_frequency.png" alt="Commit Frequency Chart">
            </div>
            
            <div class="chart-container">
                <h2>File Type Distribution</h2>
                <img class="chart" src="file_types.png" alt="File Types Chart">
            </div>
            
            <div class="chart-container">
                <h2>Top Contributors</h2>
                <img class="chart" src="top_contributors.png" alt="Top Contributors Chart">
            </div>
            
            <div class="chart-container">
                <h2>Author Activity</h2>
                <img class="chart" src="author_activity.png" alt="Author Activity Chart">
            </div>
            
            <footer>
                <p>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </footer>
        </body>
        </html>
        """
        
        # Write HTML to file
        output_path = os.path.join(self.output_dir, 'stats_report.html')
        with open(output_path, 'w') as f:
            f.write(html_content)
        
        print(f"HTML report generated: {output_path}")
        return output_path

def main():
    """Parse arguments and run the visualizer."""
    parser = argparse.ArgumentParser(description="Generate visualizations from repository statistics")
    parser.add_argument("--input", required=True, help="Input JSON file with repository statistics")
    parser.add_argument("--output", default="./charts", help="Output directory for charts")
    
    args = parser.parse_args()
    
    # Load statistics data
    try:
        with open(args.input, 'r') as f:
            stats_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading statistics data: {e}")
        sys.exit(1)
    
    # Generate visualizations
    visualizer = StatsVisualizer(stats_data, args.output)
    visualizer.generate_html_report()

if __name__ == "__main__":
    main()