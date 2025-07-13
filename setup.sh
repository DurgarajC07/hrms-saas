#!/bin/bash

# HRMS Development Setup Script

echo "Setting up HRMS development environment..."

# Check if Python 3.11+ is installed
python_version=$(python3 --version 2>&1 | grep -o '[0-9]\+\.[0-9]\+')
if [[ $(echo "$python_version >= 3.11" | bc) -eq 0 ]]; then
    echo "Error: Python 3.11+ is required. Current version: $python_version"
    exit 1
fi

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Check if PostgreSQL is running
if ! pg_isready -q; then
    echo "Warning: PostgreSQL is not running. Please start PostgreSQL service."
    echo "On Ubuntu/Debian: sudo systemctl start postgresql"
    echo "On macOS with Homebrew: brew services start postgresql"
fi

# Check if Redis is running
if ! redis-cli ping > /dev/null 2>&1; then
    echo "Warning: Redis is not running. Please start Redis service."
    echo "On Ubuntu/Debian: sudo systemctl start redis"
    echo "On macOS with Homebrew: brew services start redis"
fi

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cp .env.example .env
    echo "Please edit .env file with your configuration before running the application."
fi

# Initialize database
echo "Setting up database..."
python setup.py

echo ""
echo "✅ Development setup complete!"
echo ""
echo "To start the development server:"
echo "1. Activate virtual environment: source venv/bin/activate"
echo "2. Start the server: uvicorn main:app --reload"
echo ""
echo "API Documentation will be available at:"
echo "- Swagger UI: http://localhost:8000/api/docs"
echo "- ReDoc: http://localhost:8000/api/redoc"
echo ""
echo "Default credentials:"
echo "- Super Admin: admin@hrms.com / SuperAdmin123!"
echo "- HR Manager: hr@techcorp.com / HRManager123!"
echo "- Employee: john.doe@techcorp.com / Employee123!"
