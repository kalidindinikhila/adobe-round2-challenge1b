# Adobe India Hackathon 2025 - Document Intelligence Solution

## Overview
This solution tackles both **Round 1A** (PDF outline extraction) and **Round 1B** (persona-driven document intelligence) challenges for the Adobe India Hackathon 2025 "Connecting the Dots" competition.

## Quick Start

### Prerequisites
- Docker installed on your system
- Input PDF files in the `input/` directory
- Output directory will be created automatically

### Build and Run Commands

```bash
# 1. Build the Docker image (required for both rounds)
docker build --platform linux/amd64 -t adobe-hackathon-solution .

# 2a. Run Round 1A (PDF Outline Extraction) - DEFAULT BEHAVIOR
docker run --rm -v $(pwd)/input:/app/input:ro -v $(pwd)/output:/app/output --network none adobe-hackathon-solution

# 2b. Run Round 1B (Persona-Driven Intelligence) - OVERRIDE COMMAND  
docker run --rm -v $(pwd)/input:/app/input:ro -v $(pwd)/output:/app/output --network none adobe-hackathon-solution python round1b.py

# Alternative: Use entrypoint to specify the round
# For Round 1A:
docker run --rm -v $(pwd)/input:/app/input:ro -v $(pwd)/output:/app/output --network none adobe-hackathon-solution python round1a.py

# For Round 1B:
docker run --rm -v $(pwd)/input:/app/input:ro -v $(pwd)/output:/app/output --network none adobe-hackathon-solution python round1b.py
```

### Docker Command Breakdown
- `--rm`: Remove container after execution
- `-v $(pwd)/input:/app/input:ro`: Mount input directory as read-only
- `-v $(pwd)/output:/app/output`: Mount output directory for results
- `--network none`: No internet access (competition requirement)
- `python round1b.py`: Override default command for Round 1B

### Local Testing (Without Docker)
```bash
# Install dependencies
pip install -r requirements.txt

# Run Round 1A locally
python test_round1a_local.py

# Run Round 1B locally  
python test_round1b_local.py
```

## Project Structure
```
adobe-hackathon/
├── input/                          # Input PDF files
├── output/                         # Generated JSON outputs
├── round1a.py                      # Round 1A: PDF outline extraction
├── round1b.py                      # Round 1B: Persona-driven intelligence
├── test_round1a_local.py          # Local testing for Round 1A
├── test_round1b_local.py          # Local testing for Round 1B
├── requirements.txt               # Python dependencies
├── Dockerfile                     # Container configuration
├── challenge1b_input.json        # Round 1B input specification
└── README.md                     # This file
```

## Round 1A: PDF Outline Extraction

### Objective
Extract structured outlines (Title, H1, H2, H3 headings) from PDF documents with high accuracy.

### Technical Approach
- **PyMuPDF**: Robust PDF parsing and text extraction
- **Font Analysis**: Size-based heading detection with adaptive thresholds
- **Layout Analysis**: Position and spacing-based classification
- **Pattern Recognition**: Numbered/lettered section identification
- **Multi-language Support**: Handles various languages including Japanese

### Output Format
```json
{
  "title": "Document Title",
  "outline": [
    {
      "level": "H1|H2|H3",
      "text": "Heading text",
      "page": 1
    }
  ]
}
```

### Performance
- **Speed**: <10 seconds for 50-page PDF
- **Model Size**: <200MB (no ML models for Round 1A)
- **Accuracy**: Handles complex layouts and formatting inconsistencies

## Round 1B: Persona-Driven Document Intelligence

### Objective
Extract and rank document sections based on specific persona requirements and job tasks.

### Technical Approach
- **Sentence Transformers**: Semantic similarity analysis using all-MiniLM-L6-v2
- **Multi-stage Scoring**: Relevance ranking with multiple factors
- **Section Extraction**: Intelligent boundary detection and classification
- **Context Analysis**: Persona-aware content prioritization

### Input Format
```json
{
  "persona": {"role": "Travel Planner"},
  "job_to_be_done": {"task": "Plan a trip for college friends"},
  "documents": [{"filename": "guide.pdf", "title": "Travel Guide"}]
}
```

### Output Format
```json
{
  "metadata": {
    "input_documents": ["doc1.pdf"],
    "persona": "Travel Planner",
    "job_to_be_done": "Plan a trip...",
    "processing_timestamp": "2025-07-27T..."
  },
  "extracted_sections": [
    {
      "document": "doc1.pdf",
      "section_title": "Section Name",
      "importance_rank": 1,
      "page_number": 5
    }
  ],
  "subsection_analysis": [
    {
      "document": "doc1.pdf", 
      "refined_text": "Detailed content...",
      "page_number": 5
    }
  ]
}
```

### Performance
- **Model Size**: ~90MB (sentence-transformers)
- **Processing**: <60 seconds for multiple documents
- **Accuracy**: High semantic relevance matching

## Verification Instructions

### Quick Test with Provided Scripts
```bash
# Run complete build and test (recommended)
./build_and_test.sh

# Or validate existing outputs
./validate_outputs.sh
```

### Manual Testing Steps

#### 1. Prepare Test Environment
```bash
# Ensure input directory exists with PDF files
ls input/*.pdf

# Build the Docker image
docker build --platform linux/amd64 -t adobe-hackathon-solution .

# Verify image was built successfully
docker images | grep adobe-hackathon-solution
```

#### 2. Test Round 1A (PDF Outline Extraction)
```bash
# Run Round 1A (default behavior)
docker run --rm -v $(pwd)/input:/app/input:ro -v $(pwd)/output:/app/output --network none adobe-hackathon-solution

# Check outputs were generated
ls -la output/
echo "Round 1A generates: filename.json for each filename.pdf"

# Validate JSON format
for file in output/*.json; do
  if [[ "$file" != *"challenge1b_output.json"* ]]; then
    python -m json.tool "$file" > /dev/null && echo "Valid: $file" || echo "Invalid: $file"
  fi
done
```

#### 3. Test Round 1B (Persona-Driven Intelligence)
```bash
# Ensure Round 1B input file exists
ls challenge1b_input.json

# Run Round 1B (override command)
docker run --rm -v $(pwd)/input:/app/input:ro -v $(pwd)/output:/app/output --network none adobe-hackathon-solution python round1b.py

# Check Round 1B output
ls -la output/challenge1b_output.json
python -m json.tool output/challenge1b_output.json > /dev/null && echo "Round 1B JSON valid" || echo "Round 1B JSON invalid"
```

#### 4. Verify Output Formats
#### 4. Verify Output Formats
```bash
# Check Round 1A format (title + outline)
cat output/filename.json | jq '{title, outline: .outline[0:2]}'

# Check Round 1B format (metadata + sections + analysis)
cat output/challenge1b_output.json | jq '{metadata, section_count: (.extracted_sections | length), analysis_count: (.subsection_analysis | length)}'

# Validate all JSON files
python -c "
import json, glob
files = glob.glob('output/*.json')
valid = sum(1 for f in files if json.load(open(f, 'r')))
print(f'Valid JSON files: {valid}/{len(files)}')
"
```

### Expected Results

#### Round 1A Success Indicators:
- One JSON file per input PDF
- Each JSON contains `title` and `outline` fields
- Outline items have `level`, `text`, `page` fields
- Processing completes in <10 seconds per PDF

#### Round 1B Success Indicators:  
- Single `challenge1b_output.json` file generated
- Contains `metadata`, `extracted_sections`, `subsection_analysis`
- Sections ranked by importance (1-10)
- Processing completes in <60 seconds

## Docker Command Reference

### Single Command Execution
```bash
# Build once, use for both rounds
docker build --platform linux/amd64 -t adobe-hackathon-solution .

# Round 1A (default): Extract PDF outlines
docker run --rm -v $(pwd)/input:/app/input:ro -v $(pwd)/output:/app/output --network none adobe-hackathon-solution

# Round 1B (override): Persona-driven analysis  
docker run --rm -v $(pwd)/input:/app/input:ro -v $(pwd)/output:/app/output --network none adobe-hackathon-solution python round1b.py

# Alternative explicit commands
docker run --rm -v $(pwd)/input:/app/input:ro -v $(pwd)/output:/app/output --network none adobe-hackathon-solution python round1a.py
docker run --rm -v $(pwd)/input:/app/input:ro -v $(pwd)/output:/app/output --network none adobe-hackathon-solution python round1b.py
```

### Debugging and Development
```bash
# Interactive shell for debugging
docker run -it --rm -v $(pwd)/input:/app/input:ro -v $(pwd)/output:/app/output adobe-hackathon-solution /bin/bash

# Check container contents
docker run --rm adobe-hackathon-solution ls -la /app

# View logs during execution
docker run --rm -v $(pwd)/input:/app/input:ro -v $(pwd)/output:/app/output --network none adobe-hackathon-solution python round1a.py 2>&1 | tee execution.log
```

## Competition Compliance

### Adobe Hackathon Requirements
- **Platform**: linux/amd64 architecture
- **Network**: No internet access during runtime  
- **Performance**: Meets speed and resource constraints
- **Output Format**: Matches official schema requirements
- **Docker**: Fully containerized solution
- **Open Source**: Uses only open-source libraries

### Technical Stack
- **Python 3.10**: Runtime environment
- **PyMuPDF**: PDF processing and text extraction
- **sentence-transformers**: Semantic analysis for Round 1B
- **scikit-learn**: Machine learning utilities
- **Docker**: Containerization

## Model Dependencies
- **Round 1A**: No ML models (PyMuPDF only)
- **Round 1B**: sentence-transformers/all-MiniLM-L6-v2 (~90MB)
- **Total Size**: <200MB for Round 1A, <1GB for Round 1B
