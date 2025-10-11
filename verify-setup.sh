#!/bin/bash

# Antelligence Setup Verification Script
# This script checks if all required components are properly configured

echo "🔍 Antelligence Setup Verification"
echo "=================================="
echo ""

# Check if .env file exists
echo "1. Checking .env file..."
if [ -f ".env" ]; then
    echo "   ✅ .env file found"
    
    # Check for required environment variables
    source .env 2>/dev/null
    
    if [ -z "$IO_SECRET_KEY" ]; then
        echo "   ⚠️  IO_SECRET_KEY not set"
    else
        echo "   ✅ IO_SECRET_KEY is set"
    fi
    
    if [ -z "$SEPOLIA_RPC_URL" ]; then
        echo "   ⚠️  SEPOLIA_RPC_URL not set"
    else
        echo "   ✅ SEPOLIA_RPC_URL is set"
    fi
    
    if [ -z "$PRIVATE_KEY" ]; then
        echo "   ⚠️  PRIVATE_KEY not set"
    else
        echo "   ✅ PRIVATE_KEY is set"
    fi
    
    if [ -z "$MEMORY_ADDR" ]; then
        echo "   ⚠️  MEMORY_ADDR not set (deploy contracts first)"
    else
        echo "   ✅ MEMORY_ADDR is set: $MEMORY_ADDR"
    fi
    
    if [ -z "$FOOD_ADDR" ]; then
        echo "   ⚠️  FOOD_ADDR not set (deploy contracts first)"
    else
        echo "   ✅ FOOD_ADDR is set: $FOOD_ADDR"
    fi
else
    echo "   ❌ .env file not found! Create one using .env.example as template"
fi

echo ""

# Check Python dependencies
echo "2. Checking Python dependencies..."
if command -v python3 &> /dev/null; then
    echo "   ✅ Python 3 is installed"
    
    # Check if virtual environment is active
    if [[ "$VIRTUAL_ENV" != "" ]]; then
        echo "   ✅ Virtual environment is active"
    else
        echo "   ⚠️  Virtual environment not active (recommended)"
    fi
    
    # Check key packages
    python3 -c "import fastapi" 2>/dev/null && echo "   ✅ fastapi installed" || echo "   ⚠️  fastapi not installed"
    python3 -c "import web3" 2>/dev/null && echo "   ✅ web3 installed" || echo "   ⚠️  web3 not installed"
    python3 -c "import google.generativeai" 2>/dev/null && echo "   ✅ google-generativeai installed" || echo "   ⚠️  google-generativeai not installed"
    python3 -c "import mistralai" 2>/dev/null && echo "   ✅ mistralai installed" || echo "   ⚠️  mistralai not installed"
else
    echo "   ❌ Python 3 not found"
fi

echo ""

# Check Node.js dependencies
echo "3. Checking Node.js dependencies..."
if command -v node &> /dev/null; then
    echo "   ✅ Node.js is installed ($(node --version))"
    
    if [ -d "blockchain/node_modules" ]; then
        echo "   ✅ Blockchain dependencies installed"
    else
        echo "   ⚠️  Blockchain dependencies not installed (run: cd blockchain && npm install)"
    fi
    
    if [ -d "frontend/node_modules" ]; then
        echo "   ✅ Frontend dependencies installed"
    else
        echo "   ⚠️  Frontend dependencies not installed (run: cd frontend && npm install)"
    fi
else
    echo "   ❌ Node.js not found"
fi

echo ""

# Check compiled contracts
echo "4. Checking smart contract compilation..."
if [ -d "blockchain/artifacts/contracts" ]; then
    echo "   ✅ Contracts compiled"
    if [ -f "blockchain/artifacts/contracts/ColonyMemory.sol/ColonyMemory.json" ]; then
        echo "   ✅ ColonyMemory artifact found"
    else
        echo "   ⚠️  ColonyMemory artifact not found"
    fi
    if [ -f "blockchain/artifacts/contracts/FoodToken.sol/FoodToken.json" ]; then
        echo "   ✅ FoodToken artifact found"
    else
        echo "   ⚠️  FoodToken artifact not found"
    fi
else
    echo "   ⚠️  Contracts not compiled (run: cd blockchain && npx hardhat compile)"
fi

echo ""

# Check frontend build
echo "5. Checking frontend build..."
if [ -d "frontend/dist" ]; then
    echo "   ✅ Frontend built"
else
    echo "   ⚠️  Frontend not built (run: cd frontend && npm run build)"
fi

echo ""

# Summary
echo "=================================="
echo "Setup Verification Complete!"
echo ""
echo "Next Steps:"
echo "1. If contracts not deployed: cd blockchain && npx hardhat run scripts/deploy.js --network sepolia"
echo "2. Update .env with contract addresses from deployment output"
echo "3. Start backend: cd backend && python -m uvicorn main:app --reload --port 8001"
echo "4. Start frontend: cd frontend && npm run dev"
echo "5. Open http://localhost:5173"
echo ""
echo "For production deployment, see IMPLEMENTATION_SUMMARY.md"
echo "=================================="

