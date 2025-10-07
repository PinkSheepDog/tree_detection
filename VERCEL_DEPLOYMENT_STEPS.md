# Complete Vercel Deployment Guide - Step by Step

## ⚠️ Important: Two-Part Deployment

Your application needs TWO separate deployments:
1. **Backend (FastAPI + YOLOv7)** → Railway/Render (NOT Vercel)
2. **Frontend (React)** → Vercel

---

## STEP 1: Prepare Your Repository

### 1.1 Create a GitHub Repository (if you haven't already)

```bash
# Initialize git if not already done
cd /Users/ananyagulati/Desktop/tree-detection
git init

# Create .gitignore if needed
echo "node_modules/" >> .gitignore
echo "venv/" >> .gitignore
echo "__pycache__/" >> .gitignore
echo ".DS_Store" >> .gitignore

# Add all files
git add .

# Commit
git commit -m "Initial commit - Tree Detection App"

# Create GitHub repo and push
# Go to github.com, create a new repository
# Then run:
git remote add origin https://github.com/YOUR_USERNAME/tree-detection.git
git branch -M main
git push -u origin main
```

---

## STEP 2: Deploy Backend to Railway

### 2.1 Sign Up for Railway
1. Go to **https://railway.app/**
2. Click "Sign up with GitHub"
3. Authorize Railway to access your GitHub account

### 2.2 Create New Project
1. Click "New Project"
2. Select "Deploy from GitHub repo"
3. Choose your `tree-detection` repository
4. Railway will automatically detect it's a Python project

### 2.3 Configure Deployment
1. Railway will auto-detect the `Dockerfile` or `railway.json`
2. Go to "Settings" tab
3. Under "Environment", add any variables if needed
4. Under "Deploy", ensure start command is:
   ```
   uvicorn app:app --host 0.0.0.0 --port $PORT
   ```

### 2.4 Deploy
1. Click "Deploy" button
2. Wait for deployment to complete (5-10 minutes)
3. Check logs to ensure model loads successfully

### 2.5 Get Your Backend URL
1. Go to "Settings" tab
2. Click "Generate Domain" under "Domains"
3. Copy the URL (e.g., `https://your-app-name.up.railway.app`)
4. Test it by visiting: `https://your-app-name.up.railway.app/health`

**✅ SAVE THIS URL - You'll need it for Step 3!**

---

## STEP 3: Deploy Frontend to Vercel

### 3.1 Update Frontend Configuration

Before deploying to Vercel, you need to configure the API URL.

**Option A: Using Vercel Dashboard (Recommended)**
You'll set the environment variable in Vercel dashboard (Step 3.4)

**Option B: Using Local .env (For Testing)**
Create a `.env` file locally:
```bash
echo "REACT_APP_API_URL=http://localhost:8000" > .env
```

### 3.2 Sign Up for Vercel
1. Go to **https://vercel.com/**
2. Click "Sign up with GitHub"
3. Authorize Vercel to access your GitHub account

### 3.3 Import Your Project
1. Click "Add New..." → "Project"
2. Select "Import Git Repository"
3. Find and select your `tree-detection` repository
4. Click "Import"

### 3.4 Configure Project Settings

**Framework Preset**: Vercel should auto-detect "Create React App"

**Build Settings**:
- Build Command: `npm run build`
- Output Directory: `build`
- Install Command: `npm install`

**Root Directory**: Leave as `.` (root)

### 3.5 Add Environment Variables

Click "Environment Variables" and add:

| Name | Value |
|------|-------|
| `REACT_APP_API_URL` | `https://your-app-name.up.railway.app` |

**⚠️ IMPORTANT**: Replace with your actual Railway URL from Step 2.5!

Check "Production", "Preview", and "Development"

### 3.6 Deploy
1. Click "Deploy" button
2. Wait for build to complete (2-5 minutes)
3. Vercel will provide a URL like: `https://tree-detection-xxx.vercel.app`

### 3.7 Test Your Deployment
1. Visit your Vercel URL
2. Check if "Backend Status" shows ✅ Connected
3. Try uploading a test image
4. Verify tree detection works

---

## STEP 4: Update Backend CORS (If Needed)

If you get CORS errors, update `app.py` to include your Vercel domain:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://your-app-name.vercel.app",  # Add your Vercel URL
        "https://*.vercel.app"  # Allow all Vercel preview deployments
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Then push to GitHub and Railway will auto-redeploy.

---

## STEP 5: Set Up Automatic Deployments

### For Backend (Railway):
✅ Already configured! Railway auto-deploys on every push to `main` branch.

### For Frontend (Vercel):
✅ Already configured! Vercel auto-deploys on every push to `main` branch.

**To deploy updates:**
```bash
git add .
git commit -m "Your update message"
git push origin main
```

Both services will automatically redeploy!

---

## Alternative: Deploy Backend to Render.com

If Railway doesn't work, try Render:

### Steps:
1. Go to **https://render.com/**
2. Sign up with GitHub
3. Click "New +" → "Web Service"
4. Connect your repository
5. Configure:
   - **Name**: tree-detection-backend
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app:app --host 0.0.0.0 --port $PORT`
   - **Instance Type**: Free (or upgrade if needed)
6. Add Environment Variables:
   - `PYTHON_VERSION`: `3.11.0`
7. Click "Create Web Service"
8. Get your URL: `https://tree-detection-backend.onrender.com`
9. Use this URL in Vercel environment variables

---

## Troubleshooting

### Backend Issues

**Problem**: Model file too large
- **Solution**: Use Git LFS (Large File Storage)
  ```bash
  git lfs install
  git lfs track "*.pt"
  git add .gitattributes
  git add best.pt
  git commit -m "Add model with LFS"
  git push
  ```

**Problem**: Out of memory
- **Solution**: Upgrade to a paid plan with more RAM (Railway Pro or Render Starter)

**Problem**: Deployment timeout
- **Solution**: Increase timeout in Railway/Render settings

### Frontend Issues

**Problem**: Backend status shows disconnected
- **Solution**: Check that `REACT_APP_API_URL` is set correctly in Vercel

**Problem**: CORS errors
- **Solution**: Update CORS origins in `app.py` to include Vercel domain

**Problem**: Build fails
- **Solution**: Check build logs in Vercel for specific errors

---

## Cost Summary

### Free Tier (Development/Testing):
- **Railway**: $5 credit/month (usually sufficient for testing)
- **Vercel**: Unlimited deployments, 100GB bandwidth
- **Total**: FREE

### Production:
- **Railway Starter**: $5-10/month
- **Vercel Pro** (optional): $20/month (only if you need teams)
- **Total**: $5-10/month

---

## Quick Command Reference

```bash
# Test backend locally
source venv/bin/activate
python app.py

# Test frontend locally
npm start

# Build frontend for production
npm run build

# Push updates to deploy
git add .
git commit -m "Update"
git push origin main

# Check deployed backend
curl https://your-app-name.railway.app/health

# View Vercel logs
vercel logs your-deployment-url
```

---

## Next Steps After Deployment

1. ✅ Test with various image sizes
2. ✅ Monitor Railway usage/costs
3. ✅ Set up custom domain (optional)
4. ✅ Add analytics (optional)
5. ✅ Set up monitoring/alerts
6. ✅ Create backup of model file

---

## Support Links

- Railway Docs: https://docs.railway.app/
- Render Docs: https://render.com/docs
- Vercel Docs: https://vercel.com/docs
- FastAPI Deployment: https://fastapi.tiangolo.com/deployment/

---

## Need Help?

If you encounter issues:
1. Check Railway/Render logs for backend errors
2. Check Vercel logs for frontend errors
3. Test backend health endpoint directly
4. Verify environment variables are set correctly
5. Check CORS configuration in backend

**Common URLs to test:**
- Backend health: `https://your-backend.railway.app/health`
- Backend root: `https://your-backend.railway.app/`
- Frontend: `https://your-frontend.vercel.app/`

