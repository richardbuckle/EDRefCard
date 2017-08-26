#!/usr/bin/env python3

import unittest
from collections import OrderedDict
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

    def testParseOneKeyBind(self):
        path = Path('bindings/testCases/one_keystroke.binds')
        (physicalKeys, modifiers, devices) = bindings.parseLocalFile(path)
        expectedKey = {
            'Keyboard::0::Key_Minus': {
                'BaseKey': 'Key_Minus',
                'Binds': {
                    'Unmodified': {
                        'Controls': OrderedDict( 
                            [
                                (
                                    'WingNavLock', 
                                    {
                                        'Group': 'Ship',
                                        'HasAnalogue': False,
                                        'Name': 'Wingman navlock',
                                        'Order': 405,
                                        'OverriddenBy': [],
                                        'Type': 'Digital'
                                    }
                                )
                            ]
                        )
                    }
                },
                'Device': 'Keyboard',
                'DeviceIndex': 0,
                'Key': 'Key_Minus'
            }
        }
        expectedDevice = {'Keyboard::0': {'HandledDevices': ['Keyboard'], 'Template': 'keyboard'}}
        self.assertEqual(physicalKeys, (expectedKey))
        self.assertEqual(modifiers, {})
        self.assertEqual(devices, (expectedDevice))

def main():
    unittest.main()

if __name__ == '__main__':
    main()
