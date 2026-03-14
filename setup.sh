#!/bin/bash
# Insurance Fraud Detection - Setup Script
set -e

echo "=== Insurance Fraud Detection Setup ==="
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv || python -m venv venv
source venv/bin/activate

# Install backend dependencies
echo "Installing backend dependencies..."
pip install -r requirements.txt

# Create data directory and generate synthetic data
echo "Generating synthetic data..."
mkdir -p data
python data_generator.py

# Initialize database
echo "Initializing database..."
python -c "from models import init_database; init_database(); print('Database initialized')"

# Train ML model
echo "Training ML model..."
python train_model.py

# Install frontend dependencies
echo "Installing frontend dependencies..."
cd frontend 2>/dev/null || (mkdir -p frontend && cd frontend)
if [ -f package.json ]; then
    npm install
else
    echo "Frontend not yet created. Run setup after frontend is added."
fi
cd ..

echo ""
echo "=== Setup Complete ==="
echo "To run the application:"
echo "1. Backend:  source venv/bin/activate && python app.py"
echo "2. Frontend: cd frontend && npm run dev"
echo ""
echo "API will be available at http://localhost:5000"
