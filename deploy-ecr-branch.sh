#!/bin/bash

# Antelligence AWS ECR Deployment Script for Branch-specific deployments
echo "🚀 Starting Antelligence ECR deployment for branch: ${BRANCH_NAME:-main}..."

# ECR Repository details - Update these for your new branch/account
ECR_ACCOUNT_ID="983240697534"
ECR_REGION="us-east-1"
ECR_REPO_NAME="antelligence"
BRANCH_NAME=${BRANCH_NAME:-main}

# Construct full ECR repository URL
ECR_REPO="${ECR_ACCOUNT_ID}.dkr.ecr.${ECR_REGION}.amazonaws.com/${ECR_REPO_NAME}"

echo "📋 Deployment Configuration:"
echo "  ECR Repository: $ECR_REPO"
echo "  Region: $ECR_REGION"
echo "  Branch: $BRANCH_NAME"
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

# Login to ECR
echo "🔐 Logging into ECR..."
aws ecr get-login-password --region $ECR_REGION | docker login --username AWS --password-stdin $ECR_REPO

if [ $? -ne 0 ]; then
    echo "❌ Failed to login to ECR. Please check your AWS credentials."
    echo "💡 Make sure you have AWS CLI configured with: aws configure"
    exit 1
fi

# Build the Docker image
echo "🔨 Building Docker image..."
docker build -t antelligence .

if [ $? -eq 0 ]; then
    echo "✅ Docker image built successfully!"
else
    echo "❌ Docker build failed!"
    exit 1
fi

# Tag the image for ECR with branch name
echo "🏷️ Tagging image for ECR..."
docker tag antelligence:latest $ECR_REPO:latest
docker tag antelligence:latest $ECR_REPO:$BRANCH_NAME

# Push to ECR
echo "📤 Pushing to ECR..."
docker push $ECR_REPO:latest
docker push $ECR_REPO:$BRANCH_NAME

if [ $? -eq 0 ]; then
    echo "✅ Successfully pushed to ECR!"
    echo ""
    echo "🌐 Your images are now available at:"
    echo "  - $ECR_REPO:latest"
    echo "  - $ECR_REPO:$BRANCH_NAME"
    echo ""
    echo "📋 To deploy on EC2 (44.220.130.72):"
    echo "1. SSH to your EC2 instance: ssh -i your-key.pem ec2-user@44.220.130.72"
    echo "2. Run: docker pull $ECR_REPO:latest"
    echo "3. Run: docker run -p 8001:8001 $ECR_REPO:latest"
    echo ""
    echo "🔧 Or use docker-compose with ECR image:"
    echo "   docker-compose -f docker-compose-ecr.yml up -d"
    echo ""
    echo "🌐 Frontend should connect to: http://44.220.130.72:8001"
else
    echo "❌ Failed to push to ECR!"
    exit 1
fi

echo "🎉 ECR deployment completed successfully!"
echo ""
echo "🔧 Configuration Summary:"
echo "  Backend URL: http://44.220.130.72:8001"
echo "  ECR Repository: $ECR_REPO"
echo "  Health Check: http://44.220.130.72:8001/health"
