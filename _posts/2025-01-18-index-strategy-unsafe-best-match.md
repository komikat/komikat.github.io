---
layout: post
title:  "--index-strategy unsafe-best-match"
date:   2025-01-18 04:00:47 +0530
categories: jekyll update
comments: false
---

Installing PyTorch 2.5.1, Fairseq2, CUDA 12.1.

`uv pip install fairseq2 --pre --extra-index-url https://fair.pkg.atmeta.com/fairseq2/whl/pt2.5.1/cu121 --upgrade --index-strategy unsafe-best-match`

Note from uv:
"A compatible version may be available on a subsequent index (e.g., https://pypi.org/simple). By default, uv will only consider versions that are published on the first index that contains a given package,
to avoid dependency confusion attacks. If all indexes are equally trusted, use `--index-strategy unsafe-best-match` to consider all versions from all indexes, regardless of the order in which they were
defined."
