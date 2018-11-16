#!/bin/sh
DIR=`dirname "$0"`

# purge all .jpg files
find "$DIR/www/configs" -name "*.jpg" -delete
