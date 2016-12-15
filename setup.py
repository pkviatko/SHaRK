import sys
from cx_Freeze import setup, Executable

build_exe_options = {"packages": ["os", "scipy", "tempfile"], "excludes": ["tkinter"], "includes": ["func", "tempfile"],
                     "include_files": [r"pic", "syn.csv", "func.py",
                                       "window.ui", "stats.ui", "muscle.exe",
                                       "pref.ui", "about.ui"]}

base = None
#if sys.platform == "win32":
#    base = "Win32GUI"
#elif sys.platform == "win64":
#    base = "Win64GUI"

setup(name="SHaRK",
      version="0.9.1",
      description="Sequence Handling and Resampling Kit",
      options={"build_exe": build_exe_options},
      executables=[Executable("ui.py", base=base, targetName="SHaRK.exe", icon=r"pic\\256x256_BlackLogo.ico")])
