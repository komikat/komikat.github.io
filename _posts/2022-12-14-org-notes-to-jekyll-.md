---
layout: post
title: "Org notes to Jekyll "
date: 2022-12-14 20:46:22 +0530
categories: post
comments: false
---


```emacs-lisp
  (defun generate-file-name (title)
	(interactive "sEnter title:")
	(message
	 (format "/Some/Folder/komikat.github.io/_posts/%s-%s.md"
		   (format-time-string "%Y-%m-%d")
				   (replace-regexp-in-string " " "-" (downcase title))))
  )

  (defun generate-header-post (title)
	(format "---
layout: post
title: \"%s\"
date: %s
categories: post
comments: false
---
" title (format-time-string "%Y-%m-%d %H:%M:%S %z")))
```

then combine the two after converting the org buffer to markdown using [ox-gfm](https://github.com/larstvei/ox-gfm).

```emacs-lisp
(defun generate-post (title)
(interactive "sEnter title:")
  (progn
	(org-gfm-export-as-markdown)
	(write-region (generate-header-post title) nil (generate-file-name title) t)
	(write-region nil nil (generate-file-name title) t)
	)
  )
```

Doesn't support images for now.