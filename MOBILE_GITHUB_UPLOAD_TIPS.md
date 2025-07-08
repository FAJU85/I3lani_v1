# Quick Guide: Upload to GitHub from Mobile

## Option 1: GitHub Mobile App
1. Download GitHub app (iOS/Android)
2. Create new repository
3. Upload files directly from your device
4. Commit and push

## Option 2: GitHub Website (Mobile Browser)
1. Go to github.com
2. Click "+" → "New repository"
3. Name it: `i3lani-bot`
4. Click "uploading an existing file"
5. Drag/select all bot files
6. Commit changes

## Important Files to Upload
✅ All .py files (main.py, handlers.py, etc.)
✅ requirements.txt
✅ render.yaml
✅ README.md
✅ All .md documentation files

## Files to SKIP
❌ .env (contains secrets)
❌ bot.db (local database)
❌ __pycache__ folders
❌ .replit files

## After GitHub Upload
1. Go to render.com
2. Sign up/login
3. New → Web Service
4. Connect GitHub repo
5. It will auto-detect render.yaml
6. Deploy!

## Quick Tip
Update README.md line 21:
Replace `YOUR_USERNAME/YOUR_REPO_NAME` with your actual GitHub username and repo name

Example: `https://github.com/johndoe/i3lani-bot`