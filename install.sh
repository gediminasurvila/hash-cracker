#!/bin/bash

echo "Hash Type Detector & Cracker - Installation Script"
echo "=================================================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.7 or higher."
    exit 1
fi

echo "✓ Python 3 found"

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Check if John the Ripper is installed
echo "Checking for John the Ripper..."
if command -v john &> /dev/null; then
    echo "✓ John the Ripper found"
    john --help | head -1
else
    echo "⚠ John the Ripper not found"
    echo "Hash detection will work, but cracking will be unavailable."
    echo ""
    echo "To install John the Ripper:"
    echo "  Ubuntu/Debian: sudo apt-get install john"
    echo "  macOS: brew install john"
    echo "  Or visit: https://www.openwall.com/john/"
fi

echo ""
echo "Installation complete!"
echo ""
echo "To start the application:"
echo "  1. Activate virtual environment: source venv/bin/activate"
echo "  2. Run the app: python app.py"
echo "  3. Open browser: http://localhost:5000"
echo ""
echo "To deactivate virtual environment later: deactivate"