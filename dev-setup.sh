#!/bin/bash

# Development script for Azure Files Demo Django Application

set -e

echo "🚀 Azure Files Demo - Development Setup"
echo "====================================="

# Change to app directory
cd app

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Create data directory for local development
echo "📁 Creating local data directory..."
mkdir -p data

# Run migrations
echo "🗃️  Running database migrations..."
python manage.py migrate

# Collect static files
echo "🎨 Collecting static files..."
python manage.py collectstatic --noinput

echo "✅ Development setup complete!"
echo ""
echo "🏃 To start the development server:"
echo "   cd app && source venv/bin/activate && python manage.py runserver"
echo ""
echo "🌐 The application will be available at:"
echo "   http://localhost:8000"
echo ""
echo "📁 Files will be stored in:"
echo "   $(pwd)/data"
