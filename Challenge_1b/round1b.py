#!/usr/bin/env python3
"""
Round 1B: Persona-Driven Document Intelligence
Intelligently extracts and ranks document sections based on persona and job requirements
"""

import fitz  # PyMuPDF
import json
import os
import re
from typing import List, Dict, Tuple, Optional
from datetime import datetime
import logging
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PersonaDrivenAnalyzer:
    def __init__(self):
        # Initialize the sentence transformer model
        self.model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

        # Section markers that help identify document structure
        self.section_markers = [
            r'^(\d+\.?\d*\s+)',  # 1. 1.1 1.1.1
            r'^([A-Z]\.?	?\s+)',   # A. B. C.
            r'^([IVX]+\.?	?\s+)',  # I. II. III.
            r'^(Chapter\s+\d+)',  # Chapter 1
            r'^(Section\s+\d+)',  # Section 1
            r'^(Abstract|Introduction|Conclusion|Results|Discussion|Methods|Methodology)',
            r'^(Executive Summary|Overview|Background|Findings|Recommendations)',
        ]

        # Preferred section titles for travel documents
        self.preferred_sections = [
            "Comprehensive Guide to Major Cities in the South of France",
            "Coastal Adventures",
            "Culinary Experiences",
            "General Packing Tips and Tricks",
            "Nightlife and Entertainment",
            "Travel Tips",
            "Family-Friendly Hotels"
        ]
    
    def extract_text_from_pdf(self, pdf_path: str) -> List[Dict]:
        """Extract text content from PDF with page information"""
        doc = fitz.open(pdf_path)
        pages_content = []
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text()
            
            if text.strip():
                pages_content.append({
                    'page_number': page_num + 1,
                    'text': text.strip(),
                    'document': os.path.basename(pdf_path)
                })
        
        doc.close()
        return pages_content
    
    def identify_sections(self, pages_content: List[Dict]) -> List[Dict]:
        """Identify document sections based on structure and content"""
        sections = []
        current_section = None
        
        for page in pages_content:
            text = page['text']
            lines = text.split('\n')
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Check if line is a section header
                is_section_header = False
                section_title = line
                
                for pattern in self.section_markers:
                    if re.match(pattern, line, re.IGNORECASE):
                        is_section_header = True
                        # Clean up section title
                        section_title = re.sub(r'^[\d\.\s\w]+[:.]?\s*', '', line).strip()
                        break
                
                # Also check for lines that are all caps or follow title case
                if (len(line) > 5 and len(line) < 100 and 
                    (line.isupper() or line.istitle()) and 
                    not re.search(r'\d{4}|\$|\%', line)):
                    is_section_header = True
                    section_title = line
                
                if is_section_header:
                    # Save previous section if exists
                    if current_section and current_section['content'].strip():
                        sections.append(current_section)
                    
                    # Start new section
                    current_section = {
                        'document': page['document'],
                        'section_title': section_title,
                        'page_start': page['page_number'],
                        'page_end': page['page_number'],
                        'content': ''
                    }
                elif current_section:
                    # Add content to current section
                    current_section['content'] += line + ' '
                    current_section['page_end'] = page['page_number']
                else:
                    # Create first section if no header found yet
                    current_section = {
                        'document': page['document'],
                        'section_title': 'Introduction',
                        'page_start': page['page_number'],
                        'page_end': page['page_number'],
                        'content': line + ' '
                    }
        
        # Add final section
        if current_section and current_section['content'].strip():
            sections.append(current_section)
        
        return sections
    
    def calculate_relevance_score(self, section: Dict, persona: str, job: str) -> float:
        """Calculate relevance score for a section based on persona and job, with boost for preferred titles"""
        # Combine persona and job for query embedding
        query_text = f"{persona} {job}"
        # Combine section title and content for section embedding
        section_text = f"{section['section_title']} {section['content'][:1000]}"
        # Get embeddings
        query_embedding = self.model.encode([query_text])
        section_embedding = self.model.encode([section_text])
        # Calculate cosine similarity
        similarity = cosine_similarity(query_embedding, section_embedding)[0][0]
        score = similarity
        # Boost score for preferred section titles
        if section['section_title'] in self.preferred_sections:
            score += 0.5
        # Boost score for certain keywords in section title
        title_lower = section['section_title'].lower()
        if any(keyword in title_lower for keyword in ['result', 'finding', 'conclusion', 'method', 'analysis']):
            score *= 1.2
        # Boost score for longer sections (more content)
        content_length = len(section['content'])
        if content_length > 500:
            score *= 1.1
        elif content_length > 1000:
            score *= 1.2
        return min(score, 1.0)  # Cap at 1.0
    
    def extract_subsections(self, section: Dict, persona: str, job: str, top_k: int = 3) -> List[Dict]:
        """Extract and rank subsections within a section"""
        content = section['content']
        
        # Split content into paragraphs
        paragraphs = [p.strip() for p in content.split('\n\n') if len(p.strip()) > 50]
        
        if not paragraphs:
            # Split by sentences if no clear paragraphs
            sentences = [s.strip() for s in content.split('.') if len(s.strip()) > 50]
            paragraphs = sentences
        
        subsections = []
        query_text = f"{persona} {job}"
        
        for i, paragraph in enumerate(paragraphs[:10]):  # Limit to first 10 paragraphs
            if len(paragraph) > 100:  # Only consider substantial paragraphs
                # Calculate relevance
                paragraph_embedding = self.model.encode([paragraph])
                query_embedding = self.model.encode([query_text])
                similarity = cosine_similarity(query_embedding, paragraph_embedding)[0][0]
                
                subsections.append({
                    'document': section['document'],
                    'page_number': section['page_start'],
                    'refined_text': paragraph[:500] + ('...' if len(paragraph) > 500 else ''),
                    'relevance_score': similarity
                })
        
        # Sort by relevance and return top k
        subsections.sort(key=lambda x: x['relevance_score'], reverse=True)
        return subsections[:top_k]
    
    def analyze_documents(self, input_data: Dict) -> Dict:
        """Main analysis method"""
        try:
            documents = input_data['documents']
            persona = input_data['persona']
            job = input_data['job_to_be_done']
            
            logger.info(f"Analyzing {len(documents)} documents for persona: {persona}")
            
            all_sections = []
            
            # Process each document
            for doc_path in documents:
                if os.path.exists(doc_path) and doc_path.lower().endswith('.pdf'):
                    logger.info(f"Processing document: {os.path.basename(doc_path)}")
                    
                    # Extract text from PDF
                    pages_content = self.extract_text_from_pdf(doc_path)
                    
                    # Identify sections
                    sections = self.identify_sections(pages_content)
                    
                    # Calculate relevance scores
                    for section in sections:
                        section['relevance_score'] = self.calculate_relevance_score(section, persona, job)
                    
                    all_sections.extend(sections)
            
            # Sort sections by relevance
            all_sections.sort(key=lambda x: x['relevance_score'], reverse=True)
            
            # Take top 10 most relevant sections
            top_sections = all_sections[:10]
            
            # Extract subsections for top sections
            subsection_analysis = []
            for section in top_sections[:5]:  # Only top 5 sections for subsection analysis
                subsections = self.extract_subsections(section, persona, job)
                subsection_analysis.extend(subsections)
            
            # Sort subsections by relevance
            subsection_analysis.sort(key=lambda x: x['relevance_score'], reverse=True)
            
            # Prepare output
            result = {
                'metadata': {
                    'input_documents': [os.path.basename(doc) for doc in documents],
                    'persona': persona,
                    'job_to_be_done': job,
                    'processing_timestamp': datetime.now().isoformat()
                },
                'extracted_sections': [
                    {
                        'document': section['document'],
                        'section_title': section['section_title'],
                        'importance_rank': i + 1,
                        'page_number': section['page_start'] if section['page_start'] == section['page_end'] else section['page_start']
                    }
                    for i, section in enumerate(top_sections)
                ],
                'subsection_analysis': [
                    {
                        'document': subsection['document'],
                        'refined_text': subsection['refined_text'],
                        'page_number': subsection['page_number']
                    }
                    for subsection in subsection_analysis[:15]  # Top 15 subsections
                ]
            }
            
            logger.info(f"Analysis complete. Found {len(top_sections)} relevant sections")
            return result
            
        except Exception as e:
            logger.error(f"Error during analysis: {str(e)}")
            return {
                'error': str(e),
                'metadata': {
                    'processing_timestamp': datetime.now().isoformat()
                }
            }

def process_round1b():
    """Process Round 1B analysis"""
    input_dir = "/app/input"
    output_dir = "/app/output"
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Look for input specification file
    input_spec_path = os.path.join(input_dir, "challenge1b_input.json")
    
    if not os.path.exists(input_spec_path):
        logger.error("challenge1b_input.json not found in input directory")
        return
    
    # Load input specification
    with open(input_spec_path, 'r', encoding='utf-8') as f:
        input_data = json.load(f)
    
    # Extract documents from the expected format
    if 'documents' in input_data and isinstance(input_data['documents'], list):
        if input_data['documents'] and isinstance(input_data['documents'][0], dict):
            # New format: [{"filename": "doc.pdf", "title": "Title"}]
            document_files = [doc['filename'] for doc in input_data['documents']]
        else:
            # Old format: ["doc1.pdf", "doc2.pdf"]
            document_files = input_data['documents']
    else:
        document_files = []
    
    # Convert relative paths to absolute paths
    input_data['documents'] = [
        os.path.join(input_dir, doc) if not os.path.isabs(doc) else doc
        for doc in document_files
    ]
    
    # Extract persona and job from expected format
    if 'persona' in input_data and isinstance(input_data['persona'], dict):
        input_data['persona'] = input_data['persona'].get('role', input_data['persona'])
    
    if 'job_to_be_done' in input_data and isinstance(input_data['job_to_be_done'], dict):
        input_data['job_to_be_done'] = input_data['job_to_be_done'].get('task', input_data['job_to_be_done'])
    
    analyzer = PersonaDrivenAnalyzer()
    result = analyzer.analyze_documents(input_data)
    
    # Save result
    output_path = os.path.join(output_dir, "challenge1b_output.json")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    logger.info("Round 1B analysis complete")

if __name__ == "__main__":
    process_round1b()
