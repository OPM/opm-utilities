# coding: utf-8
# ======================================================================================================================
#
"""OPMRUN.py - Run OPM Flow

OPMRUN is a Graphical User Interface ("GNU") program for the Open Porous Media ("OPM") Flow simulator.
The software enables submitting OPM Flow simulation input decks together with editing of the associated PARAM file,
as well as compressing and uncompress OPM Flow's input and output files in order to save disk space. This is the main
code based which allows for incorporating additional tools via the Tool menu. See the OPMRUN function for further
details.

PySimpleGUI is the GUI tool used to build OPMRUN. It is in active development and is frequently updated for fixes and
new features. Each release of OPMRUN will update to the latest release of PySimpleGUI.

Program Documentation
---------------------
Only Python 3 is supported and tested Python2 support has been depreciated.

2021.07-01  - Implemented support for Windows 10 WSL. OPMRUN can now run under Windows 10 and run OPM Flow via WSL with
              the same functionality as that under Linux. For running under WSL the terminal type should be set to wsl
              under the Edit/Options menu item. The compression/uncompression tool has also been implemented under WSL
              using the same linux commands, as the Windows 10 command line tools have limited functionality. A message
              is now written to the screen if the zip/unzip commands are not available. The WSL option has been tested
              via Unbuntu 20.04 LTS using OPM Flow 20.04.
            - Added the facility to add a directory of jobs recursively with automatic checking and generation of the
              associated parameter files.
              Added additional tools under the Tools Menu:
              (1)  Simulation Input
                   (1) Keywords (Major re-factoring of code to implement loading of an input file and basic editing).
                   (2) Production Schedule to generate production schedule using WCONHIST.
                   (3) Sensitivities (previously available).
                   (4) Well Specification to generate WELSPECS, COMPDATA and COMPLUMP keywords.
              (2) Well Trajectory Conversion to convert Petrel exported trajectories to OPM Resinght format.
            - Added a terminal parameter in order to support various terminals in batch processing, currently konsole,
              mate-terminal and xterm supported. Option can be selected via Edit/Options.
            - Added File/Properties option to list OPMRUN properties.
            - Added Help/System option to display OPM system properties.
            - Improvements to opm-sensitivity and renaming of all functions to be consistent with module name.
            - Add the ability to cancel all jobs in a queue if the user kills a job.
            - Updated keyword and model velocity templates.
            - Major refactoring to improve code readability and moving some common routines to opm-common, including
              moving compress and uncompress routines to separate module.
            - Changed output elements to multi-line elements in order to support color output, also added job queue
              statistics after the all the jobs have been completed in the queue.
            - Upgraded PySimpleGUI~=4.44.0 and also check if this or a later version is installed at run time.
2021.04.01  - Added OPMRUN Sensitivity Case Generator Utility to generate sensitivity cases using a base case run.
            - For the RUN jobs option, the program now checks the parameter file exists, if not then the user has the
              to use the option to use the current. This can happen when a series of jobs are load from a QUE file.
            - Catch Background terminal error when xterm is not available on the system.
            - Added SUMMARY Performance section set of keywords.
            - Change the Output window to to MultiLine for greater flexibility and coloring of the output.
            - Added a COPY option to the main window to copy output to the clipboard.
            - Upgraded PySimpleGUI~=4.41.2
2020.04.05  - Remove debug popup when loading ResInsight with job results.
            - Fixed bug when loading and the default directory does not exist.
2020.04.04  - Add right-click menu options to the status table to edit files, view results, load results into OPM
              ResInsight, etc.
            - Refactor code to improve maintainability, including moving some functions to the opm-common module.
            - Moved various global variables to global dictionary variable opmsys to simplify code, the intention is
              to eventually remove all global variables.
            - Re-factored the manner in which imports are loaded to be more robust and moved to PySimpleGUI~=4.19.0
            - Refactored compress and uncompress routines to be use the print to multiline option.
            - Re-factored job run functions to be more robust in checking for OPM Flow aborts and segmentation faults,
              also added code to kill orphaned mpirun processes caused by segmentation faults.
            - Changed version number and added __version__  variable.
2020.04.03  - Changed version number.
            - Updated all templates to be consistent with OPM Flow manual.
            - Updated documentation for this release.
2020.04.02  - Fix a bug with Compress/Uncompress windows preventing printing to the main Out element. This was because
              these two windows used an an Out element as well, and there can be only one Out element in the
              application. The fix was to use the Multiline element for the Compress/Uncompress windows, this resulted
              in various code changes to other functions.
              Fix initial directory bug when loading a queue. Need to set default and initial directory variables in
              popup_get_file() call.
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
2020.04.01  - Fixed a tKinter bug that centers windows by the total x-direction display space, rather than the using
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
2019.04.05  - Added checks and warnings for importing PySimpleGUI and pathlib/pathlib2 for robustness.
            - Fixed display bug in several popup_get_file() calls and add_job and load_queue functions.
            - Updated program code documentation and the Release-Notes.txt file.
            - Updated README.md file fixing some minor layout issues
2019.04.04  - Added suport for Python 2 by using the pathlib2 module from https://pypi.org/project/pathlib2/
              (not tested).
            - Updated program code documentation and the Release-Notes.txt file.
            - Updated README.md file to based on PDF documentation
            - Deleted binary file from the repository.
2019.04.03  - Added OPM Flow icon to all Windows via Base64 Encoded PNG File and added OPMRUN.svg icon to release.
            - Changed all Popup messages to have no title bar, grab anywhere, and keep on top options.
            - Moved job parameter manipulation into a separate function get__job function to reduce code duplication,
              as well as to have most of the path manipulation in the one routine.
            - Modified documentation.
            - Re-compiled binary generated tested on Unbuntu-Mate 18-04 and 19-04.
2019.04.02  - Fixed menu layout bug.
            - Fixed Project Directory bug for when the default OPMRUN.ini file is created.
            - Fixed Edit Parameters bug for when OPM Flow has not been installed.
            - Changed some text messages to be consistent with Options.
            - Re-compiled binary generated.
2019.04.01  - Fixed bug in running parallel jobs.
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
2018.10.02  - Fix printing bug associated with listing of jobparam.
              Create stand alone executable for Linux systems (works on Ubuntu-Mate 18-04)
2018.10.01  - Initial release.

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

Note there are other tools for compiling Python code; however, PyInstaller's main advantages over similar tools are that
PyInstaller works with Python 2.7 and 3.4-3.7, it builds smaller executables thanks to transparent compression,
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

Copyright (C) 2018-2021 Equinox International Petroleum Consultants Pte Ltd.

Author  : David Baxendale
          david.baxendale@eipc.co
Date    : 30-July-2021
"""
# ----------------------------------------------------------------------------------------------------------------------
# 3456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890
#        1         2         3         4         5         6         7         8         9         0         1         2
#        0         0         0         0         0         0         0         0         0         1         1         1
# ----------------------------------------------------------------------------------------------------------------------
#
# Set OPMRUN Version Number
#
__version__ = '2021.07.1'

# ----------------------------------------------------------------------------------------------------------------------
# Import Modules and Start Up Section
# ----------------------------------------------------------------------------------------------------------------------

print('OPMRUN Startup: Importing Standard Modules')
#
# Check if tkinter Has Been Installed on the System
#
try:
    import tkinter as tk

except ImportError as error:
    print('   Error importing module')
    print('   ' + str(error) + ' ' + str(type(error)))
    print('   On Linux based systems install tkinter via package manager. \n' +
          '   Debian versions of Linux you have to install it manually by \n' +
          '   using the following command: sudo apt-get install python3-tk')
    print('OPMRUN Startup: Importing Standard Modules Failed')
    exit('Program Will Exit')
#
# Standard Library Modules
#
import getpass
import importlib
import os
import pkg_resources
import platform
import psutil
import subprocess
import sys
from pathlib import Path, PureWindowsPath

print('OPMRUN Startup: Importing Standard Modules Complete')
#
# Check for Python 2 Version
#
print('OPMRUN Startup: Python Version Check')
if platform.python_version_tuple()[0] == '2':
    print('OPMRUN Startup: Program only works with Python 3, Python 2 Support is Depreciated')
    raise SystemExit('Program Will Exit')
print('OPMRUN Startup: Python Version Check Complete')
#
# Import Required Non-Standard Modules
#
print('OPMRUN Startup: Importing Non-Standard Modules')
starterr = False
for package in  {'airspeed', 'numpy', 'pandas', 'psutil', 'pyDOE2', 'PySimpleGUI'}:
    try:
        dist = pkg_resources.get_distribution(package)
        if package == 'PySimpleGUI':
            sg = importlib.import_module(package)
        elif package == 'pandas':
            pd = importlib.import_module(package)
        elif package == 'psutil':
            from psutil import cpu_count
        else:
            importlib.import_module(package)
        print('   Require Module - ' + dist.key + '(' + dist.version + ') Imported')
    except pkg_resources.DistributionNotFound:
        print('   Import Require Package - ' + package + ' Failed')
#       print('Startup: Use "python -m pip install --user ' + package + '" to install')
        print('   Use "pip install ' + package + '" to install')
        starterr = True

if starterr:
    print('   Alternatively use: pip install -r requirements.txt to install required packages')
    print('   Use "python -m pip --verbose list" to get a list of installed packages')
    print('OPMRUN Startup: Importing Non-Standard Modules Failed')
    raise SystemExit('Program Will Exit')

print('OPMRUN Startup: Importing Non-Standard Modules Complete')
#
# Check for Suitable Version of PySimpleGUI
#
try:
    version = sg.__version__
except Exception:
    text = ('PySimpleGUI Version Not Found and is invalid, require version 4.44.0 or higher.' +
            'To upgrade use:\n\n"pip install --user --upgrade PySimpleGUI"\n\nProgram Will Exit')
    sg.popup_error(text, title='PySimpleGUI Version Check', no_titlebar=False, grab_anywhere=False, keep_on_top=True)
    raise SystemExit(text)
if pkg_resources.parse_version(sg.__version__) < pkg_resources.parse_version('4.44.0'):
    text = ('PySimpleGUI Version ' + str(sg.version) + ' is invalid, require version 4.45 or higher.' +
            'To upgrade use:\n\n"pip install --user --upgrade PySimpleGUI"\n\nProgram Will Exit')
    sg.popup_error(text, title='PySimpleGUI Version Check', no_titlebar=False, grab_anywhere=False, keep_on_top=True)
    raise SystemExit(text)
#
# Import OPMRUN Modules
#
from opm_common import (copy_to_clipboard, convert_string, get_time, kill_job, set_gui_options, opm_popup, print_dict,
                        remove_ansii_escape_codes, run_command, tail, wsl_path)
from opm_compress import (change_directory, compress_cmd, compress_files, uncompress_files)
from opm_keyw import keyw_main
from opm_sensitivity import *
from opm_prodsched import *
from opm_wellspec import wellspec_main
from opm_welltraj import welltraj_main
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
#                   'Program will continue', no_titlebar=False, grab_anywhere=False, keep_on_top=True)

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

    ncpu = cpu_count()
    if ncpu > 1:
        bcpu = False
    else:
        bcpu = True

    if not jobparam:
        sg.popup_error('Job Parameters Missing; Cannot Add Cases - Check if OPM Flow is Installed',
                      no_titlebar=False, grab_anywhere=False, keep_on_top=True)
        return()

    layout1 = [[sg.Text('File to Add to Queue')],
               [sg.InputText(key='_jobdir_', size=(80, None)),
                sg.FilesBrowse(target='_jobdir_', initial_folder=Path().absolute(),
                               file_types=[('OPM', ['*.data', '*.DATA']), ('All', '*.*')])],
               [sg.Text('Run and Parameter File Options')],
               [sg.Radio('Sequential Run' , "bRadio", key='_jobseq_', default =True)],
               [sg.Radio('Parallel Run Number of Nodes' , "bRadio", key='_jobpar_', disabled=bcpu),
                sg.Listbox(values=list(range(1, ncpu + 1)), size=(10, 3), key='_jobnode_', default_values=[ncpu],
                           disabled=bcpu),
                sg.Text('Overwrite Parameter\nFile Options'),
                sg.Listbox(values=['Ask', 'Keep', 'Overwrite'], size=(10, 3), key='_jobopt_', default_values='Ask')],
               [sg.Submit(), sg.Exit()]]
    window1 = sg.Window('Select OPM Flow Input File', layout=layout1)

    while True:
        (event, values) = window1.read()
        jobs    = values['_jobdir_']
        jobseq  = values['_jobseq_']
        jobpar  = values['_jobpar_']
        jobnode = values['_jobnode_'][0]
        jobopt  = values['_jobopt_'][0]
        if not jobnode:
            jobnode = 2

        if event == 'Exit' or event is None:
            break

        if event == 'Submit':
            if len(jobs) == 0:
                sg.popup_ok('No Simulation Input Files Found', title='OPMRUN Directory Load',
                            no_titlebar=False, grab_anywhere=False, keep_on_top=True)
                continue

            jobs = jobs.split(';')
            for job in jobs:
                jobbase = Path(job).name
                jobfile = Path(job).with_suffix('.param')
                if jobseq:
                    joblist.append('flow --parameter-file=' + str(jobfile))
                if jobpar:
                    joblist.append('mpirun -np ' + str(jobnode) + ' flow --parameter-file='
                                   + str(jobfile))

                window0['_joblist_'].update(joblist)
                #
                # PARAM File Processing
                #
                if jobfile.is_file() and jobopt == 'Ask':
                    text = sg.popup('Parameter file:', str(jobfile),
                                    'Already exists; do you wish to overwrite it with the current defaults,'
                                    ' or keep the existing parameter file?', custom_text=('Overwrite', 'Keep', None),
                                    title='OPMRUN Directory Load', no_titlebar=False,
                                    grab_anywhere=False, keep_on_top=True)
                    if text == 'Overwrite':
                        save_parameters(job, jobparam, jobbase, jobfile, jobsys)

                if jobfile.is_file() and jobopt == ['Overwrite']:
                    save_parameters(job, jobparam, jobbase, jobfile, jobsys)

            window1['_jobdir_'].update('')

    window1.Close()
    return()


def add_jobs_recursively(joblist, jobparam, jobsys):
    """Add a OPM Flow Simulation Jobs to the Job List Queue Recursively

    The function first checks if OPM Flow is present on the system by examining jobparam, if okay, it then it checks if
    there are existing jobs in the queue, and asks if the queue should be over written, if so the function requests the
    directory to add the data files recurseively into the joblist variable. The function also creates the associated
    parameter files if necessary. Note that the directory selected is applied recursively, that is all data files in the
    selected directory and below will be added to the job queue.

    Parameters
    ----------
    joblist : list
        Current job list in the job queue
    jobparam : list
        OPM Flow PARAM parameter list
    jobsys : dict
        Contains a dictionary list of all OPMRUN System parameters

    Returns
    -------
    joblist : list
        Updated job list via global variable
    """

    ncpu = cpu_count()
    if ncpu > 1:
        bcpu = False
    else:
        bcpu = True
    #
    # Check if OPM Flow Parameters Have Been Set
    #
    if not jobparam:
        sg.popup_error('Job Parameters Missing; Cannot Load Job Queue - Check if OPM Flow is Installed',
                      no_titlebar=False, grab_anywhere=False, keep_on_top=True)
        return()
    #
    # Check Job Queue for Entries
    #
    if joblist:
        text = sg.popup_yes_no('OPMRUN Directory Load Will Delete the Existing Queue, Continue?',
                             no_titlebar=False, grab_anywhere=False, keep_on_top=True)
        if text == 'No':
            return()
    #
    # Load Queue if Valid Entry
    #
    layout1 = [[sg.Text('Load all OPM Flow data files in a directory recursively to the job queue.')],
               [sg.InputText(key='_jobdir_', size=(100, None)),
                sg.FolderBrowse(target='_jobdir_', initial_folder=Path().absolute())],
               [sg.Text('Run and Parameter File Options')],
               [sg.Radio('Sequential Run' , "bRadio", key='_jobseq_', default =True)],
               [sg.Radio('Parallel Run Number of Nodes' , "bRadio", key='_jobpar_', disabled=bcpu),
                sg.Listbox(values=list(range(1, ncpu + 1)), size=(10, 3), key='_jobnode_', default_values=[ncpu],
                           disabled=bcpu),
                sg.Text('Overwrite Parameter\nFile Options'),
                sg.Listbox(values=['Ask','Keep', 'Overwrite'], size=(10,3), key='_jobopt_', default_values='Ask')],
               [sg.Text('\nNote, if the parameter file does not exist for a given data file, then the current ' +
                        'default parameter set will be used\n')],
               [sg.Submit(), sg.Exit()]]
    window1 = sg.Window('Select OPM Flow Input File', layout=layout1)

    while True:
        (event, values) = window1.read()
        jobdir  = values['_jobdir_']
        jobseq  = values['_jobseq_']
        jobpar  = values['_jobpar_']
        jobnode = values['_jobnode_'][0]
        jobopt  = values['_jobopt_'][0]
        if not jobnode:
            jobnode = 2

        if event == 'Exit' or event is None:
            break

        if event == 'Submit':
            if jobdir == '' or not Path(jobdir).is_dir():
                sg.popup_ok('Invalid Directory Selected', title='OPMRUN Directory Load',
                            no_titlebar=False, grab_anywhere=False, keep_on_top=True)
                continue

            files = [file for file in Path(jobdir).rglob('*') if file.suffix in ['.DATA', '.data']]

            if len(files) == 0:
                sg.popup_ok('No Simulation Input Files Found', title='OPMRUN Directory Load',
                            no_titlebar=False, grab_anywhere=False, keep_on_top=True)
                continue
            else:
                text = sg.popup_yes_no('Found a Total of ' + str(len(files)) + ' Simulation Input Files.\n',
                                       'Do you wish to add all this files to the job queue?',
                                       title='OPMRUN Directory Load',
                                       no_titlebar=False, grab_anywhere=False, keep_on_top=True)
                if text == 'No':
                    continue

            joblist = []
            for job in files:
                jobbase = Path(job).name
                jobfile = Path(job).with_suffix('.param')
                if jobseq:
                    joblist.append('flow --parameter-file=' + str(jobfile))
                if jobpar:
                    joblist.append('mpirun -np ' + str(jobnode) + ' flow --parameter-file=' + str(jobfile))
                #
                # PARAM File Processing
                #
                if jobfile.is_file() and jobopt == 'Ask':
                    text = sg.popup('Parameter file:', str(jobfile),
                                    'Already exists; do you wish to overwrite it with the current defaults,'
                                    ' or keep the existing parameter file?', custom_text=('Overwrite', 'Keep', None),
                                    title='OPMRUN Directory Load', no_titlebar=False,
                                    grab_anywhere=False, keep_on_top=True)
                    if text == 'Overwrite':
                        save_parameters(job, jobparam, jobbase, jobfile, jobsys)

                if jobfile.is_file() and jobopt == 'Overwrite':
                    save_parameters(job, jobparam, jobbase, jobfile, jobsys)

            window1['_jobdir_'].update('')

 #           set_window_status(True)
            window0['_joblist_'].update(joblist)
 #           set_window_status(False)
            sg.popup_ok('Add Jobs Directory Load: From: ' + jobdir,'A Total of ' + str(len(files)) + ' Jobs Added',
                        'Complete', title='OPMRUN Directory Load',no_titlebar=False, grab_anywhere=False,
                        keep_on_top=True)
            break

    window1.Close()
    return


def clear_queue(joblist1):
    """Clear Job Queue

    Clears the job queue of all jobs

    Parameters
    ----------
    joblist1 : list
        List of jobs in the job queue

    Returns
    ------
    None
    """

    if joblist1 == []:
        sg.popup_ok('No Cases In Job Queue to Delete', no_titlebar=False,
                   grab_anywhere=False, keep_on_top=True)
    else:
        text = sg.popup_yes_no('Delete All Cases in Queue?', no_titlebar=False,
                             grab_anywhere=False, keep_on_top=True)
        if text == 'Yes':
            joblist1 = []
            window0['_joblist_'].update(joblist1)
    return joblist1


def default_parameters(jobparam, opmsys1):
    """Define OPM Flow Default PARAM Parameters

    Function sets the default PARAM parameters for all new cases by loading the parameters from the default set from
    OPM Flow, from an existing PARAM file, or an existing parameter file.

    Parameters
    ----------
    jobparam : list
        Current default PARAM data set
    opmsys1 : dict
        Contains a dictionary list of all OPMRUN System parameters, here the 'opmparam' is the OPM Flow parameter file.
        The complete dictionary is passed to the load_parameters function, to enable both Linux and Windows 10 WSL
        implementations to work.

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
        (event, values) = window1.read()
        if event == 'Submit':
            if values[0]:
                jobparam, jobhelp = load_parameters(opmsys1)
                break

            elif values[1]:
                filename = sg.popup_get_file('OPM Flow Parameter File Name', default_extension='param', save_as=False,
                                           file_types=[('Parameter File', ['*.param', '*.PARAM']), ('All', '*.*')],
                                           keep_on_top=False)
                if filename:
                    file  = open(filename, 'r')
                    for n, x in enumerate(file):
                        if '=' in x:
                            jobparam.append(x.rstrip())
                    file.close()
                    sg.popup_ok('OPM Flow User Parameters Loaded from: ' + filename,
                               no_titlebar=False, grab_anywhere=False, keep_on_top=True)
                    break

            elif values[2]:
                filename = sg.popup_get_file('OPM Flow PRT File Name', default_extension='prt', save_as=False,
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
                            sg.popup_ok('OPM Flow User Parameters Loaded from: ' + filename,
                                       no_titlebar=False, grab_anywhere=False, keep_on_top=True)
                            break
                    break

        elif event == 'Cancel' or event is None:
            break

    window1.Close()
    if not jobparam:
        sg.popup_ok('OPM Flow User Parameters Not Set, Using Previous Values Instead',
                   no_titlebar=False, grab_anywhere=False, keep_on_top=True)
        jobparam = jobparam0

    set_window_status(True)
    return jobparam


def delete_job(joblist, job):
    """Delete OPM Flow job form job Queue

    Deletes an existing job in the job queue from the job queue

    Parameters
    ----------
    joblist : list
        The list of jobs in the jb queue
    job : str
        The currently selected job to be deleted from the job queue

    Returns
    ------
    joblist : list
        Updated job queue via global variable
    """

    if not joblist:
        sg.popup_ok('No Cases in job Queue', no_titlebar=False, grab_anywhere=False, keep_on_top=True)

    elif not job:
        sg.popup_ok('No Case Selected', no_titlebar=False, grab_anywhere=False, keep_on_top=True)
    else:
        text = sg.popup_yes_no('Delete \n ' + job[0] + '?', no_titlebar=False, grab_anywhere=False, keep_on_top=True)
        if text == 'Yes':
            joblist.remove(job[0])
            window0['_joblist_'].update(joblist)


def edit_data(job, jobsys, filetype='.data'):
    """Edit Job Input/Output File

    The function sets up the parameters to call the default editor to edit the selected DATA file .

    Parameters
    ----------
    job : str
        The selected job
    filetype : str
        File suffix type to check if job input/output file exists, checks for upper and lower suffices.

    Returns
    -------
    None
    """

    if not job:
        sg.popup_ok('No Case Selected', no_titlebar=False, grab_anywhere=False, keep_on_top=True)
        return()
    #
    # Edit Data File or Parameter File Option
    #
    job    = str(job[0]).rstrip()
    istart = job.find('=') + 1
    file1  = Path(job[istart:]).with_suffix(filetype.lower())
    file2  = Path(job[istart:]).with_suffix(filetype.upper())
    if file1.is_file():
        file0 = file1
    elif file2.is_file():
        file0 = file2
    else:
        sg.popup_error('Cannot Find  File: ', str(file1),
                      'or ' , str(file2),
                      no_titlebar=False, grab_anywhere=False, keep_on_top=True)
        out_log('Cannot Find: ' + str(file1) + ' or ' + str(file2), True)

        return()
    #
    # Data File Processing
    #
    if opmoptn['edit-command'] == 'None':
        sg.popup_ok('Editor command has not been set in the properties file',
                   'Use Edit OPMRUN Options to set the Editor Command',
                   no_titlebar=False, grab_anywhere=False, keep_on_top=True)
        out_log('Editor Command Has Not Been Set: ' + str(opmoptn['edit-command']), True)
        return()
    else:
        command = str(opmoptn['edit-command']).rstrip()
        out_log('Executing Editor Command: ' + command + ' ' + str(file0), True)

        try:
            subprocess.Popen([command, str(file0)])
        except Exception as error:
            sg.popup_error('Error Executing Editor Command: ' + command + ' ' + str(file0),
                           str(error) + ': ' + str(type(error)),
                           no_titlebar=False, grab_anywhere=False, keep_on_top=True)
            out_log('Error Executing Editor Command: ' + command + ' ' + str(file0), True)
            return()

    return()


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

    if not job:
        sg.popup_ok('No Case Selected', no_titlebar=False, grab_anywhere=False, keep_on_top=True)
        return()
    #
    # Display Edit Options
    #
    #
    jobfile  = str(job[0]).rstrip()
    istart   = jobfile.find('=') + 1
    filebase = Path(jobfile[istart:]).stem
    layout1  = [[sg.Text('Edit Options for Job: ' + str(filebase))],
                [sg.Radio('Edit Data File'     , 'bRadio', default=True)],
                [sg.Radio('Edit Parameter File', 'bRadio'              )],
                [sg.Submit(), sg.Cancel()]]
    window1  = sg.Window('Edit Job Options', layout=layout1)
    (event, values) = window1.read()
    window1.Close()
    #
    # Data File Processing
    #
    if event == 'Submit' and values[0] is True:
        edit_data(job, jobsys, filetype='.data')
        return()
    #
    # Parameter File Processing
    #
    elif event == 'Submit' and values[1] is True:
        edit_param(job, jobsys, **jobhelp)
        return()

    else:
        return()


def edit_param(job, jobsys, **jobhelp):
    """Edit Job DATA or PARAM File

    The function sets up the parameters to call the edit_parameters function that allows the user to edit the PARAM file.

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

    if not job:
        sg.popup_ok('No Case Selected', no_titlebar=False, grab_anywhere=False, keep_on_top=True)
        return()
    #
    # Edit Data File or Parameter File Option
    #
    jobparam   = []
    jobparam1  = []
    job        = str(job[0]).rstrip()
    istart     = job.find('=') + 1
    #
    # Check for Data File
    #
    filebase   = Path(job[istart:]).stem
    filedata1  = Path(job[istart:]).with_suffix('.data')
    filedata2  = Path(job[istart:]).with_suffix('.DATA')
    filedata   = ''
    if filedata1.is_file():
        filedata = filedata1
    if filedata2.is_file():
        filedata = filedata2
    if filedata == '':
        sg.popup_error('Cannot Find Data File: ', str(filedata1),
                      'or ' , str(filedata2), no_titlebar=False, grab_anywhere=False, keep_on_top=True)
        out_log('Cannot Find: ' + str(filedata1) + ' or ' + str(filedata2), True)

        return()
    #
    # Check for PARAM File
    #
    filebase   = Path(job[istart:]).stem
    fileparam1 = Path(job[istart:]).with_suffix('.param')
    fileparam2 = Path(job[istart:]).with_suffix('.PARAM')
    fileparam  = ''
    if fileparam1.is_file():
        fileparam = fileparam1
    if not fileparam2.is_file():
        fileparam = fileparam2
    if fileparam == '':
        sg.popup_error('Cannot Find Parameter File: ',  str(fileparam1),
                      'or ', str(fileparam2), no_titlebar=False, grab_anywhere=False, keep_on_top=True)
        out_log('Cannot Find Parameter File: ' + str(fileparam1) + ' or ' + str(fileparam2), True)
        return()
    #
    # Parameter File Processing
    #
    if fileparam.is_file():
        file  = open(str(fileparam).rstrip(), 'r')
        for n, line in enumerate(file):
            if '=' in line:
                jobparam.append(line.rstrip())
        file.close()
        #
        # Edit Job Parameters
        #
        (jobparam1, exitcode) = edit_parameters(fileparam, jobparam, **jobhelp)
        if exitcode == 'Exit':
            save_parameters(filedata, jobparam1, filebase, fileparam, jobsys)

    else:
        sg.popup_error('Cannot Find Parameter File: ' + str(fileparam),
                      no_titlebar=False, grab_anywhere=False, keep_on_top=True)
        out_log('Cannot Find Parameter File: ' + str(fileparam), True)

    return()


def edit_options(opmsys1, opmoptn1):
    """Edit OPMRUN Options that Define Various Configuration Options

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
            output-font      = set the output font type (Liberation Mono)
            output-font-size = set the output font size (9)
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

    # Define Terminal and Terminal Commands
    terminals = ['konsole', 'mate-terminal', 'xterm', 'wsl']
    if opmoptn1['term-command'] in terminals:
        term = opmoptn1['term-command']
    else:
        term = terminals [2]

    column1   = [
                 [sg.Text('OPM Flow Manual Location'                                                  )],
                 [sg.InputText(opmoptn1['opm-flow-manual'], key='_opm-flow-manual_', size=(80, None))   ,
                  sg.FileBrowse(target='_opm-flow-manual_',
                                file_types=(('Manual Files', '*.pdf'),), initial_folder=defmanual)     ],

                 [sg.Text('OPM Keyword Generator Template Directory'                                  )],
                 [sg.InputText(opmoptn1['opm-keywdir'    ], key='_opm-keywdir_'       , size=(80, None)),
                  sg.FolderBrowse(target='_opm-keywdir_', initial_folder=defkeyw)                      ],

                 [sg.Text('ResInsight Command'                                                        )],
                 [sg.InputText(opmoptn1['opm-resinsight' ], key='_opm-resinsight_'   , size=(80, None)),
                  sg.FileBrowse(target='_opm-resinsight_', initial_folder=defresinsight)               ],

                 [sg.Text('Editor Command for Editing Input Files'                                    )],
                 [sg.InputText(opmoptn1['edit-command'   ], key='_edit-command_'     , size=(80, None))],

                 [sg.Text('Terminal Command for Running in Backgroud Mode'                            )],
                 [sg.Listbox(values= terminals,key='_term-command_', default_values=term, size=(80, 4))],

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

    (event, values) = window1.read()
    window1.Close()

    if event == 'Cancel' or event is None:
        opmoptn1 = opmoptn0

    if event == 'Submit':
        opmoptn1['opm-flow-manual' ] = values['_opm-flow-manual_' ]
        opmoptn1['opm-keywdir'     ] = values['_opm-keywdir_'     ]
        opmoptn1['opm-resinsight'  ] = values['_opm-resinsight_'  ]
        opmoptn1['edit-command'    ] = values['_edit-command_'    ]
        opmoptn1['term-command'    ] = values['_term-command_'    ][0]

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


def edit_parameters(fileparam, jobparam, **jobhelp):
    """Edit OPM Flow Parameters

    The function edits the OPM Flow Parameters and first checks if the parameters have been loaded via calling  of OPM
    Flow, in  case  OPM Flow has not been installed, or the system cannot find the program. If the parameters
    are not found, the routine sets the exitcode, displays error message, and returns.

    Parameters
    ----------
    fileparam : str
        OPM Flow PARAM parameter file
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
        layout1    = [[sg.Text('Edit File:')],
                      [sg.InputText(str(fileparam), size=(80, 1), disabled= True,
                                    font=(opmoptn['output-font'], opmoptn['output-font-size']))],
                      [sg.Text('Select Parameter to Change:')],
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
            (event, values) = window1.read()

            if event == 'Edit' or event == '_listbox_':
                if not values['_listbox_']:
                    sg.popup_error('Please select a parameter from the list',
                                  no_titlebar=False, grab_anywhere=False, keep_on_top=True)
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

            if event == 'Cancel' or event is None:
                text = sg.popup_yes_no('Cancel Changes?',
                                     no_titlebar=False, grab_anywhere=False, keep_on_top=True)
                if text == 'Yes':
                    jobparam  = jobparam0
                    exitcode  = event
                    break
                else:
                    event = 'Edit'
                    continue

            if event == 'Exit':
                text = sg.popup_yes_no('Save and Exit?',
                                     no_titlebar=False, grab_anywhere=False, keep_on_top=True)
                if text == 'Yes':
                    jobparam = window1['_listbox_'].get_list_values()
                    exitcode = event
                    break

        window1.Close()
        set_window_status(True)
        window0['_outlog_'+sg.WRITE_ONLY_KEY].update()

    else:
        exitcode  = 'Cancel'
        sg.popup_error('OPM Flow Parameters Have Not Been Set',
                      no_titlebar=False, grab_anywhere=False, keep_on_top=True)

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

    (event, values) = window1.read()
    window1.Close()

    if event == 'Cancel' or event is None:
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


def flow_job(cmd):
    """Define Job Parameters for OPM Flow

    Converts job parameters into various forms for processing a flow simulation job. The routine reduces duplication
    of code for job parameter manipulation

    Parameters
    ----------
    cmd : str
        Job command

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
    joblog : str
        The job file with suffix '.LOG'
    """

    istart  = cmd.find('=')
    job     = cmd[istart + 1:]
    jobcmd  = cmd[:istart + 1]
    jobpath = Path(job).parents[0]
    jobbase = Path(job).name
    jobroot = Path(job).stem
    joblog  = Path(jobbase).with_suffix('.LOG')
    return job, jobcmd, jobpath, jobbase, jobroot, joblog


def load_manual(opmsys1, filename):
    """Loads the OPM Flow User Manual

    Loads the OPM Flow User Manual in PDF format using the systems default PDF reader/viewer. The location of the manual
    is stored in the opmoptn dictionary and the filename is a reference to this variable.

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
        sg.popup_ok('OPM Flow Manual has not been defined in the Options.',
                   'Use the Edit Options menu to set the File Name.',
                   no_titlebar=False, grab_anywhere=False, keep_on_top=True)
        return()

    if not Path(filename).is_file():
        sg.popup_ok('OPM Flow Manual File Cannot be Found. \n', str(filename) + ' \n',
                   'Use the Edit Options menu to set the File Name.',
                   no_titlebar=False, grab_anywhere=False, keep_on_top=True)
        return ()
    #
    # Linux System
    #
    if opmsys1['system'] == 'Linux':
        try:
            subprocess.Popen(["xdg-open", filename])
        except Exception:
            sg.popup_error('OPM Flow Manual Error \n \n' + 'Cannot run: \n \n' +
                          '"xdg-open ' + str(filename) + '" \n \n' +
                          'Either the default PDF viewer is not available, or the OPM Flow Manual cannot be found.',
                          line_width=len(filename) + 12, no_titlebar=False, grab_anywhere=False, keep_on_top=True)
    #
    # Windows System
    #
    if opmsys1['system'] == 'Windows':
        try:
            os.startfile(filename)
        except Exception:
            sg.popup_error('OPM Flow Manual Error \n \n' + 'Cannot run: \n \n' +
                          str(filename) + ' \n \n' +
                          'Either the default PDF viewer is not available, or the OPM Flow Manual cannot be found.',
                          line_width=len(filename) + 12, no_titlebar=False, grab_anywhere=False, keep_on_top=True)

    return()


def load_options(opmoptn1, opmsys1, opmlog1):
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
            output-font      = set the output font type ('Liberation Mono')
            output-font-size = set the output font size (10)

            opm-flow-manual  = define the location of the OPM Flow Manual (None)
            opm-resinsight   = defines the ResInsight command
            edit-command     = defines the edit and editor options to edit the input deck (None)
            term-command     = defines the terminal command to run the jobs in background (['xterm', '-hold', '-e'] )

            prj-name-00      =  OPMRUN Default Working Directory
            prj-dirc-00      =  Project Directory 0
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
    opmlog1 : tuple
        OPM log file pointer set to None in calling routine

    Returns
    -------
    opmoptn1 : dict
        Updated dictionary list of all OPMRUN options
    """
    #
    # Define Default Options
    #
    if sg.running_windows():
        font = 'Courier'
        term = 'wsl'
    else:
        font = 'Liberation Mono'
        term = 'xterm'
    opmdef                     = dict()
    opmdef['input-width'     ] = 164
    opmdef['input-heigt'     ] = 10
    opmdef['output-width'    ] = 162
    opmdef['output-heigt'    ] = 30
    opmdef['output-font'     ] = font
    opmdef['output-font-size'] = 9
    opmdef['opm-keywdir'     ] = 'None'
    opmdef['opm-flow-manual' ] = 'None'
    opmdef['opm-resinsight'  ] = 'None'
    opmdef['edit-command'    ] = 'None'
    opmdef['term-command'    ] = term
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
            sg.popup_error('OPMRUN Options Error \n \n' + 'Problem Reading: \n \n' + str(opmsys1['opmini']) + '\n \n' +
                          'Try Deleting the File and Restarting OPMRUN - Program Will Abort',
                          no_titlebar=False, grab_anywhere=False, keep_on_top=True)
            exit('Error Reading ' + str(opmsys1['opmini']) + 'Try Deleting the File and Restarting')
        #
        # Check for Missing Options
        #
        errors = False
        for key in opmdef:
            if key not in opmoptn1:
                opmoptn1[key] = opmdef[key]
                errors = True

        if errors:
            save_options(opmsys1, opmoptn1, False)
            sg.popup_ok('OPMRUN Options Have Been Created/Updated for this Release',
                       no_titlebar=False, grab_anywhere=False, keep_on_top=True)

    else:
        opmoptn1 = opmdef
        save_options(opmsys1, opmoptn1, False)
        sg.popup_ok('OPMRUN Default Options Created and Saved',
                   no_titlebar=False, grab_anywhere=False, keep_on_top=True)
    #
    # Write Initial Options to Log File
    #
    for item in opmoptn1:
        opmlog1.write('{}: OPMOPTN Key: {:<16} , Value : {:} \n'.format(get_time(), item, opmoptn1[item]))
        opmlog1.flush()

    return opmoptn1


def load_parameters(opmsys1, outpop=True):
    """Load OPM Flow Parameters

    Function runs OPM Flow via a subprocess to get OPM Flow's Help parameters, and then then loads the help into
    jobhelp dict[] variable for future reference.

    Parameters
    ----------
    opmsys1 : dict
        Contains a dictionary list of all OPMRUN System parameters, uses 'opmcmd' for the simulator command and
        'opmparm' for the OPM Flow parameter file.

    outpop : bool
        Popup display option (True to display Popup, false no display).

    Returns
    -------
    jobparam : List
        OPM Flow PARAM list

    jobhelp : dict
        OPM Flow PARAM list help information stored in a dictionary with the key being the PARAM variable
    """
    if sg.running_windows():
        run_command('wsl flow --help > ' + str(opmsys1['opmparam']))
    else:
        run_command('flow --help > ' + str(opmsys1['opmparam']))

    jobparam = []
    jobhelp  = dict()
    file     = open(opmsys1['opmparam'], 'r')
    for n, line in enumerate(file):
        if '--' in line and 'help' not in line:
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
    if outpop:
        sg.popup_ok('OPM Flow Parameters Loaded from Flow: ' + str(opmsys1['opmparam']),
                   no_titlebar=False, grab_anywhere=False, keep_on_top=True)

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
    if not jobparam:
        sg.popup_error('Job Parameters Missing; Cannot Load Job Queue - Check if OPM Flow is Installed',
                      no_titlebar=False, grab_anywhere=False, keep_on_top=True)
        return()
    #
    # Check Job Queue for Entries
    #
    if joblist:
        text = sg.popup_yes_no('Loading a OPMRUN Queue from File Will Delete the Existing Queue, Continue?',
                             no_titlebar=False, grab_anywhere=False, keep_on_top=True)
        if text == 'No':
            return()
    #
    # Load Queue if Valid Entry
    #
    filename = sg.popup_get_file('OPMRUN Queue File Name', default_extension='que', save_as=False,
                               default_path=str(Path().absolute()), initial_folder=str(Path().absolute()),
                               file_types=[('OPM Queues', '*.que'), ('All', '*.*')], keep_on_top=False)
    if filename is None:
        sg.popup_ok('OPMRUN Queue: Loading of Queue Cancelled', no_titlebar=False, grab_anywhere=False,
                    keep_on_top=True)

    elif Path(filename).is_file():
        joblist = []

        file  = open(filename, 'r')
        for n, line in enumerate(file):
            if 'flow' in line:
                joblist.append(line.rstrip())
        file.close()
        window0['_joblist_'].update(joblist)
        sg.popup_ok('OPMRUN Queue: Loaded from: ' + filename,
                   no_titlebar=False, grab_anywhere=False, keep_on_top=True)
    else:
        sg.popup_ok('OPMRUN Queue: Nothing to Load', no_titlebar=False, grab_anywhere=False, keep_on_top=True)

    return joblist


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

    opmsys1                 = platform.uname()._asdict()
    opmsys1['python'       ] = platform.python_version()
    opmsys1['opmgui'       ] = 'PySimpleGUI - ' + str(sg.version)
    opmsys1['airspeed'     ] = 'airspeed - ' + str(pkg_resources.get_distribution('airspeed').version)
    opmsys1['datetime'     ] = 'datetime - ' + opmsys1['python']
    opmsys1['getpass'      ] = 'getpass - ' + str(pd.__version__)
    opmsys1['importlib'    ] = 'importlib - ' + opmsys1['python']
    opmsys1['os'           ] = 'os - ' + opmsys1['python']
    opmsys1['pandas'       ] = 'pandas - ' + str(pd.__version__)
    opmsys1['pathlib'      ] = 'pathlib - ' + opmsys1['python']
    opmsys1['pkg_resources'] = 'pkg_resources - ' + opmsys1['python']
    opmsys1['platform'     ] = 'platform - ' + opmsys1['python']
    opmsys1['psutil'       ] = 'psutil - ' + str(psutil.__version__)
    opmsys1['pyDOE2'       ] = 'pyDOE2 - ' + str(pkg_resources.get_distribution('pyDOE2').version)
    opmsys1['re'           ] = 're - ' + opmsys1['python']
    opmsys1['subprocess'   ] = 'subprocess - ' + opmsys1['python']
    opmsys1['sys'          ] = 'sys - ' + opmsys1['python']
    #
    # Check for Windows 10 for Windows Based Operating Systems
    #
    if opmsys1['system'] == 'Windows' and opmsys1['release'] != '10':
        sg.popup_error('Windows ' + str(opmsys1['release']) + 'Detected\n' +
                       'OPMRUN Requires Windows 10 and WSL to Run and Windows Operating Systems\n' +
                       'Program Will Exit', no_titlebar=False, grab_anywhere=False, keep_on_top=True)
        raise SystemExit('Windows ' + str(opmsys1['release']) + 'Detected - Require Windows 10 or Linux')
    #
    # Get OPM Flow Version
    #
    if sg.running_windows():
        opmflow = run_command('wsl flow --version')
        opmjob  = 'OPMRUN.ps1'
    else:
        opmflow = run_command('flow --version')
        opmjob = 'OPMRUN.job'
    opmsys1['opmvers'] = opmvers
    opmsys1['opmflow'] = opmflow.rstrip()
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
    opmsys1['opmini'  ] = Path(opmsys1['opmhome'] / 'OPMRUN.ini'  )
    opmsys1['opmlog'  ] = Path(opmsys1['opmhome'] / 'OPMRUN.log'  )
    opmsys1['opmjob'  ] = Path(opmsys1['opmhome'] / opmjob        )
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


def out_log(text, outlog, outprt=False, window=None, colors=(None,None)):
    """Print and Display Log Information

    Function prints log information to display and /or log file, and / or Multiline element with time stamp.

    Parameters
    ----------
    text : str
        String to be printed and/or displayed
    outlog : bool
        Boolean log file output (True to write to log file, False not to write).
    outprt : bool
        Boolean log file output (True to print, False not to print).
    window : PySimpleGUI window
        The PySimpleGUI window that the output is going to (needed to do refresh on).
    colors : str
        String or Tuple[text, background] the text and background colors for the sg.print command.

    Returns
    -------
    None
    """

    if outprt:
        sg.cprint(text, colors=colors)

    if window is not None:
        window['_outlog1_'].update(text + '\n', append=True)

    text = get_time() + ': ' + text + '\n'
    # Write to Main Window if Not Closed
    try:
        window0['_outlog_'+sg.WRITE_ONLY_KEY].update(text, append=True)
    except Exception:
        sg.popup_ok(text, title='OPMRUN', no_titlebar=False, grab_anywhere=False, keep_on_top=True)

    if outlog:
        opmlog.write(text)
        opmlog.flush()

    return()


def run_job(command, opmsys):
    """Run an OPM Flow Job

    Runs a OPM Flow job via the subprocess command, gets process ID, and sends output to the OPM Flow output element.

    Parameters
    ----------
    command : str
        The OPM Flow command to execute
    opmsys : dict
        Contains a dictionary list of all OPMRUN System parameters

    Returns
    -------
    exitcode : int
        Return code from the sub-process command
    """
    #
    # Submit Job and Get Process ID
    #
    segmjob = False
    errors  = ['Exception',  'exception', 'Error: Unrecoverable errors']
    failjob = False
    killed  = []
    killjob = False
    if sg.running_windows():
        jobproc = subprocess.Popen(['powershell.exe ','wsl', command], shell=True, stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT, bufsize=1, universal_newlines=True)
    else:
        jobproc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                   bufsize=1, universal_newlines=True)
    out_log('Simulation PID ' + str(jobproc.pid), True)
    window0['_status_bar_'].update(value='Running: ' + str(command), visible=True)
    #
    # Process OPM Flow Output
    #
    for line in jobproc.stdout:
        line = remove_ansii_escape_codes(line.rstrip())
        sg.cprint(line)
        window0.refresh()
        #
        # Check if Job Failed
        #
        if any(err in line for err in errors):
            failjob = True
            killed = jobproc.pid
            out_log(line, False)
            #
            # Fix for mpiruns hanging
            #
            if 'Exception' in line or 'exception' in line and 'mpirun' in command:
                failjob, killed = kill_job('None', jobproc.pid)

            continue
        #
        # Check for Segmentation Fault
        #
        if 'Segmentation fault' in line:
            segmjob = True
        #
        # Check if User Requested for the Job to be Killed
        #
        event, values = window0.read(timeout=10)
        if event == '_kill_job_':
            killjob, killed = kill_job('Do You Wish to Kill the Current OPM Flow Job ? \n \n' +
                                       'Job: ' + str(command) + '\n \n', jobproc.pid)
            if killjob:
                sg.popup_ok('OPM Flow Process ' + str(jobproc.pid) + ' Has Been Stopped by ' + opmsys['opmuser'],
                             auto_close=True, no_titlebar=False, grab_anywhere=False, keep_on_top=True)

            continue
    #
    # Process Complete
    #
    returncode = jobproc.wait()
    if failjob:
        out_log('Failed: ' + str(killed), True, True)
        out_log('OPM Flow Process ' + str(jobproc.pid) + ' Has Failed', True, True, colors=('red', None))

    elif killjob:
        out_log('Killed: ' + str(killed), True, True, colors=('red', None))
        out_log('OPM Flow Process ' + str(jobproc.pid) + ' Has Been Stopped by ' + opmsys['opmuser'], True, True,
                colors = ('red', None))

    elif segmjob or returncode != 0:
        killjob = True
        out_log('OPM Flow Process ' + str(jobproc.pid) + ' Segmentation Fault - Job Aborted', True, True,
                colors=('red', None))
        sg.popup_error('OPM Flow Process Error', 'Process:',  str(command), 'Exit Code: ' + str(returncode),
                       non_blocking=True, auto_close=True, no_titlebar=False, grab_anywhere=False, keep_on_top=True)

    sg.cprint('Process Complete (' + str(returncode) + ') \n \n')
    window0['_status_bar_'].update(value='', visible=False)
    window0.refresh()
    return (failjob, killjob)


def run_jobs(joblist, jobsys, outlog):
    """Run Jobs Main Function for Both Background and Foreground Options

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

    jobcase  = ''
    jobnum   = 0
    jobsfail = 0
    jobskill = 0
    upper    = ['.DBG', '.EGRID', '.INIT', '.LOG', '.PRT', '.RSM', '.SMSPEC', '.UNRST', '.UNSMRY', '.INFOSTEP']
    if sg.running_windows():
        jobext   = upper
        tail_len = 1
    else:
        jobext   = upper + [item.lower() for item in upper]
        tail_len = 14

    if not joblist:
        sg.popup_ok('No Jobs In Queue', no_titlebar=False, grab_anywhere=False, keep_on_top=True)
        return()

    layout1 = [[sg.Text('Select the Run Option for All ' + str(len(joblist)) + ' Cases in Queue?'  )],
               [sg.Radio('Run in No Simulation Mode'      , 'bRadio1', key='_nosim_'               )],
               [sg.Radio('Run in Standard Simulation Mode', 'bRadio1', key='_rusim_',  default=True)],
               [sg.Text('Submit jobs for foreground or background processing'                      )],
               [sg.Radio('Foreground Processing'          , 'bRadio2', key='_fore_'  , default=True)],
               [sg.Radio('Background Processing'          , 'bRadio2', key='_back_'                )],
               [sg.Text(''                                                                         )],
               [sg.Submit(), sg.Cancel()]]
    window1 = sg.Window('Select Run Option', layout=layout1)
    (event, values) = window1.read()
    window1.Close()

    # ------------------------------------------------------------------------------------------------------------------
    # Background Processing
    # ------------------------------------------------------------------------------------------------------------------
    if values['_back_']:
        if values['_nosim_']:
            save_jobs(joblist, '_nosim_', jobext, opmsys, outlog=True)
        else:
            save_jobs(joblist, '_rusim_', jobext, opmsys, outlog=True)

        if opmoptn['term-command'] == 'konsole':
            cmd = ['konsole', '--hold', '-e', '$SHELL', '-c']
        elif opmoptn['term-command'] == 'mate-terminal':
            cmd = ['mate-terminal', '-e']
        elif opmoptn['term-command'] == 'xterm':
            cmd = ['xterm', '-hold', '-e']
        elif opmoptn['term-command'] == 'wsl':
            # powershell -ExecutionPolicy  Unrestricted -File OPMRUN.ps1
            cmd = ['powershell.exe', '-ExecutionPolicy', 'Unrestricted', '-NoExit', '-File']
        else:
            sg.popup_error('Background Processing Error',
                           'Invalid Terminal Type: ' + str(opmoptn['term-command']) +'\n' +
                           'Use Edit/Options to Set the Correct Terminal Type for Background Processing',
                           'Process Terminated', no_titlebar=False, grab_anywhere=False, keep_on_top=True)
            return()
        try:
            out_log('OPMRUN Running Batch Command: ' + ', '.join(cmd) + ', ' + str(jobsys['opmjob']), True)
            if sg.running_windows():
                subprocess.Popen([*cmd, str(jobsys['opmjob'])], creationflags=subprocess.CREATE_NEW_CONSOLE)
            else:
                subprocess.Popen([*cmd, str(jobsys['opmjob'])], stdout=subprocess.PIPE)
        except FileNotFoundError as error:
            sg.popup_error('Background Processing Error', 'Cannot Find Terminal Emulator or File \n \n' +
                           str(error) + ': ' + str(type(error)),
                           no_titlebar=False, grab_anywhere=False, keep_on_top=True)
            out_log('Cannot Find Terminal Emulator or File Error ' + str(error), True)
        return()

    # ------------------------------------------------------------------------------------------------------------------
    # Foreground Processing
    # ------------------------------------------------------------------------------------------------------------------
    for cmd in joblist:
        jobnum  = jobnum + 1
        window0['_joblist_'].update(set_to_index=jobnum - 1, scroll_to_index=jobnum - 1)
        (job, jobcmd, jobpath, jobbase, jobroot, joblog) = flow_job(cmd)
        jobdat1 = Path(jobroot).with_suffix('.DATA')
        jobdat2 = Path(jobroot).with_suffix('.data')

        if values['_nosim_']:
            jobcase = jobcmd + str(jobbase) + ' --enable-dry-run="true"' + ' | tee ' + str(joblog)
            sg.cprint(jobcase)

        if values['_rusim_']:
            jobcase = jobcmd + str(jobbase)  + ' | tee ' + str(joblog)

        if event == 'Cancel' or event is None:
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
            errors = set_directory(jobpath, outlog=False)
            if not errors:
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
                sg.popup_error('Data file ' + str(jobdat1) + ' or ' + str(jobdat2) + ' does not exist; aborting job?',
                               non_blocking=False, auto_close=True, auto_close_duration=5,
                               no_titlebar=False, grab_anywhere=False, keep_on_top=True)
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
                                          no_titlebar=False, grab_anywhere=False, keep_on_top=True)
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
            for text in jobext:
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
            sg.cprint(jobcase)
            out_log('Simulation Started', outlog)
            failed, killed = run_job(jobcase, opmsys)
            #
            # Job Failed
            #
            if failed:
                jobsfail = jobsfail + 1
            #
            # Job Killed
            #
            if killed:
                jobskill = jobskill + 1
                text = sg.popup_yes_no('Kill All Jobs in Queue?', no_titlebar=False, grab_anywhere=False,
                                       keep_on_top=True)
                if text == 'Yes':
                    out_log('Job Queue Killed by User', True, True, colors=('red', None))
                    out_log('Queue Processing Complete', True, True, colors=('red', None))
                    out_log('', outlog)
                    opmlog.flush()
                    break
            #
            # Job Complete
            #
            if not killed:
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
                    lines, status = tail(file, tail_len, offset=None)
                    file.close()
                    if status:
                        for line in enumerate(lines):
                            if line[1] == '':
                                continue
                            out_log(remove_ansii_escape_codes(line[1]), outlog)

            out_log('End   Job: ' + jobcase, outlog)
            out_log('Completed Job No. ' + str(jobnum), outlog)
            out_log('', outlog)
            opmlog.flush()
    #
    # Ena of Processing So Print Summary and Enable Buttons
    #
    jobsrun = jobnum - jobsfail - jobskill
    sg.cprint('Queue Schedule Statistics', text_color='blue')
    sg.cprint('Number of Jobs Processed: ' + str(jobnum), text_color='blue')
    if jobsfail == 0:
        sg.cprint('Number of Jobs Failed: ' + str(jobsfail), text_color='blue')
    else:
        sg.cprint('Number of Jobs Failed: ' + str(jobsfail), text_color='red')
    if jobskill == 0:
        sg.cprint('Number of Jobs Killed: ' + str(jobskill), text_color='blue')
    else:
        sg.cprint('Number of Jobs Killed: ' + str(jobskill), text_color='red')
    sg.cprint('Number of Jobs Completed: ' + str(jobsrun), text_color='blue')

    set_button_status(False)
    return()


def run_resinsight(command, jobfile='None'):
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
        sg.popup_ok('OPM ResInsight Command has not been defined in the Options.',
                   'Use the Edit Options menu to define the command.',
                   no_titlebar=False, grab_anywhere=False, keep_on_top=True)
        out_log('ResInsight Command: ' + str(command) + ' is Undefined', True)
        return()

    if not jobfile:
        sg.popup_ok('No Case Selected', no_titlebar=False, grab_anywhere=False, keep_on_top=True)
        return()

    if not jobfile == 'None':
        job = str(jobfile[0]).rstrip()
        istart = job.find('=') + 1
        file1 = Path(job[istart:]).with_suffix('.GRID')
        file2 = Path(job[istart:]).with_suffix('.EGRID')
        if file1.is_file():
            file0 = file1
        elif file2.is_file():
            file0 = file2
        else:
            sg.popup_error('Cannot Find GRID/EGRID File: ', str(file1),
                           'or ', str(file2),
                           no_titlebar=False, grab_anywhere=False, keep_on_top=True)
            out_log('Cannot Find: ' + str(file1) + ' or ' + str(file2), True)

            return ()
        command = command + str(' --startdir ') + str(file0.parent) + str(' --case ') + str(file0.name)

    try:
        out_log('Executing ResInsight Command: ' + str(command) , True)
        subprocess.Popen(command, shell=True)

    except Exception:
        sg.popup_error('OPM ResInsight Error Executing: \n' + command,
                      no_titlebar=False, grab_anywhere=False, keep_on_top=True)
        out_log('Executing ResInsight Command Error: ' + str(command), True)

    return()


def save_jobs(joblist, jobtype, jobext, jobsys, outlog=True):
    """ Save OPM Flow Jobs to File

    Save OPMRUN jobs in the job queue to a file in the users #Home directory called #HOME/OPM/OPMRUN.job. This is used
    to run jobs in background mode, as oppose to foreground mode.

    Parameters
    ----------
    joblist : list
        List of jobs in the job queue
    jobtype :str
        Type of job for this queue
    jobext : list
        List of simulation output files to be removed
    jobsys : dict
        Contains a dictionary list of all OPMRUN System parameters
    outlog : bool
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
        (job, jobcmd, jobpath, jobbase, jobroot, joblog) = flow_job(cmd)

        if jobtype == '_nosim_':
            jobcase = jobcmd + str(jobbase) + ' --enable-dry-run="true"' + ' | tee ' + str(joblog)
        else:
            jobcase = jobcmd + str(jobbase)  + ' | tee ' + str(joblog)
        if sg.running_windows():
            jobcase = 'wsl ' + jobcase

        file.write('# \n')
        file.write('# Job Number ' + str(jobnum) + ' \n')
        file.write('# \n')
        file.write('cd ' + str(jobpath) + ' \n')
        status =  set_directory(jobpath, outlog=False, outpop=False, outprt=False, window=None)
        if status == False:
            sg.popup_ok('Change Directory Error', 'On Trying to Cleanup Existing Output Files', 'Will Try to Continue',
                        no_titlebar=False, grab_anywhere=False, keep_on_top=True)

        for text in jobext:
            filename = Path(jobbase).with_suffix(text)
            if filename.is_file():
                file.write('rm ' + str(filename) + ' \n')
        file.write(jobcase + ' \n')

    file.write('# \n')
    file.write('# End of OPMRUN Jobs File \n')
    file.close()
    #
    # Set Permissions for Linux
    #
    if sg.running_linux():
        try:
            subprocess.call(['chmod', 'u=rwx', jobsys['opmjob']])
        except FileNotFoundError as error:
            sg.popup_error('Changing Access Control Error', str(error) + ': ' + str(type(error)),
            no_titlebar=False, grab_anywhere=False, keep_on_top=True)

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
    outlog : bool
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
    sg.popup_ok(str(jobbase) + ' parameter file written to:', str(jobfile),
               'Complete', no_titlebar=False, grab_anywhere=False, keep_on_top=True)


def save_queue(joblist, opmuser):
    """Save Job Queue to File

    Save the current job queue to a user selected file that can be loaded back into OPMRUN to re-run jobs when
    required

    Parameters
    ----------
    joblist : list
        Job list for queue
    opmuser : str
        User name

    Returns
    -------
    None
    """

    if not joblist:
        sg.popup_ok('No Cases In Job Queue; Queue will Not Be Saved',
                   no_titlebar=False, grab_anywhere=False, keep_on_top=True)
    else:
        filename = sg.popup_get_file('OPMRUN Queue File Name', default_extension='.que', save_as=True,
                                   default_path=str(Path().absolute()), keep_on_top=False,
                                   file_types=(('OPM Queues', '*.que'), ('All', '*.*')))
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
            sg.popup_ok('OPMRUN Queue File Saved to: ' + filename,
                       no_titlebar=False, grab_anywhere=False, keep_on_top=True)


def set_button_status(status, statuskill=False):
    """Set Main Window Button Status

    Sets the display buttons for the main window to enabled (False) or disable (True) depending on the value of status.

    Parameters
    ----------
    status : bool
         Boolean that sets the display buttons to enabled (False) or disable (True)
    statuskill : bool
         Boolean that sets the "kill Job" button to enabled (False) or disable (True)

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
    window0['_copy_'       ].update(disabled=status)
    window0['_clear_'      ].update(disabled=status)
    window0['_exit_'       ].update(disabled=status)

    if statuskill:
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
            sg.cprint('Current Working Directory ' , str(Path().absolute()))

        if window is not None:
            window['_outlog1_'].update('Working Directory ' + str(Path().absolute()) + '\n', append=True)

    except OSError:
        if outpop or window is not None:
            sg.popup_error('Change Working Directory Error \n', 'Please See Log Output',
                           no_titlebar=False, grab_anywhere=False, keep_on_top=True)

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
    key : str
        The project name to look up in opmoptn to get the directory name to set to the current directory
    opmoptn : dict
        Contains the project names and their associated directories.

    Returns
    -------
    None
    """

    key = key[(key.find('_') + 1):-1]
    name = opmoptn.get(key)
    if name is None or name == '':
        sg.popup_error('Project Name ' + key + ' not Found',
                      no_titlebar=False, grab_anywhere=False, keep_on_top=True)
        return()
    dirc = key.replace('name', 'dirc')
    dirc = opmoptn.get(dirc)
    if dirc is None or dirc == '':
        sg.popup_error('Project Directory ' + str(dirc) + ' not Found',
                      no_titlebar=False, grab_anywhere=False, keep_on_top=True)
        return()

    status = set_directory(Path(dirc), True, True, False)
    if status:
        sg.popup_ok('Change Directory',
                   'Project Name: '     + name + '\n' +
                   'Project Directory:' + dirc + '\n',
                   no_titlebar=False, grab_anywhere=False, keep_on_top=True)


def set_menu(opmoptn):
    """Set the Main Window Menus

    Set the main window menus for the first time to display, and for when the menu needs to be updated. Used for when
    the menu changes due to the projects being edited; to use:

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

    menu  = [['File',  ['Add Jobs',
                        'Add Jobs Recursively',
                        'Project',
                                  [opmoptn['prj-name-01'] + '::_prj-name-01_',
                                   opmoptn['prj-name-02'] + '::_prj-name-02_',
                                   opmoptn['prj-name-03'] + '::_prj-name-03_',
                                   opmoptn['prj-name-04'] + '::_prj-name-04_',
                                   opmoptn['prj-name-05'] + '::_prj-name-05_'],
                        'Properties',
                        'Save',
                        'Exit'
                        ]
              ],
             ['Edit',  ['Edit Data File',
                        'Edit Parameter File',
                        'Edit Parameters',
                        'List Parameters',
                        'Set Parameters',
                        'Options',
                        'Projects'],
              ],
             ['View',  ['View Debug File',
                        'View Log File',
                        'View Print File',
                        'View RSM File',
                        'View in ResInsight'],
              ],
             ['Tools', ['Compress Jobs',
                                        ['Compress Jobs',
                                         'Uncompress Jobs'],
                        'Simulator Input',
                                        ['Keywords',
                                         'Production Schedule',
                                         'Sensitivities',
                                         'Well Specification'],
                        'ResInsight',
                        'Well Trajectory Conversion'], ],
             ['Help',  ['Manual',
                        'Help',
                        'System',
                        'About'],
              ]]
    return menu


def set_window_status(status):
    """Set the Main Window Status

    Set the main window status to active or inactive for when a second window is being displayed.

    Parameters
    ----------
    status : bool
        Boolean that sets the window status, True for active and False for inactive

    Returns
    -------
    None
    """

    if status:
        # window0.enable   # Not Working Causes Display to Freeze on Linux Systems
        set_button_status(False, True)
        window0.set_alpha(1.00)
        window0.refresh()

    else:
        window0.set_alpha(0.75)
        set_button_status(True, True)
        # window0.disable  # Not Working Causes Display to Freeze Linux Systems


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
    global joblist
    global jobparam

    joblist  = []
    jobparam = []

    global opmoptn
    global opmlog
    global opmsys
    global window0
    #
    # OPMRUN Startup Setup System Variables and File Creation
    #
    opmlog         = ''
    opmsys         = dict()
    opmsys, opmlog = opm_startup(__version__, opmsys, opmlog,)
    #
    # Load OPMRUN Configuration Parameters and Set Last Working Directory as Default
    #
    opmoptn = dict()
    opmoptn = load_options(opmoptn, opmsys, opmlog)
    if (Path(opmoptn['prj-dirc-00']).is_dir()):
        os.chdir(opmoptn['prj-dirc-00'])
    else:
        sg.popup_error('Cannot Find Last Used Default Directory', 'Resetting Default Directory to: \n' ,
                        str(opmsys['opmhome']), '\n And Continuing',
                       no_titlebar=False, grab_anywhere=False, keep_on_top=True)
        opmoptn['prj-dirc-00'] = opmsys['opmhome']
        os.chdir(opmoptn['prj-dirc-00'])
    #
    # Run OPM Flow Help and Store Command Line Parameters
    #
    set_gui_options()
    jobparam, jobhelp = load_parameters(opmsys, outpop=False)
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
                'Copyright (C) 2018-2021 Equinox International Petroleum Consultants Pte Ltd. \n'
                '\n' +
                'Author  : David Baxendale (david.baxendale@eipc.co)')

    helptext = (
                'OPMRun is a Graphical User Interface ("GUI") program for the Open Porous Media ("OPM") Flow ' +
                'simulator. \n' +
                '\n'
                'The intent is for OPMRUN to have similar functionality to the commercial simulators program, with ' +
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
                'Various utility options are included via the the Tools menu including:\n' +
                '\n'
                '(1) Compress and uncompress the input and output files into one ZIP file to save disk space.\n' +
                '(2) Deck Generator:\n' +
                '    (a) Keywords: Utility to create input decks. \n' +
                '    (b) Production Schedule: To generate a production schedule using WCONHIST.\n' +
                '    (c) Sensitivity: Utility to generate sensitivity cases using factorial and DOE options.\n' +
                '    (d) Well Specification: To generate WELSPECS, COMPDAT and COMPLUMP keywords.\n'
                '(3) Launch OPM ResInsight the open source post processing visualization program. \n' +
                '(4) Well Trajectory conversion for OPM ResInsight.\n' +
                '\n'
                'Finally, the Edit Options menu allows for editing OPMRUN options, set the OPM Flow Manual location, ' +
                'default editor command, ResInsight command etc. \n' +
                '\n'
                'See the OPM Flow manual for further information. \n')

    # ------------------------------------------------------------------------------------------------------------------
    # Initialize GUI Setup and Define Main Window
    # ------------------------------------------------------------------------------------------------------------------
    menulayout = set_menu(opmoptn)
    mainmenu   = sg.Menu(menulayout)

    flowlayout = [[sg.Multiline(background_color='white', text_color='black',
                                size=(opmoptn['output-width'], opmoptn['output-heigt']),
                                key='_outflow_'+sg.WRITE_ONLY_KEY,
                                font=(opmoptn['output-font'], opmoptn['output-font-size']))]]

    loglayout  = [[sg.Multiline(background_color='white', text_color='darkgreen', do_not_clear=True,
                                key='_outlog_'+sg.WRITE_ONLY_KEY,
                                size=(opmoptn['output-width'], opmoptn['output-heigt']),
                                font=(opmoptn['output-font'], opmoptn['output-font-size']))]]

    mainwind   = [[mainmenu],
                  [sg.Text('OPM Flow Command Schedule')],

                  [sg.Listbox(values=joblist, size=(opmoptn['input-width'], opmoptn['input-heigt']), key='_joblist_',
                              right_click_menu=['&options', ['Edit Data File', 'Edit Parameter File', 'View Debug File',
                                                             'View Log File', 'View Print File', 'View RSM File',
                                                             'View in ResInsight']],
                              enable_events=True, default_values=0,
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
                      sg.Button('Clear'   , key='_clear_'    , tooltip='Clear output'),
                      sg.Button('Copy'    , key='_copy_'     , tooltip='Copy output to clipboard'),
                      sg.Button('Exit'    , key='_exit_'    )],
                  [sg.StatusBar('', size=(opmoptn['output-width'],1), auto_size_text=False, text_color='green',
                                font=(opmoptn['output-font'], opmoptn['output-font-size']),
                                key='_status_bar_', relief='flat', justification='left', visible=True)]]

    window0 = sg.Window('OPMRUN - Flow Job Scheduler ',
                        layout=mainwind, disable_close=False, finalize=True, location=(300, 100))
    #
    #   Set Output Multiline Window for CPRINT
    #
    sg.cprint_set_output_destination(window0, '_outflow_'+sg.WRITE_ONLY_KEY)

    out_log('OPMRUN Started', True, True)
    out_log('Working Directory set to ' + str(opmoptn['prj-dirc-00']), False, False)

    # ------------------------------------------------------------------------------------------------------------------
    # Define GUI Event Loop, Read Buttons, and Make Callbacks etc. Section
    # ------------------------------------------------------------------------------------------------------------------
    while True:
        #
        # Set Output Multiline Window for CPRINT, Read the Form and Process Action Based on event
        #
        sg.cprint_set_output_destination(window0, '_outflow_' + sg.WRITE_ONLY_KEY)
        event, values = window0.read()
        # Check if Window Has Been Closed
        if event in [None, sg.WIN_CLOSED]:
            break

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
        elif event == '_add_job_' or event == 'Add Jobs':
            set_window_status(False)
            add_job(joblist, jobparam, opmsys)
            set_window_status(True)
            continue
        #
        # Add Jobs Recursively
        #
        elif event == 'Add Jobs Recursively':
            set_window_status(False)
            add_jobs_recursively(joblist, jobparam, opmsys)
            set_window_status(True)
            continue
        #
        # Clear Log
        #
        elif event == '_clear_':
            if window0['_tab_out_'].get() == '_tab_outlog_':
                window0['_outlog_'+sg.WRITE_ONLY_KEY].update('')
            if window0['_tab_out_'].get() == '_tab_outflow_':
                window0['_outflow_'+sg.WRITE_ONLY_KEY].update('')
            continue
        #
        # Copy Output or Log
        #
        elif event == '_copy_':
            if window0['_tab_out_'].get() == '_tab_outlog_':
                copy_to_clipboard(window0['_outlog_'+sg.WRITE_ONLY_KEY].get())
                sg.popup_timed('Output Log Copied to Clipboard', no_titlebar=False, grab_anywhere=False,
                               keep_on_top=True)
            if window0['_tab_out_'].get() == '_tab_outflow_':
                copy_to_clipboard(window0['_outflow_'+sg.WRITE_ONLY_KEY].get())
                sg.popup_timed('Simulator Output Copied to Clipboard', no_titlebar=False, grab_anywhere=False,
                               keep_on_top=True)
            continue
        #
        # Clear Queue
        #
        elif event == '_clear_queue_':
            joblist = clear_queue(window0['_joblist_'].get_list_values())
            continue
        #
        # Compress Jobs
        #
        elif event == 'Compress Jobs':
            set_window_status(False)
            compress_files(opmoptn)
            set_window_status(True)
            continue
        #
        # Delete Job
        #
        elif event == '_delete_job_':
            delete_job(joblist, values['_joblist_'])
            continue
        #
        # Edit Data File
        #
        elif event == 'Edit Data File':
            edit_data(values['_joblist_'], opmsys, filetype='.data')
            continue
        #
        # Edit Job
        #
        elif event == '_edit_job_':
            edit_job(values['_joblist_'], opmsys, **jobhelp)
            continue
        #
        # Edit Parameter File
        #
        elif event == 'Edit Parameter File':
            edit_param(values['_joblist_'], opmsys, **jobhelp)
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
            (jobparam, exitcode) = edit_parameters('Default Parameters', jobparam, **jobhelp)
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
        elif event in [ '_exit_', 'Exit', None, sg.WIN_CLOSED]:
            text = sg.popup_yes_no('Exit OPMRUN?', no_titlebar=False, grab_anywhere=False, keep_on_top=True)
            if text == 'Yes':
                text = sg.popup_yes_no('Are You Sure You wish to Exit OPMRUN?', no_titlebar=False,
                                     grab_anywhere=False, keep_on_top=True)
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
                sg.cprint('Start of OPM Flow Parameters')
                for k in enumerate(jobparam):
                    sg.cprint('{}: {}'.format(*k))
                sg.cprint('End of OPM Flow Parameters')
            else:
                sg.popup_error('OPM Flow Parameters Have Not Been Set',
                              no_titlebar=False, grab_anywhere=False, keep_on_top=True)
            continue
        #
        # Keyword Generation
        #
        elif event == 'Keywords':
            set_window_status(False)
            keyw_main(opmoptn, opmsys)
            set_window_status(True)
            continue
        #
        # Load Queue
        #
        elif event == '_load_queue_':
            joblist = load_queue(joblist, jobparam)
            continue
        #
        # Manual
        #
        elif event == 'Manual':
            load_manual(opmsys, opmoptn['opm-flow-manual'])
            continue
        #
        # Production Schedule Generation
        #
        elif event == 'Production Schedule':
            set_window_status(False)
            prodsched_main(opmoptn, opmsys)
            set_window_status(True)
            continue
        #
        # Properties
        #
        elif event == 'Properties':
            print_dict('OPMOPTN', opmoptn, option='print')
            continue
        #
        # ResInsight
        #
        elif event == 'ResInsight':
            run_resinsight(opmoptn['opm-resinsight'], jobfile='None')
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
            jobparam = default_parameters(jobparam, opmsys)
            continue
        #
        # Set Project
        #
        elif event.find('::_prj-name') != -1:
            set_directory_project(event, opmoptn)
            continue
        #
        # Sensitivity Generator
        #
        elif event == 'Sensitivities':
            set_window_status(False)
            sensitivity_main(jobparam, opmoptn, opmsys)
            set_window_status(True)
            continue
        #
        # System
        #
        elif event == 'System':
            print_dict('OPMSYS', opmsys, option='popup')
            continue
        #
        # Uncompress Jobs
        #
        elif event == 'Uncompress Jobs':
            set_window_status(False)
            uncompress_files(opmoptn)
            set_window_status(True)
            continue
        #
        # View Output Files
        #
        elif event == 'View Debug File':
            edit_data(values['_joblist_'], opmsys, filetype='.dbg')
        elif event == 'View Log File':
            edit_data(values['_joblist_'], opmsys, filetype='.log')
        elif event == 'View Print File':
            edit_data(values['_joblist_'], opmsys, filetype='.prt')
        elif event == 'View RSM File':
            edit_data(values['_joblist_'], opmsys, filetype='.rsm')
        #
        # View in ResInsight
        #
        elif event == 'View in ResInsight':
            run_resinsight(opmoptn['opm-resinsight'], jobfile=values['_joblist_'])
            continue
        #
        # Well Specification
        #
        elif event == 'Well Specification':
            set_window_status(False)
            wellspec_main(opmoptn, opmsys)
            set_window_status(True)
            continue
        #
        # Well Trajectory Conversion
        #
        elif event == 'Well Trajectory Conversion':
            set_window_status(False)
            welltraj_main(opmoptn, opmsys)
            set_window_status(True)
            continue

    # ------------------------------------------------------------------------------------------------------------------
    # Post Processing Section
    # ------------------------------------------------------------------------------------------------------------------
    opmoptn['prj-dirc-00'] = str(Path().absolute())
    if event in [None, sg.WIN_CLOSED]:
        #
        # Save Working Directory and Close log File
        #
        save_options(opmsys, opmoptn, False)
        out_log('OPMRUN Processing Terminated by User ', True)
        opmlog.close()
    else:
        #
        # Save Working Directory, Close Log File and Window
        #
        save_options(opmsys, opmoptn, True)
        out_log('OPMRUN Processing Complete ', True)
        opmlog.close()
        window0.close()

    exit('OPMRUN Complete')

# ----------------------------------------------------------------------------------------------------------------------
# Execute Module
# ----------------------------------------------------------------------------------------------------------------------
if __name__ == '__main__':
    opmrun()

# ======================================================================================================================
# End of OPMRUN.py
# ======================================================================================================================
