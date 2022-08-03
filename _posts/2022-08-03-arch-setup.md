---
layout: post
title: "Asahi Linux Setup"
date: 2022-08-03 18:06:10 +0530
categories: arch emacs
comments: false
---

Extremely easy to get it running thanks to the wonderful people working on Asahi. 

Why? i3 and less clutter, MacOS has no real alternative to what i3 offers and had 
some time to burn thanks to not having DSM in 2-1 (yet). 

#### Display Manager and ZSH
LightDM is a mess and couldn't get myself to configure SDDM so no display managers for now. 
`startx` after login -- remove `xdisplay` commands and append `exec i3` to .xinitrc. ZSH
is the default shell, oh-my-zsh is essential for autosuggestions and syntax highlighting. 

#### Emacs 
AUR has a native-comp install which fortunately works on ARM64. 
I find it way faster than native-comp on MAC OSX, not sure why. `init.el` would require 
a few changes, have an `arch` branch on `komikat/.emacs.d` now. 

#### Git
Github push required some extra config, IIIT has blocked the default ports on LAN,
```config
Host github.com
    Hostname ssh.github.com
    Port 443
    User git

Host gitlab.com
    Hostname altssh.gitlab.com
    Port 443
    User git
    PreferredAuthentications publickey
```
after setting username and email.

### Email
WIP
