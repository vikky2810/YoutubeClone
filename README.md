# ViewTube - Privacy-Focused YouTube Frontend

A lightweight, privacy-focused YouTube frontend built with Flask and deployed on Vercel.

## Features

- 🔒 **Privacy First** - No tracking, no cookies, no data collection
- ⚡ **Lightning Fast** - Optimized for Vercel serverless deployment
- 🎯 **Simple & Clean** - Minimal interface, maximum functionality

## Tech Stack

- **Backend**: Python + Flask
- **Frontend**: HTML + CSS (Jinja templates)
- **Video Data**: yt-dlp
- **Deployment**: Vercel (serverless)

## Local Development

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the development server**:
   ```bash
   python api/index.py
   ```

3. **Open in browser**:
   ```
   http://localhost:5000
   ```

## Deployment

Deploy to Vercel with one click:

```bash
vercel
```

Or connect your GitHub repository to Vercel for automatic deployments.

## Project Structure

```
YoutubeClone/
├── api/
│   └── index.py          # Flask app (Vercel entry point)
├── templates/
│   ├── home.html         # Home page
│   ├── results.html      # Search results (coming soon)
│   └── watch.html        # Video player (coming soon)
├── static/
│   └── style.css         # Styles
├── requirements.txt      # Python dependencies
├── vercel.json          # Vercel configuration
└── README.md            # This file
```

## Vercel Constraints

This project is designed to work within Vercel's free tier limits:

- ⏱️ 10-second execution timeout
- 💾 No persistent filesystem
- 🚫 No background workers
- 📦 Limited response size

## Development Roadmap

- [x] Feature #1: Home page with search
- [x] Feature #2: Search results page
- [x] Feature #3: Video watch page

**All core features complete!** 🎉

## License

MIT License - feel free to use this project for learning and portfolio purposes.
