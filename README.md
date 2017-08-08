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
* Adjust `Config.dirRoot` and `Confog.webRoot` in `www/scripts/bindings.py` as necessary.
* Add redirects as follows (in Apache 2 notation):

```
RewriteRule ^/elite/binds/(.+)$ /elite/scripts/bindings.py?replay=$1
RewriteRule ^/elite/configs/([a-z][a-z])([^/]+)$ /elite/configs/$1/$1$2
```

# Credits

EDRefCard is derived with permission from code originally developed by CMDR jgm.
