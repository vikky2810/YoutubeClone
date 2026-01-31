"""
Test script to debug YouTube search functionality
This will help us see what's happening with yt-dlp
"""

import yt_dlp
import sys

def test_search(query):
    """Test YouTube search with detailed output"""
    print("=" * 60)
    print(f"Testing search for: '{query}'")
    print("=" * 60)
    
    try:
        ydl_opts = {
            'quiet': False,
            'no_warnings': False,
            'extract_flat': True,
            'format': 'best',
            'ignoreerrors': True,
        }
        
        # IMPORTANT: Use ytsearch prefix for YouTube search
        search_query = f"ytsearch10:{query}"
        
        print("\n1. Creating YoutubeDL instance...")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print(f"2. Extracting info for query: {search_query}")
            result = ydl.extract_info(search_query, download=False)
            
            print("\n3. Checking result...")
            if not result:
                print("❌ ERROR: No result returned from yt-dlp")
                return
            
            print(f"✅ Result received. Type: {type(result)}")
            print(f"✅ Result keys: {list(result.keys())}")
            
            if 'entries' not in result:
                print(f"❌ ERROR: No 'entries' in result")
                print(f"Available keys: {list(result.keys())}")
                return
            
            entries = result['entries']
            print(f"\n4. Found {len(entries)} entries")
            
            if not entries:
                print("❌ ERROR: Entries list is empty")
                return
            
            print("\n5. Processing videos...")
            videos = []
            for i, entry in enumerate(entries):
                if entry:
                    video_id = entry.get('id', 'N/A')
                    title = entry.get('title', 'Untitled')
                    channel = entry.get('uploader', entry.get('channel', 'Unknown'))
                    duration = entry.get('duration', 0)
                    views = entry.get('view_count', 0)
                    
                    print(f"\n   Video {i+1}:")
                    print(f"   - ID: {video_id}")
                    print(f"   - Title: {title}")
                    print(f"   - Channel: {channel}")
                    print(f"   - Duration: {duration}s")
                    print(f"   - Views: {views}")
                    
                    # Get thumbnail
                    thumbnail = entry.get('thumbnail', '')
                    if not thumbnail and 'thumbnails' in entry:
                        thumbnails = entry.get('thumbnails', [])
                        if thumbnails and len(thumbnails) > 0:
                            thumbnail = thumbnails[0].get('url', '')
                    print(f"   - Thumbnail: {thumbnail[:50]}..." if thumbnail else "   - Thumbnail: None")
                    
                    videos.append({
                        'id': video_id,
                        'title': title,
                        'channel': channel,
                        'duration': duration,
                        'views': views,
                        'thumbnail': thumbnail
                    })
                else:
                    print(f"\n   Video {i+1}: ❌ Entry is None")
            
            print("\n" + "=" * 60)
            print(f"✅ SUCCESS: Found {len(videos)} valid videos")
            print("=" * 60)
            
            return videos
    
    except Exception as e:
        print(f"\n❌ EXCEPTION OCCURRED:")
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    # Test with the query the user mentioned
    query = "hello world in cpp"
    
    print("\n" + "🔍 YouTube Search Test Script")
    print("This will test if yt-dlp can search YouTube\n")
    
    # Check if yt-dlp is installed
    try:
        import yt_dlp
        print(f"✅ yt-dlp version: {yt_dlp.version.__version__}")
    except ImportError:
        print("❌ yt-dlp is not installed!")
        print("Run: pip install yt-dlp")
        sys.exit(1)
    
    # Run the test
    videos = test_search(query)
    
    if videos:
        print(f"\n📊 SUMMARY:")
        print(f"   Total videos found: {len(videos)}")
        print(f"\n   First 3 video titles:")
        for i, video in enumerate(videos[:3]):
            print(f"   {i+1}. {video['title']}")
    else:
        print("\n❌ FAILED: No videos found")
        print("\nPossible issues:")
        print("1. Internet connection problem")
        print("2. YouTube is blocking requests")
        print("3. yt-dlp needs updating: pip install --upgrade yt-dlp")
        print("4. Firewall or proxy blocking YouTube")
