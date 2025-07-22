#!/bin/bash

# Antelligence AWS ARM64 Deployment Script
# This script builds and deploys the application to AWS EC2

set -e

echo "🚀 Starting Antelligence deployment..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if docker-compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create logs directory if it doesn't exist
mkdir -p logs

# Build the Docker image
echo "🔨 Building Docker image..."
docker-compose build

# Check if build was successful
if [ $? -eq 0 ]; then
    echo "✅ Docker image built successfully!"
else
    echo "❌ Docker build failed!"
    exit 1
fi

# Start the application
echo "🚀 Starting Antelligence application..."
docker-compose up -d

# Wait for the application to be ready
echo "⏳ Waiting for application to be ready..."
sleep 10

# Check if the application is running
if curl -f http://localhost:8001/health &> /dev/null; then
    echo "✅ Application is running successfully!"
    echo "🌐 Access the application at: http://localhost:8001"
    echo "📊 API documentation at: http://localhost:8001/docs"
else
    echo "❌ Application failed to start properly."
    echo "📋 Checking logs..."
    docker-compose logs
    exit 1
fi

echo "🎉 Deployment completed successfully!"
echo ""
echo "📋 Useful commands:"
echo "  View logs: docker-compose logs -f"
echo "  Stop app: docker-compose down"
echo "  Restart app: docker-compose restart"
echo "  Update app: ./deploy.sh" 