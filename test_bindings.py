#!/usr/bin/env python3

import unittest
import string
from collections import OrderedDict
from pathlib import Path
from www.scripts import bindings


class ConfigTests(unittest.TestCase):
    
    def testNameRequired(self):
        with self.assertRaises(ValueError):
            config = bindings.Config('')
        
    def testPath(self):
        config = bindings.Config('abcdef')
        configPath = config.path()
        cwd = Path.cwd()
        expectedPath = cwd.parent  / 'configs/ab/abcdef'
        self.assertEqual(configPath, expectedPath)
    
    def testRandomNameValid(self):
        config = bindings.Config.newRandom()
        name = config.name
        self.assertEqual(len(name), 6)
        for char in name:
            self.assertIn(char, string.ascii_lowercase)


class ParserTests(unittest.TestCase):
    
    def testParseEmptyFile(self):
        path = Path('bindings/testCases/empty.binds')
        result = bindings.parseLocalFile(path)
        expectedResult = ({}, {}, {})
        self.assertEqual(result, expectedResult)

    def testParseOneKeyBind(self):
        path = Path('bindings/testCases/one_keystroke.binds')
        (physicalKeys, modifiers, devices) = bindings.parseLocalFile(path)
        expectedKeys = {
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
        expectedDevices = {'Keyboard::0': {'HandledDevices': ['Keyboard'], 'Template': 'keyboard'}}
        self.assertEqual(physicalKeys, expectedKeys)
        self.assertEqual(modifiers, {})
        self.assertEqual(devices, expectedDevices)

    def testParseOneModifier(self):
        path = Path('bindings/testCases/single_modifier.binds')
        (physicalKeys, modifiers, devices) = bindings.parseLocalFile(path)
        expectedKeys = {
            'T16000MTHROTTLE::0::Joy_4': {
                'BaseKey': 'Joy_4',
                'Binds': {
                    'T16000MTHROTTLE::0::Joy_2': {
                        'Controls': OrderedDict(
                            [
                                (
                                    'SetSpeedZero',
                                     {
                                         'Category': 'Navigation',
                                          'Group': 'Ship',
                                          'HasAnalogue': False,
                                          'Name': 'All stop',
                                          'Order': 20,
                                          'OverriddenBy': [],
                                          'Type': 'Digital'
                                    }
                                )
                            ]
                        )
                    }
                },
               'Device': 'T16000MTHROTTLE',
               'DeviceIndex': 0,
               'Key': 'Joy_4'
            }
        }
        expectedModifers = {
            'T16000MTHROTTLE::0::Joy_2': 
                [
                    {
                        'Device': 'T16000MTHROTTLE',
                        'DeviceIndex': 0,
                        'Key': 'Joy_2',
                        'ModifierKey': 'T16000MTHROTTLE::0::Joy_2',
                        'Number': 1
                    }
                ]
        }
        expectedDevices = {
            'T16000MTHROTTLE::0': {'HandledDevices': ['T16000MFCS', 'T16000MTHROTTLE'], 'Template': 't16000mfcs'}
        }
        self.assertEqual(physicalKeys, expectedKeys)
        self.assertEqual(modifiers, expectedModifers)
        self.assertEqual(devices, expectedDevices)

def main():   # pragma: no cover
    unittest.main()

if __name__ == '__main__':   # pragma: no cover
    main()
