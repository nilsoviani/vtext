import cx_Freeze
import sys
import os

os.environ['TCL_LIBRARY'] = "C:\\Program Files\\Python36\\tcl\\tcl8.6" # change the directory if your python files are in different place
os.environ['TK_LIBRARY'] = "C:\\Program Files\\Python36\\tcl\\tk8.6"   # change the directory if your python files are in different place

base = None

if sys.platform == 'win32':
	base = "Win32GUI"

executables = [cx_Freeze.Executable("Vtext.py", base=base, icon="Vtext.ico")]

cx_Freeze.setup(
	name = "Vtext",
	options = {"build_exe": {"packages":["tkinter"], "include_files":["vtext.ico", "vtext.png", "python_logo.png"]}},
	version = "1.0",
	description = "Vtext",
	executables = executables
	)
