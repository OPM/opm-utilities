# =======================================================================================================================
#
"""OPM_WELLTRAJ.py - Convert Well Trajectories to OPM ResInsight Format

The module reads in reads an Petrel trajectory file containing a well's deviation data and writes out the data in the
OPM ResInsight format. The module also allows for conversion of both areal and depth units.

Program Documentation
--------------------
Only Python 3 is supported and tested Python2 support has been depreciated.

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
          david.baxendale@eipc.co
Version : 2021.07.01
Date    : 19-Jul-2021
"""
# ----------------------------------------------------------------------------------------------------------------------
# 3456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890
#        1         2         3         4         5         6         7         8         9         0         1         2
#        0         0         0         0         0         0         0         0         0         1         1         1
# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
# Import Modules and Start Up Section
# ----------------------------------------------------------------------------------------------------------------------
from pathlib import Path
import pandas as pd
#
# Import Required Non-Standard Modules
#
import PySimpleGUI as sg
#
# Import OPM Common Modules
#
from opm_common import change_directory, file_lstrip, opm_header_file, opm_view, print_dict, window_debug

# ----------------------------------------------------------------------------------------------------------------------
# Define Modules Section
# ----------------------------------------------------------------------------------------------------------------------
def welltraj(file_list, units, file_out, opmsys):
    """Reads Petrel Petrel Well Trajectories, Converts and Writes Out OPM ResInsight Trajectories

    The function converts Schlumberger Petrel well trajectories into OPM ResInsight format for loading into
    OPM ResInsight, the program can also convert the data to different units.

    Parameters
    ----------
    file_list : list
        List of trajectory files to be converted
    units : dict
        A dictionary of units used to converted from various unit types
    file_out : str
        Name of the output file
    opmsys : dict
        A dictionary containing the OPMRUN system parameters

    Returns
    -------
    error : boolean
        Set to True for errors, otherwise False.
    """

    # ------------------------------------------------------------------------------------------------------------------
    # Initialize
    # ------------------------------------------------------------------------------------------------------------------
    confact = dict()
    confact['none'] = 1.0
    confact['msft'] = 3.28083989501312
    confact['ftms'] = 1 / confact['msft']
    unit    = str(units['out'])
    col_in  = []
    col_out = ['CMT', 'XCORD', 'YCORD', 'TVDSS', 'MD']
    col_fmt = {'XCORD': '{:14.6e}', 'YCORD': '{:14.6e}', 'TVDSS': '{:10.2f}', 'MD': '{:10.2f}'}
    col_txt = pd.DataFrame([['--', 'XCORD', 'YCORD', 'TVDSS', 'MD'  ],
                            ['--', '     ', '     ', 'DEPTH', 'DEPTH'],
                            ['--',  unit  ,  unit  ,  unit  ,  unit  ],
                            ['--', '--------------', '--------------', '----------', '----------']], columns=col_out)
    #                               12345678901234    12345678901234    1234567890    1234567890
    debug     = False
    header    = '-- ' + '-' * 129 + '\n'
    well_name = ''
    # ------------------------------------------------------------------------------------------------------------------
    # Process All Trajectory Files
    # ------------------------------------------------------------------------------------------------------------------
    try:
        file = open(file_out, 'w')
        text = ['Petrel Well Trajectory Conversion to OPM ResInsight Trajectory File:',
                '(1) Areal Conversion Factor Option - ' + str(units['out']),
                '(2) Depth Conversion Factor Option - ' + str(units['out'])]
        opm_header_file(file, '', file_out, ['start', 'none'], text, opmsys)
    except IOError as error:
        sg.popup_error('Error Writing to: ' + '\n  \n' + str(file_out),
                       str(error) + ': ' + str(type(error)),
                       no_titlebar=False, grab_anywhere=False, keep_on_top=False)
        return (False)
    #
    # Process Each Trajectory File
    #
    try:
        for item in file_list:
            sg.cprint('Processing: ' + str(item))
            file.write(header)
            file.write('-- ' + str(item) + '\n')
            file.write(header)
            #
            # Read Trajectory File into Memory
            #
            file_in =open(item, 'r')
            data = file_in.readlines()
            file_in.close()
            # Find All the Parameters
            nskip = 0
            for line in data:
                nskip = nskip + 1
                if line[:2] == '# ':
                    file.write('-- ' + line[2:])
                    if 'WELL NAME:' in line:
                        well_name = line[12:].strip()
                        sg.cprint('Processing: ' + well_name)
                    if '# DX DY' in line:
                        if 'm-UNITS' in line:
                            units['areal'] = 'ms'
                        else:
                            units['areal'] = 'ft'
                        sg.cprint('Processing: ' + well_name + ' Areal Input Units: ' + units.get('areal'))

                    if '# DEPTH ' in line:
                        if 'm-UNITS' in line:
                            units['depth'] = 'ms'
                        else:
                            units['depth'] = 'ft'
                        sg.cprint('Processing: ' + well_name + ' Depth Input Units: ' + units.get('depth'))

                elif 'DLS' in line:
                    col_in  = line.split()
                    sg.cprint('Processing: ' + well_name + ' Column Headers at Line ' + str(nskip))
                    nskip = nskip + 1
                    break
            #
            # Load Trajectory into a Data Frame
            #
            sg.cprint('Processing: ' + well_name + ' Trajectory Data at Line ' + str(nskip))
            data = pd.read_table(item, delimiter=' ', skiprows=nskip, header=None, names=col_in, skipinitialspace=True)
            if debug:
                sg.Print(data.columns.ravel())
                sg.Print(data)
            #
            # Set Conversion Factors If Necessary
            #
            if units['areal'] == units['out']:
                confact['areal'] = confact['none']
            else:
                if units['areal'] == units['ft']:
                    confact['areal'] = confact['ftms']
                else:
                    confact['areal'] = confact['msft']

            if units['depth'] == units['out']:
                confact['depth'] = confact['none']
            else:
                if units['depth'] == units['ft']:
                    confact['depth'] = confact['ftms']
                else:
                    confact['depth'] = confact['msft']

            if debug:
                print_dict('confact', confact, option='debug')
                print_dict('units'  , units,   option='debug')

            file.write('-- \n')
            file.write('-- APPLIED AREAL CONVERSION FACTOR: ' + str(confact['areal']) + ' \n')
            file.write('-- APPLIED DEPTH CONVERSION FACTOR: ' + str(confact['depth']) + ' \n')
            file.write('-- \n')
            file.write('WELLNAME:' + well_name + '\n')

            out  = pd.DataFrame(columns=col_out)
            out['XCORD'] = data['X' ] * confact['areal']
            out['YCORD'] = data['Y' ] * confact['areal']
            out['TVDSS'] = data['Z' ] * confact['depth'] * -1
            out['MD'   ] = data['MD'] * confact['depth']
            out['CMT'  ] = '   '
            for key, value in col_fmt.items():
                out[key] = out[key].apply(value.format)
            out = col_txt.append(pd.DataFrame(out, columns=col_out))
            out = out.to_string(index=False, header=False)

            file.write(out)
            file.write('   \n')
            file.write('-- \n')
            sg.cprint('Processing: ' + well_name + ' Complete')
        #
        # Write End of File Header
        #
        opm_header_file(file, None, file_out, ['end', 'none'], text, opmsys)
        file.close()

    except Exception as error:
        sg.popup_error('Error Writing: ' + '\n  \n' + str(file_out),
                       str(error) + ': ' + str(type(error)),
                       no_titlebar=False, grab_anywhere=False, keep_on_top=False)
        file.close()
        return(True)
    #
    # Read and Write Out Trajectory File to Remove Blanks in First Column (work around for df.to_string() issue)
    #
    file_lstrip(file_out)
    sg.cprint('Process Complete')
    return(False)


def welltraj_main(opmoptn, opmsys):
    """Main function for Converting Petrel Well Trajectories to OPM ResInsight Trajectories

    The function converts Schlumberger Petrel well trajectories into OPM ResInsight format for loading into
    OPM ResInsight, the program can also convert the data to different units.

    Parameters
    ----------
    opmoptn : dict
        Contains a dictionary list of all OPMRUN user parameters
    opmsys : dict
        A dictionary containing the OPMRUN system parameters

    Returns
    -------
    None
    """

    # ------------------------------------------------------------------------------------------------------------------
    # Initialize
    # ------------------------------------------------------------------------------------------------------------------
    debug        = False
    files        = None
    file_list    = []
    units        = dict()
    units['ft' ] = 'ft'
    units['ms' ] = 'ms'
    units['out'] = units['ft']

    # ------------------------------------------------------------------------------------------------------------------
    # Initialize GUI Setup and Define Main Window
    # ------------------------------------------------------------------------------------------------------------------
    outlog   = '_outlog1_' + sg.WRITE_ONLY_KEY
    layout1  = [[sg.Text('Select Petrel Well Trajectory Files to Convert to OPM ResInsight Trajectory File')],
                [sg.Listbox(values='', size=(100, 10), key='_filelist_',
                            font = (opmoptn['output-font'], opmoptn['output-font-size']))],
                [sg.Text('Output')],
                [sg.Multiline(key=outlog, size=(100, 15), text_color='blue', autoscroll=True,
                              font = (opmoptn['output-font'], opmoptn['output-font-size']))],
                [sg.Text('Areal and Depth Data Output Options')],
                [sg.Radio('Areal and Depth Output in feet  ', "bRadio1", key='_output_ft_', default=True)],
                [sg.Radio('Areal and Depth Output in metres', "bRadio1", key='_output_ms_')],
                [sg.Button('Add'), sg.Button('Clear',  tooltip='Clear Output'), sg.Button('List'),
                 sg.Button('Remove', tooltip='Remove Files'), sg.Submit(),
                 sg.Button('View', disabled=True, tooltip='View Results', key='_view_'), sg.Exit()]]
    window1 = sg.Window('OPM Well Trajectory Conversion Utility', layout=layout1)
    #
    #   Set Output Multiline Window for CPRINT
    #
    sg.cprint_set_output_destination(window1, outlog)

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
        # Add Files
        #
        if event == 'Add':
            files = sg.popup_get_file('Select Petrel Trajectory Files to Convert', no_window=False, size=(100,5),
                                   default_path=str(Path().absolute()), initial_folder=str(Path().absolute()),
                                   multiple_files=True, file_types=[('OPM', ['*.*'])],
                                   no_titlebar = False, grab_anywhere = False, keep_on_top = True)
            if files is not None:
                files = files.split(';')
                for file in files:
                    file_list.append(file)

                window1['_filelist_'].update(file_list)
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
            text = sg.popup_yes_no('Exit OPM Well Trajectory Utility?', no_titlebar=False,
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
            file_path = sg.popup_get_folder('Select Directory', no_window=False, size=(100,1),
                                        default_path=str(Path().absolute()), initial_folder=str(Path().absolute()))
            if file_path is not None:
                error = change_directory(file_path, popup=True, outprt=True)
                if not error:
                    file_path = Path().absolute()
                    for file in Path(File_path).glob("*.*"):
                        sg.cprint(str(Path(file).name))
                    sg.cprint('Listing Complete ' + str(file_path))
            continue
        #
        # Remove Files
        #
        if event == 'Remove':
            file_list = []
            window1['_filelist_'].update(file_list)
            continue
        #
        # Submit Options
        #
        elif event == 'Submit':
            if files is not None:
                #
                # Get Output File
                #
                file_out = Path().absolute().with_name('OPM_ResInsight_WellTrajectories.asci')
                file_out = sg.popup_get_file('Select OPM ResInsight Trajectory Output File', no_window=False,
                                             size=(100, 1),
                                             save_as=True, default_path=str(file_out),
                                             initial_folder=str(Path().absolute()),
                                             multiple_files=False,
                                             file_types=[('OPM ResInsight Trajectory', ['*.asci'])])
                if file_out is None:
                    sg.popup_error('No Output File Selected',
                                   no_titlebar=False, grab_anywhere=False, keep_on_top=False)
                    continue
                else:
                    # Set Output Units
                    if values['_output_ft_']:
                        units['out'] = units['ft']
                    else:
                        units['out'] = units['ms']
                    error = welltraj(file_list, units, file_out, opmsys)
                    if error:
                        continue
                    window1['_view_'].update(disabled=False)
                    sg.popup_ok('Process Complete Data Written to: ' + '\n  \n' + str(file_out),
                                no_titlebar=False, grab_anywhere=False, keep_on_top=False)
                    continue
            #
            # No Well Trajectories Selected
            #
            else:
                sg.popup_error('No Well Trajectories Selected', no_titlebar=False,
                               grab_anywhere=False, keep_on_top=False)
            continue
        #
        # View
        #
        elif event == '_view_':
            opm_view(file_out, opmoptn)
            continue
    #
    # Close Main Window
    #
    window1.close()

# ======================================================================================================================
# End of OPM_WELLTRAJ.PY
# ======================================================================================================================
