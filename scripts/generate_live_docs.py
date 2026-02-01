"""
Generate Advanced Data Dictionary for Power BI Reports (AdventureWorks Format)

This script automatically generates data dictionary documentation matching
the AdventureWorks Sales reference format.
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

def parse_relationships(semantic_model_dir):
    """Parse relationships.tmdl to create Mermaid diagram"""
    relationships_path = None
    
    if os.path.basename(semantic_model_dir) == 'definition':
        relationships_path = os.path.join(semantic_model_dir, 'relationships.tmdl')
    else:
        relationships_path = os.path.join(semantic_model_dir, 'definition', 'relationships.tmdl')
    
    relationships = []
    
    if os.path.exists(relationships_path):
        with open(relationships_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Parse each relationship block
        rel_blocks = re.findall(r'relationship\s+[^\n]*\n((?:\s+[^\n]+\n)*)', content, re.MULTILINE)
        
        for block in rel_blocks:
            from_table = None
            from_col = None
            to_table = None
            to_col = None
            
            # Parse fromColumn
            from_match = re.search(r"fromColumn:\s+([^.]+)\.(.+)", block)
            if from_match:
                from_table = from_match.group(1).strip().strip("'\"")
                from_col = from_match.group(2).strip().strip("'\"")
            
            # Parse toColumn
            to_match = re.search(r"toColumn:\s+([^.]+)\.(.+)", block)
            if to_match:
                to_table = to_match.group(1).strip().strip("'\"")
                to_col = to_match.group(2).strip().strip("'\"")
            
            if from_table and to_table:
                relationships.append({
                    'from_table': from_table,
                    'from_col': from_col,
                    'to_table': to_table,
                    'to_col': to_col
                })
    
    return relationships

def parse_tmdl_table(file_path):
    """Parse a TMDL table file and extract columns and measures"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        lines = content.split('\n')
    
    table_info = {
        'columns': [],
        'measures': [],
        'name': None
    }
    
    # Extract table name
    table_match = re.search(r'^table\s+(?:[\'"]([^\'"]+)[\'"]|(\S+))', content, re.MULTILINE)
    if table_match:
        table_info['name'] = table_match.group(1) if table_match.group(1) else table_match.group(2)
        table_info['name'] = table_info['name'].strip()
    
    # Parse measures
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Check for measure with /// comment
        if line.strip().startswith('///'):
            description = line.strip()[3:].strip()
            i += 1
            if i < len(lines) and 'measure' in lines[i]:
                measure_match = re.search(r'measure\s+(?:[\'"]([^\'"=`]+)[\'"]|([^=`]+))', lines[i])
                if measure_match:
                    measure_name = measure_match.group(1) if measure_match.group(1) else measure_match.group(2)
                    measure_name = measure_name.strip()
                    
                    # Extract DAX formula
                    dax_lines = []
                    if '```' in lines[i] or (i+1 < len(lines) and '```' in lines[i+1]):
                        in_dax = False
                        for j in range(i, min(i+20, len(lines))):
                            if '```' in lines[j] and not in_dax:
                                in_dax = True
                                continue
                            elif '```' in lines[j] and in_dax:
                                break
                            elif in_dax:
                                dax_lines.append(lines[j].rstrip())
                    
                    table_info['measures'].append({
                        'name': measure_name,
                        'description': description if description else 'No description provided',
                        'dax': '\n'.join(dax_lines) if dax_lines else ''
                    })
        
        # Check for measure without /// comment
        elif line.strip().startswith('measure'):
            measure_match = re.search(r'measure\s+(?:[\'"]([^\'"=`]+)[\'"]|([^=`\s]+))', line)
            if measure_match:
                measure_name = measure_match.group(1) if measure_match.group(1) else measure_match.group(2)
                measure_name = measure_name.strip()
                
                # Check for description property
                description = None
                for j in range(i+1, min(i+10, len(lines))):
                    if lines[j].strip().lower().startswith('description'):
                        desc_match = re.search(r'description\s*:\s*"([^"]*)"', lines[j], re.IGNORECASE)
                        if desc_match:
                            description = desc_match.group(1)
                        break
                
                # Extract DAX
                dax_lines = []
                if '```' in line or (i+1 < len(lines) and '```' in lines[i+1]):
                    in_dax = False
                    for j in range(i, min(i+20, len(lines))):
                        if '```' in lines[j] and not in_dax:
                            in_dax = True
                            continue
                        elif '```' in lines[j] and in_dax:
                            break
                        elif in_dax:
                            dax_lines.append(lines[j].rstrip())
                
                table_info['measures'].append({
                    'name': measure_name,
                    'description': description if description else 'No description provided',
                    'dax': '\n'.join(dax_lines) if dax_lines else ''
                })
        
        # Parse columns
        elif line.strip().startswith('column'):
            col_match = re.search(r'column\s+(?:[\'"]([^\'"]+)[\'"]|(\S+))', line)
            if col_match:
                col_name = col_match.group(1) if col_match.group(1) else col_match.group(2)
                col_name = col_name.strip()
                
                # Get data type from next lines
                data_type = '-'
                description = '-'
                for j in range(i+1, min(i+15, len(lines))):
                    if 'dataType:' in lines[j]:
                        type_match = re.search(r'dataType:\s*(\w+)', lines[j])
                        if type_match:
                            data_type = f'`{type_match.group(1)}`'
                    if lines[j].strip().lower().startswith('description'):
                        desc_match = re.search(r'description\s*:\s*"([^"]*)"', lines[j], re.IGNORECASE)
                        if desc_match:
                            description = desc_match.group(1)
                    # Stop at next column/measure/partition
                    if lines[j].strip() and not lines[j].startswith('\t') and j > i+1:
                        break
                
                table_info['columns'].append({
                    'name': col_name,
                    'type': data_type,
                    'folder': '-',
                    'description': description
                })
        
        i += 1
    
    return table_info

def generate_report_documentation(semantic_model_dir, report_dir):
    """Generate AdventureWorks-style data dictionary"""
    
    # Extract report name
    parts = semantic_model_dir.split(os.sep)
    report_name = "Unknown Report"
    for part in parts:
        if part.endswith('.SemanticModel'):
            report_name = part.replace('.SemanticModel', '')
            break
    
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    doc_lines = []
    
    # Title
    doc_lines.append(f"# {report_name} - Documentation")
    doc_lines.append("")
    doc_lines.append(f"> **Generated:** {timestamp}")
    doc_lines.append(f"> **Context:** This document is auto-generated from the model's metadata.")
    doc_lines.append("")
    
    # Table of Contents
    doc_lines.append("## 📑 Quick Navigation")
    doc_lines.append("")
    doc_lines.append("- [Relationship Map](#-relationship-map)")
    doc_lines.append("- [Model Blueprint](#-model-blueprint)")
    doc_lines.append("- [Factory Data (Facts)](#-factory-data-facts)")
    doc_lines.append("- [Business Context (Dimensions)](#-business-context-dimensions)")
    doc_lines.append("")
    doc_lines.append("---")
    doc_lines.append("")
    
    # Parse relationships for Mermaid diagram
    relationships = parse_relationships(semantic_model_dir)
    
    if relationships:
        doc_lines.append("## 🔗 Relationship Map")
        doc_lines.append("")
        doc_lines.append("*Visual representation of how tables are connected in the data model.*")
        doc_lines.append("")
        doc_lines.append("```mermaid")
        doc_lines.append("erDiagram")
        for rel in relationships:
            # Format: "FromTable.FromCol" ||--o{ "ToTable.ToCol" : "relationship"
            doc_lines.append(f'    "{rel["from_table"]}.{rel["from_col"]}" ||--o{{ "{rel["to_table"]}.{rel["to_col"]}" : "relationship"')
        doc_lines.append("```")
        doc_lines.append("")
        doc_lines.append("---")
        doc_lines.append("")
    
    # Parse all tables
    if os.path.basename(semantic_model_dir) == 'definition':
        tables_dir = os.path.join(semantic_model_dir, 'tables')
    else:
        tables_dir = os.path.join(semantic_model_dir, 'definition', 'tables')
    
    all_tables = []
    
    if os.path.exists(tables_dir):
        for table_file in sorted(os.listdir(tables_dir)):
            if table_file.endswith('.tmdl'):
                table_path = os.path.join(tables_dir, table_file)
                table_info = parse_tmdl_table(table_path)
                table_info['file'] = table_file
                # Simple heuristic: tables with measures are facts, others are dimensions
                table_info['type'] = 'Fact' if table_info['measures'] else 'Dimension'
                all_tables.append(table_info)
    
    # Model Blueprint
    doc_lines.append("## 📋 Model Blueprint")
    doc_lines.append("")
    doc_lines.append("*Overview of all tables, their types, and item counts.*")
    doc_lines.append("")
    doc_lines.append("| Table Type | Table Name | Items | Description |")
    
    for table in all_tables:
        table_name = table['name'] or table['file'].replace('.tmdl', '')
        items_count = len(table['columns']) + len(table['measures'])
        emoji = "📈" if table['type'] == 'Fact' else "👤"
        anchor = table_name.lower().replace(' ', '-')
        doc_lines.append(f"| {emoji} **{table['type']}** | [{table_name}](#{anchor}) | {items_count} | - |")
    
    doc_lines.append("")
    doc_lines.append("---")
    doc_lines.append("")
    
    # Factory Data (Facts)
    fact_tables = [t for t in all_tables if t['type'] == 'Fact']
    if fact_tables:
        doc_lines.append("## 📈 Factory Data (Facts)")
        doc_lines.append("")
        doc_lines.append("*Tables containing transactional data and metrics (measures).*")
        doc_lines.append("")
        
        for table in fact_tables:
            table_name = table['name'] or table['file'].replace('.tmdl', '')
            
            doc_lines.append(f"### {table_name}")
            doc_lines.append(f"*Path: `{table['file']}`*")
            doc_lines.append("")
            
            # Measures
            if table['measures']:
                doc_lines.append("#### 📐 Measures")
                doc_lines.append("")
                doc_lines.append("**📁 Other Measures**")
                for measure in table['measures']:
                    doc_lines.append(f"<details><summary><b>{measure['name']}</b>: <i>{measure['description']}</i></summary>")
                    doc_lines.append("")
                    if measure['dax']:
                        doc_lines.append("```dax")
                        doc_lines.append(f"{measure['name']} = ")
                        doc_lines.append("```")
                        for line in measure['dax'].split('\n'):
                            doc_lines.append(f"  \t{line}")
                        doc_lines.append("  \t```")
                        doc_lines.append("```")
                    doc_lines.append("</details>")
                    doc_lines.append("")
            
            # Columns
            if table['columns']:
                doc_lines.append("")
                doc_lines.append("#### 📋 Columns")
                doc_lines.append("")
                doc_lines.append("| Name | Type | Folder | Description |")
                for col in table['columns']:
                    doc_lines.append(f"| {col['name']} | {col['type']} | {col['folder']} | {col['description']} |")
                doc_lines.append("")
            
            doc_lines.append("---")
            doc_lines.append("")
    
    # Business Context (Dimensions)
    dim_tables = [t for t in all_tables if t['type'] == 'Dimension']
    if dim_tables:
        doc_lines.append("## 👤 Business Context (Dimensions)")
        doc_lines.append("")
        doc_lines.append("*Reference tables providing context and descriptive attributes for analysis.*")
        doc_lines.append("")
        
        for table in dim_tables:
            table_name = table['name'] or table['file'].replace('.tmdl', '')
            
            doc_lines.append(f"### {table_name}")
            doc_lines.append(f"*Path: `{table['file']}`*")
            doc_lines.append("")
            
            # Columns
            if table['columns']:
                doc_lines.append("")
                doc_lines.append("#### 📋 Columns")
                doc_lines.append("")
                doc_lines.append("| Name | Type | Folder | Description |")
                for col in table['columns']:
                    doc_lines.append(f"| {col['name']} | {col['type']} | {col['folder']} | {col['description']} |")
                doc_lines.append("")
            
            doc_lines.append("---")
            doc_lines.append("")
    
    # Write documentation file
    parts = semantic_model_dir.split(os.sep)
    for i, part in enumerate(parts):
        if part.endswith('.SemanticModel'):
            project_dir = os.sep.join(parts[:i])
            break
    else:
        project_dir = os.path.dirname(os.path.dirname(semantic_model_dir))
    
    doc_path = os.path.join(project_dir, f'{report_name}_Documentation.md')
    
    with open(doc_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(doc_lines))
    
    # Also generate HTML version
    try:
        import importlib.util
        html_converter_path = os.path.join(os.path.dirname(__file__), 'markdown_to_html.py')
        spec = importlib.util.spec_from_file_location("html_converter", html_converter_path)
        html_converter = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(html_converter)
        
        html_path = html_converter.convert_markdown_file(doc_path)
        print(f"   📄 Also created HTML: {html_path}")
    except Exception as e:
        print(f"   ⚠️ HTML generation failed: {e}")
    
    return doc_path

def generate_all_documentation(project_dir):
    """Generate documentation for all reports in the project directory"""
    
    print(f"\n📚 Generating documentation for: {project_dir}\n")
    
    generated_count = 0
    
    for item in os.listdir(project_dir):
        item_path = os.path.join(project_dir, item)
        
        if os.path.isdir(item_path) and item.endswith('.SemanticModel'):
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
                import traceback
                traceback.print_exc()
    
    print(f"\n🎉 Documentation generation complete! ({generated_count} reports)")

if __name__ == "__main__":
    target_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    generate_all_documentation(target_dir)
