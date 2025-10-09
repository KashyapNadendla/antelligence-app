# 🚀 Antelligence AWS ARM64 Deployment Guide

This guide will help you deploy the Antelligence application to an AWS EC2 ARM64 instance.

## 📋 Prerequisites

1. **AWS EC2 Instance** (ARM64/Graviton)
   - Recommended: `t4g.medium` or larger
   - Ubuntu 22.04 LTS or Amazon Linux 2023
   - At least 2GB RAM, 20GB storage

2. **Security Group Configuration**
   - Port 22 (SSH)
   - Port 8001 (Application)

## 🛠️ Installation Steps

### 1. Connect to your EC2 instance
```bash
ssh -i your-key.pem ubuntu@18.219.29.154
```

### 2. Install Docker and Docker Compose
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Logout and login again for group changes
exit
# SSH back in
```

### 3. Clone the repository
```bash
git clone https://github.com/your-username/antelligence-app.git
cd antelligence-app
```

### 4. Configure environment variables
```bash
# Create .env file for backend
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
```

### 5. Deploy the application
```bash
# Make deploy script executable
chmod +x deploy.sh

# Run deployment
./deploy.sh
```

## 🌐 Accessing the Application

Once deployed, you can access:

- **Main Application**: `http://18.219.29.154:8001`
- **API Documentation**: `http://18.219.29.154:8001/docs`
- **Health Check**: `http://18.219.29.154:8001/health`

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the root directory:

```env
# Required
IO_SECRET_KEY=your_io_api_key_here

# Optional - Blockchain Integration
CHAIN_RPC=http://127.0.0.1:8545
SEPOLIA_RPC_URL=https://sepolia.infura.io/v3/your_project_id
PRIVATE_KEY=your_private_key_here
FOOD_ADDR=your_food_contract_address
MEMORY_ADDR=your_memory_contract_address
```

### Frontend Configuration

The frontend automatically uses relative URLs, so it will work with any domain/IP.

## 📊 Monitoring

### View logs
```bash
docker-compose logs -f
```

### Check application status
```bash
docker-compose ps
```

### Health check
```bash
curl http://localhost:8001/health
```

## 🔄 Updates

To update the application:

1. Pull latest changes
```bash
git pull origin main
```

2. Rebuild and restart
```bash
./deploy.sh
```

## 🛑 Troubleshooting

### Application won't start
```bash
# Check logs
docker-compose logs

# Check if port is in use
sudo netstat -tlnp | grep 8001

# Restart Docker
sudo systemctl restart docker
```

### Frontend not loading
```bash
# Check if static files are built
docker exec -it antelligence-app-antelligence-1 ls -la /app/static

# Rebuild frontend
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Memory issues
```bash
# Check memory usage
docker stats

# Increase swap if needed
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

## 🔒 Security

### Firewall configuration
```bash
# Allow only necessary ports
sudo ufw allow 22
sudo ufw allow 8001
sudo ufw enable
```

### SSL/HTTPS (Optional)
For production, consider using a reverse proxy like Nginx with Let's Encrypt:

```bash
# Install Nginx
sudo apt install nginx

# Configure reverse proxy
sudo nano /etc/nginx/sites-available/antelligence
```

## 📈 Scaling

For higher traffic, consider:

1. **Load Balancer**: AWS Application Load Balancer
2. **Auto Scaling**: EC2 Auto Scaling Group
3. **Database**: RDS for persistent data
4. **Caching**: ElastiCache for Redis

## 🆘 Support

If you encounter issues:

1. Check the logs: `docker-compose logs -f`
2. Verify environment variables
3. Check system resources: `htop`, `df -h`
4. Restart the application: `docker-compose restart`

---

**Happy Deploying! 🐜✨** 