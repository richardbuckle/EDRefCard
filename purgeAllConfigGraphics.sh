#!/bin/sh
DIR=`dirname "$0"`

# purge all .jpg and .svg files
find "$DIR/www/configs" \( -iname "*.jpg" -or -iname "*.svg" \) -delete
