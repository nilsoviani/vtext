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
	options = {"build_exe": {"packages":["tkinter"], "include_files":["Vtext.ico", "vtext_logo_187x187.gif", "python_logo.gif"]}},
	version = "1.0",
	description = "Vtext",
	executables = executables
	)