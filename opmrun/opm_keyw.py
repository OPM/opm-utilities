# ======================================================================================================================
#
"""OPM_KEYW.py - OPMRUN Keyword Generation Utility

OPM Flow Keyword Generation Utility is a Graphical User Interface ("GUI") program for the Open Porous Media ("OPM")
Flow simulator

This module generates input decks based of the keywords available for the simulator and users the Apache Velocity
Template Language ("VTL") for the templates. VTL is a common templating language used by many programming editors, and
therefore the templates can also be used directly with an editor provided the editor supports VTL. The Python airspeed
package is used to parse the templates and the key templates are comparable to the examples depicted in the
OPM Flow Manual.

The "Keyword Filter" button allows for the filtering of the various keywords in the selected section, including being
able to list all the keywords available for all sections. Clicking on a keyword will result in the keyword being
"pasted" into the Deck element. This element is editable by simply clicking anywhere in the element and making changes.

The "Clear" button will will clear the Deck element of all text, and the "Copy" button will copy the text in the Deck
element to the clipboard from which you can paste the text in your chosen editor. The text can also be saved to a file
by selecting the "Save" button

See the OPM Flow manual for further information.

Program Documentation
---------------------
Only Python 3 is supported and tested Python2 support has been depreciated.

2021.07.01 - Minor re-factoring of code.
2020.04.03 - Removed the option for stand alone running to simplify code base.
2020.04.02 - Added a DATA (Set) option for data sets and added various data set templates.
           - Added MODEL option and added various selected OPM Flow models as complete examples.
           - Fixed inconsistent Python major release check.
           - Updated SUMMARY template to cover additional variables and added dialog box to display the options in
             order to be consistent with the manual.
           - Move several functions to opm_common to reduce code duplication.
           - Users NumPy/SciPy Docstrings documentation format and documented all functions.
2020.04.01 - Initial release of OPMKEYW
           - Support for Python 3 only.
           - Based PySimpleGUI version 4.14.1

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
Date    : 26-Jul-2021

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
import platform
from datetime import datetime
from pathlib import Path
#
# Import Required Non-Standard Modules
#
import airspeed
import PySimpleGUI as sg
#
# Import OPM Common Modules
#
from opm_common import copy_to_clipboard, opm_initialize, opm_popup, print_dict

# ----------------------------------------------------------------------------------------------------------------------
# Define OPMKEYW Specific Modules
# ----------------------------------------------------------------------------------------------------------------------
def keyw_check_directory(keywdir):
    """Check for the OPMKEYW Template Directory

    Checks if keywdir is a valid OPMKEYW template directory

    Parameters
    ----------
    keywdir : str
        The directory to check for the OPMKEYW keyword templates

    Returns
    -------
    patherr : boolean
         True for valid template path, otherwise false.
    """

    pathchk = ''
    try:
        pathchk = Path(keywdir).joinpath('02_RUNSPEC')

    except Exception:
        patherr = True
        return patherr

    if pathchk.exists():
        patherr = False
    else:
        patherr = True

    return patherr


def keyw_get_file(key):
    """ Get File Name for Keyword

    The function displays Popup and Window to get the INCLUDE and LOAD files and to set the file format for the
    the file

    Parameters
    ----------
    key : str
        OPM Flow keyword

    Returns
    -------
    event : str
        Set to Cancel if Popup window is cancelled
    file : str
        The file name in the desired format or None if the Popup was cancelled

    """

    if key == 'INCLUDE':
        file = sg.popup_get_file('Select ' + key + ' File to be Included',
                               no_titlebar=False, grab_anywhere=False, keep_on_top=True)
        if file is not None:
            filebase1 = Path(file).name
            filebase2 = '../' + str(Path(file).name)
            filebase3 = file
            layout1 = [
                [sg.Text('Select ' + key + ' File Format')],
                [sg.Listbox(values=[filebase1, filebase2, filebase3], size=(120, 3), default_values=filebase1,
                            key='_file_')],
                [sg.Submit(), sg.Cancel()]]

            window2 = sg.Window('Generate Schedule Date Keywords', layout=layout1,
                                no_titlebar=False, grab_anywhere=False, keep_on_top=True)
            (event, values) = window2.read()
            window2.Close()
            if event == 'Submit':
                file = "'" + str(values['_file_'][0]) + "'"

            if event == 'Cancel':
                file = None

        else:
            file = None
            event = 'Cancel'
    #
    # Get LOAD File
    #
    elif key == 'LOAD':
        file = sg.popup_get_file('Select ' + key + ' File to be Loaded',
                               no_titlebar=False, grab_anywhere=False, keep_on_top=True)
        if file is not None:
            event = 'Submit'
            file = "'" + str(Path(file).stem) + "'"

        else:
            file = None
            event = 'Cancel'

    else:
        file = None
        event = 'Submit'

    return event, file


def keyw_get_items(key):
    """ Gets Additional Information for a Given Keyword

    Displays a dialog Window to get the Section Keyword Options Date Parameters etc. that are substituted back into the
    Velocity Template keyword file

    Parameters
    ----------
    key :str
        OPM Flow keyword

    Returns
    -------
    keyitems : dict
        A dictionary of options to be used in the Velocity Template for the keyword
    """
    #
    # Setup Dictionary Items
    #
    keyitems = dict()
    keyitems['ans']      = 'No'
    keyitems['comment']  = ''
    keyitems['filepath'] = None
    keyitems['filename'] = None
    keyitems['sumopt01'] = 'No'
    keyitems['sumopt02'] = 'No'
    keyitems['sumopt03'] = 'No'
    keyitems['sumopt04'] = 'No'
    keyitems['sumopt05'] = 'No'
    keyitems['sumopt06'] = 'No'
    keyitems['sumopt07'] = 'No'
    keyitems['sumopt08'] = 'No'
    keyitems['sumopt09'] = 'No'
    keyitems['sumopt10'] = 'No'
    keyitems['sumopt11'] = 'No'
    keyitems['sch']      = None
    keyitems['step']     = None
    keyitems['yearstr']  = None
    keyitems['yearend']  = None
    keyheadr = ['HEADER-INCLUDE', 'HEADER-LONG', 'HEADER-SHORT']
    keysectn = ['RUNSPEC', 'GRID', 'EDIT', 'PROPS', 'SOLUTION']
    #
    # COMMENT Keyword Processing
    #
    if key == 'COMMENT':
        keyitems['comment'] = sg.popup_get_text('Enter ' + key + ' Text',
                                              no_titlebar=False, grab_anywhere=False, keep_on_top=True)
        if keyitems['comment'] is None:
            keyitems['comment'] = ''

        return keyitems
    #
    # TSTEP Keyword Processing
    #
    if key == 'TSTEP':
        keyitems['ans'] = sg.popup('Select ' + key + ' Step Option \n', custom_text=('Monthly', 'Quarterly'),
                                   no_titlebar=False, grab_anywhere=False, keep_on_top=True)
        return keyitems
    #
    #
    # HEADER File Processing
    #
    if key in keyheadr:
        filename = sg.popup_get_file('Save ' + key + ' to File', save_as=True, initial_folder=str(Path().absolute()),
                                   default_path=str(Path().absolute()),
                                   file_types=[('OPM', ['*.data', '*.DATA']), ('All', '*.*')],
                                   no_titlebar=False, grab_anywhere=False, keep_on_top=True)
        try:
            keyitems['filename'] = Path(filename).name
            keyitems['filepath'] = Path(filename).parent

        except Exception:
            keyitems['filename'] = ''
            keyitems['filepath'] = ''

        keyitems['ans'] = sg.popup_yes_no('Do You Wish to Include the OPM License for the ' + key + ' Header?',
                                        no_titlebar=False, grab_anywhere=False, keep_on_top=True)
        return keyitems
    #
    # Ask if SECTION Keywords Should be Generated
    #
    if key in keysectn:
        keyitems['ans'] = sg.popup_yes_no('Do You Wish to Generate the Standard Keywords for the ' + key + ' Section?',
                                        no_titlebar=False, grab_anywhere=False, keep_on_top=True)
        if keyitems['ans'] == 'No':
            return keyitems

    #
    # Generate SCHEDULE Section Date Keywords
    #
    if key == 'SCHEDULE':
        keyitems['yearstr'] = 2000
        keyitems['yearend'] = 2020
        keyitems['ans']     = 'No'
        keyitems['sch']     = 'No'
        keyitems['step']    = 'Monthly'
        #
        # Standard Keywords
        #
        keyitems['ans'] = sg.popup_yes_no('Do You Wish to Generate ' + key + ' Section Standard Keywords?',
                                        no_titlebar=False, grab_anywhere=False, keep_on_top=True)
        #
        # Date Keywords
        #
        keyitems['sch'] = sg.popup_yes_no('Do You Wish to Generate ' + key + ' Section Date Keywords?',
                                        no_titlebar=False, grab_anywhere=False, keep_on_top=True)
        if keyitems['sch'] == 'Yes':
            layout1 = [
                [sg.Text('Generate ' + key + ' Section Date Keywords Parameters')],
                [sg.Text('')],
                [sg.Text('Start Year', size=(14, None)), sg.InputText(keyitems['yearstr'], key='_yearstr_')],
                [sg.Text('End Year', size=(14, None)), sg.InputText(keyitems['yearend'], key='_yearend_')],
                [sg.Radio('Annual Report and Time Steps', 'bRadio', key='_annual_')],
                [sg.Radio('Annual Report and Quarterly Time Steps', 'bRadio', key='_quarter_')],
                [sg.Radio('Annual Report and Monthly Time Steps', 'bRadio', key='_month_', default=True)],
                [sg.Submit(), sg.Cancel()]]

            window2 = sg.Window('Generate Schedule Date Keywords', layout=layout1,
                                no_titlebar=False, grab_anywhere=False, keep_on_top=True)
            (event, values) = window2.read()
            window2.Close()

            if event == 'Submit':
                keyitems['sch']     = 'Yes'
                keyitems['yearstr'] = int(values['_yearstr_'])
                keyitems['yearend'] = int(values['_yearend_'])
                if values['_annual_']:
                    keyitems['step'] = 'Annual'

                if values['_quarter_']:
                    keyitems['step'] = 'Quarterly'

                if values['_month_']:
                    keyitems['step'] = 'Monthly'
    #
    # Generate SCHEDULE Section Date Keywords
    #
    if key == 'SUMMARY':
        layout1 = [
            [sg.Text('Generate ' + key + ' Section Date Keywords Parameters')],
            [sg.Checkbox('API and Tracer Tracking'         , key='_sumopt01_')],
            [sg.Checkbox('Aquifer (Analytical) Variables'  , key='_sumopt02_')],
            [sg.Checkbox('Aquifer (Numerical) Variables'   , key='_sumopt03_')],
            [sg.Checkbox('Brine Variables'                 , key='_sumopt04_')],
            [sg.Checkbox('Foam Variables'                  , key='_sumopt05_')],
            [sg.Checkbox('Multi-Segment Wells Variables'   , key='_sumopt06_')],
            [sg.Checkbox('Polymer Variables'               , key='_sumopt07_')],
            [sg.Checkbox('Simulation Performance Variables', key='_sumopt08_')],
            [sg.Checkbox('Solvent Variables'               , key='_sumopt09_')],
            [sg.Checkbox('Standard Production and Injection Summary Variables', True, key='_sumopt10_')],
            [sg.Checkbox('Thermal Variables'               , key='_sumopt11_')],
            [sg.Submit(), sg.Cancel()]]

        window2 = sg.Window('Generate Summary Date Keywords', layout=layout1,
                            no_titlebar=False, grab_anywhere=False, keep_on_top=True)
        (event, values) = window2.read()
        window2.Close()

        if event == 'Submit':
            if values['_sumopt01_']:
                keyitems['sumopt01'] = 'Yes'
            if values['_sumopt02_']:
                keyitems['sumopt02'] = 'Yes'
            if values['_sumopt03_']:
                keyitems['sumopt03'] = 'Yes'
            if values['_sumopt04_']:
                keyitems['sumopt04'] = 'Yes'
            if values['_sumopt05_']:
                keyitems['sumopt05'] = 'Yes'
            if values['_sumopt06_']:
                keyitems['sumopt06'] = 'Yes'
            if values['_sumopt07_']:
                keyitems['sumopt07'] = 'Yes'
            if values['_sumopt08_']:
                keyitems['sumopt08'] = 'Yes'
            if values['_sumopt09_']:
                keyitems['sumopt09'] = 'Yes'
            if values['_sumopt10_']:
                keyitems['sumopt10'] = 'Yes'

        else:
            keyitems['sumopt09'] = 'No'

    return keyitems


def keyw_get_keywords(keywdir, keysection, keywords, keyall, keyfiles):
    """Searches a Template Directory and Generates a Keyword List from the Template Files

    This function searches the template directories and makes a dictionary list of both the templates and keywords

    Parameters
    ----------
    keywdir : str
        Template directory to search for keyword template files
    keysection : str
        OPM Flow section keyword (RUNSPEC, GRID, etc.)
    keywords : list
        List of OPM Flow keywords
    keyall : list
        List of all current keywords
    keyfiles : list
        List of all keyword templates files

    Returns
    -------
    keywords : list
        List of OPM Flow keywords
    keyall : list
        List of all current keywords
    keyfiles : list
        List of all keyword templates files
   """

    keyfile = dict()
    for keyobj in list(Path(keywdir).glob('*')):
        if keyobj.is_dir():
            if keysection in str(keyobj):
                keyfile[keysection] = list(Path(keyobj).glob('*.vm'))
                keylist = []
                for key in keyfile[keysection]:
                    keyword = Path(key).stem
                    keylist.append(keyword)
                    keyall.append(keyword)
                    keyfiles[keyword] = key

                keywords[keysection] = keylist


def keyw_save_keywords(text):
    """Save Displayed Keywords to File

    Saves the displayed keyword text to a file selected by the user

    Parameters
    ----------
    text : str
        A block of text containing the displayed keywords

    Returns
    -------
    None
    """

    filename = sg.popup_get_file('Save Keywords to File', save_as=True, default_path=str(Path().absolute()),
                               no_titlebar=False, grab_anywhere=False, keep_on_top=True,
                               file_types=[('OPM', ['*.data', '*.DATA']), ('All', '*.*')])
    if filename is None:
        sg.popup_ok('Save Keywords to File Cancelled',
                   no_titlebar=False, grab_anywhere=False, keep_on_top=True)
        return ()

    file = open(filename, 'w')
    file.write(text)
    file.close()
    sg.popup_ok('Keywords Saved to: ' + filename,
               no_titlebar=False, grab_anywhere=False, keep_on_top=True)


def keyw_main(opmvers, **opmoptn):
    """OPMRUN Keyword Generation Utility

    OPM Flow Keyword Generation Utility is a Graphical User Interface ("GUI") program for the Open Porous Media ("OPM")
    Flow simulator

    This module generates input decks based of the keywords available for the simulator and users the Apache Velocity
    Template Language ("VTL") for the templates. VTL is a common templating language used by many programming editors,
    and therefore the templates can also be used directly with an editor provided the editor supports VTL. The Python
    airspeed module is used to parse the templates and the key templates are comparable to the examples depicted in the
    OPM Flow Manual.

    This is the main display GUI module for the OPM Keyword Generator program. The window object, window1, is the main
    global window object for other routines to access in this module.

    Parameters
    ----------
    opmvers; str
        The version of OPMRUN currently running
    opmoptn; dict
        A dictionary containing the OPMRUN default parameters

    Returns
    -------
    Nothing
    """

    #
    # Initialize
    #
    opm_initialize()
    keywdir = opmoptn['opm-keywdir']
    patherr = keyw_check_directory(keywdir)

    if patherr:
        keywdir = Path(Path().absolute()).joinpath('opmvtl')
        patherr = keyw_check_directory(keywdir)

        if patherr:
            sg.popup_error('Error in "keyw_main" Module \n',
                          'Cannot Find Keyword Template Directory: \n \n' + str(keywdir) + '\n',
                          'Please Set Keyword Template Directory',
                          no_titlebar=False, grab_anywhere=False, keep_on_top=True)

            keywdir = sg.popup_get_folder('Set Keyword Template Directory', default_path=str(Path().absolute()),
                                        initial_folder=str(Path().absolute()),
                                        no_titlebar=False, grab_anywhere=False, keep_on_top=True)
            #
            # Process Cancel with Return to OPMRUN Main
            #
            if keywdir is None:
                return ()
            #
            # Process Directory
            #
            patherr = keyw_check_directory(keywdir)
            if patherr:
                sg.popup_error('Error in "keyw_main" Module RUNSPEC Directory Missing: \n ',
                              str(keywdir) + '\n',
                              'Does Not Contain Template Directories - Process Stopped',
                              no_titlebar=False, grab_anywhere=False, keep_on_top=True)
                return ()


    opmoptn['opm-keywdir'] = keywdir
    sg.popup_ok('Using Keyword Template Directory \n \n' + str(keywdir) + '\n ',
               no_titlebar=False, grab_anywhere=False, keep_on_top=True)

    filetype = 'OPM FLOW SIMULATION FILE'
    helptext = (
            'OPM Flow Input Keyword Generation Utility is a Graphical User Interface ("GUI") program for the '
            'Open Porous Media ("OPM") Flow simulator \n' +
            '\n'
            'This module generates input decks based of the keywords available for the simulator and users the ' +
            'Apache Velocity Template Language ("VTL") for the templates. VTL is a common templating language ' +
            'used by many programming editors, and therefore the templates can also be used directly with an ' +
            'editor provided the editor supports VTL. The Python airspeed module is used to parse the templates ' +
            'and the key templates are comparable to the examples depicted in the OPM Flow Manual. \n'
            '\n'
            'The "Keyword Filter" button allows for the filtering of the various keywords in the selected ' +
            'section, including being able to list all the keywords available for all sections. Clicking on a ' +
            'keyword will result in the keyword being "pasted" into the Deck element. This element is editable ' +
            'by simply clicking anywhere in the element and making changes. \n'
            '\n'
            'The "Clear" button will will clear the Deck element of all text, and the "Copy" button will copy ' +
            'the text in the Deck element to the clipboard from which you can paste the text in your chosen  ' +
            'editor. The text can also be save saved to a file by selecting the "Save" button \n' +
            '\n'
            'See the OPM Flow manual for further information. \n')
    helptemp = (
            'Velocity Template Language \n' +
            '\n'
            'The Velocity Template Language (VTL) is used to embed dynamic elements within what would otherwise ' +
            'be static templates. By using VTL it is possible to interact with the user, calculate values, ' +
            'incorporate conditional logic, and much more. \n' +
            '\n' +
            'Directives \n' +
            'Directives are script elements in the Velocity Template Language that can be used to manipulate ' +
            'the output generated by the Velocity engine.Brief summaries of the standard VTL directives are ' +
            'included below. For a more detailed description, refer to the Velocity User Guide on the Apache ' +
            'website. \n' +
            '\n' +
            'Comment Directive \n' +
            'Like most programming languages, VTL includes constructs for inserting descriptive text comments ' +
            'into a template.Both single-line and multi-line (block) comments are supported. A single - line ' +
            'comment starts with  ## and only lasts until the end of the line. The following are examples of ' +
            'single-line comments: \n' +
            '\n' +
            '                            This is not a comment.  ## This is a comment \n' +
            '                            ## This whole line is a comment \n' +
            '\n' +
            'Multi-line comments are indicated by a start (  # *) and end comment indicator (*#). ' +
            'For example: \n' +
            '\n' +
            '                           This text is outside of the comment block.It will be processed by the \n' +
            '                           template engine \n' +
            '                           #* \n' +
            '                              This text is inside the comment block \n' +
            '                              Therefore it will be ignored by the template engine \n' +
            '                           *# \n' +
            '                           Back outside the comment block.This text will be processed \n' +
            '\n' +
            'Set Directive (#set) \n' +
            'One  of the most basic VTL directives is the  # set directive. It is used to assign a value to ' +
            'either a variable reference or a property reference. For example, the following are all valid  ' +
            '# set statements: \n' +
            '\n' +
            '                          $set ($ANS = "Yes") \n' +
            '                          #srt ($YearStart = 2020) \n' +
            '\n' +
            'Conditional Directives(#if/#elseif/#else) \n' +
            'Velocity allows for the optional inclusion of text through the use of the conditional  #if ' +
            'directive. The statement is considered true if it is passed; that is a boolean variable whose ' +
            'value is true, an expression which evaluates to true, and an object which is not null. The ' +
            'following code illustrates these three cases: \n' +
            '\n' +
            '                          #set ( $test = "true" )                           ## boolean variable \n' +
            '                          #if ( $test ) \n' +
            '                          This text is processed. \n' +
            '                          #end \n' +
            '\n' +
            '                          #if ($Year < $YearEnd)                            ## boolean expression \n' +
            '                          $Year = $Year + 1 \n' +
            '                          #end \n' +
            '\n' +
            '                          #set ( $ANS = "Yes") \n' +
            '                          #if ( $Ans )                                       ## non-null object \n' +
            '                          This text is processed. \n' +
            '                          #end \n' +
            '\n' +
            'In addition, Velocity supports the logical AND ( & &), OR( | |) and NOT(!) operators, as well as ' +
            'standard relational operators  such as equivalence( ==), greater than( >) and less than( <). Refer ' +
            'to the Velocity User"s Guide for more information. \n' +
            '\n' +
            'Loop Directive (# foreach) \n' +
            'The #foreach directive provides a way to loop over a template segment once for each object in a ' +
            'list of objects. For example, the following template code: \n' +
            '\n' +
            '                          #foreach ( $Year in [$YearStart .. $YearEnd] ) \n' +
            '                          RPTSCHED \n' +
            '                          WELLS=2     WELSPECS      CPU=2      FIP=2                        /\n' +
            '\n' +
            '                          DATES \n' +
            '                          1  JAN   $Year  / \n' +
            '                          / \n' +
            '\n' +
            'Include Directive (#include) \n' +
            'The # include directive is used to import a local file at the location where the #include ' +
            'directive is encountered. The contents of the file are not parsed by the template engine, but just ' +
            'included, for example: \n' +
            '\n' +
            '                          #include ("WCONPROD.vm") \n' +
            '                          #include ("WCONINJE.vm") \n' +
            '\n' +
            'Parse Directive (#parse) \n' +
            'The #parse directive is similar to the #include directive, but rather than importing a static text ' +
            'file, the imported file is also parsed by the template engine, for example: \n' +
            '\n' +
            '                          #include ("SCHEDULE.vm") \n' +
            '\n' +
            'Will parse all the directives in the SCHEDULE.vm template \n' +
            '\n' +
            'Stop Directive (#stop) \n' +
            'The #stop directive will halt template processing by the template engine. This is useful for ' +
            'debugging during template design. \n' +
            '\n' +
            'Macro Directive (#macro) \n' +
            'The #macro directive provides an easy method of defining repeated segments in a template. Here is ' +
            'a simple example: \n' +
            '\n' +
            '                          #macro (datemacro) \n' +
            '                          This a Test Macro \n' +
            '                          #end \n' +
            'The call to macro is: \n' +
            '                          datemacro \n' +
            '                          datemacro \n' +
            '\n')
    #
    #  Print opmoptn dictionary if Requested
    #
    debug = False
    if debug:
        print_dict('opmoptn', opmoptn, option='debug')
    #
    # Get Keyword Templates
    #
    keyall   = []
    keyfiles = dict()
    keylist  = []
    keywords = dict()

    keyw_get_keywords(keywdir, 'HEADER'  , keywords, keylist, keyfiles)
    keyw_get_keywords(keywdir, 'GLOBAL'  , keywords, keylist, keyfiles)
    keyw_get_keywords(keywdir, 'RUNSPEC' , keywords, keylist, keyfiles)
    keyw_get_keywords(keywdir, 'GRID'    , keywords, keylist, keyfiles)
    keyw_get_keywords(keywdir, 'EDIT'    , keywords, keylist, keyfiles)
    keyw_get_keywords(keywdir, 'PROPS'   , keywords, keylist, keyfiles)
    keyw_get_keywords(keywdir, 'SOLUTION', keywords, keylist, keyfiles)
    keyw_get_keywords(keywdir, 'SUMMARY' , keywords, keylist, keyfiles)
    keyw_get_keywords(keywdir, 'SCHEDULE', keywords, keylist, keyfiles)

    if debug:
        print_dict('keyfiles', keyfiles, option='debug')
    #
    # Make ALL Keyword List
    #
    keylist.sort()
    keywords['ALL'] = list(keylist)
    #
    # Get DATA, Models and USER Keyword List
    #
    keyw_get_keywords(keywdir, 'DATA'  , keywords, keylist, keyfiles)
    keyw_get_keywords(keywdir, 'MODELS', keywords, keylist, keyfiles)
    keyw_get_keywords(keywdir, 'USER'  , keywords, keylist, keyfiles)
    if debug:
        print_dict('keyfiles', keyfiles, option='debug')
    #
    # Set Initial Keyword List to Display
    #
    keylist = 'GLOBAL'
    #
    # Define Display Window
    #
    mainwind = [
        [sg.Button('Filter' , size=(16, None), key='_filter_'),
         sg.Radio('HEADER'  , 'optn01', key='_header_'),
         sg.Radio('GLOBAL'  , 'optn01', key='_global_', default=True),
         sg.Radio('RUNSPEC' , 'optn01', key='_runspec'),
         sg.Radio('GRID'    , 'optn01', key='_grid_'),
         sg.Radio('EDIT'    , 'optn01', key='_edit_'),
         sg.Radio('PROPS'   , 'optn01', key='_props_'),
         sg.Radio('SOLUTION', 'optn01', key='_solution_'),
         sg.Radio('SUMMARY' , 'optn01', key='_summary_'),
         sg.Radio('SCHEDULE', 'optn01', key='_schedule_'),
         sg.Radio('ALL'     , 'optn01', key='_all_')],

        [sg.Text('', size=(19, None)),
         sg.Radio('DATA'  , 'optn01', size=(8, None), key='_data_'),
         sg.Radio('MODELS', 'optn01', key='_models_'),
         sg.Radio('USER'  , 'optn01', key='_user_')],

        [sg.Listbox(values=keywords[keylist], size=(18, 40), font=('Courier', 9),
                    right_click_menu=['Template', ['Template', 'Template Help']],
                    enable_events=True, key='_keylist_'),
         sg.Multiline(size=(132, 40), font=('Courier', 9), do_not_clear=True, key='_deckinput_')],

        [sg.Text('')],

        [sg.Button('Clear', key='_clear_'),
         sg.Button('Copy' , key='_copy_' ),
         sg.Button('Help' , key='_help_' ),
         sg.Button('Save' , key='_save_' ),
         sg.Exit()]
    ]

    window1 = sg.Window('OPMRUN Keyword Generation Utility', no_titlebar=False, grab_anywhere=False,
                        layout=mainwind, finalize=True)
    #
    #   Define GUI Event Loop, Read Buttons, and Make Callbacks etc. Section
    #
    while True:
        #
        # Read the Window and Process
        #
        event, values = window1.read()
        if debug:
            sg.Print('Buttons')
            sg.Print(event)
            sg.Print('Values')
            sg.Print(values)
        #
        # Get Main Window Location and Set Default Location for other Windows
        #
        #        x = int((window0.Size[0] / 2) + window0.CurrentLocation()[0])
        #        y = int((window0.Size[1] / 4) + window0.CurrentLocation()[1])
        #        sg.SetOptions(window_location=(x, y))
        #
        # Clear
        #
        if event == '_clear_':
            window1['_deckinput_'].update('')
            continue
        #
        # Copy
        #
        elif event == '_copy_':
            copy_to_clipboard(window1['_deckinput_'].get())
            sg.popup_timed('Deck Copied to Clipboard', no_titlebar=False, grab_anywhere=False, keep_on_top=True)
            continue
        #
        # Exit
        #
        elif event == 'Exit':
            text = sg.popup_yes_no('Exit Keyword Generation?',
                                   no_titlebar=False, grab_anywhere=False, keep_on_top=True)
            if text == 'Yes':
                break
            else:
                continue
        elif event == sg.WIN_CLOSED:
            break
        #
        # File Name
        #
        elif event == '_deckfile_':
            continue
        #
        # Help
        #
        elif event == '_help_':
            opm_popup('Keyword Generator Help', helptext, 22)
            continue
        #
        # Keywords
        #
        elif event == '_keylist_':
            if not values['_keylist_']:
                continue

            key = str(values['_keylist_'][0])
            tempdirc = Path(keyfiles[key]).parents[0]
            tempkey  = Path(keyfiles[key]).name
            if debug:
                sg.Print(key)
                sg.Print(keyfiles[key])
                sg.Print(tempdirc)
                sg.Print(tempkey)
            #
            # Keyword
            #
            templates = airspeed.CachingFileLoader(tempdirc)
            template  = templates.load_template(tempkey)
            #
            # Process Keyword Options
            #
            keyitems = keyw_get_items(key)
            (status, file) = keyw_get_file(key)
            if status == 'Cancel':
                continue

            if debug:
                print_dict('opmoptn', opmoptn, option='debug')

            date = datetime.now().strftime('%d-%b-%Y')
            time = datetime.now().strftime('%H:%M:%S')
            try:
                window1['_deckinput_'].update(template.merge({'FileType' : filetype,
                                                                      'Date'     : str(date),
                                                                      'Time'     : str(time),
                                                                      'OSName'   : platform.system(),
                                                                      'OSLevel'  : platform.release(),
                                                                      'OSArch'   : platform.machine(),
                                                                      'Ans'      : keyitems['ans'],
                                                                      'Author1'  : opmoptn ['opm-author1'],
                                                                      'Author2'  : opmoptn ['opm-author2'],
                                                                      'Author3'  : opmoptn ['opm-author3'],
                                                                      'Author4'  : opmoptn ['opm-author4'],
                                                                      'Author5'  : opmoptn ['opm-author5'],
                                                                      'Comment'  : keyitems['comment'    ],
                                                                      'File'     : file,
                                                                      'FileName' : keyitems['filename'   ],
                                                                      'FilePath' : keyitems['filepath'   ],
                                                                      'SumOpt01' : keyitems['sumopt01'   ],
                                                                      'SumOpt02' : keyitems['sumopt02'   ],
                                                                      'SumOpt03' : keyitems['sumopt03'   ],
                                                                      'SumOpt04' : keyitems['sumopt04'   ],
                                                                      'SumOpt05' : keyitems['sumopt05'   ],
                                                                      'SumOpt06' : keyitems['sumopt06'   ],
                                                                      'SumOpt07' : keyitems['sumopt07'   ],
                                                                      'SumOpt08' : keyitems['sumopt08'   ],
                                                                      'SumOpt09' : keyitems['sumopt09'   ],
                                                                      'SumOpt10' : keyitems['sumopt10'   ],
                                                                      'SumOpt11' : keyitems['sumopt11'   ],
                                                                      'Option'   : keyitems['step'       ],
                                                                      'Schedule' : keyitems['sch'        ],
                                                                      'YearStart': keyitems['yearstr'    ],
                                                                      'YearEnd'  : keyitems['yearend'    ]},
                                                                     loader=templates),
                                                      append=True, autoscroll=True)
            except Exception as error:
                sg.popup_error('Error Processing Keyword Template: ' + str(key) + '\n  \n' + str(error),
                              no_titlebar=False, grab_anywhere=False, keep_on_top=True)
            continue
        #
        # Keyword Filter
        #
        elif event == '_filter_':
            if values['_header_']:
                window1['_keylist_'].update(keywords['HEADER'])

            if values['_global_']:
                window1['_keylist_'].update(keywords['GLOBAL'])

            if values['_runspec']:
                window1['_keylist_'].update(keywords['RUNSPEC'])

            if values['_grid_']:
                window1['_keylist_'].update(keywords['GRID'])

            if values['_edit_']:
                window1['_keylist_'].update(keywords['EDIT'])

            if values['_props_']:
                window1['_keylist_'].update(keywords['PROPS'])

            if values['_solution_']:
                window1['_keylist_'].update(keywords['SOLUTION'])

            if values['_summary_']:
                window1['_keylist_'].update(keywords['SUMMARY'])

            if values['_schedule_']:
                window1['_keylist_'].update(keywords['SCHEDULE'])

            if values['_all_']:
                window1['_keylist_'].update(keywords['ALL'])

            if values['_data_']:
                window1['_keylist_'].update(keywords['DATA'])

            if values['_models_']:
                window1['_keylist_'].update(keywords['MODELS'])

            if values['_user_']:
                window1['_keylist_'].update(keywords['USER'])

            continue
        #
        # Save
        #
        elif event == '_save_':
            keyw_save_keywords(window1['_deckinput_'].get())
            continue
        #
        # Template
        #
        elif event == 'Template':
            key = None
            try:
                key = str(values['_keylist_'][0])
                tempname = Path(keyfiles[key])
                tempfile = open(tempname, "r")
                window1['_deckinput_'].update('')
                window1['_deckinput_'].update(tempfile.read())
                tempfile.close()
            except Exception as error:
                sg.popup_error('Error Displaying Velocity Template Source: ' + str(key) + '\n  \n' + str(error),
                              no_titlebar=False, grab_anywhere=False, keep_on_top=True)
                continue
            continue
        #
        # Template Help
        #
        #
        elif event == 'Template Help':
            opm_popup('Keyword Generator Template Help', helptemp, 22)
            continue
    #
    # Define Post Processing Section
    #
    ans = sg.popup_yes_no('Do You Wish to Save the Keyword to File?',
                        no_titlebar=False, grab_anywhere=False, keep_on_top=True)
    if ans == 'Yes':
        keyw_save_keywords(window1['_deckinput_'].get())

    window1.Close()
    sg.popup_ok('Keyword Generation Processing Complete',
               no_titlebar=False, grab_anywhere=False, keep_on_top=True)

# ======================================================================================================================
# End of OPMKEYW
# ======================================================================================================================
