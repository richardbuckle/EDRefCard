#! /bin/bash

# For use with the Apache logs for EDRefCard, to identify unsupported controls.
# Extract and uniquify any text that occurs after the phrase "No control for " in the files given in the args.

zgrep -Poh '.*No control for \K(.+)' $@ | sort -u
