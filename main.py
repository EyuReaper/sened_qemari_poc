import argparse
import os
import io

from PIL import Image
import pytesseract
from googletrans import Translator
import pandas as pd
from docx import Document

# Ensure the output directory exists
OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def perform_ocr(image_path: str) -> str:
    """
    Performs OCR on the given image path and returns the extracted text using Tesseract.
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found at {image_path}")
    
    img = Image.open(image_path)
    text = pytesseract.image_to_string(img, lang='eng+amh') 
    return text

def translate_text(text: str, target_language: str) -> str:
    """
    Translates the given text to the target language.
    target_language can be 'en' for English or 'am' for Amharic.
    """
    translator = Translator()
    
    if target_language == 'en':
        translated_text = translator.translate(text, dest='en').text
    elif target_language == 'am':
        translated_text = translator.translate(text, dest='am').text
    else:
        raise ValueError("Target language must be 'en' (English) or 'am' (Amharic).")
    
    return translated_text

def is_tabular(text: str, confidence_threshold: float = 0.7) -> bool:
    """
    Heuristically determines if the text is tabular or a passage.
    A simple heuristic: count lines with consistent 'columns' (separated by multiple spaces/tabs).
    """
    lines = text.strip().split('\n')
    
    if not lines:
        return False

    # Filter out empty lines or lines that are too short to be meaningful table rows
    meaningful_lines = [line for line in lines if len(line.strip()) > 5] 
    if not meaningful_lines:
        return False
        
    column_counts = []
    for line in meaningful_lines:
        # Split by multiple spaces or tabs to identify potential columns
        columns = [col.strip() for col in line.split('  ') if col.strip()] # Split by at least two spaces
        if not columns: # If splitting by '  ' yields no columns, try splitting by single space
            columns = [col.strip() for col in line.split(' ') if col.strip()]
        column_counts.append(len(columns)) # Append the count here

    if not column_counts:
        return False

    # Analyze column counts for consistency
    from collections import Counter
    counts_frequency = Counter(column_counts)
    
    # Find the most common column count
    most_common_count, most_common_frequency = counts_frequency.most_common(1)[0]
    
    # If the most common column count is 1 or 2 (typical for passages with some minor spacing)
    # AND its frequency is very high, it's probably a passage.
    if most_common_count <= 2 and most_common_frequency / len(meaningful_lines) > confidence_threshold:
        return False # Likely a passage

    # If a significant portion of meaningful lines have more than 2 columns, consider it tabular
    multi_column_lines = sum(1 for count in column_counts if count > 2)
    
    if multi_column_lines / len(meaningful_lines) > confidence_threshold:
        return True # Likely tabular

    return False # Default to false if no strong indication

def create_spreadsheet(text: str, output_path: str):
    """
    Converts the text into a pandas DataFrame and saves it as an XLSX file.
    Assumes whitespace-separated columns.
    """
    data = []
    lines = text.strip().split('\n')
    for line in lines:
        # Split by any whitespace for robustness
        row = [item.strip() for item in line.split() if item.strip()]
        if row: # Only add non-empty rows
            data.append(row)
    
    if not data:
        print("Warning: No parseable data found for spreadsheet. No file created.")
        return
        
    # Pad rows to ensure they all have the same number of columns for DataFrame creation
    max_cols = max(len(row) for row in data)
    padded_data = [row + [''] * (max_cols - len(row)) for row in data]
    
    df = pd.DataFrame(padded_data)
    df.to_excel(output_path, index=False, header=False) # No header for raw data
    print(f"Spreadsheet saved to {output_path}")

def create_word_document(text: str, output_path: str):
    """
    Creates a Word document from the given text.
    """
    document = Document()
    for paragraph in text.split('\n'):
        if paragraph.strip(): # Add non-empty paragraphs
            document.add_paragraph(paragraph.strip())
    document.save(output_path)
    print(f"Word document saved to {output_path}")

def main():
    parser = argparse.ArgumentParser(description="Digitize physical data from images.")
    parser.add_argument("image_path", help="Path to the input image file.")
    parser.add_argument("--lang", default="en", choices=["en", "am"], 
                        help="Target language for output (en for English, am for Amharic). Default is 'en'.")
    
    args = parser.parse_args()

    print(f"Processing image: {args.image_path}")
    print(f"Target language: {args.lang}")

    try:
        # Step 1: Perform OCR
        print("Performing OCR...")
        extracted_text = perform_ocr(args.image_path)
        if not extracted_text.strip():
            print("No text detected by OCR. Exiting.")
            return

        print("\n--- Extracted Text ---")
        print(extracted_text[:500] + "..." if len(extracted_text) > 500 else extracted_text)
        print("----------------------\n")

        # Step 2: Translate text
        print(f"Translating to {args.lang}...")
        translated_text = translate_text(extracted_text, args.lang)
        
        print("\n--- Translated Text ---")
        print(translated_text[:500] + "..." if len(translated_text) > 500 else translated_text)
        print("----------------------\n")

        # Step 3: Determine if tabular or passage
        print("Analyzing text structure...")
        if is_tabular(translated_text):
            print("Detected as tabular data.")
            output_file = os.path.join(OUTPUT_DIR, f"{os.path.basename(args.image_path).split('.')[0]}_output.xlsx")
            create_spreadsheet(translated_text, output_file)
        else:
            print("Detected as passage/document data.")
            output_file = os.path.join(OUTPUT_DIR, f"{os.path.basename(args.image_path).split('.')[0]}_output.docx")
            create_word_document(translated_text, output_file)

    except FileNotFoundError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()