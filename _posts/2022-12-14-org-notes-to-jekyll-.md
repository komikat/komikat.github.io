---
layout: post
title: "Org notes to Jekyll "
date: 2022-12-14 20:46:22 +0530
categories: post
comments: false
---
Finally got around creating an (almost) working pipeline to parse my org notes into a jekyll-friendly markdown. I expect to repopulate this site after having promised myself that almost exactly 11 months ago. I think this was pretty quickly done by my standards and I'm fairly proud of the 20 lines of code I wrote for this.

I use the extremely convenient `format` and `format-time-string` to generate a file name and the post header,

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

and then combine the two after converting the org buffer to markdown using [ox-gfm](https://github.com/larstvei/ox-gfm).

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

Doesn't support images for now but I don't intend to include images in most of my posts anyway.