export DISPLAY=:0
n=$(()($RANDOM%3)+1))
xdotool key --clearmodifiers ctrl+$n
