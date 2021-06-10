#!/bin/zsh
# encoding: utf-8

# Made by Lux
# https://github.com/lifeunexpected

# Scripts are based on code by:
# https://groups.google.com/forum/#!topic/munki-dev/FADUXPWJeds - Michal Moravec
# https://github.com/rednoah/notarize-app/blob/master/notarize-app - rednoah
# https://github.com/munki/munki/tree/master/code/tools - Greg Neagle
# https://stackoverflow.com/a/57083245 - Perry

# 1: Copy script to Munki folder
# 2: In terminal "cd FolderWheremunki" git repo is located
# 3: run script
# 4 Enter Password when asked for it

# Tip: if you get “You must first sign the relevant contracts online. (1048)” error
# Go to Apple.developer.com and sign in with the account you are trying to notarize the app with and agree to the updated license agreement.

# Defaults do NOT Change!
MUNKIROOT="."
# Convert to absolute path.
MUNKIROOT=$(cd "$MUNKIROOT"; pwd)
OUTPUTDIR="$(pwd)"

# Change what is needed below this line
# _____________________
# Change DevApp to your personal/company Developer ID Application Name + ID number
DevApp=""
# Change DevInst to your personal/company Developer ID Installer Name + ID number
DevInst=""
# Change Bundle_ID if you are using a custom one, default is "com.googlecode.munki"
BUNDLE_ID="com.googlecode.munki"



$MUNKIROOT/code/tools/build_python_framework.sh

find $MUNKIROOT/Python.framework/Versions/3.9/lib/ -type f -perm -u=x -exec codesign --force --deep --verbose -s "$DevApp" {} \;
find $MUNKIROOT/Python.framework/Versions/3.9/bin/ -type f -perm -u=x -exec codesign --force --deep --verbose -s "$DevApp" {} \;

find $MUNKIROOT/Python.framework/Versions/3.9/lib/ -type f -name "*dylib" -exec codesign --force --deep --verbose -s "$DevApp" {} \;
find $MUNKIROOT/Python.framework/Versions/3.9/lib/ -type f -name "*so" -exec codesign --force --deep --verbose -s "$DevApp" {} \;

/usr/libexec/PlistBuddy -c "Add :com.apple.security.cs.allow-unsigned-executable-memory bool true" $MUNKIROOT/entitlements.plist

codesign --force --options runtime --entitlements $MUNKIROOT/entitlements.plist --deep --verbose -s "$DevApp" $MUNKIROOT/Python.framework/Versions/3.9/Resources/Python.app/

codesign --force --options runtime --entitlements $MUNKIROOT/entitlements.plist --deep --verbose -s "$DevApp" $MUNKIROOT/Python.framework/Versions/3.9/bin/python3.9
codesign --force --deep --verbose -s  "$DevApp" $MUNKIROOT/Python.framework

# Creating munkitools.pkg

sudo $MUNKIROOT/code/tools/make_munki_mpkg.sh -i "$BUNDLE_ID" -o "$OUTPUTDIR"
