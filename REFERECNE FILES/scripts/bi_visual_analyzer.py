"""
BI Factory - Visual Analyzer
Analyzes Report visuals to determine which parts of the model are actually utilized.
Provides a 'Utilization Score' for the dataset.
"""

import json
import argparse
import os
import sys
from pathlib import Path
from collections import defaultdict

# Fix Windows console encoding for emojis
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

class VisualAnalyzer:
    def __init__(self, pbip_folder):
        self.pbip_folder = Path(pbip_folder)
        self.used_columns = defaultdict(int)
        self.used_measures = defaultdict(int)
        self.visual_count = 0
        self.page_count = 0

    def find_visual_files(self):
        """Find all visual.json files in the Report folder"""
        report_folders = list(self.pbip_folder.glob("*.Report"))
        if not report_folders:
            # Check if current folder IS the report folder
            if self.pbip_folder.name.endswith('.Report'):
                report_folders = [self.pbip_folder]
        
        visual_files = []
        for report in report_folders:
            self.page_count += len(list(report.glob("definition/pages/*")))
            visuals = list(report.glob("definition/pages/**/visual.json"))
            visual_files.extend(visuals)
        
        self.visual_count = len(visual_files)
        return visual_files

    def analyze_visual(self, file_path):
        """Parse visual.json and extract referenced fields"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Convert to string to easily find references (simplified approach)
            content = json.dumps(data)
            
            # Look for "Property": "Table.Column" or "Table.Measure"
            # Note: This is an approximation for PBIP visuals
            import re
            
            # Find references like [Table].[Field]
            refs = re.findall(rf"['\"]([^'\"\s]+\.[^'\"\s]+)['\"]", content)
            
            for ref in refs:
                if '.' in ref:
                    table, field = ref.split('.', 1)
                    # We don't know if it's a measure or column for sure here, 
                    # but we'll flag it as 'used'
                    self.used_columns[f"{table}[{field}]"] += 1

        except Exception as e:
            print(f"⚠️ Error parsing {file_path.name}: {e}")

    def run(self):
        visuals = self.find_visual_files()
        if not visuals:
            print("❌ No visual files found. Point to a .pbip or .Report folder.")
            return

        print(f"🔍 Analyzing {len(visuals)} visuals across {self.page_count} pages...")
        for visual in visuals:
            self.analyze_visual(visual)

        self.print_report()

    def print_report(self):
        print("\n" + "="*50)
        print("📊 REPORT UTILIZATION SUMMARY")
        print("="*50)
        print(f"Total Visuals: {self.visual_count}")
        print(f"Unique Fields Used: {len(self.used_columns)}")
        print("-" * 50)
        
        print("\n🚀 Top Utilized Fields:")
        sorted_fields = sorted(self.used_columns.items(), key=lambda x: x[1], reverse=True)
        for field, count in sorted_fields[:10]:
            print(f"  • {field:30} used {count} times")

        print("\n💡 Optimization Tip:")
        if len(self.used_columns) < 5:
            print("  Low utilization detected. Consider if this dataset is too large for the report's needs.")
        else:
            print("  High utilization. Ensure all transformations are pushed to the source for better performance.")
        print("="*50 + "\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Analyze Power BI visual utilization')
    parser.add_argument('pbip_folder', help='Path to .pbip or .Report folder')
    args = parser.parse_args()
    
    analyzer = VisualAnalyzer(args.pbip_folder)
    analyzer.run()
