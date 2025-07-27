#!/usr/bin/env python3
"""
Test Round 1B locally
"""


import sys
import os
# Ensure the current directory is in sys.path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from round1b import PersonaDrivenAnalyzer
import json

def test_round1b_local():
    """Test Round 1B locally"""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    input_dir = os.path.join(base_dir, 'input')
    output_dir = os.path.join(base_dir, 'output')
    
    # Look for input specification file
    input_spec_path = os.path.join(input_dir, "challenge1b_input.json")
    
    if not os.path.exists(input_spec_path):
        print("challenge1b_input.json not found in input directory")
        return
    
    # Load input specification
    with open(input_spec_path, 'r', encoding='utf-8') as f:
        input_data = json.load(f)
    
    print("Input data loaded:")
    print(json.dumps(input_data, indent=2))
    
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
    
    print(f"\nProcessing {len(input_data['documents'])} documents...")
    print(f"Persona: {input_data['persona']}")
    print(f"Job: {input_data['job_to_be_done'][:100]}...")
    
    # Check which files actually exist
    existing_docs = []
    for doc_path in input_data['documents']:
        if os.path.exists(doc_path):
            existing_docs.append(doc_path)
            print(f"✓ Found: {os.path.basename(doc_path)}")
        else:
            print(f"✗ Missing: {os.path.basename(doc_path)}")
    
    input_data['documents'] = existing_docs
    
    if not existing_docs:
        print("No documents found! Exiting.")
        return
    
    analyzer = PersonaDrivenAnalyzer()
    result = analyzer.analyze_documents(input_data)
    
    # Save result
    output_path = os.path.join(output_dir, "challenge1b_output.json")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"\nAnalysis complete!")
    print(f"Found {len(result.get('extracted_sections', []))} relevant sections")
    print(f"Generated {len(result.get('subsection_analysis', []))} subsection analyses")
    
    # Show top sections
    print("\nTop 3 most relevant sections:")
    for i, section in enumerate(result.get('extracted_sections', [])[:3]):
        print(f"{i+1}. {section['section_title']} (page {section['page_number']}) - {section['document']}")

if __name__ == "__main__":
    test_round1b_local()
