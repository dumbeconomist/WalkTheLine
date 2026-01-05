# PDF Line Number Tool

Adds line numbers to PDF files based on actual OCR'd text lines. I wrote this because someone asked me to pay $60 American Dollars for this -- and I said "rediculous!" So here it is for you, for free, as well! 

## Installation

Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

```bash
python add_line_numbers_to_pdf.py input.pdf output.pdf
```

This will add line numbers starting from 1 on each page.

### Options

- `--continuous` - Continue line numbering across all pages (instead of restarting each page)
- `--start N` - Start numbering from a specific number (default: 1)
- `--font-size N` - Font size for line numbers (default: 8)
- `--x-position N` - Horizontal position in points from left edge (default: 30)

### Examples

```bash
# Continuous numbering across entire document
python add_line_numbers_to_pdf.py input.pdf output.pdf --continuous

# Start from line 100
python add_line_numbers_to_pdf.py input.pdf output.pdf --start 100

# Custom font size and position
python add_line_numbers_to_pdf.py input.pdf output.pdf --font-size 10 --x-position 20

# All options combined
python add_line_numbers_to_pdf.py input.pdf output.pdf --continuous --start 1 --font-size 9 --x-position 25
```

## How It Works

The script:
1. Reads the OCR'd text layer from your PDF
2. Detects actual text lines based on their Y-coordinates
3. Groups text fragments that appear on the same line
4. Places line numbers at the exact vertical position of each detected text line

## Requirements

- Python 3.7+
- PyPDF2 >= 3.0.0
- reportlab >= 4.0.0

## Notes

- The PDF must have an OCR'd text layer (searchable text)
- Line numbers are placed based on detected text positions
- Empty lines or lines without text will not be numbered
