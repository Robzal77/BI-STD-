"""
Wiki Builder for BI Factory Knowledge Base

This script creates and maintains a Wiki-based knowledge base from Power BI
project documentation. Supports local testing and Azure DevOps Wiki integration.

Usage:
    python scripts/wiki_builder.py
"""

import os
import sys
import csv
from datetime import datetime
import shutil

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

WIKI_ROOT = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'wiki')
PROJECTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ActiveReports')
LOGS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')

def ensure_wiki_structure():
    """Create Wiki folder structure if it doesn't exist"""
    directories = [
        WIKI_ROOT,
        os.path.join(WIKI_ROOT, 'Projects'),
        os.path.join(WIKI_ROOT, 'Governance-Logs')
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"[+] Created: {directory}")
    
    # Create .order files for ADO Wiki navigation
    with open(os.path.join(WIKI_ROOT, '.order'), 'w') as f:
        f.write('Home\n')
        f.write('Projects\n')
        f.write('Governance-Logs\n')
    
    with open(os.path.join(WIKI_ROOT, 'Projects', '.order'), 'w') as f:
        f.write('')  # Will be populated dynamically
    
    print("[+] Wiki structure initialized")

def get_project_status():
    """Read governance logs to get project compliance status"""
    log_file = os.path.join(LOGS_DIR, 'governance_log.csv')
    
    if not os.path.exists(log_file):
        return []
    
    projects = {}
    
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                report_name = row['report_name']
                # Keep only the most recent entry for each report
                if report_name not in projects or row['timestamp'] > projects[report_name]['timestamp']:
                    projects[report_name] = {
                        'name': report_name,
                        'status': row['overall_status'],
                        'timestamp': row['timestamp'],
                        'developer': row['developer'],
                        'failures': int(row['failure_count'])
                    }
    except Exception as e:
        print(f"[!] Warning: Could not read log file: {e}")
    
    return list(projects.values())

def generate_home_page(projects):
    """Generate Wiki Home page with project index"""
    
    home_content = []
    
    # Header
    home_content.append("# 📊 Power BI Knowledge Base")
    home_content.append("")
    home_content.append("> **Auto-generated documentation for all AB InBev Power BI reports**")
    home_content.append("")
    home_content.append(f"*Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")
    home_content.append("")
    home_content.append("---")
    home_content.append("")
    
    # Quick Links
    home_content.append("## 🔗 Quick Links")
    home_content.append("")
    home_content.append("- [View All Projects →](Projects)")
    home_content.append("- [Governance Logs →](Governance-Logs/Compliance-Status)")
    home_content.append("- [Developer Guide](https://github.com/your-org/bi-factory#readme)")
    home_content.append("")
    home_content.append("---")
    home_content.append("")
    
    # Active Projects Table
    home_content.append("## 📁 Active Projects")
    home_content.append("")
    
    if projects:
        home_content.append("| Report Name | Status | Last Updated | Developer |")
        home_content.append("|-------------|:------:|--------------|-----------|")
        
        for project in sorted(projects, key=lambda x: x['timestamp'], reverse=True):
            status_emoji = "✅" if project['status'] == 'PASS' else "❌"
            # Convert report name to Wiki-safe format
            wiki_name = project['name'].replace(' ', '-').replace('_', '-')
            
            home_content.append(
                f"| [{project['name']}](Projects/{wiki_name}) | "
                f"{status_emoji} {project['status']} | "
                f"{project['timestamp']} | "
                f"{project['developer']} |"
            )
    else:
        home_content.append("*No projects found. Run governance checks to populate.*")
    
    home_content.append("")
    home_content.append("---")
    home_content.append("")
    
    # Compliance Overview
    total = len(projects)
    passing = sum(1 for p in projects if p['status'] == 'PASS')
    failing = total - passing
    pass_rate = (passing / total * 100) if total > 0 else 0
    
    home_content.append("## 📈 Compliance Overview")
    home_content.append("")
    home_content.append(f"- **Total Reports:** {total}")
    home_content.append(f"- **Passing:** {passing} ({pass_rate:.0f}%)")
    home_content.append(f"- **Failing:** {failing}")
    home_content.append("")
    
    if failing > 0:
        home_content.append("> [!WARNING]")
        home_content.append(f"> **{failing} report(s) not meeting governance standards**")
        home_content.append(">")
        home_content.append("> Common issues:")
        home_content.append("> - Auto Date/Time enabled")
        home_content.append("> - Bidirectional relationships")
        home_content.append("> - Missing measure descriptions")
    
    home_content.append("")
    home_content.append("---")
    home_content.append("")
    
    # Footer
    home_content.append("## 💡 How to Use This Wiki")
    home_content.append("")
    home_content.append("1. **Browse Projects** - Click any project name to view its data dictionary")
    home_content.append("2. **Check Status** - Green ✅ means compliant, Red ❌ needs attention")
    home_content.append("3. **View Details** - Each project page includes:")
    home_content.append("   - Relationship diagrams")
    home_content.append("   - Table definitions")
    home_content.append("   - Measure documentation with DAX formulas")
    home_content.append("   - Column descriptions")
    home_content.append("")
    home_content.append("---")
    home_content.append("")
    home_content.append("*This Wiki is automatically updated when governance checks pass.*")
    
    # Write Home page
    home_path = os.path.join(WIKI_ROOT, 'Home.md')
    with open(home_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(home_content))
    
    print(f"[+] Generated: Home.md")

def sync_project_documentation():
    """Copy project documentation files to Wiki/Projects folder (recursively)"""
    
    project_order = []
    synced_count = 0
    
    # Walk through all subdirectories in ActiveReports
    for root, dirs, files in os.walk(PROJECTS_DIR):
        # Skip Archive and Templates folders - they're references only
        dirs[:] = [d for d in dirs if d not in ['Archive', 'Templates']]
        
        for filename in files:
            if filename.endswith('_DOCUMENTATION.md'):
                source_path = os.path.join(root, filename)
                
                # Get subfolder name for organization
                rel_path = os.path.relpath(root, PROJECTS_DIR)
                if rel_path == '.':
                    category = 'Root'
                else:
                    # Use first subfolder name as category (LocalTest, Templates, etc.)
                    category = rel_path.split(os.sep)[0]
                
                # Convert filename to Wiki format (spaces → hyphens)
                wiki_filename = filename.replace(' ', '-').replace('_DOCUMENTATION.md', '.md')
                
                # Add category prefix for better organization
                if category != 'Root':
                    wiki_filename = f"{category}-{wiki_filename}"
                
                dest_path = os.path.join(WIKI_ROOT, 'Projects', wiki_filename)
                
                # Copy file
                shutil.copy2(source_path, dest_path)
                print(f"[+] Synced [{category}]: {filename} → Projects/{wiki_filename}")
                
                # Add to navigation order
                project_order.append(wiki_filename[:-3])  # Remove .md extension
                synced_count += 1
    
    # Update .order file for Projects folder
    if project_order:
        with open(os.path.join(WIKI_ROOT, 'Projects', '.order'), 'w') as f:
            f.write('\n'.join(sorted(project_order)))
    
    print(f"[+] Synced {synced_count} project documentation file(s)")
    return synced_count

def generate_compliance_status():
    """Generate Governance Logs compliance status page"""
    
    log_file = os.path.join(LOGS_DIR, 'governance_log.csv')
    
    if not os.path.exists(log_file):
        print("[!] No governance log found")
        return
    
    content = []
    
    content.append("# 📊 Governance Compliance Status")
    content.append("")
    content.append("> **Detailed compliance tracking for all reports**")
    content.append("")
    content.append(f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")
    content.append("")
    content.append("---")
    content.append("")
    
    # Read and display recent checks
    content.append("## 📋 Recent Governance Checks")
    content.append("")
    content.append("| Report | Status | Auto Date/Time | Bidirectional Filters | Missing Descriptions | Developer | Timestamp |")
    content.append("|--------|:------:|:--------------:|:---------------------:|:--------------------:|-----------|-----------|")
    
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            
            # Show most recent 50 entries
            for row in rows[-50:]:
                status_emoji = "✅" if row['overall_status'] == 'PASS' else "❌"
                auto_dt_emoji = "✅" if row['auto_datetime_status'] == 'PASS' else "❌"
                bidir_count = int(row['bidirectional_count'])
                missing_count = int(row['missing_descriptions_count'])
                
                content.append(
                    f"| {row['report_name']} | "
                    f"{status_emoji} {row['overall_status']} | "
                    f"{auto_dt_emoji} | "
                    f"{bidir_count} | "
                    f"{missing_count} | "
                    f"{row['developer']} | "
                    f"{row['timestamp']} |"
                )
    except Exception as e:
        content.append(f"*Error reading log file: {e}*")
    
    content.append("")
    content.append("---")
    content.append("")
    
    # Governance Rules Reference
    content.append("## ✅ Governance Rules")
    content.append("")
    content.append("### Performance")
    content.append("- **Auto Date/Time** must be DISABLED in model settings")
    content.append("")
    content.append("### Logic")
    content.append("- **No bidirectional relationships** allowed")
    content.append("- All relationships should be single-direction")
    content.append("")
    content.append("### Documentation")
    content.append("- **All measures must have descriptions**")
    content.append("- Use the Properties pane in Power BI to add descriptions")
    
    # Write compliance status page
    status_path = os.path.join(WIKI_ROOT, 'Governance-Logs', 'Compliance-Status.md')
    with open(status_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(content))
    
    print(f"[+] Generated: Governance-Logs/Compliance-Status.md")

def build_wiki():
    """Main function to build complete Wiki"""
    
    print("\n==> Building Wiki Knowledge Base...\n")
    
    # Step 1: Ensure folder structure
    ensure_wiki_structure()
    print()
    
    # Step 2: Sync project documentation
    project_count = sync_project_documentation()
    print()
    
    # Step 3: Get project status from logs
    projects = get_project_status()
    
    # Step 4: Generate Home page
    generate_home_page(projects)
    print()
    
    # Step 5: Generate compliance status
    generate_compliance_status()
    print()
    
    print("=" * 70)
    print("==> Wiki build complete!")
    print("=" * 70)
    print(f"\nWiki Location: {WIKI_ROOT}")
    print(f"Projects Synced: {project_count}")
    print(f"\n[>] Open wiki/Home.md in a Markdown viewer to preview")
    print("\n[!] Tip: Use VS Code, Typora, or GitHub to view Markdown files")

if __name__ == "__main__":
    build_wiki()
