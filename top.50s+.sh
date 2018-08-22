#!/usr/bin/env bash

SYNC_OUTPUT=$(ruby \~/.config/.gdfl/drivesync/drivesync.rb)
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
echo "About | iconName=help-about-symbolic href="
# voor (syncen) :clouds: :cry: gebruik icon systen-reboot-symbolic
# voor up-to-date gebruik objec3t-select-symbolic

# INPUT='someletters_12345_moreleters.ext'
# a="ERR:PID1234"
# tmp=${a#*"ERR:PID"}
# echo $tmp 
# SUBSTRING=$(echo $INPUT| cut -d'_' -f "ERR:PID")
# echo $SUBSTRING

# echo $SYNC_OUTPUT
# echo "$SYNC_OUTPUT" | tr -d "Local folder"
# echo "$HAS_SYNCED"
# echo "$SYNC_OUTPUT"
  # echo "$SYNC_OUTPUT | font=monospace bash=top"
# else
  # echo "Loading..."
# fi