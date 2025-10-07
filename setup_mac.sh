#!/bin/bash

echo "🌳 Setting up Tree Detection for macOS..."
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Homebrew is installed
if ! command -v brew &> /dev/null; then
    print_warning "Homebrew not found. Installing Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    print_success "Homebrew installed"
else
    print_success "Homebrew found: $(brew --version | head -n1)"
fi

# Check if Python 3.11 is installed (recommended for ARM64 Macs)
if ! command -v python3.11 &> /dev/null; then
    print_warning "Python 3.11 not found. Installing Python 3.11..."
    arch -arm64 brew install python@3.11
    print_success "Python 3.11 installed"
else
    print_success "Python 3.11 found: $(python3.11 --version)"
fi

# Use Python 3.11 for better ARM64 compatibility
PYTHON_CMD="python3.11"

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    print_warning "Node.js not found. Installing Node.js..."
    brew install node
    print_success "Node.js installed"
else
    print_success "Node.js found: $(node --version)"
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    print_error "npm is not installed. Please install npm."
    exit 1
fi

print_success "npm found: $(npm --version)"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    print_status "Creating virtual environment with Python 3.11..."
    $PYTHON_CMD -m venv venv
    print_success "Virtual environment created"
else
    print_success "Virtual environment already exists"
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
print_status "Upgrading pip..."
pip install --upgrade pip

# Install Python requirements
print_status "Installing Python dependencies..."
pip install -r requirements.txt

# Check if YOLOv7 repository exists
if [ ! -d "yolov7" ]; then
    print_status "Cloning YOLOv7 repository..."
    git clone https://github.com/WongKinYiu/yolov7.git
    print_success "YOLOv7 repository cloned"
else
    print_success "YOLOv7 repository already exists"
fi

# Create symbolic links for YOLOv7 modules (remove existing links first)
print_status "Setting up YOLOv7 modules..."
if [ -L "models" ]; then
    rm models
fi
if [ -L "utils" ]; then
    rm utils
fi

# Create new symbolic links
ln -sf yolov7/models models
ln -sf yolov7/utils utils

print_success "YOLOv7 modules linked"

# Check for model file
if [ ! -f "best.pt" ]; then
    print_warning "Model file 'best.pt' not found!"
    print_status "Please place your trained YOLOv7 model file in the current directory."
    print_status "You can update the model path in app.py if needed."
else
    print_success "Model file found: best.pt"
fi

# Install frontend dependencies
print_status "Installing frontend dependencies..."
npm install

print_success "Frontend dependencies installed"

echo ""
echo "🎉 Setup complete!"
echo ""
echo "Next steps:"
echo "1. Start the backend: ./start_backend.sh"
echo "2. Start the frontend: npm start"
echo "3. Open your browser to: http://localhost:3000"
echo ""
echo "Happy tree detecting! 🌲" 