#===================================================================================================================================
#
'''
OPMRUN.py - Run OPM Flow


The program allows the user to select files to be submitted to OPM Flow and has a variety of features.

Program Documentation
--------------------
2019-04-01 - Fixed bug in running parallel jobs.
           - Added functionality to kill a running job, and disable certain buttons when jobs are running.
           - Fixed printing bug when OPM Flow terminates with errors.
           - Added windows dialog sizes to OPMRUN.ini file so that user can change the windows size at next re-start.
           - Moved pre-processing code to separate module for code readability (after suggestion by Joakim Hove).
           - Upgraded to PySimpleGUI 3.36.0.
           - Disable X close button or check for None.
           - Added option to Edit OPMRUN options.
           - When adding a job clear the file name field after the job has been added to the queue.
           - Added Compress Jobs and Uncompress Jobs to the Tools menus.
           - Added ResInsight option to the Tools menu.
           - Added option to clear the output and log elements.
           - For the Add Job dialog list the number of CPUs available; previously the range went from one to 64. Also
             implemented multiple job selection.
           - Added projects as shortcut to project directories.
           - Added option to run job queue in foreground (that is under OPMRUN) and background via xterm (should be
             computationally more efficient).
           - Major re-factoring of code and code clean up.
           - Create stand alone executable for Linux systems (works on Unbuntu-Mate 18-04)
           
2018-10-02 - Fix printing bug associated with listing of jobparm.
             Create stand alone executable for Linux systems (works on Unbuntu-Mate 18-04)
             
2018-10-01 - Initial release.

To Do List
----------
(1) Add a status tab to the bottom element with a table showing the project name, job name start time and end time,
    and job status (Aborted, Completed, Killed, Running, etc.)
(2) Add right-click menu options to the status table to edit files, view results, load results into ResInsight, etc.
(3) Write job status files to update status table for both foreground and background jobs.

Compiling Source
----------------
It's possible to create a single .EXE file that can be distributed to Linux users. There is no requirement to install
the Python interpreter on the PC you wish to run it on. Everything it needs is in the one EXE file, assuming you're
running a somewhat up to date version of Linux.

Installation of the packages, you'll need to install PySimpleGUI and PyInstaller (you need to install only once)

       pyinstaller --clean --onefile OPMRUN.py

You will be left with a single file, OPMRUN.bin, located in a folder named dist under the folder where you executed
the pyinstaller command. OPMRUN file should run without creating a "terminal window". Only the GUI window should show up.

Note there are other tools for compiling Python code; however, PyInstaller’s main advantages over similar tools are that
PyInstaller works with Python 2.7 and 3.4—3.7, it builds smaller executables thanks to transparent compression,
it is fully multi-platform, and use the OS support to load the dynamic libraries, thus ensuring full compatibility.
See https://www.pyinstaller.org/ for further information

Copyright Notice
----------------
This file is part of the Open Porous Media project (OPM).

OPM is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

OPM is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the aforementioned GNU General Public Licenses for more details.

Copyright (C) 2018-2019 Equinor
Copyright (C) 2018-2019 Equinox International Petroleum Consultants Pte Ltd.

Author  : David Baxendale
          david.baxendale@eipc.co 
Version : 1.0
Date    : 03-Nov-2018
          Copyright (C) 2018 David Baxendale         
'''
#-----------------------------------------------------------------------------------------------------------------------------------
# 3456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012
#        1         2         3         4         5         6         7         8         9         0         1         2         3
#        0         0         0         0         0         0         0         0         0         1         1         1         1
#-----------------------------------------------------------------------------------------------------------------------------------

#-----------------------------------------------------------------------------------------------------------------------------------
# Import Modules Section 
#-----------------------------------------------------------------------------------------------------------------------------------
import PySimpleGUI as sg
import datetime
import getpass
import os
import sys
import psutil
import re
import subprocess
from   pathlib  import Path

if sys.version_info[0] >= 3:
    import PySimpleGUI as sg
else:
    import PySimpleGUI27 as sg
    
#-----------------------------------------------------------------------------------------------------------------------------------
# Define Constants Section 
#----------------------------------------------------------------------------------------------------------------------------------- 
joblist  = []
jobparam = []
jobhelp  = dict()

opmoptn  = dict()
opmvers  = '2019-04.01'
opm      = Path.home()
opmhome  = Path(opm  / 'OPM')
if not opmhome.is_dir():
    opmhome.mkdir()
    
opmini   = Path(opmhome / 'OPMRUN.ini')
opmrun   = Path(opmhome / 'OPMRUN.que')
opmfile  = Path(opmhome / 'OPMRUN.log')
opmjob   = Path(opmhome / 'OPMRUN.job')
opmlog   = open(opmfile,'w')

opmparam = Path(opmhome / 'OPMRUN.param')

opmuser  = getpass.getuser()

sg.SetOptions(icon=None,      
        button_color=('green','white'),      
        element_size=(None,None),      
        margins=(None,None),      
        element_padding=(None,None),      
        auto_size_text=None,      
        auto_size_buttons=None,      
        font=None,      
        border_width=None,      
        slider_border_width=None,      
        slider_relief=None,      
        slider_orientation=None,      
        autoclose_time=None,      
        message_box_line_width=None,      
        progress_meter_border_depth=None,      
        progress_meter_style=None,      
        progress_meter_relief=None,      
        progress_meter_color=None,      
        progress_meter_size=None,      
        text_justification=None,     
        text_color=None,      
        background_color=None,      
        element_background_color=None,      
        text_element_background_color=None,      
        input_elements_background_color=None ,     
        element_text_color='green',      
        input_text_color=None,      
        scrollbar_color=None,      
        debug_win_size=(None,None),      
        window_location=(None,None),      
        tooltip_time = None
        )

abouttext = ('OPMRun is a Grapical User Interface ("GNU") program for the Open Porous Media ("OPM") Flow simulator .\n' +
             '\n'
             'The software enables submiting OPM Flow simulation input decks together with editing of the associated ' +
             'PARAM file \n' +
             '\n' +
             'This file is part of the Open Porous Media project (OPM). OPM is free software: you can redistribute ' +
             'it and/or modify it under the terms of the GNU General Public License as published by the Free ' +
             'Software Foundation, either version 3 of the License, or (at your option) any later version. \n' +
             '\n' +
             'OPM is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the ' +
             'implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the aforementioned ' +
             'GNU General Public Licenses for more details. \n' +
             '\n' +
             'Copyright (C) 2018-2019 Equinor \n'
             'Copyright (C) 2018-2019 Equinox International Petroleum Consultants Pte Ltd. \n'
             '\n' +
             'Author  : David Baxendale (david.baxendale@eipc.co)') 

helptext = ('OPMRun is a Grapical User Interface ("GUI") program for the Open Porous Media ("OPM") Flow simulator \n'  +
             '\n'
             'The intent is for OPMRUN to have similar functionality to the commercial simulator’s program, with the ' +
             'targeted audience being Reservoir Engineers in a production environment.  Developers and experienced '   +
             'Linux users will already have compatible work flows.  OPMRUN enables the editing and management of '     +
             'OPM Flow’s run time parameters, setting up job queues to run a series of simulation jobs sequentially, ' +
             ' as well as the management of the job queues. Features include: \n'                                      +
             '\n'
             'Projects allow setting "default" directories to enable shortcuts to frequent directories for selecting ' +
             'input decks and job queues. \n'                                                                          +     
             '\n'
             'Input decks can be added to a job queue for processing and the input deck and the associated parameter ' +
             'file can be edited. The input deck is edited via a user selected editor and the parameter file is '      +
             'edited interactively in OPMRUN. \n'                                                                      +
             '\n'
             'Default parameters can be loaded from OPM Flow, an existing PARAM file or a PRINT file. \n'              +
             '\n'
             'Job queues can be edited, loaded and saved, and jobs in the job queue can all be run in "NOSIM" mode '   +
             'to verify the input decks, or "RUN" mode, without editing the input decks. \n'                           +
             '\n'
             'Jobs in the job queue can be run in foreground mode under OPMRUN, or background in a xterm terminal.'    +
             'The latter is slightly more computationally efficient than the foreground mode. \n'                      +
             '\n'
             'The Tools menu allows one to compress and uncompress the DATA, PARAM and output files into one ZIP '     +
             'file to save disk space. The Tool menu also allows one to launch ResInsight. \n'                         +
             '\n'
             'Finaly, the Edit Options menu allows for editing OPMRUN options, set the OPM Flow Manual location, '     +
             'default editor command, ResInsight command etc. \n'                                                      +           
             '\n'
             'See the OPM Flow manual for further information. \n'                                                     )

#-----------------------------------------------------------------------------------------------------------------------------------
# Define Modules Section 
#-----------------------------------------------------------------------------------------------------------------------------------
def add_job(joblist,jobparam,opmuser):

    if (jobparam == []):
        sg.PopupOK('Job Parameters Missing; Cannot Add Cases - Check if OPM Flow is Installed')
        return()

    window0.Disable
    layout1 = [[sg.Text('File to Add to Queue')],    
                 [sg.InputText(key='_job_', size=(80, None)),
                  sg.FilesBrowse(target='_job_', initial_folder=os.getcwd,
                                 file_types=[('OPM', ['*.data','*.DATA']), ('All', '*.*')])],
                 [sg.Text('Run Parameters')],
                 [sg.Radio('Sequential Run' , "bRadio", default=True)],
                 [sg.Radio('Parallel Run   ', "bRadio"              ), sg.Text('No. of Nodes'),
                  sg.Listbox(values=list(range(1,psutil.cpu_count() + 1)), size=(5,3))],                
                 [sg.Submit(), sg.Cancel()]]
    window1 = sg.Window('Select OPM Flow Input File', layout= layout1)
    
    while True:
        (button, values) = window1.Read()
        jobs     = values['_job_']
        jobseq  = values[0]
        jobpar  = values[1]
        jobnode = values[2]
        if not jobnode:
            jobnode = 2

        if (button == 'Submit' and jobs != None):
            jobs = jobs.split(';')
            for job in jobs:
                jobpath = Path(job).parents[0]
                jobbase = Path(job).name
                jobfile = Path(job).with_suffix('.param')
                if jobseq:
                    joblist.append('flow --parameter-file=' + str(jobfile)) 
                if jobpar:
                    joblist.append('mpirun -np ' + str(jobnode).strip("[]") + ' flow --parameter-file=' + str(jobfile))                
                window0.Enable
                window0.Element('_joblist_').Update(joblist)
                window0.Disable
                #
                # Write Out PARAM File?
                #
                if (jobfile.is_file()):
                    text = sg.PopupYesNo('Parameter file:',
                                  str(jobfile),
                                  'Already exists; do you wish to overwite it with the current parameter defaults?',
                                  'Press YES to overwrite the file and NO to keep existing file',
                                  '',
                                  grab_anywhere=True, no_titlebar=True)
#                    if (text == 'No'):
#                        sg.PopupOK('Writing out parameter file cancelled, will use existing file instead')
                else:
                    text = 'Yes'
                    
                if (text == 'Yes'):
                    save_parameters(job, jobparam, jobbase, jobfile, opmuser)

                window1.Element('_job_').Update(value='')
                                
        elif (button == 'Cancel' or button == None):
            break
        
    window1.Close()
    window0.Enable
    return()


def clear_output():
    '''
    Clears the requested Output and Log elements in the main window.
    '''
    layout1  = [
                [sg.Radio('Clear Log Display'           , 'bRadio', key='_log_'               )],
                [sg.Radio('Clear Output Display'        , 'bRadio', key='_out_', default=True )],
                [sg.Radio('Clear Log and Output Display', 'bRadio', key='_all_'               )],
                [sg.Submit(), sg.Cancel()                                                         ]
                ]
    
    window1 = sg.Window('Clear Display Options', layout= layout1)
    (button, values) = window1.Read()
    window1.Close()    

    if (button == 'Submit'):
        if (values['_log_'] or values['_all_']):
            window0.Element('_outlog_').Update('')
            
        if (values['_out_'] or values['_all_']):    
           window0.Element('_outflow_').Update('')


def clear_queue(joblist):
    if joblist == []:
        sg.PopupOK('No Case Selected for Deletion')
    else:
        text = sg.PopupYesNo('Delete All Cases in Queue?')
        if text == 'Yes':
            joblist = []
            window0.Element('_joblist_').Update(joblist)


def compress_job():

    set_window_status(False)
    
    joblist1 = []
    layout1  = [[sg.Text('Select Multiple Job Data Files to Compress'                           )],    
                 [sg.Listbox(values='', size=(100,10), key='_joblist1_'                         )],                
                 [sg.Text('Output'                                                              )],
                 [sg.Output(key='_outlog1_', size=(100,15),font=('Courier',9) ,text_color='blue')],
                 [sg.Text('Compression Options'                                                 )],
                 [sg.Radio('Compress Job' , "bRadio", default=True                              )],
                 [sg.Radio('Compress Job and then Remove Job Files', "bRadio"                   )],
                 [sg.Button('Add'), sg.Button('List'), sg.Submit(), sg.Cancel()                  ]]
    window1 = sg.Window('Compress Job Files', layout=layout1)
    
    while True:
        (button, values) = window1.Read()
        jobopt  = values[0]
        #
        # Add Files
        #
        if button == 'Add':
            jobs= sg.PopupGetFile('Select Job Data Files to Compress', no_window=False,
                                   multiple_files=True,
                                   default_path=str(os.getcwd),
                                   file_types=[('OPM', ['*.data','*.DATA'])])
            if jobs != None:
                jobs = jobs.split(';')
                for job in jobs:
                    joblist1.append(job)
                    
                window1.Element('_joblist1_').Update(joblist1)
        #
        # Get Directory and List Files
        #
        if button == 'List':
            jobpath = sg.PopupGetFolder('Select Directory', no_window=False)
            if jobpath != None:
                set_directory(jobpath)
                print(jobpath + '\n')

            jobpath = os.getcwd()
            for file in Path(jobpath).glob("*.data"):
                print(str(Path(file).name))
                
            for file in Path(jobpath).glob('*.DATA'):  
                print(str(Path(file).name))
        #
        # Compress Files
        #
        if button == 'Submit':
            if jobopt:
                zipcmd = 'zip -uv '
            else:
                zipcmd = 'zip -mv '
                    
            for job in joblist1:
                out_log('Start Compression', opmlog, True)
                jobpath = Path(job).parents[0]
                jobbase = Path(job).name
                jobroot = Path(job).stem
                jobfile = Path(jobbase).with_suffix('.*')
                jobzip  = Path(jobbase).with_suffix('.zip')
                set_directory(jobpath)
                jobcmd = zipcmd + str(jobzip) + ' ' + str(jobfile)  
                out_log('   ' + jobcmd, opmlog, True)
                run_command(jobcmd)
                out_log('End Compression', opmlog, True)
                window1.Refresh()
                
            joblist1 = []
            window1.Element('_joblist1_').Update(joblist1)
        #
        # Cancel
        #
        if (button == 'Cancel' or button == None):
            break
        
    joblist1 = []   
    window1.Close()
    set_window_status(True)
    return()


def convert_string(string, option):
    '''
    The regular expression looks for letters that are either at the beginning of the string,
    or preceded by an underscore. The given letter is captured.
    Each of those occurences (undescore + letter) is replaced by the uppercase version of
    the found letter.
    '''
    if (option  == 'snake2camel'):
        return (re.sub(r'(?:^|_)([a-z])', lambda x: x.group(1).upper(), string))                
    '''
    This method works exactly as snake2camel, except that the first character is not
    taken into account for capitalization.
    '''
    if (option == 'snake2camelback'):
        return (re.sub(r'_([a-z])', lambda x: x.group(1).upper(), string))
    '''
    The regular expression capture every capital letters in the given string.
    For each of these groups, the character found is replaced by an underscore,
    followed by the lowercase version of the character.
    '''
    if (option  == 'camel2snake'):
        return (string[0].lower() + re.sub(r'(?!^)[A-Z]', lambda x: '_' + x.group(0).lower(), string[1:]))
    '''
    The conversion is very similar to the one performed in camelback2snake,
    except that the first character is processed out of the regular expression.
    '''
    if (option  == 'camelback2snake'):
        return (re.sub(r'[A-Z]', lambda x: '_' + x.group(0).lower(), string))
    '''
    The regular expression capture every capital letters in the given string.
    For each of these groups, the character found is replaced by a '-',
    followed by the lowercase version of the character.
    '''
    if (option  == 'camel2flow'):
        return (string[0].lower() + re.sub(r'(?!^)[A-Z]', lambda x: '-' + x.group(0).lower(), string[1:]))
    '''
    The conversion is very similar to the one performed in camelback2snake,
    except that the first character is processed out of the regular expression.
    '''
    if (option  == 'camelback2flow'):
        return (re.sub(r'[A-Z]', lambda x: '-' + x.group(0).lower(), string))


def default_parameters(jobparam,opmparam):
    
    set_window_status(False)
    
    jobparam0 = jobparam
    jobparam  = []

    layout1   = [ [sg.Text('Define OPM Flow Default Parameters for New Cases')],    
                   [sg.Radio('Load Parameters from OPM Flow '               , 'bRadio', default=True)],
                   [sg.Radio('Load Parameters from OPM Flow Parameter File' , 'bRadio'              )],
                   [sg.Radio('Load Parameters from OPM Flow Print File'     , 'bRadio'              )],
                   [sg.Text('Only cases added after the default parameters are loaded , will use the selected paramter set')],   
                   [sg.Submit(), sg.Cancel()] ]
    window1   = sg.Window('Define OPM Flow Default Run Time Parameters', layout=layout1)
        
    while True:
        (button, values) = window1.Read()
        if (button == 'Submit'):
            if (values[0]):
                jobparam, jobhelp = load_parameters(opmparam)
                break
    
            elif (values[1]):
                filename = sg.PopupGetFile('OPM Flow Parameter File Name',default_extension='param', save_as=False,
                                        file_types=[('Parameter File', ['*.param','*.PARAM']), ('All', '*.*')], keep_on_top=False)      
                if filename:
                    file  = open(filename,'r')
                    for n, x in enumerate(file):
                        if ('=' in x):
                            jobparam.append(x.rstrip())                        
                    file.close()
                    sg.PopupOK('OPM Flow User Parameters Loaded from: ' + filename)
                    break
                
            elif (values[2]):
                filename = sg.PopupGetFile('OPM Flow PRT File Name',default_extension='prt', save_as=False,
                                        file_types=[('Print File', ['*.prt','*.PRT']), ('All', '*.*')], keep_on_top=False)      
                if (filename):
                    file  = open(filename,'r')
                    for n, x in enumerate(file):
                        if ('="' in x):
                            if ('# default:' in x):
                                x    = x[:x.find('#') - 1]
                                xcmd = convert_string(x[:x.find('=')], 'camel2flow')
                                x    = xcmd + x[x.find('='):]
                                jobparam.append(x.rstrip())
                        elif('==Saturation' in x):
                            file.close()
                            sg.PopupOK('OPM Flow User Parameters Loaded from: ' + filename)
                            break
                    break
                                 
        elif (button == 'Cancel' or button == None):
            break
        
    window1.Close()
    if not jobparam:
        sg.PopupOK('OPM Flow User Parameters Not Set, Using Previous Values Instead')
        jobparam = jobparam0

    set_window_status(True)
    return(jobparam)
    

def delete_job(joblist,Job):
    if (not joblist):
        sg.PopupOK('No Cases in Job Queue')
    else:
        text = sg.PopupYesNo('Delete ' + Job[0] + '?')
        if (text == 'Yes'):
            joblist.remove(Job[0])
            window0.Element('_joblist_').Update(joblist)
            

def edit_job(job, jobhelp, opmuser):
    if (job == []):
        sg.PopupOK('No Case to Edit; Process Will Terminate') 
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
    if (filedata1.is_file()):
        filedata = filedata1
    if (filedata2.is_file()):
        filedata = filedata2
    if (filedata == ''):    
        sg.PopupError('Cannot Find Data File: ', str(filedata1),
                      'or ' , str(filedata2))
        return()
         
    fileparam1  = Path(job[istart:]).with_suffix('.param')
    fileparam2  = Path(job[istart:]).with_suffix('.PARAM')
    fileparam   = ''
    if (fileparam1.is_file()):
        fileparam = fileparam1
    if (not fileparam2.is_file()):
        fileparam = fileparam2
    if (fileparam ==''):
        sg.PopupError('Cannot Find Data File: ',  str(fileparam1),
                      'or ', str(fileparam2))
        return()
    #
    # Files Found So Display Edit Options
    #
    layout1   = [ [sg.Text('Edit Options for Job: ' + str(filebase))],    
                   [sg.Radio('Edit Data File'     , 'bRadio', default=True)],
                   [sg.Radio('Edit Parameter File', 'bRadio'              )],
                   [sg.Submit(), sg.Cancel()] ]
    window1   = sg.Window('Edit Job Options', layout=layout1)

    (button, values) = window1.Read()
    window1.Close()
    
    if (button == 'Cancel' or button == None):
        return()
    #
    # Data File Processing
    #
    if (button == 'Submit' and values[0] == True):
        if (opmoptn['edit-command'] == 'None'):
            sg.PopupOK('Editor command has not been set in the properties file',
                       'Use Edit OPMRUN Options to set the Editor Command')
            return()
        else:
            command = str(opmoptn['edit-command']).rstrip()
            command = command.replace('"', '')
            command = command 
            print(command + ' ' + str(filedata))
            subprocess.Popen([command, filedata])
    #
    # Parameter File Processing
    #
    if (button == 'Submit' and values[1] == True):
        if (fileparam.is_file()):
            file  = open(str(fileparam).rstrip(),'r')
            for n, line in enumerate(file):
                 if ('=' in line):
                     jobparam.append(line.rstrip())
            file.close()
            #
            # Edit Job Parameters
            #
            (jobparam1, exitcode) = edit_parameters(jobparam, jobhelp)
            if (exitcode == 'Exit'):
                save_parameters(filedata, jobparam1, filebase, fileparam, opmuser)
            
        else:
            sg.PopupError('Cannot Find File: ' + str(fileparam))

    return()

        
def edit_options(opmoptn):
    '''
    Edit OPMRUN options that define various configuration options:
    
        input-width      = set the size of the input list window in the x-direction (144)
        input-heigt      = set the size of the input list window in the y-direction (10)
        output-font      = set the output font type (Courier) 
        output-font-size = set the output font size (10) 
        output-width     = set the size of the output log windows in the x-direction (140)
        output-heigt     = set the size of the output log windows in the y-direction (30)
        opm-flow-manual  = define the location of the OPM Flow Manual (None)
        opm-resinsight   = defines the ResInsight command
        edit-command     = defines the edit and editor options to edit the input deck (None) 

    If the OPMINI file is not found then the default values are used.
    '''
    set_window_status(False)
    
    opmoptn0  =  opmoptn   
    column1   = [[sg.Text('Input Element Width '                                     , size=(30, None)) ,
                  sg.InputText(opmoptn['input-width'     ], key ='_input-width_'     , size=(10, None))],    
                 [sg.Text('Input Element Height'                                     , size=(30, None)) ,
                  sg.InputText(opmoptn['input-heigt'     ], key ='_input-heigt_'     , size=(10, None))],
                 [sg.Text('Output Element Width'                                     , size=(30, None)) ,
                  sg.InputText(opmoptn['output-width'    ], key ='_output-width_'    , size=(10, None))],
                 [sg.Text('Output Element Height'                                    , size=(30, None)) ,
                  sg.InputText(opmoptn['output-heigt'    ], key ='_output-heigt_'    , size=(10, None))],
                 [sg.Text('Output Element Font'                                      , size=(30, None)) ,
                  sg.InputText(opmoptn['output-font'     ], key ='_output-font_'     , size=(10, None))],
                 [sg.Text('Output Element Font Size'                                 , size=(30, None)) ,
                  sg.InputText(opmoptn['output-font-size'], key ='_output-font-size_', size=(10, None))],
                 [sg.Text('OPM Flow Manual Location'                                                  )],
                 [sg.InputText(opmoptn['opm-flow-manual' ], key = '_opm-flow-manual_'                 ),
                  sg.FileBrowse(target='_opm-flow-manual_', file_types=(('Manual Files', '*.pdf'),))   ],
                 [sg.Text('ResInsight Command'                                    )],
                 [sg.InputText(opmoptn['opm-resinsight'  ], key = '_opm-resinsight_')                  ],
                 [sg.Text('Editor Command for Editing Input Files'                                    )],
                 [sg.InputText(opmoptn['edit-command'    ], key = '_edit-command_')                    ]]
    
    layout1   = [ [sg.Column(column1)       ],
                  [sg.Submit(), sg.Cancel() ]]
    
    window1   = sg.Window('Edit Options', layout=layout1)
    
    (button, values) = window1.Read()
    window1.Close()
    
    if (button == 'Cancel' or button == None):
        opmoptn = opmoptn0 
    
    if (button == 'Submit'):
        opmoptn['input-width'     ] = values['_input-width_'     ]
        opmoptn['input-heigt'     ] = values['_input-heigt_'     ]
        opmoptn['output-width'    ] = values['_output-width_'    ]
        opmoptn['output-heigt'    ] = values['_output-heigt_'    ]
        opmoptn['output-font'     ] = values['_output-font_'     ]
        opmoptn['output-font-size'] = values['_output-font-size_']
        opmoptn['opm-flow-manual' ] = values['_opm-flow-manual_' ]           
        opmoptn['opm-resinsight'  ] = values['_opm-resinsight_'  ]
        opmoptn['edit-command'    ] = values['_edit-command_'    ]
        save_options(opmoptn)

    set_window_status(True)
    return(opmoptn)


def edit_parameters(jobparam, jobhelp):
    if (jobparam):
        set_window_status(False)
        
        jobparam0  = jobparam
        layout1    = [ [sg.Text('Select Parameter to Change:')],
                     [sg.Listbox(values=jobparam, size=(80, 20), key='_listbox_', bind_return_key=True,
                      font=(opmoptn['output-font'], opmoptn['output-font-size']))],
                     [sg.Text('Parameter to Change:')],
                     [sg.InputText('', size=(80, 1), key='_text_',
                      font=(opmoptn['output-font'], opmoptn['output-font-size']))],
                     [sg.Text('Parameter Help:')],
                     [sg.Multiline('', size=(80,4), key='_texthelp_',
                       font=(opmoptn['output-font'], opmoptn['output-font-size']))],
                     [sg.Button('Edit'), sg.Button('Save'), sg.Button('Cancel'), sg.Button('Exit')] ]
        window1 = sg.Window('Edit Parameters', layout=layout1)
    
        while True:
            (button, values) = window1.Read()
            
            if (button == 'Edit' or button == '_listbox_'):
                if values['_listbox_'] == []:               
                    sg.PopupError('Please select a parameter from the list')
                else:
                    window1.Element('_text_').Update(values['_listbox_'][0])
                    texthelp = values['_listbox_'][0]
                    texthelp = texthelp[:texthelp.find('=')]
                    if (texthelp in jobhelp):
                        paramhelp = jobhelp[texthelp]
                    else:
                        paramhelp = 'Help not found for ' + texthelp                   
                    window1.Element('_texthelp_').Update(paramhelp)
                    
            if (button == 'Save'):
                param = values['_text_']
                key   = param[:param.find('=')]
                for n, text in enumerate(jobparam):
                    if (text[:text.find('=')] == key):
                        jobparam[n] = param
                        paramhelp = 'Parameter: ' + str(jobparam[n]) + ' has be updated'                 
                        window1.Element('_texthelp_').Update(paramhelp)
                        break
                window1.Element('_listbox_').Update(jobparam)                        
                
            if (button == 'Cancel' or button == None):
                text = sg.PopupYesNo('Cancel Changes?')
                if (text == 'Yes'):
                    jobparam  = jobparam0
                    exitcode  = button
                    break
                else:
                    button = 'Edit'
                    continue
                
            if (button == 'Exit'):
                text = sg.PopupYesNo('Save and Exit?')
                if (text == 'Yes'):
                    jobparam = window1.Element('_listbox_').GetListValues()
                    exitcode = button
                    break
                
        window1.Close()
        set_window_status(True)
        window0.Element('_outlog_').Update()

    else:
        sg.PopupError('OPM Flow Parameters Have Not Been Set')
        
    return(jobparam, exitcode)

       
def edit_projects(opmoptn):
    '''
    Function allows the editing of project names and their assoicated directories.
    Projects are basically shorcuts to directories, so that one can quickly set the
    default directory. A maximum of five projects are current available.
    '''
    set_window_status(False)
    
    opmoptn0  =  opmoptn   
    column1   = [ [sg.Text('No.'              , justification='center', size=( 3, 1)),
                   sg.Text('Project Name'     , justification='center', size=(20, 1)),
                   sg.Text('Project Directory', justification='center', size=(80, 1))],
                  [sg.Text('1. '),
                   sg.InputText(opmoptn['prj-name-01' ], key = '_prj-name-01_', size=(20, 1)),
                   sg.InputText(opmoptn['prj-dirc-01' ], key = '_prj-dirc-01_', size=(80, 1)),
                   sg.FolderBrowse(                    target= '_prj-dirc-01_')],
                  [sg.Text('2. '),
                   sg.InputText(opmoptn['prj-name-02' ], key = '_prj-name-02_', size=(20, 1)),
                   sg.InputText(opmoptn['prj-dirc-02' ], key = '_prj-dirc-02_', size=(80, 1)),
                   sg.FolderBrowse(                    target= '_prj-dirc-02_')],
                  [sg.Text('3. '),
                   sg.InputText(opmoptn['prj-name-03' ], key = '_prj-name-03_', size=(20, 1)),
                   sg.InputText(opmoptn['prj-dirc-03' ], key = '_prj-dirc-03_', size=(80, 1)),
                   sg.FolderBrowse(                    target= '_prj-dirc-03_')],
                  [sg.Text('4. '),
                   sg.InputText(opmoptn['prj-name-04' ], key = '_prj-name-04_', size=(20, 1)),
                   sg.InputText(opmoptn['prj-dirc-04' ], key = '_prj-dirc-04_', size=(80, 1)),
                   sg.FolderBrowse(                    target= '_prj-dirc-04_')],
                  [sg.Text('5. '),
                   sg.InputText(opmoptn['prj-name-05' ], key = '_prj-name-05_', size=(20, 1)),
                   sg.InputText(opmoptn['prj-dirc-05' ], key = '_prj-dirc-05_', size=(80, 1)),
                   sg.FolderBrowse(                    target= '_prj-dirc-05_')]
                  ]
    
    layout1   = [ [sg.Column(column1) ],
                  [sg.Submit(), sg.Cancel() ]]
    
    window1   = sg.Window('Edit Projects', layout=layout1)
    
    (button, values) = window1.Read()
    window1.Close()
    
    if (button == 'Cancel' or button == None):
        opmoptn = opmoptn0
    
    if (button == 'Submit'):
        opmoptn['prj-name-01'] = values['_prj-name-01_']
        opmoptn['prj-name-02'] = values['_prj-name-02_']
        opmoptn['prj-name-03'] = values['_prj-name-03_']
        opmoptn['prj-name-04'] = values['_prj-name-04_']
        opmoptn['prj-name-05'] = values['_prj-name-05_']
        opmoptn['prj-dirc-01'] = values['_prj-dirc-01_']
        opmoptn['prj-dirc-02'] = values['_prj-dirc-02_']
        opmoptn['prj-dirc-03'] = values['_prj-dirc-03_']
        opmoptn['prj-dirc-04'] = values['_prj-dirc-04_']
        opmoptn['prj-dirc-05'] = values['_prj-dirc-05_']
        save_options(opmoptn)
        
    set_window_status(True)
    
    return(opmoptn)

                                
def get_time():             
    time = datetime.datetime.now()
    time = str(time.strftime('%Y-%m-%d %H:%M:%S'))
    return(time)


def kill_job(jobpid):
    button, values = window0.Read(timeout = 1)
    if (button != '_kill_job_'):
        return()
         
    text = sg.PopupYesNo('Do You Wish to Kill the Current OPM Flow Job ' + str(jobpid) + ' ?')
    if (text =='Yes'):
        run_process(['kill ' + str(jobpid)])
        out_log   ('OPM Flow Process ' + str(jobpid) + ' Has Been Stopped by ' + str(getpass.getuser()), True, True)
        sg.PopupOK('OPM Flow Process ' + str(jobpid) + ' Has Been Stopped by ' + str(getpass.getuser()))
    return()


def load_manual(filename):
    if (filename == 'None'):
        sg.PopupOK('OPM Flow Manual has not been set in the properties file',
                   'Use the Edit OPMRUN Options menu to define the command')
        return()

    elif (filename):
        if (sys.platform.startswith('linux')):
            filename = "/" + str(filename[2:len(filename) - 1])
            print("xdg-open " + str(filename))            
            subprocess.Popen(["xdg-open", filename])
        else:
           try:
                os.startfile(filename)
           except:
                sg.PopupError('OPM Flow Manual Not Found: ' + filename)
                pass
    else:
        sg.PopupError('OPM Flow Manual Not Found: ' + filename)
        
    return()


def load_options(opmoptn):
    '''
    Loads OPMRUN options that define various configuration options:
    
        input-width      = set the size of the input list window in the x-direction (144)
        input-heigt      = set the size of the input list window in the y-direction (10)
        output-width     = set the size of the output log windows in the x-direction (140)
        output-heigt     = set the size of the output log windows in the y-direction (30)
        output-font      = set the output font type (Courier) 
        output-font-size = set the output font size (10) 
        opm-flow-manual  = define the location of the OPM Flow Manual (None)
        opm-resinsight   = defines the ResInsight command
        edit-command     = defines the edit and editor options to edit the input deck (None) 

    If the OPMINI file is not found then it is created using the default values in #HOME/OPM/OPMRUN.ini
    '''
    if (opmini.is_file()):
        file  = open(opmini,'r')
        for n, line in enumerate(file):
            if ('=' in line):
                key   = line[:line.find('=')]
                value = line[line.find('=') + 1:].rstrip()
                opmoptn[key] = value
        file.close()
        '''
        for key,val in opmoptn.items():
            sg.Print (key, "=>", val)
        print(opmoptn)
        '''
    else:    
        opmoptn['input-width'     ] = 144
        opmoptn['input-heigt'     ] = 10
        opmoptn['output-width'    ] = 140
        opmoptn['output-heigt'    ] = 30
        opmoptn['output-font'     ] = 'Courier'
        opmoptn['output-font-size'] = 10
        opmoptn['opm-flow-manual' ] = 'None'
        opmoptn['opm-resinsight'  ] = 'None'
        opmoptn['edit-command'    ] = 'None'
        opmoptn['prj-name-01'     ] = 'Home'
        opmoptn['prj-dirc-01'     ] = '$Home'
        opmoptn['prj-name-02'     ] = 'Home'
        opmoptn['prj-dirc-02'     ] = '$Home'
        opmoptn['prj-name-03'     ] = 'Home'
        opmoptn['prj-dirc-03'     ] = '$Home'
        opmoptn['prj-name-04'     ] = 'Home'
        opmoptn['prj-dirc-04'     ] = '$Home'
        opmoptn['prj-name-05'     ] = 'Home'
        opmoptn['prj-dirc-05'     ] = '$Home'
        
        save_options(opmoptn, False)
        sg.PopupOK('OPMRUN Default Options Created and Saved')
    #
    # Write Header to Log File
    #
    try:
        opmlog.write('# \n')
        opmlog.write('# OPMRUN Log File \n')
        opmlog.write('# \n')
        opmlog.write('# File Name   : ' + str(opmfile) + '\n')
        opmlog.write('# Created By  : ' + opmuser + '\n')
        opmlog.write('# Date Created: ' + get_time()  + '\n')
        opmlog.write('# \n')
    except:
        pass

    return(opmoptn)


def load_parameters(filename, outpop=True):
    '''
    Function runs OPM Flow via a subprocess to get OPM Flow's Help parameters,
    and then then loads the help into jobhelp dict[] variable for future reference.
    
        outpop = Boolean Popup display option (True to display Popup, false no display).
        
    '''
    run_process('flow --help > '+ str(filename), outprt=False)
    jobparam = []
    jobhelp = dict()
    file  = open(filename,'r')
    for n, line in enumerate(file):
        if ('--' in line  and 'help' not in line):
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
    if (outpop):
        sg.PopupOK('OPM Flow Parameters Loaded from Flow: ' + str(filename))
        
    return(jobparam, jobhelp)


def load_queue(joblist):
    
        if (joblist != []):
            text = sg.PopupYesNo('Loading a OPMRUN Queue from File Will Delete the Existing Queue, Continue?')
        else:
            text = 'Yes'
            
        if (text == 'Yes'):   
            filename = sg.PopupGetFile('OPMRUN Queue File Name',default_extension='que', save_as=False,
                                   default_path=os.getcwd,   
                                   file_types=[('OPM Queues', '*.que'), ('All', '*.*')], keep_on_top=False )      
            if (filename):
                joblist = []
                file  = open(filename,'r')
                for n, line in enumerate(file):
                    if ('flow' in line):
                        joblist.append(line.rstrip())
                file.close()
                window0.Element('_joblist_').Update(joblist)                
                sg.PopupOK('OPMRUN Queue Loaded from: ' + filename)


def out_log(text,outlog,outprt=False):
    '''
    Function prints log information to display and log file with time stamp.
    
        outlog = Boolean log file output (True to write to log file, false not to write).
        outprt = Boolean print option (True to print to display, false not to print)).
        
    '''
    if (outprt):
        print(text + '\n')

    text = get_time() + ': ' + text + '\n'
    window0.Element('_outlog_').Update(text, append=True)
    
    if (outlog):
        opmlog.write(text)

    return()


def opm_popup(text,nrow):
    layout1 = [ [sg.Multiline(text, size=(80,nrow), background_color='white', text_color='darkgreen')],
                  [sg.CloseButton('OK')] ]
    window1 = sg.Window('OPMRUN - Flow Job Scheduler ' + opmvers, layout=layout1)
    (button, values) = window1.Read()
    return()


def run_command(cmd, timeout=None, window=None):
    '''
        Run shell command
	@param cmd: command to execute
	@param timeout: timeout for command execution
	@param window: the PySimpleGUI window that the output is going to (needed to do refresh on)
	@return: (return code from command, command output)
	
    '''
    try:
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        output = ''
        for line in p.stdout:
            line = line.decode(errors='replace' if (sys.version_info) < (3, 5) else 'backslashreplace').rstrip()
            output += line
            print(line)
            #window.Refresh() if window else None        # yes, a 1-line if
            window0.Refresh()
        retval = p.wait(timeout)
        return (retval, output)

    except:
       pass
    
    return()


def run_job(command):
    '''
    Runs a OPM Flow job via the subprocess command, gets process ID, and sends output to the
    OPM Flow outpur element.
    '''
    #
    # Submit Job and Get Process ID
    #
    i       = 0
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    while True:
        i = i + 1
        out_log('Getting Process PID Pass ' + str(i), opmlog)
        window0.Refresh()
        jobpid  = (subprocess.run(['pidof', '-s', 'flow'], stdout=subprocess.PIPE).stdout)
        if (jobpid.decode()) != '':
            break
        if (i == 10):
            out_log('Getting Process PID Pass Failed Aborting Job', opmlog)
            return()
            
    jobpid = int(jobpid)
    out_log('Simulation PID ' + str(jobpid), opmlog)
    #
    # Process OPM Flow Output
    #
    while True:
        line = process.stdout.readline()
        line = line.decode("utf-8").strip()
        if (line == '' and process.poll() is not None):
            break
        print(line)
        window0.Refresh()
        kill_job(jobpid)
    #
    # Process Complete - Get Last Output
    #
    output   = process.communicate()[0]
    output   = output.decode("utf-8")
    print(output)
    for  line in output.split(os.linesep):
        if ('Errors' in line  or 'terminate' in line or 'what()' in line or 'Aborted' in line):       
            out_log(line, opmlog)
    #
    # Processs Complete - Get Exit Code
    #
    exitCode = process.returncode
    if (exitCode != 0):
        #raise ProcessException(command, exitCode, output)
        raise subprocess.CalledProcessError(exitCode, command)
    
    print('Process Complete (' + str(exitCode) +')')
    return (exitCode)

    
def run_jobs(joblist,outlog):
    '''
    Function allows user to select options for running jobs and submits jobss for execution.

        joblist = List of jobs to run.
        outlog  = Boolean log file output (True to write to log file, false not to write).
      
    '''
    if (joblist == []):
        sg.PopupOK('No Jobs In Queue')
        return()
    
    jobnum = 0
    layout1   = [ [sg.Text('Select the Run Option for All ' + str(len(joblist)) + ' Cases in Queue?' )],    
                  [sg.Radio('Run in No Simulation Mode'      , 'bRadio1', key ='_nosim_'                )],
                  [sg.Radio('Run in Standard Simulation Mode', 'bRadio1', key ='_rusim_',   default=True)],
                  [sg.Text('Submit jobs for foreground or background processing'                        )],
                  [sg.Radio('Foreground Processing'          , 'bRadio2', key ='_fore_'  ,  default=True)],
                  [sg.Radio('Background Processing'          , 'bRadio2', key ='_back_'                 )],
                  [sg.Text(''                                                                           )],
                  [sg.Submit(), sg.Cancel()] ]
    window1   = sg.Window('Select Run Option', layout=layout1)
    (button, values) = window1.Read()
    window1.Close()
    #
    # Background Processing
    #
    if (values['_back_']):
        if values['_nosim_']:
            save_jobs(joblist, '_nosim_', outlog=True)
        else:
            save_jobs(joblist, '_rusim_', outlog=True)

        #subprocess.Popen(['mate-terminal', '-e', str(opmjob)], stdout=subprocess.PIPE)
        subprocess.Popen(['xterm', '-hold', '-e', str(opmjob)], stdout=subprocess.PIPE)
        return()
    #
    # Foreground Processing
    #    
    for x in joblist:
        jobnum  = jobnum + 1
        istart  = x.find('=') 
        job     = x[istart + 1:]
        jobcmd  = x[:istart + 1]
        jobpath = Path(job).parents[0]
        jobbase = Path(job).name
        jobroot = Path(job).stem
        joblog  = Path(jobbase).with_suffix('.LOG')

        if (values['_nosim_']):
            jobcase = jobcmd + str(jobbase) + ' --enable-dry-run="true"' + ' | tee ' + str(joblog)
            print (jobcase)

        if (values['_rusim_']):
            jobcase = jobcmd + str(jobbase)  + ' | tee ' + str(joblog)
            
        if (button == 'Cancel'  or button == None):
            out_log('Job Processing Canceled', opmlog, True)
            return()
          
        if (button == 'Submit'):
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
            if (error == False):
                out_log('End   Job: ' + jobcase, outlog)
                out_log('Completed Job No. ' + str(jobnum), outlog)
                out_log('', outlog)
                continue
                
            #
            # Remove Existing Output Files
            #
            out_log('Removing Existing Output Files', outlog)
            for text in ['.DBG', '.EGRID', '.INIT', '.LOG', '.PRT', '.SMSPEC', '.UNRST', '.UNSMRY',
                         '.dbg', '.egrid', '.init', '.log', '.prt', '.smspec', '.unrst', '.unsmry' ]:
                filename = Path(jobbase).with_suffix(text)
                if (filename.is_file()):
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
            if (not filename.exists()):
                sg.Print('Debug Start')
                sg.Print('   Log File Not Found Error')         
                sg.Print('   Current Working Directory ' , str(os.getcwd()))
                sg.Print('   Log File                  ' , joblog)
                sg.Print('Debug End')
            else:     
                file          = open(filename,'r')
                lines, status = tail(file,11, offset=None)
                file.close()
                if (status):
                    for line in enumerate(lines):
                        if (line[1] == ''):
                            continue
                        out_log(line[1],outlog)
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
    '''
    Run a command as a subprocess.
    
        outprt = Boolean print option (True to print to display, false not to print)).
        
    '''
    try:
        sp       = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        out, err = sp.communicate()
        if (out and outprt == True):
            print(out[0].decode("utf-8"))

    except:
        out ,err = sp.communicate()
        sg.PopupError('Subprocess Call Error: \n' + str(command))
        pass
    
    if (out):
        return(out[1])
    else:
        return()
            
def run_resinsight(command):
    if (command == 'None'):
        sg.PopupOK('OPM ResInsight Command has not been set in the properties file',
                 'Use the Edit Options menu to define the command'                )
        return()

    try:
        command = command.replace('"', '')
        print(str(command))
        subprocess.Popen(command)
    except:
        sg.PopupError('OPM ResInsight Not Found: ' + command)
        pass
    return()


def save_jobs(joblist, jobtype, outlog=True):
    '''
    Save OPMRUN jobs to file in #HOME/OPM/OPMRUN.job
    
        outlog = Boolean log file output (True to write to log file, false not to write).
        
    '''
    jobnum = 0
    file   = open(opmjob,'w')
    file.write('# \n')
    file.write('# OPMRUN Job File \n')
    file.write('# \n')
    file.write('# File Name   : "' + str(opmhome) + '"\n')
    file.write('# Created By  : '  + str(opmuser) + '\n')
    file.write('# Date Created: '  + get_time() + '\n')
    file.write('# \n')
    for x in joblist:
        jobnum  = jobnum + 1
        istart  = x.find('=') 
        job     = x[istart + 1:]
        jobcmd  = x[:istart + 1]
        jobpath = Path(job).parents[0]
        jobbase = Path(job).name
        jobroot = Path(job).stem
        joblog  = Path(jobbase).with_suffix('.LOG')
        
        if (jobtype == '_nosim_'):
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
    subprocess.call(['chmod', 'u=rwx', opmjob])
    if (outlog):
        out_log('OPMRUN Jobs File Saved: ' + str(opmini), outlog)


def save_options(opmoptn, outlog=True):
    '''
    Save OPMRUN options to file in #HOME/OPM/OPMRUN.ini
    
        outlog = Boolean log file output (True to write to log file, false not to write).
        
    '''
    file  = open(opmini,'w')
    file.write('# \n')
    file.write('# OPMRUN Options File \n')
    file.write('# \n')
    file.write('# File Name   : "' + str(opmhome) + '"\n')
    file.write('# Created By  : '  + str(opmuser) + '\n')
    file.write('# Date Created: '  + get_time() + '\n')
    file.write('# \n')
    for key, value in opmoptn.items():
        if (str(value).isdigit):
            file.write(str(key) + '=' + str(value) + ' \n')       
        else:
            file.write(str(key) + '="' + str(value) + '" \n')       
    file.write('# \n')
    file.write('# End of OPMRUN Options File \n')
    file.close()
    if (outlog):
        out_log('OPMRUN Options File Saved: ' + str(opmini), outlog)
    

def save_parameters(job, jobparam, jobbase, jobfile, opmuser):
    file  = open(jobfile,'w')
    file.write('# \n')
    file.write('# OPMRUN Parameter File \n')
    file.write('# \n')
    file.write('# File Name   : "' + str(jobfile) + '"\n')
    file.write('# Created By  : '  + opmuser + '\n')
    file.write('# Date Created: '  + get_time() + '\n')
    file.write('# \n')
    for x in jobparam:
        if ('EclDeckFileName' in x ):
            file.write('EclDeckFileName="' + Path(job).name  + '"\n')
        elif ('ecl-deck-file-name' in x):
            file.write('ecl-deck-file-name="' + Path(job).name  + '"\n')
        else:
            file.write(x + '\n')
    file.write('# \n')
    file.write('# End of Parameter File \n')
    file.close()
    sg.PopupOK(str(jobbase) + ' parameter file written to:',
               str(jobfile),
               'Complete',no_titlebar=True)
    
    
def save_queue(joblist):
    if not joblist:
        sg.PopupOK('No Cases In Job Queue; Queue will Not Be Saved')
    else:
        filename = sg.PopupGetFile('OPMRUN Queue File Name',default_extension='que', save_as=True,
                               file_types=[('OPM Queues', '*.que'), ('All', '*.*')], keep_on_top=False )      
        if (filename):
            file       = open(filename,'w') 
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
            sg.PopupOK('OPMRUN Queue File Saved to: ' + filename)

            
def set_button_status(status, all=False):
    '''
    Set the display buttons to enabled (False) or disable (True) depending
    on the value of status.

        all = Boolean that set addition elements status
              (True to up date status of additional element, false not to)
              
    '''
    window0.Element('_run_jobs_'   ).Update(disabled = status)    
    window0.Element('_exit_'       ).Update(disabled = status)    
    window0.Element('_clear_'      ).Update(disabled = status)
    
    window0.Element('_clear_queue_').Update(disabled = status)
    window0.Element('_load_queue_' ).Update(disabled = status)
    window0.Element('_save_queue_' ).Update(disabled = status)

    if (all):
        window0.Element('_add_job_'   ).Update(disabled = status)         
        window0.Element('_delete_job_').Update(disabled = status)         
        window0.Element('_edit_job_'  ).Update(disabled = status)         
        window0.Element('_kill_job_'  ).Update(disabled = status)         

        
def set_directory(jobpath, outlog=True, outpop=False, outprt=True):
    '''
    Set the current directory to jobpath
    
        outlog = Boolean log file output (True to write to log file, false not to write).
        outpop = Boolean Popup display option (True to display Popup, false no display).
        outprt = Boolean print option (True to print to display, false not to print)).
        
    '''
    try:
        os.chdir(jobpath)
        print("Current Working Directory " , str(os.getcwd()))

    except OSError:
        if (outpop):
            sg.PopupError('Change Working Directory Error \n'
                          'Please See Log Output'            )
        
        out_log('Cannot Change the Current Working Directory', outlog, outprt)
        out_log(str(jobpath), outlog, outprt)
        return(False)
        
    return(True)


def set_directory_project(key,opmoptn):
    '''
    Set the default directory via the project name/directory
    '''
    key = key[(key.find('_') + 1):-1] 
    name = opmoptn.get(key)
    if (name == None or name == ''):
        sg.PopupError('Project Name ' + key + ' not Found')
        return()
    dirc = key.replace('name','dirc')
    dirc = opmoptn.get(dirc)
    if (dirc == None or dirc == ''):
        sg.PopupError('Project Directory ' + dirc + ' not Found')
        return()

    status = set_directory(Path(dirc), True)
    if (status):
        sg.PopupOK('Change Directory',
                  'Project Name: '     + name + '\n' +
                  'Project Directory:' + dirc + '\n'  )


def set_menu():
    '''
    Set the main menu for the first time to display, and for when the menu needs to be updated.
    Use:
    
        menulayout = set_menu()
        mainmenu.Update(menulayout)
        
    To update menus.
    '''
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
                         'Uncompress Jobs',
                         'ResInsight'],],      
              ['Help',  ['Manual',
                         'ResInsight Help',
                         'Help',
                         'About'],
                        ] ]
    return(menu)


def set_window_status(status):
    '''
    Set the main window status to active or inactive for when a second window
    is being displayed.
    
        status = True  window0 is active
                 False window0 is inactive 
    '''
    if (status):
        # window0.Enable()   Not Working Causes Display to Freeze on Linux Systems
        set_button_status(False, True)
        window0.SetAlpha(1.00)
        window0.Refresh()        
    else:
        window0.SetAlpha(0.85)
        set_button_status(True, True)
        #window0.Disable()  Not Working Causes Display to Freeze Linux Systems
        
    
def tail(f, n, offset=None):
    '''
    Reads a n lines from f with an offset of offset lines.  The return
    value is a tuple in the form ``(lines, has_more)`` where `has_more` is
    an indicator that is `True` if there are more lines in the file.
    '''
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
        if (len(lines) >= to_read or pos == 0):
            return lines[-to_read:offset and -offset or None], \
                   len(lines) > to_read or pos > 0
        avg_line_length *= 1.3

def uncompress_job():

    set_window_status(False)
    
    joblist1 = []
    layout1  = [[sg.Text('Select Multiple Archive Files to Uncompress'                           )],    
                 [sg.Listbox(values='', size=(100,10), key='_joblist1_'                          )],                
                 [sg.Text('Output'                                                               )],
                 [sg.Output(key='_outlog1_', size=(100,15),font=('Courier',9) ,text_color='blue' )],
                 [sg.Text('Uncompression Options'                                                )],
                 [sg.Radio('Uncompress and Keep Existing Files'        , "bRadio1", default=True,
                           key='_bRadio1_'                                                       )],
                 [sg.Radio('Uncompress and Overwrite Existing Files'   , "bRadio1"               )],
                 [sg.Text('Compressed File Options'                                              )],
                 [sg.Radio('Keep Compressed File After Uncompressing'  , "bRadio2", default=True,
                           key='_bRadio2_'                                                       )],
                 [sg.Radio('Delete Compressed File After Uncompressing', "bRadio2"               )],
                 [sg.Button('Add'), sg.Button('List'), sg.Submit(), sg.Cancel()                  ]]
    window1 = sg.Window('Compress Job Files', layout=layout1)
                                                  
    while True:
        (button, values) = window1.Read()
        
        if (button == 'Add'):
            jobs = sg.PopupGetFile('Select ZIP Files to Ucompress',no_window=False,
                                   multiple_files=True,
                                   default_path=os.getcwd,
                                   file_types=[('zip', ['*.zip','*.ZIP'])])
            if (jobs != None):
                jobs = jobs.split(';')
                for job in jobs:
                    joblist1.append(job)
                    
                window1.Element('_joblist1_').Update(joblist1)
        #
        # Get Directory and List Files
        #
        if (button == 'List'):
            jobpath = sg.PopupGetFolder('Select Directory', no_window=False)
            if (jobpath != None):
                set_directory(jobpath)
                print(jobpath + '\n')

            jobpath = os.getcwd()
            for file in Path(jobpath).glob("*.zip"):
                print(str(Path(file).name))
                
            for file in Path(jobpath).glob('*.ZIP'):  
                print(str(Path(file).name))
        #
        # Uncompress Files
        #
        if (button == 'Submit'):
            if (values['_bRadio1_']):
                zipcmd = 'unzip -u -n '
            else:
                zipcmd = 'unzip -u -o '
                    
            for job in joblist1:
                out_log('Start Uncompress', opmlog, True)
                jobpath = Path(job).parents[0]
                jobbase = Path(job).name
                jobroot = Path(job).stem
                jobfile  = Path(jobbase).with_suffix('.zip')
                set_directory(jobpath)
                jobcmd = zipcmd + str(jobfile)
                out_log('   ' + jobcmd, opmlog,True)
                print(str(jobpath))
                run_command(jobcmd)
                if (values['_bRadio2_'] == False):
                    jobcmd = 'rm -v ' + str(jobfile)
                    out_log('   ' + jobcmd, opmlog, True)
                    run_command(jobcmd)
                    
                out_log('End Uncompressing', opmlog, True)
                window1.Refresh()
               
            joblist1 = []
            window1.Element('_joblist1_').Update(joblist1)
                           
        if (button == 'Cancel' or button == None):
            break
        
    joblist1 = []   
    window1.Close()
    set_window_status(True)
    return()

#-----------------------------------------------------------------------------------------------------------------------------------
# Pre-Processing Section
#-----------------------------------------------------------------------------------------------------------------------------------
#
# Load OPMRUN Configuration Parameters
#
opmoptn           = load_options(opmoptn)
#
# Run Flow Help and Store Command Line Parameters
#
jobparam, jobhelp = load_parameters(opmparam, outpop=False)

#-----------------------------------------------------------------------------------------------------------------------------------
# Define GUI Section 
#-----------------------------------------------------------------------------------------------------------------------------------
menulayout = set_menu()
mainmenu   = sg.Menu(menulayout)

flowlayout = [[sg.Text('Output',background_color='black',text_color='white')],
                  [sg.Output(background_color='white', text_color='black', 
                             size=(opmoptn['output-width'], opmoptn['output-heigt']),
                             key='_outflow_',font=(opmoptn['output-font'], opmoptn['output-font-size']))] ] 

loglayout  = [[sg.Text('Log',background_color='darkgreen',text_color='white')],
                  [sg.Multiline(background_color='white', text_color='darkgreen', do_not_clear=True, 
                                key='_outlog_',size=(opmoptn['output-width'], opmoptn['output-heigt']),
                                font=(opmoptn['output-font'],opmoptn['output-font-size']))] ] 

mainwind   = [[mainmenu],
              [sg.Text('OPM Flow Command Schedule')],
              [sg.Listbox(values=joblist, size=(opmoptn['input-width'], opmoptn['input-heigt']), key='_joblist_',
                          font=(opmoptn['output-font'],opmoptn['output-font-size']))],
        
              [sg.Button('Add Job'       , key = '_add_job_'    ),
                  sg.Button('Edit Job'   , key = '_edit_job_'   ),
                  sg.Button('Delete Job' , key = '_delete_job_' ),
                  sg.Button('Clear Queue', key = '_clear_queue_'),
                  sg.Button('Load Queue' , key = '_load_queue_' ),
                  sg.Button('Save Queue' , key = '_save_queue_' )],
                
              [sg.TabGroup([[sg.Tab('Output', flowlayout, key='_tab_output_',
                                    title_color='black', background_color='white'),
                             sg.Tab('Log'    , loglayout , key='_tab_outlog_'     ,    
                                    title_color='darkgreen', background_color='white', border_width=None)]],  
                             title_color='black',background_color='white')],
              
              [sg.Button('Run Jobs'   , key = '_run_jobs_'),
                  sg.Button('Kill Job', key = '_kill_job_'),
                  sg.Button('Clear'   , key = '_clear_'    ),
                  sg.Button('Exit'    , key = '_exit_'    )],
              [sg.Text('')] ]

window0 = sg.Window('OPMRUN - Flow Job Scheduler ' + opmvers, layout=mainwind, disable_close=True)
out_log('OPMRUN Started', opmlog)

#-----------------------------------------------------------------------------------------------------------------------------------
# Define GUI Event Loop, Read Buttons, and Make Callbacks etc. Section 
#-----------------------------------------------------------------------------------------------------------------------------------
while True:
    #
    # Read the Form and Process and Take appropriate action based on button
    #
    button, values = window0.Read()   
    joblist = window0.Element('_joblist_').GetListValues()

    #
    # About 
    #
    if (button == 'About'):
        opm_popup(abouttext,20)
        continue
    #
    # Add Job 
    #
    elif (button == '_add_job_'):
        add_job(joblist,jobparam,opmuser)
        continue
    #
    # Clear Log
    #
    elif (button == '_clear_'):
        clear_output()
        continue
    #
    # Clear Queue
    #
    elif (button == '_clear_queue_'):
        clear_queue(values['_joblist_'])
        continue
    #
    # Compress Jobs
    #
    elif (button == 'Compress Jobs'):
        compress_job()
        continue
    #
    # Delete Job
    #
    elif (button == '_delete_job_'):
        delete_job(joblist,values['_joblist_'])
        continue
    #
    # Edit Job
    #
    elif (button == '_edit_job_'):
        edit_job(values['_joblist_'], jobhelp, opmuser)
        continue
    #
    # Edit Options
    #
    elif (button == 'Options'):
        opmoptn = edit_options(opmoptn)
        continue
    #
    # Edit Parameters
    #
    elif (button == 'Edit Parameters'):
       (jobparam, exitcode) = edit_parameters(jobparam, jobhelp)
       continue
    #
    # Edit Projects
    #
    elif (button == 'Projects'):
        opmoptn    = edit_projects(opmoptn)
        menulayout = set_menu()
        mainmenu.Update(menulayout)
        continue
    #        
    # Exit
    #
    elif (button == '_exit_' or button == 'Exit' or button is None):
        text = sg.PopupYesNo('Exit OPMRUN?')
        if (text == 'Yes'):          
            text = sg.PopupYesNo('Are You Sure You wish to Exit OPMRUN?')
            if (text == 'Yes'):
                break
    #
    # Help
    #
    if (button == 'Help'):
        opm_popup(helptext,35)
        continue
        
    elif button == 'List Parameters':
        if (jobparam):
            print('Start of OPM Flow Parameters')
            for k in enumerate(jobparam):
                print('{}: {}'.format(*k))
            print('End of OPM Flow Parameters')
        else:
            sg.PopupError('OPM Flow Parameters Have Not Been Set')
        continue
    #
    # Load Queue
    #
    elif (button == '_load_queue_' or button == 'Open'):
        load_queue(joblist)
        continue
    #
    # Manual
    #
    elif (button == 'Manual'):
        load_manual(opmoptn['opm-flow-manual'])
        continue
    #
    # ResInsight
    #
    elif (button == 'ResInsight'):
        run_resinsight(opmoptn['opm-resinsight'])
        continue
    #
    # Run Jobs
    #
    elif (button == '_run_jobs_'):
        run_jobs(joblist,opmlog)
        continue
    #
    # Save Queue
    #
    elif (button == '_save_queue_' or button == 'Save'):
         save_queue(joblist)
         continue
   #        
    # Set Parameters
    #
    elif (button == 'Set Parameters'):
        jobparam = default_parameters(jobparam,opmparam)
        continue
    #        
    # Set Project
    #
    elif (button.find('::_prj-name') != -1):
        set_directory_project(button,opmoptn)
        continue
    #
    # Uncompress Jobs
    #
    elif (button == 'Uncompress Jobs'):
       uncompress_job()
       continue
        
#-----------------------------------------------------------------------------------------------------------------------------------
# Post Processing Section 
#-----------------------------------------------------------------------------------------------------------------------------------
window0.Close()

out_log('OPMRUN Processing Complete ', opmlog)
opmlog.close()


#===================================================================================================================================
# End of OPMRUN.py
#===================================================================================================================================
