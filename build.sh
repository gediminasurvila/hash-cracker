#!/bin/bash

# Hash Type Detector & Cracker - Docker Build Script

echo "Building Hash Type Detector & Cracker Docker image..."

# Build the Docker image
docker build -t hash-detector-cracker:latest .

if [ $? -eq 0 ]; then
    echo "✓ Docker image built successfully!"
    echo ""
    echo "To run the container:"
    echo "  docker run -p 5000:5000 hash-detector-cracker:latest"
    echo ""
    echo "Or use docker-compose:"
    echo "  docker-compose up"
    echo ""
    echo "To tag for DockerHub (replace 'yourusername'):"
    echo "  docker tag hash-detector-cracker:latest yourusername/hash-detector-cracker:latest"
    echo "  docker push yourusername/hash-detector-cracker:latest"
else
    echo "❌ Docker build failed!"
    exit 1
fi