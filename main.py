import os
import re
import cv2
import pytesseract
import pandas as pd

# --- Configuration ---
IMAGE_DIR = 'images'
OUTPUT_FILE = 'output/results.xlsx'
LANGUAGE = 'amh+eng' # Process Amharic and English

# --- Main Processing Logic ---

def preprocess_image(image_path):
    """
    Loads an image and applies basic preprocessing for OCR.
    - Converts to grayscale
    - Applies a binary threshold
    """
    try:
        img = cv2.imread(image_path)
        if img is None:
            print(f"Warning: Could not read image file: {image_path}")
            return None
        
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # A simple binary threshold can be effective for high-contrast, handwritten documents.
        # The value 150 is a starting point and may need tuning.
        _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
        
        return thresh
    except Exception as e:
        print(f"Error preprocessing image {image_path}: {e}")
        return None

def extract_text_from_image(image):
    """
    Uses Tesseract to extract text from a preprocessed image.
    --psm 4: Assume a single column of text of variable sizes. This is often
             better for preserving the line-by-line structure of a document.
    """
    try:
        custom_config = f'-l {LANGUAGE} --psm 4'
        text = pytesseract.image_to_string(image, config=custom_config)
        return text
    except pytesseract.TesseractNotFoundError:
        print("\n--- TESSERACT NOT FOUND ---")
        print("Error: `tesseract` is not installed or it's not in your system's PATH.")
        return None
    except Exception as e:
        print(f"Error during OCR extraction: {e}")
        return None

def main():
    """
    Main function to orchestrate the OCR process.
    This version focuses on extracting raw lines of text from each image.
    """
    print("Starting document processing...")
    
    if not os.path.isdir(IMAGE_DIR):
        print(f"Error: Image directory '{IMAGE_DIR}' not found.")
        return

    if not os.path.isdir('output'):
        os.makedirs('output')

    image_files = [f for f in os.listdir(IMAGE_DIR) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    
    if not image_files:
        print(f"No images found in the '{IMAGE_DIR}' directory.")
        return

    all_lines = []

    for image_file in image_files:
        image_path = os.path.join(IMAGE_DIR, image_file)
        print(f"\n--- Processing: {image_path} ---")
        
        preprocessed_image = preprocess_image(image_path)
        
        if preprocessed_image is None:
            continue
            
        raw_text = extract_text_from_image(preprocessed_image)
        
        if not raw_text or not raw_text.strip():
            print("Could not extract text from this image.")
            continue
        
        # Split the raw text into individual lines and filter out empty lines
        lines = [line.strip() for line in raw_text.split('\n') if line.strip()]
        
        print(f"Extracted {len(lines)} lines of text.")
        
        for line in lines:
            all_lines.append({
                'Source File': image_file,
                'Extracted Line': line
            })

    if not all_lines:
        print("\nNo data was successfully extracted from any image.")
        return

    # --- Export to Excel ---
    print(f"\nExporting {len(all_lines)} total lines to {OUTPUT_FILE}...")
    df = pd.DataFrame(all_lines)
    
    try:
        df.to_excel(OUTPUT_FILE, index=False)
        print(f"Successfully created Excel file at: {OUTPUT_FILE}")
    except Exception as e:
        print(f"\n--- PANDAS/EXCEL ERROR ---")
        print(f"Could not write to Excel file: {e}")

if __name__ == '__main__':
    main()
