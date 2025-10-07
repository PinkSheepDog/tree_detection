# Tree Detection Application - Deployment Guide

## Overview
This guide will help you deploy your Tree Detection application with:
- **Frontend (React)** → Vercel
- **Backend (FastAPI + YOLOv7)** → Railway / Render / Hugging Face

---

## Part 1: Deploy Backend (Railway - Recommended)

### Why Railway?
- ✅ Supports large files (your 71MB model)
- ✅ No timeout limits for ML inference
- ✅ Easy deployment from GitHub
- ✅ Free tier available ($5 credit/month)
- ✅ Auto-scaling and persistent deployment

### Steps:

#### 1.1 Prepare Backend for Deployment

Create necessary configuration files (these will be created for you).

#### 1.2 Sign up for Railway
1. Go to https://railway.app/
2. Sign up with GitHub
3. Create a new project

#### 1.3 Deploy to Railway
1. Click "New Project" → "Deploy from GitHub repo"
2. Select your repository
3. Railway will auto-detect the Python app
4. Add environment variables (if needed)
5. Deploy!

#### 1.4 Get Your Backend URL
After deployment, Railway will provide a URL like:
`https://your-app-name.up.railway.app`

**Save this URL - you'll need it for the frontend!**

---

## Part 2: Deploy Frontend to Vercel

### Steps:

#### 2.1 Update Frontend API Endpoint
Before deploying, you need to update the frontend to use your deployed backend URL.

#### 2.2 Create Vercel Account
1. Go to https://vercel.com/
2. Sign up with GitHub

#### 2.3 Deploy to Vercel
1. Click "Add New..." → "Project"
2. Import your GitHub repository
3. Configure project:
   - **Framework Preset**: Create React App
   - **Build Command**: `npm run build`
   - **Output Directory**: `build`
   - **Install Command**: `npm install`

4. Add Environment Variable:
   - Name: `REACT_APP_API_URL`
   - Value: Your Railway backend URL (e.g., `https://your-app.railway.app`)

5. Click "Deploy"

#### 2.4 Access Your App
Vercel will provide a URL like:
`https://your-app-name.vercel.app`

---

## Alternative Backend Hosting Options

### Option 2: Render.com
- Similar to Railway
- Free tier available
- Good for Python/ML apps
- https://render.com/

### Option 3: Hugging Face Spaces
- Specifically designed for ML apps
- Free hosting for ML models
- Great community
- https://huggingface.co/spaces

### Option 4: Google Cloud Run / AWS Lambda (Advanced)
- More complex setup
- Better for production at scale
- Requires containerization (Docker)

---

## Important Notes

### Backend Considerations:
1. **Model File Size**: Your `best.pt` is 71MB - ensure it's included in deployment
2. **Dependencies**: Make sure all YOLOv7 dependencies are in `requirements.txt`
3. **Timeout**: ML inference can take time - choose a platform without strict timeouts
4. **Memory**: YOLOv7 requires at least 2GB RAM

### Frontend Considerations:
1. **CORS**: Your backend needs CORS configured (already done in `app.py`)
2. **API URL**: Must be updated to point to deployed backend
3. **Environment Variables**: Use env vars for flexibility

---

## Quick Deployment Checklist

- [ ] Create Dockerfile for backend (optional but recommended)
- [ ] Create railway.json configuration
- [ ] Update frontend API URLs to use environment variables
- [ ] Test backend locally one more time
- [ ] Deploy backend to Railway
- [ ] Get backend URL
- [ ] Update frontend with backend URL
- [ ] Deploy frontend to Vercel
- [ ] Test the deployed application

---

## Troubleshooting

### Backend Issues:
- **Model not loading**: Ensure `best.pt` is in the repository
- **Dependencies missing**: Check `requirements.txt` includes all packages
- **Out of memory**: Upgrade to a paid plan with more RAM

### Frontend Issues:
- **CORS errors**: Check backend CORS configuration allows your Vercel domain
- **API not connecting**: Verify backend URL is correct and backend is running
- **Build fails**: Check Node.js version compatibility

---

## Cost Estimate

### Free Tier (Good for Development):
- Railway: $5 credit/month (usually enough for testing)
- Vercel: Unlimited deployments, 100GB bandwidth
- **Total**: FREE for light usage

### Production (Recommended):
- Railway: ~$5-10/month for persistent backend
- Vercel: FREE (Pro at $20/month for teams)
- **Total**: ~$5-10/month

---

## Need Help?
- Railway Docs: https://docs.railway.app/
- Vercel Docs: https://vercel.com/docs
- FastAPI Deployment: https://fastapi.tiangolo.com/deployment/

