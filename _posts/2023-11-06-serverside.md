---
layout: post
title: "lastfm server side experiments"
categories: server python
comments: false
---

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