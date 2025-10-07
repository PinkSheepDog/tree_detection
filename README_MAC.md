# Tree Detection Application - macOS Setup

This guide will help you set up and run the Tree Detection application on macOS.

## Prerequisites

- macOS 10.15 or later
- Python 3.8+ (included with macOS or install via Homebrew)
- Node.js 14+ and npm
- Git

## Quick Start

1. **Setup the environment:**

   ```bash
   ./setup_mac.sh
   ```

2. **Start the application:**

   ```bash
   ./start_all.sh
   ```

3. **Open your browser:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## Manual Setup

If the quick start doesn't work, follow these steps:

### 1. Install Dependencies

```bash
# Install Homebrew (if not already installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python and Node.js
brew install python node

# Verify installations
python3 --version
node --version
npm --version
```

### 2. Setup Python Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt
```

### 3. Setup YOLOv7

```bash
# Clone YOLOv7 repository (if not already present)
git clone https://github.com/WongKinYiu/yolov7.git

# Create symbolic links
ln -sf yolov7/models models
ln -sf yolov7/utils utils
```

### 4. Setup Frontend

```bash
# Install frontend dependencies
npm install
```

### 5. Start the Application

**Option 1: Use the startup script**

```bash
./start_all.sh
```

**Option 2: Start manually**

```bash
# Terminal 1 - Start backend
source venv/bin/activate
python3 start_backend.py

# Terminal 2 - Start frontend
npm start
```

## Troubleshooting

### Backend Issues

**Problem: "YOLOv7 modules not found"**

```bash
# Solution: Ensure symbolic links are correct
rm -f models utils
ln -sf yolov7/models models
ln -sf yolov7/utils utils
```

**Problem: "Model file not found"**

```bash
# Solution: Ensure best.pt is in the project directory
ls -la best.pt
```

**Problem: Port 8000 already in use**

```bash
# Solution: Kill existing process
lsof -ti:8000 | xargs kill -9
```

### Frontend Issues

**Problem: Port 3000 already in use**

```bash
# Solution: Kill existing process
lsof -ti:3000 | xargs kill -9
```

**Problem: "Network error: Unable to connect to server"**

```bash
# Solution: Check if backend is running
curl http://localhost:8000/health
```

**Problem: npm install fails**

```bash
# Solution: Clear npm cache and retry
npm cache clean --force
rm -rf node_modules package-lock.json
npm install
```

### General Issues

**Problem: Permission denied errors**

```bash
# Solution: Make scripts executable
chmod +x setup_mac.sh start_all.sh start_backend.sh
```

**Problem: Virtual environment not found**

```bash
# Solution: Recreate virtual environment
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Testing the Application

1. **Test Backend API:**

   ```bash
   curl http://localhost:8000/health
   ```

2. **Test File Upload:**

   ```bash
   curl -X POST http://localhost:8000/api/detect-trees \
     -F "file=@test_image.jpg"
   ```

3. **Test Frontend:**
   - Open http://localhost:3000
   - Upload an image
   - Check browser console for errors

## File Structure

```
tree-detection/
├── app.py                 # FastAPI backend
├── start_backend.py       # Backend startup script
├── setup_mac.sh          # Mac setup script
├── start_all.sh          # Complete startup script
├── best.pt               # YOLOv7 model file
├── requirements.txt       # Python dependencies
├── package.json          # Node.js dependencies
├── src/                  # React frontend source
├── public/               # React public files
├── venv/                 # Python virtual environment
├── node_modules/         # Node.js dependencies
└── yolov7/              # YOLOv7 repository
```

## Development

### Backend Development

```bash
source venv/bin/activate
python3 start_backend.py
```

### Frontend Development

```bash
npm start
```

### API Testing

```bash
# Test health endpoint
curl http://localhost:8000/health

# Test tree detection
curl -X POST http://localhost:8000/api/detect-trees \
  -F "file=@your_image.jpg"
```

## Support

If you encounter issues:

1. Check the browser console for JavaScript errors
2. Check the terminal for Python errors
3. Ensure all dependencies are installed
4. Verify the model file is present
5. Check that both servers are running on the correct ports

## System Requirements

- **CPU:** Intel/Apple Silicon (M1/M2 supported)
- **RAM:** 4GB minimum, 8GB recommended
- **Storage:** 2GB free space
- **OS:** macOS 10.15 or later

## Performance Notes

- The application runs on CPU by default
- GPU acceleration is available if CUDA is installed
- Large images may take longer to process
- The model file (best.pt) is ~71MB
