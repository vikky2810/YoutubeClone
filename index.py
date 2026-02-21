from flask import Flask, render_template, request, redirect, url_for, jsonify, flash, abort
import yt_dlp
import re
import random
import os
import socket
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import mock_data
import invidious
import time
import json

# ─────────────────────────────────────────────────────────────────────
# THREE-TIER DATA SOURCE  (auto-selected per request, cached 60 s)
#
#  Tier 1 — yt-dlp        : YouTube DNS resolves  OR  VERCEL env set
#  Tier 2 — Invidious API : YouTube blocked, but Invidious reachable
#  Tier 3 — Static mock   : Everything offline (last resort only)
# ─────────────────────────────────────────────────────────────────────
_net_cache   = {'yt': None, 'inv': None, 'at': 0}
CACHE_TTL    = 60   # seconds

# ── Suggestion cache: {query: (timestamp, [results])} ──
_suggest_cache = {}
SUGGEST_TTL    = 300  # 5 minutes

# ── Trending pool cache ──
_trending_cache = {'videos': [], 'at': 0}
TRENDING_TTL    = 600   # 10 minutes — refresh once per session roughly
TRENDING_POOL   = 36    # fetch this many up-front; JS pages through in chunks of 12
TRENDING_PAGE   = 12    # videos per infinite-scroll page

def check_network():
    """Cached DNS check — returns True if YouTube is directly reachable."""
    global _net_cache
    now = time.time()
    if now - _net_cache['at'] < CACHE_TTL and _net_cache['yt'] is not None:
        return _net_cache['yt']
    try:
        socket.setdefaulttimeout(4)
        socket.getaddrinfo('www.youtube.com', 443)
        result = True
    except OSError:
        result = False
    _net_cache['yt'] = result
    _net_cache['at'] = now
    return result

def get_data_source():
    """
    Returns the backend to use for this request:
      'ytdlp'     — real yt-dlp calls (YouTube directly reachable)
      'invidious' — Invidious proxy API (YouTube blocked but Invidious ok)
      'mock'      — static hardcoded data (nothing works)
    """
    # Vercel always uses yt-dlp
    if os.environ.get('VERCEL'):
        return 'ytdlp'

    # Check YouTube directly
    if check_network():
        print("[ViewTube] Source: yt-dlp (YouTube reachable)")
        return 'ytdlp'

    # Check Invidious (cache result too)
    global _net_cache
    now = time.time()
    if _net_cache['inv'] is None or now - _net_cache['at'] >= CACHE_TTL:
        _net_cache['inv'] = invidious.is_available()
        _net_cache['at']  = now

    if _net_cache['inv']:
        print("[ViewTube] Source: Invidious proxy (YouTube blocked)")
        return 'invidious'

    print("[ViewTube] Source: static mock (all networks blocked)")
    return 'mock'

# Keep backward compat for any remaining call sites
def should_use_mock():
    return get_data_source() == 'mock'

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-viewtube-secret-key')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

def search_youtube(query, max_results=10):
    """
    Search YouTube using yt-dlp
    Returns a list of video dictionaries with metadata
    Limited to max_results to avoid Vercel timeout
    """
    print(f"Searching for: {query}")  # Debug log
    try:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': 'in_playlist',  # Fast extraction
            'force_generic_extractor': False,
            'noprogress': True,
            'check_formats': False,
            'ignoreerrors': True,
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
                        'channel_id': entry.get('channel_id', entry.get('uploader_id', '')),
                        'duration': invidious.fmt_dur(entry.get('duration', 0)),
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
        raise e  # Propagate error so caller can handle it or show 500


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
                        'channel_id': entry.get('channel_id', entry.get('uploader_id', '')),
                        'duration': invidious.fmt_dur(entry.get('duration', 0)),
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

def get_channel_videos(channel_id):
    """
    Get videos from a specific channel
    Returns tuple (videos, channel_info)
    """
    print(f"Fetching videos for channel: {channel_id}")
    try:
        ydl_opts = {
            'quiet': False,
            'no_warnings': False,
            'extract_flat': True,
            'format': 'best',
            'ignoreerrors': True,
            'playlistend': 30, # Limit to 30 latest videos
        }
        
        # Use channel URL format
        if channel_id.startswith('UC'):
            url = f"https://www.youtube.com/channel/{channel_id}"
        elif channel_id.startswith('@'):
             url = f"https://www.youtube.com/{channel_id}"
        else:
            # Fallback try user or channel
            url = f"https://www.youtube.com/channel/{channel_id}"
            
        print(f"Channel URL: {url}")
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            result = ydl.extract_info(url, download=False)
            
            if not result:
                return [], {}

            # Extract channel info from result
            channel_info = {
                'title': result.get('channel', result.get('uploader', result.get('title', 'Channel'))),
                'description': result.get('description', ''),
                'thumbnail': None,
                'banner': None
            }

            # Try to find channel avatar in thumbnails
            # For channels, thumbnails usually contains avatars
            thumbnails = result.get('thumbnails', [])
            if thumbnails:
                # Get the last one (usually highest quality)
                channel_info['thumbnail'] = thumbnails[-1].get('url')
            elif result.get('thumbnail'):
                channel_info['thumbnail'] = result.get('thumbnail')
                
            entries = result.get('entries', [])
            if not entries:
                return [], channel_info
            
            videos = []
            
            def process_entry(entry):
                """Helper to extract video data from an entry"""
                if not entry:
                    return None
                    
                video = {
                    'id': entry.get('id', ''),
                    'title': entry.get('title', 'Untitled'),
                    'thumbnail': entry.get('thumbnail', entry.get('thumbnails', [{}])[0].get('url', '')),
                    'channel': entry.get('uploader', entry.get('channel', 'Unknown')),
                    'channel_id': channel_id,
                    'duration': format_duration(entry.get('duration', 0)),
                    'view_count': format_views(entry.get('view_count', 0)),
                    'upload_date': format_date(entry.get('upload_date', '')), # Add date if available
                    'url': f"https://www.youtube.com/watch?v={entry.get('id', '')}"
                }
                return video

            for entry in entries:
                if entry:
                    entry_type = entry.get('_type')
                    # If it's a playlist (e.g. "Videos" tab, "Live" tab), iterate through its contents
                    if entry_type == 'playlist':
                        print(f"Processing playlist: {entry.get('title')}")
                        playlist_entries = entry.get('entries', [])
                        # Handle if entries is a generator or list
                        for sub_entry in playlist_entries:
                            v = process_entry(sub_entry)
                            if v and v['id']:
                                videos.append(v)
                    # If it's a direct video entry
                    elif entry_type == 'url' or entry.get('id'):
                         v = process_entry(entry)
                         if v and v['id']:
                             videos.append(v)
            
            # Remove duplicates based on ID
            unique_videos = []
            seen_ids = set()
            for v in videos:
                if v['id'] not in seen_ids:
                    unique_videos.append(v)
                    seen_ids.add(v['id'])
            
            print(f"Found {len(unique_videos)} unique videos")
            
            # Try to fetch dates from RSS feed if we have a valid channel ID
            # Use the channel_id from the first video if available, as it's likely the UC ID
            if unique_videos:
                target_channel_id = unique_videos[0].get('channel_id')
                if not target_channel_id or not target_channel_id.startswith('UC'):
                    target_channel_id = channel_id
                
                if target_channel_id and target_channel_id.startswith('UC'):
                    print(f"Fetching RSS dates for {target_channel_id}...")
                    rss_dates = fetch_channel_dates_rss(target_channel_id)
                    if rss_dates:
                        print(f"Found {len(rss_dates)} dates from RSS")
                        for video in unique_videos:
                            if video['id'] in rss_dates:
                                video['upload_date'] = format_date(rss_dates[video['id']])
            
            return unique_videos, channel_info
            
    except Exception as e:
        print(f"Error fetching channel videos: {e}")
        return [], {}

def get_channel_avatar(channel_id):
    """
    Fetch channel avatar URL separately using yt-dlp
    """
    try:
        # Use channel URL format
        if channel_id.startswith('UC'):
            url = f"https://www.youtube.com/channel/{channel_id}"
        elif channel_id.startswith('@'):
             url = f"https://www.youtube.com/{channel_id}"
        else:
            url = f"https://www.youtube.com/channel/{channel_id}"
            
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True,
            'playlist_items': '0', # Don't fetch any videos, just metadata
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print(f"Fetching avatar info from: {url}")
            info = ydl.extract_info(url, download=False)
            
            # Try to find channel avatar in thumbnails
            thumbnails = info.get('thumbnails', [])
            if thumbnails:
                return thumbnails[-1].get('url')
                
            return info.get('thumbnail')
            
    except Exception as e:
        print(f"Error fetching channel avatar: {e}")
        return None

def fetch_channel_dates_rss(channel_id):
    """
    Fetch upload dates from YouTube RSS feed
    Returns dict {video_id: iso_date_string}
    """
    try:
        url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        
        with urllib.request.urlopen(req, timeout=5) as response:
            xml_data = response.read()
            root = ET.fromstring(xml_data)
            
            # Namespace map usually needed for findall with default ns
            ns = {'atom': 'http://www.w3.org/2005/Atom', 'yt': 'http://www.youtube.com/xml/schemas/2015'}
            
            dates = {}
            # Find all entries using namespace
            for entry in root.findall('atom:entry', ns):
                video_id_elem = entry.find('yt:videoId', ns)
                published_elem = entry.find('atom:published', ns)
                
                if video_id_elem is not None and published_elem is not None:
                    dates[video_id_elem.text] = published_elem.text
                    
            return dates
    except Exception as e:
        print(f"Error fetching RSS dates: {e}")
        return {}

def get_trending_videos(max_results=15):
    """
    Fetch niche developer / coding content instead of generic regional trending.
    Picks 3 random topics, fetches a few results from each, then merges & shuffles
    so every home page load feels fresh.
    """
    print("Fetching niche trending videos...")

    # Re-use the single source of truth defined in invidious.py
    selected = random.sample(invidious.NICHE_TOPICS, k=3)
    per_topic = max(5, max_results // 3)

    all_videos = []
    seen_ids   = set()

    for topic in selected:
        print(f"  → Fetching: '{topic}'")
        try:
            results = search_youtube(topic, max_results=per_topic)
            for v in (results or []):
                if v.get('id') not in seen_ids:
                    seen_ids.add(v['id'])
                    all_videos.append(v)
        except Exception as e:
            print(f"  → Error for '{topic}': {e}")

    random.shuffle(all_videos)
    return all_videos[:max_results]

@app.route('/api/trending')
def trending():
    """
    API endpoint for trending/home-page videos.
    Supports ?offset=N for infinite scroll.

    Server-side pool cache:
      • On first call (offset=0 or cache stale) fetches TRENDING_POOL videos
        via the 3-tier fallback and stores them for TRENDING_TTL seconds.
      • Subsequent calls slice the cached pool — zero extra API calls.
      • Returns [] when offset ≥ pool size (signals end-of-feed to JS).
    """
    global _trending_cache
    offset = int(request.args.get('offset', 0))
    now    = time.time()

    # Refresh the pool if stale or empty
    if not _trending_cache['videos'] or now - _trending_cache['at'] >= TRENDING_TTL:
        source = get_data_source()
        videos = None

        if source == 'ytdlp':
            try:
                videos = get_trending_videos(max_results=TRENDING_POOL)
            except Exception as e:
                print(f"[yt-dlp] trending error: {e}")
            if not videos:
                source = 'invidious'

        if source == 'invidious':
            videos = invidious.get_trending(max_results=TRENDING_POOL)
            if not videos:
                source = 'mock'

        if source == 'mock' or not videos:
            videos = mock_data.get_mock_trending()

        _trending_cache['videos'] = videos
        _trending_cache['at']     = now
        print(f"[Trending] Cache refreshed: {len(videos)} videos")

    pool = _trending_cache['videos']
    page = pool[offset : offset + TRENDING_PAGE]
    return jsonify(page)


@app.route('/api/autocomplete')
def autocomplete():
    """
    API endpoint for search autocomplete — uses Google's YouTube suggestion
    API (same source as the real YouTube search bar, near-instant).
    """
    query = request.args.get('q', '').strip()

    if not query or len(query) < 2:
        return jsonify([])

    suggestions = get_search_suggestions(query)
    return jsonify(suggestions)

# ── Channel avatar cache: {channel_id: (timestamp, url_or_None)} ──
_avatar_cache = {}
AVATAR_TTL = 600  # 10 minutes

@app.route('/api/channel-avatar')
def channel_avatar():
    """
    Fetch and redirect to a YouTube channel's avatar image.
    Cached in-memory to avoid repeated yt-dlp calls.
    Returns 302 redirect to the avatar URL, or 404 if unavailable.
    """
    channel_id = request.args.get('channel_id', '').strip()
    if not channel_id:
        abort(404)

    now = time.time()

    # Return cached result if still fresh
    cached = _avatar_cache.get(channel_id)
    if cached:
        ts, avatar_url = cached
        if now - ts < AVATAR_TTL:
            if avatar_url:
                return redirect(avatar_url)
            abort(404)

    avatar_url = None
    source = get_data_source()

    # Tier 1: yt-dlp
    if source == 'ytdlp':
        try:
            avatar_url = get_channel_avatar(channel_id)
        except Exception as e:
            print(f"[Avatar] yt-dlp error for {channel_id}: {e}")

    # Tier 2: Invidious
    if not avatar_url and source in ('ytdlp', 'invidious'):
        try:
            _, ch_info = invidious.get_channel(channel_id)
            avatar_url = ch_info.get('thumbnail') or ch_info.get('authorThumbnails', [{}])[-1].get('url')
        except Exception as e:
            print(f"[Avatar] Invidious error for {channel_id}: {e}")

    _avatar_cache[channel_id] = (now, avatar_url)

    if avatar_url:
        return redirect(avatar_url)
    abort(404)



@app.route('/api/search-more')
def search_more():
    """Infinite scroll — load more results with 3-tier fallback."""
    query  = request.args.get('q', '').strip()
    offset = int(request.args.get('offset', 0))
    if not query:
        return jsonify({'videos': []})

    source = get_data_source()

    if source == 'ytdlp':
        try:
            videos = search_youtube_with_offset(query, offset, max_results=10)
            return jsonify({'videos': videos or []})
        except Exception as e:
            print(f"[yt-dlp] search-more error: {e}")
            source = 'invidious'

    if source == 'invidious':
        videos = invidious.search(query, max_results=10)
        if videos:
            page = videos[offset:offset + 10]
            return jsonify({'videos': page})
        source = 'mock'

    results   = mock_data.get_mock_search(query)
    page      = results[offset:offset + 10] if offset < len(results) else []
    return jsonify({'videos': page})


def get_search_suggestions(query):
    """
    Fetch YouTube search suggestions via Google's suggestion API.
    Same data source the real YouTube search bar uses — responds in <100 ms.
    Results are cached for 5 minutes to avoid redundant network calls.
    """
    global _suggest_cache
    query_lower = query.lower()

    # Return cached result if still fresh
    cached = _suggest_cache.get(query_lower)
    if cached:
        ts, results = cached
        if time.time() - ts < SUGGEST_TTL:
            return results

    try:
        # Google's YouTube suggestion endpoint (same one the real YT bar uses)
        params = urllib.parse.urlencode({
            'client': 'firefox',
            'ds':     'yt',
            'q':      query,
        })
        url = f"https://suggestqueries.google.com/complete/search?{params}"
        req = urllib.request.Request(
            url,
            headers={'User-Agent': 'Mozilla/5.0', 'Accept': 'application/json'}
        )
        with urllib.request.urlopen(req, timeout=3) as resp:
            data = json.loads(resp.read().decode())
            # Response format: ["query", ["suggestion1", "suggestion2", ...]]
            suggestions = data[1][:8] if len(data) > 1 else []

        _suggest_cache[query_lower] = (time.time(), suggestions)
        return suggestions

    except Exception as e:
        print(f"[Autocomplete] Suggestion API error: {e}")
        return []


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
    """Home page with search input and trending videos"""
    # Don't fetch videos synchronously to avoid blocking page load
    # client-side JS will fetch from /api/trending
    return render_template('home.html', videos=[])

@app.route('/search')
def search():
    """Search results page — 3-tier fallback."""
    query = request.args.get('q', '').strip()
    if not query:
        return redirect(url_for('home'))

    source = get_data_source()

    if source == 'ytdlp':
        try:
            videos = search_youtube(query, max_results=10)
            if videos:
                return render_template('results.html', query=query, videos=videos)
        except Exception as e:
            print(f"[yt-dlp] search error: {e}")
        source = 'invidious'

    if source == 'invidious':
        videos = invidious.search(query, max_results=10)
        if videos:
            return render_template('results.html', query=query, videos=videos)
        source = 'mock'

    videos = mock_data.get_mock_search(query)
    return render_template('results.html', query=query, videos=videos)


@app.route('/watch')
def watch():
    """Watch page — 3-tier fallback."""
    video_id = request.args.get('v', '')
    if not video_id:
        return redirect(url_for('home'))

    source = get_data_source()

    if source == 'ytdlp':
        try:
            video_data = get_video_info(video_id)
            if video_data:
                return render_template('watch.html', video=video_data)
        except Exception as e:
            print(f"[yt-dlp] watch error: {e}")
        source = 'invidious'

    if source == 'invidious':
        video_data = invidious.get_video_info(video_id)
        if video_data:
            return render_template('watch.html', video=video_data)
        source = 'mock'

    video_data = mock_data.get_mock_video_info(video_id)
    return render_template('watch.html', video=video_data)


@app.route('/channel/<channel_id>')
def channel(channel_id):
    """Channel page — 3-tier fallback."""
    if not channel_id:
        return redirect(url_for('home'))

    channel_name_param = request.args.get('name', '')
    source = get_data_source()

    if source == 'ytdlp':
        try:
            videos, channel_info = get_channel_videos(channel_id)
            if videos:
                channel_name = channel_info.get('title') or channel_name_param or 'Channel'
                if channel_name == 'Channel' and videos:
                    channel_name = videos[0].get('channel', 'Channel')
                return render_template('channel.html',
                                       channel_id=channel_id,
                                       channel_name=channel_name,
                                       channel_thumbnail=channel_info.get('thumbnail'),
                                       videos=videos)
        except Exception as e:
            print(f"[yt-dlp] channel error: {e}")
        source = 'invidious'

    if source == 'invidious':
        videos, channel_info = invidious.get_channel(channel_id)
        if videos:
            channel_name = channel_info.get('title') or channel_name_param or 'Channel'
            return render_template('channel.html',
                                   channel_id=channel_id,
                                   channel_name=channel_name,
                                   channel_thumbnail=channel_info.get('thumbnail', ''),
                                   videos=videos)
        source = 'mock'

    videos, channel_info = mock_data.get_mock_channel(channel_id)
    channel_name = channel_name_param or channel_info.get('title', 'Demo Channel')
    return render_template('channel.html',
                           channel_id=channel_id,
                           channel_name=channel_name,
                           channel_thumbnail=channel_info.get('thumbnail', ''),
                           videos=videos)



def get_video_info(video_id):
    """
    Get detailed video information using yt-dlp
    Returns video metadata dictionary
    """
    print(f"Fetching video info for ID: {video_id}")  # Debug
    try:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'get_comments': False, # Extremely slow, disable by default
            'extract_flat': False,
            'skip_download': True,
            'ignoreerrors': True,
        }
        
        url = f"https://www.youtube.com/watch?v={video_id}"
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            if not info:
                print("ERROR: No info returned from yt-dlp")
                return None
            
            print(f"Successfully fetched info for: {info.get('title', 'Unknown')}")
            
            # Find the best progressive video (video + audio)
            video_url = None
            formats = info.get('formats', [])
            
            # Sort formats by resolution (height) descending to get best quality first
            # Filter for mp4, video and audio present
            progressive_formats = [
                f for f in formats 
                if f.get('ext') == 'mp4' 
                and f.get('vcodec') != 'none' 
                and f.get('acodec') != 'none'
            ]
            
            # Sort by height (quality)
            progressive_formats.sort(key=lambda x: x.get('height') or 0, reverse=True)
            
            if progressive_formats:
                video_url = progressive_formats[0]['url']
                print(f"Found progressive MP4 video URL: {progressive_formats[0].get('format_id')}")
            else:
                print("No progressive MP4 format found. Falling back to iframe.")
            
            # Extract video data
            video = {
                'id': video_id,
                'title': info.get('title', 'Untitled'),
                'channel': info.get('uploader', 'Unknown'),
                'channel_id': info.get('channel_id', info.get('uploader_id', '')),
                'channel_url': info.get('uploader_url', '#'),
                'channel_thumbnail': info.get('channel_thumbnail') or info.get('uploader_avatar') or info.get('avatar', ''),
                'view_count': format_views(info.get('view_count', 0)),
                'like_count': format_number(info.get('like_count', 0)),
                'upload_date': format_date(info.get('upload_date', '')),
                'description': info.get('description', 'No description available'),
                'thumbnail': info.get('thumbnail', ''),
                'duration': format_duration(info.get('duration', 0)),
                'video_url': video_url,
                'comments': extract_comments(info.get('comments', [])),
            }
            
            # Fetch channel avatar specifically if we didn't get it
            if not video.get('channel_thumbnail') and video.get('channel_id'):
                print(f"Fetching separate avatar for channel: {video['channel_id']}")
                video['channel_thumbnail'] = get_channel_avatar(video['channel_id'])
            
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
    """Format date from YYYYMMDD or ISO format to readable format"""
    if not date_str:
        return "Unknown date"
        
    try:
        # Handle ISO format (YYYY-MM-DD...)
        if '-' in date_str:
            if 'T' in date_str:
                date_str = date_str.split('T')[0]
            
            parts = date_str.split('-')
            if len(parts) == 3:
                year, month, day = parts
                months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                          'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
                month_name = months[int(month) - 1]
                return f"{month_name} {int(day)}, {year}"

        # Handle YYYYMMDD
        if len(date_str) == 8 and date_str.isdigit():
            year = date_str[0:4]
            month = date_str[4:6]
            day = date_str[6:8]
            
            months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                      'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
            month_name = months[int(month) - 1]
            
            return f"{month_name} {int(day)}, {year}"
            
        return "Unknown date"
    except Exception:
        return "Unknown date"

def extract_comments(comments_data):
    """Extract and format top comments"""
    if not comments_data:
        return []
        
    formatted_comments = []
    # Limit to top 20 comments to keep it light
    for comment in comments_data[:20]:
        try:
            formatted_comments.append({
                'author': comment.get('author', 'Anonymous'),
                'author_thumbnail': comment.get('author_thumbnail', ''),
                'text': comment.get('text', ''),
                'like_count': format_number(comment.get('like_count', 0)),
                'id': comment.get('id', ''),
                'timestamp': comment.get('timestamp', 0)
            })
        except Exception as e:
            print(f"Error parsing comment: {e}")
            continue
            
    return formatted_comments

# Export the app for Vercel
# This is required for Vercel's serverless function handler
application = app

# For local development
if __name__ == '__main__':
    app.run(debug=True, port=5000)
