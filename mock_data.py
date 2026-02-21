"""
mock_data.py — Realistic fake video data used in LOCAL development mode.
On Vercel (production), real yt-dlp data is used instead.
"""

# ──────────────────────────────────────────────
# Shared mock video pool
# ──────────────────────────────────────────────
MOCK_VIDEOS = [
    {
        'id': 'dQw4w9WgXcQ',
        'title': 'Python Full Course for Beginners — 12 Hours',
        'channel': 'freeCodeCamp.org',
        'thumbnail': 'https://i.ytimg.com/vi/dQw4w9WgXcQ/hqdefault.jpg',
        'duration': '12:02:38',
        'view_count': '8.4M views',
        'upload_date': 'Jan 5, 2024',
    },
    {
        'id': 'rfscVS0vtbw',
        'title': 'Learn CSS in 20 Minutes',
        'channel': 'Web Dev Simplified',
        'thumbnail': 'https://i.ytimg.com/vi/rfscVS0vtbw/hqdefault.jpg',
        'duration': '20:14',
        'view_count': '3.1M views',
        'upload_date': 'Mar 12, 2023',
    },
    {
        'id': 'W6NZfCO5SIk',
        'title': 'JavaScript Tutorial for Beginners: Learn JS in 1 Hour',
        'channel': 'Programming with Mosh',
        'thumbnail': 'https://i.ytimg.com/vi/W6NZfCO5SIk/hqdefault.jpg',
        'duration': '48:17',
        'view_count': '12.0M views',
        'upload_date': 'Aug 22, 2022',
    },
    {
        'id': 'kqtD5dpn9C8',
        'title': 'Python for Everybody — Full Course',
        'channel': 'freeCodeCamp.org',
        'thumbnail': 'https://i.ytimg.com/vi/kqtD5dpn9C8/hqdefault.jpg',
        'duration': '13:41:41',
        'view_count': '6.2M views',
        'upload_date': 'Sep 1, 2023',
    },
    {
        'id': 'yfoY53QXEnI',
        'title': 'CSS Crash Course For Absolute Beginners',
        'channel': 'Traversy Media',
        'thumbnail': 'https://i.ytimg.com/vi/yfoY53QXEnI/hqdefault.jpg',
        'duration': '1:25:09',
        'view_count': '5.8M views',
        'upload_date': 'Apr 10, 2022',
    },
    {
        'id': 'qz0aGYrrlhU',
        'title': 'HTML Tutorial for Beginners: HTML Crash Course',
        'channel': 'Programming with Mosh',
        'thumbnail': 'https://i.ytimg.com/vi/qz0aGYrrlhU/hqdefault.jpg',
        'duration': '1:07:24',
        'view_count': '10.1M views',
        'upload_date': 'Feb 18, 2023',
    },
    {
        'id': 'pTB0EiLXUC8',
        'title': 'React JS Full Course for Beginners — 9 Hours',
        'channel': 'Dave Gray',
        'thumbnail': 'https://i.ytimg.com/vi/pTB0EiLXUC8/hqdefault.jpg',
        'duration': '9:06:49',
        'view_count': '1.5M views',
        'upload_date': 'Nov 11, 2023',
    },
    {
        'id': 'Ke90Tje7VS0',
        'title': 'React JS Crash Course',
        'channel': 'Traversy Media',
        'thumbnail': 'https://i.ytimg.com/vi/Ke90Tje7VS0/hqdefault.jpg',
        'duration': '1:48:04',
        'view_count': '4.2M views',
        'upload_date': 'Jul 30, 2023',
    },
    {
        'id': 'OXGznpKZ_sA',
        'title': 'Node.js and Express.js — Full Course',
        'channel': 'freeCodeCamp.org',
        'thumbnail': 'https://i.ytimg.com/vi/OXGznpKZ_sA/hqdefault.jpg',
        'duration': '8:16:48',
        'view_count': '2.9M views',
        'upload_date': 'Jun 14, 2023',
    },
    {
        'id': 'MFh0Fd7BsjE',
        'title': 'TypeScript Tutorial: TypeScript for React Developers',
        'channel': 'Codevolution',
        'thumbnail': 'https://i.ytimg.com/vi/MFh0Fd7BsjE/hqdefault.jpg',
        'duration': '3:22:10',
        'view_count': '890K views',
        'upload_date': 'Dec 5, 2023',
    },
    {
        'id': 'a_7Z7C_JCyo',
        'title': 'Flask Full Course — Python Web Framework',
        'channel': 'Tech With Tim',
        'thumbnail': 'https://i.ytimg.com/vi/a_7Z7C_JCyo/hqdefault.jpg',
        'duration': '5:20:00',
        'view_count': '1.2M views',
        'upload_date': 'Oct 20, 2023',
    },
    {
        'id': 'HXV3zeQKqGY',
        'title': 'SQL Tutorial — Full Database Course for Beginners',
        'channel': 'freeCodeCamp.org',
        'thumbnail': 'https://i.ytimg.com/vi/HXV3zeQKqGY/hqdefault.jpg',
        'duration': '4:20:38',
        'view_count': '7.7M views',
        'upload_date': 'May 3, 2022',
    },
]

# ──────────────────────────────────────────────
# Mock API functions
# ──────────────────────────────────────────────

def get_mock_trending():
    """Return shuffled mock videos for the home page."""
    import random
    pool = MOCK_VIDEOS.copy()
    random.shuffle(pool)
    return pool


def get_mock_search(query):
    """Return mock search results filtered loosely by query."""
    query_lower = query.lower()
    results = [v for v in MOCK_VIDEOS if query_lower in v['title'].lower()
               or query_lower in v['channel'].lower()]
    # If no match, return all (better than empty)
    return results if results else MOCK_VIDEOS[:6]


def get_mock_video_info(video_id):
    """Return mock video detail for the watch page."""
    # Find the matching mock video or create a generic one
    matched = next((v for v in MOCK_VIDEOS if v['id'] == video_id), None)
    base = matched or {
        'id': video_id,
        'title': f'Demo Video ({video_id})',
        'channel': 'Demo Channel',
        'thumbnail': f'https://i.ytimg.com/vi/{video_id}/hqdefault.jpg',
        'duration': '10:00',
        'view_count': '100K views',
        'upload_date': 'Jan 1, 2024',
    }
    return {
        **base,
        'channel_id': 'UCmock123',
        'channel_url': '#',
        'channel_thumbnail': '',
        'like_count': '12K',
        'description': (
            '⚠️  LOCAL MOCK MODE — Running without internet access.\n\n'
            'This is placeholder content. Deploy to Vercel to see real YouTube data.\n\n'
            'The video player below uses YouTube\'s embed player which works from '
            'the browser even when the Flask backend has no internet access.'
        ),
        'video_url': None,   # Causes watch.html to use the iframe fallback
        'comments': [
            {
                'author': 'Alice Dev',
                'author_thumbnail': '',
                'text': 'Great video! Learned a lot.',
                'like_count': '342',
                'id': 'c1',
                'timestamp': 0,
            },
            {
                'author': 'Bob Coder',
                'author_thumbnail': '',
                'text': 'Could you make a follow-up on advanced topics?',
                'like_count': '128',
                'id': 'c2',
                'timestamp': 0,
            },
        ],
    }


def get_mock_channel(channel_id):
    """Return mock channel info and a list of videos."""
    import random
    channel_info = {
        'title': 'Demo Channel',
        'thumbnail': '',
        'subscriber_count': '1.2M subscribers',
        'description': 'This is a mock channel for local development.',
    }
    videos = random.sample(MOCK_VIDEOS, k=min(8, len(MOCK_VIDEOS)))
    return videos, channel_info
