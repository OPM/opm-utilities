# ======================================================================================================================
#
"""OPM_COMMON.py - Common Utility Functions

This module contains common utility functions used by other modules in OPMRUN in order to avoid code duplication.

Notes:
------
Only Python 3 is currently supported and tested Python2 support has been depreciated. The following standard module
libraries are used in this version.

(1) PySimpleGUI
(2) tkinter as tk

Program Documentation
--------------------
2020-04.01 - Initial release

Copyright (C) 2018-2020 Equinox International Petroleum Consultants Pte Ltd.

Author  : David Baxendale
          david.baxendale@eipc.co
Version : 2020-04.01
Date    : 27-Feb-2020
"""
# ----------------------------------------------------------------------------------------------------------------------
# 3456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890
#        1         2         3         4         5         6         7         8         9         0         1         2
#        0         0         0         0         0         0         0         0         0         1         1         1
# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
# Import Modules Section
# ----------------------------------------------------------------------------------------------------------------------
import os
import sys
#
# Check for Python Version and Import Required Non-Standard Modules
#
if sys.version_info[0] == 2:
    exit('OPMRUN Only Works with Python 3, Python 2 Support is Depreciated')

try:
    import PySimpleGUI as sg
except ImportError:
    exit('OPMRUN Cannot Import PySimpleGUI - Please Install Using pip3')

try:
    from pathlib import Path
except ImportError:
    exit('OPMRUN Cannot Import Path from pathlib module - Please Install Using pip3')

try:
    import tkinter as tk
except ImportError:
    exit('OPMRUN Cannot Import tkinter - Please Install Using pip3')

# ----------------------------------------------------------------------------------------------------------------------
# Define Modules Section
# ----------------------------------------------------------------------------------------------------------------------
def copy_to_clipboard(input):
    """Copies Text to the Clipboard

    Copies the input text to the clipboard for pasting into another application

    Parameters
    ----------
    input: str
        Input text to be copied to the clipboard

    Returns
    ------
    None
    """
    #
    # Define Tk Window and Prevent from Showing
    #
    root= tk.Tk()
    root.withdraw()
    #
    # Clear Clipboard and Append Text
    #
    root.clipboard_clear()
    root.clipboard_append(input)

def opm_initialize():
    """ Initialized OPMRUN

    The function initializes OPMRUN environment and should be call for all sub-modules to ensure a consistent user
    interface.

    Parameters
    ----------
    None

    Returns
    -------
    None

    """

    #
    # OPMRUN ICON Base64 Encoded PNG File
    #
    opmicon  = Path(str(os.path.dirname( __file__ )) + '/opmrun.png')
    if not os.path.isfile(opmicon):
        sg.PopupError('Cannot Find ICON File: \n \n' + str(opmicon) + '\n \n' + 'Program will Continue',
                      no_titlebar=True, grab_anywhere=True, keep_on_top=True)
        opmicon = None
    #
    # Set PySimpleGUI Defaults
    #
    sg.SetOptions(icon=opmicon,
            button_color=('green','white'),
            element_size=(None,None),
            margins=(None,None),
            element_padding=(None,None),
            auto_size_text=None,
            auto_size_buttons=None,
            font=None,
            border_width=1,
            slider_border_width=None,
            slider_relief=None,
            slider_orientation=None,
            autoclose_time=5,
            message_box_line_width=None,
            progress_meter_border_depth=None,
            progress_meter_style=None,
            progress_meter_relief=None,
            progress_meter_color=None,
            progress_meter_size=None,
            text_justification=None,
            text_color='black',
            background_color='white',
            element_background_color='white',
            text_element_background_color='white',
            input_elements_background_color=None ,
            element_text_color='green',
            input_text_color=None,
            scrollbar_color=None,
            debug_win_size=(None,None),
            window_location=(None,None),
            tooltip_time = None
            )
#
# Define OPMRUN Modules for Stand Alone Running
#
def opm_popup(opmvers, text,nrow):
    """Display Text Message in a Display Window

    Displays a text message in a multiline popup. Normally used for displaying help information, but any text string
    can be used.

    Parameters
    ----------
    opmvers : str
        Version information to be displayed
    text : str
        Text message to be displayed
    nrow : int
        The number of initial rows to be displayed, after which scrolling is used to the display the rest of the
        message.

    Returns
    -------
    None
    """

    layout1 = [ [sg.Multiline(text, size=(80,nrow), background_color='white', text_color='darkgreen')],
                  [sg.CloseButton('OK')] ]
    window1 = sg.Window('OPMRUN - Flow Job Scheduler ' + opmvers, layout=layout1)
    (button, values) = window1.Read()
    return()

# ======================================================================================================================
# End of OPMKEYW
# ======================================================================================================================