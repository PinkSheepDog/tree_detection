# Tree Detection Application

A cross-platform YOLOv7-based tree detection application with a React frontend and FastAPI backend.

## 🌟 Features

- **Cross-platform compatibility**: Works on Windows, macOS, and Linux
- **YOLOv7-based tree detection**: Accurate tree detection using YOLOv7 model
- **React frontend**: Modern, responsive web interface
- **FastAPI backend**: High-performance API with automatic documentation
- **Large image support**: Handles images of any size with tiling
- **Real-time processing**: Fast inference with GPU acceleration support

## 🚀 Quick Start

### Prerequisites

- **Python 3.9+** (3.11 recommended)
- **Node.js 16+** and npm
- **Git** (for cloning YOLOv7 repository)

### Installation

#### Windows

```bash
# Run the setup script
setup.bat

# Or manually
python setup.py
```

#### macOS/Linux

```bash
# Make scripts executable
chmod +x setup.sh start_backend.sh start_all.sh

# Run the setup script
./setup.sh

# Or manually
python3 setup.py
```

### Starting the Application

#### Option 1: Start Both Servers (Recommended)

```bash
# Windows
start_all.bat

# macOS/Linux
./start_all.sh

# Or manually
python start_all_cross_platform.py
```

#### Option 2: Start Servers Separately

**Backend (API Server):**

```bash
# Windows
start_backend.bat

# macOS/Linux
./start_backend.sh

# Or manually
python start_backend_cross_platform.py
```

**Frontend (React App):**

```bash
npm start
```

### Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 📁 Project Structure

```
tree-detection/
├── app.py                          # FastAPI backend application
├── setup.py                        # Cross-platform setup script
├── start_backend_cross_platform.py # Cross-platform backend starter
├── start_all_cross_platform.py     # Cross-platform full app starter
├── requirements.txt                 # Python dependencies
├── package.json                    # Node.js dependencies
├── best.pt                         # YOLOv7 model file (you need to add this)
├── yolov7/                         # YOLOv7 repository (cloned automatically)
├── models/                         # YOLOv7 models (symlinked/copied)
├── utils/                          # YOLOv7 utilities (symlinked/copied)
├── src/                            # React frontend source
└── public/                         # React frontend public files
```

## 🔧 Setup Details

The setup script automatically:

1. **Detects your Python installation** (3.9+ required)
2. **Creates a virtual environment** (`venv/`)
3. **Installs Python dependencies** from `requirements.txt`
4. **Clones YOLOv7 repository** if not present
5. **Sets up YOLOv7 modules** (symbolic links on Unix, copies on Windows)
6. **Installs Node.js dependencies** via npm
7. **Checks for model file** (`best.pt`)

## 🎯 Usage

1. **Upload an image** through the web interface
2. **Process the image** - the backend will detect trees using YOLOv7
3. **View results** - bounding boxes and confidence scores are displayed
4. **Download results** - processed images can be downloaded

## 🛠️ API Endpoints

- `POST /api/detect-trees` - Detect trees in uploaded image
- `POST /api/detect-trees-tile` - Process large images with tiling
- `GET /health` - Health check endpoint
- `GET /docs` - Interactive API documentation

## 🔍 Troubleshooting

### Common Issues

**"Virtual environment not found"**

```bash
# Run setup again
python setup.py
```

**"YOLOv7 modules not found"**

```bash
# The setup script should handle this automatically
# If issues persist, manually clone YOLOv7:
git clone https://github.com/WongKinYiu/yolov7.git
```

**"Model file not found"**

- Place your trained YOLOv7 model file (`best.pt`) in the project root
- Update the model path in `app.py` if needed

**Port conflicts**

- The scripts automatically kill processes on ports 8000 and 3000
- If issues persist, manually stop processes using those ports

### Platform-Specific Notes

**Windows:**

- Uses `python` command (make sure Python is in PATH)
- YOLOv7 modules are copied (not symlinked)
- Uses `taskkill` for process management

**macOS/Linux:**

- Uses `python3` command
- YOLOv7 modules are symlinked
- Uses `kill` for process management

## 🧪 Development

### Running Tests

```bash
# Test model loading
python test_model_loading.py

# Test full pipeline
python test_full_pipeline.py

# Test simple functionality
python test_simple.py
```

### Adding New Features

1. Backend changes: Modify `app.py`
2. Frontend changes: Modify files in `src/`
3. Dependencies: Update `requirements.txt` (Python) or `package.json` (Node.js)

## 📦 Dependencies

### Python Dependencies

- `fastapi` - Web framework
- `torch` - PyTorch for ML
- `opencv-python` - Image processing
- `Pillow` - Image handling
- `requests` - HTTP client
- `psutil` - Process management

### Node.js Dependencies

- `react` - Frontend framework
- `axios` - HTTP client
- `lucide-react` - Icons

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test on multiple platforms
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- [YOLOv7](https://github.com/WongKinYiu/yolov7) - Object detection model
- [FastAPI](https://fastapi.tiangolo.com/) - Web framework
- [React](https://reactjs.org/) - Frontend framework

---

**Happy tree detecting! 🌲**
