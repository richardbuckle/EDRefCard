## 1.3
* Added support for VKB Gladiator Left and Right sticks, courtesy of awerschlan and esabouraud.
* Added support for VPC Alpha Left and Right grips, courtesy of Slion.
* Added searching by controller type, courtesy of alewando.
* Added support for Odyssey's "On Foot" bindings.

## 1.2.8
* Added support for VKB Kosmosima SCG Left and Right grips, courtesy of ajhewett.
* Handled invalid keyboard bindings of the form `Device="Keyboard" Key=""`

## 1.2.7
* Added support for Thrustmaster Hotas Cougar.

## 1.2.6
* Added binding for Store Toggle Preview.

## 1.2.5
* Added bindings for the Store Camera.
* Revised the color palette.

## 1.2.4

* Amended the VKB Gladiator bindings: my thanks to KellyR (CMDR Analee Winston) for kicking my behind on this an providing corroborating data.
* Added a new URL `https://edrefcard/devices` listing all supported devices by primary name and linking to:
  * New endpoints `https://edrefcard//device/xxx` that show the given device's button names in rectangles shaded in light green and outlined in red, to assist with (a) debugging button mappings and (b) aligning the rectangles pixel-perfect.
* Tweaked CSS styling and column width settings for `/list` and `/devices` to make the table neater. I'll be the first to admit this isn't my strong suit.
* Reduced the maximum input length for the "description" field to 190 characters in light of the above.
* Updated the forum thread URL.

## 1.2.3

* Restored caching of rendered JPEGs to one day now that we have more disk space.

## 1.2.2

* Improved the error reporting when there is an error parsing the bindings file.

## 1.2.1

* Added the new bindings introduced in Chapter 4 beta 3.
* Updated the code that prevents redundant specialisations from being shown on the same card (e.g. when GalMap pitch axis is the same as your regular pitch axis). This should make cards more concise w/o loss of clarity.

## 1.2

* Command names are now in Title Case and some have been abbreviated.
* The keyboard chart makes more use of symbols to identify the keys.
* The Galaxy map controls now say "GalMap" rather than "Camera".
* Added support for Dual Virpil VPC WarBRD DELTA joysticks.
* Added support for Saitek X45 HOTAS.

## 1.1

* Blocking "spammy" descriptions is as those starting with punctuation.

## 1.0.8

* Added bindings introduced in Chapter 4, notable the FSS scanner.

## 1.0.7

* Fixed errors with non-ASCII file encodings. Should now be fully Unicode.

## 1.0.6

* The list view is now sorted in a case-insensitive manner.
* The home page now correctly uses https to access its style sheet from Google APIs. Thanks to eeisenhart.

