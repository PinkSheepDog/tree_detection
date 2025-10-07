#!/bin/bash

# Setup Git LFS for large model file
echo "Setting up Git LFS for large model file..."

# Check if git-lfs is installed
if ! command -v git-lfs &> /dev/null; then
    echo "Git LFS is not installed. Installing..."
    
    # Check OS and install accordingly
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if command -v brew &> /dev/null; then
            brew install git-lfs
        else
            echo "Please install Homebrew first: https://brew.sh/"
            exit 1
        fi
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        sudo apt-get update
        sudo apt-get install git-lfs
    else
        echo "Please install Git LFS manually: https://git-lfs.github.com/"
        exit 1
    fi
fi

# Initialize Git LFS
echo "Initializing Git LFS..."
git lfs install

# Track large files
echo "Tracking large model files..."
git lfs track "*.pt"
git lfs track "*.pth"
git lfs track "*.onnx"

# Add .gitattributes
git add .gitattributes

# Check if best.pt is tracked
echo "Checking if best.pt is tracked..."
git lfs track

echo ""
echo "✅ Git LFS setup complete!"
echo ""
echo "Next steps:"
echo "1. Run: git add best.pt"
echo "2. Run: git commit -m 'Add model file with LFS'"
echo "3. Run: git push"
echo ""
echo "Note: Some platforms (Railway, Render) support Git LFS automatically."
echo "If deployment fails due to file size, you may need to:"
echo "  - Use a platform with better LFS support"
echo "  - Upload the model file separately and load it at runtime"
echo "  - Use a smaller model"

