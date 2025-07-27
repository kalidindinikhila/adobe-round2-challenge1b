#!/usr/bin/env python3
"""
Test Round 1A locally
"""


import sys
import os
# Ensure the current directory is in sys.path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from round1a import PDFOutlineExtractor
import json

def test_round1a_local():
    """Test Round 1A locally"""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    input_dir = os.path.join(base_dir, 'input')
    output_dir = os.path.join(base_dir, 'output')

    extractor = PDFOutlineExtractor()

    # Process all PDF files in input directory
    for filename in os.listdir(input_dir):
        if filename.lower().endswith('.pdf'):
            pdf_path = os.path.join(input_dir, filename)
            output_filename = filename.replace('.pdf', '.json')
            output_path = os.path.join(output_dir, output_filename)

            print(f"Processing {filename}")

            # Extract outline
            outline = extractor.extract_outline(pdf_path)

            # Save to JSON
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(outline, f, indent=2, ensure_ascii=False)

            print(f"Saved outline to {output_filename}")
            print(f"Found {len(outline['outline'])} headings")

            # Print first few headings as sample
            for i, heading in enumerate(outline['outline'][:5]):
                print(f"  {heading['level']}: {heading['text']} (page {heading['page']})")
            if len(outline['outline']) > 5:
                print(f"  ... and {len(outline['outline']) - 5} more headings")

if __name__ == "__main__":
    test_round1a_local()
