"""
Generate Live Documentation for Power BI Reports

This script automatically generates comprehensive markdown documentation
for Power BI reports by parsing TMDL files.

Usage:
    python generate_live_docs.py <project_directory>
    
Example:
    python generate_live_docs.py "C:/Users/robza/.../BI-STD/Project"
"""

import os
import sys
import re
from datetime import datetime

# Force UTF-8 encoding for stdout
sys.stdout.reconfigure(encoding='utf-8')

def get_developer_name():
    """Get developer name from Windows username"""
    return os.getenv('USERNAME', 'Unknown')

def parse_measure_from_tmdl(line):
    """Extract measure name from TMDL measure definition"""
    match = re.search(r'^\s*measure\s+[\'"]?([^\'"=]+)[\'"]?', line)
    if match:
        return match.group(1).strip()
    return None

def extract_dax_formula(lines, start_idx):
    """Extract multi-line DAX formula from TMDL"""
    dax_lines = []
    in_formula = False
    
    for i in range(start_idx, len(lines)):
        line = lines[i]
        if '```' in line and not in_formula:
            in_formula = True
            continue
        elif '```' in line and in_formula:
            break
        elif in_formula:
            dax_lines.append(line.rstrip())
    
    return '\n'.join(dax_lines)

def generate_report_documentation(semantic_model_dir, report_dir):
    """Generate comprehensive Notion-style markdown documentation for a single report"""
    
    # Extract report name by finding .SemanticModel in path
    parts = semantic_model_dir.split(os.sep)
    report_name = "Unknown Report"
    for part in parts:
        if part.endswith('.SemanticModel'):
            report_name = part.replace('.SemanticModel', '')
            break
    
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    developer = get_developer_name()
    
    doc_lines = []
    
    # Title with report name only (no emoji)
    doc_lines.append(f"# {report_name}")
    doc_lines.append("")
    
    # Metadata callout
    doc_lines.append("> [!NOTE]")
    doc_lines.append(f"> **Last Updated:** {timestamp}")
    doc_lines.append(f"> **Developer:** {developer}")
    doc_lines.append("")
    
    # Navigation TOC
    doc_lines.append("### 📑 Table of Contents")
    doc_lines.append("")
    doc_lines.append("- [Overview](#-overview)")
    doc_lines.append("- [Data Model](#-data-model)")
    doc_lines.append("- [Measures](#-measures)")
    doc_lines.append("- [Governance Compliance](#-governance-compliance)")
    doc_lines.append("- [Change History](#-change-history)")
    doc_lines.append("")
    doc_lines.append("---")
    doc_lines.append("")
    
    # Section 1: Overview
    doc_lines.append("### 🎯 Overview")
    doc_lines.append("")
    doc_lines.append(f"This Power BI report provides comprehensive data analysis and visualization capabilities for **{report_name}**.")
    doc_lines.append("")
    
    # Section 2: Data Model
    doc_lines.append("### 🗄️ Data Model")
    doc_lines.append("")
    
    # Parse relationships
    relationships_path = os.path.join(semantic_model_dir, 'definition', 'relationships.tmdl')
    if os.path.exists(relationships_path):
        with open(relationships_path, 'r', encoding='utf-8') as f:
            content = f.read()
            # Count relationships
            rel_count = content.count('relationship ')
            bidirectional = content.count('crossFilteringBehavior: bothDirections')
            
            doc_lines.append("#### 🔗 Relationships")
            doc_lines.append("")
            doc_lines.append("| Metric | Count |")
            doc_lines.append("|---------|--------|")
            doc_lines.append(f"| Total Relationships | {rel_count} |")
            doc_lines.append(f"| Bidirectional Filters | {bidirectional} |")
            doc_lines.append("")
            
            if bidirectional > 0:
                doc_lines.append("> [!WARNING]")
                doc_lines.append(f"> This model contains **{bidirectional} bidirectional relationship(s)** which may impact performance.")
                doc_lines.append("")
    
    # Section 3: Measures
    doc_lines.append("### 📐 Measures")
    doc_lines.append("")
    
    tables_dir = os.path.join(semantic_model_dir, 'definition', 'tables')
    measure_count = 0
    all_measures = []
    
    if os.path.exists(tables_dir):
        for table_file in sorted(os.listdir(tables_dir)):
            if table_file.endswith('.tmdl'):
                table_path = os.path.join(tables_dir, table_file)
                table_name = table_file.replace('.tmdl', '')
                
                with open(table_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                table_measures = []
                has_description = False
                description_text = ""
                
                for i, line in enumerate(lines):
                    stripped = line.strip()
                    
                    # Check for /// description
                    if stripped.startswith('///'):
                        description_text = stripped[3:].strip()
                        has_description = True
                        continue
                    
                    # Check for measure definition
                    measure_name = parse_measure_from_tmdl(line)
                    if measure_name:
                        measure_count += 1
                        dax = extract_dax_formula(lines, i)
                        
                        # Check for inline description property
                        inline_desc = ""
                        for j in range(i, min(i+10, len(lines))):
                            if 'description:' in lines[j].lower():
                                inline_desc = lines[j].split(':', 1)[1].strip().strip('"')
                                break
                        
                        final_desc = inline_desc or description_text if has_description else "*(No description provided)*"
                        
                        table_measures.append({
                            'name': measure_name,
                            'description': final_desc,
                            'dax': dax,
                            'table': table_name
                        })
                        
                        has_description = False
                        description_text = ""
                
                if table_measures:
                    all_measures.extend(table_measures)
    
    # Group measures by table
    if all_measures:
        current_table = None
        for m in all_measures:
            if m['table'] != current_table:
                if current_table is not None:
                    doc_lines.append("")
                doc_lines.append(f"#### 📊 {m['table']}")
                doc_lines.append("")
                current_table = m['table']
            
            # Measure card
            doc_lines.append(f"##### {m['name']}")
            doc_lines.append("")
            doc_lines.append(f"**📝 Description:** {m['description']}")
            doc_lines.append("")
            
            if m['dax']:
                doc_lines.append("<details>")
                doc_lines.append("<summary><b>💡 View DAX Formula</b></summary>")
                doc_lines.append("")
                doc_lines.append("```dax")
                doc_lines.append(m['dax'])
                doc_lines.append("```")
                doc_lines.append("")
                doc_lines.append("</details>")
                doc_lines.append("")
    
    doc_lines.append("> [!TIP]")
    doc_lines.append(f"> **Total Measures:** {measure_count}")
    doc_lines.append("")
    
    # Section 4: Governance Status
    doc_lines.append("### ✅ Governance Compliance")
    doc_lines.append("")
    doc_lines.append("> [!IMPORTANT]")
    doc_lines.append("> Run `Run_Governance_Check.bat` to verify current compliance status.")
    doc_lines.append(">")
    doc_lines.append("> Checks performed:")
    doc_lines.append("> - ⚡ Performance: Auto Date/Time must be disabled")
    doc_lines.append("> - 🔀 Logic: No bidirectional relationships")
    doc_lines.append("> - 📝 Documentation: All measures must have descriptions")
    doc_lines.append("")
    
    # Section 5: Change History
    doc_lines.append("### 📜 Change History")
    doc_lines.append("")
    doc_lines.append("| Date | Developer | Changes |")
    doc_lines.append("|------|-----------|---------|")
    doc_lines.append(f"| {datetime.now().strftime('%Y-%m-%d')} | {developer} | 🎉 Initial documentation generated |")
    doc_lines.append("")
    
    # Footer
    doc_lines.append("---")
    doc_lines.append("")
    doc_lines.append("*This documentation was automatically generated by the AB InBev BI Factory governance tools.*")
    
    # Write documentation file to PROJECT FOLDER (where .pbip file is)
    # semantic_model_dir could be either:
    #   "Project/Report.SemanticModel/definition" or
    #   "Project/Report.SemanticModel"
    # We need to get to "Project/" folder
    
    # Find the .SemanticModel folder in the path
    parts = semantic_model_dir.split(os.sep)
    for i, part in enumerate(parts):
        if part.endswith('.SemanticModel'):
            # Project folder is one level up from .SemanticModel
            project_dir = os.sep.join(parts[:i])
            break
    else:
        # Fallback: go up two levels from current location
        project_dir = os.path.dirname(os.path.dirname(semantic_model_dir))
    
    doc_path = os.path.join(project_dir, f'{report_name}_DOCUMENTATION.md')
    
    with open(doc_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(doc_lines))
    
    return doc_path

def generate_all_documentation(project_dir):
    """Generate documentation for all reports in the project directory"""
    
    print(f"\n📚 Generating live documentation for: {project_dir}\n")
    
    generated_count = 0
    
    for item in os.listdir(project_dir):
        item_path = os.path.join(project_dir, item)
        
        # Look for .SemanticModel directories
        if os.path.isdir(item_path) and item.endswith('.SemanticModel'):
            # Find corresponding .Report directory
            report_name = item.replace('.SemanticModel', '')
            report_dir = os.path.join(project_dir, f"{report_name}.Report")
            
            if not os.path.exists(report_dir):
                report_dir = None
            
            print(f"📄 Generating documentation for: {report_name}")
            
            try:
                doc_path = generate_report_documentation(item_path, report_dir)
                print(f"   ✅ Created: {doc_path}")
                generated_count += 1
            except Exception as e:
                print(f"   ❌ Error: {e}")
    
    print(f"\n🎉 Documentation generation complete! ({generated_count} reports)")

if __name__ == "__main__":
    target_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    generate_all_documentation(target_dir)
