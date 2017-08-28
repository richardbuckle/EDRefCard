#!/usr/bin/env python3

__version__ = '1.0.5'

from lxml import etree

from collections import OrderedDict

from wand.drawing import Drawing
from wand.image import Image
from wand.font import Font
from wand.color import Color

import cgi
import cgitb
import sys
import string
import random
import datetime
import codecs
import os
import pickle
import re
from enum import Enum
from pathlib import Path
from urllib.parse import urljoin

try:
    from .bindingsData import *
except: # pragma: no cover
    from bindingsData import *


class Config:
    dirRoot = Path(os.environ.get('CONTEXT_DOCUMENT_ROOT', '..')).resolve()
    webRoot = urljoin(os.environ.get('SCRIPT_URI', 'https://edrefcard.info/'), '/')
    
    def newRandom():
        config = Config(Config.randomName())
        while(config.exists()):
            config = Config(Config.randomName())
        return config
    
    def __init__(self, name):
        if not name:
            raise ValueError('Config must have a name')
        self.name = name
    
    def __repr__(self):
        return "Config('%s')" % self.name
    
    def randomName():
        name = ''.join(random.choice(string.ascii_lowercase) for x in range(6))
        return name
    
    def configsPath():
        return Config.dirRoot / 'configs'
        
    def path(self):
        path = Config.configsPath() / self.name[:2] / self.name
        return path
    
    def pathWithNameAndSuffix(self, name, suffix):
        newName = '-'.join([self.name, name])
        p = self.path().with_name(newName)
        return p.with_suffix(suffix)
    
    def pathWithSuffix(self, suffix):
        return self.path().with_suffix(suffix)
        
    def exists(self):
        return self.path().exists()
        
    def makeDir(self):
        fullPath = self.path()
        dirPath = fullPath.parent
        dirPath.mkdir(parents=True, exist_ok=True)
        
    def refcardURL(self):
        url = urljoin(self.webRoot, "binds/%s" % self.name)
        return url
        
    def bindsURL(self):
        url = urljoin(self.webRoot, "configs/%s.binds" % self.name)
        return url
    
    def allConfigs(sortKey=None):
        configsPath = Config.configsPath()
        picklePaths = list(configsPath.glob('**/*.replay'))
        def loader(path):
            with path.open('rb') as file:
                object = pickle.load(file)
                object['runID'] = path.stem
                return object
        objs = [loader(path) for path in picklePaths]
        if sortKey is not None:
            objs.sort(key=sortKey)
        return objs


class Mode(Enum):
    blocks = 1
    list = 2
    replay = 3
    generate = 4


class Errors:
    
    def __init__(
            self,
            unhandledDevicesWarnings = '',
            deviceWarnings = '',
            misconfigurationWarnings = '',
            errors = ''
        ):
        self.unhandledDevicesWarnings = unhandledDevicesWarnings
        self.deviceWarnings = deviceWarnings
        self.misconfigurationWarnings = misconfigurationWarnings
        self.errors = errors
    
    def __repr__(self):
        return ("Errors(unhandledDevicesWarnings='%s', deviceWarnings='%s', misconfigurationWarnings='%s', errors='%s')" 
            % (self.unhandledDevicesWarnings, self.deviceWarnings, self.misconfigurationWarnings, self.errors))

# Utility section

# Helper to obtain a font path
def getFontPath(weight, style):
    if style == 'Normal':
        style = ''
    if weight == 'Regular' and style != '':
        weight = ''
    return '../fonts/Exo2.0-%s%s.otf' % (weight, style)

# Command group styling
groupStyles = {
    'General': {'Color': Color('#000000'), 'Font': getFontPath('Regular', 'Normal')},
    'Misc': {'Color': Color('#000000'), 'Font': getFontPath('Regular', 'Normal')},
    'Modifier': {'Color': Color('#000000'), 'Font': getFontPath('Bold', 'Normal')},
    'Galaxy map': {'Color': Color('#CCCC00'), 'Font': getFontPath('Regular', 'Normal')},
    'Commander creator': {'Color': Color('#CCCC00'), 'Font': getFontPath('Regular', 'Italic')},
    'Multicrew': {'Color': Color('#CCCC00'), 'Font': getFontPath('Bold', 'Italic')},
    'Fighter': {'Color': Color('#777777'), 'Font': getFontPath('Regular', 'Normal')},
    'Camera': {'Color': Color('#777777'), 'Font': getFontPath('Regular', 'Italic')},
    'Head look': {'Color': Color('#CC00CC'), 'Font': getFontPath('Regular', 'Normal')},
    'Ship': {'Color': Color('#CC0000'), 'Font': getFontPath('Regular', 'Normal')},
    'SRV': {'Color': Color('#00CC00'), 'Font': getFontPath('Regular', 'Normal')},
    'UI': {'Color': Color('#00CCCC'), 'Font': getFontPath('Regular', 'Normal')},
}

# Command category styling
categoryStyles = {
    'General': {'Color': Color('#0000CC'), 'Font': getFontPath('Regular', 'Normal')},
    'Combat': {'Color': Color('#CC0000'), 'Font': getFontPath('Regular', 'Normal')},
    'Social': {'Color': Color('#00CC00'), 'Font': getFontPath('Regular', 'Normal')},
    'Navigation': {'Color': Color('#000000'), 'Font': getFontPath('Regular', 'Normal')},
    'UI': {'Color': Color('#CCCC00'), 'Font': getFontPath('Regular', 'Normal')},
}

# Modifier styling - note a list not a dictionary as modifiers are numeric
modifierStyles = [
    {'Color': Color('#000000'), 'Font': getFontPath('Regular', 'Normal')},
    {'Color': Color('#FF0000'), 'Font': getFontPath('Regular', 'Normal')},
    {'Color': Color('#00FF00'), 'Font': getFontPath('Regular', 'Normal')},
    {'Color': Color('#0000FF'), 'Font': getFontPath('Regular', 'Normal')},
    {'Color': Color('#777700'), 'Font': getFontPath('Regular', 'Normal')},
    {'Color': Color('#770077'), 'Font': getFontPath('Regular', 'Normal')},
    {'Color': Color('#007777'), 'Font': getFontPath('Regular', 'Normal')},
    {'Color': Color('#777777'), 'Font': getFontPath('Regular', 'Normal')},
    {'Color': Color('#FF7777'), 'Font': getFontPath('Regular', 'Normal')},
    {'Color': Color('#77FF77'), 'Font': getFontPath('Regular', 'Normal')},
    {'Color': Color('#7777FF'), 'Font': getFontPath('Regular', 'Normal')},
    {'Color': Color('#CCCC77'), 'Font': getFontPath('Regular', 'Normal')},
    {'Color': Color('#CC77CC'), 'Font': getFontPath('Regular', 'Normal')},
    {'Color': Color('#77CCCC'), 'Font': getFontPath('Regular', 'Normal')},
]

def transKey(key):
    if key is None:
        return None
    trans = keymap.get(key)
    if trans is None:
        trans = key.replace('Key_', '')
    return trans

# Output section

def writeUrlToDrawing(config, drawing, public):
    url = config.refcardURL() if public else config.webRoot
    drawing.push()
    drawing.font = getFontPath('SemiBold', 'Normal')
    drawing.font_size = 72
    drawing.text(x=23, y=252, body=url)
    drawing.pop()

# Create a keyboard image from the template plus bindings
def createKeyboardImage(physicalKeys, modifiers, source, imageDevices, biggestFontSize, displayGroups, runId, public):
    config = Config(runId)
    filePath = config.pathWithNameAndSuffix(source, '.jpg')

    # See if it already exists or if we need to recreate it
    if filePath.exists():
        return True
    with Image(filename='../res/' + source + '.jpg') as sourceImg:
        with Drawing() as context:

            # Defaults for the font
            context.font = getFontPath('Regular', 'Normal')
            context.text_antialias = True
            context.font_style = 'normal'
            context.stroke_width = 0
            context.fill_color = Color('#000')
            context.fill_opacity = 1

            # Add the ID to the title
            writeUrlToDrawing(config, context, public)

            outputs = {}
            for group in displayGroups:
                outputs[group] = {}

            # Find the correct bindings and order them appropriately
            for physicalKeySpec, physicalKey in physicalKeys.items():
                itemDevice = physicalKey.get('Device')
                itemKey = physicalKey.get('Key')

                # Only show it if we are handling the appropriate image at this time
                if itemDevice not in imageDevices:
                    continue

                for modifier, bind in physicalKey.get('Binds').items():
                    for controlKey, control in bind.get('Controls').items():
                        bind = {}
                        bind['Control'] = control
                        bind['Key'] = itemKey
                        bind['Modifiers'] = []

                        if modifier != 'Unmodified':
                            for modifierKey, modifierControls in modifiers.items():
                                for modifierControl in modifierControls:
                                    if modifierControl.get('ModifierKey') == modifier and modifierControl.get('Key') is not None:
                                        bind['Modifiers'].append(modifierControl.get('Key'))

                        outputs[control['Group']][control['Name']] = bind

            # Set up a screen state to handle output
            screenState = {}
            screenState['baseX'] = 60
            screenState['baseY'] = 320
            screenState['maxWidth'] = 0
            screenState['thisWidth'] = 0
            screenState['currentX'] = screenState['baseX']
            screenState['currentY'] = screenState['baseY']

            font = Font(getFontPath('Regular', 'Normal'), antialias=True, size=biggestFontSize)
            groupTitleFont = Font(getFontPath('Regular', 'Normal'), antialias=True, size=biggestFontSize*2)
            context.stroke_width=2
            context.stroke_color=Color('#000')
            context.fill_opacity=0

            # Go through once for each display group
            for displayGroup in displayGroups:
                if outputs[displayGroup] == {}:
                    continue

                writeText(context, sourceImg, displayGroup, screenState, groupTitleFont, False, True)

                orderedOutputs = OrderedDict(sorted(outputs[displayGroup].items(), key=lambda x: x[1].get('Control').get('Order')))
                for bindKey, bind in orderedOutputs.items():
                    for modifier in bind.get('Modifiers', []):
                        writeText(context, sourceImg, transKey(modifier), screenState, font, True, False)
                    writeText(context, sourceImg, transKey(bind.get('Key')), screenState, font, True, False)
                    writeText(context, sourceImg, bind.get('Control').get('Name'), screenState, font, False, True)

            context.draw(sourceImg)
            sourceImg.save(filename=str(filePath))
    return True

def appendKeyboardImage(createdImages, physicalKeys, modifiers, displayGroups, runId, public):
    def countKeyboardItems(physicalKeys):
        keyboardItems = 0
        for  physicalKey in physicalKeys.values():
            if physicalKey.get('Device') == 'Keyboard':
                for bind in physicalKey.get('Binds').values():
                    keyboardItems = keyboardItems + len(bind.get('Controls'))
        return keyboardItems
    
    def fontSizeForKeyBoardItems(physicalKeys):
        keyboardItems = countKeyboardItems(physicalKeys)
        if keyboardItems > 48:
            fontSize = 40 - int(((keyboardItems - 48) / 20) * 4)
            if fontSize < 24:
                fontSize = 24
        else:
            fontSize = 40
        return fontSize
    
    fontSize = fontSizeForKeyBoardItems(physicalKeys)
    createKeyboardImage(physicalKeys, modifiers, 'keyboard', ['Keyboard'], fontSize, displayGroups, runId, public)
    createdImages.append('Keyboard')

# Write text, possible wrapping
def writeText(context, img, text, screenState, font, surround, newLine):
    if text is None:
        return
    border = 4

    # Work out the size of the text
    context.font = font.path
    context.font_style = 'normal'
    context.font_size = font.size
    context.push()
    context.stroke_width=0
    context.fill_color=Color('#000')
    context.fill_opacity=1

    metrics = context.get_font_metrics(img, text, multiline=False)
    if screenState['currentY'] + int(metrics.text_height + 32) > 2160:
        # Gone off the bottom of the page; go to next column
        screenState['currentY'] = screenState['baseY']
        screenState['baseX'] = screenState['baseX'] + screenState['maxWidth'] + 49
        screenState['currentX'] = screenState['baseX']
        screenState['maxWidth'] = 0
        screenState['thisWidth'] = 0
    # Center the text
    x = screenState['currentX']
    y = screenState['currentY'] + int(metrics.ascender)
    context.text(x=x, y=y, body=text)
    context.pop()

    if surround is True:
        # text y is baseline, rectangle y is top
        y = screenState['currentY'] - border
        context.rectangle(left=x - (border * 4), top=y - (border * 2), width=int(metrics.text_width) + (border*8), height=int(metrics.text_height) + (border*4), radius=30)
        width = int(metrics.text_width + 48)
    else:
        width = int((metrics.text_width + 72)/48)*48
    screenState['thisWidth'] = screenState['thisWidth'] + width

    if newLine is True:
        if screenState['thisWidth'] > screenState['maxWidth']:
            screenState['maxWidth'] = screenState['thisWidth']
        screenState['currentY'] = screenState['currentY'] + int(metrics.text_height + 32)
        screenState['currentX'] = screenState['baseX']
        screenState['thisWidth'] = 0
    else:
        screenState['currentX'] = screenState['currentX'] + width

def createBlockImage(supportedDeviceKey):
    supportedDevice = supportedDevices[supportedDeviceKey]
    # Set up the path for our file
    templateName = supportedDevice['Template']
    config = Config(templateName)
    config.makeDir()
    filePath = config.pathWithSuffix('.jpg')
    
    with Image(filename='../res/' + supportedDevice['Template'] + '.jpg') as sourceImg:
        with Drawing() as context:
            context.stroke_width=1
            context.stroke_color=Color('#F00')
            context.fill_color=Color('#0F0')

            for keyDevice in supportedDevice.get('KeyDevices', supportedDevice.get('HandledDevices')):
                for box in hotasDetails[keyDevice].values():
                    context.rectangle(top=box['y'], left=box['x'], width=box['width'], height=box.get('height', 54))

            context.draw(sourceImg)
            sourceImg.save(filename=str(filePath))

# We have a limited number of modifier styles so balance them out across the modifier number
def getModifierStyle(num):
    if num == 0:
        return modifierStyles[0]
    elif num < 100:
        return modifierStyles[0 + (num % 13)]
    else:
        return modifierStyles[(113 - num) % 13]

# Create a HOTAS image from the template plus bindings
def createHOTASImage(physicalKeys, modifiers, source, imageDevices, biggestFontSize, config, public, styling, deviceIndex, misconfigurationWarnings):
    # Set up the path for our file
    runId = config.name
    if deviceIndex == 0:
        name = source
    else:
        name = '%s-%s' % (source, deviceIndex)
    filePath = config.pathWithNameAndSuffix(name, '.jpg')
    
    # See if it already exists or if we need to recreate it
    if filePath.exists():
        return True
    with Image(filename='../res/' + source + '.jpg') as sourceImg:
        with Drawing() as context:

            # Defaults for the font
            context.font = getFontPath('Regular', 'Normal')
            context.text_antialias = True
            context.font_style = 'normal'
            context.stroke_width = 0
            context.fill_color = Color('#000')
            context.fill_opacity = 1

            # Add the ID to the title
            writeUrlToDrawing(config, context, public)

            for physicalKeySpec, physicalKey in physicalKeys.items():
                itemDevice = physicalKey.get('Device')
                itemDeviceIndex = int(physicalKey.get('DeviceIndex'))
                itemKey = physicalKey.get('Key')

                # Only show it if we are handling the appropriate image at this time
                if itemDevice not in imageDevices:
                    continue

                # Only show it if we are handling the appropriate index at this time
                if itemDeviceIndex != deviceIndex: 
                    continue

                # Find the details for the control
                texts = []
                hotasDetail = None
                try:
                    hotasDetail = hotasDetails.get(itemDevice).get(itemKey)
                except AttributeError:
                    hotasDetail = None
                if hotasDetail is None:
                    sys.stderr.write('%s: No control detail for %s\n' % (runId, physicalKeySpec))
                    continue

                # First obtain the modifiers if there are any
                for keyModifier in modifiers.get(physicalKeySpec, []):
                    if styling == 'Modifier':
                        style = modifierStyles[keyModifier.get('Number') % 13]
                    else:
                        style = groupStyles.get('Modifier')
                    texts.append({'Text': 'Modifier %s' % (keyModifier.get('Number')), 'Group': 'Modifier', 'Style': style})
                if '::Joy' in physicalKeySpec:
                    # Same again but for positive modifier
                    for keyModifier in modifiers.get(physicalKeySpec.replace('::Joy', '::Pos_Joy'), []):
                        if styling == 'Modifier':
                            style = modifierStyles[keyModifier.get('Number') % 13]
                        else:
                            style = groupStyles.get('Modifier')
                        texts.append({'Text': 'Modifier %s' % (keyModifier.get('Number')), 'Group': 'Modifier', 'Style': style})
                    # Same again but for negative modifier
                    for keyModifier in modifiers.get(physicalKeySpec.replace('::Joy', '::Neg_Joy'), []):
                        if styling == 'Modifier':
                            style = modifierStyles[keyModifier.get('Number') % 13]
                        else:
                            style = groupStyles.get('Modifier')
                        texts.append({'Text': 'Modifier %s' % (keyModifier.get('Number')), 'Group': 'Modifier', 'Style': style})

                # Next obtain unmodified bindings
                for modifier, bind in physicalKey.get('Binds').items():
                    if modifier == 'Unmodified':
                        for controlKey, control in bind.get('Controls').items():
                            overridden = False
                            for overrideKey in bind.get('Controls').keys():
                                if overrideKey in control.get('OverriddenBy'):
                                    overridden = True
                            if overridden is True:
                                continue
                            # Check if this is a digital control on an analogue stick with an analogue equivalent
                            if control.get('Type') == 'Digital' and control.get('HasAnalogue') is True and hotasDetail.get('Type') == 'Analogue':
                                if misconfigurationWarnings == '':
                                    misconfigurationWarnings = '<h1>Misconfiguration detected</h1>You have one or more analogue controls configured incorrectly. Please see <a href="https://forums.frontier.co.uk/showthread.php?t=209792">this thread</a> for details of the problem and how to correct it.<br/> <b>Your misconfigured controls:</b> <b>%s</b> ' % control['Name']
                                else:
                                    misconfigurationWarnings = '%s, <b>%s</b>' % (misconfigurationWarnings, control['Name'])
                                #sys.stderr.write('%s: Digital command %s found on hotas control %s::%s\n' % (runId, control['Name'], itemDevice, itemKey))

                            if styling == 'Modifier':
                                texts.append({'Text': '%s' % (control.get('Name')), 'Group': control.get('Group'), 'Style': modifierStyles[0]})
                            elif styling == 'Category':
                                texts.append({'Text': '%s' % (control.get('Name')), 'Group': control.get('Group'), 'Style': categoryStyles.get(control.get('Category', 'General'))})
                            else:
                                texts.append({'Text': '%s' % (control.get('Name')), 'Group': control.get('Group'), 'Style': groupStyles.get(control.get('Group'))})

                # Next obtain bindings with modifiers
                # Lazy approach to do this but covers us for now
                for curModifierNum in range(1, 200):
                    for modifier, bind in physicalKey.get('Binds').items():
                        if modifier != 'Unmodified':
                            keyModifiers = modifiers.get(modifier)
                            modifierNum = 0
                            for keyModifier in keyModifiers:
                                if keyModifier['ModifierKey'] == modifier:
                                    modifierNum = keyModifier['Number']
                                    break
                            if modifierNum != curModifierNum:
                                continue
                            for controlKey, control in bind.get('Controls').items():
                                overridden = False
                                for overrideKey in bind.get('Controls').keys():
                                    if overrideKey in control.get('OverriddenBy'):
                                        overridden = True
                                if overridden == True:
                                    continue
                                else:
                                    if styling == 'Modifier':
                                        texts.append({'Text': '%s' % control.get('Name'), control.get('Group'): 'Modifier', 'Style': getModifierStyle(curModifierNum)})
                                        # sys.stderr.write('Writing %s with style %s\n' % (control.get('Name'), getModifierStyle(curModifierNum)));
                                    elif styling == 'Category':
                                        texts.append({'Text': '%s[%s]' % (control.get('Name'), curModifierNum), 'Group': control.get('Group'), 'Style': categoryStyles.get(control.get('Category', 'General'))})
                                    else:
                                        texts.append({'Text': '%s[%s]' % (control.get('Name'), curModifierNum), 'Group': control.get('Group'), 'Style': groupStyles.get(control.get('Group'))})
            
                # Obtain the layout of the texts and write them
                texts = layoutText(sourceImg, context, texts, hotasDetail, biggestFontSize)
                for text in texts:
                    context.font_size = text['Size']
                    context.font = text['Style']['Font']
                    if styling != 'None':
                        context.fill_color = text['Style']['Color']
                    context.text(x=text['X'], y=text['Y'], body=text['Text'])

            # Also need to add standalone modifiers (those without other binds)
            for modifierSpec, keyModifiers in modifiers.items():
                modifierTexts = []
                for keyModifier in keyModifiers:
                    if keyModifier.get('Device') not in imageDevices:
                        # We don't have an image for this device
                        continue
                    if int(keyModifier.get('DeviceIndex')) != deviceIndex:
                        # This is not four our current device
                        continue
                    if '/' in modifierSpec:
                        # This is a logical modifier so ignore it
                        continue
                    if physicalKeys.get(modifierSpec) is not None or physicalKeys.get(modifierSpec.replace('::Pos_Joy', '::Joy')) is not None or physicalKeys.get(modifierSpec.replace('::Neg_Joy', '::Joy')) is not None:
                        # This has already been handled because it has other binds
                        continue

                    modifierKey = keyModifier.get('Key')
                    hotasDetail = hotasDetails.get(keyModifier.get('Device')).get(modifierKey)
                    if hotasDetail is None:
                        sys.stderr.write('%s: No location for %s\n' % (runId, modifierSpec))
                        continue

                    if styling == 'Modifier':
                        style = getModifierStyle(keyModifier.get('Number'))
                    else:
                        style = groupStyles.get('Modifier')
                    modifierTexts.append({'Text': 'Modifier %s' % (keyModifier.get('Number')), 'Group': 'Modifier', 'Style': style})

                if modifierTexts != []:
                    # Obtain the layout of the modifier text and write it
                    modifierTexts = layoutText(sourceImg, context, modifierTexts, hotasDetail, biggestFontSize)
                    for text in modifierTexts:
                        context.font_size = text['Size']
                        context.font = text['Style']['Font']
                        if styling != 'None':
                            context.fill_color = text['Style']['Color']
                        context.text(x=text['X'], y=text['Y'], body=text['Text'])

            context.draw(sourceImg)
            sourceImg.save(filename=str(filePath))
    return True

def layoutText(img, context, texts, hotasDetail, biggestFontSize):
    width = hotasDetail.get('width')
    height = hotasDetail.get('height', 54)

    # Work out the best font size
    fontSize = calculateBestFitFontSize(context, width, height, texts, biggestFontSize)

    # Work out location of individual texts
    currentX = hotasDetail.get('x')
    currentY = hotasDetail.get('y')
    maxX = hotasDetail.get('x') + hotasDetail.get('width')
    metrics = None

    for text in texts:
        text['Size'] = fontSize
        context.font = text['Style']['Font']
        context.font_size = fontSize
        metrics = context.get_font_metrics(img, text['Text'], multiline=False)
        if currentX + int(metrics.text_width) > maxX:
            # Newline
            currentX = hotasDetail.get('x')
            currentY = currentY + fontSize
        text['X'] = currentX
        text['Y'] = currentY + int(metrics.ascender)
        currentX = currentX + int(metrics.text_width + metrics.character_width)

    # We want to centre the texts vertically, which we can now do as we know how much space the texts take up
    textHeight = currentY + fontSize - hotasDetail.get('y')
    yOffset = int((height - textHeight) / 2) - int(fontSize / 6)
    for text in texts:
        text['Y'] = text['Y'] + yOffset

    return texts

# Calculate the best fit font size for our text given the dimensions of the box
def calculateBestFitFontSize(context, width, height, texts, biggestFontSize):
    fontSize = biggestFontSize
    context.push()
    with Image(width=width, height=height) as img:
        # Step through the font size until we find one that fits
        fits = False
        while fits == False:
            currentX = 0
            currentY = 0
            tooLong = False
            for text in texts:
                context.font = text['Style']['Font']
                context.font_size = fontSize
                metrics = context.get_font_metrics(img, text['Text'], multiline=False)
                if currentX + int(metrics.text_width) > width:
                    if currentX == 0:
                        # This single entry is too long for the box; shrink it
                        tooLong = True
                        break
                    else:
                        # Newline
                        currentX = 0
                        currentY = currentY + fontSize
                text['X'] = currentX
                text['Y'] = currentY + int(metrics.ascender)
                currentX = currentX + int(metrics.text_width + metrics.character_width)
            if tooLong is False and currentY + metrics.text_height < height:
                fits = True
            else:
                fontSize = fontSize -1 
    context.pop()
    return fontSize
    
def calculateBestFontSize(context, text, hotasDetail, biggestFontSize):
    width = hotasDetail.get('width')
    height = hotasDetail.get('height', 54)
    with Image(width=width, height=height) as img:

        # Step through the font size until we find one that fits
        fontSize = biggestFontSize
        fits = False
        while fits == False:
            fitText = text
            context.font_size = fontSize
            # See if it fits on a single line
            metrics = context.get_font_metrics(img, fitText, multiline=False)
            if metrics.text_width <= hotasDetail.get('width'):
                fits = True
            else:
                # See if we can break out the text on to multiple lines
                lines = max(int(height / metrics.text_height), 1)
                if lines == 1:
                    # Not enough room for more lines
                    fontSize = fontSize - 1
                else:
                    fitText = ''
                    minLineLength = int(len(text) / lines)
                    regex = r'.{%s}[^,]*, |.+' % minLineLength
                    matches = re.findall(regex, text)
                    for match in matches:
                        if fitText == '':
                            fitText = match
                        else:
                            fitText = '%s\n%s' % (fitText, match)

                    metrics = context.get_font_metrics(img, fitText, multiline=True)
                    if metrics.text_width <= hotasDetail.get('width'):
                        fits = True
                    else:
                        fontSize = fontSize - 1

    return (fitText, fontSize, metrics)

def printList():
    print('<div id="banner"><h1>EDRefCard: public configurations</h1></div>')
    print('<p>Yes, we know this is very basic. Proper search support is coming soon.</p>')
    objs = Config.allConfigs(sortKey=lambda obj: str(obj['description']))
    print('<table>')
    print('''
        <tr>
            <th align="left">Description</th>
            <th align="left">Controllers</th>
            <th align="left">Date</th>
        </tr>
    ''')
    for obj in objs:
        config = Config(obj['runID'])
        refcardURL = str(config.refcardURL())
        dateStr = str(obj['timestamp'].ctime())
        name = str(obj['description'])
        controllers = [fullKey.split('::')[0] for fullKey in obj['devices'].keys()]
        silencedComtrollers = ['Mouse', 'Keyboard']
        controllers = [controller for controller in controllers if not controller in silencedComtrollers]
        controllers.sort()
        controllersStr = ', '.join(controllers)
        if name is '': 
            # if the uploader didn't bother to name their config, skip it
            continue
        print('''
        <tr>
            <td>
                <a href=%s>%s</a>
            </td>
            <td>
                %s
            </td>
            <td>
                %s
            </td>
        </tr>
        ''' % (refcardURL, cgi.escape(name, quote=True), controllersStr, dateStr))
    print ('</table>')

def printRefCard(config, public, createdImages, deviceForBlockImage, errors):
    runId = config.name
    if errors.unhandledDevicesWarnings != '':
        print('%s<br/>' % errors.unhandledDevicesWarnings)
    if errors.misconfigurationWarnings != '':
        print('%s<br/>' % errors.misconfigurationWarnings)
    if errors.deviceWarnings != '':
        print('%s<br/>' % errors.deviceWarnings)
    if errors.errors != '':
        print('%s<br/>' % errors.errors)
    else:
        for createdImage in createdImages:
            if '::' in createdImage:
                # Split the created image in to device and device index
                m = re.search(r'(.*)\:\:([01])', createdImage)
                device = m.group(1)
                deviceIndex = int(m.group(2))
            else:
                device = createdImage
                deviceIndex = 0
            if deviceIndex == 0:
                print('<img width="100%%" src="../configs/%s/%s-%s.jpg"/><br/>' % (runId[:2], runId, supportedDevices[device]['Template']))
            else:
                print('<img width="100%%" src="../configs/%s/%s-%s-%s.jpg"/><br/>' % (runId[:2], runId, supportedDevices[device]['Template'], deviceIndex))
        if deviceForBlockImage is not None:
            print('<img width="100%%" src="../configs/%s/%s.jpg"/><br/>' % (supportedDevices[deviceForBlockImage]['Template'][:2], supportedDevices[deviceForBlockImage]['Template']))
        if deviceForBlockImage is None and public is True:
            linkURL = config.refcardURL()
            bindsURL = config.bindsURL()
            print('<p/>Link directly to this page with the URL <a href="%s">%s</a>' % (linkURL, linkURL))
            print('<p/>You can download the custom binds file for the configuration shown above at <a href="%s">%s</a>.  Replace your existing custom binds file with this file to use these controls.' % (bindsURL, bindsURL))
    print('<p/>')

def printBody(mode, config, public, createdImages, deviceForBlockImage, errors):
    if mode is Mode.list:
        printList()
    else:
        printRefCard(config, public, createdImages, deviceForBlockImage, errors)

def printSupportPara():
    supportPara = '<p>Version %s<br>Please direct questions and suggestions and support requests to <a href="https://forums.frontier.co.uk/showthread.php?t=212866">the thread on the official Elite: Dangerous forums</a>.</p>' % __version__
    print(supportPara)

def printHTML(mode, config, public, createdImages, deviceForBlockImage, errors):
    print('Content-Type: text/html')
    print()
    print('<html>')
    print('<head><title>EDRefCard</title></head>')
    print('<body>')
    printBody(mode, config, public, createdImages, deviceForBlockImage, errors)
    printSupportPara()
    print('<p><a href="/">Home</a>.')
    print('</body>')
    print('</html>')

# Parser section

def parseBindings(runId, xml, displayGroups, errors):
    parser = etree.XMLParser(encoding='utf-8')
    try:
        tree = etree.fromstring(bytes(xml, 'utf-8'), parser=parser)
    except etree.XMLSyntaxError:
        errors.errors = '<h1>Incorrect file supplied; please go back and select your binds file as per the instructions.<h1>'
        xml = '<root></root>'
        tree = etree.fromstring(bytes(xml, 'utf-8'), parser=parser)
    
    physicalKeys = {}
    modifiers = {}
    hotasModifierNum = 1
    keyboardModifierNum = 101
    devices = {}

    if len(tree.findall(".//*[@Device='T16000MTHROTTLE']")) > 0:
        hasT16000MThrottle = True
    else:
        hasT16000MThrottle = False

    xmlBindings = tree.findall(".//Binding") + tree.findall(".//Primary") + tree.findall(".//Secondary")
    for xmlBinding in xmlBindings:
        controlName = xmlBinding.getparent().tag

        device = xmlBinding.get('Device')
        if device == '{NoDevice}':
            continue

        # Rewrite the device if this is a T16000M stick and we have a T16000M throttle
        if device == 'T16000M' and hasT16000MThrottle == True:
            device = 'T16000MFCS'

        deviceIndex = xmlBinding.get('DeviceIndex', 0)

        key = xmlBinding.get('Key')
        # Remove the Neg_ and Pos_ headers to put digital buttons on analogue devices
        if key is not None:
            if key.startswith('Neg_'):
                key = key.replace('Neg_', '', 1)
            if key.startswith('Pos_'):
                key = key.replace('Pos_', '', 1)

        def modifierSortKey(modifierInfo):
            modifierDevice = modifierInfo.get('Device')
            # Rewrite the device if this is a T16000M stick and we have a T16000M throttle
            if modifierDevice == 'T16000M' and hasT16000MThrottle == True:
                modifierDevice = 'T16000MFCS'
            modifierKey = '%s::%s::%s' % (modifierDevice, modifierInfo.get('DeviceIndex', 0), modifierInfo.get('Key'))
            return modifierKey
            
        modifiersInfo = xmlBinding.findall('Modifier')
        modifiersInfo = sorted(modifiersInfo, key=modifierSortKey)
        modifiersKey = 'Unmodified'
        if modifiersInfo:
            modifiersKey = ''
            for modifierInfo in modifiersInfo:
                modifierKey = modifierSortKey(modifierInfo)
                if modifiersKey == '':
                    modifiersKey = modifierKey
                else:
                    modifiersKey = '%s/%s' % (modifiersKey, modifierKey)
            # See if we already have the modifier
            foundKeyModifier = False
            keyModifiers = modifiers.get(modifiersKey, [])
            # Store it in case it didn't exist prior to the above call
            modifiers[modifiersKey] = keyModifiers
            for keyModifier in keyModifiers:
                if keyModifier.get('ModifierKey') == modifiersKey:
                    foundKeyModifier = True
                    break
            if not foundKeyModifier:
                # Create individual modifiers
                for modifierInfo in modifiersInfo:
                    modifier = {}
                    modifier['ModifierKey'] = modifiersKey
                    modifierDevice = modifierInfo.get('Device')
                    # Rewrite the device if this is a T16000M stick and we have a T16000M throttle
                    if modifierDevice == 'T16000M' and hasT16000MThrottle == True:
                        modifierDevice = 'T16000MFCS'
                    if modifierDevice == 'Keyboard':
                        modifier['Number'] = keyboardModifierNum
                    else:
                        modifier['Number'] = hotasModifierNum
                    modifier['Device'] = modifierDevice
                    modifier['DeviceIndex'] = modifierInfo.get('DeviceIndex', 0)
                    modifier['Key'] = modifierInfo.get('Key')
                    modifierKey = '%s::%s::%s' % (modifierDevice, modifierInfo.get('DeviceIndex', 0), modifierInfo.get('Key'))
                    updatedModifiers = modifiers.get(modifierKey, [])
                    updatedModifiers.append(modifier)
                    modifiers[modifierKey] = updatedModifiers
                if '/' in modifiersKey:
                    # Also need to add composite modifier
                    modifier = {}
                    modifier['ModifierKey'] = modifiersKey
                    modifierDevice = modifierInfo.get('Device')
                    # Rewrite the device if this is a T16000M stick and we have a T16000M throttle
                    if modifierDevice == 'T16000M' and hasT16000MThrottle == True:
                        modifierDevice = 'T16000MFCS'
                    if modifierDevice == 'Keyboard':
                        modifier['Number'] = keyboardModifierNum
                    else:
                        modifier['Number'] = hotasModifierNum
                    keyModifiers.append(modifier)
                if modifierInfo.get('Device') == 'Keyboard':
                    keyboardModifierNum = keyboardModifierNum + 1
                else:
                    hotasModifierNum = hotasModifierNum + 1
        control = controls.get(controlName)
        if control is None:
            sys.stderr.write('%s: No control for %s\n' % (runId, controlName))
            control = {}
            control['Group'] = 'General'
            control['Name'] = controlName
            control['Order'] = 999
            control['OverriddenBy'] = []
            control['Type'] = 'Digital'
        if control['Group'] not in displayGroups:
            # The user isn't interested in this control group so drop it
            continue

        itemKey = '%s::%s::%s' % (device, deviceIndex, key)
        deviceKey = '%s::%s' % (device, deviceIndex)
        # Obtain the relevant supported device
        thisDevice = None
        for supportedDevice in supportedDevices.values():
            if device in supportedDevice['HandledDevices']:
                thisDevice = supportedDevice
                break
        devices[deviceKey] = thisDevice
        physicalKey = physicalKeys.get(itemKey)
        if physicalKey is None:
            physicalKey = {}
            physicalKey['Device'] = device
            physicalKey['DeviceIndex'] = deviceIndex
            # Get the unaltered key (might be prefixed with Neg_ or Pos_) and the mapped key
            physicalKey['BaseKey'] = xmlBinding.get('Key')
            physicalKey['Key'] = key
            physicalKey['Binds'] = {}
            physicalKeys[itemKey] = physicalKey
        bind = physicalKey['Binds'].get(modifiersKey)
        if bind is None:
            bind = {}
            bind['Controls'] = OrderedDict()
            physicalKey['Binds'][modifiersKey] = bind
        bind['Controls'][controlName] = control

    return (physicalKeys, modifiers, devices)

def parseForm(form):
    displayGroups = []
    if form.getvalue('showgalaxymap'):
        displayGroups.append('Galaxy map')
    if form.getvalue('showheadlook'):
        displayGroups.append('Head look')
    if form.getvalue('showsrv'):
        displayGroups.append('SRV')
    if form.getvalue('showship'):
        displayGroups.append('Ship')
    if form.getvalue('showui'):
        displayGroups.append('UI')
    if form.getvalue('showfighter'):
        displayGroups.append('Fighter')
    if form.getvalue('showmulticrew'):
        displayGroups.append('Multicrew')
    if form.getvalue('showcamera'):
        displayGroups.append('Camera')
    if form.getvalue('showcommandercreator'):
        displayGroups.append('Commander creator')
    if form.getvalue('showmisc'):
        displayGroups.append('Misc')
    if form.getvalue('keyboard'):
        showKeyboard = True
    else:
        showKeyboard = False
    
    styling = 'None'  # Yes we do mean a string 'None'
    if form.getvalue('styling') == 'group':
        styling = 'Group'
    if form.getvalue('styling') == 'category':
        styling = 'Category'
    if form.getvalue('styling') == 'modifier':
        styling = 'Modifier'
    description = form.getvalue('description')
    if description is None:
        description = ''
    return (displayGroups, showKeyboard, styling, description)
    
def determineMode(form):
    deviceForBlockImage = form.getvalue('blocks')
    wantList = form.getvalue('list')
    runIdToReplay = form.getvalue('replay')
    
    if deviceForBlockImage is not None:
        mode = Mode.blocks
    elif wantList is not None:
        mode = Mode.list
    elif runIdToReplay is not None:
        mode = Mode.replay
    else:
        mode = Mode.generate
    return mode

def saveReplayInfo(config, description, styling, displayGroups, devices, showKeyboard, errors):
    replayInfo = {}
    replayInfo['displayGroups'] = displayGroups
    replayInfo['showKeyboard'] = showKeyboard
    replayInfo['misconfigurationWarnings'] = errors.misconfigurationWarnings
    replayInfo['unhandledDevicesWarnings'] = errors.unhandledDevicesWarnings
    replayInfo['deviceWarnings'] = errors.deviceWarnings
    replayInfo['styling'] = styling
    replayInfo['description'] = description
    replayInfo['timestamp'] = datetime.datetime.now(datetime.timezone.utc)
    replayInfo['devices'] = devices
    replayPath = config.pathWithSuffix('.replay')
    with replayPath.open('wb') as pickleFile:
        pickle.dump(replayInfo, pickleFile)

def parseLocalFile(filePath):
    displayGroups = groupStyles.keys()
    styling = 'None'  # Yes we do mean a string 'None'
    config = Config('000000')
    errors = Errors()
    with filePath.open() as f:
        xml = f.read()
        (physicalKeys, modifiers, devices) = parseBindings(config.name, xml, displayGroups, errors)
        return ((physicalKeys, modifiers, devices), errors)

# API section

def main():
    cgitb.enable()
    
    # Obtain form input and set up our variables
    form = cgi.FieldStorage()
    
    config = Config.newRandom()
    styling = 'None'
    description = ''
    public = False
    createdImages = []
    errors = Errors()
    
    deviceForBlockImage = form.getvalue('blocks')
    mode = determineMode(form)
    if mode is Mode.blocks:
        try:
            deviceForBlockImage = form.getvalue('blocks')
            createBlockImage(deviceForBlockImage)
        except KeyError:
            errors.errors = '<h1>%s is not a supported controller.</h1>' % deviceForBlockImage
            xml = '<root></root>'
        createdImages = []
    elif mode is Mode.replay:
        fileitem = {}
        runId = form.getvalue('replay')
        public = True
        try:
            config = Config(runId)
            bindsPath = config.pathWithSuffix('.binds')
            replayPath = config.pathWithSuffix('.replay')
            if not (bindsPath.exists() and replayPath.exists):
                raise FileNotFoundError
            with codecs.open(str(bindsPath), 'r', 'utf-8') as fileInput:
                xml = fileInput.read()
            try:
                with replayPath.open("rb") as pickleFile:
                    replayInfo = pickle.load(pickleFile)
                    displayGroups =  replayInfo.get('displayGroups', ['Galaxy map', 'General', 'Head look', 'SRV', 'Ship', 'UI'])
                    showKeyboard = replayInfo.get('showKeyboard', True)
                    errors.misconfigurationWarnings = replayInfo.get('misconfigurationWarnings', replayInfo.get('warnings', ''))
                    errors.deviceWarnings = replayInfo.get('deviceWarnings', '')
                    errors.unhandledDevicesWarnings = ''
                    styling = replayInfo.get('styling', 'None')
                    description = replayInfo.get('description', '')
                    timestamp = replayInfo.get('timestamp')
                    # devices = replayInfo['devices']
            except FileNotFoundError:
                displayGroups = ['Galaxy map', 'General', 'Head look', 'SRV', 'Ship', 'UI']
                showKeyboard = True
        except (ValueError, FileNotFoundError):
            errors.errors = '<h1>Configuration "%s" not found</h1>' % runId
            displayGroups = ['Galaxy map', 'General', 'Head look', 'SRV', 'Ship', 'UI']
            xml = '<root></root>'
    elif mode is Mode.generate:
        config = Config.newRandom()
        config.makeDir()
        runId = config.name
        displayGroups = []
        xml = form.getvalue('bindings')
        if xml is None or xml is b'':
            errors.errors = '<h1>No bindings file supplied; please go back and select your binds file as per the instructions.</h1>'
            xml = '<root></root>'
        else:
            xml = xml.decode(encoding='utf-8')
            bindsPath = config.pathWithSuffix('.binds')
            with codecs.open(str(bindsPath), 'w', 'utf-8') as xmlOutput:
                xmlOutput.write(xml)
        
        (displayGroups, showKeyboard, styling, description) = parseForm(form)
        public = len(description) > 0
        
    if mode is Mode.replay or mode is Mode.generate:
        (physicalKeys, modifiers, devices) = parseBindings(runId, xml, displayGroups, errors)
        
        alreadyHandledDevices = []
        createdImages = []
        for supportedDeviceKey, supportedDevice in supportedDevices.items():
            if supportedDeviceKey == 'Keyboard':
                # We handle the keyboard separately below
                continue

            for deviceIndex in [0, 1]:
                # See if we handle this device
                handled = False
                for handledDevice in supportedDevice.get('KeyDevices', supportedDevice.get('HandledDevices')):
                    if devices.get('%s::%s' % (handledDevice, deviceIndex)) is not None:
                        handled = True
                        break

                if handled is True:
                    # See if we have any new bindings for this device
                    hasNewBindings = False
                    for device in supportedDevice.get('KeyDevices', supportedDevice.get('HandledDevices')):
                        deviceKey = '%s::%s' % (device, deviceIndex)
                        if deviceKey not in alreadyHandledDevices:
                            hasNewBindings = True
                            break
                    if hasNewBindings is True:
                        createHOTASImage(physicalKeys, modifiers, supportedDevice['Template'], supportedDevice['HandledDevices'], 40, config, public, styling, deviceIndex, errors.misconfigurationWarnings)
                        createdImages.append('%s::%s' % (supportedDeviceKey, deviceIndex))
                        for handledDevice in supportedDevice['HandledDevices']:
                            alreadyHandledDevices.append('%s::%s' % (handledDevice, deviceIndex))
        
        if devices.get('Keyboard::0') is not None:
            appendKeyboardImage(createdImages, physicalKeys, modifiers, displayGroups, runId, public)
        
        for deviceKey, device in devices.items():
            # Arduino Leonardo is used for head tracking so ignore it, along with vJoy (Tobii Eyex) and 16D00AEA (EDTracker)
            if device is None and deviceKey != 'Mouse::0' and deviceKey != 'ArduinoLeonardo::0' and deviceKey != 'vJoy::0' and deviceKey != 'vJoy::1' and deviceKey != '16D00AEA::0':
                sys.stderr.write('%s: found unsupported device %s\n' % (runId, deviceKey))
                if errors.unhandledDevicesWarnings  == '':
                    errors.unhandledDevicesWarnings = '<h1>Unknown controller detected</h1>You have a device that is not supported at this time. Please report details of your device by following the link at the bottom of this page supplying the reference "%s" and we will attempt to add support for it.' % runId
            if device is not None and 'ThrustMasterWarthogCombined' in device['HandledDevices'] and errors.deviceWarnings == '':
                errors.deviceWarnings = '<h2>Mapping Software Detected</h2>You are using the ThrustMaster TARGET software. As a result it is possible that not all of the controls will show up. If you have missing controls then you should remove the mapping from TARGET and map them using Elite\'s own configuration UI.'
        
        if len(createdImages) == 0 and errors.misconfigurationWarnings == '' and errors.unhandledDevicesWarnings == '' and errors.errors == '':
            errors.errors = '<h1>The file supplied does not have any bindings for a supported controller or keyboard.</h1>'
    
    # Save variables for later replays
    if (mode is Mode.generate and public):
        saveReplayInfo(config, description, styling, displayGroups, devices, showKeyboard, errors)
    
    printHTML(mode, config, public, createdImages, deviceForBlockImage, errors)

if __name__ == '__main__':
    main()
