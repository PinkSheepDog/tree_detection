import React, { useState, useRef } from 'react';
import axios from 'axios';
import { Upload, Leaf, AlertCircle, CheckCircle, Clock, Image as ImageIcon } from 'lucide-react';
import './App.css';
import API_URL from './config';

function App() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [isUploading, setIsUploading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [isDragOver, setIsDragOver] = useState(false);
  const [backendStatus, setBackendStatus] = useState('unknown');
  const [processingInfo, setProcessingInfo] = useState(null);
  const fileInputRef = useRef(null);

  // Test backend connection on component mount
  React.useEffect(() => {
    const testBackendConnection = async () => {
      try {
        const response = await axios.get(`${API_URL}/`);
        setBackendStatus('connected');
        console.log('Backend connected:', response.data);
      } catch (error) {
        setBackendStatus('disconnected');
        console.error('Backend connection failed:', error);
      }
    };
    
    testBackendConnection();
  }, []);

  const handleFileSelect = (file) => {
    // Check file size (2GB = 2 * 1024 * 1024 * 1024 bytes)
    const maxSize = 2 * 1024 * 1024 * 1024;
    if (file.size > maxSize) {
      setError('File size must be less than 2GB.');
      return;
    }
    
    // Check file type
    const validTypes = ['image/tiff', 'image/tif', 'image/jpeg', 'image/jpg', 'image/png'];
    if (!validTypes.includes(file.type) && !file.name.toLowerCase().endsWith('.tif') && !file.name.toLowerCase().endsWith('.tiff')) {
      setError('Please select a valid image file (TIFF, JPG, PNG).');
      return;
    }
    
    setSelectedFile(file);
    setError(null);
    setResult(null);
    setProcessingInfo(null);
    
    // Log file size for debugging
    const fileSizeMB = (file.size / (1024 * 1024)).toFixed(2);
    console.log(`Selected file: ${file.name}, Size: ${fileSizeMB} MB`);
    
    // Create preview URL
    const reader = new FileReader();
    reader.onload = (e) => {
      console.log('Preview URL created:', e.target.result.substring(0, 50) + '...');
      setPreviewUrl(e.target.result);
    };
    reader.onerror = (e) => {
      console.error('Error reading file:', e);
      setError('Error reading image file.');
    };
    reader.readAsDataURL(file);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragOver(false);
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      handleFileSelect(files[0]);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragOver(false);
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      setError('Please select an image first.');
      return;
    }

    setIsLoading(true);
    setIsUploading(true);
    setError(null);
    setUploadProgress(0);
    setProcessingInfo(null);

    try {
      const formData = new FormData();
      formData.append('file', selectedFile);

      // Show processing info for large files
      const fileSizeMB = (selectedFile.size / (1024 * 1024)).toFixed(2);
      if (parseFloat(fileSizeMB) > 10) {
        setProcessingInfo({
          message: 'Large image detected. This may take a while as the image will be processed in tiles. Very large images may be automatically resized for optimal processing.',
          type: 'info'
        });
      }

      const response = await axios.post(`${API_URL}/api/detect-trees`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        timeout: 300000, // 5 minute timeout for very large images
        onUploadProgress: (progressEvent) => {
          const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          setUploadProgress(percentCompleted);
          console.log('Upload progress:', percentCompleted + '%');
        },
      });

      setResult(response.data);
      
      // Show processing method info
      if (response.data.processingMethod === 'tiled') {
        setProcessingInfo({
          message: `Image processed using tiling method. ${response.data.tilesProcessed} tiles were processed.`,
          type: 'success'
        });
      } else {
        setProcessingInfo({
          message: 'Image processed using single-pass method.',
          type: 'success'
        });
      }
    } catch (err) {
      console.error('Upload error:', err);
      console.error('Error details:', {
        message: err.message,
        response: err.response?.data,
        status: err.response?.status,
        statusText: err.response?.statusText
      });
      
      if (err.response) {
        const errorMessage = err.response.data?.detail || err.response.data?.message || 'Unknown server error';
        setError(`Server error (${err.response.status}): ${errorMessage}`);
      } else if (err.request) {
        setError(`Network error: Unable to connect to the server at ${API_URL}. Please check if your backend is running.`);
      } else {
        setError(`An unexpected error occurred: ${err.message}`);
      }
    } finally {
      setIsLoading(false);
      setIsUploading(false);
      setUploadProgress(0);
    }
  };

  const handleFileInputChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      handleFileSelect(file);
    }
  };

  const resetForm = () => {
    setSelectedFile(null);
    setPreviewUrl(null);
    setResult(null);
    setError(null);
    setUploadProgress(0);
    setProcessingInfo(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <div className="App">
      <div className="container">
        <header className="header">
          <div className="header-content">
            <Leaf className="header-icon" />
            <h1>Tree Detection</h1>
            <p>Upload an image to detect and count trees using YOLOv7</p>
          </div>
        </header>

        <div className="card">
          <h2>Upload Image</h2>
          
          <div className="backend-status">
            <span>Backend Status: </span>
            <span className={backendStatus === 'connected' ? 'status-connected' : 'status-disconnected'}>
              {backendStatus === 'connected' ? '✅ Connected' : backendStatus === 'disconnected' ? '❌ Disconnected' : '⏳ Checking...'}
            </span>
          </div>
          
          {error && (
            <div className="error">
              <AlertCircle size={20} />
              <span>{error}</span>
            </div>
          )}

          {processingInfo && (
            <div className={`info ${processingInfo.type}`}>
              {processingInfo.type === 'info' ? <Clock size={20} /> : <ImageIcon size={20} />}
              <span>{processingInfo.message}</span>
            </div>
          )}

          {result && (
            <div className="success">
              <CheckCircle size={20} />
              <span>Tree detection completed successfully!</span>
            </div>
          )}

          <div
            className={`upload-area ${isDragOver ? 'dragover' : ''}`}
            onDrop={handleDrop}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
          >
            <Upload size={48} />
            <h3>Drop your image here or click the button below</h3>
            <p>Supports TIFF, JPG, PNG up to 2GB</p>
            <p className="upload-note">Large images will be automatically processed in tiles for better accuracy</p>
            <p className="upload-note">Very large images (&gt;100M pixels) will be automatically resized for optimal processing</p>
            <input
              ref={fileInputRef}
              type="file"
              accept=".tif,.tiff,.jpg,.jpeg,.png"
              onChange={handleFileInputChange}
              style={{ display: 'none' }}
            />
            <button
              className="btn"
              onClick={() => fileInputRef.current?.click()}
              style={{ marginTop: '20px' }}
            >
              <Upload size={20} />
              Choose Image
            </button>
          </div>

          {previewUrl && (
            <div className="preview-section">
              <h3>Selected Image:</h3>
              {selectedFile && (
                <div className="file-info">
                  <span><strong>File:</strong> {selectedFile.name}</span>
                  <span><strong>Size:</strong> {(selectedFile.size / (1024 * 1024)).toFixed(2)} MB</span>
                </div>
              )}
              <div className="image-container">
                <img 
                  src={previewUrl} 
                  alt="Preview" 
                  onLoad={() => console.log('Image loaded successfully')}
                  onError={(e) => console.error('Image failed to load:', e)}
                />
              </div>
              
              {(isLoading || isUploading) && (
                <div className="progress-section">
                  <div className="progress-bar">
                    <div 
                      className="progress-fill" 
                      style={{ width: `${uploadProgress}%` }}
                    ></div>
                  </div>
                  <div className="progress-text">
                    {isUploading && uploadProgress > 0 && uploadProgress < 100 
                      ? `Uploading: ${uploadProgress}%`
                      : isLoading && uploadProgress === 100 
                        ? 'Processing image...'
                        : 'Starting upload...'
                    }
                  </div>
                </div>
              )}
              
              <div className="button-group">
                <button
                  className="btn"
                  onClick={handleUpload}
                  disabled={isLoading || isUploading}
                >
                  {isLoading || isUploading ? (
                    <>
                      <div className="loading"></div>
                      {isUploading ? 'Uploading...' : 'Processing...'}
                    </>
                  ) : (
                    <>
                      <Leaf size={20} />
                      Detect Trees
                    </>
                  )}
                </button>
                <button
                  className="btn btn-secondary"
                  onClick={resetForm}
                  disabled={isLoading || isUploading}
                >
                  Reset
                </button>
              </div>
            </div>
          )}
        </div>

        {result && (
          <div className="card">
            <h2>Detection Results</h2>
            
            <div className="stats">
              <div className="stat-card">
                <div className="stat-number">{result.treeCount}</div>
                <div className="stat-label">Trees Detected</div>
              </div>
              <div className="stat-card">
                <div className="stat-number">{result.confidence}%</div>
                <div className="stat-label">Average Confidence</div>
              </div>
              <div className="stat-card">
                <div className="stat-number">{result.processingTime}s</div>
                <div className="stat-label">Processing Time</div>
              </div>
              {result.processingMethod === 'tiled' && (
                <div className="stat-card">
                  <div className="stat-number">{result.tilesProcessed}</div>
                  <div className="stat-label">Tiles Processed</div>
                </div>
              )}
            </div>

            {result.labeledImageUrl && (
              <div className="result-section">
                <h3>Labeled Image:</h3>
                <div className="image-container">
                  <img 
                    src={result.labeledImageUrl} 
                    alt="Detected trees with bounding boxes" 
                  />
                </div>
              </div>
            )}

            {result.detections && result.detections.length > 0 && (
              <div className="detections-section">
                <h3>Detection Details:</h3>
                <div className="detections-grid">
                  {result.detections.map((detection, index) => (
                    <div key={index} className="detection-item">
                      <strong>Tree {index + 1}:</strong>
                      <span>Confidence: {detection.confidence.toFixed(2)}%</span>
                      <span>Box: ({detection.bbox.x}, {detection.bbox.y}, {detection.bbox.width}, {detection.bbox.height})</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default App; 