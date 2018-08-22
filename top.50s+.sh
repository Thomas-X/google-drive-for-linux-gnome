#!/usr/bin/env bash

SYNC_OUTPUT=$(ruby ${HOME}/.config/.gdfl/drivesync/drivesync.rb)
UP_TO_DATE='Up-to-date | iconName=object-select-symbolic'
SYNCING="Syncing.. | iconName=system-reboot-symbolic"
ECHO_MESSAGE=$UP_TO_DATE
if [[ $SYNC_OUTPUT = *"Uploading"* || $SYNC_OUTPUT = *"Downloading"* || $SYNC_OUTPUT == *"Updating"* ]]; then 
  ECHO_MESSAGE=$SYNCING
fi
# if sync is already running update echo to say syncing
if [[ $SYNC_OUTPUT == *"ERR:PID"* ]]; then
    ECHO_MESSAGE=$SYNCING
fi
echo $ECHO_MESSAGE
echo '---'
echo "About | iconName=help-about-symbolic href=https://github.com/Thomas-X/google-drive-gnome/"
