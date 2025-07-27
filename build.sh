#!/bin/bash

# Build script for Adobe Hackathon Solution

echo "Building Adobe Hackathon Solution..."

# Build the Docker image
docker build --platform linux/amd64 -t adobe-solution:v1 .

if [ $? -eq 0 ]; then
    echo "✓ Docker image built successfully!"
    echo ""
    echo "Usage instructions:"
    echo "For Round 1A (PDF outline extraction):"
    echo "docker run --rm -v \$(pwd)/input:/app/input:ro -v \$(pwd)/output:/app/output --network none adobe-solution:v1"
    echo ""
    echo "For Round 1B (persona-driven analysis):"
    echo "docker run --rm -v \$(pwd)/input:/app/input:ro -v \$(pwd)/output:/app/output --network none adobe-solution:v1 python round1b.py"
    echo ""
    echo "Make sure to place your PDF files in the 'input' directory before running."
else
    echo "✗ Docker build failed!"
    exit 1
fi
