#!/bin/bash

# Antelligence EC2 Setup Script for 44.220.130.72
echo "🚀 Setting up Antelligence on EC2 instance 44.220.130.72..."

# Update system
echo "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install Docker
echo "🐳 Installing Docker..."
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
echo "📦 Installing Docker Compose..."
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Install curl for health checks
echo "📦 Installing curl..."
sudo apt install -y curl

# Create logs directory
echo "📁 Creating logs directory..."
mkdir -p logs

# Create .env file
echo "⚙️ Creating environment file..."
cat > .env << EOF
# API Configuration
IO_SECRET_KEY=your_actual_api_key_here

# Blockchain Configuration (optional)
CHAIN_RPC=http://127.0.0.1:8545
SEPOLIA_RPC_URL=https://sepolia.infura.io/v3/your_project_id
PRIVATE_KEY=your_private_key_here
FOOD_ADDR=your_food_contract_address
MEMORY_ADDR=your_memory_contract_address
EOF

echo "✅ Setup completed!"
echo ""
echo "📋 Next steps:"
echo "1. Edit .env file with your actual API key"
echo "2. Run: ./deploy.sh"
echo "3. Access your app at: http://44.220.130.72:8001"
echo ""
echo "🔧 To edit .env file:"
echo "   nano .env"
echo ""
echo "🚀 To deploy:"
echo "   ./deploy.sh" 