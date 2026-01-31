# 🚀 Quick Start Guide - ViewTube

## Prerequisites
- Python 3.7 or higher
- pip (Python package manager)

---

## Step 1: Install Dependencies

Open your terminal in the project directory and run:

```bash
pip install -r requirements.txt
```

This will install:
- Flask 3.0.0
- yt-dlp 2024.8.6

---

## Step 2: Run the Development Server

```bash
python api\index.py
```

You should see output like:
```
 * Serving Flask app 'index'
 * Debug mode: on
 * Running on http://127.0.0.1:5000
```

---

## Step 3: Open in Browser

Navigate to:
```
http://localhost:5000
```

---

## Step 4: Test the Features

### Test Feature #1: Home Page
1. You should see a beautiful dark-themed landing page
2. Notice the animated gradient background
3. Try hovering over the feature cards

### Test Feature #2: Search
1. Enter a search query (e.g., "python tutorial")
2. Click the Search button
3. You should see 10 video results with thumbnails
4. Try hovering over video cards
5. Use the header search bar to search again

### Test Feature #3: Watch Video
1. Click on any video from search results
2. The video should load in a privacy-enhanced player
3. See video metadata (views, likes, date)
4. Read the video description
5. Notice the sidebar privacy cards

---

## Common Issues & Solutions

### Issue: "pip is not recognized"
**Solution:** Make sure Python is added to your PATH, or use:
```bash
python -m pip install -r requirements.txt
```

### Issue: "Module not found: Flask"
**Solution:** Install Flask manually:
```bash
pip install Flask
```

### Issue: "yt-dlp not working"
**Solution:** Update yt-dlp to the latest version:
```bash
pip install --upgrade yt-dlp
```

### Issue: Port 5000 already in use
**Solution:** Change the port in `api/index.py`:
```python
app.run(debug=True, port=5001)  # Use a different port
```

### Issue: Videos not loading
**Solution:** 
1. Check your internet connection
2. YouTube might be blocking requests - try again later
3. Check console for error messages

---

## Keyboard Shortcuts (Browser)

- `Ctrl + R` - Reload page
- `Ctrl + Shift + I` - Open developer tools
- `F11` - Fullscreen mode
- `Esc` - Exit fullscreen

---

## Development Tips

### Hot Reload
The Flask development server has auto-reload enabled. Just save your files and refresh the browser!

### Debug Mode
Debug mode is ON by default. You'll see detailed error messages if something goes wrong.

### Viewing Logs
Check the terminal where you ran `python api\index.py` to see server logs and any errors.

---

## Deploy to Vercel

### Option 1: Vercel CLI
```bash
# Install Vercel CLI
npm i -g vercel

# Login
vercel login

# Deploy
vercel
```

### Option 2: GitHub Integration
1. Push your code to GitHub
2. Go to vercel.com
3. Click "New Project"
4. Import your GitHub repository
5. Deploy!

---

## Environment Variables (Optional)

If you need to add environment variables for Vercel:

Create a `.env` file:
```
# Add any environment variables here
# Example:
# API_KEY=your_api_key
```

Add to `.gitignore`:
```
.env
```

---

## Testing Checklist

- [ ] Home page loads correctly
- [ ] Search bar is functional
- [ ] Search returns results
- [ ] Video cards display properly
- [ ] Thumbnails load
- [ ] Video player works
- [ ] Metadata displays correctly
- [ ] Header search works on all pages
- [ ] Mobile responsive (resize browser)
- [ ] No console errors

---

## Performance Tips

1. **Limit Search Results**: Already set to 10 (good for Vercel)
2. **Use Fast Internet**: yt-dlp needs good connection
3. **Clear Browser Cache**: If styles look broken
4. **Update Dependencies**: Keep yt-dlp updated

---

## Getting Help

### Check Logs
Always check the terminal output for error messages.

### Common Error Messages

**"No module named 'flask'"**
→ Run: `pip install Flask`

**"Connection timeout"**
→ Check internet connection or try again later

**"Video not found"**
→ The video might be private or deleted

**"Template not found"**
→ Make sure you're running from the project root directory

---

## Project Structure Reference

```
YoutubeClone/
├── api/
│   └── index.py          ← Flask app (run this!)
├── templates/
│   ├── home.html         ← Home page
│   ├── results.html      ← Search results
│   └── watch.html        ← Video player
├── static/
│   └── style.css         ← All styles
└── requirements.txt      ← Dependencies
```

---

## Next Steps

1. ✅ Run the app locally
2. ✅ Test all features
3. ✅ Customize the design (optional)
4. ✅ Deploy to Vercel
5. ✅ Share with friends!

---

## Support

If you encounter issues:
1. Check this guide
2. Read the error messages carefully
3. Check `PROJECT_SUMMARY.md` for technical details
4. Review the code comments in `api/index.py`

---

**Happy coding! 🎉**
