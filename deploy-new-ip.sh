#!/bin/bash

# Antelligence Deployment Script for New IP: 44.220.130.72
echo "🚀 Deploying Antelligence to new IP: 44.220.130.72"

# Configuration
BACKEND_IP="44.220.130.72"
BACKEND_PORT="8001"
ECR_REPO="983240697534.dkr.ecr.us-east-1.amazonaws.com/antelligence"

echo "📋 Deployment Configuration:"
echo "  Backend IP: $BACKEND_IP"
echo "  Backend Port: $BACKEND_PORT"
echo "  ECR Repository: $ECR_REPO"
echo ""

# Check if we're deploying locally or to EC2
if [ "$1" = "local" ]; then
    echo "🏠 Deploying locally..."
    
    # Build and run locally
    echo "🔨 Building Docker image..."
    docker build -t antelligence .
    
    echo "🚀 Starting application locally..."
    docker run -d -p $BACKEND_PORT:$BACKEND_PORT \
        -e IO_SECRET_KEY="${IO_SECRET_KEY:-your_api_key_here}" \
        -e CHAIN_RPC="${CHAIN_RPC:-http://127.0.0.1:8545}" \
        -e SEPOLIA_RPC_URL="${SEPOLIA_RPC_URL:-}" \
        -e PRIVATE_KEY="${PRIVATE_KEY:-}" \
        -e FOOD_ADDR="${FOOD_ADDR:-}" \
        -e MEMORY_ADDR="${MEMORY_ADDR:-}" \
        --name antelligence-app \
        antelligence:latest
    
    echo "✅ Application started locally!"
    echo "🌐 Access at: http://localhost:$BACKEND_PORT"
    echo "📊 API docs at: http://localhost:$BACKEND_PORT/docs"
    
elif [ "$1" = "ecr" ]; then
    echo "☁️ Deploying via ECR..."
    
    # Use the ECR deployment script
    BRANCH_NAME=${2:-main}
    echo "📤 Deploying branch: $BRANCH_NAME"
    BRANCH_NAME=$BRANCH_NAME ./deploy-ecr-branch.sh
    
else
    echo "📋 Usage:"
    echo "  Local deployment:  ./deploy-new-ip.sh local"
    echo "  ECR deployment:    ./deploy-new-ip.sh ecr [branch-name]"
    echo ""
    echo "🔧 For EC2 deployment:"
    echo "1. SSH to your EC2 instance:"
    echo "   ssh -i your-key.pem ec2-user@$BACKEND_IP"
    echo ""
    echo "2. Pull and run the latest image:"
    echo "   docker pull $ECR_REPO:latest"
    echo "   docker run -d -p $BACKEND_PORT:$BACKEND_PORT $ECR_REPO:latest"
    echo ""
    echo "3. Or use docker-compose:"
    echo "   docker-compose -f docker-compose-ecr.yml up -d"
    echo ""
    echo "🌐 Frontend configuration:"
    echo "  Update VITE_API_BASE_URL to: http://$BACKEND_IP:$BACKEND_PORT"
fi

echo ""
echo "🎉 Deployment script completed!"
echo "🔗 Backend URL: http://$BACKEND_IP:$BACKEND_PORT"
echo "❤️ Health check: http://$BACKEND_IP:$BACKEND_PORT/health"
