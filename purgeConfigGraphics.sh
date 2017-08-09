#!/bin/sh

# purge all .jpg files over 1 day old
find /home/edrefcardinfoi7/www/configs -name "*.jpg" \! \( -newerct '1 day ago' \) -print
