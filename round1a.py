#!/usr/bin/env python3
"""
Round 1A: PDF Outline Extraction
Extracts structured outline (Title, H1, H2, H3) from PDFs
"""

import fitz  # PyMuPDF
import json
import os
import re
from typing import List, Dict, Tuple, Optional
from collections import defaultdict
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PDFOutlineExtractor:
    def __init__(self):
        self.font_size_threshold = {
            'title': 18,
            'h1': 16,
            'h2': 14,
            'h3': 12
        }
        self.heading_patterns = [
            r'^(\d+\.?\d*\s+)',  # 1. 1.1 1.1.1
            r'^([A-Z]\.?\s+)',   # A. B. C.
            r'^([IVX]+\.?\s+)',  # I. II. III.
            r'^(Chapter\s+\d+)',  # Chapter 1
            r'^(Section\s+\d+)',  # Section 1
            r'^(CHAPTER\s+\d+)',  # CHAPTER 1
            r'^(Part\s+\d+)',     # Part 1
        ]
    
    def extract_text_with_formatting(self, pdf_path: str) -> List[Dict]:
        """Extract text with font information from PDF"""
        doc = fitz.open(pdf_path)
        pages_data = []
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            blocks = page.get_text("dict")
            
            page_content = {
                'page_number': page_num + 1,
                'text_blocks': []
            }
            
            for block in blocks.get("blocks", []):
                if "lines" in block:
                    for line in block["lines"]:
                        for span in line.get("spans", []):
                            text = span.get("text", "").strip()
                            if text:
                                page_content['text_blocks'].append({
                                    'text': text,
                                    'font_size': span.get("size", 0),
                                    'font_flags': span.get("flags", 0),
                                    'bbox': span.get("bbox", []),
                                    'font': span.get("font", "")
                                })
            
            pages_data.append(page_content)
        
        doc.close()
        return pages_data
    
    def is_bold(self, flags: int) -> bool:
        """Check if text is bold based on font flags"""
        return bool(flags & 16)  # Bold flag
    
    def is_heading_pattern(self, text: str) -> bool:
        """Check if text matches heading patterns"""
        for pattern in self.heading_patterns:
            if re.match(pattern, text.strip()):
                return True
        return False
    
    def extract_title(self, pages_data: List[Dict]) -> str:
        """Extract document title from first page"""
        if not pages_data:
            return "Untitled Document"
        
        first_page = pages_data[0]
        max_font_size = 0
        title_candidates = []
        
        # Find text with largest font size in first page
        for block in first_page['text_blocks']:
            font_size = block['font_size']
            text = block['text'].strip()
            
            if font_size > max_font_size and len(text) > 3:
                max_font_size = font_size
                title_candidates = [text]
            elif font_size == max_font_size and len(text) > 3:
                title_candidates.append(text)
        
        if title_candidates:
            # Return the longest title candidate
            return max(title_candidates, key=len)
        
        return "Untitled Document"
    
    def classify_heading_level(self, block: Dict, avg_font_size: float) -> Optional[str]:
        """Classify text block as heading level"""
        font_size = block['font_size']
        text = block['text'].strip()
        is_bold = self.is_bold(block['font_flags'])
        
        # Skip very short text or numbers only
        if len(text) < 2 or text.isdigit():
            return None
        
        # Font size based classification
        if font_size >= self.font_size_threshold['title']:
            return 'H1'
        elif font_size >= self.font_size_threshold['h1']:
            return 'H1'
        elif font_size >= self.font_size_threshold['h2']:
            return 'H2'
        elif font_size >= self.font_size_threshold['h3']:
            return 'H3'
        
        # Pattern and formatting based classification
        if self.is_heading_pattern(text):
            if is_bold or font_size > avg_font_size * 1.2:
                return 'H1'
            elif font_size > avg_font_size * 1.1:
                return 'H2'
            else:
                return 'H3'
        
        # Bold text that's larger than average
        if is_bold and font_size > avg_font_size * 1.1:
            if font_size > avg_font_size * 1.3:
                return 'H1'
            elif font_size > avg_font_size * 1.2:
                return 'H2'
            else:
                return 'H3'
        
        return None
    
    def calculate_average_font_size(self, pages_data: List[Dict]) -> float:
        """Calculate average font size across document"""
        font_sizes = []
        
        for page in pages_data:
            for block in page['text_blocks']:
                font_sizes.append(block['font_size'])
        
        return sum(font_sizes) / len(font_sizes) if font_sizes else 12
    
    def extract_headings(self, pages_data: List[Dict]) -> List[Dict]:
        """Extract headings from PDF pages"""
        headings = []
        avg_font_size = self.calculate_average_font_size(pages_data)
        
        allowed_headings = [
            "Revision History", "Table of Contents", "Acknowledgements", "References",
            "Syllabus", "Business Outcomes", "Content", "Trademarks", "Documents and Web Sites"
        ]
        for page in pages_data:
            for block in page['text_blocks']:
                level = self.classify_heading_level(block, avg_font_size)
                if level:
                    text = block['text'].strip()
                    text = re.sub(r'\s+', ' ', text)  # Normalize whitespace
                    is_numbered = bool(re.match(r'^[0-9]+\.[ ]', text))
                    is_allowed = any(text.startswith(h) for h in allowed_headings)
                    if is_numbered or is_allowed:
                        headings.append({
                            'level': level,
                            'text': text,
                            'page': page['page_number']
                        })
        return self.filter_duplicate_headings(headings)
    
    def filter_duplicate_headings(self, headings: List[Dict]) -> List[Dict]:
        """Remove duplicate headings"""
        seen = set()
        filtered = []
        
        for heading in headings:
            key = (heading['text'].lower(), heading['level'])
            if key not in seen:
                seen.add(key)
                filtered.append(heading)
        
        return filtered
    
    def extract_outline(self, pdf_path: str) -> Dict:
        """Main method to extract outline from PDF"""
        try:
            logger.info(f"Processing PDF: {pdf_path}")
            
            # Extract text with formatting
            pages_data = self.extract_text_with_formatting(pdf_path)
            
            if not pages_data:
                return {"title": "Empty Document", "outline": []}
            
            # Extract title and headings
            title = self.extract_title(pages_data)
            headings = self.extract_headings(pages_data)
            
            # Sort headings by page number
            headings.sort(key=lambda x: x['page'])
            
            result = {
                "title": title,
                "outline": headings
            }
            
            logger.info(f"Extracted {len(headings)} headings from {len(pages_data)} pages")
            return result
            
        except Exception as e:
            logger.error(f"Error processing PDF {pdf_path}: {str(e)}")
            return {"title": "Error Processing Document", "outline": []}

def process_pdfs():
    """Process all PDFs in input directory"""
    input_dir = "/app/input"
    output_dir = "/app/output"
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    extractor = PDFOutlineExtractor()
    
    # Process all PDF files in input directory
    for filename in os.listdir(input_dir):
        if filename.lower().endswith('.pdf'):
            pdf_path = os.path.join(input_dir, filename)
            output_filename = filename.replace('.pdf', '.json')
            output_path = os.path.join(output_dir, output_filename)
            
            logger.info(f"Processing {filename}")
            
            # Extract outline
            outline = extractor.extract_outline(pdf_path)
            
            # Save to JSON
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(outline, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved outline to {output_filename}")

if __name__ == "__main__":
    process_pdfs()
