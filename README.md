# vtext
A simple text editor coded with Python 3, and tkinter library for GUI

The libraries used in Vtext.py that you'll need to install are:

tkFontChooser

win32clipboard

For tkfontchooser use the content at https://pypi.python.org/pypi/tkfontchooser 

Or install it using pip: pip install tkfontchooser

For win32clipboard use the content at: https://sourceforge.net/projects/pywin32/files/pywin32/

Or install it using pip: pip install pywin32

===== EXECUTABLE =====

You need to install cx_Freeze if you want to make a .exe or .msi of this project
for this, follow the steps in https://anthony-tuininga.github.io/cx_Freeze/ you can install it through pip or download the file
 
This pocess is very explained in this site: https://pythonprogramming.net/converting-tkinter-to-exe-with-cx-freeze/
If you have issues with TCL_LIBRARY and TK_LIBRARY the file setup.py has these lines added 
you could need to change the directoy where python is installed

===== USE THIS FILES FOR TESTS ===== 

For using the capabilities of this app you could use the .txt files attached in this repository (romeo.txt and mbox.txt)
