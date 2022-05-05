# ======================================================================================================================
#
"""OPM_COMPRESS.py - Compression Utility

This module contains the compress.pt and uncompress.py functions to compress/uncompress simulation cases input and
output files into a casename.zip file.

Program Documentation
---------------------
Only Python 3 is supported and tested Python2 support has been depreciated.

2022.04.01 - Add compression option to add Ensemble directories recursively and updated help information.
2022.04.01 - Add compression/uncompression option to add files recursively and also added help information.
2022.04.01 - Add compression option to add Ensemble directories recursively and updated help information.
2021.07.01 - New module with code moved from main module to here for code maintainability reasons.
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
Version : 2021-07.01
Date    : 14-Jul-2021
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
import PySimpleGUI as sg
from pathlib import Path

from opm_common import (change_directory, copy_to_clipboard, opm_popup, run_command)

# ----------------------------------------------------------------------------------------------------------------------
# Define OPM_COMPRESS Specific Modules
# ----------------------------------------------------------------------------------------------------------------------
def compress_cmd(cmd):
    """Define Compress Job Parameters Based On Job Type

    Converts job parameters into various forms for processing the compress and uncompress commands. The routine reduces
    duplication of code for job parameter manipulation

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
    jobfile : str
        The job file with suffix '.*'
    jobzip : str
        The job file with suffix '*.zip'
    """

    job     = cmd
    jobcmd  = cmd
    jobpath = Path(job).parents[0]
    jobbase = Path(job).name
    jobroot = Path(job).stem
    jobfile = Path(jobbase).with_suffix('.*')
    jobzip  = Path(jobbase).with_suffix('.zip')
    return job, jobcmd, jobpath, jobbase, jobroot, jobfile, jobzip


def compress_chk(cmd, window):
    """Check that the Linux ZIP and UNZIP Packages Have Been Installed

    The function if the Linux ZIP and UNZIP packages have been installed for both Linux and Windows 10 WSL environments.
    Command line compression tools have limted functionality and OPMRUN therefore users the Linux tools for both
    environments

    Parameters
    ----------
    cmd : str
        Command to check; either zip or unzip
    Returns
    -------
    Status : boolean
        Set to True if the
    """
    if sg.running_windows():
        status = run_command(['wsl', 'which', cmd], timeout=None, window=window)
    else:
        status = run_command(['which ' + cmd], timeout=None, window=window)
    if status != 0:
        status = False
        text = ('Cannot find '  +cmd + ' package in the Windows 10 WSL environment. One can use:\n\nsudo apt install ' +
                cmd + '\n\nto install the package in the Windows 10 WSL environment currently being used for running ' +
                'OPMRUN')
        sg.cprint(text, text_color='red')
        status = True
    return status


def compress_files(opmoptn):
    """Compress All Jobs Input and Output into a Zip File Using the Base Name

    The function allows the use to select a group of DATA files for compression of all files associated with the case
    name (*.DATA), using the standard zip utility on Linux systems. In addition, files can be added recursively by
    selecting the "top" directory.

    Parameters
    ----------
    opmoptn; dict
        A dictionary containing the OPMRUN default parameters

    Returns
    ------
    None
    """

    if sg.running_windows():
        wsl = 'wsl '
    else:
        wsl = ''
    joblist1 = []

    outlog   = '_outlog1_'+sg.WRITE_ONLY_KEY
    layout1  = [[sg.Text('Select Multiple Job Data Files to Compress'                             )],
                [sg.Listbox(values='', size=(112, 10), key='_joblist1_',
                            font=(opmoptn['output-font'], opmoptn['output-font-size'])            )],
                [sg.Text('Output'                                                                 )],
                [sg.Multiline(key=outlog, size=(112, 20), text_color='blue', autoscroll=True,
                              font=(opmoptn['output-font'], opmoptn['output-font-size'])          )],
                [sg.Text('Compression Options'                                                    )],
                [sg.Radio('Compress Job' , "bRadio", default=True                                 )],
                [sg.Radio('Compress Job and then Remove Job Files', "bRadio"                      )],
                [sg.Button('Add'), sg.Button('Add Recursively', tooltip='Add *.DATA Files Recursively'),
                 sg.Button('Add Ensembles', tooltip='Add Ensemble Directories Recursively'),
                 sg.Button('Clear', tooltip='Clear Output'),
                 sg.Button('Copy', tooltip='Copy Output to Clipboard'), sg.Button('List'),
                 sg.Button('Remove', tooltip='Remove Data Files'), sg.Submit(), sg.Button('Help'), sg.Exit()]]
    window1 = sg.Window('Compress Job Files', layout=layout1, finalize=True)
    #
    #   Set Output Multiline Window for CPRINT and Check If ZIP Package is Available
    #
    sg.cprint_set_output_destination(window1, outlog)
    compress_chk('zip', window1)
    #
    #   Define GUI Event Loop, Read Buttons, and Make Callbacks etc. Section
    #
    while True:
        (event, values) = window1.read()

        if event == sg.WIN_CLOSED:
            break

        jobopt  = values[0]
        #
        # Add Files
        #
        if event == 'Add':
            jobs = sg.popup_get_file('Select Job Data Files to Compress', no_window=False,
                                   default_path=str(Path().absolute()), initial_folder=str(Path().absolute()),
                                   multiple_files=True, file_types=[('OPM', ['*.data', '*.DATA'])])
            if jobs is not None:
                jobs = jobs.split(';')
                for job in jobs:
                    joblist1.append(job)

                window1['_joblist1_'].update(joblist1)
            continue
        #
        # Add Files Recursively
        #
        if event == 'Add Recursively':
            jobdir = sg.popup_get_folder('Select Job Directory for Data Files to Compress Recursively',
                                         default_path=str(Path().absolute()), initial_folder=Path().absolute())
            jobs   = [job for job in Path(jobdir).rglob('*') if job.suffix in ['.DATA', '.data']]
            if len(jobs) == 0:
                sg.popup_ok('No Simulation Input Files Found', title='OPMRUN Add Recursively',
                            no_titlebar=False, grab_anywhere=False, keep_on_top=True)
                continue
            else:
                text = sg.popup_yes_no('Found a Total of ' + str(len(jobs)) + ' Simulation Input Files.\n',
                                       'Do you wish to add all this files to the job queue?',
                                       title='OPMRUN Add Recursively',
                                       no_titlebar=False, grab_anywhere=False, keep_on_top=True)
                if text == 'Yes':
                    joblist1 = jobs
                    window1['_joblist1_'].update(joblist1)
                continue
        #
        # Add Files Ensembles
        #
        if event == 'Add Ensembles':
            jobdir = sg.popup_get_folder('Select Main Ensemble Directory for Directory Compression Recursively',
                                         default_path=str(Path().absolute()), initial_folder=Path().absolute())
            jobs   = [job for job in Path(jobdir).glob('**/')]
            jobs   = jobs[1:]
            if len(jobs) == 0:
                sg.popup_ok('No Ensemble Directories Found', title='OPMRUN Add Ensembles',
                            no_titlebar=False, grab_anywhere=False, keep_on_top=True)
                continue
            else:
                text = sg.popup_yes_no('Found a Total of ' + str(len(jobs)) + ' Ensemble Directories.\n',
                                       'Do you wish to add all this Ensemble Directories to the job queue?',
                                       title='OPMRUN Add Ensembles',
                                       no_titlebar=False, grab_anywhere=False, keep_on_top=True)
                if text == 'Yes':
                    joblist1 = jobs
                    window1['_joblist1_'].update(joblist1)
                continue
        #
        # Clear Output
        #
        if event == 'Clear':
            window1[outlog].update('')
            continue
        #
        # Copy Output to Clipboard
        #
        elif event == 'Copy':
            copy_to_clipboard(window1[outlog].get())
            sg.popup_timed('Output Copied to Clipboard', no_titlebar=False, grab_anywhere=False, keep_on_top=True)
            continue
        #
        # Exit
        #
        elif event == 'Exit':
            text = sg.popup_yes_no('Exit Compress Utility?', no_titlebar=False,
                                   grab_anywhere=False, keep_on_top=False)
            if text == 'Yes':
                break
            else:
                continue
        #
        # Help
        #
        elif event == 'Help':
            compress_help(opmoptn)
        #
        # Get Directory and List Files
        #
        if event == 'List':
            jobpath = sg.popup_get_folder('Select Directory', no_window=False,
                                        default_path=str(Path().absolute()), initial_folder=str(Path().absolute()))
            if jobpath is not None:
                error = change_directory(jobpath, popup=True, outprt=True)
                if not error:
                    jobpath = Path().absolute()
                    for file in Path(jobpath).glob("*.data"):
                        sg.cprint(str(Path(file).name))
                    for file in Path(jobpath).glob('*.DATA'):
                        sg.cprint(str(Path(file).name))
                    sg.cprint('Listing Complete ' + str(jobpath))
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
                sg.cprint('\nStart Compression')
                (job, jobcmd, jobpath, jobbase, jobroot, jobfile, jobzip) = compress_cmd(cmd)
                #
                # File or Ensemble Compression
                #
                if Path(cmd).is_file():
                    error  = change_directory(jobpath, popup=True, outprt=True)
                    jobcmd = wsl + zipcmd + str(jobzip) + ' ' + str(jobfile)
                else:
                    error  = change_directory(jobcmd, popup=True, outprt=True)
                    jobcmd = wsl + zipcmd + str(jobzip) + ' ' + '*.*'
                if not error:
                    sg.cprint('   ' + jobcmd)
                    run_command(jobcmd, timeout=None, window=window1)
                    sg.cprint('End Compression')
                    window1.refresh()

            window1['_joblist1_'].update(joblist1)
            continue

    window1.Close()
    return()


def compress_help(opmoptn):
    """Compress and Uncompress Help

    Display compress and uncompress help information.

    Parameters
    ----------
    opmoptn; dict
        A dictionary containing the OPMRUN default parameters

    Returns
    ------
    None
    """

    helptext = (
                'OPMRun is a Graphical User Interface ("GUI") program for the Open Porous Media ("OPM") Flow ' +
                'simulator. \n' +
                '\n'
                'The Compress and Uncompress utilities enable compression and uncompression to be performed on ' +
                'OPM Flow datasets. Currently the following options are available:\n\n' +
                'Add             - Allows one to select the individual files, *.DATA for \n' +
                '                  compression jobs and *.ZIP for uncompressing jobs.\n' +
                'Add Recursively - Lets one select the main directory, and all files within and\n' +
                '                  below the selected directory will be selected, based on \n' +
                '                  the compression (*.DATA) and uncompression (*.ZIP) option.\n' +
                'Add Ensembles   - Select the main Ensemble directory, and all directories \n' +
                '                  within and below will be selected. All files within a \n' +
                '                  a directory will be compressed into one zip file. Use the \n' +
                '                  Add Recursively uncompression (*.ZIP) option to unzip the \n' +
                '                  files.\n' +
                'Clear           - Clears the Output window.\n' +
                'List            - Allows one to select a directory and display all the *.DATA\n' +
                '                  or *.ZIP files.\n' +
                'Remove          - Remove all compression jobs from the queue.\n' +
                'Submit          - Submit all compression jobs for processing.\n' +
                'Exit            - Exit the utility.\n' +
                '\n' +
                'For the compression option one also has the option to remove the files once they have been ' +
                'compressed in order to save space.\n\n' +
                'The uncompressing options include being able or not able to over write existing files, as well as ' +
                'the option to remove the zip files or to keep the zip files once all the files have been ' +
                'uncompressed. \n\n' +
                'See the OPM Flow manual for further information. \n')

    opm_popup('Compression Utility Help', helptext, 25, font= (opmoptn['output-font'],opmoptn['output-font-size']))


def uncompress_files(opmoptn):
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

    if sg.running_windows():
        wsl = 'wsl '
    else:
        wsl = ''
    joblist1 = []

    outlog   = '_outlog1_'+sg.WRITE_ONLY_KEY
    layout1  = [[sg.Text('Select Multiple Archive Files to Uncompress')],
                [sg.Listbox(values='', size=(100, 10), key='_joblist1_',
                            font=(opmoptn['output-font'], opmoptn['output-font-size']))],
                [sg.Text('Output')],
                [sg.Multiline(key=outlog, size=(100, 20), text_color='blue', autoscroll=True,
                              font=(opmoptn['output-font'], opmoptn['output-font-size']))],
                [sg.Text('Uncompress Options', size=(42,1)),sg.Text('Compressed File Options' )],
                [sg.Radio('Uncompress and Keep Existing Files', "bRadio1", size=(40,1), default=True, key='_bRadio1_'),
                 sg.Radio('Keep Compressed File After Uncompressing', "bRadio2", default=True, key='_bRadio2_')],
                [sg.Radio('Uncompress and Overwrite Existing Files', "bRadio1", size=(40,1)),
                 sg.Radio('Delete Compressed File After Uncompressing', "bRadio2")],
                [sg.Button('Add'), sg.Button('Add Recursively'), sg.Button('Clear',  tooltip='Clear Output'),
                 sg.Button('Copy', tooltip='Copy Output to Clipboard'), sg.Button('List'),
                 sg.Button('Remove', tooltip='Remove Zip Files'), sg.Submit(), sg.Button('Help'),
                 sg.Exit()]]
    window1 = sg.Window('Uncompress Job Files', layout=layout1, finalize=True)
    #
    #   Set Output Multiline Window for CPRINT and Check If ZIP Package is Available
    #
    sg.cprint_set_output_destination(window1, outlog)
    compress_chk('unzip', window1)
    #
    #   Define GUI Event Loop, Read Buttons, and Make Callbacks etc. Section
    #
    while True:
        (event, values) = window1.read()

        if event == sg.WIN_CLOSED:
            break
        #
        # Add Files
        #
        if event == 'Add':
            jobs = sg.popup_get_file('Select ZIP Files to Uncompress', no_window=False,
                                   default_path=str(Path().absolute()), initial_folder=str(Path().absolute()),
                                   multiple_files=True, file_types=[('zip', ['*.zip', '*.ZIP'])])
            if jobs is not None:
                jobs = jobs.split(';')
                for job in jobs:
                    joblist1.append(job)

                window1['_joblist1_'].update(joblist1)
            continue
        #
        # Add Files Recursively
        #
        if event == 'Add Recursively':
            jobdir = sg.popup_get_folder('Select Job Directory for ZIP Files to Uncompress Recursively',
                                         default_path=str(Path().absolute()), initial_folder=Path().absolute())
            jobs   = [job for job in Path(jobdir).rglob('*') if job.suffix in ['.zip', '.ZIP']]
            if len(jobs) == 0:
                sg.popup_ok('No ZIP Files Found', title='OPMRUN Add Recursively',
                            no_titlebar=False, grab_anywhere=False, keep_on_top=True)
                continue
            else:
                text = sg.popup_yes_no('Found a Total of ' + str(len(jobs)) + ' ZIP Files.\n',
                                       'Do you wish to add all these files to the job queue?',
                                       title='OPMRUN Add Recursively',
                                       no_titlebar=False, grab_anywhere=False, keep_on_top=True)
                if text == 'Yes':
                    joblist1 = jobs
                    window1['_joblist1_'].update(joblist1)
                continue
        #
        # Clear Output
        #
        if event == 'Clear':
            window1[outlog].update('')
            continue
        #
        # Copy Output to Clipboard
        #
        elif event == 'Copy':
            copy_to_clipboard(window1[outlog].get())
            sg.popup_timed('Output Copied to Clipboard', no_titlebar=False, grab_anywhere=False, keep_on_top=True)
            continue
        #
        # Exit
        #
        elif event == 'Exit':
            text = sg.popup_yes_no('Exit Uncompress Utility?', no_titlebar=False,
                                   grab_anywhere=False, keep_on_top=False)
            if text == 'Yes':
                break
            else:
                continue
        #
        # Help
        #
        elif event == 'Help':
            compress_help(opmoptn)
        #
        # Get Directory and List Files
        #
        if event == 'List':
            jobpath = sg.popup_get_folder('Select Directory', no_window=False,
                                        default_path=str(Path().absolute()), initial_folder=str(Path().absolute()))
            if jobpath is not None:
                error = change_directory(jobpath, popup=True, outprt=True)
                if not error:
                    jobpath = Path().absolute()
                    for file in Path(jobpath).glob("*.zip"):
                        sg.cprint(str(Path(file).name))
                    for file in Path(jobpath).glob('*.ZIP'):
                        sg.cprint(str(Path(file).name))
                    sg.cprint('Listing Complete ' + str(jobpath))
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
                sg.cprint('Start Uncompression')
                (job, jobcmd, jobpath, jobbase, jobroot, jobfile, jobzip) = compress_cmd(cmd)

                error = change_directory(jobpath, popup=True, outprt=True)
                if not error:
                    jobcmd = wsl + zipcmd + str(jobzip)
                    sg.cprint('   ' + jobcmd)
                    sg.cprint(str(jobpath))
                    run_command(jobcmd, timeout=None, window=window1)
                    if not values['_bRadio2_']:
                        jobcmd = wsl + 'rm -v ' + str(jobzip)
                        sg.cprint('   ' + jobcmd)
                    run_command(jobcmd, timeout=None, window=window1)
                    sg.cprint('End Uncompressing')
                    window1.refresh()

            window1['_joblist1_'].update(joblist1)
            continue

    window1.Close()
    return()

# ======================================================================================================================
# End of OPM_COMMON.PY
# ======================================================================================================================