# OPMRUN
OPMRUN is graphical user interface to Flow that has similar functionality to the commercial simulator’s ECLRUN program. 
Target audience are Reservoir Engineers in a production environment. Developers and experienced Linux users will already 
have compatible work flows.

Allows editing and management of OPM Flow’s run time parameters. Default parameters are automatically loaded from 
OPM Flow, and the user can reset the default set either from a parameter or PRT file. Editing of a job’s parameter file 
is also available.

Allows simulation jobs to be queued and run in either foreground (under OPMRUN), or background (in an xterm terminal 
session). Jobs in the queue can be set to run in NOSIM mode or RUN mode.

Foreground jobs can be killed from OPMRUN.

Queues can be edited, saved and loaded.

Jobs can be compressed to save space (DATA , and all OPM Flow output files) and uncompressed.

OPMRUN now includes a keyword generator (OPMKEYW) based on the Apache Velocity Template Language (“VTL”). The templates 
can therefore also be used with any editor that supports VTL, jEdit for example. There is one template per keyword, with 
formatting the same as the OPM Flow manual. Over 450 templates are currently implemented.

One can also customize the existing templates as well as creating User defined templates by including the templates in 
the template directory and following the VTL language syntax. Keywords filtered by Section in alphabetic order, and can 
also list all the keywords. Multiple keywords can be generated at a time and copied to the clipboard or saved to a file.
Section keywords (RUNSPEC, GRID, EDIT, PROPS, SOLUTION, SUMMARY and SCHEDULE) can optionally generate a set of keywords 
for the section. 
The keywords are examples, one still has to edit the resulting deck with the actual required data, but the format with 
comments should make this a straight forward process.

OPMRUN is written in Python 3 and tested under Unbuntu-Mate 18.04 TLS.

Compiled binary version should work on all Linux systems, no need to install dependencies or Python.

## Notes:
Only Python 3 is currently supported and tested Python2 support has been depreciated. The following standard module 
libraries are used in this version.

1. datetime
2. getpass
3. os
4. sys
5. re
8. subprocess

In addition the following Python modules are required for OPMRUN:

1. PySimpleGUI
2. psutil
3. pathlib 

For OPMKEYW the integrated OPM Flow Keyword Generator the following additional modelues are required:
1. platform
2. tkinter as tk
3. airspeed

PySimpleGUI is the GUI tool used to build OPMRUN. It is in active development and is frequently updated
for fixes and new features. This version of OPMRUN used verion 3.36.0 of PySimpleGUI, later and older
versions of PySimpleGUI may not work. Each release of OPMRUN will update to the latest release of
PySimpleGUI.

# OPMRUN Functionality

## Simple and Clean Interface.

![](.images/opmrun-01.png)

## Add Job and Select Run Type

![](.images/opmrun-02.png)
## Job Queue.

![](.images/opmrun-03.png)

## Set Parameter Default Options.

![](.images/opmrun-04.png)

## Edit Job Data and Parameter File.

![](.images/opmrun-05.png)

## Edit Data File with Preferred Editor.

![](.images/opmrun-06.png)

## Edit Parameter File with Help.

![](.images/opmrun-07.png)

## Run Jobs in Queue with Various Options.

![](.images/opmrun-08.png)

## Run Jobs in Queue Creates Log File.

![](.images/opmrun-09.png)

## Schedule Log for Tracking Progress.

![](.images/opmrun-10.png)

## Manual Available.

![](.images/opmrun-11.png)

## Job File Compression and Uncompression for Saving Space and Archiving.

![](.images/opmrun-12.png)

## OPMRUN.INI Settings File.

Stored in user’s home directory in sub directory OPM. Options includes:

  * OPM Flow manual location.
  * OPMKEYW  “template directory”.
  * ResInsight location.
  * Setting the editor command.
  * Author property fields used in some templates in OPMKEYW.
  * Defining OPMRUN output panel’s size, font and font size.

![](.images/opmrun-13.png)

Use the Edit/Options menu to edit options and Edit/Projects menu to edit project names and directories.

# OPMRUN Keyword Generator (OPMKEYW) Functionality

## OPMKEYW - OPM Flow Keyword Generator
The Keyword Generator is located under the “Tools” menu “Deck Generator” option. Additional Deck Generator applications 
are planned for future versions.

![](.images/opmkeyw-01.png)

The main elements are the KEYWORD LIST, KEYWORD FILTER OPTIONS and the DECK ELEMENT, as shown below

![](.images/opmkeyw-02.png)

The "Keyword Filter" button allows for the filtering of the various keywords in the selected section, including being 
able to list all the keywords available for all sections.  The HEADER section allows for a start and end of file 
comment headers. Clicking on a keyword will result in the keyword being "pasted" into the Deck element.

![](.images/opmkeyw-03.png)

The Deck element is editable by simply clicking anywhere in the element and making changes. Use the “Clear” button to 
clear the Deck element display.

![](.images/opmkeyw-04.png)

If a keyword requires a file, for example, the INCLUDE and LOAD keywords, then a dialog box is presented to enable the 
file to be selected. The application will also allow one to select the file name format, after the file has been 
selected.

Note that The COMMENT keyword, is not an actual keyword, but a comment block to make the deck more readable.

![](.images/opmkeyw-05.png)

Selecting a Section keyword (RUNSPEC, GRID,  EDIT, PROPS, SOLUTION, SUMMARY, and SCHEDULE) will give you an option to 
generate a representative set of keywords for that section. One can therefore generate a complete input deck in a 
matter of minutes.

However, you still have to edit this with your actual data.

![](.images/opmkeyw-06.png)

For The SCHEDULE Section keyword, one can also generate a date schedule from  a start year to and end year, using 
Annual, Quarterly, or Monthly time steps. A standard report is written at the beginning of each year and is 
subsequently switch off for intermediate  Quarterly and Monthly time steps. A final report is written at the end end of 
the run.

![](.images/opmkeyw-07.png)

Use the “Copy” button to copy the data in the Deck element to the clipboard, which you can then paste into your 
favorite editor. Alternatively, one can save the file directly to a *.DATA or *.INC file for further editing and 
processing.

![](.images/opmkeyw-08.png)

After selecting a keyword, right clicking on the keyword allows one to load the actual template for the keyword.
One can then edit the template and save the changes back to the same template or another template. Probably a good idea 
to save as a separate template.

![](.images/opmkeyw-09.png)


The Template Help option displays a brief introduction to VTL.







