#!/bin/bash

xhost +local:er >/dev/null

while ! xset q >/dev/null 2>1; do sleep 2; done

xset s off
xset -dpms
xset s noblank

firefox \
    --kiosk \
    --private-window \
    "http://0.0.0.0:8000/" \
    &
    
while true; do
    sleep 60
    xdotool key F11
done
