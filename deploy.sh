#!/bin/bash

# Hash Type Detector & Cracker - DockerHub Deployment Script

if [ -z "$1" ]; then
    echo "Usage: ./deploy.sh <dockerhub-username>"
    echo "Example: ./deploy.sh myusername"
    exit 1
fi

DOCKERHUB_USERNAME=$1
IMAGE_NAME="hash-detector-cracker"
TAG="latest"

echo "Deploying to DockerHub as ${DOCKERHUB_USERNAME}/${IMAGE_NAME}:${TAG}"

# Build the image
echo "Building Docker image..."
docker build -t ${IMAGE_NAME}:${TAG} .

if [ $? -ne 0 ]; then
    echo "❌ Docker build failed!"
    exit 1
fi

# Tag for DockerHub
echo "Tagging image for DockerHub..."
docker tag ${IMAGE_NAME}:${TAG} ${DOCKERHUB_USERNAME}/${IMAGE_NAME}:${TAG}

# Push to DockerHub
echo "Pushing to DockerHub..."
docker push ${DOCKERHUB_USERNAME}/${IMAGE_NAME}:${TAG}

if [ $? -eq 0 ]; then
    echo "✓ Successfully deployed to DockerHub!"
    echo ""
    echo "Your image is now available at:"
    echo "  docker pull ${DOCKERHUB_USERNAME}/${IMAGE_NAME}:${TAG}"
    echo ""
    echo "To run from DockerHub:"
    echo "  docker run -p 5000:5000 ${DOCKERHUB_USERNAME}/${IMAGE_NAME}:${TAG}"
else
    echo "❌ DockerHub push failed!"
    echo "Make sure you're logged in: docker login"
    exit 1
fi