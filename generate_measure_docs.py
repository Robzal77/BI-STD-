import os
import re
import datetime

def generate_docs(start_dir):
    print(f"Scanning {start_dir} for measures...\n")
    
    measures_data = [] # List of dicts: {model, table, name, dax, description}
    
    for root, dirs, files in os.walk(start_dir):
        # We look for 'tables' directories which contain the table definitions
        if os.path.basename(root).lower() == 'tables':
            # The parent of 'tables' is usually 'definition', and parent of that is the SemanticModel folder
            # typically: Project/Name.SemanticModel/definition/tables
            # So Model Name can be derived from the path
            
            # Go up two levels to find .SemanticModel folder name
            definition_dir = os.path.dirname(root)
            model_dir = os.path.dirname(definition_dir)
            model_name = os.path.basename(model_dir).replace('.SemanticModel', '')
            
            for t_file in files:
                if t_file.endswith('.tmdl'):
                    t_path = os.path.join(root, t_file)
                    table_name = t_file.replace('.tmdl', '')
                    
                    try:
                        with open(t_path, 'r', encoding='utf-8') as f:
                            lines = f.readlines()
                        
                        current_measure = {}
                        in_expression_block = False
                        
                        for i, line in enumerate(lines):
                            stripped = line.strip()
                            if not stripped: continue
                            
                            # Check for measure definition
                            # measure 'Name' = ... or measure Name = ...
                            measure_match = re.search(r'^\s*measure\s+[\'"]?([^\'"=]+)[\'"]?\s*=\s*(.*)', line)
                            
                            if measure_match:
                                # Save previous measure if exists
                                if current_measure:
                                    measures_data.append(current_measure)
                                    current_measure = {}
                                
                                name = measure_match.group(1).strip()
                                rest_of_line = measure_match.group(2).strip()
                                
                                current_measure = {
                                    'model': model_name,
                                    'table': table_name,
                                    'name': name,
                                    'dax': '',
                                    'description': 'No description provided'
                                }
                                
                                # Check for multi-line expression start ```
                                if rest_of_line.startswith('```'):
                                    in_expression_block = True
                                    # If there is content after ```, include it (rare but possible)
                                    content_after = rest_of_line.replace('```', '', 1).strip()
                                    if content_after:
                                        current_measure['dax'] += content_after + '\n'
                                else:
                                    current_measure['dax'] = rest_of_line
                                continue
                                
                            # If inside expression block
                            if in_expression_block and current_measure:
                                if '```' in line:
                                    in_expression_block = False
                                    # check content before close
                                    content_before = line.split('```')[0].strip()
                                    if content_before:
                                        current_measure['dax'] += content_before
                                else:
                                    current_measure['dax'] += line.strip() + ' ' # Collapse to single line for table readability? Or keep newlines? 
                                    # For table, maybe replace \n with <br> or keep raw? 
                                    # Let's keep it raw but sanitize for markdown table later.
                                continue

                            # Properties (Description)
                            if current_measure and not in_expression_block:
                                # Check if new object started (e.g. column)
                                first_word = stripped.split()[0]
                                if first_word in ['column', 'partition', 'hierarchy', 'measure']:
                                    if first_word != 'measure': # if it IS measure, regex above catches it
                                        measures_data.append(current_measure)
                                        current_measure = {}
                                        continue
                                    else:
                                        # It IS a measure, so we are about to start a new one (regex will catch in next loop? No, this loop iterates lines)
                                        # We are scanning line by line. Regex check is at top of loop.
                                        # So if we are here, regex DID NOT MATCH this line implies it's not a measure start line?
                                        # Wait, regex only checks if it STARTS with measure.
                                        # If regex matched, we essentially skipped the rest of the loop for that line.
                                        pass

                                if stripped.startswith('description:'):
                                    # Handle description
                                    # format: description: "The description text"
                                    # or description: The description text
                                    desc_part = line.split('description:', 1)[1].strip()
                                    # remove quotes if present
                                    if desc_part.startswith('"') and desc_part.endswith('"'):
                                        desc_part = desc_part[1:-1]
                                    current_measure['description'] = desc_part

                        # End of file, save last measure
                        if current_measure:
                            measures_data.append(current_measure)

                    except Exception as e:
                        print(f"Error parsing {t_path}: {e}")

    # Generate Markdown
    md_content = f"# Power BI Measures Documentation\n\n"
    md_content += f"**Last Refreshed Date:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    
    if not measures_data:
        md_content += "No measures found."
    else:
        # Table Header
        md_content += "| Model | Table | Measure Name | DAX Formula | Description |\n"
        md_content += "| --- | --- | --- | --- | --- |\n"
        
        for m in measures_data:
            # Sanitize DAX for markdown table
            # Replace newlines with <br>, escape pipes
            dax_clean = m['dax'].replace('\n', '<br>').replace('|', '\|')
            # Extract just first few chars if too long? No, user asked for formula.
            # Maybe wrap in code ticks?
            dax_display = f"`{dax_clean}`"
            
            desc_clean = m['description'].replace('|', '\|')
            
            md_content += f"| {m['model']} | {m['table']} | {m['name']} | {dax_display} | {desc_clean} |\n"

    output_file = os.path.join(start_dir, "BI-STD", "MEASURES_README.md")
    # Ensure BI-STD exists, though it should
    if not os.path.exists(os.path.dirname(output_file)):
         os.makedirs(os.path.dirname(output_file))
         
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(md_content)
        print(f"Documentation generated at: {output_file}")
    except Exception as e:
        print(f"Error writing output file: {e}")

if __name__ == "__main__":
    generate_docs(".")
