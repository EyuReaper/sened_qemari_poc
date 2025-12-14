# Sened Qemari - Document Digitization POC

This project is a proof-of-concept (POC) for a command-line tool that digitizes physical documents from images. It uses Optical Character Recognition (OCR) to extract text, translates it, analyzes the content to determine its structure, and saves it as either a Microsoft Word document or an Excel spreadsheet.

## Features

- **OCR on Images**: Extracts text from image files using Tesseract OCR.
- **Text Translation**: Translates the extracted text to a desired language (supports English and Amharic) using `googletrans`.
- **Structure Analysis**: Heuristically determines if the document content is a passage or a table.
- **Automatic Formatting**:
    - Saves tabular data as a `.xlsx` spreadsheet.
    - Saves passage data as a `.docx` Word document.
- **Command-Line Interface**: Easy to use from the terminal.

## Setup and Installation

### 1. System Dependencies (Tesseract OCR Engine)

This tool requires the Tesseract OCR engine to be installed on your system.

**For Fedora (as you are using):**
```bash
sudo dnf install tesseract tesseract-langpack-eng tesseract-langpack-amh
```

**For Debian/Ubuntu:**
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr tesseract-ocr-eng tesseract-ocr-amh
```

### 2. Python Dependencies

Clone the repository and install the required Python packages from `requirements.txt`.

```bash
pip install -r requirements.txt
```

## How to Run

Run the script from your terminal, providing the path to the input image. The processed file will be saved in the `output/` directory.

### Syntax
```bash
python main.py <path_to_image> [--lang <language_code>]
```

- `<path_to_image>`: The path to the image file you want to process.
- `[--lang <language_code>]`: (Optional) The target language.
    - `en` for English (default)
    - `am` for Amharic

### Example

To process a printed document and translate it to English:
```bash
python main.py images/image_3.jpg --lang en
```
The script will analyze the content and save either `output/image_3_output.docx` or `output/image_3_output.xlsx`.

## Known Limitations

- **OCR Accuracy**: The Tesseract engine works best on clear, printed, machine-readable text. Its performance on handwritten documents is very limited.
- **Translation Stability**: The `googletrans` library is an unofficial, free client that can sometimes be unreliable or face network issues.
- **Structure Analysis**: The table vs. passage detection is based on a simple heuristic and may not be accurate for complex document layouts.