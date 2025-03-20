#!/usr/bin/env python3
"""
Repository Statistics Generator

This script analyzes a GitHub repository and generates statistics about:
- Commit frequency
- File types distribution
- Contributors activity

Usage:
    python repo_stats.py --repo username/repository [--days 30]
"""

import argparse
import datetime
import json
import os
import sys
from collections import Counter, defaultdict

try:
    import requests
except ImportError:
    print("Error: This script requires the 'requests' library.")
    print("Install it using: pip install requests")
    sys.exit(1)

class RepoAnalyzer:
    """Analyze GitHub repository statistics."""
    
    def __init__(self, repo, days=30, token=None):
        """Initialize with repository name and analysis period."""
        self.repo = repo
        self.days = days
        self.headers = {}
        if token:
            self.headers["Authorization"] = f"token {token}"
        
        # Base GitHub API URL
        self.api_base = "https://api.github.com"
    
    def get_commits(self):
        """Retrieve commits from the repository within the specified time period."""
        since_date = datetime.datetime.now() - datetime.timedelta(days=self.days)
        since_iso = since_date.isoformat()
        
        url = f"{self.api_base}/repos/{self.repo}/commits"
        params = {"since": since_iso, "per_page": 100}
        
        all_commits = []
        page = 1
        
        while True:
            params["page"] = page
            response = requests.get(url, headers=self.headers, params=params)
            
            if response.status_code != 200:
                print(f"Error fetching commits: {response.status_code}")
                print(response.json().get("message", "Unknown error"))
                break
            
            commits = response.json()
            if not commits:
                break
                
            all_commits.extend(commits)
            page += 1
            
            # Check if we've reached the last page
            if len(commits) < 100:
                break
        
        return all_commits
    
    def get_file_types(self):
        """Analyze file types in the repository."""
        url = f"{self.api_base}/repos/{self.repo}/git/trees/main?recursive=1"
        response = requests.get(url, headers=self.headers)
        
        if response.status_code != 200:
            print(f"Error fetching repository contents: {response.status_code}")
            return Counter()
        
        data = response.json()
        files = [item["path"] for item in data.get("tree", []) if item["type"] == "blob"]
        
        # Count file extensions
        extensions = [os.path.splitext(f)[1][1:].lower() or "no_extension" for f in files]
        return Counter(extensions)
    
    def get_contributors(self):
        """Analyze contributor activity."""
        url = f"{self.api_base}/repos/{self.repo}/contributors"
        response = requests.get(url, headers=self.headers)
        
        if response.status_code != 200:
            print(f"Error fetching contributors: {response.status_code}")
            return []
            
        return response.json()
    
    def generate_report(self):
        """Generate a complete repository statistics report."""
        print(f"Analyzing repository: {self.repo} for the past {self.days} days")
        
        # Get commits
        commits = self.get_commits()
        commit_count = len(commits)
        
        # Analyze commit dates
        commit_dates = defaultdict(int)
        authors = defaultdict(int)
        
        for commit in commits:
            date = commit["commit"]["author"]["date"][:10]  # YYYY-MM-DD
            commit_dates[date] += 1
            
            author = commit["commit"]["author"]["name"]
            authors[author] += 1
        
        # Get file types
        file_types = self.get_file_types()
        
        # Get contributors
        contributors = self.get_contributors()
        
        # Generate report
        report = {
            "repository": self.repo,
            "analysis_period_days": self.days,
            "total_commits": commit_count,
            "commit_frequency": dict(commit_dates),
            "authors": dict(authors),
            "file_types": dict(file_types),
            "contributors": [
                {"login": c["login"], "contributions": c["contributions"]}
                for c in contributors[:10]  # Top 10 contributors
            ]
        }
        
        return report

def main():
    """Parse arguments and run the analyzer."""
    parser = argparse.ArgumentParser(description="Generate GitHub repository statistics")
    parser.add_argument("--repo", required=True, help="Repository name (username/repo)")
    parser.add_argument("--days", type=int, default=30, help="Analysis period in days")
    parser.add_argument("--token", help="GitHub API token (optional)")
    parser.add_argument("--output", help="Output JSON file (optional)")
    
    args = parser.parse_args()
    
    analyzer = RepoAnalyzer(args.repo, args.days, args.token)
    report = analyzer.generate_report()
    
    # Output the report
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"Report saved to {args.output}")
    else:
        print(json.dumps(report, indent=2))

if __name__ == "__main__":
    main()