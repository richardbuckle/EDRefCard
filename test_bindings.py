#!/usr/bin/env python3

import unittest
import os
import string
from collections import OrderedDict
from pathlib import Path
import contextlib
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
    
    def testRepr(self):
        representation = repr(self.config)
        self.assertEqual(representation, "Config('abcdef')")
        
    def testConfigPath(self):
        path = bindings.Config.configsPath()
        print(path)
        
    def testNames(self):
        # should not raise
        allConfigs = bindings.Config.allConfigs(sortKey=lambda obj: str(obj['description']).casefold())
        with contextlib.redirect_stdout(None):
            for obj in allConfigs:
                bindings.printListItem(obj)


class ErrorTests(unittest.TestCase):
    
    def testInitWithBlankData(self):
        errors = bindings.Errors()
        self.assertEqual(errors.unhandledDevicesWarnings, '')
        self.assertEqual(errors.deviceWarnings, '')
        self.assertEqual(errors.misconfigurationWarnings, '')
        self.assertEqual(errors.errors, '')
    
    def testInitWithData(self):
        errors = bindings.Errors(
            unhandledDevicesWarnings='spam',
            deviceWarnings='eggs',
            misconfigurationWarnings='my hovercraft is full of eels',
            errors='the larch'
        )
        self.assertEqual(errors.unhandledDevicesWarnings, 'spam')
        self.assertEqual(errors.deviceWarnings, 'eggs')
        self.assertEqual(errors.misconfigurationWarnings, 'my hovercraft is full of eels')
        self.assertEqual(errors.errors, 'the larch')
    
    def testRepr(self):
        errors = bindings.Errors(
            unhandledDevicesWarnings='spam',
            deviceWarnings='eggs',
            misconfigurationWarnings='my hovercraft is full of eels',
            errors='the larch'
        )
        expectedRepr = "Errors(unhandledDevicesWarnings='spam', deviceWarnings='eggs', misconfigurationWarnings='my hovercraft is full of eels', errors='the larch')"
        self.assertEqual(repr(errors), expectedRepr)


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


class uploadTests(unittest.TestCase):
    
    def setUp(self):
        self.testCasesPath = Path('../../bindings/testUploads').resolve(True)
    
    def testUnicodeName(self):
        path = self.testCasesPath / 'eu/euymtn.replay'
        obj = bindings.Config.unpickle(path)
        with contextlib.redirect_stdout(None):
            bindings.printListItem(obj)

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
    

class FormTests(unittest.TestCase):

    def testLeadingPunctuationNotAllowed(self):
        class FormProxy :
            def getvalue(self, key):
                return '----starts with punctuation' if key == 'description' else 'boo'
        formProxy = FormProxy()
        mode = bindings.determineMode(formProxy)
        print(mode)	
        self.assertEqual(bindings.Mode.invalid, mode)
    
    
class ParserTests(unittest.TestCase):
    
    def setUp(self):
        self.testCasesPath = Path('../../bindings/testCases').resolve(True)

    def testParseEmptyFile(self):
        path = self.testCasesPath / 'empty.binds'
        (result, errors) = bindings.parseLocalFile(path)
        expectedResult = ({}, {}, {})
        self.assertEqual(result, expectedResult)

    def testParseInvalidFile(self):
        path = self.testCasesPath / 'Help.txt'
        (result, errors) = bindings.parseLocalFile(path)
        expectedResult = ({}, {}, {})
        self.assertEqual(result, expectedResult)
        self.assertTrue(len(errors.errors) > 0)

    def testParseOneKeyBind(self):
        path = self.testCasesPath / 'one_keystroke.binds'
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
                                        'Name': 'Wingman Navlock',
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
        path = self.testCasesPath / 'single_modifier.binds'
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
                                          'Name': 'All Stop',
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

    def testParseTwoModifiers(self):
        path = self.testCasesPath / 'two_modifiers.binds'
        ((physicalKeys, modifiers, devices), errors) = bindings.parseLocalFile(path)
        expectedModifers = {
            'LogitechExtreme3DPro::0::Joy_7': 
            [
                {
                    'Device': 'LogitechExtreme3DPro',
                     'DeviceIndex': 0,
                     'Key': 'Joy_7',
                     'ModifierKey': 'LogitechExtreme3DPro::0::Joy_7/LogitechExtreme3DPro::0::Joy_8',
                     'Number': 1
                }
            ],
            'LogitechExtreme3DPro::0::Joy_7/LogitechExtreme3DPro::0::Joy_8': 
            [
                {
                    'ModifierKey': 'LogitechExtreme3DPro::0::Joy_7/LogitechExtreme3DPro::0::Joy_8',
                    'Number': 1
                }
            ],
            'LogitechExtreme3DPro::0::Joy_8': 
            [
                {
                    'Device': 'LogitechExtreme3DPro',
                    'DeviceIndex': 0,
                    'Key': 'Joy_8',
                    'ModifierKey': 'LogitechExtreme3DPro::0::Joy_7/LogitechExtreme3DPro::0::Joy_8',
                    'Number': 1
                }
            ]
        }
        self.assertEqual(modifiers, expectedModifers)

    def testParseTwoModifiersSwapped(self):
        path = self.testCasesPath / 'two_modifiers_swapped.binds'
        ((physicalKeys, modifiers, devices), errors) = bindings.parseLocalFile(path)
        expectedModifers = {
            'LogitechExtreme3DPro::0::Joy_7': 
            [
                {
                    'Device': 'LogitechExtreme3DPro',
                     'DeviceIndex': 0,
                     'Key': 'Joy_7',
                     'ModifierKey': 'LogitechExtreme3DPro::0::Joy_7/LogitechExtreme3DPro::0::Joy_8',
                     'Number': 1
                }
            ],
            'LogitechExtreme3DPro::0::Joy_7/LogitechExtreme3DPro::0::Joy_8': 
            [
                {
                    'ModifierKey': 'LogitechExtreme3DPro::0::Joy_7/LogitechExtreme3DPro::0::Joy_8',
                    'Number': 1
                }
            ],
            'LogitechExtreme3DPro::0::Joy_8': 
            [
                {
                    'Device': 'LogitechExtreme3DPro',
                    'DeviceIndex': 0,
                    'Key': 'Joy_8',
                    'ModifierKey': 'LogitechExtreme3DPro::0::Joy_7/LogitechExtreme3DPro::0::Joy_8',
                    'Number': 1
                }
            ]
        }
        self.maxDiff = None
        self.assertEqual(modifiers, expectedModifers)

def setUpModule():
    scriptsPath = Path.cwd() / 'www/scripts'
    os.chdir(scriptsPath)
    os.environ['CONTEXT_DOCUMENT_ROOT'] = str(scriptsPath.parent.resolve(True))
    
def main():   # pragma: no cover
    unittest.main()

if __name__ == '__main__':   # pragma: no cover
    main()
