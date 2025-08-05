#!/bin/bash

# Build script for Azure Files Demo Django Application

set -e

# Configuration
IMAGE_NAME="azure-files-demo"
IMAGE_TAG="latest"
REGISTRY=${AZURE_CONTAINER_REGISTRY:-""}

echo "🏗️  Building Azure Files Demo Django Application"
echo "=========================================="

# Build the Docker image
echo "📦 Building Docker image..."
cd app
docker build -t ${IMAGE_NAME}:${IMAGE_TAG} .

if [ -n "$REGISTRY" ]; then
    echo "🏷️  Tagging image for registry: $REGISTRY"
    docker tag ${IMAGE_NAME}:${IMAGE_TAG} ${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}
    
    echo "📤 Pushing to registry..."
    docker push ${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}
    
    # Update deployment with registry image
    echo "🔄 Updating deployment with registry image..."
    cd ../k8s
    sed -i "s|image: azure-files-demo:latest|image: ${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}|g" deployment.yaml
else
    echo "ℹ️  No registry specified. Image will be available locally only."
    echo "   Set AZURE_CONTAINER_REGISTRY environment variable to push to a registry."
fi

echo "✅ Build completed successfully!"
echo ""
echo "🚀 To deploy:"
echo "   kubectl apply -k k8s/ -n <your-namespace>"
