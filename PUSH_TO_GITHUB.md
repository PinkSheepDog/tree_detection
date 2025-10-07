# 🚀 Push to GitHub - Quick Guide

## Step 1: Get Your Personal Access Token

1. **Click this link**: https://github.com/settings/tokens/new
2. **Log in as PinkSheepDog** if prompted

3. **Fill in the form**:
   - **Note**: `tree-detection-upload`
   - **Expiration**: Select `90 days` (or choose your preference)
   - **Select scopes**: ✅ Check the box for **`repo`** (Full control of private repositories)
4. **Scroll down and click** "Generate token" (green button)

5. **COPY THE TOKEN** - It looks like: `ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`
   - ⚠️ **IMPORTANT**: Copy it NOW! You won't see it again!

---

## Step 2: Use the Token to Push

After you copy the token, open your terminal and run these commands:

Replace `YOUR_TOKEN_HERE` with the token you just copied:

```bash
cd /Users/ananyagulati/Desktop/tree-detection

git remote set-url origin https://YOUR_TOKEN_HERE@github.com/PinkSheepDog/tree_detection.git

git push -u origin main
```

---

## Example:

If your token is `ghp_ABC123XYZ`, you would run:

```bash
git remote set-url origin https://ghp_ABC123XYZ@github.com/PinkSheepDog/tree_detection.git
git push -u origin main
```

---

## ✅ After Success

Your code will be at: https://github.com/PinkSheepDog/tree_detection

Then you can proceed with Vercel deployment!

---

## 🔒 Security Note

- Don't share your token with anyone
- The token gives full access to your repositories
- You can delete it later from: https://github.com/settings/tokens
