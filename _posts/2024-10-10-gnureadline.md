---
layout: post
title: "emacs python repl fix"
categories: emacs python
comments: false
---

The default `uv` python install uses libedit readline which doesn't [work well](https://github.com/syl20bnr/spacemacs/issues/15998) with emacs.

#### Fix
- `pip install gnureadline`
- `python3 -m override_readline`
- might have to remove `__file__` from `override_readline.py`, this has been solved already [here](https://github.com/ludwigschwardt/python-gnureadline/pull/75) but not merged yet.
- this should make the repl use gnureadline.
- final check
```py
import readline
print(readline.__doc__)
```
should print `'Importing this module enables command line editing using GNU readline.'`.

