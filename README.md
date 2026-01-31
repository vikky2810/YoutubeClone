# viewtube

a privacy focused youtube frontend built with flask

this project exists because my college sometimes blocks youtube.

not permanently, but randomly. one day it works, the next day it doesn’t. tutorials stop loading. lectures don’t open. debugging videos are suddenly unreachable. when you rely on youtube to learn tech, that inconsistency is frustrating.

so instead of waiting for the block to be lifted every time, i built my own way to access youtube content.

this is a lightweight youtube frontend built using python and flask, deployed on vercel. it does not use the official youtube ui, it does not track users, and it does not store personal data. it simply fetches video information and streams it in a clean, minimal interface.

this project is not about breaking rules. it is about solving a real problem i personally faced while learning.

---

## what this project does

* lets you search and watch youtube videos
* streams videos using progressive mp4 playback
* shows basic metadata and comments
* keeps the ui simple and distraction free
* works within vercel free tier limits

no ads. no tracking. no cookies. no noise.

---

## tech stack

* backend: python + flask
* frontend: html + css using jinja templates
* video extraction: yt-dlp
* deployment: vercel (serverless)

the stack is intentionally simple. no docker. no heavy setup. just code that works.

---

## local development

install dependencies:

```
pip install -r requirements.txt
```

run the app:

```
python index.py
```

open in browser:

```
http://localhost:5000
```

---

## deployment

this project is designed for vercel’s serverless environment.

deploy using the cli:

```
vercel
```

or connect the github repo directly to vercel.

---

## project structure

```
youtubeclone/
├── index.py
├── templates/
├── static/
├── requirements.txt
├── vercel.json
├── plan.md
├── features.md
├── fixes.md
└── readme.md
```

---

## vercel constraints

this project respects vercel free tier limits:

* short execution timeout
* no persistent storage
* no background workers
* limited response size

architecture choices were made around these limits.

---

## why i built this

i built this because youtube being blocked “sometimes” is worse than being blocked forever.

you never know when it will fail, and that breaks learning momentum.

this project helped me learn:

* real flask deployment
* serverless limitations
* video streaming basics
* structuring a real-world project
* building solutions instead of waiting for permission

---

## license

mit license.
use it for learning or portfolio projects.

---

## live demo

[https://ytviks.vercel.app/](https://ytviks.vercel.app/)
