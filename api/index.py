from flask import Flask, render_template, request, redirect, url_for, jsonify
import yt_dlp
import re

app = Flask(__name__, template_folder='../templates', static_folder='../static')

def search_youtube(query, max_results=10):
    """
    Search YouTube using yt-dlp
    Returns a list of video dictionaries with metadata
    Limited to max_results to avoid Vercel timeout
    """
    print(f"Searching for: {query}")  # Debug log
    try:
        ydl_opts = {
            'quiet': False,  # Show output for debugging
            'no_warnings': False,
            'extract_flat': True,  # Don't download, just get metadata
            'format': 'best',
            'ignoreerrors': True,  # Continue on errors
        }
        
        # IMPORTANT: Use ytsearch prefix for YouTube search
        search_query = f"ytsearch{max_results}:{query}"
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print(f"Extracting info for query: {search_query}")  # Debug
            result = ydl.extract_info(search_query, download=False)
            
            if not result:
                print("No result returned from yt-dlp")
                return []
            
            if 'entries' not in result:
                print(f"No entries in result. Keys: {result.keys()}")
                return []
            
            videos = []
            for entry in result['entries']:
                if entry:
                    # Extract video data
                    video = {
                        'id': entry.get('id', ''),
                        'title': entry.get('title', 'Untitled'),
                        'thumbnail': entry.get('thumbnail', entry.get('thumbnails', [{}])[0].get('url', '')),
                        'channel': entry.get('uploader', entry.get('channel', 'Unknown')),
                        'duration': format_duration(entry.get('duration', 0)),
                        'view_count': format_views(entry.get('view_count', 0)),
                        'url': f"https://www.youtube.com/watch?v={entry.get('id', '')}"
                    }
                    videos.append(video)
                    print(f"Added video: {video['title']}")  # Debug
            
            print(f"Total videos found: {len(videos)}")  # Debug
            return videos
    
    except Exception as e:
        print(f"Error searching YouTube: {e}")
        import traceback
        traceback.print_exc()
        return []

def search_youtube_with_offset(query, offset=0, max_results=10):
    """
    Search YouTube with pagination support
    Fetches results starting from offset
    """
    print(f"Searching with offset {offset} for: {query}")
    try:
        # Calculate how many total results we need
        total_needed = offset + max_results
        
        ydl_opts = {
            'quiet': False,
            'no_warnings': False,
            'extract_flat': True,
            'format': 'best',
            'ignoreerrors': True,
        }
        
        # Fetch more results than needed to account for offset
        search_query = f"ytsearch{total_needed}:{query}"
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print(f"Extracting info for query: {search_query}")
            result = ydl.extract_info(search_query, download=False)
            
            if not result or 'entries' not in result:
                return []
            
            videos = []
            for entry in result['entries']:
                if entry:
                    video = {
                        'id': entry.get('id', ''),
                        'title': entry.get('title', 'Untitled'),
                        'thumbnail': entry.get('thumbnail', entry.get('thumbnails', [{}])[0].get('url', '')),
                        'channel': entry.get('uploader', entry.get('channel', 'Unknown')),
                        'duration': format_duration(entry.get('duration', 0)),
                        'view_count': format_views(entry.get('view_count', 0)),
                        'url': f"https://www.youtube.com/watch?v={entry.get('id', '')}"
                    }
                    videos.append(video)
            
            # Return only the slice we need (from offset to offset+max_results)
            paginated_videos = videos[offset:offset + max_results]
            print(f"Returning {len(paginated_videos)} videos from offset {offset}")
            return paginated_videos
    
    except Exception as e:
        print(f"Error searching YouTube with offset: {e}")
        import traceback
        traceback.print_exc()
        return []

@app.route('/api/autocomplete')
def autocomplete():
    """
    API endpoint for search autocomplete suggestions
    """
    query = request.args.get('q', '').strip()
    
    if not query or len(query) < 2:
        return jsonify([])
    
    try:
        # Use yt-dlp to get search suggestions
        # We'll do a quick search and return video titles as suggestions
        suggestions = get_search_suggestions(query)
        return jsonify(suggestions)
    except Exception as e:
        print(f"Autocomplete error: {e}")
        return jsonify([])

@app.route('/api/search-more')
def search_more():
    """
    API endpoint for infinite scroll - load more search results
    """
    query = request.args.get('q', '').strip()
    offset = int(request.args.get('offset', 0))
    
    if not query:
        return jsonify({'videos': []})
    
    try:
        # Fetch 10 more results starting from offset
        videos = search_youtube_with_offset(query, offset, max_results=10)
        return jsonify({'videos': videos})
    except Exception as e:
        print(f"Search more error: {e}")
        return jsonify({'videos': [], 'error': str(e)})

def get_search_suggestions(query):
    """
    Get search suggestions based on query
    Returns a list of suggestion strings
    """
    try:
        # Quick search for 5 results to generate suggestions
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True,
            'ignoreerrors': True,
        }
        
        # Use ytsearch prefix
        search_query = f"ytsearch5:{query}"
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            result = ydl.extract_info(search_query, download=False)
            
            if not result or 'entries' not in result:
                return []
            
            suggestions = []
            seen = set()
            
            for entry in result['entries']:
                if entry and entry.get('title'):
                    title = entry['title']
                    # Add the full title
                    if title not in seen:
                        suggestions.append(title)
                        seen.add(title)
                    
                    # Also add the channel name as a suggestion
                    channel = entry.get('uploader', entry.get('channel'))
                    if channel and channel not in seen and len(suggestions) < 8:
                        suggestions.append(channel)
                        seen.add(channel)
            
            return suggestions[:8]  # Limit to 8 suggestions
    
    except Exception as e:
        print(f"Error getting suggestions: {e}")
        return []


def format_duration(seconds):
    """Convert seconds to MM:SS or HH:MM:SS format"""
    if not seconds:
        return "0:00"
    
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    
    if hours > 0:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    else:
        return f"{minutes}:{secs:02d}"

def format_views(count):
    """Format view count to readable format (e.g., 1.2M, 45K)"""
    if not count:
        return "0 views"
    
    if count >= 1_000_000:
        return f"{count / 1_000_000:.1f}M views"
    elif count >= 1_000:
        return f"{count / 1_000:.1f}K views"
    else:
        return f"{count} views"

@app.route('/')
def home():
    """Home page with search input"""
    return render_template('home.html')

@app.route('/search')
def search():
    """Search results page"""
    query = request.args.get('q', '').strip()
    if not query:
        return redirect(url_for('home'))
    
    # Search YouTube (limited to 10 results for Vercel safety)
    videos = search_youtube(query, max_results=10)
    
    return render_template('results.html', query=query, videos=videos)

@app.route('/watch')
def watch():
    """Watch page with video player"""
    video_id = request.args.get('v', '')
    if not video_id:
        return redirect(url_for('home'))
    
    # Simply pass the video ID to the template
    # The iframe will handle the video playback
    # We'll use basic info without fetching metadata to avoid bot detection
    video_data = {
        'id': video_id,
        'title': 'Video Player',  # Simple title
        'channel': 'YouTube',
        'view_count': '',
        'like_count': '',
        'upload_date': '',
        'description': 'Watch this video on ViewTube - a privacy-focused YouTube frontend.',
    }
    
    return render_template('watch.html', video=video_data)


def get_video_info(video_id):
    """
    Get detailed video information using yt-dlp
    Returns video metadata dictionary
    """
    print(f"Fetching video info for ID: {video_id}")  # Debug
    try:
        ydl_opts = {
            'quiet': False,  # Show output for debugging
            'no_warnings': False,
            'format': 'best',
        }
        
        url = f"https://www.youtube.com/watch?v={video_id}"
        print(f"URL: {url}")  # Debug
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            if not info:
                print("ERROR: No info returned from yt-dlp")
                return None
            
            print(f"Successfully fetched info for: {info.get('title', 'Unknown')}")  # Debug
            
            # Extract video data
            video = {
                'id': video_id,
                'title': info.get('title', 'Untitled'),
                'channel': info.get('uploader', 'Unknown'),
                'channel_url': info.get('uploader_url', '#'),
                'view_count': format_views(info.get('view_count', 0)),
                'like_count': format_number(info.get('like_count', 0)),
                'upload_date': format_date(info.get('upload_date', '')),
                'description': info.get('description', 'No description available'),
                'thumbnail': info.get('thumbnail', ''),
                'duration': format_duration(info.get('duration', 0)),
            }
            
            return video
    
    except Exception as e:
        print(f"ERROR fetching video info: {e}")
        import traceback
        traceback.print_exc()
        return None

def format_number(num):
    """Format numbers to readable format (e.g., 1.2M, 45K)"""
    if not num:
        return "0"
    
    if num >= 1_000_000:
        return f"{num / 1_000_000:.1f}M"
    elif num >= 1_000:
        return f"{num / 1_000:.1f}K"
    else:
        return str(num)

def format_date(date_str):
    """Format date from YYYYMMDD to readable format"""
    if not date_str or len(date_str) != 8:
        return "Unknown date"
    
    try:
        year = date_str[0:4]
        month = date_str[4:6]
        day = date_str[6:8]
        
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                  'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        month_name = months[int(month) - 1]
        
        return f"{month_name} {int(day)}, {year}"
    except:
        return "Unknown date"

# Export the app for Vercel
# This is required for Vercel's serverless function handler
application = app

# For local development
if __name__ == '__main__':
    app.run(debug=True, port=5000)
