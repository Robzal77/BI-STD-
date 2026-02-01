"""
Markdown to HTML Converter for Power BI Documentation

Converts generated Markdown documentation to styled HTML for easy viewing in browsers.
Includes syntax highlighting, responsive design, and professional styling.

Usage:
    python Scripts/markdown_to_html.py path/to/documentation.md
"""

import os
import sys
import re
from datetime import datetime

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - Power BI Documentation</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f5f5f5;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 40px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        
        header {{
            border-bottom: 3px solid #0066cc;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }}
        
        h1 {{
            color: #0066cc;
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        
        h2 {{
            color: #0066cc;
            font-size: 2em;
            margin-top: 40px;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid #e0e0e0;
        }}
        
        h3 {{
            color: #333;
            font-size: 1.5em;
            margin-top: 30px;
            margin-bottom: 10px;
        }}
        
        h4 {{
            color: #666;
            font-size: 1.2em;
            margin-top: 20px;
            margin-bottom: 10px;
        }}
        
        blockquote {{
            background: #f9f9f9;
            border-left: 4px solid #0066cc;
            padding: 15px 20px;
            margin: 20px 0;
            color: #666;
        }}
        
        code {{
            background: #f4f4f4;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Consolas', 'Monaco', monospace;
            font-size: 0.9em;
            color: #c7254e;
        }}
        
        pre {{
            background: #282c34;
            color: #abb2bf;
            padding: 20px;
            border-radius: 5px;
            overflow-x: auto;
            margin: 20px 0;
        }}
        
        pre code {{
            background: transparent;
            color: inherit;
            padding: 0;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        
        th, td {{
            padding: 12px;
            text-align: left;
            border: 1px solid #ddd;
        }}
        
        th {{
            background: #0066cc;
            color: white;
            font-weight: 600;
        }}
        
        tr:nth-child(even) {{
            background: #f9f9f9;
        }}
        
        tr:hover {{
            background: #f0f7ff;
        }}
        
        details {{
            margin: 15px 0;
            padding: 15px;
            background: #f8f9fa;
            border-left: 3px solid #0066cc;
            border-radius: 4px;
        }}
        
        summary {{
            cursor: pointer;
            font-weight: 600;
            padding: 5px 0;
            color: #0066cc;
        }}
        
        summary:hover {{
            color: #004999;
        }}
        
        details[open] {{
            background: #e8f4f8;
        }}
        
        a {{
            color: #0066cc;
            text-decoration: none;
        }}
        
        a:hover {{
            text-decoration: underline;
        }}
        
        nav {{
            background: #f0f7ff;
            padding: 20px;
            border-radius: 5px;
            margin: 30px 0;
        }}
        
        nav h2 {{
            margin-top: 0;
            font-size: 1.3em;
            border-bottom: none;
        }}
        
        nav ul {{
            list-style: none;
            padding-left: 0;
        }}
        
        nav li {{
            margin: 8px 0;
        }}
        
        footer {{
            margin-top: 60px;
            padding-top: 20px;
            border-top: 2px solid #e0e0e0;
            text-align: center;
            color: #666;
            font-size: 0.9em;
        }}
        
        .mermaid {{
            text-align: center;
            margin: 30px 0;
        }}
        
        .dax-code {{
            background: #1e1e1e;
            color: #dcdcaa;
            padding: 20px;
            border-radius: 5px;
            margin: 10px 0;
            font-family: 'Consolas', 'Monaco', monospace;
        }}
        
        @media print {{
            body {{
                background: white;
                padding: 0;
            }}
            
            .container {{
                box-shadow: none;
                padding: 20px;
            }}
            
            details {{
                border: 1px solid #ddd;
            }}
            
            details[open] summary ~ * {{
                display: block;
            }}
        }}
    </style>
    <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
    <script>
        mermaid.initialize({{ startOnLoad: true }});
        
        window.addEventListener('DOMContentLoaded', (event) => {{
            // Smooth scrolling for anchor links
            document.querySelectorAll('a[href^="#"]').forEach(anchor => {{
                anchor.addEventListener('click', function (e) {{
                    e.preventDefault();
                    const target = document.querySelector(this.getAttribute('href'));
                    if (target) {{
                        target.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
                    }}
                }});
            }});
        }});
    </script>
</head>
<body>
    <div class="container">
        {content}
        <footer>
            <p>Generated on {timestamp} | Power BI BI Factory | AB InBev</p>
        </footer>
    </div>
</body>
</html>
"""

def markdown_to_html(md_content):
    """Convert Markdown to HTML with basic formatting"""
    
    html = md_content
    
    # Headers
    html = re.sub(r'^#### (.*?)$', r'<h4>\1</h4>', html, flags=re.MULTILINE)
    html = re.sub(r'^### (.*?)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
    html = re.sub(r'^## (.*?)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
    html = re.sub(r'^# (.*?)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)
    
    # Blockquotes
    html = re.sub(r'^> (.*?)$', r'<blockquote>\1</blockquote>', html, flags=re.MULTILINE)
    
    # Horizontal rules
    html = html.replace('---', '<hr>')
    
    # Bold
    html = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', html)
    html = re.sub(r'__(.*?)__', r'<strong>\1</strong>', html)
    
    # Italic
    html = re.sub(r'\*(.*?)\*', r'<em>\1</em>', html)
    html = re.sub(r'_(.*?)_', r'<em>\1</em>', html)
    
    # Code blocks (must come before inline code)
    html = re.sub(r'```mermaid(.*?)```', r'<div class="mermaid">\1</div>', html, flags=re.DOTALL)
    html = re.sub(r'```dax(.*?)```', r'<pre class="dax-code"><code>\1</code></pre>', html, flags=re.DOTALL)
    html = re.sub(r'```(.*?)```', r'<pre><code>\1</code></pre>', html, flags=re.DOTALL)
    
    # Inline code
    html = re.sub(r'`([^`]+)`', r'<code>\1</code>', html)
    
    # Links [text](url)
    html = re.sub(r'\[([^\]]+)\]\(([^\)]+)\)', r'<a href="\2">\1</a>', html)
    
    # Process tables
    html = process_tables(html)
    
    # Line breaks
    html = html.replace('\n\n', '</p><p>')
    html = '<p>' + html + '</p>'
    
    # Clean up empty paragraphs
    html = re.sub(r'<p>\s*</p>', '', html)
    html = re.sub(r'<p>(<h[1-6]>)', r'\1', html)
    html = re.sub(r'(</h[1-6]>)</p>', r'\1', html)
    html = re.sub(r'<p>(<hr>)</p>', r'\1', html)
    html = re.sub(r'<p>(<pre)', r'\1', html)
    html = re.sub(r'(</pre>)</p>', r'\1', html)
    html = re.sub(r'<p>(<div)', r'\1', html)
    html = re.sub(r'(</div>)</p>', r'\1', html)
    html = re.sub(r'<p>(<table)', r'\1', html)
    html = re.sub(r'(</table>)</p>', r'\1', html)
    html = re.sub(r'<p>(<details)', r'\1', html)
    html = re.sub(r'(</details>)</p>', r'\1', html)
    html = re.sub(r'<p>(<blockquote)', r'\1', html)
    html = re.sub(r'(</blockquote>)</p>', r'\1', html)
    
    return html

def process_tables(md_content):
    """Convert Markdown tables to HTML"""
    
    lines = md_content.split('\n')
    html_lines = []
    in_table = False
    
    for i, line in enumerate(lines):
        # Detect table rows
        if '|' in line and line.strip().startswith('|'):
            if not in_table:
                # Start of table
                html_lines.append('<table>')
                in_table = True
                is_header = True
            
            # Skip separator rows
            if re.match(r'\|[\s\-:|]+\|', line):
                continue
            
            # Parse table row
            cells = [cell.strip() for cell in line.split('|')[1:-1]]
            
            if is_header:
                html_lines.append('<thead><tr>')
                for cell in cells:
                    html_lines.append(f'<th>{cell}</th>')
                html_lines.append('</tr></thead><tbody>')
                is_header = False
            else:
                html_lines.append('<tr>')
                for cell in cells:
                    html_lines.append(f'<td>{cell}</td>')
                html_lines.append('</tr>')
        else:
            if in_table:
                # End of table
                html_lines.append('</tbody></table>')
                in_table = False
            html_lines.append(line)
    
    if in_table:
        html_lines.append('</tbody></table>')
    
    return '\n'.join(html_lines)

def convert_markdown_file(md_path):
    """Convert a Markdown file to HTML"""
    
    with open(md_path, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    # Extract title from first header
    title_match = re.search(r'^# (.+)$', md_content, re.MULTILINE)
    title = title_match.group(1) if title_match else "Power BI Documentation"
    
    # Convert content
    html_content = markdown_to_html(md_content)
    
    # Generate full HTML
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    html = HTML_TEMPLATE.format(
        title=title,
        content=html_content,
        timestamp=timestamp
    )
    
    # Output path
    html_path = md_path.replace('.md', '.html')
    
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    return html_path

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python markdown_to_html.py <markdown_file.md>")
        sys.exit(1)
    
    md_file = sys.argv[1]
    
    if not os.path.exists(md_file):
        print(f"Error: File not found: {md_file}")
        sys.exit(1)
    
    print(f"Converting {md_file} to HTML...")
    html_file = convert_markdown_file(md_file)
    print(f"✅ Created: {html_file}")
