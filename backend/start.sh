#!/bin/bash

# InsightHire Backend Startup Script

echo "Starting InsightHire Backend..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install requirements
echo "Installing requirements..."
pip install -r requirements.txt

# Set environment variables
export FLASK_HOST=0.0.0.0
export FLASK_PORT=5000
export FLASK_DEBUG=True

# Start the Flask application
echo "Starting Flask server..."
python app.py
