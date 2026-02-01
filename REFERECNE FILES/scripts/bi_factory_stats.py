"""
BI Factory - Stats & Categorization
Analyzes audit_log.csv to categorize reports into Gold, Silver, and Bronze.
Identifies the 'Fastest Transformed' and 'Best Performing' reports.
"""

import csv
import os
import sys
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# Fix Windows console encoding for characters like ⭐
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

class FactoryStats:
    def __init__(self, log_path):
        self.log_path = Path(log_path)
        self.reports = defaultdict(list) # report_name -> list of logs

    def load_logs(self):
        if not self.log_path.exists():
            print(f"❌ Log file not found at {self.log_path}")
            return False
        
        with open(self.log_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                self.reports[row['report_name']].append(row)
        return True

    def analyze(self):
        gold = []   # Score == 100
        silver = [] # Score >= 70
        bronze = [] # Score < 70
        
        fastest_report = None
        min_transformation_time = float('inf')

        for name, logs in self.reports.items():
            # Get latest log
            logs.sort(key=lambda x: x['timestamp'])
            latest = logs[-1]
            score = float(latest['score'])
            
            if score == 100:
                gold.append(name)
            elif score >= 70:
                silver.append(name)
            else:
                bronze.append(name)

            # Analyze transformation speed (Time from first log to first 100 score)
            if len(logs) > 1:
                first_ts = datetime.strptime(logs[0]['timestamp'], '%Y-%m-%d %H:%M:%S')
                for log in logs:
                    if float(log['score']) == 100:
                        reached_100_ts = datetime.strptime(log['timestamp'], '%Y-%m-%d %H:%M:%S')
                        diff = (reached_100_ts - first_ts).total_seconds()
                        if diff < min_transformation_time:
                            min_transformation_time = diff
                            fastest_report = name
                        break

        self.print_summary(gold, silver, bronze, fastest_report, min_transformation_time)

    def print_summary(self, gold, silver, bronze, fastest, fastest_time):
        print("\n" + "⭐" * 25)
        print("🏛️  BI FACTORY PERFORMANCE DASHBOARD")
        print("⭐" * 25 + "\n")

        print(f"🏆 GOLD REPORTS (10/10 Compliance):")
        if gold:
            for g in gold: print(f"  • {g}")
        else: print("  _None yet. Keep fixing!_")

        print(f"\n🥈 SILVER REPORTS (Compliant with warnings):")
        if silver:
            for s in silver: print(f"  • {s}")
        else: print("  _None._")

        print(f"\n🥉 BRONZE REPORTS (Critical Failures):")
        if bronze:
            for b in bronze: print(f"  • {b}")
        else: print("  _None. Great job!_")

        print("\n" + "-" * 50)
        print("🏎️  TRANSFORMATION CHAMPIONS")
        print("-" * 50)
        if fastest:
            mins = int(fastest_time // 60)
            secs = int(fastest_time % 60)
            print(f"Fastest to 100%: {fastest} ({mins}m {secs}s)")
        else:
            print("Transformation speed analysis requires at least one Gold report.")
        
        print("\n" + "=" * 50)
        total = len(self.reports)
        if total > 0:
            gold_pct = (len(gold) / total) * 100
            print(f"Factory Compliance Rate: {gold_pct:.1f}%")
        print("=" * 50 + "\n")

if __name__ == "__main__":
    # Calculate relative path
    script_dir = Path(__file__).parent
    root_dir = script_dir.parent
    log_file = root_dir / "projects" / "audit_log.csv"
    stats = FactoryStats(log_file)
    if stats.load_logs():
        stats.analyze()
