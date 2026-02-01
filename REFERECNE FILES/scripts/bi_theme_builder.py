"""
Power BI Theme Generator
Reads config.json and generates a Power BI JSON theme file
"""

import json
import os
from pathlib import Path


def generate_theme():
    """Generate Power BI theme from config.json"""
    
    # Get the parent directory
    script_dir = Path(__file__).parent
    parent_dir = script_dir.parent
    
    # Read config.json
    config_path = parent_dir / "config.json"
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    # Extract visuals section
    visuals = config.get('visuals', {})
    theme_config = visuals.get('theme', {})
    fonts = visuals.get('fonts', {})
    
    # Build Power BI theme structure
    theme = {
        "name": theme_config.get('name', 'Corporate Standard'),
        "dataColors": theme_config.get('dataColors', []),
        "background": theme_config.get('background', '#FFFFFF'),
        "foreground": theme_config.get('foreground', '#000000'),
        "tableAccent": theme_config.get('tableAccent', '#FFC400'),
        "good": "#107C10",
        "neutral": "#FFC400",
        "bad": "#E81123",
        "visualStyles": {
            "*": {
                "*": {
                    "border": [
                        {
                            "show": False
                        }
                    ],
                    "title": [
                        {
                            "fontFamily": fonts.get('family', 'Segoe UI'),
                            "fontSize": fonts.get('title_size', 12)
                        }
                    ]
                }
            }
        }
    }
    
    # Ensure templates directory exists
    templates_dir = parent_dir / "templates"
    templates_dir.mkdir(exist_ok=True)
    
    # Write theme file
    output_path = templates_dir / "Corporate_Standard.json"
    with open(output_path, 'w') as f:
        json.dump(theme, f, indent=2)
    
    print('Theme Generated Successfully')


if __name__ == "__main__":
    generate_theme()
