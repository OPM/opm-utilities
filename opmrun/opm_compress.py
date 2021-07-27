# ======================================================================================================================
#
"""OPM_COMPRESS.py - Compression Utility

This module contains the compress.pt and uncompress.py functions to compress/uncompress simulation cases input and
output files into a casename.zip file.

Program Documentation
---------------------
Only Python 3 is supported and tested Python2 support has been depreciated.

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

from opm_common import (change_directory, run_command)

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


def compress_files(opmoptn):
    """Compress All Jobs Input and Output into a Zip File Using the Base Name

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

    joblist1 = []
    outlog   = '_outlog1_'+sg.WRITE_ONLY_KEY
    layout1  = [[sg.Text('Select Multiple Job Data Files to Compress'                             )],
                [sg.Listbox(values='', size=(100, 10), key='_joblist1_',
                            font=(opmoptn['output-font'], opmoptn['output-font-size'])            )],
                [sg.Text('Output'                                                                 )],
                [sg.Multiline(key=outlog, size=(100, 15), text_color='blue', autoscroll=True,
                              font=(opmoptn['output-font'], opmoptn['output-font-size'])          )],
                [sg.Text('Compression Options'                                                    )],
                [sg.Radio('Compress Job' , "bRadio", default=True                                 )],
                [sg.Radio('Compress Job and then Remove Job Files', "bRadio"                      )],
                [sg.Button('Add'), sg.Button('Clear',  tooltip='Clear Output'), sg.Button('List'),
                                   sg.Button('Remove', tooltip='Remove Data Files'), sg.Submit(), sg.Exit()]]
    window1 = sg.Window('Compress Job Files', layout=layout1)
    #
    #   Set Output Multiline Window for CPRINT
    #
    sg.cprint_set_output_destination(window1, outlog)
    #
    #   Define GUI Event Loop, Read Buttons, and Make Callbacks etc. Section
    #
    while True:
        (event, values) = window1.read()
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
        # Clear Output
        #
        if event == 'Clear':
            window1[outlog].update('')
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
        elif event == sg.WIN_CLOSED:
            break
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
                sg.cprint('Start Compression\n')
                (job, jobcmd, jobpath, jobbase, jobroot, jobfile, jobzip) = compress_cmd(cmd)

                error = change_directory(jobpath, popup=True, outprt=True)
                if not error:
                    jobcmd = zipcmd + str(jobzip) + ' ' + str(jobfile)
                    sg.cprint('   ' + jobcmd)
                    run_command(jobcmd, timeout=None, window=window1)
                    sg.cprint('End Compression')
                    window1.refresh()

            window1['_joblist1_'].update(joblist1)
            continue

    window1.Close()
    return()


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

    joblist1 = []
    outlog   = '_outlog1_'+sg.WRITE_ONLY_KEY
    layout1  = [[sg.Text('Select Multiple Archive Files to Uncompress'                           )],
                [sg.Listbox(values='', size=(100, 10), key='_joblist1_',
                            font=(opmoptn['output-font'], opmoptn['output-font-size']))],
                [sg.Text('Output')],
                [sg.Multiline(key=outlog, size=(100, 15), text_color='blue', autoscroll=True,
                              font=(opmoptn['output-font'], opmoptn['output-font-size']))],
                [sg.Text('Uncompress Options'                                                 )],
                [sg.Radio('Uncompress and Keep Existing Files'        , "bRadio1", default=True,
                          key='_bRadio1_'                                                        )],
                [sg.Radio('Uncompress and Overwrite Existing Files'   , "bRadio1"                )],
                [sg.Text('Compressed File Options'                                               )],
                [sg.Radio('Keep Compressed File After Uncompressing'  , "bRadio2", default=True,
                          key='_bRadio2_'                                                        )],
                [sg.Radio('Delete Compressed File After Uncompressing', "bRadio2"                )],
                [sg.Button('Add'), sg.Button('Clear',  tooltip='Clear Output'), sg.Button('List'),
                                   sg.Button('Remove', tooltip='Remove Zip Files'), sg.Submit(), sg.Exit()]]
    window1 = sg.Window('Uncompress Job Files', layout=layout1)
    #
    #   Set Output Multiline Window for CPRINT
    #
    sg.cprint_set_output_destination(window1, outlog)
    #
    #   Define GUI Event Loop, Read Buttons, and Make Callbacks etc. Section
    #
    while True:
        (event, values) = window1.read()

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
        # Clear Output
        #
        if event == 'Clear':
            window1[outlog].update('')
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
        elif event == sg.WIN_CLOSED:
            break
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
                    jobcmd = zipcmd + str(jobzip)
                    sg.cprint('   ' + jobcmd)
                    sg.cprint(str(jobpath))
                    run_command(jobcmd, timeout=None, window=window1)
                    if not values['_bRadio2_']:
                        jobcmd = 'rm -v ' + str(jobzip)
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