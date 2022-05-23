
import os
import sys

# Add src directory to PYTHONPATH so cxfreeze can find modules in that folder imported by main.py
# if not "PYTHONPATH" in os.environ:
#     os.environ["PYTHONPATH"] = os.path.join(os.path.dirname(__file__), "src")
# else:
#     os.environ["PYTHONPATH"] = os.environ["PYTHONPATH"] + os.pathsep + os.path.join(os.path.dirname(__file__), "src")
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need
# fine tuning.
build_options = {
    'packages': [], 
    'excludes': [],
    'include_files': ['res/icon.png']
}

import sys
base = 'Win32GUI' if sys.platform=='win32' else None

executables = [
    Executable('src/main.py', base=base, target_name = 'CFModpackImporter', icon='res/icon.png')
]

version = "unknown"
versionfilepath = os.path.join(os.path.dirname(__file__), "res", "version.txt")
if os.path.exists(versionfilepath):
    with open(versionfilepath, "r") as versionfile:
        version = versionfile.readline().strip()

setup(name='CFModpackImporter',
        version = version,
        description = 'Proof of Concept tool to download curseforge modpacks without using the API.',
        options = {'build_exe': build_options},
        author = 'Marcus Behel',
        author_email = 'marcus.behel@mindspring.com',
        executables = executables)
