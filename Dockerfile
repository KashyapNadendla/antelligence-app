# Multi-stage Dockerfile for ARM64 deployment

# Stage 1: Frontend build
FROM node:18-alpine AS frontend-builder

# Set working directory
WORKDIR /app/frontend

# Copy frontend package files
COPY frontend/package*.json ./
COPY frontend/bun.lockb ./

# Install dependencies
RUN npm install

# Copy frontend source code
COPY frontend/ ./

# Build frontend to static files
RUN npm run build

# Stage 2: Backend with frontend static files
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies for ARM64
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements
COPY backend/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source code
COPY backend/ ./backend/

# Copy blockchain client folder (make sure this folder exists before building)
COPY blockchain/ ./blockchain/

# Copy built frontend static files from stage 1
COPY --from=frontend-builder /app/frontend/dist ./static

# Create .env file for backend (can be overridden at runtime)
RUN echo "# Backend Environment Configuration\n\
# API Configuration\n\
IO_SECRET_KEY=your_api_key_here\n\
\n\
# Blockchain Configuration (optional)\n\
CHAIN_RPC=http://127.0.0.1:8545\n\
SEPOLIA_RPC_URL=https://sepolia.infura.io/v3/your_project_id\n\
PRIVATE_KEY=your_private_key_here\n\
FOOD_ADDR=your_food_contract_address\n\
MEMORY_ADDR=your_memory_contract_address" > .env

# Set Python path to include /app so imports work for backend and simulation
ENV PYTHONPATH=/app

# Expose port
EXPOSE 8001

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8001/health || exit 1

# Start the application
CMD ["python", "-m", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8001"]