# ======================================================================================================================
#
"""OPMRUN.py - Run OPM Flow

OPMRUN is a Graphical User Interface ("GNU") program for the Open Porous Media ("OPM") Flow simulator.
The software enables submitting OPM Flow simulation input decks together with editing of the associated PARAM file,
as well as compressing and uncompress OPM Flow's input and output files in order to save disk space. This is the main
code based which allows for incorporating additional tools via the Tool menu. See the OPMRUN function for further
details.

Program Documentation
---------------------
2020-04.04 - Replace import sys with import platform
             Refactor code to improve maintainability, including moving some functions to the opm-common module.
             Moved various global variables to global dictionary variable opmsys to simplifiy code, the intention is
             to eventually remove all global variables.
             Refactored compress and uncompress routines to be use the print to multiline option.

2020-04.03 - Changed version number.
           - Updated all templates to be consistent with OPM Flow manual.
           - Updated documentation for this release.

2020-04.02 - Fix a bug with Compress/Uncompress windows preventing printing to the main Out element. This was because
             these two windows used an an Out element as well, and there can be only one Out element in the application.
             The fix was to use the Multiline element for the Compress/Uncompress windows, this resulted in various
             code changes to other functions.
             Fix initial directory bug when loading a queue. Need to set default and initial directory variables in
             PopupGetFile() call.
           - Moved main code into function to comply with PEP8 and refactored where necessary. Changed event status
             when running jobs. Also fixed some typos in the Help and About text.
           - Fixed inconsistent Python major release check.
           - Changed the job queue list so that the current job is highlighted in the list when running in
             foreground mode.
           - Fixed potential bug in the add_job() function by using the set_window_status() function to enable and
             disable the main window. Previously the direct methods were used and this may cause the application to
             freeze under Linux.
           - Fixed some typos.
           - Used NumPy/SciPy Docstrings documentation format and document all functions.
           - Move several functions to opm_common to reduce code duplication.

2020-04.01 - Fixed a tKinter bug that centers windows by the total x-direction display space, rather than the using
           - just the primary display size (multi-monitor issue). All pops are now based on the current main window
             location.
           - Added initial folder option when setting the  OPM Flow manual location.
           - Removed base64 icon graphic from code, and loaded png graphic from file, for code readability reasons and
             replaced manual reference of icon for all windows with SetOption default.
           - Fixed warning message associated with logging before main window was realized.
           - Added warning message if Python 3.7.3 or greater is being used.
           - Fixed Popup displays not showing text in PySimpleGUI 4.14.1 due to default color of text being None.
           - Support for Python 2 depreciated.
           - Moved to PySimpleGUI version 4.14.1
           - Added PySimpleGUI version to About dialog box for additional information
           - Initial release of OPMKEYW.

2019-04.05 - Added checks and warnings for importing PySimpleGUI and pathlib/pathlib2 for robustness.
           - Fixed display bug in several PopupGetFile() calls and add_job and load_queue functions.
           - Updated program code documentation and the Release-Notes.txt file.
           - Updated README.md file fixing some minor layout issues

2019-04.04 - Added suport for Python 2 by using the pathlib2 module from https://pypi.org/project/pathlib2/
             (not tested).
           - Updated program code documentation and the Release-Notes.txt file.
           - Updated README.md file to based on PDF documentation
           - Deleted binary file from the repository.

2019-04.03 - Added OPM Flow icon to all Windows via Base64 Encoded PNG File and added OPMRUN.svg icon to release.
           - Changed all Popup messages to have no title bar, grab anywhere, and keep on top options.
           - Moved job parameter manipulation into a separate function get__job function to reduce code duplication,
             as well as to have most of the path manipulation in the one routine.
           - Modified documentation.
           - Re-compiled binary generated tested on Unbuntu-Mate 18-04 and 19-04.

2019-04.02 - Fixed menu layout bug.
           - Fixed Project Directory bug for when the default OPMRUN.ini file is created.
           - Fixed Edit Parameters bug for when OPM Flow has not been installed.
           - Changed some text messages to be consistent with Options.
           - Re-compiled binary generated.

2019-04.01 - Fixed bug in running parallel jobs.
           - Added functionality to kill a running job, and disable certain buttons when jobs are running.
           - Fixed printing bug when OPM Flow terminates with errors.
           - Added windows dialog sizes to OPMRUN.ini file so that user can change the windows size at next re-start.
           - Moved pre-processing code to separate module for code readability (after suggestion by Joakim Hove).
           - Upgraded to PySimpleGUI 3.36.0.
           - Disable X close event or check for None.
           - Added option to Edit OPMRUN options.
           - When adding a job clear the file name field after the job has been added to the queue.
           - Added Compress Jobs and Uncompress Jobss to the Tools menu.
           - Added ResInsight option to the Tools menu.
           - Added option to clear the output and log elements.
           - For the Add Job dialog list the number of CPUs available; previously the range went from one to 64. Also
             implemented multiple job selection.
           - Added projects as shortcut to project directories.
           - Added option to run job queue in foreground (that is under OPMRUN) and background via xterm (should be
             computationally more efficient).
           - Major re-factoring of code and code clean up.
           - Create stand alone executable for Linux systems (works on Ubuntu-Mate 18-04).

2018-10.02 - Fix printing bug associated with listing of jobparam.
             Create stand alone executable for Linux systems (works on Ubuntu-Mate 18-04)

2018-10.01 - Initial release.

Notes:
------
Only Python 3 is currently supported and tested Python2 support has been depreciated. The following standard module
libraries are used in this version.

(1) datetime
(2) getpass
(3) os
(4) pathlib
(5) psutil
(6) platform
(7) re
(8) subprocess

For OPMRUN the following Python modules are required:

(1) PySimpleGUI

PySimpleGUI is the GUI tool used to build OPMRUN. It is in active development and is frequently updated
for fixes and new features. Each release of OPMRUN will update to the latest release of PySimpleGUI.

To Do List
----------
(1) Add a status tab to the bottom element with a table showing the project name, job name start time and end time,
    and job status (Aborted, Completed, Killed, Running, etc.)
(2) Add right-click menu options to the status table to edit files, view results, load results into ResInsight, etc.
(3) Write job status files to update status table for both foreground and background jobs.

Compiling Source
----------------
It's possible to create a single executable binary file that can be distributed to Linux users. There is no
requirement to install the Python interpreter on the PC you wish to run it on. Everything it needs is in the one
binary executable file, assuming you are running a somewhat up to date version of Linux.

Installation of the packages, you'll need to install PySimpleGUI and PyInstaller (you need to install only once)

       pyinstaller --clean --onefile opmrun.py

You will be left with a single file, opmrun, located in a folder named dist under the folder where you executed
the pyinstaller command. opmrun file should run without creating a "terminal window". Only the GUI window should show
up.

Note there are other tools for compiling Python code; however, PyInstaller’s main advantages over similar tools are that
PyInstaller works with Python 2.7 and 3.4—3.7, it builds smaller executables thanks to transparent compression,
it is fully multi-platform, and use the OS support to load the dynamic libraries, thus ensuring full compatibility.
See https://www.pyinstaller.org/ for further information

Copyright Notice
----------------
This file is part of the Open Porous Media project (OPM).

OPM is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as
published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

OPM is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the aforementioned GNU General Public Licenses for more
details.

Copyright (C) 2018-2020 Equinox International Petroleum Consultants Pte Ltd.

Author  : David Baxendale
          david.baxendale@eipc.co
Version : 2020-04.01
Date    : 13-May-2020
"""
# ----------------------------------------------------------------------------------------------------------------------
# 3456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890
#        1         2         3         4         5         6         7         8         9         0         1         2
#        0         0         0         0         0         0         0         0         0         1         1         1
# ----------------------------------------------------------------------------------------------------------------------
#
# ----------------------------------------------------------------------------------------------------------------------
# Import Modules and Start Up Section
# ----------------------------------------------------------------------------------------------------------------------
#
# Standard Library Modules
#
import datetime
import getpass
import importlib
import os
import pkg_resources
import platform
import re
import subprocess
import tkinter as tk
from pathlib import Path
from psutil import cpu_count
#
# Non Standard Library Modules
#
import PySimpleGUI
import pandas
import airspeed
import pyDOE2
#
# Check for Python 2 Version
#
if platform.python_version_tuple()[0] == '2':
    exit('OPMRUN Only Works with Python 3, Python 2 Support is Depreciated')
#
# Import Required Non-Standard Modules
#
starterr = False
required = {'airspeed', 'pandas', 'pyDOE2', 'PySimpleGUI'}
for package in required:
    try:
        dist = pkg_resources.get_distribution(package)
        if package == 'PySimpleGUI':
            sg = importlib.import_module(package)
        elif package == 'pandas':
            pd = importlib.import_module(package)
        else:
            importlib.import_module(package)
        print('Startup: Require Module - ' + dist.key + '(' + dist.version + ') Imported')
    except pkg_resources.DistributionNotFound:
        print('Startup: Import Require Package - ' + package + ' Failed')
        print('Startup: Use "python3 -m pip install --user ' + package + '" to install')
        starterr = True

if starterr:
    print('Startup: Use "python3 -m pip --verbose list" to get a list of installed packages')
    exit('Startup: Failed due to Missing Module(s)')
#
# Import OPMRUN Modules
#
from opm_common   import convert_string, get_time, opm_initialize, opm_popup, opm_startup
from opmkeyw      import keyw_main
#
# Check for Python Version for 3.7 and Issue Warning Message and Continue
#
# if platform.python_version_tuple() >=  ('3' ,'7', '3'):
#     sg.popup_error('Python 3.7.3 and Greater Detected OPMRUN May Have Problems \n' +
#                   '\n' +
#                   'The version of tkinter that is being supplied with the 3.7.3 and later versions of Python is \n' +
#                   'known to have a problem with table colors, basically they do not work. As a result, if you wish \n'
#                   'to use the plain PySimpleGUI running on tkinter, you should be using 3.7.2 or less. \n' +
#                   '\n' +
#                   'Note that PySimpleGUI version 3.6 is the recommended version for most users. \n'
#                   '\n' +
#                   'Program will continue', no_titlebar=True, grab_anywhere=True, keep_on_top=True)

# ----------------------------------------------------------------------------------------------------------------------
# Define Modules Section 
# ----------------------------------------------------------------------------------------------------------------------
def add_job(joblist, jobparam, jobsys):
    """Add a OPM Flow Simulation job to the Job List Queue

    The function adds a DATA file to the job list queue by selecting the file via a window, and also defining the job
    parameters for this series of jobs. Multiple jobs can be selected at a time.

    Parameters
    ----------
    joblist : list
        Job list for queue
    jobparam : list
        OPM Flow PARAM file data set
    jobsys : dict
        Contains a dictionary list of all OPMRUN System parameters

    Returns
    -------
    joblist : list
        The updated joblist
    """

    if jobparam == []:
        sg.PopupError('Job Parameters Missing; Cannot Add Cases - Check if OPM Flow is Installed',
                      no_titlebar=True, grab_anywhere=True, keep_on_top=True)
        return()
    set_window_status(False)
    layout1 = [[sg.Text('File to Add to Queue')],
               [sg.InputText(key='_job_', size=(80, None)),
                sg.FilesBrowse(target='_job_', initial_folder=Path().absolute(),
                               file_types=[('OPM', ['*.data','*.DATA']), ('All', '*.*')])],
               [sg.Text('Run Parameters')],
               [sg.Radio('Sequential Run' , "bRadio", default=True)],
               [sg.Radio('Parallel Run   ', "bRadio"              ), sg.Text('No. of Nodes'),
                sg.Listbox(values=list(range(1, cpu_count() + 1)), size=(5, 3))],
               [sg.Submit(), sg.Cancel()]]
    window1 = sg.Window('Select OPM Flow Input File', layout=layout1)

    while True:
        (event, values) = window1.Read()
        jobs    = values['_job_']
        jobseq  = values[0]
        jobpar  = values[1]
        jobnode = values[2]
        if not jobnode:
            jobnode = 2

        if event == 'Submit' and len(jobs) != 0:
            jobs = jobs.split(';')
            for job in jobs:
                jobpath = Path(job).parents[0]
                jobbase = Path(job).name
                jobfile = Path(job).with_suffix('.param')
                if jobseq:
                    joblist.append('flow --parameter-file=' + str(jobfile))
                if jobpar:
                    joblist.append('mpirun -np ' + str(jobnode).strip("[]") + ' flow --parameter-file=' + str(jobfile))
                set_window_status(True)
                window0['_joblist_'].update(joblist)
                set_window_status(False)
                #
                # Write Out PARAM File?
                #
                if jobfile.is_file():
                    text = sg.PopupYesNo('Parameter file:', str(jobfile),
                                         'Already exists; do you wish to overwite it with the current defaults?',
                                         'Press YES to overwrite the file and NO to keep existing file',
                                         '', no_titlebar=True, grab_anywhere=True, keep_on_top=True)
                else:
                    text = 'Yes'

                if text == 'Yes':
                    save_parameters(job, jobparam, jobbase, jobfile, jobsys)

                window1['_job_'].update(value='')

        elif event == 'Cancel' or event == None:
            break

    window1.Close()
    set_window_status(True)
    return()


def clear_queue(joblist):
    """ Clear Job Queue

    Clears the job queue of all jobs

    Parameters
    ----------
    joblist : list
        List of jobs in the job queue

    Returns
    ------
    None
    """

    if joblist == []:
        sg.PopupOK('No Cases In Job Queue to Delete', no_titlebar=True,
                   grab_anywhere=True, keep_on_top=True)
    else:
        text = sg.PopupYesNo('Delete All Cases in Queue?', no_titlebar=True,
                             grab_anywhere=True, keep_on_top=True)
        if text == 'Yes':
            joblist = []
            window0['_joblist_'].update(joblist)


def compress_job(opmoptn):
    """ Compress All Jobs Input and Output into a Zip File Using the Base Name

    The function allows the use to select a group of DATA files for compression of all files associated with the case
    name (*.DATA), using the standard zip utility on Linux systems

    Parameters
    ----------
    opmoptn; dict
        A dictionary containing the OPMRUN default parameters

    Returns
    ------
    None
    """

    set_window_status(False)

    joblist1 = []
    layout1  = [[sg.Text('Select Multiple Job Data Files to Compress'                             )],
                [sg.Listbox(values='', size=(100, 10), key='_joblist1_',
                            font=(opmoptn['output-font'], opmoptn['output-font-size'])            )],
                [sg.Text('Output'                                                                 )],
                [sg.Multiline(key='_outlog1_', size=(100, 15), text_color='blue', autoscroll=True,
                              font=(opmoptn['output-font'], opmoptn['output-font-size'])          )],
                [sg.Text('Compression Options'                                                    )],
                [sg.Radio('Compress Job' , "bRadio", default=True                                 )],
                [sg.Radio('Compress Job and then Remove Job Files', "bRadio"                      )],
                [sg.Button('Add'), sg.Button('Clear',  tooltip='Clear Output'), sg.Button('List'),
                                   sg.Button('Remove', tooltip='Remove Data Files'), sg.Submit(), sg.Cancel()]]
    window1 = sg.Window('Compress Job Files', layout=layout1)

    while True:
        (event, values) = window1.Read()
        jobopt  = values[0]
        #
        # Add Files
        #
        if event == 'Add':
            jobs = sg.PopupGetFile('Select Job Data Files to Compress', no_window=False,
                                   default_path=str(Path().absolute()), initial_folder=str(Path().absolute()),
                                   multiple_files=True, file_types=[('OPM', ['*.data','*.DATA'])])
            if jobs != None:
                jobs = jobs.split(';')
                for job in jobs:
                    joblist1.append(job)

                window1['_joblist1_'].update(joblist1)
            continue
        #
        # Clear Output
        #
        if event == 'Clear':
            window1['_outlog1_'].update('')
            continue
        #
        # Get Directory and List Files
        #
        if event == 'List':
            jobpath = sg.PopupGetFolder('Select Directory', no_window=False,
                                        default_path=str(Path().absolute()), initial_folder=str(Path().absolute()))
            if jobpath != None:
                set_directory(jobpath, outlog=False, outpop=False, outprt=False, window=window1)

            jobpath = Path().absolute()
            for file in Path(jobpath).glob("*.data"):
                window1['_outlog1_'].update(str(Path(file).name) + '\n', append=True)

            for file in Path(jobpath).glob('*.DATA'):
                window1['_outlog1_'].update(str(Path(file).name) + '\n', append=True)

            window1['_outlog1_'].update('Listing Complete ' + str(jobpath) + '\n', append=True)
            continue
        #
        # Remove Files
        #
        if event == 'Remove':
            joblist1 = []
            window1['_joblist1_'].update(joblist1)
            continue
        #
        # Compress Files
        #
        if event == 'Submit':
            if jobopt:
                zipcmd = 'zip -uv '
            else:
                zipcmd = 'zip -mv '

            jobnum = -1
            for cmd in joblist1:
                jobnum = jobnum + 1
                window1['_joblist1_'].update(set_to_index=jobnum, scroll_to_index=jobnum)
                window1['_outlog1_'].update('\n', append=True)
                out_log('Start Compression', True, False, window1)
                (job, jobcmd, jobpath, jobbase, jobroot, jobfile, jobzip) = get_job(cmd, option='zip')
                set_directory(jobpath, outlog=False, outpop=False, outprt=False, window=window1)
                jobcmd = zipcmd + str(jobzip) + ' ' + str(jobfile)
                out_log('   ' + jobcmd, True, False, window1)
                run_command(jobcmd, timeout=None, window=window1)
                out_log('End Compression', True, False, window1)
                window1.refresh()

            window1['_joblist1_'].update(joblist1)
            continue
        #
        # Cancel
        #
        if event == 'Cancel' or event == None:
            break

    window1.Close()
    set_window_status(True)
    return()


def default_parameters(jobparam, fileparam):
    """Define OPM Flow Default PARAM Parameters

    Function sets the default PARAM parameters for all new cases by loading the parameters from the default set from
    OPM Flow, from an existing PARAM file, or an existing parameter file.

    Parameters
    ----------
    jobparam : list
        Current default PARAM data set
    fileparam : str
        Job file name that is used to store the OPM Flow help information

    Returns
    -------
    jobparam : list
        Updated default PARAM data set
    """

    set_window_status(False)

    jobparam0 = jobparam
    jobparam  = []

    layout1   = [[sg.Text('Define OPM Flow Default Parameters for New Cases')],
                 [sg.Radio('Load Parameters from OPM Flow '               , 'bRadio', default=True)],
                 [sg.Radio('Load Parameters from OPM Flow Parameter File' , 'bRadio'              )],
                 [sg.Radio('Load Parameters from OPM Flow Print File'     , 'bRadio'              )],
                 [sg.Text('Only cases added after the parameters are loaded will use the selected parameter set')],
                 [sg.Submit(), sg.Cancel()]]
    window1   = sg.Window('Define OPM Flow Default Run Time Parameters', layout=layout1)

    while True:
        (event, values) = window1.Read()
        if event == 'Submit':
            if values[0]:
                jobparam, jobhelp = load_parameters(fileparam)
                break

            elif values[1]:
                filename = sg.PopupGetFile('OPM Flow Parameter File Name', default_extension='param', save_as=False,
                                           file_types=[('Parameter File', ['*.param', '*.PARAM']), ('All', '*.*')],
                                           keep_on_top=False)
                if filename:
                    file  = open(filename, 'r')
                    for n, x in enumerate(file):
                        if '=' in x:
                            jobparam.append(x.rstrip())
                    file.close()
                    sg.PopupOK('OPM Flow User Parameters Loaded from: ' + filename,
                               no_titlebar=True, grab_anywhere=True, keep_on_top=True)
                    break

            elif values[2]:
                filename = sg.PopupGetFile('OPM Flow PRT File Name', default_extension='prt', save_as=False,
                                           file_types=[('Print File', ['*.prt', '*.PRT']), ('All', '*.*')],
                                           keep_on_top=False)
                if filename:
                    file  = open(filename, 'r')
                    for n, x in enumerate(file):
                        if '="' in x:
                            if '# default:' in x:
                                x    = x[:x.find('#') - 1]
                                xcmd = convert_string(x[:x.find('=')], 'camel2flow')
                                x    = xcmd + x[x.find('='):]
                                jobparam.append(x.rstrip())
                        elif '==Saturation' in x:
                            file.close()
                            sg.PopupOK('OPM Flow User Parameters Loaded from: ' + filename,
                                       no_titlebar=True, grab_anywhere=True, keep_on_top=True)
                            break
                    break

        elif event == 'Cancel' or event == None:
            break

    window1.Close()
    if not jobparam:
        sg.PopupOK('OPM Flow User Parameters Not Set, Using Previous Values Instead',
                   no_titlebar=True, grab_anywhere=True, keep_on_top=True)
        jobparam = jobparam0

    set_window_status(True)
    return jobparam


def delete_job(joblist, Job):
    """ Delete OPM Flow Job form Job Queue

    Deletes an existing job in the job queue from the job queue

    Parameters
    ----------
    joblist : list
        The list of jobs in the jb queue
    Job : str
        The currently selected job to be deleted from the job queue

    Returns
    ------
    joblist : list
        Updated job queue via global variable
    """

    if not joblist:
        sg.PopupOK('No Cases in Job Queue', no_titlebar=True, grab_anywhere=True, keep_on_top=True)

    elif not Job:
        sg.PopupOK('No Case Selected', no_titlebar=True, grab_anywhere=True, keep_on_top=True)
    else:
        text = sg.PopupYesNo('Delete \n ' + Job[0] + '?', no_titlebar=True, grab_anywhere=True, keep_on_top=True)
        if text == 'Yes':
            joblist.remove(Job[0])
            window0['_joblist_'].update(joblist)


def edit_job(job, jobsys, **jobhelp):
    """Edit Job DATA or PARAM File

    The function sets up the parameters to call the default editor to edit the selected DATA file and also the
    parameters to call the edit_parameters function that allows the user to edit the PARAM file.

    Parameters
    ----------
    job : str
        The selected job
    jobsys : dict
        Contains a dictionary list of all OPMRUN System parameters
    jobhelp : dict
        OPM Flow PARAM list help information stored in a dictionary with the key being the PARAM variable

    Returns
    -------
    None
    """

    if job == []:
        sg.PopupOK('No Case Selected', no_titlebar=True, grab_anywhere=True, keep_on_top=True)
        return()
    #
    # Edit Data File or Parameter File Option
    #
    jobparam   = []
    jobparam1  = []
    job        = str(job[0]).rstrip()
    istart     = job.find('=') + 1

    filebase   = Path(job[istart:]).stem
    filedata1  = Path(job[istart:]).with_suffix('.data')
    filedata2  = Path(job[istart:]).with_suffix('.DATA')
    filedata   = ''
    if filedata1.is_file():
        filedata = filedata1
    if filedata2.is_file():
        filedata = filedata2
    if filedata == '':
        sg.PopupError('Cannot Find Data File: ', str(filedata1),
                      'or ' , str(filedata2),
                      no_titlebar=True, grab_anywhere=True, keep_on_top=True)
        out_log('Cannot Find: ' + str(filedata1) + ' or ' + str(filedata2), True)

        return()

    fileparam1  = Path(job[istart:]).with_suffix('.param')
    fileparam2  = Path(job[istart:]).with_suffix('.PARAM')
    fileparam   = ''
    if fileparam1.is_file():
        fileparam = fileparam1
    if not fileparam2.is_file():
        fileparam = fileparam2
    if fileparam == '':
        sg.PopupError('Cannot Find Parameter File: ',  str(fileparam1),
                      'or ', str(fileparam2),
                      no_titlebar=True, grab_anywhere=True, keep_on_top=True)
        out_log('Cannot Find Parameter File: ' + str(fileparam1) + ' or ' + str(fileparam2), True)
        return()
    #
    # Files Found So Display Edit Options
    #
    layout1   = [[sg.Text('Edit Options for Job: ' + str(filebase))],
                 [sg.Radio('Edit Data File'     , 'bRadio', default=True)],
                 [sg.Radio('Edit Parameter File', 'bRadio'              )],
                 [sg.Submit(), sg.Cancel()]]
    window1   = sg.Window('Edit Job Options', layout=layout1)

    (event, values) = window1.Read()
    window1.Close()

    if event == 'Cancel' or event == None:
        return()
    #
    # Data File Processing
    #
    if event == 'Submit' and values[0] == True:
        if opmoptn['edit-command'] == 'None':
            sg.PopupOK('Editor command has not been set in the properties file',
                       'Use Edit OPMRUN Options to set the Editor Command',
                       no_titlebar=True, grab_anywhere=True, keep_on_top=True)
            out_log('Editor Command Has Not Been Set: ' + str(opmoptn['edit-command']), True)
            return()
        else:
            command = str(opmoptn['edit-command']).rstrip()
            out_log('Executing Editor Command: ' + command + ' ' + str(filedata), True)

            try:
                subprocess.Popen([command, filedata])

            except Exception:
                sg.PopupError('Error Executing Editor Command: ' + command + ' ' + str(filedata),
                              no_titlebar=True, grab_anywhere=True, keep_on_top=True)
                out_log('Error Executing Editor Command: ' + command + ' ' + str(filedata), True)
                return()
    #
    # Parameter File Processing
    #
    if event == 'Submit' and values[1] == True:
        if fileparam.is_file():
            file  = open(str(fileparam).rstrip(), 'r')
            for n, line in enumerate(file):
                if '=' in line:
                    jobparam.append(line.rstrip())
            file.close()
            #
            # Edit Job Parameters
            #
            (jobparam1, exitcode) = edit_parameters(jobparam, **jobhelp)
            if exitcode == 'Exit':
                save_parameters(filedata, jobparam1, filebase, fileparam, jobsys)

        else:
            sg.PopupError('Cannot Find Parameter File: ' + str(fileparam),
                          no_titlebar=True, grab_anywhere=True, keep_on_top=True)
            out_log('Cannot Find Parameter File: ' + str(fileparam), True)

    return()


def edit_options(opmsys1, opmoptn1):
    """ Edit OPMRUN Options that Define Various Configuration Options

    The routine allows the editing of the module's options stored in the OPMINI file that is read into the opmoptn
    dictionary variable. If the OPMINI file is not found then the default values defined in this function are used.

    Parameters
    ----------
    opmsys1 : dict
        Contains a dictionary list of all OPMRUN System parameters
    opmoptn1 : dict
        Contains the various options for the program as outlined below
            opm-author1      = Author
            opm-author2      = Company Name
            opm-author3      = Address
            opm-author3      = Address Line
            opm-author4      = Address Line
            opm-author5      = Email Address

            opm-flow-manual  = define the location of the OPM Flow Manual (None)
            opm-resinsight   = defines the ResInsight command
            edit-command     = defines the edit and editor options to edit the input deck (None)

            input-width      = set the size of the input list window in the x-direction (144)
            input-heigt      = set the size of the input list window in the y-direction (10)
            output-font      = set the output font type (Courier)
            output-font-size = set the output font size (10)
            output-width     = set the size of the output log windows in the x-direction (140)
            output-heigt     = set the size of the output log windows in the y-direction (30)

    Returns
    -------
    opmoptn1 : dict
        Updated via global variable
    """

    set_window_status(False)
    opmoptn0  =  opmoptn1
    if Path(opmoptn1['opm-flow-manual']).exists():
        defmanual = Path(opmoptn['opm-flow-manual']).parents[0]
    else:
        defmanual = opmsys1['opmhome']

    if Path(opmoptn1['opm-keywdir']).exists():
        defkeyw = Path(opmoptn['opm-keywdir']).parents[0]
    else:
        defkeyw = opmsys1['opmhome']

    if Path(opmoptn1['opm-resinsight']).exists():
        defresinsight = Path(opmoptn['opm-resinsight']).parents[0]
    else:
        defresinsight = opmsys1['opmhome']

    column1   = [
                 [sg.Text('OPM Flow Manual Location'                                                  )],
                 [sg.InputText(opmoptn1['opm-flow-manual'], key='_opm-flow-manual_', size=(80, None))   ,
                  sg.FileBrowse(target='_opm-flow-manual_',
                                file_types=(('Manual Files', '*.pdf'),), initial_folder=defmanual)     ],

                 [sg.Text('OPM Keyword Generator Template Directory'                                  )],
                 [sg.InputText(opmoptn1['opm-keywdir'    ], key='_opm-keywdir_'       , size=(80, None)),
                  sg.FolderBrowse(target='_opm-keywdir_', initial_folder=defkeyw)                      ],

                 [sg.Text('ResInsight Command'                                                        )],
                 [sg.InputText(opmoptn1['opm-resinsight'  ], key='_opm-resinsight_'   , size=(80, None)),
                  sg.FileBrowse(target='_opm-resinsight_', initial_folder=defresinsight)               ],

                 [sg.Text('Editor Command for Editing Input Files'                                    )],
                 [sg.InputText(opmoptn1['edit-command'   ], key='_edit-command_'     , size=(80, None))],

                 [sg.Text(''                                                                          )],
                 [sg.Text('OPM Keyword Generator Variables'                                           )],
                 [sg.Text('Author'                                                   , size=(30, None)) ,
                  sg.InputText(opmoptn1['opm-author1'    ], key='_opm-author1_'      , size=(48, None))],
                 [sg.Text('Company Name'                                             , size=(30, None)) ,
                  sg.InputText(opmoptn1['opm-author2'    ], key='_opm-author2_'      , size=(48, None))],
                 [sg.Text('Address Line 1'                                           , size=(30, None)) ,
                  sg.InputText(opmoptn1['opm-author3'    ], key='_opm-author3_'      , size=(48, None))],
                 [sg.Text('Address Line 2'                                           , size=(30, None)) ,
                  sg.InputText(opmoptn1['opm-author4'    ], key='_opm-author4_'      , size=(48, None))],
                 [sg.Text('Email Address'                                            , size=(30, None)) ,
                  sg.InputText(opmoptn1['opm-author5'    ], key='_opm-author5_'      , size=(48, None))],

                 [sg.Text(''                                                                          )],
                 [sg.Text('Main Window Configuration Setting'                                         )],
                 [sg.Text('Input Element Width '                                     , size=(30, None)) ,
                  sg.InputText(opmoptn1['input-width'     ], key='_input-width_'     , size=(20, None))],
                 [sg.Text('Input Element Height'                                     , size=(30, None)) ,
                  sg.InputText(opmoptn1['input-heigt'     ], key='_input-heigt_'     , size=(20, None))],
                 [sg.Text('Output Element Width'                                     , size=(30, None)) ,
                  sg.InputText(opmoptn1['output-width'    ], key='_output-width_'    , size=(20, None))],
                 [sg.Text('Output Element Height'                                    , size=(30, None)) ,
                  sg.InputText(opmoptn1['output-heigt'    ], key='_output-heigt_'    , size=(20, None))],
                 [sg.Text('Output Element Font'                                      , size=(30, None)) ,
                  sg.InputText(opmoptn1['output-font'     ], key='_output-font_'     , size=(20, None))],
                 [sg.Text('Output Element Font Size'                                 , size=(30, None)) ,
                  sg.InputText(opmoptn1['output-font-size'], key='_output-font-size_', size=(20, None))]
                ]

    layout1   = [[sg.Column(column1)      ],
                 [sg.Submit(), sg.Cancel()]]

    window1   = sg.Window('Edit Options', layout=layout1)

    (event, values) = window1.Read()
    window1.Close()

    if event == 'Cancel' or event == None:
        opmoptn1 = opmoptn0

    if event == 'Submit':
        opmoptn1['opm-flow-manual' ] = values['_opm-flow-manual_' ]
        opmoptn1['opm-keywdir'     ] = values['_opm-keywdir_'     ]
        opmoptn1['opm-resinsight'  ] = values['_opm-resinsight_'  ]
        opmoptn1['edit-command'    ] = values['_edit-command_'    ]

        opmoptn1['opm-author1'     ] = values['_opm-author1_'     ]
        opmoptn1['opm-author2'     ] = values['_opm-author2_'     ]
        opmoptn1['opm-author3'     ] = values['_opm-author3_'     ]
        opmoptn1['opm-author4'     ] = values['_opm-author4_'     ]

        opmoptn1['input-width'     ] = values['_input-width_'     ]
        opmoptn1['input-heigt'     ] = values['_input-heigt_'     ]
        opmoptn1['output-width'    ] = values['_output-width_'    ]
        opmoptn1['output-heigt'    ] = values['_output-heigt_'    ]
        opmoptn1['output-font'     ] = values['_output-font_'     ]
        opmoptn1['output-font-size'] = values['_output-font-size_']

        save_options(opmsys1, opmoptn1)

    set_window_status(True)
    return opmoptn1


def edit_parameters(jobparam, **jobhelp):
    """Edit OPM Flow Parameters

    The function edits the OPM Flow Parameters and first checks if the parameters have been loaded via calling  of OPM
    Flow, in  case  OPM Flow has not been installed, or the system cannot find the program. If the parameters
    are not found, the routine sets the exitcode, displays error message, and returns.

    Parameters
    ----------
    jobparam : list
        OPM Flow PARAM parameter list
    jobhelp : dict
        OPM Flow PARAM list help information stored in a dictionary with the key being the PARAM variable

    Returns
    -------
    jobparam : list
        Updated OPM Flow PARAM parameter list
    exitcode :
        Return code for calling routine
    """

    exitcode = ''
    if jobparam:
        set_window_status(False)

        jobparam0  = jobparam
        layout1    = [[sg.Text('Select Parameter to Change:')],
                      [sg.Listbox(values=jobparam, size=(80, 20), key='_listbox_', bind_return_key=True,
                                  font=(opmoptn['output-font'], opmoptn['output-font-size']))],
                      [sg.Text('Parameter to Change:')],
                      [sg.InputText('', size=(80, 1), key='_text_',
                                    font=(opmoptn['output-font'], opmoptn['output-font-size']))],
                      [sg.Text('Parameter Help:')],
                      [sg.Multiline('', size=(80, 4), key='_texthelp_',
                                    font=(opmoptn['output-font'], opmoptn['output-font-size']))],
                      [sg.Button('Edit'), sg.Button('Save'), sg.Button('Cancel'), sg.Button('Exit')]]
        window1 = sg.Window('Edit Parameters', layout=layout1)

        while True:
            (event, values) = window1.Read()

            if event == 'Edit' or event == '_listbox_':
                if values['_listbox_'] == []:
                    sg.PopupError('Please select a parameter from the list',
                                  no_titlebar=True, grab_anywhere=True, keep_on_top=True)
                else:
                    window1['_text_'].update(values['_listbox_'][0])
                    texthelp = values['_listbox_'][0]
                    texthelp = texthelp[:texthelp.find('=')]
                    if texthelp in jobhelp:
                        paramhelp = jobhelp[texthelp]
                    else:
                        paramhelp = 'Help not found for ' + texthelp
                    window1['_texthelp_'].update(paramhelp)

            if event == 'Save':
                param = values['_text_']
                key   = param[:param.find('=')]
                for n, text in enumerate(jobparam):
                    if text[:text.find('=')] == key:
                        jobparam[n] = param
                        paramhelp = 'Parameter: ' + str(jobparam[n]) + ' has been updated'
                        window1['_texthelp_'].update(paramhelp)
                        break
                window1['_listbox_'].update(jobparam)

            if event == 'Cancel' or event == None:
                text = sg.PopupYesNo('Cancel Changes?',
                                     no_titlebar=True, grab_anywhere=True, keep_on_top=True)
                if text == 'Yes':
                    jobparam  = jobparam0
                    exitcode  = event
                    break
                else:
                    event = 'Edit'
                    continue

            if event == 'Exit':
                text = sg.PopupYesNo('Save and Exit?',
                                     no_titlebar=True, grab_anywhere=True, keep_on_top=True)
                if text == 'Yes':
                    jobparam = window1['_listbox_'].get_list_values()
                    exitcode = event
                    break

        window1.Close()
        set_window_status(True)
        window0['_outlog_'].update()

    else:
        exitcode  = 'Cancel'
        sg.PopupError('OPM Flow Parameters Have Not Been Set',
                      no_titlebar=True, grab_anywhere=True, keep_on_top=True)

    return jobparam, exitcode


def edit_projects(opmoptn1, opmsys1):
    """Edit Project Names and Directories

    Function allows the editing of project names and their associated directories. Projects are basically shortcuts to
    directories, so that one can quickly set the default directory. A maximum of five projects are current available.

    Parameters
    ----------
    opmoptn1 : dict
        Contains the project names and their associated directories
    opmsys1 : dict
        Contains a dictionary list of all OPMRUN System parameters

    Returns
    -------
    opmoptn1 : dict
        Updated via global variable
    """

    set_window_status(False)

    opmoptn0  =  opmoptn1
    column1   = [[sg.Text('No.'              , justification='center', size=( 3, 1)),
                  sg.Text('Project Name'     , justification='center', size=(20, 1)),
                  sg.Text('Project Directory', justification='center', size=(80, 1))],
                 [sg.Text('1. '),
                  sg.InputText(opmoptn1['prj-name-01'], key='_prj-name-01_', size=(20, 1)),
                  sg.InputText(opmoptn1['prj-dirc-01'], key='_prj-dirc-01_', size=(80, 1)),
                  sg.FolderBrowse(                   target='_prj-dirc-01_')],
                 [sg.Text('2. '),
                  sg.InputText(opmoptn1['prj-name-02'], key='_prj-name-02_', size=(20, 1)),
                  sg.InputText(opmoptn1['prj-dirc-02'], key='_prj-dirc-02_', size=(80, 1)),
                  sg.FolderBrowse(                   target='_prj-dirc-02_')],
                 [sg.Text('3. '),
                  sg.InputText(opmoptn1['prj-name-03'], key='_prj-name-03_', size=(20, 1)),
                  sg.InputText(opmoptn1['prj-dirc-03'], key='_prj-dirc-03_', size=(80, 1)),
                  sg.FolderBrowse(                   target='_prj-dirc-03_')],
                 [sg.Text('4. '),
                  sg.InputText(opmoptn1['prj-name-04'], key='_prj-name-04_', size=(20, 1)),
                  sg.InputText(opmoptn1['prj-dirc-04'], key='_prj-dirc-04_', size=(80, 1)),
                  sg.FolderBrowse(                   target='_prj-dirc-04_')],
                 [sg.Text('5. '),
                  sg.InputText(opmoptn1['prj-name-05'], key='_prj-name-05_', size=(20, 1)),
                  sg.InputText(opmoptn1['prj-dirc-05'], key='_prj-dirc-05_', size=(80, 1)),
                  sg.FolderBrowse(                   target='_prj-dirc-05_')]]

    layout1   = [[sg.Column(column1) ],
                 [sg.Submit(), sg.Cancel()]]

    window1   = sg.Window('Edit Projects', layout=layout1)

    (event, values) = window1.Read()
    window1.Close()

    if event == 'Cancel' or event == None:
        opmoptn1 = opmoptn0

    if event == 'Submit':
        opmoptn1['prj-name-01'] = values['_prj-name-01_']
        opmoptn1['prj-name-02'] = values['_prj-name-02_']
        opmoptn1['prj-name-03'] = values['_prj-name-03_']
        opmoptn1['prj-name-04'] = values['_prj-name-04_']
        opmoptn1['prj-name-05'] = values['_prj-name-05_']
        opmoptn1['prj-dirc-01'] = values['_prj-dirc-01_']
        opmoptn1['prj-dirc-02'] = values['_prj-dirc-02_']
        opmoptn1['prj-dirc-03'] = values['_prj-dirc-03_']
        opmoptn1['prj-dirc-04'] = values['_prj-dirc-04_']
        opmoptn1['prj-dirc-05'] = values['_prj-dirc-05_']
        save_options(opmsys1, opmoptn1)

    set_window_status(True)
    return opmoptn1


def get_job(cmd, option='opmflow'):
    """ Define Job Parameters Based On Job Type

    Converts job parameters into various forms for processing based on the option parameter. The routine reduces
    duplication of code for job parameter manipulation

    Parameters
    ----------
    cmd : str
        Job command
    option : str
        Type of job to be processed set to:
            (1) opmflow jobs    - option is set to 'opmflow'
            (2) compress jobs   - option is set to 'zip'
            (3) uncompress jobs - option is set to 'zip'

    Returns
    -------
    jobcmd : str
        The job command
    jobpath : str
        The path of the job file being processed
    jobbase : str
        The base name of the the job file being processed
    jobroot : str
        The base root  of the the job file being processed
    jobfile : str
        The job file with suffix '.*'
    joblog : str
        The job file with suffix '.LOG'
    jobzip : str
        The job file with suffix '*.zip'
    """

    job    = ''
    jobcmd = ''
    if option == 'opmflow':
        istart  = cmd.find('=')
        job     = cmd[istart + 1:]
        jobcmd  = cmd[:istart + 1]
    elif option == 'zip':
        job    = cmd
        jobcmd = cmd

    jobpath = Path(job).parents[0]
    jobbase = Path(job).name
    jobroot = Path(job).stem
    joblog  = Path(jobbase).with_suffix('.LOG')
    jobfile = Path(jobbase).with_suffix('.*')
    jobzip  = Path(jobbase).with_suffix('.zip')

    if option == 'opmflow':
        return job, jobcmd, jobpath, jobbase, jobroot, joblog
    elif option == 'zip':
        return job, jobcmd, jobpath, jobbase, jobroot, jobfile, jobzip


def kill_job(jobpid):
    """Kill OPMRUN Job

    Kills a running OPMRUN job using the passed PID for the job

    Parameters
    ----------
    jobpid : int
        Job processing PID

    Returns
    -------
    None
    """

    event, values = window0.Read(timeout=1)
    if event != '_kill_job_':
        return()

    text = sg.PopupYesNo('Do You Wish to Kill the Current OPM Flow Job ' + str(jobpid) + ' ?'
                         , no_titlebar=True, grab_anywhere=True, keep_on_top=True)
    if text == 'Yes':
        run_process(['kill ' + str(jobpid)])
        out_log   ('OPM Flow Process ' + str(jobpid) + ' Has Been Stopped by ' + str(getpass.getuser()), True, True)
        sg.PopupOK('OPM Flow Process ' + str(jobpid) + ' Has Been Stopped by ' + str(getpass.getuser()),
                   no_titlebar=True, grab_anywhere=True, keep_on_top=True)
    return()


def load_manual(opmsys1, filename):
    """Loads the OPM Flow User Manual

    Loads the OPM Flow User Manual in PDF format using the systems default PDF reader/viewer. The location of the manual
    is stored in the opmoptns dictionary and the filename is a reference to this variable.

    Parameters
    ----------
    opmsys1 : dict
        Contains a dictionary list of all OPMRUN System parameters
    filename : str
        OPM Flow User Manual full file name.

    Returns
    -------
    None
    """

    if filename == 'None':
        sg.PopupOK('OPM Flow Manual has not been defined in the Options.',
                   'Use the Edit Options menu to set the File Name.',
                   no_titlebar=True, grab_anywhere=True, keep_on_top=True)
        return()

    if Path(filename).is_file() == False:
        sg.PopupOK('OPM Flow Manual File Cannot be Found. \n', str(filename) + ' \n',
                   'Use the Edit Options menu to set the File Name.',
                   no_titlebar=True, grab_anywhere=True, keep_on_top=True)
        return ()
    #
    # Linux System
    #
    if opmsys1['system'] == 'Linux':
        try:
            subprocess.Popen(["xdg-open", filename])
        except Exception:
            sg.PopupError('OPM Flow Manual Error \n \n' + 'Cannot run: \n \n' +
                          '"xdg-open ' + str(filename) + '" \n \n' +
                          'Either the default PDF viewer is not available, or the OPM Flow Manual cannot be found.',
                          line_width=len(filename) + 12, no_titlebar=True, grab_anywhere=True, keep_on_top=True)
    #
    # Windows System
    #
    if opmsys1['system'] == 'Windows':
        try:
            os.startfile(filename)
        except Exception:
            sg.PopupError('OPM Flow Manual Error \n \n' + 'Cannot run: \n \n' +
                          str(filename) + ' \n \n' +
                          'Either the default PDF viewer is not available, or the OPM Flow Manual cannot be found.',
                          line_width=len(filename) + 12, no_titlebar=True, grab_anywhere=True, keep_on_top=True)

    return()


def load_options(opmoptn1, opmsys1):
    """Loads OPMRUN Options

    Loads OPMRUN options and projects that define various configuration options for the module. If the OPMINI file is
    not found then it is created in #HOME/OPM/OPMRUN.ini using the default values defined in this function. This routine
    also adds any options that are new in this release but unavailable in previous releases.

    Note that the order of the options are irrelevant due to using a dictionary variable.

    Parameters
    ----------
    opmoptn1 : dict
        Contains a dictionary list of all OPMRUN options as follows:
            input-width      = set the size of the input list window in the x-direction (144)
            input-heigt      = set the size of the input list window in the y-direction (10)
            output-width     = set the size of the output log windows in the x-direction (140)
            output-heigt     = set the size of the output log windows in the y-direction (30)
            output-font      = set the output font type (Courier)
            output-font-size = set the output font size (10)
            opm-flow-manual  = define the location of the OPM Flow Manual (None)
            opm-resinsight   = defines the ResInsight command
            edit-command     = defines the edit and editor options to edit the input deck (None)

            prj-name-01      =  Project Name 01
            prj-dirc-01      =  Project Directory 01
            prj-name-02      =  Project Name 02
            prj-dirc-02      =  Project Directory 02
            prj-name-03      =  Project Name 03
            prj-dirc-03      =  Project Directory 03
            prj-name-04      =  Project Name 04
            prj-dirc-04      =  Project Directory 04
            prj-name-05      =  Project Name 05
            prj-dirc-05      =  Project Directory 05

            opm-keywdir      = template keyword directory for OPMKEYW
            opm-author1      = template author and author address for OPMKEYW
            opm-author2      = template author and author address for OPMKEYW
            opm-author3      = template author and author address for OPMKEYW
            opm-author4      = template author and author address for OPMKEYW
            opm-author5      = template author and author address for OPMKEYW
    opmsys1 : dict
        Contains a dictionary list of all OPMRUN System parameters

    Returns
    -------
    opmoptn1 : dict
        Updated dictionary list of all OPMRUN options
    """
    #
    # Define Default Options
    #
    opmdef                     = dict()
    opmdef['input-width'     ] = 144
    opmdef['input-heigt'     ] = 10
    opmdef['output-width'    ] = 140
    opmdef['output-heigt'    ] = 30
    opmdef['output-font'     ] = 'Courier'
    opmdef['output-font-size'] = 10
    opmdef['opm-keywdir'     ] = 'None'
    opmdef['opm-flow-manual' ] = 'None'
    opmdef['opm-resinsight'  ] = 'None'
    opmdef['edit-command'    ] = 'None'
    opmdef['prj-name-00'     ] = 'OPMRUN Default Working Directory'
    opmdef['prj-dirc-00'     ] = str(opmsys1['opmhome'])
    opmdef['prj-name-01'     ] = 'Home'
    opmdef['prj-dirc-01'     ] = str(opmsys1['opmhome'])
    opmdef['prj-name-02'     ] = 'Home'
    opmdef['prj-dirc-02'     ] = str(opmsys1['opmhome'])
    opmdef['prj-name-03'     ] = 'Home'
    opmdef['prj-dirc-03'     ] = str(opmsys1['opmhome'])
    opmdef['prj-name-04'     ] = 'Home'
    opmdef['prj-dirc-04'     ] = str(opmsys1['opmhome'])
    opmdef['prj-name-05'     ] = 'Home'
    opmdef['prj-dirc-05'     ] = str(opmsys1['opmhome'])
    opmdef['opm-keywdir'     ] = 'None'
    opmdef['opm-author1'     ] = None
    opmdef['opm-author2'     ] = None
    opmdef['opm-author3'     ] = None
    opmdef['opm-author4'     ] = None
    opmdef['opm-author5'     ] = None

    if opmsys1['opmini'].is_file():
        try:
            file  = open(opmsys1['opmini'], 'r')
            for n, line in enumerate(file):
                if '=' in line:
                    key   = line[:line.find('=')]
                    value = line[line.find('=') + 1:].rstrip()
                    opmoptn1[key] = value
            file.close()
        except IOError:
            #
            # PROGRAM EXIT DUE TO ERROR
            #
            sg.PopupError('OPMRUN Options Error \n \n' + 'Problem Reading: \n \n' + str(opmsys1['opmini']) + '\n \n' +
                          'Try Deleting the File and Restarting OPMRUN - Program Will Abort',
                           no_titlebar=True, grab_anywhere=True, keep_on_top=True)
            exit('Error Reading ' + str(opmsys1['opmini']) + 'Try Deleting the File and Restarting')
        #
        # Check for Missing Options
        #
        error = False
        for key in opmdef:
            if key not in opmoptn1:
                opmoptn1[key] = opmdef[key]
                error = True

        if error:
            save_options(opmsys1, opmoptn1, False)
            sg.PopupOK('OPMRUN Options Have Been Created/Updated for this Release',
                       no_titlebar=True, grab_anywhere=True, keep_on_top=True)

        '''
        for key,val in opmoptn.items():
            sg.Print (key, "=>", val)
        print(opmoptn)
        '''
    else:
        opmoptn1 = opmdef
        save_options(opmsys1, opmoptn1, False)
        sg.PopupOK('OPMRUN Default Options Created and Saved',
                   no_titlebar=True, grab_anywhere=True, keep_on_top=True)
    return opmoptn1


def load_parameters(filename, outpop=True):
    """Load OPM Flow Parameters

    Function runs OPM Flow via a subprocess to get OPM Flow's Help parameters, and then then loads the help into
    jobhelp dict[] variable for future reference.

    Parameters
    ----------
    filename : str
        Job file name that is used to store the OPM Flow help information

    outpop : bool
        Popup display option (True to display Popup, false no display).

    Returns
    -------
    jobparam : List
        OPM Flow PARAM list

    jobhelp : dict
        OPM Flow PARAM list help information stored in a dictionary with the key being the PARAM variable
    """

    run_process('flow --help > ' + str(filename), outprt=False)
    jobparam = []
    jobhelp  = dict()
    file     = open(filename, 'r')
    for n, line in enumerate(file):
        if '--' in line  and 'help' not in line:
            line      = line[line.find('--') + 2:]
            default   = line[line.find('Default: ') + 9:]
            command   = line.split("  ", 1)
            command   = line[:line.find('=')] + '=' + str(default)
            command   = command.rstrip()
            jobparam.append(command)
            paramkey  = command[:command.find('=')]
            paramhelp = line.split("  ", 1)[1].lstrip()
            jobhelp[paramkey] = paramhelp
    file.close()
    #for key,val in jobhelp.items():
    #    sg.Print (key, "=>", val)   
    if outpop:
        sg.PopupOK('OPM Flow Parameters Loaded from Flow: ' + str(filename),
                   no_titlebar=True, grab_anywhere=True, keep_on_top=True)

    return jobparam, jobhelp


def load_queue(joblist, jobparam):
    """Load OPMRUN Job Queue

    The function first checks if OPM Flow is present on the system by examining jobparam, if okay, it then it checks if
    there are existing jobs in the queue, and asks if the queue should be over written, if so the function loads the
    requested job queue into joblist variable.

    Parameters
    ----------
    joblist : list
        Current job list in the job queue
    jobparam : list
        OPM Flow PARAM parameter list

    Returns
    -------
    joblist : list
        Updated job list via global variable
    """
    #
    # Check if OPM Flow Parameters Have Been Set
    #
    if jobparam == []:
        sg.PopupError('Job Parameters Missing; Cannot Load Job Queue - Check if OPM Flow is Installed',
                      no_titlebar=True, grab_anywhere=True, keep_on_top=True)
        return()
    #
    # Check Job Queue for Entries
    #
    if joblist != []:
        text = sg.PopupYesNo('Loading a OPMRUN Queue from File Will Delete the Existing Queue, Continue?',
                             no_titlebar=True, grab_anywhere=True, keep_on_top=True)
        if text == 'No':
            return()
    #
    # Load Queue if Valid Entry
    #
    filename = sg.PopupGetFile('OPMRUN Queue File Name', default_extension='que', save_as=False,
                               default_path=str(Path().absolute()), initial_folder=str(Path().absolute()),
                               file_types=[('OPM Queues', '*.que'), ('All', '*.*')], keep_on_top=False)
    if filename == None:
        sg.PopupOK('OPMRUN Queue: Loading of Queue Cancelled',
                    no_titlebar=True, grab_anywhere=True, keep_on_top=True)

    elif Path(filename).is_file():
        joblist = []

        file  = open(filename,'r')
        for n, line in enumerate(file):
            if 'flow' in line:
                joblist.append(line.rstrip())
        file.close()
        window0['_joblist_'].update(joblist)
        sg.PopupOK('OPMRUN Queue: Loaded from: ' + filename,
                   no_titlebar=True, grab_anywhere=True, keep_on_top=True)
    else:
        sg.PopupOK('OPMRUN Queue: Nothing to Load', no_titlebar=True, grab_anywhere=True, keep_on_top=True)

    return joblist


def out_log(text, outlog, outprt=False, window=None):
    """Print and Display Log Information

    Function prints log information to display and /or log file, and / or Multiline element with time stamp.

    Parameters
    ----------
    text : str
        String to be printed and/or displayed
    outlog : bool
        Boolean log file output (True to write to log file, False not to write).
    window : PySimpleGUI window
        The PySimpleGUI window that the output is going to (needed to do refresh on)

    Returns
    -------
    None
    """

    if outprt:
        print(text + '\n')

    if window is not None:
        window['_outlog1_'].update(text + '\n', append=True)

    text = get_time() + ': ' + text + '\n'
    window0['_outlog_'].update(text, append=True)

    if outlog:
        opmlog.write(text)

    return()


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

    try:
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
#
#       Old Code to Be Deleted
#
#        output = ''
#        for line in process.stdout:
#            line = line.decode()
#            output += line
#            window['_outlog1_').update(line, append=True)
#
#        retval = p.wait(timeout)
#        return retval, output

        while True:
            line = process.stdout.readline()
            line = line.decode("utf-8").strip()
            if line == '' and process.poll() is not None:
                break
            window['_outlog1_'].print(line)
            window.refresh()

    except Exception as e:
        window['_outlog1_'].print(e, type(e))
        pass
    #
    # Processs Complete - Get Exit Code
    #
    exitcode = process.returncode
    if exitcode != 0:
        window['_outlog1_'].print('Exit Code ' + str(exitcode))
    return(exitcode)


def run_job(command):
    """Run an OPM Flow Job

    Runs a OPM Flow job via the subprocess command, gets process ID, and sends output to the OPM Flow output element.

    Parameters
    ----------
    command : str
        The OPM Flow command to execute

    Returns
    -------
    exitcode : int
        Return code from the sub-process command
    """
    #
    # Submit Job and Get Process ID
    #
    i       = 0
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    while True:
        i = i + 1
        out_log('Getting Process PID Pass ' + str(i), True)
        window0.refresh()
        jobpid  = subprocess.run(['pidof', '-s', 'flow'], stdout=subprocess.PIPE).stdout
        if jobpid.decode() != '':
            break
        if i == 10:
            out_log('Getting Process PID Pass Failed Aborting Job', True)
            return()

    jobpid = int(jobpid)
    out_log('Simulation PID ' + str(jobpid), True)
    #
    # Process OPM Flow Output
    #
    while True:
        line = process.stdout.readline()
        line = line.decode("utf-8").strip()
        if line == '' and process.poll() is not None:
            break
        print(line)
        window0.refresh()
        kill_job(jobpid)
    #
    # Process Complete - Get Last Output
    #
    output   = process.communicate()[0]
    output   = output.decode("utf-8")
    print(output)
    for line in output.split(os.linesep):
        if 'Errors' in line  or 'terminate' in line or 'what()' in line or 'Aborted' in line:
            out_log(line, True)
    #
    # Processs Complete - Get Exit Code
    #
    exitcode = process.returncode
    if exitcode != 0:
        raise subprocess.CalledProcessError(exitcode, command)

    print('Process Complete (' + str(exitcode) + ')')
    return exitcode


def run_jobs(joblist, jobsys, outlog):
    """Run Jobs

    This is the main function to submit the OPM Flow jobs for processing. The function allows the user to select
    various options for running jobs and submits jobs for execution.

    Parameters
    ----------
    joblist : list
        Current job list in the job queue that are to be run
    jobsys : dict
        Contains a dictionary list of all OPMRUN System parameters
    outlog  : bool
        Boolean log file output (True to write to log file, False not to write).

    Returns
    -------
    None
    """

    jobcase = ''
    if joblist == []:
        sg.PopupOK('No Jobs In Queue', no_titlebar=True, grab_anywhere=True, keep_on_top=True)
        return()

    jobnum  = 0
    layout1 = [[sg.Text('Select the Run Option for All ' + str(len(joblist)) + ' Cases in Queue?'  )],
               [sg.Radio('Run in No Simulation Mode'      , 'bRadio1', key='_nosim_'               )],
               [sg.Radio('Run in Standard Simulation Mode', 'bRadio1', key='_rusim_',  default=True)],
               [sg.Text('Submit jobs for foreground or background processing'                      )],
               [sg.Radio('Foreground Processing'          , 'bRadio2', key='_fore_'  , default=True)],
               [sg.Radio('Background Processing'          , 'bRadio2', key='_back_'                )],
               [sg.Text(''                                                                         )],
               [sg.Submit(), sg.Cancel()]]
    window1 = sg.Window('Select Run Option', layout=layout1)
    (event, values) = window1.Read()
    window1.Close()
    #
    # Background Processing
    #
    if values['_back_']:
        if values['_nosim_']:
            save_jobs(joblist, '_nosim_', opmsys, outlog=True)
        else:
            save_jobs(joblist, '_rusim_', opmsys, outlog=True)

        #subprocess.Popen(['mate-terminal', '-e', str(jobsys['opmjob'])], stdout=subprocess.PIPE)
        subprocess.Popen(['xterm', '-hold', '-e', str(jobsys['opmjob'])], stdout=subprocess.PIPE)
        return()
    #
    # Foreground Processing
    #    
    for cmd in joblist:
        jobnum  = jobnum + 1
        window0['_joblist_'].update(set_to_index=jobnum - 1, scroll_to_index=jobnum - 1)
        (job, jobcmd, jobpath, jobbase, jobroot, joblog) = get_job(cmd, option='opmflow')
        jobdat1 = Path(jobroot).with_suffix('.DATA')
        jobdat2 = Path(jobroot).with_suffix('.data')

        if values['_nosim_']:
            jobcase = jobcmd + str(jobbase) + ' --enable-dry-run="true"' + ' | tee ' + str(joblog)
            print(jobcase)

        if values['_rusim_']:
            jobcase = jobcmd + str(jobbase)  + ' | tee ' + str(joblog)

        if event == 'Cancel' or event == None:
            out_log('Job Processing Canceled', outlog, True)
            return()

        if event == 'Submit':
            #
            # Disable Buttons 
            #
            set_button_status(True)
            out_log('Run Job ' + str(jobnum) + ' of ' + str(len(joblist)), outlog)
            out_log('Start Job: ' + jobcase, outlog)
            #
            # Change Working Directory
            #
            error = set_directory(jobpath, outlog=False)
            if error == False:
                out_log('End   Job: ' + jobcase, outlog)
                out_log('Completed Job No. ' + str(jobnum), outlog)
                out_log('', outlog)
                continue
            #
            # Check if DATA File Exists
            #
            if jobdat1.is_file():
                jobdata = jobdat1
            elif jobdat2.is_file():
                jobdata = jobdat2
            else:
                sg.popup_error('Data file ' + str(jobdat1) + ' or ' + str(jobdat2) + ' do not exist; aborting job?',
                                non_blocking=False, auto_close=True, auto_close_duration=5,
                                no_titlebar=True, grab_anywhere=True, keep_on_top=True)
                out_log('Aborted  : Missing ' + str(jobdat1) + ' or ' + str(jobdat2), outlog)
                out_log('End   Job: ' + jobcase, outlog)
                out_log('Completed Job No. ' + str(jobnum), outlog)
                out_log('', outlog)
                continue
            #
            # Check if PARAM File Exists
            #
            if not Path(jobbase).is_file():
                text = sg.popup_ok_cancel('Parameter file ' + str(jobbase) + ' does not exists; do you wish to use ' +
                                          'the current default PARAM set, or cancel the job?',
                                          no_titlebar=True, grab_anywhere=True, keep_on_top=True)
                if text == 'Cancel':
                    out_log('Cancelled: Missing ' + jobbase, outlog)
                    out_log('End   Job: ' + jobcase, outlog)
                    out_log('Completed Job No. ' + str(jobnum), outlog)
                    out_log('', outlog)
                    continue
                else:
                     save_parameters(jobdata, jobparam, jobbase, job, jobsys)
                     out_log('Missing  : Using default PARAM set ' + jobbase, outlog)
            #
            # Remove Existing Output Files
            #
            out_log('Removing Existing Output Files', outlog)
            for text in ['.DBG', '.EGRID', '.INIT', '.LOG', '.PRT', '.RSM', '.SMSPEC', '.UNRST', '.UNSMRY',
                         '.dbg', '.egrid', '.init', '.log', '.prt', '.rsm', '.smspec', '.unrst', '.unsmry' ]:
                filename = Path(jobbase).with_suffix(text)
                if filename.is_file():
                    try:
                        filename.unlink()
                        out_log('   rm ' + str(filename), outlog)
                    except OSError:
                        out_log('   rm ' + str(filename) + ' Failed - File in Use', outlog)
                        continue
            #
            # Run Job
            #
            print(jobcase)
            out_log('Simulation Started', outlog)
            run_job(jobcase)
            #
            # Job Complete
            #
            os.chdir(jobpath)
            filename = joblog
            if not filename.exists():
                sg.Print('Debug Start')
                sg.Print('   Log File Not Found Error')
                sg.Print('   Current Working Directory ' , str(Path().absolute()))
                sg.Print('   Log File                  ' , joblog)
                sg.Print('Debug End')
            else:
                file          = open(filename, 'r')
                lines, status = tail(file, 11, offset=None)
                file.close()
                if status:
                    for line in enumerate(lines):
                        if line[1] == '':
                            continue
                        out_log(line[1], outlog)
            out_log('End   Job: ' + jobcase, outlog)
            out_log('Completed Job No. ' + str(jobnum), outlog)
            out_log('', outlog)
            opmlog.flush()
    #
    # Enable Buttons
    #
    set_button_status(False)

    return()


def run_process(command, outprt=True):
    """Run a Command as a Sub-Process

    Run a command as a subprocess.

    Parameters
    ----------
    command : str
        The command to be run
    outprt: bool
        A boolean print option (True to print to display, False not to print)

    Returns
    -------
    out : str
        Returns output from sub-process if requested by `outprt`
    """

    err = ''
    out = ''
    sp  = ''
    try:
        sp       = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        out, err = sp.communicate()
        if out and outprt == True:
            print(out[0].decode("utf-8"))

    except:
        sg.PopupError('Subprocess Call Error: ' + str(command) + '\n \n'
                      'OUT:' + str(out.decode("utf-8")) + 'ERR:' + str(err) + '\n',
                      no_titlebar=True, grab_anywhere=True, keep_on_top=True)
        pass

    if out:
        return out[1]
    else:
        return()


def run_resinsight(command):
    """Run ResInsight

    Runs ResInsight for viewing results of OPM Flow runs. The command itself is stored in the opmoptn dictionary

    Parameters
    ----------
    command : str
        Command string to invoke OPM ResInsight

    Returns
    -------
    None
    """

    if command == 'None':
        sg.PopupOK('OPM ResInsight Command has not been defined in the Options.',
                   'Use the Edit Options menu to define the command.',
                   no_titlebar=True, grab_anywhere=True, keep_on_top=True)
        out_log('ResInsight Command: ' + str(command) + ' is Undefined', True)
        return()

    try:
        out_log('Executing ResInsight Command: ' + str(command) , True)
        subprocess.Popen(command)

    except Exception:
        sg.PopupError('OPM ResInsight Not Found: ' + command,
                      no_titlebar=True, grab_anywhere=True, keep_on_top=True)
        out_log('Executing ResInsight Command Error: ' + str(command), True)

    return()


def save_jobs(joblist, jobtype, jobsys, outlog=True):
    """ Save OPM Flow Jobs to File

    Save OPMRUN jobs in the job queue to a file in the users #Home directory called #HOME/OPM/OPMRUN.job. This is used
    to run jobs in background mode, as oppose to foreground mode.

    Parameters
    ----------
    joblist : list
        List of jobs in the job queue
    jobtype :str
        Type of job for this queue
    jobsys : dict
        Contains a dictionary list of all OPMRUN System parameters
   outlog: bool
        A boolean print option for the log file (True to print to display, False not to print)

    Returns
    -------
    None
    """

    jobnum = 0
    file   = open(jobsys['opmjob'], 'w')
    file.write('# \n')
    file.write('# OPMRUN Job File \n')
    file.write('# \n')
    file.write('# File Name   : '  + str(jobsys['opmjob']) + '\n')
    file.write('# Created By  : '  + str(jobsys['opmuser']) + '\n')
    file.write('# Date Created: '  + get_time() + '\n')
    file.write('# \n')
    for cmd in joblist:
        jobnum  = jobnum + 1
        (job, jobcmd, jobpath, jobbase, jobroot, joblog) = get_job(cmd, option='opmflow')

        if jobtype == '_nosim_':
            jobcase = jobcmd + str(jobbase) + ' --enable-dry-run="true"' + ' | tee ' + str(joblog)
        else:
            jobcase = jobcmd + str(jobbase)  + ' | tee ' + str(joblog)

        file.write('# \n')
        file.write('# Job Number ' + str(jobnum) + ' \n')
        file.write('# \n')
        file.write('cd ' + str(jobpath) + ' \n')
        file.write(jobcase + ' \n')

    file.write('# \n')
    file.write('# End of OPMRUN Jobs File \n')
    file.close()
    subprocess.call(['chmod', 'u=rwx', jobsys['opmjob']])
    if outlog:
        out_log('OPMRUN Jobs File Saved: ' + str(jobsys['opmjob']), outlog)


def save_options(opmsys, opmoptn, outlog=True):
    """Save OPMRUN options to File

    Save OPMRUN options to file in the users #HOME directory in a file named #HOME/OPM/OPMRUN.ini

    Parameters
    ----------
    opmsys : dict
        Contains a dictionary list of all OPMRUN System parameters
    opmoptn : dict
        Contains a dictionary list of all OPMRUN options
    outlog: bool
        A boolean print option for the log file (True to print to display, False not to print)

    Returns
    -------
    None
    """

    file  = open(opmsys['opmini'], 'w')
    file.write('# \n')
    file.write('# OPMRUN Options File \n')
    file.write('# \n')
    file.write('# File Name   : '  + str(opmsys['opmini']) + '\n')
    file.write('# Created By  : '  + str(opmsys['opmuser']) + '\n')
    file.write('# Date Created: '  + get_time() + '\n')
    file.write('# \n')
    for key, value in opmoptn.items():
        if str(value).isdigit:
            file.write(str(key) + '=' + str(value) + ' \n')
        else:
            file.write(str(key) + '="' + str(value) + '" \n')
    file.write('# \n')
    file.write('# End of OPMRUN Options File \n')
    file.close()
    if outlog:
        out_log('OPMRUN Options File Saved: ' + str(opmsys['opmini']), outlog)


def save_parameters(job, jobparam, jobbase, jobfile, jobsys):
    """Save a Job's Parameter File

    Functions saves the current default parameter set to a job's parameter file that used to run an OPM Flow job. The
    file also contains some additional comments including the user who created the job for documentation.

    Parameters
    ----------
    job : str
        The job for which the PARAM file is being generated
     jobparam : list
        OPM Flow PARAM parameter list
    jobbase :str
        The base part of the job file name
    jobfile
        The full job file name
    jobsys : dict
        Contains a dictionary list of all OPMRUN System parameters

    Returns
    -------
    None
    """

    file  = open(jobfile, 'w')
    file.write('# \n')
    file.write('# OPMRUN Parameter File \n')
    file.write('# \n')
    file.write('# File Name   : "' + str(jobfile) + '"\n')
    file.write('# Created By  : '  + str(jobsys['opmuser']) + '\n')
    file.write('# Date Created: '  + get_time() + '\n')
    file.write('# \n')
    for x in jobparam:
        if 'EclDeckFileName' in x:
            file.write('EclDeckFileName="' + Path(job).name  + '"\n')
        elif 'ecl-deck-file-name' in x:
            file.write('ecl-deck-file-name="' + Path(job).name  + '"\n')
        else:
            file.write(x + '\n')
    file.write('# \n')
    file.write('# End of Parameter File \n')
    file.close()
    sg.PopupOK(str(jobbase) + ' parameter file written to:', str(jobfile),
               'Complete', no_titlebar=True, grab_anywhere=True, keep_on_top=True)


def save_queue(joblist, opmuser):
    """Save Job Queue to File

    Save the current job queue to a user selected file that can be loaded back into OPMRUN to re-run jobs when
    required

    Parameters
    ----------
    joblist : list
        Job list for queue
    opmuser: str
        User name

    Returns
    -------
    None
    """

    if not joblist:
        sg.PopupOK('No Cases In Job Queue; Queue will Not Be Saved',
                   no_titlebar=True, grab_anywhere=True, keep_on_top=True)
    else:
        filename = sg.PopupGetFile('OPMRUN Queue File Name', default_extension='que', save_as=True,
                                   default_path=str(Path().absolute()), keep_on_top=False,
                                   file_types=[('OPM Queues', '*.que'), ('All', '*.*')])
        if filename:
            file       = open(filename, 'w')
            file.write('# \n')
            file.write('# OPMRUN Queue File \n')
            file.write('# \n')
            file.write('# Created By  : '  + opmuser + '\n')
            file.write('# Date Created: '  + get_time() + '\n')
            file.write('# Queue Length: ' + str(len(joblist)) + '\n')
            file.write('# \n')
            for x in joblist:
                file.write(x + '\n')
            file.write('# \n')
            file.write('# End of Queue \n')
            file.close()
            sg.PopupOK('OPMRUN Queue File Saved to: ' + filename,
                       no_titlebar=True, grab_anywhere=True, keep_on_top=True)


def set_button_status(status, all=False):
    """Set Main Window Button Status

    Sets the display buttons for the main window to enabled (False) or disable (True) depending on the value of status.

    Parameters
    ----------
    status : bool
         Boolean that sets the display buttons to enabled (False) or disable (True)

    Returns
    -------
    None
    """

    window0['_add_job_'    ].update(disabled=status)
    window0['_delete_job_' ].update(disabled=status)
    window0['_edit_job_'   ].update(disabled=status)

    window0['_clear_queue_'].update(disabled=status)
    window0['_load_queue_' ].update(disabled=status)
    window0['_save_queue_' ].update(disabled=status)

    window0['_run_jobs_'   ].update(disabled=status)
    window0['_clear_'      ].update(disabled=status)
    window0['_exit_'       ].update(disabled=status)

    if all:
        window0['_kill_job_'].update(disabled=status)


def set_directory(jobpath, outlog=True, outpop=False, outprt=True, window=None):
    """Set the Job Path

    Set the current directory to the job's path (`jobpath`)

    Parameters
    ----------
    jobpath : str
        The path of the job for which the change directory request is being executed
    outlog :bool
        Boolean log file output (True to write to log file, False not to write)
    outpop : bool
        Boolean Popup display option (True to display Popup, False no display)
    outprt : bool
         Boolean print option (True to print to display, False not to print)
    window : PySimpleGUI window
        The PySimpleGUI window that the output is going to (needed to do refresh on)

    Returns
    -------
    True if successful, otherwise False
    """

    try:
        os.chdir(jobpath)
        if outprt:
            print('Current Working Directory ' , str(Path().absolute()))

        if window is not None:
            window['_outlog1_'].update('Working Directory ' + str(Path().absolute()) + '\n', append=True)

    except OSError:
        if outpop or window is not None:
            sg.PopupError('Change Working Directory Error \n'
                          'Please See Log Output',
                          no_titlebar=True, grab_anywhere=True, keep_on_top=True)

        out_log('Cannot Change the Current Working Directory', outlog, outprt)
        out_log(str(jobpath), outlog, outprt)
        return False

    return True


def set_directory_project(key, opmoptn):
    """Sets the Default Directory Based On Project Directory

    Sets the default directory via the project name/directory variable in the opmoptn dictionary. This is used when
    selecting files for job submission etc

    Parameters
    ----------
    key ; str
        The project name to look up in opmoptn to get the directory name to set to the current directory
    opmoptn : dict
        Contains the project names and their associated directories.

    Returns
    -------
    None
    """

    key = key[(key.find('_') + 1):-1]
    name = opmoptn.get(key)
    if name == None or name == '':
        sg.PopupError('Project Name ' + key + ' not Found',
                      no_titlebar=True, grab_anywhere=True, keep_on_top=True)
        return()
    dirc = key.replace('name', 'dirc')
    dirc = opmoptn.get(dirc)
    if dirc == None or dirc == '':
        sg.PopupError('Project Directory ' + dirc + ' not Found',
                      no_titlebar=True, grab_anywhere=True, keep_on_top=True)
        return()

    status = set_directory(Path(dirc), True, True, False)
    if status:
        sg.PopupOK('Change Directory',
                   'Project Name: '     + name + '\n' +
                   'Project Directory:' + dirc + '\n',
                   no_titlebar=True, grab_anywhere=True, keep_on_top=True)


def set_menu(opmoptn):
    """Set the Main Window Menus

    Set the main window menus for the first time to display, and for when the menu needs to be updated. Used for when
    the menu changes due to the projects being edited to use:

        menulayout = set_menu(opmoptn)

    to initialize the menu structure, and

        mainmenu.update(menulayout)

    to update then menus after the projects names have been edited

    Parameters
    ----------
    opmoptn : dict
        Contains a dictionary list of all OPMRUN run parameters


    Returns
    -------
    None
    """

    menu  = [['File',  ['Open',
                        'Project',
                                  [opmoptn['prj-name-01'] + '::_prj-name-01_',
                                   opmoptn['prj-name-02'] + '::_prj-name-02_',
                                   opmoptn['prj-name-03'] + '::_prj-name-03_',
                                   opmoptn['prj-name-04'] + '::_prj-name-04_',
                                   opmoptn['prj-name-05'] + '::_prj-name-05_'],
                        'Save',
                        'Exit'
                        ]
              ],
             ['Edit',  ['Edit Parameters',
                        'List Parameters',
                        'Set Parameters',
                        'Options',
                        'Projects'],
              ],
             ['Tools', ['Compress Jobs',
                                        ['Compress Jobs',
                                         'Uncompress Jobs'],
                        'Deck Generator',
                                        ['Keyword Generator'],
                        'ResInsight'],],
             ['Help',  ['Manual',
                        'Help',
                        'About'],
              ]]
    return menu


def set_window_status(status):
    """Set the Main Window Status

    Set the main window status to active or inactive for when a second window is being displayed.

    Parameters
    ----------
    status ; bool
        Boolean that sets the window status, True for active and False for inactive

    Returns
    -------
    None
    """

    if status:
        # window0.enable()   Not Working Causes Display to Freeze on Linux Systems
        set_button_status(False, True)
        window0.SetAlpha(1.00)
        window0.refresh()

    else:
        window0.SetAlpha(0.85)
        set_button_status(True, True)
        #window0.disable()()  Not Working Causes Display to Freeze Linux Systems


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



def uncompress_job(opmoptn):
    """Uncompress All Jobs that Have Been Compressed in a Zip File Using the Base Name

     The function allows the use to select a group of ZIP files for unzipping of all files associated with the case
     name (*.DATA), using the standard unzip utility on Linux systems

     Parameters
     ----------
    opmoptn; dict
        A dictionary containing the OPMRUN default parameters

     Returns
     ------
     None
     """

    set_window_status(False)

    joblist1 = []
    layout1  = [[sg.Text('Select Multiple Archive Files to Uncompress'                           )],
                [sg.Listbox(values='', size=(100, 10), key='_joblist1_',
                            font=(opmoptn['output-font'], opmoptn['output-font-size']))],
                [sg.Text('Output')],
                [sg.Multiline(key='_outlog1_', size=(100, 15), text_color='blue', autoscroll=True,
                              font=(opmoptn['output-font'], opmoptn['output-font-size']))],
                [sg.Text('Uncompression Options'                                                 )],
                [sg.Radio('Uncompress and Keep Existing Files'        , "bRadio1", default=True,
                          key='_bRadio1_'                                                        )],
                [sg.Radio('Uncompress and Overwrite Existing Files'   , "bRadio1"                )],
                [sg.Text('Compressed File Options'                                               )],
                [sg.Radio('Keep Compressed File After Uncompressing'  , "bRadio2", default=True,
                          key='_bRadio2_'                                                        )],
                [sg.Radio('Delete Compressed File After Uncompressing', "bRadio2"                )],
                [sg.Button('Add'), sg.Button('Clear',  tooltip='Clear Output'), sg.Button('List'),
                                   sg.Button('Remove', tooltip='Remove Zip Files'), sg.Submit(), sg.Cancel()]]
    window1 = sg.Window('Uncompress Job Files', layout=layout1)

    while True:
        (event, values) = window1.Read()

        if event == 'Add':
            jobs = sg.PopupGetFile('Select ZIP Files to Uncompress', no_window=False,
                                   default_path=str(Path().absolute()), initial_folder=str(Path().absolute()),
                                   multiple_files=True, file_types=[('zip', ['*.zip', '*.ZIP'])])
            if jobs != None:
                jobs = jobs.split(';')
                for job in jobs:
                    joblist1.append(job)

                window1['_joblist1_'].update(joblist1)
            continue
        #
        # Clear Output
        #
        if event == 'Clear':
            window1['_outlog1_'].update('')
            continue
        #
        # Get Directory and List Files
        #
        if event == 'List':
            jobpath = sg.PopupGetFolder('Select Directory', no_window=False,
                                        default_path=str(Path().absolute()), initial_folder=str(Path().absolute()))
            if jobpath != None:
                set_directory(jobpath, outlog=False, outpop=False, outprt=False, window=window1)

            jobpath = Path().absolute()
            for file in Path(jobpath).glob("*.zip"):
                window1['_outlog1_'].update(str(Path(file).name) + '\n', append=True)

            for file in Path(jobpath).glob('*.ZIP'):
                window1['_outlog1_'].update(str(Path(file).name) + '\n', append=True)

            window1['_outlog1_'].update('Listing Complete ' + str(jobpath) + '\n', append=True)
            continue
        #
        # Remove Files
        #
        if event == 'Remove':
            joblist1 = []
            window1['_joblist1_'].update(joblist1)
            continue
        #
        # Uncompress Files
        #
        if event == 'Submit':
            if values['_bRadio1_']:
                zipcmd = 'unzip -u -n '
            else:
                zipcmd = 'unzip -u -o '

            jobnum = -1
            for cmd in joblist1:
                jobnum = jobnum + 1
                window1['_joblist1_'].update(set_to_index=jobnum , scroll_to_index=jobnum)
                window1['_outlog1_'].update('\n', append=True)
                out_log('Start Uncompress', True, False, window=window1)
                (job, jobcmd, jobpath, jobbase, jobroot, jobfile, jobzip) = get_job(cmd, option='zip')
                set_directory(jobpath, outlog=False, outpop=False, outprt=False, window=window1)
                jobcmd = zipcmd + str(jobzip)
                out_log('   ' + jobcmd, True, False, window1)
                window1['_outlog1_'].update(str(jobpath), append=True)
                run_command(jobcmd, timeout=None, window=window1)
                if values['_bRadio2_'] == False:
                    jobcmd = 'rm -v ' + str(jobzip)
                    out_log('   ' + jobcmd, True, False, window1)
                    run_command(jobcmd, timeout=None, window=window1)

                out_log('End Uncompressing', True, False, window1)
                window1.refresh()

            window1['_joblist1_'].update(joblist1)
            continue

        if event == 'Cancel' or event == None:
            break

    window1.Close()
    set_window_status(True)
    return()


def opmrun():
    """OPMRUN Main Program

    The program allows the user to select files to be submitted to OPM Flow and has a variety of features.
    OPMRUN is a Graphical User Interface ("GNU") program for the Open Porous Media ("OPM") Flow simulator.
    The software enables submitting OPM Flow simulation input decks together with editing of the associated PARAM file,
    as well as being able to compress and uncompress OPM Flow's output files in order to save disk space.

    In addition there is an OPM Flow Keyword Generation Utility module that generates input decks based of the keywords
    available for the simulator which users the Apache Velocity Template Language ("VTL") for the templates.

    Parameters
    ----------


    Returns
    -------
    None
    """
    # ------------------------------------------------------------------------------------------------------------------
    # Pre-Processing Section
    # ------------------------------------------------------------------------------------------------------------------
    #
    # Initialize
    #
    global jobhelp
    global joblist
    global jobparam
    global joblist

    jobhelp  = dict()
    joblist  = []
    jobparam = []

    global opmoptn
    global opmlog
    global opmsys
    global window0
    #
    # OPMRUN Startup Setup System Variables and File Creation
    #
    opmlog          = ''
    opmsys          = dict()
    opmsys, opmlog = opm_startup(opmsys, opmlog)
    #
    # Load OPMRUN Configuration Parameters and Set Last Working Directory as Default
    #
    opmoptn           = dict()
    opmoptn           = load_options(opmoptn, opmsys)
    try:
        os.chdir(opmoptn['prj-dirc-00'])

    except IsADirectoryError:
        opmoptn['prj-dirc-00'] = opmsys['opmhome']
        os.chdir(opmoptn['prj-dirc-00'])
    #
    # Run OPM Flow Help and Store Command Line Parameters
    #
    jobparam, jobhelp = load_parameters(opmsys['opmparam'], outpop=False)
    #
    # Define General Text Variables
    #
    abouttext = (
                'OPMRUN is a Graphical User Interface ("GNU") program for the Open Porous Media ("OPM") Flow ' +
                'simulator. The software enables submitting OPM Flow simulation input decks together with editing of ' +
                'the associated PARAM file. \n' +
                '\n' +
                'This file is part of the Open Porous Media project (OPM). OPM is free software: you can redistribute '+
                'it and/or modify it under the terms of the GNU General Public License as published by the Free ' +
                'Software Foundation, either version 3 of the License, or (at your option) any later version. \n' +
                '\n' +
                'OPM is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the ' +
                'implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the aforementioned ' +
                'GNU General Public Licenses for more details. \n' +
                '\n' +
                'OPMRUN Version: ' + str(opmsys['opmvers']) + '\n'
                'OPMRUN GUI Module: ' + str(opmsys['opmgui']) + '\n'
                '\n' +
                'Copyright (C) 2018-2020 Equinox International Petroleum Consultants Pte Ltd. \n'
                '\n' +
                'Author  : David Baxendale (david.baxendale@eipc.co)')

    helptext = (
                'OPMRun is a Graphical User Interface ("GUI") program for the Open Porous Media ("OPM") Flow ' +
                'simulator. \n' +
                '\n'
                'The intent is for OPMRUN to have similar functionality to the commercial simulator’s program, with ' +
                'the targeted audience being Reservoir Engineers in a production environment.  Developers and ' +
                'experienced Linux users will already have compatible work flows.  OPMRUN enables the editing and ' +
                'management of OPM Flow’s run time parameters, setting up job queues to run a series of simulation ' +
                ' jobs sequentially, as well as the management of the job queues. Features include: \n' +
                '\n'
                'Projects allow setting "default" directories to enable shortcuts to frequent directories for ' +
                'selecting input decks and job queues. \n' +
                '\n'
                'Input decks can be added to a job queue for processing and the input deck and the associated ' +
                'parameter file can be edited. The input deck is edited via a user selected editor and the parameter ' +
                'file is edited interactively in OPMRUN. \n' +
                '\n'
                'Default parameters can be loaded from OPM Flow, an existing PARAM file or a PRINT file. \n' +
                '\n'
                'Job queues can be edited, loaded and saved, and jobs in the job queue can all be run in "NOSIM" mode '+
                'to verify the input decks, or "RUN" mode, without editing the input decks. \n' +
                '\n'
                'Jobs in the job queue can be run in foreground mode under OPMRUN, or background in a xterm terminal.' +
                'The latter is slightly more computationally efficient than the foreground mode. \n' +
                '\n'
                'The Tools menu allows one to:\n' +
                '\n'
                '(1) Compress and uncompress the input and output files into one ZIP file to save disk space.\n' +
                '(2) Deck Generator - Keyword Generator to generator input decks. \n' +
                '(3) Launch OPM ResInsight the open source post processing visualization program. \n' +
                '\n'
                'Finally, the Edit Options menu allows for editing OPMRUN options, set the OPM Flow Manual location, ' +
                'default editor command, ResInsight command etc. \n' +
                '\n'
                'See the OPM Flow manual for further information. \n')

    # ------------------------------------------------------------------------------------------------------------------
    # Define GUI Section
    # ------------------------------------------------------------------------------------------------------------------
    #
    # Initialize GUI Setup and Define Main Window
    #
    opm_initialize()

    menulayout = set_menu(opmoptn)
    mainmenu   = sg.Menu(menulayout)

    flowlayout = [[sg.Output(background_color='white', text_color='black',
                             size=(opmoptn['output-width'], opmoptn['output-heigt']),
                             key='_outflow_', font=(opmoptn['output-font'], opmoptn['output-font-size']))]]

    loglayout  = [[sg.Multiline(background_color='white', text_color='darkgreen', do_not_clear=True,
                                key='_outlog_', size=(opmoptn['output-width'], opmoptn['output-heigt']),
                                font=(opmoptn['output-font'], opmoptn['output-font-size']))]]

    mainwind   = [[mainmenu],
                  [sg.Text('OPM Flow Command Schedule')],
                  [sg.Listbox(values=joblist, size=(opmoptn['input-width'], opmoptn['input-heigt']), key='_joblist_',
                              font=(opmoptn['output-font'], opmoptn['output-font-size']))],

                  [sg.Button('Add Job'       , key='_add_job_'    ),
                      sg.Button('Edit Job'   , key='_edit_job_'   ),
                      sg.Button('Delete Job' , key='_delete_job_' ),
                      sg.Button('Clear Queue', key='_clear_queue_'),
                      sg.Button('Load Queue' , key='_load_queue_' ),
                      sg.Button('Save Queue' , key='_save_queue_' )],

                  [sg.TabGroup([[sg.Tab('Output', flowlayout, key='_tab_outflow_',
                                        title_color='black', background_color='white'),
                                 sg.Tab('Log'    , loglayout , key='_tab_outlog_'     ,
                                        title_color='darkgreen', background_color='white', border_width=None)]],
                               key='_tab_out_', title_color='black', background_color='white')],

                  [sg.Button('Run Jobs'   , key='_run_jobs_'),
                      sg.Button('Kill Job', key='_kill_job_'),
                      sg.Button('Clear'   , key='_clear_'   ),
                      sg.Button('Exit'    , key='_exit_'    )],
                  [sg.Text('')]]

    window0 = sg.Window('OPMRUN - Flow Job Scheduler ',
                        layout=mainwind, disable_close=True, finalize=True, location=(300, 100))

    out_log('OPMRUN Started', True, True)
    out_log('Working Directory set to ' + str(opmoptn['prj-dirc-00']), False, False)

    # ------------------------------------------------------------------------------------------------------------------
    # Define GUI Event Loop, Read Buttons, and Make Callbacks etc. Section
    # ------------------------------------------------------------------------------------------------------------------
    while True:
        #
        # Read the Form and Process and Take appropriate action based on event
        #
        event, values = window0.Read()
        joblist = window0['_joblist_'].GetListValues()
        #
        # Get Main Window Location and Set Default Location for other Windows
        #
        x = int((window0.Size[0] / 2) + window0.CurrentLocation()[0])
        y = int((window0.Size[1] / 4) + window0.CurrentLocation()[1])
        sg.SetOptions(window_location=(x, y))
        #
        # About
        #
        if event == 'About':
            opm_popup('About', abouttext, 20)
            continue
        #
        # Add Job
        #
        elif event == '_add_job_':
            add_job(joblist, jobparam, opmsys)
            continue
        #
        # Clear Log
        #
        elif event == '_clear_':
            if window0['_tab_out_'].get() == '_tab_outlog_':
                window0['_outlog_'].update('')
            if window0['_tab_out_'].get() == '_tab_outflow_':
                window0['_outflow_'].update('')
            continue
        #
        # Clear Queue
        #
        elif event == '_clear_queue_':
            clear_queue(values['_joblist_'])
            continue
        #
        # Compress Jobs
        #
        elif event == 'Compress Jobs':
            compress_job(opmoptn)
            continue
        #
        # Delete Job
        #
        elif event == '_delete_job_':
            delete_job(joblist, values['_joblist_'])
            continue
        #
        # Edit Job
        #
        elif event == '_edit_job_':
            edit_job(values['_joblist_'], opmsys, **jobhelp)
            continue
        #
        # Edit Options
        #
        elif event == 'Options':
            opmoptn = edit_options(opmsys, opmoptn)
            continue
        #
        # Edit Parameters
        #
        elif event == 'Edit Parameters':
            (jobparam, exitcode) = edit_parameters(jobparam, **jobhelp)
            continue
        #
        # Edit Projects
        #
        elif event == 'Projects':
            opmoptn    = edit_projects(opmoptn, opmsys)
            menulayout = set_menu(opmoptn)
            mainmenu.update(menulayout)
            continue
        #
        # Exit
        #
        elif event == '_exit_' or event == 'Exit':
            text = sg.PopupYesNo('Exit OPMRUN?', no_titlebar=True, grab_anywhere=True, keep_on_top=True)
            if text == 'Yes':
                text = sg.PopupYesNo('Are You Sure You wish to Exit OPMRUN?', no_titlebar=True,
                                     grab_anywhere=True, keep_on_top=True)
                if text == 'Yes':
                    break
        #
        # Help
        #
        elif event == 'Help':
            opm_popup('Help', helptext, 35)
            continue
        #
        # List Parameters
        #
        elif event == 'List Parameters':
            if jobparam:
                print('Start of OPM Flow Parameters')
                for k in enumerate(jobparam):
                    print('{}: {}'.format(*k))
                print('End of OPM Flow Parameters')
            else:
                sg.PopupError('OPM Flow Parameters Have Not Been Set',
                              no_titlebar=True, grab_anywhere=True, keep_on_top=True)
            continue
        #
        # Keyword Generator
        #
        elif event == 'Keyword Generator':
            set_window_status(False)
            keyw_main(opmsys['opmvers'], **opmoptn)
            set_window_status(True)
            continue
        #
        # Load Queue
        #
        elif event == '_load_queue_' or event == 'Open':
            joblist = load_queue(joblist, jobparam)
            continue
        #
        # Manual
        #
        elif event == 'Manual':
            load_manual(opmsys, opmoptn['opm-flow-manual'])
            continue
        #
        # ResInsight
        #
        elif event == 'ResInsight':
            run_resinsight(opmoptn['opm-resinsight'])
            continue
        #
        # Run Jobs
        #
        elif event == '_run_jobs_':
            run_jobs(joblist, opmsys, True)
            continue
        #
        # Save Queue
        #
        elif event == '_save_queue_' or event == 'Save':
            save_queue(joblist, opmsys['opmuser'])
            continue
        #
        # Set Parameters
        #
        elif event == 'Set Parameters':
            jobparam = default_parameters(jobparam, opmsys['opmparam'])
            continue
        #
        # Set Project
        #
        elif event.find('::_prj-name') != -1:
            set_directory_project(event, opmoptn)
            continue
        #
        # Uncompress Jobs
        #
        elif event == 'Uncompress Jobs':
            uncompress_job(opmoptn)
            continue

    # -------------------------------------------------------------------------------------------------------------------
    # Post Processing Section
    # ------------------------------------------------------------------------------------------------------------------
    #
    # Close Main Window
    #
    window0.Close()
    #
    # Save Working Directory and Exit
    #
    opmoptn['prj-dirc-00'] = str(Path().absolute())
    save_options(opmsys,opmoptn, True)

    out_log('OPMRUN Processing Complete ', True)
    opmlog.close()
    exit('OPMRUN Complete')

# ----------------------------------------------------------------------------------------------------------------------
# Execute Module
# ----------------------------------------------------------------------------------------------------------------------
if __name__ == '__main__':
    opmrun()

# ======================================================================================================================
# End of OPMRUN.py
# ==========================================================================================================           