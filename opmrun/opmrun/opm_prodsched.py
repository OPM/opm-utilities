# =======================================================================================================================
#
"""OPM_PRODSCHED.py - Generate Production and Injection Schedule Section Based on CSV Input File

The script reads in reads an CSV file containing daily production data into a DataFrame for processing, and creates the
various variables required to generate the OPM Flow SCHEDULE section production data. The function then writes out the
schedule include file (*.inc). In addition, a debug file (*.dbg) is also written out to verify the the results of the
processing. Currently only production data via the WCONHIST keyword is supported.

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
          david.baxendale@eipc.co
Version : 2021.07.01
Date    : 15-Jul-2021
"""
# -----------------------------------------------------------------------------------------------------------------------
# 3456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890
#        1         2         3         4         5         6         7         8         9         0         1         2
#        0         0         0         0         0         0         0         0         0         1         1         1
# -----------------------------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------------------
# Import Modules and Start Up Section
# -----------------------------------------------------------------------------------------------------------------------
import datetime
from pathlib import Path
import pandas as pd
import numpy as np
#
# Import Required Non-Standard Modules
#
import FreeSimpleGUI as sg
#
# Import OPM Common Modules
#
from opmrun.opm_common import file_lstrip , opm_popup, opm_header_file, opm_view, window_debug

# ----------------------------------------------------------------------------------------------------------------------
# Define Modules Section
# ----------------------------------------------------------------------------------------------------------------------
def prodsched_check(df, list, name, default, text, window):
    """Checks if a Dataframe Column is in a List

    The function Checks if a Dataframe column is in a list, and logs the status and return code if or if not found,
    as well as updating the output data frame.

    Parameters
    ----------
    df : df
       Input dataframe.
    list : list
       List of possible column names.
    name : str
        Column name used to reset input column name.
    default: boolean
        If not found set to default value of 1* (True), or an error (False).
    text: str
        Test to printed with status.
    window : window object
        Window for display output.

    Returns
    -------
    df : df
       Output dataframe.
    error : int
        Error return code
    """
    #
    # Process
    #
    for column_name in df:
        if column_name in list:
            sg.cprint('    ' + text + ' column found as ' + column_name + ' in Column ' +
                      str(df.columns.get_loc(column_name) + 1))
            if column_name != name:
                df.rename(columns={column_name: name}, inplace=True)
            return (df, 0)

    if default:
        df[name] = '1*'
        sg.cprint('    ' + text + ' Column Not Found in ' + str(list))
        sg.cprint('    ' + text + ' Set to Default Value')
        return (df, 0)

    sg.cprint('    ' + text + ' Column Not Found in ' + str(list), text_color='red')
    return (df, 1)


def prodsched_daily(file_in, file_inc, options, window, opmsys):
    """Reads a CSV File Containing Production Data

    The function reads in a CSV file containing daily production data into a DataFrame for processing, and
    creates the various variables required to generate the SCHEDULE section production data. The function then writes
    out the schedule include file. In addition, a debug file (*.dbg) is also written out to verify the results of
    the processing.

    Parameters
    ----------
    file_in : str
       Name of input file used to capture the comp_data.
    file_inc : str
       Name of output include file used to write the keywords to.
    options : list
        options[0] : Production input volume type, set to rate, or volume.
        options[1] : THP and BHP conversion from gauge to absolute conversion factor etc.
        options[2] : THP and BHP conversion kPa to bars and MPa to bars.
        options[3] : Control mode (ORAT,GRAT etc.)
    window : window object
        Window for display output.
    opmsys : dict
        A dictionary containing the OPMRUN system parameters

    Returns
    -------
    error: int
        Error return code
    """

    # ------------------------------------------------------------------------------------------------------------------
    # Initialize Variables and Read In Data
    # ------------------------------------------------------------------------------------------------------------------
    debug = False
    if Path(file_in).is_file():
        file_dbg = Path(file_inc).with_suffix('.dbg')  # OPM Flow Debug File

    cols_in = ['oil', 'wat', 'gas', 'vfp', 'alfq', 'thp', 'bhp']
    cols_out = ['wname', 'status', 'cntl', 'oil', 'wat', 'gas', 'vfp', 'alfq', 'thp', 'bhp', 'end', 'date']
    data = pd.DataFrame()
    df = pd.DataFrame(columns=cols_out)
    df_in = pd.DataFrame()
    alfq_lst = ['alfq', 'vfp alfq', 'gas lift', 'pump speed', 'ALFQ', 'VFP ALFQ', 'GAS LIFT', 'PUMP SPEED']
    bhp_lst  = ['bhp', 'bottom-hole pressure', 'BHP', 'BOTTOM-HOLE PRESSURE']
    date_lst = ['date', 'dates', 'DATE', 'DATES', 'Date']
    oil_lst = ['oil', 'oil rate', 'orat', 'OIL', 'OIL RATE', 'ORAT', 'Prd_dly.Cond']
    thp_lst = ['thp', 'whp', 'tubing head pressure', 'THP', 'WHP', 'TUBING HEAD PRESSURE', 'Prd_dly.whp']
    wat_lst = ['wat', 'water', 'water rate', 'wrat', 'WAT', 'WATER', 'WATER RATE', 'WRAT', 'Prd_dly.Water']
    gas_lst = ['gas', 'gas rate', 'grat', 'GAS', 'GAS RATE', 'GRAT', 'Prd_dly.Gas']
    vfp_lst = ['vfp', 'vfp table', 'vfp number', 'VFP', 'VFP TABLE', 'VFP NUMBER']
    wname_lst = ['wname', 'well', 'wells', 'wellname', 'WNAME', 'WELL', 'WELLS', 'WELLNAME', 'Xy.Wellcompl']
    #
    # List Vector Names
    #
    if options[0] == 'list':
        sg.cprint('Daily Production Vector Names\n')
        sg.cprint('Artifical Lift Quantiy = ' + str(alfq_lst))
        sg.cprint('Bottom Hole Pressure   = ' + str(bhp_lst))
        sg.cprint('Date                   = ' + str(date_lst))
        sg.cprint('Oil Rate               = ' + str(oil_lst))
        sg.cprint('Tubing Head Pressure   = ' + str(thp_lst))
        sg.cprint('Water Rate             = ' + str(wat_lst))
        sg.cprint('Gas Rate               = ' + str(gas_lst))
        sg.cprint('VFP Table Number       = ' + str(vfp_lst))
        sg.cprint('Well Name              = ' + str(wname_lst) + '\n')
        return(0)
    #
    # Read In Data
    #
    sg.cprint('Reading Production Data CSV File: \n' + str(file_in))
    try:
        df_in = pd.read_csv(file_in)
        df_in = df_in.fillna(0.0)
    except Exception as error:
        sg.popup_error('Error Reading: ' + '\n  \n' + str(file_in),
                       str(error) + ': ' + str(type(error)), no_titlebar=False, grab_anywhere=False, keep_on_top=True)
        sg.cprint('Error Reading Production Data File')
        return(1)

    sg.cprint(df_in.head().to_string())
    sg.cprint('Reading Production Data File Complete \n')
    #
    # Check Column Headers, Rename Vols, and Drop Unused Cols
    #
    sg.cprint('Checking Data:')
    err_count = 0
    df_in, err = prodsched_check(df_in, wname_lst, 'wname', False, 'Well', window)
    err_count = err_count + err
    df_in, err = prodsched_check(df_in, date_lst, 'date', False, 'Date', window)
    err_count = err_count + err
    df_in, err = prodsched_check(df_in, oil_lst, 'oil', False, 'Oil Rate', window)
    err_count = err_count + err
    df_in, err = prodsched_check(df_in, wat_lst, 'wat', False, 'Water Rate', window)
    err_count = err_count + err
    df_in, err = prodsched_check(df_in, gas_lst, 'gas', False, 'Gas Rate', window)
    err_count = err_count + err
    # VFP and VFP ALQ Data Set to Default Vales if Missing
    df_in, err = prodsched_check(df_in, vfp_lst, 'vfp', True, 'VFP Tables', window)
    df_in, err = prodsched_check(df_in, alfq_lst, 'alfq', True, 'VFP Artificial Lift', window)
    # THP and BHP Data Set to Default Vales if Missing
    df_in, err = prodsched_check(df_in, thp_lst, 'thp', True, 'THP', window)
    df_in, err = prodsched_check(df_in, bhp_lst, 'bhp', True, 'BHP', window)
    sg.cprint('Checking Data: Complete \n')
    if err_count > 0:
        sg.cprint('Stopping Due to Errors')
        return (err_count)
    #
    # Replace Default Pressure Values with Zero, and Replace Spaces in Well Names with Underscores
    #
    df_in['bhp'].replace('1*', 0.0, inplace=True)
    df_in['thp'].replace('1*', 0.0, inplace=True)
    df_in['wname'] = df_in['wname'].str.replace(' ', '_')
    sg.cprint('Processing Data')
    sg.cprint(df_in.head().to_string() + '\n')

    # ------------------------------------------------------------------------------------------------------------------
    # Process Data and Setup Variables for Daily and Monthly Average Options
    # ------------------------------------------------------------------------------------------------------------------
    data['wname'] = df_in['wname']
    try:
        data['date'] = pd.to_datetime(df_in['date'])
        data[cols_in] = df_in[cols_in]
        data.sort_values(['date', 'wname'], ascending=[True, True])
        start_date = data['date'].min().strftime('%d %b %Y')
        end_date = data['date'].max().strftime('%d %b %Y')
        data['index'] = data['date']
        data.set_index('index', inplace=True)
    except ValueError as error:
        sg.popup_error('Error on Date Variable in File: ' + '\n  \n' + str(file_inc) + '\n \n' +
                       str(error) + ': ' + str(type(error)),
                       no_titlebar=False, grab_anywhere=False, keep_on_top=True)
        sg.cprint('Stopping Due to Errors')
        err_count = 1
        return (err_count)

    # Calculate Liquid Rates, and Convert THP and BHP if Requested
    data['rate'] = data['oil'] + data['wat'] + data['gas']
    data['bhp_cor'] = (pd.to_numeric(data['bhp']    , errors='ignore') + options[1]).round(1)
    data['bhp_cor'] = (pd.to_numeric(data['bhp_cor'], errors='ignore') * options[2]).round(1)
    data['thp_cor'] = (pd.to_numeric(data['thp']    , errors='ignore') + options[1]).round(1)
    data['thp_cor'] = (pd.to_numeric(data['thp_cor'], errors='ignore') * options[2]).round(1)

    # Status and Open/Close Change Flag
    data['status'] = np.where(data['rate'] > 0, 'OPEN', 'SHUT')
    data['cflag'] = np.where(data['status'].ne(data['status'].shift(1)), 1, 0)

    # Sum Monthly Volumes and Days by Well
    data['Np'] = data.groupby(['wname', pd.Grouper(freq='M')])['oil'].cumsum()
    data['Wp'] = data.groupby(['wname', pd.Grouper(freq='M')])['wat'].cumsum()
    data['Gp'] = data.groupby(['wname', pd.Grouper(freq='M')])['gas'].cumsum()
    data['days'] = data.groupby(['wname', pd.Grouper(freq='M')]).cumcount() + 1

    # Calculate Average Monthly Rates
    data['oil_avg'] = (data['Np'] / data['days']).round(1)
    data['wat_avg'] = (data['Wp'] / data['days']).round(1)
    data['gas_avg'] = (data['Gp'] / data['days']).round(1)

    # Calculate Days on Production in a Month
    data['day_opn'] = 1.0
    data['day_opn'] = np.where(data['status'] == 'OPEN', 1.0, 0.0)
    data['day_opn'] = data.groupby(['wname', pd.Grouper(freq='M'), 'day_opn'])['day_opn'].cumsum()

    # Calculate Shut-In Days in a Month
    data['day_cls'] = 1.0
    data['day_cls'] = np.where(data['status'] == 'SHUT', 1.0, 0.0)
    data['day_cls'] = data.groupby(['wname', pd.Grouper(freq='M'), 'day_cls'])['day_cls'].cumsum()
    # Replace Missing Values by Previous Value by Well and by Month
    data.replace([np.inf, -np.inf], np.nan, inplace=True)
    data = data.fillna(0)

    # Set Start of Production Date and Shut-In Date
    data['date_dbg'] = data['date'].where(data['cflag'] == 1, np.nan)
    data['date_dbg'] = data['date'].where(data['day_opn'] == 1, data['date_dbg'])
    data['date_dbg'] = data['date'].where(data['day_cls'] == 1, data['date_dbg'])
    data['date_eff'] = data['date_dbg']

    # Fill Forward Missing Dates
    data['date_eff'] = data['date_eff'].fillna(method='ffill')
    data['day_eff'] = data['date'] - data['date_eff']
    data['day_eff'] = data['day_eff'].dt.days.astype(int) + 1
    #
    # Define Producing and Shut-in Intervals for Effective Monthly Rates
    #
    data['ops_eff'] = data['cflag']
    data['ops_eff'] = data.groupby(['wname', pd.Grouper(freq='M')])['ops_eff'].cumsum()

    # Calculate Effective Monthly Rates Based and Pressures over Producing Interval
    data['oil_eff'] = data.groupby(['wname', pd.Grouper(freq='M'), 'ops_eff'])['oil'].cumsum() / data['day_eff']
    data['wat_eff'] = data.groupby(['wname', pd.Grouper(freq='M'), 'ops_eff'])['wat'].cumsum() / data['day_eff']
    data['gas_eff'] = data.groupby(['wname', pd.Grouper(freq='M'), 'ops_eff'])['gas'].cumsum() / data['day_eff']
    data['thp_eff'] = data.groupby(['wname', pd.Grouper(freq='M'), 'ops_eff'])['thp_cor'].cumsum() / data['day_eff']
    data['bhp_eff'] = data.groupby(['wname', pd.Grouper(freq='M'), 'ops_eff'])['bhp_cor'].cumsum() / data['day_eff']

    # Round Values
    data['oil_eff'] = data['oil_eff'].round(1)
    data['oil_eff'] = data['oil_eff'].round(1)
    data['wat_eff'] = data['wat_eff'].round(1)
    data['gas_eff'] = data['gas_eff'].round(1)
    data['thp_eff'] = data['thp_eff'].round(1)
    data['bhp_eff'] = data['bhp_eff'].round(1)

    # File Output Text
    text = ['OPM Flow Production and Injection Schedule keywords via OPMRUN(PRODSCHED) option:', '',
            '  1) Production Schedule Option: ' + str(options[0]).upper(),
            '  2) Pressure Conversion Factor: ' + str(options[1]).upper(),
            '  2) Pressure Scale Factor     : ' + str(options[2]).upper(),
            '  2) Well Control Mode         : ' + options[3],
            '  3) Start Date                : ' + str(start_date),
            '  4) End Date                  : ' + str(end_date), '',
            'Data generated from CSV file containing well names dates and production data. The current implementation '+
            'only considers CSV \n-- files as input.',
            'Only production data is currently used, injection data not implemented.']
    #
    # Debug and Debug File Output
    #
    if debug:
        sg.Print(data.columns.ravel())
        sg.Print(data)

    file = open(file_dbg, 'w')
    opm_header_file(file, file_in, file_inc, ['start', ''], text, opmsys)
    opm_header_file(file, file_in, file_inc, ['', ''], ['DEBUG START: DATA DATAFRAME POST PROCESSING '], opmsys)
    file.write(data.to_string())
    opm_header_file(file, file_in, file_inc, ['', ''], ['DEBUG END: DATA DATAFRAME POST PROCESSING '], opmsys)
    file.close()
    sg.cprint('Debug Data Written to Debug File')

    # ------------------------------------------------------------------------------------------------------------------
    # Setup Output Dataframe Based on Selected Option
    # ------------------------------------------------------------------------------------------------------------------
    if options[0] == 'daily':
        df['wname'] = data['wname']
        df['status'] = data['status']
        df['cntl'] = options[3]
        df['oil'] = data['oil']
        df['wat'] = data['wat']
        df['gas'] = data['gas']
        df['vfp'] = data['vfp']
        df['alfq'] = data['alfq']
        df['bhp'] = data['bhp_cor']
        df['thp'] = data['thp_cor']
        df['end'] = '/'
        df['date'] = data['date']

    elif options[0] == 'monthly':
        df['wname'] = data['wname']
        df['status'] = data['status']
        df['cntl'] = options[3]
        df['oil'] = data['oil_avg']
        df['wat'] = data['wat_avg']
        df['gas'] = data['gas_avg']
        df['vfp'] = data['vfp']
        df['alfq'] = data['alfq']
        df['bhp'] = data['bhp_cor']
        df['thp'] = data['thp_cor']
        df['end'] = '/'
        df['date'] = data['date']
        df['status'] = np.where((df['oil'] + df['wat'] + df['gas']) > 0, 'OPEN', 'SHUT')
        df = df.groupby(['wname', df.index.year, df.index.month]).tail(1)

    elif options[0] == 'monthly_eff':
        df['wname'] = data['wname']
        df['status'] = data['status']
        df['cntl'] = options[3]
        df['oil'] = data['oil_eff']
        df['wat'] = data['wat_eff']
        df['gas'] = data['gas_eff']
        df['vfp'] = data['vfp']
        df['alfq'] = data['alfq']
        df['bhp'] = data['bhp_eff']
        df['thp'] = data['thp_eff']
        df['end'] = '/'
        df['date'] = data['date_eff']
        df = df.groupby(['wname', df.date]).tail(1)

    sg.cprint('Creating Output')
    sg.cprint(df.head().to_string() + '\n')
    #
    # Debug File Output
    #
    file = open(file_dbg, 'a')
    opm_header_file(file, file_in, file_inc, ['', ''], ['DEBUG START: DATA DATAFRAME POST PROCESSING '], opmsys)
    file.write(df.to_string())
    opm_header_file(file, file_in, file_inc, ['', ''], ['DEBUG END: DATA DATAFRAME POST PROCESSING '], opmsys)
    file.close()
    sg.cprint('Summary Data Written to Debug File')
    #
    # Write Out WCONHIST Keywords per Time Step
    #
    try:
        file = open(file_inc, 'w')
        opm_header_file(file, file_in, file_inc, ['start', 'NOECHO'], text, opmsys)
        sched = df.groupby('date')

        for key, item in sched:
            if options[0] == 'daily':
                file.write('DATES \n' + str(key.strftime('%d %b %Y')) + '  /\n/\n\n')
            if options[0] == 'monthly':
                file.write('DATES \n' + str(key.strftime('01 %b %Y')) + '  /\n/\n\n')
            if options[0] == 'monthly_eff':
                file.write('DATES \n' + str(key.strftime('%d %b %Y')) + '  /\n/\n\n')

            out = sched.get_group(key)
            prodsched_keyword(file, 'WCONHIST', '', out)

        opm_header_file(file, file_in, file_inc, ['end', 'ECHO'], [' '], opmsys)
        file.close()
        sg.cprint('Schedule Data Written to Include File')

    except Exception as error:
        sg.popup_error('Error Writing: ' + '\n  \n' + str(file_inc) + '\n \n' + str(error) + ': ' + str(type(error)),
                       no_titlebar=False, grab_anywhere=False, keep_on_top=True)
        return(1)
    #
    # Read and Write Out Schedule File to Remove Blanks in First Column (work around for df.to_string() issue)
    #
    file_lstrip(file_inc)
    sg.cprint('Process Complete')
    return(0)


def prodsched_keyword(file, keyword, unit='', data=None):
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

    if keyword == 'WCONHIST':
        file.write('--                                     \n')
        file.write('-- WELL HISTORICAL PRODUCTION CONTROLS \n')
        file.write('--                                     \n')
        out = pd.DataFrame([['-- WELL ', 'OPEN', 'CNTL', 'OIL', 'WAT', 'GAS', 'VFP', 'VFP', 'THP', 'BHP',
                             ' ', ' '],
                            ['-- NAME ', 'SHUT', 'MODE', 'RATE', 'RATE', 'RATE', 'TABLE', 'ALFQ', 'PRES', 'PRES',
                             ' ', ' '],
                            ['WCONHIST', '    ', '    ', '    ', '    ', '    ', '     ', '    ', '    ', '    ',
                             ' ', ' ']], columns=data.columns)
    else:
        sg.popup_error('Error Keyword Not Found: ' + '\n  \n' + keyword, no_titlebar=False, grab_anywhere=False,
                       keep_on_top=True)
    try:
        out = pd.concat([out, data])
        out = out.to_string(index=False, header=False, justify='start',
                            formatters={'date':  lambda x: x if type(x) == str else x.strftime('%Y-%m-%d')})
        file.write(out)
        file.write('\n/\n\n')
    except Exception as error:
        sg.popup_error('Error Processing ' + keyword + '\n \n' +
                       str(error) + ': ' + str(type(error)), no_titlebar=False, grab_anywhere=False, keep_on_top=True)
    return ()


def prodsched_monthly(file_in, file_inc, options, window, opmsys):
    """Reads a CSV File Containing Production Data

    The function reads in a CSV file containing monthly production data into a DataFrame for processing, and
    creates the various variables required to generate the SCHEDULE section production data. The function then writes
    out the schedule include file. In addition, a debug file (*.dbg) is also written out to verify the results of
    the processing.

    Parameters
    ----------
    file_in : str
       Name of input file used to capture the comp_data.
    file_inc : str
       Name of output include file used to write the keywords to.
    options : list
        options[0] : Production input volume type, set to rate, or volume.
        options[1] : THP and BHP conversion from gauge to absolute conversion factor etc.
        options[2] : THP and BHP conversion kPa to bars and MPa to bars.
        options[3] : Control mode (ORAT,GRAT etc.)
    window : window object
        Window for display output.
    opmsys : dict
        A dictionary containing the OPMRUN system parameters

    Returns
    -------
    error: int
        Error return code
    """

    # ------------------------------------------------------------------------------------------------------------------
    # Initialize Variables and Read In Data
    # ------------------------------------------------------------------------------------------------------------------
    debug = False
    if Path(file_in).is_file():
        file_dbg = Path(file_inc).with_suffix('.dbg')  # OPM Flow Debug File

    cols_in = ['oil', 'wat', 'gas', 'vfp', 'alfq', 'thp', 'bhp', 'days']
    cols_out = ['wname', 'status', 'cntl', 'oil', 'wat', 'gas', 'vfp', 'alfq', 'thp', 'bhp', 'end', 'date']
    data = pd.DataFrame()
    df = pd.DataFrame(columns=cols_out)
    df_in = pd.DataFrame()
    alfq_lst = ['alfq', 'vfp alfq', 'gas lift', 'pump speed', 'ALFQ', 'VFP ALFQ', 'GAS LIFT', 'PUMP SPEED']
    bhp_lst = ['bhp', 'bottom-hole pressure', 'BHP', 'BOTTOM-HOLE PRESSURE']
    date_lst = ['date', 'dates', 'DATE', 'DATES', 'Date', 'ProdDate']
    days_lst = ['Hist Days']
    oil_lst = ['oil', 'oil rate', 'orat', 'OIL', 'OIL RATE', 'ORAT', 'Hist Oil']
    thp_lst = ['thp', 'whp', 'tubing head pressure', 'THP', 'WHP', 'TUBING HEAD PRESSURE']
    wat_lst = ['wat', 'water', 'water rate', 'wrat', 'WAT', 'WATER', 'WATER RATE', 'WRAT', 'Hist Water']
    gas_lst = ['gas', 'gas rate', 'grat', 'GAS', 'GAS RATE', 'GRAT', 'Hist Gas']
    vfp_lst = ['vfp', 'vfp table', 'vfp number', 'VFP', 'VFP TABLE', 'VFP NUMBER']
    wname_lst = ['wname', 'Well', 'well', 'wells', 'wellname', 'WNAME', 'WELL', 'WELLS', 'WELLNAME', 'Xy.Wellcompl']
    #
    # List Vector Names
    #
    if options[0] == 'list':
        sg.cprint('Monthly Production Vector Names\n')
        sg.cprint('Artifical Lift Quantiy = ' + str(alfq_lst))
        sg.cprint('Bottom Hole Pressure   = ' + str(bhp_lst))
        sg.cprint('Date                   = ' + str(date_lst))
        sg.cprint('Days                   = ' + str(days_lst))
        sg.cprint('Oil Volume             = ' + str(oil_lst))
        sg.cprint('Tubing Head Pressure   = ' + str(thp_lst))
        sg.cprint('Water Volume           = ' + str(wat_lst))
        sg.cprint('Gas Volume             = ' + str(gas_lst))
        sg.cprint('VFP Table Number       = ' + str(vfp_lst))
        sg.cprint('Well Name              = ' + str(wname_lst) + '\n')
        return(0)
    #
    # Read In Data
    #
    sg.cprint('Reading Production Data CSV File: \n' + str(file_in))
    try:
        df_in = pd.read_csv(file_in)
        df_in = df_in.fillna(0.0)
    except Exception as error:
        sg.popup_error('Error Reading: ' + '\n  \n' + str(file_in),
                       str(error) + ': ' + str(type(error)), no_titlebar=False, grab_anywhere=False, keep_on_top=True)
        sg.cprint('Error Reading Production Data File')
        return(1)

    sg.cprint(df_in.head().to_string())
    sg.cprint('Reading Production Data File Complete \n')
    #
    # Check Column Headers, Rename Vols, and Drop Unused Cols
    #
    sg.cprint('Checking Data:')
    err_count = 0
    df_in, err = prodsched_check(df_in, wname_lst, 'wname', False, 'Well', window)
    err_count = err_count + err
    df_in, err = prodsched_check(df_in, date_lst, 'date', False, 'Date', window)
    err_count = err_count + err
    df_in, err = prodsched_check(df_in, days_lst, 'days', False, 'Days', window)
    err_count = err_count + err
    df_in, err = prodsched_check(df_in, oil_lst, 'oil', False, 'Oil Volume', window)
    err_count = err_count + err
    df_in, err = prodsched_check(df_in, wat_lst, 'wat', False, 'Water Volume', window)
    err_count = err_count + err
    df_in, err = prodsched_check(df_in, gas_lst, 'gas', False, 'Gas Volume', window)
    err_count = err_count + err
    # VFP and VFP ALQ Data Set to Default Vales if Missing
    df_in, err = prodsched_check(df_in, vfp_lst, 'vfp', True, 'VFP Tables', window)
    df_in, err = prodsched_check(df_in, alfq_lst, 'alfq', True, 'VFP Artificial Lift', window)
    # THP and BHP Data Set to Default Vales if Missing
    df_in, err = prodsched_check(df_in, thp_lst, 'thp', True, 'THP', window)
    df_in, err = prodsched_check(df_in, bhp_lst, 'bhp', True, 'BHP', window)
    sg.cprint('Checking Data: Complete \n')
    if err_count > 0:
        sg.cprint('Stopping Due to Errors')
        return (err_count)
    #
    # Replace Default Pressure Values with Zero, and Replace Spaces in Well Names with Underscores
    #
    df_in['bhp'].replace('1*', 0.0, inplace=True)
    df_in['thp'].replace('1*', 0.0, inplace=True)
    df_in['wname'] = df_in['wname'].str.replace(' ', '_')
    sg.cprint('Processing Data')
    sg.cprint(df_in.head().to_string() + '\n')

    # ------------------------------------------------------------------------------------------------------------------
    # Process Data and Setup Variables
    # ------------------------------------------------------------------------------------------------------------------
    data['wname'] = df_in['wname']
    try:
        data['date'] = pd.to_datetime(df_in['date'])
        data[cols_in] = df_in[cols_in]
        data.sort_values(['date', 'wname'], ascending=[True, True])
        start_date = data['date'].min().strftime('%d %b %Y')
        end_date = data['date'].max().strftime('%d %b %Y')
        data['index'] = data['date']
        data.set_index('index', inplace=True)
    except ValueError as error:
        sg.popup_error('Error on Date Variable in File: ' + '\n  \n' + str(file_inc) + '\n \n' +
                       str(error) + ': ' + str(type(error)),
                       no_titlebar=False, grab_anywhere=False, keep_on_top=True)
        sg.cprint('Stopping Due to Errors')
        err_count = 1
        return (err_count)

    # Calculate Liquid Rates, and Convert THP and BHP if Requested
    data['rate'] = data['oil'] + data['wat'] + data['gas']
    data['bhp_cor'] = (pd.to_numeric(data['bhp']    , errors='ignore') + options[1]).round(1)
    data['bhp_cor'] = (pd.to_numeric(data['bhp_cor'], errors='ignore') * options[2]).round(1)
    data['thp_cor'] = (pd.to_numeric(data['thp']    , errors='ignore') + options[1]).round(1)
    data['thp_cor'] = (pd.to_numeric(data['thp_cor'], errors='ignore') * options[2]).round(1)

    # Status and Open/Close Change Flag
    data['status'] = np.where(data['rate'] > 0, 'OPEN', 'SHUT')
    data['cflag'] = np.where(data['status'].ne(data['status'].shift(1)), 1, 0)

    # Set Monthly Volumes and Days by Well
    data['Np']   = data['oil']
    data['Wp']   = data['wat']
    data['Gp']   = data['gas']

    # Calculate Average Daily Rates
    data['oil_avg'] = (data['Np'] / data['days']).round(1)
    data['wat_avg'] = (data['Wp'] / data['days']).round(1)
    data['gas_avg'] = (data['Gp'] / data['days']).round(1)

    # Replace Missing Values by Previous Value by Well and by Month
    data.replace([np.inf, -np.inf], np.nan, inplace=True)
    data = data.fillna(0)

    # File Output Text
    text = ['OPM Flow Production and Injection Schedule keywords via OPMRUN(PRODSCHED) option:', '',
            '  1) Production Schedule Option: ' + str(options[0]).upper(),
            '  2) Pressure Conversion Factor: ' + str(options[1]).upper(),
            '  2) Pressure Scale Factor     : ' + str(options[2]).upper(),
            '  2) Well Control Mode         : ' + options[3],
            '  3) Start Date                : ' + str(start_date),
            '  4) End Date                  : ' + str(end_date), '',
            'Data generated from CSV file containing well names dates and production data. The current implementation '+
            'only considers CSV \n-- files as input.',
            'Only production data is currently used, injection data not implemented.']
    #
    # Debug and Debug File Output
    #
    if debug:
        sg.Print(data.columns.ravel())
        sg.Print(data)

    file = open(file_dbg, 'w')
    opm_header_file(file, file_in, file_inc, ['start', ''], text, opmsys)
    opm_header_file(file, file_in, file_inc, ['', ''], ['DEBUG START: DATA DATAFRAME POST PROCESSING '], opmsys)
    file.write(data.to_string())
    opm_header_file(file, file_in, file_inc, ['', ''], ['DEBUG END: DATA DATAFRAME POST PROCESSING '], opmsys)
    file.close()
    sg.cprint('Debug Data Written to Debug File')

    # ------------------------------------------------------------------------------------------------------------------
    # Setup Output Dataframe Based on Selected Option
    # ------------------------------------------------------------------------------------------------------------------
    if options[0] == 'rate':
        df['wname'] = data['wname']
        df['status'] = data['status']
        df['cntl'] = options[3]
        df['oil'] = data['oil']
        df['wat'] = data['wat']
        df['gas'] = data['gas']
        df['vfp'] = data['vfp']
        df['alfq'] = data['alfq']
        df['bhp'] = data['bhp_cor']
        df['thp'] = data['thp_cor']
        df['end'] = '/'
        df['date'] = data['date']

    elif options[0] == 'volume':
        df['wname'] = data['wname']
        df['status'] = data['status']
        df['cntl'] = options[3]
        df['oil'] = data['oil_avg']
        df['wat'] = data['wat_avg']
        df['gas'] = data['gas_avg']
        df['vfp'] = data['vfp']
        df['alfq'] = data['alfq']
        df['bhp'] = data['bhp_cor']
        df['thp'] = data['thp_cor']
        df['end'] = '/'
        df['date'] = data['date']
        df['status'] = np.where((df['oil'] + df['wat'] + df['gas']) > 0, 'OPEN', 'SHUT')
        df = df.groupby(['wname', df.index.year, df.index.month]).tail(1)

    sg.cprint('Creating Output')
    sg.cprint(df.head().to_string() + '\n')
    #
    # Debug File Output
    #
    file = open(file_dbg, 'a')
    opm_header_file(file, file_in, file_inc, ['', ''], ['DEBUG START: DATA DATAFRAME POST PROCESSING '], opmsys)
    file.write(df.to_string())
    opm_header_file(file, file_in, file_inc, ['', ''], ['DEBUG END: DATA DATAFRAME POST PROCESSING '], opmsys)
    file.close()
    sg.cprint('Summary Data Written to Debug File')
    #
    # Write Out WCONHIST Keywords per Time Step
    #
    try:
        file = open(file_inc, 'w')
        opm_header_file(file, file_in, file_inc, ['start', 'NOECHO'], text, opmsys)
        sched = df.groupby('date')

        for key, item in sched:
            file.write('DATES \n' + str(key.strftime('01 %b %Y')) + '  /\n/\n\n')
            out = sched.get_group(key)
            prodsched_keyword(file, 'WCONHIST', '', out)

        opm_header_file(file, file_in, file_inc, ['end', 'ECHO'], [' '], opmsys)
        file.close()
        sg.cprint('Schedule Data Written to Include File')

    except Exception as error:
        sg.popup_error('Error Writing: ' + '\n  \n' + str(file_inc) + '\n \n' + str(error) + ': ' + str(type(error)),
                       no_titlebar=False, grab_anywhere=False, keep_on_top=True)
        return(1)
    #
    # Read and Write Out Schedule File to Remove Blanks in First Column (work around for df.to_string() issue)
    #
    file_lstrip(file_inc)
    sg.cprint('Process Complete')
    return(0)


def prodsched_main(opmoptn, opmsys):
    """Main function to Generate the OPM Flow WCONHIST Keywords from Daily Production Data

    OPMRUN is a Graphical User Interface ("GUI") program for the Open Porous Media ("OPM") Flow simulator. The
    OPM_PRODSCHED option reads a CSV file (comma delimiter file) containing the the daily production data, and writes
    out a daily or monthly OPM Flow SCHEDULE section accounting for any shut-in periods. That is if a well is shut-in
    during a month the production volume is accounted for up to the point of shut-in, and the well is shut-in. If well
    re-opens then the production rate is calculated to the end of the month.

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
    # Initialize
    # ------------------------------------------------------------------------------------------------------------------
    debug    = False
    file_in  = ''
    file_inc = ''
    controls = ('ORAT', 'WRAT', 'GRAT', 'LRAT', 'RESV', 'BHP')
    pressure = ('No Conversion', 'barsg to barsa', 'kPag to barsa', 'MPag to barsa', 'psig to psia')
    constant = (0.0            ,  1.01325        ,  101.325       ,  101.325       ,  14.7         )
    scale    = (1.0            ,  1.0            ,  0.01          ,  0.10          ,  1.0          )
    schedule = ('Daily Production and Injection Schedule', 'Monthly Averaged Daily Production & Injection Schedule',
                'Monthly On-stream Average Daily Production & Injection Schedule')
    options = []
    #
    # Define General Text Variables
    #
    helptext = (
        'OPMRUN is a Graphical User Interface ("GUI") program for the Open Porous Media ("OPM") Flow ' +
        'simulator. \n' +
        ' \n' +
        'The OPM_PROD_SCHED option reads an csv file (comma delimiter file) containing the the daily production ' +
        'data and writes out a daily or monthly OPM Flow SCHEDULE section accounting for any shut-in periods. ' +
        'The input file consists of a column header row that defines the data type of each column, which is then '  +
        'followed by the data, as shown below: \n' +
        '\n'
        'WELL, Date, Prd_dly.Time, ORAT, WRAT, GRAT, Prd_dly.whp, Prd_dly.wht \n'
        'GP-P1-01, 03/01/2020, 24, 25, 16, 10528, 551, 133\n'
        'GP-P1-01, 03/02/2020, 24, 25, 16, 10507, 551, 133\n'
        'GP-P1-01, 03/03/2020, 24, 25, 16, 10513, 550, 133\n' +
        '\n'

        'Various column headers have been accounted for and software will list out the options as it processing ' +
        'the input file\n' +
        '\n' +
         'The schedule data can be generated in various ways to account for well opening and closing:\n' +
        '\n' +
        'Daily Projection and Injection Schedule: This option writes out the data as is with all the opening and ' +
        'closing of the wells inherent in the schedule. However, this will cause the simulator to take daily ' +
        'time steps which will seriously impact computational performance.' +
        '\n\n' +
        'Monthly Average Production and Injection Schedule: Here the rates are averaged over the month, and is ' +
        'the typical way a schedule section is generated. The disadvantage of this formulation is that if a ' +
        'well"s production status changes in a month, the average monthly rate will not reflect a well"s true ' +
        'rate. Nevertheless, in this case the simulation will be able to take a maximum of monthly time steps. ' +
        '\n\n' +
        'Monthly On-stream Average Daily Production & Injection Schedule: This option attempts, to combine the ' +
        'advantages of the previous two formulations. Here, the average rate is based on a well"s producing ' +
        'days, and includes any operational changes to a well. That is if a well is shut-in during a month the ' +
        'production volume is accounted for up to the point of the shut-in, and the well is shut-in. If a well ' +
        're-opens then the production rate is calculated to the end of the month. This will result in variable ' +
        'time steps but with majority of them being monthly time steps.' +
        '\n\n' +
        'Note: \n' +
        '----- \n' +
        'The program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without ' +
        'even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the ' +
        'GNU General Public Licenses for more details. \n' +
        '\n' +
        'Copyright (C) 2020-2021 Equinox International Petroleum Consultants Pte Ltd. \n'
        '\n' +
        'Author  : David Baxendale (david.baxendale@eipc.co)')

    # ------------------------------------------------------------------------------------------------------------------
    # Define GUI Section
    # ------------------------------------------------------------------------------------------------------------------
    outlog = '_outlog1_'
    layout1 = [
        [sg.Text('OPM_PROD_SCHED Option to Generate the OPM Flow WCONHIST Keywords from Exported Production Data')],
        [sg.Text('Exported Production Data File Type: '),
         sg.Radio('Daily Production Data', "bRadio1",  key='_daily_', enable_events = True, default= True),
         sg.Radio('Monthly Average Rate Production Data',"bRadio1", key='_rate_', enable_events = True),
         sg.Radio('Monthly Volume Production Data',"bRadio1", key='_volume_', enable_events = True)],
        [sg.Input(file_in, key='_input_', size=(130, None)),
         sg.FilesBrowse(target='_input_', initial_folder=str(Path().absolute()),
                        file_types=(('PROD', '*.csv *.CSV'), ('All', '*.*')))],
        [sg.Text('OPM Flow Schedule Section Output Include File (Leave Blank for Default)')],
        [sg.InputText(file_inc, key='_output_', size=(130, None)),
         sg.FilesBrowse(target='_output_', initial_folder=Path().absolute(),
                        file_types=(('Simulator Include File', '*.inc *.INC'), ('All', '*.*')))],
        [sg.Text('Output Log')],
        [sg.Multiline(key=outlog, size=(137, 20), text_color='blue', autoscroll=True, auto_refresh=True,
                      write_only = True, font=(opmoptn['output-font'], opmoptn['output-font-size']))],
        [sg.Text('\nOutput Options:')],
        [sg.Text('Well \nControl \nOptions'),
         sg.Listbox(controls, default_values='GRAT', key='_control_', size=(15, 7)),
         sg.Text('Pressure \nConversion \nOptions'),
         sg.Listbox(pressure, default_values='No Conversion', key='_pressure_', size=(15, 7)),
         sg.Text('Daily Data \nProduction \nSchedule \nOutput \nOptions'),
         sg.Listbox(schedule, default_values='Daily Production and Injection Schedule', key='_schedule_', size=(68, 7))
         ],
        [sg.Text('')],
        [sg.Button('Clear', key='_clear_'), sg.Button('Help', key='_help_'),
         sg.Button('List', key='_list_', tooltip='List available vector names for selected option'), sg.Submit(),
         sg.Button('View', disabled=True, tooltip='View Results', key='_view_'), sg.Exit()]]

    window1 = sg.Window('OPM_PROD_SCHED Production Schedule Utility', layout=layout1, no_titlebar=False,
                        grab_anywhere=False)

    #   Set Output Multiline Window for CPRINT
    sg.cprint_set_output_destination(window1, outlog)

    # ------------------------------------------------------------------------------------------------------------------
    # Define GUI Event Loop, Read Buttons, and Make Callbacks etc. Section
    # ------------------------------------------------------------------------------------------------------------------
    while True:
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
            text = sg.popup_yes_no('Exit OPMRUN: Production Schedule Utility?', no_titlebar=False, grab_anywhere=False,
                                   keep_on_top=True)
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
        #  List
        #
        elif event == '_list_':
            if values['_rate_'] or values['_volume_']:
                error = prodsched_monthly(file_in, file_inc, ['list'], window1, opmsys)
            else:
                error = prodsched_daily(file_in, file_inc, ['list'], window1, opmsys)
            continue
        # --------------------------------------------------------------------------------------------------------------
        # Submit Daily Input File Processing
        # --------------------------------------------------------------------------------------------------------------
        elif event == '_daily_':
            window1['_schedule_'].update(values = schedule, set_to_index=0)
            continue

        elif event == 'Submit' and values['_daily_']:
            options = []
            if 'Daily Production and Injection Schedule' in values['_schedule_']:
                options.append('daily')
            elif 'Monthly Averaged Daily Production & Injection Schedule' in values['_schedule_']:
                options.append('monthly')
            else:
                options.append('monthly_eff')

            n = pressure.index(values['_pressure_'][0])
            options.append(constant[n])
            options.append(scale[n])
            options.append(values['_control_'][0])
            #
            # Check for Valid Input File and Process
            #
            file_in = values['_input_']
            file_inc = values['_output_']
            if not Path(file_in).is_file():
                sg.popup_error('Cannot Find Input File: ', str(file_in),
                               no_titlebar=False, grab_anywhere=False, keep_on_top=True)
                continue
            if not Path(file_inc).is_file():
                file_inc = Path(file_in).with_suffix('.inc')  # Include File
                window1['_output_'].update(file_inc)
                sg.cprint(file_inc)

            error = prodsched_daily(file_in, file_inc, options, window1, opmsys)
            if error !=0:
                continue
            window1['_view_'].update(disabled=False)
            sg.popup_ok('OPM_PROD_SCHED Process Complete Data Written to: ' + '\n  \n' + str(file_inc),
                        no_titlebar=False, grab_anywhere=False, keep_on_top=True)
            continue
        # --------------------------------------------------------------------------------------------------------------
        # Submit Monthly Input Data Processing
        # --------------------------------------------------------------------------------------------------------------
        elif event == '_rate_' or event == '_volume_':
            window1['_schedule_'].update('')
            continue

        elif event == 'Submit' and not values['_daily_'] :
            options = []
            if values['_rate_']:
                options.append('rate')
            else:
                options.append('volume')

            n = pressure.index(values['_pressure_'][0])
            options.append(constant[n])
            options.append(scale[n])
            options.append(values['_control_'][0])
            #
            # Check for Valid Input File and Process
            #
            file_in = values['_input_']
            file_inc = values['_output_']
            if not Path(file_in).is_file():
                sg.popup_error('Cannot Find Input File: ', str(file_in),
                               no_titlebar=False, grab_anywhere=False, keep_on_top=True)
                continue
            if not Path(file_inc).is_file():
                file_inc = Path(file_in).with_suffix('.inc')  # Include File
                window1['_output_'].update(file_inc)
                sg.cprint(file_inc)

            error = prodsched_monthly(file_in, file_inc, options, window1, opmsys)
            if error !=0:
                continue
            window1['_view_'].update(disabled=False)
            sg.popup_ok('OPM_PROD_SCHED Process Complete Data Written to: ' + '\n  \n' + str(file_inc),
                        no_titlebar=False, grab_anywhere=False, keep_on_top=True)
            continue
        #
        # View
        #
        elif event == '_view_':
            opm_view(values['_output_'], opmoptn)
            continue

    # ------------------------------------------------------------------------------------------------------------------
    # Post Processing Section - Close Main Window
    # ------------------------------------------------------------------------------------------------------------------
    window1.close()
    return ()

# ======================================================================================================================
# End of OPM_PRODSCHED.py
# ======================================================================================================================
