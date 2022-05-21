#!/usr/bin/env python3

import sys
import re


def replaceInFileRegex(filename, a, b):
    # Read in the file
    with open(filename, 'r') as file :
        filedata = file.read()

    # Replace the target string
    filedata = re.sub(a, b, filedata, re.MULTILINE)

    # Write the file out again
    with open(filename, 'w') as file:
        file.write(filedata)

if len(sys.argv) != 2:
    print("Usage: " + sys.argv[0] + " VERSION_NAME")
    exit(1)

# Change in resource used by java app
with open("res/version.txt", 'w') as file:
        file.write(sys.argv[1])

# replaceInFileRegex("packaging/windows/win_installer.iss", "#define MyAppVersion \".*\"", "#define MyAppVersion \"" + sys.argv[1] + "\"")

# replaceInFileRegex("macos_resources/Info.plist", "<key>CFBundleShortVersionString</key>\n\s<string>.*</string>", "<key>CFBundleShortVersionString</key>\n\t<string>" + sys.argv[1] + "</string>")
# replaceInFileRegex("macos_resources/Info.plist", "<key>CFBundleVersion</key>\n\s<string>.*</string>", "<key>CFBundleVersion</key>\n\t<string>" + sys.argv[1] + "</string>")

# replaceInFileRegex("packaging/linux_pyinstaller/deb_control", "Version: .*\n", "Version: " + sys.argv[1] + "\n")
# replaceInFileRegex("packaging/linux_source/deb_control", "Version: .*\n", "Version: " + sys.argv[1] + "\n")


# replaceInFileRegex("linux_resources/PKGBUILD", "pkgver=.*\n", "pkgver=" + sys.argv[1] + "\n")
# replaceInFileRegex("linux_resources/PKGBUILD", "pkgrel=.*\n", "pkgrel=" + sys.argv[1].replace(".", "") + "\n")
