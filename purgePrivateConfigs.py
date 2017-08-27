#!/usr/bin/env python3

'''
Walk the configs dir and reap all unpublished configs.
These are configs that have no saved ".replay" pickle file.
'''

import sys
from pathlib import Path


class Purger:

    def __init__(self):
        self.configsDir = Path('./www/configs')
    
    def allBindings(self):
        return list(self.configsDir.glob('**/*.binds'))
    
    def replayPath(self, path):
        return path.with_suffix('.replay')
    
    def hasReplay(self, bindPath):
        replayPath = self.replayPath(bindPath)
        return replayPath.exists()
        
    def thoseWithoutReplay(self, bindingsPaths):
        return [path for path in bindingsPaths if not self.hasReplay(path)]    
    
    def allFilesWithStartingWithStem(self, path):
        nameGlob = '%s*.*' % path.stem
        parent = path.parent
        return list(parent.glob(nameGlob))
    
    def purgeFile(self, path):
        print(path)
        # path.unlink()
    
    def purge(self):
        if not self.configsDir.exists():
            # script probably installed in the wrong place or called with the wrong working directory
            sys.exit('%s not found' % self.configsDir)
        allBindings = self.allBindings()
        privateBindings = self.thoseWithoutReplay(allBindings)
        deepListToPurge = [self.allFilesWithStartingWithStem(path) for path in privateBindings]
        filesToPurge = [x for sublist in deepListToPurge for x in sublist] 
        for path in filesToPurge:
            self.purgeFile(path)
        

def main():
    purger = Purger()
    purger.purge()

if __name__ == '__main__':
    main()
