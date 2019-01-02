#===================================================================================================================================
#
'''
OPMRUN.py - Run OPM Flow

The program allows the user to select files to be submitted to OPM Flow 

Program Doumentation
--------------------

Copyright Notice
----------------
This file is part of the Open Porous Media project (OPM).

OPM is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

OPM is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the aforementioned GNU General Public Licenses for more details.

Copyright (C) 2018 Equinor
Copyright (C) 2018 Equinox International Petroleum Consultants Pte Ltd.

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
import os
import getpass
import re
import sys
import subprocess
from datetime import datetime
from pathlib import Path

#-----------------------------------------------------------------------------------------------------------------------------------
# Define Constants Section 
#----------------------------------------------------------------------------------------------------------------------------------- 
joblist  = []
jobparam = []
jobhelp  = dict()

opmoptn  = dict()
opmvers  = '2018-10.01'
opm      = Path.home()
opmhome  = Path(opm  / 'OPM')
if not opmhome.is_dir():
    opmhome.mkdir()
    
opmini   = Path(opmhome / 'OPMRUN.ini')
opmrun   = Path(opmhome / 'OPMRUN.que')
opmfile  = Path(opmhome / 'OPMRUN.log')
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
        tooltip_time = None,
        )

abouttext = ('OPMRun is a Grapical User Interface ("GNU") program for the Open Porous Media ("OPM") Flow simulator \n' +
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
             'Copyright (C) 2018 Equinor \n'
             'Copyright (C) 2018 Equinox International Petroleum Consultants Pte Ltd. \n'
             '\n' +
             'Author  : David Baxendale (david.baxendale@eipc.co)') 

helptext = ('OPMRun is a Grapical User Interface ("GNU") program for the Open Porous Media ("OPM") Flow simulator \n' +
             '\n'
             'The software enables submiting OPM Flow simulation input decks together with editing of the associated ' +
             'PARAM file \n' +
             '\n'
             'Author  : David Baxendale (david.baxendale@eipc.co)') 

#-----------------------------------------------------------------------------------------------------------------------------------
# Define Modules Section 
#-----------------------------------------------------------------------------------------------------------------------------------
def add_job(joblist,jobparam,opmuser):

    if (jobparam == []):
        sg.PopupOK('Job Parameters Missing; Cannot Add Cases')
        return()
        
    window0.Disable
    layout1 = [[sg.Text('File to Add to Queue')],    
                 [sg.InputText(size=(80, None)), sg.FileBrowse(file_types=[('OPM', ['*.data','*.DATA']), ('All', '*.*')])],
                 [sg.Text('Run Parameters')],
                 [sg.Radio('Sequential Run' , "bRadio", default=True)],
                 [sg.Radio('Parallel Run   ', "bRadio"              ), sg.Text('No. of Nodes'),
                  sg.Listbox(values=list(range(1,65)), size=(5,3))],                
                 [sg.Submit(), sg.Cancel()]]
    window1 = sg.Window('Select OPM Flow Input File').Layout(layout1)
    
    while True:
        (button, values) = window1.Read()
        job     = values[0]
        jobseq  = values[1]
        jobpar  = values[2]
        jobnode = values[3]
        if not jobnode:
            jobnode = 2
        if button == 'Submit':
            if len(job) > 0:
                jobpath = Path(job).parents[0]
                jobbase = Path(job).name
                jobfile = Path(job).with_suffix('.param')
                if jobseq:
                    joblist.append('flow --parameter-file=' + str(jobfile)) 
                if jobpar:
                    joblist.append('mpirun -np ' + str(jobnode) + ' flow --parameter file=' + str(jobfile))                
                window0.Enable
                window0.FindElement('_joblist_').Update(joblist)
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
                                  no_titlebar=True)
                    if (text == 'No'):
                        sg.PopupOK('Writing out paraamter file cancelled, will use existing file instead')
                else:
                    text = 'Yes'
                    
                if (text == 'Yes'):
                    out_param(job, jobparam, jobbase, jobfile, opmuser)
                                
        elif button == 'Cancel':
            break
        
    window1.Close()
    window0.Enable
    return()

def clear_queue(joblist):
    if joblist == []:
        sg.PopupOK('No Case Selected for Deletion')
    else:
        text = sg.PopupYesNo('Delete All Cases in Queue?')
        if text == 'Yes':
            joblist = []
            window0.FindElement('_joblist_').Update(joblist)

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
    jobparam0 = jobparam
    jobparam  = []

    layout1   = [ [sg.Text('Define OPM Flow Default Parameters for New Cases')],    
                   [sg.Radio('Load Parameters from OPM Flow '               , 'bRadio', default=True)],
                   [sg.Radio('Load Parameters from OPM Flow Parameter File' , 'bRadio'              )],
                   [sg.Radio('Load Parameters from OPM Flow Print File'     , 'bRadio'              )],
                   [sg.Text('Only cases added after the default parameters are loaded , will use the selected paramter set')],   
                   [sg.Submit(), sg.Cancel()] ]
    window1   = sg.Window('Define OPM Flow Default Run Time Parameters').Layout(layout1)
        
    while True:
        (button, values) = window1.Read()
        if button == 'Submit':
            if (values[0]):
                jobparam, jobhelp = opm_flow_parameters(opmparam)
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
                if filename:
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
                                 
        elif button == 'Cancel':
            break
        
    window1.Close()
    if not jobparam:
        sg.PopupOK('OPM Flow User Parameters Not Set, Using Previous Values Instead')
        jobparam = jobparam0
    return(jobparam)
    

def delete_job(joblist,Job):
    if not joblist:
        sg.PopupOK('No Cases in Job Queue')
    else:
        text = sg.PopupYesNo('Delete ' + Job[0] + '?')
        if text == 'Yes':
            joblist.remove(Job[0])
            window0.FindElement('_joblist_').Update(joblist)
            

def edit_job(job, jobhelp, opmuser):
    if job == []:
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
    if not filedata1.exists():
        if not filedata2.exists():
            sg.PopupError('Cannot Find Data File: ', str(filedata1),
                          'or ' , str(filedata2))
            return()
        else:
            filedata = filedata2
    else:
        filedata = filedata1
         
    fileparam1  = Path(job[istart:]).with_suffix('.param')
    fileparam2  = Path(job[istart:]).with_suffix('.PARAM')
    if not fileparam1.exists():
        if not fileparam2.exists():
            sg.PopupError('Cannot Find Data File: ',  str(fileparam1),
                          'or ', str(fileparam2))
            return()
        else:
            fileparam = fileparam2
    else:
        fileparam = fileparam1
    #
    # Files Found So Display Edit Options
    #
    layout1   = [ [sg.Text('Edit Options for Job: ' + str(filebase))],    
                   [sg.Radio('Edit Data File'     , 'bRadio', default=True)],
                   [sg.Radio('Edit Parameter File', 'bRadio'              )],
                   [sg.Submit(), sg.Cancel()] ]
    window1   = sg.Window('Edit Job Options').Layout(layout1)

    (button, values) = window1.Read()
    window1.Close()
    
    if button == 'Cancel' or button is None:
        return()
    #
    # Data File Processing
    #
    if button == 'Submit' and values[0] == True:
        if (opmoptn['edit-command'] == 'None'):
            sg.PopupOK('Editor command has not been set in the properties file',
                       'See the OPMRUN.ini file in the home directory')
            return()
        else:
            command = str(opmoptn['edit-command']).rstrip()
            command = command.replace('"', '')
            command = command + ' ' + str(filedata)
            print(command)
            subprocess.Popen(['jedit', filedata])
    #
    # Parameter File Processing
    #
    if button == 'Submit' and values[1] == True:
        if fileparam.is_file():
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
                out_param(job, jobparam1, filebase, fileparam, opmuser)
            
        else:
            sg.PopupError('Cannot Find File: ' + str(fileparam))

    return()
        
def edit_parameters(jobparam, jobhelp):
    if (jobparam):
        jobparam0 = jobparam
        window0.Disable

        layout1  = [ [sg.Text('Select Parameter to Change:')],
                     [sg.Listbox(values=jobparam, size=(80, 20), key='_listbox_', bind_return_key=True,
                      font=(opmoptn['output-font'], opmoptn['output-font-size']))],
                     [sg.Text('Parameter to Change:')],
                     [sg.InputText('', size=(80, 1), key='_text_',
                      font=(opmoptn['output-font'], opmoptn['output-font-size']))],
                     [sg.Text('Parameter Help:')],
                     [sg.Multiline('', size=(80,4), key='_texthelp_',
                       font=(opmoptn['output-font'], opmoptn['output-font-size']))],
                     [sg.Button('Edit'), sg.Button('Save'), sg.Button('Cancel'), sg.Button('Exit')] ]
        window1 = sg.Window('OPM Flow Default Parameters').Layout(layout1)
    
        while True:
            (button, values) = window1.Read()
            
            if button == 'Edit' or button == '_listbox_':
                if values['_listbox_'] == []:               
                    sg.PopupError('Please select a parameter from the list')
                else:
                    window1.FindElement('_text_').Update(values['_listbox_'][0])
                    texthelp = values['_listbox_'][0]
                    texthelp = texthelp[:texthelp.find('=')]
                    if (texthelp in jobhelp):
                        paramhelp = jobhelp[texthelp]
                    else:
                        paramhelp = 'Help not found for ' + texthelp                   
                    window1.FindElement('_texthelp_').Update(paramhelp)
                    
            if button == 'Save':
                param = values['_text_']
                key   = param[:param.find('=')]
                for n, text in enumerate(jobparam):
                    if (text[:text.find('=')] == key):
                        jobparam[n] = param
                        paramhelp = 'Parameter: ' + str(jobparam[n]) + ' has be updated'                 
                        window1.FindElement('_texthelp_').Update(paramhelp)
                        break
                window1.FindElement('_listbox_').Update(jobparam)                        
                
            if button == 'Cancel':
                text = sg.PopupYesNo('Cancel Changes?')
                if text == 'Yes':
                    jobparam  = jobparam0
                    exitcode  = button
                    break
                
            if button == 'Exit':
                text = sg.PopupYesNo('Save and Exit?')
                if text == 'Yes':
                    jobparam = window1.FindElement('_listbox_').GetListValues()
                    exitcode = button
                    break
                
        window1.Close()
        window0.Enable
    else:
        sg.PopupError('OPM Flow Parametes Have Not Been Set')
    return(jobparam, exitcode)

        
def execute_command_subprocess(command,realtime):
    #
    # Real Time Output - Poll process for new output until finished
    #
    if(realtime):
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        while True:
            nextline = process.stdout.readline()
            nextline = nextline.decode("utf-8").strip()
            if nextline == '' and process.poll() is not None:
                break
            print(nextline)
            window0.Refresh()
        print('Process Complete')
            
        output = process.communicate()[0]
        exitCode = process.returncode

        if (exitCode == 0):
            return (exitCode)
        else:
            #raise ProcessException(command, exitCode, output)
            raise subprocess.CalledProcessError(exitCode, command)
            print(output)
            return (output)
    #
    # Batch Output - Output after finished
    #
    else:
        try:
            sp = subprocess.Popen([command], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = sp.communicate()
#            if out:
#                print(out.decode("utf-8"))
#            if err:
#                print(err.decode("utf-8"))
        except:
            pass
        return()


def get_time():             
    time = datetime.now()
    time = str(time.strftime('%Y-%m-%d %H:%M:%S'))
    return(time)


def load_queue(joblist):
        text = sg.PopupYesNo('Loading a OPMRUN Queue from File Will Delete the Existing Queue, Continue?')
        if text == 'Yes':    
            filename = sg.PopupGetFile('OPMRUN Queue File Name',default_extension='que', save_as=False,
                                   file_types=[('OPM Queues', '*.que'), ('All', '*.*')], keep_on_top=False )      
            if filename:
                joblist = []
                file  = open(filename,'r')
                for n, line in enumerate(file):
                    if ('flow' in line):
                        joblist.append(line.rstrip())
                file.close()
                window0.FindElement('_joblist_').Update(joblist)                
                sg.PopupOK('OPMRUN Queue Loaded from: ' + filename)


def kill_job(joblist):
    sg.PopupOK('Kill Case Option Not Available')
    return()


def opm_flow_manual(filename):
    if filename == 'None':
        sg.PopupOK('OPM Flow Manual has not been set in the properties file',
                   'See the OPMRUN.ini file in the home directory')
        return()

    elif filename:
        if sys.platform.startswith('linux'):
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


def out_log(text,opmlog):
    text = get_time() + ': ' + text + '\n'
    window0.FindElement('_outlog_').Update(text, append=True)
    if opmlog:
        opmlog.write(text)
    return()


def out_param(job, jobparam, jobbase, jobfile, opmuser):
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
    sg.Popup(str(jobbase) + ' parameter file written to:',
              str(jobfile),
            'Complete',no_titlebar=True)
    
                                
def opm_flow_parameters(filename):
    execute_command_subprocess('flow --help > '+ str(filename), False)
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
    sg.PopupOK('OPM Flow Parameters Loaded from Flow: ' + str(filename))
    return(jobparam, jobhelp)


def opm_popup(text,nrow):
    layout1 = [ [sg.Multiline(text, size=(80,nrow), background_color='white', text_color='darkgreen')],
                  [sg.CloseButton('OK')] ]
    window1 = sg.Window('OPMRUN - Flow Job Scheduler ' + opmvers).Layout(layout1)
    (button, values) = window1.Read()
    return()


def run_jobs(joblist,opmlog):
    if joblist == []:
        sg.PopupOK('No Jobs In Queue')
        return()
    jobnum = 0
    layout1   = [ [sg.Text('Selection the Run Option for All ' + str(len(joblist)) + ' Cases in Queue?')],    
                   [sg.Radio('Run in No Simulation Mode'      , 'bRadio'              )],
                   [sg.Radio('Run in Standard Simulation Mode', 'bRadio', default=True)],
                   [sg.Submit(), sg.Cancel()] ]
    window1   = sg.Window('Select Run Option').Layout(layout1)
    (button, values) = window1.Read()
    window1.Close()
    
    for x in joblist:
        jobnum  = jobnum + 1
        istart  = x.find('=') 
        job     = x[istart + 1:]
        jobcmd  = x[:istart + 1]
        jobpath = Path(job).parents[0]
        jobbase = Path(job).name
        jobroot = Path(job).stem
        joblog  = Path(jobbase).with_suffix('.LOG')

        if values[0]:
            jobcase = jobcmd + str(jobbase) + ' --enable-dry-run="true"' + ' | tee ' + str(joblog)
            print (jobcase)

        if values[1]:
            jobcase = jobcmd + str(jobbase)  + ' | tee ' + str(joblog)
            
        if button == 'Cancel':
            print(jobpath)
            print(jobcase)
        
        if button == 'Submit':
            out_log('Run Job ' + str(jobnum) + ' of ' + str(len(joblist)), opmlog)
            out_log('Start Job: ' + jobcase, opmlog)
            #
            # Change Working Directory
            #
            try:
                os.chdir(jobpath)
                print("Current Working Directory " , str(os.getcwd()))
            except OSError:
                print('Cannot change the Current Working Directory')
                out_log('Cannot change the Current Working Directory', opmlog)
                out_log('End   Job: ' + jobcase, opmlog)
                out_log('Completed Job No. ' + str(jobnum), opmlog)
                out_log('', opmlog)                
                continue
            #
            # Remove Existing Output Files
            #
            out_log('Removing Existing Output Files', opmlog)
            for text in ['.DBG', '.EGRID', '.INIT', '.LOG', '.PRT', '.SMSPEC', '.UNRST', '.UNSMRY',
                         '.dbg', '.egrid', '.init', '.log', '.prt', '.smspec', '.unrst', '.unsmry' ]:
                filename = Path(jobbase).with_suffix(text)
                if (filename.is_file()):
                    filename.unlink()
                    out_log('rm ' + str(filename), opmlog)
            #
            # Run Job
            #
            print(jobcase)
            out_log('Simulation Started', opmlog)
            execute_command_subprocess(jobcase, True)
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
                if status:
                    for line in enumerate(lines):
                        if (line[1] == ''):
                            continue
                        out_log(line[1],opmlog)
            out_log('End   Job: ' + jobcase, opmlog)
            out_log('Completed Job No. ' + str(jobnum), opmlog)
            out_log('', opmlog)
            opmlog.flush()
    return()
            

def save_queue(joblist):
    if not joblist:
        sg.PopupOK('No Cases In Job Queue; Queue will Not Be Saved')
    else:
        filename = sg.PopupGetFile('OPMRUN Queue File Name',default_extension='que', save_as=True,
                               file_types=[('OPM Queues', '*.que'), ('All', '*.*')], keep_on_top=False )      
        if filename:
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
        if len(lines) >= to_read or pos == 0:
            return lines[-to_read:offset and -offset or None], \
                   len(lines) > to_read or pos > 0
        avg_line_length *= 1.3

#-----------------------------------------------------------------------------------------------------------------------------------
# Pre-Processing Section
#-----------------------------------------------------------------------------------------------------------------------------------
#
# Display Opening Window
#
# Note Coded 

#
# Process Configuration Options
#
opmoptn  = dict()

if opmini.is_file():
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
    opmoptn['edit-command' ]     = 'None' 
    opmoptn['opm-flow-manual']   = 'None'
    opmoptn['output-font'  ]     = 'Courier'
    opmoptn['output-font-size']  = 10
    
    file  = open(opmini,'w')
    file.write('# \n')
    file.write('# OPMRUN Initial File \n')
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
    file.write('# End of OPMRUN Initial File \n')
    file.close()
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
#
# Run Flow Help and Store Commands
#
jobparam, jobhelp = opm_flow_parameters(opmparam)

#-----------------------------------------------------------------------------------------------------------------------------------
# Define GUI Section 
#-----------------------------------------------------------------------------------------------------------------------------------
mainmenu   = [['File', ['Open', 'Save', 'Exit'  ]],      
              ['Edit', ['Edit OPM Flow Default Parameters', 'List OPM Flow Default Parameters', 'Set OPM Flow Default Parameters'],],      
              ['Help', ['OPM Flow Manual', 'Help', 'About'],] ]
           
flowlayout = [[sg.Text('OPM Flow',background_color='black',text_color='white')],
                  [sg.Output(background_color='white', text_color='black', size=(160, 30),
                             key='_outflow_',font=(opmoptn['output-font'], opmoptn['output-font-size']))] ] 

loglayout  = [[sg.Text('OPM Run',background_color='darkgreen',text_color='white')],
                  [sg.Multiline(get_time() + ' Start', background_color='white', text_color='darkgreen',
                                do_not_clear=True, key='_outlog_',size=(160, 30),
                                font=(opmoptn['output-font'],opmoptn['output-font-size']))] ] 

mainwind   = [ [sg.Menu(mainmenu)],
              [sg.Text('OPM Flow Command Schedule')],
              [sg.Listbox(values=joblist, size=(164, 10), key='_joblist_', font=(opmoptn['output-font'],opmoptn['output-font-size']))],
           
              [sg.Button('Add Job'),
                  sg.Button('Edit Job'),
                  sg.Button('Delete Job'),
                  sg.Button('Clear Queue'),
                  sg.Button('Load Queue'),
                  sg.Button('Save Queue')],
                
              [sg.TabGroup([[sg.Tab('OPM Flow Output', flowlayout, title_color='black', background_color=None),
                             sg.Tab('OPM Run Log'    , loglayout , title_color='white', background_color=None)]],  
                             title_color=None,background_color=None)],
              
              [sg.Button('Run Jobs'),
                  sg.Button('Kill Job'),
                  sg.Button('Exit')],
              [sg.Text('')] ]

window0 = sg.Window('OPMRUN - Flow Job Scheduler ' + opmvers).Layout(mainwind)

#-----------------------------------------------------------------------------------------------------------------------------------
# Define GUI Event Loop, Read Buttons, and Make Callbacks etc. Section 
#-----------------------------------------------------------------------------------------------------------------------------------
while True:
    #
    # Read the Form and Process and Take appropriate action based on button
    #
    button, values = window0.Read()
    
    joblist = window0.FindElement('_joblist_').GetListValues()

    #
    # About Section
    #
    if button == 'About':
        opm_popup(abouttext,20)
    #
    # Add Job Section
    #
    elif button == 'Add Job':
        add_job(joblist,jobparam,opmuser)
    #
    # Clear Queue Section
    #
    elif button == 'Clear Queue':
        clear_queue(values['_joblist_'])
    #
    # Delete Job Section
    #
    elif button == 'Delete Job':
        delete_job(joblist,values['_joblist_'])
    #
    # Edit Job Section
    #
    elif button == 'Edit Job':
        edit_job(values['_joblist_'], jobhelp, opmuser)
    #
    # Edit OPM Flow Default Parameters Section
    #
    elif button == 'Edit OPM Flow Default Parameters':
       (jobparam, exitcode) = edit_parameters(jobparam, jobhelp)
    #        
    # Exit Section
    #
    elif button == 'Exit' or button is None:
        text = sg.PopupYesNo('Exit OPMRUN?')
        if text == 'Yes':          
            text = sg.PopupYesNo('Are You Sure You wish to Exit OPMRUN?')
            if text == 'Yes':
                break
    #
    # Help Section
    #
    if button == 'Help':
        opm_popup(helptext,10)
    #
    #  Kill Job Section
    #
    elif button == 'Kill Job':
        kill_job(joblist)
    #        
    #   List OPM Flow Parameter Section
    #
    elif button == 'List OPM Flow Default Parameters':
        if (jobparam):
            print('Start of OPM Flow Parameters')
            print(*('{}: {}'.format(*k) for k in enumerate(jobparam)), sep="\n")
            print('End   of OPM Flow Parameters')
        else:
            sg.PopupError('OPM Flow Parameters Have Not Been Set')
    #
    # Load Queue Section
    #
    elif button == 'Load Queue' or button == 'Open':
        load_queue(joblist)
    #
    # OPM Flow Manual Section
    #
    elif button == 'OPM Flow Manual':
        opm_flow_manual(opmoptn['opm-flow-manual'])
    #
    # Save Queue Section
    #
    elif button == 'Save Queue' or button == 'Save':
        save_queue(joblist)
    #        
    #   Set OPM Flow Default Parameters Section
    #
    elif button == 'Set OPM Flow Default Parameters':
        jobparam = default_parameters(jobparam,opmparam)
    #
    # Run Jobs Section
    #
    elif button == 'Run Jobs':
        run_jobs(joblist,opmlog)
        
#-----------------------------------------------------------------------------------------------------------------------------------
# Post Processing Section 
#-----------------------------------------------------------------------------------------------------------------------------------
window0.Close()

out_log('OPMRUN Processing Complete ', opmlog)
opmlog.close()


#===================================================================================================================================
# End of OPMRUN.py
#===================================================================================================================================
