#!/bin/bash

# Antelligence ECR Deployment - Exact Commands
echo "🚀 Deploying Antelligence to ECR with exact commands..."

# ECR Repository details
ECR_REPO="983240697534.dkr.ecr.us-east-1.amazonaws.com/antelligence"
REGION="us-east-1"

echo "📋 Configuration:"
echo "  ECR Repository: $ECR_REPO"
echo "  Region: $REGION"
echo "  Backend IP: 44.220.130.72"
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI is not installed. Please install AWS CLI first."
    exit 1
fi

# Build the Docker image first
echo "🔨 Building Docker image..."
docker build -t antelligence .

if [ $? -ne 0 ]; then
    echo "❌ Docker build failed!"
    exit 1
fi

echo "✅ Docker image built successfully!"

# Execute the exact commands you provided
echo "🔐 Logging into ECR..."
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 983240697534.dkr.ecr.us-east-1.amazonaws.com

if [ $? -ne 0 ]; then
    echo "❌ Failed to login to ECR. Please check your AWS credentials."
    exit 1
fi

echo "🏷️ Tagging image for ECR..."
docker tag antelligence:latest 983240697534.dkr.ecr.us-east-1.amazonaws.com/antelligence:latest

echo "📤 Pushing to ECR..."
docker push 983240697534.dkr.ecr.us-east-1.amazonaws.com/antelligence:latest

if [ $? -eq 0 ]; then
    echo "✅ Successfully pushed to ECR!"
    echo ""
    echo "🌐 Your image is now available at: $ECR_REPO:latest"
    echo ""
    echo "📋 To deploy on EC2 (44.220.130.72):"
    echo "1. SSH to your EC2 instance:"
    echo "   ssh -i your-key.pem ec2-user@44.220.130.72"
    echo ""
    echo "2. Pull and run the image:"
    echo "   aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 983240697534.dkr.ecr.us-east-1.amazonaws.com"
    echo "   docker pull $ECR_REPO:latest"
    echo "   docker run -d -p 8001:8001 $ECR_REPO:latest"
    echo ""
    echo "3. Or use docker-compose:"
    echo "   docker-compose -f docker-compose-ecr.yml up -d"
    echo ""
    echo "🌐 Frontend should connect to: http://44.220.130.72:8001"
    echo "❤️ Health check: http://44.220.130.72:8001/health"
else
    echo "❌ Failed to push to ECR!"
    exit 1
fi

echo "🎉 ECR deployment completed successfully!"
