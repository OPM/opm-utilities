# OPMRUN
OPMRUN is graphical user interface to Flow that has similar functionality to the commercial simulator’s ECLRUN program.
Target audience are Reservoir Engineers in a production environment. Developers and experienced Linux users will already
have compatible work flows.

  * Allows editing and management of OPM Flow’s run time parameters. Default parameters are automatically loaded from
OPM Flow, and the user can reset the default set either from a parameter or PRT file. Editing of a job’s parameter file
is also available.

  * Allows simulation jobs to be queued and run in either foreground (under OPMRUN), or background (in an xterm terminal
session). Jobs in the queue can be set to run in NOSIM mode or RUN mode.

  * Foreground jobs can be killed from OPMRUN.

  * Queues can be edited, saved and loaded.

  * Jobs can be compressed to save space (DATA , and all OPM Flow output files) and uncompressed.

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

OPMRUN is written in Python 3 and tested under Unbuntu-Mate 18.04 TLS. Compiled binary version should work on all Linux
systems, no need to install dependencies or Python.

## Notes:
Only Python 3 is currently supported and tested Python2 support has been deprecated. The following standard module
libraries are used in this version.

1. datetime
2. getpass
3. os
4. pathlib
5. psutil
6. sys
7. re
8. subprocess

In addition the following Python modules are required for OPMRUN:

1. FreeSimpleGUI

For OPMKEYW, the integrated OPM Flow Keyword Generator, the following standard modules are required:

1. datetime
2. platform
3. pathlib
4. tkinter as tk

In addition the OPMKEYW requires the following additional modules:

1. FreeSimpleGUI
2. airspeed

Copyright (C) 2018-2020 Equinox International Petroleum Consultants Pte Ltd.

Author  : David Baxendale
          david.baxendale@eipc.co
