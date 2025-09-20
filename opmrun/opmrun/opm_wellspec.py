# =======================================================================================================================
#
"""OPM_WELLSPEC.py - Generate WELSPECS, COMPDAT and COMPLUMP Keywords from OPM ResInsight Export File

The WELSPEC option re-formats the WELSPECS and COMPDAT keywords exported from OPM ResInsight to be more readable. At the
same time, it writes out the OPM ResInsight Completion Data File, so that the data can be loaded back into to OPM
ResInsight. This is done so that in OPM ResInsight one can declare one perforation for the whole well and run the export
through this routine to get completions based on on reservoir unit. The module can optionally read an OPM ResInsight
Formation Name Layer File and stores the date for determining the completion number in the COMPLUMP keyword. In this
case COMPLUMP keyword is also generated.

Program Documentation
--------------------
Only Python 3 is supported and tested Python2 support has been depreciated.

2025.09.19 - Switch from PySimpleGUI to FreeSimpleGUI package
2021.07.01 - New module initial release.

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
Version : 2021.07.01
Date    : 20-Jul-2021
"""
# -----------------------------------------------------------------------------------------------------------------------
# 3456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890
#        1         2         3         4         5         6         7         8         9         0         1         2
#        0         0         0         0         0         0         0         0         0         1         1         1
# -----------------------------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------------------
# Import Modules and Start Up Section
# -----------------------------------------------------------------------------------------------------------------------
from pathlib import Path
import pandas as pd
#
# Import Required Non-Standard Modules
#
import FreeSimpleGUI as sg
#
# Import OPM Common Modules
#
from opmrun.opm_common import file_lstrip, opm_header_file, opm_popup, opm_view, window_debug

# ----------------------------------------------------------------------------------------------------------------------
# Define Modules Section
# ----------------------------------------------------------------------------------------------------------------------
def wellspec_check_file(file, file_in, extension, window):
    """ Checks the Status of a File.

    This function checks the status of a file and returns the filename and a error code.

    Parameters
    ----------
    file : str
       Name of output file to be checked.
    file_in : str
       Name of input file, used to optionally derive the output file.
    extension : str
        file extension.
    window : window object
        Window for display output.

    Returns
    -------
    file_out : str
       Name of the resulting output file.
    error : boolean
        Set to True for errors otherwise False.
    """

    error = False
    if Path(file).is_file():
        file_out = file
        text = sg.popup_yes_no('Output File Exists: ', str(file_out), 'Overwrite the File?',
                               no_titlebar=False, grab_anywhere=False, keep_on_top=True)
        if text == 'No':
            error = True
    else:
        file_out = Path(file_in).with_suffix(extension)
        window.update(file_out)
    return(file_out, error)


def wellspec_complump(file_inc, comp_name, comp_data, depth):
    """ Writes Out the OPM Flow COMPLUMP keyword to a File

    This function writes an OPM Flow well COMPLUMP keyword based on an OPM ResInsight simulation perforation export
    file.

    Parameters
    ----------
    file_in : str
       Name of output file used for documenting the creation of the keywords.
    comp_name : df
        Dataframe containing completion layers and layer names.
    comp_data : df
      Dataframe containing the data required for the OPM ResInsight Perforation file.
    depth : str
        Depth units for report headers.

    Returns
    -------
    comp_zone : df
      Dataframe containing the zone data required for the OPM ResInsight Perforation comment.
    error : boolean
        Set to True for errors otherwise False.
    """

    debug = False
    error = False
    #
    # Check if Completion Zones Have been Loaded
    #
    if comp_name.empty:
        sg.popup_error('Cannot Find Formation Names to Generate COMPLUMP Keyword.',
                       'Please Load Formation Names If You Wish to Use this Option.',
                       'Writing of Keywords Completed.',
                       no_titlebar=False, grab_anywhere=False, keep_on_top=True)
        return(None, True)
    #
    # Lookup Completion Zones
    #
    for n in range(0, comp_data.shape[0]):
        k = int(comp_data.at[n, 'k1'])
        if n == 0:
            comp_zone = comp_name.query('@k >= k1 and @k <= k2')
        else:
            comp_zone = comp_zone.append(comp_name.query('@k >= k1 and @k <= k2'))

    comp_zone.columns = ['zone', 'ztop', 'zbot', 'zcomp']
    comp_zone = comp_zone.reset_index()
    comp_zone.pop('index')
    #
    # Create COMPLUMP Data DataFrame for Processing
    #
    comp_lump = pd.DataFrame(columns=['wname', 'i1', 'j1', 'k1', 'k2', 'comp', 'end', 'zone', 'mdin', 'mdout', 'mdlen'])
    comp_lump['wname'] = comp_data['wname']
    comp_lump['i1'] = comp_data['i1'].astype(int)
    comp_lump['j1'] = comp_data['j1'].astype(int)
    comp_lump['k1'] = comp_data['k1'].astype(int)
    comp_lump['k2'] = comp_data['k2'].astype(int)
    comp_lump['comp'] = comp_zone['zcomp']
    comp_lump['end'] = comp_data['end']
    comp_lump['zone'] = comp_zone['zone']
    comp_lump['mdin'] = comp_data['mdin'].astype(float)
    comp_lump['mdout'] = comp_data['mdout'].astype(float)
    comp_lump['mdlen'] = comp_lump['mdout'] - comp_lump['mdin']
    # Sum by Well
    comp_lump['mdwel'] = comp_lump.groupby(['wname'])['mdlen'].cumsum()
    # Sum by Well and Zone Zone
    comp_lump['mdzon'] = comp_lump.groupby(['wname', 'zone'])['mdlen'].cumsum()

    comp_lump = comp_lump.reset_index()
    comp_lump = pd.concat((comp_lump, comp_zone['ztop'], comp_zone['zbot'], comp_zone['zcomp']), axis=1, sort=False)
    comp_lump.pop('index')

    if debug:
        sg.Print('COMP_ZONE')
        sg.Print(comp_zone.to_string(index=False))
        sg.Print('COMP_LUMP')
        sg.Print(comp_lump.to_string(index=False))
    #
    # Write Data to File
    #
    sg.cprint('\nCOMP_LUMP')
    sg.cprint(comp_lump.head().to_string())
    with open(file_inc, 'a') as file:
        wellspec_keyword(file, 'COMPLUMP', depth, comp_lump)
    # Read and Write Remove Blanks in First Column (work around for df.to_string() issue)
    file_lstrip(file_inc)
    sg.cprint('Process Complete for COMPLUMP Keyword')
    return (comp_zone, error)


def wellspec_formation_names(file):
    """Reads an OPM ResInsight Formation Name Layer File (*.lyr)

    OPM_UTILITIES is a Graphical User Interface ("GUI") program for the Open Porous Media ("OPM") Flow simulator. This
    function reads an OPM ResInsight Formation Name Layer File and stores the date for determining the completion number
    in the COMPLUMP keyword.

    Parameters
    ----------
    file : str
       File name to read the OPM ResInsight data from

    Returns
    -------
    zone_name : df
       Contains the formation layer names and the associated k layer numbers, and a sequential completion number.
    error : boolean
        Set to True for errors otherwise False.

    """
    #
    # Initialize
    #
    debug = False
    error = False
    zone_name = pd.DataFrame(columns=['zname', 'k1', 'k2', 'comp_no'])
    try:
        file = open(file, 'r')
        data = file.read().splitlines()
        file.close()
    except FileNotFoundError as error:
        sg.popup_error('Error Reading: ' + '\n  \n' + str(file) + '\n \n' +
                       str(error) + ': ' + str(type(error)), no_titlebar=False, grab_anywhere=False, keep_on_top=True)
        error = True
        return (zone_name, error)

    n = 0
    for line in data:
        sg.cprint(str(line[:120]))
        try:
            if '--' not in line:
                n = n + 1

                line = "',".join(line.rsplit("' " , 1))  # Reverse replace
                line = ", ".join(line.rsplit(" - ", 1))  # Reverse replace
                line = (line.strip() + ', ' + str(n))
                zone_name.loc[n] = line.split(',')

        except ValueError as error:
            sg.popup_error('Error Reading: ' + '\n  \n' + str(file) + '\n \n' +
                           'Line ' + str(line) + '\n \n' + str(error) + ': ' + str(type(error)), no_titlebar=False,
                           grab_anywhere=False, keep_on_top=True)
            error = True
            return (zone_name, error)

    zone_name['k1'] = zone_name['k1'].astype(int)
    zone_name['k2'] = zone_name['k2'].astype(int)
    zone_name['comp_no'] = zone_name['comp_no'].astype(int)
    if debug:
        sg.Print(zone_name.columns.ravel())
        sg.Print(zone_name)

    return (zone_name, error)


def wellspec_keyword(file, keyword, unit='', data=None):
    """Write Keyword Header, Keyword and Data to File

    Writes out keyword header and data to a file.

    Parameters
    ----------
    file : file
        File object that was used to writing data to.
    keyword : keyword
        The name of the keyword header to be written out together with the keyword.
    unit : str
        Unit string
    data : df
        Data frame to be written out

    Returns
    -------
    None
    """

    if keyword == 'COMPDATA':
        file.write('--                        \n')
        file.write('--  WELL CONNECTION DATA  \n')
        file.write('--                        \n')
        out = pd.DataFrame([['-- WELL ', 'LOC.', 'LOC.', 'LOC.', 'LOC.', 'OPEN', 'SAT', 'CONN', 'WELL', 'KH  ', 'SKIN',
                             'D   ', 'DIR', ' ', 'MD-IN', 'MD-OUT', 'CONN  '],
                            ['-- NAME ', 'II  ', 'JJ  ', 'K1  ', 'K2  ', 'SHUT', 'TAB', 'FACT', 'DIA ', 'FACT', 'FACT',
                             'FACT', 'PEN',  ' ', unit,    unit,     'FACTOR'],
                            ['COMPDAT', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ',' ']],
                           columns=data.columns)
    elif keyword == 'COMPLUMP':
        file.write('--                                         \n')
        file.write('--  ASSIGN WELL CONNECTIONS TO COMPLETIONS \n')
        file.write('--                                         \n')
        out = pd.DataFrame([['-- WELL ', 'LOC.', 'LOC.', 'LOC.', 'LOC.', 'COMPL', ' ', 'ZONE', 'MD-IN', 'MD-OUT',
                             'MD-LEN'  , 'MD-WEL', 'MD-ZON', 'TOP', 'BOT', 'COMPL'],
                            ['-- NAME ',  'II  ', 'JJ  ', 'K1  ', 'K2  ', 'NO.  ', ' ', 'NAME',  unit  ,  unit   ,
                             unit     ,  unit   ,  unit   , 'K  ', 'K  ', 'NO.  '],
                            ['COMPLUMP',  ' '  , ' '   , ' '   , ' '   , ' '    , ' ', ' '   , ' '    , ' '     ,
                             ' '       , ' '     , ' '     , ' '  , ' '  , ' ' ]], columns=data.columns)
    elif keyword == 'WELSPECS':
        file.write('--                         \n')
        file.write('-- WELL SPECIFICATION DATA \n')
        file.write('--                         \n')
        out = pd.DataFrame([['-- WELL ', 'GROUP', 'LOC.', 'LOC.', 'BHP  ', 'PHASE', 'DRAIN', 'INFLOW', 'OPEN', 'CROSS',
                             'PVT  ', 'HYDS', 'FIP ', ' '],
                            ['-- NAME ', 'NAME',   'I  ', 'J   ', 'DEPTH', 'FLUID', 'AREA ', 'EQUANS', 'SHUT', 'FLOW ',
                             'TABLE', 'DENS', 'REGN', ' '],
                             ['WELSPECS ','    ', ' ',    ' ',    '     ', '     ', '     ', '      ', '    ', '     ',
                              '    ', '    ', '    ', ' ']], columns=data.columns)
    else:
        sg.popup_error('Error Keyword Not Found: ' + '\n  \n' + keyword, no_titlebar=False, grab_anywhere=False,
                       keep_on_top=True)
    try:
        out = out.append(data)
        out = out.to_string(index=False, header=False, justify='start')
        file.write(out)
        file.write('\n/\n\n')
    except Exception as error:
        sg.popup_error('Error Processing ' + keyword + '\n \n' +
                       str(error) + ': ' + str(type(error)), no_titlebar=False, grab_anywhere=False, keep_on_top=True)
    return ()


def wellspec_perforations(file_ev, file_in, comp_name, comp_data, comp_zone, depth, opmsys):
    """Writes an OPM ResInsight Well Perforation file (*.ev)

    This function writes an OPM ResInsight Well Perforation file (*.ev) based on the generated completion data.

    Parameters
    ----------
    file_ev : str
       Name of file to write the OPM ResInsight perforation data.
    file_in : str
       Name of input file used to capture the comp_data.
    comp_name : df
        Dataframe containing completion layers and layer names.
    comp_data : df
      Dataframe containing the data required for the OPM ResInsight Perforation file.
    comp_zone : df
      Dataframe containing the zone data required for the OPM ResInsight Perforation comment.
    depth : str
        Depth units for report headers.
    opmsys : dict
        A dictionary containing the OPMRUN system parameters

    Returns
    -------
    None
    """

    debug = False
    #
    # Check if Completion Zones Have been Loaded
    #
    if comp_name.empty:
        sg.popup_error('Cannot Find Formation Names to Generate PERFORATIONS.',
                       'Please Load Formation Names If You Wish to Use this Option.',
                       'Writing of Keywords Completed.',
                       no_titlebar=False, grab_anywhere=False, keep_on_top=True)
        return()
    #
    # Create PERFORATIONS Data DataFrame for Processing
    #
    perf_zone = pd.DataFrame(columns=['wname', 'soh', 'perf', 'top', 'bot', 'weldia', 'skin', 'end', 'zone'])
    perf_zone['wname'] = comp_data['wname']
    perf_zone['top'] = comp_data['mdin']
    perf_zone['bot'] = comp_data['mdout']
    perf_zone['soh'] = '"SOH"   '
    perf_zone['perf'] = 'perforation'
    perf_zone['weldia'] = comp_data['weldia']
    perf_zone['skin'] = comp_data['skin']
    perf_zone['end'] = '--'
    perf_zone['zone'] = comp_zone['zone']
    #
    # Write OPM ResInsight PERFORATIONS File
    #
    text = ['OPM ResInsight Input Perforation file for Loading into OPM ResInsight via ' +
            'OPM_UTILITIES(WELSPEC) option', ' ',
            'Units            : Field',
            'Wellbore Diameter: As per OPM ResInsight Completion File',
            'Skin Factor      : As per OPM ResInsight Completion File'
            + ' ']
    wells = perf_zone['wname'].unique()

    if debug:
        sg.Print(perf_zone.columns.ravel())
        sg.Print(perf_zone)

    sg.cprint('\nOPM ResInsight Perforation file for the following wells')
    sg.cprint(str(wells))
    try:
        with open(file_ev, 'w') as file:
            opm_header_file(file, file_in, file_ev, ['start', 'UNITS FIELD'], text, opmsys)
            for well in wells:
                perf_data = perf_zone[perf_zone['wname'].str.contains(well)]
                perf_data.pop('wname')
                out = pd.DataFrame([['--      ', '           ', '   ' , '   ' , '    ', '    ', '  ', '    '],
                                    ['-- DATE ', 'PERFORATION', 'TOP' , 'BOT' , 'WELL', 'SKIN', '  ', 'ZONE'],
                                    ['--      ', '           ',  depth,  depth, 'DIAM', 'FACT', '  ', '    '],
                                    ['WELLNAME',  well        , '    ', '    ', '    ', '    ', '  ', '    ']],
                                    columns=perf_data.columns)
                out = out.append(perf_data)
                out = out.to_string(index=False, header=False, justify='start')
                file.write('\n')
                file.write(out)
            opm_header_file(file, file_in, file_ev, ['end', ''], text, opmsys)
    except Exception as error:
        sg.popup_error('Error Processing PERFORATIONS to: ' + '\n  \n' + str(file_ev) + '\n \n' +
                       str(error) + ': ' + str(type(error)),
                       no_titlebar=False, grab_anywhere=False, keep_on_top=True)
    # Read and Write Remove Blanks in First Column (work around for df.to_string() issue)
    file_lstrip(file_ev)

    sg.cprint('OPM ResInsight Perforations Process Complete')
    sg.popup_ok('OPM ResInsight Perforations Process Complete Data Written to: ' + '\n  \n' + str(file_ev),
                no_titlebar=False, grab_anywhere=False, keep_on_top=True)


def wellspec_welscomp(file_in, file_inc, depth, opmsys):
    """Writes the OPM Flow WELSPECS and COMPDAT Keywords to a file

    This function writes an OPM Flow well specification data set using the WELSPECS and COMPDAT keyword based on an
    OPM ResInsight simulation perforation export file.

    Parameters
    ----------
    file_in : str
       Name of input file used to capture the comp_data.
    file_inc : str
       Name of output include file used to write the keywords to.
    depth : str
        Depth units for report headers.
    opmsys : dict
        A dictionary containing the OPMRUN system parameters

    Returns
    -------
    comp_data : df
      Contains the COMPDAT keyword data
    wels_data : df
      Contains the WELSPECS keyword data
    error : boolean
        Set to True for errors otherwise False.
    """
    #
    # Initialize Variables and Constants
    #
    debug = False
    error = False
    comp_data = pd.DataFrame(columns=['wname', 'i1', 'j1', 'k1', 'k2', 'status', 'satab', 'confact', 'weldia',
                                      'kh', 'skin', 'd_fact', 'pen', 'end', 'mdin', 'mdout', 'trans'])
    comp_zone = pd.DataFrame()
    wels_data = pd.DataFrame(columns=['wname', 'i1', 'j1', 'k1', 'depth', 'phase', 'area', 'inflow', 'status',
                                      'xflow', 'pvtab', 'hydr', 'fiip', 'end'])
    #
    # Read Input File and Get Indices for Keywords
    #
    try:
        file = open(file_in, 'r')
        data = file.read().splitlines()
        file.close()
    except FileNotFoundError as error:
        sg.popup_error('Error Reading: ' + '\n  \n' + str(file_in) + '\n \n' +
                       str(error) + ': ' + str(type(error)), no_titlebar=False, grab_anywhere=False, keep_on_top=True)
        error = True
        return (wels_data, comp_data, error)

    n = 0
    comp_start = 0
    comp_end = 0
    wels_start = 0
    wels_end = 0
    for line in data:
        n = n + 1
        if 'WELSPECS' in line:
            wels_start = n + 1
            continue

        if 'COMPDAT' in line:
            comp_start = n + 1
            wels_end = n - 4
            break
    #
    # Load WELSPECS Data Into DataFrame for Processing
    #
    comp_end = len(data) - 1
    sg.cprint('WELSPECS Start: ' + str(wels_start))
    sg.cprint('WELSPECS End  : ' + str(wels_end))
    n = -1
    try:
        for line in data[wels_start:wels_end]:
            n = n + 1
            sg.cprint(str(line))
            line = line.split()
            wels_data.loc[n] = line
    except ValueError as error:
        sg.popup_error('Error Processing WELSPECS: ' + '\n  \n' + str(line) + '\n \n' +
                       str(error) + ': ' + str(type(error)),
                       no_titlebar=False, grab_anywhere=False, keep_on_top=True)
        error = True
        return (wels_data, comp_data, error)

    wels_data.sort_values(by=['wname'], inplace=True)
    #
    # Load COMPDAT Data Into DataFrame for Processing
    #
    sg.cprint('COMPDAT Start : ' + str(comp_start))
    sg.cprint('COMPDAT End   : ' + str(comp_end))
    n = 0
    try:
        for line in data[comp_start:comp_end]:
            if '-- Perforation Completion' in line:
                line0 = line.split()
            else:
                n = n + 1
                sg.cprint(str(line))
                line = (line + ' ' + line0[6] + ' ' + line0[10] + ' ' + line0[12]).split()
                comp_data.loc[n] = line

    except Exception as error:
        sg.popup_error('Error Processing COMPDAT: ' + '\n  \n' + str(file_in) + '\n \n' +
                       str(error) + ': ' + str(type(error)),
                       no_titlebar=False, grab_anywhere=False, keep_on_top=True)
        error = True
        return (wels_data, comp_data, error)

    comp_data = comp_data.reset_index()
    comp_data['mdin'] = comp_data['mdin'].astype(float)
    comp_data['mdout'] = comp_data['mdout'].astype(float)
    comp_data['trans'] = comp_data['trans'].astype(float)
    comp_data.pop('index')
    if debug:
        sg.Print(comp_data.columns.ravel())
        sg.Print(comp_data)

    sg.cprint('WELS_DATA')
    sg.cprint(wels_data.head().to_string())
    sg.cprint('COMP_DATA')
    sg.cprint(comp_data.head().to_string())
    #
    # Write Out WELSPECS and COMPDAT Keywords
    #
    text = ['OPM Flow Well Specification keywords via OPMRUN(WELSPEC) option', ' ',
            'Data Generated using an OPM ResInsight export file for completions combined with an OPM ',
            'ResInsight Formation Layer file to generate perforation COMPLUMP units']
    with open(file_inc, 'w') as file:
        opm_header_file(file, file_in, file_inc, ['start', 'NOECHO'], text, opmsys)
        wellspec_keyword(file, 'WELSPECS', depth, wels_data)
        wellspec_keyword(file, 'COMPDATA', depth, comp_data)
    # Read and Write Remove Blanks in First Column (work around for df.to_string() issue)
    file_lstrip(file_inc)
    sg.cprint('Process Complete for WELSPECS and COMPDAT Keywords')
    return (wels_data, comp_data, error)


def wellspec_main(opmoptn, opmsys):
    """ Main Function to Generate the OPM Flow WELSPECS and COMPDAT Keywords from OPM ResInsight Export

    OPM_UTILITIES is a Graphical User Interface ("GUI") program for the Open Porous Media ("OPM") Flow simulator. The
    WELSPEC option reformats the WELSPECS and COMPDAT keywords exported from OPM ResInsight to be more readable. At
    the same time, it writes out the OPM ResInsight Completion Data File, so that the data can be loaded back into to
    OPM ResInsight. This is done so that in OPM ResInsight one can declare one perforation for the whole well and run
    the export through this routine to get completions based on on reservoir unit.

    In addition, the routine calls OPM ResInsight to get an array that indicates the completion number for a
    connection and then writes out the COMPLUMP keyword for all the connections.

    Parameters
    ----------
    opmoptn : dict
        A dictionary containing the OPMRUN default parameters
    opmsys : dict
        A dictionary containing the OPMRUN system parameters

    Returns
    -------
    None
    """
    # ------------------------------------------------------------------------------------------------------------------
    # Initialize Variables
    # ------------------------------------------------------------------------------------------------------------------
    debug    = False
    file_in  = ''
    file_lyr = ''
    file_ev  = ''
    file_inc = ''
    comp_name = pd.DataFrame()
    comp_zone = pd.DataFrame()
    unit_depth = {'field': 'MDFT', 'metric': 'MDMS'}
    #
    # Define General Text Variables
    #
    helpintr = ('The Well Specification option uses the OPM ResInsight exported completions (with comments) to ' +
                'reformat the data and to generate the COMPLUMP keyword base on the OPM Resinsight import ' +
                'formation layers file (*.Lyr).')
    helptext = (
            'OPMRUN is a Graphical User Interface ("GUI") program for the Open Porous Media ("OPM") Flow ' +
            'simulator. \n' +
            ' \n' +
            'The WELSPEC option reformats the WELSPECS and COMPDAT keywords exported from OPM ResInsight to a more ' +
            'readable format. At the same time, it writes out the OPM ResInsight Completion Data File, so that the ' +
            'data can be loaded back into to OPM ResInsight. This is done so that in OPM ResInsight one can declare ' +
            'one perforation for the whole well and run the export through this routine to get completions based on ' +
            'reservoir units. \n' +
            '\n ' +
            'In addition, the routine reads an OPM ResInsight Formation Layer file to get the completion number for '
            'a connection and then writes out the COMPLUMP keyword for all the connections. ' +
            '\n\n' +
            'Note: \n' +
            '----- \n' +
            'For wells that do not have defined perforrations, first genrate the perforations by defining the ' +
            'one perforation interval from the top to the base of the well in OPM ResInsight and export the data. ' +
            'The program will then generate a complete set of perforations, and one can use the WELOPEN keyword in ' +
            'simulation input deck to open various COMPLUMP units \n' +
            '\n' +
            'The program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without ' +
            'even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the ' +
            'GNU General Public Licenses for more details. \n' +
            '\n' +
            'Copyright (C) 2020-2021 Equinox International Petroleum Consultants Pte Ltd. \n'
            '\n' +
            'Author  : David Baxendale (david.baxendale@eipc.co)')

    # ------------------------------------------------------------------------------------------------------------------
    # Initialize GUI Setup and Define Main Window
    # ------------------------------------------------------------------------------------------------------------------
    outlog  = '_outlog1_' + sg.WRITE_ONLY_KEY
    layout1 = [[sg.Text('OPM_WELSPEC Option to Generate the OPM Flow WELSPECS and COMPDAT Keywords from ' +
                        'OPM ResInsight Export')],
               [sg.Text('OPM ResInsight Exported Well Specification File')],
               [sg.Input(file_in, key='_input_', size=(125, None)),
                sg.FilesBrowse(target='_input_', initial_folder=Path(file_in).absolute(),
                               file_types=(('OPM ResInsight', '*.exp *.EXP'), ('All', '*.*')))],
               [sg.Text('OPM ResInSight Perforation Output File (Leave Blank for Default)')],
               [sg.InputText(file_ev, key='_output1_', size=(125, None)),
                sg.FilesBrowse(target='_output1_', initial_folder=Path(file_in).absolute(),
                               file_types=(('OPM ResInsight Perforation File', '*.ev *.EV'), ('All', '*.*')))],
               [sg.Text('OPM Flow Well Specification Output Include File (Leave Blank for Default)')],
               [sg.InputText(file_inc, key='_output2_', size=(125, None)),
                sg.FilesBrowse(target='_output2_', initial_folder=Path(file_in).absolute(),
                               file_types=(('Simulator Include File', '*.inc *.INC'), ('All', '*.*')))],
               [sg.Text('Output')],
               [sg.Multiline(key=outlog, size=(125, 20), text_color='blue', autoscroll=True,
                             font=(opmoptn['output-font'], opmoptn['output-font-size']))],
               [sg.Text('')],
               [sg.Checkbox('Generate COMPLUMP Keyword Based on OPM ResInsight Array', key='_complump1_',
                            default=False, disabled=True, visible=True, size=(70, None)),
                sg.Radio('Output Header Units (ft)', "bRadio1", key='_field_', default=True)],
               [sg.Checkbox('Generate COMPLUMP Keyword Based on OPM ResInsight Formation Names File', key='_complump2_',
                            default=True, size=(70, None)),
                sg.Radio('Output Header Units (ms)', "bRadio1", key='_metric_', default=False)],
               [sg.Checkbox('Generate OPM ResInsight Perforation File', size=(70, None), key='_perforations_',
                            default=True)],
               [sg.Text('')],
               [sg.Button('Load Formation Names', key='_loadnames_'), sg.Button('Generate Keywords', key='_submit_'),
                sg.Button('Clear', key='_clear_'), sg.Button('Help', key='_help_'),
                sg.Button('View', disabled=True, tooltip='View Results', key='_view_'), sg.Exit()]]
    window1 = sg.Window('OPM Flow Well Specification Generation (WELSPECS, COMPDAT, and COMPLUMP)', layout=layout1,
                        finalize=True, no_titlebar=False, grab_anywhere=False)
    #
    #   Set Output Multiline Window for CPRINT
    #
    sg.cprint_set_output_destination(window1, outlog)
    sg.cprint(helpintr)

    # ------------------------------------------------------------------------------------------------------------------
    # Define GUI Event Loop, Read Buttons, and Make Callbacks etc. Section
    # ------------------------------------------------------------------------------------------------------------------
    while True:
        #
        # Read the Form and Process and Take appropriate action based on event
        #
        event, values = window1.read()
        window_debug(event, 'values', values, False)
        #
        # Clear
        #
        if event == '_clear_':
            window1[outlog].update('')
        #
        # Exit
        #
        elif event == 'Exit':
            text = sg.popup_yes_no('Exit OPM Well Specification Utility?', no_titlebar=False,
                                   grab_anywhere=False, keep_on_top=False)
            if text == 'Yes':
                break
            else:
                continue
        elif event == sg.WIN_CLOSED:
            break
        #
        # Help
        #
        elif event == '_help_':
            opm_popup('Help', helptext, 35)
            continue
        #
        # Load OPM ResInsight Formation Names
        #
        elif event == '_loadnames_':
            file_lyr = sg.popup_get_file('Selected OPM ResInsight Layer File', 'OPM ResInsight Layer File',
                                         size=(125, None),
                                         file_types=(('OPM ResInsight Layer File', '*.Lyr *.LYR'), ('All', '*.*')))
            if file_lyr is None:
                sg.popup_ok('OPM ResInsight Layer File Cancelled', no_titlebar=False, grab_anywhere=False,
                               keep_on_top=False)
                continue
            elif not Path(file_lyr).is_file():
                sg.popup_error('OPM ResInsight Layer File Not Found', 'File: ', str(file_lyr),
                               no_titlebar=False, grab_anywhere=False, keep_on_top=True)
                continue
            else:
                comp_name, error = wellspec_formation_names(file_lyr)
            continue
        #
        # Submit
        #
        elif event == '_submit_':
            # OPM ResInsight Input Well Specification Input File
            file_in = values['_input_']
            if not Path(file_in).is_file():
                sg.popup_error('OPM ResInsight Well Specification File Not Found', 'File: ', str(file_in),
                               no_titlebar=False, grab_anywhere=False, keep_on_top=True)
                continue

            # OPM ResInsight Output Perforation File
            file_ev, error = wellspec_check_file(values['_output1_'], file_in, '.ev', window1['_output1_'])
            if error:
                continue

            # OPM Flow Output Well Specification Include File
            file_inc, error = wellspec_check_file(values['_output2_'], file_in, '.inc', window1['_output2_'])
            if error:
                continue

            # Get Unit Options
            if values['_field_']:
                depth = unit_depth['field']
            else:
                depth = unit_depth['metric']

            # Read Input File and Process WELSPECS and COMPDAT Keywords Exported from OPM ResInsight
            wels_data, comp_data, error = wellspec_welscomp(file_in, file_inc, depth,opmsys)
            if error:
                continue
            else:
                window1['_view_'].update(disabled=False)

            # Create and Write COMPLUMP if Required.
            if values['_complump1_'] or values['_complump2_']:
                comp_zone, error = wellspec_complump(file_inc, comp_name, comp_data, depth)

            # Write End of File Headers
            try:
                with open(file_inc, 'a') as file:
                    opm_header_file(file, file_in, file_inc, ['end', 'ECHO'], [' '], opmsys)
            except Exception as error:
                sg.popup_error('Error Writing: ' + '\n  \n' + str(file_inc) + '\n \n' +
                               str(error) + ': ' + str(type(error)),
                               no_titlebar=False, grab_anywhere=False, keep_on_top=True)
            sg.popup_ok('Well Specification Process Complete Data Written to: ' + '\n  \n' + str(file_inc),
                        no_titlebar=False, grab_anywhere=False, keep_on_top=True)

            # Write OPM ResInsight PERFORATIONS File if Required
            if values['_perforations_']:
                 wellspec_perforations(file_ev, file_in, comp_name, comp_data, comp_zone, depth, opmsys)

            continue
        #
        # View
        #
        elif event == '_view_':
            opm_view(str(file_inc), opmoptn)
            continue

    # ------------------------------------------------------------------------------------------------------------------
    # Post Processing Section - Close Main Window
    # ------------------------------------------------------------------------------------------------------------------
    window1.close()
    return ()

# ======================================================================================================================
# End of OPM_WELLSPEC.py
# ======================================================================================================================
