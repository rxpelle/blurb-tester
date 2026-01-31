#!/usr/bin/env python3
"""Convert markdown manuscript to PDF"""

import sys
from markdown_pdf import MarkdownPdf, Section

def main():
    input_file = "COMPLETE_MANUSCRIPT.md"
    output_file = "The_Aethelred_Cipher_Book1.pdf"

    print(f"Converting {input_file} to {output_file}...")

    try:
        # Create PDF converter
        pdf = MarkdownPdf(toc_level=2)

        # Add the manuscript
        pdf.add_section(Section(input_file, toc=True))

        # Save to PDF
        pdf.save(output_file)

        print(f"✓ Successfully created {output_file}")
        return 0

    except Exception as e:
        print(f"✗ Error: {e}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())
