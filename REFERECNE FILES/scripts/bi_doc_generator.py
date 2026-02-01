"""
BI Factory - Live Documentation Builder (Pro Edition)
Parses TMDL model files and generates a Power BI specific Data Dictionary.
Includes Fact/Dim identification, full DAX logic, and Display Folders.
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path
from datetime import datetime

# Fix Windows console encoding
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass


class DocBuilder:
    """Builds documentation from Power BI TMDL files"""
    
    def __init__(self, pbip_folder):
        self.pbip_folder = Path(pbip_folder)
        self.tables = []
        self.measures = []
        self.relationships = []
        self.model_info = {}
        
    def find_semantic_model(self):
        """Find the .SemanticModel folder"""
        if str(self.pbip_folder).endswith('.SemanticModel'):
            return self.pbip_folder
        
        for item in self.pbip_folder.iterdir():
            if item.is_dir() and item.name.endswith('.SemanticModel'):
                return item
        
        if (self.pbip_folder / 'definition').exists():
            return self.pbip_folder
            
        return None
    
    def parse_model_tmdl(self, model_path):
        """Parse model.tmdl for high-level info"""
        if not model_path.exists():
            return
            
        content = model_path.read_text(encoding='utf-8')
        culture_match = re.search(r'culture:\s*(.+)', content)
        if culture_match:
            self.model_info['culture'] = culture_match.group(1).strip()
        
        name_match = re.search(r'model\s+(.+)', content)
        if name_match:
            self.model_info['name'] = name_match.group(1).strip().strip("'").strip('"')
    
    def parse_table_tmdl(self, table_path):
        """Parse a table TMDL file with support for Display Folders and Full DAX"""
        content = table_path.read_text(encoding='utf-8')
        
        # Skip hidden/system tables
        if 'LocalDateTable' in table_path.name or 'DateTableTemplate' in table_path.name:
            return None
        
        # Extract table name
        first_line = content.split('\n')[0]
        table_match = re.match(r"table\s+['\"]?(.+?)['\"]?\s*$", first_line)
        table_name = table_match.group(1).strip() if table_match else table_path.stem
        
        # Check if table is hidden
        header_end = content.find('\n\tcolumn ') if '\n\tcolumn ' in content else len(content)
        table_header = content[:header_end]
        is_table_hidden = bool(re.search(r'^\tisHidden\s*$', table_header, re.MULTILINE))
        
        table_info = {
            'name': table_name,
            'file': str(table_path),
            'columns': [],
            'measures': [],
            'is_hidden': is_table_hidden,
            'type': 'Dimension' # Default, will be updated based on relationships
        }
        
        # Parse columns
        column_blocks = re.split(r'\n\tcolumn\s+', content)
        for block in column_blocks[1:]:
            lines = block.split('\n')
            col_name_line = lines[0]
            col_name_match = re.match(r"['\"]?(.+?)['\"]?\s*$", col_name_line)
            col_name = col_name_match.group(1).strip() if col_name_match else 'Unknown'
            
            # Extract attributes
            col_body = '\n'.join(lines[1:30])
            dtype_match = re.search(r'dataType:\s*(\w+)', col_body)
            folder_match = re.search(r'displayFolder:\s*[\'"]?(.+?)[\'"]?\s*$', col_body, re.MULTILINE)
            desc_match = re.search(r'description:\s*[\'"]?(.+?)[\'"]?\s*$', col_body, re.MULTILINE)
            
            table_info['columns'].append({
                'name': col_name,
                'dataType': dtype_match.group(1) if dtype_match else 'unknown',
                'isHidden': bool(re.search(r'^\s+isHidden\s*$', col_body, re.MULTILINE)),
                'displayFolder': folder_match.group(1) if folder_match else None,
                'description': desc_match.group(1) if desc_match else None
            })
        
        # Parse measures
        measure_blocks = re.split(r'\n\tmeasure\s+', content)
        for block in measure_blocks[1:]:
            lines = block.split('\n')
            first_line = lines[0]
            
            measure_match = re.match(r"['\"]?(.+?)['\"]?\s*=\s*(.*)$", first_line)
            if measure_match:
                measure_name = measure_match.group(1).strip()
                expr_start = measure_match.group(2).strip()
                
                # Capture FULL DAX expression
                expr_lines = [expr_start]
                block_text = '\n'.join(lines)
                
                # Find end of DAX expression (stops at known keywords like description, displayFolder, formatString)
                for line in lines[1:]:
                    stripped = line.strip()
                    if any(stripped.startswith(k) for k in ['description:', 'displayFolder:', 'formatString:', 'lineageTag:', 'annotation']):
                        break
                    expr_lines.append(line.replace('\t\t', '  ')) # Minimal indentation fix
                
                full_dax = '\n'.join(expr_lines).strip()
                
                # Extract metadata
                desc_match = re.search(r'description:\s*[\'"]?(.+?)[\'"]?\s*$', block_text, re.MULTILINE)
                folder_match = re.search(r'displayFolder:\s*[\'"]?(.+?)[\'"]?\s*$', block_text, re.MULTILINE)
                
                measure_info = {
                    'name': measure_name,
                    'table': table_name,
                    'expression': full_dax,
                    'description': desc_match.group(1) if desc_match else None,
                    'displayFolder': folder_match.group(1) if folder_match else None
                }
                
                table_info['measures'].append(measure_info)
                self.measures.append(measure_info)
        
        return table_info
    
    def parse_relationships(self, rel_path):
        """Parse relationships.tmdl"""
        if not rel_path.exists():
            return
            
        content = rel_path.read_text(encoding='utf-8')
        rel_pattern = r'relationship\s+([a-f0-9\-]+)\s*\n((?:\t+[^\n]+\n)*)'
        for match in re.finditer(rel_pattern, content):
            rel_body = match.group(2)
            from_match = re.search(r'fromColumn:\s*([^\n]+)', rel_body)
            to_match = re.search(r'toColumn:\s*([^\n]+)', rel_body)
            
            if from_match and to_match:
                from_full = from_match.group(1).strip().replace("'", "").replace('"', '')
                to_full = to_match.group(1).strip().replace("'", "").replace('"', '')
                
                # Identify Fact/Dim candidates
                # PBI/TMDL uses Table.Column or Table[Column]
                if '[' in from_full:
                    from_table = from_full.split('[')[0].strip()
                elif '.' in from_full:
                    from_table = from_full.split('.')[0].strip()
                else:
                    from_table = from_full
                
                self.relationships.append({
                    'from': from_full,
                    'to': to_full,
                    'fromTable': from_table,
                    'active': 'isActive: false' not in rel_body,
                    'bidirectional': 'both' in rel_body.lower()
                })

    def identify_table_types(self):
        """Classify tables as Fact or Dimension based on relationships"""
        many_side_tables = set(rel['fromTable'] for rel in self.relationships)
        
        for table in self.tables:
            if table['name'] in many_side_tables:
                table['type'] = 'Fact'
            else:
                table['type'] = 'Dimension'

    def build(self):
        """Main build process"""
        semantic_model = self.find_semantic_model()
        if not semantic_model: return None
        
        definition_path = semantic_model / 'definition'
        if not definition_path.exists(): return None
        
        self.parse_model_tmdl(definition_path / 'model.tmdl')
        self.parse_relationships(definition_path / 'relationships.tmdl')
        
        tables_path = definition_path / 'tables'
        if tables_path.exists():
            for table_file in tables_path.glob('*.tmdl'):
                table_info = self.parse_table_tmdl(table_file)
                if table_info:
                    self.tables.append(table_info)
        
        self.identify_table_types()
        return True
    
    def generate_markdown(self):
        """Generate a sleek, developer-friendly PBI Data Dictionary"""
        lines = []
        model_name = self.model_info.get('name', 'Power BI Project')
        
        lines.append(f"# 💎 {model_name} - Advanced Data Dictionary")
        lines.append(f"\n> **Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"> **Context:** This document is auto-generated from the model's metadata.")
        lines.append("")
        
        # Relationship Diagram (Simplified Text)
        if self.relationships:
            lines.append("## 🔗 Relationship Map")
            lines.append("```mermaid")
            lines.append("erDiagram")
            for rel in self.relationships:
                from_t = rel['from'].split('[')[0].strip()
                to_t = rel['to'].split('[')[0].strip()
                line_style = "||--o{" if not rel['bidirectional'] else "||--||"
                lines.append(f'    "{to_t}" {line_style} "{from_t}" : "relationship"')
            lines.append("```")
            lines.append("")

        # Table Inventory
        lines.append("## 📋 Model Blueprint")
        lines.append("| Table Type | Table Name | Items | Description |")
        lines.append("|:---:|---|:---:|---|")
        for table in sorted(self.tables, key=lambda x: (x['type'], x['name'])):
            if table['is_hidden']: continue
            icon = "📈" if table['type'] == 'Fact' else "👤"
            item_count = len(table['columns']) + len(table['measures'])
            lines.append(f"| {icon} **{table['type']}** | [{table['name']}](#{table['name'].lower().replace(' ', '-')}) | {item_count} | - |")
        lines.append("")

        # Detailed Sections
        for table_type in ['Fact', 'Dimension']:
            type_tables = [t for t in self.tables if t['type'] == table_type and not t['is_hidden']]
            if not type_tables: continue
            
            lines.append(f"---")
            lines.append(f"## {'📈 Factory Data (Facts)' if table_type == 'Fact' else '👤 Business Context (Dimensions)'}")
            lines.append("")
            
            for table in sorted(type_tables, key=lambda x: x['name']):
                lines.append(f"### {table['name']}")
                lines.append(f"*Path: `{Path(table['file']).name}`*")
                lines.append("")
                
                # Group measures by Display Folder
                if table['measures']:
                    lines.append("#### 📐 Measures")
                    folders = {}
                    for m in table['measures']:
                        folder = m['displayFolder'] or "Other Measures"
                        if folder not in folders: folders[folder] = []
                        folders[folder].append(m)
                    
                    for folder in sorted(folders.keys()):
                        lines.append(f"\n**📁 {folder}**")
                        for m in folders[folder]:
                            lines.append(f"<details><summary><b>{m['name']}</b>: {m['description'] or '<i>No description provided</i>'}</summary>")
                            lines.append("\n```dax")
                            lines.append(f"{m['name']} = \n{m['expression']}")
                            lines.append("```")
                            lines.append("</details>")
                    lines.append("")

                # Columns Table
                visible_cols = [c for c in table['columns'] if not c['isHidden']]
                if visible_cols:
                    lines.append("#### 📋 Columns")
                    lines.append("| Name | Type | Folder | Description |")
                    lines.append("|---|---|---|---|")
                    for col in visible_cols:
                        lines.append(f"| {col['name']} | `{col['dataType']}` | {col['displayFolder'] or '-'} | {col['description'] or '-'} |")
                lines.append("")

        return '\n'.join(lines)
    
    def save(self, output_path=None):
        """Save documentation to file"""
        if output_path is None:
            output_path = self.pbip_folder.parent / f"{self.pbip_folder.stem}_DataDictionary.md"
        
        content = self.generate_markdown()
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"📄 Documentation saved to: {output_path}")
        return output_path


def main():
    parser = argparse.ArgumentParser(description='BI Factory - PBI Data Dictionary Builder')
    parser.add_argument('pbip_folder', help='Path to the PBIP folder')
    parser.add_argument('--output', '-o', help='Output file path')
    
    args = parser.parse_args()
    print("🚀 Enhancing model documentation...")
    
    builder = DocBuilder(args.pbip_folder)
    if builder.build():
        output = builder.save(args.output)
        print(f"✅ Success! View your live documentation here: {output}")
    else:
        print("❌ Error: Could not find valid PBIP structure.")
        return 1
    return 0


if __name__ == "__main__":
    exit(main())
