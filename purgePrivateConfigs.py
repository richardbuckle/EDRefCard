#!/usr/bin/env python3

'''
Walk the configs dir and reap all unpublished configs.
These are configs that have no saved pickle file.
'''

import sys
from pathlib import Path


class Purger:

    def __init__(self):
        self.configsDir = Path('./www/configs/')
    
        
    def purge(self):
        if not self.configsDir.exists():
            # script probably installed in the wrong place or called with the wrong cwd
            sys.exit('%s not found' % self.configsDir)


def main():
    purger = Purger()
    purger.purge()

if __name__ == '__main__':
    main()
