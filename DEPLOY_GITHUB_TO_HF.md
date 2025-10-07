# 🚀 Deploy from GitHub to Hugging Face - Complete Guide

## ✨ Deploy Your Entire App (Frontend + Backend) from GitHub!

This is the **BEST** and **EASIEST** way to deploy! Hugging Face can automatically sync with your GitHub repository.

---

## 🎯 What You Get:

✅ **One unified app** - No separate frontend/backend  
✅ **Auto-sync** - Push to GitHub → Auto-deploy to HF  
✅ **Beautiful UI** - Professional Gradio interface  
✅ **Free hosting** - No credit card needed  
✅ **Easy sharing** - One URL for everything  

---

## 📋 Step-by-Step Deployment

### **Step 1: Create Hugging Face Account** (2 minutes)

1. Go to: **https://huggingface.co/**
2. Click **"Sign Up"**
3. Sign up with email or **GitHub** (recommended!)
4. Verify your email

---

### **Step 2: Create a New Space** (3 minutes)

1. Click your profile picture (top right)
2. Click **"New Space"**
3. Fill in the form:

   **Owner:** Your username  
   **Space name:** `tree-detection`  
   **License:** MIT  
   **Select SDK:** **Gradio** ⭐  
   **Space hardware:** **CPU basic - Free!**  
   **Space visibility:** Public (or Private)

4. **✅ IMPORTANT:** Check **"Link to a Git repository"**
5. Click **"Create Space"**

---

### **Step 3: Connect Your GitHub Repository** (5 minutes)

After creating the Space, you'll see options to connect:

#### **Option A: Direct GitHub Connection (Recommended)**

1. In your new Space, click **"Settings"** tab
2. Scroll to **"Repository"** section
3. Click **"Link to GitHub repository"**
4. Authorize Hugging Face to access GitHub
5. Select your repository: **`PinkSheepDog/tree_detection`**
6. Choose branch: **`main`**
7. Click **"Link repository"**

#### **Option B: Manual Git Setup**

If Option A doesn't work, use Git:

```bash
cd ~/Desktop/tree-detection

# Add Hugging Face as a remote
git remote add hf https://huggingface.co/spaces/YOUR_USERNAME/tree-detection

# Push to Hugging Face
git push hf main
```

---

### **Step 4: Configure Your Space** (2 minutes)

You need to tell HF which files to use. Create a special README:

1. In your Space, click **"Files"** tab
2. Click **"Add file"** → **"Create a new file"**
3. Name it: **`README.md`**
4. Paste this content:

```markdown
---
title: Tree Detection YOLOv7
emoji: 🌳
colorFrom: green
colorTo: blue
sdk: gradio
sdk_version: 4.44.0
app_file: app_fullstack_hf.py
pinned: false
license: mit
---

# 🌳 Tree Detection with YOLOv7

AI-powered tree detection in aerial and satellite imagery.

## Features
- 🎯 Accurate tree detection
- 📊 Detailed statistics
- 🔲 Tiling support for large images
- ⚡ Fast processing

Upload an image to detect trees!
```

5. Click **"Commit new file to main"**

---

### **Step 5: Handle Large Files (Model)** (5 minutes)

Your `best.pt` file (71MB) needs Git LFS:

```bash
cd ~/Desktop/tree-detection

# Install Git LFS if not installed
brew install git-lfs  # Mac
# or
sudo apt-get install git-lfs  # Linux

# Initialize Git LFS
git lfs install

# Track large files
git lfs track "*.pt"

# Add .gitattributes
git add .gitattributes

# Commit
git commit -m "Setup Git LFS for model file"

# Push to GitHub (and HF if linked)
git push origin main

# If using separate HF remote:
git push hf main
```

---

### **Step 6: Rename App File** (1 minute)

Hugging Face needs the file to be named `app.py`:

**Option A: Via Git**
```bash
cd ~/Desktop/tree-detection
cp app_fullstack_hf.py app.py
git add app.py
git commit -m "Add main app file for Hugging Face"
git push origin main
```

**Option B: Via HF Web UI**
1. Go to your Space → "Files" tab
2. Upload `app_fullstack_hf.py`
3. Rename it to `app.py`

---

### **Step 7: Update requirements.txt** (1 minute)

Make sure you have the right dependencies:

**Option A: Create new file**
```bash
cd ~/Desktop/tree-detection
cp requirements_hf.txt requirements.txt
git add requirements.txt
git commit -m "Update requirements for HF"
git push origin main
```

**Option B: Or ensure requirements.txt has:**
```
gradio==4.44.0
torch==2.0.1
torchvision==0.15.2
opencv-python-headless==4.8.1.78
numpy==1.24.3
Pillow==10.0.0
PyYAML==6.0.1
scipy==1.11.2
tqdm==4.66.1
matplotlib==3.7.2
```

---

### **Step 8: Wait for Build & Deploy** (5-10 minutes)

1. Go to your Space page
2. Click **"Logs"** tab
3. Watch the build progress:
   - Installing dependencies
   - Loading model
   - Starting Gradio
4. When you see: `Running on public URL:` → **SUCCESS!** ✅

---

### **Step 9: Test Your App** 🎉

1. Click **"App"** tab
2. Upload a test image
3. Click "Detect Trees"
4. See the results!

**Your app is live at:**
```
https://huggingface.co/spaces/YOUR_USERNAME/tree-detection
```

---

## 🔄 Auto-Deployment Setup

Once connected, any push to GitHub automatically deploys to HF!

```bash
# Make changes
git add .
git commit -m "Update model"
git push origin main

# HF automatically rebuilds! 🚀
```

---

## 📁 Required Files in Your Repo

Make sure these files are in your GitHub repo:

```
tree_detection/
├── app.py (or app_fullstack_hf.py renamed)
├── requirements.txt
├── README.md (with HF header)
├── best.pt (with Git LFS)
├── yolov7/
│   ├── models/
│   └── utils/
└── .gitattributes (for LFS)
```

---

## 🎛️ Space Settings

### Hardware Options:
- **CPU basic:** FREE ✅ (Recommended for this app)
- **CPU upgraded:** $0.60/hour
- **GPU T4:** $0.60/hour (if you want faster processing)

### Visibility:
- **Public:** Anyone can use
- **Private:** Only you can access

---

## 🔧 Troubleshooting

### Issue: Build fails with "Model not found"

**Solution:** Make sure `best.pt` is in the repo root and tracked with Git LFS

```bash
git lfs track "*.pt"
git add .gitattributes best.pt
git commit -m "Add model with LFS"
git push
```

### Issue: "Module not found" error

**Solution:** Check `requirements.txt` has all dependencies

### Issue: Space stuck on "Building"

**Solution:** 
1. Check "Logs" tab for specific error
2. May need to restart Space (Settings → Factory Reboot)

### Issue: GitHub sync not working

**Solution:**
1. Go to Settings → Repository
2. Click "Unlink" then "Link" again
3. Or use manual Git push to HF remote

---

## 💡 Pro Tips

### Tip 1: Use Secrets for API Keys
If you need API keys:
1. Settings → Repository secrets
2. Add secrets (they're encrypted)
3. Access in code: `os.getenv("SECRET_NAME")`

### Tip 2: Add Example Images
Create `examples/` folder with sample images:
```python
gr.Examples(
    examples=["examples/forest1.jpg", "examples/forest2.jpg"],
    inputs=input_image
)
```

### Tip 3: Enable Analytics
Settings → Analytics → Enable
See your Space usage stats!

### Tip 4: Custom Domain
Settings → Domains → Add custom domain
Use your own domain name!

---

## 🌐 Sharing Your Space

### Direct Link:
```
https://huggingface.co/spaces/YOUR_USERNAME/tree-detection
```

### Embed in Website:
```html
<gradio-app src="https://YOUR_USERNAME-tree-detection.hf.space"></gradio-app>
<script type="module" src="https://gradio.s3-us-west-2.amazonaws.com/4.44.0/gradio.js"></script>
```

### Share on Social Media:
HF automatically creates preview cards!

---

## 📊 Monitoring

### View Logs:
Logs tab → See real-time logs

### Check Usage:
Settings → Usage → See compute hours

### Monitor Errors:
Logs automatically capture errors

---

## 🎉 Summary

**What you did:**
1. ✅ Created HF Space
2. ✅ Connected GitHub repo
3. ✅ Configured files
4. ✅ Set up Git LFS
5. ✅ Deployed!

**What you get:**
- 🌐 Live web app
- 🔄 Auto-deployment from GitHub
- 📊 Beautiful Gradio UI
- 🆓 Free hosting
- 📈 Analytics

**Your app URL:**
```
https://huggingface.co/spaces/YOUR_USERNAME/tree-detection
```

---

## 🚀 Next Steps

1. **Test thoroughly** with different images
2. **Share** your Space URL
3. **Monitor** usage and logs
4. **Update** by pushing to GitHub
5. **Upgrade** hardware if needed

---

## 📚 Useful Links

- **Your Spaces:** https://huggingface.co/spaces
- **HF Spaces Docs:** https://huggingface.co/docs/hub/spaces
- **Gradio Docs:** https://gradio.app/docs/
- **Git LFS:** https://git-lfs.github.com/
- **Your GitHub Repo:** https://github.com/PinkSheepDog/tree_detection

---

**Congratulations! Your entire app is now live on Hugging Face!** 🎉🌳

No need for separate Vercel deployment - everything is in one place!

