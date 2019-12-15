# Reo ~ The Simple Dictionary
**Reo** is a dictionary application using the WordNet 3.1 (or 3.0) database for definitions and the reliable eSpeak for pronunciations (both audio and phoneme).

Light Mode                       |  Dark Mode
:-------------------------------:|:--------------------------------:
![Light Mode](/ss.png?raw=true)  |  ![Dark Mode](/ss1.png?raw=true)

### Requirements
 * DICT official client and server (dictd and dict)
 * WordNet 3.1 or 3.0 database for dictd (dict-wn)
 * Python 3
 * Python GObject
 * Gtk+ 3.20+
 * eSpeak-ng (For pronunciations and audio)

You can confirm all the requirements by running Reo with the arguments `--check` (`-c`) or `--adversion` (`-d`).

#### Slow?
If the output is slow, it's possibly because the definition is obtained from dict.org rather than localhost. So, run  
`sudo systemctl enable dictd.service && sudo systemctl start dictd.service`

### Features
 * Neat output with proper coloring and formatting
 * Random Word
 * Custom Definitions feature using Pango Markup Syntax for formatting
 * Lightweight. 1 mb only and further reducible (It does nothing on its own, so yeah)
 * Support for GNOME Dark Mode and launching app in dark mode. Also supports gtk3-nocsd.

#### Future
Honestly, I feel like just deleting this and forgetting it ever existed. But well, it works and has no bugs I know. So, guess I'll keep it and since I do use it, I might improve a lot of the little things. But overall, I'm pretty satisfied with this.  

Basically it's just a GUI for some CLI tools. It doesn't even directly interact with dictd. And even the UI is badly done with Glade. So yeah, I'm lazy.
