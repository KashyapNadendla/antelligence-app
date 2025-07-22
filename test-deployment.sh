#!/bin/bash

# Test script for Antelligence deployment
echo "🧪 Testing Antelligence deployment..."

# Test health endpoint
echo "📊 Testing health endpoint..."
if curl -f http://18.219.29.154:8001/health &> /dev/null; then
    echo "✅ Health check passed!"
else
    echo "❌ Health check failed!"
    exit 1
fi

# Test main application
echo "🌐 Testing main application..."
if curl -f http://18.219.29.154:8001/ &> /dev/null; then
    echo "✅ Main application accessible!"
else
    echo "❌ Main application not accessible!"
    exit 1
fi

# Test API documentation
echo "📚 Testing API documentation..."
if curl -f http://18.219.29.154:8001/docs &> /dev/null; then
    echo "✅ API documentation accessible!"
else
    echo "❌ API documentation not accessible!"
    exit 1
fi

# Test static files
echo "📁 Testing static files..."
if curl -f http://18.219.29.154:8001/static/ &> /dev/null; then
    echo "✅ Static files accessible!"
else
    echo "❌ Static files not accessible!"
    exit 1
fi

echo "🎉 All tests passed! Deployment is working correctly."
echo ""
echo "🌐 Access your application at: http://18.219.29.154:8001"
echo "📊 API docs at: http://18.219.29.154:8001/docs" 