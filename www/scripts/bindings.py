#!/usr/bin/env python3

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
import pickle
import re
from pathlib import Path
from urllib.parse import urljoin


class Config:
  dirRoot = Path('/home/edrefcardinfoi7/www').resolve()
  webRoot = 'https://edrefcard.info/'
  
  def newRandom():
    config = Config(Config.randomName())
    while(config.exists()):
      config = Config(Config.randomName())
    return config
  
  def __init__(self, name):
    self.name = name
  
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
    objs.sort(key=sortKey)
    return objs


cgitb.enable()


unhandledDevicesWarnings = ''
deviceWarnings = ''
misconfigurationWarnings = ''
errors = ''

supportedDevices = OrderedDict([
  ('LogitechExtreme3DPro', {'Template': 'extreme3dpro', 'HandledDevices': ['LogitechExtreme3DPro']}),
  ('Logitech710WirelessGamepad', {'Template': 'f710', 'HandledDevices': ['Logitech710WirelessGamepad']}),
  ('LogitechGTWheel', {'Template': 'gtwheel', 'HandledDevices': ['046DC29A']}),
  ('LogitechG940', {'Template': 'g940', 'HandledDevices': ['LogitechG940Joystick', 'LogitechG940Throttle']}),
  ('T16000M', {'Template': 't16000m', 'HandledDevices': ['T16000M']}),
  ('T16000MFCS', {'Template': 't16000mfcs', 'HandledDevices': ['T16000MFCS', 'T16000MTHROTTLE']}),
  ('TFlightHOTASX', {'Template': 'hotasx', 'HandledDevices': ['ThrustMasterTFlightHOTASX']}),
  ('ThrustMasterHOTAS4', {'Template': 'hotas4', 'HandledDevices': ['ThrustMasterHOTAS4']}),
  ('T-Rudder', {'Template': 'tfrp', 'HandledDevices': ['T-Rudder']}),
  ('TFlightStickX', {'Template': 'stickx', 'HandledDevices': ['044FB106']}),
  ('Warthog', {'Template': 'warthog', 'HandledDevices': ['ThrustMasterWarthogJoystick', 'ThrustMasterWarthogThrottle', 'ThrustMasterWarthogCombined']}),
  ('CobraM5', {'Template': 'cobram5', 'HandledDevices': ['11C05603', '11C05605']}),
  ('Gladiator', {'Template': 'gladiator', 'HandledDevices': ['231D0121']}),
  ('Cougar', {'Template': 'cougar', 'HandledDevices': ['044FB351', '044FB352']}),
  ('SaitekFLY5', {'Template': 'fly5', 'HandledDevices': ['SaitekFLY5', '06A30836']}),
  ('SaitekX52', {'Template': 'x52', 'HandledDevices': ['SaitekX52']}),
  ('SaitekX52Pro', {'Template': 'x52pro', 'HandledDevices': ['SaitekX52Pro']}),
  ('SaitekX55', {'Template': 'x55', 'HandledDevices': ['SaitekX55Joystick', 'SaitekX55Throttle']}),
  ('SaitekX56', {'Template': 'x56', 'HandledDevices': ['SaitekX56Joystick', 'SaitekX56Throttle', '07382221', '0738A221']}),
  ('SaitekProFlightPedals', {'Template': 'proflightpedals', 'HandledDevices': ['SaitekProFlightRudderPedals', '06A30765']}),
  ('SaitekProFlightCombatPedals', {'Template': 'proflightcombatpedals', 'HandledDevices': ['SaitekProFlightCombatRudderPedals']}),
  ('CHFighterStick', {'Template': 'chfighter', 'KeyDevices': ['CHFighterStick', '068EC0F3'], 'HandledDevices': ['CHFighterStick', '068EC0F3', 'CHProThrottle1', 'CHProThrottle2', '068EC010']}),
  ('CHCombatStick', {'Template': 'chcombat', 'KeyDevices': ['CHCombatStick'], 'HandledDevices': ['CHCombatStick', 'CHProThrottle1', 'CHProThrottle2', '068EC010']}),
  ('CHProThrottle', {'Template': 'chfighter', 'HandledDevices': ['CHProThrottle1', 'CHProThrottle2', '068EC010']}),
  ('CHThrottleQuadrant', {'Template': 'chquadrant', 'HandledDevices': ['068E00FA']}),
  ('CHProFlightThrottleQuadrant', {'Template': 'chproflightquadrant', 'HandledDevices': ['06A30C2D']}),
  ('CHProPedals', {'Template': 'chpropedals', 'HandledDevices': ['CHProPedals', '068E00F2']}),
  ('SidePanelControlDeck', {'Template': 'sidepanelcontroldeck', 'HandledDevices': ['07382218']}),
  ('XBox', {'Template': 'xbox', 'HandledDevices': ['XB360 Pad', '045E02FF', '045E02DD']}),
  ('XBoxElite', {'Template': 'xboxelite', 'HandledDevices': ['045E02E3']}),
  ('GamePad', {'Template': 'xbox', 'HandledDevices': ['GamePad']}),
  ('Sabretooth', {'Template': 'sabretooth', 'HandledDevices': ['1689FE00']}),
  ('LogitechG940Pedals', {'Template': 'g940pedals', 'HandledDevices': ['LogitechG940Pedals']}),
  ('SlawBF109Pedals', {'Template': 'slawbf109pedals', 'HandledDevices': ['SlawFlightControlRudder']}),
  ('MFGCrosswind', {'Template': 'crosswind', 'HandledDevices': ['16D00A38', '85640203']}),
  ('DS4', {'Template': 'ds4', 'HandledDevices': ['DS4']}),
  ('Keyboard', {'Template': 'keyboard', 'HandledDevices': ['Keyboard']})
])

controls = {
  #
  # Controls for the galaxy map
  #
  'CamTranslateUp': {'Group': 'Galaxy map', 'Category': 'UI', 'Order': 1, 'Name': 'Camera up', 'Type': 'Digital', 'HasAnalogue': True, 'OverriddenBy': []},
  'CamTranslateDown': {'Group': 'Galaxy map', 'Category': 'UI', 'Order': 2, 'Name': 'Camera down', 'Type': 'Digital', 'HasAnalogue': True, 'OverriddenBy': []},
  'CamTranslateLeft': {'Group': 'Galaxy map', 'Category': 'UI', 'Order': 3, 'Name': 'Camera left', 'Type': 'Digital', 'HasAnalogue': True, 'OverriddenBy': []},
  'CamTranslateRight': {'Group': 'Galaxy map', 'Category': 'UI', 'Order': 4, 'Name': 'Camera right', 'Type': 'Digital', 'HasAnalogue': True, 'OverriddenBy': []},
  'CamTranslateForward': {'Group': 'Galaxy map', 'Category': 'UI', 'Order': 5, 'Name': 'Camera forward', 'Type': 'Digital', 'HasAnalogue': True, 'OverriddenBy': []},
  'CamTranslateBackward': {'Group': 'Galaxy map', 'Category': 'UI', 'Order': 6, 'Name': 'Camera backward', 'Type': 'Digital', 'HasAnalogue': True, 'OverriddenBy': []},
  'CamTranslateXAxis': {'Group': 'Galaxy map', 'Category': 'UI', 'Order': 7, 'Name': 'Camera X', 'Type': 'Analogue', 'OverriddenBy': []},
  'CamTranslateYAxis': {'Group': 'Galaxy map', 'Category': 'UI', 'Order': 8, 'Name': 'Camera Y', 'Type': 'Analogue', 'OverriddenBy': []},
  'CamTranslateZAxis': {'Group': 'Galaxy map', 'Category': 'UI', 'Order': 9, 'Name': 'Camera Z', 'Type': 'Analogue', 'OverriddenBy': []},
  'CamTranslateZHold': {'Group': 'Galaxy map', 'Category': 'UI', 'Order': 10, 'Name': 'Camera Z hold', 'Type': 'Digital', 'HasAnalogue': False, 'OverriddenBy': []},
  'CamPitchAxis': {'Group': 'Galaxy map', 'Category': 'UI', 'Order': 11, 'Name': 'Camera pitch', 'Type': 'Analogue', 'OverriddenBy': []},
  'CamPitchUp': {'Group': 'Galaxy map', 'Category': 'UI', 'Order': 12, 'Name': 'Camera pitch up', 'Type': 'Digital', 'HasAnalogue': True, 'OverriddenBy': []},
  'CamPitchDown': {'Group': 'Galaxy map', 'Category': 'UI', 'Order': 13, 'Name': 'Camera pitch down', 'Type': 'Digital', 'HasAnalogue': True, 'OverriddenBy': []},
  'CamYawAxis': {'Group': 'Galaxy map', 'Category': 'UI', 'Order': 14, 'Name': 'Camera yaw', 'Type': 'Analogue', 'OverriddenBy': []},
  'CamYawLeft': {'Group': 'Galaxy map', 'Category': 'UI', 'Order': 15, 'Name': 'Camera yaw left', 'Type': 'Digital', 'HasAnalogue': True, 'OverriddenBy': []},
  'CamYawRight': {'Group': 'Galaxy map', 'Category': 'UI', 'Order': 16, 'Name': 'Camera yaw right', 'Type': 'Digital', 'HasAnalogue': True, 'OverriddenBy': []},
  'CamZoomAxis': {'Group': 'Galaxy map', 'Category': 'UI', 'Order': 17, 'Name': 'Camera zoom', 'Type': 'Analogue', 'OverriddenBy': []},
  'CamZoomIn': {'Group': 'Galaxy map', 'Category': 'UI', 'Order': 18, 'Name': 'Camera zoom in', 'Type': 'Digital', 'HasAnalogue': True, 'OverriddenBy': []},
  'CamZoomOut': {'Group': 'Galaxy map', 'Category': 'UI', 'Order': 19, 'Name': 'Camera zoom out', 'Type': 'Digital', 'HasAnalogue': True, 'OverriddenBy': []},

  #
  # General items available on both ship and SRV
  #
  'RadarRangeAxis': {'Group': 'Misc', 'Category': 'Navigation', 'Order': 1, 'Name': 'Sensors range', 'Type': 'Analogue', 'OverriddenBy': []},
  'RadarDecreaseRange': {'Group': 'Misc', 'Category': 'Navigation', 'Order': 2, 'Name': 'Decrease sensors range', 'Type': 'Digital', 'HasAnalogue': True, 'OverriddenBy': []},
  'RadarIncreaseRange': {'Group': 'Misc', 'Category': 'Navigation', 'Order': 3, 'Name': 'Increase sensors range', 'Type': 'Digital', 'HasAnalogue': True, 'OverriddenBy': []},
  'MicrophoneMute': {'Group': 'Misc', 'Category': 'General', 'Order': 4, 'Name': 'Microphone', 'Type': 'Digital', 'HasAnalogue': False, 'OverriddenBy': []},
  'HMDReset': {'Group': 'Misc', 'Category': 'General', 'Order': 5, 'Name': 'Reset HMD', 'Type': 'Digital', 'HasAnalogue': False, 'OverriddenBy': []},
  'OculusReset': {'Group': 'Misc', 'Category': 'General', 'Order': 6, 'Name': 'Reset Oculus', 'Type': 'Digital', 'HasAnalogue': False, 'OverriddenBy': []},
  'Pause': {'Group': 'Misc', 'Category': 'General', 'Order': 8, 'Name': 'Main menu', 'Type': 'Digital', 'HasAnalogue': False, 'OverriddenBy': []},
  'FriendsMenu': {'Group': 'Misc', 'Category': 'General', 'Order': 9, 'Name': 'Friends', 'Type': 'Digital', 'HasAnalogue': False, 'OverriddenBy': []},
  'CommanderCreator_Undo': {'Group': 'Misc', 'Category': 'General', 'Order': 10, 'Name': 'Undo', 'Type': 'Digital', 'HasAnalouge': False, 'OverriddenBy': []},
  'CommanderCreator_Redo': {'Group': 'Misc', 'Category': 'General', 'Order': 11, 'Name': 'Redo', 'Type': 'Digital', 'HasAnalouge': False, 'OverriddenBy': []},
  'CommanderCreator_Rotation_MouseToggle': {'Group': 'Misc', 'Category': 'General', 'Order': 12, 'Name': 'Rotation toggle', 'Type': 'Digital', 'HasAnalouge': False, 'OverriddenBy': []},
  'CommanderCreator_Rotation': {'Group': 'Misc', 'Category': 'General', 'Order': 13, 'Name': 'Rotation', 'Type': 'Digital', 'OverriddenBy': []},

  #
  # Head look 
  #
  'HeadLookPitchAxis': {'Group': 'Head look', 'Category': 'Navigation', 'Order': 1, 'Name': 'Look up/down', 'Type': 'Analogue', 'OverriddenBy': []},
  'HeadLookPitchAxisRaw': {'Group': 'Head look', 'Category': 'Navigation', 'Order': 2, 'Name': 'Look up/down', 'Type': 'Analogue', 'OverriddenBy': []},
  'HeadLookPitchUp': {'Group': 'Head look', 'Category': 'Navigation', 'Order': 3, 'Name': 'Look up', 'Type': 'Digital', 'HasAnalogue': True, 'OverriddenBy': []},
  'HeadLookPitchDown': {'Group': 'Head look', 'Category': 'Navigation', 'Order': 4, 'Name': 'Look down', 'Type': 'Digital', 'HasAnalogue': True, 'OverriddenBy': []},
  'HeadLookYawAxis': {'Group': 'Head look', 'Category': 'Navigation', 'Order': 5, 'Name': 'Look left/right', 'Type': 'Analogue', 'OverriddenBy': []},
  'HeadLookYawAxisRaw': {'Group': 'Head look', 'Category': 'Navigation', 'Order': 6, 'Name': 'Look left/right', 'Type': 'Analogue', 'OverriddenBy': []},
  'HeadLookYawLeft': {'Group': 'Head look', 'Category': 'Navigation', 'Order': 7, 'Name': 'Look left', 'Type': 'Digital', 'HasAnalogue': True, 'OverriddenBy': []},
  'HeadLookYawRight': {'Group': 'Head look', 'Category': 'Navigation', 'Order': 8, 'Name': 'Look right', 'Type': 'Digital', 'HasAnalogue': True, 'OverriddenBy': []},
  'HeadLookReset': {'Group': 'Head look', 'Category': 'Navigation', 'Order': 9, 'Name': 'Reset headlook', 'Type': 'Digital', 'HasAnalogue': False, 'OverriddenBy': []},

  #
  # Controls only available in the SRV
  #
  # Driving
  'SteeringAxis': {'Group': 'SRV', 'Category': 'Navigation', 'Order': 1, 'Name': 'Steering', 'Type': 'Analogue', 'OverriddenBy': []},
  'SteerLeftButton': {'Group': 'SRV', 'Category': 'Navigation', 'Order': 2, 'Name': 'Steer left', 'Type': 'Digital', 'HasAnalogue': True, 'OverriddenBy': []},
  'SteerRightButton': {'Group': 'SRV', 'Category': 'Navigation', 'Order': 3, 'Name': 'Steer right', 'Type': 'Digital', 'HasAnalogue': True, 'OverriddenBy': []},
  'DriveSpeedAxis': {'Group': 'SRV', 'Category': 'Navigation', 'Order': 4, 'Name': 'Speed', 'Type': 'Analogue', 'OverriddenBy': []},
  'IncreaseSpeedButtonPartial': {'Group': 'SRV', 'Category': 'Navigation', 'Order': 5, 'Name': 'Increase speed', 'Type': 'Digital', 'HasAnalogue': True, 'OverriddenBy': []},
  'DecreaseSpeedButtonPartial': {'Group': 'SRV', 'Category': 'Navigation', 'Order': 6, 'Name': 'Decrease speed', 'Type': 'Digital', 'HasAnalogue': True, 'OverriddenBy': []},
  'IncreaseSpeedButtonMax': {'Group': 'SRV', 'Category': 'Navigation', 'Order': 7, 'Name': 'Maximum speed', 'Type': 'Digital', 'HasAnalogue': False, 'OverriddenBy': []},
  'DecreaseSpeedButtonMax': {'Group': 'SRV', 'Category': 'Navigation', 'Order': 8, 'Name': 'Zero speed', 'Type': 'Digital', 'HasAnalogue': False, 'OverriddenBy': []},
  'BuggyPitchAxis': {'Group': 'SRV', 'Category': 'Navigation', 'Order': 9, 'Name': 'Pitch', 'Type': 'Analogue', 'OverriddenBy': ['PitchAxis', 'PitchAxisRaw']},
  'BuggyPitchAxisRaw': {'Group': 'SRV', 'Category': 'Navigation', 'Order': 10, 'Name': 'Pitch', 'Type': 'Analogue', 'OverriddenBy': ['PitchAxis', 'PitchAxisRaw', 'BuggyPitchAxis']},
  'BuggyPitchUpButton': {'Group': 'SRV', 'Category': 'Navigation', 'Order': 11, 'Name': 'Pitch up', 'Type': 'Digital', 'HasAnalogue': True, 'OverriddenBy': ['PitchUpButton']},
  'BuggyPitchDownButton': {'Group': 'SRV', 'Category': 'Navigation', 'Order': 12, 'Name': 'Pitch down', 'Type': 'Digital', 'HasAnalogue': True, 'OverriddenBy': ['PitchDownButton']},
  'BuggyRollAxis': {'Group': 'SRV', 'Category': 'Navigation', 'Order': 13, 'Name': 'Roll', 'Type': 'Analogue', 'OverriddenBy': ['RollAxis', 'RollAxisRaw']},
  'BuggyRollAxisRaw': {'Group': 'SRV', 'Category': 'Navigation', 'Order': 14, 'Name': 'Roll', 'Type': 'Analogue', 'OverriddenBy': ['RollAxis', 'RollAxisRaw']},
  'BuggyRollLeft': {'Group': 'SRV', 'Category': 'Navigation', 'Order': 15, 'Name': 'Roll left', 'Type': 'Digital', 'HasAnalogue': True, 'OverriddenBy': ['RollLeftButton']},
  'BuggyRollLeftButton': {'Group': 'SRV', 'Category': 'Navigation', 'Order': 15, 'Name': 'Roll left', 'Type': 'Digital', 'HasAnalogue': True, 'OverriddenBy': ['RollLeftButton']},
  'BuggyRollRight': {'Group': 'SRV', 'Category': 'Navigation', 'Order': 16, 'Name': 'Roll right', 'Type': 'Digital', 'HasAnalogue': True, 'OverriddenBy': ['RollRightButton']},
  'BuggyRollRightButton': {'Group': 'SRV', 'Category': 'Navigation', 'Order': 17, 'Name': 'Roll right', 'Type': 'Digital', 'HasAnalogue': True, 'OverriddenBy': ['RollRightButton']},
  'AutoBreakBuggyButton': {'Group': 'SRV', 'Category': 'Navigation', 'Order': 18, 'Name': 'Hand brake', 'Type': 'Digital', 'HasAnalogue': False, 'OverriddenBy': []},
  'BuggyToggleReverseThrottleInput': {'Group': 'SRV', 'Category': 'Navigation', 'Order': 19, 'Name': 'Reverse', 'Type': 'Digital', 'HasAnalogue': False, 'OverriddenBy': ['ToggleReverseThrottleInput']},
  'VerticalThrustersButton': {'Group': 'SRV', 'Category': 'Navigation', 'Order': 20, 'Name': 'Vertical thrusters', 'Type': 'Digital', 'HasAnalogue': False, 'OverriddenBy': []},
  'ToggleDriveAssist': {'Group': 'SRV', 'Category': 'Navigation', 'Order': 21, 'Name': 'Drive assist', 'Type': 'Digital', 'HasAnalogue': False, 'OverriddenBy': []},
  'HeadlightsBuggyButton': {'Group': 'SRV', 'Category': 'Navigation', 'Order': 22, 'Name': 'Lights', 'Type': 'Digital', 'HasAnalogue': False, 'OverriddenBy': ['ShipSpotLightToggle']},
  'ToggleCargoScoop_Buggy': {'Group': 'SRV', 'Category': 'Navigation', 'Order': 23, 'Name': 'Cargo scoop', 'Type': 'Digital', 'HasAnalogue': False, 'OverriddenBy': ['ToggleCargoScoop']},
  'RecallDismissShip': {'Group': 'SRV', 'Category': 'Navigation', 'Order': 24, 'Name': 'Recall/dismiss ship', 'Type': 'Digital', 'HasAnalogue': False, 'OverriddenBy': []},

   # Targeting and firing
  'SelectTarget_Buggy': {'Group': 'SRV', 'Category': 'Combat', 'Order': 101, 'Name': 'Target ahead', 'Type': 'Digital', 'HasAnalogue': False, 'OverriddenBy': ['SelectTarget']},
  'ToggleBuggyTurretButton': {'Group': 'SRV', 'Category': 'Combat', 'Order': 102, 'Name': 'Turret mode', 'Type': 'Digital', 'HasAnalogue': False, 'OverriddenBy': []},
  'BuggyPrimaryFireButton': {'Group': 'SRV', 'Category': 'Combat', 'Order': 103, 'Name': 'Primary weapons', 'Type': 'Digital', 'HasAnalogue': False, 'OverriddenBy': ['PrimaryFire']},
  'BuggySecondaryFireButton': {'Group': 'SRV', 'Category': 'Combat', 'Order': 104, 'Name': 'Secondary weapons', 'Type': 'Digital', 'HasAnalogue': False, 'OverriddenBy': ['SecondaryFire']},
  'BuggyTurretPitchAxis': {'Group': 'SRV', 'Category': 'Combat', 'Order': 105, 'Name': 'Turret up/down', 'Type': 'Analogue', 'OverriddenBy': []},
  'BuggyTurretPitchAxisRaw': {'Group': 'SRV', 'Category': 'Combat', 'Order': 106, 'Name': 'Turret up/down', 'Type': 'Analogue', 'OverriddenBy': []},
  'BuggyTurretPitchDownButton': {'Group': 'SRV', 'Category': 'Combat', 'Order': 107, 'Name': 'Turret down', 'Type': 'Digital', 'HasAnalogue': True, 'OverriddenBy': []},
  'BuggyTurretPitchUpButton': {'Group': 'SRV', 'Category': 'Combat', 'Order': 108, 'Name': 'Turret up', 'Type': 'Digital', 'HasAnalogue': True, 'OverriddenBy': []},
  'BuggyTurretYawAxis': {'Group': 'SRV', 'Category': 'Combat', 'Order': 109, 'Name': 'Turret left/right', 'Type': 'Analogue', 'OverriddenBy': []},
  'BuggyTurretYawAxisRaw': {'Group': 'SRV', 'Category': 'Combat', 'Order': 110, 'Name': 'Turret left/right', 'Type': 'Analogue', 'OverriddenBy': []},
  'BuggyTurretYawLeftButton': {'Group': 'SRV', 'Category': 'Combat', 'Order': 111, 'Name': 'Turret left', 'Type': 'Digital', 'HasAnalogue': True, 'OverriddenBy': []},
  'BuggyTurretYawRightButton': {'Group': 'SRV', 'Category': 'Combat', 'Order': 112, 'Name': 'Turret right', 'Type': 'Digital', 'HasAnalogue': True, 'OverriddenBy': []},

   # Managing power
  'ResetPowerDistribution_Buggy': {'Group': 'SRV', 'Category': 'Combat', 'Order': 201, 'Name': 'Equalise power', 'Type': 'Digital', 'HasAnalogue': False, 'OverriddenBy': ['ResetPowerDistribution']},
  'IncreaseEnginesPower_Buggy': {'Group': 'SRV', 'Category': 'Combat', 'Order': 202, 'Name': 'Increase engine power', 'Type': 'Digital', 'HasAnalogue': False, 'OverriddenBy': ['IncreaseEnginesPower']},
  'IncreaseSystemsPower_Buggy': {'Group': 'SRV', 'Category': 'Combat', 'Order': 203, 'Name': 'Increase system power', 'Type': 'Digital', 'HasAnalogue': False, 'OverriddenBy': ['IncreaseSystemsPower']},
  'IncreaseWeaponsPower_Buggy': {'Group': 'SRV', 'Category': 'Combat', 'Order': 204, 'Name': 'Increase weapon power', 'Type': 'Digital', 'HasAnalogue': False, 'OverriddenBy': ['IncreaseWeaponsPower']},

   # Navigation
  'GalaxyMapOpen_Buggy': {'Group': 'SRV', 'Category': 'Navigation', 'Order': 301, 'Name': 'Galaxy map', 'Type': 'Digital', 'HasAnalogue': False, 'OverriddenBy': ['GalaxyMapOpen']},
  'SystemMapOpen_Buggy': {'Group': 'SRV', 'Category': 'Navigation', 'Order': 302, 'Name': 'System map', 'Type': 'Digital', 'HasAnalogue': False, 'OverriddenBy': ['SystemMapOpen']},

   # UI
  'FocusCommsPanel_Buggy': {'Group': 'SRV', 'Order': 401, 'Name': 'Comms panel', 'Type': 'Digital', 'HasAnalogue': False, 'OverriddenBy': ['FocusCommsPanel']},
  'FocusLeftPanel_Buggy': {'Group': 'SRV', 'Order': 402, 'Name': 'Navigation panel', 'Type': 'Digital', 'HasAnalogue': False, 'OverriddenBy': ['FocusLeftPanel']},
  'FocusRadarPanel_Buggy': {'Group': 'SRV', 'Order': 403, 'Name': 'Role panel', 'Type': 'Digital', 'HasAnalogue': False, 'OverriddenBy': ['FocusRadarPanel']},
  'FocusRightPanel_Buggy': {'Group': 'SRV', 'Order': 404, 'Name': 'Systems panel', 'Type': 'Digital', 'HasAnalogue': False, 'OverriddenBy': ['FocusRightPanel']},
  'QuickCommsPanel_Buggy': {'Group': 'SRV', 'Order': 405, 'Name': 'Quick comms', 'Type': 'Digital', 'HasAnalogue': False, 'OverriddenBy': ['QuickCommsPanel']},
  'UIFocus_Buggy': {'Group': 'SRV', 'Order': 406, 'Name': 'User interface', 'Type': 'Digital', 'HasAnalogue': False, 'OverriddenBy': ['UIFocus']},

   # Misc
  'EjectAllCargo_Buggy': {'Group': 'SRV', 'Order': 501, 'Name': 'Eject cargo', 'Type': 'Digital', 'HasAnalogue': False, 'OverriddenBy': ['EjectAllCargo']},
  'HeadLookToggle_Buggy': {'Group': 'SRV', 'Order': 502, 'Name': 'Toggle headlook', 'Type': 'Digital', 'HasAnalogue': False, 'OverriddenBy': ['HeadLookToggle']},

  #
  # Controls only available in the ship
  #
  # Flying
  'PitchAxis': {'Group': 'Ship', 'Category': 'Navigation', 'Order': 1, 'Name': 'Pitch', 'Type': 'Analogue', 'OverriddenBy': []},
  'PitchAxisRaw': {'Group': 'Ship', 'Category': 'Navigation', 'Order': 2, 'Name': 'Pitch', 'Type': 'Analogue', 'OverriddenBy': []},
  'PitchUpButton': {'Group': 'Ship', 'Category': 'Navigation', 'Order': 3, 'Name': 'Pitch up', 'Type': 'Digital', 'HasAnalogue': True, 'OverriddenBy': []},
  'PitchDownButton': {'Group': 'Ship', 'Category': 'Navigation', 'Order': 4, 'Name': 'Pitch down', 'Type': 'Digital', 'HasAnalogue': True, 'OverriddenBy': []},
  'RollAxis': {'Group': 'Ship', 'Category': 'Navigation', 'Order': 5, 'Name': 'Roll', 'Type': 'Analogue', 'OverriddenBy': []},
  'RollAxisRaw': {'Group': 'Ship', 'Category': 'Navigation', 'Order': 6, 'Name': 'Roll', 'Type': 'Analogue', 'OverriddenBy': []},
  'RollLeftButton': {'Group': 'Ship', 'Category': 'Navigation', 'Order': 7, 'Name': 'Roll left', 'Type': 'Digital', 'HasAnalogue': True, 'OverriddenBy': []},
  'RollRightButton': {'Group': 'Ship', 'Category': 'Navigation', 'Order': 8, 'Name': 'Roll right', 'Type': 'Digital', 'HasAnalogue': True, 'OverriddenBy': []},
  'YawAxis': {'Group': 'Ship', 'Category': 'Navigation', 'Order': 9, 'Name': 'Yaw', 'Type': 'Analogue', 'OverriddenBy': []},
  'YawAxisRaw': {'Group': 'Ship', 'Category': 'Navigation', 'Order': 10, 'Name': 'Yaw', 'Type': 'Analogue', 'OverriddenBy': []},
  'YawLeftButton': {'Group': 'Ship', 'Category': 'Navigation', 'Order': 11, 'Name': 'Yaw left', 'Type': 'Digital', 'HasAnalogue': True, 'OverriddenBy': []},
  'YawRightButton': {'Group': 'Ship', 'Category': 'Navigation', 'Order': 12, 'Name': 'Yaw right', 'Type': 'Digital', 'HasAnalogue': True, 'OverriddenBy': []},
  'YawToRollButton': {'Group': 'Ship', 'Category': 'Navigation', 'Order': 13, 'Name': 'Yaw to roll', 'Type': 'Digital', 'HasAnalogue': False, 'OverriddenBy': []},
  'ThrottleAxis': {'Group': 'Ship', 'Category': 'Navigation', 'Order': 14, 'Name': 'Throttle', 'Type': 'Analogue', 'OverriddenBy': []},
  'ThrottleAxisRaw': {'Group': 'Ship', 'Category': 'Navigation', 'Order': 15, 'Name': 'Throttle', 'Type': 'Analogue', 'OverriddenBy': []},
  'SetSpeed100': {'Group': 'Ship', 'Category': 'Navigation', 'Order': 16, 'Name': 'Full throttle', 'Type': 'Digital', 'HasAnalogue': False, 'OverriddenBy': []},
  'SetSpeed75': {'Group': 'Ship', 'Category': 'Navigation', 'Order': 17, 'Name': 'Three quarter throttle', 'Type': 'Digital', 'HasAnalogue': False, 'OverriddenBy': []},
  'SetSpeed50': {'Group': 'Ship', 'Category': 'Navigation', 'Order': 18, 'Name': 'Half throttle', 'Type': 'Digital', 'HasAnalogue': False, 'OverriddenBy': []},
  'SetSpeed25': {'Group': 'Ship', 'Category': 'Navigation', 'Order': 19, 'Name': 'Quarter throttle', 'Type': 'Digital', 'HasAnalogue': False, 'OverriddenBy': []},
  'SetSpeedZero': {'Group': 'Ship', 'Category': 'Navigation', 'Order': 20, 'Name': 'All stop', 'Type': 'Digital', 'HasAnalogue': False, 'OverriddenBy': []},
  'SetSpeedMinus25': {'Group': 'Ship', 'Category': 'Navigation', 'Order': 21, 'Name': 'Quarter reverse throttle', 'Type': 'Digital', 'HasAnalogue': False, 'OverriddenBy': []},
  'SetSpeedMinus50': {'Group': 'Ship', 'Category': 'Navigation', 'Order': 22, 'Name': 'Half reverse throttle', 'Type': 'Digital', 'HasAnalogue': False, 'OverriddenBy': []},
  'SetSpeedMinus75': {'Group': 'Ship', 'Category': 'Navigation', 'Order': 23, 'Name': 'Three quarter reverse throttle', 'Type': 'Digital', 'HasAnalogue': False, 'OverriddenBy': []},
  'SetSpeedMinus100': {'Group': 'Ship', 'Category': 'Navigation', 'Order': 24, 'Name': 'Full reverse throttle', 'Type': 'Digital', 'HasAnalogue': False, 'OverriddenBy': []},
  'AheadThrust': {'Group': 'Ship', 'Category': 'Navigation', 'Order': 25, 'Name': 'Ahead thrust', 'Type': 'Analogue', 'OverriddenBy': []},
  'ForwardKey': {'Group': 'Ship', 'Category': 'Navigation', 'Order': 26, 'Name': 'Forward thrust', 'Type': 'Digital', 'HasAnalogue': True, 'OverriddenBy': []},
  'ForwardThrustButton': {'Group': 'Ship', 'Category': 'Navigation', 'Order': 27, 'Name': 'Forward thrust', 'Type': 'Digital', 'HasAnalogue': True, 'OverriddenBy': []},
  'BackwardKey': {'Group': 'Ship', 'Category': 'Navigation', 'Order': 28, 'Name': 'Backward thrust', 'Type': 'Digital', 'HasAnalogue': True, 'OverriddenBy': []},
  'BackwardThrustButton': {'Group': 'Ship', 'Category': 'Navigation', 'Order': 29, 'Name': 'Backward thrust', 'Type': 'Digital', 'HasAnalogue': True, 'OverriddenBy': []},
  'VerticalThrust': {'Group': 'Ship', 'Category': 'Navigation', 'Order': 30, 'Name': 'Vertical thrust', 'Type': 'Analogue', 'OverriddenBy': []},
  'VerticalThrustRaw': {'Group': 'Ship', 'Category': 'Navigation', 'Order': 31, 'Name': 'Vertical thrust', 'Type': 'Analogue', 'OverriddenBy': []},
  'UpThrustButton': {'Group': 'Ship', 'Category': 'Navigation', 'Order': 32, 'Name': 'Thrust up', 'Type': 'Digital', 'HasAnalogue': True, 'OverriddenBy': []},
  'DownThrustButton': {'Group': 'Ship', 'Category': 'Navigation', 'Order': 33, 'Name': 'Thrust down', 'Type': 'Digital', 'HasAnalogue': True, 'OverriddenBy': []},
  'LateralThrust': {'Group': 'Ship', 'Category': 'Navigation', 'Order': 34, 'Name': 'Lateral thrust', 'Type': 'Analogue', 'OverriddenBy': []},
  'LateralThrustRaw': {'Group': 'Ship', 'Category': 'Navigation', 'Order': 35, 'Name': 'Lateral thrust', 'Type': 'Analogue', 'OverriddenBy': []},
  'LeftThrustButton': {'Group': 'Ship', 'Category': 'Navigation', 'Order': 36, 'Name': 'Thrust left', 'Type': 'Digital', 'HasAnalogue': True, 'OverriddenBy': []},
  'RightThrustButton': {'Group': 'Ship', 'Category': 'Navigation', 'Order': 37, 'Name': 'Thrust right', 'Type': 'Digital', 'HasAnalogue': True, 'OverriddenBy': []},
  'ToggleReverseThrottleInput': {'Group': 'Ship', 'Category': 'Navigation', 'Order': 38, 'Name': 'Reverse throttle', 'Type': 'Digital', 'HasAnalogue': False, 'OverriddenBy': []},
  'ToggleFlightAssist': {'Group': 'Ship', 'Category': 'Navigation', 'Order': 39, 'Name': 'Flight assist', 'Type': 'Digital', 'HasAnalogue': False, 'OverriddenBy': []},
  'UseBoostJuice': {'Group': 'Ship', 'Category': 'Navigation', 'Order': 40, 'Name': 'Boost', 'Type': 'Digital', 'HasAnalogue': False, 'OverriddenBy': []},
  'ToggleButtonUpInput': {'Group': 'Ship', 'Category': 'Navigation', 'Order': 41, 'Name': 'Silent running', 'Type': 'Digital', 'HasAnalogue': False, 'OverriddenBy': []},
  'ToggleCargoScoop': {'Group': 'Ship', 'Category': 'Navigation', 'Order': 42, 'Name': 'Cargo scoop', 'Type': 'Digital', 'HasAnalogue': False, 'OverriddenBy': []},
  'ShipSpotLightToggle': {'Group': 'Ship', 'Category': 'Navigation', 'Order': 43, 'Name': 'Lights', 'Type': 'Digital', 'HasAnalogue': False, 'OverriddenBy': []},
  'UseAlternateFlightValuesToggle': {'Group': 'Ship', 'Category': 'Navigation', 'Order': 44, 'Name': 'Alternate controls', 'Type': 'Digital', 'HasAnalogue': False, 'OverriddenBy': []},
  'PitchAxisAlternate': {'Group': 'Ship', 'Category': 'Navigation', 'Order': 45, 'Name': 'Pitch (alternate)', 'Type': 'Analogue', 'OverriddenBy': ['PitchAxisRaw']},
  'RollAxisAlternate': {'Group': 'Ship', 'Category': 'Navigation', 'Order': 46, 'Name': 'Roll (alternate)', 'Type': 'Analogue', 'OverriddenBy': ['RollAxisRaw']},
  'YawAxisAlternate': {'Group': 'Ship', 'Category': 'Navigation', 'Order': 47, 'Name': 'Yaw (alternate)', 'Type': 'Analogue', 'OverriddenBy': ['YawAxisRaw']},
  'VerticalThrustAlternate': {'Group': 'Ship', 'Category': 'Navigation', 'Order': 48, 'Name': 'Vertical thrust (alternate)', 'Type': 'Analogue', 'OverriddenBy': ['VerticalThrustRaw']},
  'LateralThrustAlternate': {'Group': 'Ship', 'Category': 'Navigation', 'Order': 49, 'Name': 'Lateral thrust (alternate)', 'Type': 'Analogue', 'OverriddenBy': ['LateralThrustRaw']},

  # Selecting a target and firing
  'SelectTarget': {'Group': 'Ship', 'Category': 'Combat', 'Order': 101, 'Name': 'Target ahead', 'Type': 'Digital', 'HasAnalogue': False, 'OverriddenBy': []},
  'SelectHighestThreat': {'Group': 'Ship', 'Category': 'Combat', 'Order': 102, 'Name': 'Target highest threat', 'Type': 'Digital', 'HasAnalogue': False, 'OverriddenBy': []},
  'CycleNextTarget': {'Group': 'Ship', 'Category': 'Combat', 'Order': 103, 'Name': 'Target next', 'Type': 'Digital', 'HasAnalogue': False, 'OverriddenBy': []},
  'CyclePreviousTarget': {'Group': 'Ship', 'Category': 'Combat', 'Order': 104, 'Name': 'Target previous', 'Type': 'Digital', 'HasAnalogue': False, 'OverriddenBy': []},
  'CycleNextHostileTarget': {'Group': 'Ship', 'Category': 'Combat', 'Order': 105, 'Name': 'Target next hostile', 'Type': 'Digital', 'HasAnalogue': False, 'OverriddenBy': []},
  'CyclePreviousHostileTarget': {'Group': 'Ship', 'Category': 'Combat', 'Order': 106, 'Name': 'Target previous hostile', 'Type': 'Digital', 'HasAnalogue': False, 'OverriddenBy': []},
  'DeployHardpointToggle': {'Group': 'Ship', 'Category': 'Combat', 'Order': 107, 'Name': 'Hardpoints', 'Type': 'Digital', 'HasAnalogue': False, 'OverriddenBy': []},
  'PrimaryFire': {'Group': 'Ship', 'Category': 'Combat', 'Order': 108, 'Name': 'Primary weapons', 'Type': 'Digital', 'HasAnalogue': False, 'OverriddenBy': []},
  'SecondaryFire': {'Group': 'Ship', 'Category': 'Combat', 'Order': 109, 'Name': 'Secondary weapons', 'Type': 'Digital', 'HasAnalogue': False, 'OverriddenBy': []},
  'CycleFireGroupNext': {'Group': 'Ship', 'Category': 'Combat', 'Order': 110, 'Name': 'Next fire group', 'Type': 'Digital', 'HasAnalogue': False, 'OverriddenBy': []},
  'CycleFireGroupPrevious': {'Group': 'Ship', 'Category': 'Combat', 'Order': 111, 'Name': 'Previous fire group', 'Type': 'Digital', 'HasAnalogue': False, 'OverriddenBy': []},
  'CycleNextSubsystem': {'Group': 'Ship', 'Category': 'Combat', 'Order': 112, 'Name': 'Target next subsystem', 'Type': 'Digital', 'HasAnalogue': False, 'OverriddenBy': []},
  'CyclePreviousSubsystem': {'Group': 'Ship', 'Category': 'Combat', 'Order': 113, 'Name': 'Target previous subsystem', 'Type': 'Digital', 'HasAnalogue': False, 'OverriddenBy': []},
  'FireChaffLauncher': {'Group': 'Ship', 'Category': 'Combat', 'Order': 114, 'Name': 'Launch chaff', 'Type': 'Digital', 'HasAnalogue': False, 'OverriddenBy': []},
  'DeployHeatSink': {'Group': 'Ship', 'Category': 'Combat', 'Order': 116, 'Name': 'Heatsink', 'Type': 'Digital', 'HasAnalogue': False, 'OverriddenBy': []},
  'UseShieldCell': {'Group': 'Ship', 'Category': 'Combat', 'Order': 117, 'Name': 'Shield cell', 'Type': 'Digital', 'HasAnalogue': False, 'OverriddenBy': []},
  'ChargeECM': {'Group': 'Ship', 'Category': 'Combat', 'Order': 118, 'Name': 'Charge ECM', 'Type': 'Digital', 'HasAnalogue': False, 'OverriddenBy': []},

  # Managing power
  'ResetPowerDistribution': {'Group': 'Ship', 'Category': 'Combat', 'Order': 201, 'Name': 'Equalise power', 'Type': 'Digital', 'HasAnalogue': False, 'OverriddenBy': []},
  'IncreaseEnginesPower': {'Group': 'Ship', 'Category': 'Combat', 'Order': 202, 'Name': 'Increase engine power', 'Type': 'Digital', 'HasAnalogue': False, 'OverriddenBy': []},
  'IncreaseSystemsPower': {'Group': 'Ship', 'Category': 'Combat', 'Order': 203, 'Name': 'Increase system power', 'Type': 'Digital', 'HasAnalogue': False, 'OverriddenBy': []},
  'IncreaseWeaponsPower': {'Group': 'Ship', 'Category': 'Combat', 'Order': 204, 'Name': 'Increase weapon power', 'Type': 'Digital', 'HasAnalogue': False, 'OverriddenBy': []},

  # Fighter
  'OrderRequestDock': {'Group': 'Fighter', 'Category': 'Combat', 'Order': 251, 'Name': 'Dock fighter', 'Type': 'Digital', 'HasAnalogue': False, 'OverriddenBy': []},
  'OrderDefensiveBehaviour': {'Group': 'Fighter', 'Category': 'Combat', 'Order': 252, 'Name': 'Defensive stance', 'Type': 'Digital', 'HasAnalogue': False, 'OverriddenBy': []},
  'OrderAggressiveBehaviour': {'Group': 'Fighter', 'Category': 'Combat', 'Order': 253, 'Name': 'Aggressive stance', 'Type': 'Digital', 'HasAnalogue': False, 'OverriddenBy': []},
  'OrderFocusTarget': {'Group': 'Fighter', 'Category': 'Combat', 'Order': 253, 'Name': 'Focus target', 'Type': 'Digital', 'HasAnalogue': False, 'OverriddenBy': []},
  'OrderHoldFire': {'Group': 'Fighter', 'Category': 'Combat', 'Order': 254, 'Name': 'Hold fire', 'Type': 'Digital', 'HasAnalogue': False, 'OverriddenBy': []},
  'OrderHoldPosition': {'Group': 'Fighter', 'Category': 'Combat', 'Order': 256, 'Name': 'Hold position', 'Type': 'Digital', 'HasAnalogue': False, 'OverriddenBy': []},
  'OrderFollow': {'Group': 'Fighter', 'Category': 'Combat', 'Order': 257, 'Name': 'Follow', 'Type': 'Digital', 'HasAnalogue': False, 'OverriddenBy': []},
  'OpenOrders': {'Group': 'Fighter', 'Category': 'Combat', 'Order': 258, 'Name': 'Crew orders', 'Type': 'Digital', 'HasAnalogue': False, 'OverriddenBy': []},

  # Multicrew
  'MultiCrewToggleMode': {'Group': 'Multicrew', 'Category': 'General', 'Order': 280, 'Name': 'Multicrew mode', 'Type': 'Digital', 'HasAnalogue': False, 'OverriddenBy': []},
  'MultiCrewThirdPersonPitchAxisRaw': {'Group': 'Multicrew', 'Category': 'General', 'Order': 281, 'Name': 'Pitch', 'Type': 'Analogue', 'OverriddenBy': ['PitchAxis', 'PitchAxisRaw']},
  'MultiCrewThirdPersonPitchUpButton': {'Group': 'Multicrew', 'Category': 'General', 'Order': 282, 'Name': 'Pitch up', 'Type': 'Digital', 'HasAnalogue': True, 'OverriddenBy': []},
  'MultiCrewThirdPersonPitchDownButton': {'Group': 'Multicrew', 'Category': 'General', 'Order': 283, 'Name': 'Pitch down', 'Type': 'Digital', 'HasAnalogue': True, 'OverriddenBy': []},
  'MultiCrewThirdPersonYawAxisRaw': {'Group': 'Multicrew', 'Category': 'General', 'Order': 284, 'Name': 'Yaw', 'Type': 'Analogue', 'OverriddenBy': ['YawAxis', 'YawAxisRaw']},
  'MultiCrewThirdPersonYawLeftButton': {'Group': 'Multicrew', 'Category': 'General', 'Order': 285, 'Name': 'Yaw left', 'Type': 'Digital', 'HasAnalogue': True, 'OverriddenBy': []},
  'MultiCrewThirdPersonYawRightButton': {'Group': 'Multicrew', 'Category': 'General', 'Order': 286, 'Name': 'Yaw right', 'Type': 'Digital', 'HasAnalogue': True, 'OverriddenBy': []},
  'MultiCrewThirdPersonFovAxisRaw': {'Group': 'Multicrew', 'Category': 'General', 'Order': 287, 'Name': 'Field of view', 'Type': 'Analogue', 'OverriddenBy': []},
  'MultiCrewThirdPersonFovOutButton': {'Group': 'Multicrew', 'Category': 'General', 'Order': 288, 'Name': 'Field of view out', 'Type': 'Digital', 'HasAnalogue': True, 'OverriddenBy': []},
  'MultiCrewThirdPersonFovInButton': {'Group': 'Multicrew', 'Category': 'General', 'Order': 289, 'Name': 'Field of view in', 'Type': 'Digital', 'HasAnalogue': True, 'OverriddenBy': []},
  'MultiCrewPrimaryFire': {'Group': 'Multicrew', 'Category': 'General', 'Order': 290, 'Name': 'Primary weapons', 'Type': 'Digital', 'HasAnalogue': False, 'OverriddenBy': ['PrimaryFire']},
  'MultiCrewSecondaryFire': {'Group': 'Multicrew', 'Category': 'General', 'Order': 292, 'Name': 'Secondary weapons', 'Type': 'Digital', 'HasAnalogue': False, 'OverriddenBy': ['SecondaryFire']},
  'MultiCrewPrimaryUtilityFire': {'Group': 'Multicrew', 'Category': 'General', 'Order': 292, 'Name': 'Primary utility', 'Type': 'Digital', 'HasAnalogue': False, 'OverriddenBy': []},
  'MultiCrewSecondaryUtilityFire': {'Group': 'Multicrew', 'Category': 'General', 'Order': 293, 'Name': 'Secondary utility', 'Type': 'Digital', 'HasAnalogue': False, 'OverriddenBy': []},
  'MultiCrewCockpitUICycleForward': {'Group': 'Multicrew', 'Category': 'General', 'Order': 294, 'Name': 'UI forward', 'Type': 'Digital', 'HasAnalogue': False, 'OverriddenBy': ['UI_Up', 'UI_Down']},
  'MultiCrewCockpitUICycleBackward': {'Group': 'Multicrew', 'Category': 'General', 'Order': 295, 'Name': 'UI backward', 'Type': 'Digital', 'HasAnalogue': False, 'OverriddenBy': ['UI_Up', 'UI_Down']},

  # Navigation
  'GalaxyMapOpen': {'Group': 'Ship', 'Category': 'Navigation', 'Order': 301, 'Name': 'Galaxy map', 'Type': 'Digital', 'HasAnalogue': False, 'OverriddenBy': []},
  'SystemMapOpen': {'Group': 'Ship', 'Category': 'Navigation', 'Order': 302, 'Name': 'System map', 'Type': 'Digital', 'HasAnalogue': False, 'OverriddenBy': []},
  'HyperSuperCombination': {'Group': 'Ship', 'Category': 'Navigation', 'Order': 303, 'Name': 'Hyperspace/Supercruise', 'Type': 'Digital', 'HasAnalogue': False, 'OverriddenBy': []},
  'Hyperspace': {'Group': 'Ship', 'Category': 'Navigation', 'Order': 304, 'Name': 'Hyperspace', 'Type': 'Digital', 'HasAnalogue': False, 'OverriddenBy': []},
  'EngageSupercruise': {'Group': 'Ship', 'Category': 'Navigation', 'Order': 305, 'Name': 'Supercruise', 'Type': 'Digital', 'HasAnalogue': False, 'OverriddenBy': []},
  'Supercruise': {'Group': 'Ship', 'Category': 'Navigation', 'Order': 306, 'Name': 'Supercruise', 'Type': 'Digital', 'HasAnalogue': False, 'OverriddenBy': []},
  'TargetNextRouteSystem': {'Group': 'Ship', 'Category': 'Navigation', 'Order': 307, 'Name': 'Next jump destination', 'Type': 'Digital', 'HasAnalogue': False, 'OverriddenBy': []},

  # Wings
  'TargetWingman0': {'Group': 'Ship', 'Order': 401, 'Name': 'Target first wingman', 'Type': 'Digital', 'HasAnalogue': False, 'OverriddenBy': []},
  'TargetWingman1': {'Group': 'Ship', 'Order': 402, 'Name': 'Target second wingman', 'Type': 'Digital', 'HasAnalogue': False, 'OverriddenBy': []},
  'TargetWingman2': {'Group': 'Ship', 'Order': 403, 'Name': 'Target third wingman', 'Type': 'Digital', 'HasAnalogue': False, 'OverriddenBy': []},
  'SelectTargetsTarget': {'Group': 'Ship', 'Order': 404, 'Name': 'Target wingman\'s target', 'Type': 'Digital', 'HasAnalogue': False, 'OverriddenBy': []},
  'WingNavLock': {'Group': 'Ship', 'Order': 405, 'Name': 'Wingman navlock', 'Type': 'Digital', 'HasAnalogue': False, 'OverriddenBy': []},

  # UI
  'UIFocus': {'Group': 'Ship', 'Order': 501, 'Name': 'User interface', 'Type': 'Digital', 'HasAnalogue': False, 'OverriddenBy': []},
  'FocusCommsPanel': {'Group': 'Ship', 'Order': 502, 'Name': 'Comms panel', 'Type': 'Digital', 'HasAnalogue': False, 'OverriddenBy': []},
  'QuickCommsPanel': {'Group': 'Ship', 'Order': 503, 'Name': 'Quick comms', 'Type': 'Digital', 'HasAnalogue': False, 'OverriddenBy': []},
  'FocusLeftPanel': {'Group': 'Ship', 'Order': 504, 'Name': 'Navigation panel', 'Type': 'Digital', 'HasAnalogue': False, 'OverriddenBy': []},
  'FocusRightPanel': {'Group': 'Ship', 'Order': 505, 'Name': 'Systems panel', 'Type': 'Digital', 'HasAnalogue': False, 'OverriddenBy': []},
  'FocusRadarPanel': {'Group': 'Ship', 'Order': 506, 'Name': 'Role panel', 'Type': 'Digital', 'HasAnalogue': False, 'OverriddenBy': []},

  # Landing
  'LandingGearToggle': {'Group': 'Ship', 'Category': 'Navigation', 'Order': 601, 'Name': 'Landing gear', 'Type': 'Digital', 'HasAnalogue': False, 'OverriddenBy': []},
  'PitchAxis_Landing': {'Group': 'Ship', 'Category': 'Navigation', 'Order': 602, 'Name': 'Pitch (landing)', 'Type': 'Analogue', 'OverriddenBy': ['PitchAxis', 'PitchAxisRaw']},
  'PitchUpButton_Landing': {'Group': 'Ship', 'Category': 'Navigation', 'Order': 603, 'Name': 'Pitch up (landing)', 'Type': 'Digital', 'HasAnalogue': True, 'OverriddenBy': ['PitchUpButton']},
  'PitchDownButton_Landing': {'Group': 'Ship', 'Category': 'Navigation', 'Order': 604, 'Name': 'Pitch down (landing)', 'Type': 'Digital', 'HasAnalogue': True, 'OverriddenBy': ['PitchDownButton']},
  'RollAxis_Landing': {'Group': 'Ship', 'Category': 'Navigation', 'Order': 605, 'Name': 'Roll (landing)', 'Type': 'Analogue', 'OverriddenBy': ['RollAxis', 'RollAxisRaw']},
  'RollLeftButton_Landing': {'Group': 'Ship', 'Category': 'Navigation', 'Order': 606, 'Name': 'Roll left (landing)', 'Type': 'Digital', 'HasAnalogue': True, 'OverriddenBy': ['RollLeftButton']},
  'RollRightButton_Landing': {'Group': 'Ship', 'Category': 'Navigation', 'Order': 607, 'Name': 'Roll right (landing)', 'Type': 'Digital', 'HasAnalogue': True, 'OverriddenBy': ['RollRightButton']},
  'YawAxis_Landing': {'Group': 'Ship', 'Category': 'Navigation', 'Order': 608, 'Name': 'Yaw', 'Type': 'Analogue', 'OverriddenBy': ['YawAxis', 'YawAxisRaw']},
  'YawLeftButton_Landing': {'Group': 'Ship', 'Category': 'Navigation', 'Order': 609, 'Name': 'Yaw left (landing)', 'Type': 'Digital', 'HasAnalogue': True, 'OverriddenBy': ['YawLeftButton']},
  'YawRightButton_Landing': {'Group': 'Ship', 'Category': 'Navigation', 'Order': 610, 'Name': 'Yaw right (landing)', 'Type': 'Digital', 'HasAnalogue': True, 'OverriddenBy': ['YawRightButton']},
  'AheadThrust_Landing': {'Group': 'Ship', 'Category': 'Navigation', 'Order': 611, 'Name': 'Ahead thrust (landing)', 'Type': 'Analogue', 'OverriddenBy': ['AheadThrust']},
  'ForwardThrustButton_Landing': {'Group': 'Ship', 'Category': 'Navigation', 'Order': 612, 'Name': 'Forward thrust (landing)', 'Type': 'Digital', 'HasAnalogue': True, 'OverriddenBy': ['ForwardThrustButton']},
  'BackwardThrustButton_Landing': {'Group': 'Ship', 'Category': 'Navigation', 'Order': 613, 'Name': 'Backward thrust (landing)', 'Type': 'Digital', 'HasAnalogue': True, 'OverriddenBy': ['BackwardThrustButton']},
  'VerticalThrust_Landing': {'Group': 'Ship', 'Category': 'Navigation', 'Order': 614, 'Name': 'Vertical thrust (landing)', 'Type': 'Analogue', 'OverriddenBy': ['VerticalThrust', 'VerticalThrustRaw']},
  'UpThrustButton_Landing': {'Group': 'Ship', 'Category': 'Navigation', 'Order': 615, 'Name': 'Thrust up (landing)', 'Type': 'Digital', 'HasAnalogue': True, 'OverriddenBy': ['UpThrustButton']},
  'DownThrustButton_Landing': {'Group': 'Ship', 'Category': 'Navigation', 'Order': 616, 'Name': 'Thrust down (landing)', 'Type': 'Digital', 'HasAnalogue': True, 'OverriddenBy': ['DownThrustButton']},
  'LateralThrust_Landing': {'Group': 'Ship', 'Category': 'Navigation', 'Order': 617, 'Name': 'Lateral thrust (landing)', 'Type': 'Analogue', 'OverriddenBy': ['LateralThrust']},
  'LeftThrustButton_Landing': {'Group': 'Ship', 'Category': 'Navigation', 'Order': 618, 'Name': 'Thrust left (landing)', 'Type': 'Digital', 'HasAnalogue': True, 'OverriddenBy': ['LeftThrustButton']},
  'RightThrustButton_Landing': {'Group': 'Ship', 'Category': 'Navigation', 'Order': 619, 'Name': 'Thrust right (landing)', 'Type': 'Digital', 'HasAnalogue': True, 'OverriddenBy': ['RightThrustButton']},
  'DisableRotationCorrectToggle': {'Group': 'Ship', 'Category': 'Navigation', 'Order': 620, 'Name': 'Rotational correction', 'Type': 'Digital', 'HasAnalogue': False, 'OverriddenBy': []},

  # Misc
  'EjectAllCargo': {'Group': 'Ship', 'Category': 'General', 'Order': 701, 'Name': 'Eject cargo', 'Type': 'Digital', 'HasAnalogue': False, 'OverriddenBy': []},
  'HeadLookToggle': {'Group': 'Ship', 'Category': 'General', 'Order': 702, 'Name': 'Toggle headlook', 'Type': 'Digital', 'HasAnalogue': False, 'OverriddenBy': []},
  'OrbitLinesToggle': {'Group': 'Ship', 'Category': 'General', 'Order': 703, 'Name': 'Orbit lines', 'Type': 'Digital', 'HasAnalogue': False, 'OverriddenBy': []},
  'ShowPGScoreSummaryInput': {'Group': 'Ship', 'Category': 'General', 'Order': 704, 'Name': 'Show CQC score', 'Type': 'Digital', 'HasAnalogue': False, 'OverriddenBy': []},
  'MouseReset': {'Group': 'Ship', 'Category': 'General', 'Order': 705, 'Name': 'Reset mouse', 'Type': 'Digital', 'HasAnalogue': False, 'OverriddenBy': []},
  'WeaponColourToggle': {'Group': 'Ship', 'Category': 'General', 'Order': 706, 'Name': 'Weapon colour', 'Type': 'Digital', 'HasAnalogue': False, 'OverriddenBy': []},
  'EngineColourToggle': {'Group': 'Ship', 'Category': 'General', 'Order': 707, 'Name': 'Engine colour', 'Type': 'Digital', 'HasAnalogue': False, 'OverriddenBy': []},

  # Camera
  'PhotoCameraToggle': {'Group': 'Camera', 'Category': 'Camera', 'Order': 801, 'Name': 'External camera', 'Type': 'Digital', 'HasAnalogue': False, 'OverriddenBy': []},
  'PhotoCameraToggle_Buggy': {'Group': 'Camera', 'Category': 'Camera', 'Order': 802, 'Name': 'External camera', 'Type': 'Digital', 'HasAnalogue': False, 'OverriddenBy': ['PhotoCameraToggle']},
  'ToggleFreeCam': {'Group': 'Camera', 'Category': 'General', 'Order': 803, 'Name': 'Free camera', 'Type': 'Digital', 'HasAnalogue': False, 'OverriddenBy': []},
  'QuitCamera': {'Group': 'Camera', 'Category': 'General', 'Order': 804, 'Name': 'Exit free camera', 'Type': 'Digital', 'HasAnalogue': False, 'OverriddenBy': ['ToggleFreeCam']},
  'VanityCameraOne': {'Group': 'Camera', 'Category': 'General', 'Order': 805, 'Name': 'Camera - Cockpit Front', 'Type': 'Digital', 'HasAnalogue': False, 'OverriddenBy': []},
  'VanityCameraTwo': {'Group': 'Camera', 'Category': 'General', 'Order': 806, 'Name': 'Camera - Cockpit Back', 'Type': 'Digital', 'HasAnalogue': False, 'OverriddenBy': []},
  'VanityCameraThree': {'Group': 'Camera', 'Category': 'General', 'Order': 808, 'Name': 'Camera - Commander 1', 'Type': 'Digital', 'HasAnalogue': False, 'OverriddenBy': []},
  'VanityCameraFour': {'Group': 'Camera', 'Category': 'General', 'Order': 808, 'Name': 'Camera - Commander 2', 'Type': 'Digital', 'HasAnalogue': False, 'OverriddenBy': []},
  'VanityCameraFive': {'Group': 'Camera', 'Category': 'General', 'Order': 809, 'Name': 'Camera - Co-pilot 1', 'Type': 'Digital', 'HasAnalogue': False, 'OverriddenBy': []},
  'VanityCameraSix': {'Group': 'Camera', 'Category': 'General', 'Order': 810, 'Name': 'Camera - Co-pilot 2', 'Type': 'Digital', 'HasAnalogue': False, 'OverriddenBy': []},
  'VanityCameraSeven': {'Group': 'Camera', 'Category': 'General', 'Order': 811, 'Name': 'Camera - Front', 'Type': 'Digital', 'HasAnalogue': False, 'OverriddenBy': []},
  'VanityCameraEight': {'Group': 'Camera', 'Category': 'General', 'Order': 812, 'Name': 'Camera - Back', 'Type': 'Digital', 'HasAnalogue': False, 'OverriddenBy': []},
  'VanityCameraNine': {'Group': 'Camera', 'Category': 'General', 'Order': 813, 'Name': 'Camera - Low', 'Type': 'Digital', 'HasAnalogue': False, 'OverriddenBy': []},
  'VanityCameraScrollRight': {'Group': 'Camera', 'Category': 'General', 'Order': 814, 'Name': 'Next camera', 'Type': 'Digital', 'HasAnalogue': False, 'OverriddenBy': []},
  'VanityCameraScrollLeft': {'Group': 'Camera', 'Category': 'General', 'Order': 815, 'Name': 'Previous camera', 'Type': 'Digital', 'HasAnalogue': False, 'OverriddenBy': []},
  'FreeCamToggleHUD': {'Group': 'Camera', 'Category': 'General', 'Order': 816, 'Name': 'Toggle HUD', 'Type': 'Digital', 'HasAnalogue': False, 'OverriddenBy': []},
  'FreeCamSpeedInc': {'Group': 'Camera', 'Category': 'General', 'Order': 817, 'Name': 'Increase speed', 'Type': 'Digital', 'HasAnalogue': False, 'OverriddenBy': []},
  'FreeCamSpeedDec': {'Group': 'Camera', 'Category': 'General', 'Order': 818, 'Name': 'Decrease speed', 'Type': 'Digital', 'HasAnalogue': False, 'OverriddenBy': []},
  'FreeCamZoomIn': {'Group': 'Camera', 'Category': 'General', 'Order': 819, 'Name': 'Zoom in', 'Type': 'Digital', 'HasAnalogue': False, 'OverriddenBy': []},
  'FreeCamZoomOut': {'Group': 'Camera', 'Category': 'General', 'Order': 820, 'Name': 'Zoom out', 'Type': 'Digital', 'HasAnalogue': False, 'OverriddenBy': []},
  'MoveFreeCamX': {'Group': 'Camera', 'Category': 'General', 'Order': 821, 'Name': 'Camera left/right', 'Type': 'Analogue', 'OverriddenBy': []},
  'MoveFreeCamLeft': {'Group': 'Camera', 'Category': 'General', 'Order': 822, 'Name': 'Camera left', 'Type': 'Digital', 'HasAnalouge': True, 'OverriddenBy': []},
  'MoveFreeCamRight': {'Group': 'Camera', 'Category': 'General', 'Order': 823, 'Name': 'Camera right', 'Type': 'Digital', 'HasAnalouge': True, 'OverriddenBy': []},
  'MoveFreeCamY': {'Group': 'Camera', 'Category': 'General', 'Order': 824, 'Name': 'Camera forwards/backwards', 'Type': 'Analogue', 'OverriddenBy': []},
  'MoveFreeCamUp': {'Group': 'Camera', 'Category': 'General', 'Order': 825, 'Name': 'Camera up', 'Type': 'Digital', 'HasAnalouge': True, 'OverriddenBy': []},
  'MoveFreeCamDown': {'Group': 'Camera', 'Category': 'General', 'Order': 826, 'Name': 'Camera down', 'Type': 'Digital', 'HasAnalouge': True, 'OverriddenBy': []},
  'MoveFreeCamZ': {'Group': 'Camera', 'Category': 'General', 'Order': 827, 'Name': 'Camera up/down', 'Type': 'Analogue', 'OverriddenBy': []},
  'MoveFreeCamForward': {'Group': 'Camera', 'Category': 'General', 'Order': 828, 'Name': 'Camera forwards', 'Type': 'Digital', 'HasAnalouge': True, 'OverriddenBy': []},
  'MoveFreeCamBackwards': {'Group': 'Camera', 'Category': 'General', 'Order': 829, 'Name': 'Camera backwards', 'Type': 'Digital', 'HasAnalouge': True, 'OverriddenBy': []},
  'PitchCamera': {'Group': 'Camera', 'Category': 'General', 'Order': 830, 'Name': 'Camera pitch', 'Type': 'Analogue', 'OverriddenBy': []},
  'PitchCameraUp': {'Group': 'Camera', 'Category': 'General', 'Order': 831, 'Name': 'Camera pitch up', 'Type': 'Digital', 'HasAnalouge': True, 'OverriddenBy': []},
  'PitchCameraDown': {'Group': 'Camera', 'Category': 'General', 'Order': 832, 'Name': 'Camera pitch down', 'Type': 'Digital', 'HasAnalouge': True, 'OverriddenBy': []},
  'RollCamera': {'Group': 'Camera', 'Category': 'General', 'Order': 833, 'Name': 'Camera roll', 'Type': 'Analogue', 'OverriddenBy': []},
  'RollCameraLeft': {'Group': 'Camera', 'Category': 'General', 'Order': 834, 'Name': 'Camera roll up', 'Type': 'Digital', 'HasAnalouge': True, 'OverriddenBy': []},
  'RollCameraRight': {'Group': 'Camera', 'Category': 'General', 'Order': 835, 'Name': 'Camera roll down', 'Type': 'Digital', 'HasAnalouge': True, 'OverriddenBy': []},
  'YawCamera': {'Group': 'Camera', 'Category': 'General', 'Order': 836, 'Name': 'Camera yaw', 'Type': 'Analogue', 'OverriddenBy': []},
  'YawCameraLeft': {'Group': 'Camera', 'Category': 'General', 'Order': 837, 'Name': 'Camera yaw left', 'Type': 'Digital', 'HasAnalouge': True, 'OverriddenBy': []},
  'YawCameraRight': {'Group': 'Camera', 'Category': 'General', 'Order': 838, 'Name': 'Camera yaw right', 'Type': 'Digital', 'HasAnalouge': True, 'OverriddenBy': []},
  'ToggleRotationLock': {'Group': 'Camera', 'Category': 'General', 'Order': 839, 'Name': 'Rotation lock', 'Type': 'Digital', 'HasAnalogue': False, 'OverriddenBy': []},
  'ToggleReverseThrottleInputFreeCam': {'Group': 'Camera', 'Category': 'General', 'Order': 840, 'Name': 'Reverse', 'Type': 'Digital', 'HasAnalogue': False, 'OverriddenBy': ['ToggleReverseThrottleInput', 'BuggyToggleReverseThrottleInput']},
  'FixCameraRelativeToggle': {'Group': 'Camera', 'Category': 'General', 'Order': 841, 'Name': 'Lock to vehicle', 'Type': 'Digital', 'HasAnalogue': False, 'OverriddenBy': []},
  'FixCameraWorldToggle': {'Group': 'Camera', 'Category': 'General', 'Order': 842, 'Name': 'Lock to world', 'Type': 'Digital', 'HasAnalogue': False, 'OverriddenBy': []},
  'ToggleAdvanceMode': {'Group': 'Camera', 'Category': 'General', 'Order': 843, 'Name': 'Advance mode', 'Type': 'Digital', 'HasAnalogue': False, 'OverriddenBy': []},
  'FStopInc': {'Group': 'Camera', 'Category': 'General', 'Order': 844, 'Name': 'Increase blur', 'Type': 'Digital', 'HasAnalouge': True, 'OverriddenBy': []},
  'FStopDec': {'Group': 'Camera', 'Category': 'General', 'Order': 845, 'Name': 'Decrease blur', 'Type': 'Digital', 'HasAnalouge': True, 'OverriddenBy': []},
  'FocusDistanceInc': {'Group': 'Camera', 'Category': 'General', 'Order': 846, 'Name': 'Increase focus distance', 'Type': 'Digital', 'HasAnalouge': True, 'OverriddenBy': []},
  'FocusDistanceDec': {'Group': 'Camera', 'Category': 'General', 'Order': 847, 'Name': 'Decrease focus distance', 'Type': 'Digital', 'HasAnalouge': True, 'OverriddenBy': []},

  #
  # Controls for the UI panels
  #
  'UI_Up': {'Group': 'UI', 'Category': 'UI', 'Order': 1, 'Name': 'UI up', 'Type': 'Digital', 'HasAnalogue': False, 'OverriddenBy': []},
  'UI_Down': {'Group': 'UI', 'Category': 'UI', 'Order': 2, 'Name': 'UI down', 'Type': 'Digital', 'HasAnalogue': False, 'OverriddenBy': []},
  'UI_Left': {'Group': 'UI', 'Category': 'UI', 'Order': 3, 'Name': 'UI left', 'Type': 'Digital', 'HasAnalogue': False, 'OverriddenBy': []},
  'UI_Right': {'Group': 'UI', 'Category': 'UI', 'Order': 4, 'Name': 'UI right', 'Type': 'Digital', 'HasAnalogue': False, 'OverriddenBy': []},
  'CycleNextPanel': {'Group': 'UI', 'Category': 'UI', 'Order': 5, 'Name': 'Next UI panel', 'Type': 'Digital', 'HasAnalogue': False, 'OverriddenBy': []},
  'CyclePreviousPanel': {'Group': 'UI', 'Category': 'UI', 'Order': 6, 'Name': 'Previous UI panel', 'Type': 'Digital', 'HasAnalogue': False, 'OverriddenBy': []},
  'UI_Select': {'Group': 'UI', 'Category': 'UI', 'Order': 7, 'Name': 'UI select', 'Type': 'Digital', 'HasAnalogue': False, 'OverriddenBy': []},
  'UI_Back': {'Group': 'UI', 'Category': 'UI', 'Order': 8, 'Name': 'UI back', 'Type': 'Digital', 'HasAnalogue': False, 'OverriddenBy': []},
  'UI_Toggle': {'Group': 'UI', 'Category': 'UI', 'Order': 9, 'Name': 'UI toggle', 'Type': 'Digital', 'HasAnalogue': False, 'OverriddenBy': []},
}

hotasDetails = {
  'LogitechExtreme3DPro': {
    'Joy_1': {'Type': 'Digital', 'x': 474, 'y': 904, 'width': 1092}, # Primary trigger
    'Joy_2': {'Type': 'Digital', 'x': 474, 'y': 1004, 'width': 1092}, # Side trigger
    'Joy_3': {'Type': 'Digital', 'x': 424, 'y': 784, 'width': 1092}, # Bottom-left button
    'Joy_4': {'Type': 'Digital', 'x': 2124, 'y': 784, 'width': 1092}, # Bottom-right button
    'Joy_5': {'Type': 'Digital', 'x': 424, 'y': 654, 'width': 1092}, # Top-left button
    'Joy_6': {'Type': 'Digital', 'x': 2124, 'y': 654, 'width': 1092}, # Top-right button
    'Joy_7': {'Type': 'Digital', 'x': 244, 'y': 1434, 'width': 542, 'height': 108}, # Left bank top-left button
    'Joy_8': {'Type': 'Digital', 'x': 794, 'y': 1434, 'width': 542, 'height': 108}, # Left bank top-right button
    'Joy_9': {'Type': 'Digital', 'x': 244, 'y': 1550, 'width': 542, 'height': 108}, # Left bank middle-left button
    'Joy_10': {'Type': 'Digital', 'x': 794, 'y': 1550, 'width': 542, 'height': 108}, # Left bank middle-right button
    'Joy_11': {'Type': 'Digital', 'x': 244, 'y': 1666, 'width': 542, 'height': 108}, # Left bank bottom-left button
    'Joy_12': {'Type': 'Digital', 'x': 794, 'y': 1666, 'width': 542, 'height': 108}, # Left bank bottom-right button
    'Joy_POV1Up': {'Type': 'Digital', 'x': 864, 'y': 374, 'width': 1932}, # PoV hat up
    'Joy_POV1Right': {'Type': 'Digital', 'x': 864, 'y': 430, 'width': 1932}, # PoV hat right
    'Joy_POV1Down': {'Type': 'Digital', 'x': 864, 'y': 486, 'width': 1932}, # PoV hat down
    'Joy_POV1Left': {'Type': 'Digital', 'x': 864, 'y': 542, 'width': 1932}, # PoV hat left
    'Joy_RZAxis': {'Type': 'Analogue', 'x': 2357, 'y': 980, 'width': 1132}, # Stick twist
    'Joy_UAxis': {'Type': 'Analogue', 'x': 2864, 'y': 1574, 'width': 832}, # Stick throttle slider
    'Joy_XAxis': {'Type': 'Analogue', 'x': 2357, 'y': 924, 'width': 1132}, # Stick pitch
    'Joy_YAxis': {'Type': 'Analogue', 'x': 2357, 'y': 868, 'width': 1132}, # Stick roll
  },
  'T16000M': {
    'Joy_1': {'Type': 'Digital', 'x': 2124, 'y': 624, 'width': 1092}, # Primary trigger
    'Joy_2': {'Type': 'Digital', 'x': 474, 'y': 624, 'width': 1092}, # Bottom button
    'Joy_3': {'Type': 'Digital', 'x': 474, 'y': 494, 'width': 1092}, # Left-hand button
    'Joy_4': {'Type': 'Digital', 'x': 2124, 'y': 494, 'width': 1092}, # Right-hand button
    'Joy_5': {'Type': 'Digital', 'x': 24, 'y': 1104, 'width': 542, 'height': 108}, # Left bank top-left button
    'Joy_6': {'Type': 'Digital', 'x': 574, 'y': 1104, 'width': 542, 'height': 108}, # Left bank top-middle button
    'Joy_7': {'Type': 'Digital', 'x': 1124, 'y': 1104, 'width': 542, 'height': 108}, # Left bank top-right button
    'Joy_8': {'Type': 'Digital', 'x': 1124, 'y': 1220, 'width': 542, 'height': 108}, # Left bank bottom-right button
    'Joy_9': {'Type': 'Digital', 'x': 574, 'y': 1220, 'width': 542, 'height': 108}, # Left bank bottom-middle button
    'Joy_10': {'Type': 'Digital', 'x': 24, 'y': 1220, 'width': 542, 'height': 108}, # Left bank bottom-left button
    'Joy_11': {'Type': 'Digital', 'x': 3264, 'y': 1104, 'width': 542, 'height': 108}, # Right bank top-right button
    'Joy_12': {'Type': 'Digital', 'x': 2714, 'y': 1104, 'width': 542, 'height': 108}, # Right bank top-middle button
    'Joy_13': {'Type': 'Digital', 'x': 2164, 'y': 1104, 'width': 542, 'height': 108}, # Right bank top-left button
    'Joy_14': {'Type': 'Digital', 'x': 2164, 'y': 1220, 'width': 542, 'height': 108}, # Right bank bottom-left button
    'Joy_15': {'Type': 'Digital', 'x': 2714, 'y': 1220, 'width': 542, 'height': 108}, # Right bank bottom-middle button
    'Joy_16': {'Type': 'Digital', 'x': 3264, 'y': 1220, 'width': 542, 'height': 108}, # Right bank bottom-right button
    'Joy_POV1Up': {'Type': 'Digital', 'x': 1542, 'y': 214, 'width': 1532}, # PoV hat up
    'Joy_POV1Right': {'Type': 'Digital', 'x': 1542, 'y': 270, 'width': 1532}, # PoV hat right
    'Joy_POV1Down': {'Type': 'Digital', 'x': 1542, 'y': 326, 'width': 1532}, # PoV hat down
    'Joy_POV1Left': {'Type': 'Digital', 'x': 1542, 'y': 382, 'width': 1532}, # PoV hat left
    'Joy_RZAxis': {'Type': 'Analogue', 'x': 2357, 'y': 980, 'width': 1132}, # Stick twist
    'Joy_UAxis': {'Type': 'Analogue', 'x': 2584, 'y': 1750, 'width': 832}, # Stick throttle slider
    'Joy_XAxis': {'Type': 'Analogue', 'x': 2357, 'y': 924, 'width': 1132}, # Stick pitch
    'Joy_YAxis': {'Type': 'Analogue', 'x': 2357, 'y': 868, 'width': 1132}, # Stick roll
  },
  'T16000MFCS': {
    'Joy_1': {'Type': 'Digital', 'x': 1804, 'y': 844, 'width': 642, 'height': 108}, # Primary trigger
    'Joy_2': {'Type': 'Digital', 'x': 2764, 'y': 604, 'width': 992}, # Bottom button
    'Joy_3': {'Type': 'Digital', 'x': 1754, 'y': 484, 'width': 692}, # Left-hand button
    'Joy_4': {'Type': 'Digital', 'x': 2764, 'y': 504, 'width': 992}, # Right-hand button
    'Joy_5': {'Type': 'Digital', 'x': 1254, 'y': 1244, 'width': 292, 'height': 108}, # Left bank top-left button
    'Joy_6': {'Type': 'Digital', 'x': 1554, 'y': 1244, 'width': 292, 'height': 108}, # Left bank top-middle button
    'Joy_7': {'Type': 'Digital', 'x': 1854, 'y': 1244, 'width': 292, 'height': 108}, # Left bank top-right button
    'Joy_8': {'Type': 'Digital', 'x': 1854, 'y': 1360, 'width': 292, 'height': 108}, # Left bank bottom-right button
    'Joy_9': {'Type': 'Digital', 'x': 1554, 'y': 1360, 'width': 292, 'height': 108}, # Left bank bottom-middle button
    'Joy_10': {'Type': 'Digital', 'x': 1254, 'y': 1360, 'width': 292, 'height': 108}, # Left bank bottom-left button
    'Joy_11': {'Type': 'Digital', 'x': 3484, 'y': 992, 'width': 292, 'height': 108}, # Right bank top-right button
    'Joy_12': {'Type': 'Digital', 'x': 3184, 'y': 992, 'width': 292, 'height': 108}, # Right bank top-middle button
    'Joy_13': {'Type': 'Digital', 'x': 2884, 'y': 992, 'width': 292, 'height': 108}, # Right bank top-left button
    'Joy_14': {'Type': 'Digital', 'x': 2884, 'y': 1108, 'width': 292, 'height': 108}, # Right bank bottom-left button
    'Joy_15': {'Type': 'Digital', 'x': 3184, 'y': 1108, 'width': 292, 'height': 108}, # Right bank bottom-middle button
    'Joy_16': {'Type': 'Digital', 'x': 3484, 'y': 1108, 'width': 292, 'height': 108}, # Right bank bottom-right button
    'Joy_POV1Up': {'Type': 'Digital', 'x': 2524, 'y': 214, 'width': 1192}, # PoV hat up
    'Joy_POV1Right': {'Type': 'Digital', 'x': 2524, 'y': 270, 'width': 1192}, # PoV hat right
    'Joy_POV1Down': {'Type': 'Digital', 'x': 2524, 'y': 326, 'width': 1192}, # PoV hat down
    'Joy_POV1Left': {'Type': 'Digital', 'x': 2524, 'y': 382, 'width': 1192}, # PoV hat left
    'Joy_RZAxis': {'Type': 'Analogue', 'x': 2824, 'y': 856, 'width': 932}, # Stick twist
    'Joy_UAxis': {'Type': 'Analogue', 'x': 2944, 'y': 1593, 'width': 832}, # Stick throttle slider
    'Joy_XAxis': {'Type': 'Analogue', 'x': 2824, 'y': 800, 'width': 932}, # Stick pitch
    'Joy_YAxis': {'Type': 'Analogue', 'x': 2824, 'y': 744, 'width': 932}, # Stick roll
  },
  'T16000MTHROTTLE': {
    'Joy_1': {'Type': 'Digital', 'x': 294, 'y': 1244, 'width': 792}, # Thumb button
    'Joy_2': {'Type': 'Digital', 'x': 1774, 'y': 1774, 'width': 892}, # Pinky button
    'Joy_3': {'Type': 'Digital', 'x': 1714, 'y': 1664, 'width': 892}, # Ring finger button
    'Joy_4': {'Type': 'Digital', 'x': 1484, 'y': 1514, 'width': 692}, # Middle finger rocker up
    'Joy_5': {'Type': 'Digital', 'x': 1484, 'y': 1570, 'width': 692}, # Middle finger rocker down
    'Joy_6': {'Type': 'Digital', 'x': 244, 'y': 1866, 'width': 732}, # Index finger mouse push
    'Joy_7': {'Type': 'Digital', 'x': 1024, 'y': 654, 'width': 692}, # Middle hat up
    'Joy_8': {'Type': 'Digital', 'x': 1024, 'y': 710, 'width': 692}, # Middle hat right
    'Joy_9': {'Type': 'Digital', 'x': 1024, 'y': 766, 'width': 692}, # Middle hat down
    'Joy_10': {'Type': 'Digital', 'x': 1024, 'y': 820, 'width': 692}, # Middle hat left
    'Joy_11': {'Type': 'Digital', 'x': 1034, 'y': 929, 'width': 692}, # Middle hat up
    'Joy_12': {'Type': 'Digital', 'x': 1034, 'y': 985, 'width': 692}, # Castle hat right
    'Joy_13': {'Type': 'Digital', 'x': 1034, 'y': 1041, 'width': 692}, # Castle hat down
    'Joy_14': {'Type': 'Digital', 'x': 1034, 'y': 1097, 'width': 692}, # Castle hat left
    'Joy_POV1Up': {'Type': 'Digital', 'x': 1014, 'y': 364, 'width': 692}, # PoV hat up
    'Joy_POV1Right': {'Type': 'Digital', 'x': 1014, 'y': 420, 'width': 692}, # PoV hat right
    'Joy_POV1Down': {'Type': 'Digital', 'x': 1014, 'y': 476, 'width': 692}, # PoV hat down
    'Joy_POV1Left': {'Type': 'Digital', 'x': 1014, 'y': 532, 'width': 692}, # PoV hat left
    'Joy_XAxis': {'Type': 'Analogue', 'x': 244, 'y': 1810, 'width': 732}, # Index finger mouse X
    'Joy_YAxis': {'Type': 'Analogue', 'x': 244, 'y': 1754, 'width': 732}, # Index finger mouse Y
    'Joy_ZAxis': {'Type': 'Analogue', 'x': 84, 'y': 555, 'width': 572}, # Throttle
    'Joy_UAxis': {'Type': 'Analogue', 'x': 1874, 'y': 1914, 'width': 832}, # Pinky dial
    'Joy_RZAxis': {'Type': 'Analogue', 'x': 1954, 'y': 2054, 'width': 832}, # Paddle
  },
  'SaitekFLY5': {
    'Joy_1': {'Type': 'Digital', 'x': 684, 'y': 794, 'width': 1092}, # Primary trigger
    'Joy_2': {'Type': 'Digital', 'x': 734, 'y': 874, 'width': 1092}, # Bottom-left button
    'Joy_3': {'Type': 'Digital', 'x': 2414, 'y': 744, 'width': 1092}, # Bottom-right button
    'Joy_4': {'Type': 'Digital', 'x': 624, 'y': 704, 'width': 1092}, # Top-left button
    'Joy_5': {'Type': 'Digital', 'x': 2414, 'y': 594, 'width': 1092}, # Top-right button
    'Joy_6': {'Type': 'Digital', 'x': 584, 'y': 1847, 'width': 1092}, # Bottom bank first button
    'Joy_7': {'Type': 'Digital', 'x': 734, 'y': 1927, 'width': 1092}, # Bottom bank second button
    'Joy_8': {'Type': 'Digital', 'x': 884, 'y': 2007, 'width': 1092}, # Bottom bank third button
    'Joy_9': {'Type': 'Digital', 'x': 1034, 'y': 2090, 'width': 1092}, # Bottom bank fourth button
    'Joy_10': {'Type': 'Digital', 'x': 304, 'y': 1604, 'width': 1092}, # Rear left button
    'Joy_11': {'Type': 'Digital', 'x': 664, 'y': 1204, 'width': 1092}, # Rear right button
    'Joy_12': {'Type': 'Digital', 'x': 2474, 'y': 864, 'width': 1132}, # Scroll wheel up
    'Joy_13': {'Type': 'Digital', 'x': 2474, 'y': 920, 'width': 1132}, # Scroll wheel down
    'Joy_14': {'Type': 'Digital', 'x': 2594, 'y': 1504, 'width': 1092}, # Base button
    'Joy_POV1Up': {'Type': 'Digital', 'x': 990, 'y': 304, 'width': 1932}, # PoV hat up
    'Joy_POV1Right': {'Type': 'Digital', 'x': 990, 'y': 360, 'width': 1932}, # PoV hat right
    'Joy_POV1Down': {'Type': 'Digital', 'x': 990, 'y': 416, 'width': 1932}, # PoV hat down
    'Joy_POV1Left': {'Type': 'Digital', 'x': 990, 'y': 472, 'width': 1932}, # PoV hat left
    'Joy_RZAxis': {'Type': 'Analogue', 'x': 2484, 'y': 1136, 'width': 1132}, # Stick twist
    'Joy_XAxis': {'Type': 'Analogue', 'x': 2484, 'y': 1080, 'width': 1132}, # Stick roll
    'Joy_YAxis': {'Type': 'Analogue', 'x': 2484, 'y': 1024, 'width': 1132}, # Stick pitch
    'Joy_ZAxis': {'Type': 'Analogue', 'x': 264, 'y': 1404, 'width': 1032}, # Throttle
  },
  '06A30836': {
    'Joy_1': {'Type': 'Digital', 'x': 684, 'y': 794, 'width': 1092}, # Primary trigger
    'Joy_2': {'Type': 'Digital', 'x': 734, 'y': 874, 'width': 1092}, # Bottom-left button
    'Joy_3': {'Type': 'Digital', 'x': 2414, 'y': 744, 'width': 1092}, # Bottom-right button
    'Joy_4': {'Type': 'Digital', 'x': 624, 'y': 704, 'width': 1092}, # Top-left button
    'Joy_5': {'Type': 'Digital', 'x': 2414, 'y': 594, 'width': 1092}, # Top-right button
    'Joy_6': {'Type': 'Digital', 'x': 584, 'y': 1847, 'width': 1092}, # Bottom bank first button
    'Joy_7': {'Type': 'Digital', 'x': 734, 'y': 1927, 'width': 1092}, # Bottom bank second button
    'Joy_8': {'Type': 'Digital', 'x': 884, 'y': 2007, 'width': 1092}, # Bottom bank third button
    'Joy_9': {'Type': 'Digital', 'x': 1034, 'y': 2090, 'width': 1092}, # Bottom bank fourth button
    'Joy_10': {'Type': 'Digital', 'x': 304, 'y': 1604, 'width': 1092}, # Rear left button
    'Joy_11': {'Type': 'Digital', 'x': 664, 'y': 1204, 'width': 1092}, # Rear right button
    'Joy_12': {'Type': 'Digital', 'x': 2474, 'y': 864, 'width': 1132}, # Scroll wheel up
    'Joy_13': {'Type': 'Digital', 'x': 2474, 'y': 920, 'width': 1132}, # Scroll wheel down
    'Joy_14': {'Type': 'Digital', 'x': 2594, 'y': 1504, 'width': 1092}, # Base button
    'Joy_POV1Up': {'Type': 'Digital', 'x': 990, 'y': 304, 'width': 1932}, # PoV hat up
    'Joy_POV1Right': {'Type': 'Digital', 'x': 990, 'y': 360, 'width': 1932}, # PoV hat right
    'Joy_POV1Down': {'Type': 'Digital', 'x': 990, 'y': 416, 'width': 1932}, # PoV hat down
    'Joy_POV1Left': {'Type': 'Digital', 'x': 990, 'y': 472, 'width': 1932}, # PoV hat left
    'Joy_RZAxis': {'Type': 'Analogue', 'x': 2484, 'y': 1136, 'width': 1132}, # Stick twist
    'Joy_XAxis': {'Type': 'Analogue', 'x': 2484, 'y': 1080, 'width': 1132}, # Stick roll
    'Joy_YAxis': {'Type': 'Analogue', 'x': 2484, 'y': 1024, 'width': 1132}, # Stick pitch
    'Joy_ZAxis': {'Type': 'Analogue', 'x': 264, 'y': 1404, 'width': 1032}, # Throttle
  },
  'SaitekX52': {
    'Joy_1': {'Type': 'Digital', 'x': 3164, 'y': 858, 'width': 600}, # Stick primary trigger half press
    'Joy_2': {'Type': 'Digital', 'x': 2524, 'y': 210, 'width': 560}, # Stick 'Safe'
    'Joy_3': {'Type': 'Digital', 'x': 3108, 'y': 478, 'width': 560}, # Stick blue button right of Safe
    'Joy_4': {'Type': 'Digital', 'x': 3118, 'y': 662, 'width': 560}, # Stick blue button right of hat
    'Joy_5': {'Type': 'Digital', 'x': 2071, 'y': 674, 'width': 570}, # Stick black button left of hat
    'Joy_6': {'Type': 'Digital', 'x': 3102, 'y': 1148, 'width': 570}, # Stick pinky trigger
    'Joy_7': {'Type': 'Digital', 'x': 1334, 'y': 1038, 'width': 740}, # Throttle blue button
    'Joy_8': {'Type': 'Digital', 'x': 1142, 'y': 656, 'width': 760}, # Throttle top rotary button
    'Joy_9': {'Type': 'Digital', 'x': 1630, 'y': 1556, 'width': 560}, # Stick first switch up
    'Joy_10': {'Type': 'Digital', 'x': 1630, 'y': 1608, 'width': 560}, # Stick first switch down
    'Joy_11': {'Type': 'Digital', 'x': 1785, 'y': 1716, 'width': 560}, # Stick second switch up
    'Joy_12': {'Type': 'Digital', 'x': 1785, 'y': 1768, 'width': 560}, # Stick second switch down
    'Joy_13': {'Type': 'Digital', 'x': 2110, 'y': 1872, 'width': 560}, # Stick third switch up
    'Joy_14': {'Type': 'Digital', 'x': 2110, 'y': 1924, 'width': 560}, # Stick third switch down
    'Joy_15': {'Type': 'Digital', 'x': 3164, 'y': 910, 'width': 600}, # Stick primary trigger full press
    'Joy_16': {'Type': 'Digital', 'x': 2044, 'y': 422, 'width': 740}, # Stick top hat down
    'Joy_17': {'Type': 'Digital', 'x': 2044, 'y': 370, 'width': 740}, # Stick top hat right
    'Joy_18': {'Type': 'Digital', 'x': 2044, 'y': 318, 'width': 740}, # Stick top hat up
    'Joy_19': {'Type': 'Digital', 'x': 2044, 'y': 476, 'width': 740}, # Stick top hat left
    'Joy_20': {'Type': 'Digital', 'x': 254, 'y': 330, 'width': 750}, # Throttle rear hat up
    'Joy_21': {'Type': 'Digital', 'x': 254, 'y': 382, 'width': 750}, # Throttle rear hat right
    'Joy_22': {'Type': 'Digital', 'x': 254, 'y': 434, 'width': 750}, # Throttle rear hat down
    'Joy_23': {'Type': 'Digital', 'x': 254, 'y': 486, 'width': 750}, # Throttle rear hat left
    'Joy_27': {'Type': 'Digital', 'x': 26, 'y': 1748, 'width': 570}, # Throttle bottom left button (RST)
    'Joy_28': {'Type': 'Digital', 'x': 198, 'y': 1850, 'width': 570}, # Throttle bottom middle button
    'Joy_29': {'Type': 'Digital', 'x': 355, 'y': 1954, 'width': 570}, # Throttle bottom right button (FUN)
    'Joy_30': {'Type': 'Digital', 'x': 1498, 'y': 1316, 'width': 750}, # Throttle bottom rotary button
    'Joy_31': {'Type': 'Digital', 'x': 1114, 'y': 2014, 'width': 620}, # Throttle mouse click
    'Joy_32': {'Type': 'Digital', 'x': 124, 'y': 752, 'width': 650}, # Throttle rear wheel click
    'Joy_POV1Up': {'Type': 'Digital', 'x': 1878, 'y': 786, 'width': 740}, # PoV hat up
    'Joy_POV1Right': {'Type': 'Digital', 'x': 1878, 'y': 838, 'width': 740}, # PoV hat right
    'Joy_POV1Down': {'Type': 'Digital', 'x': 1878, 'y': 890, 'width': 740}, # PoV hat down
    'Joy_POV1Left': {'Type': 'Digital', 'x': 1878, 'y': 942, 'width': 740}, # PoV hat left
    'Joy_RXAxis': {'Type': 'Analogue', 'x': 1498, 'y': 1264, 'width': 750}, # Throttle bottom rotary
    'Joy_RYAxis': {'Type': 'Analogue', 'x': 1142, 'y': 604, 'width': 740}, # Throttle top rotary
    'Joy_RZAxis': {'Type': 'Analogue', 'x': 3074, 'y': 1946, 'width': 720}, # Stick yaw
    'Joy_UAxis': {'Type': 'Analogue', 'x': 422, 'y': 584, 'width': 460}, # Throttle 'volume' slider
    'Joy_XAxis': {'Type': 'Analogue', 'x': 3074, 'y': 1894, 'width': 720}, # Stick roll
    'Joy_YAxis': {'Type': 'Analogue', 'x': 3074, 'y': 1842, 'width': 720}, # Stick pitch
    'Joy_ZAxis': {'Type': 'Analogue', 'x': 102, 'y': 1224, 'width': 460}, # Throttle main slider
    '?Wheel': {'Type': 'Analogue', 'x': 120, 'y': 694, 'width': 660}, # Throttle rear wheel
  },
  'SaitekX52Pro': {
    'Joy_1': {'Type': 'Digital', 'x': 3164, 'y': 824, 'width': 652}, # Stick primary trigger half press
    'Joy_2': {'Type': 'Digital', 'x': 2404, 'y': 214, 'width': 792}, # Stick 'Safe'
    'Joy_3': {'Type': 'Digital', 'x': 3104, 'y': 484, 'width': 692}, # Stick red button right of Safe
    'Joy_4': {'Type': 'Digital', 'x': 3104, 'y': 674, 'width': 692}, # Stick red button right of hat
    'Joy_5': {'Type': 'Digital', 'x': 1964, 'y': 674, 'width': 692}, # Stick black button left of hat
    'Joy_6': {'Type': 'Digital', 'x': 3092, 'y': 1144, 'width': 732}, # Stick pinky trigger
    'Joy_7': {'Type': 'Digital', 'x': 1364, 'y': 1054, 'width': 792}, # Throttle red button
    'Joy_8': {'Type': 'Digital', 'x': 1144, 'y': 660, 'width': 772}, # Throttle top rotary button
    'Joy_9': {'Type': 'Digital', 'x': 1624, 'y': 1554, 'width': 572}, # Stick first switch up
    'Joy_10': {'Type': 'Digital', 'x': 1624, 'y': 1610, 'width': 572}, # Stick first switch down
    'Joy_11': {'Type': 'Digital', 'x': 1784, 'y': 1724, 'width': 572}, # Stick second switch up
    'Joy_12': {'Type': 'Digital', 'x': 1784, 'y': 1780, 'width': 572}, # Stick second switch down
    'Joy_13': {'Type': 'Digital', 'x': 2084, 'y': 1864, 'width': 572}, # Stick third switch up
    'Joy_14': {'Type': 'Digital', 'x': 2084, 'y': 1920, 'width': 572}, # Stick third switch down
    'Joy_15': {'Type': 'Digital', 'x': 3164, 'y': 880, 'width': 652}, # Stick primary trigger full press
    'Joy_16': {'Type': 'Digital', 'x': 1004, 'y': 2016, 'width': 932}, # Throttle mouse click
    'Joy_17': {'Type': 'Digital', 'x': 104, 'y': 700, 'width': 732}, # Throttle rear wheel down
    'Joy_18': {'Type': 'Digital', 'x': 104, 'y': 644, 'width': 732}, # Throttle rear wheel up
    'Joy_19': {'Type': 'Digital', 'x': 104, 'y': 756, 'width': 732}, # Throttle rear wheel click
    'Joy_20': {'Type': 'Digital', 'x': 1814, 'y': 304, 'width': 932}, # Stick top hat up
    'Joy_21': {'Type': 'Digital', 'x': 1814, 'y': 360, 'width': 932}, # Stick top hat right
    'Joy_22': {'Type': 'Digital', 'x': 1814, 'y': 416, 'width': 932}, # Stick top hat down
    'Joy_23': {'Type': 'Digital', 'x': 1814, 'y': 472, 'width': 932}, # Stick top hat left
    'Joy_24': {'Type': 'Digital', 'x': 244, 'y': 284, 'width': 972}, # Throttle rear hat up
    'Joy_25': {'Type': 'Digital', 'x': 244, 'y': 340, 'width': 972}, # Throttle rear hat right
    'Joy_26': {'Type': 'Digital', 'x': 244, 'y': 396, 'width': 972}, # Throttle rear hat down
    'Joy_27': {'Type': 'Digital', 'x': 244, 'y': 452, 'width': 972}, # Throttle rear hat left
    'Joy_31': {'Type': 'Digital', 'x': 1494, 'y': 1320, 'width': 772}, # Throttle bottom rotary button
    'Joy_32': {'Type': 'Digital', 'x': 44, 'y': 1864, 'width': 752}, # Left-hand MFD button
    #'Joy_???': {'Type': 'Digital', 'x': 26, 'y': 1748, 'width': 570}, # Throttle bottom left button
    #'Joy_???': {'Type': 'Digital', 'x': 198, 'y': 1850, 'width': 570}, # Throttle bottom middle button
    #'Joy_???': {'Type': 'Digital', 'x': 355, 'y': 1954, 'width': 570}, # Throttle bottom right button
    'Joy_POV1Up': {'Type': 'Digital', 'x': 1694, 'y': 774, 'width': 932}, # PoV hat up
    'Joy_POV1Right': {'Type': 'Digital', 'x': 1694, 'y': 830, 'width': 932}, # PoV hat right
    'Joy_POV1Down': {'Type': 'Digital', 'x': 1694, 'y': 886, 'width': 932}, # PoV hat down
    'Joy_POV1Left': {'Type': 'Digital', 'x': 1694, 'y': 942, 'width': 932}, # PoV hat left
    'Joy_RXAxis': {'Type': 'Analogue', 'x': 1494, 'y': 1264, 'width': 772}, # Throttle bottom rotary
    'Joy_RYAxis': {'Type': 'Analogue', 'x': 1144, 'y': 604, 'width': 772}, # Throttle top rotary
    'Joy_RZAxis': {'Type': 'Analogue', 'x': 3034, 'y': 1956, 'width': 792}, # Stick yaw
    'Joy_UAxis': {'Type': 'Analogue', 'x': 264, 'y': 554, 'width': 632}, # Throttle 'volume' slider
    'Joy_XAxis': {'Type': 'Analogue', 'x': 3034, 'y': 1900, 'width': 792}, # Stick roll
    'Joy_YAxis': {'Type': 'Analogue', 'x': 3034, 'y': 1844, 'width': 792}, # Stick pitch
    'Joy_ZAxis': {'Type': 'Analogue', 'x': 84, 'y': 1054, 'width': 472, 'height': 108}, # Throttle main slider
    #'?Wheel': {'Type': 'Analogue', 'x': 120, 'y': 694, 'width': 660}, # Throttle rear wheel
  },
  'SaitekX55Joystick': {
    'Joy_1': {'Type': 'Digital', 'x': 2044, 'y': 604, 'width': 642, 'height': 108}, # Primary trigger
    'Joy_2': {'Type': 'Digital', 'x': 2144, 'y': 224, 'width': 792}, # Top trigger
    'Joy_3': {'Type': 'Digital', 'x': 3064, 'y': 554, 'width': 692}, # Side trigger
    'Joy_4': {'Type': 'Digital', 'x': 2044, 'y': 744, 'width': 642, 'height': 108}, # Secondary trigger
    'Joy_5': {'Type': 'Digital', 'x': 3024, 'y': 974, 'width': 792}, # Pinky button
    'Joy_6': {'Type': 'Digital', 'x': 2044, 'y': 884, 'width': 642, 'height': 108}, # Pinky trigger
    'Joy_7': {'Type': 'Digital', 'x': 3054, 'y': 224, 'width': 772}, # Witch hat up
    'Joy_8': {'Type': 'Digital', 'x': 3054, 'y': 280, 'width': 772}, # Witch hat right
    'Joy_9': {'Type': 'Digital', 'x': 3054, 'y': 336, 'width': 772}, # Witch hat down
    'Joy_10': {'Type': 'Digital', 'x': 3054, 'y': 392, 'width': 772}, # Witch hat left
    'Joy_11': {'Type': 'Digital', 'x': 3074, 'y': 724, 'width': 742}, # Castle hat up
    'Joy_12': {'Type': 'Digital', 'x': 3074, 'y': 780, 'width': 742}, # Castle hat right
    'Joy_13': {'Type': 'Digital', 'x': 3074, 'y': 836, 'width': 742}, # Castle hat down
    'Joy_14': {'Type': 'Digital', 'x': 3074, 'y': 892, 'width': 742}, # Castle hat left
    'Joy_POV1Up': {'Type': 'Digital', 'x': 1744, 'y': 304, 'width': 1072}, # PoV hat up
    'Joy_POV1Right': {'Type': 'Digital', 'x': 1744, 'y': 360, 'width': 1072}, # PoV hat right
    'Joy_POV1Down': {'Type': 'Digital', 'x': 1744, 'y': 416, 'width': 1072}, # PoV hat down
    'Joy_POV1Left': {'Type': 'Digital', 'x': 1744, 'y': 472, 'width': 1072}, # PoV hat left
    'Joy_RZAxis': {'Type': 'Analogue', 'x': 3194, 'y': 1166, 'width': 632},
    'Joy_XAxis': {'Type': 'Analogue', 'x': 3194, 'y': 1110, 'width': 632},
    'Joy_YAxis': {'Type': 'Analogue', 'x': 3194, 'y': 1054, 'width': 632}
  },
  'SaitekX55Throttle': {
    'Joy_1': {'Type': 'Digital', 'x': 44, 'y': 604, 'width': 852},  # E button
    'Joy_2': {'Type': 'Digital', 'x': 1874, 'y': 1660, 'width': 672}, # F push
    'Joy_3': {'Type': 'Digital', 'x': 1534, 'y': 1810, 'width': 672}, # G push
    'Joy_4': {'Type': 'Digital', 'x': 2574, 'y': 1694, 'width': 892}, # H button
    'Joy_5': {'Type': 'Digital', 'x': 2744, 'y': 1784, 'width': 892}, # I button
    'Joy_6': {'Type': 'Digital', 'x': 74, 'y': 1604, 'width': 572}, # Switch 1
    'Joy_7': {'Type': 'Digital', 'x': 74, 'y': 1660, 'width': 572}, # Switch 2
    'Joy_8': {'Type': 'Digital', 'x': 94, 'y': 1754, 'width': 572}, # Switch 3
    'Joy_9': {'Type': 'Digital', 'x': 94, 'y': 1810, 'width': 572}, # Switch 4
    'Joy_10': {'Type': 'Digital', 'x': 764, 'y': 1754, 'width': 572}, # Switch 5
    'Joy_11': {'Type': 'Digital', 'x': 764, 'y': 1810, 'width': 572}, # Switch 6
    'Joy_12': {'Type': 'Digital', 'x': 1104, 'y': 1424, 'width': 572}, # TGL 1 up
    'Joy_13': {'Type': 'Digital', 'x': 1104, 'y': 1480, 'width': 572}, # TGL 1 down
    'Joy_14': {'Type': 'Digital', 'x': 1164, 'y': 1284, 'width': 572}, # TGL 2 up
    'Joy_15': {'Type': 'Digital', 'x': 1164, 'y': 1340, 'width': 572}, # TGL 2 down
    'Joy_16': {'Type': 'Digital', 'x': 1224, 'y': 1154, 'width': 572}, # TGL 3 up
    'Joy_17': {'Type': 'Digital', 'x': 1224, 'y': 1210, 'width': 572}, # TGL 3 down
    'Joy_18': {'Type': 'Digital', 'x': 1244, 'y': 1014, 'width': 572}, # TGL 4 up
    'Joy_19': {'Type': 'Digital', 'x': 1244, 'y': 1070, 'width': 572}, # TGL 4 down
    'Joy_20': {'Type': 'Digital', 'x': 1154, 'y': 564, 'width': 772}, # H3 up
    'Joy_21': {'Type': 'Digital', 'x': 1154, 'y': 620, 'width': 772}, # H3 right
    'Joy_22': {'Type': 'Digital', 'x': 1154, 'y': 676, 'width': 772}, # H3 down
    'Joy_23': {'Type': 'Digital', 'x': 1154, 'y': 732, 'width': 772}, # H3 left
    'Joy_24': {'Type': 'Digital', 'x': 1364, 'y': 1924, 'width': 772}, # H4 up
    'Joy_25': {'Type': 'Digital', 'x': 1364, 'y': 1980, 'width': 772}, # H4 right
    'Joy_26': {'Type': 'Digital', 'x': 1364, 'y': 2036, 'width': 772}, # H4 down
    'Joy_27': {'Type': 'Digital', 'x': 1364, 'y': 2092, 'width': 772}, # H4 left
    'Joy_28': {'Type': 'Digital', 'x': 3124, 'y': 2034, 'width': 692}, # Pinky rocker up
    'Joy_29': {'Type': 'Digital', 'x': 3124, 'y': 2090, 'width': 692}, # Pinky rocker down
    'Joy_30': {'Type': 'Digital', 'x': 3134, 'y': 1884, 'width': 692}, # Pinky spin up
    'Joy_31': {'Type': 'Digital', 'x': 3134, 'y': 1940, 'width': 692}, # Pinky spin down
    'Joy_XAxis': {'Type': 'Analogue', 'x': 164, 'y': 680, 'width': 572}, # Throttle
    'Joy_UAxis': {'Type': 'Analogue', 'x': 1194, 'y': 870, 'width': 732}, # Mouse left/right
    'Joy_VAxis': {'Type': 'Analogue', 'x': 1194, 'y': 814, 'width': 732}, # Mouse up/down
    'Joy_ZAxis': {'Type': 'Analogue', 'x': 1874, 'y': 1604, 'width': 672}, # F spin
    'Joy_RXAxis': {'Type': 'Analogue', 'x': 1534, 'y': 1754, 'width': 672}, # G spin
    'Joy_RYAxis': {'Type': 'Analogue', 'x': 1014, 'y': 1574, 'width': 692}, # RTY2 axis
    'Joy_RZAxis': {'Type': 'Analogue', 'x': 854, 'y': 1654, 'width': 692}, # RTY1 axis
  },
  'SaitekX56Joystick':
  {
    'Joy_1': {'Type': 'Digital', 'x': 1964, 'y': 618, 'width': 642, 'height': 108}, # Primary trigger
    'Joy_2': {'Type': 'Digital', 'x': 2084, 'y': 208, 'width': 792}, # 'R' button
    'Joy_3': {'Type': 'Digital', 'x': 3014, 'y': 604, 'width': 792}, # Side button
    'Joy_4': {'Type': 'Digital', 'x': 2024, 'y': 904, 'width': 642}, # Stick press
    'Joy_5': {'Type': 'Digital', 'x': 3024, 'y': 974, 'width': 792}, # Pinky button
    'Joy_6': {'Type': 'Digital', 'x': 1964, 'y': 1038, 'width': 642, 'height': 108}, # Pinky trigger
    'Joy_7': {'Type': 'Digital', 'x': 3054, 'y': 224, 'width': 772}, # Witch hat up
    'Joy_8': {'Type': 'Digital', 'x': 3054, 'y': 280, 'width': 772}, # Witch hat right
    'Joy_9': {'Type': 'Digital', 'x': 3054, 'y': 336, 'width': 772}, # Witch hat down
    'Joy_10': {'Type': 'Digital', 'x': 3054, 'y': 392, 'width': 772}, # Witch hat left
    'Joy_11': {'Type': 'Digital', 'x': 3074, 'y': 724, 'width': 742}, # Castle hat up
    'Joy_12': {'Type': 'Digital', 'x': 3074, 'y': 780, 'width': 742}, # Castle hat right
    'Joy_13': {'Type': 'Digital', 'x': 3074, 'y': 836, 'width': 742}, # Castle hat down
    'Joy_14': {'Type': 'Digital', 'x': 3074, 'y': 892, 'width': 742}, # Castle hat left
    'Joy_POV1Up': {'Type': 'Digital', 'x': 1684, 'y': 288, 'width': 1072}, # PoV hat up
    'Joy_POV1Right': {'Type': 'Digital', 'x': 1684, 'y': 344, 'width': 1072}, # PoV hat right
    'Joy_POV1Down': {'Type': 'Digital', 'x': 1684, 'y': 400, 'width': 1072}, # PoV hat down
    'Joy_POV1Left': {'Type': 'Digital', 'x': 1684, 'y': 456, 'width': 1072}, # PoV hat left
    'Joy_RXAxis': {'Type': 'Analogue', 'x': 2024, 'y': 848, 'width': 642}, # Stick x
    'Joy_RYAxis': {'Type': 'Analogue', 'x': 2024, 'y': 792, 'width': 642}, # Stick y
    'Joy_RZAxis': {'Type': 'Analogue', 'x': 3194, 'y': 1166, 'width': 632}, # z
    'Joy_XAxis': {'Type': 'Analogue', 'x': 3194, 'y': 1110, 'width': 632}, # x
    'Joy_YAxis': {'Type': 'Analogue', 'x': 3194, 'y': 1054, 'width': 632} # y
  },
  '07382221': # Old name for Saitek X56 joystick
  {
    'Joy_1': {'Type': 'Digital', 'x': 1964, 'y': 618, 'width': 642, 'height': 108}, # Primary trigger
    'Joy_2': {'Type': 'Digital', 'x': 2084, 'y': 208, 'width': 792}, # 'R' button
    'Joy_3': {'Type': 'Digital', 'x': 3014, 'y': 604, 'width': 792}, # Side button
    'Joy_4': {'Type': 'Digital', 'x': 2024, 'y': 904, 'width': 642}, # Stick press
    'Joy_5': {'Type': 'Digital', 'x': 3024, 'y': 974, 'width': 792}, # Pinky button
    'Joy_6': {'Type': 'Digital', 'x': 1964, 'y': 1038, 'width': 642, 'height': 108}, # Pinky trigger
    'Joy_7': {'Type': 'Digital', 'x': 3054, 'y': 224, 'width': 772}, # Witch hat up
    'Joy_8': {'Type': 'Digital', 'x': 3054, 'y': 280, 'width': 772}, # Witch hat right
    'Joy_9': {'Type': 'Digital', 'x': 3054, 'y': 336, 'width': 772}, # Witch hat down
    'Joy_10': {'Type': 'Digital', 'x': 3054, 'y': 392, 'width': 772}, # Witch hat left
    'Joy_11': {'Type': 'Digital', 'x': 3074, 'y': 724, 'width': 742}, # Castle hat up
    'Joy_12': {'Type': 'Digital', 'x': 3074, 'y': 780, 'width': 742}, # Castle hat right
    'Joy_13': {'Type': 'Digital', 'x': 3074, 'y': 836, 'width': 742}, # Castle hat down
    'Joy_14': {'Type': 'Digital', 'x': 3074, 'y': 892, 'width': 742}, # Castle hat left
    'Joy_POV1Up': {'Type': 'Digital', 'x': 1684, 'y': 288, 'width': 1072}, # PoV hat up
    'Joy_POV1Right': {'Type': 'Digital', 'x': 1684, 'y': 344, 'width': 1072}, # PoV hat right
    'Joy_POV1Down': {'Type': 'Digital', 'x': 1684, 'y': 400, 'width': 1072}, # PoV hat down
    'Joy_POV1Left': {'Type': 'Digital', 'x': 1684, 'y': 456, 'width': 1072}, # PoV hat left
    'Joy_RXAxis': {'Type': 'Analogue', 'x': 2024, 'y': 848, 'width': 642}, # Stick x
    'Joy_RYAxis': {'Type': 'Analogue', 'x': 2024, 'y': 792, 'width': 642}, # Stick y
    'Joy_RZAxis': {'Type': 'Analogue', 'x': 3194, 'y': 1166, 'width': 632}, # z
    'Joy_XAxis': {'Type': 'Analogue', 'x': 3194, 'y': 1110, 'width': 632}, # x
    'Joy_YAxis': {'Type': 'Analogue', 'x': 3194, 'y': 1054, 'width': 632} # y
  },
  'SaitekX56Throttle':
  {
    'Joy_1': {'Type': 'Digital', 'x': 24, 'y': 604, 'width': 752},  # E button
    'Joy_2': {'Type': 'Digital', 'x': 1874, 'y': 1660, 'width': 672}, # F push
    'Joy_3': {'Type': 'Digital', 'x': 1534, 'y': 1810, 'width': 672}, # G push
    'Joy_4': {'Type': 'Digital', 'x': 2744, 'y': 1784, 'width': 892}, # I button
    'Joy_5': {'Type': 'Digital', 'x': 2574, 'y': 1694, 'width': 892}, # H button
    'Joy_6': {'Type': 'Digital', 'x': 74, 'y': 1604, 'width': 532}, # Switch 1
    'Joy_7': {'Type': 'Digital', 'x': 74, 'y': 1660, 'width': 532}, # Switch 2
    'Joy_8': {'Type': 'Digital', 'x': 94, 'y': 1754, 'width': 572}, # Switch 3
    'Joy_9': {'Type': 'Digital', 'x': 94, 'y': 1810, 'width': 572}, # Switch 4
    'Joy_10': {'Type': 'Digital', 'x': 764, 'y': 1754, 'width': 572}, # Switch 5
    'Joy_11': {'Type': 'Digital', 'x': 764, 'y': 1810, 'width': 572}, # Switch 6
    'Joy_12': {'Type': 'Digital', 'x': 1104, 'y': 1444, 'width': 572}, # TGL 1 up
    'Joy_13': {'Type': 'Digital', 'x': 1104, 'y': 1500, 'width': 572}, # TGL 1 down
    'Joy_14': {'Type': 'Digital', 'x': 1164, 'y': 1304, 'width': 572}, # TGL 2 up
    'Joy_15': {'Type': 'Digital', 'x': 1164, 'y': 1360, 'width': 572}, # TGL 2 down
    'Joy_16': {'Type': 'Digital', 'x': 1224, 'y': 1168, 'width': 572}, # TGL 3 up
    'Joy_17': {'Type': 'Digital', 'x': 1224, 'y': 1224, 'width': 572}, # TGL 3 down
    'Joy_18': {'Type': 'Digital', 'x': 1224, 'y': 1026, 'width': 572}, # TGL 4 up
    'Joy_19': {'Type': 'Digital', 'x': 1224, 'y': 1082, 'width': 572}, # TGL 4 down
    'Joy_20': {'Type': 'Digital', 'x': 1154, 'y': 534, 'width': 772}, # H3 up
    'Joy_21': {'Type': 'Digital', 'x': 1154, 'y': 590, 'width': 772}, # H3 right
    'Joy_22': {'Type': 'Digital', 'x': 1154, 'y': 646, 'width': 772}, # H3 down
    'Joy_23': {'Type': 'Digital', 'x': 1154, 'y': 702, 'width': 772}, # H3 left
    'Joy_24': {'Type': 'Digital', 'x': 1364, 'y': 1924, 'width': 772}, # H4 up
    'Joy_25': {'Type': 'Digital', 'x': 1364, 'y': 1980, 'width': 772}, # H4 right
    'Joy_26': {'Type': 'Digital', 'x': 1364, 'y': 2036, 'width': 772}, # H4 down
    'Joy_27': {'Type': 'Digital', 'x': 1364, 'y': 2092, 'width': 772}, # H4 left
    'Joy_28': {'Type': 'Digital', 'x': 3124, 'y': 2034, 'width': 692}, # Pinky rocker up
    'Joy_29': {'Type': 'Digital', 'x': 3124, 'y': 2090, 'width': 692}, # Pinky rocker down
    'Joy_30': {'Type': 'Digital', 'x': 3134, 'y': 1884, 'width': 692}, # Pinky spin up
    'Joy_31': {'Type': 'Digital', 'x': 3134, 'y': 1940, 'width': 692}, # Pinky spin down
    'Joy_32': {'Type': 'Digital', 'x': 1224, 'y': 894, 'width': 642}, # Stick press
    'Joy_XAxis': {'Type': 'Analogue', 'x': 84, 'y': 784, 'width': 572}, # Throttle (left/both)
    'Joy_YAxis': {'Type': 'Analogue', 'x': 124, 'y': 694, 'width': 572}, # Throttle (right)
    'Joy_ZAxis': {'Type': 'Analogue', 'x': 1874, 'y': 1604, 'width': 672}, # F spin
    'Joy_RXAxis': {'Type': 'Analogue', 'x': 1224, 'y': 838, 'width': 642}, # Stick x
    'Joy_RYAxis': {'Type': 'Analogue', 'x': 1224, 'y': 782, 'width': 642}, # Stick y
    'Joy_RZAxis': {'Type': 'Analogue', 'x': 1534, 'y': 1754, 'width': 672}, # G spin
    'Joy_UAxis': {'Type': 'Analogue', 'x': 1014, 'y': 1588, 'width': 692}, # RTY3 axis
    'Joy_VAxis': {'Type': 'Analogue', 'x': 854, 'y': 1668, 'width': 692}, # RTY4 axis
  },
  '0738A221': # Old name for Saitek X56 throttle
  {
    'Joy_1': {'Type': 'Digital', 'x': 24, 'y': 604, 'width': 752},  # E button
    'Joy_2': {'Type': 'Digital', 'x': 1874, 'y': 1660, 'width': 672}, # F push
    'Joy_3': {'Type': 'Digital', 'x': 1534, 'y': 1810, 'width': 672}, # G push
    'Joy_4': {'Type': 'Digital', 'x': 2574, 'y': 1694, 'width': 892}, # H button
    'Joy_5': {'Type': 'Digital', 'x': 2744, 'y': 1784, 'width': 892}, # I button
    'Joy_6': {'Type': 'Digital', 'x': 74, 'y': 1604, 'width': 532}, # Switch 1
    'Joy_7': {'Type': 'Digital', 'x': 74, 'y': 1660, 'width': 532}, # Switch 2
    'Joy_8': {'Type': 'Digital', 'x': 94, 'y': 1754, 'width': 572}, # Switch 3
    'Joy_9': {'Type': 'Digital', 'x': 94, 'y': 1810, 'width': 572}, # Switch 4
    'Joy_10': {'Type': 'Digital', 'x': 764, 'y': 1754, 'width': 572}, # Switch 5
    'Joy_11': {'Type': 'Digital', 'x': 764, 'y': 1810, 'width': 572}, # Switch 6
    'Joy_12': {'Type': 'Digital', 'x': 1104, 'y': 1444, 'width': 572}, # TGL 1 up
    'Joy_13': {'Type': 'Digital', 'x': 1104, 'y': 1500, 'width': 572}, # TGL 1 down
    'Joy_14': {'Type': 'Digital', 'x': 1164, 'y': 1304, 'width': 572}, # TGL 2 up
    'Joy_15': {'Type': 'Digital', 'x': 1164, 'y': 1360, 'width': 572}, # TGL 2 down
    'Joy_16': {'Type': 'Digital', 'x': 1224, 'y': 1168, 'width': 572}, # TGL 3 up
    'Joy_17': {'Type': 'Digital', 'x': 1224, 'y': 1224, 'width': 572}, # TGL 3 down
    'Joy_18': {'Type': 'Digital', 'x': 1224, 'y': 1026, 'width': 572}, # TGL 4 up
    'Joy_19': {'Type': 'Digital', 'x': 1224, 'y': 1082, 'width': 572}, # TGL 4 down
    'Joy_20': {'Type': 'Digital', 'x': 1154, 'y': 534, 'width': 772}, # H3 up
    'Joy_21': {'Type': 'Digital', 'x': 1154, 'y': 590, 'width': 772}, # H3 right
    'Joy_22': {'Type': 'Digital', 'x': 1154, 'y': 646, 'width': 772}, # H3 down
    'Joy_23': {'Type': 'Digital', 'x': 1154, 'y': 702, 'width': 772}, # H3 left
    'Joy_24': {'Type': 'Digital', 'x': 1364, 'y': 1924, 'width': 772}, # H4 up
    'Joy_25': {'Type': 'Digital', 'x': 1364, 'y': 1980, 'width': 772}, # H4 right
    'Joy_26': {'Type': 'Digital', 'x': 1364, 'y': 2036, 'width': 772}, # H4 down
    'Joy_27': {'Type': 'Digital', 'x': 1364, 'y': 2092, 'width': 772}, # H4 left
    'Joy_28': {'Type': 'Digital', 'x': 3124, 'y': 2034, 'width': 692}, # Pinky rocker up
    'Joy_29': {'Type': 'Digital', 'x': 3124, 'y': 2090, 'width': 692}, # Pinky rocker down
    'Joy_30': {'Type': 'Digital', 'x': 3134, 'y': 1884, 'width': 692}, # Pinky spin up
    'Joy_31': {'Type': 'Digital', 'x': 3134, 'y': 1940, 'width': 692}, # Pinky spin down
    'Joy_32': {'Type': 'Digital', 'x': 1224, 'y': 894, 'width': 642}, # Stick press
    'Joy_XAxis': {'Type': 'Analogue', 'x': 84, 'y': 784, 'width': 572}, # Throttle (left/both)
    'Joy_YAxis': {'Type': 'Analogue', 'x': 124, 'y': 694, 'width': 572}, # Throttle (right)
    'Joy_ZAxis': {'Type': 'Analogue', 'x': 1874, 'y': 1604, 'width': 672}, # F spin
    'Joy_RXAxis': {'Type': 'Analogue', 'x': 1224, 'y': 838, 'width': 642}, # Stick x
    'Joy_RYAxis': {'Type': 'Analogue', 'x': 1224, 'y': 782, 'width': 642}, # Stick y
    'Joy_RZAxis': {'Type': 'Analogue', 'x': 1534, 'y': 1754, 'width': 672}, # G spin
    'Joy_UAxis': {'Type': 'Analogue', 'x': 1014, 'y': 1588, 'width': 692}, # RTY3 axis
    'Joy_VAxis': {'Type': 'Analogue', 'x': 854, 'y': 1668, 'width': 692}, # RTY4 axis
  },
  'CHCombatStick': {
    'Joy_1': {'Type': 'Digital', 'x': 1974, 'y': 854, 'width': 592}, # Primary trigger
    'Joy_2': {'Type': 'Digital', 'x': 2984, 'y': 944, 'width': 832}, # Thumb button
    'Joy_3': {'Type': 'Digital', 'x': 2964, 'y': 654, 'width': 832}, # Top button
    'Joy_4': {'Type': 'Digital', 'x': 2084, 'y': 1159, 'width': 592}, # Pinky trigger
    'Joy_5': {'Type': 'Digital', 'x': 1754, 'y': 234, 'width': 892}, # Side trigger
    'Joy_6': {'Type': 'Digital', 'x': 1664, 'y': 334, 'width': 892}, # Top trigger
    'Joy_7': {'Type': 'Digital', 'x': 1689, 'y': 464, 'width': 832}, # PoV hat up
    'Joy_8': {'Type': 'Digital', 'x': 1689, 'y': 520, 'width': 832}, # PoV hat right
    'Joy_9': {'Type': 'Digital', 'x': 1689, 'y': 576, 'width': 832}, # PoV hat down
    'Joy_10': {'Type': 'Digital', 'x': 1689, 'y': 632, 'width': 832}, # PoV hat left
    'Joy_POV1Up': {'Type': 'Digital', 'x': 2964, 'y': 212, 'width': 832}, # Right hat up
    'Joy_POV1Right': {'Type': 'Digital', 'x': 2964, 'y': 268, 'width': 832}, # Right hat right
    'Joy_POV1Down': {'Type': 'Digital', 'x': 2964, 'y': 324, 'width': 832}, # Right hat down
    'Joy_POV1Left': {'Type': 'Digital', 'x': 2964, 'y': 380, 'width': 832}, # Right hat left
    'Joy_XAxis': {'Type': 'Analogue', 'x': 3124, 'y': 1168, 'width': 692}, # Stick X axis
    'Joy_YAxis': {'Type': 'Analogue', 'x': 3124, 'y': 1112, 'width': 692}, # Stick Y axis
    'Joy_ZAxis': {'Type': 'Analogue', 'x': 2254, 'y': 1894, 'width': 692}, # Wheel on left of base
  },
  'CHFighterStick': {
    'Joy_1': {'Type': 'Digital', 'x': 1974, 'y': 854, 'width': 592}, # Primary trigger
    'Joy_2': {'Type': 'Digital', 'x': 1664, 'y': 334, 'width': 892}, # Top trigger
    'Joy_3': {'Type': 'Digital', 'x': 1754, 'y': 234, 'width': 892}, # Side trigger
    'Joy_4': {'Type': 'Digital', 'x': 2084, 'y': 1159, 'width': 592}, # Pinky trigger
    'Joy_5': {'Type': 'Digital', 'x': 1689, 'y': 464, 'width': 832}, # Left hat up
    'Joy_6': {'Type': 'Digital', 'x': 1689, 'y': 520, 'width': 832}, # Left hat right
    'Joy_7': {'Type': 'Digital', 'x': 1689, 'y': 576, 'width': 832}, # Left hat down
    'Joy_8': {'Type': 'Digital', 'x': 1689, 'y': 632, 'width': 832}, # Left hat left
    'Joy_9': {'Type': 'Digital', 'x': 2994, 'y': 494, 'width': 832}, # Castle hat up
    'Joy_10': {'Type': 'Digital', 'x': 2994, 'y': 550, 'width': 832}, # Castle hat right
    'Joy_11': {'Type': 'Digital', 'x': 2994, 'y': 606, 'width': 832}, # Castle hat down
    'Joy_12': {'Type': 'Digital', 'x': 2994, 'y': 662, 'width': 832}, # Castle hat left
    'Joy_13': {'Type': 'Digital', 'x': 3058, 'y': 810, 'width': 772}, # Thumb hat up
    'Joy_14': {'Type': 'Digital', 'x': 3058, 'y': 866, 'width': 772}, # Thumb hat right
    'Joy_15': {'Type': 'Digital', 'x': 3058, 'y': 922, 'width': 772}, # Thumb hat down
    'Joy_16': {'Type': 'Digital', 'x': 3058, 'y': 978, 'width': 772}, # Thumb hat left
    'Joy_POV1Up': {'Type': 'Digital', 'x': 2964, 'y': 212, 'width': 832}, # POV hat up (looks like witch hat)
    'Joy_POV1Right': {'Type': 'Digital', 'x': 2964, 'y': 268, 'width': 832}, # POV hat right (looks like witch hat)
    'Joy_POV1Down': {'Type': 'Digital', 'x': 2964, 'y': 324, 'width': 832}, # POV hat down (looks like witch hat)
    'Joy_POV1Left': {'Type': 'Digital', 'x': 2964, 'y': 380, 'width': 832}, # POV hat left (looks like witch hat)
    'Joy_XAxis': {'Type': 'Analogue', 'x': 3124, 'y': 1112, 'width': 692}, # Stick X axis
    'Joy_YAxis': {'Type': 'Analogue', 'x': 3124, 'y': 1168, 'width': 692}, # Stick Y axis
    'Joy_ZAxis': {'Type': 'Analogue', 'x': 2254, 'y': 1894, 'width': 692}, # Wheel on left of base
  },
  '068EC0F3': { # CH FighterStick with CH manager
    'Joy_1': {'Type': 'Digital', 'x': 1974, 'y': 854, 'width': 592}, # Primary trigger
    'Joy_2': {'Type': 'Digital', 'x': 1664, 'y': 334, 'width': 892}, # Top trigger
    'Joy_3': {'Type': 'Digital', 'x': 1754, 'y': 234, 'width': 892}, # Side trigger
    'Joy_4': {'Type': 'Digital', 'x': 2084, 'y': 1159, 'width': 592}, # Pinky trigger
    'Joy_5': {'Type': 'Digital', 'x': 1689, 'y': 464, 'width': 832}, # Left hat up
    'Joy_6': {'Type': 'Digital', 'x': 1689, 'y': 520, 'width': 832}, # Left hat right
    'Joy_7': {'Type': 'Digital', 'x': 1689, 'y': 576, 'width': 832}, # Left hat down
    'Joy_8': {'Type': 'Digital', 'x': 1689, 'y': 632, 'width': 832}, # Left hat left
    'Joy_9': {'Type': 'Digital', 'x': 2994, 'y': 494, 'width': 832}, # Castle hat up
    'Joy_10': {'Type': 'Digital', 'x': 2994, 'y': 550, 'width': 832}, # Castle hat right
    'Joy_11': {'Type': 'Digital', 'x': 2994, 'y': 606, 'width': 832}, # Castle hat down
    'Joy_12': {'Type': 'Digital', 'x': 2994, 'y': 662, 'width': 832}, # Castle hat left
    'Joy_13': {'Type': 'Digital', 'x': 3058, 'y': 810, 'width': 772}, # Thumb hat up
    'Joy_14': {'Type': 'Digital', 'x': 3058, 'y': 866, 'width': 772}, # Thumb hat right
    'Joy_15': {'Type': 'Digital', 'x': 3058, 'y': 922, 'width': 772}, # Thumb hat down
    'Joy_16': {'Type': 'Digital', 'x': 3058, 'y': 978, 'width': 772}, # Thumb hat left
    'Joy_POV1Up': {'Type': 'Digital', 'x': 2964, 'y': 212, 'width': 832}, # POV hat up (looks like witch hat)
    'Joy_POV1Right': {'Type': 'Digital', 'x': 2964, 'y': 268, 'width': 832}, # POV hat right (looks like witch hat)
    'Joy_POV1Down': {'Type': 'Digital', 'x': 2964, 'y': 324, 'width': 832}, # POV hat down (looks like witch hat)
    'Joy_POV1Left': {'Type': 'Digital', 'x': 2964, 'y': 380, 'width': 832}, # POV hat left (looks like witch hat)
    'Joy_XAxis': {'Type': 'Analogue', 'x': 3124, 'y': 1112, 'width': 692}, # Stick X axis
    'Joy_YAxis': {'Type': 'Analogue', 'x': 3124, 'y': 1168, 'width': 692}, # Stick Y axis
    'Joy_ZAxis': {'Type': 'Analogue', 'x': 2254, 'y': 1894, 'width': 692}, # Wheel on left of base
  },
  'CHProThrottle1': {
    'Joy_1': {'Type': 'Digital', 'x': 1114, 'y': 966, 'width': 832}, # Castle hat right
    'Joy_2': {'Type': 'Digital', 'x': 1114, 'y': 1022, 'width': 832}, # Castle hat down
    'Joy_3': {'Type': 'Digital', 'x': 1114, 'y': 1078, 'width': 832}, # Castle hat left
    'Joy_4': {'Type': 'Digital', 'x': 1114, 'y': 910, 'width': 832}, # Castle hat up
    'Joy_5': {'Type': 'Digital', 'x': 1189, 'y': 1696, 'width': 1032}, # Bottom hat right
    'Joy_6': {'Type': 'Digital', 'x': 1189, 'y': 1752, 'width': 1032}, # Bottom hat down
    'Joy_7': {'Type': 'Digital', 'x': 1189, 'y': 1808, 'width': 1032}, # Bottom hat left
    'Joy_8': {'Type': 'Digital', 'x': 1189, 'y': 1640, 'width': 1032}, # Bottom hat up
    'Joy_9': {'Type': 'Digital', 'x': 1198, 'y': 1275, 'width': 832}, # Rear hat down
    'Joy_10': {'Type': 'Digital', 'x': 1198, 'y': 1219, 'width': 832}, # Rear hat right
    'Joy_11': {'Type': 'Digital', 'x': 1198, 'y': 1163, 'width': 832}, # Rear hat up
    'Joy_12': {'Type': 'Digital', 'x': 1198, 'y': 1331, 'width': 832}, # Rear hat left
    'Joy_13': {'Type': 'Digital', 'x': 1261, 'y': 1549, 'width': 932}, # Mouse button
    'Joy_14': {'Type': 'Digital', 'x': 1042, 'y': 814, 'width': 892}, # Right back
    'Joy_15': {'Type': 'Digital', 'x': 904, 'y': 724, 'width': 892}, # Middle back
    'Joy_16': {'Type': 'Digital', 'x': 684, 'y': 634, 'width': 892}, # Left back
    'Joy_POV1Up': {'Type': 'Digital', 'x': 132, 'y': 1896, 'width': 932}, # PoV hat up (looks like witch hat)
    'Joy_POV1Right': {'Type': 'Digital', 'x': 132, 'y': 1952, 'width': 932}, # PoV hat right (looks like witch hat)
    'Joy_POV1Down': {'Type': 'Digital', 'x': 132, 'y': 2008, 'width': 932}, # PoV hat down (looks like witch hat)
    'Joy_POV1Left': {'Type': 'Digital', 'x': 132, 'y': 1840, 'width': 932}, # PoV hat left (looks like witch hat)
    'Joy_XAxis': {'Type': 'Analogue', 'x': 1261, 'y': 1493, 'width': 932}, # Mouse X axis
    'Joy_YAxis': {'Type': 'Analogue', 'x': 1261, 'y': 1437, 'width': 932}, # Mouse Y axis
    'Joy_ZAxis': {'Type': 'Analogue', 'x': 80, 'y': 714, 'width': 692}, # Throttle
  },
  'CHProThrottle2': { # CH Pro Throttle with CH manager
    'Joy_1': {'Type': 'Digital', 'x': 1261, 'y': 1549, 'width': 932}, # Mouse button
    'Joy_2': {'Type': 'Digital', 'x': 1042, 'y': 814, 'width': 892}, # Right back
    'Joy_3': {'Type': 'Digital', 'x': 904, 'y': 724, 'width': 892}, # Middle back
    'Joy_4': {'Type': 'Digital', 'x': 684, 'y': 634, 'width': 892}, # Left back
    'Joy_5': {'Type': 'Digital', 'x': 1198, 'y': 1275, 'width': 832}, # Rear hat down
    'Joy_6': {'Type': 'Digital', 'x': 1198, 'y': 1219, 'width': 832}, # Rear hat right
    'Joy_7': {'Type': 'Digital', 'x': 1198, 'y': 1163, 'width': 832}, # Rear hat up
    'Joy_8': {'Type': 'Digital', 'x': 1198, 'y': 1331, 'width': 832}, # Rear hat left
    'Joy_9': {'Type': 'Digital', 'x': 1114, 'y': 966, 'width': 832}, # Castle hat right
    'Joy_10': {'Type': 'Digital', 'x': 1114, 'y': 1022, 'width': 832}, # Castle hat down
    'Joy_11': {'Type': 'Digital', 'x': 1114, 'y': 1078, 'width': 832}, # Castle hat left
    'Joy_12': {'Type': 'Digital', 'x': 1114, 'y': 910, 'width': 832}, # Castle hat up
    'Joy_13': {'Type': 'Digital', 'x': 1189, 'y': 1696, 'width': 1032}, # Bottom hat right
    'Joy_14': {'Type': 'Digital', 'x': 1189, 'y': 1752, 'width': 1032}, # Bottom hat down
    'Joy_15': {'Type': 'Digital', 'x': 1189, 'y': 1808, 'width': 1032}, # Bottom hat left
    'Joy_16': {'Type': 'Digital', 'x': 1189, 'y': 1640, 'width': 1032}, # Bottom hat up
    'Joy_POV1Up': {'Type': 'Digital', 'x': 132, 'y': 1896, 'width': 932}, # PoV hat up (looks like witch hat)
    'Joy_POV1Right': {'Type': 'Digital', 'x': 132, 'y': 1952, 'width': 932}, # PoV hat right (looks like witch hat)
    'Joy_POV1Down': {'Type': 'Digital', 'x': 132, 'y': 2008, 'width': 932}, # PoV hat down (looks like witch hat)
    'Joy_POV1Left': {'Type': 'Digital', 'x': 132, 'y': 1840, 'width': 932}, # PoV hat left (looks like witch hat)
    'Joy_XAxis': {'Type': 'Analogue', 'x': 1261, 'y': 1493, 'width': 932}, # Mouse X axis
    'Joy_YAxis': {'Type': 'Analogue', 'x': 1261, 'y': 1437, 'width': 932}, # Mouse Y axis
    'Joy_ZAxis': {'Type': 'Analogue', 'x': 80, 'y': 714, 'width': 692}, # Throttle
  },
  '068EC010': { # CH Pro Throttle with CH manager, alternate
    'Joy_1': {'Type': 'Digital', 'x': 1261, 'y': 1549, 'width': 932}, # Mouse button
    'Joy_2': {'Type': 'Digital', 'x': 1042, 'y': 814, 'width': 892}, # Right back
    'Joy_3': {'Type': 'Digital', 'x': 904, 'y': 724, 'width': 892}, # Middle back
    'Joy_4': {'Type': 'Digital', 'x': 684, 'y': 634, 'width': 892}, # Left back
    'Joy_5': {'Type': 'Digital', 'x': 1198, 'y': 1275, 'width': 832}, # Rear hat down
    'Joy_6': {'Type': 'Digital', 'x': 1198, 'y': 1219, 'width': 832}, # Rear hat right
    'Joy_7': {'Type': 'Digital', 'x': 1198, 'y': 1163, 'width': 832}, # Rear hat up
    'Joy_8': {'Type': 'Digital', 'x': 1198, 'y': 1331, 'width': 832}, # Rear hat left
    'Joy_9': {'Type': 'Digital', 'x': 1114, 'y': 966, 'width': 832}, # Castle hat right
    'Joy_10': {'Type': 'Digital', 'x': 1114, 'y': 1022, 'width': 832}, # Castle hat down
    'Joy_11': {'Type': 'Digital', 'x': 1114, 'y': 1078, 'width': 832}, # Castle hat left
    'Joy_12': {'Type': 'Digital', 'x': 1114, 'y': 910, 'width': 832}, # Castle hat up
    'Joy_13': {'Type': 'Digital', 'x': 1189, 'y': 1696, 'width': 1032}, # Bottom hat right
    'Joy_14': {'Type': 'Digital', 'x': 1189, 'y': 1752, 'width': 1032}, # Bottom hat down
    'Joy_15': {'Type': 'Digital', 'x': 1189, 'y': 1808, 'width': 1032}, # Bottom hat left
    'Joy_16': {'Type': 'Digital', 'x': 1189, 'y': 1640, 'width': 1032}, # Bottom hat up
    'Joy_POV1Up': {'Type': 'Digital', 'x': 132, 'y': 1896, 'width': 932}, # PoV hat up (looks like witch hat)
    'Joy_POV1Right': {'Type': 'Digital', 'x': 132, 'y': 1952, 'width': 932}, # PoV hat right (looks like witch hat)
    'Joy_POV1Down': {'Type': 'Digital', 'x': 132, 'y': 2008, 'width': 932}, # PoV hat down (looks like witch hat)
    'Joy_POV1Left': {'Type': 'Digital', 'x': 132, 'y': 1840, 'width': 932}, # PoV hat left (looks like witch hat)
    'Joy_XAxis': {'Type': 'Analogue', 'x': 1261, 'y': 1493, 'width': 932}, # Mouse X axis
    'Joy_YAxis': {'Type': 'Analogue', 'x': 1261, 'y': 1437, 'width': 932}, # Mouse Y axis
    'Joy_ZAxis': {'Type': 'Analogue', 'x': 80, 'y': 714, 'width': 692}, # Throttle
  },
  '068E00FA': { # CH Quadrant throttle
    'Joy_XAxis': {'Type': 'Analogue', 'x': 354, 'y': 804, 'width': 932}, # Throttle 1
    'Joy_YAxis': {'Type': 'Analogue', 'x': 554, 'y': 564, 'width': 932}, # Throttle 2
    'Joy_ZAxis': {'Type': 'Analogue', 'x': 754, 'y': 324, 'width': 932}, # Throttle 3
    'Joy_RXAxis': {'Type': 'Analogue', 'x': 2214, 'y': 324, 'width': 932}, # Throttle 4
    'Joy_RYAxis': {'Type': 'Analogue', 'x': 2414, 'y': 564, 'width': 932}, # Throttle 5
    'Joy_RZAxis': {'Type': 'Analogue', 'x': 2614, 'y': 804, 'width': 932}, # Throttle 6
    'Joy_1': {'Type': 'Digital', 'x': 354, 'y': 1484, 'width': 932}, # Switch 1 up
    'Joy_2': {'Type': 'Digital', 'x': 354, 'y': 1540, 'width': 932}, # Switch 1 down
    'Joy_3': {'Type': 'Digital', 'x': 554, 'y': 1724, 'width': 932}, # Switch 2 up
    'Joy_4': {'Type': 'Digital', 'x': 554, 'y': 1780, 'width': 932}, # Switch 2 down
    'Joy_5': {'Type': 'Digital', 'x': 754, 'y': 1964, 'width': 932}, # Switch 3 up
    'Joy_6': {'Type': 'Digital', 'x': 754, 'y': 2020, 'width': 932}, # Switch 3 down
    'Joy_7': {'Type': 'Digital', 'x': 2214, 'y': 1964, 'width': 932}, # Switch 4 up
    'Joy_8': {'Type': 'Digital', 'x': 2214, 'y': 2020, 'width': 932}, # Switch 4 down
    'Joy_9': {'Type': 'Digital', 'x': 2414, 'y': 1724, 'width': 932}, # Switch 5 up
    'Joy_10': {'Type': 'Digital', 'x': 2414, 'y': 1780, 'width': 932}, # Switch 5 down
    'Joy_11': {'Type': 'Digital', 'x': 2614, 'y': 1484, 'width': 932}, # Switch 6 up
    'Joy_12': {'Type': 'Digital', 'x': 2614, 'y': 1540, 'width': 932}, # Switch 6 down
  },
  '06A30C2D': { # CH Pro Flight Quadrant throttle
    'Joy_XAxis': {'Type': 'Analogue', 'x': 554, 'y': 564, 'width': 932}, # Throttle 1
    'Joy_YAxis': {'Type': 'Analogue', 'x': 1474, 'y': 324, 'width': 932}, # Throttle 2
    'Joy_ZAxis': {'Type': 'Analogue', 'x': 2414, 'y': 564, 'width': 932}, # Throttle 3
    'Joy_1': {'Type': 'Digital', 'x': 354, 'y': 1484, 'width': 932}, # Switch 1 up
    'Joy_2': {'Type': 'Digital', 'x': 354, 'y': 1540, 'width': 932}, # Switch 1 down
    'Joy_3': {'Type': 'Digital', 'x': 1474, 'y': 1754, 'width': 932}, # Switch 2 up
    'Joy_4': {'Type': 'Digital', 'x': 1474, 'y': 1810, 'width': 932}, # Switch 2 down
    'Joy_5': {'Type': 'Digital', 'x': 2614, 'y': 1484, 'width': 932}, # Switch 3 up
    'Joy_6': {'Type': 'Digital', 'x': 2614, 'y': 1540, 'width': 932}, # Switch 3 down
  },
  'ThrustMasterHOTAS4': {
    'Joy_1': {'Type': 'Digital', 'x': 1394, 'y': 614, 'width': 1082}, # Stick primary trigger
    'Joy_2': {'Type': 'Digital', 'x': 2114, 'y': 264, 'width': 1192}, # Stick L1 button
    'Joy_3': {'Type': 'Digital', 'x': 2954, 'y': 544, 'width': 792, 'height': 108}, # Stick R3 button
    'Joy_4': {'Type': 'Digital', 'x': 2754, 'y': 374, 'width': 832, 'height': 108}, # Stick L3 button
    'Joy_5': {'Type': 'Digital', 'x': 950, 'y': 734, 'width': 592, 'height': 108}, # Throttle 'square'
    'Joy_6': {'Type': 'Digital', 'x': 950, 'y': 898, 'width': 592, 'height': 108}, # Throttle 'cross'
    'Joy_7': {'Type': 'Digital', 'x': 950, 'y': 1046, 'width': 592, 'height': 108}, # Throttle 'circle'
    'Joy_8': {'Type': 'Digital', 'x': 1044, 'y': 1374, 'width': 592, 'height': 108}, # Throttle 'triangle'
    'Joy_9': {'Type': 'Digital', 'x': 1628, 'y': 710, 'width': 832}, # Throttle R2 button
    'Joy_10': {'Type': 'Digital', 'x': 1928, 'y': 790, 'width': 532, 'height': 108}, # Throttle L2 button
    'Joy_11': {'Type': 'Digital', 'x': 284, 'y': 2044, 'width': 592}, # Throttle SE button
    'Joy_12': {'Type': 'Digital', 'x': 984, 'y': 2044, 'width': 592}, # Throttle ST button
    'Joy_POV1Up': {'Type': 'Digital', 'x': 994, 'y': 354, 'width': 1532}, # PoV hat up
    'Joy_POV1Right': {'Type': 'Digital', 'x': 994, 'y': 410, 'width': 1532}, # PoV hat right
    'Joy_POV1Down': {'Type': 'Digital', 'x': 994, 'y': 466, 'width': 1532}, # PoV hat down
    'Joy_POV1Left': {'Type': 'Digital', 'x': 994, 'y': 522, 'width': 1532}, # PoV hat left
    'Joy_RZAxis': {'Type': 'Analogue', 'x': 3018, 'y': 1988, 'width': 792, 'height': 108}, # Stick twist
    'Joy_XAxis': {'Type': 'Analogue', 'x': 3018, 'y': 1878, 'width': 792, 'height': 108}, # Stick left/right
    'Joy_YAxis': {'Type': 'Analogue', 'x': 3018, 'y': 1768, 'width': 792, 'height': 108}, # Stick up/down
    'Joy_ZAxis': {'Type': 'Analogue', 'x': 96, 'y': 736, 'width': 692}, # Throttle
    'Joy_UAxis': {'Type': 'Analogue', 'x': 1114, 'y': 1504, 'width': 932, 'height': 108}, # Throttle rocker
  },
  'ThrustMasterTFlightHOTASX': {
    'Joy_1': {'Type': 'Digital', 'x': 1394, 'y': 614, 'width': 1082}, # Stick primary trigger
    'Joy_2': {'Type': 'Digital', 'x': 2114, 'y': 264, 'width': 1192}, # Stick L1 button
    'Joy_3': {'Type': 'Digital', 'x': 2954, 'y': 544, 'width': 792, 'height': 108}, # Stick R3 button
    'Joy_4': {'Type': 'Digital', 'x': 2754, 'y': 374, 'width': 832, 'height': 108}, # Stick L3 button
    'Joy_5': {'Type': 'Digital', 'x': 950, 'y': 734, 'width': 592, 'height': 108}, # Throttle 'square'
    'Joy_6': {'Type': 'Digital', 'x': 950, 'y': 898, 'width': 592, 'height': 108}, # Throttle 'cross'
    'Joy_7': {'Type': 'Digital', 'x': 950, 'y': 1046, 'width': 592, 'height': 108}, # Throttle 'circle'
    'Joy_8': {'Type': 'Digital', 'x': 1044, 'y': 1374, 'width': 592, 'height': 108}, # Throttle 'triangle'
    'Joy_9': {'Type': 'Digital', 'x': 1628, 'y': 710, 'width': 832}, # Throttle R2 button
    'Joy_10': {'Type': 'Digital', 'x': 1928, 'y': 790, 'width': 532, 'height': 108}, # Throttle L2 button
    'Joy_11': {'Type': 'Digital', 'x': 284, 'y': 2004, 'width': 592}, # Throttle SE button
    'Joy_12': {'Type': 'Digital', 'x': 984, 'y': 2004, 'width': 592}, # Throttle ST button
    'Joy_POV1Up': {'Type': 'Digital', 'x': 994, 'y': 354, 'width': 1532}, # PoV hat up
    'Joy_POV1Right': {'Type': 'Digital', 'x': 994, 'y': 410, 'width': 1532}, # PoV hat right
    'Joy_POV1Down': {'Type': 'Digital', 'x': 994, 'y': 466, 'width': 1532}, # PoV hat down
    'Joy_POV1Left': {'Type': 'Digital', 'x': 994, 'y': 522, 'width': 1532}, # PoV hat left
    'Joy_RZAxis': {'Type': 'Analogue', 'x': 3018, 'y': 947, 'width': 792, 'height': 108}, # Stick twist
    'Joy_XAxis': {'Type': 'Analogue', 'x': 3018, 'y': 837, 'width': 792, 'height': 108}, # Stick left/right
    'Joy_YAxis': {'Type': 'Analogue', 'x': 3018, 'y': 727, 'width': 792, 'height': 108}, # Stick up/down
    'Joy_ZAxis': {'Type': 'Analogue', 'x': 96, 'y': 736, 'width': 692}, # Throttle
    'Joy_UAxis': {'Type': 'Analogue', 'x': 1114, 'y': 1504, 'width': 932, 'height': 108}, # Throttle rocker
  },
  '044FB106': {
    'Joy_1': {'Type': 'Digital', 'x': 684, 'y': 822, 'width': 1092}, # Primary trigger
    'Joy_2': {'Type': 'Digital', 'x': 2204, 'y': 744, 'width': 1092}, # Secondary trigger
    'Joy_3': {'Type': 'Digital', 'x': 2124, 'y': 564, 'width': 1092}, # Button 3
    'Joy_4': {'Type': 'Digital', 'x': 2174, 'y': 654, 'width': 1092}, # Button 4
    'Joy_5': {'Type': 'Digital', 'x': 474, 'y': 1564, 'width': 1092}, # Button 5
    'Joy_6': {'Type': 'Digital', 'x': 544, 'y': 1424, 'width': 1092}, # Button 6
    'Joy_7': {'Type': 'Digital', 'x': 584, 'y': 1266, 'width': 1092}, # Button 7
    'Joy_8': {'Type': 'Digital', 'x': 584, 'y': 1204, 'width': 1092}, # Button 8
    'Joy_9': {'Type': 'Digital', 'x': 554, 'y': 1704, 'width': 1092}, # Button 9
    'Joy_10': {'Type': 'Digital', 'x': 554, 'y': 1766, 'width': 1092}, # Button 10
    'Joy_11': {'Type': 'Digital', 'x': 2824, 'y': 1428, 'width': 692}, # Button 11
    'Joy_12': {'Type': 'Digital', 'x': 2824, 'y': 1338, 'width': 692}, # Button 12
    'Joy_POV1Up': {'Type': 'Digital', 'x': 990, 'y': 304, 'width': 1932}, # PoV hat up
    'Joy_POV1Right': {'Type': 'Digital', 'x': 990, 'y': 360, 'width': 1932}, # PoV hat right
    'Joy_POV1Down': {'Type': 'Digital', 'x': 990, 'y': 416, 'width': 1932}, # PoV hat down
    'Joy_POV1Left': {'Type': 'Digital', 'x': 990, 'y': 472, 'width': 1932}, # PoV hat left
    'Joy_RZAxis': {'Type': 'Analogue', 'x': 2364, 'y': 966, 'width': 1132}, # Stick twist
    'Joy_UAxis': {'Type': 'Analogue', 'x': 2584, 'y': 1833, 'width': 892}, # Throttle axis
    'Joy_XAxis': {'Type': 'Analogue', 'x': 2364, 'y': 910, 'width': 1132}, # Stick left/right
    'Joy_YAxis': {'Type': 'Analogue', 'x': 2364, 'y': 854, 'width': 1132}, # Stick up/down
  },
  'ThrustMasterWarthogJoystick': {
    'Joy_1': {'Type': 'Digital', 'x': 2042, 'y': 548, 'width': 620}, # Primary trigger half press
    'Joy_2': {'Type': 'Digital', 'x': 1952, 'y': 214, 'width': 880}, # Top trigger red button
    'Joy_3': {'Type': 'Digital', 'x': 2084, 'y': 1102, 'width': 580}, # Pinky button
    'Joy_4': {'Type': 'Digital', 'x': 2084, 'y': 1012, 'width': 580}, # Pinky trigger
    'Joy_5': {'Type': 'Digital', 'x': 2886, 'y': 212, 'width': 880}, # Top side button
    'Joy_6': {'Type': 'Digital', 'x': 2042, 'y': 602, 'width': 620}, # Primary trigger full press
    'Joy_7': {'Type': 'Digital', 'x': 1916, 'y': 300, 'width': 760}, # Left hat up
    'Joy_8': {'Type': 'Digital', 'x': 1916, 'y': 354, 'width': 760}, # Left hat right
    'Joy_9': {'Type': 'Digital', 'x': 1916, 'y': 408, 'width': 760}, # Left hat down
    'Joy_10': {'Type': 'Digital', 'x': 1916, 'y': 462, 'width': 760}, # Left hat left
    'Joy_11': {'Type': 'Digital', 'x': 3048, 'y': 562, 'width': 760}, # Right hat up
    'Joy_12': {'Type': 'Digital', 'x': 3048, 'y': 616, 'width': 760}, # Right hat right
    'Joy_13': {'Type': 'Digital', 'x': 3048, 'y': 670, 'width': 760}, # Right hat down
    'Joy_14': {'Type': 'Digital', 'x': 3048, 'y': 724, 'width': 760}, # Right hat left
    'Joy_15': {'Type': 'Digital', 'x': 2004, 'y': 700, 'width': 660}, # Thumb hat up
    'Joy_16': {'Type': 'Digital', 'x': 2004, 'y': 754, 'width': 660}, # Thumb hat right
    'Joy_17': {'Type': 'Digital', 'x': 2004, 'y': 808, 'width': 660}, # Thumb hat down
    'Joy_18': {'Type': 'Digital', 'x': 2004, 'y': 862, 'width': 660}, # Thumb hat left
    'Joy_19': {'Type': 'Digital', 'x': 2004, 'y': 914, 'width': 660}, # Thumb hat push
    'Joy_POV1Up': {'Type': 'Digital', 'x': 3048, 'y': 308, 'width': 760}, # PoV hat up
    'Joy_POV1Right': {'Type': 'Digital', 'x': 3048, 'y': 362, 'width': 760}, # PoV hat right
    'Joy_POV1Down': {'Type': 'Digital', 'x': 3048, 'y': 416, 'width': 760}, # PoV hat down
    'Joy_POV1Left': {'Type': 'Digital', 'x': 3048, 'y': 470, 'width': 760}, # PoV hat left
    'Joy_XAxis': {'Type': 'Analogue', 'x': 3126, 'y': 872, 'width': 680}, # Stick left/right
    'Joy_YAxis': {'Type': 'Analogue', 'x': 3126, 'y': 818, 'width': 680}, # Stick up/down
  },
  'ThrustMasterWarthogThrottle': {
    'Joy_1': {'Type': 'Digital', 'x': 2870, 'y': 1422, 'width': 680}, # Rear analogue push
    'Joy_2': {'Type': 'Digital', 'x': 1674, 'y': 1672, 'width': 660}, # Side hat push
    'Joy_3': {'Type': 'Digital', 'x': 1674, 'y': 1456, 'width': 660}, # Side hat up
    'Joy_4': {'Type': 'Digital', 'x': 1674, 'y': 1510, 'width': 660}, # Side hat right
    'Joy_5': {'Type': 'Digital', 'x': 1674, 'y': 1564, 'width': 660}, # Side hat down
    'Joy_6': {'Type': 'Digital', 'x': 1674, 'y': 1618, 'width': 660}, # Side hat left
    'Joy_7': {'Type': 'Digital', 'x': 1694, 'y': 1810, 'width': 640}, # Side top switch right
    'Joy_8': {'Type': 'Digital', 'x': 1694, 'y': 1756, 'width': 640}, # Side top switch left
    'Joy_9': {'Type': 'Digital', 'x': 1694, 'y': 1950, 'width': 640}, # Side middle switch right
    'Joy_10': {'Type': 'Digital', 'x': 1694, 'y': 1896, 'width': 640}, # Side middle switch left
    'Joy_11': {'Type': 'Digital', 'x': 1694, 'y': 2088, 'width': 640}, # Side bottom switch right
    'Joy_12': {'Type': 'Digital', 'x': 1694, 'y': 2034, 'width': 640}, # Side bottom switch left
    'Joy_13': {'Type': 'Digital', 'x': 3386, 'y': 1976, 'width': 420}, # Side toggle up
    'Joy_14': {'Type': 'Digital', 'x': 3386, 'y': 2030, 'width': 420}, # Side toggle down
    'Joy_15': {'Type': 'Digital', 'x': 3196, 'y': 1514, 'width': 620}, # Rear red button
    'Joy_16': {'Type': 'Digital', 'x': 1080, 'y': 566, 'width': 620}, # ENG left button
    'Joy_17': {'Type': 'Digital', 'x': 1200, 'y': 666, 'width': 620}, # ENG right button
    'Joy_18': {'Type': 'Digital', 'x': 1316, 'y': 1000, 'width': 420}, # ENG operate left down
    'Joy_19': {'Type': 'Digital', 'x': 1354, 'y': 844, 'width': 420}, # ENG operate right down
    'Joy_20': {'Type': 'Digital', 'x': 1140, 'y': 1118, 'width': 620}, # APU start button
    'Joy_21': {'Type': 'Digital', 'x': 960, 'y': 1362, 'width': 620}, # LDGH silence button
    'Joy_22': {'Type': 'Digital', 'x': 88, 'y': 750, 'width': 320}, # Flaps up
    'Joy_23': {'Type': 'Digital', 'x': 88, 'y': 804, 'width': 320}, # Flaps down
    'Joy_24': {'Type': 'Digital', 'x': 36, 'y': 1428, 'width': 480}, # EAC
    'Joy_25': {'Type': 'Digital', 'x': 218, 'y': 1542, 'width': 480}, # RDR ALT
    'Joy_26': {'Type': 'Digital', 'x': 436, 'y': 1646, 'width': 480}, # Autopilot
    'Joy_27': {'Type': 'Digital', 'x': 1020, 'y': 1460, 'width': 420}, # Autopilot select up
    'Joy_28': {'Type': 'Digital', 'x': 1020, 'y': 1514, 'width': 420}, # Autopilot select down
    'Joy_31': {'Type': 'Digital', 'x': 1316, 'y': 946, 'width': 420}, # ENG operate left up
    'Joy_32': {'Type': 'Digital', 'x': 1354, 'y': 790, 'width': 420}, # ENG operate right up
    'Joy_POV1Up': {'Type': 'Digital', 'x': 1964, 'y': 1214, 'width': 760}, # Rear PoV hat up
    'Joy_POV1Right': {'Type': 'Digital', 'x': 1964, 'y': 1268, 'width': 760}, # Rear PoV hat right
    'Joy_POV1Down': {'Type': 'Digital', 'x': 1964, 'y': 1322, 'width': 760}, # Rear PoV hat down
    'Joy_POV1Left': {'Type': 'Digital', 'x': 1964, 'y': 1376, 'width': 760}, # Rear PoV hat left
    'Joy_UAxis': {'Type': 'Analogue', 'x': 1082, 'y': 1252, 'width': 520}, # Throttle friction control
    'Joy_XAxis': {'Type': 'Analogue', 'x': 2870, 'y': 1368, 'width': 680}, # Rear analogue left/right
    'Joy_YAxis': {'Type': 'Analogue', 'x': 2870, 'y': 1314, 'width': 680}, # Rear analogue up/down
    'Joy_ZAxis': {'Type': 'Analogue', 'x': 530, 'y': 316, 'width': 540}, # Throttle
  },
  'ThrustMasterWarthogCombined': {
    # Stick
    'Joy_1': {'Type': 'Digital', 'x': 2042, 'y': 548, 'width': 620}, # Primary trigger half press
    'Joy_2': {'Type': 'Digital', 'x': 1952, 'y': 214, 'width': 880}, # Top trigger red button
    'Joy_3': {'Type': 'Digital', 'x': 2084, 'y': 1102, 'width': 580}, # Pinky button
    'Joy_4': {'Type': 'Digital', 'x': 2084, 'y': 1012, 'width': 580}, # Pinky trigger
    'Joy_5': {'Type': 'Digital', 'x': 2886, 'y': 212, 'width': 880}, # Top side button
    'Joy_6': {'Type': 'Digital', 'x': 2042, 'y': 602, 'width': 620}, # Primary trigger full press
    'Joy_7': {'Type': 'Digital', 'x': 1916, 'y': 300, 'width': 760}, # Left hat up
    'Joy_8': {'Type': 'Digital', 'x': 1916, 'y': 354, 'width': 760}, # Left hat right
    'Joy_9': {'Type': 'Digital', 'x': 1916, 'y': 408, 'width': 760}, # Left hat down
    'Joy_10': {'Type': 'Digital', 'x': 1916, 'y': 462, 'width': 760}, # Left hat left
    'Joy_11': {'Type': 'Digital', 'x': 3048, 'y': 562, 'width': 760}, # Right hat up
    'Joy_12': {'Type': 'Digital', 'x': 3048, 'y': 616, 'width': 760}, # Right hat right
    'Joy_13': {'Type': 'Digital', 'x': 3048, 'y': 670, 'width': 760}, # Right hat down
    'Joy_14': {'Type': 'Digital', 'x': 3048, 'y': 724, 'width': 760}, # Right hat left
    'Joy_15': {'Type': 'Digital', 'x': 2004, 'y': 700, 'width': 660}, # Thumb hat up
    'Joy_16': {'Type': 'Digital', 'x': 2004, 'y': 754, 'width': 660}, # Thumb hat right
    'Joy_17': {'Type': 'Digital', 'x': 2004, 'y': 808, 'width': 660}, # Thumb hat down
    'Joy_18': {'Type': 'Digital', 'x': 2004, 'y': 862, 'width': 660}, # Thumb hat left
    'Joy_19': {'Type': 'Digital', 'x': 2004, 'y': 914, 'width': 660}, # Thumb hat push
    'Joy_POV1Up': {'Type': 'Digital', 'x': 3048, 'y': 308, 'width': 760}, # PoV hat up
    'Joy_POV1Right': {'Type': 'Digital', 'x': 3048, 'y': 362, 'width': 760}, # PoV hat right
    'Joy_POV1Down': {'Type': 'Digital', 'x': 3048, 'y': 416, 'width': 760}, # PoV hat down
    'Joy_POV1Left': {'Type': 'Digital', 'x': 3048, 'y': 470, 'width': 760}, # PoV hat left
    'Joy_XAxis': {'Type': 'Analogue', 'x': 3126, 'y': 872, 'width': 680}, # Stick left/right
    'Joy_YAxis': {'Type': 'Analogue', 'x': 3126, 'y': 818, 'width': 680}, # Stick up/down
    # Throttle
    'Joy_20': {'Type': 'Digital', 'x': 3196, 'y': 1514, 'width': 620}, # Rear red button
    'Joy_21': {'Type': 'Digital', 'x': 960, 'y': 1362, 'width': 620}, # LDGH silence button
    'Joy_22': {'Type': 'Digital', 'x': 1964, 'y': 1214, 'width': 760}, # Rear PoV hat up
    'Joy_23': {'Type': 'Digital', 'x': 1964, 'y': 1268, 'width': 760}, # Rear PoV hat right
    'Joy_24': {'Type': 'Digital', 'x': 1964, 'y': 1322, 'width': 760}, # Rear PoV hat down
    'Joy_25': {'Type': 'Digital', 'x': 1964, 'y': 1376, 'width': 760}, # Rear PoV hat left
    #'Joy_25': {'Type': 'Digital', 'x': 2870, 'y': 1422, 'width': 680}, # Rear analogue push
    'Joy_26': {'Type': 'Digital', 'x': 1674, 'y': 1672, 'width': 660}, # Side hat push
    'Joy_27': {'Type': 'Digital', 'x': 1674, 'y': 1456, 'width': 660}, # Side hat up
    'Joy_28': {'Type': 'Digital', 'x': 1674, 'y': 1510, 'width': 660}, # Side hat right
    'Joy_29': {'Type': 'Digital', 'x': 1674, 'y': 1564, 'width': 660}, # Side hat down
    'Joy_30': {'Type': 'Digital', 'x': 1674, 'y': 1618, 'width': 660}, # Side hat left
    #'Joy_31': {'Type': 'Digital', 'x': 1694, 'y': 1810, 'width': 640}, # Side top switch right
    #'Joy_32': {'Type': 'Digital', 'x': 1694, 'y': 1756, 'width': 640}, # Side top switch left
    #'Joy_33': {'Type': 'Digital', 'x': 1694, 'y': 1950, 'width': 640}, # Side middle switch right
    #'Joy_34': {'Type': 'Digital', 'x': 1694, 'y': 1896, 'width': 640}, # Side middle switch left
    #'Joy_35': {'Type': 'Digital', 'x': 1694, 'y': 2088, 'width': 640}, # Side bottom switch right
    #'Joy_36': {'Type': 'Digital', 'x': 1694, 'y': 2034, 'width': 640}, # Side bottom switch left
    #'Joy_37': {'Type': 'Digital', 'x': 3386, 'y': 1976, 'width': 420}, # Side toggle up
    #'Joy_38': {'Type': 'Digital', 'x': 3386, 'y': 2030, 'width': 420}, # Side toggle down
    #'Joy_40': {'Type': 'Digital', 'x': 1080, 'y': 566, 'width': 620}, # ENG left button
    #'Joy_41': {'Type': 'Digital', 'x': 1200, 'y': 666, 'width': 620}, # ENG right button
    'Joy_31': {'Type': 'Digital', 'x': 1316, 'y': 1000, 'width': 420}, # ENG operate left down
    'Joy_32': {'Type': 'Digital', 'x': 1354, 'y': 844, 'width': 420}, # ENG operate right down
    #'Joy_44': {'Type': 'Digital', 'x': 1140, 'y': 1118, 'width': 620}, # APU start button
    #'Joy_46': {'Type': 'Digital', 'x': 88, 'y': 750, 'width': 320}, # Flaps up
    #'Joy_47': {'Type': 'Digital', 'x': 88, 'y': 804, 'width': 320}, # Flaps down
    #'Joy_48': {'Type': 'Digital', 'x': 36, 'y': 1428, 'width': 480}, # EAC
    #'Joy_49': {'Type': 'Digital', 'x': 218, 'y': 1542, 'width': 480}, # RDR ALT
    #'Joy_50': {'Type': 'Digital', 'x': 436, 'y': 1646, 'width': 480}, # Autopilot
    #'Joy_51': {'Type': 'Digital', 'x': 1020, 'y': 1460, 'width': 420}, # Autopilot select up
    #'Joy_52': {'Type': 'Digital', 'x': 1020, 'y': 1514, 'width': 420}, # Autopilot select down
    #'Joy_53': {'Type': 'Digital', 'x': 1316, 'y': 946, 'width': 420}, # ENG operate left up
    #'Joy_54': {'Type': 'Digital', 'x': 1354, 'y': 790, 'width': 420}, # ENG operate right up
    'Joy_VAxis': {'Type': 'Analogue', 'x': 1082, 'y': 1252, 'width': 520}, # Throttle friction control
    'Joy_RXAxis': {'Type': 'Analogue', 'x': 2870, 'y': 1368, 'width': 680}, # Rear analogue left/right
    'Joy_RYAxis': {'Type': 'Analogue', 'x': 2870, 'y': 1314, 'width': 680}, # Rear analogue up/down
    'Joy_ZAxis': {'Type': 'Analogue', 'x': 530, 'y': 316, 'width': 540}, # Throttle
  },
  '07382218': { # Saitek Side Panel Control Deck
    'Joy_1': {'Type': 'Digital', 'x': 34, 'y': 584, 'width': 592},
    'Joy_2': {'Type': 'Digital', 'x': 634, 'y': 584, 'width': 592},
    'Joy_3': {'Type': 'Digital', 'x': 1234, 'y': 584, 'width': 592},
    'Joy_4': {'Type': 'Digital', 'x': 2629, 'y': 584, 'width': 592},
    'Joy_5': {'Type': 'Digital', 'x': 3229, 'y': 584, 'width': 592},
    'Joy_6': {'Type': 'Digital', 'x': 34, 'y': 646, 'width': 592},
    'Joy_7': {'Type': 'Digital', 'x': 634, 'y': 646, 'width': 592},
    'Joy_8': {'Type': 'Digital', 'x': 1234, 'y': 646, 'width': 592},
    'Joy_9': {'Type': 'Digital', 'x': 2629, 'y': 646, 'width': 592},
    'Joy_10': {'Type': 'Digital', 'x': 3229, 'y': 646, 'width': 592},
    'Joy_11': {'Type': 'Digital', 'x': 34, 'y': 884, 'width': 592},
    'Joy_12': {'Type': 'Digital', 'x': 34, 'y': 946, 'width': 592},
    'Joy_13': {'Type': 'Digital', 'x': 634, 'y': 884, 'width': 592},
    'Joy_14': {'Type': 'Digital', 'x': 634, 'y': 946, 'width': 592},
    'Joy_15': {'Type': 'Digital', 'x': 1234, 'y': 884, 'width': 592},
    'Joy_16': {'Type': 'Digital', 'x': 1234, 'y': 946, 'width': 592},
    'Joy_17': {'Type': 'Digital', 'x': 2629, 'y': 884, 'width': 592},
    'Joy_18': {'Type': 'Digital', 'x': 3229, 'y': 884, 'width': 592},
    'Joy_19': {'Type': 'Digital', 'x': 2629, 'y': 946, 'width': 592},
    'Joy_20': {'Type': 'Digital', 'x': 3229, 'y': 946, 'width': 592},
    'Joy_21': {'Type': 'Digital', 'x': 2624, 'y': 1132, 'width': 992},
    'Joy_22': {'Type': 'Digital', 'x': 2624, 'y': 1222, 'width': 992},
    'Joy_23': {'Type': 'Digital', 'x': 2624, 'y': 1284, 'width': 992},
    'Joy_24': {'Type': 'Digital', 'x': 2624, 'y': 1344, 'width': 992},
    'Joy_25': {'Type': 'Digital', 'x': 1060, 'y': 1371, 'width': 772}, # Scroll wheel press
    'Joy_26': {'Type': 'Digital', 'x': 1060, 'y': 1259, 'width': 772},
    'Joy_27': {'Type': 'Digital', 'x': 1060, 'y': 1315, 'width': 772},
    'Joy_28': {'Type': 'Digital', 'x': 835, 'y': 1160, 'width': 992}, # Stick red button
    'Joy_XAxis': {'Type': 'Analogue', 'x': 695, 'y': 1556, 'width': 1132, 'height': 108},
    'Joy_YAxis': {'Type': 'Analogue', 'x': 695, 'y': 1666, 'width': 1132, 'height': 108},
    'Joy_ZAxis': {'Type': 'Analogue', 'x': 695, 'y': 1776, 'width': 1132, 'height': 108},
    'Joy_RXAxis': {'Type': 'Analogue', 'x': 2685, 'y': 1556, 'width': 1132, 'height': 108},
    'Joy_RYAxis': {'Type': 'Analogue', 'x': 2685, 'y': 1666, 'width': 1132, 'height': 108},
    'Joy_RZAxis': {'Type': 'Analogue', 'x': 2685, 'y': 1776, 'width': 1132, 'height': 108},
  },
  'XB360 Pad': {
    'Pad_LBumper': {'Type': 'Digital', 'x': 74, 'y': 624, 'width': 1392, 'height': 108},
    'Pad_LTrigger': {'Type': 'Digital', 'x': 74, 'y': 518, 'width': 1392},
    'Pad_RBumper': {'Type': 'Digital', 'x': 2368, 'y': 624, 'width': 1442, 'height': 108},
    'Pad_RTrigger': {'Type': 'Digital', 'x': 2368, 'y': 520, 'width': 1442},
    'Pad_Y': {'Type': 'Digital', 'x': 2625, 'y': 894, 'width': 1192},
    'Pad_B': {'Type': 'Digital', 'x': 2625, 'y': 988, 'width': 1192},
    'Pad_A': {'Type': 'Digital', 'x': 2625, 'y': 1083, 'width': 1192},
    'Pad_X': {'Type': 'Digital', 'x': 2625, 'y': 1178, 'width': 1192},
    'Pad_Back': {'Type': 'Digital', 'x': 74, 'y': 786, 'width': 1192},
    'Pad_Start': {'Type': 'Digital', 'x': 2625, 'y': 786, 'width': 1192},
    'Pad_DPadUp': {'Type': 'Digital', 'x': 134, 'y': 1308, 'width': 1032, 'height': 108},
    'Pad_DPadRight': {'Type': 'Digital', 'x': 134, 'y': 1418, 'width': 1032, 'height': 108},
    'Pad_DPadDown': {'Type': 'Digital', 'x': 134, 'y': 1528, 'width': 1032, 'height': 108},
    'Pad_DPadLeft': {'Type': 'Digital', 'x': 134, 'y': 1638, 'width': 1032, 'height': 108},
    'Pad_RStickY': {'Type': 'Analogue', 'x': 2765, 'y': 1322, 'width': 1052, 'height': 108},
    'Pad_RStickX': {'Type': 'Analogue', 'x': 2765, 'y': 1432, 'width': 1052, 'height': 108},
    'Pad_RThumb': {'Type': 'Digital', 'x': 2765, 'y': 1542, 'width': 1052, 'height': 108},
    'Pad_LStickY': {'Type': 'Analogue', 'x': 134, 'y': 930, 'width': 1032, 'height': 108},
    'Pad_LStickX': {'Type': 'Analogue', 'x': 134, 'y': 1040, 'width': 1032, 'height': 108},
    'Pad_LThumb': {'Type': 'Digital', 'x': 134, 'y': 1150, 'width': 1032, 'height': 108},
    # 2.3 appears to have renamed 'Pad' to 'GamePad'
    'GamePad_LBumper': {'Type': 'Digital', 'x': 74, 'y': 624, 'width': 1392, 'height': 108},
    'GamePad_LTrigger': {'Type': 'Digital', 'x': 74, 'y': 518, 'width': 1392},
    'GamePad_RBumper': {'Type': 'Digital', 'x': 2368, 'y': 624, 'width': 1442, 'height': 108},
    'GamePad_RTrigger': {'Type': 'Digital', 'x': 2368, 'y': 520, 'width': 1442},
    'GamePad_FaceUp': {'Type': 'Digital', 'x': 2625, 'y': 894, 'width': 1192},
    'GamePad_FaceRight': {'Type': 'Digital', 'x': 2625, 'y': 988, 'width': 1192},
    'GamePad_FaceDown': {'Type': 'Digital', 'x': 2625, 'y': 1083, 'width': 1192},
    'GamePad_FaceLeft': {'Type': 'Digital', 'x': 2625, 'y': 1178, 'width': 1192},
    'GamePad_Back': {'Type': 'Digital', 'x': 74, 'y': 786, 'width': 1192},
    'GamePad_Start': {'Type': 'Digital', 'x': 2625, 'y': 786, 'width': 1192},
    'GamePad_DPadUp': {'Type': 'Digital', 'x': 134, 'y': 1308, 'width': 1032, 'height': 108},
    'GamePad_DPadRight': {'Type': 'Digital', 'x': 134, 'y': 1418, 'width': 1032, 'height': 108},
    'GamePad_DPadDown': {'Type': 'Digital', 'x': 134, 'y': 1528, 'width': 1032, 'height': 108},
    'GamePad_DPadLeft': {'Type': 'Digital', 'x': 134, 'y': 1638, 'width': 1032, 'height': 108},
    'GamePad_RStickY': {'Type': 'Analogue', 'x': 2765, 'y': 1322, 'width': 1052, 'height': 108},
    'GamePad_RStickX': {'Type': 'Analogue', 'x': 2765, 'y': 1432, 'width': 1052, 'height': 108},
    'GamePad_RThumb': {'Type': 'Digital', 'x': 2765, 'y': 1542, 'width': 1052, 'height': 108},
    'GamePad_LStickY': {'Type': 'Analogue', 'x': 134, 'y': 930, 'width': 1032, 'height': 108},
    'GamePad_LStickX': {'Type': 'Analogue', 'x': 134, 'y': 1040, 'width': 1032, 'height': 108},
    'GamePad_LThumb': {'Type': 'Digital', 'x': 134, 'y': 1150, 'width': 1032, 'height': 108},
  },
  '045E02FF': { # Copy of XB360 controls
    'Pad_LBumper': {'Type': 'Digital', 'x': 74, 'y': 624, 'width': 1392, 'height': 108},
    'Pad_LTrigger': {'Type': 'Digital', 'x': 74, 'y': 518, 'width': 1392},
    'Pad_RBumper': {'Type': 'Digital', 'x': 2368, 'y': 624, 'width': 1442, 'height': 108},
    'Pad_RTrigger': {'Type': 'Digital', 'x': 2368, 'y': 520, 'width': 1442},
    'Pad_Y': {'Type': 'Digital', 'x': 2625, 'y': 894, 'width': 1192},
    'Pad_B': {'Type': 'Digital', 'x': 2625, 'y': 988, 'width': 1192},
    'Pad_A': {'Type': 'Digital', 'x': 2625, 'y': 1083, 'width': 1192},
    'Pad_X': {'Type': 'Digital', 'x': 2625, 'y': 1178, 'width': 1192},
    'Pad_Back': {'Type': 'Digital', 'x': 74, 'y': 786, 'width': 1192},
    'Pad_Start': {'Type': 'Digital', 'x': 2625, 'y': 786, 'width': 1192},
    'Pad_DPadUp': {'Type': 'Digital', 'x': 134, 'y': 1308, 'width': 1032, 'height': 108},
    'Pad_DPadRight': {'Type': 'Digital', 'x': 134, 'y': 1418, 'width': 1032, 'height': 108},
    'Pad_DPadDown': {'Type': 'Digital', 'x': 134, 'y': 1528, 'width': 1032, 'height': 108},
    'Pad_DPadLeft': {'Type': 'Digital', 'x': 134, 'y': 1638, 'width': 1032, 'height': 108},
    'Pad_RStickY': {'Type': 'Analogue', 'x': 2765, 'y': 1322, 'width': 1052, 'height': 108},
    'Pad_RStickX': {'Type': 'Analogue', 'x': 2765, 'y': 1432, 'width': 1052, 'height': 108},
    'Pad_RThumb': {'Type': 'Digital', 'x': 2765, 'y': 1542, 'width': 1052, 'height': 108},
    'Pad_LStickY': {'Type': 'Analogue', 'x': 134, 'y': 930, 'width': 1032, 'height': 108},
    'Pad_LStickX': {'Type': 'Analogue', 'x': 134, 'y': 1040, 'width': 1032, 'height': 108},
    'Pad_LThumb': {'Type': 'Digital', 'x': 134, 'y': 1150, 'width': 1032, 'height': 108},
    # 2.3 appears to have renamed 'Pad' to 'GamePad'
    'GamePad_LBumper': {'Type': 'Digital', 'x': 74, 'y': 624, 'width': 1392, 'height': 108},
    'GamePad_LTrigger': {'Type': 'Digital', 'x': 74, 'y': 518, 'width': 1392},
    'GamePad_RBumper': {'Type': 'Digital', 'x': 2368, 'y': 624, 'width': 1442, 'height': 108},
    'GamePad_RTrigger': {'Type': 'Digital', 'x': 2368, 'y': 520, 'width': 1442},
    'GamePad_FaceUp': {'Type': 'Digital', 'x': 2625, 'y': 894, 'width': 1192},
    'GamePad_FaceRight': {'Type': 'Digital', 'x': 2625, 'y': 988, 'width': 1192},
    'GamePad_FaceDown': {'Type': 'Digital', 'x': 2625, 'y': 1083, 'width': 1192},
    'GamePad_FaceLeft': {'Type': 'Digital', 'x': 2625, 'y': 1178, 'width': 1192},
    'GamePad_Back': {'Type': 'Digital', 'x': 74, 'y': 786, 'width': 1192},
    'GamePad_Start': {'Type': 'Digital', 'x': 2625, 'y': 786, 'width': 1192},
    'GamePad_DPadUp': {'Type': 'Digital', 'x': 134, 'y': 1308, 'width': 1032, 'height': 108},
    'GamePad_DPadRight': {'Type': 'Digital', 'x': 134, 'y': 1418, 'width': 1032, 'height': 108},
    'GamePad_DPadDown': {'Type': 'Digital', 'x': 134, 'y': 1528, 'width': 1032, 'height': 108},
    'GamePad_DPadLeft': {'Type': 'Digital', 'x': 134, 'y': 1638, 'width': 1032, 'height': 108},
    'GamePad_RStickY': {'Type': 'Analogue', 'x': 2765, 'y': 1322, 'width': 1052, 'height': 108},
    'GamePad_RStickX': {'Type': 'Analogue', 'x': 2765, 'y': 1432, 'width': 1052, 'height': 108},
    'GamePad_RThumb': {'Type': 'Digital', 'x': 2765, 'y': 1542, 'width': 1052, 'height': 108},
    'GamePad_LStickY': {'Type': 'Analogue', 'x': 134, 'y': 930, 'width': 1032, 'height': 108},
    'GamePad_LStickX': {'Type': 'Analogue', 'x': 134, 'y': 1040, 'width': 1032, 'height': 108},
    'GamePad_LThumb': {'Type': 'Digital', 'x': 134, 'y': 1150, 'width': 1032, 'height': 108},
  },
  '045E02DD': { # Copy of XB360 controls
    'Pad_LBumper': {'Type': 'Digital', 'x': 74, 'y': 624, 'width': 1392, 'height': 108},
    'Pad_LTrigger': {'Type': 'Digital', 'x': 74, 'y': 518, 'width': 1392},
    'Pad_RBumper': {'Type': 'Digital', 'x': 2368, 'y': 624, 'width': 1442, 'height': 108},
    'Pad_RTrigger': {'Type': 'Digital', 'x': 2368, 'y': 520, 'width': 1442},
    'Pad_Y': {'Type': 'Digital', 'x': 2625, 'y': 894, 'width': 1192},
    'Pad_B': {'Type': 'Digital', 'x': 2625, 'y': 988, 'width': 1192},
    'Pad_A': {'Type': 'Digital', 'x': 2625, 'y': 1083, 'width': 1192},
    'Pad_X': {'Type': 'Digital', 'x': 2625, 'y': 1178, 'width': 1192},
    'Pad_Back': {'Type': 'Digital', 'x': 74, 'y': 786, 'width': 1192},
    'Pad_Start': {'Type': 'Digital', 'x': 2625, 'y': 786, 'width': 1192},
    'Pad_DPadUp': {'Type': 'Digital', 'x': 134, 'y': 1308, 'width': 1032, 'height': 108},
    'Pad_DPadRight': {'Type': 'Digital', 'x': 134, 'y': 1418, 'width': 1032, 'height': 108},
    'Pad_DPadDown': {'Type': 'Digital', 'x': 134, 'y': 1528, 'width': 1032, 'height': 108},
    'Pad_DPadLeft': {'Type': 'Digital', 'x': 134, 'y': 1638, 'width': 1032, 'height': 108},
    'Pad_RStickY': {'Type': 'Analogue', 'x': 2765, 'y': 1322, 'width': 1052, 'height': 108},
    'Pad_RStickX': {'Type': 'Analogue', 'x': 2765, 'y': 1432, 'width': 1052, 'height': 108},
    'Pad_RThumb': {'Type': 'Digital', 'x': 2765, 'y': 1542, 'width': 1052, 'height': 108},
    'Pad_LStickY': {'Type': 'Analogue', 'x': 134, 'y': 930, 'width': 1032, 'height': 108},
    'Pad_LStickX': {'Type': 'Analogue', 'x': 134, 'y': 1040, 'width': 1032, 'height': 108},
    'Pad_LThumb': {'Type': 'Digital', 'x': 134, 'y': 1150, 'width': 1032, 'height': 108},
    # 2.3 appears to have renamed 'Pad' to 'GamePad'
    'GamePad_LBumper': {'Type': 'Digital', 'x': 74, 'y': 624, 'width': 1392, 'height': 108},
    'GamePad_LTrigger': {'Type': 'Digital', 'x': 74, 'y': 518, 'width': 1392},
    'GamePad_RBumper': {'Type': 'Digital', 'x': 2368, 'y': 624, 'width': 1442, 'height': 108},
    'GamePad_RTrigger': {'Type': 'Digital', 'x': 2368, 'y': 520, 'width': 1442},
    'GamePad_FaceUp': {'Type': 'Digital', 'x': 2625, 'y': 894, 'width': 1192},
    'GamePad_FaceRight': {'Type': 'Digital', 'x': 2625, 'y': 988, 'width': 1192},
    'GamePad_FaceDown': {'Type': 'Digital', 'x': 2625, 'y': 1083, 'width': 1192},
    'GamePad_FaceLeft': {'Type': 'Digital', 'x': 2625, 'y': 1178, 'width': 1192},
    'GamePad_Back': {'Type': 'Digital', 'x': 74, 'y': 786, 'width': 1192},
    'GamePad_Start': {'Type': 'Digital', 'x': 2625, 'y': 786, 'width': 1192},
    'GamePad_DPadUp': {'Type': 'Digital', 'x': 134, 'y': 1308, 'width': 1032, 'height': 108},
    'GamePad_DPadRight': {'Type': 'Digital', 'x': 134, 'y': 1418, 'width': 1032, 'height': 108},
    'GamePad_DPadDown': {'Type': 'Digital', 'x': 134, 'y': 1528, 'width': 1032, 'height': 108},
    'GamePad_DPadLeft': {'Type': 'Digital', 'x': 134, 'y': 1638, 'width': 1032, 'height': 108},
    'GamePad_RStickY': {'Type': 'Analogue', 'x': 2765, 'y': 1322, 'width': 1052, 'height': 108},
    'GamePad_RStickX': {'Type': 'Analogue', 'x': 2765, 'y': 1432, 'width': 1052, 'height': 108},
    'GamePad_RThumb': {'Type': 'Digital', 'x': 2765, 'y': 1542, 'width': 1052, 'height': 108},
    'GamePad_LStickY': {'Type': 'Analogue', 'x': 134, 'y': 930, 'width': 1032, 'height': 108},
    'GamePad_LStickX': {'Type': 'Analogue', 'x': 134, 'y': 1040, 'width': 1032, 'height': 108},
    'GamePad_LThumb': {'Type': 'Digital', 'x': 134, 'y': 1150, 'width': 1032, 'height': 108},
  },
  'GamePad': { # Copy of XBox controls
    'Pad_LBumper': {'Type': 'Digital', 'x': 74, 'y': 624, 'width': 1392, 'height': 108},
    'Pad_LTrigger': {'Type': 'Digital', 'x': 74, 'y': 518, 'width': 1392},
    'Pad_RBumper': {'Type': 'Digital', 'x': 2368, 'y': 624, 'width': 1442, 'height': 108},
    'Pad_RTrigger': {'Type': 'Digital', 'x': 2368, 'y': 520, 'width': 1442},
    'Pad_Y': {'Type': 'Digital', 'x': 2625, 'y': 894, 'width': 1192},
    'Pad_B': {'Type': 'Digital', 'x': 2625, 'y': 988, 'width': 1192},
    'Pad_A': {'Type': 'Digital', 'x': 2625, 'y': 1083, 'width': 1192},
    'Pad_X': {'Type': 'Digital', 'x': 2625, 'y': 1178, 'width': 1192},
    'Pad_Back': {'Type': 'Digital', 'x': 74, 'y': 786, 'width': 1192},
    'Pad_Start': {'Type': 'Digital', 'x': 2625, 'y': 786, 'width': 1192},
    'Pad_DPadUp': {'Type': 'Digital', 'x': 134, 'y': 1308, 'width': 1032, 'height': 108},
    'Pad_DPadRight': {'Type': 'Digital', 'x': 134, 'y': 1418, 'width': 1032, 'height': 108},
    'Pad_DPadDown': {'Type': 'Digital', 'x': 134, 'y': 1528, 'width': 1032, 'height': 108},
    'Pad_DPadLeft': {'Type': 'Digital', 'x': 134, 'y': 1638, 'width': 1032, 'height': 108},
    'Pad_RStickY': {'Type': 'Analogue', 'x': 2765, 'y': 1322, 'width': 1052, 'height': 108},
    'Pad_RStickX': {'Type': 'Analogue', 'x': 2765, 'y': 1432, 'width': 1052, 'height': 108},
    'Pad_RThumb': {'Type': 'Digital', 'x': 2765, 'y': 1542, 'width': 1052, 'height': 108},
    'Pad_LStickY': {'Type': 'Analogue', 'x': 134, 'y': 930, 'width': 1032, 'height': 108},
    'Pad_LStickX': {'Type': 'Analogue', 'x': 134, 'y': 1040, 'width': 1032, 'height': 108},
    'Pad_LThumb': {'Type': 'Digital', 'x': 134, 'y': 1150, 'width': 1032, 'height': 108},
    # 2.3 appears to have renamed 'Pad' to 'GamePad'
    'GamePad_LBumper': {'Type': 'Digital', 'x': 74, 'y': 624, 'width': 1392, 'height': 108},
    'GamePad_LTrigger': {'Type': 'Digital', 'x': 74, 'y': 518, 'width': 1392},
    'GamePad_RBumper': {'Type': 'Digital', 'x': 2368, 'y': 624, 'width': 1442, 'height': 108},
    'GamePad_RTrigger': {'Type': 'Digital', 'x': 2368, 'y': 520, 'width': 1442},
    'GamePad_FaceUp': {'Type': 'Digital', 'x': 2625, 'y': 894, 'width': 1192},
    'GamePad_FaceRight': {'Type': 'Digital', 'x': 2625, 'y': 988, 'width': 1192},
    'GamePad_FaceDown': {'Type': 'Digital', 'x': 2625, 'y': 1083, 'width': 1192},
    'GamePad_FaceLeft': {'Type': 'Digital', 'x': 2625, 'y': 1178, 'width': 1192},
    'GamePad_Back': {'Type': 'Digital', 'x': 74, 'y': 786, 'width': 1192},
    'GamePad_Start': {'Type': 'Digital', 'x': 2625, 'y': 786, 'width': 1192},
    'GamePad_DPadUp': {'Type': 'Digital', 'x': 134, 'y': 1308, 'width': 1032, 'height': 108},
    'GamePad_DPadRight': {'Type': 'Digital', 'x': 134, 'y': 1418, 'width': 1032, 'height': 108},
    'GamePad_DPadDown': {'Type': 'Digital', 'x': 134, 'y': 1528, 'width': 1032, 'height': 108},
    'GamePad_DPadLeft': {'Type': 'Digital', 'x': 134, 'y': 1638, 'width': 1032, 'height': 108},
    'GamePad_RStickY': {'Type': 'Analogue', 'x': 2765, 'y': 1322, 'width': 1052, 'height': 108},
    'GamePad_RStickX': {'Type': 'Analogue', 'x': 2765, 'y': 1432, 'width': 1052, 'height': 108},
    'GamePad_RThumb': {'Type': 'Digital', 'x': 2765, 'y': 1542, 'width': 1052, 'height': 108},
    'GamePad_LStickY': {'Type': 'Analogue', 'x': 134, 'y': 930, 'width': 1032, 'height': 108},
    'GamePad_LStickX': {'Type': 'Analogue', 'x': 134, 'y': 1040, 'width': 1032, 'height': 108},
    'GamePad_LThumb': {'Type': 'Digital', 'x': 134, 'y': 1150, 'width': 1032, 'height': 108},
  },
  '045E02E3': { # XBox Elite controller
    'Pad_LBumper': {'Type': 'Digital', 'x': 74, 'y': 624, 'width': 1392, 'height': 108},
    'Pad_LTrigger': {'Type': 'Digital', 'x': 74, 'y': 518, 'width': 1392},
    'Pad_RBumper': {'Type': 'Digital', 'x': 2368, 'y': 624, 'width': 1442, 'height': 108},
    'Pad_RTrigger': {'Type': 'Digital', 'x': 2368, 'y': 520, 'width': 1442},
    'Pad_Y': {'Type': 'Digital', 'x': 2625, 'y': 894, 'width': 1192},
    'Pad_B': {'Type': 'Digital', 'x': 2625, 'y': 988, 'width': 1192},
    'Pad_A': {'Type': 'Digital', 'x': 2625, 'y': 1083, 'width': 1192},
    'Pad_X': {'Type': 'Digital', 'x': 2625, 'y': 1178, 'width': 1192},
    'Pad_Back': {'Type': 'Digital', 'x': 74, 'y': 786, 'width': 1192},
    'Pad_Start': {'Type': 'Digital', 'x': 2625, 'y': 786, 'width': 1192},
    'Pad_DPadUp': {'Type': 'Digital', 'x': 134, 'y': 1308, 'width': 1032, 'height': 108},
    'Pad_DPadRight': {'Type': 'Digital', 'x': 134, 'y': 1418, 'width': 1032, 'height': 108},
    'Pad_DPadDown': {'Type': 'Digital', 'x': 134, 'y': 1528, 'width': 1032, 'height': 108},
    'Pad_DPadLeft': {'Type': 'Digital', 'x': 134, 'y': 1638, 'width': 1032, 'height': 108},
    'Pad_RStickY': {'Type': 'Analogue', 'x': 2765, 'y': 1322, 'width': 1052, 'height': 108},
    'Pad_RStickX': {'Type': 'Analogue', 'x': 2765, 'y': 1432, 'width': 1052, 'height': 108},
    'Pad_RThumb': {'Type': 'Digital', 'x': 2765, 'y': 1542, 'width': 1052, 'height': 108},
    'Pad_LStickY': {'Type': 'Analogue', 'x': 134, 'y': 930, 'width': 1032, 'height': 108},
    'Pad_LStickX': {'Type': 'Analogue', 'x': 134, 'y': 1040, 'width': 1032, 'height': 108},
    'Pad_LThumb': {'Type': 'Digital', 'x': 134, 'y': 1150, 'width': 1032, 'height': 108},
    # 2.3 appears to have renamed 'Pad' to 'GamePad'
    'GamePad_LBumper': {'Type': 'Digital', 'x': 74, 'y': 624, 'width': 1392, 'height': 108},
    'GamePad_LTrigger': {'Type': 'Digital', 'x': 74, 'y': 518, 'width': 1392},
    'GamePad_RBumper': {'Type': 'Digital', 'x': 2368, 'y': 624, 'width': 1442, 'height': 108},
    'GamePad_RTrigger': {'Type': 'Digital', 'x': 2368, 'y': 520, 'width': 1442},
    'GamePad_FaceUp': {'Type': 'Digital', 'x': 2625, 'y': 894, 'width': 1192},
    'GamePad_FaceRight': {'Type': 'Digital', 'x': 2625, 'y': 988, 'width': 1192},
    'GamePad_FaceDown': {'Type': 'Digital', 'x': 2625, 'y': 1083, 'width': 1192},
    'GamePad_FaceLeft': {'Type': 'Digital', 'x': 2625, 'y': 1178, 'width': 1192},
    'GamePad_Back': {'Type': 'Digital', 'x': 74, 'y': 786, 'width': 1192},
    'GamePad_Start': {'Type': 'Digital', 'x': 2625, 'y': 786, 'width': 1192},
    'GamePad_DPadUp': {'Type': 'Digital', 'x': 134, 'y': 1308, 'width': 1032, 'height': 108},
    'GamePad_DPadRight': {'Type': 'Digital', 'x': 134, 'y': 1418, 'width': 1032, 'height': 108},
    'GamePad_DPadDown': {'Type': 'Digital', 'x': 134, 'y': 1528, 'width': 1032, 'height': 108},
    'GamePad_DPadLeft': {'Type': 'Digital', 'x': 134, 'y': 1638, 'width': 1032, 'height': 108},
    'GamePad_RStickY': {'Type': 'Analogue', 'x': 2765, 'y': 1322, 'width': 1052, 'height': 108},
    'GamePad_RStickX': {'Type': 'Analogue', 'x': 2765, 'y': 1432, 'width': 1052, 'height': 108},
    'GamePad_RThumb': {'Type': 'Digital', 'x': 2765, 'y': 1542, 'width': 1052, 'height': 108},
    'GamePad_LStickY': {'Type': 'Analogue', 'x': 134, 'y': 930, 'width': 1032, 'height': 108},
    'GamePad_LStickX': {'Type': 'Analogue', 'x': 134, 'y': 1040, 'width': 1032, 'height': 108},
    'GamePad_LThumb': {'Type': 'Digital', 'x': 134, 'y': 1150, 'width': 1032, 'height': 108},
  },
  '1689FE00': { # Razer Sabretooth (xbox-like pad)
    'Pad_LBumper': {'Type': 'Digital', 'x': 74, 'y': 624, 'width': 1392, 'height': 108},
    'Pad_LTrigger': {'Type': 'Digital', 'x': 74, 'y': 518, 'width': 1392},
    'Pad_RBumper': {'Type': 'Digital', 'x': 2368, 'y': 624, 'width': 1442, 'height': 108},
    'Pad_RTrigger': {'Type': 'Digital', 'x': 2368, 'y': 520, 'width': 1442},
    'Pad_Y': {'Type': 'Digital', 'x': 2625, 'y': 894, 'width': 1192},
    'Pad_B': {'Type': 'Digital', 'x': 2625, 'y': 988, 'width': 1192},
    'Pad_A': {'Type': 'Digital', 'x': 2625, 'y': 1083, 'width': 1192},
    'Pad_X': {'Type': 'Digital', 'x': 2625, 'y': 1178, 'width': 1192},
    'Pad_Back': {'Type': 'Digital', 'x': 74, 'y': 786, 'width': 1192},
    'Pad_Start': {'Type': 'Digital', 'x': 2625, 'y': 786, 'width': 1192},
    'Pad_DPadUp': {'Type': 'Digital', 'x': 134, 'y': 1308, 'width': 1032, 'height': 108},
    'Pad_DPadRight': {'Type': 'Digital', 'x': 134, 'y': 1418, 'width': 1032, 'height': 108},
    'Pad_DPadDown': {'Type': 'Digital', 'x': 134, 'y': 1528, 'width': 1032, 'height': 108},
    'Pad_DPadLeft': {'Type': 'Digital', 'x': 134, 'y': 1638, 'width': 1032, 'height': 108},
    'Pad_RStickY': {'Type': 'Analogue', 'x': 2765, 'y': 1322, 'width': 1052, 'height': 108},
    'Pad_RStickX': {'Type': 'Analogue', 'x': 2765, 'y': 1432, 'width': 1052, 'height': 108},
    'Pad_RThumb': {'Type': 'Digital', 'x': 2765, 'y': 1542, 'width': 1052, 'height': 108},
    'Pad_LStickY': {'Type': 'Analogue', 'x': 134, 'y': 930, 'width': 1032, 'height': 108},
    'Pad_LStickX': {'Type': 'Analogue', 'x': 134, 'y': 1040, 'width': 1032, 'height': 108},
    'Pad_LThumb': {'Type': 'Digital', 'x': 134, 'y': 1150, 'width': 1032, 'height': 108},
    # 2.3 appears to have renamed 'Pad' to 'GamePad'
    'GamePad_LBumper': {'Type': 'Digital', 'x': 74, 'y': 624, 'width': 1392, 'height': 108},
    'GamePad_LTrigger': {'Type': 'Digital', 'x': 74, 'y': 518, 'width': 1392},
    'GamePad_RBumper': {'Type': 'Digital', 'x': 2368, 'y': 624, 'width': 1442, 'height': 108},
    'GamePad_RTrigger': {'Type': 'Digital', 'x': 2368, 'y': 520, 'width': 1442},
    'GamePad_FaceUp': {'Type': 'Digital', 'x': 2625, 'y': 894, 'width': 1192},
    'GamePad_FaceRight': {'Type': 'Digital', 'x': 2625, 'y': 988, 'width': 1192},
    'GamePad_FaceDown': {'Type': 'Digital', 'x': 2625, 'y': 1083, 'width': 1192},
    'GamePad_FaceLeft': {'Type': 'Digital', 'x': 2625, 'y': 1178, 'width': 1192},
    'GamePad_Back': {'Type': 'Digital', 'x': 74, 'y': 786, 'width': 1192},
    'GamePad_Start': {'Type': 'Digital', 'x': 2625, 'y': 786, 'width': 1192},
    'GamePad_DPadUp': {'Type': 'Digital', 'x': 134, 'y': 1308, 'width': 1032, 'height': 108},
    'GamePad_DPadRight': {'Type': 'Digital', 'x': 134, 'y': 1418, 'width': 1032, 'height': 108},
    'GamePad_DPadDown': {'Type': 'Digital', 'x': 134, 'y': 1528, 'width': 1032, 'height': 108},
    'GamePad_DPadLeft': {'Type': 'Digital', 'x': 134, 'y': 1638, 'width': 1032, 'height': 108},
    'GamePad_RStickY': {'Type': 'Analogue', 'x': 2765, 'y': 1322, 'width': 1052, 'height': 108},
    'GamePad_RStickX': {'Type': 'Analogue', 'x': 2765, 'y': 1432, 'width': 1052, 'height': 108},
    'GamePad_RThumb': {'Type': 'Digital', 'x': 2765, 'y': 1542, 'width': 1052, 'height': 108},
    'GamePad_LStickY': {'Type': 'Analogue', 'x': 134, 'y': 930, 'width': 1032, 'height': 108},
    'GamePad_LStickX': {'Type': 'Analogue', 'x': 134, 'y': 1040, 'width': 1032, 'height': 108},
    'GamePad_LThumb': {'Type': 'Digital', 'x': 134, 'y': 1150, 'width': 1032, 'height': 108},
  },
  'Logitech710WirelessGamepad': { # Logitech F710 (xbox-like pad)
    'Joy_1': {'Type': 'Digital', 'x': 2625, 'y': 1178, 'width': 1192}, # X
    'Joy_2': {'Type': 'Digital', 'x': 2625, 'y': 1083, 'width': 1192}, # A
    'Joy_3': {'Type': 'Digital', 'x': 2625, 'y': 988, 'width': 1192}, # B
    'Joy_4': {'Type': 'Digital', 'x': 2625, 'y': 894, 'width': 1192}, # Y
    'Joy_5': {'Type': 'Digital', 'x': 74, 'y': 510, 'width': 1392, 'height': 108}, # Left bumper
    'Joy_6': {'Type': 'Digital', 'x': 2368, 'y': 510, 'width': 1442, 'height': 108}, # Right bumper
    'Joy_7': {'Type': 'Digital', 'x': 74, 'y': 406, 'width': 1392}, # Left trigger
    'Joy_8': {'Type': 'Digital', 'x': 2368, 'y': 406, 'width': 1442}, # Right trigger
    'Joy_9': {'Type': 'Digital', 'x': 74, 'y': 706, 'width': 1192}, # Back
    'Joy_10': {'Type': 'Digital', 'x': 2625, 'y': 706, 'width': 1192}, # Start
    'Joy_11': {'Type': 'Digital', 'x': 134, 'y': 1542, 'width': 1032, 'height': 108}, # Left stick button
    'Joy_12': {'Type': 'Digital', 'x': 2765, 'y': 1542, 'width': 1052, 'height': 108}, # Right stick button
    'Joy_POV1Up': {'Type': 'Digital', 'x': 134, 'y': 864, 'width': 1032, 'height': 108},
    'Joy_POV1Right': {'Type': 'Digital', 'x': 134, 'y': 974, 'width': 1032, 'height': 108},
    'Joy_POV1Down': {'Type': 'Digital', 'x': 134, 'y': 1084, 'width': 1032, 'height': 108},
    'Joy_POV1Left': {'Type': 'Digital', 'x': 134, 'y': 1194, 'width': 1032, 'height': 108},
    'Joy_RZAxis': {'Type': 'Analogue', 'x': 2765, 'y': 1322, 'width': 1052, 'height': 108},
    'Joy_ZAxis': {'Type': 'Analogue', 'x': 2765, 'y': 1432, 'width': 1052, 'height': 108},
    'Joy_YAxis': {'Type': 'Analogue', 'x': 134, 'y': 1322, 'width': 1032, 'height': 108},
    'Joy_XAxis': {'Type': 'Analogue', 'x': 134, 'y': 1432, 'width': 1032, 'height': 108},
  },
  'DS4': {
    'Joy_1': {'Type': 'Digital', 'x': 2625, 'y': 1378, 'width': 1192}, # Square
    'Joy_2': {'Type': 'Digital', 'x': 2625, 'y': 1283, 'width': 1192}, # Cross
    'Joy_3': {'Type': 'Digital', 'x': 2625, 'y': 1188, 'width': 1192}, # Circle
    'Joy_4': {'Type': 'Digital', 'x': 2625, 'y': 1094, 'width': 1192}, # Triangle
    'Joy_5': {'Type': 'Digital', 'x': 74, 'y': 824, 'width': 1392, 'height': 108}, # Left bumper
    'Joy_6': {'Type': 'Digital', 'x': 2368, 'y': 824, 'width': 1442, 'height': 108}, # Right bumper
    'Joy_7': {'Type': 'Digital', 'x': 74, 'y': 986, 'width': 1192}, # Share (?)
    'Joy_8': {'Type': 'Digital', 'x': 2625, 'y': 986, 'width': 1192}, # Options (?)
    'Joy_9': {'Type': 'Digital', 'x': 1428, 'y': 551, 'width': 1052, 'height': 108}, # Trackpad press (?)
    'Joy_10': {'Type': 'Digital', 'x': 1328, 'y': 1866, 'width': 1192}, # PS button (?)
    'Joy_11': {'Type': 'Digital', 'x': 134, 'y': 1824, 'width': 1032, 'height': 108}, # Press of left stick
    'Joy_12': {'Type': 'Digital', 'x': 2765, 'y': 1824, 'width': 1052, 'height': 108}, # Press of right stick
    'Joy_POV1Up': {'Type': 'Digital', 'x': 134, 'y': 1104, 'width': 1032, 'height': 108},
    'Joy_POV1Right': {'Type': 'Digital', 'x': 134, 'y': 1214, 'width': 1032, 'height': 108},
    'Joy_POV1Down': {'Type': 'Digital', 'x': 134, 'y': 1324, 'width': 1032, 'height': 108},
    'Joy_POV1Left': {'Type': 'Digital', 'x': 134, 'y': 1434, 'width': 1032, 'height': 108},
    'Joy_YAxis': {'Type': 'Analogue', 'x': 134, 'y': 1604, 'width': 1032, 'height': 108}, # Vertical axis of left stick
    'Joy_XAxis': {'Type': 'Analogue', 'x': 134, 'y': 1714, 'width': 1032, 'height': 108}, # Horizontal axis of left stick
    'Joy_RZAxis': {'Type': 'Analogue', 'x': 2765, 'y': 1604, 'width': 1052, 'height': 108}, # Vertical axis of right stick
    'Joy_ZAxis': {'Type': 'Analogue', 'x': 2765, 'y': 1714, 'width': 1052, 'height': 108}, # Horizontal axis of right stick
    'Joy_RXAxis': {'Type': 'Analogue', 'x': 74, 'y': 718, 'width': 1392}, # Left trigger
    'Joy_RYAxis': {'Type': 'Analogue', 'x': 2368, 'y': 720, 'width': 1442}, # Right trigger
    #'?': {'Type': 'Analogue', 'x': 1428, 'y': 331, 'width': 1052, 'height': 108}, # Vertical axis of trackpad
    #'?': {'Type': 'Analogue', 'x': 1428, 'y': 441, 'width': 1052, 'height': 108}, # Horizontal axis of trackpad
  },
  'CHProPedals': {
    # Although the individual pedals are analogue, they often have digital binds due to their nature so we pretend they are digital
    'Joy_XAxis': {'Type': 'Digital', 'x': 164, 'y': 588, 'width': 1332, 'height': 162}, # Left pedal
    'Joy_YAxis': {'Type': 'Digital', 'x': 2264, 'y': 588, 'width': 1332, 'height': 162}, # Right pedal
    'Joy_ZAxis': {'Type': 'Analogue', 'x': 1208, 'y': 331, 'width': 1332, 'height': 162}, # Rudder
  },
  '068E00F2': {
    # Although the individual pedals are analogue, they often have digital binds due to their nature so we pretend they are digital
    'Joy_XAxis': {'Type': 'Digital', 'x': 164, 'y': 588, 'width': 1332, 'height': 162}, # Left pedal
    'Joy_YAxis': {'Type': 'Digital', 'x': 2264, 'y': 588, 'width': 1332, 'height': 162}, # Right pedal
    'Joy_ZAxis': {'Type': 'Analogue', 'x': 1208, 'y': 331, 'width': 1332, 'height': 162}, # Rudder
  },
  'LogitechG940Joystick': {
    'Joy_1': {'Type': 'Digital', 'x': 2034, 'y': 604, 'width': 652}, # Primary trigger half-press
    'Joy_2': {'Type': 'Digital', 'x': 2044, 'y': 424, 'width': 642, 'height': 108}, # Fire button
    'Joy_3': {'Type': 'Digital', 'x': 2124, 'y': 234, 'width': 642, 'height': 108}, # S1 button
    'Joy_4': {'Type': 'Digital', 'x': 3064, 'y': 496, 'width': 752}, # S2 button
    'Joy_5': {'Type': 'Digital', 'x': 3064, 'y': 584, 'width': 752}, # S3 button
    'Joy_6': {'Type': 'Digital', 'x': 2044, 'y': 764, 'width': 642, 'height': 108}, # S4 button
    'Joy_7': {'Type': 'Digital', 'x': 2044, 'y': 1018, 'width': 642, 'height': 108}, # S5 button
    'Joy_8': {'Type': 'Digital', 'x': 2954, 'y': 386, 'width': 832}, # Ministick button
    'Joy_VAxis': {'Type': 'Analogue', 'x': 2954, 'y': 330, 'width': 832}, # Ministick X
    'Joy_UAxis': {'Type': 'Analogue', 'x': 2954, 'y': 274, 'width': 832}, # Ministick Y
    'Joy_9': {'Type': 'Digital', 'x': 2034, 'y': 660, 'width': 652}, # Primary trigger full-press
    'Joy_POV1Up': {'Type': 'Digital', 'x': 3124, 'y': 694, 'width': 692}, # POV hat up
    'Joy_POV1Right': {'Type': 'Digital', 'x': 3124, 'y': 750, 'width': 692}, # POV hat right
    'Joy_POV1Down': {'Type': 'Digital', 'x': 3124, 'y': 806, 'width': 692}, # POV hat down
    'Joy_POV1Left': {'Type': 'Digital', 'x': 3124, 'y': 862, 'width': 692}, # POV hat left
    'Joy_XAxis': {'Type': 'Analogue', 'x': 3144, 'y': 1060, 'width': 672}, # Stick X axis
    'Joy_YAxis': {'Type': 'Analogue', 'x': 3144, 'y': 1004, 'width': 672}, # Stick Y axis
    'Joy_RXAxis': {'Type': 'Analogue', 'x': 3084, 'y': 1824, 'width': 592}, # Trim 2
    'Joy_RYAxis': {'Type': 'Analogue', 'x': 3224, 'y': 1744, 'width': 592}, # Trim 3
    'Joy_RZAxis': {'Type': 'Analogue', 'x': 2934, 'y': 1904, 'width': 592}, # Trim 1
  },
  'LogitechG940Throttle': {
  },
  'LogitechG940Pedals': {
    # Although the individual pedals are analogue, they often have digital binds due to their nature so we pretend they are digital
    'Joy_XAxis': {'Type': 'Digital', 'x': 2264, 'y': 588, 'width': 1332, 'height': 162}, # Right pedal (unconfirmed)
    'Joy_YAxis': {'Type': 'Digital', 'x': 164, 'y': 588, 'width': 1332, 'height': 162}, # Left pedal (unconfirmed)
    'Joy_RZAxis': {'Type': 'Analogue', 'x': 1208, 'y': 331, 'width': 1332, 'height': 162}, # Rudder
  },
  'T-Rudder': {
    # Although the individual pedals are analogue, they often have digital binds due to their nature so we pretend they are digital
    'Joy_XAxis': {'Type': 'Digital', 'x': 164, 'y': 588, 'width': 1332, 'height': 162}, # Left pedal
    'Joy_YAxis': {'Type': 'Digital', 'x': 2264, 'y': 588, 'width': 1332, 'height': 162}, # Right pedal
    'Joy_ZAxis': {'Type': 'Analogue', 'x': 1208, 'y': 331, 'width': 1332, 'height': 162}, # Rudder
  },
  'SaitekProFlightRudderPedals': {
    # Although the individual pedals are analogue, they often have digital binds due to their nature so we pretend they are digital
    'Joy_XAxis': {'Type': 'Digital', 'x': 164, 'y': 588, 'width': 1332, 'height': 162}, # Left pedal
    'Joy_YAxis': {'Type': 'Digital', 'x': 2264, 'y': 588, 'width': 1332, 'height': 162}, # Right pedal
    'Joy_RZAxis': {'Type': 'Analogue', 'x': 1208, 'y': 331, 'width': 1332, 'height': 162}, # Rudder
  },
  '06A30765': { # Copy of SaitekProFlightRudderPedals (although actually Cessna pedals)
    # Although the individual pedals are analogue, they often have digital binds due to their nature so we pretend they are digital
    'Joy_XAxis': {'Type': 'Digital', 'x': 164, 'y': 588, 'width': 1332, 'height': 162}, # Left pedal
    'Joy_YAxis': {'Type': 'Digital', 'x': 2264, 'y': 588, 'width': 1332, 'height': 162}, # Right pedal
    'Joy_RZAxis': {'Type': 'Analogue', 'x': 1208, 'y': 331, 'width': 1332, 'height': 162}, # Rudder
  },
  'SaitekProFlightCombatRudderPedals': {
    # Although the individual pedals are analogue, they often have digital binds due to their nature so we pretend they are digital
    'Joy_XAxis': {'Type': 'Digital', 'x': 164, 'y': 588, 'width': 1332, 'height': 162}, # Left pedal (unconfirmed)
    'Joy_YAxis': {'Type': 'Digital', 'x': 2264, 'y': 588, 'width': 1332, 'height': 162}, # Right pedal (unconfirmed)
    'Joy_RZAxis': {'Type': 'Analogue', 'x': 1208, 'y': 331, 'width': 1332, 'height': 162}, # Rudder
  },
  'SlawFlightControlRudder': {
    # Although the individual pedals are analogue, they often have digital binds due to their nature so we pretend they are digital
    'Joy_XAxis': {'Type': 'Digital', 'x': 164, 'y': 588, 'width': 1332, 'height': 162}, # Left pedal (unconfirmed)
    'Joy_YAxis': {'Type': 'Digital', 'x': 2264, 'y': 588, 'width': 1332, 'height': 162}, # Right pedal (unconfirmed)
    'Joy_RZAxis': {'Type': 'Analogue', 'x': 1208, 'y': 331, 'width': 1332, 'height': 162}, # Rudder
  },
  '16D00A38': { # MFG Crosswind
    # Although the individual pedals are analogue, they often have digital binds due to their nature so we pretend they are digital
    'Joy_XAxis': {'Type': 'Digital', 'x': 164, 'y': 588, 'width': 1332, 'height': 162}, # Left pedal (unconfirmed)
    'Joy_YAxis': {'Type': 'Digital', 'x': 2264, 'y': 588, 'width': 1332, 'height': 162}, # Right pedal (unconfirmed)
    'Joy_RZAxis': {'Type': 'Analogue', 'x': 1208, 'y': 331, 'width': 1332, 'height': 162}, # Rudder
  },
  '85640203': { # MFG Crosswind (alternate address)
    # Although the individual pedals are analogue, they often have digital binds due to their nature so we pretend they are digital
    'Joy_XAxis': {'Type': 'Digital', 'x': 164, 'y': 588, 'width': 1332, 'height': 162}, # Left pedal (unconfirmed)
    'Joy_YAxis': {'Type': 'Digital', 'x': 2264, 'y': 588, 'width': 1332, 'height': 162}, # Right pedal (unconfirmed)
    'Joy_RZAxis': {'Type': 'Analogue', 'x': 1208, 'y': 331, 'width': 1332, 'height': 162}, # Rudder
  },
  '046DC29A': { # Logitech GT Wheel
    'Joy_1': {'Type': 'Digital', 'x': 2624, 'y': 1089, 'width': 1192, 'height': 54}, # Cross button
    'Joy_2': {'Type': 'Digital', 'x': 2624, 'y': 1184, 'width': 1192, 'height': 54}, # Square button
    'Joy_3': {'Type': 'Digital', 'x': 2624, 'y': 994, 'width': 1192, 'height': 54}, # Circle button
    'Joy_4': {'Type': 'Digital', 'x': 2624, 'y': 900, 'width': 1192, 'height': 54}, # Triangle button
    'Joy_5': {'Type': 'Digital', 'x': 2404, 'y': 594, 'width': 992, 'height': 108}, # Right back paddle
    'Joy_6': {'Type': 'Digital', 'x': 24, 'y': 594, 'width': 992, 'height': 108}, # Left back paddle
    'Joy_7': {'Type': 'Digital', 'x': 2404, 'y': 484, 'width': 992, 'height': 54}, # Right shoulder button
    'Joy_8': {'Type': 'Digital', 'x': 24, 'y': 484, 'width': 992, 'height': 54}, # Left shoulder button
    'Joy_9': {'Type': 'Digital', 'x': 484, 'y': 1720, 'width': 1192, 'height': 54}, # Select button
    'Joy_10': {'Type': 'Digital', 'x': 1744, 'y': 1720, 'width': 1192, 'height': 54}, # Start button
    'Joy_11': {'Type': 'Digital', 'x': 2404, 'y': 354, 'width': 992, 'height': 54}, # R3 button
    'Joy_12': {'Type': 'Digital', 'x': 24, 'y': 354, 'width': 992, 'height': 54}, # L3 button
    'Joy_13': {'Type': 'Digital', 'x': 2684, 'y': 808, 'width': 1132, 'height': 54}, # Gear stick towards
    'Joy_14': {'Type': 'Digital', 'x': 2684, 'y': 752, 'width': 1132, 'height': 54}, # Gear stick away
    'Joy_15': {'Type': 'Digital', 'x': 2684, 'y': 1494, 'width': 1132, 'height': 108}, # Dial button
    'Joy_16': {'Type': 'Digital', 'x': 84, 'y': 1554, 'width': 1132, 'height': 54}, # Plus button
    'Joy_17': {'Type': 'Digital', 'x': 2684, 'y': 1274, 'width': 1132, 'height': 108}, # Dial clockwise
    'Joy_18': {'Type': 'Digital', 'x': 2684, 'y': 1384, 'width': 1132, 'height': 108}, # Dial anticlockwise
    'Joy_19': {'Type': 'Digital', 'x': 84, 'y': 1610, 'width': 1132, 'height': 54}, # Minus button
    'Joy_20': {'Type': 'Digital', 'x': 1544, 'y': 554, 'width': 332, 'height': 108}, # Horn
    'Joy_21': {'Type': 'Digital', 'x': 1114, 'y': 1824, 'width': 1192, 'height': 54}, # Central button
    'Joy_POV1Up': {'Type': 'Digital', 'x': 84, 'y': 870, 'width': 932, 'height': 108}, # PoV up
    'Joy_POV1Right': {'Type': 'Digital', 'x': 84, 'y': 980, 'width': 932, 'height': 108}, # PoV right
    'Joy_POV1Down': {'Type': 'Digital', 'x': 84, 'y': 1090, 'width': 932, 'height': 108}, # PoV down
    'Joy_POV1Left': {'Type': 'Digital', 'x': 84, 'y': 1200, 'width': 932, 'height': 108}, # PoV left
    'Joy_XAxis': {'Type': 'Analogue', 'x': 1284, 'y': 304, 'width': 932, 'height': 54}, # Steering wheel
  },
  '044FB351': { # Cougar MFD 1
    'Joy_1': {'Type': 'Digital', 'x': 134, 'y': 604, 'width': 592, 'height': 100},
    'Joy_2': {'Type': 'Digital', 'x': 239, 'y': 464, 'width': 592, 'height': 100},
    'Joy_3': {'Type': 'Digital', 'x': 644, 'y': 320, 'width': 592, 'height': 100},
    'Joy_4': {'Type': 'Digital', 'x': 1054, 'y': 464, 'width': 592, 'height': 100},
    'Joy_5': {'Type': 'Digital', 'x': 1161, 'y': 604, 'width': 592, 'height': 100},
    'Joy_6': {'Type': 'Digital', 'x': 1424, 'y': 932, 'width': 452, 'height': 100},
    'Joy_7': {'Type': 'Digital', 'x': 1424, 'y': 1040, 'width': 452, 'height': 100},
    'Joy_8': {'Type': 'Digital', 'x': 1424, 'y': 1148, 'width': 452, 'height': 100},
    'Joy_9': {'Type': 'Digital', 'x': 1424, 'y': 1256, 'width': 452, 'height': 100},
    'Joy_10': {'Type': 'Digital', 'x': 1424, 'y': 1364, 'width': 452, 'height': 100},
    'Joy_11': {'Type': 'Digital', 'x': 1161, 'y': 1694, 'width': 592, 'height': 100},
    'Joy_12': {'Type': 'Digital', 'x': 1054, 'y': 1834, 'width': 592, 'height': 100},
    'Joy_13': {'Type': 'Digital', 'x': 644, 'y': 1974, 'width': 592, 'height': 100},
    'Joy_14': {'Type': 'Digital', 'x': 239, 'y': 1834, 'width': 592, 'height': 100},
    'Joy_15': {'Type': 'Digital', 'x': 134, 'y': 1694, 'width': 592, 'height': 100},
    'Joy_16': {'Type': 'Digital', 'x': 24, 'y': 1364, 'width': 452, 'height': 100},
    'Joy_17': {'Type': 'Digital', 'x': 24, 'y': 1256, 'width': 452, 'height': 100},
    'Joy_18': {'Type': 'Digital', 'x': 24, 'y': 1148, 'width': 452, 'height': 100},
    'Joy_19': {'Type': 'Digital', 'x': 24, 'y': 1040, 'width': 452, 'height': 100},
    'Joy_20': {'Type': 'Digital', 'x': 24, 'y': 932, 'width': 452, 'height': 100},
    'Joy_21': {'Type': 'Digital', 'x': 1484, 'y': 762, 'width': 392, 'height': 80},
    'Joy_22': {'Type': 'Digital', 'x': 1484, 'y': 844, 'width': 392, 'height': 80},
    'Joy_23': {'Type': 'Digital', 'x': 1484, 'y': 1472, 'width': 392, 'height': 80},
    'Joy_24': {'Type': 'Digital', 'x': 1484, 'y': 1554, 'width': 392, 'height': 80},
    'Joy_25': {'Type': 'Digital', 'x': 84, 'y': 1472, 'width': 392, 'height': 80},
    'Joy_26': {'Type': 'Digital', 'x': 84, 'y': 1554, 'width': 392, 'height': 80},
    'Joy_27': {'Type': 'Digital', 'x': 84, 'y': 762, 'width': 392, 'height': 80},
    'Joy_28': {'Type': 'Digital', 'x': 84, 'y': 844, 'width': 392, 'height': 80},
  },
  '044FB352': { # Cougar MFD 2
    'Joy_1': {'Type': 'Digital', 'x': 2068, 'y': 604, 'width': 592, 'height': 100},
    'Joy_2': {'Type': 'Digital', 'x': 2173, 'y': 464, 'width': 592, 'height': 100},
    'Joy_3': {'Type': 'Digital', 'x': 2578, 'y': 320, 'width': 592, 'height': 100},
    'Joy_4': {'Type': 'Digital', 'x': 2988, 'y': 464, 'width': 592, 'height': 100},
    'Joy_5': {'Type': 'Digital', 'x': 3095, 'y': 604, 'width': 592, 'height': 100},
    'Joy_6': {'Type': 'Digital', 'x': 3358, 'y': 932, 'width': 452, 'height': 100},
    'Joy_7': {'Type': 'Digital', 'x': 3358, 'y': 1040, 'width': 452, 'height': 100},
    'Joy_8': {'Type': 'Digital', 'x': 3358, 'y': 1148, 'width': 452, 'height': 100},
    'Joy_9': {'Type': 'Digital', 'x': 3358, 'y': 1256, 'width': 452, 'height': 100},
    'Joy_10': {'Type': 'Digital', 'x': 3358, 'y': 1364, 'width': 452, 'height': 100},
    'Joy_11': {'Type': 'Digital', 'x': 3095, 'y': 1694, 'width': 592, 'height': 100},
    'Joy_12': {'Type': 'Digital', 'x': 2988, 'y': 1834, 'width': 592, 'height': 100},
    'Joy_13': {'Type': 'Digital', 'x': 2578, 'y': 1974, 'width': 592, 'height': 100},
    'Joy_14': {'Type': 'Digital', 'x': 2173, 'y': 1834, 'width': 592, 'height': 100},
    'Joy_15': {'Type': 'Digital', 'x': 2068, 'y': 1694, 'width': 592, 'height': 100},
    'Joy_16': {'Type': 'Digital', 'x': 1958, 'y': 1364, 'width': 452, 'height': 100},
    'Joy_17': {'Type': 'Digital', 'x': 1958, 'y': 1256, 'width': 452, 'height': 100},
    'Joy_18': {'Type': 'Digital', 'x': 1958, 'y': 1148, 'width': 452, 'height': 100},
    'Joy_19': {'Type': 'Digital', 'x': 1958, 'y': 1040, 'width': 452, 'height': 100},
    'Joy_20': {'Type': 'Digital', 'x': 1958, 'y': 932, 'width': 452, 'height': 100},
    'Joy_21': {'Type': 'Digital', 'x': 3418, 'y': 762, 'width': 392, 'height': 80},
    'Joy_22': {'Type': 'Digital', 'x': 3418, 'y': 844, 'width': 392, 'height': 80},
    'Joy_23': {'Type': 'Digital', 'x': 3418, 'y': 1472, 'width': 392, 'height': 80},
    'Joy_24': {'Type': 'Digital', 'x': 3418, 'y': 1554, 'width': 392, 'height': 80},
    'Joy_25': {'Type': 'Digital', 'x': 2018, 'y': 1472, 'width': 392, 'height': 80},
    'Joy_26': {'Type': 'Digital', 'x': 2018, 'y': 1554, 'width': 392, 'height': 80},
    'Joy_27': {'Type': 'Digital', 'x': 2018, 'y': 762, 'width': 392, 'height': 80},
    'Joy_28': {'Type': 'Digital', 'x': 2018, 'y': 844, 'width': 392, 'height': 80},
  },
  '11C05603': { # Cobra M5
    'Joy_1': {'Type': 'Digital', 'x': 64, 'y': 1273, 'width': 1392, 'height': 54}, # Primary trigger
    'Joy_2': {'Type': 'Digital', 'x': 2264, 'y': 922, 'width': 1392, 'height': 54}, # Secondary trigger
    'Joy_3': {'Type': 'Digital', 'x': 124, 'y': 1124, 'width': 1332, 'height': 54}, # NAV left red button
    'Joy_4': {'Type': 'Digital', 'x': 2324, 'y': 734, 'width': 1332, 'height': 54}, # NAV right red button
    'Joy_5': {'Type': 'Digital', 'x': 184, 'y': 722, 'width': 1272, 'height': 54}, # NAV witch hat left
    'Joy_6': {'Type': 'Digital', 'x': 184, 'y': 554, 'width': 1272, 'height': 54}, # NAV witch hat up
    'Joy_7': {'Type': 'Digital', 'x': 184, 'y': 610, 'width': 1272, 'height': 54}, # NAV witch hat right
    'Joy_8': {'Type': 'Digital', 'x': 184, 'y': 666, 'width': 1272, 'height': 54}, # NAV witch hat down
    'Joy_9': {'Type': 'Digital', 'x': 124, 'y': 1414, 'width': 1332, 'height': 54}, # NAV pinky trigger
    'Joy_10': {'Type': 'Digital', 'x': 124, 'y': 1064, 'width': 1332, 'height': 54}, # BVR left red button
    'Joy_11': {'Type': 'Digital', 'x': 2324, 'y': 674, 'width': 1332, 'height': 54}, # BVR right red button
    'Joy_12': {'Type': 'Digital', 'x': 184, 'y': 492, 'width': 1272, 'height': 54}, # BVR witch hat left
    'Joy_13': {'Type': 'Digital', 'x': 184, 'y': 324, 'width': 1272, 'height': 54}, # BVR witch hat up
    'Joy_14': {'Type': 'Digital', 'x': 184, 'y': 380, 'width': 1272, 'height': 54}, # BVR witch hat right
    'Joy_15': {'Type': 'Digital', 'x': 184, 'y': 436, 'width': 1272, 'height': 54}, # BVR witch hat down
    'Joy_16': {'Type': 'Digital', 'x': 124, 'y': 1354, 'width': 1332, 'height': 54}, # BVR pinky trigger
    'Joy_17': {'Type': 'Digital', 'x': 124, 'y': 1184, 'width': 1332, 'height': 54}, # VIS left red button
    'Joy_18': {'Type': 'Digital', 'x': 2324, 'y': 794, 'width': 1332, 'height': 54}, # VIS right red button
    'Joy_19': {'Type': 'Digital', 'x': 184, 'y': 952, 'width': 1272, 'height': 54}, # VIS witch hat left
    'Joy_20': {'Type': 'Digital', 'x': 184, 'y': 784, 'width': 1272, 'height': 54}, # VIS witch hat up
    'Joy_21': {'Type': 'Digital', 'x': 184, 'y': 840, 'width': 1272, 'height': 54}, # VIS witch hat right
    'Joy_22': {'Type': 'Digital', 'x': 184, 'y': 896, 'width': 1272, 'height': 54}, # VIS witch hat down
    'Joy_23': {'Type': 'Digital', 'x': 124, 'y': 1474, 'width': 1332, 'height': 54}, # VIS pinky trigger
    'Joy_POV1Up': {'Type': 'Digital', 'x': 1864, 'y': 324, 'width': 1932, 'height': 54}, # PoV up
    'Joy_POV1Right': {'Type': 'Digital', 'x': 1864, 'y': 380, 'width': 1932, 'height': 54}, # PoV right
    'Joy_POV1Down': {'Type': 'Digital', 'x': 1864, 'y': 436, 'width': 1932, 'height': 54}, # PoV down
    'Joy_POV1Left': {'Type': 'Digital', 'x': 1864, 'y': 492, 'width': 1932, 'height': 54}, # PoV left
    'Joy_XAxis': {'Type': 'Analogue', 'x': 2324, 'y': 1080, 'width': 1332, 'height': 54},
    'Joy_YAxis': {'Type': 'Analogue', 'x': 2324, 'y': 1024, 'width': 1332, 'height': 54},
    'Joy_RZAxis': {'Type': 'Analogue', 'x': 2324, 'y': 1136, 'width': 1332, 'height': 54},
  },
  '11C05605': { # Cobra M5 variant
    'Joy_1': {'Type': 'Digital', 'x': 64, 'y': 1273, 'width': 1392, 'height': 54}, # Primary trigger
    'Joy_2': {'Type': 'Digital', 'x': 2264, 'y': 922, 'width': 1392, 'height': 54}, # Secondary trigger
    'Joy_3': {'Type': 'Digital', 'x': 124, 'y': 1124, 'width': 1332, 'height': 54}, # NAV left red button
    'Joy_4': {'Type': 'Digital', 'x': 2324, 'y': 734, 'width': 1332, 'height': 54}, # NAV right red button
    'Joy_5': {'Type': 'Digital', 'x': 184, 'y': 722, 'width': 1272, 'height': 54}, # NAV witch hat left
    'Joy_6': {'Type': 'Digital', 'x': 184, 'y': 554, 'width': 1272, 'height': 54}, # NAV witch hat up
    'Joy_7': {'Type': 'Digital', 'x': 184, 'y': 610, 'width': 1272, 'height': 54}, # NAV witch hat right
    'Joy_8': {'Type': 'Digital', 'x': 184, 'y': 666, 'width': 1272, 'height': 54}, # NAV witch hat down
    'Joy_9': {'Type': 'Digital', 'x': 124, 'y': 1414, 'width': 1332, 'height': 54}, # NAV pinky trigger
    'Joy_10': {'Type': 'Digital', 'x': 124, 'y': 1064, 'width': 1332, 'height': 54}, # BVR left red button
    'Joy_11': {'Type': 'Digital', 'x': 2324, 'y': 674, 'width': 1332, 'height': 54}, # BVR right red button
    'Joy_12': {'Type': 'Digital', 'x': 184, 'y': 492, 'width': 1272, 'height': 54}, # BVR witch hat left
    'Joy_13': {'Type': 'Digital', 'x': 184, 'y': 324, 'width': 1272, 'height': 54}, # BVR witch hat up
    'Joy_14': {'Type': 'Digital', 'x': 184, 'y': 380, 'width': 1272, 'height': 54}, # BVR witch hat right
    'Joy_15': {'Type': 'Digital', 'x': 184, 'y': 436, 'width': 1272, 'height': 54}, # BVR witch hat down
    'Joy_16': {'Type': 'Digital', 'x': 124, 'y': 1354, 'width': 1332, 'height': 54}, # BVR pinky trigger
    'Joy_17': {'Type': 'Digital', 'x': 124, 'y': 1184, 'width': 1332, 'height': 54}, # VIS left red button
    'Joy_18': {'Type': 'Digital', 'x': 2324, 'y': 794, 'width': 1332, 'height': 54}, # VIS right red button
    'Joy_19': {'Type': 'Digital', 'x': 184, 'y': 952, 'width': 1272, 'height': 54}, # VIS witch hat left
    'Joy_20': {'Type': 'Digital', 'x': 184, 'y': 784, 'width': 1272, 'height': 54}, # VIS witch hat up
    'Joy_21': {'Type': 'Digital', 'x': 184, 'y': 840, 'width': 1272, 'height': 54}, # VIS witch hat right
    'Joy_22': {'Type': 'Digital', 'x': 184, 'y': 896, 'width': 1272, 'height': 54}, # VIS witch hat down
    'Joy_23': {'Type': 'Digital', 'x': 124, 'y': 1474, 'width': 1332, 'height': 54}, # VIS pinky trigger
    'Joy_POV1Up': {'Type': 'Digital', 'x': 1864, 'y': 324, 'width': 1932, 'height': 54}, # PoV up
    'Joy_POV1Right': {'Type': 'Digital', 'x': 1864, 'y': 380, 'width': 1932, 'height': 54}, # PoV right
    'Joy_POV1Down': {'Type': 'Digital', 'x': 1864, 'y': 436, 'width': 1932, 'height': 54}, # PoV down
    'Joy_POV1Left': {'Type': 'Digital', 'x': 1864, 'y': 492, 'width': 1932, 'height': 54}, # PoV left
    'Joy_XAxis': {'Type': 'Analogue', 'x': 2324, 'y': 1080, 'width': 1332, 'height': 54},
    'Joy_YAxis': {'Type': 'Analogue', 'x': 2324, 'y': 1024, 'width': 1332, 'height': 54},
    'Joy_RZAxis': {'Type': 'Analogue', 'x': 2324, 'y': 1136, 'width': 1332, 'height': 54},
  },
  '231D0121': { # VKB Gladiator
    'Joy_1': {'Type': 'Digital', 'x': 2184, 'y': 584, 'width': 1472, 'height': 54}, # Primary trigger (mode 1, unshifted)
    'Joy_3': {'Type': 'Digital', 'x': 2184, 'y': 640, 'width': 1472, 'height': 56}, # Primary trigger (mode 1, shifted)
    'Joy_5': {'Type': 'Digital', 'x': 2184, 'y': 704, 'width': 1472, 'height': 54}, # Primary trigger (mode 2, unshifted)
    'Joy_27': {'Type': 'Digital', 'x': 2184, 'y': 760, 'width': 1472, 'height': 56}, # Primary trigger (mode 2, shifted)
    'Joy_2': {'Type': 'Digital', 'x': 2124, 'y': 304, 'width': 1472, 'height': 54}, # Thumb trigger (mode 1, unshifted)
    'Joy_4': {'Type': 'Digital', 'x': 2124, 'y': 360, 'width': 1472, 'height': 56}, # Thumb trigger (mode 1, shifted)
    'Joy_28': {'Type': 'Digital', 'x': 2124, 'y': 424, 'width': 1472, 'height': 54}, # Thumb trigger (mode 2, unshifted)
    'Joy_29': {'Type': 'Digital', 'x': 2124, 'y': 480, 'width': 1472, 'height': 56}, # Thumb trigger (mode 2, shifted)
    'Joy_POV1Up': {'Type': 'Digital', 'x': 274, 'y': 304, 'width': 1112, 'height': 54}, # POV hat up (mode 1, unshifted)
    'Joy_19': {'Type': 'Digital', 'x': 274, 'y': 360, 'width': 1112, 'height': 54}, # POV hat up (mode 1, shifted)
    'Joy_POV1Right': {'Type': 'Digital', 'x': 274, 'y': 416, 'width': 1112, 'height': 52}, # POV hat right (mode 1, unshifted)
    'Joy_22': {'Type': 'Digital', 'x': 274, 'y': 470, 'width': 1112, 'height': 54}, # POV hat right (mode 1, shifted)
    'Joy_POV1Down': {'Type': 'Digital', 'x': 274, 'y': 526, 'width': 1112, 'height': 52}, # POV hat down (mode 1, unshifted)
    'Joy_20': {'Type': 'Digital', 'x': 274, 'y': 580, 'width': 1112, 'height': 54}, # POV hat down (mode 1, shifted)
    'Joy_POV1Left': {'Type': 'Digital', 'x': 274, 'y': 636, 'width': 1112, 'height': 52}, # POV hat right (mode 1, unshifted)
    'Joy_21': {'Type': 'Digital', 'x': 274, 'y': 690, 'width': 1112, 'height': 66}, # POV hat right (mode 1, shifted)
    'Joy_POV2Up': {'Type': 'Digital', 'x': 274, 'y': 764, 'width': 1112, 'height': 54}, # POV hat up (mode 2, unshifted)
    'Joy_23': {'Type': 'Digital', 'x': 274, 'y': 820, 'width': 1112, 'height': 54}, # POV hat up (mode 2, shifted)
    'Joy_POV2Right': {'Type': 'Digital', 'x': 274, 'y': 876, 'width': 1112, 'height': 52}, # POV hat right (mode 2, unshifted)
    'Joy_26': {'Type': 'Digital', 'x': 274, 'y': 930, 'width': 1112, 'height': 54}, # POV hat right (mode 2, shifted)
    'Joy_POV2Down': {'Type': 'Digital', 'x': 274, 'y': 986, 'width': 1112, 'height': 52}, # POV hat down (mode 2, unshifted)
    'Joy_24': {'Type': 'Digital', 'x': 274, 'y': 1040, 'width': 1112, 'height': 54}, # POV hat down (mode 2, shifted)
    'Joy_POV2Left': {'Type': 'Digital', 'x': 274, 'y': 1096, 'width': 1112, 'height': 52}, # POV hat right (mode 2, unshifted)
    'Joy_25': {'Type': 'Digital', 'x': 274, 'y': 1150, 'width': 1112, 'height': 66}, # POV hat right (mode 2, shifted)
    'Joy_XAxis': {'Type': 'Analogue', 'x': 2164, 'y': 910, 'width': 1532, 'height': 54},
    'Joy_YAxis': {'Type': 'Analogue', 'x': 2164, 'y': 854, 'width': 1532, 'height': 54},
    'Joy_RXAxis': {'Type': 'Analogue', 'x': 2164, 'y': 966, 'width': 1532, 'height': 54}, # Yaw
    'Joy_ZAxis': {'Type': 'Analogue', 'x': 564, 'y': 1402, 'width': 832, 'height': 54}, # Throttle
    'Joy_6': {'Type': 'Digital', 'x': 204, 'y': 1524, 'width': 992, 'height': 54}, # Flaps up
    'Joy_7': {'Type': 'Digital', 'x': 254, 'y': 1624, 'width': 992, 'height': 54}, # Flaps down
    'Joy_8': {'Type': 'Digital', 'x': 784, 'y': 1904, 'width': 992, 'height': 54}, # A1
    'Joy_9': {'Type': 'Digital', 'x': 2524, 'y': 1514, 'width': 992, 'height': 54}, # A2
    'Joy_10': {'Type': 'Digital', 'x': 2464, 'y': 1424, 'width': 992, 'height': 54}, # A3
    'Joy_11': {'Type': 'Digital', 'x': 1144, 'y': 1994, 'width': 992, 'height': 54}, # B1
    'Joy_12': {'Type': 'Digital', 'x': 2484, 'y': 1814, 'width': 992, 'height': 54}, # B2
    'Joy_13': {'Type': 'Digital', 'x': 2564, 'y': 1604, 'width': 992, 'height': 54}, # B3
    'Joy_14': {'Type': 'Digital', 'x': 2244, 'y': 1994, 'width': 992, 'height': 54}, # C1
    'Joy_15': {'Type': 'Digital', 'x': 2414, 'y': 1904, 'width': 992, 'height': 54}, # C2
    'Joy_16': {'Type': 'Digital', 'x': 2624, 'y': 1694, 'width': 992, 'height': 54}, # C3
    'Joy_17': {'Type': 'Digital', 'x': 2274, 'y': 1254, 'width': 1192, 'height': 54}, # Engine start
    'Joy_18': {'Type': 'Digital', 'x': 2204, 'y': 1114, 'width': 1192, 'height': 54}, # Eject
  },
}

keymap = {
  'Key_Comma': ',',
  'Key_LeftAlt': 'Left alt',
  'Key_LeftBracket': '[',
  'Key_LeftControl': 'Left ctrl',
  'Key_LeftShift': 'Left shift',
  'Key_Minus': '-',
  'Key_Plus': '+',
  'Key_Equals': '=',
  'Key_Period': '.',
  'Key_RightAlt': 'Right alt',
  'Key_RightBracket': ']',
  'Key_RightControl': 'Right ctrl',
  'Key_RightShift': 'Right shift',
  'Key_RightArrow': 'Right arrow',
  'Key_UpArrow': 'Up arrow',
  'Key_LeftArrow': 'Left arrow',
  'Key_DownArrow': 'Down arrow',
  'Key_LessThan': '<',
  'Key_GreaterThan': '>',
  'Key_LeftParenthesis': '(',
  'Key_RightParenthesis': ')',
  'Key_Numpad_0': 'Numpad 0',
  'Key_Numpad_1': 'Numpad 1',
  'Key_Numpad_2': 'Numpad 2',
  'Key_Numpad_3': 'Numpad 3',
  'Key_Numpad_4': 'Numpad 4',
  'Key_Numpad_5': 'Numpad 5',
  'Key_Numpad_6': 'Numpad 6',
  'Key_Numpad_7': 'Numpad 7',
  'Key_Numpad_8': 'Numpad 8',
  'Key_Numpad_9': 'Numpad 9',
  'Key_Numpad_Decimal': 'Numpad .',
  'Key_Numpad_Multiply': 'Numpad *',
  'Key_Numpad_Divide': 'Numpad /',
  'Key_Numpad_Add': 'Numpad +',
  'Key_Numpad_Subtract': 'Numpad -',
  'Key_Numpad_Enter': 'Numpad enter',
  'Key_PageDown': 'Pg Dn',
  'Key_PageUp': 'Pg Up',
  'Key_Grave': '`',
  'Key_BackSlash': '\\',
}

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

def parseBindings(runId, tree, displayGroups):
  items = {}
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

    modifiersInfo = xmlBinding.findall('Modifier')
    modifiersKey = 'Unmodified'
    if modifiersInfo:
      modifiersKey = ''
      for modifierInfo in modifiersInfo:
        modifierDevice = modifierInfo.get('Device')
        # Rewrite the device if this is a T16000M stick and we have a T16000M throttle
        if modifierDevice == 'T16000M' and hasT16000MThrottle == True:
          modifierDevice = 'T16000MFCS'
        modifierKey = '%s::%s::%s' % (modifierDevice, modifierInfo.get('DeviceIndex', 0), modifierInfo.get('Key'))
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
    item = items.get(itemKey)
    if item is None:
      item = {}
      item['Device'] = device
      item['DeviceIndex'] = deviceIndex
      # Get the unaltered key (might be prefixed with Neg_ or Pos_) and the mapped key
      item['BaseKey'] = xmlBinding.get('Key')
      item['Key'] = key
      item['Binds'] = {}
      items[itemKey] = item
    bind = item['Binds'].get(modifiersKey)
    if bind is None:
      bind = {}
      bind['Controls'] = OrderedDict()
      item['Binds'][modifiersKey] = bind
    bind['Controls'][controlName] = control

  return (items, modifiers, devices)

# Create a keyboard image from the template plus bindings
def createKeyboardImage(items, modifiers, source, imageDevices, biggestFontSize, displayGroups, runId, public):
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
      if public is True:
        context.push()
        context.font = getFontPath('SemiBold', 'Normal')
        context.font_size = 72
        context.text(x=966,y=252,body='binds/%s' % runId)
        context.pop()

      outputs = {}
      for group in displayGroups:
        outputs[group] = {}

      # Find the correct bindings and order them appropriately
      for key, item in items.items():
        itemDevice = item.get('Device')
        itemKey = item.get('Key')

        # Only show it if we are handling the appropriate image at this time
        if itemDevice not in imageDevices:
          continue

        for modifier, bind in item.get('Binds').items():
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
def createHOTASImage(items, modifiers, source, imageDevices, biggestFontSize, runId, public, styling, deviceIndex):
  global misconfigurationWarnings

  # Set up the path for our file
  config = Config(runId)
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
      if public is True:
        context.push()
        context.font = getFontPath('SemiBold', 'Normal')
        context.font_size = 72
        context.text(x=966,y=252,body='binds/%s' % runId)
        context.pop()

      for key, item in items.items():
        itemDevice = item.get('Device')
        itemDeviceIndex = int(item.get('DeviceIndex'))
        itemKey = item.get('Key')

        # Only show it if we are handling the appropriate image at this time
        if itemDevice not in imageDevices:
          continue

        # Only show it if we are handling the appropriate index at this time
        if itemDeviceIndex != deviceIndex: 
          continue

        # Find the details for the control
        texts = []
        hotasDetail = hotasDetails.get(itemDevice).get(itemKey)
        if hotasDetail is None:
          sys.stderr.write('%s: No control detail for %s\n' % (runId, key))
          continue

        # First obtain the modifiers if there are any
        for keyModifier in modifiers.get(key, []):
          if styling == 'Modifier':
            style = modifierStyles[keyModifier.get('Number') % 13]
          else:
            style = groupStyles.get('Modifier')
          texts.append({'Text': 'Modifier %s' % (keyModifier.get('Number')), 'Group': 'Modifier', 'Style': style})
        if '::Joy' in key:
          # Same again but for positive modifier
          for keyModifier in modifiers.get(key.replace('::Joy', '::Pos_Joy'), []):
            if styling == 'Modifier':
              style = modifierStyles[keyModifier.get('Number') % 13]
            else:
              style = groupStyles.get('Modifier')
            texts.append({'Text': 'Modifier %s' % (keyModifier.get('Number')), 'Group': 'Modifier', 'Style': style})
          # Same again but for negative modifier
          for keyModifier in modifiers.get(key.replace('::Joy', '::Neg_Joy'), []):
            if styling == 'Modifier':
              style = modifierStyles[keyModifier.get('Number') % 13]
            else:
              style = groupStyles.get('Modifier')
            texts.append({'Text': 'Modifier %s' % (keyModifier.get('Number')), 'Group': 'Modifier', 'Style': style})

        # Next obtain unmodified bindings
        for modifier, bind in item.get('Binds').items():
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
                  misconfigurationWarnings = '<h1>Misconfiguration detected</h1>You have one or more analogue controls configured incorrectly.  Please see <a href="https://forums.frontier.co.uk/showthread.php?t=209792">this thread</a> for details of the problem and how to correct it.<br/> <b>Your misconfigured controls:</b> <b>%s</b> ' % control['Name']
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
          for modifier, bind in item.get('Binds').items():
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
      for key, keyModifiers in modifiers.items():
        modifierTexts = []
        for keyModifier in keyModifiers:
          if keyModifier.get('Device') not in imageDevices:
            # We don't have an image for this device
            continue
          if int(keyModifier.get('DeviceIndex')) != deviceIndex:
            # This is not four our current device
            continue
          if '/' in key:
            # This is a logical modifier so ignore it
            continue
          if items.get(key) is not None or items.get(key.replace('::Pos_Joy', '::Joy')) is not None or items.get(key.replace('::Neg_Joy', '::Joy')) is not None:
            # This has already been handled because it has other binds
            continue

          modifierKey = keyModifier.get('Key')
          hotasDetail = hotasDetails.get(keyModifier.get('Device')).get(modifierKey)
          if hotasDetail is None:
            sys.stderr.write('%s: No location for %s\n' % (runId, key))
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

# Obtain form input and set up our variables
form = cgi.FieldStorage()

# TODO get rid if these globals
styling = 'None'
description = ''

blocks = form.getvalue('blocks')
wantList = form.getvalue('list')
if blocks is not None:
  mode = 'Blocks'
  try:
    createBlockImage(blocks)
  except KeyError:
    errors = '<h1>%s is not a supported controller.</h1>' % blocks
    xml = '<root></root>'
  createdImages = []
elif wantList is not None:
  mode = 'list'
else:
  replay = form.getvalue('replay')
  if replay is not None:
    mode = 'Replay'
    fileitem = {}
    runId = replay
    config = Config(runId)
    public = True
    try:
      bindsPath = config.pathWithSuffix('.binds')
      replayPath = config.pathWithSuffix('.replay')
      with codecs.open(str(bindsPath), 'r', 'utf-8') as fileInput:
        xml = fileInput.read()
      try:
        with replayPath.open("rb") as pickleFile:
          replayInfo = pickle.load(pickleFile)
          displayGroups =  replayInfo.get('displayGroups', ['Galaxy map', 'General', 'Head look', 'SRV', 'Ship', 'UI'])
          showKeyboard = replayInfo.get('showKeyboard', True)
          misconfigurationWarnings = replayInfo.get('misconfigurationWarnings', replayInfo.get('warnings', ''))
          deviceWarnings = replayInfo.get('deviceWarnings', '')
          unhandledDevicesWarnings = ''
          styling = replayInfo.get('styling', 'None')
          description = replayInfo.get('description', '')
          timestamp = replayInfo.get('timestamp')
          # devices = replayInfo['devices']
      except FileNotFoundError:
        displayGroups = ['Galaxy map', 'General', 'Head look', 'SRV', 'Ship', 'UI']
        showKeyboard = True
    except FileNotFoundError:
      errors = '<h1>Unknown configuration %s</h1>' % (runId)
      displayGroups = ['Galaxy map', 'General', 'Head look', 'SRV', 'Ship', 'UI']
      xml = '<root></root>'
  else:
    mode = 'Generate'
    config = Config.newRandom()
    config.makeDir()
    runId = config.name
    displayGroups = []
    public = False
    xml = form.getvalue('bindings')
    if xml is None or xml is b'':
      errors = '<h1>No bindings file supplied; please go back and select your binds file as per the instructions.</h1>'
      xml = '<root></root>'
    else:
      xml = xml.decode(encoding='utf-8')
      bindsPath = config.pathWithSuffix('.binds')
      with codecs.open(str(bindsPath), 'w', 'utf-8') as xmlOutput:
        xmlOutput.write(xml)
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
    if form.getvalue('public'):
      public = True
    if form.getvalue('keyboard'):
      showKeyboard = True
    else:
      showKeyboard = False

    if form.getvalue('styling') == 'group':
      styling = 'Group'
    if form.getvalue('styling') == 'category':
      styling = 'Category'
    if form.getvalue('styling') == 'modifier':
      styling = 'Modifier'
    description = form.getvalue('description')
    if description is None:
      description = ''

  # Obtain the bindings from the configuration file
  parser = etree.XMLParser(encoding='utf-8')
  try:
    tree = etree.fromstring(bytes(xml, 'utf-8'), parser=parser)
  except etree.XMLSyntaxError:
    errors = '<h1>Incorrect file supplied; please go back and select your binds file as per the instructions.<h1>'
    xml = '<root></root>'
    tree = etree.fromstring(bytes(xml, 'utf-8'), parser=parser)
  (items, modifiers, devices) = parseBindings(runId, tree, displayGroups)

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
          createHOTASImage(items, modifiers, supportedDevice['Template'], supportedDevice['HandledDevices'], 40, runId, public, styling, deviceIndex)
          createdImages.append('%s::%s' % (supportedDeviceKey, deviceIndex))
          for handledDevice in supportedDevice['HandledDevices']:
            alreadyHandledDevices.append('%s::%s' % (handledDevice, deviceIndex))

  if devices.get('Keyboard::0') is not None:
    keyboardItems = 0
    for  item in items.values():
      if item.get('Device') == 'Keyboard':
        for bind in item.get('Binds').values():
          keyboardItems = keyboardItems + len(bind.get('Controls'))
    if keyboardItems > 48:
      fontSize = 40 - int(((keyboardItems - 48)/20)*4)
      if fontSize < 24:
        fontSize = 24
    else:
      fontSize = 40
    createKeyboardImage(items, modifiers, 'keyboard', ['Keyboard'], fontSize, displayGroups, runId, public)
    createdImages.append('Keyboard')

  for deviceKey, device in devices.items():
    # Arduino Leonardo is used for head tracking so ignore it, along with vJoy (Tobii Eyex) and 16D00AEA (EDTracker)
    if device is None and deviceKey != 'Mouse::0' and deviceKey != 'ArduinoLeonardo::0' and deviceKey != 'vJoy::0' and deviceKey != 'vJoy::1' and deviceKey != '16D00AEA::0':
      sys.stderr.write('%s: found unsupported device %s\n' % (runId, deviceKey))
      if unhandledDevicesWarnings  == '':
        unhandledDevicesWarnings = '<h1>Unknown controller detected</h1>You have a device that is not supported at this time.  Please report details of your device by following the link at the bottom of this page supplying the reference "%s" and we will attempt to add support for it.' % runId
    if device is not None and 'ThrustMasterWarthogCombined' in device['HandledDevices'] and deviceWarnings == '':
      deviceWarnings = '<h2>Mapping Software Detected</h2>You are using the ThrustMaster TARGET software.  As a result it is possible that not all of the controls will show up.  If you have missing controls then you should remove the mapping from TARGET and map them using Elite\'s own configuration UI.'
    
  if len(createdImages) == 0 and misconfigurationWarnings == '' and unhandledDevicesWarnings == '' and errors == '':
    errors = '<h1>The file supplied does not have any bindings for a supported HOTAS or keyboard.</h1>'

# Save variables for later replays
if mode == 'Generate':
  replayInfo = {}
  replayInfo['displayGroups'] = displayGroups
  replayInfo['showKeyboard'] = showKeyboard
  replayInfo['misconfigurationWarnings'] = misconfigurationWarnings
  replayInfo['unhandledDevicesWarnings'] = unhandledDevicesWarnings
  replayInfo['deviceWarnings'] = deviceWarnings
  replayInfo['styling'] = styling
  replayInfo['description'] = description
  replayInfo['timestamp'] = datetime.datetime.now(datetime.timezone.utc)
  replayInfo['devices'] = devices
  config = Config(runId)
  replayPath = config.pathWithSuffix('.replay')
  with replayPath.open('wb') as pickleFile:
    pickle.dump(replayInfo, pickleFile)

def printList():
  print('<p>Full search support is coming soon</p>')
  objs = Config.allConfigs()
  print('<table>')
  print('''
    <tr>
      <th>Descripton</th>
      <th>Date</th>
    </tr>
  ''')
  for obj in objs:
    config = Config(obj['runID'])
    refcardURL = config.refcardURL()
    dateStr = obj['timestamp'].ctime()
    name = obj['description']
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
    </tr>
    ''') % (refcardURL, name, dateStr)
  print ('</table>')

def printBody():
  if mode is 'list':
    printList()
    return
  if unhandledDevicesWarnings != '':
    print('%s<br/>' % unhandledDevicesWarnings)
  if misconfigurationWarnings != '':
    print('%s<br/>' % misconfigurationWarnings)
  if deviceWarnings != '':
    print('%s<br/>' % deviceWarnings)
  if errors != '':
    print('%s<br/>' % errors)
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
    if blocks is not None:
      print('<img width="100%%" src="../configs/%s/%s.jpg"/><br/>' % (supportedDevices[blocks]['Template'][:2], supportedDevices[blocks]['Template']))
    if blocks is None and public is True:
      linkURL = config.refcardURL()
      bindsURL = config.bindsURL()
      print('<p/>Link directly to this page with the URL <a href="%s">%s</a>' % (linkURL, linkURL))
      print('<p/>You can download the custom binds file for the configuration shown above at <a href="%s">%s</a>.  Replace your existing custom binds file with this file to use these controls.' % (bindsURL, bindsURL))
  print('<p/>')

def printSupportPara():
  print('<p>Please direct questions and suggestions and support requests to <a href="https://forums.frontier.co.uk/showthread.php?t=212866">the thread on the official Elite: Dangerous forums</a>.</p>')

def printHTML():
  print('Content-Type: text/html')
  print()
  print('<html>')
  print('<head><title>Elite: Dangerous bindings</title></head>')
  print('<body>')
  printBody()
  print('<p>Please direct questions and suggestions and support requests to <a href="https://forums.frontier.co.uk/showthread.php?t=212866">the thread on the official Elite: Dangerous forums</a>.')
  print('</body>')
  print('</html>')

printHTML()

