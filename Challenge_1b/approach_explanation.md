# Adobe Hackathon Solution - Approach Explanation

## Round 1A: PDF Outline Extraction

### Methodology
Our approach combines multiple techniques to accurately extract document structure:

1. **Multi-layered Text Analysis**: Uses PyMuPDF to extract text with comprehensive formatting information including font sizes, styles, and positional data.

2. **Font-based Classification**: Implements adaptive font size thresholds that adjust based on document characteristics rather than fixed values, making it robust across different PDF styles.

3. **Pattern Recognition**: Employs regex patterns to identify common heading structures (numbered sections, lettered lists, chapter/section keywords) regardless of font formatting.

4. **Contextual Analysis**: Considers text positioning, spacing, and surrounding content to improve heading detection accuracy.

5. **Multilingual Support**: Handles various character sets and languages, including Japanese, with proper Unicode handling.

### Key Innovation
The system doesn't rely solely on font sizes but uses a scoring system that combines font attributes, text patterns, and document structure. This makes it resilient to PDFs with inconsistent formatting.

## Round 1B: Persona-Driven Document Intelligence

### Methodology
Our intelligent document analysis system uses semantic understanding to match content with user needs:

1. **Semantic Embedding**: Utilizes sentence-transformers (all-MiniLM-L6-v2) to create vector representations of both user requirements (persona + job) and document content.

2. **Hierarchical Section Detection**: Implements smart section boundary detection using structural cues, formatting patterns, and content analysis.

3. **Multi-factor Relevance Scoring**: Combines semantic similarity with content quality indicators (section length, keyword presence, structural importance) for accurate ranking.

4. **Granular Subsection Analysis**: Extracts and ranks paragraph-level content within top sections for detailed relevance mapping.

5. **Context-Aware Filtering**: Prioritizes substantial content blocks while filtering noise and irrelevant formatting artifacts.

### Scoring Strategy
- Base relevance: Cosine similarity between persona/job embeddings and section content
- Content quality boost: Longer, more substantial sections receive higher scores
- Structural importance: Key sections (Results, Methods, Conclusions) get priority
- Subsection refinement: Paragraph-level analysis for granular insights

This approach ensures that the most relevant and actionable content surfaces first, tailored specifically to the user's role and objectives.
