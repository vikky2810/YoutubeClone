
import yt_dlp
import json

def test_get_video_url(video_id):
    print(f"Testing video URL extraction for ID: {video_id}")
    
    ydl_opts = {
        'quiet': False,
        'no_warnings': False,
        'listformats': True, # List formats instead of downloading
        'get_comments': False, 
    }
    
    url = f"https://www.youtube.com/watch?v={video_id}"
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print("Extracting info...")
            info = ydl.extract_info(url, download=False)
            
            if not info:
                print("No info returned.")
                return
            
            print(f"Title: {info.get('title')}")
            
            video_url = info.get('url')
            print(f"Direct Video URL found: {'Yes' if video_url else 'No'}")
            if video_url:
                print(f"URL: {video_url[:100]}...") # Print first 100 chars
                
            # Check other formats if main url is missing
            if not video_url:
                print("\nChecking formats list:")
                formats = info.get('formats', [])
                for f in formats[-5:]: # Show last 5 formats (usually best quality)
                    print(f"Format ID: {f.get('format_id')}, Ext: {f.get('ext')}, URL: {'Yes' if f.get('url') else 'No'}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # Test with a video ID (e.g., standard request)
    # Using a common video ID for testing
    video_id = "dQw4w9WgXcQ" # Rick Roll - usually works
    test_get_video_url(video_id)
