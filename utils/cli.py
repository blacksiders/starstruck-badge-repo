#!/usr/bin/env python3
"""
GitHub Repository Tools CLI

A unified command-line interface for repository analysis and visualization tools.
This CLI provides a single entry point for all repository-related operations.

Usage:
    python cli.py stats --repo username/repository [--days 30] [--output stats.json]
    python cli.py visualize --input stats.json [--output charts_dir]
    python cli.py analyze --repo username/repository [--days 30] [--output-dir ./analysis]
"""

import argparse
import importlib.util
import os
import sys
from pathlib import Path


class RepositoryToolsCLI:
    """Command-line interface for repository analysis tools."""
    
    def __init__(self):
        """Initialize the CLI with command parsers."""
        self.parser = argparse.ArgumentParser(
            description="GitHub Repository Analysis Tools",
            formatter_class=argparse.RawDescriptionHelpFormatter
        )
        self.subparsers = self.parser.add_subparsers(dest="command", help="Command to execute")
        
        # Initialize commands
        self._init_stats_command()
        self._init_visualize_command()
        self._init_analyze_command()
    
    def _init_stats_command(self):
        """Initialize the 'stats' command parser."""
        stats_parser = self.subparsers.add_parser(
            "stats", 
            help="Generate repository statistics"
        )
        stats_parser.add_argument("--repo", required=True, help="Repository name (username/repo)")
        stats_parser.add_argument("--days", type=int, default=30, help="Analysis period in days")
        stats_parser.add_argument("--token", help="GitHub API token (optional)")
        stats_parser.add_argument("--output", default="stats.json", help="Output JSON file")
    
    def _init_visualize_command(self):
        """Initialize the 'visualize' command parser."""
        viz_parser = self.subparsers.add_parser(
            "visualize", 
            help="Generate visualizations from statistics"
        )
        viz_parser.add_argument("--input", required=True, help="Input JSON file with repository statistics")
        viz_parser.add_argument("--output", default="./charts", help="Output directory for charts")
    
    def _init_analyze_command(self):
        """Initialize the 'analyze' command parser (combines stats and visualize)."""
        analyze_parser = self.subparsers.add_parser(
            "analyze", 
            help="Analyze repository and generate visualizations"
        )
        analyze_parser.add_argument("--repo", required=True, help="Repository name (username/repo)")
        analyze_parser.add_argument("--days", type=int, default=30, help="Analysis period in days")
        analyze_parser.add_argument("--token", help="GitHub API token (optional)")
        analyze_parser.add_argument("--output-dir", default="./analysis", help="Output directory")
    
    def _import_module(self, module_path):
        """Dynamically import a module from file path."""
        module_name = os.path.basename(module_path).replace(".py", "")
        spec = importlib.util.spec_from_file_location(module_name, module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    
    def run_stats(self, args):
        """Run the repository statistics generator."""
        try:
            # Dynamically import the repo_stats module
            current_dir = os.path.dirname(os.path.abspath(__file__))
            stats_path = os.path.join(current_dir, "repo_stats.py")
            
            if not os.path.exists(stats_path):
                print(f"Error: Could not find repo_stats.py at {stats_path}")
                return 1
            
            stats_module = self._import_module(stats_path)
            
            # Create analyzer and generate report
            analyzer = stats_module.RepoAnalyzer(args.repo, args.days, args.token)
            report = analyzer.generate_report()
            
            # Save report to file
            with open(args.output, 'w') as f:
                import json
                json.dump(report, f, indent=2)
            
            print(f"Statistics saved to {args.output}")
            return 0
            
        except Exception as e:
            print(f"Error generating statistics: {e}")
            return 1
    
    def run_visualize(self, args):
        """Run the statistics visualizer."""
        try:
            # Dynamically import the stats_visualizer module
            current_dir = os.path.dirname(os.path.abspath(__file__))
            viz_path = os.path.join(current_dir, "stats_visualizer.py")
            
            if not os.path.exists(viz_path):
                print(f"Error: Could not find stats_visualizer.py at {viz_path}")
                return 1
            
            viz_module = self._import_module(viz_path)
            
            # Load statistics data
            with open(args.input, 'r') as f:
                import json
                stats_data = json.load(f)
            
            # Generate visualizations
            visualizer = viz_module.StatsVisualizer(stats_data, args.output)
            visualizer.generate_html_report()
            
            print(f"Visualizations saved to {args.output}")
            return 0
            
        except Exception as e:
            print(f"Error generating visualizations: {e}")
            return 1
    
    def run_analyze(self, args):
        """Run both statistics and visualization in sequence."""
        try:
            # Create output directory
            os.makedirs(args.output_dir, exist_ok=True)
            
            # Run statistics
            stats_output = os.path.join(args.output_dir, "stats.json")
            stats_args = argparse.Namespace(
                repo=args.repo,
                days=args.days,
                token=args.token,
                output=stats_output
            )
            stats_result = self.run_stats(stats_args)
            
            if stats_result != 0:
                return stats_result
            
            # Run visualization
            viz_output = os.path.join(args.output_dir, "charts")
            viz_args = argparse.Namespace(
                input=stats_output,
                output=viz_output
            )
            viz_result = self.run_visualize(viz_args)
            
            if viz_result == 0:
                print(f"Analysis complete! Results saved to {args.output_dir}")
                print(f"Open {os.path.join(viz_output, 'stats_report.html')} to view the report")
            
            return viz_result
            
        except Exception as e:
            print(f"Error during analysis: {e}")
            return 1
    
    def run(self):
        """Parse arguments and execute the appropriate command."""
        args = self.parser.parse_args()
        
        if args.command is None:
            self.parser.print_help()
            return 1
        
        # Execute the appropriate command
        if args.command == "stats":
            return self.run_stats(args)
        elif args.command == "visualize":
            return self.run_visualize(args)
        elif args.command == "analyze":
            return self.run_analyze(args)
        else:
            print(f"Unknown command: {args.command}")
            return 1


def main():
    """Main entry point for the CLI."""
    cli = RepositoryToolsCLI()
    sys.exit(cli.run())


if __name__ == "__main__":
    main()