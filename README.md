<h1 align="center">Google drive gnome extension</h1>
<h3 align="center">Keep your files in sync</h3>

### Prerequisites
* Ruby >= 2.0.0, see [rvm](https://rvm.io/)
* Bash >= 4.4.19 (tested, but will probably work on other versions as well)
* GNOME-shell >= 3.28.2 (tested, but will probably work on other version as well)

## Installation
There's an install script, but manually installing the 2 dependencies of this plugin is recommended for optimal usage.

#### Install script
```bash
wget -o /tmp/gdrivegnome.sh https://raw.githubusercontent.com/Thomas-X/google-drive-gnome/master/installscript.sh && chmod +x /tmp/gdrivegnome.sh && ./tmp/gdrivegnome.sh 
```

#### Manually
* Make sure you've got all the prerequisites installed
* Clone both [this](https://github.com/Thomas-X/drivesync.git) and [this](https://github.com/Thomas-X/argos.git) repo
* Make sure the drivesync repo is in `~/.config/.gdfl/` make the directory if needed
* Follow install instructions of both repos (see README.md)
* Move the .sh script to your ~/.config/argos dir and restart gnome via `Alt+F2` and typing `r` in the command prompt
* You're all set!
