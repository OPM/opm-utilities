# ======================================================================================================================
#
"""OPM_COMMON.py - Common Utility Functions

This module contains common utility functions used by other modules in OPMRUN in order to avoid code duplication.

Notes:
------
Only Python 3 is currently supported and tested Python2 support has been depreciated. The following standard module
libraries are used in this version.

import datetime
import getpass
import pandas as pd
import platform
import PySimpleGUI as sg
import re
import tkinter as tk
from pathlib import Path

Program Documentation
--------------------
2020-04.04 - Refactored code to be more compact as import checks are done in the main routine.
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
#
# ----------------------------------------------------------------------------------------------------------------------
# Import Modules Section
# ----------------------------------------------------------------------------------------------------------------------
import datetime
import getpass
import platform
import re
import subprocess
import sys
import tkinter as tk
from pathlib import Path

import airspeed
import pandas as pd
import psutil
import pyDOE2
import PySimpleGUI as sg


# ----------------------------------------------------------------------------------------------------------------------
# Define Modules Section
# ----------------------------------------------------------------------------------------------------------------------
def convert_string(string, option):
    """Convert a String from One Format to Another

    The regular expression looks for letters that are either at the beginning of the string,
    or preceded by an underscore. The given letter is captured.
    Each of those occurrences (underscore + letter) is replaced by the uppercase version of
    the found letter.

    Parameters
    ----------
    string : str
        String to be converted
    option :str
        String conversion format

    Returns
    -------
    Converted String
    """

    if option  == 'snake2camel':
        return re.sub(r'(?:^|_)([a-z])', lambda x: x.group(1).upper(), string)
    '''
    This method works exactly as snake2camel, except that the first character is not
    taken into account for capitalization.
    '''
    if option == 'snake2camelback':
        return re.sub(r'_([a-z])', lambda x: x.group(1).upper(), string)
    '''
    The regular expression capture every capital letters in the given string.
    For each of these groups, the character found is replaced by an underscore,
    followed by the lowercase version of the character.
    '''
    if option  == 'camel2snake':
        return string[0].lower() + re.sub(r'(?!^)[A-Z]', lambda x: '_' + x.group(0).lower(), string[1:])
    '''
    The conversion is very similar to the one performed in camelback2snake,
    except that the first character is processed out of the regular expression.
    '''
    if option  == 'camelback2snake':
        return re.sub(r'[A-Z]', lambda x: '_' + x.group(0).lower(), string)
    '''
    The regular expression capture every capital letters in the given string.
    For each of these groups, the character found is replaced by a '-',
    followed by the lowercase version of the character.
    '''
    if option  == 'camel2flow':
        return string[0].lower() + re.sub(r'(?!^)[A-Z]', lambda x: '-' + x.group(0).lower(), string[1:])
    '''
    The conversion is very similar to the one performed in camelback2snake,
    except that the first character is processed out of the regular expression.
    '''
    if option  == 'camelback2flow':
        return re.sub(r'[A-Z]', lambda x: '-' + x.group(0).lower(), string)


def copy_to_clipboard(inputs):
    """Copies Text to the Clipboard

    Copies the input text to the clipboard for pasting into another application

    Parameters
    ----------
    inputs: str
        Input text to be copied to the clipboard

    Returns
    ------
    None
    """
    #
    # Define Tk Window and Prevent from Showing
    #
    root = tk.Tk()
    root.withdraw()
    #
    # Clear Clipboard and Append Text
    #
    root.clipboard_clear()
    root.clipboard_append(inputs)


def get_time():
    """Gets the Current Time and Data

    Gets the current time and date and returns the value in the standard OPMRUN format

    Parameters
    ----------


    Returns
    -------
    time : str
        The current date and time in the standard OPMRUN format
    """

    time = datetime.datetime.now()
    time = str(time.strftime('%Y-%m-%d %H:%M:%S'))
    return time


def kill_job(mesg, pid):
    """ Kill a Job Process and All It's Children Processes

    The function initializes OPMRUN environment and should be call for all sub-modules to ensure a consistent user
    interface.

    Parameters
    ----------
    mesg :str
        Process message to be be displayed if set to 'None then no confirmation message is displayed.
    pid : int
        Main process to be killed.

    Returns
    -------
    kill : bool
        Set to True to kill job processes, other wise False.
    killed : list
        List of processes killed.

    """
    #
    # Get Child Processes and Kill if Requested
    #
    kill    = False
    killed  = []
    if mesg != 'None':
        killjob = sg.popup_yes_no(mesg + 'pid: ' + str(pid), no_titlebar=True, grab_anywhere=True, keep_on_top=True)
    else:
        killjob = 'Yes'

    if killjob == 'Yes':
        kill = True
        try:
            process = psutil.Process(pid)
            for proc in process.children(recursive=True):
                killed.append(proc.pid)
                proc.kill()

            killed.append(process.pid)
            process.kill()

        except psutil.Error:
            pass

    return kill, killed


def opm_initialize():
    """ Initialized OPMRUN

    The function initializes OPMRUN environment and should be call for all sub-modules to ensure a consistent user
    interface.

    Parameters
    ----------


    Returns
    -------
    None

    """
    #
    # OPMRUN ICON Base64 Encoded PNG File
    #
    opmicon = Path(Path(__file__).parent.absolute() / 'opmrun.png')
    if not Path(opmicon).is_file():
        sg.popup_error('Cannot Find ICON File: \n \n' + str(opmicon) + '\n \n' + 'Program will Continue',
                      no_titlebar=True, grab_anywhere=True, keep_on_top=True)
        opmicon = None
    #
    # Set PySimpleGUI Defaults
    #
    sg.SetOptions(icon=opmicon,
                  button_color=('green', 'white'),
                  element_size=(None, None),
                  margins=(None, None),
                  element_padding=(None, None),
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
                  input_elements_background_color=None,
                  element_text_color='green',
                  input_text_color=None,
                  scrollbar_color=None,
                  debug_win_size=(None, None),
                  window_location=(None, None),
                  tooltip_time=None
                  )


def opm_popup(title, text, nrow):
    """Display Text Message in a Display Window

    Displays a text message in a multiline popup. Normally used for displaying help information, but any text string
    can be used.

    Parameters
    ----------
    title : str
        Title text message to be displayed
    text : str
        Text message to be displayed
    nrow : int
        The number of initial rows to be displayed, after which scrolling is used to the display the rest of the
        message.

    Returns
    -------
    None
    """

    layout1 = [[sg.Multiline(text, size=(80, nrow), background_color='white', text_color='darkgreen')],
               [sg.CloseButton('OK')]]
    window1 = sg.Window('OPMRUN - Flow Job Scheduler: ' + title, layout=layout1)
    window1.Read()
    return ()


def opm_startup(opmvers, opmsys1, opmlog1):
    """OPMRUN Startup Setup System Variables and File Creation

    Sets up the various system variables in the opmsys dictionary which is then routine to the global version of
    opmsys. The function then checks for the users OPM home directory and if not available creates it. Finally, the
    function opens the log file and writes a header to the file.

    Parameters
    ----------
    opmvers :str
        OPMRUN version string
    opmsys1 : dict
        Contains a dictionary list of all OPMRUN System parameters
    opmlog1 : tuple
        OPM log file pointer set to None in calling routine

    Returns
    -------
    opmsys1 : dict
        Updated dictionary list of all OPMRUN System parameters

    opmlog1 : tuple
        OPM log file pointer
    """

    opmsys1             = platform.uname()._asdict()
    opmsys1['python'  ] = platform.python_version()
    opmsys1['opmvers' ] = opmvers
    #
    # Get OPM Flow Version
    #
    opmflow = run_command('flow --version')
    opmsys1['opmflow' ] = opmflow.rstrip()
    opmsys1['opmgui'  ] = 'PySimpleGUI - ' + str(sg.version)
    opmsys1['airspeed'] = 'airspeed - ' + 'No version attribute'  # str(airspeed.__version__)
    opmsys1['pandas'  ] = 'pandas - ' + str(pd.__version__)
    opmsys1['psutil'  ] = 'psutil - ' + str(psutil.__version__)
    opmsys1['pyDOE2'  ] = 'pyDOE2 - ' + 'No version attribute'    # str(pyDOE2.__version__)
    #
    # Determine If Running in Exe or Script Mode
    #
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        opmsys1['opmmode' ] = 'Exe'
    else:
        opmsys1['opmmode' ] = 'Script'
    #
    opmsys1['opmpath' ] = Path().absolute()
    opmsys1['opmhome' ] = Path.home() / 'OPM'
    opmsys1['opmini'  ] = Path(opmsys1['opmhome'] / 'OPMRUN.ini')
    opmsys1['opmlog'  ] = Path(opmsys1['opmhome'] / 'OPMRUN.log')
    opmsys1['opmjob'  ] = Path(opmsys1['opmhome'] / 'OPMRUN.job')
    opmsys1['opmparam'] = Path(opmsys1['opmhome'] / 'OPMRUN.param')
    opmsys1['opmuser' ] = getpass.getuser()
    #
    # Create OPM Directory if Missing
    #
    if not opmsys1['opmhome'].is_dir():
        try:
            opmsys1['opmhome'].mkdir()
        except OSError:
            sg.popup_error('Cannot Create: ' + str(opmsys1['opmhome']) + ' Directory \n  Will try and continue',
                          no_titlebar=True, grab_anywhere=True, keep_on_top=True)
    #
    # Open Log File and Write Header
    #
    try:
        opmlog1 = open(opmsys1['opmlog'], 'w')
        opmlog1.write('# \n')
        opmlog1.write('# OPMRUN Log File \n')
        opmlog1.write('# \n')
        opmlog1.write('# File Name   : ' + str(opmsys1['opmlog']) + '\n')
        opmlog1.write('# Created By  : ' + str(opmsys1['opmuser']) + '\n')
        opmlog1.write('# Date Created: ' + get_time()  + '\n')
        opmlog1.write('# \n')
        for item in opmsys1:
            opmlog1.write('{}: OPMSYS  Key: {:<16} , Value : {:} \n'.format(get_time(), item, opmsys1[item]))
            opmlog1.flush()

    except OSError:
        sg.popup_error('Error Opening Log File \n \n' + 'Will try to continue',
                      no_titlebar=True, grab_anywhere=True, keep_on_top=True)
        pass

    return opmsys1, opmlog1


def opm_prtdict(dictname, dictvar, option='debug'):
    """OPMRUN Print Python Dictionary

    Prints a  Python dictionary in tabular form

    Parameters
    ----------
    dictname : str
        Variable name of the dictionary to be printed
    dictvar : dict
        Dictionary to be printed
    option : str
        Print option set to 'debug' for sg.Print, otherwise standard print

    Returns
    -------
    None
    """

    if option == 'debug':
        sg.Print('Print Dictionary Variable Start: ' + dictname)
        sg.Print(pd.DataFrame.from_dict(dictvar, orient='index', columns=['Value']))
        sg.Print('Print Dictionary Variable End: ' + dictname)
    else:
        print('Print Dictionary Variable Start: ' + dictname)
        for item in dictvar:
            print('{}: Key: {:<10} , Value : {:}'.format(dictname, item, dictvar[item]))
        print('Print Dictionary Variable End: ' + dictname)

    return


def remove_ansii_escape_codes(linein):
    """Remove ASCII Escape Codes

    Removes ascii escape code sequence from a string, based on  Martijn Pieters's answer with Jeff's regexp and
    Édouard Lopez answer on stack overflow
    https://stackoverflow.com/questions/14693701/how-can-i-remove-the-ansi-escape-sequences-from-a-string-in-python

    Parameters
    ----------
    linein : str
        String to have the ascii escape sequences removed.

    Returns
    -------
    lineout: str
        Returns line without the ascii escape codes
    """

    ansi_escape = re.compile(r'(?:\x1B[@-_]|[\x80-\x9F])[0-?]*[ -/]*[@-~]')
    lineout     = ansi_escape.sub('', linein)
    return lineout


def run_command(command, timeout=None, window=None):
    """Run Shell Command

    Runs a shell command as a sub-process and displays the output in a pre-declared window.

    Parameters
    ----------
    command : str
        The command to execute
    timeout : real
        Timeout for command execution
    window : PySimpleGUI window
        The PySimpleGUI window that the output is going to (needed to do refresh on)

    Returns
    -------
    exitcode : int
        Return code from the sub-process command
    """
    #
    # Run Process with No Output
    #
    if window == None:
        try:
            jobproc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                       universal_newlines=True)
            out, err = jobproc.communicate()

        except Exception:
            sg.popup_error('Subprocess Call Error: \n \n' + str(command) + '\n \n' +
                           'OUT:' + str(out) + 'ERR:' + str(err) + '\n',
                           no_titlebar=True, grab_anywhere=True, keep_on_top=True)
            pass
        #
        # Process Complete - Get Exit Code
        #
        returncode = jobproc.wait(timeout)
        if jobproc.returncode > 1:
            sg.popup_error('Subprocess Call Error: \n \n' + str(command) + '\n \n' +
                           'Return Code:' + str(returncode) + '\n',
                           no_titlebar=True, grab_anywhere=True, keep_on_top=True)
        return out
    #
    # Run Process with Realtime Output to Window
    #
    else:
        try:
            jobproc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                       bufsize=1, universal_newlines=True)
            for line in jobproc.stdout:
                line = line.rstrip()
                window['_outlog1_'].print(line)
                window.refresh()

        except Exception as err:
            window['_outlog1_'].print(err, type(err))
            pass
        #
        # Process Complete - Get Exit Code
        #
        returncode = jobproc.wait(timeout)
        if jobproc.returncode > 1:
            window['_outlog1_'].print('Exit Code ' + str(returncode))
        return returncode

# ======================================================================================================================
# End of OPM_COMMON.PY
# ======================================================================================================================
