#!/bin/sh
DIR=`dirname "$0"`

# purge all .jpg and .svg files over 1 day old
find "$DIR/www/configs" \( -iname "*.jpg" -or -iname "*.svg" \) \! \( -newerct '1 day ago' \) -delete
