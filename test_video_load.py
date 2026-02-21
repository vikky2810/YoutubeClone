"""
===========================================================
  ViewTube - Full Diagnostic Test
  Run this to pinpoint exactly why videos are not loading.
===========================================================
  Usage:  python test_video_load.py
===========================================================
"""

import sys
import socket
import urllib.request
import subprocess

# ─────────────────────────────────────────────
# ANSI helpers
# ─────────────────────────────────────────────
OK   = "[OK]   "
FAIL = "[FAIL] "
INFO = "[INFO] "
SKIP = "[SKIP] "

def section(title):
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def ok(msg):   print(f"  {OK}{msg}")
def fail(msg): print(f"  {FAIL}{msg}")
def info(msg): print(f"  {INFO}{msg}")
def skip(msg): print(f"  {SKIP}{msg}")


# ─────────────────────────────────────────────
# TEST 1 – Python version
# ─────────────────────────────────────────────
section("TEST 1: Python Environment")
v = sys.version_info
info(f"Python {v.major}.{v.minor}.{v.micro}")
if v.major < 3 or (v.major == 3 and v.minor < 8):
    fail("Python 3.8+ is required.")
    sys.exit(1)
else:
    ok("Python version is fine.")


# ─────────────────────────────────────────────
# TEST 2 – yt-dlp installed?
# ─────────────────────────────────────────────
section("TEST 2: yt-dlp Installation")
try:
    import yt_dlp
    ok(f"yt-dlp is installed — version {yt_dlp.version.__version__}")
except ImportError:
    fail("yt-dlp is NOT installed.")
    print("\n  FIX: Run   pip install yt-dlp")
    sys.exit(1)


# ─────────────────────────────────────────────
# TEST 3 – DNS resolution
# ─────────────────────────────────────────────
section("TEST 3: DNS Resolution for www.youtube.com")
try:
    socket.setdefaulttimeout(5)
    addrs = socket.getaddrinfo('www.youtube.com', 443)
    ip = addrs[0][4][0]
    ok(f"DNS resolved  →  {ip}")
    dns_ok = True
except OSError as e:
    fail(f"DNS resolution FAILED: {e}")
    print()
    print("  This is the DIRECT cause of 'Failed to resolve www.youtube.com'.")
    print()
    print("  Possible fixes:")
    print("    1. Check your internet connection.")
    print("    2. Change your DNS to Google (8.8.8.8) or Cloudflare (1.1.1.1).")
    print("       Windows: Settings → Network → Change adapter options")
    print("               → IPv4 properties → set preferred DNS to 8.8.8.8")
    print("    3. If you are using a VPN, make sure it allows DNS lookups.")
    print("    4. If YouTube is blocked in your country/ISP, you need a VPN.")
    dns_ok = False


# ─────────────────────────────────────────────
# TEST 4 – HTTP connectivity
# ─────────────────────────────────────────────
section("TEST 4: HTTP Connectivity to YouTube")
if not dns_ok:
    skip("Skipping HTTP test because DNS failed.")
    http_ok = False
else:
    try:
        req = urllib.request.Request(
            "https://www.youtube.com",
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        with urllib.request.urlopen(req, timeout=10) as r:
            code = r.getcode()
        ok(f"HTTP GET returned status {code}")
        http_ok = True
    except Exception as e:
        fail(f"HTTP request failed: {e}")
        print("  Your DNS works but HTTP is blocked. Try a VPN.")
        http_ok = False


# ─────────────────────────────────────────────
# TEST 5 – yt-dlp search test
# ─────────────────────────────────────────────
section("TEST 5: yt-dlp YouTube Search (ytsearch3:python)")
if not http_ok:
    skip("Skipping yt-dlp search because HTTP is not available.")
else:
    try:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': 'in_playlist',
            'ignoreerrors': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            result = ydl.extract_info("ytsearch3:python programming", download=False)

        if not result or 'entries' not in result:
            fail("yt-dlp returned no results.")
            print("  Try: pip install -U yt-dlp")
        else:
            entries = [e for e in result['entries'] if e]
            if not entries:
                fail("yt-dlp returned an empty entries list.")
            else:
                ok(f"yt-dlp returned {len(entries)} result(s).")
                for i, e in enumerate(entries[:3]):
                    title   = e.get('title', 'N/A')
                    vid_id  = e.get('id', 'N/A')
                    channel = e.get('uploader') or e.get('channel', 'N/A')
                    print(f"    {i+1}. [{vid_id}] {title} — {channel}")
    except Exception as e:
        fail(f"yt-dlp search raised an exception: {e}")
        import traceback
        traceback.print_exc()


# ─────────────────────────────────────────────
# TEST 6 – Flask app running?
# ─────────────────────────────────────────────
section("TEST 6: Flask Server Reachability (localhost:5000)")
try:
    req = urllib.request.Request(
        "http://127.0.0.1:5000/",
        headers={'User-Agent': 'ViewTube-Test'}
    )
    with urllib.request.urlopen(req, timeout=5) as r:
        ok(f"Flask server is UP — status {r.getcode()}")
        flask_ok = True
except urllib.error.URLError as e:
    if 'Connection refused' in str(e):
        fail("Flask is NOT running on port 5000.")
        print("  FIX: In another terminal, run:  python index.py")
    else:
        fail(f"Flask check failed: {e}")
    flask_ok = False
except Exception as e:
    fail(f"Unexpected error checking Flask: {e}")
    flask_ok = False


# ─────────────────────────────────────────────
# TEST 7 – /api/trending endpoint
# ─────────────────────────────────────────────
section("TEST 7: /api/trending Endpoint")
if not flask_ok:
    skip("Skipping API test because Flask is not running.")
else:
    import json
    try:
        req = urllib.request.Request(
            "http://127.0.0.1:5000/api/trending",
            headers={'User-Agent': 'ViewTube-Test'}
        )
        with urllib.request.urlopen(req, timeout=60) as r:
            raw = r.read().decode()
            data = json.loads(raw)

        if isinstance(data, list):
            if len(data) == 0:
                fail("API returned an empty list [] — no videos.")
                print("  This means yt-dlp search returned nothing.")
                print("  Check TEST 5 above for root cause.")
            else:
                ok(f"API returned {len(data)} video(s)!")
                for i, v in enumerate(data[:3]):
                    print(f"    {i+1}. {v.get('title','N/A')} [{v.get('id','N/A')}]")
        elif isinstance(data, dict) and data.get('error'):
            fail(f"API returned error: {data.get('error')} — {data.get('message','')}")
        else:
            info(f"Unexpected API response: {str(data)[:200]}")

    except urllib.error.HTTPError as e:
        raw = e.read().decode()
        fail(f"API returned HTTP {e.code}")
        try:
            err_data = json.loads(raw)
            print(f"    error  : {err_data.get('error')}")
            print(f"    message: {err_data.get('message')}")
        except Exception:
            print(f"    body: {raw[:300]}")
    except Exception as e:
        fail(f"Could not reach /api/trending: {e}")


# ─────────────────────────────────────────────
# SUMMARY
# ─────────────────────────────────────────────
section("SUMMARY & NEXT STEPS")
if not dns_ok:
    print("  ROOT CAUSE → YouTube DNS resolution is FAILING.")
    print()
    print("  Most likely fix:")
    print("    1. Open Control Panel → Network Connections")
    print("    2. Right-click your active adapter → Properties")
    print("    3. Select 'Internet Protocol Version 4 (TCP/IPv4)' → Properties")
    print("    4. Set Preferred DNS server to: 8.8.8.8")
    print("    5. Set Alternate DNS server to:  8.8.4.4")
    print("    6. Click OK, then retry.")
    print()
    print("  Alternative: Install and activate a VPN.")
elif not http_ok:
    print("  ROOT CAUSE → DNS resolves but HTTP to YouTube is blocked.")
    print("  FIX: Use a VPN.")
else:
    print("  Your network can reach YouTube.")
    print("  If videos still don't load, run:  pip install -U yt-dlp")
    print("  Then restart Flask:               python index.py")
