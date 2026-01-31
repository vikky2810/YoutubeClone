
# project plan – simple youtube frontend (flask + vercel)

## goal

build a small youtube frontend using python and flask.
the app must be simple enough to deploy on vercel free tier.
this is a learning + portfolio project, not a production service.

---

## deployment target

- platform: vercel (free tier)
- backend: python serverless function
- no background workers
- no long-running processes
- no docker
- no external services

---

## what this project is

- a minimal flask app
- runs as a serverless app on vercel
- fetches youtube data on demand
- renders html pages using jinja
- privacy-focused and lightweight

---

## what this project is not

- not a full invidious clone
- not high traffic ready
- no user accounts
- no subscriptions
- no heavy backend processing

---

## tech stack

- python 3.x
- flask
- yt-dlp (metadata only, no downloads)
- html + css (jinja templates)

---

## features (vercel-safe)

### 1. home page
- search input
- submit keyword

### 2. search results
- list of videos
- title + thumbnail
- limit results (important for vercel timeout)

### 3. watch page
- embedded video player
- title
- channel name
- view count

---

## important vercel constraints

- requests must finish quickly
- limit yt-dlp calls
- avoid large responses
- no filesystem writes
- no background tasks

design decisions must respect this.

---

## project structure (simple)

```text
api/
└── index.py        # flask app entry (vercel)
templates/
├── home.html
├── results.html
└── watch.html
static/
└── style.css
requirements.txt
vercel.json
````

---

## basic flow

1. user opens home page
2. enters search keyword
3. flask route calls yt-dlp (limited results)
4. results rendered immediately
5. user clicks video
6. watch page loads with embedded player

---

## caching (vercel-friendly)

* use in-memory python cache
* cache only during single request lifecycle
* no redis
* no file-based cache

caching is best-effort, not guaranteed.

---

## error handling

* yt-dlp failure → show friendly message
* empty search → show “no results”
* timeout risk → reduce result count

never crash the function.

---

## development steps

1. create minimal flask app
2. make it work locally
3. integrate yt-dlp carefully
4. limit search results
5. build watch page
6. add basic css
7. deploy to vercel
8. test cold start behavior

---

## success criteria

* deploys on vercel free tier
* app loads without timeout
* search works reliably
* video watch page renders
* code is simple and readable

---

## why this project is worth hosting

this project shows:

* understanding of serverless limits
* backend fundamentals
* third-party data handling
* real deployment experience
* practical engineering choices

