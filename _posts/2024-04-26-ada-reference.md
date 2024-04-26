---
layout: post
title: "Ada reference"
comments: false
---

- `ncdu` for looking at the disk usage.
- `sinteractive -c 10 -g 2` for getting a node.
- Jupyter setup
  - Run `jupyter lab password` followed by `jupyter lab --no-browser` on ada.
  - Tunnel to your system: `ssh -L 1025:localhost:8888 -J akshit.kumar@ada.iiit.ac.in akshit.kumar@gnodeXX`
  - connect to `localhost:1025` using emacs/browser.
- pyenv and pipenv
  - torch install `pipenv install torch torchaudio torchvision`
  - set local python as: `pyenv local 3.X`
  - run `pipenv shell` to use the installed configuration.
