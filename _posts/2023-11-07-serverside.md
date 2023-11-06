---
layout: post
title: "Fetching what I'm listening to (experiments with server side rendering)"
categories: server python
comments: false
---

Decided to write a tiny python script to render my website's `index.html` page with
the song I was last listening to using lastfm's [generous](https://www.last.fm/api) api.

```python
#!/usr/bin/env python3

import http.client
import json

api_key = "thistotallyworks"
username = "marxplank"

conn = http.client.HTTPSConnection("ws.audioscrobbler.com")

url = f"/2.0/?method=user.getrecenttracks&user={username}&api_key={api_key}&format=json"
conn.request("GET", url)

response = conn.getresponse()

if response.status == 200:
    data = json.loads(response.read().decode("utf-8"))
    track = data["recenttracks"]["track"][0]
    artist = track["artist"]["#text"]
    track_name = track["name"]

    result = f"{track_name} by {artist}"
else:
    result = "Failed to retrieve recent tracks."

conn.close()

code = (
    "<website code />"
    f'{result}'
    "<rest of it />"
)
from pathlib import Path

root_folder = Path(__file__).parents[0]

rpath = root_folder / "public_html/index.html"
with open(rpath, "w") as f:
    f.seek(0)
    f.write(code)

```

Planning to extend this by highlighting the name of the song with the dominant color from the album artwork but 
that's for another day.
