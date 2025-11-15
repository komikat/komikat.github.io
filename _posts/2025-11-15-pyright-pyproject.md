---
layout: post
title: "Getting pyright to work with uv"
comments: false
---

To get pyright to look at the correct package installation folder (using pyproject.toml, like uv does),
add the following to the pyproject.toml.

```toml
[tool.pyright]
venv = ".venv"
venvPath = "."
```
