#!/usr/bin/env python3

from unittest import TestCase, mock, main as testmain
from unittest.mock import MagicMock
import os
import pprint
import string
from collections import OrderedDict
from pathlib import Path
import contextlib
from www.scripts import bindings


class ConfigTests(TestCase):
    
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
        
    def testNames(self):
        # should not raise
        allConfigs = bindings.Config.allConfigs(sortKey=lambda obj: str(obj['description']).casefold())
        searchOpts = {}
        with contextlib.redirect_stdout(None):
            for obj in allConfigs:
                bindings.printListItem(obj, searchOpts)


class ErrorTests(TestCase):
    
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


class testTransKey(TestCase):
    
    def testNoneReturnsNone(self):
        k = bindings.transKey(None)
        self.assertIsNone(k)
    
    def testMappedKey(self):
        k = bindings.transKey('Key_Comma')
        self.assertEqual(k, ',')
    
    def testUnmappedKey(self):
        k = bindings.transKey('Key_A')
        self.assertEqual(k, 'A')


class testGroups(TestCase):
    
    def testGroupsHaveStyles(self):
        styledGroups = set(bindings.groupStyles.keys())
        allGroups = set({'General', 'Modifier'})
        for controlValue in bindings.controls.values():
            allGroups.add(controlValue['Group'])
        self.assertTrue(allGroups.issubset(styledGroups))
    
    def testNoRedundantGroupStyles(self):
        styledGroups = set(bindings.groupStyles.keys())
        allGroups = set({'General', 'Modifier'})
        for controlValue in bindings.controls.values():
            allGroups.add(controlValue['Group'])
        self.assertTrue(allGroups.issuperset(styledGroups))


class uploadTests(TestCase):
    
    def setUp(self):
        self.testCasesPath = Path('../../bindings/testUploads').resolve(True)
    
    def testUnicodeName(self):
        path = self.testCasesPath / 'eu/euymtn.replay'
        obj = bindings.Config.unpickle(path)
        searchOpts = {}
        with contextlib.redirect_stdout(None):
            bindings.printListItem(obj, searchOpts)


class FontPathTests(TestCase):
    
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
    

class FormTests(TestCase):

    def testLeadingPunctuationNotAllowed(self):
        class FormProxy :
            def getvalue(self, key):
                return '----starts with punctuation' if key == 'description' else 'boo'
        formProxy = FormProxy()
        mode = bindings.determineMode(formProxy)
        self.assertEqual(bindings.Mode.invalid, mode)
    

class BlocksTests(TestCase):

    def createBlockImage(self, device):
        if device == 'Keyboard': return
        bindings.createBlockImage(device, dryRun=True)

    def testDS4IsValid(self):
        self.createBlockImage('DS4') # should not raise
        
    def testAllValid(self):
        for device in bindings.supportedDevices.keys():
            self.createBlockImage(device)
    

class ModiferStylesTests(TestCase):
    
    def testZeroIndex(self):
        style = bindings.ModifierStyles.index(0)
        self.assertEqual(bindings.ModifierStyles.styles[0], style)
    
    def testTwoPastEnd(self):
        i = len(bindings.ModifierStyles.styles) + 1
        style = bindings.ModifierStyles.index(i)
        self.assertEqual(bindings.ModifierStyles.styles[1], style)

    
class ParserTests(TestCase):
    
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
        
    def testRedundantSpecialisation(self):
        control = {'Group': 'Galaxy map', 'Category': 'UI', 'Order': 12, 'Name': 'GalMap Pitch Up', 'Type': 'Digital', 'HasAnalogue': True, 'HideIfSameAs': ['PitchUpButton']}
        bind = {'Controls': OrderedDict([('CamPitchUp', 'blah'), ('PitchUpButton', 'blah')])}
        isRedundant = bindings.isRedundantSpecialisation(control, bind)
        self.assertTrue(isRedundant)

    def testNonRedundantSpecialisation(self):
        control = {'Group': 'Galaxy map', 'Category': 'UI', 'Order': 12, 'Name': 'GalMap Pitch Up', 'Type': 'Digital', 'HasAnalogue': True, 'HideIfSameAs': ['PitchUpButton']}
        bind = {'Controls': OrderedDict([('CamPitchUp', 'blah'), ('PitchDownButton', 'blah')])}
        isRedundant = bindings.isRedundantSpecialisation(control, bind)
        self.assertFalse(isRedundant)

    def testControlHasNoRedundantSpecialisation(self):
        control = {'Group': 'Misc', 'Category': 'General', 'Order': 14, 'Name': 'Night Vision', 'Type': 'Digital', 'HideIfSameAs': []}
        bind = {'Controls': OrderedDict([('NightVisionToggle', 'blah')])}
        isRedundant = bindings.isRedundantSpecialisation(control, bind)
        self.assertFalse(isRedundant)

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
                                        'HideIfSameAs': [],
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

    def testParseTwoKeyBinds(self):
        path = self.testCasesPath / 'issue26.binds'
        ((physicalKeys, modifiers, devices), errors) = bindings.parseLocalFile(path)
        expectedKeys = {
            'Keyboard::0::Key_Apostrophe': {
                'BaseKey': 'Key_Apostrophe',
                'Device': 'Keyboard',
                'DeviceIndex': 0,
                'Key': 'Key_Apostrophe',
            },
            'Keyboard::0::Key_RightShift': {
                'BaseKey': 'Key_RightShift',
                'Device': 'Keyboard',
                'DeviceIndex': 0,
                'Key': 'Key_RightShift',
            }
        }
        expectedDevices = {
            'Keyboard::0': {'HandledDevices': ['Keyboard'], 'Template': 'keyboard'}
        }
        self.assertEqual(physicalKeys.keys(), expectedKeys.keys())
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
                                          'HideIfSameAs': [],
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
        
    def test26FSSOnly(self):
        path = self.testCasesPath / 'issue26full.xml'
        errors = bindings.Errors()
        displayGroups = ['Scanners',]
        with path.open() as f:
            xml = f.read()
            (physicalKeys, modifiers, devices) = bindings.parseBindings("test", xml, displayGroups, errors)
            pprint.pprint(physicalKeys['Keyboard::0::Key_RightShift'])

    def test26FSSandShip(self):
        path = self.testCasesPath / 'issue26full.xml'
        errors = bindings.Errors()
        displayGroups = ['Ship', 'Scanners']
        with path.open() as f:
            xml = f.read()
            (physicalKeys, modifiers, devices) = bindings.parseBindings("test", xml, displayGroups, errors)
            pprint.pprint(physicalKeys['Keyboard::0::Key_RightShift'])

def setUpModule():
    scriptsPath = Path.cwd() / 'www/scripts'
    os.chdir(scriptsPath)
    os.environ['CONTEXT_DOCUMENT_ROOT'] = str(scriptsPath.parent.resolve(True))
    
def main():   # pragma: no cover
    testmain()

if __name__ == '__main__':   # pragma: no cover
    main()
