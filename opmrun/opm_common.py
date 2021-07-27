# ======================================================================================================================
#
"""OPM_COMMON.py - Common Utility Functions

This module contains common utility functions used by other modules in OPMRUN in order to avoid code duplication,
togther with other useful routines.

Notes:
------
Only Python 3 is currently supported and tested Python2 support has been depreciated. The following standard module
libraries are used in this version.

Program Documentation
---------------------
Only Python 3 is supported and tested Python2 support has been depreciated.

2021.07.01 - Minor re-factoring and additional routines moved from other modules to here.
2020.04.04 - Refactored code to be more compact as import checks are done in the main routine.
2020.04.01 - Initial release

Copyright Notice
----------------
This file is part of the Open Porous Media project (OPM).

OPM is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as
published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

OPM is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the aforementioned GNU General Public Licenses for more
details.

Copyright (C) 2018-2021 Equinox International Petroleum Consultants Pte Ltd.

Author  : David Baxendale
          david.baxendale@eipc.co
Version : 2021.07.01
Date    : 20-Jul-2021
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
import os
import pkg_resources
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
def change_directory(jobpath, popup=False, outprt=False):
    """Change the Working Directory

    Change the current working directory to the job's path (`jobpath`)

    Parameters
    ----------
    jobpath : str
        The path of the job for which the change directory request is being executed
    popup : bool
        Boolean Popup display option (True to display Popup, False no display)
    outprt : bool
         Boolean print option (True to print to display, False not to print) to the PySimpleGUI window using cprint

    Returns
    -------
    error : boolean
        True if errors, otherwise False
    """

    try:
        os.chdir(jobpath)
        if outprt:
            sg.cprint('Working Directory ' + str(Path().absolute()) + '\n')
    except OSError:
        text = 'Change Working Directory Error \n\n' + str(jobpath) + 'Cannot Change the Current Working Directory'
        if popup:
            sg.popup_error(text,no_titlebar=False, grab_anywhere=False, keep_on_top=True)
        if outprt:
            sg.cprint(text)
        return True
    return False


def convert_string(string, option):
    """Convert a String from One Format to Another

    The regular expression looks for letters that are either at the beginning of the string, or preceded by an
    underscore. The given letter is captured. Each of those occurrences (underscore + letter) is replaced by the
    uppercase version of the found letter.

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


def copy_to_clipboard(input):
    """Copies Text to the Clipboard

    Copies the input text to the clipboard for pasting into another application

    Parameters
    ----------
    input : str
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
    root.clipboard_append(input)


def file_lstrip(file_name):
    """Strip File of Space in First Column Only

    Reads in a file and strips out the first space in a record if present and writes back out the file.

    Parameters
    ----------
    file_name : str
        Name of file to be processed.

    Returns
    -------
    None
    """

    with open(file_name, 'r') as file:
        data = file.readlines()

    with open(file_name, 'w') as file:
        for line in data:
            line = line.rstrip() + '\n'
            if line[0:1].lstrip():
                file.write(line)
            else:
                file.write(line[1:])


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


def is_not_blank(string):
    """Check if a String is Empty

    Checks if a string is empty with for "", "   ", and None strings

    Parameters
    ----------
    string :str
        String to test if empty.

    Returns
    -------
    True or False
    """

    return bool(string and not string.isspace())


def kill_job(mesg, pid):
    """Kill a Job Process and All It's Children Processes

    The function kills a running Linux process and all of the assoicated child processes.

    Parameters
    ----------
    mesg : str
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
        killjob = sg.popup_yes_no(mesg + 'pid: ' + str(pid), no_titlebar=False, grab_anywhere=False, keep_on_top=True)
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


def opm_header_file(file, file_in, file_out, optn, text, opmsys):
    """Write File Header to File

    Writes out OPM Flow include file header records to a file.

    Parameters
    ----------
    file : file
        File object that was used used as input to generate the output data set
    file_in : str
        Name of input file
    file_out : Name of output file
        File object that was used used as input to generate the output data set
    optn : list
        File header option set to "start" for Start Header or "end" for End Header
    text : list
        List of text messages to be printed
    opmsys : dict
        A dictionary containing the OPMRUN system parameters

    Returns
    -------
    None
    """

    header = '-- ' + '*' * 129 + '\n'
    time = datetime.datetime.now()
    time = str(time.strftime('%Y-%m-%d %H:%M:%S'))
    if optn[0] == "start":
        file.write(header)
        file.write('--\n')
        file.write('--                                                SIMULATION INCLUDE FILE\n')
        file.write('--\n')
        file.write('-- DESCRIPTION\n')
        file.write('-- -----------\n')
        for item in text:
            file.write('-- ' + item + '\n')
        file.write('--\n')
        if file_in is not None:
            file.write('-- FILE IN    : ' + str(Path(file_in).name) + '\n')
        file.write('-- FILE OUT   : ' + str(Path(file_out).name) + '\n')
        file.write('-- FILE PATH  : ' + str(Path(file_out).parents[0]) + '\n')
        file.write('--\n')
        file.write('-- GENERATED  : ' + str(opmsys['opmuser']) + '\n')
        file.write('-- MACHINE    : ' + str(opmsys['node']) + '\n')
        file.write('-- SYSTEM     : ' + str(opmsys['system']) + ': ' + str(opmsys['release']) + '\n')
        file.write('-- PYTHON     : ' + str(opmsys['python']) + '\n')
        file.write('-- PYTHON GUI : ' + str(opmsys['opmgui']) + '\n')
        file.write('-- DATE       : ' + str(time) + '\n')
        file.write('--\n')
        file.write('-- 45678901234567890123456789012345678901234567890123456789012345678901234567890' +
                   '1234567890123456789012345678901234567890123456789012\n')
        file.write('--       1         2         3         4         5         6         7         8' +
                   '         9         0         1         2         3\n')
        file.write('--       0         0         0         0         0         0         0         0' +
                   '         0         1         1         1         1\n')
        file.write(header)
        file.write('--\n')
        if optn[1] != "none":
            file.write(str(optn[1]) + '\n')
            file.write('--\n')

    elif optn[0] == 'end':
        file.write('\n--\n')
        if optn[1] == 'ECHO':
            file.write('ECHO\n')
            file.write('--\n')
        file.write(header)
        file.write('-- END OF FILE\n')
        file.write(header)

    else:
        file.write('\n')
        file.write(header)
        if text is not None:
            for item in text:
                file.write('--' + item + '\n')
            file.write(header)
    return ()


def opm_initialize():
    """Initialized OPMRUN

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
                      no_titlebar=False, grab_anywhere=False, keep_on_top=True)
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


def opm_popup(title, text, nrow=10, font = None):
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

    layout1 = [[sg.Multiline(text, size=(80, nrow), background_color='white', text_color='darkgreen', font=font)],
               [sg.CloseButton('OK')]]
    window1 = sg.Window('OPMRUN - OPM Flow Job Scheduler: ' + title, layout=layout1)
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
    opmsys1['opmflow'   ] = opmflow.rstrip()
    opmsys1['opmgui'    ] = 'PySimpleGUI - ' + str(sg.version)
    opmsys1['airspeed'  ] = 'airspeed - ' + str(pkg_resources.get_distribution('airspeed').version)
    opmsys1['datetime'  ] = 'datetime - ' + opmsys1['python']
    opmsys1['getpass'   ] = 'getpass - ' + str(pd.__version__)
    opmsys1['os'        ] = 'os - ' + opmsys1['python']
    opmsys1['pandas'    ] = 'pandas - ' + str(pd.__version__)
    opmsys1['pathlib'   ] = 'pathlib - ' + opmsys1['python']
    opmsys1['platform'  ] = 'platform - ' + opmsys1['python']
    opmsys1['psutil'    ] = 'psutil - ' + str(psutil.__version__)
    opmsys1['pyDOE2'    ] = 'pyDOE2 - ' + str(pkg_resources.get_distribution('pyDOE2').version)
    opmsys1['re'        ] = 're - ' + opmsys1['python']
    opmsys1['subprocess'] = 'subprocess - ' + opmsys1['python']
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
                          no_titlebar=False, grab_anywhere=False, keep_on_top=True)
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
                      no_titlebar=False, grab_anywhere=False, keep_on_top=True)
        pass

    return opmsys1, opmlog1


def opm_view(file, opmoptn):
    """View/Edit Results Output File

    The function sets up the parameters to call the default editor to edit the selected DATA file .

    Parameters
    ----------
    file : str
        The output file results.
    opmoptn : dict
        A dictionary containing the OPMRUN default parameters

    Returns
    -------
    None
    """
    #
    # Edit/View Production Schedule File
    #
    if Path(file).is_file():
        if opmoptn['edit-command'] == 'None':
            sg.popup_error('Editor command has not been set in the properties file',
                        'Use Edit OPMRUN Options to set the Editor Command',
                        no_titlebar=False, grab_anywhere=False, keep_on_top=True)
            sg.cprint('Editor Command Has Not Been Set: ' + str(opmoptn['edit-command']))
            return ()
        else:
            command = str(opmoptn['edit-command']).rstrip()
            try:
                sg.execute_command_subprocess(command, file, wait=False, pipe_output=False)
            except Exception:
                sg.popup_error('Error Executing Editor Command: ' + command + ' ' + str(file),
                               no_titlebar=False, grab_anywhere=False, keep_on_top=True)
                sg.cprint('Error Executing Editor Command: ' + command + ' ' + str(file))
                return ()
    else:
        sg.popup_error('Cannot Find  File:/n ', str(file),
                      no_titlebar=False, grab_anywhere=False, keep_on_top=True)
        sg.cprint('Cannot Find: ' + str(file))
    return()


def print_dict(dict_name, dict_var, option='debug'):
    """PRINT_DICT.py Print Python Dictionary

    Prints a  Python dictionary in tabular form in various formats depending on the output option.

    Parameters
    ----------
    dict_name : str
        Variable name of the dictionary to be printed
    dict_var : dict
        Dictionary to be printed
    option : str
        Print option set to 'debug' for sg.Print, otherwise standard print

    Returns
    -------
    None
    """

    if option == 'debug':
        sg.Print('Print Dictionary Variable Start: ' + dict_name)
        sg.Print(pd.DataFrame.from_dict(dict_var, orient='index', columns=['Value']))
        sg.Print('Print Dictionary Variable End: ' + dict_name)
    elif option == 'popup':
        text = pd.DataFrame.from_dict(dict_var, orient='index', columns=['Value'])
        text = text.to_string(header=False, justify='left')
        opm_popup(dict_name + ' Dictionary Listing ', text, 30)
    else:
        sg.cprint(dict_name + ':Dictionary Listing')
        for item in dict_var:
            sg.cprint(dict_name + '({:<18}) = {:}'.format(item, dict_var[item]))
        sg.cprint(dict_name + ':End')
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
    lineout : str
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
                           no_titlebar=False, grab_anywhere=False, keep_on_top=True)
            pass
        #
        # Process Complete - Get Exit Code
        #
        returncode = jobproc.wait(timeout)
        if jobproc.returncode > 1:
            sg.popup_error('Subprocess Call Error: \n \n' + str(command) + '\n \n' +
                           'Return Code:' + str(returncode) + '\n',
                           no_titlebar=False, grab_anywhere=False, keep_on_top=True)
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
                sg.cprint(line)
                window.refresh()

        except Exception as err:
            sg.cprint(err, type(err))
            pass
        #
        # Process Complete - Get Exit Code
        #
        returncode = jobproc.wait(timeout)
        if jobproc.returncode > 1:
            sg.cprint('Exit Code ' + str(returncode))
        return returncode


def tail(f, n, offset=None):
    """Read The Last Lines of Output from a Sub-Process Command

    Reads a n lines from f with an offset of offset lines.  The return value is a tuple in the form
    ``(lines, has_more)`` where `has_more` is  an indicator that is `True` if there are more lines in the file.

    Parameters
    ----------
    f : str
        File for which the last number of lines are to be read
    n : int
        The last number of lines requires
    offset :int
        The line offset

    Returns
    -------
    lines :str
        Requested last n lines of text
    """

    avg_line_length = 74
    to_read = n + (offset or 0)

    while 1:
        try:
            f.seek(-(avg_line_length * to_read), 2)
        except IOError:
            # woops.  apparently file is smaller than what we want
            # to step back, go to the beginning instead
            f.seek(0)

        pos = f.tell()
        lines = f.read().splitlines()
        if len(lines) >= to_read or pos == 0:
            return lines[-to_read:offset and -offset or None], \
                   len(lines) > to_read or pos > 0
        avg_line_length *= 1.3


def version_check(version):
    """Check Installed Package Version Against Minimum Require Version

    Checks an installed package version against a minimum require version, after Jason Yang (jason990420)
    (https://github.com/PySimpleGUI/PySimpleGUI/issues/4551)

    Parameters
    ----------
    version : minimum required version, '4.25.0'
        The required minimum version of the package.

    Returns
    -------
    boolean : boolean
        True if required met otherwise False.
    """

    def get_tuple(version):
        return tuple(map(int, version.split(".")))

    return get_tuple(sg.__version__) >= get_tuple(version)

# ======================================================================================================================
# End of OPM_COMMON.PY
# ======================================================================================================================
