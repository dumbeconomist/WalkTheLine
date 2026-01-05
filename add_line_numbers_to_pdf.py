#!/usr/bin/env python3
"""
Script to add line numbers to a PDF file based on actual text lines from OCR.
Uses PyPDF2 for PDF manipulation and reportlab for adding line numbers.
"""

import sys
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from io import BytesIO
import argparse
import re


def extract_text_lines_with_positions(page):
    """
    Extract text lines from a PDF page along with their Y positions.

    Args:
        page: PyPDF2 page object

    Returns:
        List of tuples (y_position, line_text)
    """
    def visitor_body(text, cm, tm, font_dict, font_size):
        """Visitor function to extract text with position information."""
        y_position = tm[5]  # Transformation matrix [5] contains Y coordinate
        lines_with_positions.append((y_position, text, font_size))

    lines_with_positions = []
    page.extract_text(visitor_text=visitor_body)

    return lines_with_positions


def group_text_into_lines(text_fragments, tolerance=2):
    """
    Group text fragments that are on the same line based on Y position.

    Args:
        text_fragments: List of (y_position, text, font_size) tuples
        tolerance: Y position tolerance for grouping (points)

    Returns:
        List of (y_position, line_text) tuples, sorted by Y position (top to bottom)
    """
    if not text_fragments:
        return []

    # Sort by Y position (descending - top to bottom)
    text_fragments.sort(key=lambda x: x[0], reverse=True)

    lines = []
    current_line_y = None
    current_line_text = []

    for y_pos, text, font_size in text_fragments:
        # Skip empty text
        if not text.strip():
            continue

        # Start new line or add to current line
        if current_line_y is None or abs(y_pos - current_line_y) > tolerance:
            # Save previous line if exists
            if current_line_text:
                lines.append((current_line_y, ' '.join(current_line_text)))

            # Start new line
            current_line_y = y_pos
            current_line_text = [text]
        else:
            # Add to current line
            current_line_text.append(text)

    # Don't forget the last line
    if current_line_text:
        lines.append((current_line_y, ' '.join(current_line_text)))

    return lines


def add_line_numbers_to_pdf(input_pdf_path, output_pdf_path, font_size=8, x_position=30,
                            continuous=False, start_number=1):
    """
    Add line numbers to a PDF file based on actual OCR'd text lines.

    Args:
        input_pdf_path: Path to the input PDF file
        output_pdf_path: Path to save the output PDF file
        font_size: Font size for line numbers (default: 8)
        x_position: X position for line numbers in points (default: 30)
        continuous: If True, continue line numbering across pages (default: False)
        start_number: Starting line number (default: 1)
    """
    # Read the existing PDF
    reader = PdfReader(input_pdf_path)
    writer = PdfWriter()

    print(f"Processing {len(reader.pages)} pages...")

    current_line_number = start_number

    # Process each page
    for page_num, page in enumerate(reader.pages):
        page_width = float(page.mediabox.width)
        page_height = float(page.mediabox.height)

        # Extract text with positions
        text_fragments = extract_text_lines_with_positions(page)

        # Group into lines
        lines = group_text_into_lines(text_fragments)

        print(f"Page {page_num + 1}: Found {len(lines)} text lines")

        # Create a new PDF with line numbers
        packet = BytesIO()
        can = canvas.Canvas(packet, pagesize=(page_width, page_height))
        can.setFont("Helvetica", font_size)

        # Reset line number for each page if not continuous
        if not continuous:
            page_line_number = start_number

        # Add line numbers at detected positions
        for y_position, line_text in lines:
            # Use current line number
            line_num = current_line_number if continuous else page_line_number

            # Draw line number
            can.drawString(x_position, y_position, str(line_num))

            # Increment counters
            if continuous:
                current_line_number += 1
            else:
                page_line_number += 1

        can.save()

        # Move to the beginning of the BytesIO buffer
        packet.seek(0)

        # Read the line numbers PDF
        line_numbers_pdf = PdfReader(packet)
        line_numbers_page = line_numbers_pdf.pages[0]

        # Merge the line numbers with the original page
        page.merge_page(line_numbers_page)
        writer.add_page(page)

        if continuous:
            print(f"  Line numbers: {start_number if page_num == 0 else 'continued'} - {current_line_number - 1}")
        else:
            print(f"  Line numbers: {start_number} - {page_line_number - 1}")

    # Write the output PDF
    with open(output_pdf_path, 'wb') as output_file:
        writer.write(output_file)

    print(f"\nSuccess! Output saved to: {output_pdf_path}")

    if continuous:
        print(f"Total lines numbered: {current_line_number - start_number}")


def main():
    parser = argparse.ArgumentParser(
        description='Add line numbers to a PDF file based on actual OCR\'d text lines',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python add_line_numbers_to_pdf.py input.pdf output.pdf
  python add_line_numbers_to_pdf.py input.pdf output.pdf --continuous
  python add_line_numbers_to_pdf.py input.pdf output.pdf --font-size 10 --x-position 20
  python add_line_numbers_to_pdf.py input.pdf output.pdf --start 100
        """
    )

    parser.add_argument('input_pdf', help='Path to the input PDF file')
    parser.add_argument('output_pdf', help='Path to save the output PDF file')
    parser.add_argument('--font-size', type=int, default=8,
                        help='Font size for line numbers (default: 8)')
    parser.add_argument('--x-position', type=int, default=30,
                        help='X position for line numbers in points (default: 30)')
    parser.add_argument('--continuous', action='store_true',
                        help='Continue line numbering across pages (default: restart each page)')
    parser.add_argument('--start', type=int, default=1,
                        help='Starting line number (default: 1)')

    args = parser.parse_args()

    try:
        add_line_numbers_to_pdf(
            args.input_pdf,
            args.output_pdf,
            font_size=args.font_size,
            x_position=args.x_position,
            continuous=args.continuous,
            start_number=args.start
        )
    except FileNotFoundError:
        print(f"Error: Input file '{args.input_pdf}' not found.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
