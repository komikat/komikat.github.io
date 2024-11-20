---
layout: post
title: "Asahi Linux Setup"
date: 2022-08-03 18:06:10 +0530
categories: arch emacs
comments: false
---

Why? i3 and less clutter

#### Display Manager and ZSH
- LightDM is a mess.
- `startx` after login -- remove `xdisplay` commands and append `exec i3` to .xinitrc. ZSH
is the default shell.

#### Emacs
- AUR has a native-comp install which works on ARM64. 
- find it way faster than native-comp on MAC OSX, not sure why.
- [ ] TODO: custom emacs init functions for mac/linux

#### IIIT Git setup
IIIT has blocked the default ports on LAN,
```config
Host github.com
    Hostname ssh.github.com
    Port 443
    User git

Host gitlab.com
    Hostname altssh.gitlab.com
    Port 443
    User git
    PreferredAuthentications publickey```
after setting username and email.

### Email
WIP
