# ======================================================================================================================
#
"""OPM_SENSITIVITY.py - OPMRUN Sensitivity Case Generator Utility

OPM Flow  Sensitivity Case Generator Utility is a Graphical User Interface ("GUI") program for the Open Porous Media
("OPM") Flow simulator.

This module generates sensitivity input decks using a base template input deck and a list of sensitivity factors
with Low, Best and High estimates. The utility generates both the required OPM Flow PARAM file and DATA files for
various sensitivity scenarios. A sensitivity scenario is a combination of the the various sensitivity factors, for
example one can run all the Low factors as one sensitivity case, or a full factorial scenario on the Low and High
sensitivity factors. Various Experimental Designs scenarios are included in the package, including full factorial,
two-level full factorial, Plackett-Burman and Box-Behnken designs based on the pyDOE2 package.

The factors (the statistical term for the variables being used) are defined as $X01 to $X20, as presented on the
"Factors" tab. These names are used in a "Base" template input deck to define the location and values to be substituted
by the factor values for a given sensitivity scenario. The factor values can can have any value, including a string. For
example, if one wanted to run sensitivities with different relative permeability data sets, on could have the different
data sets in different files (Low-RelPerm, High-RelPerm, for example) and set the factors to these strings. In the
"Base" template file one would have an INCLUDE keyword of the form INCLUDE $X01 /.

To enter the data for a factor click on the table row and a dialog box will popup allowing one to enter the required
data; factor description, and the factor low, Best and High values. Right clicking on the factor description will
present a list of standard factor descriptions. Note it is only necessary to enter the data required to define the
selected scenario, so for example, if only Low and High cases are going to be run then one does not have to enter
values for the Best case.

The buttons at the base of the screen perform the following actions:

"Base" - Selects the "Base" template file and once loaded is displayed in the "Base" tab.
"Clear" - Clears the factor descriptions and values.
"Copy"  - Copies the displayed factor table to the clipboard.
"Generate - Generates the PARAM and DATA files based on the factors and the selected scenario.
"Load" - loads a factor table from a previously "Saved" CSV file.
"Save" - Saves the factor table to a CSV file.
"Help" - Displays help information.
"Exit" - Terminates the program.

Note that the "Generate" option also generates an OPMRUN queue file that contains all the jobs in the scenario. One
can then load the queue file into OPMRUN and run all the jobs.

See the OPM Flow manual for further information.

Program Documentation
---------------------
Only Python 3 is supported and tested Python2 support has been depreciated.

2021.07-01 - Major re-factoring and function re-naming for consistency with other modules, together with minor bug
             fixes.
2020.04.01 - Initial release of OPMSENS
           - Support for Python 3 only.
           - Based PySimpleGUI version 4.14.1
           - Users NumPy/SciPy Docstrings documentation format.

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
Date    : 17-Jul-2021

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
from pathlib import Path
from psutil import cpu_count
#
# Import Required Non-Standard Modules
#
import pandas as pd
import PySimpleGUI as sg
import pyDOE2
#
# Import OPM Common Modules
#
from opm_common import get_time, opm_popup, set_gui_options, window_debug

# ----------------------------------------------------------------------------------------------------------------------
# Define Modules Section
# ----------------------------------------------------------------------------------------------------------------------
def sensitivity_base_file(jobparam, jobsys, window1):
    """Add a OPM Flow Simulation job to the Job List Queue

    The function adds a DATA file to the job list queue by selecting the file via a window, and also defining the job
    parameters for this series of jobs. Multiple jobs can be selected at a time.

    Parameters
    ----------
    jobparam : str
        OPM Flow PARAM file data set
    jobsys : dict
        Contains a dictionary list of all OPMRUN System parameters
    window : PySimpleGUI window
        The PySimpleGUI window that the output is going to (needed to do refresh on).

    Returns
    -------
    jobfile : str
        Base file name.
    """

    jobfile = ''
    if not jobparam:
        sg.popup_error('Job Parameters Missing; Cannot Add Cases - Check if OPM Flow is Installed',
                      no_titlebar=False, grab_anywhere=False, keep_on_top=True)
        return()

    layout1 = [[sg.Text('Base and Sensitivity Cases File Options')],
               [sg.InputText(key='_jobfile_', size=(80, None)),
                sg.FilesBrowse(target='_jobfile_', initial_folder=Path().absolute(),
                               file_types=[('OPM', ['*.data', '*.DATA']), ('All', '*.*')])],
               [sg.Text('Parameter File Options')],
               [sg.Radio('Keep Existing Parameter File'    , "bRadio", key='_keep_', default =True)],
               [sg.Radio('Overwrite Existing Paramter File', "bRadio", key='_write_')],
               [sg.Submit(), sg.Exit()]]
    window2 = sg.Window('Select OPM Flow Input File', layout=layout1)

    while True:
        (event, values) = window2.read()
        if event == 'Exit' or event == sg.WIN_CLOSED:
            break

        jobfile = values['_jobfile_']
        if event == 'Submit':
            if not Path(jobfile).is_file():
                sg.popup_error('Base Simulation Parameter File Does Not Exist:\n\n' + str(jobfile) + '\n',
                               title='OPMRUN Sensitivity', no_titlebar=False, grab_anywhere=False, keep_on_top=True)
                jobfile = ''
                window1['_basefile_'].update(value=jobfile)
                continue
            # Read in Data File
            file = open(jobfile, 'r')
            data = file.read()
            file.close()
            # Update Display
            window1['_basefile_'].update(value=jobfile)
            window1['_basedeck_'].update('')
            window1['_basedeck_'].update(value=data)
            window1['_tab_base_'].select()
            # PARAM File Processing
            jobbase  = Path(jobfile).name
            fileout  = Path(jobfile).with_suffix('.param')
            if fileout.is_file() and values['_write_']:
                sensitivity_base_param(jobparam, jobbase, fileout, 'Overwritten', jobsys)
            if not fileout.is_file():
                sensitivity_base_param(jobparam, jobbase, fileout, 'Created', jobsys)
            break
    window2.Close()
    return(jobfile)


def sensitivity_base_param(jobparam, jobbase, jobfile, jobmsg, jobsys):
    """Save a Job's Parameter File

    Functions saves the current default parameter set to a job's parameter file that used to run an OPM Flow job. The
    file also contains some additional comments including the user who created the job for documentation.

    Parameters
    ----------
    jobparam : list
        OPM Flow PARAM parameter list
    jobbase :str
        The base part of the job file name
    jobfile : str
        The full job file name
    jobmsg : str
        Short message to be displayed after the file has been written, normally set to 'Created or 'Overwritten'
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
            file.write('EclDeckFileName="' + jobbase + '"\n')
        elif 'ecl-deck-file-name' in x:
            file.write('ecl-deck-file-name="' + jobbase + '"\n')
        else:
            file.write(x + '\n')
    file.write('# \n')
    file.write('# End of Parameter File \n')
    file.close()
    sg.popup_ok('Base Simulation Parameter File ' + jobmsg + ':\n\n' + str(jobfile) + '\n',
                title='OPMRUN Sensitivity', no_titlebar=False, grab_anywhere=False, keep_on_top=True)


def sensitivity_check(basefile, header, factors, scenario):
    """ Checks Files and Data Prior to Generating Sensitivity Scenarios

    Parameters
    ----------
    basefile : str
        The basefile used to generate all the cases
    header : list
        A list of of header names
    factors : table
        A table of design factors
    scenario : str
        The type of scenario to be generated

    Returns
    ------
    checkerr : int
        An error counter with zero being no errors found
    """

    sg.cprint('Checkerr: Start')
    checkerr  = 0
    #
    # File Checks
    #
    if Path(basefile).is_file():
        parmfile = Path(basefile).with_suffix('.param')
        # Check for PARAM File
        if Path(parmfile).is_file():
            sg.cprint('Checkerr: Base File Parameter File Found:\n'  + str(parmfile.name))
        # PARAM File Missing
        else:
            sg.cprint('Checkerr: Base File Parameter File Does Not Exist\n' + 'Checkerr: ' + str(parmfile.name))
            checkerr = checkerr + 1
    else:
        # Base DATA File Missing
        sg.cprint('Checkerr: Base File Does Not Exist')
        checkerr = checkerr + 1
    #
    # Factor Design Checks
    #
    try:
        df   = pd.DataFrame(factors, columns=header)
        low  = (df['Low' ].values == '').sum()
        best = (df['Best'].values == '').sum()
        high = (df['High'].values == '').sum()
        df   = df[df != ''].dropna()
        nrow = df.shape[0]
        ncol = df.shape[1]

    except Exception as error:
        checkerr = checkerr + 1
        sg.cprint('Checkerr: Found ' + str(checkerr) + ' Errors That Need to be Resolved')
        sg.cprint('Checkerr: End')
        sg.popup_error('OPMSENS Error Checking Factors - Cannot Continue',
                      no_titlebar=False, grab_anywhere=False, keep_on_top=True)
        return checkerr
    #
    # Factorial and Non-Factorial Checks
    #
    if nrow == 0:
        sg.cprint('Checkerr: No Factor Values')
        checkerr = checkerr + 1

    if scenario == 'Low and High - One Job per Factor' and low != high:
        sg.cprint('Checkerr: Low and High - One Job per Factor Error - ' +
                  'Number of Factors for Low and High are Different')
        checkerr = checkerr + 1

    if scenario == 'Factorial Low, Best and High Full' and nrow >= 6:
        sg.cprint('Checkerr: Factorial Low, Best and High Full Error - Number of Factors is Greater Than ' + str(nrow))
        checkerr = checkerr + 1
    #
    # Checkerr Message
    #
    if checkerr:
        sg.cprint('Checkerr: Found ' + str(checkerr) + ' Error(s) That Need(s) to be Resolved')
        sg.popup_error('OPMSENS Sensitivity Generation Errors \n Unable to Generate Runs \n See Messages',
                      no_titlebar=False, grab_anywhere=False, keep_on_top=True)

    sg.cprint('Checkerr: End')
    return(checkerr)


def sensitivity_clean(basefile):
    """ Cleans Scenario Directory

    Clean (deletes) existing DATA, PARAM and all OPM Flow Output files

    Parameters
    ----------
    basefile : str
        The basefile used to generate all the cases

    Returns
    -------
    None
    """

    jobdir  = Path(basefile).parent
    jobname = Path(basefile).stem + '-*'
    joblst  = list(jobdir.glob(jobname))
    sg.cprint('WriteClean: ' + str(jobdir))
    for job in joblst:
        Path(job).unlink()
        sg.cprint('WriteClean: Deleted ' + str(Path(job).name))


def sensitivity_edit_factor(header, nrow, factors):
    """ Edit Factor Table

    Enables editing of the factor table and allows for inserting "standard" factor descriptions

    Parameters
    ----------
    header : list
        A list of of header names
    nrow : int
        The row number in the table to be edited
    factors : table
        A table of design factors

    Returns
    ------
    factors : table
        The updated table of design factors
    """

    factorlst = ['GRID - PERMX', 'GRID - PERMY', 'GRID - PERMZ', 'GRID - PORO', 'GRID - PORV',
                 'GRID - MULTX', 'GRID - MULTY', 'GRID - MULTZ',
                 'ENDPOINT - Krow(Swc)', 'ENDPOINT - Krow(Sorw)', 'ENDPOINT - Krw(Swc)', 'ENDPOINT - Krw(Sorw)',
                 'ENDPOINT - Krw(Swmax)',
                 'RATE - FGPR', 'RATE - FOPR', 'RATE - FWPR', 'RATE - FGIR', 'RATE - FOIR', 'RATE - FWIR',
                 'RATE - GGPR', 'RATE - GOPR', 'RATE - GWPR', 'RATE - GGIR', 'RATE - GOIR', 'RATE - GWIR',
                 'RATE - WGPR', 'RATE - WOPR', 'RATE - WWPR', 'RATE - WGIR', 'RATE - WOIR', 'RATE - WWIR',
                 'WELL - BHP',  'WELL - PI'  , 'WELL - SKIN'
                 ]

    layout2 = [[sg.Text(header[0], size=(10, 1)),
                sg.Text(header[1], size=(30, 1)),
                sg.Text(header[2], size=(10, 1)),
                sg.Text(header[3], size=(10, 1)),
                sg.Text(header[4], size=(10, 1))],

               [sg.Input(factors[nrow][0], size=(11, 1), disabled=True, key='_var01_'),
                sg.Input(factors[nrow][1], size=(30, 1), right_click_menu=['Option', ['Factors']], key='_var02_'),
                sg.Input(factors[nrow][2], size=(11, 1), key='_var03_'),
                sg.Input(factors[nrow][3], size=(11, 1), key='_var04_'),
                sg.Input(factors[nrow][4], size=(11, 1), key='_var05_')],

               [sg.Submit(), sg.Cancel()]]

    window2 = sg.Window('Factor Properties', layout=layout2, finalize=True,
                        no_titlebar=False, grab_anywhere=False, keep_on_top=True)
    while True:
        event2, values2 = window2.read()
        if event2 == 'Factors':
            layout3 = [[sg.Text('Standard Factors')],
                       [sg.Listbox(values=factorlst, enable_events=True, size=(30, 15))],
                       [sg.Text('')]]
            window3 = sg.Window('Standard Factors', layout=layout3, finalize=True,
                                no_titlebar=False, grab_anywhere=False, keep_on_top=True)
            (event3, values3) = window3.read()
            if event3 != None:
                window2['_var02_'].update(value=(values3[0][0]))
            window3.Close()
            continue

        elif event2 == 'Submit':
            factors[nrow] = [values2['_var01_'], values2['_var02_'], values2['_var03_'],
                             values2['_var04_'], values2['_var05_']]
            break

        else:
            break

    window2.Close()
    return factors


def sensitivity_set_factors(header, nrow):
    """ Create Empty Factor Table

    Creates an empty factor table so clear the factor table

    Parameters
    ----------
    header : list
        A list of of header names
    nrow : int
        The row number in the table to be edited

    Returns
    ------
    factors : table
        The updated table of design factors
    """

    df     = pd.DataFrame(columns=header)
    for i in range (nrow):
        df.loc[i] = ['$X' + str(i+1).zfill(2), '', '', '' , '']

    df.index += 1
    factors  = df.values.tolist()
    return factors


def sensitivity_write_cases(basefile, header, factors, scenario):
    """ Main Function for Writing out Scenario Cases

    This is the main function that controls the writing out of the various requested scenario cases (jobs). The
    function first calls the opmsens_checkerr routine to check for errors and then the opmsens_clean routine to
    remove previously created scenario files. After which the opmsens_write_param and opmsens_write_data functions are
    called to create the scenario PARAM and DATA files

    Parameters
    ----------
    basefile : str
        The basefile used to generate all the cases
    header : list
        A list of of header names
    factors : table
        A table of design factors
    scenario : str
        The type of scenario to be generated

    Returns
    ------
    None
    """

    # Check for Errors and Return if Errors Found
    checkerr = sensitivity_check(basefile, header, factors, scenario)
    if checkerr:
        return()
    #
    # Cleanup Existing Files
    #
    sensitivity_clean(basefile)
    #
    # Define Factor and Job Data Frame
    #
    df                = pd.DataFrame(factors, columns=header)
    df                = df[df != ''].dropna()
    jobdf             = pd.DataFrame()
    jobdf[header[1]] = df [header[1]]
    for slevel in ['Low', 'Best', 'High']:
        if slevel in scenario:
            jobdf[slevel] = df[slevel]

    nfactor  = jobdf.shape[0]
    nlevel   = jobdf.shape[1]
    #
    # Write PARAM and DATA Files
    #
    jobs     = []
    jobstart = 1
    joberr   = False
    jobdata  = Path(basefile)
    jobparam = Path(basefile).with_suffix('.param')
    jobque   = Path(basefile).with_suffix('.que')
    sg.cprint('Scenario:  ' + scenario + ' Start')
    #
    # Low, Best and High Scenario
    #
    if 'Scenario' in scenario:
        jobnum = 0
        for joblevel in range(1, nlevel):
            (joberr, jobs) = sensitivity_write_param(jobstart, jobnum, jobparam, jobdata, jobs)
            if joberr:
                break
            joberr = sensitivity_write_data(scenario, joblevel, nfactor, jobdf, jobstart, jobnum, jobdata)
            if joberr:
                break
            jobstart = jobstart + joblevel
    #
    # One Job per Factor
    #
    elif 'One Job per Factor' in scenario:
        for joblevel in range(1, nlevel):
            for jobnum in range(0, nfactor):
                (joberr, jobs) = sensitivity_write_param(jobstart, jobnum, jobparam, jobdata, jobs)
                if joberr:
                    break
                joberr = sensitivity_write_data(scenario, joblevel, nfactor, jobdf, jobstart, jobnum, jobdata)
                if joberr:
                    break
            jobstart = jobstart + nfactor
    #
    # Factorial Low and High Full
    #
    elif 'Factorial' in scenario:
        #
        # Obtain DOE Matrix and Convert to Data Frame
        #
        doedata = pd.DataFrame()
        if 'Factorial Low and High Full' in scenario:
            doedata = pyDOE2.ff2n(nfactor) + 2

        if 'Factorial Low and High Plackett-Burman' in scenario:
            doedata = pyDOE2.pbdesign(nfactor) + 2

        if 'Factorial Low, Best and High Full' in scenario:
            doedata = (pyDOE2.fullfact([nlevel - 1]*nfactor)) - 1

        if 'Factorial Low, Best and High Box-Behnken' in scenario:
            doedata = pyDOE2.bbdesign(nfactor)

        doedf = pd.DataFrame(data=doedata).transpose()
        doedf = doedf.rename(columns=lambda x: 'RUN' + str(x + 1).zfill(3), inplace=False)
        #
        # Set Factor Values
        #
        for n in range(0, nfactor):
            doedf.iloc[n, :] = doedf.iloc[n, :].replace([1.0, 2.0, 3.0], [df.iloc[n, 2], df.iloc[n, 3], df.iloc[n, 4]])
        #
        # Merge Data Frames and Write Out Files
        #
        jobdf            = pd.DataFrame()
        jobdf[header[1]] = df[header[1]]
        jobdf            = pd.concat([jobdf, doedf], axis=1)
        nfactor          = jobdf.shape[0]
        nlevel           = jobdf.shape[1]
        jobstart         = 0
        for joblevel in range(1, nlevel):
            jobnum = joblevel
            (joberr, jobs) = sensitivity_write_param(jobstart, jobnum, jobparam, jobdata, jobs)
            if joberr:
                break
            joberr = sensitivity_write_data(scenario, joblevel, nfactor, jobdf, jobstart, jobnum, jobdata)
            if joberr:
                break

    sg.cprint('Scenario:  ' + scenario + ' End')
    if not joberr:
        text = sg.popup_yes_no('Scenario: ' + scenario + 'as Created ' + str(len(jobs)) + ' Jobs\n\n' +
                               'Do You Wish to Continue and Generate the OPMRUN Queue File to Run the Jobs?',
                               title='Scenario: ' + scenario, no_titlebar=False, grab_anywhere=False, keep_on_top=True)
        if text == 'Yes':
            sg.cprint('WriteQueu: Start')
            sensitivity_write_queue(jobs)
            sg.cprint('WriteQueu: End')
        else:
            sg.cprint('WriteQueu: Cancelled')
            sg.popup_ok('OPMRUN Queue File Generation Cancelled', title='Scenario: ' + scenario,
                        no_titlebar=False, grab_anywhere=False, keep_on_top=True)

    return()


def sensitivity_write_data(scenario, nlevel, nfactor, jobdf, jobstart, jobnum, jobbase):
    """ Write Scenario DATA File

    This routine writes out the OPM Flow DATA file for one case with the factor values for the scenario replacing the
    factor names, that is $X01 replced by the factor vlaue of this variable. A header is also written to the file to
    document the case being defined.

    Parameters
    ----------
    scenario : str
        The job scenario
    nlevel : int
        The design Level parameter
    nfactor : int
        The number of factors.
    jobdf : table
        Job data frame containing the factors
    jobstart : int
        The first job number counter
    jobnum : int
        The current job number
    jobbase : str
    the base parameter file used to create the case DATA file

    Returns
    -------
    joberr :bool
        set to True if errors otherwise false
    """

    joberr   = False
    jobnum   = str(jobnum + jobstart).zfill(3)
    jobname  = Path(jobbase).stem + '-' + jobnum + str(Path(jobbase).suffix)
    jobfile  = Path(jobbase).with_name(jobname)
    header   = '-- ' + '*'*129 + '\n'
    #
    # Create DATA File
    #
    try:
        file = open(jobfile, 'w')
        file.write(header)
        file.write('--                                      \n')
        file.write('-- OPMRUN SENSITIVITY GENERATOR CASE    \n')
        file.write('-- ---------------------------------    \n')
        file.write('--                                      \n')
        file.write('-- JOB SCENARIO                       : ' + str(scenario) + '\n')
        file.write('-- JOB BASE                           : ' + str(jobbase)  + '\n')
        file.write('-- JOB NAME                           : ' + str(jobname)  + '\n')
        for i in range(0, nfactor):
            file.write('--                                  \n')
            file.write('-- FACTOR LEVEL                       : ' + jobdf.columns[nlevel]           + '\n')
            file.write('-- FACTOR IDENTIFIER                  : ' + str('X')  + str(i + 1).zfill(2) + '\n')
            file.write('-- FACTOR DESCRIPTION                 : ' + jobdf.iloc[i, 0]                + '\n')
            file.write('-- FACTOR VALUE                       : ' + str('$X') + str(i + 1).zfill(2) + '\n')
        file.write('--                                      \n')
        file.write(header)
        base = Path(jobbase).read_text()
        file.write(base)
        file.close()

    except Exception as error:
        sg.popup_error('Error Writing: ' + '\n  \n' + str(jobfile), no_titlebar=False, grab_anywhere=False,
                       keep_on_top=True)
        sg.cprint('WriteParam: Error Writing - ' + str(jobname))
        return True
    #
    # DATA Template Processing
    #
    try:
        file = open(jobfile, 'r')
        data = file.read()
        file.close()
        for i in range(0, nfactor):
            xfac = str('$X') + str(i + 1).zfill(2)
            xdat = jobdf.iloc[i, nlevel]
            data = data.replace(xfac, str(xdat))
#           sg.Print(str(i) + '   ' + str(nlevel) + '  ' + str(xfac), '  ' + str(xdat))

        file = open(jobfile, 'w')
        file.write(data)
        file.close()
        sg.cprint('WriteData: Generated ' + str(jobname))

    except Exception as error:
        sg.popup_error('Error Processing Base Data File: ' + '\n  \n' + str(jobfile), title='OPMRUN Sensitivity',
                      no_titlebar=False, grab_anywhere=False, keep_on_top=True)
        sg.cprint('WriteData: Error Processing Base Data File ' + str(jobname))
        return True

    return joberr


def sensitivity_write_param(jobstart, jobnum, jobparm, jobdata, jobs):
    """ Write Scenario PARAM File

    This routine writes out the OPM Flow PARAM file for one case and substitutes the 'ecl-deck-file-name' variable
    with the correct file name for the case

    Parameters
    ----------
    jobstart : int
        The first job number counter
    jobnum : int
        The current job number
    jobparm: str
        The base parameter file used to create the case PARAM file
    jobdata: str
        The base data file used to create the case DATA file
    jobs: list
        A list of jobs for the job queue

    Returns
    -------
    joberr : bool
        Set to True for error otherwise False
    """

    joberr  = False
    jobnum  = str(jobnum + jobstart).zfill(3)
    jobname = Path(jobparm).stem + '-' + jobnum + str(Path(jobparm).suffix)
    jobfile = Path(jobparm).with_name(jobname)
    jobdeck = Path(jobdata).stem + '-' + jobnum + str(Path(jobdata).suffix)
    #
    # Create PARAM File
    #
    try:
        Path(jobfile).write_text(Path(jobparm).read_text())
    except Exception as error:
        sg.popup_error('Error Writing Parameter File: ' + '\n\n' + str(jobfile), str(error) + ': ' + str(type(error)),
                       title='OPMRUN Sensitivity', no_titlebar=False, grab_anywhere=False, keep_on_top=True)
        sg.cprint('WriteParam: Error Writing - ' + str(jobname))
        return True
    #
    # Edit PARAM File
    #
    try:
        file = open(jobfile, 'r')
        data = file.readlines()
        file.close()
        file = open(jobfile, 'w')
        for line in data:
            if 'ecl-deck-file-name=' in line:
                file.write('ecl-deck-file-name=' + str(jobdeck) + '\n')
            else:
                file.write(line)

        file.close()
        jobs.append(jobfile)
        sg.cprint('WriteParm: Generated ' + str(jobname))

    except Exception as error:
        sg.popup_error('Error Processing Parameter File ' + '\n\n' + str(jobfile), str(error) + ': ' + str(type(error)),
                       title='OPMRUN Sensitivity', no_titlebar=False, grab_anywhere=False, keep_on_top=True)
        sg.cprint('WriteParam: Processing Error - ' + str(jobname))
        return True

    return joberr, jobs


def sensitivity_write_queue(jobs):
    """Write Out Jobs to a OPMRUN Job Queue File

    Requests the job run parameters for the jobs in the jobs list and writes out the required job and job parameters
    to the job queue file

    Parameters
    ----------
    jobs: list
        A list of jobs to be written to the user selected job queue file

    Returns
    -------
    None
    """

    if jobs == []:
        sg.popup_ok('No Job Jobs to Process', no_titlebar=False, grab_anywhere=False, keep_on_top=True)
        return ()

    layout2 = [[sg.Text('OPMRUN Queue File')],
                [sg.InputText(key='_jobfile_', size=(80, None)),
                 sg.FileSaveAs(target='_jobfile_', initial_folder=Path(jobs[0]).parent,
                               file_types=[('OPMRUN Queue File', ['*.que', '*.QUE']), ('All', '*.*')])],
                [sg.Text('Run Parameters')],
                [sg.Radio('Sequential Run', "bRadio", key='_jobseq_', default=True)],
                [sg.Radio('Parallel Run  ', "bRadio", key='_jobpar_'),
                 sg.Text('No. of Nodes'),
                 sg.Listbox(values=list(range(1, cpu_count() + 1)), default_values=[1], size=(5, 3), key='_jobnode_')],
                [sg.Submit(), sg.Cancel()]]

    window2 = sg.Window('Select OPMRUN Queue File', layout=layout2, finalize=True,
                        no_titlebar=False, grab_anywhere=False, keep_on_top=True)

    (event, values) = window2.read()
    while True:
        jobfile = values['_jobfile_']
        jobseq  = values['_jobseq_']
        jobpar  = values['_jobpar_']
        jobnode = values['_jobnode_']
        jobcmd  = 'flow --parameter-file='
        if jobpar:
            jobcmd = 'mpirun -np ' + str(jobnode).strip("[]") + ' flow --parameter-file='

        if event == 'Submit':
            if jobfile:
                file = open(jobfile, 'w')
                file.write('# \n')
                file.write('# OPMRUN Queue File \n')
                file.write('# \n')
            #    file.write('# Created By  : ' + opmuser + '\n')
                file.write('# Date Created: ' + get_time() + '\n')
                file.write('# Queue Length: ' + str(len(jobs)) + '\n')
                file.write('# \n')
                for job in jobs:
                    file.write(jobcmd + str(job) + '\n')

                file.write('# \n')
                file.write('# End of Queue \n')
                file.close()

                sg.popup_ok('OPMRUN Queue File Saved to: ' + jobfile,
                            no_titlebar=False, grab_anywhere=False, keep_on_top=True)
                break
            else:
                sg.popup_error('OPMRUN Queue File Invalid: ' + jobfile,
                            no_titlebar=False, grab_anywhere=False, keep_on_top=True)
                continue
        else:
            break

    window2.Close()
    return()


def sensitivity_main(jobparam, opmoptn, opmsys):
    """OPMRUN Sensitivity Case Generator Utility Main Function

    OPM Flow  Sensitivity Case Generator Utility is a Graphical User Interface ("GUI") program for the Open Porous Media
    ("OPM") Flow simulator.

    This module generates sensitivity input decks using a base template input deck and a list of sensitivity factors
    with Low, Best and High estimates. The utility generates both the required OPM Flow PARAM file and DATA files for
    various sensitivity scenarios. A sensitivity scenario is a combination of the the various sensitivity factors, for
    example one can run all the Low factors as one sensitivity case, or a full factorial scenario on the Low and High
    sensitivity factors. Various Experimental Designs scenarios are included in the package, including full factorial,
    two-level full factorial, Plackett-Burman and Box-Behnken designs.

    This is the main display GUI module for the OPM Keyword Generator program. The window object, window1, is the main
    global window object for other routines to access in this module.

    Parameters
    ----------
    opmoptn; dict
        A dictionary containing the OPMRUN default parameters

    Returns
    -------
    None
    """
    #
    # Initialize
    #
    set_gui_options()

    helptext = ('OPMRUN Sensitivity Case Generator Utility \n' +
                '\n'
                'OPM Flow  Sensitivity Case Generator Utility is a Graphical User Interface ("GUI") program for the ' +
                'Open Porous Media ("OPM") Flow simulator. \n'
                '\n'
                'This module generates sensitivity input decks using a base template input deck and a list of '       +
                'sensitivity factors with Low, Best and High estimates. The utility generates both the required '     +
                'OPM Flow PARAM file and DATA files for various sensitivity scenarios. A sensitivity scenario is a '  +
                'combination of the the various sensitivity factors, for example one can run all the Low factors as ' +
                'one sensitivity case, or a full factorial scenario on the Low and High sensitivity factors. '        +
                'Various Experimental Designs scenarios are included in the package, including full factorial, '      +
                'two-level full factorial, Plackett-Burman and Box-Behnken designs. \n'
                '\n'
                'The factors (the statistical term for the variables being used) are defined as $X01 to $X20, as '    +
                'presented on the "Factors" tab. These names are used in a "Base" template input deck to define the ' +
                'location and values to be substituted by the factor values for a given sensitivity scenario. The '   +
                'factor values can have any value, including a string. For example, if one wanted to run scenario'    +
                'sensitivities with different relative permeability data sets, one could have the different data '    +
                'sets in different files (Low-RelPerm, High-RelPerm, for example) and set the factors to these '      +
                'strings. In the "Base" template file one would have an INCLUDE keyword of the form INCLUDE $X01 /. \n'
                '\n'
                'To enter the data for a factor click on the table row and a dialog box will popup allowing one to '  +
                'enter the required data; factor description, and the factor low, Best and High values. Right '       +
                'clicking on the factor description will present a list of standard factor descriptions. Note it is ' +
                'only necessary to enter the data required to define the selected scenario, so for example, if only ' +
                'Low and High cases are going to be run then one does not have to enter values for the Best case. \n'   
                '\n'
                'The buttons at the base of the screen perform the following actions: \n'
                '\n'
                '"Base" - Selects the "Base" template file and once loaded is displayed in the "Base" tab. \n'
                '"Clean" - Cleans (deletes) all Cases based on the current "Base" file. \n'
                '"Clear" - Clears the factor descriptions and values.\n'
                '"Copy"  - Copies the displayed factor table to the clipboard. \n'
                '"Generate - Generates the PARAM and DATA files based on the factors and the selected scenario.\n'
                '"Load" - Loads a factor table from a previously "Saved" CSV file.\n'
                '"Save" - Saves the factor table to a CSV file.\n'
                '"Help" - Displays help information.\n'
                '"Exit" - Terminates the program.\n'
                '\n'
                'Note that the "Generate" option also generates an OPMRUN queue file that contains all the jobs in '  +
                'the scenario. One can then load the queue file into OPMRUN and run all the jobs.\n'
                '\n'
                'See the OPM Flow manual for further information. \n')
    #
    #  Define Constants
    #
    basefile  = ''
    checkerr  = True
    debug     = False
    header    = ['Factor', 'Factor Description', 'Low', 'Best', 'High']
    nrow      = 20
    ncol      = 105

    i         = 0
    factors   =  sensitivity_set_factors(header, nrow)

    scenarios = ['Low Scenario', 'Best Scenario', 'High Scenario', 'Low and High Scenario',
                 'Low One Job per Factor', 'Best One Job per Factor', 'High One Job per Factor',
                 'Low and High One Job per Factor',
                 'Factorial Low and High Full',
                 'Factorial Low and High Plackett-Burman',
                 'Factorial Low, Best and High Full',
                 'Factorial Low, Best and High Box-Behnken']
    # ------------------------------------------------------------------------------------------------------------------
    # Define Display Window col_widths=[12, 44, 12, 12, 12],
    # ------------------------------------------------------------------------------------------------------------------
    outlog     = '_outlog1_'+sg.WRITE_ONLY_KEY

    factlayout = [[sg.Text('Sensitivity Factor Parameters')],
                  [sg.Table(values=factors, headings=header, display_row_numbers=False, col_widths=[12, 55, 12, 12, 12],
                   num_rows=nrow, alternating_row_color='lightgreen', text_color='black', justification='left',
                   font=(opmoptn['output-font'], int(opmoptn['output-font-size']) + 1),
                   auto_size_columns=False, enable_events=True, select_mode='browse', key='_factors_')]]

    baselayout = [[sg.Text('Deck Sensitivity Base Template')],
                  [sg.Multiline(background_color='lightgreen', text_color='black', do_not_clear=True,
                                font=(opmoptn['output-font'], int(opmoptn['output-font-size']) - 1 ),
                                key='_basedeck_', size=(ncol + 33, 23))]]

    mainwind  = [[sg.Text('OPMSENS Deck Sensitivity Generation')],
                 [sg.TabGroup([
                    [sg.Tab('Factors', factlayout, key='_tab_factors_', title_color='black', background_color='white'),
                     sg.Tab('Base', baselayout, key='_tab_base_', title_color='darkgreen', background_color='white',
                            border_width=None)]],
                     title_color='black', background_color='white')],

                 [sg.Text('Sensitivity Base OPM Flow Input Deck Template')],
                 [sg.InputText(basefile, size=(ncol + 15, 1), tooltip='Name of Simulation File with $X01 Factor ' +
                               'Variables, all Cases Will be Generated in this Directory',
                               background_color='lightgreen', key='_basefile_')],

                 [sg.Text('Sensitivity Scenario Options')],
                 [sg.Listbox(values=scenarios, default_values=scenarios[0], size=(ncol + 14, 8), key='_scenarios_')],

                 [sg.Text('Messages')],
                 [sg.Multiline(key=outlog, size=(ncol +13, 5), text_color='blue', autoscroll=True,
                               font=(opmoptn['output-font'], opmoptn['output-font-size']))],

                 [sg.Text('')],

                 [sg.Button('Base'    , tooltip='Base Input and Parameter File'      , key='_base_'    ),
                  sg.Button('Clean'   , tooltip='Clean All Base Derived Runs'        , key='_clean_'   ),
                  sg.Button('Clear'   , tooltip='Clear All Factor Parameters'        , key='_clear_'   ),
                  sg.Button('Copy'    , tooltip='Copy Factor Parameters to Clipboard', key='_copy_'    ),
                  sg.Button('Generate', tooltip='Generate Sensitivity Cases'         , key='_generate_'),
                  sg.Button('Load'    , tooltip='Load Factor Parameters from File'   , key='_load_'    ),
                  sg.Button('Save'    , tooltip='Save Factor Parameters to File'     , key='_save_'    ),
                  sg.Button('Help'    , key='_help_'),
                  sg.Exit()]]

    window1 = sg.Window('OPMSENS Deck Sensitivity Generation', no_titlebar=False, grab_anywhere=False,
                        layout=mainwind, disable_close=False, finalize=True)
    #
    #   Set Output Multiline Window for CPRINT
    #
    sg.cprint_set_output_destination(window1, outlog)

    # ------------------------------------------------------------------------------------------------------------------
    #   Define GUI Event Loop, Read Buttons, and Make Callbacks etc. Section
    # ------------------------------------------------------------------------------------------------------------------
    while True:
        #
        # Read the Window and Process
        #
        event, values = window1.read()
        window_debug(event, 'values', values, False)
        #
        # Base (Input Deck Template)
        #
        if event == '_base_':
            basefile = sensitivity_base_file(jobparam, opmsys, window1)
            continue
        #
        # Clean
        #
        elif event == '_clean_':
            if not Path(basefile).is_file():
                sg.popup_ok('No BASE file selected, please select a BASE file first, before selecting this option.',
                            no_titlebar = True, grab_anywhere = True, keep_on_top = True)
                continue

            text = sg.popup_yes_no('Do You Wish to Clean, that is remove all sensitivity cases derived from the ' +
                               'current BASE file? \n' 'Note that files are automatically removed when generating ' +
                               'a new set of sensitivity cases.',
                               no_titlebar=False, grab_anywhere=False, keep_on_top=True)
            if text == 'Yes':
                sensitivity_clean(basefile)
                sg.popup_ok('All files from BASE all sensitivity cases have been deleted, see messages.',
                        no_titlebar=False, grab_anywhere=False, keep_on_top=True)
                continue

            continue
        #
        # Clear
        #
        elif event == '_clear_':
            window1['_tab_factors_'].select()
            text = sg.popup_yes_no('Do You Wish to Clear All the Factor Properties?',
                                 no_titlebar=False, grab_anywhere=False, keep_on_top=True)
            if text == 'Yes':
                factors =  sensitivity_set_factors(header, nrow)
                window1['_factors_'].update(factors)
                window1['_tab_factors_'].select()

            continue
        #
        # Copy
        #
        elif event == '_copy_':
            window1['_tab_factors_'].select()
            dt = window1['_factors_'].get()
            df = pd.DataFrame(dt, columns=header)
            try:
                df.to_clipboard(sep=',', index=False)
            except Exception:
                sg.popup_error('OPMSENS Factors Copied to Clipboard Error.\n \n' +
                              'Currently, this error only appears on Linux systems. \n'
                              'It can be fixed by installing one of the copy/paste mechanisms via:\n \n' +
                              'sudo apt-get install xclip python3-pyqt4 \n',
                              no_titlebar=False, grab_anywhere=False, keep_on_top=True)
                continue

            sg.popup_timed('OPMSENS Factors Copied to Clipboard', no_titlebar=False, grab_anywhere=False, keep_on_top=True)
            continue
        #
        # Exit
        #
        elif event == 'Exit':
            text = sg.popup_yes_no('Exit OPMSENS Sensitivity Generation?',
                                    no_titlebar=False, grab_anywhere=False, keep_on_top=True)
            if text == 'Yes':
                break
            else:
                continue
        elif event == sg.WIN_CLOSED:
            break
        #
        # Factors (Edit)
        #
        elif event == '_factors_':
            try:
                edit_row = values['_factors_'][0]
            except IndexError as e:
                sg.popup_error('OPMSENS Bug in OPMSENS_MAIN: Failed to Get Factor Table Row\n ',
                               'Event Value is: ' + str(event) ,
                               'Row Value is: ' + str(edit_row) + '\n' ,
                               'Program Will Continue \n',
                                no_titlebar=False, grab_anywhere=False, keep_on_top=True)
                continue

            factors = sensitivity_edit_factor(header, edit_row, factors)
            window1['_factors_'].update(factors)
            # Need to Read Window Again to Clear Events and Values
            window1.read()
            continue
        #
        # Generate
        #
        elif event == '_generate_':
            window1[outlog].update('')
            basefile = window1['_basefile_'].get()
            factors  = window1['_factors_'].get()
            scenario = values['_scenarios_'][0]
            sensitivity_write_cases(basefile, header, factors, scenario)
            continue
        #
        # Help
        #
        elif event == '_help_':
            opm_popup('OPMRUN Sensitivity Case Generator Utility', helptext, 25)
            continue
        #
        # Load
        #
        elif event == '_load_':
            file = sg.popup_get_file('Load OPMSENS Sensitivity Factor File', default_path=str(os.getcwd()),
                                   initial_folder=str(os.getcwd()), save_as=False,
                                   file_types=[('OPMSENS Factors', '*.fac'), ('All', '*.*')], size=(110,1),
                                   no_titlebar=False, grab_anywhere=False, keep_on_top=True)
            if file is not None:
                if Path(file).is_file():
                    df      = pd.read_csv(file, keep_default_na=False)
                    factors = df.values.tolist()
                    window1['_tab_factors_'].select()
                    window1['_factors_'].update(values=factors)
                else:
                    sg.popup_error('File Does Not Exist: \n\n' + str(file) + '\n',
                                  no_titlebar=False, grab_anywhere=False, keep_on_top=True)

            continue
        #
        # Save
        #
        elif event == '_save_':
            window1['_tab_factors_'].select()
            file = sg.popup_get_file('Save OMPSENS Sensitivity Factor File', default_path=str(os.getcwd()),
                                   initial_folder=str(os.getcwd()), save_as=True,
                                   file_types=[('OPMSENS Factors', '*.fac'), ('All', '*.*')],
                                   no_titlebar=False, grab_anywhere=False, keep_on_top=True)
            dt = window1['_factors_'].get()
            df = pd.DataFrame(dt, columns=header)
            df.to_csv(file, sep=',', index=False)
            sg.popup_timed('OPMSENS Factors Saved to File',
                          no_titlebar=False, grab_anywhere=False, keep_on_top=True)
            continue
    #
    # Define Post Processing Section
    #
    ans = sg.popup_yes_no('Do You Wish to Save the OPMSENS Sensitivity Factors to File?',
                        no_titlebar=False, grab_anywhere=False, keep_on_top=True)
    if ans == 'Yes':
        file = sg.popup_get_file('Save OMPSENS Sensitivity Factor File', default_path=str(os.getcwd()),
                               initial_folder=str(os.getcwd()), save_as=True,
                               file_types=[('OPMSENS Factors', '*.fac'), ('All', '*.*')],
                               no_titlebar=False, grab_anywhere=False, keep_on_top=True)
        dt = window1['_factors_'].get()
        df = pd.DataFrame(dt, columns=header)
        df.to_csv(file, sep=',', index=False)
        sg.popup_timed('OPMSENS Factors Saved to File',
                      no_titlebar=False, grab_anywhere=False, keep_on_top=True)

    window1.Close()
    sg.popup_ok('OPMSENS Sensitivity Generation Processing Complete',
               no_titlebar=False, grab_anywhere=False, keep_on_top=True)


# ======================================================================================================================
# End of OPMSENS
# ======================================================================================================================