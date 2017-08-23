# Build status
* master  [![Build Status](https://travis-ci.org/richardbuckle/EDRefCard.svg?branch=master)](https://travis-ci.org/richardbuckle/EDRefCard)  [![Coverage Status](https://coveralls.io/repos/github/richardbuckle/EDRefCard/badge.svg?branch=master)](https://coveralls.io/github/richardbuckle/EDRefCard?branch=master)
* dev [![Build Status](https://travis-ci.org/richardbuckle/EDRefCard.svg?branch=dev)](https://travis-ci.org/richardbuckle/EDRefCard)  [![Coverage Status](https://coveralls.io/repos/github/richardbuckle/EDRefCard/badge.svg?branch=dev)](https://coveralls.io/github/richardbuckle/EDRefCard?branch=master)

# Purpose
Elite: Dangerous has a great many command bindings to learn. To help with that, EDFRefCard generates a printable reference card from your Elite: Dangerous bindings file.

Currently hosted at [https://edrefcard.info/](https://edrefcard.info/).

# Dependencies

* Python 3
	* Python3 module `lxml`
	* Python3 module `wand`
* ImageMagick v6 (at the time of writing python wand doesn't support ImageMagick v7)
	* you may need to configure the `MAGICK_HOME` env var to get `wand` to see the ImageMagick libraries.

# Installation in a web server

* Base the server on the `www` subdirectory of this repo.
* Check that your server is supplying the env vars `CONTEXT_DOCUMENT_ROOT` and `SCRIPT_URI` so that `Config.dirRoot` and `Config.webRoot` in `www/scripts/bindings.py` get set correctly. Apache 2 does this by default.
* Add redirects as follows (in Apache 2 notation):

```
RewriteRule ^/list$ /scripts/bindings.py?list=all
RewriteRule ^/binds/(.+)$ /scripts/bindings.py?replay=$1
RewriteRule ^/configs/([a-z][a-z])([^/]+)$ /configs/$1/$1$2
```

# Credits

EDRefCard is derived with permission from code originally developed by CMDR jgm.
