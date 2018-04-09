# vtext
A simple text editor coded with Python 3, and tkinter library for GUI

The libraries used in Vtext.py are:

import tkinter as tk
from tkinter import StringVar, IntVar, ttk, filedialog as FileDialog, messagebox as MessageBox
import tkinter.colorchooser
from tkFontChooser import askfont
import datetime
import win32clipboard
import win32api
import win32print
import tempfile
import os, sys

For tkfontchooser use the content at https://pypi.python.org/pypi/tkfontchooser for install it using pip

You need to install cx_Freeze if you want to make a .exe or .msi of this project
for this, follow the steps in https://anthony-tuininga.github.io/cx_Freeze/ you can install it through pip or download the file
 
This pocess is very explained in this site: https://pythonprogramming.net/converting-tkinter-to-exe-with-cx-freeze/
If you have issues with TCL_LIBRARY and TK_LIBRARY the file setup.py has these lines added 
you could need to change the directoy where python is installed

For using the capabilities of this app you could use the .txt files attached in this repository (romeo.txt and mbox.txt)
