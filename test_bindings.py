#!/usr/bin/env python3

import unittest
from pathlib import Path
from www.scripts import bindings


class ConfigTests(unittest.TestCase):

    def testPath(self):
        config = bindings.Config('abcdef')
        configPath = config.path()
        cwd = Path.cwd()
        expectedPath = cwd.parent  / 'configs/ab/abcdef'
        self.assertEqual(configPath, expectedPath)


class ParserTests(unittest.TestCase):
    
    def testParseEmptyFile(self):
        path = Path('bindings/testCases/empty.binds')
        result = bindings.parseLocalFile(path)
        expectedResult = ({}, {}, {})
        self.assertEqual(result, expectedResult)

def main():
    unittest.main()

if __name__ == '__main__':
    main()
