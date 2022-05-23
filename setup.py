
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
build_options = {'packages': [], 'excludes': []}

import sys
base = 'Win32GUI' if sys.platform=='win32' else None

executables = [
    Executable('src/main.py', base=base, target_name = 'CFModpackImporter')
]

# oldcwd = os.getcwd()
# try:
#     os.chdir(os.path.join(os.path.dirname(__file__), "src"))
    
# finally:
#     os.chdir(oldcwd)

setup(name='CFModpackImporter',
        version = '1.0',
        description = '',
        options = {'build_exe': build_options},
        executables = executables)
