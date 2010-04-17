#!/usr/bin/env python

from distutils.core import setup

import py2exe

setup(
    windows = [
        {
            "script": "intro.py",
            "icon_resources": [(1, "images/window_icon.ico")]
        }
    ],
    options = {"py2exe": {"packages": ["encodings"]}}

)

#excludes = ["pywin", "pywin.debugger", "pywin.debugger.dbgcon",
#            "pywin.dialogs", "pywin.dialogs.list",
#            "Tkconstants","Tkinter","tcl"
#            ]
#
#
#"_imagingtk", "PIL._imagingtk", "ImageTk", "PIL.ImageTk", "FixTk"