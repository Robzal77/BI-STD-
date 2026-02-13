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

def generate_report_documentation(semantic_model_dir, report_dir):
    """Generate documentation for a single report
    
    This is a wrapper function that calls generate_technical_design_document
    and returns the path to the generated documentation file.
    
    Args:
        semantic_model_dir: Path to the semantic model directory or definition subdirectory
        report_dir: Path to the report directory (optional)
    
    Returns:
        Tuple of (markdown_path, html_path) or (None, None) if generation fails
    """
    try:
        # Determine the correct semantic model directory and extract report name
        current_dir = os.path.abspath(semantic_model_dir)
        
        # If we're in a definition folder, go up one level
        if os.path.basename(current_dir) == 'definition':
            current_dir = os.path.dirname(current_dir)
        
        # Now extract the report name from the .SemanticModel folder
        semantic_model_name = os.path.basename(current_dir)
        if semantic_model_name.endswith('.SemanticModel'):
            report_name = semantic_model_name.replace('.SemanticModel', '')
        else:
            report_name = semantic_model_name
        
        # Ensure we have the correct semantic model directory
        semantic_model_dir = current_dir
        
        # Generate the Technical Design Document
        content = generate_technical_design_document(semantic_model_dir, report_name)
        
        # Write the documentation file in parent directory (same as .pbip)
        parent_dir = os.path.dirname(semantic_model_dir)
        md_path = os.path.join(parent_dir, f'{report_name}_DOCUMENTATION.md')
        
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Generate HTML version
        html_path = None
        try:
            import importlib.util
            html_converter_path = os.path.join(os.path.dirname(__file__), 'markdown_to_html.py')
            spec = importlib.util.spec_from_file_location("html_converter", html_converter_path)
            html_converter = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(html_converter)
            
            html_path = html_converter.convert_markdown_file(md_path)
        except Exception as e:
            # HTML conversion is optional, don't fail if it doesn't work
            pass
        
        return md_path, html_path
    except Exception as e:
        raise Exception(f"Failed to generate report documentation: {str(e)}")

def generate_measure_description(measure_name, dax_formula=''):
    """Generate intelligent description for measures based on name and DAX"""
    name = measure_name.lower().strip()
    
    # Common patterns for measure descriptions
    if 'count' in name or name.startswith('#'):
        if 'active' in name:
            return "Count of active records or items"
        elif 'complete' in name:
            return "Count of completed items or records"
        elif 'incomplete' in name:
            return "Count of incomplete items or records"
        else:
            return "Count of records or items"
    
    elif 'total' in name or 'sum' in name:
        if 'response' in name:
            return "Total number of responses received"
        elif 'distribution' in name:
            return "Total number of distributions sent"
        elif 'dl' in name or 'distribution list' in name:
            return "Total distribution list size"
        else:
            return "Sum or total of values"
    
    elif 'rate' in name or '%' in name:
        if 'response' in name:
            return "Percentage of responses received vs distributed"
        elif 'complete' in name:
            return "Percentage of completed items"
        else:
            return "Calculated percentage or rate"
    
    elif 'last refresh' in name or 'refresh' in name:
        return "Timestamp of last data refresh"
    
    elif 'status' in name:
        return "Current status information or indicator"
    
    elif 'header' in name or 'summary' in name:
        return "Display header or summary text for reports"
    
    elif 'nps' in name:
        return "Net Promoter Score calculation"
    
    elif 'avg' in name or 'average' in name:
        return "Average or mean value calculation"
    
    elif 'max' in name or 'maximum' in name:
        return "Maximum value in the dataset"
    
    elif 'min' in name or 'minimum' in name:
        return "Minimum value in the dataset"
    
    # Check DAX for additional context
    if dax_formula:
        dax_lower = dax_formula.lower()
        if 'utcn' in dax_lower:
            return "Current UTC timestamp"
        elif 'select' in dax_lower and 'value' in dax_lower:
            return "Selected value from context"
        elif 'divide' in dax_lower:
            return "Division calculation result"
        elif 'counta' in dax_lower:
            return "Count of non-blank values"
        elif 'sum' in dax_lower:
            return "Sum of values"
    
    # Default descriptions based on common naming patterns
    if name.startswith('01_') or name.startswith('02_'):
        return "Ordered display element or calculation"
    
    if '_' in name and len(name.split('_')) > 1:
        parts = name.split('_')
        if len(parts) >= 2:
            return f"Calculation related to {parts[0]} and {parts[1]}"
    
    # Generic fallback
    return "Calculated measure for reporting and analysis"

def generate_table_description(table_name, columns_count=0, measures_count=0):
    """Generate intelligent description for tables based on name and structure"""
    name = table_name.lower().strip() if table_name else ''
    
    # Common table naming patterns
    if 'date' in name or 'time' in name or 'calendar' in name:
        return "Date dimension table for time-based analysis"
    
    elif 'localdatetable' in name:
        return "Auto-generated date table for time intelligence"
    
    elif 'dim' in name or 'dimension' in name:
        return "Dimension table containing reference data"
    
    elif 'fact' in name or 'fct' in name:
        return "Fact table containing transactional or measurement data"
    
    elif 'lookup' in name or 'vlookup' in name:
        return "Lookup table for data validation and reference"
    
    elif 'mapping' in name:
        return "Mapping table for data transformation and relationships"
    
    elif 'distribution' in name:
        return "Distribution list and contact information"
    
    elif 'response' in name:
        return "Survey or feedback response data"
    
    elif 'contact' in name or 'vendor' in name:
        return "Contact and vendor information"
    
    elif 'kria' in name:
        return "Kria-specific business data"
    
    elif 'nps' in name:
        return "Net Promoter Score survey data"
    
    elif 'h1' in name or 'h2' in name:
        return "H1/H2 category data and classifications"
    
    elif 'email' in name or 'mail' in name:
        return "Email communication and tracking data"
    
    elif 'zone' in name or 'region' in name:
        return "Geographic zone and region information"
    
    elif 'category' in name:
        return "Category classification and grouping data"
    
    elif 'historical' in name:
        return "Historical data archive"
    
    elif 'combined' in name:
        return "Combined or aggregated data from multiple sources"
    
    elif '2024' in name or '2025' in name or any(char.isdigit() for char in name[-4:]):
        return "Time-specific data for the mentioned period"
    
    # Based on structure
    if measures_count > 0 and columns_count < 10:
        return "Calculated table with measures and KPIs"
    
    elif columns_count > 50:
        return "Large reference table with extensive attributes"
    
    elif 'survey' in name or 'export' in name:
        return "External survey or data export results"
    
    # Generic fallbacks
    if name:
        return f"Business data table containing {name.replace('_', ' ')} information"
    
    return "Data table for business intelligence and reporting"

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
            
        # Split content by relationship declarations
        rel_sections = re.split(r'(?=relationship\s+[^\n]+\n)', content.strip())
        
        for section in rel_sections:
            if not section.strip() or not section.startswith('relationship'):
                continue
                
            from_table = None
            from_col = None
            to_table = None
            to_col = None
            
            # Parse fromColumn - handle both quoted "Table"."Column" and unquoted Table.Column formats
            from_match = re.search(r'fromColumn:\s*([^.\s]+)\.([^\s]+)', section)
            if from_match:
                from_table = from_match.group(1).strip()
                from_col = from_match.group(2).strip()
            
            # Parse toColumn
            to_match = re.search(r'toColumn:\s*([^.\s]+)\.([^\s]+)', section)
            if to_match:
                to_table = to_match.group(1).strip()
                to_col = to_match.group(2).strip()
            
            if from_table and to_table:
                relationships.append({
                    'from_table': from_table,
                    'from_col': from_col,
                    'to_table': to_table,
                    'to_col': to_col
                })
    
    return relationships

def parse_data_sources(semantic_model_dir):
    """Parse data sources from model.tmdl and expressions.tmdl"""
    data_sources = []
    
    # Check model.tmdl
    model_path = None
    if os.path.basename(semantic_model_dir) == 'definition':
        model_path = os.path.join(semantic_model_dir, 'model.tmdl')
    else:
        model_path = os.path.join(semantic_model_dir, 'definition', 'model.tmdl')
    
    if os.path.exists(model_path):
        with open(model_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find dataSource blocks
        ds_blocks = re.findall(r'dataSource\s+[^\n]*\n((?:\s+[^\n]+\n)*)', content, re.MULTILINE)
        
        for block in ds_blocks:
            ds_info = {}
            
            # Extract name
            name_match = re.search(r'dataSource\s+["\']([^"\']+)["\']', block)
            if name_match:
                ds_info['name'] = name_match.group(1)
            
            # Extract type (sqlServer, etc.)
            type_match = re.search(r'=\s*(\w+)\s*\{', block)
            if type_match:
                ds_info['type'] = type_match.group(1)
            
            # Extract connection details
            if 'sqlServer' in block:
                server_match = re.search(r'server:\s*["\']([^"\']+)["\']', block)
                database_match = re.search(r'database:\s*["\']([^"\']+)["\']', block)
                if server_match:
                    ds_info['server'] = server_match.group(1)
                if database_match:
                    ds_info['database'] = database_match.group(1)
                ds_info['connection_type'] = 'SQL Server'
            elif 'folder' in block:
                path_match = re.search(r'path:\s*["\']([^"\']+)["\']', block)
                if path_match:
                    ds_info['path'] = path_match.group(1)
                ds_info['connection_type'] = 'Folder'
            
            data_sources.append(ds_info)
    
    # Check expressions.tmdl for additional data sources
    expressions_path = None
    if os.path.basename(semantic_model_dir) == 'definition':
        expressions_path = os.path.join(semantic_model_dir, 'expressions.tmdl')
    else:
        expressions_path = os.path.join(semantic_model_dir, 'definition', 'expressions.tmdl')
    
    if os.path.exists(expressions_path):
        with open(expressions_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Look for common data source patterns
        if 'AzureStorage.Blobs' in content:
            data_sources.append({
                'name': 'Azure Storage',
                'type': 'Azure Blob Storage',
                'connection_type': 'Cloud Storage'
            })
        if 'Sql.Database' in content or 'sqlServer' in content:
            data_sources.append({
                'name': 'SQL Server',
                'type': 'SQL Database',
                'connection_type': 'Database'
            })
        if 'SharePoint' in content:
            data_sources.append({
                'name': 'SharePoint',
                'type': 'SharePoint List',
                'connection_type': 'Collaboration'
            })
    
    return data_sources

def parse_model_partitions(semantic_model_dir):
    """Parse partition modes to determine architecture"""
    tables_dir = None
    
    if os.path.basename(semantic_model_dir) == 'definition':
        tables_dir = os.path.join(semantic_model_dir, 'tables')
    else:
        tables_dir = os.path.join(semantic_model_dir, 'definition', 'tables')
    
    modes = set()
    
    if os.path.exists(tables_dir):
        for table_file in os.listdir(tables_dir):
            if table_file.endswith('.tmdl'):
                table_path = os.path.join(tables_dir, table_file)
                try:
                    with open(table_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Check for partition mode
                    mode_match = re.search(r'mode:\s*(\w+)', content)
                    if mode_match:
                        modes.add(mode_match.group(1).lower())
                except Exception:
                    continue  # Skip files that can't be read
    
    if 'directquery' in modes and 'import' in modes:
        return 'Composite'
    elif 'directquery' in modes:
        return 'DirectQuery'
    else:
        return 'Import'

def parse_rls_roles(semantic_model_dir):
    """Parse Row Level Security roles from model.tmdl"""
    model_path = None
    
    if os.path.basename(semantic_model_dir) == 'definition':
        model_path = os.path.join(semantic_model_dir, 'model.tmdl')
    else:
        model_path = os.path.join(semantic_model_dir, 'definition', 'model.tmdl')
    
    roles = []
    
    if os.path.exists(model_path):
        with open(model_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find role blocks
        role_blocks = re.findall(r'role\s+[^\n]*\n((?:\s+[^\n]+\n)*)', content, re.MULTILINE)
        
        for block in role_blocks:
            role_info = {}
            
            # Extract role name
            name_match = re.search(r'role\s+["\']([^"\']+)["\']', block)
            if name_match:
                role_info['name'] = name_match.group(1)
            else:
                role_info['name'] = 'Unnamed Role'
            
            # Extract table permissions
            table_perms = re.findall(r'tablePermission\s+[^\n]*\n((?:\s+[^\n]+\n)*)', block, re.MULTILINE)
            permissions = []
            for perm in table_perms:
                table_match = re.search(r'tablePermission\s+["\']([^"\']+)["\']', perm)
                filter_match = re.search(r'filterExpression:\s*["\']([^"\']*)["\']', perm)
                if table_match:
                    perm_info = {'table': table_match.group(1)}
                    if filter_match:
                        perm_info['filter'] = filter_match.group(1)
                    permissions.append(perm_info)
            
            role_info['permissions'] = permissions
            roles.append(role_info)
    
    return roles

def parse_calculation_groups(semantic_model_dir):
    """Parse calculation groups from tables"""
    tables_dir = None
    
    if os.path.basename(semantic_model_dir) == 'definition':
        tables_dir = os.path.join(semantic_model_dir, 'tables')
    else:
        tables_dir = os.path.join(semantic_model_dir, 'definition', 'tables')
    
    calc_groups = []
    
    if os.path.exists(tables_dir):
        for table_file in os.listdir(tables_dir):
            if table_file.endswith('.tmdl'):
                table_path = os.path.join(tables_dir, table_file)
                try:
                    with open(table_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    if 'calculationGroup' in content:
                        # This is a calculation group
                        group_info = {'name': table_file.replace('.tmdl', ''), 'items': []}
                        
                        # Parse calculation items
                        item_blocks = re.findall(r'calculationItem\s+[^\n]*\n((?:\s+[^\n]+\n)*)', content, re.MULTILINE)
                        for block in item_blocks:
                            item_info = {}
                            
                            # Name
                            name_match = re.search(r'calculationItem\s+["\']([^"\']+)["\']', block)
                            if name_match:
                                item_info['name'] = name_match.group(1)
                            
                            # Expression
                            expr_match = re.search(r'expression:\s*["\']([^"\']*)["\']', block)
                            if expr_match:
                                item_info['expression'] = expr_match.group(1)
                            
                            # Format string
                            format_match = re.search(r'formatString:\s*["\']([^"\']*)["\']', block)
                            if format_match:
                                item_info['format'] = format_match.group(1)
                            
                            group_info['items'].append(item_info)
                        
                        calc_groups.append(group_info)
                except Exception:
                    continue
    
    return calc_groups

def parse_parameters(semantic_model_dir):
    """Parse Power Query parameters (if any)"""
    # Parameters might be in model.tmdl or separate files
    # For now, return empty as they might not be in TMDL
    return []

def infer_business_purpose(tables):
    """Infer business purpose from table names"""
    table_names = [t['name'].lower() for t in tables if t['name']]
    
    if any('sales' in name or 'order' in name for name in table_names):
        return "Sales Performance and Order Management"
    elif any('supply' in name or 'chain' in name or 'inventory' in name for name in table_names):
        return "Supply Chain and Inventory Management"
    elif any('finance' in name or 'budget' in name for name in table_names):
        return "Financial Reporting and Budgeting"
    elif any('hr' in name or 'employee' in name for name in table_names):
        return "Human Resources Analytics"
    else:
        return "Business Intelligence Dashboard"

def infer_business_purpose_adaptive(fact_tables, dim_tables, report_name):
    """Context-aware business purpose inference that works for any report type"""
    report_lower = report_name.lower()

    # SCFD-specific detection
    if 'scfd' in report_lower:
        return "is a Supply Chain Financial Dashboard providing comprehensive financial performance insights across procurement, operations, and supply chain activities, including budget vs actual analysis, forecast accuracy, and key financial metrics tracking."

    # Flash report detection
    if 'flash' in report_lower:
        return "is a flash reporting dashboard providing rapid insights into key business metrics and performance indicators across multiple dimensions including geography, time periods, and business segments."

    # NPS/Survey detection
    if 'nps' in report_lower or 'survey' in report_lower or 'kria' in report_lower:
        return "is a Net Promoter Score (NPS) analytics dashboard providing customer satisfaction insights, survey response analysis, and feedback metrics across different business segments and time periods."

    # Generic business purpose based on table analysis
    fact_names = [t.get('name', '').lower() for t in fact_tables]
    dim_names = [t.get('name', '').lower() for t in dim_tables]

    # Financial analysis
    if any(term in ' '.join(fact_names + dim_names) for term in ['value', 'amount', 'budget', 'forecast', 'financial']):
        return "is a financial performance dashboard providing insights into business financial metrics, budget analysis, and forecasting across key performance indicators."

    # Sales analysis
    if any(term in ' '.join(fact_names + dim_names) for term in ['sales', 'order', 'customer', 'revenue']):
        return "is a sales performance dashboard analyzing customer behavior, order patterns, and revenue metrics across different business dimensions."

    # Operational analysis
    if any(term in ' '.join(fact_names + dim_names) for term in ['operation', 'process', 'efficiency', 'performance']):
        return "is an operational performance dashboard monitoring business processes, efficiency metrics, and operational KPIs across the organization."

    # Default fallback
    return "is a business intelligence dashboard providing analytical insights and performance metrics across key business dimensions."

def categorize_measures_strict(measures):
    """Simple test: just return all measures in core_financials"""
    core_financials = measures  # Just take all
    time_intelligence = []
    ratios_variances = []
    return core_financials, time_intelligence, ratios_variances

def explain_measure_logic(measure):
    """Generate specific DAX logic explanation instead of generic phrases"""
    if not isinstance(measure, dict):
        return "Direct column reference"
        
    name = measure.get('name', '')
    dax = measure.get('expression', '') or measure.get('dax', '')

    if not dax:
        return "Direct column reference"

    dax_lower = dax.lower()

    # Time Intelligence patterns
    if 'totalytd' in dax_lower:
        date_match = re.search(r'totalytd\(\s*sum\([^)]+\),\s*([^)]+)\)', dax, re.IGNORECASE)
        if date_match:
            date_col = date_match.group(1)
            return f"Year-to-date calculation of values up to current date from {date_col}"

    if 'datesytd' in dax_lower:
        return "Year-to-date aggregation using standard date intelligence"

    # Filter-based calculations
    filter_match = re.search(r'calculate\(\s*sum\([^)]+\),\s*filter\([^,]+,\s*([^)]+)\)', dax, re.IGNORECASE)
    if filter_match:
        condition = filter_match.group(1)
        return f"Sum aggregation filtered by {condition}"

    # Division patterns (ratios)
    if 'divide' in dax_lower:
        divide_match = re.search(r'divide\(\s*([^,]+),\s*([^,)]+)', dax, re.IGNORECASE)
        if divide_match:
            numerator = divide_match.group(1).strip()
            denominator = divide_match.group(2).strip()
            return f"Ratio calculation: {numerator} divided by {denominator}"

    # Simple aggregations
    if dax_lower.startswith('sum('):
        sum_match = re.search(r'sum\(\s*(\w+)\[(\w+)\]', dax, re.IGNORECASE)
        if sum_match:
            table = sum_match.group(1)
            column = sum_match.group(2)
            return f"Sum of {column} from {table}"

    # Scale factor patterns
    if '/' in dax and 'scale' in dax_lower:
        return "Sum aggregation divided by scale factor"

    # Version filtering
    if 'versionlist' in dax_lower:
        version_match = re.search(r'filter\([^,]+versionlist[^=]*=\s*["\']([^"\']+)["\']', dax, re.IGNORECASE)
        if version_match:
            version = version_match.group(1)
            return f"Filtered calculation for version '{version}'"

    # Default fallback
    if 'calculate' in dax_lower:
        return "Calculated aggregation with filters"
    elif 'sum' in dax_lower:
        return "Sum aggregation"
    else:
        return "Direct column reference"

def is_complex_measure(dax):
    """Determine if a measure's DAX is complex enough to warrant showing the snippet"""
    if not dax:
        return False

    dax_lower = dax.lower()

    # Complex patterns that warrant showing DAX
    complex_indicators = [
        'calculate(',
        'filter(',
        'totalytd(',
        'datesytd(',
        'divide(',
        'if(',
        'switch(',
        'var ',
        'return',
        '&&',
        '||',
        'all(',
        'allexcept(',
        'values('
    ]

    return any(indicator in dax_lower for indicator in complex_indicators)

def parse_tmdl_table(file_path):
    """Parse a TMDL table file and extract columns, measures, partitions, etc."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        lines = content.split('\n')
    
    table_info = {
        'columns': [],
        'measures': [],
        'name': None,
        'description': None,
        'storage_mode': 'Import',  # Default
        'partitions': [],
        'is_calculation_group': False
    }
    
    # Extract table name
    table_match = re.search(r'^table\s+(?:[\'"]([^\'"]+)[\'"]|(\S+))', content, re.MULTILINE)
    if table_match:
        table_info['name'] = table_match.group(1) if table_match.group(1) else table_match.group(2)
        table_info['name'] = table_info['name'].strip()
    
    # Check if calculation group
    if 'calculationGroup' in content:
        table_info['is_calculation_group'] = True
    
    # Extract description
    desc_match = re.search(r'description:\s*["\']([^"\']*)["\']', content)
    if desc_match:
        table_info['description'] = desc_match.group(1)
    
    # Extract partitions and storage mode
    partition_blocks = re.findall(r'partition\s+[^\n]*\n((?:\s+[^\n]+\n)*)', content, re.MULTILINE)
    for block in partition_blocks:
        partition_info = {}
        
        # Name
        name_match = re.search(r'partition\s+["\']([^"\']+)["\']', block)
        if name_match:
            partition_info['name'] = name_match.group(1)
        else:
            partition_info['name'] = 'Unnamed Partition'
        
        # Mode
        mode_match = re.search(r'mode:\s*(\w+)', block)
        if mode_match:
            partition_info['mode'] = mode_match.group(1)
            table_info['storage_mode'] = mode_match.group(1)  # Assume single mode for simplicity
        
        # Source
        source_match = re.search(r'source:\s*["\']([^"\']*)["\']', block)
        if source_match:
            partition_info['source'] = source_match.group(1)
        
        table_info['partitions'].append(partition_info)
    
    # Parse measures
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Check for measure with /// comment
        if line.strip().startswith('///'):
            description = line.strip()[3:].strip()
            i += 1
            if i < len(lines) and 'measure' in lines[i]:
                measure_match = re.search(r'measure\s+(?:[\'"]([^\'"=`]+)[\'"]|([^=`\s]+))', lines[i])
                if measure_match:
                    measure_name = measure_match.group(1) if measure_match.group(1) else measure_match.group(2)
                    measure_name = measure_name.strip()
                    
                    # Extract DAX from the line after measure name =
                    dax = ''
                    measure_line_idx = i
                    # Find the line with measure name =
                    while measure_line_idx < len(lines) and not lines[measure_line_idx].strip().startswith('measure'):
                        measure_line_idx += 1
                    
                    if measure_line_idx < len(lines):
                        line = lines[measure_line_idx].strip()
                        if '=' in line:
                            # Single line measure
                            dax = line.split('=', 1)[1].strip()
                        else:
                            # Multi-line, look for next lines
                            dax_lines = []
                            for j in range(measure_line_idx + 1, min(measure_line_idx + 10, len(lines))):
                                next_line = lines[j].strip()
                                if next_line.startswith('formatString:') or next_line.startswith('lineageTag:') or next_line.startswith('annotation'):
                                    break
                                if next_line:
                                    dax_lines.append(next_line)
                            dax = ' '.join(dax_lines).strip()
                            # Remove surrounding ```
                            dax = dax.strip('`').strip()
                    
                    table_info['measures'].append({
                        'name': measure_name,
                        'description': description if description else generate_measure_description(measure_name, dax),
                        'dax': dax,
                        'display_folder': None  # Will parse later
                    })
        
        # Check for measure without /// comment
        elif line.strip().startswith('measure'):
            measure_match = re.search(r'measure\s+(?:[\'"]([^\'"=`]+)[\'"]|([^=`\s]+))', line)
            if measure_match:
                measure_name = measure_match.group(1) if measure_match.group(1) else measure_match.group(2)
                measure_name = measure_name.strip()
                
                # Check for description property
                description = None
                dax = ''
                # Extract DAX from the line after measure name =
                measure_line_idx = i
                line = lines[measure_line_idx].strip()
                if '=' in line:
                    # Single line measure
                    dax = line.split('=', 1)[1].strip()
                else:
                    # Multi-line, look for next lines
                    dax_lines = []
                    for j in range(i + 1, min(i + 10, len(lines))):
                        next_line = lines[j].strip()
                        if next_line.startswith('description:') or next_line.startswith('formatString:') or next_line.startswith('lineageTag:'):
                            if next_line.startswith('description:'):
                                desc_match = re.search(r'description\s*:\s*"([^"]*)"', next_line, re.IGNORECASE)
                                if desc_match:
                                    description = desc_match.group(1)
                            continue
                        if next_line and not next_line.startswith('annotation'):
                            dax_lines.append(next_line)
                        elif not next_line:
                            continue
                        else:
                            break
                    dax = ' '.join(dax_lines).strip()
                    # Remove surrounding ```
                    dax = dax.strip('`').strip()
                
                table_info['measures'].append({
                    'name': measure_name,
                    'description': description if description else generate_measure_description(measure_name, dax),
                    'dax': dax,
                    'display_folder': None
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
    
    # Generate description if none provided
    if not table_info['description']:
        table_info['description'] = generate_table_description(
            table_info['name'], 
            len(table_info['columns']), 
            len(table_info['measures'])
        )
    
    return table_info

def infer_business_purpose(fact_tables, report_name):
    """Infer business purpose from fact table names"""
    if not fact_tables:
        return "is a business intelligence dashboard for data analysis and reporting."

    fact_names = [f.get('name', '').lower() for f in fact_tables]

    if any('scfd' in name for name in fact_names):
        return "is a comprehensive business intelligence solution designed to monitor and analyze supply chain financial performance across global operations. The dashboard provides real-time visibility into logistics efficiency (LE) metrics, supply chain financial data (SCFD), and variance analysis between planned and actual performance."

    if any('nps' in name for name in fact_names):
        return "is a Net Promoter Score analysis dashboard that tracks customer satisfaction and loyalty metrics across different business segments and time periods."

    if any('sales' in name for name in fact_names):
        return "is a sales performance dashboard providing insights into revenue, orders, and customer behavior across different markets and time periods."

    return "is a business intelligence dashboard providing analytical insights and performance metrics for data-driven decision making."

def infer_business_purpose_adaptive(fact_tables, dim_tables, report_name):
    """Infer business purpose from fact and dimension table names - adaptive version"""
    if not fact_tables:
        return "is a business intelligence dashboard for data analysis and reporting."

    fact_names = [f.get('name', '').lower() for f in fact_tables]
    dim_names = [d.get('name', '').lower() for d in dim_tables]
    report_lower = report_name.lower()

    # Check report name first
    if 'scfd' in report_lower or any('scfd' in name for name in fact_names):
        return "is a comprehensive business intelligence solution designed to monitor and analyze supply chain financial performance across global operations. The dashboard provides real-time visibility into logistics efficiency (LE) metrics, supply chain financial data (SCFD), and variance analysis between planned and actual performance."

    if 'nps' in report_lower or any('nps' in name for name in fact_names):
        return "is a Net Promoter Score analysis dashboard that tracks customer satisfaction and loyalty metrics across different business segments and time periods."

    if 'flash' in report_lower or 'report' in report_lower:
        return "is a flash reporting dashboard providing rapid insights into key business metrics and performance indicators across multiple dimensions including geography, time periods, and business segments."

    # Check fact table names for business patterns
    if any('sales' in name for name in fact_names):
        return "is a sales performance dashboard providing insights into revenue, orders, and customer behavior across different markets and time periods."

    if any('finance' in name or 'financial' in name for name in fact_names):
        return "is a financial performance dashboard tracking key financial metrics, budgets, and variances across business operations."

    if any('inventory' in name or 'stock' in name for name in fact_names):
        return "is an inventory management dashboard monitoring stock levels, turnover, and supply chain metrics."

    # Check dimension tables for business context
    if any('customer' in name for name in dim_names):
        return "is a customer-centric analytics dashboard providing insights into customer behavior, segmentation, and performance metrics."

    if any('product' in name or 'item' in name for name in dim_names):
        return "is a product performance dashboard analyzing product sales, profitability, and market performance."

    # Generic fallback based on table structure
    if len(fact_tables) == 1 and len(dim_tables) > 3:
        return "is a dimensional analytics dashboard providing multi-dimensional analysis of business performance across various business dimensions."

    return "is a business intelligence dashboard providing analytical insights and performance metrics for data-driven decision making."

def get_model_version(semantic_model_dir):
    """Extract model version from metadata"""
    model_path = None
    if os.path.basename(semantic_model_dir) == 'definition':
        model_path = os.path.join(semantic_model_dir, 'model.tmdl')
    else:
        model_path = os.path.join(semantic_model_dir, 'definition', 'model.tmdl')

    if os.path.exists(model_path):
        with open(model_path, 'r', encoding='utf-8') as f:
            content = f.read()
            version_match = re.search(r'PBIDesktopVersion = ([^\n]+)', content)
            if version_match:
                return version_match.group(1).strip()

    return "Latest"

def infer_fact_granularity(fact_table):
    """Infer the granularity of a fact table"""
    name = fact_table.get('name', '').lower()
    columns = fact_table.get('columns', [])

    if 'scfd' in name:
        return "One row per SCFD Entity, Sub-Package, Calendar period, and Attribute combination"

    if 'le' in name:
        return "One row per Country, Sub-Package, Version, Calendar period, Reporting Item, and Period Type"

    if 'sales' in name:
        return "One row per transaction or order line item"

    # Generic inference based on columns
    key_columns = [col for col in columns if 'id' in col.get('name', '').lower() or 'key' in col.get('name', '').lower()]
    if len(key_columns) >= 3:
        return f"One row per combination of {len(key_columns)} key dimensions"

    return "One row per business transaction or event"

def get_fact_purpose(table_name):
    """Get the business purpose of a fact table"""
    name = table_name.lower()

    if 'scfd' in name:
        return "Captures financial performance metrics across the supply chain"
    if 'le' in name:
        return "Measures operational efficiency in logistics operations"
    if 'sales' in name:
        return "Records sales transactions and revenue data"
    if 'inventory' in name:
        return "Tracks inventory levels and movements"
    if 'nps' in name:
        return "Stores customer satisfaction survey responses"

    return "Captures transactional business data for analysis"

def extract_business_rules(partition):
    """Extract business rules from partition M code"""
    source = partition.get('source', '')
    rules = []

    if 'where' in source.lower():
        rules.append("Complex filtering logic applied to exclude specific combinations")

    if 'multiply' in source.lower() or '*' in source:
        rules.append("Value scaling applied for unit conversion")

    if 'conditional' in source.lower() or 'if ' in source.lower():
        rules.append("Business logic applied for categorization")

    if rules:
        return " and ".join(rules)

    return ""

def infer_dimension_hierarchy(dim_table):
    """Infer hierarchy from dimension table structure"""
    name = dim_table.get('name', '').lower()
    columns = [col.get('name', '').lower() for col in dim_table.get('columns', [])]

    if 'calendar' in name or 'date' in name:
        return "Year → Month → Date"
    if 'country' in name:
        return "ZONE → COUNTRY → BU"
    if 'package' in name:
        return "PNL_CODE → PACKAGES → SUBPACKAGES"
    if 'time' in name:
        return "Year → Quarter → Month → Date"

    # Look for hierarchical patterns in column names
    hierarchy_cols = []
    for col in ['zone', 'country', 'region', 'bu', 'business', 'category', 'subcategory']:
        if any(col in c for c in columns):
            hierarchy_cols.append(col.title())

    if len(hierarchy_cols) >= 2:
        return " → ".join(hierarchy_cols)

    return "Flat dimension structure"

def get_dimension_purpose(table_name):
    """Get the business purpose of a dimension table"""
    name = table_name.lower()

    if 'calendar' in name:
        return "Time dimension for trend analysis and period-over-period comparisons"
    if 'country' in name:
        return "Geographic organizational structure and regional groupings"
    if 'package' in name:
        return "Product and financial categorization hierarchy"
    if 'entity' in name:
        return "Manufacturing sites and production facilities"
    if 'business' in name:
        return "Business unit classification and organizational structure"
    if 'version' in name:
        return "Budget version control and scenario planning"
    if 'zone' in name:
        return "Geographic zone and regional boundaries"
    if 'period' in name:
        return "Time period definitions and groupings"

    return "Reference data and categorization for business analysis"

def categorize_measures(measures):
    """Categorize measures by business function"""
    categories = {
        "Financial Performance Metrics": [],
        "Time Intelligence Calculations": [],
        "Comparative Analysis": [],
        "Dynamic Reporting Elements": [],
        "Supporting Calculations": []
    }

    for measure in measures:
        name = measure.get('name', '').lower()
        dax = measure.get('dax', '').lower()

        if any(term in name for term in ['value', 'total', 'sum', 'vs', 'dev']):
            categories["Financial Performance Metrics"].append(measure)
        elif any(term in name for term in ['ytd', 'mtd', 'qtd', 'last', 'refresh']):
            categories["Time Intelligence Calculations"].append(measure)
        elif any(term in name for term in ['vs', 'prev', 'diff', 'variance']):
            categories["Comparative Analysis"].append(measure)
        elif any(term in name for term in ['title', 'count']):
            categories["Dynamic Reporting Elements"].append(measure)
        else:
            categories["Supporting Calculations"].append(measure)

    return categories

def extract_measure_dependencies(dax):
    """Extract measure dependencies from DAX formula"""
    dependencies = []
    if not dax:
        return dependencies

    # Find measure references in square brackets
    measure_refs = re.findall(r'\[([^\]]+)\]', dax)
    if measure_refs:
        dependencies.extend([f"[{ref}]" for ref in measure_refs])

    return dependencies

def is_complex_measure(dax):
    """Check if measure is complex enough to show DAX"""
    if not dax:
        return False

    complex_indicators = ['calculate', 'filter', 'all', 'values', 'selectedvalue', 'totalytd', 'dates']
    return any(indicator in dax.lower() for indicator in complex_indicators)

def summarize_transformations(partition):
    """Summarize ETL transformations from M code"""
    source = partition.get('source', '')
    steps = []

    if 'Sql.Database' in source:
        steps.append("Source: Azure SQL Database query execution")
    if 'where' in source.lower():
        steps.append("Filtering: Business rule application and data exclusion")
    if 'multiply' in source or '*' in source:
        steps.append("Transformation: Value scaling and unit conversion")
    if 'Table.AddColumn' in source:
        steps.append("Enhancement: Calculated column addition")
    if 'Table.SelectColumns' in source:
        steps.append("Optimization: Column selection and data reduction")
    if 'Table.TransformColumnTypes' in source:
        steps.append("Type Conversion: Data type standardization")
    if 'AzureStorage.Blobs' in source:
        steps.append("Source: Azure Blob Storage file ingestion")

    return steps if steps else ["Data extraction and basic validation"]

def parse_all_tables(semantic_model_dir):
    """Parse all tables from the semantic model directory"""
    tables_dir = os.path.join(semantic_model_dir, 'definition', 'tables') if os.path.basename(semantic_model_dir) != 'definition' else os.path.join(semantic_model_dir, 'tables')

    all_tables = []

    if os.path.exists(tables_dir):
        for table_file in sorted(os.listdir(tables_dir)):
            if table_file.endswith('.tmdl'):
                table_path = os.path.join(tables_dir, table_file)
                try:
                    table_info = parse_tmdl_table(table_path)
                    table_info['file'] = table_file
                    all_tables.append(table_info)
                except Exception as e:
                    print(f"   ⚠️ Skipping {table_file}: {e}")
                    continue

    return all_tables

def generate_star_schema_diagram(fact_tables, dim_tables, relationships):
    """Generate a fail-proof star schema diagram using multiple formats"""
    diagram_lines = []

    if not fact_tables or not dim_tables:
        return "*No core fact-dimension relationships found.*"

    # Primary: Mermaid graph (simplified)
    diagram_lines.append("```mermaid")
    diagram_lines.append("graph TD")
    diagram_lines.append("    %% Core Star Schema - Simplified View")

    # Add fact tables as central nodes
    for fact in fact_tables:
        fact_name = fact['name']
        diagram_lines.append(f"    {fact_name}[{fact_name}]")

    # Add dimension tables
    for dim in dim_tables:
        dim_name = dim['name']
        diagram_lines.append(f"    {dim_name}[{dim_name}]")

    # Add relationships with simple arrows
    relationship_count = 0
    for rel in relationships:
        from_table = rel.get('from_table', '')
        to_table = rel.get('to_table', '')
        if from_table in [f['name'] for f in fact_tables] and to_table in [d['name'] for d in dim_tables]:
            diagram_lines.append(f"    {from_table} --> {to_table}")
            relationship_count += 1
            if relationship_count >= 10:  # Limit relationships for clarity
                break

    diagram_lines.append("```")
    diagram_lines.append("")
    diagram_lines.append("**Legend:** Facts (central rectangles) connect to Dimensions (supporting tables)")
    diagram_lines.append("")

    # Backup: PlantUML class diagram
    diagram_lines.append("```plantuml")
    diagram_lines.append("@startuml Star Schema")
    diagram_lines.append("!theme plain")

    # Add fact tables
    for fact in fact_tables:
        fact_name = fact['name']
        diagram_lines.append(f"class {fact_name} <<Fact>> #LightBlue")

    # Add dimension tables
    for dim in dim_tables:
        dim_name = dim['name']
        diagram_lines.append(f"class {dim_name} <<Dimension>> #LightGreen")

    # Add relationships
    relationship_count = 0
    for rel in relationships:
        from_table = rel.get('from_table', '')
        to_table = rel.get('to_table', '')
        if from_table in [f['name'] for f in fact_tables] and to_table in [d['name'] for d in dim_tables]:
            diagram_lines.append(f"{from_table} --> {to_table}")
            relationship_count += 1
            if relationship_count >= 10:
                break

    diagram_lines.append("@enduml")
    diagram_lines.append("```")
    diagram_lines.append("")
    diagram_lines.append("*If Mermaid diagram doesn't render, use PlantUML extension to view the alternative diagram above.*")

    return "\n".join(diagram_lines)

def summarize_transformations_detailed(partition):
    """Extract detailed transformation steps from M code"""
    source = partition.get('source', '')
    steps = []

    # Look for specific transformation patterns
    if 'where' in source.lower():
        # Extract filter conditions
        where_match = re.search(r'where\s+([^,\]\}]+)', source, re.IGNORECASE)
        if where_match:
            condition = where_match.group(1).strip()
            steps.append(f"Filters for '{condition}' condition")

    if 'Table.SelectColumns' in source:
        # Extract selected columns
        col_match = re.search(r'Table\.SelectColumns\([^,]+,\s*\{([^}]+)\}', source)
        if col_match:
            columns = col_match.group(1).strip()
            steps.append(f"Selects columns: {columns}")

    if 'Table.RenameColumns' in source or 'Renamed Columns' in source:
        # Extract renamed columns
        rename_match = re.search(r'Table\.RenameColumns\([^,]+,\s*\{\{([^}]+)\}\}', source)
        if rename_match:
            rename_info = rename_match.group(1).strip()
            old_name, new_name = rename_info.split(',')
            steps.append(f"Renames '{old_name.strip()}' to '{new_name.strip()}'")

    if 'Table.AddColumn' in source:
        # Extract added columns
        add_match = re.search(r'Table\.AddColumn\([^,]+,\s*"([^"]+)"', source)
        if add_match:
            col_name = add_match.group(1)
            steps.append(f"Adds calculated column '{col_name}'")

    if 'Table.Merge' in source:
        # Extract merge operations
        merge_match = re.search(r'Table\.Merge\([^,]+,\s*"([^"]+)"', source)
        if merge_match:
            merge_table = merge_match.group(1)
            steps.append(f"Merges with '{merge_table}' table")

    if 'multiply' in source.lower() or '*' in source:
        steps.append("Applies scaling factor to numeric values")

    if 'Table.TransformColumnTypes' in source:
        steps.append("Converts column data types")

    # If no specific transformations found, provide generic ones
    if not steps:
        if 'Sql.Database' in source:
            steps.append("Extracts data from Azure SQL Database")
        if 'AzureStorage.Blobs' in source:
            steps.append("Loads data from Azure Blob Storage")
        if 'Table.SelectRows' in source:
            steps.append("Filters rows based on business criteria")

    return steps[:3]  # Return max 3 steps

def categorize_measures_strict(measures):
    """Categorize measures into the 3 specific categories"""
    categories = {
        "Core Financials": [],
        "Time Intelligence": [],
        "Ratios & Variances": []
    }

    for measure in measures:
        name = measure.get('name', '').lower()
        dax = measure.get('dax', '').lower()

        # Core Financials - values and costs
        if any(term in name for term in ['value', 'cost', 'amount', 'total', 'sum', 'le', 'scfd']):
            categories["Core Financials"].append(measure)
        # Time Intelligence - YTD, MTD, rolling periods
        elif any(term in name for term in ['ytd', 'mtd', 'qtd', 'rolling', '3+9', '6+6', '9+3', '0+12']):
            categories["Time Intelligence"].append(measure)
        # Ratios & Variances - percentages and comparisons
        elif any(term in name for term in ['%', 'ratio', 'vs', 'variance', 'diff', 'adherence', 'accuracy']):
            categories["Ratios & Variances"].append(measure)
        # Default to Core Financials if not categorized
        else:
            categories["Core Financials"].append(measure)

    return categories

def explain_measure_logic(measure):
    """Explain measure logic specifically without generic phrases"""
    name = measure.get('name', '').lower()
    dax = measure.get('dax', '')

    if not dax:
        return "Direct aggregation of source column"

    # Parse DAX for specific patterns
    if 'calculate(' in dax.lower():
        # Extract the base aggregation
        calc_match = re.search(r'calculate\(\s*(\w+)\([^)]+\)', dax, re.IGNORECASE)
        if calc_match:
            agg_func = calc_match.group(1).upper()
            if agg_func == 'SUM':
                base = "Sum of"
            elif agg_func == 'COUNT':
                base = "Count of"
            elif agg_func == 'AVERAGE' or agg_func == 'AVG':
                base = "Average of"
            else:
                base = f"{agg_func} of"

            # Extract table and column
            table_col_match = re.search(r'(\w+)\[(\w+)\]', dax)
            if table_col_match:
                table_name = table_col_match.group(1)
                col_name = table_col_match.group(2)
                logic = f"{base} {col_name} from {table_name}"
            else:
                logic = f"{base} values"
        else:
            logic = "Calculated aggregation with filters"
    else:
        # Simple aggregation
        if 'sum(' in dax.lower():
            table_col_match = re.search(r'sum\(\s*(\w+)\[(\w+)\]', dax, re.IGNORECASE)
            if table_col_match:
                table_name = table_col_match.group(1)
                col_name = table_col_match.group(2)
                logic = f"Sum of {col_name} from {table_name}"
            else:
                logic = "Sum aggregation"
        else:
            logic = "Direct column reference"

    # Add filter context if present
    if 'filter(' in dax.lower() or 'where' in dax.lower():
        filter_match = re.search(r'filter\([^,]+,\s*([^)]+)\)', dax, re.IGNORECASE)
        if filter_match:
            filter_condition = filter_match.group(1).strip()
            logic += f" where {filter_condition}"

    # Add division context
    if '/' in dax:
        parts = dax.split('/')
        if len(parts) == 2:
            logic += " divided by scale factor"

    return logic

def generate_measure_description(name, dax):
    """Generate a business-friendly description of a measure"""
    name_lower = name.lower()
    dax_lower = dax.lower() if dax else ""

    # Financial measures
    if any(term in name_lower for term in ['value', 'total', 'sum', 'amount']):
        if 'ytd' in name_lower:
            return "Calculates the year-to-date total value"
        elif 'mtd' in name_lower:
            return "Calculates the month-to-date total value"
        elif 'qtd' in name_lower:
            return "Calculates the quarter-to-date total value"
        else:
            return "Calculates the total aggregated value"

    # Variance measures
    if any(term in name_lower for term in ['vs', 'variance', 'diff', 'dev']):
        if 'prev' in name_lower or 'last' in name_lower:
            return "Calculates the variance compared to the previous period"
        else:
            return "Calculates the difference or variance between values"

    # Percentage measures
    if any(term in name_lower for term in ['pct', 'percent', '%']):
        return "Calculates the percentage or ratio"

    # Count measures
    if 'count' in name_lower:
        return "Counts the number of records or items"

    # Time intelligence
    if any(term in name_lower for term in ['last', 'refresh', 'current']):
        return "Provides the most recent or current value"

    # Generic fallback
    return "Calculates a business metric for analysis"

def generate_technical_design_document(semantic_model_dir, report_name):
    """Generate Production-Grade Technical Design Document (TDD)"""
    timestamp = datetime.now().strftime("%B %d, %Y")
    developer = get_developer_name()

    # Parse all data
    relationships = parse_relationships(semantic_model_dir)
    data_sources = parse_data_sources(semantic_model_dir)
    architecture = parse_model_partitions(semantic_model_dir)
    all_tables = parse_all_tables(semantic_model_dir)

    # PHASE 1: Adaptive Filtering - Handle different project architectures
    # Filter out system tables
    filtered_tables = [t for t in all_tables if not any(sys_table in t.get('name', '').lower()
                        for sys_table in ['localdatetable', 'datetabletemplate', 'paste'])]

    # Ignore utility tables
    utility_tables = ['last_refresh', 'reportinfo', 'scale table', 'dashboard feedback']
    filtered_tables = [t for t in filtered_tables if not any(util.lower() in t.get('name', '').lower() for util in utility_tables)]
    filtered_tables = [t for t in filtered_tables if not t.get('name', '').startswith('Query')]

    # Adaptive table identification - handle different naming conventions
    fact_tables = []
    dim_tables = []
    measures_table = None

    # First, identify measures table if it exists
    for table in filtered_tables:
        if table.get('name') == '#Measures' or table.get('name') == '#Calculations':
            measures_table = table
            break

    # Identify fact tables - multiple strategies
    for table in filtered_tables:
        table_name = table.get('name', '').lower()

        # Strategy 1: Standard naming (#FCT_ prefix)
        if '#fct' in table_name:
            fact_tables.append(table)
        # Strategy 2: Tables with measures (likely facts)
        elif table.get('measures') and len(table.get('measures', [])) > 0 and table != measures_table:
            fact_tables.append(table)
        # Strategy 3: Tables with transactional column names
        elif any(col.get('name', '').lower() in ['value', 'amount', 'quantity', 'volume', 'sales'] for col in table.get('columns', [])):
            fact_tables.append(table)

    # Identify dimension tables - multiple strategies
    for table in filtered_tables:
        if table in fact_tables or table == measures_table:
            continue

        table_name = table.get('name', '').lower()

        # Strategy 1: Standard naming (d_ prefix)
        if table_name.startswith('d_'):
            dim_tables.append(table)
        # Strategy 2: Bridge tables (common in some architectures)
        elif 'bridge' in table_name or '-bridge' in table_name:
            dim_tables.append(table)
        # Strategy 3: Date/time tables
        elif any(term in table_name for term in ['date', 'time', 'calendar', 'period']):
            dim_tables.append(table)
        # Strategy 4: Reference/lookup tables (fewer columns, referenced in relationships)
        elif len(table.get('columns', [])) < 10 and table_name not in ['#measures', '#calculations']:
            dim_tables.append(table)

    # If no facts found, try to identify the main transactional table
    if not fact_tables:
        # Look for tables with the most columns or measures
        candidate_tables = [t for t in filtered_tables if t != measures_table]
        if candidate_tables:
            # Sort by number of columns + measures (likely the main fact table)
            candidate_tables.sort(key=lambda t: len(t.get('columns', [])) + len(t.get('measures', [])), reverse=True)
            fact_tables = [candidate_tables[0]]  # Take the largest table as main fact

    # Collect all measures from various sources
    all_measures = []

    # From fact tables
    for table in fact_tables:
        for measure in table.get('measures', []):
            measure_name = measure.get('name', '')
            # Ignore measures ending in _S or _Hidden
            if not measure_name.endswith('_S') and not measure_name.endswith('_Hidden'):
                measure['table_name'] = table['name'] or table['file'].replace('.tmdl', '')
                all_measures.append(measure)

    # From measures table
    if measures_table:
        for measure in measures_table.get('measures', []):
            measure_name = measure.get('name', '')
            # Ignore measures ending in _S or _Hidden
            if not measure_name.endswith('_S') and not measure_name.endswith('_Hidden'):
                measure['table_name'] = measures_table['name']
                all_measures.append(measure)

    # Infer business purpose from available tables
    business_purpose = infer_business_purpose_adaptive(fact_tables, dim_tables, report_name)

    # Build TDD content
    doc_lines = []

    # Header
    doc_lines.append(f"# {report_name} - Technical Design Document")
    doc_lines.append("")
    doc_lines.append(f"**Report Name:** {report_name}")
    doc_lines.append(f"**Version:** {get_model_version(semantic_model_dir)}")
    doc_lines.append(f"**Generated:** {timestamp}")
    doc_lines.append(f"**Architect:** {developer}")
    doc_lines.append("")
    doc_lines.append("---")
    doc_lines.append("")

    # Section 1: High-Level Architecture
    doc_lines.append("## 1. 🏗️ High-Level Architecture")
    doc_lines.append("")
    doc_lines.append("### Star Schema Diagram")
    doc_lines.append("")

    # Generate fail-proof diagram
    diagram_content = generate_star_schema_diagram(fact_tables, dim_tables, relationships)
    doc_lines.append(diagram_content)
    doc_lines.append("")

    # Business Purpose
    doc_lines.append("### 🎯 Business Purpose")
    doc_lines.append("")
    doc_lines.append(f"This report {business_purpose}")
    doc_lines.append("")

    # Section 2: Data Flow (ETL Analysis)
    doc_lines.append("## 2. 📊 The Data Flow (ETL Analysis)")
    doc_lines.append("")

    for fact in fact_tables:
        if fact.get('partitions'):
            partition = fact['partitions'][0]
            source = partition.get('source', '')

            doc_lines.append(f"### {fact['name']} Data Pipeline")
            doc_lines.append("")

            # Source identification
            if 'Sql.Database' in source:
                doc_lines.append("**Source:** Azure SQL Database")
            elif 'Databricks' in source:
                doc_lines.append("**Source:** Databricks")
            elif 'AzureStorage.Blobs' in source:
                doc_lines.append("**Source:** Azure Blob Storage")
            else:
                doc_lines.append("**Source:** Not explicitly identified in M code")

            doc_lines.append("")

            # Transformations - extract 3 specific bullet points
            transformations = summarize_transformations_detailed(partition)
            doc_lines.append("**Transformations:**")
            for step in transformations[:3]:  # Limit to 3 key transformations
                doc_lines.append(f"- {step}")
            doc_lines.append("")

    # Section 3: Measure Logic
    doc_lines.append("## 3. 🧠 Measure Logic (The \"Why\", not just \"What\")")
    doc_lines.append("")

    # Categorize measures into the 3 specific groups
    # Filter out any non-dictionary measures
    valid_measures = [m for m in all_measures if isinstance(m, dict) and 'name' in m]
    measure_categories = categorize_measures_strict(valid_measures)
    core_financials = measure_categories["Core Financials"]
    time_intelligence = measure_categories["Time Intelligence"]
    ratios_variances = measure_categories["Ratios & Variances"]

    # A. Core Financials
    if core_financials:
        doc_lines.append("### A. Core Financials (Values & Costs)")
        doc_lines.append("")
        for measure in core_financials[:15]:  # Limit for readability
            doc_lines.append(f"**Name:** `{measure['name']}`")
            logic = explain_measure_logic(measure)
            doc_lines.append(f"**Logic:** {logic}")

            # Include DAX only for complex measures
            if is_complex_measure(measure.get('expression', '')):
                doc_lines.append("**DAX Snippet:**")
                doc_lines.append("```dax")
                doc_lines.append(measure.get('expression', '').strip())
                doc_lines.append("```")

            doc_lines.append("")

    # B. Time Intelligence
    if time_intelligence:
        doc_lines.append("### B. Time Intelligence (YTD, MTD, Rolling)")
        doc_lines.append("")
        for measure in time_intelligence[:15]:
            doc_lines.append(f"**Name:** `{measure['name']}`")
            logic = explain_measure_logic(measure)
            doc_lines.append(f"**Logic:** {logic}")

            if is_complex_measure(measure.get('expression', '')):
                doc_lines.append("**DAX Snippet:**")
                doc_lines.append("```dax")
                doc_lines.append(measure.get('expression', '').strip())
                doc_lines.append("```")

            doc_lines.append("")

            doc_lines.append("")

    # C. Ratios & Variances
    if ratios_variances:
        doc_lines.append("### C. Ratios & Variances (%)")
        doc_lines.append("")
        for measure in ratios_variances[:15]:
            doc_lines.append(f"**Name:** `{measure['name']}`")
            logic = explain_measure_logic(measure)
            doc_lines.append(f"**Logic:** {logic}")

            if is_complex_measure(measure.get('expression', '')):
                doc_lines.append("**DAX Snippet:**")
                doc_lines.append("```dax")
                doc_lines.append(measure.get('expression', '').strip())
                doc_lines.append("```")

            doc_lines.append("")

    # Footer
    doc_lines.append("---")
    doc_lines.append("")
    doc_lines.append(f"*This Technical Design Document focuses on the core star schema and business logic for {report_name}. All utility tables and helper measures have been excluded for clarity.*")

    return "\n".join(doc_lines)
    report_name = "Unknown Report"
    for part in parts:
        if part.endswith('.SemanticModel'):
            report_name = part.replace('.SemanticModel', '')
            break

    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    doc_lines = []

    # Title with Navigation
    doc_lines.append(f"# 📊 {report_name} - Power BI Model Documentation")
    doc_lines.append("")
    doc_lines.append(f"**Generated:** {timestamp} | **Developer:** {get_developer_name()}")
    doc_lines.append("")

    # Navigation Menu
    doc_lines.append("## 📋 Navigation")
    doc_lines.append("")
    doc_lines.append("| Section | Description |")
    doc_lines.append("|---------|-------------|")
    doc_lines.append("| <a href=\"#dashboard\">🏠 Dashboard</a> | Executive summary and key metrics |")
    doc_lines.append("| <a href=\"#data-model\">📈 Data Model</a> | Relationships and schema diagram |")
    doc_lines.append("| <a href=\"#tables\">📋 Tables</a> | Table definitions and columns |")
    doc_lines.append("| <a href=\"#measures\">🧮 Measures</a> | DAX measures and calculations |")
    doc_lines.append("| <a href=\"#data-sources\">🔗 Data Sources</a> | Connection details |")
    doc_lines.append("| <a href=\"#issues\">⚠️ Issues</a> | Potential problems and recommendations |")
    doc_lines.append("")

    # Parse all data
    relationships = parse_relationships(semantic_model_dir)
    data_sources = parse_data_sources(semantic_model_dir)
    architecture = parse_model_partitions(semantic_model_dir)

    # Parse tables
    tables_dir = os.path.join(semantic_model_dir, 'definition', 'tables') if os.path.basename(semantic_model_dir) != 'definition' else os.path.join(semantic_model_dir, 'tables')
    all_tables = []

    if os.path.exists(tables_dir):
        for table_file in sorted(os.listdir(tables_dir)):
            if table_file.endswith('.tmdl'):
                table_path = os.path.join(tables_dir, table_file)
                try:
                    table_info = parse_tmdl_table(table_path)
                    table_info['file'] = table_file
                    all_tables.append(table_info)
                except Exception as e:
                    print(f"   ⚠️ Skipping {table_file}: {e}")
                    continue

    # Calculate metrics for dashboard
    total_tables = len([t for t in all_tables if not t.get('is_calculation_group', False)])
    total_measures = sum(len(t.get('measures', [])) for t in all_tables)
    total_columns = sum(len(t.get('columns', [])) for t in all_tables)
    fact_tables = len([t for t in all_tables if t['name'] and t['name'].startswith('#FCT_')])
    dim_tables = total_tables - fact_tables

    # Dashboard Section
    doc_lines.append('<a id="dashboard"></a>')
    doc_lines.append("## 🏠 Dashboard")
    doc_lines.append("")
    doc_lines.append("### 📊 Model Overview")
    doc_lines.append("")
    doc_lines.append("| Metric | Count | Details |")
    doc_lines.append("|--------|-------|---------|")
    doc_lines.append(f"| **Total Tables** | {total_tables} | {fact_tables} Facts + {dim_tables} Dimensions |")
    doc_lines.append(f"| **Total Measures** | {total_measures} | DAX calculations |")
    doc_lines.append(f"| **Total Columns** | {total_columns} | Data fields |")
    doc_lines.append(f"| **Relationships** | {len(relationships)} | Active joins |")
    doc_lines.append(f"| **Data Sources** | {len(data_sources)} | External connections |")
    doc_lines.append("")

    # Architecture Summary
    doc_lines.append("### 🏗️ Architecture")
    doc_lines.append("")
    doc_lines.append(f"**Model Type:** {architecture}")
    doc_lines.append(f"**Business Purpose:** {infer_business_purpose(all_tables)}")
    doc_lines.append("")

    # Quick Stats Cards
    doc_lines.append("### 📈 Quick Stats")
    doc_lines.append("")
    doc_lines.append("| Category | Status | Notes |")
    doc_lines.append("|----------|--------|-------|")
    doc_lines.append("| **Auto Date/Time** | ⚠️ Check Required | May need manual verification |")
    doc_lines.append("| **Unused Measures** | 🔍 Analysis Needed | Requires report analysis |")
    doc_lines.append("| **Unused Columns** | 🔍 Analysis Needed | Requires report analysis |")
    doc_lines.append("| **Model Size** | 📊 Calculated | Based on parsed metadata |")
    doc_lines.append("")

    # Data Model Section
    doc_lines.append('<a id="data-model"></a>')
    doc_lines.append("## 📈 Data Model")
    doc_lines.append("")
    doc_lines.append("### Relationships Diagram")
    doc_lines.append("")

    if relationships:
        doc_lines.append("```mermaid")
        doc_lines.append("erDiagram")
        for rel in relationships:
            from_table = rel['from_table']
            from_col = rel['from_col']
            to_table = rel['to_table']
            to_col = rel['to_col']
            doc_lines.append(f'    "{from_table}" ||--o{{ "{to_table}" : "{from_col} -> {to_col}"')
        doc_lines.append("```")
    else:
        doc_lines.append("*No relationships found or unable to parse.*")
    doc_lines.append("")

    # Tables Section
    doc_lines.append('<a id="tables"></a>')
    doc_lines.append("## 📋 Tables")
    doc_lines.append("")
    doc_lines.append(f"### Overview ({total_tables} tables)")
    doc_lines.append("")

    # Table summary table
    doc_lines.append("| Table Name | Type | Columns | Measures | Description |")
    doc_lines.append("|------------|------|---------|----------|-------------|")

    for table in all_tables:
        if table.get('is_calculation_group', False):
            continue

        table_name = table['name'] or table['file'].replace('.tmdl', '')
        table_type = "Fact" if table_name.startswith('#FCT_') else "Dimension"
        col_count = len(table.get('columns', []))
        measure_count = len(table.get('measures', []))
        desc = table.get('description', 'No description')[:50] + "..." if table.get('description') and len(table.get('description', '')) > 50 else table.get('description', 'No description')

        doc_lines.append(f"| [{table_name}](#{table_name.lower().replace(' ', '-')}) | {table_type} | {col_count} | {measure_count} | {desc} |")

    doc_lines.append("")

    # Detailed table definitions
    for table in all_tables:
        if table.get('is_calculation_group', False):
            continue

        table_name = table['name'] or table['file'].replace('.tmdl', '')
        doc_lines.append(f"### {table_name}")
        doc_lines.append("")

        # Table metadata
        table_type = "Fact" if table_name.startswith('#FCT_') else "Dimension"
        doc_lines.append(f"**Type:** {table_type} | **Columns:** {len(table.get('columns', []))} | **Measures:** {len(table.get('measures', []))}")
        doc_lines.append("")

        if table.get('description'):
            doc_lines.append(f"**Description:** {table['description']}")
            doc_lines.append("")

        # Columns
        if table.get('columns'):
            doc_lines.append("#### Columns")
            doc_lines.append("")
            doc_lines.append("| Column Name | Data Type | Description |")
            doc_lines.append("|-------------|-----------|-------------|")

            for col in table['columns']:
                col_name = col.get('name', 'Unknown')
                col_type = col.get('type', 'Unknown')
                col_desc = col.get('description', '')[:50] + "..." if col.get('description') and len(col.get('description', '')) > 50 else col.get('description', '')
                doc_lines.append(f"| {col_name} | {col_type} | {col_desc or '-'} |")

            doc_lines.append("")

        # Measures
        if table.get('measures') and len(table.get('measures', [])) > 0:
            measure_count = len(table.get('measures', []))
            doc_lines.append(f"**Measures:** {measure_count} measures defined (see Measures section for details)")
            doc_lines.append("")

        doc_lines.append("---")
        doc_lines.append("")

    # Measures Section
    doc_lines.append('<a id="measures"></a>')
    doc_lines.append("## 🧮 Measures")
    doc_lines.append("")
    doc_lines.append(f"### Overview ({total_measures} measures)")
    doc_lines.append("")

    # Collect all measures
    all_measures = []
    for table in all_tables:
        for measure in table.get('measures', []):
            measure['table_name'] = table['name'] or table['file'].replace('.tmdl', '')
            all_measures.append(measure)

    if all_measures:
        doc_lines.append("| Measure Name | Table | Description |")
        doc_lines.append("|--------------|-------|-------------|")

        for measure in all_measures:
            name = measure.get('name', 'Unknown')
            table = measure.get('table_name', 'Unknown')
            desc = measure.get('description', '')[:30] + "..." if measure.get('description') and len(measure.get('description', '')) > 30 else measure.get('description', '')

            doc_lines.append(f"| [{name}](#{name.lower().replace(' ', '-').replace('_', '-')}) | {table} | {desc or '-'} |")

        doc_lines.append("")

        # Detailed measures
        doc_lines.append("### Detailed Measures")
        doc_lines.append("")

        for measure in all_measures:
            name = measure.get('name', 'Unknown')
            table = measure.get('table_name', 'Unknown')
            desc = measure.get('description', '')
            dax = measure.get('dax', '')

            doc_lines.append(f"#### {name}")
            doc_lines.append(f"**Table:** {table}")
            if desc:
                doc_lines.append(f"**Description:** {desc}")
            doc_lines.append("")
            if dax:
                doc_lines.append("**DAX Formula:**")
                doc_lines.append("```dax")
                doc_lines.append(dax.strip())
                doc_lines.append("```")
            doc_lines.append("")
    else:
        doc_lines.append("*No measures found.*")
        doc_lines.append("")

    # Data Sources Section
    doc_lines.append('<a id="data-sources"></a>')
    doc_lines.append("## 🔗 Data Sources")
    doc_lines.append("")

    if data_sources:
        doc_lines.append("| Source Name | Type | Connection | Database |")
        doc_lines.append("|-------------|------|------------|----------|")

        for ds in data_sources:
            name = ds.get('name', 'Unknown')
            conn_type = ds.get('connection_type', 'Unknown')
            db_path = ds.get('database', ds.get('path', 'Unknown'))
            ds_type = ds.get('type', 'Unknown')
            doc_lines.append(f"| {name} | {ds_type} | {conn_type} | {db_path} |")

        doc_lines.append("")
    else:
        doc_lines.append("*No data sources found.*")
        doc_lines.append("")

    # Issues and Recommendations
    doc_lines.append('<a id="issues"></a>')
    doc_lines.append("## ⚠️ Issues & Recommendations")
    doc_lines.append("")
    doc_lines.append("### Potential Issues")
    doc_lines.append("")
    issues = []

    # Check for auto date/time
    issues.append("⚠️ **Auto Date/Time:** Verify if auto date/time is disabled for better performance")

    # Check for unused elements (placeholder)
    issues.append("🔍 **Unused Analysis:** Requires Power BI report analysis to identify unused measures/columns")

    # Check model size
    if total_tables > 50:
        issues.append(f"⚠️ **Large Model:** {total_tables} tables may impact performance")

    # Check relationships
    if len(relationships) == 0:
        issues.append("❌ **No Relationships:** Model has no active relationships")

    for issue in issues:
        doc_lines.append(f"- {issue}")

    doc_lines.append("")
    doc_lines.append("---")
    doc_lines.append("")
    doc_lines.append("*Documentation generated automatically. Review and validate all information.*")

    return "\n".join(doc_lines)

def write_documentation_file(content, semantic_model_dir, report_name):
    """Write the documentation content to file and generate HTML version"""

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
        f.write(content)

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
    """Generate documentation for all reports in the project directory (recursively)"""

    print(f"\n📚 Generating Technical Design Documents for: {project_dir}\n")

    generated_count = 0

    # Walk through all subdirectories recursively
    for root, dirs, files in os.walk(project_dir):
        # Skip Archive and Templates folders - they're references only
        dirs[:] = [d for d in dirs if d not in ['Archive', 'Templates']]

        for item in dirs:
            if item.endswith('.SemanticModel'):
                item_path = os.path.join(root, item)
                report_name = item.replace('.SemanticModel', '')
                report_dir = os.path.join(root, f"{report_name}.Report")

                if not os.path.exists(report_dir):
                    report_dir = None

                # Get relative path for display
                rel_path = os.path.relpath(root, project_dir)
                if rel_path == '.':
                    location = 'Root'
                else:
                    location = rel_path

                print(f"📄 [{location}] Generating TDD for: {report_name}")

                try:
                    # Generate Technical Design Document
                    content = generate_technical_design_document(item_path, report_name)

                    # Write TDD file
                    tdd_path = os.path.join(root, f'{report_name}_TDD.md')
                    with open(tdd_path, 'w', encoding='utf-8') as f:
                        f.write(content)

                    print(f"   ✅ Created TDD: {tdd_path}")
                    generated_count += 1

                    # Also generate HTML version
                    try:
                        import importlib.util
                        html_converter_path = os.path.join(os.path.dirname(__file__), 'markdown_to_html.py')
                        spec = importlib.util.spec_from_file_location("html_converter", html_converter_path)
                        html_converter = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(html_converter)

                        html_path = html_converter.convert_markdown_file(tdd_path)
                        print(f"   📄 Also created HTML: {html_path}")
                    except Exception as e:
                        print(f"   ⚠️ HTML generation failed: {e}")

                except Exception as e:
                    print(f"   ❌ Error: {e}")
                    import traceback
                    traceback.print_exc()

    print(f"\n🎉 TDD generation complete! ({generated_count} reports)")

if __name__ == "__main__":
    target_dir = sys.argv[1] if len(sys.argv) > 1 else "BatchTesting"
    if not os.path.isabs(target_dir):
        target_dir = os.path.join(os.path.dirname(__file__), '..', target_dir)
    generate_all_documentation(target_dir)

