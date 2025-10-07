// API Configuration
// This will use the environment variable if set, otherwise fall back to localhost
const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export default API_URL;

