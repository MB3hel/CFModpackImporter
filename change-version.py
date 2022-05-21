#
# Copyright 2022 Marcus Behel
# 
# Redistribution and use in source and binary forms, with or without 
# modification, are permitted provided that the following conditions are met:

# 1. Redistributions of source code must retain the above copyright notice, 
# this list of conditions and the following disclaimer.

# 2. Redistributions in binary form must reproduce the above copyright notice, 
# this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.

# 3. Neither the name of the copyright holder nor the names of its contributors 
# may be used to endorse or promote products derived from this software without specific prior written permission.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" 
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE 
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE 
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE 
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR 
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF 
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS 
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN 
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) 
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF 
# THE POSSIBILITY OF SUCH DAMAGE.
#


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
