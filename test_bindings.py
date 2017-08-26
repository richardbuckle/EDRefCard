#!/usr/bin/env python3

import unittest
import string
from collections import OrderedDict
from pathlib import Path
from www.scripts import bindings


class ConfigTests(unittest.TestCase):
    
    def setUp(self):
        self.config = bindings.Config('abcdef')
        cwd = Path.cwd()
        self.expectedConfigPath = cwd.parent / 'configs/ab/abcdef'

    def testNameRequired(self):
        with self.assertRaises(ValueError):
            config = bindings.Config('')
    
    def testRandomNameIsValid(self):
        config = bindings.Config.newRandom()
        name = config.name
        self.assertEqual(len(name), 6)
        for char in name:
            self.assertIn(char, string.ascii_lowercase)
        
    def testPath(self):
        configPathStr = str(self.config.path())
        expectedPathStr = str(self.expectedConfigPath)
        self.assertEqual(configPathStr, expectedPathStr)
    
    def testPathWithSuffix(self):
        configPathStr = str(self.config.pathWithSuffix('.jpg'))
        expectedPathStr = str(self.expectedConfigPath) + '.jpg'
        self.assertEqual(configPathStr, expectedPathStr)
    
    def testSuffixMustStartWithDot(self):
        with self.assertRaises(ValueError):
            configPathStr = self.config.pathWithSuffix('jpg')
    
    def testPathWithNameAndSuffix(self):
        configPathStr = str(self.config.pathWithNameAndSuffix('spam', '.jpg'))
        expectedPathStr = str(self.expectedConfigPath) + '-spam.jpg'
        self.assertEqual(configPathStr, expectedPathStr)
    
    def testRefCardURL(self):
        url = self.config.refcardURL()
        expectedURL = 'https://edrefcard.info/binds/abcdef'
        self.assertEqual(url, expectedURL)
    
    def testBindsURL(self):
        url = self.config.bindsURL()
        expectedURL = 'https://edrefcard.info/configs/abcdef.binds'
        self.assertEqual(url, expectedURL)


class ErrorTests(unittest.TestCase):
    
    def testInitsWithBlankData(self):
        errors = bindings.Errors()
        self.assertEqual(errors.unhandledDevicesWarnings, '')
        self.assertEqual(errors.deviceWarnings, '')
        self.assertEqual(errors.misconfigurationWarnings, '')
        self.assertEqual(errors.errors, '')


class testTransKey(unittest.TestCase):
    
    def testNoneReturnsNone(self):
        k = bindings.transKey(None)
        self.assertIsNone(k)
    
    def testMappedKey(self):
        k = bindings.transKey('Key_Comma')
        self.assertEqual(k, ',')
    
    def testUnmappedKey(self):
        k = bindings.transKey('Key_A')
        self.assertEqual(k, 'A')


class FontPathTests(unittest.TestCase):
    
    def testRegularNormal(self):
        path = bindings.getFontPath('Regular', 'Normal')
        self.assertEqual(path, '../fonts/Exo2.0-Regular.otf')

    def testBoldNormal(self):
        path = bindings.getFontPath('Bold', 'Normal')
        self.assertEqual(path, '../fonts/Exo2.0-Bold.otf')

    def testRegularItalic(self):
        path = bindings.getFontPath('Regular', 'Italic')
        self.assertEqual(path, '../fonts/Exo2.0-Italic.otf')

    def testBoldItalic(self):
        path = bindings.getFontPath('Bold', 'Italic')
        self.assertEqual(path, '../fonts/Exo2.0-BoldItalic.otf')
    
    
class ParserTests(unittest.TestCase):
    
    def testParseEmptyFile(self):
        path = Path('bindings/testCases/empty.binds')
        (result, errors) = bindings.parseLocalFile(path)
        expectedResult = ({}, {}, {})
        self.assertEqual(result, expectedResult)

    def testParseInvalidFile(self):
        path = Path('bindings/testCases/Help.txt')
        (result, errors) = bindings.parseLocalFile(path)
        expectedResult = ({}, {}, {})
        self.assertEqual(result, expectedResult)
        self.assertTrue(len(errors.errors) > 0)

    def testParseOneKeyBind(self):
        path = Path('bindings/testCases/one_keystroke.binds')
        ((physicalKeys, modifiers, devices), errors) = bindings.parseLocalFile(path)
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
        expectedDevices = {
            'Keyboard::0': {'HandledDevices': ['Keyboard'], 'Template': 'keyboard'}
        }
        self.assertEqual(physicalKeys, expectedKeys)
        self.assertEqual(modifiers, {})
        self.assertEqual(devices, expectedDevices)

    def testParseOneModifier(self):
        path = Path('bindings/testCases/single_modifier.binds')
        ((physicalKeys, modifiers, devices), errors) = bindings.parseLocalFile(path)
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
