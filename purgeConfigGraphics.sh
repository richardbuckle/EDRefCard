#!/bin/sh
DIR=`dirname "$0"`

# purge all .jpg files over 1 day old
find "./$DIR/www/configs" -name "*.jpg" \! \( -newerct '1 day ago' \) -delete
