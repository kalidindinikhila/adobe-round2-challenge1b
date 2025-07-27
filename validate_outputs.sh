#!/bin/bash

# Quick validation script for Adobe Hackathon outputs
echo "🔍 Adobe Hackathon - Output Validation"
echo "======================================"

if [ ! -d "output" ]; then
    echo "❌ Error: output/ directory not found"
    echo "   Run the solution first to generate outputs"
    exit 1
fi

echo "📁 Checking output directory..."
output_count=$(find output -name "*.json" | wc -l)
echo "   Found $output_count JSON files"

if [ $output_count -eq 0 ]; then
    echo "❌ No JSON outputs found"
    exit 1
fi

echo ""
echo "🧪 Validating JSON files..."
valid=0
invalid=0

for json_file in output/*.json; do
    if [ -f "$json_file" ]; then
        filename=$(basename "$json_file")
        if python -c "import json; json.load(open('$json_file'))" 2>/dev/null; then
            echo "✅ $filename - Valid JSON"
            valid=$((valid + 1))
        else
            echo "❌ $filename - Invalid JSON"
            invalid=$((invalid + 1))
        fi
    fi
done

echo ""
echo "📊 JSON Validation Summary:"
echo "   ✅ Valid: $valid"
echo "   ❌ Invalid: $invalid"

# Check Round 1A format
echo ""
echo "🔍 Round 1A Format Check..."
round1a_files=$(find output -name "*.json" -not -name "challenge1b_output.json" | head -1)
if [ -n "$round1a_files" ]; then
    has_title=$(python -c "import json; data=json.load(open('$round1a_files')); print('title' in data)" 2>/dev/null)
    has_outline=$(python -c "import json; data=json.load(open('$round1a_files')); print('outline' in data)" 2>/dev/null)
    
    if [ "$has_title" = "True" ] && [ "$has_outline" = "True" ]; then
        echo "✅ Round 1A format correct (title, outline)"
    else
        echo "❌ Round 1A format incorrect"
    fi
else
    echo "⚠️  No Round 1A outputs found"
fi

# Check Round 1B format  
echo ""
echo "🔍 Round 1B Format Check..."
if [ -f "output/challenge1b_output.json" ]; then
    has_metadata=$(python -c "import json; data=json.load(open('output/challenge1b_output.json')); print('metadata' in data)" 2>/dev/null)
    has_sections=$(python -c "import json; data=json.load(open('output/challenge1b_output.json')); print('extracted_sections' in data)" 2>/dev/null)
    has_analysis=$(python -c "import json; data=json.load(open('output/challenge1b_output.json')); print('subsection_analysis' in data)" 2>/dev/null)
    
    if [ "$has_metadata" = "True" ] && [ "$has_sections" = "True" ] && [ "$has_analysis" = "True" ]; then
        echo "✅ Round 1B format correct (metadata, extracted_sections, subsection_analysis)"
    else
        echo "❌ Round 1B format incorrect"
    fi
else
    echo "⚠️  No Round 1B output found"
fi

echo ""
if [ $invalid -eq 0 ]; then
    echo "🎉 All validations passed!"
else
    echo "⚠️  Some validation issues found"
fi
