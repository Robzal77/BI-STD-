import base64
import sys
import os

def encode_image(image_path):
    if not os.path.exists(image_path):
        print(f"Error: File not found: {image_path}")
        return

    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
        # Print only the base64 string
        print(encoded_string)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python encode_image.py <image_path>")
    else:
        encode_image(sys.argv[1])
