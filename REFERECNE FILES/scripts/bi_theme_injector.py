import json
import base64
import os
import sys

def inject_image(template_path, image_path, output_path=None):
    # 1. Read Image and Encode
    if not os.path.exists(image_path):
        print(f"❌ Image not found: {image_path}")
        return

    with open(image_path, "rb") as img_f:
        b64_str = base64.b64encode(img_f.read()).decode('utf-8')
        full_b64 = f"data:image/png;base64,{b64_str}"

    # 2. Read Theme JSON
    if not os.path.exists(template_path):
        print(f"❌ Template not found: {template_path}")
        return

    with open(template_path, "r", encoding='utf-8') as json_f:
        theme_data = json.load(json_f)

    # 3. Modify JSON
    # Target: visualStyles -> page -> * -> background -> [0]
    try:
        page_bg = theme_data.get("visualStyles", {}).get("page", {}).get("*", {}).get("background", [])
        if not page_bg:
            # Create structure if missing
            if "visualStyles" not in theme_data: theme_data["visualStyles"] = {}
            if "page" not in theme_data["visualStyles"]: theme_data["visualStyles"]["page"] = {}
            if "*" not in theme_data["visualStyles"]["page"]: theme_data["visualStyles"]["page"]["*"] = {}
            theme_data["visualStyles"]["page"]["*"]["background"] = []
        
        # Define the Image Object
        image_obj = {
            "image": {
                "name": "Corporate Layout",
                "scaling": "Fit",
                "url": full_b64
            },
            "transparency": 0
        }
        
        # Replace the list with just this image object
        theme_data["visualStyles"]["page"]["*"]["background"] = [image_obj]
        
        # Also ensure 'outspace' matches or is transparent?
        # Usually outspace matches the page color or is transparent.
        # Let's clean outspace to be transparent so image shows? Or keep it grey?
        # Power BI "Wallpaper" vs "Canvas Background".
        # Theme "background" usually targets CANVAS background.
        # Wallpaper is "outspace".
        # If the image is the full slide, we want it on the Canvas.
        
        print("OK Injected Base64 Image into Theme Structure.")

    except Exception as e:
        print(f"Error modifying JSON: {e}")
        return

    # 4. Save
    target_file = output_path if output_path else template_path
    with open(target_file, "w", encoding='utf-8') as out_f:
        json.dump(theme_data, out_f, indent=4)
    
    print(f"Saved updated theme to: {target_file}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python inject_theme_image.py <template_json> <image_png> [output_json]")
    else:
        tmpl = sys.argv[1]
        img = sys.argv[2]
        out = sys.argv[3] if len(sys.argv) > 3 else None
        inject_image(tmpl, img, out)
