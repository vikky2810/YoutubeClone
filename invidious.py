"""
invidious.py — Dynamic YouTube data via Invidious public APIs.

Priority order:
  1. Invidious API (iv.melmac.space and mirrors) — confirmed working
  2. Returns None  →  caller falls back to static mock

API docs:
  Invidious: https://docs.invidious.io/api/
"""

import json
import socket
import urllib.request
import urllib.parse
from concurrent.futures import ThreadPoolExecutor, as_completed

TIMEOUT = 3   # seconds per attempt — fail fast, move to next


# ─────────────────────────────────────────────────────────────────────
# Piped instances — all confirmed dead on most networks (2026-02-21)
# Left empty so the Piped tier is skipped instantly with no retries.
# ─────────────────────────────────────────────────────────────────────
PIPED_INSTANCES = []

# ─────────────────────────────────────────────────────────────────────
# Invidious instances — only confirmed-working hosts (2026-02-21)
# ─────────────────────────────────────────────────────────────────────
INVIDIOUS_INSTANCES = [
    "https://iv.melmac.space",          # ✅ confirmed working
    "https://invidious.fdn.fr",         # reliable EU backup
    "https://inv.tux.pizza",            # fallback
]

_inv_instance = None   # cached working Invidious instance

# ─────────────────────────────────────────────────────────────────────
# Niche topic pool — used for home page "trending" on all tiers
# ─────────────────────────────────────────────────────────────────────
NICHE_TOPICS = [
    # Core programming
    "programming tutorial project build",
    "debugging error fixing coding tips",
    "data structures algorithms explained",
    "system design backend architecture",
    # College-relevant
    "final year college project walkthrough",
    "open source github project code review",
    # Applied AI
    "AI automation practical project tutorial",
    "machine learning project from scratch",
    # Tools & career
    "developer tools productivity workflow",
    "realistic tech career guidance software engineer",
    # Long-form learning
    "full course programming beginner to advanced",
    "software engineering fundamentals explained",
    # Specific hot topics
    "REST API backend project tutorial",
    "database SQL NoSQL design explained",
    "clean code refactoring best practices",
    "git github workflow developers",
    "docker containerization beginner tutorial",
    "competitive programming problem solving",
    "DSA interview preparation coding",
    "web development full stack project",
]


# ─────────────────────────────────────────────────────────────────────
# Low-level HTTP helper
# ─────────────────────────────────────────────────────────────────────

def _http_get(url):
    """Fetch URL and return parsed JSON, or raise on failure."""
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (ViewTube/1.0; +https://github.com/viewtube)",
            "Accept": "application/json",
        }
    )
    with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
        return json.loads(r.read().decode())


def _try_instances(instances, path, params=None, cache_attr=None):
    """
    Try each instance until one works. Returns (base_url, data) or (None, None).
    cache_attr: name of module-level variable to cache the working instance.
    """
    global _piped_instance, _inv_instance

    qs = ("?" + urllib.parse.urlencode(params)) if params else ""

    # Build trial list: cached instance first, then rest
    cached = globals().get(cache_attr) if cache_attr else None
    trial  = ([cached] + [i for i in instances if i != cached]) if cached else instances

    for base in trial:
        url = base + path + qs
        try:
            data = _http_get(url)
            if cache_attr:
                globals()[cache_attr] = base
            print(f"[Proxy] OK  {base}")
            return base, data
        except Exception as e:
            print(f"[Proxy] FAIL {base}: {e}")
            if cached == base and cache_attr:
                globals()[cache_attr] = None   # invalidate
            continue

    return None, None


# ─────────────────────────────────────────────────────────────────────
# Helpers — format
# ─────────────────────────────────────────────────────────────────────

def _fmt_dur(seconds):
    if not seconds:
        return ""
    s = int(seconds)
    h, rem = divmod(s, 3600)
    m, sec = divmod(rem, 60)
    return f"{h}:{m:02d}:{sec:02d}" if h else f"{m}:{sec:02d}"


def _fmt_views(n):
    if not n:
        return "0 views"
    n = int(n)
    if n >= 1_000_000:
        return f"{n/1_000_000:.1f}M views"
    if n >= 1_000:
        return f"{n/1_000:.0f}K views"
    return f"{n} views"


def _thumb(vid_id):
    return f"https://i.ytimg.com/vi/{vid_id}/hqdefault.jpg"


def _extract_id(url_or_id):
    """Extract video ID from a /watch?v=... URL or return as-is."""
    if url_or_id and "watch?v=" in url_or_id:
        return url_or_id.split("watch?v=")[-1].split("&")[0]
    return url_or_id or ""


# ─────────────────────────────────────────────────────────────────────
# Piped API  →  our video format
# ─────────────────────────────────────────────────────────────────────

def _piped_video(entry):
    vid_id = _extract_id(entry.get("url", ""))
    return {
        "id":          vid_id,
        "title":       entry.get("title", "Untitled"),
        "channel":     entry.get("uploaderName", "Unknown"),
        "channel_id":  _extract_id(entry.get("uploaderUrl", "")),
        "thumbnail":   entry.get("thumbnail") or _thumb(vid_id),
        "duration":    _fmt_dur(entry.get("duration", 0)),
        "view_count":  _fmt_views(entry.get("views", 0)),
        "upload_date": "",
    }


def _piped_trending(max_results=12):
    """Piped instances are currently unavailable — skip immediately."""
    if not PIPED_INSTANCES:
        return None
    import random
    selected  = random.sample(NICHE_TOPICS, k=3)
    per_topic = max(5, max_results // 3)
    all_videos, seen = [], set()
    for topic in selected:
        print(f"  [Piped] trending topic: '{topic}'")
        _, data = _try_instances(PIPED_INSTANCES, "/search",
                                 {"q": topic, "filter": "videos"}, "_piped_instance")
        if data and "items" in data:
            for v in data["items"][:per_topic]:
                vid = _piped_video(v)
                if vid["id"] and vid["id"] not in seen:
                    seen.add(vid["id"])
                    all_videos.append(vid)
    random.shuffle(all_videos)
    return all_videos[:max_results] or None


def _piped_search(query, max_results=10):
    _, data = _try_instances(PIPED_INSTANCES, "/search",
                             {"q": query, "filter": "videos"}, "_piped_instance")
    if not data or "items" not in data:
        return None
    videos = [_piped_video(v) for v in data["items"][:max_results] if v.get("url")]
    return videos or None


def _piped_video_info(video_id):
    _, data = _try_instances(PIPED_INSTANCES, f"/streams/{video_id}",
                             cache_attr="_piped_instance")
    if not data:
        return None

    # Best mp4 stream
    video_url = None
    for stream in data.get("videoStreams", []):
        if stream.get("mimeType", "").startswith("video/mp4") and stream.get("videoOnly") is False:
            video_url = stream.get("url")
            break
    if not video_url:
        for stream in data.get("videoStreams", []):
            if "mp4" in stream.get("mimeType", ""):
                video_url = stream.get("url")
                break

    return {
        "id":               video_id,
        "title":            data.get("title", "Untitled"),
        "channel":          data.get("uploader", "Unknown"),
        "channel_id":       _extract_id(data.get("uploaderUrl", "")),
        "channel_url":      data.get("uploaderUrl", "#"),
        "channel_thumbnail":data.get("uploaderAvatar", ""),
        "thumbnail":        data.get("thumbnailUrl") or _thumb(video_id),
        "duration":         _fmt_dur(data.get("duration", 0)),
        "view_count":       _fmt_views(data.get("views", 0)),
        "like_count":       _fmt_views(data.get("likes", 0)).replace(" views", ""),
        "upload_date":      data.get("uploadDate", ""),
        "description":      data.get("description", ""),
        "video_url":        video_url,
        "comments":         [],
    }


# ─────────────────────────────────────────────────────────────────────
# Invidious API  →  our video format  (fallback tier)
# ─────────────────────────────────────────────────────────────────────

def _inv_video(entry):
    vid_id = entry.get("videoId", "")
    return {
        "id":          vid_id,
        "title":       entry.get("title", "Untitled"),
        "channel":     entry.get("author", "Unknown"),
        "channel_id":  entry.get("authorId", ""),
        "thumbnail":   _thumb(vid_id),
        "duration":    _fmt_dur(entry.get("lengthSeconds", 0)),
        "view_count":  _fmt_views(entry.get("viewCount", 0)),
        "upload_date": "",
    }


def _inv_trending(max_results=12):
    """Search niche dev topics via Invidious — topics fetched in parallel."""
    import random
    selected  = random.sample(NICHE_TOPICS, k=3)
    per_topic = max(5, max_results // 3)

    def _fetch_topic(topic):
        print(f"  [Invidious] trending topic: '{topic}'")
        _, data = _try_instances(INVIDIOUS_INSTANCES, "/api/v1/search",
                                 {"q": topic, "type": "video"}, "_inv_instance")
        if data and isinstance(data, list):
            return [_inv_video(v) for v in data[:per_topic] if v.get("videoId")]
        return []

    all_videos, seen = [], set()
    with ThreadPoolExecutor(max_workers=3) as pool:
        futures = {pool.submit(_fetch_topic, t): t for t in selected}
        for fut in as_completed(futures):
            for vid in (fut.result() or []):
                if vid["id"] and vid["id"] not in seen:
                    seen.add(vid["id"])
                    all_videos.append(vid)

    random.shuffle(all_videos)
    return all_videos[:max_results] or None


def _inv_search(query, max_results=10):
    _, data = _try_instances(INVIDIOUS_INSTANCES, "/api/v1/search",
                             {"q": query, "type": "video"}, "_inv_instance")
    if not data or not isinstance(data, list):
        return None
    videos = [_inv_video(v) for v in data[:max_results] if v.get("videoId")]
    return videos or None


def _inv_video_info(video_id):
    _, data = _try_instances(INVIDIOUS_INSTANCES, f"/api/v1/videos/{video_id}",
                             cache_attr="_inv_instance")
    if not data:
        return None
    vid_id = data.get("videoId", video_id)
    video_url = None
    for fmt in data.get("formatStreams", []):
        if fmt.get("container") == "mp4":
            video_url = fmt.get("url")
            break
    ch_thumbs = data.get("authorThumbnails") or []
    return {
        "id":               vid_id,
        "title":            data.get("title", "Untitled"),
        "channel":          data.get("author", "Unknown"),
        "channel_id":       data.get("authorId", ""),
        "channel_url":      f"/channel/{data.get('authorId','')}",
        "channel_thumbnail":ch_thumbs[-1]["url"] if ch_thumbs else "",
        "thumbnail":        _thumb(vid_id),
        "duration":         _fmt_dur(data.get("lengthSeconds", 0)),
        "view_count":       _fmt_views(data.get("viewCount", 0)),
        "like_count":       _fmt_views(data.get("likeCount", 0)).replace(" views", ""),
        "upload_date":      "",
        "description":      data.get("description", ""),
        "video_url":        video_url,
        "comments":         [],
    }


# ─────────────────────────────────────────────────────────────────────
# Public API — called by index.py
# Each function tries Piped first, then Invidious, returns None on total failure.
# ─────────────────────────────────────────────────────────────────────

def is_available():
    """Returns True if any proxy (Piped or Invidious) is reachable."""
    for base in PIPED_INSTANCES[:2] + INVIDIOUS_INSTANCES[:2]:
        host = base.replace("https://","").replace("http://","").split("/")[0]
        try:
            socket.setdefaulttimeout(4)
            socket.getaddrinfo(host, 443)
            return True
        except OSError:
            continue
    return False


def get_trending(max_results=12):
    """
    Fetch niche dev/programming content for the home page.
    Tries Piped, then Invidious, then returns None (caller uses static mock).
    """
    videos = _piped_trending(max_results)
    if videos:
        return videos
    print("[Proxy] Piped niche trending failed, trying Invidious...")
    return _inv_trending(max_results)


def search(query, max_results=10):
    videos = _piped_search(query, max_results)
    if videos:
        return videos
    print("[Proxy] Piped search failed, trying Invidious...")
    return _inv_search(query, max_results)


def get_video_info(video_id):
    info = _piped_video_info(video_id)
    if info:
        return info
    print("[Proxy] Piped video info failed, trying Invidious...")
    return _inv_video_info(video_id)


def get_channel(channel_id, max_results=12):
    """Fetch channel videos — Invidious only (Piped uses different channel IDs)."""
    _, data = _try_instances(INVIDIOUS_INSTANCES, f"/api/v1/channels/{channel_id}",
                             cache_attr="_inv_instance")
    if not data:
        return None, {}
    channel_info = {
        "title":     data.get("author", "Unknown Channel"),
        "thumbnail": ((data.get("authorThumbnails") or [{}])[-1]).get("url", ""),
    }
    videos_raw = data.get("latestVideos") or []
    videos = [_inv_video(v) for v in videos_raw[:max_results] if v.get("videoId")]
    return videos, channel_info
