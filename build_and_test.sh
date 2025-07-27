#!/bin/bash

# Adobe Hackathon - Build and Test Script
echo "🏗️  Adobe Hackathon Solution - Build and Test"
echo "============================================="

# Check if input directory exists
if [ ! -d "input" ]; then
    echo "❌ Error: input/ directory not found"
    echo "   Please create input/ directory and add PDF files"
    exit 1
fi

# Count PDF files
pdf_count=$(find input -name "*.pdf" | wc -l)
echo "📁 Found $pdf_count PDF files in input/ directory"

if [ $pdf_count -eq 0 ]; then
    echo "❌ Error: No PDF files found in input/ directory"
    echo "   Please add PDF files to test the solution"
    exit 1
fi

echo "🏗️  Building Docker image..."
docker build --platform linux/amd64 -t adobe-hackathon-solution . || {
    echo "❌ Docker build failed!"
    exit 1
}

echo "✅ Docker image built successfully!"

# Create output directory
mkdir -p output
echo "📁 Created output/ directory"

echo ""
echo "🧪 Testing Round 1A (PDF Outline Extraction)..."
echo "================================================"

# Run Round 1A
docker run --rm \
    -v $(pwd)/input:/app/input:ro \
    -v $(pwd)/output:/app/output \
    --network none \
    adobe-hackathon-solution || {
    echo "❌ Round 1A execution failed!"
    exit 1
}

# Check Round 1A outputs
echo "✅ Round 1A completed!"
echo "📊 Generated files:"
ls -la output/*.json 2>/dev/null | grep -v challenge1b_output.json || echo "   No Round 1A outputs found"

echo ""
echo "🧪 Testing Round 1B (Persona-Driven Intelligence)..."
echo "===================================================="

# Check if Round 1B input exists
if [ ! -f "challenge1b_input.json" ]; then
    echo "❌ Error: challenge1b_input.json not found"
    echo "   Round 1B test skipped"
else
    # Run Round 1B
    docker run --rm \
        -v $(pwd)/input:/app/input:ro \
        -v $(pwd)/output:/app/output \
        --network none \
        adobe-hackathon-solution python round1b.py || {
        echo "❌ Round 1B execution failed!"
        exit 1
    }
    
    echo "✅ Round 1B completed!"
    if [ -f "output/challenge1b_output.json" ]; then
        echo "📊 Round 1B output generated: challenge1b_output.json"
    fi
fi

echo ""
echo "🔍 Validation Results"
echo "===================="

# Validate JSON outputs
valid_count=0
total_count=0

for json_file in output/*.json; do
    if [ -f "$json_file" ]; then
        total_count=$((total_count + 1))
        if python -m json.tool "$json_file" > /dev/null 2>&1; then
            valid_count=$((valid_count + 1))
            echo "✅ $(basename "$json_file") - Valid JSON"
        else
            echo "❌ $(basename "$json_file") - Invalid JSON"
        fi
    fi
done

echo ""
echo "📊 Summary"
echo "=========="
echo "🏗️  Docker build: ✅ SUCCESS"
echo "🧪 Round 1A: ✅ SUCCESS"
echo "🧪 Round 1B: $([ -f "output/challenge1b_output.json" ] && echo "✅ SUCCESS" || echo "⚠️  SKIPPED")"
echo "📄 Valid JSON outputs: $valid_count/$total_count"
echo ""

if [ $valid_count -eq $total_count ] && [ $total_count -gt 0 ]; then
    echo "🎉 All tests passed! Solution ready for submission."
else
    echo "⚠️  Some issues detected. Please review the outputs."
fi

echo ""
echo "📋 Next Steps:"
echo "- Review generated JSON files in output/ directory"
echo "- Verify output format matches competition requirements"  
echo "- Submit your Docker image and repository"
