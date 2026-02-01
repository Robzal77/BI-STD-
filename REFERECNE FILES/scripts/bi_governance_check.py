
"""
Power BI PBIP Validator
Validates TMDL model files against governance rules defined in config.json
"""

import argparse
import json
import csv
import os
import re
import sys
import subprocess
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# Fix Windows console encoding for emojis
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

# ANSI Definitions
class Colors:
    GREY = '\033[1;90m'  # Grey + Bold
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RESET = '\033[0m'

class BIValidator:
    """Validates Power BI PBIP projects against configured rules"""
    
    def __init__(self, config_path):
        """Initialize validator with config"""
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        self.errors = []
        self.warnings = []
        self.score = 100
        self.base_path = Path(__file__).parent.parent # script is in /scripts, base is / (parent.parent)
        self.project_config = {}  # Per-project overrides
        self.skipped_checks = []  # Track which checks were skipped
        self.all_measures = {}    # name -> file_path
        self.measure_references = defaultdict(int) 
    
    def load_project_config(self, pbip_folder):
        """Load project-level config overrides if present"""
        pbip_path = Path(pbip_folder)
        
        # Look for project_config.json in the PBIP folder
        possible_paths = [
            pbip_path / 'project_config.json',
            pbip_path.parent / 'project_config.json',
        ]
        
        for config_path in possible_paths:
            if config_path.exists():
                try:
                    with open(config_path, 'r') as f:
                        self.project_config = json.load(f)
                    print(f"📋 Loaded project config: {config_path.name}")
                    
                    # Report any overrides
                    overrides = self.project_config.get('overrides', {})
                    if overrides:
                        print(f"   Overrides active: {list(overrides.keys())}")
                    return
                except Exception as e:
                    print(f"⚠️  Error loading project config: {e}")
        
        # No project config found - that's fine
        self.project_config = {}
    
    def is_check_allowed(self, check_name):
        """Check if a specific validation check should run (not overridden)"""
        overrides = self.project_config.get('overrides', {})
        
        # Check for explicit allows
        if overrides.get(f'allow_{check_name}', False):
            self.skipped_checks.append(check_name)
            return False
        
        return True
    
    def has_skip_comment(self, content, check_code):
        """Check if content has a SKIP_CHECK comment for this specific check.
        
        Syntax: // SKIP_CHECK: <check_code> - <reason>
        Example: // SKIP_CHECK: bi_di_filter - Approved by Manager for cross-filtering
        
        Supported check codes:
        - auto_date_time
        - bi_di_filter (or bi_directional_filters)
        - hardcoded_colors
        - measure_description
        """
        # Normalize check code variations
        code_aliases = {
            'bi_directional_filters': ['bi_di_filter', 'bi_directional', 'bidi'],
            'auto_date_time': ['auto_datetime', 'autodate'],
            'hardcoded_colors': ['hardcoded_color', 'colors'],
            'measure_description': ['measure_desc', 'description']
        }
        
        # Build list of codes to check
        codes_to_check = [check_code]
        for main_code, aliases in code_aliases.items():
            if check_code == main_code or check_code in aliases:
                codes_to_check.extend([main_code] + aliases)
        
        # Look for skip comment pattern
        for code in set(codes_to_check):
            pattern = rf'//\s*SKIP_CHECK\s*:\s*{re.escape(code)}'
            if re.search(pattern, content, re.IGNORECASE):
                # Extract the reason if present
                reason_match = re.search(rf'//\s*SKIP_CHECK\s*:\s*{re.escape(code)}\s*-?\s*(.+)', content, re.IGNORECASE)
                reason = reason_match.group(1).strip() if reason_match else 'No reason provided'
                self.skipped_checks.append(f"{check_code} (inline: {reason[:40]}...)")
                return True
        
        return False
        
    def find_tmdl_files(self, pbip_folder):
        """Recursively find all model.tmdl files, excluding .internal and .backups folders"""
        pbip_path = Path(pbip_folder)
        all_files = list(pbip_path.rglob("*.tmdl"))
        # Exclude files in .internal or .backups folders
        return [f for f in all_files if '.internal' not in str(f) and '.backups' not in str(f)]
    
    def find_visual_files(self, pbip_folder):
        """Find all visual.json files in Report definition"""
        pbip_path = Path(pbip_folder)
        # Look for *.Report/definition/pages/**/visual.json
        report_folders = list(pbip_path.glob("*.Report"))
        visual_files = []
        for report in report_folders:
            visuals = list(report.glob("definition/pages/**/visual.json"))
            visual_files.extend(visuals)
        return visual_files
    
    def find_color_props(self, obj, color_props, found=None):
        """Recursively find color properties in JSON object"""
        if found is None:
            found = []
        
        if isinstance(obj, dict):
            for key, value in obj.items():
                if key in color_props:
                    found.append(key)
                else:
                    self.find_color_props(value, color_props, found)
        elif isinstance(obj, list):
            for item in obj:
                self.find_color_props(item, color_props, found)
        
        return list(set(found))  # Remove duplicates
    
    def check_hardcoded_colors(self, pbip_folder):
        """Check for hardcoded colors in visual definitions"""
        visual_files = self.find_visual_files(pbip_folder)
        color_properties = ['dataColors', 'fill', 'fillColor', 'defaultColor']
        
        if not visual_files:
            return  # No Report visuals to check
        
        for visual_file in visual_files:
            try:
                with open(visual_file, 'r', encoding='utf-8') as f:
                    visual_data = json.load(f)
                
                # Recursively check for color properties
                found_colors = self.find_color_props(visual_data, color_properties)
                
                if found_colors:
                    visual_name = visual_file.parent.name
                    self.errors.append({
                        'code': 'VISUAL_HARDCODED_COLOR',
                        'message': f"❌ Hardcoded Visual Colors found in {visual_name}. Properties: {', '.join(found_colors)}",
                        'impact': "Visuals with manual colors won't adapt if the Theme changes (e.g. Dark Mode).",
                        'fix': "Revert colors to default in the Format pane OR run 'reset_visual_colors.py'.",
                        'file': str(visual_file)
                    })
            except Exception as e:
                # Skip files that can't be parsed
                continue
    
    def parse_tmdl_file(self, file_path):
        """Parse TMDL file and return content"""
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def check_auto_datetime(self, content, file_path):
        """Check for autoDateTime: true or legacy annotation"""
        # Check for inline skip comment
        if self.has_skip_comment(content, 'auto_date_time'):
            return
        
        # Modern Property
        if re.search(r'autoDateTime\s*:\s*true', content, re.IGNORECASE):
            self.errors.append({
                'code': 'MODEL_AUTO_DATE_TIME_PROPERTY',
                'message': '❌ Auto Date/Time is ENABLED (Property detected)',
                'impact': '⚠️  IMPACT: This creates a hidden table for every date column. It increases file size by 20-40% and slows down refresh.',
                'fix': "🔧 FIX: File > Options > Data Load > Uncheck 'Auto Date/Time'",
                'file': str(file_path)
            })
            
        # Legacy Annotation (Crucial for V3 models)
        if re.search(r'annotation\s*__PBI_TimeIntelligenceEnabled\s*=\s*1', content, re.IGNORECASE):
            self.errors.append({
                'code': 'MODEL_AUTO_DATE_TIME_LEGACY',
                'message': "❌ Auto Date/Time is ENABLED (Legacy Annotation)",
                'impact': "This creates a hidden table for every date column. It increases file size by 20-40% and slows down refresh.",
                'fix': "File > Options > Data Load > Uncheck 'Auto Date/Time'",
                'file': str(file_path)
            })
    
    def check_bidirectional_filter(self, content, file_path):
        """Check for Bi-Directional filters"""
        if not self.is_check_allowed('bi_directional_filters'):
            return

        # Check for inline skip comment
        if self.has_skip_comment(content, 'bi_di_filter'):
            return
            
        # Look for crossFilteringBehavior: both
        if re.search(r'crossFilteringBehavior\s*:\s*both', content, re.IGNORECASE):
            self.errors.append({
                'code': 'MODEL_BI_DI_FILTER',
                'message': "❌ High Risk: Bi-Directional Filter found (Ambiguity Risk)",
                'impact': "Bi-di filters can cause ambiguity in the model path and unexpected results.",
                'fix': "Change Cross-filter direction to 'Single' unless absolutely necessary (and verify with schemas).",
                'file': str(file_path)
            })

    def check_many_to_many(self, content, file_path):
        """Check for Many-to-Many relationship cardinality"""
        if not self.is_check_allowed('many_to_many'):
            return
            
        if re.search(r'cardinality\s*:\s*manyToMany', content, re.IGNORECASE):
            self.errors.append({
                'code': 'MODEL_MANY_TO_MANY',
                'message': "❌ High Risk: Many-to-Many relationship found.",
                'impact': "M:M relationships are complex, slow, and often hide data quality issues.",
                'fix': "Try to introduce a bridge table (Star Schema) to resolve the M:M relationship.",
                'file': str(file_path)
            })
    
    def check_naming_convention(self, content, file_path):
        """Check if table and column names follow Title Case convention"""
        if not self.is_check_allowed('naming_convention'):
            return
            
        # Check Table Names
        table_match = re.search(r'table\s+["\']?([^"\'\n]+)["\']?', content)
        if table_match:
            name = table_match.group(1)
            
            # Ignore system tables
            if name.startswith('LocalDateTable') or name.startswith('DateTableTemplate'):
                return

            # Flag if contains underscores, starts with lowercase, or has default names
            if '_' in name or name[0].islower() or re.search(r'Table\d+|Query\d+', name):
                self.warnings.append({
                    'type': 'Naming',
                    'rule': 'Title Case / Meaningful Names',
                    'file': str(file_path),
                    'message': f"Table '{name}' should use Title Case and avoid underscores/defaults."
                })
        
        # Check Column Names (TAB column "Name")
        col_matches = re.finditer(r'^\tcolumn\s+["\']?([^"\'\n]+)["\']?', content, re.MULTILINE)
        for match in col_matches:
            name = match.group(1)
            if '_' in name or name[0].islower() or re.search(r'Column\d+', name):
                self.warnings.append({
                    'type': 'Naming',
                    'rule': 'Title Case / Meaningful Names',
                    'file': str(file_path),
                    'message': f"Column '{name}' in {file_path.name} should use Title Case."
                })
    
    def check_date_table_mode(self, content, file_path):
        """Check if Date table has mode: import"""
        # Look for table named 'Date' or containing 'Date' and check for mode
        date_table_pattern = r'table\s+["\']?Date["\']?\s*{([^}]*)}'
        matches = re.finditer(date_table_pattern, content, re.IGNORECASE | re.DOTALL)
        
        for match in matches:
            table_content = match.group(1)
            # Check if mode: import exists in this table
            if not re.search(r'mode\s*:\s*import', table_content, re.IGNORECASE):
                self.errors.append({
                    'code': 'MODEL_DATE_TABLE_MODE',
                    'message': '❌ Date table must have mode: import',
                    'impact': 'If the Date table is not in import mode, it cannot be used for time intelligence functions or relationships with other import mode tables.',
                    'fix': 'Ensure your custom Date table is set to mode: import.',
                    'file': str(file_path)
                })
    
    def check_measure_descriptions(self, content, file_path):
        """Check if measures have descriptions"""
        # Pattern to find measures
        measure_pattern = r'measure\s+(["\']?)(\w+)\1\s*=([^measure]*?)(?=measure\s+|$)'
        measures = re.finditer(measure_pattern, content, re.IGNORECASE | re.DOTALL)
        
        for measure in measures:
            measure_name = measure.group(2)
            measure_content = measure.group(3)
            
            # Check if description exists in measure content
            if not re.search(r'description\s*:', measure_content, re.IGNORECASE):
                self.warnings.append({
                    'type': 'Documentation',
                    'rule': 'Missing description',
                    'file': str(file_path),
                    'measure': measure_name,
                    'message': f'Measure "{measure_name}" missing description property',
                    'fix': "🔧 NEXT STEP: Add a 'description:' property to this measure in its TMDL file."
                })
            
            # Inventory all measures for unused check
            self.all_measures[measure_name] = str(file_path)
    
    def collect_references(self, content):
        """Scan content for measure references in DAX"""
        # Simple regex for [Measure Name]
        refs = re.findall(r'\[([^\]]+)\]', content)
        for ref in refs:
            self.measure_references[ref] += 1

    def check_unused_measures(self, pbip_folder):
        """Identify measures that are never referenced"""
        if not self.is_check_allowed('unused_measures'):
            return

        unused = []
        for m_name, m_file in self.all_measures.items():
            if self.measure_references[m_name] == 0:
                unused.append(m_name)
        
        if unused:
            self.warnings.append({
                'type': 'Efficiency',
                'rule': 'Unused Measures',
                'file': 'Multiple Files',
                'message': f"Detected {len(unused)} unused measures: {', '.join(unused[:5])}{'...' if len(unused)>5 else ''}"
            })
    
    def validate_pbip(self, pbip_folder):
        """Run all validation checks on PBIP folder"""
        print(f"\n{'='*70}")
        print(f"🔍 Validating PBIP: {pbip_folder}")
        print(f"{'='*70}\n")
        
        # Load project-level overrides
        self.load_project_config(pbip_folder)
        
        # Find all TMDL files
        try:
            tmdl_files = self.find_tmdl_files(pbip_folder)
            
            # 2. Check for Hidden Date Tables (The Smoking Gun)
            hidden_tables = [f for f in tmdl_files if "LocalDateTable" in f.name or "DateTableTemplate" in f.name]
            
            if len(hidden_tables) > 0 and self.is_check_allowed('auto_date_time'):
                self.errors.append({
                    'code': 'MODEL_AUTO_DATE_TIME_HIDDEN_TABLES',
                    'message': f"❌ Auto Date/Time is ENABLED ({len(hidden_tables)} hidden tables found).",
                    'impact': "This creates a hidden table for every date column. It increases file size by 20-40% and slows down refresh.",
                    'fix': "File > Options > Data Load > Uncheck 'Auto Date/Time'",
                    'file': "Multiple Files"
                })
        except Exception as e:
            print(f"❌ Error finding TMDL files: {e}")
            tmdl_files = []
        
        # Find visual files
        try:
            visual_files = self.find_visual_files(pbip_folder)
        except Exception as e:
            print(f"❌ Error finding visual files: {e}")
            visual_files = [] # Logic: handled separately
        
        if not tmdl_files and not visual_files:
            print("❌ No TMDL files or Report visuals found in the specified folder")
            print("   Please point to a folder containing .SemanticModel or .Report folders")
            return
        
        print(f"📁 Found {len(tmdl_files)} TMDL file(s)")
        print(f"📁 Found {len(visual_files)} Visual file(s)\n")
        
        # Step 1.5: Collect references from all files for the unused check
        for tmdl_file in tmdl_files:
            try:
                content = self.parse_tmdl_file(tmdl_file)
                self.collect_references(content)
            except: pass
            
        for visual_file in visual_files:
            try:
                with open(visual_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    self.collect_references(content)
            except: pass

        # Process each TMDL file for rules
        for tmdl_file in tmdl_files:
            try:
                print(f"   {Colors.GREY}Checking: {tmdl_file.name}{Colors.RESET}")
                content = self.parse_tmdl_file(tmdl_file)
                
                # Run checks (respecting project-level overrides)
                if self.config.get('rules', {}).get('forbidden_logic', {}).get('auto_date_time'):
                    if self.is_check_allowed('auto_date_time'):
                        self.check_auto_datetime(content, tmdl_file)
                
                if self.config.get('rules', {}).get('forbidden_logic', {}).get('bi_directional_filters'):
                    if self.is_check_allowed('bi_directional_filters'):
                        self.check_bidirectional_filter(content, tmdl_file)
                
                if self.config.get('rules', {}).get('forbidden_logic', {}).get('many_to_many'):
                    self.check_many_to_many(content, tmdl_file)
                
                # Naming Convention (Warning only)
                self.check_naming_convention(content, tmdl_file)
                
                # Check date table mode
                self.check_date_table_mode(content, tmdl_file)
                
                # Check measure descriptions (Populates all_measures)
                self.check_measure_descriptions(content, tmdl_file)
            except Exception as e:
                 print(f"   ⚠️  Skipping {tmdl_file.name} due to parse error: {e}")
                 self.warnings.append({
                     'type': 'Parser',
                     'rule': 'File Readable', 
                     'file': str(tmdl_file),
                     'message': f'Validation skipped due to error: {e}'
                 })
        
        # Check for hardcoded colors in Report visuals
        if visual_files:
            print(f"\n>> Checking Report visuals for hardcoded colors...")
            try:
                self.check_hardcoded_colors(pbip_folder)
            except Exception as e:
                print(f"❌ Error validating colors: {e}")
        
        # Check for unused measures globally
        self.check_unused_measures(pbip_folder)
        
        # Calculate score
        self.score -= len(self.errors) * 10
        self.score -= len(self.warnings) * 2
        self.score = max(0, self.score)  # Don't go below 0
        
        # Print results
        self.print_summary()
        
        # Log to CSV
        try:
            self.log_to_csv(pbip_folder)
        except Exception as e:
            print(f"⚠️  Warning: Could not write to log file: {e}")
    
    def print_summary(self):
        """Print educational summary to console"""
        print(f"\n{'='*70}")
        print(f"{Colors.GREY}📊 VALIDATION SUMMARY{Colors.RESET}")
        print(f"{'='*70}\n")
        
        # Errors
        if self.errors:
            print(f"{Colors.RED}🚫 ISSUES FOUND (Score: {max(0, self.score)}/100){Colors.RESET}\n")
            for error in self.errors:
                print(f"{Colors.RED}{error['message']}{Colors.RESET}")
                if 'impact' in error:
                    print(f"    {error['impact']}")
                if 'fix' in error:
                    print(f"    {error['fix']}")
                print(f"    File: {error['file']}")
                print(f"{'-'*60}")
        else:
            print(f"{Colors.GREEN}✅  SUCCESS: Report looks clean! (Score: 100/100){Colors.RESET}")
        
        # Warnings
        if self.warnings:
            print(f"\n{Colors.YELLOW}⚠️  WARNINGS ({len(self.warnings)}):{Colors.RESET}")
            for warning in self.warnings:
                print(f"   • {warning['message']}")
                print(f"     File: {warning['file']}")
        
        # Skipped Checks (Project Overrides)
        if self.skipped_checks:
            unique_skipped = list(set(self.skipped_checks))
            print(f"\n{Colors.GREY}📋 CHECKS SKIPPED (Project Override):{Colors.RESET}")
            for check in unique_skipped:
                print(f"   • {check}")
        
        print(f"\n{'='*70}")
    
    def get_issue_summary(self):
        """Categorize and summarize issues for logging"""
        summary = defaultdict(int)
        
        # Categorize Errors
        for error in self.errors:
            if error.get('code', '').startswith('MODEL_AUTO_DATE_TIME'):
                summary['Modelling_AutoDateTime'] += 1
            elif error.get('code', '') == 'MODEL_BI_DI_FILTER':
                summary['Modelling_BiDiFilter'] += 1
            elif error.get('code', '') == 'MODEL_DATE_TABLE_MODE':
                summary['Modelling_DateTableMode'] += 1
            elif error.get('code', '') == 'VISUAL_HARDCODED_COLOR':
                summary['Theme_HardcodedColors'] += 1
            else:
                summary['Other_Errors'] += 1
                
        # Categorize Warnings
        for warning in self.warnings:
            if warning.get('type') == 'Theme Compliance':
                summary['Theme_Compliance'] += 1
            elif warning.get('type') == 'Documentation':
                summary['Documentation'] += 1
            else:
                summary['Other_Warnings'] += 1
        
        # Format as string: "Modelling: 2; Theme: 5"
        parts = []
        for category, count in summary.items():
            if count > 0:
                parts.append(f"{category}: {count}")
        
        return "; ".join(parts) if parts else "None"

    def get_git_author(self, folder_path):
        """Get the last git author for the folder."""
        try:
            return "Test Developer (Demo)"
            # Check if git is available and folder is tracked
            # We run from the current script's parent or base path
            cmd = ['git', 'log', '-1', '--format=%an', folder_path]
            result = subprocess.check_output(cmd, check=True, cwd=self.base_path).decode('utf-8').strip()
            return result if result else "Unknown"
        except Exception as e:
            return "Unknown"

    def log_to_csv(self, pbip_folder):
        """
        Log keys: timestamp, report_name, developer, score, status, errors, warnings, issue_summary, failed_rules, full_path
        """
        log_dir = self.base_path / 'projects'
        log_dir.mkdir(exist_ok=True)
        log_path = log_dir / 'audit_log.csv'
        
        pbip_path_obj = Path(pbip_folder)
        report_name = pbip_path_obj.stem.replace('.SemanticModel', '').replace('.Report', '').replace('.pbip', '')
        developer = self.get_git_author(str(pbip_path_obj))
        
        # Get categorized summary
        issue_summary_str = self.get_issue_summary()
        
        # Helper: Map codes to readable text
        code_map = {
            'MODEL_AUTO_DATE_TIME_PROPERTY': 'Auto Date/Time Enabled',
            'MODEL_AUTO_DATE_TIME_LEGACY': 'Auto Date/Time Enabled (Legacy)',
            'MODEL_AUTO_DATE_TIME_HIDDEN_TABLES': 'Hidden Date Tables Found',
            'MODEL_BI_DI_FILTER': 'Bi-Directional Filter',
            'MODEL_DATE_TABLE_MODE': 'Date Table Not Import Mode',
            'VISUAL_HARDCODED_COLOR': 'Hardcoded Visual Colors'
        }
        
        # Get unique readable descriptions
        unique_failures = sorted(list(set([code_map.get(e.get('code'), e.get('code', 'Unknown Issue')) for e in self.errors])))
        failed_rules = "; ".join(unique_failures)
        
        # Write header if new
        file_exists = os.path.isfile(log_path)
        
        with open(log_path, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(['timestamp', 'report_name', 'developer', 'score', 'status', 'errors', 'warnings', 'issue_summary', 'failed_rules', 'full_path'])
            
            status_label = 'PASS' if self.score >= 70 else 'FAIL'
            
            writer.writerow([
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                report_name,
                developer,
                self.score,
                status_label,
                len(self.errors),
                len(self.warnings),
                issue_summary_str,
                failed_rules,
                pbip_folder
            ])
        
        print(f"📝 Results logged to: {log_path}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Validate Power BI PBIP projects against governance rules'
    )
    parser.add_argument(
        'pbip_folder',
        help='Path to the PBIP folder to validate'
    )
    parser.add_argument(
        '--config',
        default='config.json',
        help='Path to config.json (default: config.json in parent directory)'
    )
    
    args = parser.parse_args()
    
    # Determine config path
    if args.config == 'config.json':
        # Use config.json from script's parent directory
        script_dir = Path(__file__).parent
        config_path = script_dir.parent / 'config.json'
    else:
        config_path = Path(args.config)
    
    if not config_path.exists():
        print(f"❌ Error: Config file not found at {config_path}")
        print("   Please ensure config.json exists or provide path with --config")
        return 1
    
    # Validate PBIP folder exists
    pbip_path = Path(args.pbip_folder)
    if not pbip_path.exists():
        print(f"❌ Error: Target folder not found at {args.pbip_folder}")
        return 1
        
    if not pbip_path.is_dir():
        print(f"❌ Error: Target is not a directory: {args.pbip_folder}")
        return 1
    
    # Run validation with global exception handler
    try:
        validator = BIValidator(config_path)
        validator.validate_pbip(args.pbip_folder)
        return 0 if validator.score >= 70 else 1
    except Exception as e:
        print(f"\n❌ CRITICAL VALIDATOR FAILURE: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
