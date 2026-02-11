
import yt_dlp
import json

def test_search():
    ydl_opts = {
        'quiet': True,
        'extract_flat': True,
        'format': 'best',
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        print("Searching...")
        result = ydl.extract_info("ytsearch1:Google", download=False)
        if 'entries' in result:
            entry = result['entries'][0]
            print(json.dumps(entry, indent=2))

if __name__ == "__main__":
    test_search()
