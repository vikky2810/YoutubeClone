
import yt_dlp
import json

def check_date_fields():
    # Use a faster channel or playlist
    url = "https://www.youtube.com/channel/UC4JX40jDee_tINbkjycV4Sg"
    ydl_opts = {
        'quiet': True,
        'extract_flat': True,
        'playlistend': 1, # Just get one item
    }
    
    print(f"Fetching: {url}")
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        result = ydl.extract_info(url, download=False)
        
        if 'entries' in result:
            for entry in result['entries']:
                if entry.get('_type') == 'playlist':
                    print("Found nested playlist, checking its entries...")
                    if 'entries' in entry:
                         nested_entries = list(entry['entries'])
                         if nested_entries:
                             first_video = nested_entries[0]
                             print("\n--- Keys in first video entry ---")
                             # Print all keys that might contain "date" or "time"
                             for k, v in first_video.items():
                                 if 'date' in k or 'time' in k or k in ['id', 'title', 'upload_date']:
                                     print(f"{k}: {v}")
                             print("--------------------------------")
                             return

if __name__ == "__main__":
    check_date_fields()
